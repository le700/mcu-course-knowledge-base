#include "i8255.h"
#include "led.h"
#include "adc0809.h"
#include "delay.h"

void main(void)
{
    u8 adc_value;

    i8255_init();
    led_init();
    led_all_off();

    while (1) {
        adc_value = adc0809_read(0);
        led_write(adc_value);
        delay_ms(80);
    }
}
