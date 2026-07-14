#include "adc0809.h"
#include "delay.h"

#define ADC_ZUIDA_SHUZI     255UL
#define ADC_ZUIDA_WENDU     8000UL

u8 adc0809_read(u8 channel)
{
    u16 timeout;
    u8 value;

    channel &= 0x07;

    /*
     * A MOVX write selects channel A0..A2 and pulses START/ALE through the
     * board's 74HC02 logic. A later MOVX read enables ADC data onto P0.
     */
    ADC0809_REG(channel) = 0x00;

    timeout = 60000;
    while ((ADC0809_EOC != 0) && (timeout != 0)) {
        timeout--;
    }

    timeout = 60000;
    while ((ADC0809_EOC == 0) && (timeout != 0)) {
        timeout--;
    }

    delay_us(5);
    value = ADC0809_REG(channel);
    return value;
}

u16 adc_zhuan_wendu_x100(u8 adc_zhi)
{
    /*
     * adc_zhi 是 ADC0809 读到的原始数字量，范围 0~255。
     * 0   -> 0.00 C
     * 255 -> 80.00 C
     */
    return (u16)((u32)adc_zhi * ADC_ZUIDA_WENDU / ADC_ZUIDA_SHUZI);
}

u16 adc0809_to_temp_x100(u8 adc_zhi)
{
    return adc_zhuan_wendu_x100(adc_zhi);
}
