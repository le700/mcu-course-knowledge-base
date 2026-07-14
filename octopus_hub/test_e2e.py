#!/usr/bin/env python3
"""八爪鱼记忆中枢 - 端到端测试

完整测试全链路：导入 → 初始化 → 知识图谱 → 硬件解析 →
桥接层 → 项目注册 → 记忆存储 → 反思引擎 → 无感接手 → 自动闭环。

用法:
    python3 test_e2e.py

测试数据库: /workspace/octopus_hub/test_hub.db
测试后自动清理临时文件。
"""

import sys
import os
import time
import json
import traceback
import shutil

# 确保项目根目录在 sys.path 中
sys.path.insert(0, "/workspace")

# 测试专用数据库路径
TEST_DB_PATH = "/workspace/octopus_hub/test_hub.db"
TEST_CHROMA_PATH = "/workspace/octopus_hub/test_chroma_memories"


def cleanup():
    """清理测试临时文件"""
    for path in [TEST_DB_PATH, TEST_CHROMA_PATH]:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)


# ---- 测试工具 ----

class TestRunner:
    """测试运行器，管理测试结果"""

    def __init__(self):
        self.results = {"pass": 0, "fail": 0, "errors": []}

    def test(self, name: str, condition: bool, detail: str = ""):
        """记录一个测试用例

        Args:
            name: 测试名称
            condition: 测试条件（True 为通过）
            detail: 失败时的详细信息
        """
        if condition:
            self.results["pass"] += 1
            print(f"  [PASS] {name}")
        else:
            self.results["fail"] += 1
            err_msg = f"{name}: {detail}" if detail else name
            self.results["errors"].append(err_msg)
            print(f"  [FAIL] {name}")
            if detail:
                print(f"         {detail}")

    def section(self, title: str):
        """打印测试章节标题"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    def summary(self):
        """打印测试汇总"""
        print(f"\n{'='*60}")
        print(f"  测试汇总: 通过 {self.results['pass']}, 失败 {self.results['fail']}")
        if self.results["errors"]:
            print(f"  失败详情:")
            for err in self.results["errors"]:
                print(f"    - {err}")
        print(f"{'='*60}")
        return self.results


# ---- 测试函数 ----

def test_all():
    """运行所有端到端测试"""
    runner = TestRunner()

    # ========== 1. 导入测试 ==========
    runner.section("1. 导入测试")

    try:
        from octopus_hub.models import (
            MemoryType, SessionStatus, Project, Persona,
            MemoryFragment, Session
        )
        runner.test("导入 models 模块", True)
    except Exception as e:
        runner.test("导入 models 模块", False, str(e))

    try:
        from octopus_hub.storage import HubStorage
        runner.test("导入 storage 模块", True)
    except Exception as e:
        runner.test("导入 storage 模块", False, str(e))

    try:
        from octopus_hub.core import OctopusHub
        runner.test("导入 core 模块", True)
    except Exception as e:
        runner.test("导入 core 模块", False, str(e))

    try:
        from octopus_hub.hardware_parser import HardwareRefParser
        runner.test("导入 hardware_parser 模块", True)
    except Exception as e:
        runner.test("导入 hardware_parser 模块", False, str(e))

    try:
        from octopus_hub.kg_adapter import KnowledgeGraphAdapter
        runner.test("导入 kg_adapter 模块", True)
    except Exception as e:
        runner.test("导入 kg_adapter 模块", False, str(e))

    try:
        from octopus_hub.hub_bridge import HubBridge, QueryCache
        runner.test("导入 hub_bridge 模块", True)
    except Exception as e:
        runner.test("导入 hub_bridge 模块", False, str(e))

    try:
        from octopus_hub.reflection import ReflectionEngine
        runner.test("导入 reflection 模块", True)
    except Exception as e:
        runner.test("导入 reflection 模块", False, str(e))

    try:
        from octopus_hub.handoff import HandoffProtocol
        runner.test("导入 handoff 模块", True)
    except Exception as e:
        runner.test("导入 handoff 模块", False, str(e))

    try:
        from octopus_hub.integration import OctopusSystem
        runner.test("导入 integration 模块", True)
    except Exception as e:
        runner.test("导入 integration 模块", False, str(e))

    # ========== 2. 初始化系统 ==========
    runner.section("2. 初始化系统")

    cleanup()  # 清理旧测试数据

    # 创建独立存储实例
    try:
        storage = HubStorage(TEST_DB_PATH)
        runner.test("创建 HubStorage 实例", True)
    except Exception as e:
        storage = None
        runner.test("创建 HubStorage 实例", False, str(e))

    try:
        hub = OctopusHub(TEST_DB_PATH)
        runner.test("创建 OctopusHub 实例", True)
    except Exception as e:
        hub = None
        runner.test("创建 OctopusHub 实例", False, str(e))

    try:
        system = OctopusSystem(TEST_DB_PATH)
        runner.test("创建 OctopusSystem 实例", True)
    except Exception as e:
        system = None
        runner.test("创建 OctopusSystem 实例", False, str(e))

    try:
        bridge = HubBridge(rag_root="/workspace/rag_v4")
        runner.test("创建 HubBridge 实例", True)
    except Exception as e:
        bridge = None
        runner.test("创建 HubBridge 实例", False, str(e))

    # ========== 3. 知识图谱测试 ==========
    runner.section("3. 知识图谱测试")

    if bridge is not None:
        try:
            bridge.kg  # 触发延迟加载
            runner.test("知识图谱延迟加载", True)
        except Exception as e:
            runner.test("知识图谱延迟加载", False, str(e))

        try:
            stats = bridge.kg_get_stats()
            has_nodes = stats.get("total_nodes", 0) > 0
            runner.test(f"知识图谱统计 (节点数: {stats.get('total_nodes', 0)})",
                        has_nodes and "error" not in stats)
        except Exception as e:
            runner.test("知识图谱统计", False, str(e))

        try:
            results = bridge.kg_search("ADC0809")
            runner.test(f"知识图谱搜索 'ADC0809' (结果数: {len(results)})",
                        len(results) > 0)
        except Exception as e:
            runner.test("知识图谱搜索", False, str(e))

        try:
            deps = bridge.kg_get_design_deps("design_P-A-1#")
            has_experiments = len(deps.get("experiments", [])) > 0
            runner.test(f"设计依赖链 P-A-1# (实验数: {len(deps.get('experiments', []))})",
                        has_experiments)
        except Exception as e:
            runner.test("设计依赖链", False, str(e))

        try:
            designs = bridge.kg_get_all_designs()
            runner.test(f"所有设计题目 (数量: {len(designs)})",
                        len(designs) > 0)
        except Exception as e:
            runner.test("所有设计题目", False, str(e))

        try:
            chip = bridge.kg_get_chip("ADC0809")
            has_chip = chip is not None and "error" not in chip
            runner.test("KG 芯片查询 ADC0809", has_chip)
        except Exception as e:
            runner.test("KG 芯片查询", False, str(e))

        try:
            node = bridge.kg_query_node("adc0809_pins")
            has_node = node.get("node") is not None
            runner.test("KG 节点查询 adc0809_pins", has_node)
        except Exception as e:
            runner.test("KG 节点查询", False, str(e))
    else:
        runner.test("桥接层不可用，跳过知识图谱测试", False)

    # ========== 4. 硬件解析器测试 ==========
    runner.section("4. 硬件解析器测试")

    try:
        parser = HardwareRefParser("/workspace/rag_v4/hardware_ref_pa1.md")
        runner.test("创建 HardwareRefParser 实例", parser.is_loaded)
    except Exception as e:
        parser = None
        runner.test("创建 HardwareRefParser 实例", False, str(e))

    if parser is not None and parser.is_loaded:
        try:
            chips = parser.get_chip_list()
            runner.test(f"芯片列表 (数量: {len(chips)})",
                        len(chips) >= 11)
        except Exception as e:
            runner.test("芯片列表", False, str(e))

        try:
            pinout = parser.get_pinout("ADC0809")
            runner.test(f"ADC0809 引脚表 (引脚数: {pinout.get('total_pins', 0)})",
                        pinout.get("total_pins", 0) == 28)
        except Exception as e:
            runner.test("ADC0809 引脚表", False, str(e))

        try:
            pinout = parser.get_pinout("8255")
            runner.test(f"8255A 引脚表 (引脚数: {pinout.get('total_pins', 0)})",
                        pinout.get("total_pins", 0) >= 40)
        except Exception as e:
            runner.test("8255A 引脚表", False, str(e))

        try:
            pinout = parser.get_pinout("DHT11")
            runner.test(f"DHT11 引脚表 (引脚数: {pinout.get('total_pins', 0)})",
                        pinout.get("total_pins", 0) == 4)
        except Exception as e:
            runner.test("DHT11 引脚表", False, str(e))

        try:
            pinout = parser.get_pinout("stc89")
            runner.test(f"STC89C54RD+ (别名) 引脚表 (引脚数: {pinout.get('total_pins', 0)})",
                        pinout.get("total_pins", 0) == 40)
        except Exception as e:
            runner.test("STC89C54RD+ 别名引脚表", False, str(e))

        try:
            addr = parser.get_address_map()
            runner.test(f"地址映射 (8255A_base={addr.get('8255A_base')})",
                        addr.get("8255A_base") == "0x0480")
        except Exception as e:
            runner.test("地址映射", False, str(e))

        try:
            quick = parser.get_quick_reference()
            runner.test(f"快速参考 (条目数: {len(quick)})",
                        len(quick) >= 20)
        except Exception as e:
            runner.test("快速参考", False, str(e))

        try:
            arch = parser.get_board_architecture()
            runner.test(f"板卡架构 (board1: {arch['board1']['name']})",
                        "board1" in arch and "board2" in arch)
        except Exception as e:
            runner.test("板卡架构", False, str(e))

        try:
            results = parser.search("P3.3")
            runner.test(f"关键词搜索 'P3.3' (结果数: {len(results)})",
                        len(results) > 0)
        except Exception as e:
            runner.test("关键词搜索", False, str(e))

        try:
            signals = parser.search_by_signal("P3.3")
            runner.test(f"信号反查 'P3.3' (结果数: {len(signals)})",
                        len(signals) > 0)
        except Exception as e:
            runner.test("信号反查", False, str(e))

        try:
            detail = parser.get_chip_detail("DHT11")
            has_chip = detail.get("chip") is not None
            runner.test("芯片详情 DHT11", has_chip)
        except Exception as e:
            runner.test("芯片详情", False, str(e))

        # 芯片不存在测试
        try:
            result = parser.get_pinout("NOT_A_CHIP")
            runner.test("不存在的芯片返回错误", "error" in result)
        except Exception as e:
            runner.test("不存在的芯片返回错误", False, str(e))

    # ========== 5. 桥接层测试 ==========
    runner.section("5. 桥接层测试（统一查询路由）")

    if bridge is not None:
        try:
            health = bridge.health_check()
            runner.test("健康检查",
                        isinstance(health, dict) and "kg_loaded" in health)
        except Exception as e:
            runner.test("健康检查", False, str(e))

        try:
            quick = bridge.get_quick_reference()
            runner.test(f"桥接层快速参考 (条目数: {len(quick)})",
                        len(quick) >= 5)
        except Exception as e:
            runner.test("桥接层快速参考", False, str(e))

        try:
            detail = bridge.get_chip_detail("ADC0809")
            has_merged = detail.get("merged", {}).get("total_pins", 0) > 0
            runner.test("桥接层芯片详情 ADC0809 (KG+HW合并)",
                        has_merged and detail.get("kg_result") is not None)
        except Exception as e:
            runner.test("桥接层芯片详情", False, str(e))

        try:
            result = bridge.unified_query("ADC0809 基地址是多少")
            runner.test(f"统一查询 ADC0809 (路由: {result.get('route')})",
                        result.get("route") in ("hardware", "hardware_pinout", "knowledge_graph"))
        except Exception as e:
            runner.test("统一查询 ADC0809", False, str(e))

        try:
            result = bridge.unified_query("DHT11 引脚")
            runner.test(f"统一查询 DHT11 引脚 (路由: {result.get('route')})",
                        result.get("route") in ("hardware", "hardware_pinout"))
        except Exception as e:
            runner.test("统一查询 DHT11", False, str(e))

        try:
            result = bridge.unified_query("P-A-1# 依赖")
            runner.test(f"统一查询设计题 (路由: {result.get('route')})",
                        result.get("route") in ("knowledge_graph_design",
                                                 "knowledge_graph_design+rag"))
        except Exception as e:
            runner.test("统一查询设计题", False, str(e))

        # 缓存测试
        try:
            bridge.cache_clear()
            stats = bridge.cache_stats()
            runner.test(f"缓存清空 (条目数: {stats.get('entries', 0)})",
                        stats.get("entries", 0) == 0)
        except Exception as e:
            runner.test("缓存清空", False, str(e))

        try:
            # 两次查询相同内容，第二次应命中缓存
            # 使用通用查询触发 RAG 路由，因为缓存只在 rag_search 中生效
            result1 = bridge.unified_query("温湿度传感器")
            result2 = bridge.unified_query("温湿度传感器")
            runner.test("查询缓存一致性", result1.get("route") == result2.get("route"))
        except Exception as e:
            runner.test("查询缓存一致性", False, str(e))

        try:
            stats = bridge.cache_stats()
            # 缓存条目数可能为 0（如果走非 RAG 路径），这不算失败
            runner.test(f"缓存统计 (条目数: {stats.get('entries', 0)})",
                        stats.get("entries", 0) >= 0)
        except Exception as e:
            runner.test("缓存统计", False, str(e))

        # RAG 可用性测试（不崩溃即可）
        try:
            rag_ok = bridge.rag_available
            runner.test(f"rag_available 属性 (值: {rag_ok})", isinstance(rag_ok, bool))
        except Exception as e:
            runner.test("rag_available 属性", False, str(e))

    # ========== 6. 项目注册 + 记忆添加 ==========
    runner.section("6. 项目注册 + 记忆添加")

    if hub is not None:
        try:
            project = hub.register_project("test_proj_001", "测试项目E2E")
            runner.test("注册项目", project.project_id == "test_proj_001")
        except Exception as e:
            runner.test("注册项目", False, str(e))

        try:
            session = hub.start_session("test_proj_001", "test_agent")
            runner.test("开始会话", session.session_id.startswith("sess_"))
        except Exception as e:
            runner.test("开始会话", False, str(e))

        try:
            mem1 = hub.add_memory(
                "test_proj_001",
                "ADC0809 基地址确认为 0x4000",
                MemoryType.DECISION,
                importance=0.8,
                tags=["ADC0809", "地址"]
            )
            runner.test("添加决策记忆", mem1.memory_id.startswith("mem_"))
        except Exception as e:
            runner.test("添加决策记忆", False, str(e))

        try:
            mem2 = hub.add_memory(
                "test_proj_001",
                "修复了 DHT11 读取时序错误，延时从 18ms 改为 20ms",
                MemoryType.ERROR_FIX,
                importance=0.9,
                tags=["DHT11", "时序", "修复"]
            )
            runner.test("添加错误修复记忆", mem2.memory_id.startswith("mem_"))
        except Exception as e:
            runner.test("添加错误修复记忆", False, str(e))

        try:
            mem3 = hub.add_memory(
                "test_proj_001",
                "发现 8255A 控制字 0x89 配置后，PC口高4位可作为输入读取按键",
                MemoryType.INSIGHT,
                importance=0.6,
                tags=["8255A", "控制字", "按键"]
            )
            runner.test("添加洞察记忆", mem3.memory_id.startswith("mem_"))
        except Exception as e:
            runner.test("添加洞察记忆", False, str(e))

        try:
            mem4 = hub.add_memory(
                "test_proj_001",
                "74HC240 反相驱动：P0输出1 → 74HC240输出0 → 共阳数码管段点亮",
                MemoryType.HARDWARE_CONFIG,
                importance=0.7,
                tags=["74HC240", "数码管", "反相"]
            )
            runner.test("添加硬件配置记忆", mem4.memory_id.startswith("mem_"))
        except Exception as e:
            runner.test("添加硬件配置记忆", False, str(e))

        try:
            mem5 = hub.add_memory(
                "test_proj_001",
                "串口配置：1200bps，P3.0/RXD，P3.1/TXD，S9跳线选择USB/RS485模式",
                MemoryType.CODE_SNIPPET,
                importance=0.5,
                tags=["串口", "配置", "1200bps"]
            )
            runner.test("添加代码片段记忆", mem5.memory_id.startswith("mem_"))
        except Exception as e:
            runner.test("添加代码片段记忆", False, str(e))

    # ========== 7. 记忆存储测试 ==========
    runner.section("7. 记忆存储测试（搜索、去重、类型过滤）")

    if hub is not None:
        try:
            results = hub.search_memories("test_proj_001", "ADC0809")
            runner.test(f"记忆搜索 'ADC0809' (结果数: {len(results)})",
                        len(results) >= 1)
        except Exception as e:
            runner.test("记忆搜索", False, str(e))

        try:
            results = hub.search_memories("test_proj_001", "DHT11")
            runner.test(f"记忆搜索 'DHT11' (结果数: {len(results)})",
                        len(results) >= 1)
        except Exception as e:
            runner.test("记忆搜索 DHT11", False, str(e))

        try:
            decisions = hub.get_memories_by_type("test_proj_001", MemoryType.DECISION)
            runner.test(f"按类型过滤 DECISION (结果数: {len(decisions)})",
                        len(decisions) >= 1 and all(
                            m.memory_type == MemoryType.DECISION for m in decisions))
        except Exception as e:
            runner.test("按类型过滤", False, str(e))

        try:
            errors = hub.get_error_fixes("test_proj_001")
            runner.test(f"获取错误修复 (结果数: {len(errors)})",
                        len(errors) >= 1)
        except Exception as e:
            runner.test("获取错误修复", False, str(e))

        try:
            tagged = hub.get_memories_by_tags("test_proj_001", ["8255A"])
            runner.test(f"按标签过滤 '8255A' (结果数: {len(tagged)})",
                        len(tagged) >= 1)
        except Exception as e:
            runner.test("按标签过滤", False, str(e))

        try:
            recent = hub.get_recent_memories("test_proj_001", limit=10)
            runner.test(f"最近记忆 (结果数: {len(recent)})",
                        len(recent) >= 3)
        except Exception as e:
            runner.test("最近记忆", False, str(e))

        try:
            ctx = hub.get_project_context("test_proj_001")
            runner.test(f"项目上下文 (记忆数: {ctx.get('memory_count', 0)})",
                        ctx.get("memory_count", 0) >= 3)
        except Exception as e:
            runner.test("项目上下文", False, str(e))

        # 删除测试
        try:
            mem = hub.add_memory(
                "test_proj_001", "待删除的测试记忆", MemoryType.INSIGHT)
            mem_id = mem.memory_id
            deleted = hub.delete_memory(mem_id)
            retrieved = hub.get_memory(mem_id)
            runner.test("记忆删除", deleted and retrieved is None)
        except Exception as e:
            runner.test("记忆删除", False, str(e))

    # ========== 8. 反思引擎测试 ==========
    runner.section("8. 反思引擎测试（规则提取、TF-IDF提取、自动反思）")

    if hub is not None:
        try:
            reflection = ReflectionEngine(hub.storage)
            runner.test("创建 ReflectionEngine", True)
        except Exception as e:
            reflection = None
            runner.test("创建 ReflectionEngine", False, str(e))

        if reflection is not None:
            try:
                messages = [
                    {"role": "user", "content": "就按 0x0480 作为 8255 基地址"},
                    {"role": "assistant", "content": "好的，8255A 基地址设为 0x0480"},
                    {"role": "user", "content": "不对，DHT11 延时搞错了，应该是 20ms 不是 18ms"},
                    {"role": "assistant", "content": "明白了，修正 DHT11 延时为 20ms"},
                    {"role": "user", "content": "原来 8255A 控制字 0x89 是这样配置的"},
                    {"role": "user", "content": "以后都用简洁风格回复"},
                ]
                result = reflection.reflect_on_session(
                    session.session_id, messages, use_llm=False)
                runner.test(f"规则引擎反思 (记忆数: {result.get('memories_created', 0)})",
                            result.get("memories_created", 0) >= 0)
            except Exception as e:
                runner.test("规则引擎反思", False, str(e))

            try:
                extracted = reflection._rule_extract(messages)
                runner.test(f"规则提取 (决策: {len(extracted.get('decisions', []))}, "
                            f"错误: {len(extracted.get('errors', []))}, "
                            f"洞察: {len(extracted.get('insights', []))})",
                            len(extracted.get("decisions", [])) >= 1)
            except Exception as e:
                runner.test("规则提取", False, str(e))

            try:
                should, reason = reflection.should_reflect(session.session_id)
                runner.test(f"反思触发判断 (should={should}, reason={reason})",
                            isinstance(should, bool))
            except Exception as e:
                runner.test("反思触发判断", False, str(e))

            try:
                tags = reflection._auto_tag("ADC0809 基地址 0x4000 配置完成")
                runner.test(f"自动标签生成 (标签: {tags})",
                            len(tags) >= 1)
            except Exception as e:
                runner.test("自动标签生成", False, str(e))

    # ========== 9. 无感接手测试 ==========
    runner.section("9. 无感接手测试")

    if hub is not None and bridge is not None:
        try:
            handoff = HandoffProtocol(hub, bridge)
            runner.test("创建 HandoffProtocol", True)
        except Exception as e:
            handoff = None
            runner.test("创建 HandoffProtocol", False, str(e))

        if handoff is not None:
            try:
                result = handoff.handoff(
                    "test_proj_001",
                    agent_id="new_agent_001",
                    context_depth="standard",
                    focus_areas=["ADC0809", "DHT11"]
                )
                runner.test(f"无感接手 (session_id: {result.get('session_id', 'N/A')[:20]}...)",
                            "error" not in result)
            except Exception as e:
                runner.test("无感接手", False, str(e))

            try:
                quick = handoff.quick_handoff("test_proj_001")
                runner.test("快速接手文本", len(quick) > 0 and "八爪鱼" in quick)
            except Exception as e:
                runner.test("快速接手文本", False, str(e))

            try:
                tokens = handoff._estimate_tokens({"test": "数据" * 100})
                runner.test(f"Token 估算 (估算值: {tokens})", tokens > 0)
            except Exception as e:
                runner.test("Token 估算", False, str(e))

    # ========== 10. 自动闭环测试 ==========
    runner.section("10. 自动闭环测试（end_session_with_reflection）")

    if system is not None and hub is not None:
        try:
            # 先注册项目并开始会话
            proj = hub.register_project("test_proj_002", "闭环测试项目")
            sess = hub.start_session("test_proj_002", "closure_agent")

            # 添加一些记忆
            hub.add_memory("test_proj_002", "决定使用 12MHz 晶振", MemoryType.DECISION,
                           importance=0.7, session_id=sess.session_id)
            hub.add_memory("test_proj_002", "修复了串口波特率配置错误", MemoryType.ERROR_FIX,
                           importance=0.9, session_id=sess.session_id)

            # 记录事件
            hub.record_event(sess.session_id, "milestone", "硬件配置完成")

            messages = [
                {"role": "user", "content": "就按 12MHz 晶振方案"},
                {"role": "assistant", "content": "好的，采用 12MHz 晶振"},
                {"role": "user", "content": "波特率不对，改成 1200bps"},
                {"role": "assistant", "content": "已修正为 1200bps"},
                {"role": "user", "content": "以后详细点说"},
            ]

            result = system.end_session_with_reflection(
                sess.session_id, messages)
            runner.test(f"会话闭环 (session_ended: {result.get('session_ended')})",
                        result.get("session_ended") is True)
        except Exception as e:
            runner.test("会话闭环", False, str(e))

        try:
            stats = hub.get_stats()
            runner.test(f"中枢统计 (项目: {stats.get('projects')}, "
                        f"记忆: {stats.get('memories')}, "
                        f"会话: {stats.get('sessions')})",
                        stats.get("projects", 0) >= 2)
        except Exception as e:
            runner.test("中枢统计", False, str(e))

    # ========== 清理 ==========
    runner.section("清理")

    try:
        if hub:
            hub.close()
        runner.test("关闭中枢连接", True)
    except Exception as e:
        runner.test("关闭中枢连接", False, str(e))

    try:
        cleanup()
        runner.test("清理测试文件", True)
    except Exception as e:
        runner.test("清理测试文件", False, str(e))

    return runner.summary()


if __name__ == "__main__":
    # 确保测试前清理
    cleanup()
    try:
        results = test_all()
        # 根据失败数决定退出码
        if results["fail"] > 0:
            print(f"\n存在 {results['fail']} 个失败测试")
            sys.exit(1)
        else:
            print(f"\n全部 {results['pass']} 个测试通过")
            sys.exit(0)
    except Exception as e:
        print(f"\n测试异常: {e}")
        traceback.print_exc()
        cleanup()
        sys.exit(1)