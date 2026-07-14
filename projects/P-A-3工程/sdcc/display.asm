;--------------------------------------------------------
; File Created by SDCC : free open source ANSI-C Compiler
; Version 4.0.0 #11528 (Linux)
;--------------------------------------------------------
	.module display
	.optsdcc -mmcs51 --model-small
	
;--------------------------------------------------------
; Public variables in this module
;--------------------------------------------------------
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
	.globl _display_set_temp_PARM_3
	.globl _display_set_temp_PARM_2
	.globl _scan_index
	.globl _disp_buf
	.globl _display_init
	.globl _display_scan_isr
	.globl _display_set_temp
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
_disp_buf::
	.ds 8
_scan_index::
	.ds 1
_display_set_temp_PARM_2:
	.ds 2
;--------------------------------------------------------
; overlayable items in internal ram 
;--------------------------------------------------------
	.area	OSEG    (OVR,DATA)
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
_display_set_temp_PARM_3:
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
; global & static initialisations
;--------------------------------------------------------
	.area HOME    (CODE)
	.area GSINIT  (CODE)
	.area GSFINAL (CODE)
	.area GSINIT  (CODE)
;	display.c:8: u8 scan_index = 0;
	mov	_scan_index,#0x00
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
;Allocation info for local variables in function 'Select_HC573'
;------------------------------------------------------------
;channel                   Allocated to registers r7 
;temp                      Allocated to registers r7 
;------------------------------------------------------------
;	display.c:15: static void Select_HC573(u8 channel)
;	-----------------------------------------
;	 function Select_HC573
;	-----------------------------------------
_Select_HC573:
	ar7 = 0x07
	ar6 = 0x06
	ar5 = 0x05
	ar4 = 0x04
	ar3 = 0x03
	ar2 = 0x02
	ar1 = 0x01
	ar0 = 0x00
	mov	r7,dpl
;	display.c:18: P2 = (P2 & 0x1F) | 0x00;       /* 先清空P2高3位 */
	anl	_P2,#0x1f
;	display.c:19: temp = channel << 5;             /* 通道号左移5位映射到高3位 */
	mov	a,r7
	swap	a
	rl	a
	anl	a,#0xe0
	mov	r7,a
;	display.c:20: P2 = (P2 & 0x1F) | temp;        /* 设置对应通道 */
	mov	a,_P2
	anl	a,#0x1f
	orl	a,r7
	mov	_P2,a
;	display.c:21: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'display_init'
;------------------------------------------------------------
;i                         Allocated to registers r7 
;------------------------------------------------------------
;	display.c:65: void display_init(void)
;	-----------------------------------------
;	 function display_init
;	-----------------------------------------
_display_init:
;	display.c:70: for (i = 0; i < DIGITS; i++) {
	mov	r7,#0x00
00102$:
;	display.c:71: disp_buf[i] = 0xFF;         /* 全部熄灭 */
	mov	a,r7
	add	a,#_disp_buf
	mov	r0,a
	mov	@r0,#0xff
;	display.c:70: for (i = 0; i < DIGITS; i++) {
	inc	r7
	cjne	r7,#0x08,00115$
00115$:
	jc	00102$
;	display.c:75: P0 = 0xFF;                       /* 段选全灭 */
	mov	_P0,#0xff
;	display.c:76: Select_HC573(7);                 /* 选中段选通道 */
	mov	dpl,#0x07
	lcall	_Select_HC573
;	display.c:77: Select_HC573(0);                 /* 关闭通道 */
	mov	dpl,#0x00
	lcall	_Select_HC573
;	display.c:79: P0 = 0x00;                       /* 位选全关 */
	mov	_P0,#0x00
;	display.c:80: Select_HC573(6);                 /* 选中位选通道 */
	mov	dpl,#0x06
	lcall	_Select_HC573
;	display.c:81: Select_HC573(0);                 /* 关闭通道 */
	mov	dpl,#0x00
;	display.c:82: }
	ljmp	_Select_HC573
;------------------------------------------------------------
;Allocation info for local variables in function 'display_scan_isr'
;------------------------------------------------------------
;	display.c:93: void display_scan_isr(void)
;	-----------------------------------------
;	 function display_scan_isr
;	-----------------------------------------
_display_scan_isr:
;	display.c:96: P0 = 0xFF;
	mov	_P0,#0xff
;	display.c:97: Select_HC573(7);                 /* 段选锁存 */
	mov	dpl,#0x07
	lcall	_Select_HC573
;	display.c:98: Select_HC573(0);
	mov	dpl,#0x00
	lcall	_Select_HC573
;	display.c:101: P0 = ~weixuan_table[scan_index]; /* 位选取反 (低电平有效) */
	mov	a,_scan_index
	mov	dptr,#_weixuan_table
	movc	a,@a+dptr
	cpl	a
	mov	_P0,a
;	display.c:102: Select_HC573(6);                 /* 位选锁存 */
	mov	dpl,#0x06
	lcall	_Select_HC573
;	display.c:103: Select_HC573(0);
	mov	dpl,#0x00
	lcall	_Select_HC573
;	display.c:106: P0 = disp_buf[scan_index];       /* 段码数据 */
	mov	a,_scan_index
	add	a,#_disp_buf
	mov	r1,a
	mov	_P0,@r1
;	display.c:107: Select_HC573(7);                 /* 段选锁存 */
	mov	dpl,#0x07
	lcall	_Select_HC573
;	display.c:108: Select_HC573(0);
	mov	dpl,#0x00
	lcall	_Select_HC573
;	display.c:111: scan_index++;
	inc	_scan_index
;	display.c:112: if (scan_index >= DIGITS) {
	mov	a,#0x100 - 0x08
	add	a,_scan_index
	jnc	00103$
;	display.c:113: scan_index = 0;
	mov	_scan_index,#0x00
00103$:
;	display.c:115: }
	ret
;------------------------------------------------------------
;Allocation info for local variables in function 'display_set_temp'
;------------------------------------------------------------
;temp_x100                 Allocated with name '_display_set_temp_PARM_2'
;label                     Allocated to registers r7 
;seg_idx                   Allocated to registers r7 
;------------------------------------------------------------
;	display.c:133: void display_set_temp(char label, u16 temp_x100, __bit is_negative)
;	-----------------------------------------
;	 function display_set_temp
;	-----------------------------------------
_display_set_temp:
	mov	r7,dpl
;	display.c:138: if (label == 'A') {
	cjne	r7,#0x41,00102$
;	display.c:139: seg_idx = 10;                /* seg_table[10] = 'A' */
	mov	r7,#0x0a
	sjmp	00103$
00102$:
;	display.c:141: seg_idx = 11;                /* seg_table[11] = 'b' */
	mov	r7,#0x0b
00103$:
;	display.c:145: if (temp_x100 > 9999) {
	clr	c
	mov	a,#0x0f
	subb	a,_display_set_temp_PARM_2
	mov	a,#0x27
	subb	a,(_display_set_temp_PARM_2 + 1)
	jnc	00105$
;	display.c:146: temp_x100 = 9999;
	mov	_display_set_temp_PARM_2,#0x0f
	mov	(_display_set_temp_PARM_2 + 1),#0x27
00105$:
;	display.c:149: disp_buf[0] = seg_table[seg_idx];              /* 标签 A/B */
	mov	a,r7
	mov	dptr,#_seg_table
	movc	a,@a+dptr
	mov	r7,a
	mov	_disp_buf,r7
;	display.c:150: disp_buf[1] = is_negative ? seg_table[12] : 0xFF; /* 负号或空白 */
	jnb	_display_set_temp_PARM_3,00108$
	mov	dptr,#(_seg_table + 0x000c)
	clr	a
	movc	a,@a+dptr
	mov	r6,a
	mov	r7,#0x00
	sjmp	00109$
00108$:
	mov	r6,#0xff
	mov	r7,#0x00
00109$:
	mov	(_disp_buf + 0x0001),r6
;	display.c:151: disp_buf[2] = 0xFF;                            /* 空白 */
	mov	(_disp_buf + 0x0002),#0xff
;	display.c:152: disp_buf[3] = 0xFF;                            /* 空白 */
	mov	(_disp_buf + 0x0003),#0xff
;	display.c:153: disp_buf[4] = seg_table[temp_x100 / 1000];     /* 十位 */
	mov	__divuint_PARM_2,#0xe8
	mov	(__divuint_PARM_2 + 1),#0x03
	mov	dpl,_display_set_temp_PARM_2
	mov	dph,(_display_set_temp_PARM_2 + 1)
	lcall	__divuint
	mov	r6,dpl
	mov	r7,dph
	mov	a,r6
	add	a,#_seg_table
	mov	dpl,a
	mov	a,r7
	addc	a,#(_seg_table >> 8)
	mov	dph,a
	clr	a
	movc	a,@a+dptr
	mov	r7,a
	mov	(_disp_buf + 0x0004),r7
;	display.c:154: disp_buf[5] = seg_table[temp_x100 / 100 % 10] & 0x7F;  /* 个位+小数点 */
	mov	__divuint_PARM_2,#0x64
	mov	(__divuint_PARM_2 + 1),#0x00
	mov	dpl,_display_set_temp_PARM_2
	mov	dph,(_display_set_temp_PARM_2 + 1)
	lcall	__divuint
	mov	__moduint_PARM_2,#0x0a
	mov	(__moduint_PARM_2 + 1),#0x00
	lcall	__moduint
	mov	r6,dpl
	mov	r7,dph
	mov	a,r6
	add	a,#_seg_table
	mov	dpl,a
	mov	a,r7
	addc	a,#(_seg_table >> 8)
	mov	dph,a
	clr	a
	movc	a,@a+dptr
	mov	r7,a
	mov	a,#0x7f
	anl	a,r7
	mov	(_disp_buf + 0x0005),a
;	display.c:155: disp_buf[6] = seg_table[temp_x100 / 10 % 10];  /* 小数第一位 */
	mov	__divuint_PARM_2,#0x0a
	mov	(__divuint_PARM_2 + 1),#0x00
	mov	dpl,_display_set_temp_PARM_2
	mov	dph,(_display_set_temp_PARM_2 + 1)
	lcall	__divuint
	mov	__moduint_PARM_2,#0x0a
	mov	(__moduint_PARM_2 + 1),#0x00
	lcall	__moduint
	mov	r6,dpl
	mov	r7,dph
	mov	a,r6
	add	a,#_seg_table
	mov	dpl,a
	mov	a,r7
	addc	a,#(_seg_table >> 8)
	mov	dph,a
	clr	a
	movc	a,@a+dptr
	mov	r7,a
	mov	(_disp_buf + 0x0006),r7
;	display.c:156: disp_buf[7] = seg_table[temp_x100 % 10];       /* 小数第二位 */
	mov	__moduint_PARM_2,#0x0a
	mov	(__moduint_PARM_2 + 1),#0x00
	mov	dpl,_display_set_temp_PARM_2
	mov	dph,(_display_set_temp_PARM_2 + 1)
	lcall	__moduint
	mov	r6,dpl
	mov	r7,dph
	mov	a,r6
	add	a,#_seg_table
	mov	dpl,a
	mov	a,r7
	addc	a,#(_seg_table >> 8)
	mov	dph,a
	clr	a
	movc	a,@a+dptr
	mov	r7,a
	mov	(_disp_buf + 0x0007),r7
;	display.c:157: }
	ret
	.area CSEG    (CODE)
	.area CONST   (CODE)
_seg_table:
	.db #0xc0	; 192
	.db #0xf9	; 249
	.db #0xa4	; 164
	.db #0xb0	; 176
	.db #0x99	; 153
	.db #0x92	; 146
	.db #0x82	; 130
	.db #0xf8	; 248
	.db #0x80	; 128
	.db #0x90	; 144
	.db #0x88	; 136
	.db #0x83	; 131
	.db #0xbf	; 191
	.db #0xff	; 255
_weixuan_table:
	.db #0x01	; 1
	.db #0x02	; 2
	.db #0x04	; 4
	.db #0x08	; 8
	.db #0x10	; 16
	.db #0x20	; 32
	.db #0x40	; 64
	.db #0x80	; 128
	.area XINIT   (CODE)
	.area CABS    (ABS,CODE)
