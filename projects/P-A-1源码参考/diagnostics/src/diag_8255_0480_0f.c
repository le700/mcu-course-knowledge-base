#include <REG52.H>
#include <ABSACC.H>

#define PPI_PA   XBYTE[0x0480]
#define PPI_CTRL XBYTE[0x0483]

void main(void)
{
    PPI_CTRL = 0x89;
    while (1) {
        PPI_PA = 0x0F;
    }
}
