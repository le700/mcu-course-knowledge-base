"""
八爪鱼记忆中枢 (Octopus Hub) - 核心包

提供项目管理、记忆存储、会话追踪、人格建模等功能，
以及 RAG v4 知识库桥接层。

无本地 LLM 依赖：使用 SentenceTransformer + TF-IDF + ChromaDB 实现
记忆语义搜索、去重、聚类、反思闭环等全部功能。
"""

# 数据模型与核心 API
from .models import (
    MemoryType,
    SessionStatus,
    Project,
    Persona,
    MemoryFragment,
    Session,
)

from .storage import HubStorage
from .core import OctopusHub

# RAG v4 知识库桥接层
from .kg_adapter import KnowledgeGraphAdapter
from .hub_bridge import HubBridge, QueryCache

# 硬件参考解析器
from .hardware_parser import HardwareRefParser

# 反思引擎与无感接手协议（不依赖外部库）
from .reflection import ReflectionEngine
from .handoff import HandoffProtocol

# 记忆向量存储（需要 SentenceTransformer + ChromaDB，可选）
try:
    from .memory_vector_store import MemoryVectorStore
except ImportError:
    MemoryVectorStore = None

# 整合系统入口（可选，依赖 reflection + handoff + bridge）
try:
    from .integration import OctopusSystem
except ImportError:
    OctopusSystem = None

__all__ = [
    # 枚举
    "MemoryType",
    "SessionStatus",
    # 数据模型
    "Project",
    "Persona",
    "MemoryFragment",
    "Session",
    # 存储层
    "HubStorage",
    # 核心 API
    "OctopusHub",
    # 知识库桥接层
    "KnowledgeGraphAdapter",
    "HubBridge",
    "QueryCache",
    # 硬件解析
    "HardwareRefParser",
    # 记忆向量存储
    "MemoryVectorStore",
    # 反思 & 接手
    "ReflectionEngine",
    "HandoffProtocol",
    # 整合系统
    "OctopusSystem",
]

__version__ = "2.0.0"