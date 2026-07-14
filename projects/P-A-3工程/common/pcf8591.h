#ifndef PCF8591_H
#define PCF8591_H

#include "board.h"

void pcf8591_init(void);
u8 pcf8591_read_adc(u8 channel);

#endif