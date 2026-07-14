#include "delay.h"

/*
 * 微秒级延时函数
 * 11.0592MHz 晶振，约 3~4us 延时 (含函数调用开销)
 */
void delay_us(u16 us)
{
    while (us != 0) {
        __asm__("nop");
        __asm__("nop");
        us--;
    }
}

/*
 * 毫秒级延时函数
 * 11.0592MHz 晶振，约 1ms 延时
 */
void delay_ms(u16 ms)
{
    u16 i;

    while (ms != 0) {
        for (i = 0; i < 115; i++) {
            __asm__("nop");
        }
        ms--;
    }
}