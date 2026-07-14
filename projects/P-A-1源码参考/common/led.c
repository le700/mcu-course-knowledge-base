#include "led.h"

void led_init(void)
{
    led_guanbi();
}

void led_xianshi(u8 zhi)
{
    /*
     * 只做一件事：把 8 位数据送到 8255 PA 口显示。
     */
#if LED_ACTIVE_HIGH
    PPI_PORT_A = zhi;
#else
    PPI_PORT_A = (u8)(~zhi);
#endif
}

void led_guanbi(void)
{
    /*
     * 关闭全部 LED。
     */
#if LED_ACTIVE_HIGH
    PPI_PORT_A = 0x00;
#else
    PPI_PORT_A = 0xFF;
#endif
}

void led_write(u8 value)
{
    led_xianshi(value);
}

void led_all_off(void)
{
    led_guanbi();
}
