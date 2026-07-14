#ifndef DHT11_H
#define DHT11_H

#include "board.h"

#define DHT11_ERR_NONE       0
#define DHT11_ERR_RESP_LOW   1
#define DHT11_ERR_RESP_HIGH  2
#define DHT11_ERR_RESP_END   3
#define DHT11_ERR_BIT_READ   4
#define DHT11_ERR_BIT_END    5
#define DHT11_ERR_ALL_ZERO   6
#define DHT11_ERR_CHECKSUM   7
#define DHT11_ERR_RANGE      8
#define DHT11_ERR_UNKNOWN    9

u8 dht11_du_wendu(u16 *huanjing_wendu_x100);

u8 dht11_read_temp(u16 *temperature_x100);
u8 dht11_read(u16 *temperature_x100, u16 *humidity_x100);
u8 dht11_get_error(void);
u8 dht11_get_last_error(void);
u8 dht11_get_last_bit_index(void);
u8 dht11_get_last_raw(u8 index);

#endif
