#include "i8255.h"

void i8255_init(void)
{
    /*
     * 8255 方式 0：
     * PA 口输出给 LED；
     * PB 口输出给数码管段码；
     * PC 口输入读取 8 个开关。
     */
    PPI_CTRL = 0x89;
    PPI_PORT_A = 0x00;
    PPI_PORT_B = 0x00;
}

u8 du_kaiguan(void)
{
    /*
     * 只做一件事：读取 8255 PC 口的 8 个开关。
     * 如果板子开关是低电平有效，就取反后再返回。
     */
#if SWITCH_ACTIVE_LOW
    return (u8)(~PPI_PORT_C);
#else
    return PPI_PORT_C;
#endif
}

u8 switch_read_raw(void)
{
    return PPI_PORT_C;
}

u8 switch_read_logic(void)
{
    return du_kaiguan();
}
