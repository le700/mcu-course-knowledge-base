#include "display.h"

/*
 * 数码管显示缓存，8位
 * 对应8位数码管从左到右 (0~7)
 */
u8 disp_buf[DIGITS];
u8 scan_index = 0;

/*
 * 74HC573 通道选择函数
 * 通过 P2 口高3位 + SN74HC02 译码选择对应外设
 * channel: 4=LED(0x80), 6=位选(0xC0), 7=段选(0xE0)
 */
static void Select_HC573(u8 channel)
{
    u8 temp;
    P2 = (P2 & 0x1F) | 0x00;       /* 先清空P2高3位 */
    temp = channel << 5;             /* 通道号左移5位映射到高3位 */
    P2 = (P2 & 0x1F) | temp;        /* 设置对应通道 */
}

/*
 * 共阴数码管段码表
 * 段码位定义: bit7=dp, bit6=g, bit5=f, bit4=e, bit3=d, bit2=c, bit1=b, bit0=a
 * 低电平有效: 0=亮, 1=灭
 *
 * 索引说明:
 *   0~9: 数字 0~9
 *   10:  'A'
 *   11:  'b'
 *   12:  '-' (横杠)
 *   13:  空白 (全灭)
 */
static __code u8 seg_table[] = {
    0xC0,  /* 0 */
    0xF9,  /* 1 */
    0xA4,  /* 2 */
    0xB0,  /* 3 */
    0x99,  /* 4 */
    0x92,  /* 5 */
    0x82,  /* 6 */
    0xF8,  /* 7 */
    0x80,  /* 8 */
    0x90,  /* 9 */
    0x88,  /* A */
    0x83,  /* b */
    0xBF,  /* - */
    0xFF   /* 空白 */
};

/*
 * 数码管位选表
 * 8位数码管，从右到左依次对应 0x01~0x80
 * 低电平有效: 0=选中
 */
static __code u8 weixuan_table[DIGITS] = {
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
};

/*
 * 数码管初始化
 * 清空显示缓存，关闭所有数码管
 */
void display_init(void)
{
    u8 i;

    /* 清空显示缓存 */
    for (i = 0; i < DIGITS; i++) {
        disp_buf[i] = 0xFF;         /* 全部熄灭 */
    }

    /* 关闭所有数码管 */
    P0 = 0xFF;                       /* 段选全灭 */
    Select_HC573(7);                 /* 选中段选通道 */
    Select_HC573(0);                 /* 关闭通道 */

    P0 = 0x00;                       /* 位选全关 */
    Select_HC573(6);                 /* 选中位选通道 */
    Select_HC573(0);                 /* 关闭通道 */
}

/*
 * 数码管动态扫描函数 (在定时器中断中调用)
 * 每次扫描一位数码管，8次完成一轮扫描
 *
 * 消影处理流程:
 *   1. 先关闭段选 (P0=0xFF)，防止切换位选时出现重影
 *   2. 切换位选到下一位置
 *   3. 输出对应段码
 */
void display_scan_isr(void)
{
    /* 消影: 先关闭段选 */
    P0 = 0xFF;
    Select_HC573(7);                 /* 段选锁存 */
    Select_HC573(0);

    /* 切换位选 */
    P0 = ~weixuan_table[scan_index]; /* 位选取反 (低电平有效) */
    Select_HC573(6);                 /* 位选锁存 */
    Select_HC573(0);

    /* 输出段码 */
    P0 = disp_buf[scan_index];       /* 段码数据 */
    Select_HC573(7);                 /* 段选锁存 */
    Select_HC573(0);

    /* 移到下一位 */
    scan_index++;
    if (scan_index >= DIGITS) {
        scan_index = 0;
    }
}

/*
 * 设置温度显示
 * label: 标签字符 'A' 或 'B'
 * temp_x100: 温度绝对值乘以100 (如 25.06°C = 2506)
 * is_negative: 1=负温度, 0=正温度
 *
 * 显示格式 (8位数码管从左到右):
 *   位置0: 标签 'A' 或 'B'
 *   位置1: 负号 '-' (仅负温度时) 或空白
 *   位置2: 空白
 *   位置3: 空白
 *   位置4: 温度十位
 *   位置5: 温度个位 (带小数点)
 *   位置6: 小数第一位
 *   位置7: 小数第二位
 */
void display_set_temp(char label, u16 temp_x100, __bit is_negative)
{
    u8 seg_idx;

    /* 标签字符 */
    if (label == 'A') {
        seg_idx = 10;                /* seg_table[10] = 'A' */
    } else {
        seg_idx = 11;                /* seg_table[11] = 'b' */
    }

    /* 温度值限幅 (0~9999 对应 0.00~99.99) */
    if (temp_x100 > 9999) {
        temp_x100 = 9999;
    }

    disp_buf[0] = seg_table[seg_idx];              /* 标签 A/B */
    disp_buf[1] = is_negative ? seg_table[12] : 0xFF; /* 负号或空白 */
    disp_buf[2] = 0xFF;                            /* 空白 */
    disp_buf[3] = 0xFF;                            /* 空白 */
    disp_buf[4] = seg_table[temp_x100 / 1000];     /* 十位 */
    disp_buf[5] = seg_table[temp_x100 / 100 % 10] & 0x7F;  /* 个位+小数点 */
    disp_buf[6] = seg_table[temp_x100 / 10 % 10];  /* 小数第一位 */
    disp_buf[7] = seg_table[temp_x100 % 10];       /* 小数第二位 */
}