"""
八爪鱼记忆中枢 - 记忆向量存储模块

基于 SentenceTransformer + ChromaDB 实现记忆的语义搜索、去重和聚类。
使用 all-MiniLM-L6-v2 模型（384维）对记忆内容进行向量化编码，
通过 ChromaDB 持久化存储向量并支持余弦相似度检索。
"""

import os
import numpy as np
from typing import List, Optional, Dict, Any

from .models import MemoryFragment, MemoryType


class MemoryVectorStore:
    """记忆向量存储 - 语义搜索、去重、聚类

    使用 SentenceTransformer 将记忆文本编码为 384 维向量，
    存入 ChromaDB 持久化向量数据库，支持语义检索、去重检测和聚类分析。

    所有外部依赖（SentenceTransformer, ChromaDB, sklearn）均为延迟加载，
    只在 __init__ 时导入，不影响模块级导入。
    """

    # 模型名称常量
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    # 向量维度
    VECTOR_DIMENSION = 384
    # ChromaDB collection 名称
    COLLECTION_NAME = "hub_memories"

    def __init__(self, persist_dir: str = "/workspace/octopus_hub/memory_vectors"):
        """初始化 MemoryVectorStore。

        1. 加载 SentenceTransformer 模型（all-MiniLM-L6-v2，384维）
        2. 创建 ChromaDB PersistentClient（持久化存储）
        3. 获取或创建 collection 'hub_memories'（余弦距离）

        Args:
            persist_dir: ChromaDB 持久化存储目录路径
        """
        self.persist_dir = persist_dir

        # 确保持久化目录存在
        os.makedirs(self.persist_dir, exist_ok=True)

        # 延迟导入：只在实例化时加载外部依赖
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings

        # 加载 SentenceTransformer 模型
        try:
            self.model = SentenceTransformer(self.EMBEDDING_MODEL_NAME)
            print(f"[MemoryVectorStore] 成功加载嵌入模型: {self.EMBEDDING_MODEL_NAME}")
        except Exception as e:
            print(f"[MemoryVectorStore] 加载嵌入模型失败: {e}")
            raise RuntimeError(f"无法加载 SentenceTransformer 模型 '{self.EMBEDDING_MODEL_NAME}': {e}")

        # 创建 ChromaDB PersistentClient
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    is_persistent=True,
                ),
            )
            print(f"[MemoryVectorStore] ChromaDB 客户端已连接，持久化目录: {self.persist_dir}")
        except Exception as e:
            print(f"[MemoryVectorStore] 创建 ChromaDB 客户端失败: {e}")
            raise RuntimeError(f"无法创建 ChromaDB 客户端: {e}")

        # 获取或创建 collection（余弦距离，384维）
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            print(f"[MemoryVectorStore] Collection '{self.COLLECTION_NAME}' 已就绪")
        except Exception as e:
            print(f"[MemoryVectorStore] 创建/获取 Collection 失败: {e}")
            raise RuntimeError(f"无法创建/获取 ChromaDB Collection: {e}")

    # ------------------------------------------------------------------
    # 向量编码
    # ------------------------------------------------------------------

    def _encode(self, text: str) -> np.ndarray:
        """将文本编码为 384 维向量。

        Args:
            text: 待编码的文本内容

        Returns:
            numpy 数组，形状为 (384,) 的 float32 向量
        """
        # SentenceTransformer.encode 返回 numpy 数组
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def _encode_batch(self, texts: List[str]) -> List[np.ndarray]:
        """批量编码文本为向量。

        Args:
            texts: 待编码的文本列表

        Returns:
            numpy 向量列表
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.astype(np.float32) for emb in embeddings]

    # ------------------------------------------------------------------
    # 记忆添加
    # ------------------------------------------------------------------

    def _build_metadata(self, memory: MemoryFragment) -> Dict[str, Any]:
        """从 MemoryFragment 构建 ChromaDB metadata 字典。

        Args:
            memory: 记忆碎片实例

        Returns:
            包含 memory_id, project_id, memory_type, importance,
            tags, session_id 的元数据字典
        """
        # 将枚举类型转为字符串值
        memory_type_str = memory.memory_type.value if isinstance(memory.memory_type, MemoryType) else str(memory.memory_type)
        # 标签列表转为逗号分隔的字符串
        tags_str = ",".join(memory.tags) if memory.tags else ""

        return {
            "memory_id": memory.memory_id,
            "project_id": memory.project_id,
            "memory_type": memory_type_str,
            "importance": float(memory.importance),
            "tags": tags_str,
            "session_id": memory.session_id,
        }

    def add_memory(self, memory: MemoryFragment) -> str:
        """将一条记忆加入向量存储。

        对 memory.content 进行 SentenceTransformer 编码得到 384 维向量，
        连同元数据一起存入 ChromaDB。

        Args:
            memory: 要添加的记忆碎片实例

        Returns:
            ChromaDB 中的 document id（即 memory.memory_id）
        """
        # 编码记忆内容为向量
        embedding = self._encode(memory.content)

        # 构建元数据
        metadata = self._build_metadata(memory)

        # 使用 memory_id 作为 ChromaDB 的 document id
        doc_id = memory.memory_id

        # 添加到 ChromaDB collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding.tolist()],
            documents=[memory.content],
            metadatas=[metadata],
        )

        print(f"[MemoryVectorStore] 记忆已添加: {doc_id} (类型: {metadata['memory_type']}, 重要性: {metadata['importance']})")
        return doc_id

    def add_memories_batch(self, memories: List[MemoryFragment]) -> int:
        """批量添加记忆到向量存储。

        对每条记忆的 content 批量编码后一次性写入 ChromaDB，提高效率。

        Args:
            memories: 要添加的记忆碎片列表

        Returns:
            成功添加的记忆数量
        """
        if not memories:
            return 0

        # 收集所有需要的数据
        ids = []
        contents = []
        metadatas = []

        for memory in memories:
            ids.append(memory.memory_id)
            contents.append(memory.content)
            metadatas.append(self._build_metadata(memory))

        # 批量编码
        embeddings = self._encode_batch(contents)

        # 批量写入 ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=[emb.tolist() for emb in embeddings],
            documents=contents,
            metadatas=metadatas,
        )

        print(f"[MemoryVectorStore] 批量添加 {len(memories)} 条记忆")
        return len(memories)

    # ------------------------------------------------------------------
    # 语义搜索
    # ------------------------------------------------------------------

    def _build_where_filter(self, project_id: Optional[str] = None,
                            memory_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """构建 ChromaDB 的 where 过滤条件。

        Args:
            project_id: 可选的项目 ID 过滤
            memory_type: 可选的记忆类型过滤

        Returns:
            ChromaDB where 字典，或 None（无过滤条件）
        """
        conditions = []
        if project_id is not None:
            conditions.append({"project_id": project_id})
        if memory_type is not None:
            conditions.append({"memory_type": memory_type})

        if not conditions:
            return None
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {"$and": conditions}

    def semantic_search(self, query: str, project_id: Optional[str] = None,
                        top_k: int = 10, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """语义搜索记忆。

        对查询文本进行向量编码，在 ChromaDB 中检索最相似的 top_k 条记忆，
        支持按 project_id 和 memory_type 过滤。

        Args:
            query: 搜索查询文本
            project_id: 可选，按项目 ID 过滤
            top_k: 返回结果数量，默认 10
            memory_type: 可选，按记忆类型过滤（如 "decision", "insight" 等）

        Returns:
            搜索结果列表，每条包含：
            {memory_id, content, score, memory_type, importance, tags, project_id}
            其中 score 为余弦相似度（0.0 ~ 1.0，越大越相似）
        """
        # 编码查询文本
        query_embedding = self._encode(query)

        # 构建 where 过滤条件
        where_filter = self._build_where_filter(project_id, memory_type)

        # 在 ChromaDB 中检索
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter,
        )

        # 解析结果并格式化返回
        output = []
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                document = results["documents"][0][i] if results["documents"] else ""
                # ChromaDB 返回的是余弦距离，转换为相似度：similarity = 1 - distance
                distance = results["distances"][0][i] if results["distances"] else 0.0
                score = 1.0 - distance
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                output.append({
                    "memory_id": metadata.get("memory_id", doc_id),
                    "content": document,
                    "score": round(score, 4),
                    "memory_type": metadata.get("memory_type", ""),
                    "importance": metadata.get("importance", 0.0),
                    "tags": metadata.get("tags", ""),
                    "project_id": metadata.get("project_id", ""),
                })

        print(f"[MemoryVectorStore] 语义搜索完成: query='{query[:50]}...', 结果数={len(output)}")
        return output

    # ------------------------------------------------------------------
    # 去重与相似查找
    # ------------------------------------------------------------------

    def deduplicate(self, content: str, threshold: float = 0.85) -> bool:
        """检查 content 是否与已有记忆重复。

        将 content 编码为向量，在 ChromaDB 中检索最相似的 top-1 记忆，
        如果余弦相似度超过 threshold，则判定为重复。

        Args:
            content: 待检查的记忆内容
            threshold: 相似度阈值，默认 0.85（85% 相似即判为重复）

        Returns:
            True 表示重复（存在相似度超过阈值的已有记忆），False 表示不重复
        """
        # 编码内容
        embedding = self._encode(content)

        # 检索 top-1 最相似记忆
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=1,
        )

        if not results or not results["ids"] or not results["ids"][0]:
            # 向量库为空，不重复
            return False

        # 获取相似度分数
        distance = results["distances"][0][0] if results["distances"] else 1.0
        similarity = 1.0 - distance

        is_duplicate = similarity > threshold
        print(f"[MemoryVectorStore] 去重检查: 最高相似度={similarity:.4f}, 阈值={threshold}, 重复={is_duplicate}")
        return is_duplicate

    def find_similar_memories(self, content: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """找到与 content 最相似的已有记忆。

        实际上是对 semantic_search 的便捷封装，不设 project_id 和 memory_type 过滤。

        Args:
            content: 待匹配的记忆内容
            top_k: 返回的相似记忆数量，默认 5

        Returns:
            相似记忆列表，格式与 semantic_search 一致
        """
        return self.semantic_search(query=content, top_k=top_k)

    # ------------------------------------------------------------------
    # 聚类分析
    # ------------------------------------------------------------------

    def cluster_memories(self, project_id: str, n_clusters: int = 5) -> List[Dict[str, Any]]:
        """对项目记忆做 KMeans 聚类分析。

        1. 获取指定项目的所有记忆向量
        2. 使用 sklearn KMeans 进行聚类
        3. 返回每个簇的信息（大小、代表内容、热门标签）

        Args:
            project_id: 项目 ID
            n_clusters: 聚类数量，默认 5

        Returns:
            聚类结果列表，每条包含：
            {cluster_id, size, representative_content, top_tags}
            其中 representative_content 为簇中心记忆的前 100 字
        """
        # 获取该项目下所有记忆
        try:
            all_data = self.collection.get(
                where={"project_id": project_id},
                include=["embeddings", "documents", "metadatas"],
            )
        except Exception as e:
            print(f"[MemoryVectorStore] 获取项目记忆失败: {e}")
            return []

        if not all_data or not all_data["embeddings"] or len(all_data["embeddings"]) == 0:
            print(f"[MemoryVectorStore] 项目 {project_id} 没有记忆数据，无法聚类")
            return []

        # 提取向量和内容
        vectors = np.array(all_data["embeddings"], dtype=np.float32)
        documents = all_data["documents"]
        metadatas = all_data["metadatas"]

        num_memories = len(vectors)
        # 调整聚类数：不能超过记忆数量
        actual_n_clusters = min(n_clusters, num_memories)
        if actual_n_clusters < n_clusters:
            print(f"[MemoryVectorStore] 记忆数量({num_memories})少于目标聚类数({n_clusters})，调整为 {actual_n_clusters}")

        # KMeans 聚类
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=actual_n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(vectors)

        # 获取聚类中心
        centroids = kmeans.cluster_centers_

        # 为每个簇找到最接近质心的记忆（代表内容）
        cluster_results = []
        for cluster_id in range(actual_n_clusters):
            # 属于该簇的索引
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_size = len(cluster_indices)

            if cluster_size == 0:
                continue

            # 获取该簇的向量
            cluster_vectors = vectors[cluster_indices]

            # 计算每个向量到质心的余弦距离（使用点积近似，因为向量已归一化）
            centroid = centroids[cluster_id]
            # 计算余弦相似度：向量与质心的点积
            similarities = np.dot(cluster_vectors, centroid) / (
                np.linalg.norm(cluster_vectors, axis=1) * np.linalg.norm(centroid) + 1e-10
            )
            # 找到最接近质心的记忆索引
            closest_idx_in_cluster = cluster_indices[np.argmax(similarities)]

            # 代表内容：取前 100 字
            full_content = documents[closest_idx_in_cluster] if documents else ""
            representative_content = full_content[:100]

            # 统计该簇中所有标签的频次，取 top-3
            tag_counter: Dict[str, int] = {}
            for idx in cluster_indices:
                tags_str = metadatas[idx].get("tags", "") if metadatas else ""
                if tags_str:
                    for tag in tags_str.split(","):
                        tag = tag.strip()
                        if tag:
                            tag_counter[tag] = tag_counter.get(tag, 0) + 1

            # 按频次降序排列，取 top-3
            top_tags = sorted(tag_counter.keys(), key=lambda t: tag_counter[t], reverse=True)[:3]

            cluster_results.append({
                "cluster_id": int(cluster_id),
                "size": int(cluster_size),
                "representative_content": representative_content,
                "top_tags": top_tags,
            })

        print(f"[MemoryVectorStore] 聚类完成: 项目={project_id}, 簇数={actual_n_clusters}, 总记忆={num_memories}")
        return cluster_results

    # ------------------------------------------------------------------
    # 记忆管理
    # ------------------------------------------------------------------

    def delete_memory(self, memory_id: str) -> None:
        """从向量存储中删除指定记忆。

        Args:
            memory_id: 要删除的记忆 ID
        """
        try:
            self.collection.delete(ids=[memory_id])
            print(f"[MemoryVectorStore] 记忆已删除: {memory_id}")
        except Exception as e:
            print(f"[MemoryVectorStore] 删除记忆失败 {memory_id}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取向量存储的统计信息。

        Returns:
            包含 total_vectors 和 collection_name 的字典
        """
        try:
            count = self.collection.count()
        except Exception:
            count = 0

        return {
            "total_vectors": count,
            "collection_name": self.COLLECTION_NAME,
        }

    def update_importance(self, memory_id: str, new_importance: float) -> None:
        """更新记忆的重要性评分（在 metadata 中）。

        Args:
            memory_id: 记忆 ID
            new_importance: 新的重要性评分（0.0 ~ 1.0）
        """
        try:
            self.collection.update(
                ids=[memory_id],
                metadatas=[{"importance": float(new_importance)}],
            )
            print(f"[MemoryVectorStore] 记忆重要性已更新: {memory_id} -> {new_importance}")
        except Exception as e:
            print(f"[MemoryVectorStore] 更新重要性失败 {memory_id}: {e}")