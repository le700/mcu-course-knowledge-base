"""
八爪鱼记忆中枢 - 核心 API

提供项目管理、会话管理、记忆管理、人格管理等高层业务逻辑。
封装了存储层的细节，提供简洁易用的编程接口。
"""

from typing import List, Dict, Optional
from .models import Project, Persona, MemoryFragment, Session, MemoryType, SessionStatus
from .storage import HubStorage
import uuid
import time


class OctopusHub:
    """八爪鱼记忆中枢 - 核心 API

    中枢系统的顶层入口，负责协调项目管理、会话追踪、记忆存取和人格建模。
    用户通过此类与中枢系统交互，无需直接操作存储层。

    Usage:
        hub = OctopusHub()
        hub.register_project("proj_001", "我的项目")
        session = hub.start_session("proj_001")
        hub.add_memory("proj_001", "修复了登录 Bug", MemoryType.ERROR_FIX)
        hub.close()

    Attributes:
        storage: 底层存储实例 (HubStorage)
    """

    def __init__(self, storage_path: str = "/workspace/octopus_hub/hub.db"):
        """初始化八爪鱼中枢

        Args:
            storage_path: SQLite 数据库文件路径，默认 /workspace/octopus_hub/hub.db
        """
        self.storage = HubStorage(storage_path)

    # ==================== 项目管理 ====================

    def register_project(self, project_id: str, project_name: str,
                         workspace_path: str = "", **kwargs) -> Project:
        """注册新项目并自动创建默认人格

        Args:
            project_id: 项目唯一标识
            project_name: 项目名称
            workspace_path: 工作区路径（可选）
            **kwargs: 传递给 Project 构造函数的其他参数

        Returns:
            Project: 创建成功的项目实例
        """
        project = Project(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            **kwargs
        )
        # 自动创建默认人格
        persona = Persona(
            persona_id=f"persona_{project_id}",
            project_id=project_id
        )
        self.storage.create_persona(persona)
        return self.storage.create_project(project)

    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目信息

        Args:
            project_id: 项目 ID

        Returns:
            Optional[Project]: 项目实例或 None
        """
        return self.storage.get_project(project_id)

    def list_projects(self) -> List[Project]:
        """列出所有项目

        Returns:
            List[Project]: 项目列表
        """
        return self.storage.list_projects()

    def delete_project(self, project_id: str) -> bool:
        """删除项目及所有关联数据

        Args:
            project_id: 项目 ID

        Returns:
            bool: 删除成功返回 True
        """
        return self.storage.delete_project(project_id)

    def get_project_context(self, project_id: str) -> dict:
        """获取项目摘要上下文（约包含最近 10 条记忆）

        Args:
            project_id: 项目 ID

        Returns:
            dict: 包含项目信息、人格、最近记忆的上下文字典
        """
        project = self.storage.get_project(project_id)
        if not project:
            return {"error": f"项目 {project_id} 不存在"}

        persona = self.storage.get_persona_by_project(project_id)
        recent_memories = self.storage.get_memories_by_project(project_id, limit=10)

        return {
            "project": project.to_dict(),
            "persona": persona.to_dict() if persona else None,
            "recent_memories": [m.to_dict() for m in recent_memories],
            "memory_count": len(recent_memories)
        }

    # ==================== 会话管理 ====================

    def start_session(self, project_id: str, agent_id: str = "unknown") -> Session:
        """开始新会话

        自动结束当前项目的旧活跃会话，并更新项目的 active_session_id。

        Args:
            project_id: 项目 ID
            agent_id: Agent 标识，默认 "unknown"

        Returns:
            Session: 新创建的会话实例

        Raises:
            ValueError: 如果项目不存在
        """
        # 检查项目是否存在
        project = self.storage.get_project(project_id)
        if not project:
            raise ValueError(f"项目 {project_id} 不存在，请先注册项目")

        # 自动结束旧活跃会话
        old_session = self.storage.get_active_session(project_id)
        if old_session:
            old_session.status = SessionStatus.COMPLETED
            old_session.ended_at = time.time()
            self.storage.update_session(old_session)

        # 创建新会话，使用高精度时间戳+随机后缀避免碰撞
        session = Session(
            session_id=f"sess_{project_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            agent_id=agent_id
        )
        session = self.storage.create_session(session)

        # 更新项目的活跃会话
        project.active_session_id = session.session_id
        self.storage.update_project(project)

        return session

    def end_session(self, session_id: str) -> Optional[Session]:
        """结束会话

        Args:
            session_id: 会话 ID

        Returns:
            Optional[Session]: 结束后的会话实例，未找到则返回 None
        """
        session = self.storage.get_session(session_id)
        if session:
            session.status = SessionStatus.COMPLETED
            session.ended_at = time.time()
            self.storage.update_session(session)
        return session

    def get_active_session(self, project_id: str) -> Optional[Session]:
        """获取项目的活跃会话

        Args:
            project_id: 项目 ID

        Returns:
            Optional[Session]: 活跃会话实例或 None
        """
        return self.storage.get_active_session(project_id)

    def list_sessions(self, project_id: str, limit: int = 20) -> List[Session]:
        """列出项目的会话历史

        Args:
            project_id: 项目 ID
            limit: 返回数量上限

        Returns:
            List[Session]: 会话列表
        """
        return self.storage.list_sessions(project_id, limit=limit)

    def record_event(self, session_id: str, event_type: str, description: str):
        """记录会话事件

        Args:
            session_id: 会话 ID
            event_type: 事件类型（如 "decision", "error", "milestone"）
            description: 事件描述
        """
        session = self.storage.get_session(session_id)
        if session:
            session.key_events.append({
                "type": event_type,
                "description": description,
                "timestamp": time.time()
            })
            self.storage.update_session(session)

    # ==================== 记忆管理 ====================

    def add_memory(self, project_id: str, content: str, memory_type: MemoryType,
                   importance: float = 0.5, tags: List[str] = None,
                   session_id: str = None,
                   rag_pointers: List[Dict] = None) -> MemoryFragment:
        """添加记忆到中枢

        Args:
            project_id: 项目 ID
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性评分 (0.0 ~ 1.0)，默认 0.5
            tags: 标签列表
            session_id: 关联的会话 ID（可选，不提供则自动使用活跃会话）
            rag_pointers: RAG 知识库指针列表

        Returns:
            MemoryFragment: 创建成功的记忆实例
        """
        # 如果未指定会话，尝试使用当前活跃会话
        if session_id is None:
            active_session = self.storage.get_active_session(project_id)
            session_id = active_session.session_id if active_session else ""

        memory = MemoryFragment(
            memory_id=f"mem_{uuid.uuid4().hex[:12]}",
            project_id=project_id,
            session_id=session_id,
            memory_type=memory_type,
            importance=importance,
            content=content,
            tags=tags or [],
            rag_pointers=rag_pointers or [],
            temporal_context={"created_at": time.time()}
        )
        return self.storage.create_memory(memory)

    def search_memories(self, project_id: str, query: str,
                        memory_type: MemoryType = None,
                        limit: int = 10) -> List[MemoryFragment]:
        """搜索记忆（关键词匹配 + 可选的类型过滤）

        Args:
            project_id: 项目 ID
            query: 搜索关键词
            memory_type: 可选的记忆类型过滤
            limit: 返回数量上限

        Returns:
            List[MemoryFragment]: 匹配的记忆列表
        """
        # 先按关键词搜索
        results = self.storage.search_memories(project_id, query, limit=limit)
        # 如果指定了类型，进一步过滤
        if memory_type:
            results = [m for m in results if m.memory_type == memory_type]
        return results[:limit]

    def get_recent_memories(self, project_id: str, limit: int = 20) -> List[MemoryFragment]:
        """获取项目最近记忆

        Args:
            project_id: 项目 ID
            limit: 返回数量上限

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        return self.storage.get_memories_by_project(project_id, limit=limit)

    def get_key_decisions(self, project_id: str) -> List[MemoryFragment]:
        """获取项目的关键决策记忆

        Args:
            project_id: 项目 ID

        Returns:
            List[MemoryFragment]: 决策类记忆列表
        """
        return self.storage.get_memories_by_type(project_id, MemoryType.DECISION, limit=20)

    def get_error_fixes(self, project_id: str) -> List[MemoryFragment]:
        """获取项目的错误修复记忆

        Args:
            project_id: 项目 ID

        Returns:
            List[MemoryFragment]: 错误修复类记忆列表
        """
        return self.storage.get_memories_by_type(project_id, MemoryType.ERROR_FIX, limit=20)

    def get_memories_by_type(self, project_id: str, memory_type: MemoryType,
                              limit: int = 20) -> List[MemoryFragment]:
        """按类型获取项目记忆

        Args:
            project_id: 项目 ID
            memory_type: 记忆类型
            limit: 返回数量上限

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        return self.storage.get_memories_by_type(project_id, memory_type, limit=limit)

    def get_memories_by_tags(self, project_id: str, tags: List[str],
                              limit: int = 20) -> List[MemoryFragment]:
        """按标签获取项目记忆

        Args:
            project_id: 项目 ID
            tags: 标签列表
            limit: 返回数量上限

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        return self.storage.get_memories_by_tags(project_id, tags, limit=limit)

    def get_memory(self, memory_id: str) -> Optional[MemoryFragment]:
        """获取单条记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            Optional[MemoryFragment]: 记忆实例或 None
        """
        return self.storage.get_memory(memory_id)

    def delete_memory(self, memory_id: str) -> bool:
        """删除单条记忆

        Args:
            memory_id: 记忆 ID

        Returns:
            bool: 删除成功返回 True
        """
        return self.storage.delete_memory(memory_id)

    # ==================== 人格管理 ====================

    def get_persona(self, project_id: str) -> Optional[Persona]:
        """获取项目关联的人格

        Args:
            project_id: 项目 ID

        Returns:
            Optional[Persona]: 人格实例或 None
        """
        return self.storage.get_persona_by_project(project_id)

    def update_persona_preferences(self, project_id: str,
                                    style_updates: Dict = None,
                                    decision_updates: Dict = None,
                                    expertise_updates: Dict = None) -> Optional[Persona]:
        """更新人格偏好

        Args:
            project_id: 项目 ID
            style_updates: 风格偏好更新（如 {"verbosity": "detailed"}）
            decision_updates: 决策倾向更新
            expertise_updates: 领域专业知识更新

        Returns:
            Optional[Persona]: 更新后的人格实例，若项目无人格则返回 None
        """
        persona = self.storage.get_persona_by_project(project_id)
        if not persona:
            return None

        if style_updates:
            persona.style_preferences.update(style_updates)
        if decision_updates:
            persona.decision_tendencies.update(decision_updates)
        if expertise_updates:
            persona.domain_expertise.update(expertise_updates)

        persona.version += 1
        persona.updated_at = time.time()
        return self.storage.update_persona(persona)

    # ==================== 统计 ====================

    def get_stats(self) -> dict:
        """获取中枢整体统计信息

        Returns:
            dict: 包含项目数、记忆数、会话数、人格数的统计字典
        """
        return self.storage.get_stats()

    def close(self):
        """关闭中枢，释放数据库连接"""
        self.storage.close()