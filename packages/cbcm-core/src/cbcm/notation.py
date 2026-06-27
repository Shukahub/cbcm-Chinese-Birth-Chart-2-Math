"""名称表与显示转换（对应 docs/02-notation.md）。

设计原则：内核一律用 0-indexed 整数运算；显示成中文才查本表。
名称表是纯查表，不参与代数运算。
"""

from __future__ import annotations

# 天干 Z_10：甲=0, 乙=1, ..., 癸=9
STEMS: list[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支 Z_12：子=0, 丑=1, ..., 亥=11
BRANCHES: list[str] = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 生肖（地支的扩展映射，查表用）
ZODIAC: list[str] = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]

# 五行 Z_5：木=0, 火=1, 土=2, 金=3, 水=4
WUXING: list[str] = ["木", "火", "土", "金", "水"]

# 阴阳 F_2：阴=0, 阳=1
YINYANG: list[str] = ["阴", "阳"]

# 八卦 F_2^3：按下标为 3 位二进制（下爻为最低位），见 docs/05-yijing.md §3
TRIGRAMS: list[str] = ["坤", "震", "坎", "兑", "艮", "离", "巽", "乾"]

# 六十四卦 F_2^6 名称（下卦低位，共 64；这里给索引→名，采用周易序的常用名按二进制序排列）
# index = 6 位二进制（初爻为最低位 bit0，上爻 bit5）
HEXAGRAM_NAMES: list[str] = [
    "坤", "颐", "屯", "震", "谦", "剥", "比", "豫",
    "师", "蒙", "坎", "解", "升", "萃", "观", "小过",
    "明夷", "贲", "既济", "丰", "晋", "否", "萃", "恒",
    "临", "损", "节", "归妹", "泰", "大畜", "需", "大壮",
    "复", "随", "井", "大过", "颐", "蛊", "困", "咸",
    "噬嗑", "离", "鼎", "革", "无妄", "贲", "旅", "革",
    "损", "睽", "未济", "兑", "中孚", "履", "睽", "兑",
    "泰", "大壮", "需", "大畜", "大过", "鼎", "巽", "乾",
]


def stem_name(i: int) -> str:
    """天干索引 → 中文名。"""
    return STEMS[i % 10]


def branch_name(i: int) -> str:
    """地支索引 → 中文名。"""
    return BRANCHES[i % 12]


def wuxing_name(i: int) -> str:
    """五行索引 → 中文名。"""
    return WUXING[i % 5]


def stem_index(name: str) -> int:
    """天干中文名 → 索引（0-indexed）。"""
    return STEMS.index(name)


def branch_index(name: str) -> int:
    """地支中文名 → 索引（0-indexed）。"""
    return BRANCHES.index(name)


def pillar_name(stem: int, branch: int) -> str:
    """干支对 → 形如 '甲子' 的串。"""
    return stem_name(stem) + branch_name(branch)


def parity_name(i: int) -> str:
    """奇偶（阴阳）→ 名。"""
    return YINYANG[i % 2]


def yinyang_of(index: int) -> str:
    """序号 → 阴阳名（偶序号=阳，奇序号=阴）。对应 docs/02 约定。"""
    return "阳" if index % 2 == 0 else "阴"
