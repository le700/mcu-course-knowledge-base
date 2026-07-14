#include "i8255.h"
#include "led.h"
#include "display.h"
#include "adc0809.h"
#include "uart.h"
#include "dht11.h"

#define DENG_CHUANKOU   0
#define DENG_QIAN_SIGE  1
#define XIANSHI_ADC     2
#define XIANSHI_DHT11   3

static void xianshi_kaishi_tishi(void)
{
    shumaguan_qingkong();
    shumaguan_shezhi_zifu(0, 'A', 0);
}

static u8 dht11_chongshi_du_wendu(u16 *huanjing_wendu_x100)
{
    u8 cishu;

    for (cishu = 0; cishu < 3; cishu++) {
        if (dht11_du_wendu(huanjing_wendu_x100) != 0) {
            return 1;
        }

        shumaguan_saomiao_duoci(80);
    }

    return 0;
}

void main(void)
{
    u8 zhuangtai;
    u8 chuankou_zifu;
    u8 kaiguan_zhi;
    u8 adc_zhi;
    u16 adc_wendu_x100;
    u16 huanjing_wendu_x100;

    zhuangtai = DENG_CHUANKOU;

    i8255_init();
    led_init();
    display_init();
    uart_init_1200();
    led_guanbi();
    xianshi_kaishi_tishi();
    uart_puts("P-A-1 ready. Send ASCII A, then set switches.\r\n");

    while (1) {
        if (zhuangtai == DENG_CHUANKOU) {
            if (uart_received() != 0) {
                chuankou_zifu = uart_getchar();
                led_xianshi(chuankou_zifu);
                uart_putchar(chuankou_zifu);

                if (chuankou_zifu == PA1_UNLOCK_BYTE) {
                    zhuangtai = DENG_QIAN_SIGE;
                    uart_puts("\r\nUART unlocked. Set SK0-SK3 to logic 1.\r\n");
                    shumaguan_qingkong();
                }
            }

            shumaguan_saomiao_yici();
        } else if (zhuangtai == DENG_QIAN_SIGE) {
            kaiguan_zhi = du_kaiguan();
            led_xianshi(kaiguan_zhi);

            if ((kaiguan_zhi & 0x0F) == 0x0F) {
                zhuangtai = XIANSHI_ADC;
                uart_puts("Front four switches are 1. ADC display enabled.\r\n");
            }

            shumaguan_saomiao_yici();
        } else if (zhuangtai == XIANSHI_ADC) {
            kaiguan_zhi = du_kaiguan();

            if ((kaiguan_zhi & 0x0F) != 0x0F) {
                shumaguan_qingkong();
                led_guanbi();
                zhuangtai = DENG_QIAN_SIGE;
                uart_puts("Front switch dropped to 0. ADC display disabled.\r\n");
            } else if ((kaiguan_zhi & 0xF0) == 0xF0) {
                zhuangtai = XIANSHI_DHT11;
                uart_puts("Back four switches are 1. Reading DHT11.\r\n");
            } else {
                adc_zhi = adc0809_read(0);
                adc_wendu_x100 = adc_zhuan_wendu_x100(adc_zhi);
                led_xianshi(adc_zhi);
                shumaguan_xianshi_wendu('A', adc_wendu_x100);
                shumaguan_saomiao_duoci(20);
            }
        } else if (zhuangtai == XIANSHI_DHT11) {
            if (dht11_chongshi_du_wendu(&huanjing_wendu_x100) != 0) {
                shumaguan_xianshi_wendu('C', huanjing_wendu_x100);
            } else {
                shumaguan_xianshi_cuowu('C');
            }

            shumaguan_saomiao_duoci(100);
        }
    }
}
