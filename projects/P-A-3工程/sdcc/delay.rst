                                      1 ;--------------------------------------------------------
                                      2 ; File Created by SDCC : free open source ANSI-C Compiler
                                      3 ; Version 4.0.0 #11528 (Linux)
                                      4 ;--------------------------------------------------------
                                      5 	.module delay
                                      6 	.optsdcc -mmcs51 --model-small
                                      7 	
                                      8 ;--------------------------------------------------------
                                      9 ; Public variables in this module
                                     10 ;--------------------------------------------------------
                                     11 	.globl _S6
                                     12 	.globl _S5
                                     13 	.globl _S4
                                     14 	.globl _DQ
                                     15 	.globl _SCL
                                     16 	.globl _SDA
                                     17 	.globl _TF2
                                     18 	.globl _EXF2
                                     19 	.globl _RCLK
                                     20 	.globl _TCLK
                                     21 	.globl _EXEN2
                                     22 	.globl _TR2
                                     23 	.globl _C_T2
                                     24 	.globl _CP_RL2
                                     25 	.globl _T2CON_7
                                     26 	.globl _T2CON_6
                                     27 	.globl _T2CON_5
                                     28 	.globl _T2CON_4
                                     29 	.globl _T2CON_3
                                     30 	.globl _T2CON_2
                                     31 	.globl _T2CON_1
                                     32 	.globl _T2CON_0
                                     33 	.globl _PT2
                                     34 	.globl _ET2
                                     35 	.globl _CY
                                     36 	.globl _AC
                                     37 	.globl _F0
                                     38 	.globl _RS1
                                     39 	.globl _RS0
                                     40 	.globl _OV
                                     41 	.globl _F1
                                     42 	.globl _P
                                     43 	.globl _PS
                                     44 	.globl _PT1
                                     45 	.globl _PX1
                                     46 	.globl _PT0
                                     47 	.globl _PX0
                                     48 	.globl _RD
                                     49 	.globl _WR
                                     50 	.globl _T1
                                     51 	.globl _T0
                                     52 	.globl _INT1
                                     53 	.globl _INT0
                                     54 	.globl _TXD
                                     55 	.globl _RXD
                                     56 	.globl _P3_7
                                     57 	.globl _P3_6
                                     58 	.globl _P3_5
                                     59 	.globl _P3_4
                                     60 	.globl _P3_3
                                     61 	.globl _P3_2
                                     62 	.globl _P3_1
                                     63 	.globl _P3_0
                                     64 	.globl _EA
                                     65 	.globl _ES
                                     66 	.globl _ET1
                                     67 	.globl _EX1
                                     68 	.globl _ET0
                                     69 	.globl _EX0
                                     70 	.globl _P2_7
                                     71 	.globl _P2_6
                                     72 	.globl _P2_5
                                     73 	.globl _P2_4
                                     74 	.globl _P2_3
                                     75 	.globl _P2_2
                                     76 	.globl _P2_1
                                     77 	.globl _P2_0
                                     78 	.globl _SM0
                                     79 	.globl _SM1
                                     80 	.globl _SM2
                                     81 	.globl _REN
                                     82 	.globl _TB8
                                     83 	.globl _RB8
                                     84 	.globl _TI
                                     85 	.globl _RI
                                     86 	.globl _P1_7
                                     87 	.globl _P1_6
                                     88 	.globl _P1_5
                                     89 	.globl _P1_4
                                     90 	.globl _P1_3
                                     91 	.globl _P1_2
                                     92 	.globl _P1_1
                                     93 	.globl _P1_0
                                     94 	.globl _TF1
                                     95 	.globl _TR1
                                     96 	.globl _TF0
                                     97 	.globl _TR0
                                     98 	.globl _IE1
                                     99 	.globl _IT1
                                    100 	.globl _IE0
                                    101 	.globl _IT0
                                    102 	.globl _P0_7
                                    103 	.globl _P0_6
                                    104 	.globl _P0_5
                                    105 	.globl _P0_4
                                    106 	.globl _P0_3
                                    107 	.globl _P0_2
                                    108 	.globl _P0_1
                                    109 	.globl _P0_0
                                    110 	.globl _T2L
                                    111 	.globl _T2H
                                    112 	.globl _AUXR
                                    113 	.globl _TH2
                                    114 	.globl _TL2
                                    115 	.globl _RCAP2H
                                    116 	.globl _RCAP2L
                                    117 	.globl _T2CON
                                    118 	.globl _B
                                    119 	.globl _ACC
                                    120 	.globl _PSW
                                    121 	.globl _IP
                                    122 	.globl _P3
                                    123 	.globl _IE
                                    124 	.globl _P2
                                    125 	.globl _SBUF
                                    126 	.globl _SCON
                                    127 	.globl _P1
                                    128 	.globl _TH1
                                    129 	.globl _TH0
                                    130 	.globl _TL1
                                    131 	.globl _TL0
                                    132 	.globl _TMOD
                                    133 	.globl _TCON
                                    134 	.globl _PCON
                                    135 	.globl _DPH
                                    136 	.globl _DPL
                                    137 	.globl _SP
                                    138 	.globl _P0
                                    139 	.globl _delay_us
                                    140 	.globl _delay_ms
                                    141 ;--------------------------------------------------------
                                    142 ; special function registers
                                    143 ;--------------------------------------------------------
                                    144 	.area RSEG    (ABS,DATA)
      000000                        145 	.org 0x0000
                           000080   146 _P0	=	0x0080
                           000081   147 _SP	=	0x0081
                           000082   148 _DPL	=	0x0082
                           000083   149 _DPH	=	0x0083
                           000087   150 _PCON	=	0x0087
                           000088   151 _TCON	=	0x0088
                           000089   152 _TMOD	=	0x0089
                           00008A   153 _TL0	=	0x008a
                           00008B   154 _TL1	=	0x008b
                           00008C   155 _TH0	=	0x008c
                           00008D   156 _TH1	=	0x008d
                           000090   157 _P1	=	0x0090
                           000098   158 _SCON	=	0x0098
                           000099   159 _SBUF	=	0x0099
                           0000A0   160 _P2	=	0x00a0
                           0000A8   161 _IE	=	0x00a8
                           0000B0   162 _P3	=	0x00b0
                           0000B8   163 _IP	=	0x00b8
                           0000D0   164 _PSW	=	0x00d0
                           0000E0   165 _ACC	=	0x00e0
                           0000F0   166 _B	=	0x00f0
                           0000C8   167 _T2CON	=	0x00c8
                           0000CA   168 _RCAP2L	=	0x00ca
                           0000CB   169 _RCAP2H	=	0x00cb
                           0000CC   170 _TL2	=	0x00cc
                           0000CD   171 _TH2	=	0x00cd
                           00008E   172 _AUXR	=	0x008e
                           0000D6   173 _T2H	=	0x00d6
                           0000D7   174 _T2L	=	0x00d7
                                    175 ;--------------------------------------------------------
                                    176 ; special function bits
                                    177 ;--------------------------------------------------------
                                    178 	.area RSEG    (ABS,DATA)
      000000                        179 	.org 0x0000
                           000080   180 _P0_0	=	0x0080
                           000081   181 _P0_1	=	0x0081
                           000082   182 _P0_2	=	0x0082
                           000083   183 _P0_3	=	0x0083
                           000084   184 _P0_4	=	0x0084
                           000085   185 _P0_5	=	0x0085
                           000086   186 _P0_6	=	0x0086
                           000087   187 _P0_7	=	0x0087
                           000088   188 _IT0	=	0x0088
                           000089   189 _IE0	=	0x0089
                           00008A   190 _IT1	=	0x008a
                           00008B   191 _IE1	=	0x008b
                           00008C   192 _TR0	=	0x008c
                           00008D   193 _TF0	=	0x008d
                           00008E   194 _TR1	=	0x008e
                           00008F   195 _TF1	=	0x008f
                           000090   196 _P1_0	=	0x0090
                           000091   197 _P1_1	=	0x0091
                           000092   198 _P1_2	=	0x0092
                           000093   199 _P1_3	=	0x0093
                           000094   200 _P1_4	=	0x0094
                           000095   201 _P1_5	=	0x0095
                           000096   202 _P1_6	=	0x0096
                           000097   203 _P1_7	=	0x0097
                           000098   204 _RI	=	0x0098
                           000099   205 _TI	=	0x0099
                           00009A   206 _RB8	=	0x009a
                           00009B   207 _TB8	=	0x009b
                           00009C   208 _REN	=	0x009c
                           00009D   209 _SM2	=	0x009d
                           00009E   210 _SM1	=	0x009e
                           00009F   211 _SM0	=	0x009f
                           0000A0   212 _P2_0	=	0x00a0
                           0000A1   213 _P2_1	=	0x00a1
                           0000A2   214 _P2_2	=	0x00a2
                           0000A3   215 _P2_3	=	0x00a3
                           0000A4   216 _P2_4	=	0x00a4
                           0000A5   217 _P2_5	=	0x00a5
                           0000A6   218 _P2_6	=	0x00a6
                           0000A7   219 _P2_7	=	0x00a7
                           0000A8   220 _EX0	=	0x00a8
                           0000A9   221 _ET0	=	0x00a9
                           0000AA   222 _EX1	=	0x00aa
                           0000AB   223 _ET1	=	0x00ab
                           0000AC   224 _ES	=	0x00ac
                           0000AF   225 _EA	=	0x00af
                           0000B0   226 _P3_0	=	0x00b0
                           0000B1   227 _P3_1	=	0x00b1
                           0000B2   228 _P3_2	=	0x00b2
                           0000B3   229 _P3_3	=	0x00b3
                           0000B4   230 _P3_4	=	0x00b4
                           0000B5   231 _P3_5	=	0x00b5
                           0000B6   232 _P3_6	=	0x00b6
                           0000B7   233 _P3_7	=	0x00b7
                           0000B0   234 _RXD	=	0x00b0
                           0000B1   235 _TXD	=	0x00b1
                           0000B2   236 _INT0	=	0x00b2
                           0000B3   237 _INT1	=	0x00b3
                           0000B4   238 _T0	=	0x00b4
                           0000B5   239 _T1	=	0x00b5
                           0000B6   240 _WR	=	0x00b6
                           0000B7   241 _RD	=	0x00b7
                           0000B8   242 _PX0	=	0x00b8
                           0000B9   243 _PT0	=	0x00b9
                           0000BA   244 _PX1	=	0x00ba
                           0000BB   245 _PT1	=	0x00bb
                           0000BC   246 _PS	=	0x00bc
                           0000D0   247 _P	=	0x00d0
                           0000D1   248 _F1	=	0x00d1
                           0000D2   249 _OV	=	0x00d2
                           0000D3   250 _RS0	=	0x00d3
                           0000D4   251 _RS1	=	0x00d4
                           0000D5   252 _F0	=	0x00d5
                           0000D6   253 _AC	=	0x00d6
                           0000D7   254 _CY	=	0x00d7
                           0000AD   255 _ET2	=	0x00ad
                           0000BD   256 _PT2	=	0x00bd
                           0000C8   257 _T2CON_0	=	0x00c8
                           0000C9   258 _T2CON_1	=	0x00c9
                           0000CA   259 _T2CON_2	=	0x00ca
                           0000CB   260 _T2CON_3	=	0x00cb
                           0000CC   261 _T2CON_4	=	0x00cc
                           0000CD   262 _T2CON_5	=	0x00cd
                           0000CE   263 _T2CON_6	=	0x00ce
                           0000CF   264 _T2CON_7	=	0x00cf
                           0000C8   265 _CP_RL2	=	0x00c8
                           0000C9   266 _C_T2	=	0x00c9
                           0000CA   267 _TR2	=	0x00ca
                           0000CB   268 _EXEN2	=	0x00cb
                           0000CC   269 _TCLK	=	0x00cc
                           0000CD   270 _RCLK	=	0x00cd
                           0000CE   271 _EXF2	=	0x00ce
                           0000CF   272 _TF2	=	0x00cf
                           0000A1   273 _SDA	=	0x00a1
                           0000A0   274 _SCL	=	0x00a0
                           000094   275 _DQ	=	0x0094
                           0000B3   276 _S4	=	0x00b3
                           0000B2   277 _S5	=	0x00b2
                           0000B1   278 _S6	=	0x00b1
                                    279 ;--------------------------------------------------------
                                    280 ; overlayable register banks
                                    281 ;--------------------------------------------------------
                                    282 	.area REG_BANK_0	(REL,OVR,DATA)
      000000                        283 	.ds 8
                                    284 ;--------------------------------------------------------
                                    285 ; internal ram data
                                    286 ;--------------------------------------------------------
                                    287 	.area DSEG    (DATA)
                                    288 ;--------------------------------------------------------
                                    289 ; overlayable items in internal ram 
                                    290 ;--------------------------------------------------------
                                    291 	.area	OSEG    (OVR,DATA)
                                    292 	.area	OSEG    (OVR,DATA)
                                    293 ;--------------------------------------------------------
                                    294 ; indirectly addressable internal ram data
                                    295 ;--------------------------------------------------------
                                    296 	.area ISEG    (DATA)
                                    297 ;--------------------------------------------------------
                                    298 ; absolute internal ram data
                                    299 ;--------------------------------------------------------
                                    300 	.area IABS    (ABS,DATA)
                                    301 	.area IABS    (ABS,DATA)
                                    302 ;--------------------------------------------------------
                                    303 ; bit data
                                    304 ;--------------------------------------------------------
                                    305 	.area BSEG    (BIT)
                                    306 ;--------------------------------------------------------
                                    307 ; paged external ram data
                                    308 ;--------------------------------------------------------
                                    309 	.area PSEG    (PAG,XDATA)
                                    310 ;--------------------------------------------------------
                                    311 ; external ram data
                                    312 ;--------------------------------------------------------
                                    313 	.area XSEG    (XDATA)
                                    314 ;--------------------------------------------------------
                                    315 ; absolute external ram data
                                    316 ;--------------------------------------------------------
                                    317 	.area XABS    (ABS,XDATA)
                                    318 ;--------------------------------------------------------
                                    319 ; external initialized ram data
                                    320 ;--------------------------------------------------------
                                    321 	.area XISEG   (XDATA)
                                    322 	.area HOME    (CODE)
                                    323 	.area GSINIT0 (CODE)
                                    324 	.area GSINIT1 (CODE)
                                    325 	.area GSINIT2 (CODE)
                                    326 	.area GSINIT3 (CODE)
                                    327 	.area GSINIT4 (CODE)
                                    328 	.area GSINIT5 (CODE)
                                    329 	.area GSINIT  (CODE)
                                    330 	.area GSFINAL (CODE)
                                    331 	.area CSEG    (CODE)
                                    332 ;--------------------------------------------------------
                                    333 ; global & static initialisations
                                    334 ;--------------------------------------------------------
                                    335 	.area HOME    (CODE)
                                    336 	.area GSINIT  (CODE)
                                    337 	.area GSFINAL (CODE)
                                    338 	.area GSINIT  (CODE)
                                    339 ;--------------------------------------------------------
                                    340 ; Home
                                    341 ;--------------------------------------------------------
                                    342 	.area HOME    (CODE)
                                    343 	.area HOME    (CODE)
                                    344 ;--------------------------------------------------------
                                    345 ; code
                                    346 ;--------------------------------------------------------
                                    347 	.area CSEG    (CODE)
                                    348 ;------------------------------------------------------------
                                    349 ;Allocation info for local variables in function 'delay_us'
                                    350 ;------------------------------------------------------------
                                    351 ;us                        Allocated to registers 
                                    352 ;------------------------------------------------------------
                                    353 ;	delay.c:7: void delay_us(u16 us)
                                    354 ;	-----------------------------------------
                                    355 ;	 function delay_us
                                    356 ;	-----------------------------------------
      000097                        357 _delay_us:
                           000007   358 	ar7 = 0x07
                           000006   359 	ar6 = 0x06
                           000005   360 	ar5 = 0x05
                           000004   361 	ar4 = 0x04
                           000003   362 	ar3 = 0x03
                           000002   363 	ar2 = 0x02
                           000001   364 	ar1 = 0x01
                           000000   365 	ar0 = 0x00
      000097 AE 82            [24]  366 	mov	r6,dpl
      000099 AF 83            [24]  367 	mov	r7,dph
                                    368 ;	delay.c:9: while (us != 0) {
      00009B                        369 00101$:
      00009B EE               [12]  370 	mov	a,r6
      00009C 4F               [12]  371 	orl	a,r7
      00009D 60 09            [24]  372 	jz	00104$
                                    373 ;	delay.c:10: __asm__("nop");
      00009F 00               [12]  374 	nop
                                    375 ;	delay.c:11: __asm__("nop");
      0000A0 00               [12]  376 	nop
                                    377 ;	delay.c:12: us--;
      0000A1 1E               [12]  378 	dec	r6
      0000A2 BE FF 01         [24]  379 	cjne	r6,#0xff,00116$
      0000A5 1F               [12]  380 	dec	r7
      0000A6                        381 00116$:
      0000A6 80 F3            [24]  382 	sjmp	00101$
      0000A8                        383 00104$:
                                    384 ;	delay.c:14: }
      0000A8 22               [24]  385 	ret
                                    386 ;------------------------------------------------------------
                                    387 ;Allocation info for local variables in function 'delay_ms'
                                    388 ;------------------------------------------------------------
                                    389 ;ms                        Allocated to registers 
                                    390 ;i                         Allocated to registers r4 r5 
                                    391 ;------------------------------------------------------------
                                    392 ;	delay.c:20: void delay_ms(u16 ms)
                                    393 ;	-----------------------------------------
                                    394 ;	 function delay_ms
                                    395 ;	-----------------------------------------
      0000A9                        396 _delay_ms:
      0000A9 AE 82            [24]  397 	mov	r6,dpl
      0000AB AF 83            [24]  398 	mov	r7,dph
                                    399 ;	delay.c:24: while (ms != 0) {
      0000AD                        400 00102$:
      0000AD EE               [12]  401 	mov	a,r6
      0000AE 4F               [12]  402 	orl	a,r7
      0000AF 60 1C            [24]  403 	jz	00108$
                                    404 ;	delay.c:25: for (i = 0; i < 115; i++) {
      0000B1 7C 73            [12]  405 	mov	r4,#0x73
      0000B3 7D 00            [12]  406 	mov	r5,#0x00
      0000B5                        407 00107$:
                                    408 ;	delay.c:26: __asm__("nop");
      0000B5 00               [12]  409 	nop
      0000B6 EC               [12]  410 	mov	a,r4
      0000B7 24 FF            [12]  411 	add	a,#0xff
      0000B9 FA               [12]  412 	mov	r2,a
      0000BA ED               [12]  413 	mov	a,r5
      0000BB 34 FF            [12]  414 	addc	a,#0xff
      0000BD FB               [12]  415 	mov	r3,a
      0000BE 8A 04            [24]  416 	mov	ar4,r2
      0000C0 8B 05            [24]  417 	mov	ar5,r3
                                    418 ;	delay.c:25: for (i = 0; i < 115; i++) {
      0000C2 EA               [12]  419 	mov	a,r2
      0000C3 4B               [12]  420 	orl	a,r3
      0000C4 70 EF            [24]  421 	jnz	00107$
                                    422 ;	delay.c:28: ms--;
      0000C6 1E               [12]  423 	dec	r6
      0000C7 BE FF 01         [24]  424 	cjne	r6,#0xff,00129$
      0000CA 1F               [12]  425 	dec	r7
      0000CB                        426 00129$:
      0000CB 80 E0            [24]  427 	sjmp	00102$
      0000CD                        428 00108$:
                                    429 ;	delay.c:30: }
      0000CD 22               [24]  430 	ret
                                    431 	.area CSEG    (CODE)
                                    432 	.area CONST   (CODE)
                                    433 	.area XINIT   (CODE)
                                    434 	.area CABS    (ABS,CODE)
