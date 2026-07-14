#ifndef DS18B20_H
#define DS18B20_H

#include "board.h"

u8 ds18b20_init(void);
void ds18b20_write_byte(u8 dat);
u8 ds18b20_read_byte(void);
u16 ds18b20_read_temp(void);

#endif