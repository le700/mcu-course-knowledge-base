"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardw"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 825"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3."""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_P"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装,"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r""""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), """"
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    (""""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"),"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    (""""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"825"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile("""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    (""""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"),"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"), "DIP8/SOP8", "board1"),
]

# 芯片名别名映射，"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"), "DIP8/SOP8", "board1"),
]

# 芯片名别名映射，用于模糊匹配
_CHIP_ALIASES = {
    "8255": "825"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"), "DIP8/SOP8", "board1"),
]

# 芯片名别名映射，用于模糊匹配
_CHIP_ALIASES = {
    "8255": "8255A",
    "i8255": "8255A",
    "8255a": "8255A",
    "adc0809": "ADC0809","""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"), "DIP8/SOP8", "board1"),
]

# 芯片名别名映射，用于模糊匹配
_CHIP_ALIASES = {
    "8255": "8255A",
    "i8255": "8255A",
    "8255a": "8255A",
    "adc0809": "ADC0809",
    "adc": "ADC0809",
    "dht11": "DHT11"""
硬件参考手册结构化解析器

解析硬件参考 Markdown 文档 (hardware_ref_pa1.md)，提取芯片引脚表、
基地址、控制字、板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chip = parser.get_chip("8255")  # 模糊匹配
    results = parser.search_pin("P3.3")  # 按信号名搜索
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


# ---- 芯片名到章节标题的映射正则 ----

# 每个芯片对应的章节标题模式（正则）
_CHIP_SECTION_PATTERNS = [
    # (芯片名, 正则模式, 封装, 所属板卡)
    ("STC89C54RD+", re.compile(r"MCU\s*40脚.*引脚分配|STC89C54"), "DIP40", "board1"),
    ("ADC0809", re.compile(r"ADC0809\s*引脚表"), "DIP28", "board1"),
    ("74HC373", re.compile(r"74HC373\s*地址锁存"), "DIP20", "board1"),
    ("74HC240", re.compile(r"74HC240\s*反相驱动"), "DIP20", "board1"),
    ("74HC02", re.compile(r"74HC02\s*或非门译码"), "DIP14", "board1"),
    ("8255A", re.compile(r"8255A\s*完整引脚表"), "DIP40", "board2"),
    ("ULN2003A", re.compile(r"ULN2003A\s*引脚表"), "DIP16", "board2"),
    ("DHT11", re.compile(r"DHT11\s*引脚表"), "4Pin", "board2"),
    ("CH341T", re.compile(r"CH341T"), "SOP-16", "board1"),
    ("MAX485", re.compile(r"MAX485"), "DIP8/SOP8", "board1"),
    ("MAX708", re.compile(r"MAX708"), "DIP8/SOP8", "board1"),
]

# 芯片名别名映射，用于模糊匹配
_CHIP_ALIASES = {
    "8255": "8255A",
    "i8255": "8255A",
    "8255a": "8255A",
    "adc0809": "ADC0809",
    "adc": "ADC0809",
    "dht11": "DHT11",
    "stc89": "STC89C54RD+",
    "s