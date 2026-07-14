#include "ds18b20.h"
#include "delay.h"

/*
 * DS18B20 初始化
 * 发送复位脉冲，检测从机应答
 * 返回值: 0=成功(检测到应答), 1=失败
 */
u8 ds18b20_init(void)
{
    u8 ack;

    EA = 0;                          /* 关中断，保证时序 */

    DQ = 0;                          /* 拉低总线，复位脉冲 */
    delay_us(500);                   /* 保持至少 480us */
    DQ = 1;                          /* 释放总线 */
    delay_us(50);                    /* 等待 15~60us */
    ack = DQ;                        /* 读取应答信号 (0=应答) */

    EA = 1;                          /* 开中断 */

    delay_us(400);                   /* 等待复位完成 */

    return ack;
}

/*
 * DS18B20 写一个字节
 * dat: 要写入的字节数据
 * 注意: 写时序要求关中断保证精确延时
 */
void ds18b20_write_byte(u8 dat)
{
    u8 i;

    for (i = 0; i < 8; i++) {
        EA = 0;                      /* 关中断 */

        DQ = 0;                      /* 拉低总线，写起始 */
        delay_us(2);                 /* 保持至少 1us */
        DQ = dat & 0x01;             /* 写入最低位 */
        delay_us(60);                /* 保持至少 60us */
        DQ = 1;                      /* 释放总线 */
        delay_us(2);                 /* 恢复时间 */

        EA = 1;                      /* 开中断 */

        dat >>= 1;                   /* 准备下一位 */
    }
}

/*
 * DS18B20 读一个字节
 * 返回值: 读取到的8位数据
 * 注意: 读时序要求关中断保证精确延时
 */
u8 ds18b20_read_byte(void)
{
    u8 i, dat = 0;

    for (i = 0; i < 8; i++) {
        dat >>= 1;                   /* 先右移，为读取位腾出最高位 */

        EA = 0;                      /* 关中断 */

        DQ = 0;                      /* 拉低总线，读起始 */
        delay_us(2);                 /* 保持至少 1us */
        DQ = 1;                      /* 释放总线 */
        delay_us(2);                 /* 等待数据稳定 */
        if (DQ) dat |= 0x80;         /* 读取数据位到最高位 */
        delay_us(60);                /* 等待读时序完成 */

        EA = 1;                      /* 开中断 */
    }

    return dat;
}

/*
 * 读取 DS18B20 温度值 (原始16位)
 * 返回值: 16位原始温度数据 (含符号位)
 *
 * 操作流程:
 *   1. 初始化 DS18B20
 *   2. 跳过 ROM (0xCC)
 *   3. 启动温度转换 (0x44)
 *   4. 等待转换完成 (~750ms)
 *   5. 再次初始化
 *   6. 跳过 ROM (0xCC)
 *   7. 读暂存器 (0xBE)
 *   8. 读取低8位 + 高8位
 */
u16 ds18b20_read_temp(void)
{
    u8 LSB, MSB;
    u16 raw;

    /* 启动温度转换 */
    ds18b20_init();
    ds18b20_write_byte(0xCC);        /* 跳过 ROM */
    ds18b20_write_byte(0x44);        /* 启动温度转换 */

    /* 等待转换完成 (最大 750ms) */
    delay_ms(750);

    /* 读取温度数据 */
    ds18b20_init();
    ds18b20_write_byte(0xCC);        /* 跳过 ROM */
    ds18b20_write_byte(0xBE);        /* 读暂存器命令 */

    LSB = ds18b20_read_byte();       /* 温度低字节 */
    MSB = ds18b20_read_byte();       /* 温度高字节 */

    /* 结束读取 (读取剩余字节并复位) */
    ds18b20_init();

    raw = (MSB << 8) | LSB;          /* 合成16位原始温度值 */

    return raw;
}