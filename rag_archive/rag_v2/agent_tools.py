#!/usr/bin/env python3
"""
第五步：封装Agent工具
提供 search_pdf, read_page, extract_table, analyze_chart, quote_source, plan_query 等工具函数
"""
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import json
import re
import pickle
import sys
import numpy as np

# ============================================================
# 0. 初始化：加载索引和模型
# ============================================================
BASE_DIR = "/workspace/rag_v2"
CHUNKS_PATH = "/data/user/work/pdf_semantic_chunks.json"
DOC_TREE_PATH = "/data/user/work/pdf_document_tree.json"

# Lazy loading for heavy models
_model = None
_collection = None
_inverted_index = None
_struct_index = None
_chunks_data = None
_doc_tree = None
_tfidf_vectorizer = None
_feature_names = None

def _ensure_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _ensure_collection():
    global _collection
    if _collection is None:
        import chromadb
        chroma_client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "vector_db"))
        _collection = chroma_client.get_collection("pdf_chunks")
    return _collection

def _ensure_keyword_index():
    global _inverted_index, _tfidf_vectorizer, _feature_names
    if _inverted_index is None:
        with open(os.path.join(BASE_DIR, "keyword_index.pkl"), "rb") as f:
            kw_data = pickle.load(f)
        _inverted_index = kw_data["inverted_index"]
        _feature_names = kw_data.get("feature_names", [])
    return _inverted_index

def _ensure_struct_index():
    global _struct_index
    if _struct_index is None:
        with open(os.path.join(BASE_DIR, "struct_index.json"), "r", encoding="utf-8") as f:
            _struct_index = json.load(f)
    return _struct_index

def _ensure_chunks():
    global _chunks_data
    if _chunks_data is None:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            _chunks_data = json.load(f)
    return _chunks_data

def _ensure_doc_tree():
    global _doc_tree
    if _doc_tree is None:
        with open(DOC_TREE_PATH, "r", encoding="utf-8") as f:
            _doc_tree = json.load(f)
    return _doc_tree

# ============================================================
# 1. search_pdf - 混合检索
# ============================================================
def search_pdf(query, chapter=None, chapter_num=None, page_range=None, page_type=None, top_k=5):
    """
    混合检索，返回带引用的相关片段
    
    Args:
        query: 查询文本
        chapter: 按章节过滤（如 "第6章"）
        chapter_num: 按章节号过滤（如 6）
        page_range: 页码范围 [min, max]
        page_type: 页面类型过滤（"text", "table", "image"）
        top_k: 返回结果数量
    
    Returns:
        list of dicts: [{"chunk_id": "ch_0001", "content": "...", "page": 8, "chapter": "第4章", "section": "4.1", "score": 0.95}]
    """
    model = _ensure_model()
    collection = _ensure_collection()
    inv_index = _ensure_keyword_index()
    struct_idx = _ensure_struct_index()
    
    # Build filters
    filters = {}
    if chapter:
        filters["chapter"] = chapter
    if chapter_num is not None:
        filters["chapter_num"] = chapter_num
    if page_range:
        filters["page_range"] = page_range
    if page_type:
        filters["page_type"] = [page_type]
    
    import jieba
    chip_pattern = re.compile(r'\b(?:[A-Z]{2,}\d{2,}[A-Z]?\d*|AT89C\d+|STC\d+[A-Z]*|DS\d+[A-Z]*|ADC\d+|DAC\d+|LCD\d+|PCF\d+|ULN\d+|MAX\d+|74HC\d+)\b', re.IGNORECASE)
    
    def jieba_tokenizer(text):
        text_lower = text.lower()
        tokens = list(jieba.cut(text_lower))
        return [t.strip() for t in tokens if len(t.strip()) >= 1]
    
    # --- Vector search ---
    query_embedding = model.encode([query]).tolist()
    vec_results = collection.query(
        query_embeddings=query_embedding,
        n_results=30,
        include=["documents", "metadatas", "distances"]
    )
    
    vec_scored = []
    if vec_results["ids"] and vec_results["ids"][0]:
        for i in range(len(vec_results["ids"][0])):
            distance = vec_results["distances"][0][i]
            similarity = 1.0 - distance
            vec_scored.append({
                "chunk_id": vec_results["ids"][0][i],
                "content": vec_results["documents"][0][i],
                "metadata": vec_results["metadatas"][0][i],
                "score": similarity
            })
    
    # --- Keyword search ---
    query_tokens = jieba_tokenizer(query)
    query_lower = query.lower()
    chip_matches = chip_pattern.findall(query_lower)
    all_query_terms = set(query_tokens + [m.upper() for m in chip_matches])
    
    chunk_scores = {}
    chunks_lookup = struct_idx.get("chunk_lookup", {})
    for term in all_query_terms:
        if term in inv_index:
            cids = inv_index[term]
            idf = len(chunks_lookup) / max(len(cids), 1)
            for cid in cids:
                chunk_scores[cid] = chunk_scores.get(cid, 0) + idf
    
    sorted_kw = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:30]
    
    kw_scored = []
    for cid, score in sorted_kw:
        chunk = chunks_lookup.get(cid)
        if chunk:
            kw_scored.append({
                "chunk_id": cid,
                "content": chunk.get("content", ""),
                "metadata": {
                    "chunk_id": chunk.get("chunk_id", cid),
                    "type": chunk.get("type", ""),
                    "chapter": chunk.get("chapter", ""),
                    "chapter_num": chunk.get("chapter_num", 0),
                    "section": chunk.get("section") or "",
                    "page": chunk.get("page", 0),
                    "context": chunk.get("context", "")
                },
                "score": score
            })
    
    # --- RRF fusion ---
    k = 60
    rrf_scores = {}
    chunk_data = {}
    
    for rank, item in enumerate(vec_scored):
        cid = item["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)
        chunk_data[cid] = item
    
    for rank, item in enumerate(kw_scored):
        cid = item["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)
        if cid not in chunk_data:
            chunk_data[cid] = item
    
    sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k * 2]
    
    # Apply filters
    filtered = []
    for cid, rrf_score in sorted_rrf:
        item = chunk_data[cid]
        meta = item["metadata"]
        match = True
        
        if chapter and chapter not in meta.get("chapter", ""):
            match = False
        if chapter_num is not None and meta.get("chapter_num") != chapter_num:
            match = False
        if page_range and (meta.get("page", 0) < page_range[0] or meta.get("page", 0) > page_range[1]):
            match = False
        if page_type and meta.get("type") not in [page_type]:
            match = False
        
        if match:
            item["rrf_score"] = rrf_score
            filtered.append(item)
    
    # Format results
    formatted = []
    for item in filtered[:top_k]:
        meta = item["metadata"]
        formatted.append({
            "chunk_id": item["chunk_id"],
            "content": item["content"],
            "page": meta.get("page", 0),
            "chapter": meta.get("chapter", ""),
            "section": meta.get("section", ""),
            "score": round(item.get("rrf_score", 0), 4)
        })
    
    return formatted

# ============================================================
# 2. read_page - 读取指定页的完整内容
# ============================================================
def read_page(page_num):
    """
    读取指定页的完整内容（所有chunk）
    
    Args:
        page_num: 页码（逻辑页码）
    
    Returns:
        dict: {"page": page_num, "chunks": [...], "page_text": "合并文本"}
    """
    chunks_data = _ensure_chunks()
    chunks = chunks_data["chunks"]
    
    page_chunks = [c for c in chunks if c["page"] == page_num]
    
    if not page_chunks:
        return {"page": page_num, "chunks": [], "page_text": "", "error": f"Page {page_num} not found"}
    
    # Sort by chunk_id
    page_chunks.sort(key=lambda x: x["chunk_id"])
    
    # Merge text for a continuous reading experience
    page_text = "\n\n".join([c["content"] for c in page_chunks if c["type"] == "text"])
    
    return {
        "page": page_num,
        "chapter": page_chunks[0]["chapter"],
        "chunks": page_chunks,
        "page_text": page_text
    }

# ============================================================
# 3. extract_table - 提取结构化表格数据
# ============================================================
def extract_table(table_id=None, page_num=None):
    """
    根据表号或页码提取结构化表格数据
    
    Args:
        table_id: 表格ID（如 "table_ch_0015"）
        page_num: 页码，返回该页所有表格
    
    Returns:
        dict: {"table_id": ..., "page": ..., "data": [[row1], [row2], ...], "context": "..."}
    """
    chunks_data = _ensure_chunks()
    chunks = chunks_data["chunks"]
    
    if table_id:
        target = [c for c in chunks if c["chunk_id"] == table_id and c["type"] == "table"]
    elif page_num is not None:
        target = [c for c in chunks if c["page"] == page_num and c["type"] == "table"]
    else:
        return {"error": "Must provide table_id or page_num"}
    
    if not target:
        return {"error": f"No table found for table_id={table_id}, page_num={page_num}"}
    
    results = []
    for t in target:
        results.append({
            "table_id": t["chunk_id"],
            "page": t["page"],
            "chapter": t["chapter"],
            "data": t.get("table_data", []),
            "context": t["context"]
        })
    
    if len(results) == 1:
        return results[0]
    return {"tables": results, "count": len(results)}

# ============================================================
# 4. analyze_chart - 根据图号返回图片描述和周围文本
# ============================================================
def analyze_chart(figure_id):
    """
    根据图号返回图片描述和周围文本
    
    Args:
        figure_id: 图号，如 "图8.1", "图9.15"
    
    Returns:
        dict: {"figure_id": ..., "page": ..., "caption": ..., "surrounding_text": ...}
    """
    chunks_data = _ensure_chunks()
    doc_tree = _ensure_doc_tree()
    
    chunks = chunks_data["chunks"]
    figures = doc_tree.get("figures", [])
    
    # Find the figure in the document tree
    fig_info = None
    for f in figures:
        if f["id"] == figure_id:
            fig_info = f
            break
    
    if not fig_info:
        return {"error": f"Figure {figure_id} not found in document tree"}
    
    pdf_idx = fig_info["pdf_index"]
    caption = fig_info.get("caption", "")
    
    # Find the corresponding chunk
    fig_chunk = None
    for c in chunks:
        if c.get("figure_id") == figure_id:
            fig_chunk = c
            break
    
    # Find surrounding text chunks (same page)
    page = fig_chunk["page"] if fig_chunk else None
    surrounding = []
    if page:
        for c in chunks:
            if c["page"] == page and c["type"] == "text" and c["chunk_id"] != (fig_chunk["chunk_id"] if fig_chunk else ""):
                surrounding.append({
                    "chunk_id": c["chunk_id"],
                    "content": c["content"][:500]
                })
    
    result = {
        "figure_id": figure_id,
        "page": page,
        "pdf_index": pdf_idx,
        "caption": caption,
        "description": f"图片位于第{page}页，标题：{caption}",
        "surrounding_text": surrounding
    }
    
    if fig_chunk:
        result["chunk_id"] = fig_chunk["chunk_id"]
        result["content"] = fig_chunk["content"]
    
    return result

# ============================================================
# 5. quote_source - 返回引用格式
# ============================================================
def quote_source(chunk_id, format="inline"):
    """
    返回引用格式
    
    Args:
        chunk_id: chunk ID
        format: "inline" (行内引用) 或 "full" (完整引用)
    
    Returns:
        str: 引用格式文本
    """
    struct_idx = _ensure_struct_index()
    chunk = struct_idx.get("chunk_lookup", {}).get(chunk_id)
    
    if not chunk:
        return f"[引用未找到: {chunk_id}]"
    
    chapter = chunk.get("chapter", "未知章节")
    section = chunk.get("section", "")
    page = chunk.get("page", "?")
    content = chunk.get("content", "")
    
    # Truncate content for inline
    if format == "inline":
        excerpt = content[:150].replace("\n", " ") + ("..." if len(content) > 150 else "")
        if section:
            return f"{chapter}-{section}节，第{page}页——原文：\"{excerpt}\""
        else:
            return f"{chapter}，第{page}页——原文：\"{excerpt}\""
    else:
        # Full format
        lines = []
        lines.append(f"来源：{chapter}")
        if section:
            lines.append(f"章节：{section}")
        lines.append(f"页码：第{page}页")
        lines.append(f"Chunk ID：{chunk_id}")
        lines.append(f"---")
        lines.append(content)
        return "\n".join(lines)

# ============================================================
# 6. plan_query - 分析查询意图，规划检索路径
# ============================================================
def plan_query(query):
    """
    分析查询意图，规划检索路径
    
    Args:
        query: 用户查询文本
    
    Returns:
        dict: {"intent": "意图类型", "plan": [步骤列表], "suggested_tools": [工具列表]}
    """
    query_lower = query.lower()
    
    # Intent classification
    intent = None
    plan = []
    suggested_tools = []
    
    # 简单事实查询
    if any(kw in query for kw in ["是什么", "什么时候", "在哪里", "多少", "怎么", "如何", "要求"]):
        intent = "fact_lookup"
        plan.append("1. 使用 search_pdf 进行混合检索，定位相关片段")
        plan.append("2. 如结果不精确，使用 read_page 查看完整页面内容")
        plan.append("3. 使用 quote_source 生成带引用的回答")
        suggested_tools = ["search_pdf", "read_page", "quote_source"]
    
    # 跨章节对比
    elif any(kw in query for kw in ["对比", "区别", "不同", "比较", "异同"]):
        intent = "cross_chapter_comparison"
        plan.append("1. 使用 plan_query 分析查询，识别需要对比的章节")
        plan.append("2. 对每个章节分别调用 search_pdf 进行检索")
        plan.append("3. 汇总各章节结果，构建对比表格")
        plan.append("4. 使用 quote_source 为每个要点添加引用")
        suggested_tools = ["search_pdf", "plan_query", "quote_source"]
    
    # 表格查询
    elif any(kw in query for kw in ["表格", "表", "成绩", "评分", "分数", "统计"]):
        intent = "table_lookup"
        plan.append("1. 使用 search_pdf 找到相关表格所在页面")
        plan.append("2. 使用 extract_table 提取结构化表格数据")
        plan.append("3. 如需要，使用 read_page 查看表格周围上下文")
        suggested_tools = ["search_pdf", "extract_table", "read_page"]
    
    # 图表查询
    elif any(kw in query for kw in ["图", "图片", "电路", "原理图", "接线", "流程图"]):
        intent = "figure_lookup"
        plan.append("1. 使用 search_pdf 找到相关图片描述")
        plan.append("2. 使用 analyze_chart 获取图片详细信息和周围文本")
        plan.append("3. 使用 read_page 查看完整页面上下文")
        suggested_tools = ["search_pdf", "analyze_chart", "read_page"]
    
    # 芯片/器件查询
    elif any(kw in query_lower for kw in ["ds18b20", "adc", "lcd", "dac", "传感器", "芯片", "模块"]):
        intent = "component_lookup"
        plan.append("1. 使用 search_pdf 以器件型号为关键词进行检索")
        plan.append("2. 检查是否有对应的实验或使用说明章节")
        plan.append("3. 使用 read_page 查看完整实验内容")
        plan.append("4. 如涉及图片，使用 analyze_chart 查看接线图/原理图")
        suggested_tools = ["search_pdf", "read_page", "analyze_chart"]
    
    # 章节导航
    elif any(kw in query for kw in ["第几章", "目录", "结构", "有哪些", "包含"]):
        intent = "navigation"
        plan.append("1. 使用 search_pdf 检索目录或章节标题")
        plan.append("2. 使用 read_page 查看目录页确认结构")
        plan.append("3. 列出相关章节，提供页码导航")
        suggested_tools = ["search_pdf", "read_page"]
    
    else:
        intent = "general"
        plan.append("1. 使用 search_pdf 进行混合检索")
        plan.append("2. 根据结果相关性决定是否需要进一步查看")
        plan.append("3. 使用 read_page 或 extract_table 获取详细内容")
        suggested_tools = ["search_pdf", "read_page", "extract_table"]
    
    return {
        "query": query,
        "intent": intent,
        "plan": plan,
        "suggested_tools": suggested_tools
    }

# ============================================================
# 7. 便捷函数：完整问答流程
# ============================================================
def answer_query(query, top_k=5):
    """
    完整问答流程：规划 → 检索 → 引用
    
    Args:
        query: 用户查询
        top_k: 返回结果数
    
    Returns:
        dict: {"query": ..., "plan": ..., "results": [...], "answer": "..."}
    """
    # Step 1: Plan
    plan = plan_query(query)
    
    # Step 2: Search
    results = search_pdf(query, top_k=top_k)
    
    # Step 3: Generate answer with citations
    answer_parts = []
    answer_parts.append(f"查询：{query}")
    answer_parts.append(f"意图：{plan['intent']}")
    answer_parts.append("")
    
    if results:
        answer_parts.append(f"找到 {len(results)} 个相关片段：")
        answer_parts.append("")
        for i, r in enumerate(results):
            citation = quote_source(r["chunk_id"], format="inline")
            answer_parts.append(f"[{i+1}] {citation}")
            answer_parts.append("")
    else:
        answer_parts.append("未找到相关结果。")
    
    return {
        "query": query,
        "plan": plan,
        "results": results,
        "answer": "\n".join(answer_parts)
    }

# ============================================================
# 8. 命令行入口
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_tools.py <command> [args...]")
        print("Commands:")
        print("  search <query> [chapter] [page_range] [top_k]")
        print("  page <page_num>")
        print("  table <table_id>")
        print("  chart <figure_id>")
        print("  quote <chunk_id> [format]")
        print("  plan <query>")
        print("  answer <query>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "测试"
        chapter = sys.argv[3] if len(sys.argv) > 3 else None
        page_range = None
        if len(sys.argv) > 4:
            parts = sys.argv[4].split("-")
            page_range = [int(parts[0]), int(parts[1])]
        top_k = int(sys.argv[5]) if len(sys.argv) > 5 else 5
        results = search_pdf(query, chapter=chapter, page_range=page_range, top_k=top_k)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif cmd == "page":
        page_num = int(sys.argv[2])
        result = read_page(page_num)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "table":
        table_id = sys.argv[2]
        result = extract_table(table_id=table_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "chart":
        figure_id = sys.argv[2]
        result = analyze_chart(figure_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "quote":
        chunk_id = sys.argv[2]
        fmt = sys.argv[3] if len(sys.argv) > 3 else "inline"
        result = quote_source(chunk_id, format=fmt)
        print(result)
    
    elif cmd == "plan":
        query = sys.argv[2]
        result = plan_query(query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "answer":
        query = " ".join(sys.argv[2:])
        result = answer_query(query)
        print(result["answer"])
    
    else:
        print(f"Unknown command: {cmd}")