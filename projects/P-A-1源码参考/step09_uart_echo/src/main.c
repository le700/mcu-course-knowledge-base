#include "i8255.h"
#include "led.h"
#include "uart.h"

void main(void)
{
    u8 ch;

    i8255_init();
    led_init();
    uart_init_1200();
    uart_puts("P-A-1 UART ready, send A to unlock.\r\n");

    while (1) {
        ch = uart_getchar();
        led_write(ch);
        uart_putchar(ch);
    }
}
