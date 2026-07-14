#include "uart.h"

void uart_init_1200(void)
{
    SCON = 0x50;
    TMOD = (TMOD & 0x0F) | 0x20;
    PCON &= 0x7F;
    TH1 = 0xE6;
    TL1 = 0xE6;
    TR1 = 1;
    TI = 0;
    RI = 0;
}

u8 uart_received(void)
{
    return RI ? 1 : 0;
}

u8 uart_getchar(void)
{
    u8 ch;

    while (RI == 0) {
        ;
    }
    RI = 0;
    ch = SBUF;
    return ch;
}

void uart_putchar(u8 ch)
{
    SBUF = ch;
    while (TI == 0) {
        ;
    }
    TI = 0;
}

void uart_puts(char *s)
{
    while (*s != '\0') {
        uart_putchar((u8)*s);
        s++;
    }
}
