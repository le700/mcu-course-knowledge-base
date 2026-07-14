#include <REG52.H>
#include <ABSACC.H>

#define PPI_PA   XBYTE[0x0080]
#define PPI_CTRL XBYTE[0x0083]

void main(void)
{
    PPI_CTRL = 0x89;
    while (1) {
        PPI_PA = 0xF0;
    }
}
