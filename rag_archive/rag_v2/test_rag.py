#!/usr/bin/env python3
"""
测试脚本：验证 RAG v2 多路索引和 Agent 工具
"""
import sys
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import json

# Add parent to path
sys.path.insert(0, "/workspace/rag_v2")

# Import agent tools
from agent_tools import (
    search_pdf, read_page, extract_table, analyze_chart, 
    quote_source, plan_query, answer_query
)

print("=" * 70)
print("RAG v2 测试 - 单片机工程实训任务书")
print("=" * 70)

# ============================================================
# Test 1: search_pdf - 混合检索
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: search_pdf - 混合检索")
print("=" * 70)

test_queries = [
    "答辩时间是什么时候？",
    "成绩怎么组成？",
    "综合设计A有哪些题目？",
    "基本接口实验有哪些？",
    "DS18B20怎么用？",
    "报告格式要求是什么？"
]

for query in test_queries:
    print(f"\n{'─'*60}")
    print(f"查询: {query}")
    print(f"{'─'*60}")
    
    results = search_pdf(query, top_k=3)
    
    if not results:
        print("  未找到结果")
    else:
        for i, r in enumerate(results):
            print(f"\n  [{i+1}] chunk_id={r['chunk_id']} | ch={r['chapter']} | page={r['page']} | score={r['score']:.4f}")
            print(f"      section={r['section']}")
            content_preview = r['content'][:200].replace('\n', ' ')
            print(f"      内容: {content_preview}...")
            # Show citation
            citation = quote_source(r['chunk_id'], format="inline")
            print(f"      引用: {citation[:200]}...")

# ============================================================
# Test 2: read_page - 读取指定页
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: read_page - 读取指定页")
print("=" * 70)

test_pages = [41, 45, 51, 57, 75, 109]
for page_num in test_pages:
    result = read_page(page_num)
    if "error" in result:
        print(f"\n  页码 {page_num}: {result['error']}")
    else:
        print(f"\n  页码 {page_num} ({result.get('chapter', '?')}): {len(result['chunks'])} chunks, 文本长度 {len(result['page_text'])}")

# ============================================================
# Test 3: extract_table - 提取表格
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: extract_table - 提取表格")
print("=" * 70)

# Find a table chunk
chunks_data = json.load(open("/data/user/work/pdf_semantic_chunks.json", "r", encoding="utf-8"))
table_chunks = [c for c in chunks_data["chunks"] if c["type"] == "table"]

if table_chunks:
    # Test first 3 tables
    for i, tc in enumerate(table_chunks[:3]):
        result = extract_table(table_id=tc["chunk_id"])
        print(f"\n  表格 {i+1}: {tc['chunk_id']} (page={tc['page']}, ch={tc['chapter']})")
        if "data" in result:
            rows = result["data"]
            print(f"    行数: {len(rows)}")
            if rows:
                print(f"    列数: {len(rows[0])}")
                print(f"    首行: {rows[0][:3]}...")
        else:
            print(f"    结果: {result}")
else:
    print("  未找到表格chunks")

# ============================================================
# Test 4: analyze_chart - 分析图表
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: analyze_chart - 分析图表")
print("=" * 70)

figures = chunks_data.get("figures", [])
for fig in figures[:3]:
    fig_id = fig["id"]
    result = analyze_chart(fig_id)
    print(f"\n  {fig_id}: page={result.get('page')}, pdf_idx={result.get('pdf_index')}")
    print(f"    caption: {result.get('caption', '')[:100]}")
    if "error" not in result:
        print(f"    surrounding texts: {len(result.get('surrounding_text', []))} chunks")

# ============================================================
# Test 5: quote_source - 引用格式
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: quote_source - 引用格式")
print("=" * 70)

# Get a sample chunk
sample_chunk = chunks_data["chunks"][10]
print(f"\n  inline 格式:")
print(f"  {quote_source(sample_chunk['chunk_id'], format='inline')[:200]}")
print(f"\n  full 格式:")
print(f"  {quote_source(sample_chunk['chunk_id'], format='full')[:300]}")

# ============================================================
# Test 6: plan_query - 查询规划
# ============================================================
print("\n" + "=" * 70)
print("TEST 6: plan_query - 查询规划")
print("=" * 70)

plan_queries = [
    "答辩时间是什么时候？",
    "综合设计A和综合设计B有什么区别？",
    "成绩怎么组成的？",
    "DS18B20温度传感器怎么接线？",
    "有哪些实验？",
]
for q in plan_queries:
    result = plan_query(q)
    print(f"\n  查询: {q}")
    print(f"  意图: {result['intent']}")
    print(f"  建议工具: {result['suggested_tools']}")

# ============================================================
# Test 7: answer_query - 完整问答
# ============================================================
print("\n" + "=" * 70)
print("TEST 7: answer_query - 完整问答流程")
print("=" * 70)

for query in test_queries[:3]:
    print(f"\n{'─'*60}")
    result = answer_query(query, top_k=3)
    print(result["answer"][:500])
    print("...")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)
print(f"向量索引: ChromaDB @ /workspace/rag_v2/vector_db")
print(f"关键词索引: /workspace/rag_v2/keyword_index.pkl")
print(f"结构化索引: /workspace/rag_v2/struct_index.json")
print(f"语义切片: /data/user/work/pdf_semantic_chunks.json ({len(chunks_data['chunks'])} chunks)")