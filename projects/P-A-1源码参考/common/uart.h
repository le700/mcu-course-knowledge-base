#ifndef UART_H
#define UART_H

#include "board.h"

void uart_init_1200(void);
u8 uart_received(void);
u8 uart_getchar(void);
void uart_putchar(u8 ch);
void uart_puts(char *s);

#endif
