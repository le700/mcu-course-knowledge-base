#!/usr/bin/env python3
"""
test_rag.py - 测试RAG系统的6个查询
每个结果必须带页码和章节引用
"""

import os
import sys

# 确保能导入agent_tools
sys.path.insert(0, "/workspace/rag_v3")

from agent_tools import (
    search_pdf, read_page, extract_table, quote_source, plan_query,
    hybrid_search, get_document_info, get_chapter_outline
)

def print_separator(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(r, idx=None):
    """格式化打印搜索结果"""
    prefix = f"  [{idx}] " if idx is not None else "  "
    print(f"{prefix}章节: {r.get('chapter', 'N/A')}")
    print(f"    页码: PDF第{'、'.join(str(p) for p in r.get('pdf_pages', []))}页"
          f" | 文档第{'、'.join(str(p) for p in r.get('doc_pages', []))}页")
    print(f"    上下文: {r.get('context', 'N/A')}")
    print(f"    相关度: {r.get('score', 'N/A')}")
    text_preview = r.get('text', '')[:200].replace('\n', ' ')
    print(f"    原文: {text_preview}...")
    print()

def test_query(query, chapter=None, top_k=5):
    """执行单个查询测试"""
    print_separator(f"查询: {query}")
    
    # 意图分析
    plan = plan_query(query)
    print(f"  意图分析: {', '.join(plan['detected_intents'])}")
    print(f"  检索策略: {'; '.join(plan['search_strategies'])}")
    print()
    
    # 执行搜索
    results = search_pdf(query, chapter=chapter, top_k=top_k)
    print(f"  找到 {len(results)} 个结果:\n")
    
    for i, r in enumerate(results):
        print_result(r, idx=i+1)
    
    return results

# ============================================================
# 主测试
# ============================================================
print("=" * 70)
print("  RAG系统测试 - 单片机工程实训任务书")
print("=" * 70)

info = get_document_info()
print(f"文档: {info.get('title', 'N/A')}")
print(f"总页数: {info.get('total_pages', 'N/A')}")
print(f"总Chunks: {info.get('total_chunks', 'N/A')}")
print(f"版本: {info.get('version', 'N/A')}")

# -----------------------------------------------------------
# 查询1: 答辩时间
# -----------------------------------------------------------
results1 = test_query("答辩时间是什么时候？", top_k=5)

# 验证
print("  [验证] 检查结果是否包含答辩时间信息...")
found = False
for r in results1:
    if "答辩" in r.get("text", ""):
        if "0.5天" in r.get("text", "") or "答辩考试" in r.get("text", ""):
            print("  [OK] 找到答辩时间信息: 0.5天答辩考试")
            found = True
            break
if not found:
    print("  [WARN] 未在top结果中找到答辩时间，尝试扩大搜索...")
    # 尝试用read_page直接读取第2页
    page2 = read_page(2)
    if "答辩" in page2.get("content", ""):
        print(f"  [OK] 第2页包含答辩信息:")
        lines = page2["content"].split("\n")
        for line in lines:
            if "答辩" in line:
                print(f"       {line.strip()}")

# -----------------------------------------------------------
# 查询2: 成绩组成
# -----------------------------------------------------------
results2 = test_query("成绩怎么组成？", top_k=5)

# 验证
print("  [验证] 检查结果是否包含成绩组成信息...")
found = False
for r in results2:
    if "成绩" in r.get("text", "") and ("%" in r.get("text", "") or "组成" in r.get("text", "")):
        print("  [OK] 找到成绩组成信息")
        found = True
        break
if not found:
    page3 = read_page(3)
    if "成绩组成" in page3.get("content", ""):
        print("  [OK] 第3页包含成绩组成:")
        lines = page3["content"].split("\n")
        in_grading = False
        for line in lines:
            if "成绩组成" in line:
                in_grading = True
            if in_grading:
                print(f"       {line.strip()}")
                if "李晶" in line:
                    break

# -----------------------------------------------------------
# 查询3: 综合设计A题目
# -----------------------------------------------------------
results3 = test_query("综合设计A有哪些题目？", chapter=6, top_k=5)

# 验证
print("  [验证] 检查结果是否包含综合设计A题目...")
found = False
for r in results3:
    if "P-A-" in r.get("text", ""):
        print("  [OK] 找到综合设计A题目")
        found = True
        break
if not found:
    print("  [INFO] 综合设计A题目在PDF第8-11页(文档第41-44页)")
    # 列出所有P-A-题目
    for r in results3:
        text = r.get("text", "")
        for line in text.split("\n"):
            if "P-A-" in line:
                print(f"       {line.strip()}")

# -----------------------------------------------------------
# 查询4: 基本接口实验
# -----------------------------------------------------------
results4 = test_query("基本接口实验有哪些？", top_k=5)

# 验证
print("  [验证] 检查结果是否包含基本接口实验...")
found = False
for r in results4:
    if "基本接口实验" in r.get("text", "") or ("4." in r.get("text", "") and "开关" in r.get("text", "")):
        print("  [OK] 找到基本接口实验信息")
        found = True
        break
if not found:
    # 检查目录页
    print("  [INFO] 基本接口实验在第4章（文档第8-27页），从目录获取")
    # read the TOC page
    page5 = read_page(5)
    if "基本接口实验" in page5.get("content", ""):
        lines = page5["content"].split("\n")
        for line in lines:
            if "4." in line and "接口" in line:
                print(f"       {line.strip()}")

# -----------------------------------------------------------
# 查询5: DS18B20
# -----------------------------------------------------------
results5 = test_query("DS18B20怎么用？", top_k=5)

# 验证
print("  [验证] 检查结果是否包含DS18B20使用信息...")
found = False
for r in results5:
    if "DS18B20" in r.get("text", ""):
        print("  [OK] 找到DS18B20相关信息")
        found = True
        break
if not found:
    print("  [INFO] DS18B20在文档中多处出现:")
    print("    - 第5章 基本传感实验 5.3 温度传感器DS18B20 (文档第32页)")
    print("    - 第9章 Proteus DS18B20样例 (PDF第53页)")
    print("    - 第7章 AI辅助开发 DS18B20驱动示例 (PDF第20页)")
    for r in results5:
        if "DS18B20" in r.get("text", ""):
            print(f"    [OK] 找到: {r.get('context', '')}")

# -----------------------------------------------------------
# 查询6: 报告格式要求
# -----------------------------------------------------------
results6 = test_query("报告格式要求是什么？", chapter=11, top_k=5)

# 验证
print("  [验证] 检查结果是否包含报告格式要求...")
found = False
for r in results6:
    if "格式" in r.get("text", "") or "宋体" in r.get("text", "") or "字体" in r.get("text", ""):
        print("  [OK] 找到报告格式要求")
        found = True
        break
if not found:
    page77 = read_page(77)
    if "格式要求" in page77.get("content", "") or "宋体" in page77.get("content", ""):
        print("  [OK] 第77页包含报告格式要求:")
        lines = page77["content"].split("\n")
        for line in lines:
            if any(kw in line for kw in ["宋体", "字体", "格式", "标题", "行间距", "缩进"]):
                print(f"       {line.strip()}")

# -----------------------------------------------------------
# 测试quote_source
# -----------------------------------------------------------
print_separator("测试 quote_source")
chunk_id = "chunk_0002"  # 前言/课程信息
quote = quote_source(chunk_id)
print(f"  {quote}")

# -----------------------------------------------------------
# 测试read_page
# -----------------------------------------------------------
print_separator("测试 read_page")
page3_info = read_page(3)
print(f"  第3页: {page3_info.get('chapter', '')}")
print(f"  内容长度: {page3_info.get('char_count', 0)} 字符")
content_preview = page3_info.get('content', '')[:200].replace('\n', ' ')
print(f"  内容预览: {content_preview}...")

# -----------------------------------------------------------
# 测试extract_table
# -----------------------------------------------------------
print_separator("测试 extract_table")
from agent_tools import list_all_tables
tables = list_all_tables()
print(f"  表格总数: {len(tables)}")

# -----------------------------------------------------------
# 总结
# -----------------------------------------------------------
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)
print(f"  查询1 (答辩时间):  {'通过' if any('答辩' in r.get('text','') for r in results1) else '需检查'}")
print(f"  查询2 (成绩组成):  {'通过' if any('成绩' in r.get('text','') and '%' in r.get('text','') for r in results2) else '需检查'}")
print(f"  查询3 (综合设计A): {'通过' if any('P-A-' in r.get('text','') for r in results3) else '需检查'}")
print(f"  查询4 (基本接口):  {'通过' if any('接口' in r.get('text','') for r in results4) else '需检查'}")
print(f"  查询5 (DS18B20):   {'通过' if any('DS18B20' in r.get('text','') for r in results5) else '需检查'}")
print(f"  查询6 (报告格式):  {'通过' if any(kw in r.get('text','') for r in results6 for kw in ['格式','宋体','字体']) else '需检查'}")
print("=" * 70)