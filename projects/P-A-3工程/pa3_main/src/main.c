#include "board.h"
#include "delay.h"
#include "led.h"
#include "display.h"
#include "uart.h"
#include "pcf8591.h"
#include "ds18b20.h"

/* 全局变量 */
static u8 step = STEP_UART;          /* 当前步骤 */
static u8 mode = 0;                  /* 0=空闲, 1=PCF8591, 2=DS18B20 */
static bit Rx_flag = 0;              /* 串口接收标志 */
static u8 Rx_data;                   /* 串口接收数据 */
static u16 update_tick = 0;          /* 温度更新计数器 */
static bit flag_update = 1;          /* 温度更新标志 */

/*
 * 定时器0初始化
 * 用于数码管动态扫描，中断周期约 2ms
 * 11.0592MHz, 12T模式: 定时器计数 = 2ms * (11.0592MHz / 12) = 1843
 * 使用 2000 计数 ≈ 2.17ms，满足视觉暂留要求
 */
static void Timer0_Init(void)
{
    AUXR &= 0x7F;                    /* 定时器0 12T模式 */
    TMOD &= 0xF0;                    /* 清定时器0配置 */
    TMOD |= 0x01;                    /* 定时器0 方式1 (16位) */
    TH0 = (65536 - 2000) / 256;      /* 定时初值高字节 */
    TL0 = (65536 - 2000) % 256;      /* 定时初值低字节 */
    ET0 = 1;                         /* 允许定时器0中断 */
    TR0 = 1;                         /* 启动定时器0 */
}

/*
 * 定时器0中断服务函数
 * 功能:
 *   1. 数码管动态扫描 (每2ms扫描一位)
 *   2. 温度更新计数器 (每300ms触发一次温度更新)
 */
void Timer0_ISR(void) interrupt 1
{
    TH0 = (65536 - 2000) / 256;      /* 重装定时初值 */
    TL0 = (65536 - 2000) % 256;

    /* 数码管动态扫描 */
    display_scan_isr();

    /* 温度更新计数 (仅在步骤3/4时计数) */
    if (step >= STEP_S5_PCF8591) {
        update_tick++;
        if (update_tick >= 150) {    /* 150 * 2ms = 300ms */
            update_tick = 0;
            flag_update = 1;         /* 触发温度更新 */
        }
    }
}

/*
 * 系统初始化
 * 初始化所有外设模块
 */
static void System_Init(void)
{
    /* 关闭所有数码管 */
    P0 = 0xFF;                       /* 段选全灭 */
    P2 = (P2 & 0x1F) | HC573_DUANXUAN;
    P2 = (P2 & 0x1F);

    P0 = 0x00;                       /* 位选全关 */
    P2 = (P2 & 0x1F) | HC573_WEIXUAN;
    P2 = (P2 & 0x1F);

    /* 初始化各模块 */
    led_init();                      /* LED 初始化 */
    display_init();                  /* 数码管初始化 */
    uart_init();                     /* 串口初始化 */
    pcf8591_init();                  /* PCF8591 初始化 */
    ds18b20_init();                  /* DS18B20 初始化 */
    Timer0_Init();                   /* 定时器0初始化 */
}

/*
 * 按键扫描及处理函数
 * 包含 20ms 消抖，按步骤处理不同按键
 *
 * 按键逻辑:
 *   - 步骤2: 按 S4 → 8个LED全亮 → 进入步骤3
 *   - 步骤3/4: 按 S5 → 切换到 PCF8591 测温模式 (显示 "A  xx.x")
 *   - 步骤3/4: 按 S6 → 切换到 DS18B20 测温模式 (显示 "B  xx.x")
 */
static void Key_Scan(void)
{
    /* 步骤2: 检测 S4 按键 */
    if (step == STEP_S4) {
        if (S4 == 0) {               /* 检测按键按下 */
            delay_ms(20);            /* 消抖延时 */
            if (S4 == 0) {           /* 二次确认 */
                led_all_on();        /* 8个LED全亮 */
                step = STEP_S5_PCF8591;  /* 进入步骤3 */
                flag_update = 1;     /* 立即触发温度更新 */
                while (S4 == 0);     /* 等待按键释放 */
            }
        }
    }

    /* 步骤3/4: 检测 S5 和 S6 按键 */
    if (step >= STEP_S5_PCF8591) {
        /* S5: 切换到 PCF8591 模式 */
        if (S5 == 0) {
            delay_ms(20);            /* 消抖延时 */
            if (S5 == 0) {           /* 二次确认 */
                mode = 1;            /* PCF8591 模式 */
                step = STEP_S5_PCF8591;
                flag_update = 1;     /* 立即触发更新 */
                while (S5 == 0);     /* 等待按键释放 */
            }
        }

        /* S6: 切换到 DS18B20 模式 */
        if (S6 == 0) {
            delay_ms(20);            /* 消抖延时 */
            if (S6 == 0) {           /* 二次确认 */
                mode = 2;            /* DS18B20 模式 */
                step = STEP_S6_DS18B20;
                flag_update = 1;     /* 立即触发更新 */
                while (S6 == 0);     /* 等待按键释放 */
            }
        }
    }
}

/*
 * 串口数据处理函数
 * 处理步骤1的串口通信:
 *   - 接收任意数据 → LED显示
 *   - 回传数据到PC
 *   - 收到 SPECIAL_DATA (0xAA) 后解锁进入步骤2
 */
static void Proc_UART(void)
{
    if (Rx_flag == 0) return;        /* 无数据则返回 */

    Rx_flag = 0;

    /* 回传接收到的数据 */
    uart_send_byte(Rx_data);

    /* 步骤1: 数据显示在LED上 */
    if (step == STEP_UART) {
        /* led_write 内部取反后输出 (低电平点亮) */
        led_write(Rx_data);

        /* 检测特定解锁数据 */
        if (Rx_data == SPECIAL_DATA) {
            step = STEP_S4;          /* 解锁，进入步骤2 */
        }
    }
}

/*
 * 温度更新函数
 * 根据当前模式读取温度并更新数码管显示
 *
 * 模式1 (PCF8591):
 *   读取 ADC 通道3 (RB2) 电压值
 *   公式: temp = (adc * 8000) / 255
 *   0~255 -> 0~8000 (对应 0.00°C ~ 80.00°C)
 *
 * 模式2 (DS18B20):
 *   读取 DS18B20 真实温度
 *   原始值 * 6.25 -> 温度值 * 100
 *   例如: raw=401 (25.0625°C) -> 401*6.25≈2506 -> 25.06°C
 *   支持负数温度: 检测MSB bit7, 二补码转绝对值后计算
 */
static void Update_Display(void)
{
    u8 adc;
    u16 temp_val;
    u16 raw;
    bit is_negative;

    if (flag_update == 0) return;    /* 无需更新则返回 */
    flag_update = 0;

    if (mode == 1) {
        /* PCF8591 模式: 读取通道3，计算温度 */
        adc = pcf8591_read_adc(0x03);     /* 读取 RB2 通道 */
        temp_val = (u16)((u32)adc * 8000 / 255);  /* 0-255 -> 0-8000 */
        display_set_temp('A', temp_val, 0);  /* 显示 "A  xx.x" */
    }
    else if (mode == 2) {
        /* DS18B20 模式: 调用库函数读取真实温度 */
        raw = ds18b20_read_temp();    /* 读取16位原始温度 */

        /* 检测负数: MSB bit7=1 表示负温度 */
        is_negative = 0;
        if (raw & 0x8000) {
            is_negative = 1;
            raw = (~raw) + 1;         /* 二补码转绝对值 */
        }

        /*
         * 温度转换: raw * 0.0625°C
         * 转换为 0.01°C 单位: raw * 6.25
         * 整数运算: raw * 625 / 100
         */
        temp_val = (u16)((u32)raw * 625 / 100);
        display_set_temp('B', temp_val, is_negative);  /* 显示 "B  xx.x" */
    }
}

/*
 * 主函数
 * 4步状态机:
 *   第1步: 串口通信 → 收到0xAA解锁
 *   第2步: 按S4 → 8个LED全亮
 *   第3步: 按S5 → PCF8591读温度，显示 "A  xx.x"
 *   第4步: 按S6 → DS18B20读温度，显示 "B  xx.x"
 */
void main(void)
{
    System_Init();                   /* 系统初始化 */

    while (1) {
        /* 串口数据处理 */
        if (Rx_flag) {
            Proc_UART();
        }

        /* 按键扫描处理 */
        Key_Scan();

        /* 温度更新 (步骤3/4) */
        if (step >= STEP_S5_PCF8591) {
            Update_Display();
        }
    }
}

/*
 * 串口中断服务函数
 * 接收数据后存储到 Rx_data 并设置 Rx_flag
 */
void UART_ISR(void) interrupt 4
{
    if (RI) {
        RI = 0;                      /* 清除接收中断标志 */
        Rx_data = SBUF;              /* 保存接收数据 */
        Rx_flag = 1;                 /* 设置接收标志 */
    }
    if (TI) {
        TI = 0;                      /* 清除发送中断标志 */
    }
}