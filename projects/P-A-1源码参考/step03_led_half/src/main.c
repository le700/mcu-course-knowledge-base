#include "i8255.h"
#include "led.h"

void main(void)
{
    i8255_init();
    led_init();
    led_write(0x0F);

    while (1) {
        ;
    }
}
