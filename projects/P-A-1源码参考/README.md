# P-A-1 Temp/Humidity Keil C51 Projects

This folder contains the small programs requested by section 6.5 for the P-A-1 temperature/humidity target board with STC89C54RD+.

## Current Status

This is the strict DHT11 diagnostic version:

- No default `C25.00` temperature.
- No fallback to a previous successful DHT11 reading.
- Checksum failure returns failure.
- No `temp_int >> 2` temperature correction.
- PA1 formal flow displays temperature only: ADC as `Axx.xx`, DHT11 as `Cxx.xx`.
- DHT11 humidity raw bytes are still read for checksum/protocol validation, but PA1 does not display or cache humidity.
- `pa1_main.hex` and the desktop strict burn-folder copy are synced.

## Recommended Burn Folder

```text
C:\Users\28011\Desktop\DHT11严格诊断_现在烧这个
```

Recommended DHT11 order:

1. `00_先烧_P33翻转_万用表测DQ.hex`
2. `01_再烧_DHT11错误码_严格.hex`
3. `02_可选_DHT11原始字节.hex`
4. `03_最后_pa1_main_严格版.hex`

## Projects

- `step03_led_half`: turn on four LEDs and turn off four LEDs.
- `step04_switch_led`: read eight switches and show their raw state on LEDs.
- `step05_display_4523`: show `45.23` on the six digit 7-segment display.
- `step06_adc_led`: read ADC0809 IN0 and show the 8-bit value on LEDs.
- `step07_adc_temp`: convert ADC0809 IN0 from 0-5 V to 0-80.00 C and show it as `Axx.xx`.
- `step09_uart_echo`: 1200 baud UART echo; received byte is also shown on LEDs.
- `pa1_main`: integrated P-A-1 flow from the task book.

## How To Build

```powershell
powershell -ExecutionPolicy Bypass -File .\build-all.ps1
```

Each project writes its HEX to:

```text
<project>\build\<project>.hex
```

## Hardware Notes

- MCU: STC89C54RD+.
- Keil target uses generic 8052-compatible `8XC52` because the code only uses standard 8051/8052 features.
- 8255 PA -> LEDs, PB -> segment bus, PC -> switches.
- DHT11 data -> `P3.3`.
- ADC0809 EOC -> `P3.2`.
- UART baud rate -> `1200`, assuming 12 MHz crystal.
- 8255 base address is `0x0480`; ADC0809 base address is `0x4000`.
