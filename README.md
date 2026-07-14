# 北京石油化工学院 单片机程序设计课程知识库

> **八爪鱼记忆中枢 + RAG v4 知识图谱** — 面向单片机课程设计的智能知识管理系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-71%2F71%20Passed-brightgreen.svg)](octopus_hub/test_e2e.py)

---

## 项目简介

本项目是**北京石油化工学院 单片机程序设计课程**的智能知识库系统，融合了两种前沿架构：

- **八爪鱼记忆中枢 (Octopus Hub)**：多智能体记忆中枢，支持项目路由、人格存档、反思闭环，实现 Agent 间无感上下文交接
- **RAG v4 知识图谱**：119 节点、199 条边的课程知识图谱，三层检索（向量 + 关键词 + 结构化查询）

两项技术深度融合，构建了 **Agent 层 → 交接协议 → 中枢核心 → 桥接层 → 知识库** 的五层架构，为单片机课程设计提供从芯片选型到代码编写的全流程智能支持。

---

## 课程信息

| 项目 | 内容 |
|------|------|
| **学校** | 北京石油化工学院 (BIPT) |
| **课程** | 单片机程序设计课程设计 |
| **班级** | 电231班 |
| **教师** | 李晶 |
| **组长** | 丁家硕 |
| **组员** | 岳金豪、马敏涛 |

---

## 系统架构

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
│   │  │119节点    │ │ChromaDB  │ │TF-IDF   │  │       │
│   │  │199边     │ │          │ │         │  │       │
│   │  └──────────┘ └──────────┘ └─────────┘  │       │
│   └─────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────┘
```

### 反思闭环

```
记忆存储 → 会话结束 → 自动反思触发
    ↑                      ↓
    └── 规则提取 + TF-IDF   → 关键决策/错误/洞察
        去重后存入向量数据库
```

---

## 模块详解

### 八爪鱼记忆中枢 (`octopus_hub/`)

| 模块 | 文件 | 功能 |
|------|------|------|
| **数据模型** | `models.py` | 4 个数据类：Project, Persona, MemoryFragment, Session；2 个枚举：MemoryType (7 种), SessionStatus (4 种) |
| **存储层** | `storage.py` | SQLite 持久化存储，4 张表 (projects, personas, memories, sessions)，支持 JSON 字段和高级查询 |
| **核心中枢** | `core.py` | OctopusHub 类：项目/会话/记忆/人格管理 API |
| **知识图谱适配器** | `kg_adapter.py` | 加载 knowledge_graph.json，BFS 遍历，设计依赖链分析，芯片引脚查询 |
| **桥接层** | `hub_bridge.py` | 统一查询路由：芯片→KG/硬件文档，设计→依赖链，通用→RAG；LRU 缓存 |
| **硬件解析器** | `hardware_parser.py` | 解析 hardware_ref_pa1.md，提取 11 个芯片的结构化数据，28 条快速参考 |
| **向量语义搜索** | `memory_vector_store.py` | SentenceTransformer (384维) + ChromaDB，去重 (余弦相似度>0.85)，KMeans 聚类 |
| **反思引擎** | `reflection.py` | 规则提取 (30+ 中文模式) + TF-IDF 关键句提取 + 自动触发循环 |
| **交接协议** | `handoff.py` | 3 级深度：minimal (~50 tokens), standard (~500), full (~1500) |
| **集成层** | `integration.py` | OctopusSystem 统一入口，一站式会话 + 反思 |
| **命令行** | `cli.py` | 10 个 CLI 命令：init, project, session, memory, stats |
| **端到端测试** | `test_e2e.py` | 71 个测试用例，覆盖全部 10 个模块 |

### RAG v4 知识库 (`rag_v4/`)

| 文件 | 说明 |
|------|------|
| `knowledge_graph.json` | 119 节点、199 条边的单片机课程知识图谱 |
| `hardware_ref_pa1.md` | P-A-1# 温湿度检测系统硬件参考文档 |
| `agent_tools.py` | RAG 检索引擎，三层检索架构 |
| `chunks.pkl` | 预处理的文本块 |
| `keyword_index.pkl` | TF-IDF 关键词索引 |
| `struct_index.json` | 结构化数据索引 |
| `test_rag.py` | RAG 模块测试 |

---

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
# 克隆仓库
git clone https://github.com/le700/mcu-course-knowledge-base.git
cd mcu-course-knowledge-base

# 安装依赖
pip install -r requirements.txt --break-system-packages

# (可选) 安装中文分词
pip install jieba --break-system-packages
```

### 基础使用

```python
from octopus_hub import OctopusSystem

# 初始化系统
system = OctopusSystem(
    kg_path="rag_v4/knowledge_graph.json",
    hardware_ref_path="rag_v4/hardware_ref_pa1.md",
    db_path="hub.db"
)

# 注册项目
system.register_project(
    name="温湿度检测系统",
    description="基于DHT11的温湿度监测与报警系统",
    tags=["传感器", "LCD显示", "报警"]
)

# 开始会话
session = system.start_session("温湿度检测系统")

# 查询芯片信息
result = system.query("AT89C51的引脚功能")
print(result)

# 查询设计依赖
deps = system.query("温湿度检测系统的设计依赖链")
print(deps)

# 添加记忆
system.add_memory("选择了DHT11而非DHT22，因为精度要求不高")

# 结束会话并自动反思
summary = system.end_session_with_reflection()
```

### CLI 命令行

```bash
# 初始化
python -m octopus_hub.cli init

# 注册项目
python -m octopus_hub.cli project register "温湿度检测系统" \
  --desc "基于DHT11的温湿度监测与报警系统" \
  --tags "传感器,LCD显示,报警"

# 列出项目
python -m octopus_hub.cli project list

# 开始会话
python -m octopus_hub.cli session start "温湿度检测系统"

# 添加记忆
python -m octopus_hub.cli memory add "选择了DHT11而非DHT22"

# 搜索记忆
python -m octopus_hub.cli memory search "DHT11"

# 查看统计
python -m octopus_hub.cli stats
```

### 运行测试

```bash
cd octopus_hub
python test_e2e.py
# 预期输出: 71/71 tests passed

cd rag_v4
python test_rag.py
```

---

## 知识图谱覆盖范围

知识图谱包含 **119 个节点** 和 **199 条边**，覆盖以下领域：

- **芯片型号**: AT89C51, STC89C52, ATmega16, MSP430 等
- **传感器**: DHT11, DHT22, DS18B20, BMP180, HC-SR04 等
- **显示模块**: LCD1602, LCD12864, OLED, 数码管
- **通信协议**: I2C, SPI, UART, 1-Wire
- **课程设计**: 温湿度检测、智能交通灯、超声波测距、数字钟等
- **编程概念**: 定时器、中断、PWM、ADC、看门狗等

---

## 设计理念

### 为什么叫"八爪鱼"？

八爪鱼（Octopus）的每条触手都有独立的神经系统，但所有触手都连接到同一个中枢大脑。这正是本系统的设计哲学：

- **触手 = Agent**：每个 Agent 独立工作，处理特定领域任务
- **中枢 = Hub**：所有 Agent 通过 Hub 进行上下文交接，无需重复传递历史
- **记忆 = 神经网络**：关键决策和错误被提炼、压缩、存档，供后续 Agent 调用

### 为什么不用本地大模型？

为避免浪费 token 和降低部署门槛，本系统使用 **SentenceTransformer + TF-IDF + ChromaDB** 替代本地 LLM：

- **语义搜索**: all-MiniLM-L6-v2 (384维) 提供向量相似度搜索
- **关键词提取**: TF-IDF + jieba 分词实现关键句提取
- **规则引擎**: 30+ 中文模式匹配实现反思提取

无需 GPU，普通 CPU 即可运行。

---

## 项目结构

```
mcu-course-knowledge-base/
├── README.md                          # 本文件
├── requirements.txt                   # Python 依赖
├── .gitignore                         # Git 忽略规则
├── P-A-1-Codex参考_README.md          # P-A-1# 温湿度检测系统参考文档
├── octopus_hub/                       # 八爪鱼记忆中枢
│   ├── __init__.py                    # 包入口，优雅降级导入
│   ├── models.py                      # 数据模型 (Project, Persona, Memory, Session)
│   ├── storage.py                     # SQLite 存储层 (4 表)
│   ├── core.py                        # 中枢核心 (OctopusHub)
│   ├── kg_adapter.py                  # 知识图谱适配器 (BFS, 依赖链)
│   ├── hub_bridge.py                  # 桥接层 (统一查询路由)
│   ├── hardware_parser.py             # 硬件文档解析器 (11 芯片)
│   ├── memory_vector_store.py         # 向量语义搜索 (ChromaDB)
│   ├── reflection.py                  # 反思引擎 (规则 + TF-IDF)
│   ├── handoff.py                     # 交接协议 (3 级深度)
│   ├── integration.py                 # 集成层 (OctopusSystem)
│   ├── cli.py                         # 命令行工具 (10 个命令)
│   └── test_e2e.py                    # 端到端测试 (71 用例)
└── rag_v4/                            # RAG v4 知识库
    ├── knowledge_graph.json           # 知识图谱 (119 节点, 199 边)
    ├── hardware_ref_pa1.md            # 硬件参考文档
    ├── agent_tools.py                 # RAG 检索引擎
    ├── chunks.pkl                     # 文本块
    ├── keyword_index.pkl              # 关键词索引
    ├── struct_index.json              # 结构化索引
    └── test_rag.py                    # RAG 测试
```

---

## 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.10+** | 主语言 |
| **SQLite** | 持久化存储 |
| **SentenceTransformer** | 向量语义编码 (all-MiniLM-L6-v2) |
| **ChromaDB** | 向量数据库 |
| **scikit-learn** | TF-IDF, KMeans 聚类 |
| **jieba** | 中文分词 |
| **GitHub CLI** | 版本管理 |

---

## 贡献者

- **岳金豪** — 架构设计 & 全栈开发
- **丁家硕** (组长) — 课程设计协调
- **马敏涛** — 硬件测试

指导教师：**李晶**

---

## 许可证

MIT License

---

*Made with 🩶 at 北京石油化工学院 (BIPT) · 电231班 · 2024-2025 学年*