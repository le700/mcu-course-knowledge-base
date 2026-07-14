# MCU Course Knowledge Base

> 克隆即用：让 AI 编程智能体直接接手单片机课程设计。无需上下文，零学习成本。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-71/71-brightgreen.svg)](octopus_hub/test_e2e.py)
[![Knowledge Graph](https://img.shields.io/badge/KG-123_nodes_205_edges-blue.svg)](rag_v4/knowledge_graph.json)
[![Agent-Ready](https://img.shields.io/badge/Agent-Ready-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 目录

- [What is this?](#what-is-this)
- [Quick Start (for AI Agents)](#quick-start-for-ai-agents)
- [Supported AI Coding Agents](#supported-ai-coding-agents)
- [Knowledge Graph](#knowledge-graph)
- [课程设计覆盖情况](#课程设计覆盖情况)
- [System Architecture](#system-architecture)
- [Module Reference](#module-reference)
- [Project Structure](#project-structure)
- [Design Philosophy](#design-philosophy)
- [Tech Stack](#tech-stack)
- [Contributors](#contributors)

---

## What is this?

**The Problem** — 单片机课程设计要求学生掌握芯片引脚、传感器协议、电路连接、代码框架等大量细节。AI 编程智能体（Trae WorkBuddy、Claude Code、Codex 等）可以辅助开发，但它们缺少课程特定的硬件知识，每次对话都要重新灌输上下文，效率极低。

**The Solution** — 这个仓库是一个 **Agent-First 知识库**。它把芯片引脚表、传感器手册、电路连接、代码模板、设计依赖链全部以结构化格式（JSON + Markdown）存放在仓库里。任何能读 Git 仓库的 AI 编程智能体，克隆后就能直接查阅和使用，无需额外上下文。

**一句话**：`git clone` → 开始干活。

| 项目 | 内容 |
|------|------|
| **学校** | 北京石油化工学院 (BIPT) |
| **年级** | 2023级 |
| **专业** | 电气工程及其自动化 / 自动化 |
| **课程** | 单片机程序设计实践 |
| **课程性质** | 工程实训 / 综合设计 |

---

## Quick Start (for AI Agents)

**如果你是一个 AI 编程智能体，请按以下步骤操作：**

### Step 1 — Clone

```bash
git clone https://github.com/le700/mcu-course-knowledge-base.git
cd mcu-course-knowledge-base
```

### Step 2 — 读取知识（零依赖，最快方式）

```bash
# 知识图谱：123 个节点、205 条边，覆盖芯片/传感器/协议/课程设计
cat rag_v4/knowledge_graph.json

# 硬件参考：P-A-1# 温湿度检测系统的完整硬件文档
cat rag_v4/hardware_ref_pa1.md
```

这两个文件是纯 JSON 和 Markdown，任何 Agent 都能直接解析。读完你就知道：

- 有哪些芯片可用（AT89C51、STC89C52、ATmega16 等）
- 每个芯片的引脚功能、封装、接线方式
- 各课程设计之间的依赖关系
- 温湿度检测系统的完整硬件架构

### Step 3 — 查看项目源码

```bash
ls projects/
# P-A-1源码参考/     — P-A-1# 温湿度检测系统 (C51 源码 + 13 个分步诊断)
# P-A-3工程/         — P-A-3# 多传感器数据采集 (C51 + SDCC 双版本)
# P-B-4#炉温控制系统/ — P-B-4# 炉温控制系统 (PID+PWM 闭环控制, 5 阶段文档)
# P-B-5汇总/         — P-B-5# 智能交通灯 (7 篇设计文档)
```

### Step 4 — 启动记忆中枢（可选，需要 Python 3.10+）

```bash
pip install -r requirements.txt --break-system-packages
cd octopus_hub && python test_e2e.py
```

```python
from octopus_hub import OctopusSystem

system = OctopusSystem(
    kg_path="rag_v4/knowledge_graph.json",
    hardware_ref_path="rag_v4/hardware_ref_pa1.md"
)

# 查询芯片引脚
print(system.query("AT89C51的引脚功能"))

# 查询设计依赖链
print(system.query("温湿度检测系统的设计依赖链"))

# 获取芯片快速参考
print(system.query("DHT11快速参考"))
```

### Step 5 — 多智能体协作

```python
# Agent A 注册项目并开始会话
system.register_project("智能交通灯", "基于AT89C51的交通灯控制系统")
session = system.start_session("智能交通灯")

# Agent A 添加关键决策到记忆
system.add_memory("选择共阳极数码管，P0口段选，P2口位选")

# Agent B 通过交接协议接手，获取完整上下文
context = system.handoff(target_agent="Agent B", depth="standard")

# 会话结束时自动反思
summary = system.end_session_with_reflection()
```

---

## Supported AI Coding Agents

| Agent | 使用方式 |
|--------|----------|
| **Trae WorkBuddy** | 直接克隆到工作区，Agent 读取 `rag_v4/` 和 `octopus_hub/` |
| **Claude Code** | `git clone` 后，Claude 自动索引项目文件作为上下文 |
| **OpenAI Codex CLI** | 克隆后，Codex 可直接读取 `knowledge_graph.json` 和 `hardware_ref_pa1.md` |
| **OpenClaw** | 作为知识基座，所有 Agent 通过 OctopusHub 共享记忆 |
| **Cursor** | 直接打开仓库文件夹，Cursor 自动索引所有代码和文档 |
| **GitHub Copilot** | 仓库中的结构化知识文件可直接被 Copilot 引用 |
| **Windsurf / Cody** | 支持仓库级上下文索引，自动加载知识图谱 |

> **通用原则**：只要你的 AI 编程工具能读 Git 仓库，它就能用这个知识库。Agent 不需要提前"知道"单片机——它只需要能读 `knowledge_graph.json` 和 `hardware_ref_pa1.md`。

---

## Knowledge Graph

`rag_v4/knowledge_graph.json` — **123 节点、205 条边**，Agent 直接解析 JSON 即可检索。

| 类别 | 内容 | 节点数 |
|------|------|--------|
| 芯片型号 | AT89C51, STC89C52, ATmega16, MSP430, STM32F103 等 | 15+ |
| 传感器 | DHT11, DHT22, DS18B20, BMP180, HC-SR04, MQ-2 等 | 12+ |
| 显示模块 | LCD1602, LCD12864, OLED, 数码管, 点阵屏 | 8+ |
| 通信协议 | I2C, SPI, UART, 1-Wire, RS485 | 5+ |
| 课程设计 | 温湿度检测、炉温控制、智能交通灯、数字钟、电子琴等 | 10+ |
| 编程概念 | 定时器、中断、PID、PWM、ADC、看门狗、EEPROM 等 | 15+ |
| 引脚表 | 每个芯片的完整引脚功能表 | 7 |

**关系类型**：`uses_chip`, `depends_on`, `has_pin`, `connects_to`, `uses_protocol`, `requires_peripheral`, `based_on_experiment`, `uses_concept`, `has_teacher`, `has_class` 等。

---

## 课程设计覆盖情况

| 课题 | 源码 | 硬件文档 | 设计文档 | Agent 可独立完成 |
|------|:----:|:--------:|:--------:|:----------------:|
| P-A-1# 温湿度检测 | ✅ C51 | ✅ 完整 | ✅ | ✅ 是 |
| P-A-2# 光控系统 | ❌ | ❌ | ❌ | ❌ 仅有框架 |
| P-A-3# 多传感器采集 | ✅ C51+SDCC | ⚠️ 部分 | ✅ | ✅ 是 (SDCC) |
| P-A-4# 智能交通灯 | ❌ | ❌ | ❌ | ❌ 仅有框架 |
| P-A-5# | ❌ | ❌ | ❌ | ❌ 无内容 |
| P-B-1~P-B-3 | ❌ | ❌ | ❌ | ❌ 无内容 |
| P-B-4# 炉温控制系统 | ✅ C51 | ✅ 原理图 | ✅ 5阶段 | ✅ 是 |
| P-B-5# 智能交通灯 | ❌ | ❌ | ✅ 7篇 | ⚠️ 可参考文档 |
| P-B-6# | ❌ | ❌ | ❌ | ❌ 无内容 |

> **3 个课题 Agent 可直接接手**：P-A-1# 温湿度检测、P-B-4# 炉温控制系统、P-A-3# 多传感器采集。`hardware_ref_pa1.md` 和 P-B-4# 的 5 阶段文档格式可作为其他课题的模板。

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Agent 层                           │
│   ┌─────────┐  ┌──────────┐  ┌──────────────┐      │
│   │ 代码智能体│  │ 硬件智能体│  │ 文档智能体    │      │
│   └────┬─────┘  └────┬─────┘  └──────┬───────┘      │
│        │              │               │              │
├────────┼──────────────┼───────────────┼──────────────┤
│        ▼              ▼               ▼              │
│   ┌─────────────────────────────────────────┐       │
│   │         HandoffProtocol (交接协议)       │       │
│   │   3 级深度: minimal / standard / full    │       │
│   └──────────────────┬──────────────────────┘       │
│                      │                              │
├──────────────────────┼──────────────────────────────┤
│                      ▼                              │
│   ┌─────────────────────────────────────────┐       │
│   │          OctopusHub (中枢核心)            │       │
│   │  ┌─────────┐ ┌────────┐ ┌───────────┐   │       │
│   │  │ 项目管理  │ │人格存档 │ │ 记忆存储   │   │       │
│   │  └─────────┘ └────────┘ └───────────┘   │       │
│   │  ┌──────────────┐ ┌──────────────────┐   │       │
│   │  │ 反思引擎      │ │ 向量语义搜索      │   │       │
│   │  └──────────────┘ └──────────────────┘   │       │
│   └──────────────────┬──────────────────────┘       │
│                      │                              │
├──────────────────────┼──────────────────────────────┤
│                      ▼                              │
│   ┌─────────────────────────────────────────┐       │
│   │           HubBridge (桥接层)              │       │
│   │  芯片查询 → 知识图谱 / 硬件文档路由        │       │
│   │  设计查询 → 依赖链分析                    │       │
│   │  通用查询 → RAG 检索                      │       │
│   └──────────────────┬──────────────────────┘       │
│                      │                              │
├──────────────────────┼──────────────────────────────┤
│                      ▼                              │
│   ┌─────────────────────────────────────────┐       │
│   │          RAG v4 (知识库底座)              │       │
│   │  ┌──────────┐ ┌──────────┐ ┌─────────┐  │       │
│   │  │ 知识图谱  │ │ 向量检索  │ │关键词检索│  │       │
│   │  │123节点    │ │ChromaDB  │ │TF-IDF   │  │       │
│   │  │205边     │ │          │ │         │  │       │
│   │  └──────────┘ └──────────┘ └─────────┘  │       │
│   └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

### Reflection Loop

```
Memory Storage → Session End → Auto-Trigger Reflection
    ↑                              ↓
    └── Rule Extraction + TF-IDF → Key Decisions / Errors / Insights
        Deduplicated → Vector DB
```

---

## Module Reference

### Octopus Hub (`octopus_hub/`)

| Module | File | Description |
|--------|------|-------------|
| **Data Models** | `models.py` | 4 dataclasses (Project, Persona, MemoryFragment, Session); 2 enums (MemoryType × 7, SessionStatus × 4) |
| **Storage** | `storage.py` | SQLite persistence, 4 tables, JSON fields, advanced queries |
| **Core** | `core.py` | OctopusHub: project/session/memory/persona management API |
| **KG Adapter** | `kg_adapter.py` | Knowledge graph loader, BFS traversal, dependency chain analysis, chip pinout queries |
| **Bridge** | `hub_bridge.py` | Unified query router: chip→KG/hardware, design→dependency chain, general→RAG; LRU cache |
| **Hardware Parser** | `hardware_parser.py` | Parses `hardware_ref_pa1.md`, extracts 11 chip structures, 28 quick references |
| **HW Parser** | `hw_parser.py` | Standalone hardware parser, extensible chip queries |
| **Vector Store** | `memory_vector_store.py` | SentenceTransformer (384d) + ChromaDB, dedup (cosine > 0.85), KMeans clustering |
| **Reflection** | `reflection.py` | 30+ Chinese regex patterns + TF-IDF key sentence extraction + auto-trigger loop |
| **Handoff** | `handoff.py` | 3 depth levels: minimal (~50 tokens), standard (~500), full (~1500) |
| **Integration** | `integration.py` | OctopusSystem unified entry, one-shot session + reflection |
| **CLI** | `cli.py` | 10 commands: init, project, session, memory, stats |
| **Tests** | `test_e2e.py` | 71 test cases covering all 10 modules |

### RAG v4 (`rag_v4/`) — Agent 直接读取

| File | Format | Usage |
|------|--------|-------|
| `knowledge_graph.json` | JSON | Direct parse, BFS/DFS traversal for chips, sensors, dependencies |
| `hardware_ref_pa1.md` | Markdown | Complete hardware doc for P-A-1# temp/humidity detection |
| `agent_tools.py` | Python | 3-layer retrieval API: vector + keyword + structured query |
| `chunks.pkl` | Pickle | Preprocessed text chunks for vector retrieval |
| `keyword_index.pkl` | Pickle | TF-IDF keyword index |
| `struct_index.json` | JSON | Structured data index |

---

## Project Structure

```
mcu-course-knowledge-base/
├── README.md
├── requirements.txt
├── .gitignore
├── build_fusion_rerank.py
│
├── octopus_hub/                       # 八爪鱼记忆中枢 (12 modules, 71 tests)
│   ├── __init__.py
│   ├── models.py                      # Data models
│   ├── storage.py                     # SQLite storage
│   ├── core.py                        # OctopusHub core
│   ├── kg_adapter.py                  # Knowledge graph adapter
│   ├── hub_bridge.py                  # Unified query bridge
│   ├── hardware_parser.py             # Hardware doc parser (11 chips)
│   ├── hw_parser.py                   # Standalone HW parser
│   ├── memory_vector_store.py         # Vector semantic search
│   ├── reflection.py                  # Reflection engine
│   ├── handoff.py                     # Handoff protocol
│   ├── integration.py                 # Integration layer
│   ├── cli.py                         # CLI tools
│   └── test_e2e.py                    # E2E tests (71 cases)
│
├── rag_v4/                            # Knowledge base (Agent reads directly)
│   ├── knowledge_graph.json           # 123 nodes, 205 edges
│   ├── hardware_ref_pa1.md            # Hardware reference
│   ├── agent_tools.py                 # RAG engine
│   ├── chunks.pkl
│   ├── keyword_index.pkl
│   ├── struct_index.json
│   └── test_rag.py
│
├── projects/                          # Course design projects
│   ├── P-A-1源码参考/                  # P-A-1# 温湿度检测 (C51 + 13 diagnostics)
│   │   ├── 00_源码说明_先看我.txt
│   │   ├── P-A-1-Codex参考_README.md
│   │   ├── common/                    # Driver libs (adc0809, dht11, display, i8255, led, uart)
│   │   ├── diagnostics/               # 13 step-by-step diagnostics
│   │   ├── pa1_main/                  # Main program (Keil uVision)
│   │   └── step03~step09/             # 6 progressive learning steps
│   ├── P-A-3工程/                      # P-A-3# 多传感器采集 (C51 + SDCC)
│   │   ├── P-A-3_审查报告.md
│   │   ├── common/                    # Driver libs (ds18b20, pcf8591, display, led, uart)
│   │   ├── pa3_main/                  # Main program (Keil uVision)
│   │   └── sdcc/                      # SDCC build (with Makefile)
│   ├── P-B-4#炉温控制系统/              # P-B-4# 炉温控制 (PID+PWM closed-loop)
│   │   ├── main.c                     # Complete C51 source
│   │   ├── 阶段1-项目需求规格说明书.md
│   │   ├── 阶段2-硬件设计说明及硬件原理图.md
│   │   ├── 阶段3-软件流程图.md
│   │   ├── 阶段4-源代码及代码审查报告.md
│   │   ├── 阶段5-Bug调试日志.md        # 5-day debug log (12 bugs)
│   │   └── images/
│   └── P-B-5汇总/                      # P-B-5# 智能交通灯 (7 design docs)
│       ├── 01_项目需求规格说明书.md
│       ├── 02_硬件设计说明文档.md
│       ├── 03_代码审查报告.md
│       ├── 04_bug解决日志.md
│       ├── 05_人机协作反思.md
│       ├── 06_agent_mcp_skills.md
│       ├── 07_软件流程图_mermaid.md
│       └── 程序流程图.html
│
├── reports/                           # Analysis & audit reports
│   ├── analysis/                      # 13 deep analysis reports
│   ├── audit/                         # 2 HTML audit reports
│   └── agent_b_data/                  # Agent B intermediate data
│
├── course_docs/                       # Course documents
│   ├── 任务书/
│   ├── 参考模板/                       # Report templates (5 docx + 1 md)
│   ├── 实验报告/
│   └── 原理图/                         # CT107D board schematics
│
├── assets/                            # Source code archives
│   ├── P-A-1-源码_发给同学.zip
│   ├── P-A-3工程_完整代码.zip
│   └── 接口技术综合实验A原理图_参考.zip
│
└── rag_archive/                       # RAG evolution history
    ├── rag_v1/
    ├── rag_v2/
    └── rag_v3/
```

---

## Design Philosophy

### Why "Octopus"?

八爪鱼（Octopus）的每条触手都有独立的神经系统，但所有触手都连接到同一个中枢大脑：

- **触手 = Agent** — 每个 Agent 独立工作，处理特定领域任务
- **中枢 = Hub** — 所有 Agent 通过 Hub 进行上下文交接，无需重复传递历史
- **记忆 = 神经网络** — 关键决策和错误被提炼、压缩、存档，供后续 Agent 调用

### Why No Local LLM?

本系统使用 **SentenceTransformer + TF-IDF + ChromaDB** 替代本地 LLM，原因：

- **零 GPU 依赖** — 普通 CPU 即可运行，部署门槛极低
- **零 Token 浪费** — 语义搜索和反思提取全部本地完成，不消耗 API 配额
- **确定性推理** — 规则引擎 + 向量检索，结果可复现、可调试

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Semantic Search | all-MiniLM-L6-v2 (384d) | Vector similarity search |
| Keyword Extraction | TF-IDF + jieba | Key sentence extraction |
| Rule Engine | 30+ Chinese regex patterns | Reflection pattern matching |

---

## Tech Stack

| Technology | Purpose |
|------|------|
| **Python 3.10+** | Core language |
| **SQLite** | Persistent storage |
| **SentenceTransformer** | Vector encoding (all-MiniLM-L6-v2) |
| **ChromaDB** | Vector database |
| **scikit-learn** | TF-IDF, KMeans clustering |
| **jieba** | Chinese word segmentation |
| **JSON / Markdown** | Agent-readable knowledge format |

---

## Contributors

- **组员A** — 架构设计 & 全栈开发
- **组长** — 课程设计协调
- **组员B** — 硬件测试

指导教师：**某教师**

---

## License

MIT License

---

*Made for MCU Course Design at BIPT · 2024-2025*