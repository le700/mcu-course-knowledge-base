#include "i8255.h"
#include "display.h"
#include "dht11.h"

void main(void)
{
    u16 temp_x100;
    u8 err;

    i8255_init();
    display_init();

    while (1) {
        if (dht11_read_temp(&temp_x100) != 0) {
            display_show_temp('C', temp_x100);
        } else {
            err = dht11_get_error();

            if (err == 0) {
                err = DHT11_ERR_UNKNOWN;
            }

            display_show_temp('C', (u16)err * 100U);
        }

        display_scan_times(160);
    }
}
