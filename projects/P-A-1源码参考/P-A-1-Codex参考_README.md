# P-A-1 温湿度检测系统详细 README

## 1. 项目简介

本工程是单片机工程实训 P-A-1 温湿度检测系统代码，目标板使用 STC89C54RD+，外接 8255A、ADC0809、DHT11、8 个 LED、8 个开关和 6 位数码管。

最终程序实现三个主要阶段：

1. 串口解锁：电脑通过串口发送大写 `A`，单片机收到后进入后续流程。
2. ADC 模拟温度显示：前四个开关 `SK0-SK3` 全为 1 后，读取 ADC0809 的 IN0 电位器，LED 显示 ADC 原始值，数码管显示 `Axx.xx`。
3. DHT11 环境温度显示：后四个开关 `SK4-SK7` 全为 1 后，读取 DHT11 环境温度，成功显示 `Cxx.00`，失败显示 `C88.88`。

当前正式版已经删除临时诊断代码，不再显示 `C04.00`、`C05.00`、`C00.00` 等调试信息。

## 2. 最终效果

### 2.1 上电初始状态

单片机上电后，数码管显示左侧提示 `A`，表示程序正在等待串口解锁。

### 2.2 串口解锁

串口助手设置：

- 波特率：`1200`
- 数据位：`8`
- 停止位：`1`
- 校验位：无

电脑发送大写 `A` 后：

- 单片机回传收到的字符；
- LED 显示收到的串口数据；
- 程序进入等待前四个开关阶段。

只有大写 `A` 能解锁，小写 `a` 或其他字符不会进入下一步。

### 2.3 ADC 阶段

当前四个开关 `SK0-SK3` 全部为 1 时，程序进入 ADC 阶段。

ADC 阶段现象：

- ADC0809 读取 IN0 电位器；
- ADC 原始值范围为 `0-255`；
- 8 个 LED 显示 ADC 原始值；
- 数码管显示 `Axx.xx`；
- 电位器变化时，LED 和数码管都会变化。

ADC 温度换算规则：

```c
adc_wendu_x100 = (u16)((u32)adc_zhi * 8000UL / 255UL);
```

含义：

- `adc_zhi = 0`，显示 `A00.00`
- `adc_zhi = 255`，显示 `A80.00`
- 中间值按比例换算

这里的 `Axx.xx` 是电位器模拟温度，不是 DHT11 真实环境温度。

### 2.4 DHT11 阶段

在 ADC 阶段基础上，继续打开后四个开关 `SK4-SK7`，使后四个开关也全为 1，程序进入 DHT11 环境温度阶段。

DHT11 阶段现象：

- 读取成功：显示 `C24.00`、`C25.00`、`C26.00` 这类环境温度；
- 轻微加热 DHT11 后，温度整数会有变化趋势；
- 读取失败：显示 `C88.88`。

说明：

DHT11 当前模块温度小数字节通常为 0，老师已经确认 `C25.00` 这种显示可以。重点是能显示温度趋势，格式保留两位小数即可。

## 3. 硬件定义

硬件定义集中在：

```text
common/board.h
```

关键定义如下：

```c
#define PPI_BASE_ADDR 0x0480
#define ADC0809_BASE_ADDR 0x4000
sbit ADC0809_EOC = P3^2;
sbit DHT11_IO = P3^3;
#define PA1_UNLOCK_BYTE 'A'
```

### 3.1 STC89C54RD+

- MCU：`STC89C54RD+`
- 内核：8051/8052 兼容
- 晶振：`12 MHz`

### 3.2 8255A

8255A 地址：

```c
#define PPI_BASE_ADDR 0x0480
```

端口分配：

- `PA0-PA7`：连接 LED；
- `PB0-PB7`：连接数码管段码；
- `PC0-PC7`：连接开关 `SK0-SK7`。

为什么使用 `0x0480`：

STC89C54RD+ 可能会把低地址 MOVX 区域映射到片内扩展 RAM。使用 `0x0480` 可以避开低地址内部 XRAM，同时仍满足 8255 片选逻辑。

### 3.3 ADC0809

ADC0809 地址：

```c
#define ADC0809_BASE_ADDR 0x4000
```

ADC0809 转换结束信号：

```c
sbit ADC0809_EOC = P3^2;
```

本工程读取通道：

```c
adc0809_read(0);
```

也就是 ADC0809 的 IN0 电位器。

### 3.4 DHT11

DHT11 数据线：

```c
sbit DHT11_IO = P3^3;
```

DHT11 返回 5 个字节：

1. 湿度整数
2. 湿度小数
3. 温度整数
4. 温度小数
5. 校验和

本实验只显示温度，不显示湿度；但湿度两个字节仍必须读取，因为校验和要用。

## 4. 工程目录结构

主要目录：

```text
P-A-1-TempHumidity-Keil/
├─ common/                  公共驱动代码
├─ pa1_main/                最终正式主程序
├─ step03_led_half/         分步小程序：LED 四亮四灭
├─ step04_switch_led/       分步小程序：开关控制 LED
├─ step05_display_4523/     分步小程序：数码管显示 45.23
├─ step06_adc_led/          分步小程序：ADC 原始值显示到 LED
├─ step07_adc_temp/         分步小程序：ADC 显示 Axx.xx
├─ step09_uart_echo/        分步小程序：串口回显
├─ HEX_烧录用/              烧录用 hex 文件
├─ build-all.ps1            一键构建脚本
└─ README_详细版.md         本文档
```

平时只需要重点看：

```text
pa1_main/src/main.c
common/
```

## 5. 关键源码文件说明

### 5.1 `pa1_main/src/main.c`

最终正式主程序。

主要负责：

- 串口解锁；
- 开关状态判断；
- ADC 阶段流程；
- DHT11 阶段流程；
- 数码管和 LED 显示调度。

核心状态：

```c
#define DENG_CHUANKOU   0
#define DENG_QIAN_SIGE  1
#define XIANSHI_ADC     2
#define XIANSHI_DHT11   3
```

含义：

- `DENG_CHUANKOU`：等待串口发送大写 `A`；
- `DENG_QIAN_SIGE`：等待前四个开关全为 1；
- `XIANSHI_ADC`：ADC 显示阶段；
- `XIANSHI_DHT11`：DHT11 环境温度显示阶段。

主要变量：

- `zhuangtai`：当前程序状态；
- `chuankou_zifu`：串口收到的字符；
- `kaiguan_zhi`：8 个开关读到的值；
- `adc_zhi`：ADC0809 原始数字量；
- `adc_wendu_x100`：ADC 模拟温度，扩大 100 倍保存；
- `huanjing_wendu_x100`：DHT11 环境温度，扩大 100 倍保存。

DHT11 阶段最终逻辑：

```c
if (dht11_chongshi_du_wendu(&huanjing_wendu_x100) != 0) {
    shumaguan_xianshi_wendu('C', huanjing_wendu_x100);
} else {
    shumaguan_xianshi_cuowu('C');
}
```

### 5.2 `common/board.h`

硬件地址和引脚定义文件。

这里定义：

- 8255 地址；
- ADC0809 地址；
- DHT11 引脚；
- ADC0809 EOC 引脚；
- 数码管位选端口；
- 串口解锁字符。

这个文件非常重要，不建议随意修改。

### 5.3 `common/i8255.c` 和 `common/i8255.h`

8255A 驱动。

主要函数：

```c
void i8255_init(void);
u8 du_kaiguan(void);
```

功能：

- 初始化 8255；
- 读取开关状态。

### 5.4 `common/led.c` 和 `common/led.h`

LED 驱动。

主要函数：

```c
void led_init(void);
void led_xianshi(u8 zhi);
void led_guanbi(void);
```

用途：

- 串口阶段显示收到的数据；
- ADC 阶段显示 ADC 原始值。

### 5.5 `common/adc0809.c` 和 `common/adc0809.h`

ADC0809 驱动。

主要函数：

```c
u8 adc0809_read(u8 channel);
u16 adc_zhuan_wendu_x100(u8 adc_zhi);
```

功能：

- `adc0809_read(0)` 读取 IN0 电位器；
- `adc_zhuan_wendu_x100()` 把 0-255 换算成 0.00-80.00 摄氏度。

### 5.6 `common/display.c` 和 `common/display.h`

六位数码管显示驱动。

主要函数：

```c
void display_init(void);
void shumaguan_qingkong(void);
void shumaguan_saomiao_yici(void);
void shumaguan_saomiao_duoci(u16 cishu);
void shumaguan_xianshi_wendu(char biaoqian, u16 wendu_x100);
void shumaguan_xianshi_cuowu(char biaoqian);
```

显示格式：

```text
第 1 位：A 或 C
第 2 位：空白
第 3 位：温度十位
第 4 位：温度个位，并带小数点
第 5 位：小数第一位
第 6 位：小数第二位
```

例子：

```text
A 23.45
C 25.00
C 88.88
```

### 5.7 `common/dht11.c` 和 `common/dht11.h`

DHT11 温度读取驱动。

正式对外函数：

```c
u8 dht11_du_wendu(u16 *huanjing_wendu_x100);
```

返回值：

- `1`：读取成功；
- `0`：读取失败。

内部仍读取湿度字节：

```c
u8 shidu_zhengshu;
u8 shidu_xiaoshu;
u8 wendu_zhengshu;
u8 wendu_xiaoshu;
u8 jiaoyanhe;
```

校验：

```c
jiaoyan_jisuan = (u8)(shidu_zhengshu + shidu_xiaoshu +
                      wendu_zhengshu + wendu_xiaoshu);

if (jiaoyan_jisuan != jiaoyanhe) {
    return 0;
}
```

最终温度计算：

```c
*huanjing_wendu_x100 = (u16)wendu_zhengshu * 100U;
```

也就是 DHT11 成功后显示 `Cxx.00`。

### 5.8 `common/uart.c` 和 `common/uart.h`

串口驱动。

主要函数：

```c
void uart_init_1200(void);
bit uart_received(void);
u8 uart_getchar(void);
void uart_putchar(u8 ch);
void uart_puts(char *str);
```

用途：

- 初始化 1200 波特率串口；
- 接收电脑发送的大写 `A`；
- 回传收到的字符；
- 输出调试提示字符串。

### 5.9 `common/delay.c` 和 `common/delay.h`

延时函数。

主要函数：

```c
void delay_us(u16 us);
void delay_ms(u16 ms);
```

DHT11、ADC、数码管扫描都会用到延时。

## 6. 分步小程序说明

这些小程序用于前期验证硬件，不是最终验收时必须打开的主程序。

| 工程 | 作用 |
| --- | --- |
| `step03_led_half` | LED 四亮四灭 |
| `step04_switch_led` | 开关状态显示到 LED |
| `step05_display_4523` | 数码管显示 45.23 |
| `step06_adc_led` | ADC 原始值显示到 LED |
| `step07_adc_temp` | ADC 显示 Axx.xx |
| `step09_uart_echo` | 串口 1200 波特率回显 |

最终任务主要打开：

```text
pa1_main/pa1_main.uvproj
```

## 7. 打开 Keil 的方法

推荐直接双击桌面快捷方式：

```text
打开这个_PA1最终Keil工程
```

它指向：

```text
C:\Users\user\Desktop\P-A-1-TempHumidity-Keil\pa1_main\pa1_main.uvproj
```

如果手动打开 Keil：

1. 打开 Keil uVision；
2. 选择 `Project -> Open Project`；
3. 打开 `pa1_main.uvproj`；
4. 点击 Build 编译。

## 8. 烧录说明

正式总程序 hex：

```text
C:\Users\user\Desktop\HEX_烧录用\07_pa1_main_总程序_最终正式版.hex
```

短路径备份：

```text
C:\stc_hex\pa1_main.hex
```

烧录后按流程测试：

1. 串口助手设置 1200；
2. 上电；
3. 发送大写 `A`；
4. 打开 `SK0-SK3`；
5. 调电位器，看 `Axx.xx`；
6. 打开 `SK4-SK7`；
7. 看 DHT11 显示 `Cxx.00`。

## 9. 验收演示流程

建议按下面顺序演示：

1. 说明硬件组成：STC89C54RD+、8255A、ADC0809、DHT11、LED、开关、六位数码管。
2. 打开串口助手，设置 1200 波特率。
3. 单片机上电，数码管显示 `A`。
4. 发送大写 `A`。
5. 说明串口收到数据后，LED 显示数据并回传电脑。
6. 打开前四个开关 `SK0-SK3`。
7. 调节电位器，说明 ADC 原始值显示在 LED 上，数码管显示 `Axx.xx`。
8. 打开后四个开关 `SK4-SK7`。
9. 说明进入 DHT11 环境温度阶段，显示 `C25.00` 这类真实环境温度。
10. 轻微加热 DHT11，观察温度变化趋势。
11. 说明如果 DHT11 读取失败，会显示 `C88.88`。

## 10. 答辩讲解词

可以这样讲：

本系统使用 STC89C54RD+ 单片机作为主控。程序启动后首先等待串口解锁，电脑通过串口发送大写 A，单片机收到后会把该字符显示到 LED，并原样回传给电脑，证明串口通信正常。

解锁后，程序等待前四个开关 SK0 到 SK3 全为 1。当前四个开关满足条件后，系统进入 ADC 阶段，读取 ADC0809 的 IN0 电位器。ADC 原始值范围是 0 到 255，程序把它显示到 8 个 LED 上，同时按照 0 到 80 摄氏度的范围换算，显示为 Axx.xx。

当后四个开关 SK4 到 SK7 也全为 1 时，系统进入 DHT11 环境温度阶段。DHT11 一次返回 5 个字节，包括湿度整数、湿度小数、温度整数、温度小数和校验和。本实验只显示温度，但湿度字节仍参与校验。校验成功后，程序显示 Cxx.00；如果读取失败或校验失败，显示 C88.88。

整个程序分层编写，主程序负责流程控制，公共驱动分别负责 8255、LED、开关、ADC0809、数码管、DHT11 和串口，结构比较清楚，方便调试和维护。

## 11. 不要随便改的地方

这些地方已经调通，后面不要随意修改：

```c
#define PPI_BASE_ADDR 0x0480
#define ADC0809_BASE_ADDR 0x4000
sbit ADC0809_EOC = P3^2;
sbit DHT11_IO = P3^3;
```

也不要随便改：

- DHT11 读位节奏；
- DHT11 30us 延时；
- DHT11 里的 `EA = 0` 和 `EA = ea_save`；
- ADC 换算公式；
- 数码管六位显示格式；
- 串口 1200 波特率。

## 12. 常见问题

### 12.1 为什么 DHT11 显示 C25.00，没有小数？

当前 DHT11 模块温度小数字节通常为 0，老师已确认这种显示可以。重点是显示温度趋势，格式保留两位小数即可。

### 12.2 为什么 ADC 有两位小数？

ADC 是电位器模拟温度，0-255 可以按比例换算成 0.00-80.00，所以能显示两位小数。

### 12.3 为什么 DHT11 要读湿度字节，但又不显示湿度？

DHT11 协议规定校验和等于前四个字节相加，前四个字节包括湿度整数和湿度小数。如果不读湿度字节，就无法正确校验温度数据。

### 12.4 为什么 DHT11 失败显示 C88.88？

`C88.88` 是统一错误提示，表示 DHT11 没有成功读取或校验失败。

### 12.5 为什么 8255 地址是 0x0480？

STC89C54RD+ 可能把低地址 MOVX 区域映射到片内扩展 RAM。使用 `0x0480` 可以避开低地址内部 RAM 区，同时满足 8255 片选。

## 13. 行数统计

最终主程序相关代码约 `856` 行，包括：

- `pa1_main/src/main.c`
- `common/*.c`
- `common/*.h`

如果包含所有 step 小程序，总 `.c/.h` 源码约 `956` 行。

## 14. 最后记住

平时只看这个工程：

```text
C:\Users\user\Desktop\P-A-1-TempHumidity-Keil\pa1_main\pa1_main.uvproj
```

平时只烧这个 hex：

```text
C:\Users\user\Desktop\HEX_烧录用\07_pa1_main_总程序_最终正式版.hex
```

刚打开 Keil 不知道从哪里看时，先看：

```text
pa1_main/src/main.c
```

这个文件就是最终程序的总流程。
