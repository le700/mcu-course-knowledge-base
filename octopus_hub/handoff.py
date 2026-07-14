import time
from typing import List, Dict, Optional
from .models import Session, SessionStatus, MemoryType
from .reflection import ReflectionEngine


class HandoffProtocol:
    """无感接手协议 - 智能体上下文注入"""

    def __init__(self, hub, bridge=None):
        """
        Args:
            hub: OctopusHub 实例
            bridge: HubBridge 实例（可选）
        """
        self.hub = hub
        self.bridge = bridge
        self.reflection = ReflectionEngine(hub.storage)

    def handoff(self, project_id: str, agent_id: str = "unknown",
                context_depth: str = "standard",
                focus_areas: List[str] = None,
                previous_agent_id: str = None) -> dict:
        """
        无感接手：根据项目名返回完整上下文包

        Args:
            project_id: 项目ID（如 "P-A-1"）
            agent_id: 当前智能体标识
            context_depth: 上下文深度 - "minimal" | "standard" | "full"
            focus_areas: 关注领域（如 ["ADC0809", "DHT11"]）
            previous_agent_id: 上一个智能体ID（如果已知）

        Returns:
            {
                "session_id": str,
                "context_package": {
                    "project_snapshot": {...},
                    "persona_profile": {...},
                    "active_session_context": {...},
                    "rag_context": {...}
                },
                "instructions": {
                    "greeting": str,
                    "suggested_first_action": str
                }
            }
        """
        # 1. 路由到项目
        project = self.hub.storage.get_project(project_id)
        if not project:
            return {
                "error": f"项目 {project_id} 不存在",
                "suggestion": "请先注册项目：hub.project.register <id> <name>"
            }

        # 2. 获取/创建会话
        active_session = self.hub.storage.get_active_session(project_id)
        is_resuming = active_session is not None

        if active_session and active_session.agent_id != agent_id:
            # 不同智能体接手：先增量提炼，再创建新会话
            if active_session.message_count > 5:
                self.reflection.incremental_reflect(
                    active_session.session_id, [])
            active_session.status = SessionStatus.PAUSED
            self.hub.storage.update_session(active_session)
            active_session = None
            is_resuming = False

        if not active_session:
            active_session = self.hub.start_session(project_id, agent_id)

        # 3. 组装上下文包
        context_package = self._build_context_package(
            project, active_session, context_depth, focus_areas, is_resuming)

        # 4. 生成接手指令
        instructions = self._build_instructions(
            project, is_resuming, previous_agent_id, focus_areas)

        # 5. 记录上下文包到会话
        active_session.context_package = context_package
        self.hub.storage.update_session(active_session)

        return {
            "session_id": active_session.session_id,
            "project_id": project_id,
            "agent_id": agent_id,
            "is_resuming": is_resuming,
            "context_depth": context_depth,
            "context_package": context_package,
            "instructions": instructions,
            "estimated_tokens": self._estimate_tokens(context_package)
        }

    def _build_context_package(self, project, session, depth: str,
                                focus_areas: List[str], is_resuming: bool) -> dict:
        """构建上下文包"""
        persona = self.hub.storage.get_persona_by_project(project.project_id)

        package = {
            "project_snapshot": {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "status": project.status,
                "workspace_path": project.workspace_path,
                "context_summary": project.context_snapshot or self._auto_summary(project),
                "key_decisions": project.key_decisions[-5:] if project.key_decisions else [],
                "rag_tags": project.rag_structured_tags
            },
            "persona_profile": {
                "style": persona.style_preferences.get("verbosity", "concise") if persona else "concise",
                "code_style": persona.style_preferences.get("code_style", "descriptive") if persona else "descriptive",
                "language": persona.style_preferences.get("response_language", "zh-CN") if persona else "zh-CN",
                "version": persona.version if persona else 1
            } if persona else {},
            "active_session_context": {
                "session_id": session.session_id,
                "is_resuming": is_resuming,
                "message_count": session.message_count,
                "recent_memories": [],
                "pending_issues": []
            },
            "rag_context": {
                "preloaded_nodes": [],
                "quick_lookup": {}
            }
        }

        # 添加最近记忆
        if depth in ("standard", "full"):
            memories = self.hub.storage.get_memories_by_project(
                project.project_id, limit=20)
            package["active_session_context"]["recent_memories"] = [
                {
                    "memory_id": m.memory_id,
                    "type": m.memory_type.value,
                    "content": m.content[:200],
                    "importance": m.importance,
                    "tags": m.tags
                }
                for m in memories[:10]
            ]

            # 未解决问题
            open_issues = [m for m in memories if m.memory_type == MemoryType.ERROR_FIX
                          and m.importance > 0.7]
            package["active_session_context"]["pending_issues"] = [
                m.content[:200] for m in open_issues[:3]
            ]

        # 添加 RAG 预加载
        if depth in ("standard", "full") and self.bridge:
            try:
                # 预加载项目关联的知识图谱节点
                if project.knowledge_graph_node_ids:
                    for nid in project.knowledge_graph_node_ids[:5]:
                        node = self.bridge.kg.get_node(nid)
                        if node:
                            package["rag_context"]["preloaded_nodes"].append({
                                "node_id": nid,
                                "type": node.get("type", ""),
                                "label": node.get("label", ""),
                                "summary": str(node)[:200]
                            })

                # 快速查找表
                if focus_areas:
                    for area in focus_areas:
                        chip = self.bridge.kg_get_chip(area)
                        if chip and "error" not in chip:
                            # 提取关键信息
                            label = chip.get("label", "")
                            pins = chip.get("pins_summary", "")
                            base = chip.get("base_address", "")
                            ctrl = chip.get("control_word", "")
                            info = f"{label}"
                            if base:
                                info += f", 地址: {base}"
                            if ctrl:
                                info += f", 控制字: {ctrl}"
                            if pins:
                                info += f", 引脚: {pins}"
                            package["rag_context"]["quick_lookup"][area] = info
            except Exception as e:
                package["rag_context"]["error"] = str(e)

        return package

    def _build_instructions(self, project, is_resuming: bool,
                            previous_agent_id: str, focus_areas: List[str]) -> dict:
        """生成接手指令"""
        if is_resuming:
            greeting = f"你正在继续 {project.project_name} 项目的工作。"
            if focus_areas:
                greeting += f"当前关注领域：{', '.join(focus_areas)}。"
        else:
            greeting = f"你正在接手 {project.project_name} 项目。"
            if previous_agent_id:
                greeting += f"上一阶段由 {previous_agent_id} 完成。"
            if focus_areas:
                greeting += f"请关注以下领域：{', '.join(focus_areas)}。"

        # 建议第一步
        recent_memories = self.hub.storage.get_memories_by_project(
            project.project_id, limit=5)
        suggested_action = "查看项目上下文，了解当前进度"
        if recent_memories:
            last_memory = recent_memories[0]
            if last_memory.memory_type == MemoryType.ERROR_FIX:
                suggested_action = f"检查是否已修复：{last_memory.content[:100]}"
            elif last_memory.memory_type == MemoryType.DECISION:
                suggested_action = f"基于最近决策开展工作：{last_memory.content[:100]}"

        return {
            "greeting": greeting,
            "suggested_first_action": suggested_action,
            "workspace_path": project.workspace_path,
            "project_id": project.project_id
        }

    def _auto_summary(self, project) -> str:
        """自动生成项目摘要"""
        memories = self.hub.storage.get_memories_by_project(
            project.project_id, limit=20)
        if not memories:
            return f"项目 {project.project_name}，暂无历史记录"

        # 按类型统计
        type_counts = {}
        for m in memories:
            t = m.memory_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        parts = [f"项目 {project.project_name}"]
        parts.append(f"共 {len(memories)} 条记忆")
        for t, c in type_counts.items():
            type_names = {
                "decision": "决策", "insight": "洞察", "error_fix": "错误修正",
                "code_snippet": "代码片段", "hardware_config": "硬件配置",
                "rag_query": "知识查询", "reflection": "反思"
            }
            parts.append(f"{type_names.get(t, t)}: {c}")

        return " | ".join(parts)

    def _estimate_tokens(self, context_package: dict) -> int:
        """估算上下文包的 token 数（粗略：中文 1.5 字/token，英文 0.75 词/token）"""
        import json
        text = json.dumps(context_package, ensure_ascii=False, default=str)
        # 粗略估算：中文字符约 1.5 字/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)

    def quick_handoff(self, project_id: str) -> str:
        """
        快速接手：返回一段精简的上下文文本，可直接注入到智能体的 system prompt
        """
        result = self.handoff(project_id, context_depth="minimal")
        if "error" in result:
            return f"[八爪鱼中枢] 项目 {project_id} 未注册"

        pkg = result["context_package"]
        proj = pkg["project_snapshot"]
        pers = pkg["persona_profile"]

        lines = [
            f"[八爪鱼中枢] 项目: {proj['project_id']} - {proj['project_name']}",
            f"状态: {proj['status']} | 工作区: {proj['workspace_path']}",
            f"上下文: {proj['context_summary']}",
        ]

        if pers:
            lines.append(f"风格: {pers.get('style', 'concise')} | 语言: {pers.get('language', 'zh-CN')}")

        mems = pkg.get("active_session_context", {}).get("recent_memories", [])
        if mems:
            lines.append(f"最近记忆 ({len(mems)} 条):")
            for m in mems[:3]:
                lines.append(f"  [{m['type']}] {m['content'][:100]}")

        return '\n'.join(lines)