#!/usr/bin/env python3
"""
build_fusion_rerank.py
========================
第二层融合层 + 第三层精排层

- 依赖上一层的 agent_tools.py (已构建的向量索引 + 关键词索引 + 结构化索引)
- 不重复构建索引，专注于"融合排序"和"精排筛选"
- 四路召回 → RRF/加权融合 → Cross-Encoder/BM25精排 → 带页码章节的引用结果

安装依赖：
    pip install sentence-transformers --break-system-packages
"""

import os
import sys
import json
import re
import math
import pickle
import warnings
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple

warnings.filterwarnings("ignore")

# ============================================================
# 0. 路径配置 & 导入上层模块
# ============================================================
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 上层 agent_tools.py 所在目录
_PARENT_DIR = "/workspace/rag_v3"
sys.path.insert(0, _PARENT_DIR)

import jieba
import numpy as np

# 从 agent_tools 导入底层基础组件
from agent_tools import (
    _chunks,
    _keyword_index,
    _struct_index,
    _model,
    _collection,
    _tfidf_vectorizer,
    _tfidf_matrix,
    _inverted_index,
    _proper_noun_index,
    _jieba_texts,
    _vector_search,
    _keyword_search,
    _rrf_fusion,
    _apply_filters,
    hybrid_search,
    search_pdf,
    plan_query,
    read_page,
    extract_table,
    quote_source,
    get_chapter_outline,
    list_all_tables,
    get_document_info,
)

# ============================================================
# 1. 章节关系图谱 (为图谱检索路径服务)
# ============================================================

# 章节间关系定义
CHAPTER_NAMES_MAP = {
    0:  "前言/课程信息",
    1:  "单片机原理",
    2:  "预备实验",
    3:  "基本语言实验",
    4:  "基本接口实验",
    5:  "基本传感实验",
    6:  "单片机综合设计A",
    7:  "单片机综合设计B",
    8:  "实验系统介绍",
    9:  "软件工具使用指南",
    10: "C51简明教程",
    11: "实验报告模板及要求",
}

# 章节关系边： (a, b, relation, weight)
# relation: "prerequisite"(前置), "related"(相关), "extends"(延伸), "contains"(包含)
CHAPTER_EDGES = [
    (1, 2, "prerequisite", 0.8),  # 原理 → 预备实验
    (1, 3, "prerequisite", 0.8),  # 原理 → 基本语言实验
    (1, 4, "prerequisite", 0.7),  # 原理 → 基本接口实验
    (1, 5, "prerequisite", 0.7),  # 原理 → 基本传感实验
    (2, 3, "extends", 0.6),       # 预备实验 → 基本语言实验
    (3, 4, "extends", 0.6),       # 基本语言 → 基本接口
    (4, 5, "extends", 0.6),       # 基本接口 → 基本传感
    (2, 6, "prerequisite", 0.5),  # 预备实验 → 综合设计A
    (3, 6, "prerequisite", 0.5),  # 基本语言 → 综合设计A
    (4, 6, "prerequisite", 0.7),  # 基本接口 → 综合设计A
    (5, 6, "prerequisite", 0.7),  # 基本传感 → 综合设计A
    (2, 7, "prerequisite", 0.5),  # 预备实验 → 综合设计B
    (3, 7, "prerequisite", 0.5),  # 基本语言 → 综合设计B
    (4, 7, "prerequisite", 0.7),  # 基本接口 → 综合设计B
    (5, 7, "prerequisite", 0.7),  # 基本传感 → 综合设计B
    (6, 7, "related", 0.5),       # 综合设计A ↔ 综合设计B
    (8, 2, "related", 0.4),       # 实验系统 → 预备实验
    (8, 4, "related", 0.5),       # 实验系统 → 基本接口
    (9, 10, "related", 0.6),      # 软件工具 → C51教程
    (10, 3, "related", 0.5),      # C51教程 → 基本语言
    (11, 6, "related", 0.6),      # 报告模板 → 综合设计A
    (11, 7, "related", 0.6),      # 报告模板 → 综合设计B
    (0, 1, "related", 0.3),       # 前言 → 原理
    (0, 6, "related", 0.4),       # 前言 → 综合设计A (成绩/答辩信息)
    (0, 11, "related", 0.4),      # 前言 → 报告模板
]

def _build_graph():
    """构建章节关系图 (邻接表)"""
    graph = defaultdict(list)
    for a, b, rel, w in CHAPTER_EDGES:
        graph[a].append((b, rel, w))
        graph[b].append((a, rel, w))  # 双向
    return dict(graph)

_CHAPTER_GRAPH = _build_graph()


def _build_chunk_lookup():
    """构建 chunk_id -> chunk 快速查找"""
    return {c["chunk_id"]: c for c in _chunks}

_CHUNK_LOOKUP = _build_chunk_lookup()


# ============================================================
# 2. 四路召回: multi_recall()
# ============================================================

def _vector_recall(query: str, top_k: int = 20) -> List[Dict]:
    """
    路径1: 向量语义召回
    返回: [{"chunk_id", "content", "chapter", "section", "page", "score", "path"}]
    """
    results = _vector_search(query, top_k=top_k)
    formatted = []
    for item in results:
        meta = item["metadata"]
        cid = item["chunk_id"]
        try:
            pages = json.loads(meta.get("pdf_pages", "[]"))
        except:
            pages = []
        formatted.append({
            "chunk_id": cid,
            "content": item["document"],
            "chapter": f"第{meta.get('chapter_num', '?')}章 {meta.get('chapter_title', '')}",
            "chapter_num": meta.get("chapter_num", 0),
            "section": meta.get("section", ""),
            "page": pages[0] if pages else 0,
            "pages": pages,
            "score": item["score"],
            "path": "vector",
            "metadata": meta,
        })
    return formatted


def _keyword_recall(query: str, top_k: int = 20) -> List[Dict]:
    """
    路径2: 关键词倒排索引召回
    """
    results = _keyword_search(query, top_k=top_k)
    formatted = []
    for item in results:
        meta = item["metadata"]
        cid = item["chunk_id"]
        try:
            pages = json.loads(meta.get("pdf_pages", "[]"))
        except:
            pages = []
        formatted.append({
            "chunk_id": cid,
            "content": item["document"],
            "chapter": f"第{meta.get('chapter_num', '?')}章 {meta.get('chapter_title', '')}",
            "chapter_num": meta.get("chapter_num", 0),
            "section": meta.get("section", ""),
            "page": pages[0] if pages else 0,
            "pages": pages,
            "score": item["score"],
            "path": "keyword",
            "metadata": meta,
        })
    return formatted


def _structured_recall(query: str, top_k: int = 20) -> List[Dict]:
    """
    路径3: 结构化字段召回
    利用 struct_index 做章节/页面/表格/图匹配
    综合: 章节标题匹配 + section名称匹配 + 页码匹配
    """
    scores = defaultdict(float)

    # 3a. 章节标题匹配
    q_lower = query.lower()
    for ch_key, ch_info in _struct_index.get("chapters", {}).items():
        ch_title = ch_info.get("chapter_title", "")
        if not ch_title:
            continue
        # 计算标题与查询的匹配度
        ch_words = set(jieba.cut(ch_title))
        q_words = set(jieba.cut(query))
        overlap = ch_words & q_words
        if overlap:
            match_score = len(overlap) / max(len(q_words), 1)
            for cid in ch_info.get("chunk_ids", []):
                scores[cid] += match_score * 3.0  # 章节匹配权重高

    # 3b. Section名称匹配
    for sec_name, chunk_ids in _struct_index.get("by_section", {}).items():
        if not sec_name or sec_name == "未分类":
            continue
        sec_words = set(jieba.cut(sec_name))
        q_words = set(jieba.cut(query))
        overlap = sec_words & q_words
        if overlap:
            match_score = len(overlap) / max(len(q_words), 1)
            for cid in chunk_ids:
                scores[cid] += match_score * 2.0

    # 3c. 表格匹配 (表格标题/内容关键词匹配)
    for table in _struct_index.get("tables", []):
        table_content = table.get("content", "")
        table_words = set(jieba.cut(table_content))
        q_words = set(jieba.cut(query))
        overlap = table_words & q_words
        if overlap:
            match_score = len(overlap) / max(len(q_words), 1)
            cid = table.get("chunk_id")
            if cid:
                scores[cid] += match_score * 1.5

    # 3d. 页码匹配 (查询中提及的页码)
    page_nums = re.findall(r'第\s*(\d+)\s*页', query)
    for pn_str in page_nums:
        pn = int(pn_str)
        pn_key = str(pn)
        if pn_key in _struct_index.get("pages", {}):
            for cid in _struct_index["pages"][pn_key]:
                scores[cid] += 2.0

    # 排序
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    formatted = []
    for cid, score in sorted_items:
        chunk = _CHUNK_LOOKUP.get(cid)
        if not chunk:
            continue
        pdf_pages = chunk.get("pdf_pages", [])
        formatted.append({
            "chunk_id": cid,
            "content": chunk["text"],
            "chapter": f"第{chunk.get('chapter_num', '?')}章 {chunk.get('chapter_title', '')}",
            "chapter_num": chunk.get("chapter_num", 0),
            "section": chunk.get("section", ""),
            "page": pdf_pages[0] if pdf_pages else 0,
            "pages": pdf_pages,
            "score": score,
            "path": "structured",
            "metadata": {
                "chapter_num": chunk.get("chapter_num", 0),
                "chapter_title": chunk.get("chapter_title", ""),
                "section": chunk.get("section", ""),
                "pdf_pages": json.dumps(pdf_pages),
                "doc_pages": json.dumps(chunk.get("doc_pages", [])),
                "content_type": chunk.get("content_type", "text"),
                "context": chunk.get("context", ""),
            },
        })
    return formatted


def _graph_recall(query: str, top_k: int = 20) -> List[Dict]:
    """
    路径4: 知识图谱召回
    利用章节关系图谱，从匹配到的章节出发，沿关系边扩散获取相关章节的chunk
    """
    # 4a. 先找到查询命中的章节
    q_words = set(jieba.cut(query.lower()))
    chapter_hits = defaultdict(float)  # chapter_num -> score

    for ch_num, ch_name in CHAPTER_NAMES_MAP.items():
        ch_words = set(jieba.cut(ch_name.lower()))
        overlap = q_words & ch_words
        if overlap:
            chapter_hits[ch_num] = len(overlap) / max(len(q_words), 1)

    # 如果没命中章节名，尝试用关键词索引找最相关的章节
    if not chapter_hits:
        kw_results = _keyword_recall(query, top_k=5)
        for r in kw_results:
            ch_num = r.get("chapter_num", 0)
            chapter_hits[ch_num] += r.get("score", 0)

    # 4b. 从命中章节沿关系图扩散
    expanded_scores = dict(chapter_hits)  # chapter_num -> accumulated score
    for ch_num, base_score in chapter_hits.items():
        if ch_num in _CHAPTER_GRAPH:
            for neighbor, rel, weight in _CHAPTER_GRAPH[ch_num]:
                propagated = base_score * weight * 0.5  # 传播衰减
                if neighbor not in expanded_scores:
                    expanded_scores[neighbor] = 0.0
                expanded_scores[neighbor] += propagated

    # 4c. 收集这些章节的chunk并按相关性打分
    chunk_scores = defaultdict(float)
    for ch_num, ch_score in expanded_scores.items():
        ch_key = str(ch_num)
        if ch_key in _struct_index.get("chapters", {}):
            for cid in _struct_index["chapters"][ch_key].get("chunk_ids", []):
                chunk_scores[cid] = ch_score

    # 对有直接命中的chunk加分
    for ch_num, base_score in chapter_hits.items():
        ch_key = str(ch_num)
        if ch_key in _struct_index.get("chapters", {}):
            for cid in _struct_index["chapters"][ch_key].get("chunk_ids", []):
                chunk_scores[cid] += base_score * 2.0  # 直接命中加倍

    sorted_items = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    formatted = []
    for cid, score in sorted_items:
        chunk = _CHUNK_LOOKUP.get(cid)
        if not chunk:
            continue
        pdf_pages = chunk.get("pdf_pages", [])
        formatted.append({
            "chunk_id": cid,
            "content": chunk["text"],
            "chapter": f"第{chunk.get('chapter_num', '?')}章 {chunk.get('chapter_title', '')}",
            "chapter_num": chunk.get("chapter_num", 0),
            "section": chunk.get("section", ""),
            "page": pdf_pages[0] if pdf_pages else 0,
            "pages": pdf_pages,
            "score": score,
            "path": "graph",
            "metadata": {
                "chapter_num": chunk.get("chapter_num", 0),
                "chapter_title": chunk.get("chapter_title", ""),
                "section": chunk.get("section", ""),
                "pdf_pages": json.dumps(pdf_pages),
                "doc_pages": json.dumps(chunk.get("doc_pages", [])),
                "content_type": chunk.get("content_type", "text"),
                "context": chunk.get("context", ""),
            },
        })
    return formatted


def multi_recall(query: str, top_k: int = 20) -> Dict[str, List[Dict]]:
    """
    四路召回：向量、关键词、结构化、图谱，返回未合并的原始结果

    Args:
        query: 查询文本
        top_k: 每路召回数量

    Returns:
        {"vector": [...], "keyword": [...], "structured": [...], "graph": [...]}
    """
    return {
        "vector": _vector_recall(query, top_k),
        "keyword": _keyword_recall(query, top_k),
        "structured": _structured_recall(query, top_k),
        "graph": _graph_recall(query, top_k),
    }


# ============================================================
# 3. 意图识别: analyze_intent()
# ============================================================

def analyze_intent(query: str) -> Dict[str, Any]:
    """
    分析查询意图，返回意图类型和置信度

    Returns:
        {"type": "exact|concept|compare|table|procedure", "confidence": float, "keywords": [...]}
    """
    q = query.strip()
    q_lower = q.lower()

    # 精确查询特征：芯片型号、编号、特定代码、页码
    exact_patterns = [
        r'\b(?:DS18B20|DS1302|DHT11|ADC080[89]|PCF8591|LCD1602|LCD12864|AT89C51|STC89C52|'
        r'74LS47|74HC373|74HC138|AT24C02|L298N|RFID|RC522|L298N)\b',
        r'P-[A-Z]-\d+#',                     # 条款编号 P-A-3#
        r'[A-Z]-\d+#',                        # 编号 A-3#
        r'第\s*\d+\s*页',                      # 页码
        r'\b(?:VCC|GND|PWM|I2C|SPI|UART)\b', # 引脚/协议
        r'图\s*\d+',                           # 图编号
        r'表\s*\d+',                           # 表编号
    ]
    exact_score = 0.0
    for pat in exact_patterns:
        if re.search(pat, q, re.IGNORECASE):
            exact_score = max(exact_score, 0.7)
    # 纯芯片型号匹配
    if re.search(r'\b[A-Z]{2,}\d{2,}[A-Z]?\d*\b', q) and not re.search(r'[怎么是什么如何]', q):
        exact_score = 0.95

    # 概念查询特征
    concept_patterns = [
        r'是什么', r'什么是', r'定义', r'含义', r'概念', r'原理',
        r'介绍', r'概述', r'作用', r'功能', r'特点',
    ]
    concept_score = 0.0
    for pat in concept_patterns:
        if pat in q:
            concept_score = max(concept_score, 0.8)

    # 对比查询特征
    compare_patterns = [
        r'区别', r'不同', r'差异', r'比较', r'对比', r'vs\.?',
        r'和.*哪个', r'还是', r'或者', r'与.*区别',
        r'异同', r'优缺点', r'优劣',
    ]
    compare_score = 0.0
    for pat in compare_patterns:
        if re.search(pat, q):
            compare_score = max(compare_score, 0.8)

    # 表格/数据查询特征
    table_patterns = [
        r'表', r'成绩', r'组成', r'占比', r'评分', r'分数',
        r'多少', r'几', r'比.*例', r'百分',
        r'列表', r'清单', r'汇总',
    ]
    table_score = 0.0
    for pat in table_patterns:
        if pat in q:
            table_score = max(table_score, 0.6)

    # 流程/步骤查询特征
    procedure_patterns = [
        r'步骤', r'流程', r'怎么做', r'如何', r'怎么',
        r'方法', r'操作', r'过程', r'顺序', r'先后',
        r'验收', r'答辩', r'提交', r'要求',
    ]
    procedure_score = 0.0
    for pat in procedure_patterns:
        if pat in q:
            procedure_score = max(procedure_score, 0.7)

    # 综合判断
    scores = {
        "exact": exact_score,
        "concept": concept_score,
        "compare": compare_score,
        "table": table_score,
        "procedure": procedure_score,
    }
    best_type = max(scores, key=scores.get)
    confidence = scores[best_type]

    # 如果置信度太低，默认 concept
    if confidence < 0.5:
        best_type = "concept"
        confidence = 0.5

    # 提取关键词
    keywords = _extract_intent_keywords(q, best_type)

    return {
        "type": best_type,
        "confidence": round(confidence, 2),
        "scores": {k: round(v, 2) for k, v in scores.items()},
        "keywords": keywords,
    }


def _extract_intent_keywords(query: str, intent_type: str) -> List[str]:
    """从查询中提取关键检索词"""
    keywords = []
    # 芯片型号
    chips = re.findall(r'\b[A-Z]{2,}\d{2,}[A-Z]?\d*\b', query)
    keywords.extend(chips)
    # 编号
    codes = re.findall(r'[A-Z]-\d+#', query)
    keywords.extend(codes)
    # 中文关键词（用jieba提取）
    words = list(jieba.cut(query))
    stopwords = {'的', '了', '是', '在', '和', '与', '或', '吗', '呢', '吧', '啊',
                 '什么', '怎么', '如何', '哪个', '哪些', '这个', '那个', '一个',
                 '有', '不', '也', '都', '就', '还', '要', '会', '能', '可以',
                 '很', '非常', '比较', '更', '最', '我', '你', '他', '她', '它'}
    for w in words:
        w = w.strip()
        if len(w) >= 2 and w not in stopwords:
            keywords.append(w)
    return list(dict.fromkeys(keywords))  # 去重保序


# ============================================================
# 4. 查询改写: rewrite_query()
# ============================================================

# 口语化→专业表述映射表
_REWRITE_RULES = [
    # (口语化模式, 专业表述替换)
    (r'咋验收', '综合设计验收方式 提问形式'),
    (r'怎么验收', '综合设计验收方式 提问形式'),
    (r'如何验收', '综合设计验收方式 提问形式'),
    (r'多少分', '成绩组成 占比 考核方式'),
    (r'分数', '成绩组成 评分标准'),
    (r'咋评分', '成绩组成 评分标准 占比'),
    (r'啥时候答辩', '答辩时间 日期 地点'),
    (r'什么时候答辩', '答辩时间 日期 地点'),
    (r'答辩时间', '答辩时间 日期 地点'),
    (r'咋提交', '实验报告提交方式'),
    (r'怎么提交', '实验报告提交方式'),
    (r'报告格式', '实验报告模板 格式要求 字体'),
    (r'咋写报告', '实验报告模板 格式要求'),
    (r'题目有哪些', '综合设计选题 题目列表'),
    (r'选哪个', '综合设计选题 题目列表'),
    (r'选什么', '综合设计选题 题目列表'),
    (r'要做几个实验', '实验内容 数量'),
    (r'几个实验', '实验内容 数量'),
    (r'实验有哪些', '实验内容 列表'),
    (r'咋用', '使用方法 操作步骤'),
    (r'怎么用', '使用方法 操作步骤'),
    (r'接线', '原理图 电路连接 引脚'),
    (r'咋连', '原理图 电路连接 引脚'),
    (r'代码', '程序代码 示例'),
    (r'程序', '程序代码 示例'),
    (r'啥意思', '定义 概念 解释'),
    (r'什么意思', '定义 概念 解释'),
    (r'干嘛的', '功能 作用'),
    (r'啥功能', '功能 作用'),
    (r'和.*啥区别', '对比 区别 差异'),
    (r'哪个好', '对比 优缺点'),
    (r'能不能', '是否支持 可行性'),
    (r'可以吗', '是否支持 可行性'),
    (r'必须吗', '是否必须 要求'),
    (r'一定要', '是否必须 要求'),
    (r'有哪些', '列表 汇总'),
    (r'包含哪些', '列表 汇总'),
    (r'啥是', '定义 概念'),
    (r'上课时间', '课程安排 时间表'),
    (r'教室', '上课地点 教室'),
]


def rewrite_query(query: str) -> str:
    """
    查询改写：口语化→专业表述

    Args:
        query: 原始查询

    Returns:
        改写后的查询
    """
    rewritten = query
    for pattern, replacement in _REWRITE_RULES:
        if re.search(pattern, rewritten):
            rewritten = re.sub(pattern, replacement, rewritten)
            break  # 只应用第一个匹配的规则

    # 如果查询太短，尝试扩展
    if len(rewritten) < 10:
        intent = analyze_intent(query)
        if intent["keywords"]:
            extra = " ".join(intent["keywords"][:3])
            if extra not in rewritten:
                rewritten = rewritten + " " + extra

    return rewritten.strip()


# ============================================================
# 5. 粗筛: coarse_filter()
# ============================================================

def coarse_filter(query: str, intent: Optional[Dict] = None) -> Dict[str, Any]:
    """
    粗筛：根据意图识别结果，缩小搜索范围（章节/页码范围）

    Returns:
        {"chapters": [int], "page_ranges": [(start, end)], "content_types": [str]}
    """
    if intent is None:
        intent = analyze_intent(query)

    filters = {
        "chapters": [],
        "page_ranges": [],
        "content_types": [],
    }

    q = query
    intent_type = intent["type"]

    # 章节限定
    if "答辩" in q or "时间" in q or "日期" in q or "地点" in q:
        filters["chapters"].extend([0])  # 前言/课程信息
        filters["page_ranges"].append((1, 7))
    if "成绩" in q or "评分" in q or "占比" in q or "分数" in q:
        filters["chapters"].extend([0])
        filters["page_ranges"].append((1, 7))
    if "综合设计A" in q or "设计A" in q:
        filters["chapters"].append(6)
    if "综合设计B" in q or "设计B" in q:
        filters["chapters"].append(7)
    if "综合设计" in q and not filters["chapters"]:
        filters["chapters"].extend([6, 7])
    if "预备实验" in q or "预备" in q:
        filters["chapters"].append(2)
    if "基本语言" in q or "语言实验" in q:
        filters["chapters"].append(3)
    if "基本接口" in q or "接口实验" in q:
        filters["chapters"].append(4)
    if "基本传感" in q or "传感实验" in q or "传感器" in q:
        filters["chapters"].append(5)
    if "实验系统" in q or "实验板" in q or "开发板" in q:
        filters["chapters"].append(8)
    if "软件" in q or "Keil" in q or "Proteus" in q or "工具" in q:
        filters["chapters"].append(9)
    if "C51" in q or "C语言" in q:
        filters["chapters"].append(10)
    if "报告" in q or "模板" in q or "格式" in q:
        filters["chapters"].append(11)
    if "芯片" in q or "DS18B20" in q or "ADC" in q or "传感器" in q:
        if not filters["chapters"]:
            filters["chapters"].extend([4, 5])

    # 根据意图类型调整
    if intent_type == "table":
        # 表格查询优先搜索含表格的chunk
        filters["content_types"].append("mixed")
    elif intent_type == "exact":
        # 精确查询不需要限定章节
        pass

    # 去重
    filters["chapters"] = list(dict.fromkeys(filters["chapters"]))
    filters["content_types"] = list(dict.fromkeys(filters["content_types"]))

    # 如果没有限定，返回空（表示全量搜索）
    if not filters["chapters"] and not filters["page_ranges"] and not filters["content_types"]:
        return {"chapters": None, "page_ranges": None, "content_types": None}

    return filters


# ============================================================
# 6. 融合层: RRF融合 + 加权融合
# ============================================================

def rrf_fusion_four_paths(
    paths: Dict[str, List[Dict]],
    k: int = 60,
    top_k: int = 15,
) -> List[Dict]:
    """
    四路 RRF (Reciprocal Rank Fusion) 融合

    公式: score(doc) = sum(1 / (k + rank_i))  for each path i

    Args:
        paths: multi_recall() 返回的四路结果
        k: RRF 平滑参数 (默认60)
        top_k: 融合后返回数量

    Returns:
        融合后的文档列表
    """
    rrf_scores = defaultdict(float)
    doc_map = {}  # chunk_id -> best item

    for path_name, results in paths.items():
        for rank, item in enumerate(results):
            cid = item["chunk_id"]
            rrf_score = 1.0 / (k + rank + 1)
            rrf_scores[cid] += rrf_score
            # 保留第一次出现的item（或分数最高的）
            if cid not in doc_map:
                doc_map[cid] = item

    # 排序
    sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    fused = []
    for cid, rrf_score in sorted_ids:
        item = doc_map[cid]
        item["fusion_score"] = round(rrf_score, 6)
        item["fusion_method"] = "rrf"
        fused.append(item)

    return fused


def weighted_fusion(
    paths: Dict[str, List[Dict]],
    weights: Optional[Dict[str, float]] = None,
    intent: Optional[Dict] = None,
    top_k: int = 15,
) -> List[Dict]:
    """
    加权融合：根据查询意图动态调整各路径权重

    默认权重策略（基于意图）：
    - exact:   keyword=0.5, vector=0.3, structured=0.2, graph=0.0
    - concept: vector=0.5,  keyword=0.2, structured=0.1, graph=0.2
    - compare: vector=0.3,  keyword=0.1, structured=0.3, graph=0.3
    - table:   keyword=0.3, vector=0.2,  structured=0.4, graph=0.1
    - procedure: vector=0.3, keyword=0.3, structured=0.2, graph=0.2

    Args:
        paths: multi_recall() 返回的四路结果
        weights: 自定义权重 {"vector": 0.3, "keyword": 0.3, "structured": 0.2, "graph": 0.2}
        intent: 意图分析结果
        top_k: 返回数量

    Returns:
        加权融合后的文档列表
    """
    # 如果未提供权重，根据意图自动选择
    if weights is None:
        if intent is None:
            intent_type = "concept"
        else:
            intent_type = intent["type"]

        weight_presets = {
            "exact":     {"vector": 0.3, "keyword": 0.5, "structured": 0.2, "graph": 0.0},
            "concept":   {"vector": 0.5, "keyword": 0.2, "structured": 0.1, "graph": 0.2},
            "compare":   {"vector": 0.3, "keyword": 0.1, "structured": 0.3, "graph": 0.3},
            "table":     {"vector": 0.2, "keyword": 0.3, "structured": 0.4, "graph": 0.1},
            "procedure": {"vector": 0.3, "keyword": 0.3, "structured": 0.2, "graph": 0.2},
        }
        weights = weight_presets.get(intent_type, {"vector": 0.35, "keyword": 0.35, "structured": 0.15, "graph": 0.15})

    # 归一化权重
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}

    # 对每个路径的分数做归一化（min-max归一化到[0,1]）
    norm_paths = {}
    for path_name, results in paths.items():
        if not results:
            norm_paths[path_name] = {}
            continue
        scores = [r["score"] for r in results]
        min_s, max_s = min(scores), max(scores)
        range_s = max_s - min_s if max_s > min_s else 1.0
        norm_paths[path_name] = {
            r["chunk_id"]: (r["score"] - min_s) / range_s
            for r in results
        }

    # 加权求和
    weighted_scores = defaultdict(float)
    doc_map = {}
    for path_name, results in paths.items():
        w = weights.get(path_name, 0.0)
        if w == 0.0:
            continue
        for item in results:
            cid = item["chunk_id"]
            norm_score = norm_paths[path_name].get(cid, 0.0)
            weighted_scores[cid] += w * norm_score
            if cid not in doc_map:
                doc_map[cid] = item

    # 排序
    sorted_ids = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    fused = []
    for cid, w_score in sorted_ids:
        item = doc_map[cid]
        item["fusion_score"] = round(w_score, 6)
        item["fusion_method"] = "weighted"
        item["fusion_weights"] = weights
        fused.append(item)

    return fused


def fuse(query: str, paths: Optional[Dict] = None, method: str = "rrf",
         weights: Optional[Dict] = None, intent: Optional[Dict] = None,
         top_k: int = 15) -> List[Dict]:
    """
    融合入口：自动选择 RRF 或加权融合

    Args:
        query: 查询文本
        paths: 四路召回结果（None则自动调用multi_recall）
        method: "rrf" 或 "weighted"
        weights: 自定义权重（仅weighted模式）
        intent: 意图分析结果
        top_k: 融合后返回数量
    """
    if paths is None:
        paths = multi_recall(query, top_k=25)

    if intent is None:
        intent = analyze_intent(query)

    if method == "weighted":
        return weighted_fusion(paths, weights=weights, intent=intent, top_k=top_k)
    else:
        return rrf_fusion_four_paths(paths, k=60, top_k=top_k)


# ============================================================
# 7. 精排层 (Re-rank)
# ============================================================

# --- Cross-Encoder 相关 ---
_cross_encoder = None

def _get_cross_encoder():
    """懒加载 Cross-Encoder 模型"""
    global _cross_encoder
    if _cross_encoder is None:
        try:
            from sentence_transformers import CrossEncoder
            _cross_encoder = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2",
                device="cpu"
            )
            print("[Cross-Encoder] 模型加载成功: cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            print(f"[Cross-Encoder] 加载失败: {e}，将使用 BM25 替代")
            _cross_encoder = None
    return _cross_encoder


def _cross_encoder_rerank(query: str, candidates: List[Dict]) -> List[Tuple[int, float]]:
    """
    使用 Cross-Encoder 对候选文档逐对打分

    Returns:
        [(candidate_index, relevance_score), ...]  按分数降序
    """
    model = _get_cross_encoder()
    if model is None:
        return None  # 降级到 BM25

    pairs = []
    for cand in candidates:
        content = cand.get("content", "")
        # 截断过长文本（Cross-Encoder 有token限制）
        if len(content) > 500:
            content = content[:500]
        pairs.append([query, content])

    try:
        scores = model.predict(pairs, show_progress_bar=False)
        indexed_scores = [(i, float(s)) for i, s in enumerate(scores)]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores
    except Exception as e:
        print(f"[Cross-Encoder] 预测失败: {e}")
        return None


def _bm25_score(query: str, document: str, avgdl: float = 200.0,
                k1: float = 1.5, b: float = 0.75) -> float:
    """简化的 BM25 分数计算"""
    # 分词
    q_tokens = [t for t in jieba.cut(query) if len(t.strip()) >= 2]
    d_tokens = [t for t in jieba.cut(document) if len(t.strip()) >= 2]

    if not q_tokens or not d_tokens:
        return 0.0

    dl = len(d_tokens)
    # 词频统计
    tf = defaultdict(int)
    for t in d_tokens:
        tf[t] += 1

    score = 0.0
    for qt in q_tokens:
        if qt not in tf:
            continue
        f = tf[qt]
        # BM25 公式
        idf = 1.0  # 简化，不做完整IDF
        numerator = f * (k1 + 1)
        denominator = f + k1 * (1 - b + b * dl / avgdl)
        score += idf * numerator / denominator

    return score


def _title_match_score(query: str, chapter: str, section: str) -> float:
    """标题匹配度"""
    q_words = set(jieba.cut(query.lower()))
    ch_words = set(jieba.cut(chapter.lower()))
    sec_words = set(jieba.cut(section.lower()))

    if not q_words:
        return 0.0

    ch_overlap = q_words & ch_words
    sec_overlap = q_words & sec_words

    ch_score = len(ch_overlap) / max(len(q_words), 1)
    sec_score = len(sec_overlap) / max(len(q_words), 1)

    return ch_score * 0.6 + sec_score * 0.4


def _page_proximity_score(chunk_pages: List[int], target_pages: Optional[List[int]]) -> float:
    """页码邻近度：如果粗筛指定了页码范围，chunk越靠近目标给分越高"""
    if not target_pages or not chunk_pages:
        return 0.0
    min_dist = min(abs(cp - tp) for cp in chunk_pages for tp in target_pages)
    return 1.0 / (1.0 + min_dist * 0.1)


def _bm25_title_page_rerank(
    query: str,
    candidates: List[Dict],
    coarse_filters: Optional[Dict] = None,
) -> List[Tuple[int, float]]:
    """
    BM25 + 标题匹配度 + 页码邻近度 综合精排
    """
    # 提取目标页码
    target_pages = None
    if coarse_filters and coarse_filters.get("page_ranges"):
        target_pages = []
        for start, end in coarse_filters["page_ranges"]:
            target_pages.extend(range(start, end + 1))

    scores = []
    for i, cand in enumerate(candidates):
        bm25 = _bm25_score(query, cand.get("content", ""))
        title = _title_match_score(
            query,
            cand.get("chapter", ""),
            cand.get("section", ""),
        )
        page_prox = _page_proximity_score(
            cand.get("pages", []),
            target_pages,
        )

        # 综合分数
        combined = bm25 * 0.4 + title * 0.35 + page_prox * 0.25
        scores.append((i, combined))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def rerank(
    query: str,
    candidates: List[Dict],
    top_k: int = 5,
    coarse_filters: Optional[Dict] = None,
    use_cross_encoder: bool = True,
) -> List[Dict]:
    """
    精排层：Cross-Encoder 优先，降级到 BM25+标题+页码综合

    Args:
        query: 查询文本
        candidates: 融合后的候选文档列表
        top_k: 最终返回数量
        coarse_filters: 粗筛结果（用于页码邻近度）
        use_cross_encoder: 是否使用 Cross-Encoder

    Returns:
        精排后的 top_k 文档
    """
    # 先尝试 Cross-Encoder
    ce_scores = None
    if use_cross_encoder:
        ce_scores = _cross_encoder_rerank(query, candidates)

    if ce_scores is not None:
        # Cross-Encoder 成功
        ranked = []
        for idx, ce_score in ce_scores[:top_k]:
            cand = candidates[idx].copy()
            cand["rerank_score"] = round(ce_score, 4)
            cand["rerank_method"] = "cross-encoder"
            ranked.append(cand)
        return ranked

    # 降级: BM25 + 标题 + 页码
    bm25_scores = _bm25_title_page_rerank(query, candidates, coarse_filters)
    ranked = []
    for idx, bm25_score in bm25_scores[:top_k]:
        cand = candidates[idx].copy()
        cand["rerank_score"] = round(bm25_score, 4)
        cand["rerank_method"] = "bm25+title+page"
        ranked.append(cand)

    return ranked


# ============================================================
# 8. 引用格式化
# ============================================================

def format_citation(item: Dict) -> Dict:
    """
    为每个结果生成完整引用信息

    Returns:
        {
            "chunk_id": str,
            "content": str,          # 原文内容
            "chapter": str,          # 章节路径，如 "第6章 单片机综合设计A → 6.3 实验内容"
            "section": str,
            "page": int,             # PDF页码
            "score": float,          # 最终相关度分数
            "source_text": str,      # 原文片段（前200字）
            "citation": str,         # 完整引用文本
        }
    """
    cid = item.get("chunk_id", "")
    content = item.get("content", "")
    chapter = item.get("chapter", "")
    section = item.get("section", "")
    page = item.get("page", 0)
    pages = item.get("pages", [])
    score = item.get("rerank_score", item.get("fusion_score", item.get("score", 0)))

    # 章节路径
    chapter_path = chapter
    if section:
        chapter_path += f" -> {section}"

    # 页码
    page_str = f"PDF第{page}页"
    if len(pages) > 1:
        page_str = f"PDF第{pages[0]}-{pages[-1]}页"

    # 原文片段（前200字）
    source_text = content[:200].replace("\n", " ") if content else ""
    if len(content) > 200:
        source_text += "..."

    # 完整引用
    citation = f"{chapter_path}，{page_str}"

    return {
        "chunk_id": cid,
        "content": content,
        "chapter": chapter_path,
        "section": section,
        "page": page,
        "pages": pages,
        "score": round(score, 4),
        "source_text": source_text,
        "citation": citation,
    }


# ============================================================
# 9. 统一接口: search()
# ============================================================

def search(
    query: str,
    top_k: int = 5,
    weights: Optional[Dict[str, float]] = None,
    fusion_method: str = "weighted",
    use_cross_encoder: bool = True,
    verbose: bool = False,
) -> List[Dict]:
    """
    完整流水线：意图识别 → 查询改写 → 粗筛 → 多路召回 → 融合 → 精排 → 引用

    Args:
        query: 用户查询
        top_k: 最终返回数量
        weights: 自定义融合权重 {"vector": 0.3, "keyword": 0.3, ...}
        fusion_method: 融合方法 "rrf" 或 "weighted"
        use_cross_encoder: 是否使用 Cross-Encoder 精排
        verbose: 是否打印详细日志

    Returns:
        [{
            "chunk_id": str,
            "content": str,
            "chapter": str,       # "第6章 单片机综合设计A → 6.3 实验内容"
            "section": str,
            "page": int,          # PDF页码
            "score": float,       # 相关度分数
            "source_text": str,   # 原文片段（前200字）
            "citation": str,      # 完整引用
        }]
    """
    original_query = query

    # Step 1: 意图识别
    intent = analyze_intent(query)
    if verbose:
        print(f"[意图识别] type={intent['type']}, confidence={intent['confidence']}")
        print(f"[意图识别] scores={intent['scores']}")

    # Step 2: 查询改写
    rewritten = rewrite_query(query)
    if rewritten != query:
        if verbose:
            print(f"[查询改写] '{original_query}' -> '{rewritten}'")
        query = rewritten

    # Step 3: 粗筛
    coarse = coarse_filter(query, intent)
    if verbose:
        print(f"[粗筛] chapters={coarse.get('chapters')}, page_ranges={coarse.get('page_ranges')}")

    # Step 4: 多路召回
    if verbose:
        print(f"[多路召回] 正在检索四路...")
    paths = multi_recall(query, top_k=25)
    if verbose:
        for pname, results in paths.items():
            print(f"  [{pname}] {len(results)} results")

    # Step 5: 融合
    if verbose:
        print(f"[融合] method={fusion_method}")
    fused = fuse(query, paths=paths, method=fusion_method, weights=weights, intent=intent, top_k=15)
    if verbose:
        print(f"[融合] 产出 {len(fused)} 候选文档")

    # Step 6: 精排
    if verbose:
        print(f"[精排] use_cross_encoder={use_cross_encoder}")
    ranked = rerank(query, fused, top_k=top_k, coarse_filters=coarse,
                    use_cross_encoder=use_cross_encoder)
    if verbose:
        print(f"[精排] 最终产出 {len(ranked)} 文档")

    # Step 7: 引用格式化
    results = [format_citation(item) for item in ranked]

    return results


# ============================================================
# 10. 批量测试 & 对比
# ============================================================

def test_pipeline():
    """测试完整流水线"""
    test_queries = [
        # 精确查询
        "DS18B20是什么",
        "P-A-3#的步骤",
        # 概念查询
        "什么是综合设计",
        "单片机原理",
        # 对比查询
        "综合设计A和B的区别",
        "I2C和SPI哪个好",
        # 表格/数据查询
        "成绩组成",
        "实验有哪些",
        # 流程查询
        "怎么验收",
        "啥时候答辩",
        "咋写报告",
        # 口语化改写测试
        "多少分",
        "咋提交",
        "接线方法",
    ]

    print("=" * 80)
    print("融合层 + 精排层 完整流水线测试")
    print("=" * 80)

    for query in test_queries:
        print(f"\n{'─' * 80}")
        print(f"查询: {query}")
        print(f"{'─' * 80}")

        try:
            results = search(query, top_k=3, fusion_method="weighted",
                           use_cross_encoder=True, verbose=False)
            for i, r in enumerate(results):
                print(f"  [{i+1}] score={r['score']:.4f} | {r['citation']}")
                print(f"       {r['source_text'][:120]}...")
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("测试完成")
    print("=" * 80)


def compare_methods(query: str = "答辩时间是什么时候"):
    """对比不同融合方法和精排方法的效果"""
    print(f"\n{'=' * 80}")
    print(f"融合方法对比: '{query}'")
    print(f"{'=' * 80}")

    # 意图 + 改写 + 粗筛
    intent = analyze_intent(query)
    rewritten = rewrite_query(query)
    coarse = coarse_filter(rewritten, intent)
    print(f"意图: {intent['type']} (confidence={intent['confidence']})")
    print(f"改写: '{rewritten}'")
    print(f"粗筛: {coarse}")

    # 多路召回
    paths = multi_recall(rewritten, top_k=25)
    for pname, results in paths.items():
        print(f"  召回 [{pname}]: {len(results)} results")

    # RRF 融合
    rrf_results = fuse(rewritten, paths=paths, method="rrf", top_k=5)
    print(f"\n  [RRF融合] top 5:")
    for i, r in enumerate(rrf_results):
        print(f"    [{i+1}] {r['chapter']} | page={r['page']} | score={r['fusion_score']:.4f}")

    # 加权融合
    weighted_results = fuse(rewritten, paths=paths, method="weighted", intent=intent, top_k=5)
    print(f"\n  [加权融合] top 5:")
    for i, r in enumerate(weighted_results):
        print(f"    [{i+1}] {r['chapter']} | page={r['page']} | score={r['fusion_score']:.4f}")

    # 精排
    reranked = rerank(rewritten, weighted_results, top_k=3, coarse_filters=coarse,
                      use_cross_encoder=True)
    print(f"\n  [精排后] top 3:")
    for i, r in enumerate(reranked):
        print(f"    [{i+1}] {r['chapter']} | page={r['page']} | "
              f"score={r['rerank_score']:.4f} | method={r['rerank_method']}")


# ============================================================
# 11. 模块导出
# ============================================================

__all__ = [
    # 核心流水线
    "search",
    "multi_recall",
    "fuse",
    "rerank",
    "format_citation",
    # 意图 & 改写
    "analyze_intent",
    "rewrite_query",
    "coarse_filter",
    # 融合方法
    "rrf_fusion_four_paths",
    "weighted_fusion",
    # 精排方法
    "_cross_encoder_rerank",
    "_bm25_title_page_rerank",
    # 辅助
    "test_pipeline",
    "compare_methods",
]


# ============================================================
# 12. 主入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="融合层 + 精排层 测试")
    parser.add_argument("--query", "-q", type=str, default=None,
                        help="单次查询测试")
    parser.add_argument("--compare", "-c", type=str, default=None,
                        help="对比不同融合方法")
    parser.add_argument("--test", "-t", action="store_true",
                        help="运行批量测试")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    args = parser.parse_args()

    if args.compare:
        compare_methods(args.compare)
    elif args.query:
        results = search(args.query, top_k=5, verbose=args.verbose)
        print(f"\n查询: {args.query}")
        for i, r in enumerate(results):
            print(f"\n[{i+1}] {r['citation']}")
            print(f"    分数: {r['score']:.4f}")
            print(f"    原文: {r['source_text']}")
    elif args.test:
        test_pipeline()
    else:
        # 默认运行对比
        compare_methods("答辩时间是什么时候")
        print()
        test_pipeline()