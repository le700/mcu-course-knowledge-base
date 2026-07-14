#include "i8255.h"
#include "display.h"
#include "dht11.h"

static u8 read_dht11_retry(u16 *dht11_temp_x100)
{
    u8 i;

    display_scan_times(40);

    for (i = 0; i < 3; i++) {
        if (dht11_read_temp(dht11_temp_x100) != 0) {
            return 1;
        }

        display_scan_times(80);
    }

    return 0;
}

void main(void)
{
    u16 temp_x100;

    i8255_init();
    display_init();

    while (1) {
        if (read_dht11_retry(&temp_x100) != 0) {
            display_show_temp('C', temp_x100);
        } else {
            display_show_error('C');
        }

        display_scan_times(100);
    }
}
