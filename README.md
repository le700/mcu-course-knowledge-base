# 单片机程序设计课程知识库

> **Agent-First 知识库** — 一份仓库，喂给任何 AI 编程智能体即可直接接手单片机课程设计

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-71%2F71%20Passed-brightgreen.svg)](octopus_hub/test_e2e.py)
[![Agent-Ready](https://img.shields.io/badge/Agent-Ready-brightgreen.svg)]()

---

## 这个仓库是干什么的？

**一句话：克隆这个仓库到你的 AI 编程智能体（Trae WorkBuddy / Claude Code / Codex / OpenClaw / Cursor 等）的工作区，它就能直接开始干活。**

仓库里包含了单片机课程设计所需的全部知识——芯片引脚、传感器手册、电路连接、代码模板、设计依赖链，全部以结构化格式存放，AI 智能体无需额外上下文就能直接查阅和使用。

---

## 支持的 AI 编程智能体

| 智能体 | 使用方式 |
|--------|----------|
| **Trae WorkBuddy** | 直接克隆到工作区，Agent 读取 `rag_v4/` 和 `octopus_hub/` 即可 |
| **Claude Code** | `git clone` 后，Claude 自动索引项目文件作为上下文 |
| **OpenAI Codex CLI** | 克隆后，Codex 可直接读取 `knowledge_graph.json` 和 `hardware_ref_pa1.md` |
| **OpenClaw** | 作为知识基座，所有 Agent 通过 OctopusHub 共享记忆 |
| **Cursor** | 直接打开仓库文件夹，Cursor 会自动索引所有代码和文档 |
| **GitHub Copilot** | 仓库中的结构化知识文件可直接被 Copilot 引用 |
| **Windsurf / Cody** | 支持仓库级上下文索引，自动加载知识图谱 |

> **通用原则**：只要你的 AI 编程工具能读 Git 仓库，它就能用这个知识库。Agent 不需要提前"知道"单片机——它只需要能读 `knowledge_graph.json` 和 `hardware_ref_pa1.md`。

---

## Agent 使用指南（写给 AI 智能体看）

**如果你是一个 AI 编程智能体（如 Trae WorkBuddy、Claude Code、Codex 等），请按以下步骤使用本仓库：**

### 1. 克隆仓库

```bash
git clone https://github.com/le700/mcu-course-knowledge-base.git
cd mcu-course-knowledge-base
```

### 2. 了解仓库结构

本仓库有两个核心目录：

| 目录 | 用途 | 你该怎么做 |
|------|------|-----------|
| `rag_v4/` | 静态知识库（知识图谱 + 硬件文档 + 检索工具） | **直接读取** `knowledge_graph.json` 和 `hardware_ref_pa1.md` |
| `octopus_hub/` | 动态记忆系统（项目管理 + 会话记忆 + 反思引擎） | **安装依赖后运行**，管理多项目上下文 |

### 3. 直接读取知识（最快方式，无需安装任何依赖）

```bash
# 知识图谱：119 个节点、199 条边，覆盖芯片/传感器/协议/课程设计
cat rag_v4/knowledge_graph.json

# 硬件参考：P-A-1# 温湿度检测系统的完整硬件文档
cat rag_v4/hardware_ref_pa1.md
```

这两个文件是纯 JSON 和 Markdown，任何 Agent 都能直接解析。读完你就知道：
- 有哪些芯片可用（AT89C51、STC89C52、ATmega16 等）
- 每个芯片的引脚功能、封装、接线方式
- 各课程设计之间的依赖关系
- 温湿度检测系统的完整硬件架构

### 4. 启动记忆中枢（可选，需要 Python 3.10+）

```bash
pip install -r requirements.txt --break-system-packages

# 运行端到端测试确认环境正常
cd octopus_hub && python test_e2e.py
```

然后你就可以通过 Python API 使用完整的记忆系统：

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

### 5. 多智能体协作模式

如果你需要多个 Agent 协作完成同一个课程设计：

```python
# Agent A 注册项目并开始会话
system.register_project("智能交通灯", "基于AT89C51的交通灯控制系统")
session = system.start_session("智能交通灯")

# Agent A 添加关键决策到记忆
system.add_memory("选择共阳极数码管，P0口段选，P2口位选")

# Agent B 通过交接协议接手，获取完整上下文
context = system.handoff(target_agent="Agent B", depth="standard")
# Agent B 现在拥有 Agent A 的所有关键决策和上下文

# 会话结束时自动反思
summary = system.end_session_with_reflection()
```

---

## 知识图谱速览

`rag_v4/knowledge_graph.json` — **119 节点、199 条边**，Agent 可以直接解析 JSON 获取：

| 类别 | 内容 | 节点数 |
|------|------|--------|
| 芯片型号 | AT89C51, STC89C52, ATmega16, MSP430, STM32F103 等 | 15+ |
| 传感器 | DHT11, DHT22, DS18B20, BMP180, HC-SR04, MQ-2 等 | 12+ |
| 显示模块 | LCD1602, LCD12864, OLED, 数码管, 点阵屏 | 8+ |
| 通信协议 | I2C, SPI, UART, 1-Wire, RS485 | 5+ |
| 课程设计 | 温湿度检测、智能交通灯、超声波测距、数字钟、电子琴等 | 10+ |
| 编程概念 | 定时器、中断、PWM、ADC、看门狗、EEPROM 等 | 15+ |
| 引脚表 | 每个芯片的完整引脚功能表 | 11 |

**边的关系类型**：`uses_chip`, `depends_on`, `has_pin`, `connects_to`, `uses_protocol`, `has_teacher`, `has_class` 等。

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

### RAG v4 知识库 (`rag_v4/`) — Agent 直接读取

| 文件 | 格式 | Agent 如何使用 |
|------|------|---------------|
| `knowledge_graph.json` | JSON | 直接解析，BFS/DFS 遍历查询芯片、传感器、依赖关系 |
| `hardware_ref_pa1.md` | Markdown | 直接读取，包含温湿度检测系统的完整硬件文档 |
| `agent_tools.py` | Python | 提供三层检索 API：向量检索 + 关键词检索 + 结构化查询 |
| `chunks.pkl` | Pickle | 预处理的文本块，供向量检索使用 |
| `keyword_index.pkl` | Pickle | TF-IDF 关键词索引 |
| `struct_index.json` | JSON | 结构化数据索引 |

---

## 项目结构

```
mcu-course-knowledge-base/
├── README.md                          # 本文件（Agent 使用指南）
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
└── rag_v4/                            # RAG v4 知识库（Agent 直接读取）
    ├── knowledge_graph.json           # 知识图谱 (119 节点, 199 边)
    ├── hardware_ref_pa1.md            # 硬件参考文档
    ├── agent_tools.py                 # RAG 检索引擎
    ├── chunks.pkl                     # 文本块
    ├── keyword_index.pkl              # 关键词索引
    ├── struct_index.json              # 结构化索引
    └── test_rag.py                    # RAG 测试
```

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

## 技术栈

| 技术 | 用途 |
|------|------|
| **Python 3.10+** | 主语言 |
| **SQLite** | 持久化存储 |
| **SentenceTransformer** | 向量语义编码 (all-MiniLM-L6-v2) |
| **ChromaDB** | 向量数据库 |
| **scikit-learn** | TF-IDF, KMeans 聚类 |
| **jieba** | 中文分词 |
| **JSON / Markdown** | Agent 可直接读取的知识格式 |

---

## 贡献者

- **组员A** — 架构设计 & 全栈开发
- **组长** — 课程设计协调
- **组员B** — 硬件测试

指导教师：**某教师**

---

## 许可证

MIT License

---

*Made with ❤️ for MCU Course Design · 2024-2025 学年*