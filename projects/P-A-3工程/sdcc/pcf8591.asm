;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 4.0.0 #11528 (Linux)
;--------------------------------------------------------
	.module pcf8591
	.optsdcc -mmcs51 --model-small
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _delay_us
	.globl _S6
	.globl _S5
	.globl _S4
	.globl _DQ
	.globl _SCL
	.globl _SDA
	.globl _TF2
	.globl _EXF2
	.globl _RCLK
	.globl _TCLK
	.globl _EXEN2
	.globl _TR2
	.globl _C_T2
	.globl _CP_RL2
	.globl _T2CON_7
	.globl _T2CON_6
	.globl _T2CON_5
	.globl _T2CON_4
	.globl _T2CON_3
	.globl _T2CON_2
	.globl _T2CON_1
	.globl _T2CON_0
	.globl _PT2
	.globl _ET2
	.globl _CY
	.globl _AC
	.globl _F0
	.globl _RS1
	.globl _RS0
	.globl _OV
	.globl _F1
	.globl _P
	.globl _PS
	.globl _PT1
	.globl _PX1
	.globl _PT0
	.globl _PX0
	.globl _RD
	.globl _WR
	.globl _T1
	.globl _T0
	.globl _INT1
	.globl _INT0
	.globl _TXD
	.globl _RXD
	.globl _P3_7
	.globl _P3_6
	.globl _P3_5
	.globl _P3_4
	.globl _P3_3
	.globl _P3_2
	.globl _P3_1
	.globl _P3_0
	.globl _EA
	.globl _ES
	.globl _ET1
	.globl _EX1
	.globl _ET0
	.globl _EX0
	.globl _P2_7
	.globl _P2_6
	.globl _P2_5
	.globl _P2_4
	.globl _P2_3
	.globl _P2_2
	.globl _P2_1
	.globl _P2_0
	.globl _SM0
	.globl _SM1
	.globl _SM2
	.globl _REN
	.globl _TB8
	.globl _RB8
	.globl _TI
	.globl _RI
	.globl _P1_7
	.globl _P1_6
	.globl _P1_5
	.globl _P1_4
	.globl _P1_3
	.globl _P1_2
	.globl _P1_1
	.globl _P1_0
	.globl _TF1
	.globl _TR1
	.globl _TF0
	.globl _TR0
	.globl _IE1
	.globl _IT1
	.globl _IE0
	.globl _IT0
	.globl _P0_7
	.globl _P0_6
	.globl _P0_5
	.globl _P0_4
	.globl _P0_3
	.globl _P0_2
	.globl _P0_1
	.globl _P0_0
	.globl _T2L
	.globl _T2H
	.globl _AUXR
	.globl _TH2
	.globl _TL2
	.globl _RCAP2H
	.globl _RCAP2L
	.globl _T2CON
	.globl _B
	.globl _ACC
	.globl _PSW
	.globl _IP
	.globl _P3
	.globl _IE
	.globl _P2
	.globl _SBUF
	.globl _SCON
	.globl _P1
	.globl _TH1
	.globl _TH0
	.globl _TL1
	.globl _TL0
	.globl _TMOD
	.globl _TCON
	.globl _PCON
	.globl _DPH
	.globl _DPL
	.globl _SP
	.globl _P0
	.globl _pcf8591_init
	.globl _pcf8591_read_adc
;--------------------------------------------------------
; special function registers
;--------------------------------------------------------
	.area RSEG    (ABS,DATA)
	.org 0x0000
_P0	=	0x0080
_SP	=	0x0081
_DPL	=	0x0082
_DPH	=	0x0083
_PCON	=	0x0087
_TCON	=	0x0088
_TMOD	=	0x0089
_TL0	=	0x008a
_TL1	=	0x008b
_TH0	=	0x008c
_TH1	=	0x008d
_P1	=	0x0090
_SCON	=	0x0098
_SBUF	=	0x0099
_P2	=	0x00a0
_IE	=	0x00a8
_P3	=	0x00b0
_IP	=	0x00b8
_PSW	=	0x00d0
_ACC	=	0x00e0
_B	=	0x00f0
_T2CON	=	0x00c8
_RCAP2L	=	0x00ca
_RCAP2H	=	0x00cb
_TL2	=	0x00cc
_TH2	=	0x00cd
_AUXR	=	0x008e
_T2H	=	0x00d6
_T2L	=	0x00d7
;--------------------------------------------------------
; special function bits
;--------------------------------------------------------
	.area RSEG    (ABS,DATA)
	.org 0x0000
_P0_0	=	0x0080
_P0_1	=	0x0081
_P0_2	=	0x0082
_P0_3	=	0x0083
_P0_4	=	0x0084
_P0_5	=	0x0085
_P0_6	=	0x0086
_P0_7	=	0x0087
_IT0	=	0x0088
_IE0	=	0x0089
_IT1	=	0x008a
_IE1	=	0x008b
_TR0	=	0x008c
_TF0	=	0x008d
_TR1	=	0x008e
_TF1	=	0x008f
_P1_0	=	0x0090
_P1_1	=	0x0091
_P1_2	=	0x0092
_P1_3	=	0x0093
_P1_4	=	0x0094
_P1_5	=	0x0095
_P1_6	=	0x0096
_P1_7	=	0x0097
_RI	=	0x0098
_TI	=	0x0099
_RB8	=	0x009a
_TB8	=	0x009b
_REN	=	0x009c
_SM2	=	0x009d
_SM1	=	0x009e
_SM0	=	0x009f
_P2_0	=	0x00a0
_P2_1	=	0x00a1
_P2_2	=	0x00a2
_P2_3	=	0x00a3
_P2_4	=	0x00a4
_P2_5	=	0x00a5
_P2_6	=	0x00a6
_P2_7	=	0x00a7
_EX0	=	0x00a8
_ET0	=	0x00a9
_EX1	=	0x00aa
_ET1	=	0x00ab
_ES	=	0x00ac
_EA	=	0x00af
_P3_0	=	0x00b0
_P3_1	=	0x00b1
_P3_2	=	0x00b2
_P3_3	=	0x00b3
_P3_4	=	0x00b4
_P3_5	=	0x00b5
_P3_6	=	0x00b6
_P3_7	=	0x00b7
_RXD	=	0x00b0
_TXD	=	0x00b1
_INT0	=	0x00b2
_INT1	=	0x00b3
_T0	=	0x00b4
_T1	=	0x00b5
_WR	=	0x00b6
_RD	=	0x00b7
_PX0	=	0x00b8
_PT0	=	0x00b9
_PX1	=	0x00ba
_PT1	=	0x00bb
_PS	=	0x00bc
_P	=	0x00d0
_F1	=	0x00d1
_OV	=	0x00d2
_RS0	=	0x00d3
_RS1	=	0x00d4
_F0	=	0x00d5
_AC	=	0x00d6
_CY	=	0x00d7
_ET2	=	0x00ad
_PT2	=	0x00bd
_T2CON_0	=	0x00c8
_T2CON_1	=	0x00c9
_T2CON_2	=	0x00ca
_T2CON_3	=	0x00cb
_T2CON_4	=	0x00cc
_T2CON_5	=	0x00cd
_T2CON_6	=	0x00ce
_T2CON_7	=	0x00cf
_CP_RL2	=	0x00c8
_C_T2	=	0x00c9
_TR2	=	0x00ca
_EXEN2	=	0x00cb
_TCLK	=	0x00cc
_RCLK	=	0x00cd
_EXF2	=	0x00ce
_TF2	=	0x00cf
_SDA	=	0x00a1
_SCL	=	0x00a0
_DQ	=	0x0094
_S4	=	0x00b3
_S5	=	0x00b2
_S6	=	0x00b1
;--------------------------------------------------------
; overlayable register banks
;--------------------------------------------------------
	.area REG_BANK_0	(REL,OVR,DATA)
	.ds 8
;--------------------------------------------------------
; internal ram data
;--------------------------------------------------------
	.area DSEG    (DATA)
;--------------------------------------------------------
; overlayable items in internal ram 
;--------------------------------------------------------
;--------------------------------------------------------
; indirectly addressable internal ram data
;--------------------------------------------------------
	.area ISEG    (DATA)
;--------------------------------------------------------
; absolute internal ram data
;--------------------------------------------------------
	.area IABS    (ABS,DATA)
	.area IABS    (ABS,DATA)
;--------------------------------------------------------
; bit data
;--------------------------------------------------------
	.area BSEG    (BIT)
;--------------------------------------------------------
; paged external ram data
;--------------------------------------------------------
	.area PSEG    (PAG,XDATA)
;--------------------------------------------------------
; external ram data
;--------------------------------------------------------
	.area XSEG    (XDATA)
;--------------------------------------------------------
; absolute external ram data
;--------------------------------------------------------
	.area XABS    (ABS,XDATA)
;--------------------------------------------------------
; external initialized ram data
;--------------------------------------------------------
	.area XISEG   (XDATA)
	.area HOME    (CODE)
	.area GSINIT0 (CODE)
	.area GSINIT1 (CODE)
	.area GSINIT2 (CODE)
	.area GSINIT3 (CODE)
	.area GSINIT4 (CODE)
	.area GSINIT5 (CODE)
	.area GSINIT  (CODE)
	.area GSFINAL (CODE)
	.area CSEG    (CODE)
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area HOME    (CODE)
	.area GSINIT  (CODE)
	.area GSFINAL (CODE)
	.area GSINIT  (CODE)
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area HOME    (CODE)
	.area HOME    (CODE)
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area CSEG    (CODE)
;------------------------------------------------------------
;Allocation info for local variables in function 'I2C_Start'
;------------------------------------------------------------
;	pcf8591.c:8: static void I2C_Start(void)
;	-----------------------------------------
;	 function I2C_Start
;	-----------------------------------------
_I2C_Start:
	ar7 = 0x07
	ar6 = 0x06
	ar5 = 0x05
	ar4 = 0x04
	ar3 = 0x03
	ar2 = 0x02
	ar1 = 0x01
	ar0 = 0x00
;	pcf8591.c:10: SDA = 1;
;	assignBit
	setb	_SDA
;	pcf8591.c:11: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:12: delay_us(5);
	mov	dptr,#0x0005
	lcall	_delay_us
;	pcf8591.c:13: SDA = 0;
;	assignBit
	clr	_SDA
;	pcf8591.c:14: delay_us(5);
	mov	dptr,#0x0005
	lcall	_delay_us
;	pcf8591.c:15: SCL = 0;
;	assignBit
	clr	_SCL
;	pcf8591.c:16: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'I2C_Stop'
;------------------------------------------------------------
;	pcf8591.c:22: static void I2C_Stop(void)
;	-----------------------------------------
;	 function I2C_Stop
;	-----------------------------------------
_I2C_Stop:
;	pcf8591.c:24: SDA = 0;
;	assignBit
	clr	_SDA
;	pcf8591.c:25: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:26: delay_us(5);
	mov	dptr,#0x0005
	lcall	_delay_us
;	pcf8591.c:27: SDA = 1;
;	assignBit
	setb	_SDA
;	pcf8591.c:28: delay_us(5);
	mov	dptr,#0x0005
;	pcf8591.c:29: }
	ljmp	_delay_us
;------------------------------------------------------------
;Allocation info for local variables in function 'I2C_SendByte'
;------------------------------------------------------------
;dat                       Allocated to registers r7 
;i                         Allocated to registers r6 
;------------------------------------------------------------
;	pcf8591.c:35: static void I2C_SendByte(u8 dat)
;	-----------------------------------------
;	 function I2C_SendByte
;	-----------------------------------------
_I2C_SendByte:
	mov	r7,dpl
;	pcf8591.c:39: for (i = 0; i < 8; i++) {
	mov	r6,#0x00
00102$:
;	pcf8591.c:40: SDA = dat >> 7;              /* 取最高位发送 */
	mov	a,r7
	rl	a
	anl	a,#0x01
;	assignBit
	add	a,#0xff
	mov	_SDA,c
;	pcf8591.c:41: dat <<= 1;                   /* 左移准备下一位 */
	mov	ar5,r7
	mov	a,r5
	add	a,r5
	mov	r7,a
;	pcf8591.c:42: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:43: delay_us(5);
	mov	dptr,#0x0005
	push	ar7
	push	ar6
	lcall	_delay_us
;	pcf8591.c:44: SCL = 0;
;	assignBit
	clr	_SCL
;	pcf8591.c:45: delay_us(2);
	mov	dptr,#0x0002
	lcall	_delay_us
	pop	ar6
	pop	ar7
;	pcf8591.c:39: for (i = 0; i < 8; i++) {
	inc	r6
	cjne	r6,#0x08,00115$
00115$:
	jc	00102$
;	pcf8591.c:49: SDA = 1;
;	assignBit
	setb	_SDA
;	pcf8591.c:50: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:51: delay_us(5);
	mov	dptr,#0x0005
	lcall	_delay_us
;	pcf8591.c:52: SCL = 0;
;	assignBit
	clr	_SCL
;	pcf8591.c:53: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'I2C_ReadByte'
;------------------------------------------------------------
;i                         Allocated to registers r6 
;dat                       Allocated to registers r5 
;------------------------------------------------------------
;	pcf8591.c:59: static u8 I2C_ReadByte(void)
;	-----------------------------------------
;	 function I2C_ReadByte
;	-----------------------------------------
_I2C_ReadByte:
;	pcf8591.c:61: u8 i, dat = 0;
	mov	r7,#0x00
;	pcf8591.c:63: SDA = 1;                         /* 释放SDA，准备读取 */
;	assignBit
	setb	_SDA
;	pcf8591.c:64: for (i = 0; i < 8; i++) {
	mov	r6,#0x00
00102$:
;	pcf8591.c:65: dat <<= 1;                   /* 左移腾出最低位 */
	mov	ar5,r7
	mov	a,r5
	add	a,r5
	mov	r5,a
;	pcf8591.c:66: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:67: delay_us(5);
	mov	dptr,#0x0005
	push	ar6
	push	ar5
	lcall	_delay_us
	pop	ar5
	pop	ar6
;	pcf8591.c:68: dat |= SDA;                  /* 读取SDA电平 */
	mov	c,_SDA
	clr	a
	rlc	a
	orl	a,r5
	mov	r7,a
;	pcf8591.c:69: SCL = 0;
;	assignBit
	clr	_SCL
;	pcf8591.c:70: delay_us(2);
	mov	dptr,#0x0002
	push	ar7
	push	ar6
	lcall	_delay_us
	pop	ar6
	pop	ar7
;	pcf8591.c:64: for (i = 0; i < 8; i++) {
	inc	r6
	cjne	r6,#0x08,00117$
00117$:
	jc	00102$
;	pcf8591.c:74: SDA = 1;
;	assignBit
	setb	_SDA
;	pcf8591.c:75: SCL = 1;
;	assignBit
	setb	_SCL
;	pcf8591.c:76: delay_us(5);
	mov	dptr,#0x0005
	push	ar7
	lcall	_delay_us
	pop	ar7
;	pcf8591.c:77: SCL = 0;
;	assignBit
	clr	_SCL
;	pcf8591.c:79: return dat;
	mov	dpl,r7
;	pcf8591.c:80: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'pcf8591_init'
;------------------------------------------------------------
;	pcf8591.c:86: void pcf8591_init(void)
;	-----------------------------------------
;	 function pcf8591_init
;	-----------------------------------------
_pcf8591_init:
;	pcf8591.c:89: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'pcf8591_read_adc'
;------------------------------------------------------------
;channel                   Allocated to registers r7 
;val                       Allocated to registers r7 
;------------------------------------------------------------
;	pcf8591.c:105: u8 pcf8591_read_adc(u8 channel)
;	-----------------------------------------
;	 function pcf8591_read_adc
;	-----------------------------------------
_pcf8591_read_adc:
	mov	r7,dpl
;	pcf8591.c:109: I2C_Start();                     /* 起始信号 */
	push	ar7
	lcall	_I2C_Start
;	pcf8591.c:110: I2C_SendByte(PCF8591_WRITE_ADDR);/* 发送写地址 0x90 */
	mov	dpl,#0x90
	lcall	_I2C_SendByte
	pop	ar7
;	pcf8591.c:111: I2C_SendByte(0x40 | channel);    /* 控制字: 使能DAC+自动增量+选择通道 */
	mov	a,#0x40
	orl	a,r7
	mov	dpl,a
	lcall	_I2C_SendByte
;	pcf8591.c:112: I2C_Start();                     /* 重新起始 */
	lcall	_I2C_Start
;	pcf8591.c:113: I2C_SendByte(PCF8591_READ_ADDR); /* 发送读地址 0x91 */
	mov	dpl,#0x91
	lcall	_I2C_SendByte
;	pcf8591.c:114: val = I2C_ReadByte();            /* 读取ADC转换结果 */
	lcall	_I2C_ReadByte
	mov	r7,dpl
;	pcf8591.c:115: I2C_Stop();                      /* 停止信号 */
	push	ar7
	lcall	_I2C_Stop
	pop	ar7
;	pcf8591.c:117: return val;
	mov	dpl,r7
;	pcf8591.c:118: }
	ret
	.area CSEG    (CODE)
	.area CONST   (CODE)
	.area XINIT   (CODE)
	.area CABS    (ABS,CODE)
