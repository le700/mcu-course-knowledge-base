"""
八爪鱼记忆中枢 - 整合模块
统一入口，将核心、桥接、反思、接手协议整合
"""

import json
import os
from typing import List, Dict, Optional
from .core import OctopusHub
from .reflection import ReflectionEngine
from .handoff import HandoffProtocol
from .models import MemoryType, SessionStatus


class OctopusSystem:
    """八爪鱼记忆中枢 - 完整系统"""

    def __init__(self, storage_path: str = "/workspace/octopus_hub/hub.db",
                 rag_root: str = "/workspace/rag_v4"):
        self.hub = OctopusHub(storage_path)
        self.reflection = ReflectionEngine(self.hub.storage)

        # 延迟加载桥接
        self._bridge = None
        self._rag_root = rag_root
        self._handoff = None
        self._vector_store = None

    @property
    def bridge(self):
        if self._bridge is None:
            try:
                from .hub_bridge import HubBridge
                self._bridge = HubBridge(rag_root=self._rag_root)
            except ImportError:
                self._bridge = None
        return self._bridge

    @property
    def handoff(self):
        if self._handoff is None:
            self._handoff = HandoffProtocol(self.hub, self.bridge)
        return self._handoff

    @property
    def vector_store(self):
        if self._vector_store is None:
            try:
                from .memory_vector_store import MemoryVectorStore
                self._vector_store = MemoryVectorStore()
            except Exception:
                self._vector_store = None
        return self._vector_store

    # ---- 快捷方法 ----

    def register_project(self, project_id: str, project_name: str,
                         workspace_path: str = "", **kwargs):
        """注册项目并自动绑定知识图谱"""
        project = self.hub.register_project(project_id, project_name,
                                             workspace_path, **kwargs)

        # 尝试自动绑定知识图谱节点
        if self.bridge:
            try:
                design_node = self.bridge.kg.get_node(f"design_{project_id}")
                if design_node:
                    project.knowledge_graph_node_ids = [project_id]
                    # 获取依赖
                    deps = self.bridge.kg_get_design_deps(f"design_{project_id}")
                    if "hardware_boards" in deps:
                        for hw in deps["hardware_boards"]:
                            project.knowledge_graph_node_ids.append(hw["id"])
                    if "peripherals" in deps:
                        project.rag_structured_tags = {
                            "peripherals": [p.get("label", "") for p in deps["peripherals"]]
                        }
                    self.hub.storage.update_project(project)
            except Exception:
                pass

        return project

    def get_context(self, project_id: str, agent_id: str = "unknown",
                    depth: str = "standard", focus: List[str] = None) -> dict:
        """获取项目上下文（无感接手）"""
        return self.handoff.handoff(project_id, agent_id, depth, focus)

    def quick_context(self, project_id: str) -> str:
        """快速上下文文本"""
        return self.handoff.quick_handoff(project_id)

    def add_memory(self, project_id: str, content: str,
                   mem_type: str = "insight", importance: float = 0.5,
                   tags: List[str] = None) -> dict:
        """添加记忆"""
        try:
            mt = MemoryType(mem_type)
        except ValueError:
            mt = MemoryType.INSIGHT

        memory = self.hub.add_memory(project_id, content, mt, importance, tags)

        # 如果向量存储可用，同时加入向量存储
        vs = self.vector_store
        if vs is not None:
            try:
                vs.add_memory(memory)
            except Exception:
                pass

        return memory.to_dict()

    def reflect_session(self, session_id: str,
                        messages: List[dict] = None) -> dict:
        """反思会话"""
        return self.reflection.reflect_on_session(session_id, messages)

    def search_knowledge(self, query: str, project_id: str = "default") -> dict:
        """统一知识查询"""
        if self.bridge:
            return self.bridge.unified_query(query, project_id)
        return {"error": "桥接层未加载"}

    def get_stats(self) -> dict:
        """系统统计"""
        stats = self.hub.get_stats()
        if self.bridge:
            try:
                stats["knowledge_graph"] = self.bridge.kg_get_stats()
            except Exception:
                stats["knowledge_graph"] = {"status": "unavailable"}
        if self._bridge:
            stats["bridge_cache"] = self.bridge.cache_stats()
        return stats

    def health_check(self) -> dict:
        """健康检查"""
        result = {
            "hub": "ok",
            "storage": "ok",
            "reflection": "ok",
            "handoff": "ok",
        }
        if self.bridge:
            try:
                result["bridge"] = self.bridge.health_check()
            except Exception as e:
                result["bridge"] = {"error": str(e)}
        else:
            result["bridge"] = {"status": "not_loaded"}
        return result

    def end_session_with_reflection(self, session_id: str,
                                     messages: List[dict] = None) -> dict:
        """
        结束会话并自动触发反思闭环。

        流程：
        1. 获取会话信息
        2. 调用 auto_reflect 进行反思
        3. 结束会话
        4. 更新项目 context_snapshot
        5. 返回完整的反思结果 + 项目状态
        """
        # 1. 获取会话信息
        session = self.hub.storage.get_session(session_id)
        if not session:
            return {"error": f"会话 {session_id} 不存在"}

        project_id = session.project_id

        # 2. 调用 auto_reflect 进行反思
        vs = self.vector_store
        auto_result = self.reflection.auto_reflect(
            session_id, messages, vector_store=vs)

        # 3. 结束会话
        ended_session = self.hub.end_session(session_id)

        # 4. 更新项目 context_snapshot
        try:
            project = self.hub.storage.get_project(project_id)
            if project:
                import json
                import time
                existing_snapshot = {}
                if project.context_snapshot:
                    try:
                        existing_snapshot = json.loads(project.context_snapshot)
                    except (json.JSONDecodeError, TypeError):
                        existing_snapshot = {}
                existing_snapshot.update({
                    "last_reflection": time.time(),
                    "last_session_id": session_id,
                    "reflection_summary": auto_result.get("result", {}).get("reflection_summary", "") if auto_result.get("result") else "",
                    "memories_count": auto_result.get("result", {}).get("memories_created", 0) if auto_result.get("result") else 0
                })
                project.context_snapshot = json.dumps(existing_snapshot, ensure_ascii=False)
                self.hub.storage.update_project(project)
        except Exception:
            pass

        # 5. 返回完整结果
        return {
            "session_id": session_id,
            "session_ended": ended_session is not None,
            "reflection": auto_result.get("result"),
            "reflected": auto_result.get("reflected", False),
            "reason": auto_result.get("reason", ""),
            "project_id": project_id
        }

    def semantic_search_memories(self, project_id: str, query: str,
                                  top_k: int = 10) -> List[dict]:
        """语义搜索记忆，返回最匹配的记忆列表"""
        vs = self.vector_store
        if vs is None:
            return []
        try:
            results = vs.semantic_search(query, project_id=project_id, top_k=top_k)
            return results[:top_k]
        except Exception:
            return []

    def get_memory_clusters(self, project_id: str) -> List[dict]:
        """对项目记忆聚类，返回各簇的摘要"""
        vs = self.vector_store
        if vs is None:
            return []
        try:
            clusters = vs.cluster_memories(project_id)
            return clusters
        except Exception:
            return []

    def close(self):
        self.hub.close()