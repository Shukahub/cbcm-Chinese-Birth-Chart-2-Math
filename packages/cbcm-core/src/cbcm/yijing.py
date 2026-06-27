"""易经代数（对应 docs/05-yijing.md）。

- 阴阳 = F_2 = {0,1}，加法 = XOR（翻转）
- 八卦 = F_2^3（8 元），按下爻为 bit0
- 六十四卦 = F_2^6（64 元），下爻为 bit0，上爻为 bit5
- 卦变均为仿射/置换：错卦=全翻，综卦=位序反转，变某爻=翻该位
"""

from __future__ import annotations

N_YAO_HEX = 6
N_YAO_TRI = 3
ALL_ONES_HEX = (1 << N_YAO_HEX) - 1  # 0b111111 = 63


def yao(hex_: int, pos: int) -> int:
    """取第 pos 爻（pos=0 为初爻/最下）。"""
    return (hex_ >> pos) & 1


def with_yao(hex_: int, pos: int, val: int) -> int:
    """设置第 pos 爻为 val。"""
    mask = 1 << pos
    return (hex_ & ~mask) | ((val & 1) << pos)


def to_bits(hex_: int, n: int = N_YAO_HEX) -> tuple[int, ...]:
    """卦 → 爻元组（下→上）。"""
    return tuple((hex_ >> i) & 1 for i in range(n))


def from_bits(bits: tuple[int, ...]) -> int:
    """爻元组（下→上）→ 卦整数。"""
    v = 0
    for i, b in enumerate(bits):
        v |= (b & 1) << i
    return v


def trigrams() -> list[int]:
    """八卦 = F_2^3 的 8 个元素（作为 0..7 整数）。"""
    return list(range(1 << N_YAO_TRI))


def hexagrams() -> list[int]:
    """六十四卦 = F_2^6 的 64 个元素。"""
    return list(range(1 << N_YAO_HEX))


# ---- 卦变（仿射/置换运算）----

def cuogua(hex_: int) -> int:
    """错卦：阴阳全反 = 与全 1 异或。"""
    return hex_ ^ ALL_ONES_HEX


def zonggua(hex_: int) -> int:
    """综卦：上下颠倒 = 位序反转。"""
    bits = to_bits(hex_)
    return from_bits(bits[::-1])


def change_yao(hex_: int, pos: int) -> int:
    """变某爻：翻转第 pos 位（F_2 加单位向量）。"""
    return hex_ ^ (1 << pos)


def change_yao_set(hex_: int, positions: set[int]) -> int:
    """同时变若干爻：叠加若干单位向量（之卦）。"""
    out = hex_
    for p in positions:
        out ^= 1 << p
    return out


def lower_trigram(hex_: int) -> int:
    """下卦（初、二、三爻）。"""
    return hex_ & 0b111


def upper_trigram(hex_: int) -> int:
    """上卦（四、五、上爻）。"""
    return (hex_ >> N_YAO_TRI) & 0b111
