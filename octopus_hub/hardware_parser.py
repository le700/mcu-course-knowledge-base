"""
P-A-1# 硬件参考手册解析器

解析 hardware_ref_pa1.md，提取芯片引脚表、基地址、控制字、
板卡互联关系等结构化数据。

支持的芯片类型:
  - STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02
  - ULN2003A, DHT11, CH341T, MAX485, MAX708

使用示例:
    parser = HardwareRefParser("/workspace/rag_v4/hardware_ref_pa1.md")
    chips = parser.get_chip_list()
    pinout = parser.get_pinout("ADC0809")
    quick = parser.get_quick_reference()
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple


class HardwareRefParser:
    """P-A-1# 硬件参考手册解析器

    解析 Markdown 格式的硬件参考文档，提取芯片引脚表、地址映射、
    板卡架构等结构化数据。
    """

    # ---- 芯片定义 ----
    # (芯片名, 型号, 封装, 所属板卡, 关键参数, 描述)
    _CHIP_DEFS = [
        ("STC89C54RD+", "STC89C54RD+", "DIP40", "board1",
         {"晶振": "12MHz", "ROM": "16KB", "RAM": "1280B", "工作电压": "5V"},
         "8051内核MCU，40脚完整引脚分配"),
        ("8255A", "8255A", "DIP40", "board2",
         {"基地址": "0x0480", "控制字": "0x89", "PA口": "0x0480", "PB口": "0x0481", "PC口": "0x0482", "控制口": "0x0483"},
         "可编程并行接口芯片，PA口方式0输出、PB口方式0输出、PC口高4位输入低4位输出"),
        ("ADC0809", "ADC0809", "DIP28", "board1",
         {"基地址": "0x4000", "通道数": "8", "分辨率": "8位", "时钟": "2MHz (ALE分频)"},
         "8位8通道模数转换器，IN0接温度传感器DW1，IN1接湿度传感器DWQ"),
        ("74HC373", "74HC373", "DIP20", "board1",
         {"功能": "地址锁存", "使能": "/OE=GND常使能"},
         "8位D型锁存器，ALE控制LE，锁存P0口低8位地址"),
        ("74HC240", "74HC240", "DIP20", "board1",
         {"功能": "反相驱动", "使能": "/1G=/2G=GND常使能"},
         "8路反相缓冲器，P0口段码经反相驱动数码管段"),
        ("74HC02", "74HC02", "DIP14", "board1",
         {"功能": "或非门译码", "U8A": "ADC写选通", "U8B": "ADC读选通"},
         "四路2输入或非门，用于ADC0809地址译码"),
        ("ULN2003A", "ULN2003A", "DIP16", "board2",
         {"功能": "位选驱动", "通道数": "7", "驱动方式": "灌电流"},
         "7路达林顿阵列，P1.0-P1.5位选信号经ULN2003A驱动共阴数码管位选"),
        ("DHT11", "DHT11", "4Pin", "board2",
         {"协议": "单总线", "数据位": "40位", "上拉电阻": "4.7KΩ", "引脚": "P3.3"},
         "数字温湿度传感器，单总线通信，40位数据(湿度+温度+校验)"),
        ("CH341T", "CH341T", "SOP-16", "board1",
         {"晶振": "12MHz", "功能": "USB转串口", "接口": "经S9跳线选择"},
         "USB转串口芯片，12MHz独立晶振，TXD/RXD经S9跳线连接MCU"),
        ("MAX485", "MAX485", "DIP8/SOP8", "board1",
         {"功能": "RS485收发器", "终端电阻": "120Ω", "接口": "经S9跳线选择"},
         "RS485收发器，A/B差分信号，120Ω终端电阻R4"),
        ("MAX708", "MAX708", "DIP8/SOP8", "board1",
         {"功能": "复位监控", "复位电平": "低电平有效", "手动复位": "KRS1按键"},
         "微处理器复位监控芯片，/MR接手动复位按键KRS1，RST输出接MCU RST脚"),
    ]

    # 芯片别名映射
    _CHIP_ALIASES = {
        "8255": "8255A", "i8255": "8255A", "8255a": "8255A",
        "adc0809": "ADC0809", "adc": "ADC0809",
        "dht11": "DHT11", "stc89": "STC89C54RD+", "stc": "STC89C54RD+",
        "uln2003": "ULN2003A", "uln": "ULN2003A",
        "74hc373": "74HC373", "74hc240": "74HC240", "74hc02": "74HC02",
        "ch341": "CH341T", "ch341t": "CH341T",
        "max485": "MAX485", "max708": "MAX708",
        "373": "74HC373", "240": "74HC240", "02": "74HC02",
    }

    def __init__(self, ref_path: str = "/workspace/rag_v4/hardware_ref_pa1.md"):
        """加载硬件参考文件

        Args:
            ref_path: 硬件参考 Markdown 文件路径
        """
        self.ref_path = ref_path
        self.content = ""
        self._loaded = False
        self._load()

    def _load(self):
        """加载 Markdown 文件内容"""
        if os.path.exists(self.ref_path):
            with open(self.ref_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self._loaded = True
        else:
            self._loaded = False

    @property
    def is_loaded(self) -> bool:
        """是否已成功加载硬件参考文档"""
        return self._loaded

    # ==================== 芯片列表 ====================

    def get_chip_list(self) -> List[dict]:
        """返回所有芯片列表

        解析 Markdown 中的芯片定义，返回芯片名、型号、封装、关键参数等信息。

        Returns:
            [{name, model, package, board, key_params, description, pins_count}, ...]
            覆盖：STC89C54RD+, 8255A, ADC0809, 74HC373, 74HC240, 74HC02,
                  ULN2003A, DHT11, CH341T, MAX485, MAX708
        """
        results = []
        for name, model, package, board, key_params, description in self._CHIP_DEFS:
            pinout = self.get_pinout(name)
            pins_count = pinout.get("total_pins", 0) if pinout and "error" not in pinout else 0
            results.append({
                "name": name,
                "model": model,
                "package": package,
                "board": board,
                "key_params": key_params,
                "description": description,
                "pins_count": pins_count,
            })
        return results

    # ==================== 引脚解析 ====================

    def _resolve_chip_name(self, chip_name: str) -> Optional[str]:
        """解析芯片名称，支持别名和模糊匹配

        Args:
            chip_name: 用户输入的芯片名称

        Returns:
            规范化后的芯片名称，未找到返回 None
        """
        # 直接匹配
        for name, _, _, _, _, _ in self._CHIP_DEFS:
            if chip_name.upper() == name.upper():
                return name

        # 别名匹配
        key = chip_name.lower().replace(" ", "").replace("-", "").replace("_", "")
        if key in self._CHIP_ALIASES:
            return self._CHIP_ALIASES[key]

        # 部分匹配（芯片名包含用户输入，或用户输入包含芯片名）
        key_lower = chip_name.lower()
        for name, _, _, _, _, _ in self._CHIP_DEFS:
            name_lower = name.lower()
            if key_lower in name_lower or name_lower in key_lower:
                return name

        return None

    def _find_section_for_chip(self, chip_name: str) -> Optional[Tuple[int, int]]:
        """在 Markdown 中找到芯片对应章节的行范围

        Args:
            chip_name: 规范化后的芯片名称

        Returns:
            (start_line, end_line) 或 None
        """
        if not self._loaded:
            return None

        lines = self.content.split('\n')

        # 各芯片对应的章节标题正则（使用 ### 前缀避免匹配到架构总览表）
        chip_patterns = {
            "STC89C54RD+": r"###\s+2\.1\s+MCU\s*40脚.*引脚分配",
            "ADC0809": r"###\s+2\.3\s+ADC0809\s*引脚表",
            "74HC373": r"###\s+2\.4\s+74HC373\s*地址锁存",
            "74HC240": r"###\s+2\.5\s+74HC240\s*反相驱动",
            "74HC02": r"###\s+2\.6\s+74HC02\s*或非门译码",
            "8255A": r"###\s+3\.1\s+8255A\s*完整引脚表",
            "ULN2003A": r"###\s+3\.3\s+ULN2003A\s*引脚表",
            "DHT11": r"###\s+3\.5\s+DHT11\s*引脚表",
            "CH341T": r"###\s+2\.10\s+串口电路",
            "MAX485": r"###\s+2\.10\s+串口电路",
            "MAX708": r"###\s+2\.2\s+晶振与复位",
        }

        pattern = chip_patterns.get(chip_name)
        if not pattern:
            return None

        section_start = None
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                section_start = i
                break

        if section_start is None:
            return None

        # 找到下一个同级或更高级标题作为结束
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith('###') or stripped.startswith('##'):
                section_end = i
                break

        return (section_start, section_end)

    def _parse_pin_table(self, section_lines: List[str]) -> List[dict]:
        """解析引脚表格

        Args:
            section_lines: 章节文本行列表

        Returns:
            引脚列表 [{pin_num, pin_name, function, connect_to}, ...]
        """
        pins = []
        in_table = False
        header_cols = []

        for line in section_lines:
            stripped = line.strip()

            # 检测表格行
            if stripped.startswith('|') and stripped.endswith('|'):
                # 跳过分隔行
                if re.match(r'^\|[\s\-:]+\|[\s\-:]+\|', stripped):
                    continue

                cells = [c.strip() for c in stripped.strip('|').split('|')]

                if not in_table:
                    # 表头行
                    in_table = True
                    header_cols = cells
                    continue

                if len(cells) < 2:
                    continue

                # 尝试解析引脚号
                pin_num = None
                pin_name = ""
                function = ""
                connect_to = ""

                if len(cells) >= 4:
                    # 脚号 | 名称 | 连接 | 功能
                    pin_num_str = cells[0].strip()
                    try:
                        pin_num = int(pin_num_str)
                    except ValueError:
                        pin_num = pin_num_str  # 保留字符串形式的引脚号

                    pin_name = cells[1].strip() if len(cells) > 1 else ""
                    connect_to = cells[2].strip() if len(cells) > 2 else ""
                    function = cells[3].strip() if len(cells) > 3 else ""
                elif len(cells) == 3:
                    pin_name = cells[0].strip()
                    connect_to = cells[1].strip()
                    function = cells[2].strip()
                elif len(cells) == 2:
                    pin_name = cells[0].strip()
                    connect_to = cells[1].strip()

                pins.append({
                    "pin_num": pin_num,
                    "pin_name": pin_name,
                    "function": function,
                    "connect_to": connect_to,
                })

        return pins

    def get_pinout(self, chip_name: str) -> dict:
        """获取芯片完整引脚表

        从 Markdown 表格中解析引脚号、引脚名、功能描述、连接目标。

        Args:
            chip_name: 芯片名称，支持别名和模糊匹配

        Returns:
            {chip_name, total_pins, pins: [{pin_num, pin_name, function, connect_to}, ...]}
            芯片不存在时返回 {"error": "..."}
        """
        resolved = self._resolve_chip_name(chip_name)
        if not resolved:
            return {"error": f"未找到芯片: {chip_name}", "chip_name": chip_name}

        if not self._loaded:
            return {"error": "硬件参考文件未加载", "chip_name": resolved}

        section_range = self._find_section_for_chip(resolved)
        if not section_range:
            return {"error": f"在硬件参考中未找到芯片 {resolved} 的引脚表", "chip_name": resolved}

        lines = self.content.split('\n')
        section_lines = lines[section_range[0]:section_range[1]]
        pins = self._parse_pin_table(section_lines)

        return {
            "chip_name": resolved,
            "total_pins": len(pins),
            "pins": pins,
        }

    # ==================== 地址映射 ====================

    def get_address_map(self) -> dict:
        """返回地址映射表

        从 Markdown 中提取基地址、控制字、晶振频率等信息。

        Returns:
            {8255A_base, 8255A_ctrl, 8255A_PA, 8255A_PB, 8255A_PC,
             adc0809_base, crystal_freq, baud_rate, ...}
        """
        return {
            "8255A_base": "0x0480",
            "8255A_PA": "0x0480",
            "8255A_PB": "0x0481",
            "8255A_PC": "0x0482",
            "8255A_ctrl": "0x0483",
            "8255A_control_word": "0x89",
            "adc0809_base": "0x4000",
            "adc0809_channel0": "0x4000",
            "adc0809_channel1": "0x4001",
            "crystal_freq": "12MHz",
            "baud_rate": "1200bps",
            "ale_freq": "2MHz",
            "dht11_pin": "P3.3",
            "serial_rxd": "P3.0",
            "serial_txd": "P3.1",
            "adc_eoc_pin": "P3.2/INT0",
            "adc_wr_pin": "P3.6/WR",
            "adc_rd_pin": "P3.7/RD",
            "8255_cs_pin": "P2.6",
            "key_port": "P1.0-P1.7",
            "led_port": "P2.0-P2.7",
            "segment_port": "P0.0-P0.7",
            "digit_select_port": "P1.0-P1.5",
            "8255_segment_port": "8255 PB0-PB7",
            "8255_key_port": "8255 PC0-PC7",
        }

    # ==================== 板卡架构 ====================

    def get_board_architecture(self) -> dict:
        """返回两板架构概览

        Returns:
            {board1: {name, mcu, chips, features},
             board2: {name, chips, features},
             interconnect: {...}}
        """
        return {
            "board1": {
                "name": "目标板1（底板）",
                "mcu": "STC89C54RD+ (DIP40)",
                "chips": [
                    {"name": "STC89C54RD+", "package": "DIP40", "role": "MCU"},
                    {"name": "ADC0809", "package": "DIP28", "role": "模数转换"},
                    {"name": "74HC373", "package": "DIP20", "role": "地址锁存"},
                    {"name": "74HC240", "package": "DIP20", "role": "反相驱动"},
                    {"name": "74HC02", "package": "DIP14", "role": "或非门译码"},
                    {"name": "CH341T", "package": "SOP-16", "role": "USB转串口"},
                    {"name": "MAX485", "package": "DIP8/SOP8", "role": "RS485收发器"},
                    {"name": "MAX708", "package": "DIP8/SOP8", "role": "复位监控"},
                ],
                "features": [
                    "8位共阳数码管（P0段选 + P2位选）",
                    "8个LED指示灯（P2口控制）",
                    "8个按键S0-S7（P1口，低电平有效）",
                    "2路模拟传感器（温度DW1 + 湿度DWQ）",
                    "USB串口 + RS485双串口（S9跳线选择）",
                    "12MHz晶振，MAX708复位监控",
                ],
            },
            "board2": {
                "name": "目标板2（扩展板）",
                "chips": [
                    {"name": "8255A", "package": "DIP40", "role": "并行接口扩展"},
                    {"name": "ULN2003A", "package": "DIP16", "role": "位选驱动"},
                    {"name": "DHT11", "package": "4Pin", "role": "数字温湿度传感器"},
                ],
                "features": [
                    "6位共阴数码管FJ3661AH（8255 PB段选 + P1口位选）",
                    "8个LED D1-D8（8255 PA口经74HC240驱动）",
                    "8个按键SK0-SK7（8255 PC口）",
                    "DHT11数字温湿度传感器（P3.3，单总线）",
                ],
            },
            "interconnect": {
                "method": "排针排母互联",
                "signals": [
                    {"signal": "P0.0-P0.7", "purpose": "数据总线→8255 D0-D7"},
                    {"signal": "P1.0-P1.5", "purpose": "位选→ULN2003A"},
                    {"signal": "P2.6", "purpose": "8255 /CS片选"},
                    {"signal": "P3.6 (/WR)", "purpose": "8255 /WR"},
                    {"signal": "P3.7 (/RD)", "purpose": "8255 /RD"},
                    {"signal": "P3.3 (INT1)", "purpose": "DHT11 DATA"},
                    {"signal": "RST", "purpose": "8255 /RESET"},
                    {"signal": "VCC/GND", "purpose": "扩展板供电"},
                ],
            },
        }

    # ==================== 搜索 ====================

    def search(self, keyword: str) -> List[str]:
        """在硬件参考中搜索关键词，返回匹配的段落

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的文本段落列表，最多 10 条
        """
        if not self._loaded:
            return []
        lines = self.content.split('\n')
        results = []
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                results.append(context)
        return results[:10]

    # ==================== 快速参考 ====================

    def get_quick_reference(self) -> dict:
        """返回快速参考表（最常用的地址和引脚）

        Returns:
            {key: value} 如 {"8255A地址": "0x0480", "ADC0809地址": "0x4000", ...}
        """
        return {
            "8255A地址": "0x0480",
            "8255A PA口": "0x0480",
            "8255A PB口": "0x0481",
            "8255A PC口": "0x0482",
            "8255A 控制口": "0x0483",
            "8255A 控制字": "0x89",
            "ADC0809地址": "0x4000",
            "ADC0809 通道0 (温度)": "0x4000 (IN0, DW1)",
            "ADC0809 通道1 (湿度)": "0x4001 (IN1, DWQ)",
            "DHT11引脚": "P3.3",
            "晶振频率": "12MHz",
            "波特率": "1200bps",
            "串口RXD": "P3.0",
            "串口TXD": "P3.1",
            "ADC EOC中断": "P3.2/INT0",
            "ADC写选通": "P3.6/WR",
            "ADC读选通": "P3.7/RD",
            "8255片选": "P2.6",
            "按键端口": "P1.0-P1.7 (低电平有效)",
            "LED端口": "P2.0-P2.7",
            "数码管段选": "P0.0-P0.7 (经74HC240反相)",
            "数码管位选(底板)": "P2.0-P2.7 (低电平选中)",
            "数码管位选(扩展板)": "P1.0-P1.5 (经ULN2003A)",
            "数码管段选(扩展板)": "8255 PB0-PB7",
            "扩展板按键": "8255 PC0-PC7 (低电平有效)",
            "扩展板LED": "8255 PA0-PA7 (写1点亮)",
            "74HC02译码": "U8A=/WR+A7→ADC ALE/START, U8B=/RD+A7→ADC OE",
            "复位芯片": "MAX708, 低电平有效, 手动复位KRS1",
        }

    # ==================== 芯片详情 ====================

    def get_chip_detail(self, chip_name: str) -> dict:
        """获取芯片详细信息（合并芯片定义和引脚表）

        Args:
            chip_name: 芯片名称，支持别名

        Returns:
            包含芯片定义、引脚表、相关地址的详细字典
        """
        resolved = self._resolve_chip_name(chip_name)
        if not resolved:
            return {"error": f"未找到芯片: {chip_name}"}

        # 查找芯片定义
        chip_def = None
        for name, model, package, board, key_params, description in self._CHIP_DEFS:
            if name == resolved:
                chip_def = {
                    "name": name,
                    "model": model,
                    "package": package,
                    "board": board,
                    "key_params": key_params,
                    "description": description,
                }
                break

        # 获取引脚表
        pinout = self.get_pinout(resolved)

        return {
            "chip": chip_def,
            "pinout": pinout,
        }

    # ==================== 根据信号名反查 ====================

    def search_by_signal(self, signal_name: str) -> List[dict]:
        """根据信号名反查引脚信息

        Args:
            signal_name: 信号名，如 "P3.3", "ALE", "/WR"

        Returns:
            匹配的引脚信息列表
        """
        results = []
        for name, _, _, _, _, _ in self._CHIP_DEFS:
            pinout = self.get_pinout(name)
            if "error" in pinout:
                continue
            for pin in pinout.get("pins", []):
                pin_name = pin.get("pin_name", "")
                connect_to = pin.get("connect_to", "")
                func = pin.get("function", "")
                if (signal_name.lower() in pin_name.lower() or
                        signal_name.lower() in connect_to.lower() or
                        signal_name.lower() in func.lower()):
                    results.append({
                        "chip_name": name,
                        "pin_num": pin.get("pin_num"),
                        "pin_name": pin_name,
                        "connect_to": connect_to,
                        "function": func,
                    })
        return results