#include "i8255.h"
#include "display.h"

void main(void)
{
    i8255_init();
    display_init();

    while (1) {
        display_show_temp('A', 2345);
        display_scan_times(200);

        display_show_temp('C', 2600);
        display_scan_times(200);

        display_show_error('C');
        display_scan_times(200);
    }
}
