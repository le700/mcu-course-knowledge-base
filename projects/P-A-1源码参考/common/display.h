#ifndef DISPLAY_H
#define DISPLAY_H

#include "board.h"

#define DISPLAY_DIGITS 6

void display_init(void);

void shumaguan_qingkong(void);
void shumaguan_shezhi_duanma(u8 weizhi, u8 duanma);
void shumaguan_shezhi_zifu(u8 weizhi, char zifu, u8 dian);
void shumaguan_saomiao_yici(void);
void shumaguan_saomiao_duoci(u16 cishu);
void shumaguan_xianshi_wendu(char biaoqian, u16 wendu_x100);
void shumaguan_xianshi_cuowu(char biaoqian);

void display_blank(void);
void display_set_raw(u8 pos, u8 seg);
void display_set_char(u8 pos, char ch, u8 dot);
void display_scan_once(void);
void display_scan_times(u16 times);
void display_show_4523(void);
void display_show_temp(char label, u16 temp_x100);
void display_show_error(char label);

#endif
