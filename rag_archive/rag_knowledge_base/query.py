#!/usr/bin/env python3
"""
RAG 知识库查询脚本 (全量关键词检索版)
用法: python query.py "你的问题"
"""

import os
import sys
import re

os.environ["HF_HUB_OFFLINE"] = "1"

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

DB_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "mcukb"
TOP_K = 3


def load_model():
    print("正在加载模型...", file=sys.stderr)
    return SentenceTransformer(MODEL_NAME)


def load_collection():
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库路径不存在: {DB_PATH}", file=sys.stderr)
        sys.exit(1)
    client = PersistentClient(path=DB_PATH)
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"错误: 无法加载集合: {e}", file=sys.stderr)
        sys.exit(1)


def extract_keywords(text):
    keywords = set()
    chinese = re.findall(r'[\u4e00-\u9fff]', text)
    for i in range(len(chinese) - 1):
        keywords.add(chinese[i] + chinese[i + 1])
    for i in range(len(chinese) - 2):
        keywords.add(chinese[i] + chinese[i + 1] + chinese[i + 2])
    keywords.update(chinese)
    for w in re.findall(r'[a-zA-Z0-9]+', text.lower()):
        keywords.add(w)
    for d in re.findall(r'\d+', text):
        keywords.add(d)
    return keywords


def substring_match(query_text, target_text):
    q_ch = ''.join(re.findall(r'[\u4e00-\u9fff]+', query_text))
    if len(q_ch) < 2:
        return 0.0
    t_ch = ''.join(re.findall(r'[\u4e00-\u9fff]+', target_text))
    best = 0.0
    for size in range(len(q_ch), 1, -1):
        for i in range(len(q_ch) - size + 1):
            sub = q_ch[i:i + size]
            if sub in t_ch:
                best = max(best, size / len(q_ch))
        if best > 0:
            break
    return best


def score_document(query_text, query_kw, doc_text, doc_title):
    """计算文档得分"""
    doc_kw = extract_keywords(doc_text)
    title_kw = extract_keywords(doc_title)
    if not query_kw:
        return 0.0

    # 关键词命中率
    hits = len(query_kw & doc_kw)
    hit_rate = hits / len(query_kw)

    # 标题命中
    title_hits = len(query_kw & title_kw)
    title_bonus = min(title_hits / len(query_kw), 1.0) * 0.3

    # 精确子串匹配
    content_exact = substring_match(query_text, doc_text)
    title_exact = substring_match(query_text, doc_title)
    exact_bonus = max(content_exact * 0.3, title_exact * 0.6)

    return hit_rate * 0.4 + title_bonus + exact_bonus


def query_all(collection, query_text, top_k=TOP_K):
    """全量检索：获取所有文档，按关键词得分排序"""
    # 获取所有文档
    all_data = collection.get(include=["documents", "metadatas"])

    if not all_data or not all_data.get("ids"):
        return None

    query_kw = extract_keywords(query_text)

    scored = []
    for i in range(len(all_data["ids"])):
        doc = all_data["documents"][i]
        meta = all_data["metadatas"][i]
        score = score_document(query_text, query_kw, doc, meta.get("title", ""))
        if score > 0:
            scored.append({
                "id": all_data["ids"][i],
                "document": doc,
                "metadata": meta,
                "score": score
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:top_k]

    return {
        "ids": [[c["id"] for c in top]],
        "documents": [[c["document"] for c in top]],
        "metadatas": [[c["metadata"] for c in top]],
        "scores": [[c["score"] for c in top]]
    }


def format_results(results):
    if not results or not results.get("ids") or not results["ids"][0]:
        print("未找到相关结果。")
        return

    print("=" * 70)
    print(f"查询结果 (共 {len(results['ids'][0])} 条)")
    print("=" * 70)

    for i in range(len(results["ids"][0])):
        document = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        score = results["scores"][0][i]

        print(f"\n--- 结果 {i + 1} ---")
        print(f"得分: {score:.4f}")
        print(f"来源: {metadata.get('source', '?')} | 章节: {metadata.get('title', '?')}")
        print(f"\n{document}")
        print()

    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("用法: python query.py \"你的问题\"", file=sys.stderr)
        sys.exit(1)

    query_text = " ".join(sys.argv[1:])
    print(f"查询: {query_text}", file=sys.stderr)

    collection = load_collection()
    print(f"知识库: {collection.count()} 条 | 正在检索...", file=sys.stderr)
    print("-" * 40, file=sys.stderr)

    results = query_all(collection, query_text)
    format_results(results)


if __name__ == "__main__":
    main()