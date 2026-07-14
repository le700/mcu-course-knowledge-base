"""
知识图谱适配器 - 加载和操作 knowledge_graph.json

支持的节点类型 (node types):
  - grade: 成绩组成
  - course: 课程
  - schedule: 教学安排
  - event: 课程事件
  - basic: 基本实验
  - equipment: 实验设备
  - extended: 扩展实验
  - design: 综合设计题目 (部分节点无显式 type 字段，通过 id 前缀 design_P- 识别)
  - peripheral: 外设
  - chapter: 章节
  - reference_code: 参考代码
  - hardware_board: 硬件板卡
  - hardware_interconnect: 板卡互联
  - chip_pinout: 芯片引脚
  - teacher: 教师
  - class: 班级

支持的关系类型 (edge relations):
  - has_grade: 课程→成绩项
  - has_schedule: 课程→教学安排
  - has_event: 课程→事件
  - next_event: 事件→下一个事件
  - contains: 章节→实验 / 章节→设计
  - uses_equipment: 实验→设备
  - requires_peripheral: 设计→外设
  - based_on_experiment: 设计→前置实验
  - has_chapter: 课程→章节
  - has_reference_code: 设计→参考代码
  - uses_hardware: 设计→硬件板卡
  - interconnects_with: 板卡→板卡
  - contains_chip: 板卡→芯片引脚
  - uses_interconnect: 设计→互联关系
  - has_teacher: 课程→教师
  - has_class: 课程→班级
  - teaches: 教师→班级
"""

import json
import os
import re
from typing import List, Dict, Optional, Any
from collections import defaultdict

# 中文字符 Unicode 范围
_CJK_RE = re.compile(r'[\u4e00-\u9fff]')


class KnowledgeGraphAdapter:
    """知识图谱适配器 - 加载 knowledge_graph.json 并提供查询接口"""

    def __init__(self, kg_path: str = "/workspace/rag_v4/knowledge_graph.json"):
        """
        初始化知识图谱适配器

        Args:
            kg_path: knowledge_graph.json 文件路径

        Raises:
            FileNotFoundError: 当知识图谱文件不存在时
            json.JSONDecodeError: 当 JSON 格式错误时
        """
        if not os.path.exists(kg_path):
            raise FileNotFoundError(
                f"知识图谱文件不存在: {kg_path}\n"
                f"请确认 RAG v4 知识库已正确安装。"
            )

        self.kg_path = kg_path
        self.kg = None

        # 索引结构
        self._node_index: Dict[str, dict] = {}
        self._type_index: Dict[str, List[str]] = defaultdict(list)
        self._adjacency: Dict[str, List[tuple]] = defaultdict(list)  # node_id -> [(target, relation, edge_obj)]
        self._reverse_adjacency: Dict[str, List[tuple]] = defaultdict(list)
        self._label_index: Dict[str, List[str]] = defaultdict(list)  # token -> [node_ids]

        self._load()

    def _load(self):
        """加载 JSON 并构建所有索引"""
        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                self.kg = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"知识图谱 JSON 格式错误: {e.msg}",
                e.doc, e.pos
            ) from e

        if not isinstance(self.kg, dict):
            raise ValueError(f"知识图谱根节点应为字典，实际为 {type(self.kg).__name__}")

        # 验证必要字段
        if "nodes" not in self.kg:
            raise ValueError("知识图谱缺少 'nodes' 字段")
        if "edges" not in self.kg:
            raise ValueError("知识图谱缺少 'edges' 字段")

        # 构建节点索引
        for node in self.kg.get("nodes", []):
            nid = node.get("id")
            if not nid:
                continue  # 跳过无 id 的节点
            self._node_index[nid] = node

            # 类型索引
            node_type = node.get("type", "unknown")
            self._type_index[node_type].append(nid)

            # 如果节点 id 以 design_P- 开头，也归入 design 类型
            if nid.startswith("design_P-") and node_type != "design":
                self._type_index["design"].append(nid)

            # 构建标签倒排索引（用于关键词搜索）
            label = node.get("label", "")
            if not label:
                continue
            # 分词：处理中文、英文、数字以及特殊字符
            for token in label.replace("#", " ").replace("-", " ").replace("_", " ").split():
                token = token.strip().lower()
                if len(token) >= 2:
                    self._label_index[token].append(nid)
                    # 对于中文 token，额外添加字符级 bigram 和 trigram 索引
                    # 例如 "温湿度传感器" → 同时索引 "温湿", "湿度", "度传", "传感", "感器", "温湿度", "湿度传", "度传感", "传感器"
                    if _CJK_RE.search(token):
                        for i in range(len(token) - 1):
                            bigram = token[i:i + 2]
                            self._label_index[bigram].append(nid)
                        for i in range(len(token) - 2):
                            trigram = token[i:i + 3]
                            self._label_index[trigram].append(nid)

        # 构建邻接表
        for edge in self.kg.get("edges", []):
            src = edge.get("source")
            tgt = edge.get("target")
            if not src or not tgt:
                continue
            rel = edge.get("relation", "unknown")
            self._adjacency[src].append((tgt, rel, edge))
            self._reverse_adjacency[tgt].append((src, rel, edge))

    # ---- 基础查询 ----

    def get_node(self, node_id: str) -> Optional[dict]:
        """
        查询单个节点

        Args:
            node_id: 节点唯一标识符

        Returns:
            节点字典，不存在时返回 None
        """
        return self._node_index.get(node_id)

    def get_meta(self) -> dict:
        """
        获取知识图谱元信息

        Returns:
            包含课程名、机构、教师、版本、日期等信息的字典
        """
        return self.kg.get("meta", {}) if self.kg else {}

    def find_by_type(self, node_type: str) -> List[dict]:
        """
        按类型查找节点

        Args:
            node_type: 节点类型名，如 "grade", "event", "design", "chip_pinout" 等

        Returns:
            匹配类型的节点列表
        """
        matches = self._type_index.get(node_type, [])
        return [self._node_index[nid] for nid in matches if nid in self._node_index]

    def search(self, keyword: str) -> List[dict]:
        """
        关键词搜索节点（通过标签倒排索引匹配）

        支持中文、英文关键词，自动分词后按匹配度评分。
        中文关键词自动生成 bigram 和 trigram 以匹配中文标签。

        Args:
            keyword: 搜索关键词，支持多词组合

        Returns:
            按匹配度降序排列的节点列表，最多返回 20 条
        """
        scored = defaultdict(int)

        # 先按空格分词
        raw_keywords = keyword.lower().split()
        # 收集所有搜索 token（包括中文 bigram/trigram 扩展）
        search_tokens = []
        for kw in raw_keywords:
            search_tokens.append(kw)
            # 对于中文关键词，同样生成 bigram 和 trigram
            if _CJK_RE.search(kw):
                for i in range(len(kw) - 1):
                    search_tokens.append(kw[i:i + 2])
                for i in range(len(kw) - 2):
                    search_tokens.append(kw[i:i + 3])

        for kw in search_tokens:
            for nid in self._label_index.get(kw, []):
                scored[nid] += 1
        sorted_ids = sorted(scored.items(), key=lambda x: x[1], reverse=True)
        return [self._node_index[nid] for nid, _ in sorted_ids[:20] if nid in self._node_index]

    def get_neighbors(self, node_id: str, relation: str = None,
                      direction: str = "out") -> List[dict]:
        """
        获取邻居节点

        Args:
            node_id: 源节点 ID
            relation: 过滤关系类型，为 None 时返回所有关系
            direction: 方向，"out" (出边), "in" (入边), 或 "both" (双向)

        Returns:
            邻居节点列表，每项包含 node, relation, direction 字段
        """
        results = []
        if direction in ("out", "both"):
            for tgt, rel, edge in self._adjacency.get(node_id, []):
                if relation is None or rel == relation:
                    node = self._node_index.get(tgt)
                    if node:
                        results.append({"node": node, "relation": rel, "direction": "out"})
        if direction in ("in", "both"):
            for src, rel, edge in self._reverse_adjacency.get(node_id, []):
                if relation is None or rel == relation:
                    node = self._node_index.get(src)
                    if node:
                        results.append({"node": node, "relation": rel, "direction": "in"})
        return results

    def traverse(self, start_id: str, relation: str = None,
                 direction: str = "out", max_depth: int = 3,
                 node_type_filter: List[str] = None) -> List[dict]:
        """
        BFS 图遍历，返回访问路径

        Args:
            start_id: 起始节点 ID
            relation: 过滤关系类型，为 None 时不过滤
            direction: 遍历方向，目前仅支持 "out"
            max_depth: 最大遍历深度，默认 3
            node_type_filter: 节点类型过滤列表，仅返回匹配类型的节点

        Returns:
            遍历结果列表，每项包含 node, depth, path 字段
        """
        visited = {start_id}
        queue = [(start_id, 0, [])]  # (node_id, depth, path)
        results = []

        while queue:
            node_id, depth, path = queue.pop(0)
            if depth > max_depth:
                continue

            node = self._node_index.get(node_id)
            if node:
                if node_type_filter is None or node.get("type") in node_type_filter:
                    results.append({"node": node, "depth": depth, "path": path})

            if depth < max_depth:
                for neighbor_id, rel, edge in self._adjacency.get(node_id, []):
                    if neighbor_id not in visited and (relation is None or rel == relation):
                        visited.add(neighbor_id)
                        new_path = path + [{"from": node_id, "to": neighbor_id, "relation": rel}]
                        queue.append((neighbor_id, depth + 1, new_path))

        return results

    # ---- 业务查询 ----

    def get_design_dependencies(self, design_id: str) -> dict:
        """
        获取综合设计的完整依赖链

        包括：
        - 前置实验 (based_on_experiment)
        - 所需外设 (requires_peripheral)
        - 使用硬件板卡 (uses_hardware)
        - 包含芯片 (contains_chip，通过硬件板卡递归获取)
        - 参考代码 (has_reference_code)

        Args:
            design_id: 设计节点 ID，如 "design_P-A-1#"

        Returns:
            包含 design, experiments, peripherals, hardware_boards, chips, reference_code 的字典
        """
        result = {
            "design": self.get_node(design_id),
            "experiments": [],
            "peripherals": [],
            "hardware_boards": [],
            "chips": [],
            "reference_code": []
        }

        if not result["design"]:
            return {"error": f"设计节点 {design_id} 不存在"}

        # 获取所有出边邻居
        neighbors = self.get_neighbors(design_id, direction="out")
        for item in neighbors:
            node = item["node"]
            rel = item["relation"]

            if rel == "based_on_experiment":
                result["experiments"].append(node)
            elif rel == "requires_peripheral":
                result["peripherals"].append(node)
            elif rel == "uses_hardware":
                result["hardware_boards"].append(node)
                # 递归获取硬件板卡上的芯片
                chip_neighbors = self.get_neighbors(node["id"], relation="contains_chip", direction="out")
                for chip_item in chip_neighbors:
                    result["chips"].append(chip_item["node"])
            elif rel == "has_reference_code":
                result["reference_code"].append(node)

        return result

    def get_all_designs(self) -> List[dict]:
        """
        获取所有综合设计题目

        通过以下方式识别设计节点：
        1. 类型为 "design" 的节点
        2. id 以 "design_P-" 开头的节点
        3. 预定义的已知设计 ID 列表

        Returns:
            所有综合设计节点列表（去重）
        """
        designs = []
        seen_ids = set()

        # 方法1：按已知设计 ID 列表获取
        known_design_ids = [
            "design_P-A-1#", "design_P-A-2#", "design_P-A-3#",
            "design_P-A-4#", "design_P-A-5#", "design_P-B-1#",
            "design_P-B-2#", "design_P-B-3#", "design_P-B-4#",
            "design_P-B-5#", "design_P-B-6#"
        ]
        for nid in known_design_ids:
            node = self.get_node(nid)
            if node and nid not in seen_ids:
                designs.append(node)
                seen_ids.add(nid)

        # 方法2：按类型 "design" 搜索
        for node in self.find_by_type("design"):
            nid = node.get("id")
            if nid and nid not in seen_ids:
                designs.append(node)
                seen_ids.add(nid)

        # 方法3：扫描所有节点，按 id 前缀匹配
        for nid in self._node_index:
            if nid.startswith("design_P-") and nid not in seen_ids:
                node = self._node_index[nid]
                designs.append(node)
                seen_ids.add(nid)

        return designs

    def get_course_events(self) -> List[dict]:
        """
        获取课程事件时间线

        包含：现场培训、基本实验、综合设计、答辩考试、提交报告

        Returns:
            课程事件节点列表
        """
        event_ids = [
            "event_training",
            "event_basic_exp",
            "event_design",
            "event_defense",
            "event_report"
        ]
        events = []
        for nid in event_ids:
            node = self.get_node(nid)
            if node:
                events.append(node)
        return events

    def get_grades(self) -> List[dict]:
        """
        获取成绩组成

        Returns:
            所有 grade 类型节点列表
        """
        return self.find_by_type("grade")

    def get_chip_pinout(self, chip_name: str) -> Optional[dict]:
        """
        获取芯片引脚信息

        支持模糊匹配：自动处理大小写、空格、连字符等差异。

        Args:
            chip_name: 芯片名称，如 "ADC0809", "8255", "DHT11" 等

        Returns:
            芯片引脚节点字典，未找到时返回 None
        """
        # 规范化芯片名称
        normalized = chip_name.lower().replace(" ", "").replace("-", "").replace("_", "")

        # 已知芯片名称到节点 ID 的映射
        chip_id_map = {
            "adc0809": "adc0809_pins",
            "74hc373": "74hc373_pins",
            "74hc240": "74hc240_pins",
            "74hc02": "74hc02_pins",
            "8255": "i8255_pins",
            "8255a": "i8255_pins",
            "uln2003": "uln2003_pins",
            "uln2003a": "uln2003_pins",
            "dht11": "dht11_pins",
            "stc89c54rd": "hw_board1",
            "stc89c54rd+": "hw_board1",
            "ds18b20": "equip_DS18B20",
            "lcd1602": "equip_LCD1602",
            "at24c02": "equip_AT24C02",
        }

        # 先尝试精确映射
        node_id = chip_id_map.get(normalized)
        if node_id:
            node = self.get_node(node_id)
            if node:
                return node

        # 再尝试搜索
        results = self.search(chip_name)
        for r in results:
            if r.get("type") == "chip_pinout":
                return r

        return None

    # ---- 统计与元数据 ----

    def get_node_types(self) -> List[str]:
        """
        获取所有节点类型

        Returns:
            节点类型列表（去重排序）
        """
        return sorted(list(self._type_index.keys()))

    def get_stats(self) -> dict:
        """
        获取知识图谱统计信息

        Returns:
            包含 total_nodes, total_edges, node_types, meta 的统计字典
        """
        return {
            "total_nodes": len(self._node_index),
            "total_edges": len(self.kg.get("edges", [])),
            "node_types": {t: len(ids) for t, ids in self._type_index.items()},
            "meta": self.get_meta()
        }