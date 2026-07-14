#include "i8255.h"
#include "led.h"
#include "display.h"
#include "adc0809.h"

void main(void)
{
    u8 adc_value;
    u16 temp_x100;

    i8255_init();
    display_init();

    while (1) {
        adc_value = adc0809_read(0);
        temp_x100 = adc0809_to_temp_x100(adc_value);
        led_write(adc_value);
        display_show_temp('A', temp_x100);
        display_scan_times(20);
    }
}
