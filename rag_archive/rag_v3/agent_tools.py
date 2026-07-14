#!/usr/bin/env python3
"""
agent_tools.py - RAG Agent工具封装
提供 search_pdf, read_page, extract_table, quote_source, plan_query 等工具函数
"""

import os
import re
import json
import pickle
import warnings
import numpy as np
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")

# ============================================================
# 初始化：加载所有索引
# ============================================================
_OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载chunks
with open(os.path.join(_OUTPUT_DIR, "chunks.pkl"), "rb") as f:
    _chunks = pickle.load(f)

# 加载关键词索引
with open(os.path.join(_OUTPUT_DIR, "keyword_index.pkl"), "rb") as f:
    _keyword_index = pickle.load(f)

# 加载结构化索引
with open(os.path.join(_OUTPUT_DIR, "struct_index.json"), "r", encoding="utf-8") as f:
    _struct_index = json.load(f)

# 加载模型
from sentence_transformers import SentenceTransformer
import chromadb

_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
_chroma_client = chromadb.PersistentClient(path=os.path.join(_OUTPUT_DIR, "vector_db"))
_collection = _chroma_client.get_collection("pdf_chunks")

# TF-IDF组件
_tfidf_vectorizer = _keyword_index["tfidf_vectorizer"]
_tfidf_matrix = _keyword_index["tfidf_matrix"]
_inverted_index = _keyword_index["inverted_index"]
_proper_noun_index = _keyword_index["proper_noun_index"]
_jieba_texts = _keyword_index["jieba_texts"]

import jieba

# ============================================================
# 辅助函数
# ============================================================

def _vector_search(query: str, top_k: int = 10) -> list:
    """向量检索"""
    query_embedding = _model.encode([query])[0].tolist()
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    scored = []
    for i, chunk_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        # 余弦距离转相似度 (cosine距离 = 1 - cosine_similarity)
        similarity = 1.0 - distance
        metadata = results["metadatas"][0][i]
        scored.append({
            "chunk_id": chunk_id,
            "score": float(similarity),
            "document": results["documents"][0][i],
            "metadata": metadata
        })
    return scored

def _keyword_search(query: str, top_k: int = 10) -> list:
    """关键词检索"""
    words = list(jieba.cut(query))
    words = [w for w in words if len(w) >= 2]
    
    if not words:
        return []
    
    # 查找匹配的chunk
    chunk_scores = defaultdict(float)
    for word in words:
        if word in _inverted_index:
            for ci in _inverted_index[word]:
                chunk_scores[ci] += 1.0 / len(_inverted_index[word])
    
    # 排序
    sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    scored = []
    for ci, score in sorted_chunks:
        chunk = _chunks[ci]
        scored.append({
            "chunk_id": chunk["chunk_id"],
            "score": float(score),
            "document": chunk["text"],
            "metadata": {
                "chapter_num": chunk["chapter_num"],
                "chapter_title": chunk["chapter_title"],
                "section": chunk["section"],
                "context": chunk["context"],
                "pdf_pages": json.dumps(chunk["pdf_pages"]),
                "doc_pages": json.dumps(chunk["doc_pages"]),
                "content_type": chunk["content_type"]
            }
        })
    return scored

def _rrf_fusion(vector_results: list, keyword_results: list, k: int = 60, top_k: int = 10) -> list:
    """RRF (Reciprocal Rank Fusion) 融合"""
    scores = defaultdict(float)
    chunk_map = {}
    
    for rank, item in enumerate(vector_results):
        chunk_id = item["chunk_id"]
        scores[chunk_id] += 1.0 / (k + rank + 1)
        chunk_map[chunk_id] = item
    
    for rank, item in enumerate(keyword_results):
        chunk_id = item["chunk_id"]
        scores[chunk_id] += 1.0 / (k + rank + 1)
        if chunk_id not in chunk_map:
            chunk_map[chunk_id] = item
    
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    results = []
    for chunk_id, rrf_score in sorted_ids:
        item = chunk_map[chunk_id]
        item["rrf_score"] = float(rrf_score)
        results.append(item)
    
    return results

def _apply_filters(results: list, filters: dict) -> list:
    """应用过滤条件"""
    if not filters:
        return results
    
    filtered = []
    for item in results:
        metadata = item.get("metadata", {})
        match = True
        
        # 章节过滤
        if "chapter" in filters and filters["chapter"] is not None:
            if int(metadata.get("chapter_num", 0)) != int(filters["chapter"]):
                match = False
        
        # 页码范围过滤
        if "page_range" in filters and filters["page_range"]:
            pr = filters["page_range"]
            pdf_pages_str = metadata.get("pdf_pages", "[]")
            try:
                pdf_pages = json.loads(pdf_pages_str)
            except:
                pdf_pages = []
            if pdf_pages:
                if isinstance(pr, list) and len(pr) == 2:
                    if not any(pr[0] <= p <= pr[1] for p in pdf_pages):
                        match = False
                elif isinstance(pr, int):
                    if pr not in pdf_pages:
                        match = False
        
        # 类型过滤
        if "content_type" in filters and filters["content_type"]:
            if metadata.get("content_type") != filters["content_type"]:
                match = False
        
        if match:
            filtered.append(item)
    
    return filtered

# ============================================================
# 公开API
# ============================================================

def hybrid_search(query: str, filters: dict = None, top_k: int = 10) -> list:
    """
    混合检索：RRF融合向量检索和关键词检索
    
    Args:
        query: 查询文本
        filters: 过滤条件，如 {"chapter": 6, "page_range": [41, 50], "content_type": "text"}
        top_k: 返回结果数
    
    Returns:
        list of dict: [{"chunk_id", "score", "rrf_score", "document", "metadata"}]
    """
    if filters is None:
        filters = {}
    
    # 多检索一些结果用于融合
    search_k = max(top_k * 2, 20)
    
    vector_results = _vector_search(query, search_k)
    keyword_results = _keyword_search(query, search_k)
    
    # RRF融合
    fused = _rrf_fusion(vector_results, keyword_results, top_k=search_k)
    
    # 应用过滤
    filtered = _apply_filters(fused, filters)
    
    return filtered[:top_k]


def search_pdf(query: str, chapter: int = None, page_range: list = None, top_k: int = 5) -> list:
    """
    搜索PDF内容，返回带章节/页码/原文的片段
    
    Args:
        query: 查询文本
        chapter: 限定章节号（可选）
        page_range: 限定页码范围 [start, end]（可选）
        top_k: 返回结果数
    
    Returns:
        list of dict: 每个结果包含 chunk_id, chapter, page, context, text, score
    """
    filters = {}
    if chapter is not None:
        filters["chapter"] = chapter
    if page_range is not None:
        filters["page_range"] = page_range
    
    results = hybrid_search(query, filters=filters, top_k=top_k)
    
    formatted = []
    for item in results:
        metadata = item["metadata"]
        try:
            pdf_pages = json.loads(metadata.get("pdf_pages", "[]"))
        except:
            pdf_pages = []
        try:
            doc_pages = json.loads(metadata.get("doc_pages", "[]"))
        except:
            doc_pages = []
        
        formatted.append({
            "chunk_id": item["chunk_id"],
            "chapter": f"第{metadata.get('chapter_num', '?')}章 {metadata.get('chapter_title', '')}",
            "section": metadata.get("section", ""),
            "pdf_pages": pdf_pages,
            "doc_pages": doc_pages,
            "context": metadata.get("context", ""),
            "text": item["document"],
            "score": round(item.get("rrf_score", item.get("score", 0)), 4),
            "content_type": metadata.get("content_type", "text")
        })
    
    return formatted


def read_page(page_num: int) -> dict:
    """
    返回指定页码的完整内容
    
    Args:
        page_num: PDF页码
    
    Returns:
        dict: 包含页码、章节、内容的完整信息
    """
    page_chunks = [c for c in _chunks if page_num in c["pdf_pages"]]
    
    if not page_chunks:
        return {"error": f"第{page_num}页无内容", "page_num": page_num}
    
    combined_text = "\n\n".join([c["text"] for c in page_chunks])
    
    return {
        "page_num": page_num,
        "doc_page": page_chunks[0].get("doc_pages", [page_num])[0] if page_chunks[0].get("doc_pages") else page_num,
        "chapter": f"第{page_chunks[0]['chapter_num']}章 {page_chunks[0]['chapter_title']}",
        "section": page_chunks[0].get("section", ""),
        "content": combined_text,
        "chunk_count": len(page_chunks),
        "char_count": len(combined_text)
    }


def extract_table(table_id: str) -> dict:
    """
    返回结构化表格
    
    Args:
        table_id: 表格编号，如 "T-001"
    
    Returns:
        dict: 表格信息
    """
    for t in _struct_index.get("tables", []):
        if t["table_id"] == table_id:
            return {
                "table_id": t["table_id"],
                "chapter": f"第{t['chapter_num']}章 {t['chapter_title']}",
                "pdf_pages": t["pdf_pages"],
                "chunk_id": t["chunk_id"],
                "content": t["content"]
            }
    
    # 按编号搜索
    match = re.match(r"T-(\d+)", table_id)
    if match:
        idx = int(match.group(1)) - 1
        tables = _struct_index.get("tables", [])
        if 0 <= idx < len(tables):
            t = tables[idx]
            return {
                "table_id": t["table_id"],
                "chapter": f"第{t['chapter_num']}章 {t['chapter_title']}",
                "pdf_pages": t["pdf_pages"],
                "chunk_id": t["chunk_id"],
                "content": t["content"]
            }
    
    return {"error": f"表格 {table_id} 未找到", "table_id": table_id}


def quote_source(chunk_id: str) -> str:
    """
    返回格式化的引用字符串
    
    Args:
        chunk_id: 片段ID，如 "chunk_0001"
    
    Returns:
        str: 格式化的引用，如 "第6章 单片机综合设计A，第41页——原文：..."
    """
    for c in _chunks:
        if c["chunk_id"] == chunk_id:
            chapter_str = f"第{c['chapter_num']}章 {c['chapter_title']}"
            section_str = f", {c['section']}" if c.get("section") else ""
            doc_pages = c.get("doc_pages", [c.get("doc_page", "?")])
            page_str = f"第{'、'.join(str(p) for p in doc_pages)}页"
            text_preview = c["text"][:200].replace("\n", " ") + ("..." if len(c["text"]) > 200 else "")
            return f"{chapter_str}{section_str}，{page_str}——原文：{text_preview}"
    
    return f"未找到片段: {chunk_id}"


def plan_query(query: str) -> dict:
    """
    分析查询意图，规划检索路径
    
    Args:
        query: 用户查询
    
    Returns:
        dict: 包含意图分析、检索策略、推荐参数
    """
    # 意图分类
    intent_patterns = {
        "时间查询": ["什么时候", "时间", "日期", "答辩", "几点"],
        "成绩查询": ["成绩", "组成", "评分", "分数", "占比"],
        "题目查询": ["题目", "有哪些", "实验内容", "选题", "选一"],
        "实验查询": ["实验", "接口", "基本", "预备"],
        "器件查询": ["DS18B20", "ADC", "怎么用", "使用", "传感器", "LCD", "数码管"],
        "格式查询": ["格式", "报告", "模板", "要求", "字体", "排版"],
        "章节查询": ["第几章", "章节", "目录"],
        "概念查询": ["是什么", "定义", "原理"],
    }
    
    detected_intents = []
    for intent, keywords in intent_patterns.items():
        for kw in keywords:
            if kw.lower() in query.lower():
                detected_intents.append(intent)
                break
    
    if not detected_intents:
        detected_intents = ["通用查询"]
    
    # 检索策略
    strategies = []
    ch_filters = []
    
    if "时间查询" in detected_intents:
        strategies.append("优先检索前言/课程安排部分（第1-3页）")
        ch_filters.append(1)
    
    if "成绩查询" in detected_intents:
        strategies.append("优先检索前言/总体要求部分（第1-3页）")
        ch_filters.append(1)
    
    if "题目查询" in detected_intents:
        if "综合设计A" in query or "A" in query:
            strategies.append("检索第6章 单片机综合设计A")
            ch_filters.append(6)
        elif "综合设计B" in query or "B" in query:
            strategies.append("检索第7章 单片机综合设计B")
            ch_filters.append(7)
        else:
            strategies.append("检索第6章和第7章")
            ch_filters.extend([6, 7])
    
    if "实验查询" in detected_intents:
        if "基本" in query:
            strategies.append("检索第3-5章 基本实验")
            ch_filters.extend([3, 4, 5])
        elif "预备" in query:
            strategies.append("检索第2章 预备实验")
            ch_filters.append(2)
    
    if "器件查询" in detected_intents:
        strategies.append("检索第5章 基本传感实验 + 第4章 基本接口实验")
        ch_filters.extend([4, 5])
    
    if "格式查询" in detected_intents:
        strategies.append("检索第11章 实验报告模板及要求")
        ch_filters.append(11)
    
    if "章节查询" in detected_intents:
        strategies.append("检索目录部分（第4-6页）")
    
    # 推荐检索参数
    recommended_params = {
        "use_hybrid": True,
        "top_k": 5,
        "chapters": ch_filters if ch_filters else None,
        "page_range": None,
        "content_type": None
    }
    
    return {
        "query": query,
        "detected_intents": detected_intents,
        "search_strategies": strategies,
        "recommended_params": recommended_params,
        "explanation": f"检测到意图: {', '.join(detected_intents)}。{'; '.join(strategies)}"
    }


# ============================================================
# 便捷函数
# ============================================================

def get_chapter_outline(chapter_num: int) -> dict:
    """获取章节大纲"""
    ch_key = str(chapter_num)
    if ch_key in _struct_index["chapters"]:
        ch_info = _struct_index["chapters"][ch_key]
        return {
            "chapter": f"第{chapter_num}章 {ch_info['chapter_title']}",
            "total_chunks": ch_info["total_chunks"],
            "sections": list(ch_info["sections"].keys()),
            "pdf_pages": ch_info["pdf_pages"]
        }
    return {"error": f"章节{chapter_num}不存在"}


def list_all_tables() -> list:
    """列出所有表格"""
    return [{
        "table_id": t["table_id"],
        "chapter": f"第{t['chapter_num']}章 {t['chapter_title']}",
        "pdf_pages": t["pdf_pages"],
        "preview": t["content"][:100].replace("\n", " ")
    } for t in _struct_index.get("tables", [])]


def get_document_info() -> dict:
    """获取文档基本信息"""
    return _struct_index.get("document_info", {})


if __name__ == "__main__":
    # 测试工具函数
    print("=== Agent Tools 测试 ===\n")
    
    info = get_document_info()
    print(f"文档: {info.get('title', 'N/A')}")
    print(f"总页数: {info.get('total_pages', 'N/A')}")
    print(f"总Chunks: {info.get('total_chunks', 'N/A')}")
    
    # 测试意图分析
    print("\n--- plan_query 测试 ---")
    for q in ["答辩时间是什么时候", "成绩怎么组成", "DS18B20怎么用"]:
        plan = plan_query(q)
        print(f"\n查询: {q}")
        print(f"  意图: {plan['detected_intents']}")
        print(f"  策略: {plan['search_strategies']}")
    
    # 测试搜索
    print("\n--- search_pdf 测试 ---")
    results = search_pdf("答辩时间", top_k=3)
    for r in results:
        print(f"  [{r['score']:.4f}] {r['chapter']} | {r['context']}")
        print(f"    文本: {r['text'][:100]}...")
    
    print("\n所有工具函数就绪。")
