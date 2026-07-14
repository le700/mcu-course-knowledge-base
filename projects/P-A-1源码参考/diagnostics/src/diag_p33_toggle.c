#include <REG52.H>

sbit DHT11_DQ_TEST = P3^3;

typedef unsigned int u16;

static void delay_ms(u16 ms)
{
    u16 i;
    u16 j;

    for (i = 0; i < ms; i++) {
        for (j = 0; j < 120; j++) {
            ;
        }
    }
}

void main(void)
{
    while (1) {
        DHT11_DQ_TEST = 0;
        delay_ms(1000);

        DHT11_DQ_TEST = 1;
        delay_ms(1000);
    }
}
