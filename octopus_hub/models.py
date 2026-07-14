"""
八爪鱼记忆中枢 - 数据模型定义

定义项目(Project)、人格(Persona)、记忆碎片(MemoryFragment)、会话(Session)等核心数据结构。
使用 Python dataclass 实现，支持 JSON 序列化/反序列化。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import time
import json
import uuid


class MemoryType(Enum):
    """记忆类型枚举"""
    DECISION = "decision"            # 关键决策
    INSIGHT = "insight"              # 洞察/发现
    ERROR_FIX = "error_fix"          # 错误修复记录
    CODE_SNIPPET = "code_snippet"    # 代码片段
    HARDWARE_CONFIG = "hardware_config"  # 硬件配置
    RAG_QUERY = "rag_query"          # RAG 查询记录
    REFLECTION = "reflection"        # 反思/总结


class SessionStatus(Enum):
    """会话状态枚举"""
    ACTIVE = "active"          # 活跃中
    PAUSED = "paused"          # 已暂停
    COMPLETED = "completed"    # 已完成
    REFINING = "refining"      # 精炼中


@dataclass
class Project:
    """项目模型 - 代表一个独立的工程/任务上下文

    Attributes:
        project_id: 项目唯一标识
        project_name: 项目名称
        status: 项目状态 ("active", "archived", "paused")
        workspace_path: 工作区路径
        rag_kb_bindings: 绑定的 RAG 知识库列表
        knowledge_graph_node_ids: 关联的知识图谱节点 ID
        rag_structured_tags: RAG 结构化标签
        context_snapshot: 上下文快照（序列化字符串）
        key_decisions: 关键决策记录列表
        created_at: 创建时间戳
        updated_at: 最后更新时间戳
        active_session_id: 当前活跃会话 ID
    """
    project_id: str
    project_name: str
    status: str = "active"
    workspace_path: str = ""
    rag_kb_bindings: List[str] = field(default_factory=list)
    knowledge_graph_node_ids: List[str] = field(default_factory=list)
    rag_structured_tags: Dict = field(default_factory=dict)
    context_snapshot: str = ""
    key_decisions: List[Dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    active_session_id: Optional[str] = None

    def to_dict(self) -> dict:
        """将 Project 实例序列化为字典"""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "status": self.status,
            "workspace_path": self.workspace_path,
            "rag_kb_bindings": self.rag_kb_bindings,
            "knowledge_graph_node_ids": self.knowledge_graph_node_ids,
            "rag_structured_tags": self.rag_structured_tags,
            "context_snapshot": self.context_snapshot,
            "key_decisions": self.key_decisions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "active_session_id": self.active_session_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """从字典反序列化创建 Project 实例"""
        return cls(
            project_id=data.get("project_id", ""),
            project_name=data.get("project_name", ""),
            status=data.get("status", "active"),
            workspace_path=data.get("workspace_path", ""),
            rag_kb_bindings=data.get("rag_kb_bindings", []),
            knowledge_graph_node_ids=data.get("knowledge_graph_node_ids", []),
            rag_structured_tags=data.get("rag_structured_tags", {}),
            context_snapshot=data.get("context_snapshot", ""),
            key_decisions=data.get("key_decisions", []),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            active_session_id=data.get("active_session_id"),
        )


@dataclass
class Persona:
    """人格模型 - 记录用户偏好和行为模式

    Attributes:
        persona_id: 人格唯一标识
        user_id: 关联的用户 ID
        project_id: 关联的项目 ID
        style_preferences: 风格偏好（详略、正式度、语言、代码风格等）
        communication_patterns: 沟通模式记录
        decision_tendencies: 决策倾向记录
        domain_expertise: 领域专业知识
        interaction_history_summary: 交互历史摘要
        version: 人格版本号
        updated_at: 最后更新时间戳
    """
    persona_id: str
    user_id: str = "default"
    project_id: str = "default"
    style_preferences: Dict = field(default_factory=lambda: {
        "verbosity": "concise",
        "formality": "casual",
        "response_language": "zh-CN",
        "code_style": "descriptive_comments"
    })
    communication_patterns: Dict = field(default_factory=dict)
    decision_tendencies: Dict = field(default_factory=dict)
    domain_expertise: Dict = field(default_factory=dict)
    interaction_history_summary: str = ""
    version: int = 1
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """将 Persona 实例序列化为字典"""
        return {
            "persona_id": self.persona_id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "style_preferences": self.style_preferences,
            "communication_patterns": self.communication_patterns,
            "decision_tendencies": self.decision_tendencies,
            "domain_expertise": self.domain_expertise,
            "interaction_history_summary": self.interaction_history_summary,
            "version": self.version,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Persona":
        """从字典反序列化创建 Persona 实例"""
        return cls(
            persona_id=data.get("persona_id", ""),
            user_id=data.get("user_id", "default"),
            project_id=data.get("project_id", "default"),
            style_preferences=data.get("style_preferences", {
                "verbosity": "concise",
                "formality": "casual",
                "response_language": "zh-CN",
                "code_style": "descriptive_comments"
            }),
            communication_patterns=data.get("communication_patterns", {}),
            decision_tendencies=data.get("decision_tendencies", {}),
            domain_expertise=data.get("domain_expertise", {}),
            interaction_history_summary=data.get("interaction_history_summary", ""),
            version=data.get("version", 1),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class MemoryFragment:
    """记忆碎片模型 - 存储可检索的知识片段

    Attributes:
        memory_id: 记忆唯一标识
        project_id: 所属项目 ID
        session_id: 所属会话 ID
        memory_type: 记忆类型
        importance: 重要性评分 (0.0 ~ 1.0)
        content: 记忆内容
        tags: 标签列表
        rag_pointers: RAG 知识库指针列表
        temporal_context: 时间上下文信息
        access_count: 访问次数
        last_accessed_at: 最后访问时间戳
        ttl: 生存时间（秒），-1 表示永不过期
        version: 记忆版本号
    """
    memory_id: str
    project_id: str
    session_id: str
    memory_type: MemoryType
    importance: float = 0.5
    content: str = ""
    tags: List[str] = field(default_factory=list)
    rag_pointers: List[Dict] = field(default_factory=list)
    temporal_context: Dict = field(default_factory=dict)
    access_count: int = 0
    last_accessed_at: float = field(default_factory=time.time)
    ttl: int = -1
    version: int = 1

    def to_dict(self) -> dict:
        """将 MemoryFragment 实例序列化为字典"""
        return {
            "memory_id": self.memory_id,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "content": self.content,
            "tags": self.tags,
            "rag_pointers": self.rag_pointers,
            "temporal_context": self.temporal_context,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at,
            "ttl": self.ttl,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryFragment":
        """从字典反序列化创建 MemoryFragment 实例"""
        memory_type_raw = data.get("memory_type", "decision")
        if isinstance(memory_type_raw, MemoryType):
            memory_type = memory_type_raw
        else:
            memory_type = MemoryType(memory_type_raw)

        return cls(
            memory_id=data.get("memory_id", ""),
            project_id=data.get("project_id", ""),
            session_id=data.get("session_id", ""),
            memory_type=memory_type,
            importance=data.get("importance", 0.5),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            rag_pointers=data.get("rag_pointers", []),
            temporal_context=data.get("temporal_context", {}),
            access_count=data.get("access_count", 0),
            last_accessed_at=data.get("last_accessed_at", time.time()),
            ttl=data.get("ttl", -1),
            version=data.get("version", 1),
        )


@dataclass
class Session:
    """会话模型 - 记录一次完整的交互会话

    Attributes:
        session_id: 会话唯一标识
        project_id: 所属项目 ID
        agent_id: 执行 Agent 标识
        status: 会话状态
        context_package: 上下文包（包含初始上下文信息）
        message_count: 消息数量
        total_tokens_used: 总 Token 消耗量
        rag_queries: RAG 查询记录列表
        key_events: 关键事件记录列表
        created_at: 创建时间戳
        ended_at: 结束时间戳
        refinement_status: 精炼状态
        refined_memories: 已精炼的记忆 ID 列表
    """
    session_id: str
    project_id: str
    agent_id: str = "unknown"
    status: SessionStatus = SessionStatus.ACTIVE
    context_package: Dict = field(default_factory=dict)
    message_count: int = 0
    total_tokens_used: int = 0
    rag_queries: List[Dict] = field(default_factory=list)
    key_events: List[Dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    refinement_status: str = "pending"
    refined_memories: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """将 Session 实例序列化为字典"""
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "context_package": self.context_package,
            "message_count": self.message_count,
            "total_tokens_used": self.total_tokens_used,
            "rag_queries": self.rag_queries,
            "key_events": self.key_events,
            "created_at": self.created_at,
            "ended_at": self.ended_at,
            "refinement_status": self.refinement_status,
            "refined_memories": self.refined_memories,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """从字典反序列化创建 Session 实例"""
        status_raw = data.get("status", "active")
        if isinstance(status_raw, SessionStatus):
            status = status_raw
        else:
            status = SessionStatus(status_raw)

        return cls(
            session_id=data.get("session_id", ""),
            project_id=data.get("project_id", ""),
            agent_id=data.get("agent_id", "unknown"),
            status=status,
            context_package=data.get("context_package", {}),
            message_count=data.get("message_count", 0),
            total_tokens_used=data.get("total_tokens_used", 0),
            rag_queries=data.get("rag_queries", []),
            key_events=data.get("key_events", []),
            created_at=data.get("created_at", time.time()),
            ended_at=data.get("ended_at"),
            refinement_status=data.get("refinement_status", "pending"),
            refined_memories=data.get("refined_memories", []),
        )