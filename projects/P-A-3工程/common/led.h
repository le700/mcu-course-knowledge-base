#ifndef LED_H
#define LED_H

#include "board.h"

void led_init(void);
void led_write(u8 value);
void led_all_off(void);
void led_all_on(void);

#endif