"""五行代数（对应 docs/04-wuxing.md）。

核心结论：相克 = 相生²。
- 五行集 E = Z_5（木0 火1 土2 金3 水4）
- 相生 σ(x) = x + 1（5-循环）
- 相克 = σ²(x) = x + 2
- 任意两行关系由差分 d = (y - x) mod 5 唯一决定（5 类）
- 干→五行 τ(a) = a // 2
"""

from __future__ import annotations

from . import notation

N = 5

# 关系类别（由差分 d = (y - x) mod 5 决定）：x 为"我"，y 为目标
REL_BIHE = 0  # 比和（同类）
REL_SHENG = 1  # 我生
REL_KE = 2  # 我克
REL_KEI = 3  # 克我（被克）
REL_SHENGI = 4  # 生我（被生）

RELATION_NAMES: dict[int, str] = {
    REL_BIHE: "比和",
    REL_SHENG: "我生",
    REL_KE: "我克",
    REL_KEI: "克我",
    REL_SHENGI: "生我",
}


def sheng(x: int) -> int:
    """相生：x 生 (x+1)。"""
    return (x + 1) % N


def ke(x: int) -> int:
    """相克：x 克 (x+2)。等于相生的平方：sheng(sheng(x))。"""
    return (x + 2) % N


def rel(x: int, y: int) -> int:
    """我(x) 对 目标(y) 的五行关系 = (y - x) mod 5 ∈ {0..4}。"""
    return (y - x) % N


def stem_wuxing(a: int) -> int:
    """天干→五行 τ(a) = a // 2。甲乙木、丙丁火、戊己土、庚辛金、壬癸水。"""
    return (a // 2) % N


def relation_name(r: int) -> str:
    return RELATION_NAMES[r % N]


def relation_matrix() -> list[list[int]]:
    """5×5 循环差分表（circulant）：M[x][y] = (y - x) mod 5。"""
    return [[rel(x, y) for y in range(N)] for x in range(N)]
