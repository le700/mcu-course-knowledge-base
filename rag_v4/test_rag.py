#!/usr/bin/env python3
"""
test_rag.py - RAG v4 端到端测试
测试 8 个查询，每个输出完整引用（意图识别、召回数、精排后top3、引用格式）
"""

import os
import sys

sys.path.insert(0, "/workspace/rag_v4")

from agent_tools import (
    search_pdf, read_page, extract_table, quote_source, compare, smart_answer,
    analyze_intent, multi_recall, get_document_info
)


def print_header(title: str, width: int = 80):
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subheader(title: str):
    print(f"\n  --- {title} ---")


def print_result(r, idx: int = None):
    """格式化打印单个检索结果"""
    prefix = f"  [{idx}] " if idx is not None else "  "
    rtype = r.get("type", "text")

    if rtype == "table":
        print(f"{prefix}[表格] {r.get('table_id', '?')}")
        print(f"    引用: {r.get('citation', 'N/A')}")
        print(f"    表头: {r.get('headers', [])}")
        print(f"    行数: {len(r.get('rows', []))}")
    else:
        print(f"{prefix}[文本] {r.get('chunk_id', '?')} | 相关度: {r.get('score', 'N/A')}")
        print(f"    引用: {r.get('citation', 'N/A')}")
        text_preview = r.get("text", "")[:150].replace("\n", " ")
        print(f"    原文: {text_preview}...")
    print()


def test_query(query: str, expected_intent: str, expected_chapter: str, query_num: int):
    """
    执行单个查询的完整测试
    """
    print_header(f"查询 {query_num}: {query}")
    print(f"  预期意图: {expected_intent} | 预期章节: {expected_chapter}")

    # 1. 意图分析
    intent = analyze_intent(query)
    intent_match = "OK" if intent["type"] == expected_intent else f"MISMATCH (got {intent['type']})"
    print(f"  意图识别: {intent['type']} (置信度: {intent['confidence']:.0%}) [{intent_match}]")
    print(f"  目标章节: {intent['chapters']}")
    print(f"  关键词: {intent['keywords']}")

    # 2. 多路召回统计
    recall = multi_recall(query, top_k=20)
    v_count = len(recall["vector"])
    k_count = len(recall["keyword"])
    s_count = len(recall["structured"])
    t_count = len(recall["table"])
    print(f"  召回统计: 向量={v_count} | 关键词={k_count} | 结构化={s_count} | 表格={t_count}")

    # 3. 精排后 top3
    results = search_pdf(query, top_k=3)
    print(f"  精排后Top3 ({len(results)}条):")
    for i, r in enumerate(results):
        print_result(r, idx=i + 1)

    # 4. 引用格式
    if results:
        print_subheader("完整引用格式")
        for i, r in enumerate(results):
            citation = quote_source(r)
            print(f"  [{i+1}] {citation}")

    # 5. 验证
    passed = len(results) > 0
    print_subheader(f"验证: {'PASS' if passed else 'FAIL'} (返回{len(results)}条结果)")
    return {
        "query": query,
        "expected_intent": expected_intent,
        "actual_intent": intent["type"],
        "intent_match": intent["type"] == expected_intent,
        "expected_chapter": expected_chapter,
        "recall_stats": {"vector": v_count, "keyword": k_count, "structured": s_count, "table": t_count},
        "top3": results,
        "passed": passed
    }


# ============================================================
# 主测试流程
# ============================================================

print("=" * 80)
print("  RAG v4 端到端测试 - 单片机工程实训任务书")
print("  三层架构：召回层 + 融合层 + 精排层")
print("=" * 80)

info = get_document_info()
print(f"\n文档: {info.get('title', 'N/A')}")
print(f"总页数: {info.get('total_pages', 'N/A')}")
print(f"总Chunks: {info.get('total_chunks', 'N/A')}")
print(f"版本: {info.get('version', 'N/A')}")

# 测试用例定义
test_cases = [
    {"query": "答辩时间是什么时候？", "intent": "concept", "chapter": "前置/第20周"},
    {"query": "成绩怎么组成？", "intent": "table", "chapter": "第3页"},
    {"query": "综合设计A有哪些题目？", "intent": "exact", "chapter": "第6章"},
    {"query": "基本接口实验有哪些？", "intent": "exact", "chapter": "第4章"},
    {"query": "DS18B20怎么用？", "intent": "concept", "chapter": "第5章"},
    {"query": "报告格式要求是什么？", "intent": "concept", "chapter": "第11章"},
    {"query": "P-A-3#和P-A-1#哪个简单？", "intent": "compare", "chapter": "第6章"},
    {"query": "验收咋整？", "intent": "concept", "chapter": "第6章/第7章"},
]

all_results = []
for i, tc in enumerate(test_cases):
    result = test_query(
        tc["query"], tc["intent"], tc["chapter"], i + 1
    )
    all_results.append(result)

# ============================================================
# 汇总报告
# ============================================================
print_header("测试报告汇总", width=90)
print(f"{'序号':<4} {'查询':<28} {'预期意图':<10} {'实际意图':<10} {'匹配':<6} {'召回数':<8} {'Top3':<6} {'状态':<6}")
print("-" * 90)
for i, r in enumerate(all_results):
    recall_total = sum(r["recall_stats"].values())
    top3_count = len(r["top3"])
    status = "PASS" if r["passed"] else "FAIL"
    intent_str = "OK" if r["intent_match"] else "WRONG"
    print(f"{i+1:<4} {r['query']:<28} {r['expected_intent']:<10} {r['actual_intent']:<10} {intent_str:<6} {recall_total:<8} {top3_count:<6} {status:<6}")

print("-" * 90)
total_passed = sum(1 for r in all_results if r["passed"])
intent_matches = sum(1 for r in all_results if r["intent_match"])
print(f"\n总计: {total_passed}/{len(all_results)} 查询通过, {intent_matches}/{len(all_results)} 意图识别正确")
print("=" * 90)

# ============================================================
# 额外测试：工具函数
# ============================================================
print_header("工具函数专项测试")

# read_page
print_subheader("read_page(2) - 第2页（课程安排）")
page2 = read_page(2)
print(f"  章节: {page2['chapter']}")
print(f"  内容: {page2['content'][:200]}...")

# extract_table
print_subheader("extract_table('成绩')")
tables = extract_table("成绩")
for t in tables:
    print(f"  {t['table_id']}: {t['citation']}")
    for row in t["rows"]:
        print(f"    {row}")

# compare
print_subheader("compare('P-A-3#', 'P-A-1#')")
comp = compare("P-A-3#", "P-A-1#")
print(f"  对比结果: {len(comp['comparison_table'])} 行")
for row in comp["comparison_table"]:
    print(f"    A: {row.get('A_章节', '')[:60]}")
    print(f"    B: {row.get('B_章节', '')[:60]}")
    print()

# smart_answer
print_subheader("smart_answer 测试")
for q in ["成绩怎么组成？", "P-A-3#和P-A-1#哪个简单？", "验收咋整？"]:
    sa = smart_answer(q)
    print(f"  [{sa['route']}] {q}")
    if sa["route"] == "extract_table":
        ans = sa["answer"]
        print(f"    表格数: {ans.get('count', 0)}")
    elif sa["route"] == "compare":
        ans = sa["answer"]
        print(f"    QA: {ans.get('query_a', '')} | QB: {ans.get('query_b', '')}")
    elif sa["route"] == "search_pdf":
        ans = sa["answer"]
        print(f"    结果数: {len(ans) if isinstance(ans, list) else 'N/A'}")

print("\n" + "=" * 90)
print("  测试完成")
print("=" * 90)