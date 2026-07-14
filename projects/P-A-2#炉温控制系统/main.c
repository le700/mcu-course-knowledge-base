#include <reg51.h>
#include <intrins.h>

typedef unsigned char uchar;
typedef unsigned int  uint;

// 引脚定义（严格对应你的电路图）
sbit LCD_RS = P3^5;
sbit LCD_RW = P3^6;
sbit LCD_EN = P3^4;
#define LCD_DATA P0

sbit DQ = P3^7;       // DS18B20
sbit KEY_SET = P1^0;  // 设置键
sbit KEY_ADD = P1^1;  // 加键
sbit KEY_SUB = P1^2;  // 减键

sbit PWM_OUT = P3^0;  // 加热控制
sbit BUZZER  = P3^1;  // 蜂鸣器
sbit LED     = P3^2;  // 报警灯

// 全局变量
float SetTemp = 50.0;  // 目标温度
float CurTemp = 0.0;
uchar PWM_Duty = 0;
uchar Mode = 0;        // 0:显示 1:设上限 2:设下限

// 延时函数
void delay_us(uint us) { while(us--) { _nop_(); } }
void delay_ms(uint ms) {
    uint i,j;
    for(i=0; i<ms; i++)
        for(j=0; j<110; j++);
}

// LCD1602 驱动
void LCD_Write_Cmd(uchar cmd) {
    LCD_RS = 0;
    LCD_RW = 0;
    LCD_DATA = cmd;
    LCD_EN = 1;
    delay_us(2);
    LCD_EN = 0;
    delay_ms(2);
}

void LCD_Write_Data(uchar dat) {
    LCD_RS = 1;
    LCD_RW = 0;
    LCD_DATA = dat;
    LCD_EN = 1;
    delay_us(2);
    LCD_EN = 0;
    delay_ms(2);
}

void LCD_Init() {
    delay_ms(15);
    LCD_Write_Cmd(0x38);  // 16x2 显示
    LCD_Write_Cmd(0x0C);  // 开显示，关光标
    LCD_Write_Cmd(0x06);  // 光标右移
    LCD_Write_Cmd(0x01);  // 清屏
}

void LCD_Set_Pos(uchar x, uchar y) {
    uchar addr;
    if(y == 0) addr = 0x80 + x;
    else       addr = 0xC0 + x;
    LCD_Write_Cmd(addr);
}

void LCD_Show_String(uchar x, uchar y, uchar *str) {
    LCD_Set_Pos(x, y);
    while(*str) { LCD_Write_Data(*str++); }
}

void LCD_Show_Float(uchar x, uchar y, float num) {
    uchar integer = (uchar)num;
    uchar decimal = (uchar)((num - integer) * 10);
    LCD_Set_Pos(x, y);
    LCD_Write_Data(integer/10 + '0');
    LCD_Write_Data(integer%10 + '0');
    LCD_Write_Data('.');
    LCD_Write_Data(decimal + '0');
}

// DS18B20 驱动
uchar DS18B20_Init() {
    uchar ack;
    DQ = 1;
    delay_us(5);
    DQ = 0;
    delay_us(80);
    DQ = 1;
    delay_us(15);
    ack = DQ;
    delay_us(40);
    return ack;
}

uchar DS18B20_Read_Byte() {
    uchar i, dat = 0;
    for(i=0; i<8; i++) {
        DQ = 0;
        delay_us(2);
        DQ = 1;
        delay_us(2);
        if(DQ) dat |= (1<<i);
        delay_us(50);
    }
    return dat;
}

void DS18B20_Write_Byte(uchar dat) {
    uchar i;
    for(i=0; i<8; i++) {
        DQ = 0;
        delay_us(2);
        DQ = dat & 1;
        delay_us(50);
        DQ = 1;
        delay_us(2);
        dat >>= 1;
    }
}

float DS18B20_Get_Temp() {
    uchar L, H;
    uint t;
    DS18B20_Init();
    DS18B20_Write_Byte(0xCC);
    DS18B20_Write_Byte(0x44);
    delay_ms(800);
    DS18B20_Init();
    DS18B20_Write_Byte(0xCC);
    DS18B20_Write_Byte(0xBE);
    L = DS18B20_Read_Byte();
    H = DS18B20_Read_Byte();
    t = (H<<8) | L;
    return t * 0.0625;
}

// 按键扫描
void Key_Scan() {
    if(KEY_SET == 0) {
        delay_ms(20);
        if(KEY_SET == 0) {
            Mode++;
            if(Mode > 2) Mode = 0;
            while(!KEY_SET);
        }
    }
    if(KEY_ADD == 0) {
        delay_ms(20);
        if(KEY_ADD == 0) {
            if(Mode == 1) SetTemp += 1.0;
            else if(Mode == 2) SetTemp -= 1.0;
            while(!KEY_ADD);
        }
    }
}

// 报警检查
void Alarm_Check(float temp) {
    if(temp > 60.0 || temp < 40.0) {
        BUZZER = 0;
        LED = 0;
    } else {
        BUZZER = 1;
        LED = 1;
    }
}

// 主函数
void main() {
    LCD_Init();
    BUZZER = 1;
    LED = 1;
    while(1) {
        CurTemp = DS18B20_Get_Temp();
        Key_Scan();
        Alarm_Check(CurTemp);
        
        LCD_Write_Cmd(0x01);
        LCD_Show_String(0,0,"T:");
        LCD_Show_Float(2,0,CurTemp);
        LCD_Show_String(8,0,"S:");
        LCD_Show_Float(10,0,SetTemp);
        delay_ms(300);
    }
}