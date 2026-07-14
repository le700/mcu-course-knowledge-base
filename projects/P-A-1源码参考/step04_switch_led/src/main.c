#include "i8255.h"
#include "led.h"

void main(void)
{
    u8 sw;

    i8255_init();
    led_init();

    while (1) {
        sw = switch_read_raw();
        led_write(sw);
    }
}
