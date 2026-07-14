"""
八爪鱼记忆中枢 - 存储层 (SQLite)

提供所有数据模型的持久化存储，支持 CRUD 操作和基础查询。
使用 SQLite 作为后端存储引擎，JSON 字段自动序列化/反序列化。
"""

import sqlite3
import json
import os
import threading
from typing import List, Optional
from .models import Project, Persona, MemoryFragment, Session, MemoryType, SessionStatus

# 尝试导入 ChromaDB 向量存储依赖（降级方案：不可用时回退到 SQLite 关键词搜索）
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMER_AVAILABLE = False


class HubStorage:
    """八爪鱼中枢存储层 - 基于 SQLite 的持久化存储

    负责管理所有数据模型的 CRUD 操作，自动处理 JSON 字段的序列化与反序列化。
    使用线程本地存储确保多线程环境下的连接安全。

    Attributes:
        db_path: SQLite 数据库文件路径
    """

    def __init__(self, db_path: str = "/workspace/octopus_hub/hub.db"):
        """初始化存储层

        Args:
            db_path: SQLite 数据库文件路径，默认为 /workspace/octopus_hub/hub.db
        """
        self.db_path = db_path
        # 确保数据库文件所在目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        # 使用线程本地存储隔离连接
        self._local = threading.local()
        self._init_db()

        # ChromaDB 向量存储相关属性（延迟初始化）
        self._vector_store_initialized = False
        self._chroma_client = None
        self._chroma_collection = None
        self._embedding_model = None
        self._chroma_path = os.path.join(
            os.path.dirname(db_path) or "/workspace/octopus_hub",
            "chroma_memories"
        )

    def _get_conn(self) -> sqlite3.Connection:
        """获取当前线程的数据库连接，若不存在则创建

        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    @property
    def conn(self) -> sqlite3.Connection:
        """获取当前线程的数据库连接"""
        return self._get_conn()

    def _init_db(self):
        """初始化数据库表结构

        创建 projects、personas、memories、sessions 四张核心表，
        以及必要的索引以优化查询性能。
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # 创建项目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                workspace_path TEXT DEFAULT '',
                rag_kb_bindings TEXT DEFAULT '[]',
                kg_node_ids TEXT DEFAULT '[]',
                rag_tags TEXT DEFAULT '{}',
                context_snapshot TEXT DEFAULT '',
                key_decisions TEXT DEFAULT '[]',
                created_at REAL,
                updated_at REAL,
                active_session_id TEXT
            )
        """)

        # 创建人格表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personas (
                persona_id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'default',
                project_id TEXT DEFAULT 'default',
                style_prefs TEXT DEFAULT '{}',
                comm_patterns TEXT DEFAULT '{}',
                decision_tendencies TEXT DEFAULT '{}',
                domain_expertise TEXT DEFAULT '{}',
                interaction_summary TEXT DEFAULT '',
                version INTEGER DEFAULT 1,
                updated_at REAL
            )
        """)

        # 创建记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                session_id TEXT DEFAULT '',
                memory_type TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                content TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                rag_pointers TEXT DEFAULT '[]',
                temporal_context TEXT DEFAULT '{}',
                access_count INTEGER DEFAULT 0,
                last_accessed_at REAL,
                ttl INTEGER DEFAULT -1,
                version INTEGER DEFAULT 1
            )
        """)

        # 创建会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                agent_id TEXT DEFAULT 'unknown',
                status TEXT DEFAULT 'active',
                context_package TEXT DEFAULT '{}',
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                rag_queries TEXT DEFAULT '[]',
                key_events TEXT DEFAULT '[]',
                created_at REAL,
                ended_at REAL,
                refinement_status TEXT DEFAULT 'pending',
                refined_memories TEXT DEFAULT '[]'
            )
        """)

        # 创建索引以优化查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_project
            ON memories(project_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_session
            ON memories(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_type
            ON memories(project_id, memory_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_project
            ON sessions(project_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_status
            ON sessions(project_id, status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_personas_project
            ON personas(project_id)
        """)

        conn.commit()

    # ==================== Project CRUD ====================

    def create_project(self, project: Project) -> Project:
        """创建新项目

        Args:
            project: Project 实例

        Returns:
            Project: 创建成功的项目实例（含默认值）
        """
        conn = self._get_conn()
        data = project.to_dict()
        conn.execute("""
            INSERT OR REPLACE INTO projects
            (project_id, project_name, status, workspace_path, rag_kb_bindings,
             kg_node_ids, rag_tags, context_snapshot, key_decisions,
             created_at, updated_at, active_session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["project_id"],
            data["project_name"],
            data["status"],
            data["workspace_path"],
            json.dumps(data["rag_kb_bindings"], ensure_ascii=False),
            json.dumps(data["knowledge_graph_node_ids"], ensure_ascii=False),
            json.dumps(data["rag_structured_tags"], ensure_ascii=False),
            data["context_snapshot"],
            json.dumps(data["key_decisions"], ensure_ascii=False),
            data["created_at"],
            data["updated_at"],
            data["active_session_id"],
        ))
        conn.commit()
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """根据项目 ID 获取项目

        Args:
            project_id: 项目唯一标识

        Returns:
            Optional[Project]: 找到返回 Project 实例，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM projects WHERE project_id = ?", (project_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_project(row)

    def update_project(self, project: Project) -> Project:
        """更新项目信息

        Args:
            project: 已修改的 Project 实例

        Returns:
            Project: 更新后的项目实例
        """
        conn = self._get_conn()
        data = project.to_dict()
        conn.execute("""
            UPDATE projects SET
                project_name = ?, status = ?, workspace_path = ?,
                rag_kb_bindings = ?, kg_node_ids = ?, rag_tags = ?,
                context_snapshot = ?, key_decisions = ?,
                updated_at = ?, active_session_id = ?
            WHERE project_id = ?
        """, (
            data["project_name"],
            data["status"],
            data["workspace_path"],
            json.dumps(data["rag_kb_bindings"], ensure_ascii=False),
            json.dumps(data["knowledge_graph_node_ids"], ensure_ascii=False),
            json.dumps(data["rag_structured_tags"], ensure_ascii=False),
            data["context_snapshot"],
            json.dumps(data["key_decisions"], ensure_ascii=False),
            data["updated_at"],
            data["active_session_id"],
            data["project_id"],
        ))
        conn.commit()
        return project

    def list_projects(self) -> List[Project]:
        """列出所有项目

        Returns:
            List[Project]: 所有项目的列表
        """
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        return [self._row_to_project(row) for row in cursor.fetchall()]

    def delete_project(self, project_id: str) -> bool:
        """删除项目及其关联数据

        Args:
            project_id: 要删除的项目 ID

        Returns:
            bool: 删除成功返回 True
        """
        conn = self._get_conn()
        conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM personas WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM memories WHERE project_id = ?", (project_id,))
        conn.execute("DELETE FROM sessions WHERE project_id = ?", (project_id,))
        conn.commit()
        return True

    def _row_to_project(self, row) -> Project:
        """将数据库行转换为 Project 实例"""
        return Project(
            project_id=row["project_id"],
            project_name=row["project_name"],
            status=row["status"],
            workspace_path=row["workspace_path"],
            rag_kb_bindings=json.loads(row["rag_kb_bindings"]),
            knowledge_graph_node_ids=json.loads(row["kg_node_ids"]),
            rag_structured_tags=json.loads(row["rag_tags"]),
            context_snapshot=row["context_snapshot"],
            key_decisions=json.loads(row["key_decisions"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            active_session_id=row["active_session_id"],
        )

    # ==================== Persona CRUD ====================

    def create_persona(self, persona: Persona) -> Persona:
        """创建新人格

        Args:
            persona: Persona 实例

        Returns:
            Persona: 创建成功的人格实例
        """
        conn = self._get_conn()
        data = persona.to_dict()
        conn.execute("""
            INSERT OR REPLACE INTO personas
            (persona_id, user_id, project_id, style_prefs, comm_patterns,
             decision_tendencies, domain_expertise, interaction_summary,
             version, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["persona_id"],
            data["user_id"],
            data["project_id"],
            json.dumps(data["style_preferences"], ensure_ascii=False),
            json.dumps(data["communication_patterns"], ensure_ascii=False),
            json.dumps(data["decision_tendencies"], ensure_ascii=False),
            json.dumps(data["domain_expertise"], ensure_ascii=False),
            data["interaction_history_summary"],
            data["version"],
            data["updated_at"],
        ))
        conn.commit()
        return persona

    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """根据人格 ID 获取人格

        Args:
            persona_id: 人格唯一标识

        Returns:
            Optional[Persona]: 找到返回 Persona 实例，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM personas WHERE persona_id = ?", (persona_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_persona(row)

    def get_persona_by_project(self, project_id: str) -> Optional[Persona]:
        """根据项目 ID 获取关联的人格

        Args:
            project_id: 项目 ID

        Returns:
            Optional[Persona]: 找到返回 Persona 实例，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM personas WHERE project_id = ?", (project_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_persona(row)

    def update_persona(self, persona: Persona) -> Persona:
        """更新人格信息

        Args:
            persona: 已修改的 Persona 实例

        Returns:
            Persona: 更新后的人格实例
        """
        conn = self._get_conn()
        data = persona.to_dict()
        conn.execute("""
            UPDATE personas SET
                style_prefs = ?, comm_patterns = ?, decision_tendencies = ?,
                domain_expertise = ?, interaction_summary = ?,
                version = ?, updated_at = ?
            WHERE persona_id = ?
        """, (
            json.dumps(data["style_preferences"], ensure_ascii=False),
            json.dumps(data["communication_patterns"], ensure_ascii=False),
            json.dumps(data["decision_tendencies"], ensure_ascii=False),
            json.dumps(data["domain_expertise"], ensure_ascii=False),
            data["interaction_history_summary"],
            data["version"],
            data["updated_at"],
            data["persona_id"],
        ))
        conn.commit()
        return persona

    def _row_to_persona(self, row) -> Persona:
        """将数据库行转换为 Persona 实例"""
        return Persona(
            persona_id=row["persona_id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            style_preferences=json.loads(row["style_prefs"]),
            communication_patterns=json.loads(row["comm_patterns"]),
            decision_tendencies=json.loads(row["decision_tendencies"]),
            domain_expertise=json.loads(row["domain_expertise"]),
            interaction_history_summary=row["interaction_summary"],
            version=row["version"],
            updated_at=row["updated_at"],
        )

    # ==================== MemoryFragment CRUD ====================

    def create_memory(self, memory: MemoryFragment) -> MemoryFragment:
        """创建新记忆

        Args:
            memory: MemoryFragment 实例

        Returns:
            MemoryFragment: 创建成功的记忆实例
        """
        conn = self._get_conn()
        data = memory.to_dict()
        conn.execute("""
            INSERT OR REPLACE INTO memories
            (memory_id, project_id, session_id, memory_type, importance,
             content, tags, rag_pointers, temporal_context,
             access_count, last_accessed_at, ttl, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["memory_id"],
            data["project_id"],
            data["session_id"],
            data["memory_type"],
            data["importance"],
            data["content"],
            json.dumps(data["tags"], ensure_ascii=False),
            json.dumps(data["rag_pointers"], ensure_ascii=False),
            json.dumps(data["temporal_context"], ensure_ascii=False),
            data["access_count"],
            data["last_accessed_at"],
            data["ttl"],
            data["version"],
        ))
        conn.commit()
        return memory

    def get_memory(self, memory_id: str) -> Optional[MemoryFragment]:
        """根据记忆 ID 获取记忆

        Args:
            memory_id: 记忆唯一标识

        Returns:
            Optional[MemoryFragment]: 找到返回 MemoryFragment 实例，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM memories WHERE memory_id = ?", (memory_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_memory(row)

    def get_memories_by_project(self, project_id: str, limit: int = 50) -> List[MemoryFragment]:
        """获取指定项目的所有记忆（按最后访问时间倒序）

        Args:
            project_id: 项目 ID
            limit: 返回数量上限，默认 50

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM memories WHERE project_id = ? ORDER BY last_accessed_at DESC LIMIT ?",
            (project_id, limit)
        )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def get_memories_by_session(self, session_id: str) -> List[MemoryFragment]:
        """获取指定会话的所有记忆

        Args:
            session_id: 会话 ID

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM memories WHERE session_id = ? ORDER BY last_accessed_at DESC",
            (session_id,)
        )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def get_memories_by_type(self, project_id: str, memory_type: MemoryType,
                              limit: int = 20) -> List[MemoryFragment]:
        """获取指定类型的内存

        Args:
            project_id: 项目 ID
            memory_type: 记忆类型
            limit: 返回数量上限，默认 20

        Returns:
            List[MemoryFragment]: 记忆列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM memories WHERE project_id = ? AND memory_type = ? "
            "ORDER BY importance DESC, last_accessed_at DESC LIMIT ?",
            (project_id, memory_type.value, limit)
        )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def get_memories_by_tags(self, project_id: str, tags: List[str],
                              limit: int = 20) -> List[MemoryFragment]:
        """根据标签搜索记忆（匹配任一标签）

        Args:
            project_id: 项目 ID
            tags: 标签列表
            limit: 返回数量上限，默认 20

        Returns:
            List[MemoryFragment]: 匹配的记忆列表
        """
        conn = self._get_conn()
        # 获取项目所有记忆，然后在 Python 中过滤标签
        cursor = conn.execute(
            "SELECT * FROM memories WHERE project_id = ? ORDER BY last_accessed_at DESC",
            (project_id,)
        )
        results = []
        for row in cursor.fetchall():
            memory = self._row_to_memory(row)
            if any(tag in memory.tags for tag in tags):
                results.append(memory)
                if len(results) >= limit:
                    break
        return results

    def update_memory(self, memory: MemoryFragment) -> MemoryFragment:
        """更新记忆信息

        Args:
            memory: 已修改的 MemoryFragment 实例

        Returns:
            MemoryFragment: 更新后的记忆实例
        """
        conn = self._get_conn()
        data = memory.to_dict()
        conn.execute("""
            UPDATE memories SET
                importance = ?, content = ?, tags = ?, rag_pointers = ?,
                temporal_context = ?, access_count = ?, last_accessed_at = ?,
                ttl = ?, version = ?
            WHERE memory_id = ?
        """, (
            data["importance"],
            data["content"],
            json.dumps(data["tags"], ensure_ascii=False),
            json.dumps(data["rag_pointers"], ensure_ascii=False),
            json.dumps(data["temporal_context"], ensure_ascii=False),
            data["access_count"],
            data["last_accessed_at"],
            data["ttl"],
            data["version"],
            data["memory_id"],
        ))
        conn.commit()
        return memory

    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆

        Args:
            memory_id: 要删除的记忆 ID

        Returns:
            bool: 删除成功返回 True
        """
        conn = self._get_conn()
        conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
        conn.commit()
        return True

    def search_memories(self, project_id: str, keyword: str,
                         limit: int = 20) -> List[MemoryFragment]:
        """按关键词搜索记忆（在 content 字段中模糊匹配）

        Args:
            project_id: 项目 ID
            keyword: 搜索关键词
            limit: 返回数量上限，默认 20

        Returns:
            List[MemoryFragment]: 匹配的记忆列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM memories WHERE project_id = ? AND content LIKE ? "
            "ORDER BY importance DESC, last_accessed_at DESC LIMIT ?",
            (project_id, f"%{keyword}%", limit)
        )
        return [self._row_to_memory(row) for row in cursor.fetchall()]

    def _row_to_memory(self, row) -> MemoryFragment:
        """将数据库行转换为 MemoryFragment 实例"""
        return MemoryFragment(
            memory_id=row["memory_id"],
            project_id=row["project_id"],
            session_id=row["session_id"],
            memory_type=MemoryType(row["memory_type"]),
            importance=row["importance"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            rag_pointers=json.loads(row["rag_pointers"]),
            temporal_context=json.loads(row["temporal_context"]),
            access_count=row["access_count"],
            last_accessed_at=row["last_accessed_at"],
            ttl=row["ttl"],
            version=row["version"],
        )

    # ==================== Session CRUD ====================

    def create_session(self, session: Session) -> Session:
        """创建新会话

        Args:
            session: Session 实例

        Returns:
            Session: 创建成功的会话实例
        """
        conn = self._get_conn()
        data = session.to_dict()
        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, project_id, agent_id, status, context_package,
             message_count, total_tokens, rag_queries, key_events,
             created_at, ended_at, refinement_status, refined_memories)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["session_id"],
            data["project_id"],
            data["agent_id"],
            data["status"],
            json.dumps(data["context_package"], ensure_ascii=False),
            data["message_count"],
            data["total_tokens_used"],
            json.dumps(data["rag_queries"], ensure_ascii=False),
            json.dumps(data["key_events"], ensure_ascii=False),
            data["created_at"],
            data["ended_at"],
            data["refinement_status"],
            json.dumps(data["refined_memories"], ensure_ascii=False),
        ))
        conn.commit()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """根据会话 ID 获取会话

        Args:
            session_id: 会话唯一标识

        Returns:
            Optional[Session]: 找到返回 Session 实例，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def get_active_session(self, project_id: str) -> Optional[Session]:
        """获取项目的活跃会话

        Args:
            project_id: 项目 ID

        Returns:
            Optional[Session]: 找到返回活跃会话，否则返回 None
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE project_id = ? AND status = 'active' "
            "ORDER BY created_at DESC LIMIT 1",
            (project_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def update_session(self, session: Session) -> Session:
        """更新会话信息

        Args:
            session: 已修改的 Session 实例

        Returns:
            Session: 更新后的会话实例
        """
        conn = self._get_conn()
        data = session.to_dict()
        conn.execute("""
            UPDATE sessions SET
                status = ?, context_package = ?, message_count = ?,
                total_tokens = ?, rag_queries = ?, key_events = ?,
                ended_at = ?, refinement_status = ?, refined_memories = ?
            WHERE session_id = ?
        """, (
            data["status"],
            json.dumps(data["context_package"], ensure_ascii=False),
            data["message_count"],
            data["total_tokens_used"],
            json.dumps(data["rag_queries"], ensure_ascii=False),
            json.dumps(data["key_events"], ensure_ascii=False),
            data["ended_at"],
            data["refinement_status"],
            json.dumps(data["refined_memories"], ensure_ascii=False),
            data["session_id"],
        ))
        conn.commit()
        return session

    def list_sessions(self, project_id: str, limit: int = 20) -> List[Session]:
        """列出项目的所有会话（按创建时间倒序）

        Args:
            project_id: 项目 ID
            limit: 返回数量上限，默认 20

        Returns:
            List[Session]: 会话列表
        """
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
            (project_id, limit)
        )
        return [self._row_to_session(row) for row in cursor.fetchall()]

    def _row_to_session(self, row) -> Session:
        """将数据库行转换为 Session 实例"""
        return Session(
            session_id=row["session_id"],
            project_id=row["project_id"],
            agent_id=row["agent_id"],
            status=SessionStatus(row["status"]),
            context_package=json.loads(row["context_package"]),
            message_count=row["message_count"],
            total_tokens_used=row["total_tokens"],
            rag_queries=json.loads(row["rag_queries"]),
            key_events=json.loads(row["key_events"]),
            created_at=row["created_at"],
            ended_at=row["ended_at"],
            refinement_status=row["refinement_status"],
            refined_memories=json.loads(row["refined_memories"]),
        )

    # ==================== 统计 ====================

    def get_stats(self) -> dict:
        """获取中枢统计信息

        Returns:
            dict: 包含项目数、记忆数、会话数、人格数的统计字典
        """
        conn = self._get_conn()
        stats = {}
        for table, key in [
            ("projects", "projects"),
            ("memories", "memories"),
            ("sessions", "sessions"),
            ("personas", "personas"),
        ]:
            cursor = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}")
            row = cursor.fetchone()
            stats[key] = row["cnt"] if row else 0
        return stats

    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None