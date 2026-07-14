#ifndef UART_H
#define UART_H

#include "board.h"

void uart_init(void);
void uart_send_byte(u8 dat);
u8 uart_received(void);
u8 uart_get_char(void);

#endif