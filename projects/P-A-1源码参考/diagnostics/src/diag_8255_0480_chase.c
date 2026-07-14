#include <REG52.H>
#include <ABSACC.H>

#define PPI_PA   XBYTE[0x0480]
#define PPI_CTRL XBYTE[0x0483]

typedef unsigned char u8;
typedef unsigned int u16;

static void delay_ms(u16 ms)
{
    u16 i;
    while (ms--) {
        for (i = 0; i < 120; i++) {
            ;
        }
    }
}

void main(void)
{
    u8 value = 0x01;
    PPI_CTRL = 0x89;
    while (1) {
        PPI_PA = value;
        delay_ms(250);
        value <<= 1;
        if (value == 0) {
            value = 0x01;
        }
    }
}
