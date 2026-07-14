#include "display.h"
#include "delay.h"

/*
 * 8255 PB 口段码位：
 * bit0=dp, bit1=g, bit2=f, bit3=e, bit4=d, bit5=c, bit6=b, bit7=a
 */
#define SEG_DP 0x01
#define SEG_G  0x02
#define SEG_F  0x04
#define SEG_E  0x08
#define SEG_D  0x10
#define SEG_C  0x20
#define SEG_B  0x40
#define SEG_A  0x80

static u8 shumaguan_neirong[DISPLAY_DIGITS];  /* 6 位数码管显示缓存 */

static u8 code shumaguan_weixuan[DISPLAY_DIGITS] = {
    0x20, 0x10, 0x08, 0x04, 0x02, 0x01
};

static u8 code shuzi_duanma[10] = {
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F,
    SEG_B | SEG_C,
    SEG_A | SEG_B | SEG_D | SEG_E | SEG_G,
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_G,
    SEG_B | SEG_C | SEG_F | SEG_G,
    SEG_A | SEG_C | SEG_D | SEG_F | SEG_G,
    SEG_A | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G,
    SEG_A | SEG_B | SEG_C,
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F | SEG_G,
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_F | SEG_G
};

static u8 zifu_zhuan_duanma(char zifu)
{
    if ((zifu >= '0') && (zifu <= '9')) {
        return shuzi_duanma[zifu - '0'];
    }

    switch (zifu) {
    case 'A':
    case 'a':
        return SEG_A | SEG_B | SEG_C | SEG_E | SEG_F | SEG_G;
    case 'C':
    case 'c':
        return SEG_A | SEG_D | SEG_E | SEG_F;
    case 'F':
    case 'f':
        return SEG_A | SEG_E | SEG_F | SEG_G;
    case '-':
        return SEG_G;
    default:
        return 0x00;
    }
}

static void shumaguan_quanbu_guanbi(void)
{
    DIGIT_PORT = (DIGIT_PORT & DIGIT_KEEP_MASK);
    PPI_PORT_B = 0x00;
}

void display_init(void)
{
    shumaguan_qingkong();
    shumaguan_quanbu_guanbi();
}

void shumaguan_qingkong(void)
{
    u8 weizhi;  /* 当前清空到第几位 */

    for (weizhi = 0; weizhi < DISPLAY_DIGITS; weizhi++) {
        shumaguan_neirong[weizhi] = 0x00;
    }
}

void shumaguan_shezhi_duanma(u8 weizhi, u8 duanma)
{
    if (weizhi < DISPLAY_DIGITS) {
        shumaguan_neirong[weizhi] = duanma;
    }
}

void shumaguan_shezhi_zifu(u8 weizhi, char zifu, u8 dian)
{
    u8 duanma;  /* 一个字符转换成的段码 */

    duanma = zifu_zhuan_duanma(zifu);
    if (dian != 0) {
        duanma |= SEG_DP;
    }

    shumaguan_shezhi_duanma(weizhi, duanma);
}

void shumaguan_saomiao_yici(void)
{
    u8 weizhi;  /* 当前扫描的数码管位置 */

    for (weizhi = 0; weizhi < DISPLAY_DIGITS; weizhi++) {
        shumaguan_quanbu_guanbi();
        PPI_PORT_B = shumaguan_neirong[weizhi];
        DIGIT_PORT = (DIGIT_PORT & DIGIT_KEEP_MASK) | shumaguan_weixuan[weizhi];
        delay_ms(2);
    }

    shumaguan_quanbu_guanbi();
}

void shumaguan_saomiao_duoci(u16 cishu)
{
    while (cishu != 0) {
        shumaguan_saomiao_yici();
        cishu--;
    }
}

void shumaguan_xianshi_wendu(char biaoqian, u16 wendu_x100)
{
    u16 zhengshu;       /* 温度整数部分 */
    u16 xiaoshu;        /* 温度小数部分 */
    u8 shiwei;          /* 十位 */
    u8 gewei;           /* 个位 */
    u8 xiaoshu_shiwei;  /* 小数第一位 */
    u8 xiaoshu_gewei;   /* 小数第二位 */

    if (wendu_x100 > 9999) {
        wendu_x100 = 9999;
    }

    zhengshu = wendu_x100 / 100;
    xiaoshu = wendu_x100 % 100;

    if (zhengshu > 99) {
        zhengshu = 99;
    }

    shiwei = (u8)(zhengshu / 10);
    gewei = (u8)(zhengshu % 10);
    xiaoshu_shiwei = (u8)(xiaoshu / 10);
    xiaoshu_gewei = (u8)(xiaoshu % 10);

    /*
     * 六位数码管从左到右：
     * 第 1 位：A 或 C
     * 第 2 位：空白
     * 第 3 位：温度十位
     * 第 4 位：温度个位，并带小数点
     * 第 5 位：小数第一位
     * 第 6 位：小数第二位
     */
    shumaguan_qingkong();
    shumaguan_shezhi_zifu(0, biaoqian, 0);
    shumaguan_shezhi_duanma(1, 0x00);
    shumaguan_shezhi_zifu(2, (char)('0' + shiwei), 0);
    shumaguan_shezhi_zifu(3, (char)('0' + gewei), 1);
    shumaguan_shezhi_zifu(4, (char)('0' + xiaoshu_shiwei), 0);
    shumaguan_shezhi_zifu(5, (char)('0' + xiaoshu_gewei), 0);
}

void shumaguan_xianshi_cuowu(char biaoqian)
{
    /*
     * DHT11 失败时显示 C 88.88。
     */
    shumaguan_qingkong();
    shumaguan_shezhi_zifu(0, biaoqian, 0);
    shumaguan_shezhi_duanma(1, 0x00);
    shumaguan_shezhi_zifu(2, '8', 0);
    shumaguan_shezhi_zifu(3, '8', 1);
    shumaguan_shezhi_zifu(4, '8', 0);
    shumaguan_shezhi_zifu(5, '8', 0);
}

void display_blank(void)
{
    shumaguan_qingkong();
}

void display_set_raw(u8 pos, u8 seg)
{
    shumaguan_shezhi_duanma(pos, seg);
}

void display_set_char(u8 pos, char ch, u8 dot)
{
    shumaguan_shezhi_zifu(pos, ch, dot);
}

void display_scan_once(void)
{
    shumaguan_saomiao_yici();
}

void display_scan_times(u16 times)
{
    shumaguan_saomiao_duoci(times);
}

void display_show_4523(void)
{
    shumaguan_qingkong();
    shumaguan_shezhi_zifu(1, '4', 0);
    shumaguan_shezhi_zifu(2, '5', 1);
    shumaguan_shezhi_zifu(3, '2', 0);
    shumaguan_shezhi_zifu(4, '3', 0);
}

void display_show_temp(char label, u16 temp_x100)
{
    shumaguan_xianshi_wendu(label, temp_x100);
}

void display_show_error(char label)
{
    shumaguan_xianshi_cuowu(label);
}
