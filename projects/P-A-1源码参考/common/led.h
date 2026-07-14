#ifndef LED_H
#define LED_H

#include "board.h"

void led_init(void);
void led_xianshi(u8 zhi);
void led_guanbi(void);
void led_write(u8 value);
void led_all_off(void);

#endif
