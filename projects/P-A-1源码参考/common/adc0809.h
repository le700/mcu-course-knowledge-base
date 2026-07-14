#ifndef ADC0809_H
#define ADC0809_H

#include "board.h"

u8 adc0809_read(u8 channel);
u16 adc_zhuan_wendu_x100(u8 adc_zhi);
u16 adc0809_to_temp_x100(u8 adc_zhi);

#endif
