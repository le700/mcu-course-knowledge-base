#include <INTRINS.H>
#include "delay.h"

void delay_us(u16 us)
{
    while (us != 0) {
        _nop_();
        _nop_();
        us--;
    }
}

void delay_ms(u16 ms)
{
    u16 i;

    while (ms != 0) {
        for (i = 0; i < 115; i++) {
            _nop_();
        }
        ms--;
    }
}
