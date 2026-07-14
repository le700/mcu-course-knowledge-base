#include "i8255.h"
#include "display.h"
#include "dht11.h"

/*
 * This diagnostic displays DHT11 raw protocol bytes only.
 * A1/A2 are raw humidity bytes used by the DHT11 checksum;
 * PA1's formal function does not display humidity.
 */
static void show_byte(char label, u8 index, u8 value)
{
    u8 hundreds;
    u8 tens;
    u8 ones;

    hundreds = value / 100;
    tens = (value / 10) % 10;
    ones = value % 10;

    display_blank();
    display_set_char(0, label, 0);
    display_set_char(1, (char)('0' + index), 0);
    display_set_raw(2, 0x00);
    display_set_char(3, (char)('0' + hundreds), 0);
    display_set_char(4, (char)('0' + tens), 0);
    display_set_char(5, (char)('0' + ones), 0);
}

static void show_error_and_bit(void)
{
    u8 err;
    u8 bit_index;

    err = dht11_get_last_error();
    bit_index = dht11_get_last_bit_index();

    if (err == 0) {
        err = 9;
    }

    if (bit_index == 0) {
        bit_index = 99;
    }

    display_show_temp('F', (u16)err * 100U);
    display_scan_times(100);

    display_show_temp('A', (u16)bit_index * 100U);
    display_scan_times(100);
}

void main(void)
{
    u16 temp_x100;

    i8255_init();
    display_init();

    while (1) {
        (void)dht11_read_temp(&temp_x100);

        show_byte('A', 1, dht11_get_last_raw(0));
        display_scan_times(120);

        show_byte('A', 2, dht11_get_last_raw(1));
        display_scan_times(120);

        show_byte('C', 1, dht11_get_last_raw(2));
        display_scan_times(120);

        show_byte('C', 2, dht11_get_last_raw(3));
        display_scan_times(120);

        show_error_and_bit();
    }
}
