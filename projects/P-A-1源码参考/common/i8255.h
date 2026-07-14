#ifndef I8255_H
#define I8255_H

#include "board.h"

void i8255_init(void);
u8 du_kaiguan(void);
u8 switch_read_raw(void);
u8 switch_read_logic(void);

#endif
