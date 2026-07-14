#include <INTRINS.H>
#include "dht11.h"
#include "delay.h"

#define DHT11_CHAOSHI 60000U

static u8 dht11_cuowu = DHT11_ERR_NONE;
static u8 dht11_dangqian_wei = 0;
static u8 dht11_zuijin_chucuo_wei = 0;
static u8 dht11_zuijin_zijie[5] = {0, 0, 0, 0, 0};

u8 dht11_get_last_error(void)
{
    return dht11_cuowu;
}

u8 dht11_get_error(void)
{
    return dht11_cuowu;
}

u8 dht11_get_last_bit_index(void)
{
    return dht11_zuijin_chucuo_wei;
}

u8 dht11_get_last_raw(u8 index)
{
    if (index < 5) {
        return dht11_zuijin_zijie[index];
    }

    return 0;
}

static void dht11_yanshi_30us(void)
{
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
    _nop_(); _nop_(); _nop_(); _nop_(); _nop_();
}

static void dht11_jilu_shibai(u8 cuowu)
{
    dht11_cuowu = cuowu;
    dht11_zuijin_chucuo_wei = dht11_dangqian_wei;
}

static u8 dht11_deng_dianping(u8 dianping)
{
    u16 chaoshi;

    chaoshi = DHT11_CHAOSHI;

    while ((DHT11_IO ? 1 : 0) != dianping) {
        chaoshi--;
        if (chaoshi == 0) {
            return 0;
        }
    }

    return 1;
}

static u8 dht11_du_yige_zijie(u8 *zijie)
{
    u8 i;
    u8 dat;
    u16 chaoshi;

    dat = 0;

    for (i = 0; i < 8; i++) {
        dht11_dangqian_wei++;
        chaoshi = DHT11_CHAOSHI;

        while (DHT11_IO == 0) {
            chaoshi--;
            if (chaoshi == 0) {
                dht11_jilu_shibai(DHT11_ERR_BIT_READ);
                return 0;
            }
        }

        dht11_yanshi_30us();

        if (DHT11_IO != 0) {
            dat |= (u8)(1 << (7 - i));

            chaoshi = DHT11_CHAOSHI;
            while (DHT11_IO != 0) {
                chaoshi--;
                if (chaoshi == 0) {
                    break;
                }
            }
        }
    }

    *zijie = dat;
    return 1;
}

u8 dht11_du_wendu(u16 *huanjing_wendu_x100)
{
    bit ea_save;
    u8 shidu_zhengshu;
    u8 shidu_xiaoshu;
    u8 wendu_zhengshu;
    u8 wendu_xiaoshu;
    u8 jiaoyanhe;
    u8 jiaoyan_jisuan;

    dht11_cuowu = DHT11_ERR_NONE;
    dht11_dangqian_wei = 0;
    dht11_zuijin_chucuo_wei = 0;
    dht11_zuijin_zijie[0] = 0;
    dht11_zuijin_zijie[1] = 0;
    dht11_zuijin_zijie[2] = 0;
    dht11_zuijin_zijie[3] = 0;
    dht11_zuijin_zijie[4] = 0;

    ea_save = EA;
    EA = 0;

    DHT11_IO = 1;
    delay_ms(2);

    DHT11_IO = 0;
    delay_ms(20);

    DHT11_IO = 1;
    dht11_yanshi_30us();

    if (dht11_deng_dianping(0) == 0) {
        dht11_cuowu = DHT11_ERR_RESP_LOW;
        EA = ea_save;
        return 0;
    }

    if (dht11_deng_dianping(1) == 0) {
        dht11_cuowu = DHT11_ERR_RESP_HIGH;
        EA = ea_save;
        return 0;
    }

    if (dht11_deng_dianping(0) == 0) {
        dht11_cuowu = DHT11_ERR_RESP_END;
        EA = ea_save;
        return 0;
    }

    if (dht11_du_yige_zijie(&shidu_zhengshu) == 0) {
        if (dht11_cuowu == DHT11_ERR_NONE) {
            dht11_cuowu = DHT11_ERR_BIT_READ;
        }
        EA = ea_save;
        return 0;
    }
    dht11_zuijin_zijie[0] = shidu_zhengshu;

    if (dht11_du_yige_zijie(&shidu_xiaoshu) == 0) {
        if (dht11_cuowu == DHT11_ERR_NONE) {
            dht11_cuowu = DHT11_ERR_BIT_READ;
        }
        EA = ea_save;
        return 0;
    }
    dht11_zuijin_zijie[1] = shidu_xiaoshu;

    if (dht11_du_yige_zijie(&wendu_zhengshu) == 0) {
        if (dht11_cuowu == DHT11_ERR_NONE) {
            dht11_cuowu = DHT11_ERR_BIT_READ;
        }
        EA = ea_save;
        return 0;
    }
    dht11_zuijin_zijie[2] = wendu_zhengshu;

    if (dht11_du_yige_zijie(&wendu_xiaoshu) == 0) {
        if (dht11_cuowu == DHT11_ERR_NONE) {
            dht11_cuowu = DHT11_ERR_BIT_READ;
        }
        EA = ea_save;
        return 0;
    }
    dht11_zuijin_zijie[3] = wendu_xiaoshu;

    if (dht11_du_yige_zijie(&jiaoyanhe) == 0) {
        if (dht11_cuowu == DHT11_ERR_NONE) {
            dht11_cuowu = DHT11_ERR_BIT_READ;
        }
        EA = ea_save;
        return 0;
    }
    dht11_zuijin_zijie[4] = jiaoyanhe;

    EA = ea_save;

    if (shidu_zhengshu > 100) {
        dht11_cuowu = DHT11_ERR_RANGE;
        return 0;
    }

    if (wendu_zhengshu > 50) {
        dht11_cuowu = DHT11_ERR_RANGE;
        return 0;
    }

    if ((shidu_zhengshu == 0) &&
        (shidu_xiaoshu == 0) &&
        (wendu_zhengshu == 0) &&
        (wendu_xiaoshu == 0)) {
        dht11_cuowu = DHT11_ERR_ALL_ZERO;
        return 0;
    }

    jiaoyan_jisuan = (u8)(shidu_zhengshu + shidu_xiaoshu +
                          wendu_zhengshu + wendu_xiaoshu);

    if (jiaoyan_jisuan != jiaoyanhe) {
        dht11_cuowu = DHT11_ERR_CHECKSUM;
        return 0;
    }

    if (wendu_xiaoshu <= 9) {
        *huanjing_wendu_x100 = (u16)wendu_zhengshu * 100U +
                               (u16)wendu_xiaoshu * 10U;
    } else {
        *huanjing_wendu_x100 = (u16)wendu_zhengshu * 100U;
    }

    dht11_cuowu = DHT11_ERR_NONE;
    return 1;
}

u8 dht11_read_temp(u16 *temperature_x100)
{
    return dht11_du_wendu(temperature_x100);
}

u8 dht11_read(u16 *temperature_x100, u16 *humidity_x100)
{
    u8 ok;

    ok = dht11_du_wendu(temperature_x100);

    if (humidity_x100 != 0) {
        *humidity_x100 = 0;
    }

    return ok;
}
