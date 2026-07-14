#include "i8255.h"
#include "display.h"
#include "dht11.h"

void main(void)
{
    u16 temp_x100;
    u8 err;
    u8 bit_index;

    i8255_init();
    display_init();

    while (1) {
        if (dht11_read_temp(&temp_x100) != 0) {
            display_show_temp('C', temp_x100);
            display_scan_times(160);
        } else {
            err = dht11_get_last_error();
            bit_index = dht11_get_last_bit_index();

            if (err == 0) {
                err = 9;
            }

            if (bit_index == 0) {
                bit_index = 99;
            }

            display_show_temp('C', (u16)err * 100U);
            display_scan_times(120);

            display_show_temp('A', (u16)bit_index * 100U);
            display_scan_times(120);
        }
    }
}
