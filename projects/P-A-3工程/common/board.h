#ifndef BOARD_H
#define BOARD_H

#include <REG52.H>
#include <INTRINS.H>

/* 类型定义 */
typedef unsigned char u8;
typedef unsigned int u16;
typedef unsigned long u32;

/*
 * 目标板: P-A-3# 温度记录器
 * MCU: IAP15F2K61S2
 * 晶振: 11.0592MHz
 */
#define FOSC_HZ 11059200UL

/* IAP15F2K61S2 扩展 SFR 定义 */
sfr AUXR = 0x8E;   /* 辅助寄存器 */
sfr T2H  = 0xD6;   /* 定时器2高字节 */
sfr T2L  = 0xD7;   /* 定时器2低字节 */

/*
 * 74HC573 片选地址 (通过P2口+SN74HC02译码)
 * 通道号 << 5 映射到 P2 高3位:
 *   channel 4 → 0x80 (LED)
 *   channel 6 → 0xC0 (数码管位选)
 *   channel 7 → 0xE0 (数码管段选)
 */
#define HC573_LED     0x80   /* LED 锁存器地址 */
#define HC573_WEIXUAN 0xC0   /* 数码管位选锁存器地址 */
#define HC573_DUANXUAN 0xE0  /* 数码管段选锁存器地址 */

/* 数码管位数 */
#define DIGITS 8

/*
 * I2C 引脚定义 (PCF8591)
 * SDA = P2.1, SCL = P2.0
 */
sbit SDA = P2^1;
sbit SCL = P2^0;

/* PCF8591 I2C 地址 */
#define PCF8591_WRITE_ADDR 0x90  /* 写地址 */
#define PCF8591_READ_ADDR  0x91  /* 读地址 */

/* DS18B20 单总线引脚 */
sbit DQ = P1^4;

/* 按键引脚定义 */
sbit S4 = P3^3;
sbit S5 = P3^2;
sbit S6 = P3^1;

/* 串口解锁特定数据 */
#define SPECIAL_DATA 0xAA

/* 状态机步骤枚举 */
#define STEP_UART       1  /* 第1步: 串口通信 */
#define STEP_S4         2  /* 第2步: S4按键 */
#define STEP_S5_PCF8591 3  /* 第3步: PCF8591读温度 */
#define STEP_S6_DS18B20 4  /* 第4步: DS18B20读温度 */

#endif