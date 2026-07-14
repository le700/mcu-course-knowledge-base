;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 4.0.0 #11528 (Linux)
;--------------------------------------------------------
	.module main
	.optsdcc -mmcs51 --model-small
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
	.globl _UART_ISR
	.globl _main
	.globl _Timer0_ISR
	.globl _ds18b20_read_temp
	.globl _ds18b20_init
	.globl _pcf8591_read_adc
	.globl _pcf8591_init
	.globl _uart_send_byte
	.globl _uart_init
	.globl _display_set_temp
	.globl _display_scan_isr
	.globl _display_init
	.globl _led_all_on
	.globl _led_write
	.globl _led_init
	.globl _delay_ms
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
; overlayable bit register bank
;--------------------------------------------------------
	.area BIT_BANK	(REL,OVR,DATA)
bits:
	.ds 1
	b0 = bits[0]
	b1 = bits[1]
	b2 = bits[2]
	b3 = bits[3]
	b4 = bits[4]
	b5 = bits[5]
	b6 = bits[6]
	b7 = bits[7]
;--------------------------------------------------------
; internal ram data
;--------------------------------------------------------
	.area DSEG    (DATA)
_step:
	.ds 1
_mode:
	.ds 1
_Rx_data:
	.ds 1
_update_tick:
	.ds 2
;--------------------------------------------------------
; overlayable items in internal ram 
;--------------------------------------------------------
;--------------------------------------------------------
; Stack segment in internal ram 
;--------------------------------------------------------
	.area	SSEG
__start__stack:
	.ds	1

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
_Rx_flag:
	.ds 1
_flag_update:
	.ds 1
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
; interrupt vector 
;--------------------------------------------------------
	.area HOME    (CODE)
__interrupt_vect:
	ljmp	__sdcc_gsinit_startup
	reti
	.ds	7
	ljmp	_Timer0_ISR
	.ds	5
	reti
	.ds	7
	reti
	.ds	7
	ljmp	_UART_ISR
;--------------------------------------------------------
; global & static initialisations
;--------------------------------------------------------
	.area HOME    (CODE)
	.area GSINIT  (CODE)
	.area GSFINAL (CODE)
	.area GSINIT  (CODE)
	.globl __sdcc_gsinit_startup
	.globl __sdcc_program_startup
	.globl __start__stack
	.globl __mcs51_genXINIT
	.globl __mcs51_genXRAMCLEAR
	.globl __mcs51_genRAMCLEAR
;	main.c:10: static u8 step = STEP_UART;          /* 当前步骤 */
	mov	_step,#0x01
;	main.c:11: static u8 mode = 0;                  /* 0=空闲, 1=PCF8591, 2=DS18B20 */
	mov	_mode,#0x00
;	main.c:14: static u16 update_tick = 0;          /* 温度更新计数器 */
	clr	a
	mov	_update_tick,a
	mov	(_update_tick + 1),a
;	main.c:12: static __bit Rx_flag = 0;            /* 串口接收标志 */
;	assignBit
	clr	_Rx_flag
;	main.c:15: static __bit flag_update = 1;        /* 温度更新标志 */
;	assignBit
	setb	_flag_update
	.area GSFINAL (CODE)
	ljmp	__sdcc_program_startup
;--------------------------------------------------------
; Home
;--------------------------------------------------------
	.area HOME    (CODE)
	.area HOME    (CODE)
__sdcc_program_startup:
	ljmp	_main
;	return from main will return to caller
;--------------------------------------------------------
; code
;--------------------------------------------------------
	.area CSEG    (CODE)
;------------------------------------------------------------
;Allocation info for local variables in function 'Timer0_Init'
;------------------------------------------------------------
;	main.c:23: static void Timer0_Init(void)
;	-----------------------------------------
;	 function Timer0_Init
;	-----------------------------------------
_Timer0_Init:
	ar7 = 0x07
	ar6 = 0x06
	ar5 = 0x05
	ar4 = 0x04
	ar3 = 0x03
	ar2 = 0x02
	ar1 = 0x01
	ar0 = 0x00
;	main.c:25: AUXR &= 0x7F;                    /* 定时器0 12T模式 */
	anl	_AUXR,#0x7f
;	main.c:26: TMOD &= 0xF0;                    /* 清定时器0配置 */
	anl	_TMOD,#0xf0
;	main.c:27: TMOD |= 0x01;                    /* 定时器0 方式1 (16位) */
	orl	_TMOD,#0x01
;	main.c:28: TH0 = (65536 - 2000) / 256;      /* 定时初值高字节 */
	mov	_TH0,#0xf8
;	main.c:29: TL0 = (65536 - 2000) % 256;      /* 定时初值低字节 */
	mov	_TL0,#0x30
;	main.c:30: ET0 = 1;                         /* 允许定时器0中断 */
;	assignBit
	setb	_ET0
;	main.c:31: TR0 = 1;                         /* 启动定时器0 */
;	assignBit
	setb	_TR0
;	main.c:32: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'Timer0_ISR'
;------------------------------------------------------------
;	main.c:40: void Timer0_ISR(void) __interrupt(1)
;	-----------------------------------------
;	 function Timer0_ISR
;	-----------------------------------------
_Timer0_ISR:
	push	bits
	push	acc
	push	b
	push	dpl
	push	dph
	push	(0+7)
	push	(0+6)
	push	(0+5)
	push	(0+4)
	push	(0+3)
	push	(0+2)
	push	(0+1)
	push	(0+0)
	push	psw
	mov	psw,#0x00
;	main.c:42: TH0 = (65536 - 2000) / 256;      /* 重装定时初值 */
	mov	_TH0,#0xf8
;	main.c:43: TL0 = (65536 - 2000) % 256;
	mov	_TL0,#0x30
;	main.c:46: display_scan_isr();
	lcall	_display_scan_isr
;	main.c:49: if (step >= STEP_S5_PCF8591) {
	mov	a,#0x100 - 0x03
	add	a,_step
	jnc	00105$
;	main.c:50: update_tick++;
	inc	_update_tick
	clr	a
	cjne	a,_update_tick,00116$
	inc	(_update_tick + 1)
00116$:
;	main.c:51: if (update_tick >= 150) {    /* 150 * 2ms = 300ms */
	clr	c
	mov	a,_update_tick
	subb	a,#0x96
	mov	a,(_update_tick + 1)
	subb	a,#0x00
	jc	00105$
;	main.c:52: update_tick = 0;
	clr	a
	mov	_update_tick,a
	mov	(_update_tick + 1),a
;	main.c:53: flag_update = 1;         /* 触发温度更新 */
;	assignBit
	setb	_flag_update
00105$:
;	main.c:56: }
	pop	psw
	pop	(0+0)
	pop	(0+1)
	pop	(0+2)
	pop	(0+3)
	pop	(0+4)
	pop	(0+5)
	pop	(0+6)
	pop	(0+7)
	pop	dph
	pop	dpl
	pop	b
	pop	acc
	pop	bits
	reti
;------------------------------------------------------------
;Allocation info for local variables in function 'System_Init'
;------------------------------------------------------------
;	main.c:62: static void System_Init(void)
;	-----------------------------------------
;	 function System_Init
;	-----------------------------------------
_System_Init:
;	main.c:65: P0 = 0xFF;                       /* 段选全灭 */
	mov	_P0,#0xff
;	main.c:66: P2 = (P2 & 0x1F) | HC573_DUANXUAN;
	mov	a,_P2
	anl	a,#0x1f
	orl	a,#0xe0
	mov	_P2,a
;	main.c:67: P2 = (P2 & 0x1F);
	anl	_P2,#0x1f
;	main.c:69: P0 = 0x00;                       /* 位选全关 */
	mov	_P0,#0x00
;	main.c:70: P2 = (P2 & 0x1F) | HC573_WEIXUAN;
	mov	a,_P2
	anl	a,#0x1f
	orl	a,#0xc0
	mov	_P2,a
;	main.c:71: P2 = (P2 & 0x1F);
	anl	_P2,#0x1f
;	main.c:74: led_init();                      /* LED 初始化 */
	lcall	_led_init
;	main.c:75: display_init();                  /* 数码管初始化 */
	lcall	_display_init
;	main.c:76: uart_init();                     /* 串口初始化 */
	lcall	_uart_init
;	main.c:77: pcf8591_init();                  /* PCF8591 初始化 */
	lcall	_pcf8591_init
;	main.c:78: ds18b20_init();                  /* DS18B20 初始化 */
	lcall	_ds18b20_init
;	main.c:79: Timer0_Init();                   /* 定时器0初始化 */
;	main.c:80: }
	ljmp	_Timer0_Init
;------------------------------------------------------------
;Allocation info for local variables in function 'Key_Scan'
;------------------------------------------------------------
;	main.c:91: static void Key_Scan(void)
;	-----------------------------------------
;	 function Key_Scan
;	-----------------------------------------
_Key_Scan:
;	main.c:94: if (step == STEP_S4) {
	mov	a,#0x02
	cjne	a,_step,00109$
;	main.c:95: if (S4 == 0) {               /* 检测按键按下 */
	jb	_S4,00109$
;	main.c:96: delay_ms(20);            /* 消抖延时 */
	mov	dptr,#0x0014
	lcall	_delay_ms
;	main.c:97: if (S4 == 0) {           /* 二次确认 */
	jb	_S4,00109$
;	main.c:98: led_all_on();        /* 8个LED全亮 */
	lcall	_led_all_on
;	main.c:99: step = STEP_S5_PCF8591;  /* 进入步骤3 */
	mov	_step,#0x03
;	main.c:100: flag_update = 1;     /* 立即触发温度更新 */
;	assignBit
	setb	_flag_update
;	main.c:101: while (S4 == 0);     /* 等待按键释放 */
00101$:
	jnb	_S4,00101$
00109$:
;	main.c:107: if (step >= STEP_S5_PCF8591) {
	mov	a,#0x100 - 0x03
	add	a,_step
	jnc	00126$
;	main.c:109: if (S5 == 0) {
	jb	_S5,00116$
;	main.c:110: delay_ms(20);            /* 消抖延时 */
	mov	dptr,#0x0014
	lcall	_delay_ms
;	main.c:111: if (S5 == 0) {           /* 二次确认 */
	jb	_S5,00116$
;	main.c:112: mode = 1;            /* PCF8591 模式 */
	mov	_mode,#0x01
;	main.c:113: step = STEP_S5_PCF8591;
	mov	_step,#0x03
;	main.c:114: flag_update = 1;     /* 立即触发更新 */
;	assignBit
	setb	_flag_update
;	main.c:115: while (S5 == 0);     /* 等待按键释放 */
00110$:
	jnb	_S5,00110$
00116$:
;	main.c:120: if (S6 == 0) {
	jb	_S6,00126$
;	main.c:121: delay_ms(20);            /* 消抖延时 */
	mov	dptr,#0x0014
	lcall	_delay_ms
;	main.c:122: if (S6 == 0) {           /* 二次确认 */
	jb	_S6,00126$
;	main.c:123: mode = 2;            /* DS18B20 模式 */
	mov	_mode,#0x02
;	main.c:124: step = STEP_S6_DS18B20;
	mov	_step,#0x04
;	main.c:125: flag_update = 1;     /* 立即触发更新 */
;	assignBit
	setb	_flag_update
;	main.c:126: while (S6 == 0);     /* 等待按键释放 */
00117$:
	jnb	_S6,00117$
00126$:
;	main.c:130: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'Proc_UART'
;------------------------------------------------------------
;	main.c:139: static void Proc_UART(void)
;	-----------------------------------------
;	 function Proc_UART
;	-----------------------------------------
_Proc_UART:
;	main.c:141: if (Rx_flag == 0) return;        /* 无数据则返回 */
	jb	_Rx_flag,00102$
	ret
00102$:
;	main.c:143: Rx_flag = 0;
;	assignBit
	clr	_Rx_flag
;	main.c:146: uart_send_byte(Rx_data);
	mov	dpl,_Rx_data
	lcall	_uart_send_byte
;	main.c:149: if (step == STEP_UART) {
	mov	a,#0x01
	cjne	a,_step,00107$
;	main.c:151: led_write(Rx_data);
	mov	dpl,_Rx_data
	lcall	_led_write
;	main.c:154: if (Rx_data == SPECIAL_DATA) {
	mov	a,#0xaa
	cjne	a,_Rx_data,00107$
;	main.c:155: step = STEP_S4;          /* 解锁，进入步骤2 */
	mov	_step,#0x02
00107$:
;	main.c:158: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'Update_Display'
;------------------------------------------------------------
;adc                       Allocated to registers r7 
;temp_val                  Allocated to registers 
;raw                       Allocated to registers r6 r7 
;------------------------------------------------------------
;	main.c:175: static void Update_Display(void)
;	-----------------------------------------
;	 function Update_Display
;	-----------------------------------------
_Update_Display:
;	main.c:182: if (flag_update == 0) return;    /* 无需更新则返回 */
	jb	_flag_update,00102$
	ret
00102$:
;	main.c:183: flag_update = 0;
;	assignBit
	clr	_flag_update
;	main.c:185: if (mode == 1) {
	mov	a,#0x01
	cjne	a,_mode,00108$
;	main.c:187: adc = pcf8591_read_adc(0x03);     /* 读取 RB2 通道 */
	mov	dpl,#0x03
	lcall	_pcf8591_read_adc
	mov	r7,dpl
;	main.c:188: temp_val = (u16)((u32)adc * 8000 / 255);  /* 0-255 -> 0-8000 */
	mov	__mullong_PARM_2,r7
	mov	(__mullong_PARM_2 + 1),#0x00
	mov	(__mullong_PARM_2 + 2),#0x00
	mov	(__mullong_PARM_2 + 3),#0x00
	mov	dptr,#0x1f40
	clr	a
	mov	b,a
	lcall	__mullong
	mov	r4,dpl
	mov	r5,dph
	mov	r6,b
	mov	r7,a
	mov	__divulong_PARM_2,#0xff
	clr	a
	mov	(__divulong_PARM_2 + 1),a
	mov	(__divulong_PARM_2 + 2),a
	mov	(__divulong_PARM_2 + 3),a
	mov	dpl,r4
	mov	dph,r5
	mov	b,r6
	mov	a,r7
	lcall	__divulong
	mov	r4,dpl
	mov	r5,dph
	mov	_display_set_temp_PARM_2,r4
	mov	(_display_set_temp_PARM_2 + 1),r5
;	main.c:189: display_set_temp('A', temp_val, 0);  /* 显示 "A  xx.x" */
;	assignBit
	clr	_display_set_temp_PARM_3
	mov	dpl,#0x41
	ljmp	_display_set_temp
00108$:
;	main.c:191: else if (mode == 2) {
	mov	a,#0x02
	cjne	a,_mode,00110$
;	main.c:193: raw = ds18b20_read_temp();    /* 读取16位原始温度 */
	lcall	_ds18b20_read_temp
	mov	r6,dpl
	mov	r7,dph
;	main.c:196: is_negative = 0;
	mov	r5,#0x00
;	main.c:197: if (raw & 0x8000) {
	mov	a,r7
	jnb	acc.7,00104$
;	main.c:198: is_negative = 1;
	mov	r5,#0x01
;	main.c:199: raw = (~raw) + 1;         /* 二补码转绝对值 */
	mov	a,r6
	cpl	a
	mov	r3,a
	mov	a,r7
	cpl	a
	mov	r4,a
	mov	a,r5
	add	a,r3
	mov	r6,a
	clr	a
	addc	a,r4
	mov	r7,a
00104$:
;	main.c:207: temp_val = (u16)((u32)raw * 625 / 100);
	mov	__mullong_PARM_2,r6
	mov	(__mullong_PARM_2 + 1),r7
	mov	(__mullong_PARM_2 + 2),#0x00
	mov	(__mullong_PARM_2 + 3),#0x00
	mov	dptr,#0x0271
	clr	a
	mov	b,a
	push	ar5
	lcall	__mullong
	mov	r3,dpl
	mov	r4,dph
	mov	r6,b
	mov	r7,a
	mov	__divulong_PARM_2,#0x64
	clr	a
	mov	(__divulong_PARM_2 + 1),a
	mov	(__divulong_PARM_2 + 2),a
	mov	(__divulong_PARM_2 + 3),a
	mov	dpl,r3
	mov	dph,r4
	mov	b,r6
	mov	a,r7
	lcall	__divulong
	mov	r3,dpl
	mov	r4,dph
	pop	ar5
	mov	_display_set_temp_PARM_2,r3
	mov	(_display_set_temp_PARM_2 + 1),r4
;	main.c:208: display_set_temp('B', temp_val, is_negative);  /* 显示 "B  xx.x" */
;	assignBit
	mov	a,r5
	add	a,#0xff
	mov	_display_set_temp_PARM_3,c
	mov	dpl,#0x42
;	main.c:210: }
	ljmp	_display_set_temp
00110$:
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'main'
;------------------------------------------------------------
;	main.c:220: void main(void)
;	-----------------------------------------
;	 function main
;	-----------------------------------------
_main:
;	main.c:222: System_Init();                   /* 系统初始化 */
	lcall	_System_Init
;	main.c:224: while (1) {
00106$:
;	main.c:226: if (Rx_flag) {
	jnb	_Rx_flag,00102$
;	main.c:227: Proc_UART();
	lcall	_Proc_UART
00102$:
;	main.c:231: Key_Scan();
	lcall	_Key_Scan
;	main.c:234: if (step >= STEP_S5_PCF8591) {
	mov	a,#0x100 - 0x03
	add	a,_step
	jnc	00106$
;	main.c:235: Update_Display();
	lcall	_Update_Display
;	main.c:238: }
	sjmp	00106$
;------------------------------------------------------------
;Allocation info for local variables in function 'UART_ISR'
;------------------------------------------------------------
;	main.c:244: void UART_ISR(void) __interrupt(4)
;	-----------------------------------------
;	 function UART_ISR
;	-----------------------------------------
_UART_ISR:
;	main.c:246: if (RI) {
;	main.c:247: RI = 0;                      /* 清除接收中断标志 */
;	assignBit
	jbc	_RI,00115$
	sjmp	00102$
00115$:
;	main.c:248: Rx_data = SBUF;              /* 保存接收数据 */
	mov	_Rx_data,_SBUF
;	main.c:249: Rx_flag = 1;                 /* 设置接收标志 */
;	assignBit
	setb	_Rx_flag
00102$:
;	main.c:251: if (TI) {
;	main.c:252: TI = 0;                      /* 清除发送中断标志 */
;	assignBit
	jbc	_TI,00116$
	sjmp	00105$
00116$:
00105$:
;	main.c:254: }
	reti
;	eliminated unneeded mov psw,# (no regs used in bank)
;	eliminated unneeded push/pop psw
;	eliminated unneeded push/pop dpl
;	eliminated unneeded push/pop dph
;	eliminated unneeded push/pop b
;	eliminated unneeded push/pop acc
	.area CSEG    (CODE)
	.area CONST   (CODE)
	.area XINIT   (CODE)
	.area CABS    (ABS,CODE)
