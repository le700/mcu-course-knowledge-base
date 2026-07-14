# P-A-3# 温度记录器设计

## 项目概述

基于 IAP15F2K61S2 单片机的温度记录器系统，实现串口通信、LED控制、数码管显示、PCF8591模拟温度采集和DS18B20数字温度采集功能。

## 硬件平台

| 组件 | 型号/引脚 |
|------|-----------|
| MCU | IAP15F2K61S2, 11.0592MHz |
| 数码管 | 8位共阴，段选P0→0xE0(74HC573)，位选P0→0xC0(74HC573) |
| LED | 8个，P0→0x80(74HC573) |
| ADC | PCF8591, I2C, SDA=P2.1, SCL=P2.0 |
| 温度传感器 | DS18B20, 单总线, DQ=P1.4 |
| 按键 | S4=P3.3, S5=P3.2, S6=P3.1 |
| 串口 | 波特率4800，方式1，定时器2 1T模式 |
| 译码 | 74HC573片选通过P2口+SN74HC02译码 |

## 工程结构

```
P-A-3工程/
├── common/                     # 公共模块（Keil C51版本）
│   ├── board.h                 # 硬件定义（引脚、地址、类型）
│   ├── delay.h / delay.c       # 延时函数
│   ├── led.h / led.c           # LED控制（74HC573）
│   ├── display.h / display.c   # 8位数码管驱动（74HC573）
│   ├── pcf8591.h / pcf8591.c   # PCF8591 I2C ADC驱动
│   ├── ds18b20.h / ds18b20.c   # DS18B20 单总线驱动
│   └── uart.h / uart.c         # 串口驱动（4800bps）
├── pa3_main/                   # 主工程（Keil版本）
│   ├── src/
│   │   └── main.c              # 主程序（4步状态机）
│   └── pa3_main.uvproj         # Keil uVision5 工程文件
├── sdcc/                       # SDCC 编译版本
│   ├── board.h                 # 硬件定义（SDCC __sfr/__sbit 语法）
│   ├── delay.h / delay.c       # 延时函数（__asm__("nop")）
│   ├── led.h / led.c           # LED控制
│   ├── display.h / display.c   # 8位数码管驱动
│   ├── pcf8591.h / pcf8591.c   # PCF8591 I2C ADC驱动
│   ├── ds18b20.h / ds18b20.c   # DS18B20 单总线驱动
│   ├── uart.h / uart.c         # 串口驱动
│   ├── main.c                  # 主程序（__bit/__interrupt 语法）
│   ├── Makefile                # SDCC 编译脚本
│   └── pa3.ihx                 # 编译产物（Intel HEX 格式）
└── README.md                   # 本说明文件
```

## 编译方法

### 方法一：Keil C51 (uVision5)

1. 使用 Keil uVision5 打开 `pa3_main/pa3_main.uvproj`
2. 确保工程包含以下源文件：
   - `common/` 目录下所有 `.c` 文件
   - `pa3_main/src/main.c`
3. 编译（Project → Build Target）生成 HEX 文件
4. 使用 STC-ISP 工具烧录到 IAP15F2K61S2 单片机

### 方法二：SDCC (Small Device C Compiler)

**前置条件**：安装 SDCC 4.0.0 或更高版本

```bash
# 进入 SDCC 目录
cd sdcc/

# 清理旧编译产物
make clean

# 编译
make
```

编译产物：
- `pa3.ihx` — Intel HEX 格式固件（可直接烧录）
- `*.rel` — 各模块目标文件
- `*.lst / *.rst / *.asm` — 中间汇编文件（调试用）
- `pa3.map / pa3.mem` — 内存映射文件

**Keil C51 与 SDCC 版本差异**：

| 项目 | Keil C51 | SDCC |
|------|----------|------|
| 头文件 | `<REG52.H>` | `<8052.h>` |
| SFR 定义 | `sfr AUXR = 0x8E;` | `__sfr __at(0x8E) AUXR;` |
| 位变量 | `sbit SDA = P2^1;` | `__sbit __at(0xA1) SDA;` |
| bit 类型 | `bit` | `__bit` |
| code 存储 | `code` | `__code` |
| 中断函数 | `void ISR(void) interrupt 1` | `void ISR(void) __interrupt(1)` |
| 内嵌汇编 | `_nop_();` | `__asm__("nop");` |

## 四步实验流程

### 第1步：串口通信
- PC端串口助手（波特率4800）发送任意数据
- 单片机接收后在8个LED上显示该数据（二进制形式）
- 同时将该数据回传至PC端
- 收到特定数据 `0xAA` 后解锁，进入第2步

### 第2步：S4按键控制
- 按下 S4 按键（P3.3）
- 8个LED全部点亮
- 进入第3步

### 第3步：PCF8591模拟温度采集
- 按下 S5 按键（P3.2）
- 通过 PCF8591 读取 RB2（通道3）电压信号
- 0-5V 映射为 0-80°C（公式: `temp = (ADC * 8000) / 255`）
- 数码管显示格式: `A  xx.x`

### 第4步：DS18B20数字温度采集
- 按下 S6 按键（P3.1）
- 通过 DS18B20 读取真实温度
- 温度转换: 原始值 × 0.0625°C
- 支持负数温度显示（显示格式: `B -xx.x`）
- 数码管显示格式: `B  xx.x`（正温度）或 `B -xx.x`（负温度）

## 代码质量修复记录（v1.1）

本版本针对以下6个问题进行了修复：

| 编号 | 文件 | 问题 | 修复 |
|------|------|------|------|
| 1 | `uart.c` | 定时器2配置顺序错误：`AUXR \|= 0x04`（T2R=1）在设置 T2L/T2H/T2x12 之前启动 | 将 `AUXR \|= 0x04` 移至所有 T2 配置完成后 |
| 2 | `pcf8591.c` | `I2C_ReadByte()` 缺少显式 NACK 时钟脉冲 | 在读取8位数据后增加第9个时钟脉冲，主机发送 NACK（SDA=1） |
| 3 | `main.c` | DS18B20 负数温度处理：`(u32)raw * 625 / 100` 中 `raw` 为 `u16`，负数时 `u16→u32` 强转丢失符号位 | 检测 MSB bit7，若为负数则二补码转绝对值后再计算，并传递负号标志给显示函数 |
| 4 | `main.c` | `ds18b20_read_temp()` 已定义但未使用，代码内联重复了 DS18B20 读取逻辑 | `Update_Display()` 改为调用 `ds18b20_read_temp()` 库函数 |
| 5 | `display.c` | 段码表注释 "bit7=a" 实际应为 "bit7=dp"（0x80 对应 dp 段） | 修正为 `bit7=dp, bit6=g, bit5=f, bit4=e, bit3=d, bit2=c, bit1=b, bit0=a` |
| 6 | `delay.c` | `delay_us` 注释说"约1us"但实际约3-4us | 修正注释为"约 3~4us 延时（含函数调用开销）" |

## 关键技术点

1. **数码管消影**：每次切换位选前先关闭段选（P0=0xFF），防止重影
2. **DS18B20时序**：读写操作时关闭中断（EA=0）保证精确时序
3. **按键消抖**：20ms延时二次检测，确保按键动作可靠
4. **74HC573片选**：通过P2口高3位+SN74HC02或非门译码控制
5. **温度更新**：定时器0中断中每300ms（150×2ms）触发一次温度采集更新
6. **负数温度**：检测DS18B20原始值MSB bit7，二补码转绝对值，数码管位置1显示负号
7. **I2C NACK**：读最后一个字节后主机发送NACK（第9个时钟SDA=1），再发停止信号
8. **定时器2启动顺序**：先配置 T2L/T2H/T2x12，最后启动 T2R，避免波特率错误

## 模块依赖关系

```
main.c
├── board.h        (硬件定义、类型定义)
├── delay.h/c      (微秒/毫秒延时)
├── led.h/c        (LED 控制)
├── display.h/c    (数码管显示)
├── uart.h/c       (串口通信)
├── pcf8591.h/c    (I2C ADC) → delay.h/c
└── ds18b20.h/c    (单总线温度) → delay.h/c
```

## 参考

- 基于 P-A-1 源码架构改编
- 参考《综合设计A报告》温度记录器设计
- IAP15F2K61S2 数据手册（STC15系列）
- PCF8591 数据手册（NXP）
- DS18B20 数据手册（Maxim/Dallas）