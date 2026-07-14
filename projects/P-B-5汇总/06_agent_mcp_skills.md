# Agent MCP Skills 文档

**项目：** 智能交通灯控制系统  
**日期：** 2026-07-14

---

## 一、项目中使用的 Skills

### 1. full-project-output

**用途：** 51 单片机 Keil 工程项目创建和管理  
**触发条件：** 创建 51 单片机项目、STM32 项目、ESP32 项目等嵌入式工程  
**核心规则：**
- 始终从 `D:\Desktop\DEMO` 复制模板项目，不从零创建
- 保持原有项目结构和配置文件不变
- 只修改必要的源文件

**在本项目中的应用：**
- 基于 `D:\Desktop\DEMO\51工程模板` 创建 Keil C51 工程
- 保留 STARTUP.A51、Projectr.uvproj 等配置文件
- 只修改 main.c 源代码

---

### 2. flowchart-style-guide

**用途：** 程序流程图绘制规范  
**触发条件：** 绘制程序流程图、算法流程图、状态机图  
**核心规则：**
- 纯黑白两色，不允许彩色
- 起止框：圆角矩形
- 处理框：直角矩形
- 判断框：菱形（必须是菱形，不能用矩形）
- 线条：只允许水平线和垂直线，不允许斜线
- 箭头：一条线只能有一个箭头，紧贴下一个框的边缘
- 多对一连线使用公共竖线
- 菱形连接点对准顶点

**在本项目中的应用：**
- 绘制了 6 张 SVG 流程图（主程序、SystemTick2ms、HandleKeys、Timer0ISR、状态机、CalcGreenTime）
- 严格遵循黑白风格规范
- 所有判断框使用菱形，连线无斜线

---

### 3. monochrome-report-docs

**用途：** 黑白风格报告/文档生成  
**触发条件：** 生成课程设计报告、实验报告、技术文档  
**核心规则：**
- 纯黑白配色，不允许彩色
- 表格无底色，黑框线
- 图片/流程图使用黑白
- 保留教师/模板要求的格式

**在本项目中的应用：**
- 生成技术参考文档（Markdown 和 DOCX 格式）
- 所有表格使用黑框线，无底色
- 代码审查报告、bug 解决日志等均遵循黑白风格

---

## 二、相关 MCP 工具

### 2.1 Keil C51 编译

**工具路径：** `D:\Keil_v5\UV4\UV4.exe`  
**编译命令：**
```bash
& "D:\Keil_v5\UV4\UV4.exe" -r "项目路径\uvproj" -o "输出路径\build_log.txt"
```
**注意事项：**
- C51 项目必须使用 `.uvproj` 格式（不是 `.uvprojx`）
- ToolsetName 必须是 `MCS-51`（不是 `C51`）
- 目标芯片选择 STC89C52RC 或 AT89C52

---

### 2.2 Proteus 仿真

**仿真文件：** `.pdsprj` 格式（Proteus 8）  
**关键设置：**
- MCU 的 Program File 指向编译生成的 `.hex` 文件
- Clock Frequency 设为 `11.0592MHz`
- 共阴数码管使用 `7SEG-MPX2-CC`
- OLED 使用 `SSD1306`
- 蜂鸣器使用 `BUZZER` (DC/Active)
- NPN 使用通用 `NPN`（不是 2N2222）

---

### 2.3 Python 文档生成

**工具：** python-docx 库  
**用途：** 生成 Word 文档（.docx）  
**注意事项：**
- 设置 run 颜色为黑色或默认
- 不设置表格单元格底色
- 不使用彩色标题样式

---

## 三、Skill 使用建议

### 3.1 何时使用哪个 Skill

| 场景 | 推荐 Skill |
|------|-----------|
| 创建新的 51 单片机项目 | full-project-output |
| 绘制程序流程图 | flowchart-style-guide |
| 生成技术报告/文档 | monochrome-report-docs |
| 调试 Proteus 仿真 | proteus-debug |
| 查找本地工具链路径 | local-toolchain-paths |

### 3.2 Skill 组合使用

**典型工作流：**
1. 使用 `full-project-output` 创建项目骨架
2. 编写代码并使用 Keil 编译
3. 使用 `flowchart-style-guide` 绘制流程图
4. 使用 `monochrome-report-docs` 生成文档
5. 使用 `proteus-debug` 调试仿真问题

---

## 四、Skill 文件位置

```
C:\Users\11349\.claude\skills\
├── flowchart-style-guide\
│   └── SKILL.md
├── monochrome-report-docs\
│   └── SKILL.md
├── full-project-output\
│   └── SKILL.md
├── proteus-debug\
│   └── SKILL.md
├── local-toolchain-paths\
│   └── SKILL.md
└── ...
```
