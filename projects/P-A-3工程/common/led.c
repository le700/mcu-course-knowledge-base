#include "led.h"

/*
 * 74HC573 通道选择函数
 * 通过 P2 口高3位 + SN74HC02 译码选择对应外设
 * channel: 4=LED(0x80), 6=位选(0xC0), 7=段选(0xE0)
 */
static void Select_HC573(u8 channel)
{
    u8 temp;
    P2 = (P2 & 0x1F) | 0x00;       /* 先清空P2高3位 */
    temp = channel << 5;             /* 通道号左移5位映射到高3位 */
    P2 = (P2 & 0x1F) | temp;        /* 设置对应通道 */
}

/*
 * LED 初始化，关闭所有LED
 */
void led_init(void)
{
    led_all_off();
}

/*
 * 向LED写入8位数据
 * value: 8位LED数据，1=亮，0=灭 (低电平有效)
 */
void led_write(u8 value)
{
    P0 = ~value;                     /* 取反后输出 (低电平点亮) */
    Select_HC573(4);                 /* 选中LED锁存器通道 */
    Select_HC573(0);                 /* 关闭通道选择，锁存数据 */
}

/*
 * 关闭所有LED
 */
void led_all_off(void)
{
    P0 = 0xFF;                       /* 全部输出高电平 (LED灭) */
    Select_HC573(4);
    Select_HC573(0);
}

/*
 * 点亮所有LED
 */
void led_all_on(void)
{
    P0 = 0x00;                       /* 全部输出低电平 (LED亮) */
    Select_HC573(4);
    Select_HC573(0);
}