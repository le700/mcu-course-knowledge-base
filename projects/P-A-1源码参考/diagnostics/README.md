# P-A-1 LED Diagnostic HEX Files

Use these only to identify the real LED control path on the target board.
Burn one HEX at a time with STC-ISP.

## Test Order

1. `diag_8255_0480_chase.hex`
   - Uses 8255 base address `0x0480`.
   - If one LED moves repeatedly, 8255 external MOVX access is confirmed.

2. `diag_8255_0480_0f.hex`
   - Same address as above, writes PA=`0x0F`.
   - If this shows stable four LEDs on and four LEDs off, burn `step03_led_half.hex`.

3. `diag_8255_0080_0f.hex`
   - Uses 8255 base address `0x0080`, writes PA=`0x0F`.
   - Kept only as a fallback comparison; STC89C54RD+ may map this low MOVX address to internal XRAM.

4. `diag_8255_0080_f0.hex`
   - Same address as above, writes PA=`0xF0`.
   - If this is the opposite four LEDs from test 3, the address is correct.

5. `diag_8255_0080_chase.hex`
   - Same address, one LED moves repeatedly.
   - If this runs normally, 8255 LED output is confirmed.

6. `diag_p2_0f.hex`
   - Last-resort test only.
   - If this shows stable four LEDs on and four LEDs off, LED may be directly on P2 instead of 8255 PA.

Report exactly which file produced a stable expected phenomenon.
