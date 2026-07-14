"""
桥接主模块 - 整合 RAG v4 三层检索与知识图谱

提供统一的查询入口，自动根据查询意图路由到最佳检索路径：
  - 芯片/引脚/地址查询 → 知识图谱精确查询 + 硬件参考
  - 综合设计题目查询 → 知识图谱依赖链查询
  - 一般技术问题 → RAG v4 三层检索 (关键词召回 + 语义召回 + 精排)
  - 硬件参考手册 → 本地文件搜索

支持 LRU 查询缓存，减少重复检索开销。
"""

import os
import sys
import time
import hashlib
import importlib
from typing import List, Dict, Optional, Any
from collections import OrderedDict

# 从同包导入知识图谱适配器
from .kg_adapter import KnowledgeGraphAdapter

# 添加 RAG v4 路径到 sys.path，以便导入 agent_tools
RAG_V4_PATH = "/workspace/rag_v4"
if RAG_V4_PATH not in sys.path:
    sys.path.insert(0, RAG_V4_PATH)


class QueryCache:
    """
    LRU 查询缓存

    使用 OrderedDict 实现近似 LRU 淘汰策略，支持基于时间的 TTL 过期。

    Attributes:
        max_entries: 最大缓存条目数
        ttl_seconds: 缓存有效期（秒）
    """

    def __init__(self, max_entries: int = 500, ttl_seconds: int = 300):
        """
        初始化查询缓存

        Args:
            max_entries: 最大缓存条目数，默认 500
            ttl_seconds: 缓存有效期（秒），默认 300 秒
        """
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._cache = OrderedDict()

    def _make_key(self, query: str, project_id: str) -> str:
        """
        生成缓存键

        Args:
            query: 查询文本
            project_id: 项目/会话标识

        Returns:
            SHA256 哈希的前 16 位十六进制字符串
        """
        return hashlib.sha256(f"{project_id}|{query}".encode("utf-8")).hexdigest()[:16]

    def get(self, query: str, project_id: str) -> Optional[dict]:
        """
        从缓存获取查询结果

        Args:
            query: 查询文本
            project_id: 项目/会话标识

        Returns:
            缓存的数据字典，过期或不存在时返回 None
        """
        key = self._make_key(query, project_id)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                # 访问时移到末尾（LRU）
                self._cache.move_to_end(key)
                return entry["data"]
            else:
                # 已过期，删除
                del self._cache[key]
        return None

    def set(self, query: str, project_id: str, data: dict):
        """
        将查询结果存入缓存

        Args:
            query: 查询文本
            project_id: 项目/会话标识
            data: 要缓存的数据字典
        """
        key = self._make_key(query, project_id)
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_entries:
                # 淘汰最久未使用的条目
                self._cache.popitem(last=False)
        self._cache[key] = {"data": data, "timestamp": time.time()}

    def clear(self):
        """清空所有缓存"""
        self._cache.clear()

    def stats(self) -> dict:
        """
        获取缓存统计

        Returns:
            包含 entries, max, ttl 的统计字典
        """
        return {"entries": len(self._cache), "max": self.max_entries, "ttl": self.ttl_seconds}


class HubBridge:
    """
    八爪鱼中枢与 RAG v4 的桥接层

    整合知识图谱查询、RAG 三层检索、硬件参考手册、代码参考
    四大数据源，提供统一查询接口。

    使用示例:
        bridge = HubBridge()
        result = bridge.unified_query("ADC0809 基地址是多少")
        deps = bridge.kg_get_design_deps("design_P-A-1#")
        stats = bridge.health_check()
    """

    def __init__(self, rag_root: str = RAG_V4_PATH,
                 kg_path: str = None,
                 enable_cache: bool = True):
        """
        初始化桥接层

        Args:
            rag_root: RAG v4 根目录路径
            kg_path: 知识图谱 JSON 文件路径，为 None 时自动使用 rag_root 下的 knowledge_graph.json
            enable_cache: 是否启用查询缓存，默认 True
        """
        self.rag_root = rag_root
        if kg_path is None:
            kg_path = os.path.join(rag_root, "knowledge_graph.json")
        self.kg_path = kg_path
        self.enable_cache = enable_cache

        # 延迟加载的组件
        self._kg_adapter = None
        self._rag_engine = None
        self._rag_import_error = None
        self._hardware_parser = None
        self._cache = QueryCache() if enable_cache else None

        # 硬件参考路径
        self.hardware_ref_path = os.path.join(rag_root, "hardware_ref_pa1.md")
        # 代码参考路径
        self.codex_readme_path = "/workspace/P-A-1-Codex参考_README.md"

        # 验证关键路径
        self._verify_paths()

    def _verify_paths(self):
        """验证关键路径是否存在，记录缺失项"""
        self._path_status = {
            "kg_path": os.path.exists(self.kg_path),
            "hardware_ref": os.path.exists(self.hardware_ref_path),
            "codex_ref": os.path.exists(self.codex_readme_path),
            "rag_root": os.path.exists(self.rag_root),
        }

    # ---- 延迟加载属性 ----

    @property
    def kg(self) -> KnowledgeGraphAdapter:
        """
        延迟加载知识图谱适配器

        Returns:
            KnowledgeGraphAdapter 实例

        Raises:
            FileNotFoundError: 当知识图谱文件不存在时
        """
        if self._kg_adapter is None:
            if not self._path_status.get("kg_path", False):
                raise FileNotFoundError(
                    f"知识图谱文件不存在: {self.kg_path}\n"
                    f"请确认 RAG v4 知识库已正确安装。"
                )
            self._kg_adapter = KnowledgeGraphAdapter(self.kg_path)
        return self._kg_adapter

    @property
    def rag_available(self) -> bool:
        """
        检查 RAG 引擎是否可用

        Returns:
            True 如果 RAG 引擎成功加载，否则 False
        """
        # 触发延迟加载
        _ = self.rag
        return self._rag_engine is not None

    @property
    def rag(self):
        """
        延迟加载 RAG v4 检索引擎

        使用 importlib.import_module 延迟导入，避免模块级加载
        SentenceTransformer、ChromaDB 等重型依赖导致启动慢或失败。

        Returns:
            agent_tools 模块，加载失败时返回 None
        """
        if self._rag_engine is None and self._rag_import_error is None:
            # 先检查 agent_tools.py 是否存在
            agent_tools_path = os.path.join(self.rag_root, "agent_tools.py")
            if not os.path.exists(agent_tools_path):
                self._rag_import_error = f"agent_tools.py 不存在: {agent_tools_path}"
                self._rag_engine = None
                return None

            try:
                # 使用 importlib 延迟导入，避免模块级错误导致崩溃
                # 先确保 rag_root 在 sys.path 中
                if self.rag_root not in sys.path:
                    sys.path.insert(0, self.rag_root)
                self._rag_engine = importlib.import_module("agent_tools")
            except ImportError as e:
                self._rag_import_error = f"导入失败: {e}"
                self._rag_engine = None
            except Exception as e:
                self._rag_import_error = f"加载异常: {e}"
                self._rag_engine = None
        return self._rag_engine

    @property
    def hardware_parser(self):
        """
        延迟加载硬件参考解析器

        Returns:
            HardwareRefParser 实例，加载失败时返回 None
        """
        if self._hardware_parser is None:
            try:
                from .hardware_parser import HardwareRefParser
                self._hardware_parser = HardwareRefParser(self.hardware_ref_path)
            except Exception:
                self._hardware_parser = None
        return self._hardware_parser

    # ---- 知识图谱查询 ----

    def kg_query_node(self, node_id: str) -> dict:
        """
        查询知识图谱节点及其邻居

        Args:
            node_id: 节点 ID

        Returns:
            包含 node, neighbors, neighbor_count 的字典
        """
        try:
            node = self.kg.get_node(node_id)
            if not node:
                return {"error": f"节点 {node_id} 不存在"}
            neighbors = self.kg.get_neighbors(node_id, direction="both")
            return {
                "node": node,
                "neighbors": neighbors,
                "neighbor_count": len(neighbors)
            }
        except FileNotFoundError as e:
            return {"error": str(e)}

    def kg_get_design_deps(self, design_id: str) -> dict:
        """
        获取综合设计完整依赖链

        Args:
            design_id: 设计节点 ID，如 "design_P-A-1#"

        Returns:
            包含前置实验、外设、硬件板卡、芯片、参考代码的依赖字典
        """
        try:
            return self.kg.get_design_dependencies(design_id)
        except FileNotFoundError as e:
            return {"error": str(e)}

    def kg_get_all_designs(self) -> List[dict]:
        """
        获取所有综合设计题目

        Returns:
            所有综合设计节点列表
        """
        try:
            return self.kg.get_all_designs()
        except FileNotFoundError as e:
            return [{"error": str(e)}]

    def kg_get_chip(self, chip_name: str) -> Optional[dict]:
        """
        获取芯片引脚信息

        Args:
            chip_name: 芯片名称

        Returns:
            芯片引脚节点字典，未找到时返回 None
        """
        try:
            return self.kg.get_chip_pinout(chip_name)
        except FileNotFoundError as e:
            return {"error": str(e)}

    def kg_search(self, keyword: str) -> List[dict]:
        """
        关键词搜索知识图谱

        Args:
            keyword: 搜索关键词

        Returns:
            匹配节点列表
        """
        try:
            return self.kg.search(keyword)
        except FileNotFoundError as e:
            return [{"error": str(e)}]

    def kg_get_stats(self) -> dict:
        """
        获取知识图谱统计信息

        Returns:
            统计字典
        """
        try:
            return self.kg.get_stats()
        except FileNotFoundError as e:
            return {"error": str(e), "status": "not_loaded"}

    # ---- RAG 检索 ----

    def rag_search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        调用 RAG v4 三层检索

        先检查缓存，命中则直接返回；否则调用 agent_tools.search_pdf。

        Args:
            query: 查询文本
            top_k: 返回结果数，默认 5

        Returns:
            检索结果列表
        """
        # 检查缓存
        if self._cache:
            cached = self._cache.get(query, "default")
            if cached:
                return cached

        if self.rag is None:
            err_msg = self._rag_import_error or "RAG 引擎未加载"
            return [{"error": err_msg, "source": "rag"}]

        if hasattr(self.rag, "search_pdf"):
            try:
                results = self.rag.search_pdf(query, top_k=top_k)
                if self._cache:
                    self._cache.set(query, "default", results)
                return results
            except Exception as e:
                return [{"error": str(e), "source": "rag"}]

        return [{"error": "RAG 引擎缺少 search_pdf 方法", "source": "rag"}]

    def rag_smart_answer(self, question: str) -> dict:
        """
        调用 RAG v4 智能问答

        Args:
            question: 自然语言问题

        Returns:
            智能问答结果字典
        """
        if self.rag is None:
            return {"error": self._rag_import_error or "RAG 引擎未加载"}

        if hasattr(self.rag, "smart_answer"):
            try:
                return self.rag.smart_answer(question)
            except Exception as e:
                return {"error": str(e)}

        return {"error": "RAG 引擎缺少 smart_answer 方法"}

    # ---- 硬件参考 ----

    def hw_read_ref(self) -> str:
        """
        读取硬件参考手册全文

        Returns:
            硬件参考手册的完整文本内容，文件不存在时返回空字符串
        """
        if os.path.exists(self.hardware_ref_path):
            try:
                with open(self.hardware_ref_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"[读取错误: {e}]"
        return ""

    def hw_search(self, keyword: str) -> List[str]:
        """
        在硬件参考手册中搜索关键词

        返回包含关键词的行及其上下文（前后各 2 行）。

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的文本片段列表，最多返回 10 条
        """
        content = self.hw_read_ref()
        if not content:
            return []
        lines = content.split("\n")
        results = []
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])
                results.append(context)
        return results[:10]

    def get_quick_reference(self) -> dict:
        """
        返回硬件快速参考表（最常用的地址和引脚）

        优先从 hardware_parser 获取，回退到内置映射。

        Returns:
            {key: value} 如 {"8255A地址": "0x0480", "ADC0809地址": "0x4000", ...}
        """
        if self.hardware_parser is not None:
            try:
                return self.hardware_parser.get_quick_reference()
            except Exception:
                pass
        # 回退到内置映射
        return {
            "8255A地址": "0x0480",
            "8255A 控制口": "0x0483",
            "8255A 控制字": "0x89",
            "ADC0809地址": "0x4000",
            "DHT11引脚": "P3.3",
            "晶振频率": "12MHz",
            "串口": "1200bps, P3.0/RXD, P3.1/TXD",
        }

    def get_chip_detail(self, chip_name: str) -> dict:
        """
        获取芯片详细信息（KG + 硬件参考合并）

        先从知识图谱查询芯片引脚信息，再从硬件参考解析器获取
        补充细节并合并返回。

        Args:
            chip_name: 芯片名称，如 "ADC0809", "8255", "DHT11"

        Returns:
            包含 kg_result, hw_result, merged 三个字段的详情字典
        """
        result = {
            "chip_name": chip_name,
            "kg_result": None,
            "hw_result": None,
            "merged": {},
        }

        # 从知识图谱查询
        try:
            kg_chip = self.kg_get_chip(chip_name)
            if kg_chip and "error" not in kg_chip:
                result["kg_result"] = kg_chip
        except Exception:
            pass

        # 从硬件参考解析器查询
        if self.hardware_parser is not None:
            try:
                hw_detail = self.hardware_parser.get_chip_detail(chip_name)
                if "error" not in hw_detail:
                    result["hw_result"] = hw_detail
            except Exception:
                pass

        # 合并结果
        merged = {}
        if result["hw_result"]:
            chip_def = result["hw_result"].get("chip", {})
            merged.update(chip_def)
            pinout = result["hw_result"].get("pinout", {})
            merged["total_pins"] = pinout.get("total_pins", 0)
            merged["pins"] = pinout.get("pins", [])
        if result["kg_result"]:
            # KG 可能有更多上下文信息（如标签、属性等）
            kg_label = result["kg_result"].get("label", "")
            if kg_label:
                merged["kg_label"] = kg_label
            kg_props = result["kg_result"].get("properties", {})
            if kg_props:
                merged["kg_properties"] = kg_props

        result["merged"] = merged
        return result

    # ---- 代码参考 ----

    def code_read_ref(self) -> str:
        """
        读取 Codex P-A-1 参考 README

        Returns:
            README 文件的完整文本内容，文件不存在时返回空字符串
        """
        if os.path.exists(self.codex_readme_path):
            try:
                with open(self.codex_readme_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"[读取错误: {e}]"
        return ""

    # ---- 统一查询 ----

    def unified_query(self, query: str, project_id: str = "default",
                      sources: List[str] = None) -> dict:
        """
        统一查询入口：自动路由到最佳检索路径

        路由规则：
        - 包含芯片名/引脚/地址关键词 → 知识图谱精确查询 + 硬件参考搜索
        - 包含 P-A-#/P-B-# 设计题号 → 知识图谱依赖链查询
        - 其他情况 → RAG v4 三层检索

        Args:
            query: 用户查询文本
            project_id: 项目/会话标识，用于缓存隔离
            sources: 启用的数据源列表，默认 ["kg", "rag", "hardware"]

        Returns:
            包含 query, project_id, kg_results, rag_results, hw_results, route, retrieval_time_ms 的结果字典
        """
        if sources is None:
            sources = ["kg", "rag", "hardware"]

        start_time = time.time()
        result = {
            "query": query,
            "project_id": project_id,
            "kg_results": [],
            "rag_results": [],
            "hw_results": [],
            "route": "unknown",
            "retrieval_time_ms": 0
        }

        query_lower = query.lower()

        # 路由决策所用的关键词列表
        chip_keywords = [
            "adc0809", "8255", "8255a", "dht11", "74hc", "uln2003", "stc89",
            "ds18b20", "ds1302", "lcd1602", "pcf8591", "max485", "ch341",
            "74hc373", "74hc240", "74hc02", "at24c02", "rfid", "rc522",
            "引脚", "pin", "基地址", "地址", "端口"
        ]
        design_keywords = ["p-a-", "p-b-", "综合设计"]

        is_chip_query = any(kw in query_lower for kw in chip_keywords)
        is_design_query = any(kw in query_lower for kw in design_keywords)

        # 路由1：芯片/引脚查询
        if is_chip_query and "kg" in sources:
            result["route"] = "knowledge_graph"
            for kw in chip_keywords:
                if kw in query_lower:
                    chip = self.kg_get_chip(kw)
                    if chip and "error" not in chip:
                        result["kg_results"].append(chip)
                        break  # 找到一个即可
            if "hardware" in sources:
                result["hw_results"] = self.hw_search(query)[:3]

            # 硬件路由：如果 hardware_parser 可用，优先精确查询
            if self.hardware_parser is not None:
                result["route"] = "hardware"
                for kw in chip_keywords:
                    if kw in query_lower:
                        try:
                            detail = self.get_chip_detail(kw)
                            if detail.get("merged"):
                                result["hw_results"].append(detail["merged"])
                                break
                        except Exception:
                            pass
                # 也尝试搜索引脚信号
                if any(kw in query_lower for kw in ["引脚", "pin"]):
                    for kw in chip_keywords:
                        if kw in query_lower:
                            try:
                                pinout = self.hardware_parser.get_pinout(kw)
                                if "error" not in pinout:
                                    result["hw_results"].append(pinout)
                                    result["route"] = "hardware_pinout"
                                    break
                            except Exception:
                                pass

        # 路由2：综合设计题目查询
        elif is_design_query and "kg" in sources:
            result["route"] = "knowledge_graph_design"
            for nid in self.kg._node_index:
                if nid.startswith("design_P-"):
                    # 同时匹配完整 ID 和去掉 "design_" 前缀的短 ID
                    short_id = nid.replace("design_", "").lower()
                    if nid.lower() in query_lower or short_id in query_lower:
                        deps = self.kg_get_design_deps(nid)
                        result["kg_results"].append(deps)
                        break

        # 路由3：补充 RAG 检索
        if (not result["kg_results"] or "rag" in sources) and not is_chip_query:
            if result["route"] == "unknown":
                result["route"] = "rag"
            else:
                result["route"] = f"{result['route']}+rag"
            result["rag_results"] = self.rag_search(query, top_k=5)

        # 兜底：如果没有任何结果，默认走 RAG
        if result["route"] == "unknown":
            result["route"] = "rag"
            result["rag_results"] = self.rag_search(query, top_k=5)

        result["retrieval_time_ms"] = int((time.time() - start_time) * 1000)
        return result

    # ---- 缓存管理 ----

    def cache_clear(self):
        """清空查询缓存"""
        if self._cache:
            self._cache.clear()

    def cache_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            包含 entries, max, ttl 的统计字典
        """
        if self._cache:
            return self._cache.stats()
        return {"entries": 0, "max": 0, "ttl": 0}

    # ---- 健康检查 ----

    def health_check(self) -> dict:
        """
        健康检查：验证所有数据源是否可用

        Returns:
            包含各数据源可用状态的字典
        """
        kg_stats = {"status": "not_loaded"}
        try:
            if self._kg_adapter is not None:
                kg_stats = self.kg_get_stats()
            elif os.path.exists(self.kg_path):
                kg_stats = {"status": "available"}
        except Exception as e:
            kg_stats = {"status": "error", "message": str(e)}

        return {
            "kg_loaded": self._kg_adapter is not None or os.path.exists(self.kg_path),
            "rag_available": self.rag is not None,
            "rag_error": self._rag_import_error,
            "hardware_ref": os.path.exists(self.hardware_ref_path),
            "hardware_parser": self.hardware_parser is not None,
            "codex_ref": os.path.exists(self.codex_readme_path),
            "cache_enabled": self._cache is not None,
            "cache_stats": self.cache_stats(),
            "kg_stats": kg_stats,
            "path_status": self._path_status,
        }