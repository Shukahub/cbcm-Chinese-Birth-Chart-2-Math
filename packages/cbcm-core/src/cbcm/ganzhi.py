"""干支代数（对应 docs/03-ganzhi.md）。

- 天干 T = Z_10
- 地支 B = Z_12
- 阴阳算子 π(x) = x mod 2（两类；偶序号=阳，奇序号=阴；公式只依赖同类与否）
- 六十甲子 G = {(s,b) ∈ Z_10×Z_12 : s≡b (mod 2)} ≅ Z_60，生成元 (1,1)，阶 lcm(10,12)=60
"""

from __future__ import annotations

from . import notation

N_STEM = 10
N_BRANCH = 12
N_CYCLE = 60  # lcm(10, 12)


def parity(i: int) -> int:
    """阴阳算子 π(i) = i mod 2。两类：0=阳类(偶序号)，1=阴类(奇序号)。"""
    return i % 2


def same_yy(a: int, b: int) -> bool:
    """两者是否同阴阳（即同奇偶）。"""
    return parity(a) == parity(b)


def is_valid_pillar(stem: int, branch: int) -> bool:
    """合法干支对：干支同阴阳（同奇偶）。"""
    return parity(stem % N_STEM) == parity(branch % N_BRANCH)


def pillar_from_index(k: int) -> tuple[int, int]:
    """Z_60 的第 k 位 → (干, 支)。k=0 即甲子，k=59 即癸亥。

    pillar(k) = (k mod 10, k mod 12)；奇偶自动相同（因 10、12 同为偶）。
    """
    k %= N_CYCLE
    return (k % N_STEM, k % N_BRANCH)


def index_from_pillar(stem: int, branch: int) -> int:
    """合法干支对 → Z_60 中的索引（中国剩余定理解，唯一 mod 60）。"""
    stem %= N_STEM
    branch %= N_BRANCH
    if not is_valid_pillar(stem, branch):
        raise ValueError(
            f"非法干支对 ({notation.stem_name(stem)},{notation.branch_name(branch)})："
            "干支必须同阴阳（同奇偶）"
        )
    # 求 k ∈ [0,60) 使 k≡stem (mod 10) 且 k≡branch (mod 12)
    for t in range(6):  # stem + 10*t, t ∈ 0..5 覆盖 Z_60 中同干的 6 解
        k = stem + N_STEM * t
        if k % N_BRANCH == branch:
            return k
    raise AssertionError("不可达：合法对必可解")


def all_pillars() -> list[tuple[int, int]]:
    """六十甲子按序（甲子 → 癸亥）的 60 个 (干,支) 对。"""
    return [pillar_from_index(k) for k in range(N_CYCLE)]


def advance(k: int, n: int = 1) -> int:
    """在 Z_60 上前进 n 步。"""
    return (k + n) % N_CYCLE


# ---- 旬结构（docs/03 §5：Z_60 / Z_10 ≅ Z_6 的陪集）----

XUN_HEADS: list[int] = [0, 10, 20, 30, 40, 50]  # 六甲旬首


def xun_head(k: int) -> int:
    """索引 k 所在旬的旬首 ∈ {0,10,...,50}（同干首位，干=甲）。"""
    return (k % N_CYCLE) - (k % N_STEM)
