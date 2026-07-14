# SDCC Makefile for P-A-3# Temperature Recorder
# MCU: IAP15F2K61S2 (8052 compatible)
# Compiler: SDCC 4.0.0

CC = sdcc
CFLAGS = -mmcs51 --std-sdcc99
TARGET = pa3

# Source files
SRCS = delay.c display.c led.c uart.c pcf8591.c ds18b20.c main.c
OBJS = $(SRCS:.c=.rel)

# Default target
all: $(TARGET).ihx

# Compile each .c to .rel
%.rel: %.c
	$(CC) -c $(CFLAGS) -I. $<

# Link all .rel to .ihx
$(TARGET).ihx: $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET).ihx $(OBJS)

# Clean build artifacts
clean:
	rm -f *.rel *.ihx *.hex *.lk *.lst *.map *.mem *.rst *.sym *.asm

.PHONY: all clean