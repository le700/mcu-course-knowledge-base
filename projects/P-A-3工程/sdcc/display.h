#ifndef DISPLAY_H
#define DISPLAY_H

#include "board.h"

void display_init(void);
void display_scan_isr(void);
void display_set_temp(char label, u16 temp_x100, __bit is_negative);

/* 数码管显示缓存 (8位) */
extern u8 disp_buf[DIGITS];
/* 扫描索引 */
extern u8 scan_index;

#endif