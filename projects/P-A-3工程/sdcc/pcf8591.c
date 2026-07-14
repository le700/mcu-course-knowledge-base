#include "pcf8591.h"
#include "delay.h"

/*
 * I2C 起始信号
 * SCL高电平时，SDA由高变低
 */
static void I2C_Start(void)
{
    SDA = 1;
    SCL = 1;
    delay_us(5);
    SDA = 0;
    delay_us(5);
    SCL = 0;
}

/*
 * I2C 停止信号
 * SCL高电平时，SDA由低变高
 */
static void I2C_Stop(void)
{
    SDA = 0;
    SCL = 1;
    delay_us(5);
    SDA = 1;
    delay_us(5);
}

/*
 * I2C 发送一个字节
 * 发送8位数据后释放SDA等待应答
 */
static void I2C_SendByte(u8 dat)
{
    u8 i;

    for (i = 0; i < 8; i++) {
        SDA = dat >> 7;              /* 取最高位发送 */
        dat <<= 1;                   /* 左移准备下一位 */
        SCL = 1;
        delay_us(5);
        SCL = 0;
        delay_us(2);
    }

    /* 释放SDA，等待从机应答 */
    SDA = 1;
    SCL = 1;
    delay_us(5);
    SCL = 0;
}

/*
 * I2C 读取一个字节
 * 返回读取到的8位数据
 */
static u8 I2C_ReadByte(void)
{
    u8 i, dat = 0;

    SDA = 1;                         /* 释放SDA，准备读取 */
    for (i = 0; i < 8; i++) {
        dat <<= 1;                   /* 左移腾出最低位 */
        SCL = 1;
        delay_us(5);
        dat |= SDA;                  /* 读取SDA电平 */
        SCL = 0;
        delay_us(2);
    }

    /* 主机发送NACK (SDA=1)，第9个时钟脉冲 */
    SDA = 1;
    SCL = 1;
    delay_us(5);
    SCL = 0;

    return dat;
}

/*
 * PCF8591 初始化
 * 上电后无需额外初始化，保留接口
 */
void pcf8591_init(void)
{
    /* PCF8591 上电即可工作，无需额外配置 */
}

/*
 * 读取 PCF8591 指定通道的 ADC 值
 * channel: 通道号 (0~3)，P-A-3# 使用通道3 (RB2)
 * 返回值: 0~255 的 ADC 原始数字量
 *
 * 操作流程:
 *   1. 发送起始信号
 *   2. 发送写地址 0x90
 *   3. 发送控制字节 (0x40 | channel)，使能模拟输出+自动增量
 *   4. 重新发送起始信号
 *   5. 发送读地址 0x91
 *   6. 读取 ADC 数据
 *   7. 发送停止信号
 */
u8 pcf8591_read_adc(u8 channel)
{
    u8 val;

    I2C_Start();                     /* 起始信号 */
    I2C_SendByte(PCF8591_WRITE_ADDR);/* 发送写地址 0x90 */
    I2C_SendByte(0x40 | channel);    /* 控制字: 使能DAC+自动增量+选择通道 */
    I2C_Start();                     /* 重新起始 */
    I2C_SendByte(PCF8591_READ_ADDR); /* 发送读地址 0x91 */
    val = I2C_ReadByte();            /* 读取ADC转换结果 */
    I2C_Stop();                      /* 停止信号 */

    return val;
}