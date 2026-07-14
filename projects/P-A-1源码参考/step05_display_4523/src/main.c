#include "i8255.h"
#include "display.h"

void main(void)
{
    i8255_init();
    display_init();
    display_show_4523();

    while (1) {
        display_scan_once();
    }
}
