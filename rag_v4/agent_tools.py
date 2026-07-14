#!/usr/bin/env python3
"""
agent_tools.py - RAG v4 Agent工具封装
三层架构：召回层 + 融合层 + 精排层
提供 search_pdf, read_page, extract_table, quote_source, compare, smart_answer
"""

import os
import sys
import re
import json
import pickle
import warnings
import numpy as np
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")

# ============================================================
# 初始化：加载所有索引（与 v3 兼容）
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

# 加载agent_b的结构化表格数据（如果存在）
_tables_data = []
_tables_path = "/data/user/work/agent_b_tables.json"
if os.path.exists(_tables_path):
    with open(_tables_path, "r", encoding="utf-8") as f:
        _tables_data = json.load(f)

# 构建chunk查找索引
_chunk_by_id = {c["chunk_id"]: c for c in _chunks}
_chunks_by_page = defaultdict(list)
for c in _chunks:
    for p in c.get("pdf_pages", []):
        _chunks_by_page[p].append(c)

# 关键词-章节映射（用于意图路由）
_KEYWORD_CHAPTER_MAP = {
    "答辩": [0, 1, 2],            # 前置/课程安排
    "成绩": [0, 1, 2],            # 前置/成绩组成
    "评分": [0, 1, 2],
    "综合设计A": [6],             # 第6章
    "综合设计B": [7],             # 第7章
    "基本接口": [4],              # 第4章
    "基本语言": [3],              # 第3章
    "基本传感": [5],              # 第5章
    "DS18B20": [5],              # 第5章
    "DS1302": [5],
    "DHT11": [5],
    "LCD": [4],
    "数码管": [4],
    "矩阵键盘": [4],
    "AD": [4],
    "DA": [4],
    "PWM": [4],
    "蜂鸣器": [4],
    "定时器": [4],
    "中断": [4],
    "报告": [11],                 # 第11章
    "格式": [11],
    "模板": [11],
    "Keil": [9],                  # 第9章
    "Proteus": [9],
    "STC": [9],
    "烧录": [9],
    "原理图": [8],                # 第8章
    "硬件": [8],
    "验收": [6, 7],              # 第6章+第7章
    "答辩考试": [0, 1, 2],
    "时间安排": [0, 1, 2],
    "题目": [6, 7],
    "选题": [6, 7],
}


# ============================================================
# 第1层：召回层 (multi_recall)
# ============================================================

def _vector_recall(query: str, top_k: int = 20) -> list:
    """向量语义召回"""
    query_embedding = _model.encode([query])[0].tolist()
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, _collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    scored = []
    for i, chunk_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        similarity = 1.0 - distance
        metadata = results["metadatas"][0][i]
        scored.append({
            "chunk_id": chunk_id,
            "score": float(similarity),
            "document": results["documents"][0][i],
            "metadata": metadata,
            "source": "vector"
        })
    return scored


def _keyword_recall(query: str, top_k: int = 20) -> list:
    """关键词TF-IDF召回"""
    words = list(jieba.cut(query))
    words = [w for w in words if len(w) >= 2]

    if not words:
        return []

    chunk_scores = defaultdict(float)
    for word in words:
        if word in _inverted_index:
            for ci in _inverted_index[word]:
                chunk_scores[ci] += 1.0 / len(_inverted_index[word])

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
            },
            "source": "keyword"
        })
    return scored


def _structured_recall(query: str, top_k: int = 10) -> list:
    """结构化召回：基于章节-关键词映射直接定位"""
    results = []
    query_lower = query.lower()

    # 查找匹配的章节号
    matched_chapters = set()
    for kw, chapters in _KEYWORD_CHAPTER_MAP.items():
        if kw.lower() in query_lower:
            matched_chapters.update(chapters)

    if not matched_chapters:
        # 尝试通用关键词匹配
        for kw in ["实验", "设计", "综合", "基本", "预备", "前言"]:
            if kw in query:
                if kw == "实验":
                    matched_chapters.update([3, 4, 5])
                elif kw == "综合":
                    matched_chapters.update([6, 7])
                elif kw == "基本":
                    matched_chapters.update([3, 4, 5])
                elif kw == "预备":
                    matched_chapters.add(2)
                elif kw == "前言":
                    matched_chapters.add(0)

    if matched_chapters:
        for c in _chunks:
            if c["chapter_num"] in matched_chapters:
                results.append({
                    "chunk_id": c["chunk_id"],
                    "score": 1.0,
                    "document": c["text"],
                    "metadata": {
                        "chapter_num": c["chapter_num"],
                        "chapter_title": c["chapter_title"],
                        "section": c["section"],
                        "context": c["context"],
                        "pdf_pages": json.dumps(c["pdf_pages"]),
                        "doc_pages": json.dumps(c["doc_pages"]),
                        "content_type": c["content_type"]
                    },
                    "source": "structured"
                })
        results = results[:top_k]

    return results


def _table_recall(query: str, top_k: int = 5) -> list:
    """表格专属召回：匹配结构化表格数据"""
    results = []
    query_lower = query.lower()

    for table in _tables_data:
        caption = table.get("caption", "").lower()
        table_id = table.get("table_id", "").lower()
        # 检查表头
        headers = " ".join(table.get("headers", [])).lower()
        # 检查行内容
        all_text = caption + " " + table_id + " " + headers
        for row in table.get("rows", []):
            all_text += " " + " ".join(row).lower()

        # 关键词匹配
        score = 0.0
        words = list(jieba.cut(query_lower))
        for w in words:
            if len(w) >= 2 and w in all_text:
                score += 1.0
        if score > 0:
            results.append({
                "table_id": table.get("table_id", ""),
                "score": score,
                "page": table.get("page", "?"),
                "chapter": table.get("chapter", ""),
                "caption": table.get("caption", ""),
                "headers": table.get("headers", []),
                "rows": table.get("rows", []),
                "source": "table"
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def multi_recall(query: str, top_k: int = 20, filters: dict = None) -> dict:
    """
    多路召回：向量 + 关键词 + 结构化 + 表格
    返回各路召回结果
    """
    k = max(top_k, 20)

    results = {
        "vector": _vector_recall(query, k),
        "keyword": _keyword_recall(query, k),
        "structured": _structured_recall(query, k),
        "table": _table_recall(query, k)
    }

    return results


# ============================================================
# 第2层：融合层 (fusion)
# ============================================================

def _rrf_fusion(recall_results: dict, k: int = 60, weights: dict = None) -> list:
    """
    RRF (Reciprocal Rank Fusion) 加权融合
    weights: {"vector": 1.0, "keyword": 0.8, "structured": 0.6, "table": 0.5}
    """
    if weights is None:
        weights = {"vector": 1.0, "keyword": 0.8, "structured": 0.6, "table": 0.5}

    scores = defaultdict(float)
    chunk_map = {}

    for source_key, source_results in recall_results.items():
        w = weights.get(source_key, 0.5)
        for rank, item in enumerate(source_results):
            if "chunk_id" in item:
                chunk_id = item["chunk_id"]
                scores[chunk_id] += w / (k + rank + 1)
                if chunk_id not in chunk_map:
                    chunk_map[chunk_id] = item
            elif "table_id" in item:
                # 表格结果用特殊ID
                tid = "TABLE_" + item["table_id"]
                scores[tid] += w / (k + rank + 1)
                if tid not in chunk_map:
                    chunk_map[tid] = item

    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    fused = []
    for chunk_id, rrf_score in sorted_ids:
        item = chunk_map[chunk_id]
        item["rrf_score"] = float(rrf_score)
        fused.append(item)

    return fused


# ============================================================
# 第3层：精排层 (rerank)
# ============================================================

def analyze_intent(query: str) -> dict:
    """
    意图分析：识别查询类型
    返回 {"type": "concept|table|exact|compare", "chapters": [...], "keywords": [...]}
    """
    query_lower = query.lower()
    query_upper = query.upper()

    # 意图分类规则（按优先级）
    intent_type = "concept"  # 默认概念查询
    intent_confidence = 0.5

    # 对比意图 -- 优先级最高
    compare_patterns = ["哪个", "区别", "对比", "比较", "哪个更", "哪个简单", "哪个难", "还是"]
    if any(p in query for p in compare_patterns):
        intent_type = "compare"
        intent_confidence = 0.9

    # 表格意图
    if intent_type == "concept":
        table_patterns = ["组成", "占比", "表格", "怎么组成", "有哪些项目", "评分标准", "成绩怎么"]
        if any(p in query for p in table_patterns):
            intent_type = "table"
            intent_confidence = 0.85

    # 精确匹配意图（专有名词、编号、特定章节）
    # "有哪些" 是列举型精确查询；"怎么用"、"是什么" 是概念型
    if intent_type == "concept":
        # 列举型精确查询
        exact_patterns = ["P-A-", "P-B-", "综合设计A", "综合设计B", "基本接口实验", "基本语言实验", "基本传感实验"]
        has_exact = any(p in query for p in exact_patterns)
        has_list = any(p in query for p in ["有哪些", "哪些题目", "哪些实验", "什么题目"])
        if has_exact or has_list:
            # 但如果包含"怎么用"、"是什么"等概念型问法，则不算exact
            concept_override = any(p in query for p in ["怎么用", "是什么", "什么意思", "如何理解"])
            if not concept_override:
                intent_type = "exact"
                intent_confidence = 0.8

    # DS18B20等专有名词：默认exact，但"怎么用"类问题算concept
    if intent_type == "concept":
        device_patterns = ["DS18B20", "DS1302", "DHT11", "LCD", "AT24C"]
        if any(p in query_upper for p in device_patterns):
            if any(p in query for p in ["怎么用", "如何使用", "用法", "是什么"]):
                intent_type = "concept"
                intent_confidence = 0.7
            else:
                intent_type = "exact"
                intent_confidence = 0.8

    # 提取关键词
    keywords = []
    for kw, chapters in _KEYWORD_CHAPTER_MAP.items():
        if kw.lower() in query_lower:
            keywords.append(kw)

    if not keywords:
        words = list(jieba.cut(query))
        keywords = [w for w in words if len(w) >= 2]

    # 确定目标章节
    chapters = set()
    for kw in keywords:
        if kw in _KEYWORD_CHAPTER_MAP:
            chapters.update(_KEYWORD_CHAPTER_MAP[kw])

    if not chapters:
        chapters = set(range(0, 12))  # 全文档

    return {
        "type": intent_type,
        "confidence": intent_confidence,
        "keywords": keywords,
        "chapters": sorted(chapters),
        "query": query
    }


def rewrite_query(query: str, intent: dict) -> str:
    """
    查询改写：根据意图优化查询词
    """
    if intent["type"] == "table":
        # 表格查询：添加结构化关键词
        return query + " 表格 组成 占比 评分"

    elif intent["type"] == "exact":
        # 精确查询：提取专有名词
        return query

    elif intent["type"] == "compare":
        # 对比查询：保留原查询
        return query

    elif intent["type"] == "concept":
        # 概念查询：添加相关术语
        return query

    return query


def coarse_filter(fused_results: list, intent: dict, top_k: int = 5) -> list:
    """
    粗过滤：根据意图类型筛选和排序
    """
    if not fused_results:
        return []

    intent_type = intent["type"]
    target_chapters = set(intent.get("chapters", []))

    scored = []
    for item in fused_results:
        score = item.get("rrf_score", item.get("score", 0))

        # 章节加分
        if "metadata" in item:
            ch_num = int(item["metadata"].get("chapter_num", -1))
            if ch_num in target_chapters:
                score *= 1.5  # 目标章节加权

        # 表格意图：优先表格结果
        if intent_type == "table" and "table_id" in item:
            score *= 2.0

        # 精确匹配加分
        if intent_type == "exact":
            text = item.get("document", "")
            for kw in intent.get("keywords", []):
                if kw.upper() in text.upper():
                    score *= 1.3
                    break

        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def search(query: str, top_k: int = 5, weights: dict = None) -> list:
    """
    完整三层流水线：召回 -> 融合 -> 精排
    """
    # 第1层：意图分析
    intent = analyze_intent(query)

    # 第2层：查询改写
    rewritten = rewrite_query(query, intent)

    # 第3层：多路召回
    recall_results = multi_recall(rewritten, top_k=top_k * 2)

    # 第4层：RRF融合
    fused = _rrf_fusion(recall_results, weights=weights)

    # 第5层：粗过滤+精排
    reranked = coarse_filter(fused, intent, top_k=top_k)

    return reranked


# ============================================================
# 工具1：主检索 search_pdf
# ============================================================

def search_pdf(query: str, top_k: int = 5) -> list:
    """
    完整三层流水线检索，返回带引用的结果

    Args:
        query: 查询文本
        top_k: 返回结果数

    Returns:
        list of dict: 每个结果包含 chunk_id, chapter, section, pdf_pages,
                      doc_pages, context, text, score, content_type, citation
    """
    results = search(query, top_k=top_k)

    formatted = []
    for item in results:
        if "table_id" in item:
            # 表格结果
            formatted.append({
                "type": "table",
                "table_id": item["table_id"],
                "page": item.get("page", "?"),
                "chapter": item.get("chapter", ""),
                "caption": item.get("caption", ""),
                "headers": item.get("headers", []),
                "rows": item.get("rows", []),
                "score": round(item.get("rrf_score", item.get("score", 0)), 4),
                "citation": f"第{item.get('chapter', '?')}，第{item.get('page', '?')}页——表格：{item.get('caption', '')}",
                "source": item.get("source", "table")
            })
        else:
            # 文本chunk结果
            metadata = item.get("metadata", {})
            try:
                pdf_pages = json.loads(metadata.get("pdf_pages", "[]"))
            except:
                pdf_pages = []
            try:
                doc_pages = json.loads(metadata.get("doc_pages", "[]"))
            except:
                doc_pages = []

            chunk_id = item.get("chunk_id", "")
            chapter_num = metadata.get("chapter_num", "?")
            chapter_title = metadata.get("chapter_title", "")
            section = metadata.get("section", "")
            context = metadata.get("context", "")
            text = item.get("document", "")
            score = round(item.get("rrf_score", item.get("score", 0)), 4)

            # 生成引用
            chapter_str = f"第{chapter_num}章" if chapter_num != 0 else "前置"
            if chapter_title:
                chapter_str += f" {chapter_title}"
            section_str = f", {section}" if section else ""
            pages_str = f"第{'、'.join(str(p) for p in doc_pages) if doc_pages else '、'.join(str(p) for p in pdf_pages)}页"
            citation = f"{chapter_str}{section_str}，{pages_str}"

            formatted.append({
                "type": "text",
                "chunk_id": chunk_id,
                "chapter": chapter_str,
                "section": section,
                "pdf_pages": pdf_pages,
                "doc_pages": doc_pages,
                "context": context,
                "text": text,
                "score": score,
                "content_type": metadata.get("content_type", "text"),
                "citation": citation,
                "source": item.get("source", "fusion")
            })

    return formatted


# ============================================================
# 工具2：读指定页 read_page
# ============================================================

def read_page(page_num: int) -> dict:
    """
    返回指定PDF页码的所有chunk内容

    Args:
        page_num: PDF页码

    Returns:
        dict: 包含页码、章节、内容、chunk数等
    """
    page_chunks = _chunks_by_page.get(page_num, [])

    if not page_chunks:
        return {"error": f"第{page_num}页无内容", "page_num": page_num}

    combined_text = "\n\n".join([c["text"] for c in page_chunks])

    return {
        "page_num": page_num,
        "doc_page": page_chunks[0].get("doc_pages", [page_num])[0] if page_chunks[0].get("doc_pages") else page_num,
        "chapter": f"第{page_chunks[0]['chapter_num']}章 {page_chunks[0]['chapter_title']}" if page_chunks[0]["chapter_num"] != 0 else f"前置 {page_chunks[0]['chapter_title']}",
        "section": page_chunks[0].get("section", ""),
        "content": combined_text,
        "chunk_count": len(page_chunks),
        "char_count": len(combined_text)
    }


# ============================================================
# 工具3：抽表 extract_table
# ============================================================

def extract_table(table_keyword: str) -> list:
    """
    根据关键词提取结构化表格

    Args:
        table_keyword: 表格关键词，如 "成绩"、"课程安排"、"元件对照"

    Returns:
        list of dict: 匹配的表格列表
    """
    results = []
    kw_lower = table_keyword.lower()

    # 从问题中提取多个关键词（分词+过滤）
    kw_words = list(jieba.cut(kw_lower))
    kw_words = [w for w in kw_words if len(w) >= 2]

    for table in _tables_data:
        caption = table.get("caption", "").lower()
        table_id = table.get("table_id", "").lower()
        headers = " ".join(table.get("headers", [])).lower()
        all_text = caption + " " + table_id + " " + headers

        # 匹配：任一关键词命中即认为匹配
        matched = False
        for w in kw_words:
            if w in all_text:
                matched = True
                break
        # 也尝试完整关键词匹配
        if not matched and kw_lower in all_text:
            matched = True

        if matched:
            results.append({
                "table_id": table.get("table_id", ""),
                "page": table.get("page", "?"),
                "chapter": table.get("chapter", ""),
                "caption": table.get("caption", ""),
                "headers": table.get("headers", []),
                "rows": table.get("rows", []),
                "citation": f"{table.get('chapter', '?')}，第{table.get('page', '?')}页——表格：{table.get('caption', '')}"
            })

    return results


# ============================================================
# 工具4：生成引用 quote_source
# ============================================================

def quote_source(result: dict) -> str:
    """
    返回格式化的引用字符串

    Args:
        result: search_pdf 返回的单个结果dict

    Returns:
        str: 格式化的引用
    """
    if result.get("type") == "table":
        return result.get("citation", "")

    chunk_id = result.get("chunk_id", "")
    chunk = _chunk_by_id.get(chunk_id)

    if not chunk:
        return f"未找到片段: {chunk_id}"

    chapter_num = chunk["chapter_num"]
    chapter_title = chunk["chapter_title"]
    section = chunk.get("section", "")
    doc_pages = chunk.get("doc_pages", chunk.get("pdf_pages", []))
    text = chunk["text"]

    chapter_str = f"第{chapter_num}章" if chapter_num != 0 else "前置"
    if chapter_title:
        chapter_str += f" {chapter_title}"
    section_str = f"-{section}" if section else ""
    pages_str = f"第{'、'.join(str(p) for p in doc_pages)}页"
    text_preview = text[:200].replace("\n", " ") + ("..." if len(text) > 200 else "")

    return f"{chapter_str}{section_str}，{pages_str}——原文：{text_preview}"


# ============================================================
# 工具5：对比查询 compare
# ============================================================

def compare(query_a: str, query_b: str) -> dict:
    """
    跨章节对比，分别检索后返回对比表格

    Args:
        query_a: 第一个查询
        query_b: 第二个查询

    Returns:
        dict: 包含对比表格和两个查询的结果
    """
    results_a = search_pdf(query_a, top_k=3)
    results_b = search_pdf(query_b, top_k=3)

    # 提取对比信息
    compare_rows = []
    for i in range(max(len(results_a), len(results_b))):
        row = {}
        if i < len(results_a):
            ra = results_a[i]
            row["A_章节"] = ra.get("citation", "")
            row["A_内容"] = ra.get("text", "")[:100].replace("\n", " ")
        else:
            row["A_章节"] = "-"
            row["A_内容"] = "-"

        if i < len(results_b):
            rb = results_b[i]
            row["B_章节"] = rb.get("citation", "")
            row["B_内容"] = rb.get("text", "")[:100].replace("\n", " ")
        else:
            row["B_章节"] = "-"
            row["B_内容"] = "-"

        compare_rows.append(row)

    return {
        "query_a": query_a,
        "query_b": query_b,
        "results_a": results_a,
        "results_b": results_b,
        "comparison_table": compare_rows
    }


# ============================================================
# 工具6：意图路由 smart_answer
# ============================================================

def smart_answer(question: str) -> dict:
    """
    根据意图自动选择工具链

    Args:
        question: 用户问题

    Returns:
        dict: 包含意图分析、路由决策、检索结果
    """
    intent = analyze_intent(question)

    result = {
        "question": question,
        "intent": intent,
        "route": "",
        "answer": None
    }

    if intent["type"] == "table":
        result["route"] = "extract_table"
        # 用关键词提取表格
        tables = extract_table(question)
        result["answer"] = {
            "tables": tables,
            "count": len(tables)
        }

    elif intent["type"] == "compare":
        result["route"] = "compare"
        # 提取对比查询中的两个元素
        import re as _re
        # 多种分割方式
        parts = _re.split(r'哪个|和|还是|对比|比较|哪个更|哪个简单|哪个难', question)
        parts = [p.strip().rstrip("?？。， ") for p in parts if p.strip()]
        if len(parts) >= 2:
            qa = parts[0]
            qb = parts[1]
            result["answer"] = compare(qa, qb)
        else:
            result["answer"] = search_pdf(question, top_k=5)

    elif intent["type"] == "exact":
        result["route"] = "search_pdf"
        result["answer"] = search_pdf(question, top_k=5)

    else:  # concept
        result["route"] = "search_pdf"
        result["answer"] = search_pdf(question, top_k=5)

    return result


# ============================================================
# 便捷函数
# ============================================================

def get_chapter_outline(chapter_num: int) -> dict:
    """获取章节大纲"""
    ch_key = str(chapter_num)
    if ch_key in _struct_index.get("chapters", {}):
        ch_info = _struct_index["chapters"][ch_key]
        return {
            "chapter": f"第{chapter_num}章 {ch_info.get('chapter_title', '')}",
            "total_chunks": ch_info.get("total_chunks", 0),
            "sections": list(ch_info.get("sections", {}).keys()),
            "pdf_pages": ch_info.get("pdf_pages", [])
        }
    return {"error": f"章节{chapter_num}不存在"}


def list_all_tables() -> list:
    """列出所有表格"""
    return [{
        "table_id": t.get("table_id", ""),
        "chapter": t.get("chapter", ""),
        "page": t.get("page", "?"),
        "caption": t.get("caption", ""),
        "preview": str(t.get("headers", []))[:100]
    } for t in _tables_data]


def get_document_info() -> dict:
    """获取文档基本信息"""
    return _struct_index.get("document_info", {
        "title": "单片机工程实训任务书",
        "total_pages": 78,
        "total_chunks": len(_chunks)
    })


# ============================================================
# 自测
# ============================================================

if __name__ == "__main__":
    print("=== RAG v4 Agent Tools 自测 ===\n")

    info = get_document_info()
    print(f"文档: {info.get('title', 'N/A')}")
    print(f"总页数: {info.get('total_pages', 'N/A')}")
    print(f"总Chunks: {info.get('total_chunks', 'N/A')}")
    print(f"表格数据: {len(_tables_data)} 个")
    print(f"向量集合: {_collection.count()} 条")

    print("\n--- 意图分析测试 ---")
    for q in ["答辩时间是什么时候？", "成绩怎么组成？", "DS18B20怎么用？", "P-A-3#和P-A-1#哪个简单？"]:
        intent = analyze_intent(q)
        print(f"  [{intent['type']}] {q} -> 章节: {intent['chapters']}")

    print("\n--- 多路召回测试 ---")
    recall = multi_recall("答辩时间", top_k=5)
    print(f"  向量召回: {len(recall['vector'])} 条")
    print(f"  关键词召回: {len(recall['keyword'])} 条")
    print(f"  结构化召回: {len(recall['structured'])} 条")
    print(f"  表格召回: {len(recall['table'])} 条")

    print("\n--- search_pdf 测试 ---")
    results = search_pdf("答辩时间是什么时候？", top_k=3)
    for r in results:
        print(f"  [{r['score']:.4f}] {r['citation']}")
        print(f"    原文: {r['text'][:100]}...")

    print("\n--- read_page 测试 ---")
    page = read_page(2)
    print(f"  第2页: {page['chapter']}, {page['char_count']}字")

    print("\n--- extract_table 测试 ---")
    tables = extract_table("成绩")
    for t in tables:
        print(f"  {t['table_id']}: {t['caption']} ({t['page']}页, {len(t['rows'])}行)")

    print("\n--- compare 测试 ---")
    comp = compare("P-A-3#", "P-A-1#")
    print(f"  对比结果行数: {len(comp['comparison_table'])}")

    print("\n--- smart_answer 测试 ---")
    for q in ["成绩怎么组成？", "P-A-3#和P-A-1#哪个简单？", "答辩时间是什么时候？"]:
        sa = smart_answer(q)
        print(f"  [{sa['route']}] {q}")

    print("\n所有工具函数就绪。")