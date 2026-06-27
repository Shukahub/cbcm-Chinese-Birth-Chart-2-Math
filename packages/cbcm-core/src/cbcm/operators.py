"""算子层（对应 docs/07-operators.md）。

所有算子是命盘状态（及衍生量）上的纯函数，不引入新公理。
分两类：
- 群运算型：冲/合/害/三合/三会/旬空（写成 Z_12 或 Z_60 的一个运算）
- 查表型：刑/破/纳音/神煞（显式查找表）

十神是 (τ 差分, π 同异) → 表，结构化查表。
"""

from __future__ import annotations

from . import ganzhi, notation, wuxing
from .schemas import Chart, Pillar

# =========================================================================
# 一、十神（docs/07 §2）
# =========================================================================
# (五行差分 d, 同阴阳?) → 十神名
_TEN_GOD_TABLE: dict[tuple[int, bool], str] = {
    (0, True):  "比肩",
    (0, False): "劫财",
    (1, True):  "食神",
    (1, False): "伤官",
    (2, True):  "偏财",
    (2, False): "正财",
    (3, True):  "七杀",
    (3, False): "正官",
    (4, True):  "偏印",
    (4, False): "正印",
}

TEN_GODS: tuple[str, ...] = (
    "比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印",
)


def ten_god(day_master: int, other: int) -> str:
    """日主干 day_master 对他干 other 的十神。

    d = (τ(other) - τ(day_master)) mod 5；同阴阳→偏，异阴阳→正（d=0 例外：同→比肩，异→劫财）。
    """
    a = day_master % 10
    b = other % 10
    d = (wuxing.stem_wuxing(b) - wuxing.stem_wuxing(a)) % wuxing.N
    same = ganzhi.parity(a) == ganzhi.parity(b)
    return _TEN_GOD_TABLE[(d, same)]


def chart_stem_gods(chart: Chart) -> dict[str, str]:
    """盘中四天干相对日主的十神（年/月/时三干；日干自身即日主）。"""
    dm = chart.day_master
    return {
        "year": ten_god(dm, chart.year.stem),
        "month": ten_god(dm, chart.month.stem),
        "hour": ten_god(dm, chart.hour.stem),
    }


# =========================================================================
# 一·补 藏干（地支藏干表）+ 完整十神（docs/07 §2 扩展）
# =========================================================================
# 藏干：每个地支暗含若干天干，按旺衰分本气/中气/余气，权重 1.0/0.5/0.25。
HIDDEN_LABELS: dict[float, str] = {1.0: "本气", 0.5: "中气", 0.25: "余气"}

HIDDEN_STEMS: dict[int, tuple[tuple[int, float], ...]] = {
    0:  ((9, 1.0),),                  # 子：癸
    1:  ((5, 1.0), (7, 0.5), (9, 0.25)),  # 丑：己辛癸
    2:  ((0, 1.0), (2, 0.5), (4, 0.25)),  # 寅：甲丙戊
    3:  ((1, 1.0),),                  # 卯：乙
    4:  ((4, 1.0), (1, 0.5), (9, 0.25)),  # 辰：戊乙癸
    5:  ((2, 1.0), (6, 0.5), (4, 0.25)),  # 巳：丙庚戊
    6:  ((3, 1.0), (5, 0.5)),             # 午：丁己
    7:  ((5, 1.0), (3, 0.5), (1, 0.25)),  # 未：己丁乙
    8:  ((6, 1.0), (8, 0.5), (4, 0.25)),  # 申：庚壬戊
    9:  ((7, 1.0),),                  # 酉：辛
    10: ((4, 1.0), (7, 0.5), (3, 0.25)),  # 戌：戊辛丁
    11: ((8, 1.0), (0, 0.5)),             # 亥：壬甲
}


def hidden_stems(branch: int) -> tuple[tuple[int, float], ...]:
    """地支藏干：返回 ((干, 权重), ...)，首项为本气。"""
    return HIDDEN_STEMS[branch % 12]


def hidden_stems_detailed(branch: int) -> list[dict]:
    """藏干 → [{stem, name, wuxing, weight, label}]。"""
    out = []
    for st, w in hidden_stems(branch):
        out.append({
            "stem": notation.stem_name(st),
            "wuxing": notation.wuxing_name(wuxing.stem_wuxing(st)),
            "weight": w,
            "label": HIDDEN_LABELS[w],
        })
    return out


def wuxing_strength(chart: Chart) -> list[float]:
    """盘中五行强度（中性聚合，非断言）：4 天干各 1.0 + 各支藏干按权重。"""
    s = [0.0] * 5
    for p in chart.pillars:
        s[wuxing.stem_wuxing(p.stem)] += 1.0
        for st, w in hidden_stems(p.branch):
            s[wuxing.stem_wuxing(st)] += w
    return s


def strength_split(chart: Chart) -> tuple[float, float]:
    """日主 帮身(比劫+印) 与 耗身(食伤+财+官杀) 的强度对比（中性）。

    返回 (help_power, drain_power)。帮身=同我/生我；耗身=我生/我克/克我。
    """
    dm_wx = wuxing.stem_wuxing(chart.day_master)
    s = wuxing_strength(chart)
    help_power = sum(s[wx] for wx in range(5) if wuxing.rel(dm_wx, wx) in (wuxing.REL_BIHE, wuxing.REL_SHENGI))
    drain_power = sum(s[wx] for wx in range(5) if wuxing.rel(dm_wx, wx) in (wuxing.REL_SHENG, wuxing.REL_KE, wuxing.REL_KEI))
    return help_power, drain_power


def chart_full_gods(chart: Chart) -> dict[str, list[dict]]:
    """完整十神：每柱给出天干十神 + 各藏干十神（相对日主）。"""
    dm = chart.day_master
    out: dict[str, list[dict]] = {}
    for label, p in (("year", chart.year), ("month", chart.month),
                     ("day", chart.day), ("hour", chart.hour)):
        items = [{"stem": notation.stem_name(p.stem), "god": ten_god(dm, p.stem), "part": "天干"}]
        for st, w in hidden_stems(p.branch):
            items.append({
                "stem": notation.stem_name(st), "god": ten_god(dm, st),
                "part": HIDDEN_LABELS[w],
            })
        out[label] = items
    return out


# =========================================================================
# 二、地支关系（docs/07 §3，建在 Z_12 上）
# =========================================================================

def branch_clash(b: int) -> int:
    """六冲：(b+6) mod 12（差≡6，对合）。"""
    return (b + 6) % 12


def branch_combine(b: int) -> int:
    """六合：(1-b) mod 12（和≡1，对合）。"""
    return (1 - b) % 12


def branch_harm(b: int) -> int:
    """相害：(7-b) mod 12（和≡7，对合）。"""
    return (7 - b) % 12


# 三合局 = Z_12 / <4> 的陪集；b mod 4 决定所属局（docs/07 §3.2）
_THREE_HARMONY_HUASHEN: dict[int, int] = {
    0: 4,  # 子辰申 → 水
    1: 3,  # 丑巳酉 → 金
    2: 1,  # 寅午戌 → 火
    3: 0,  # 卯未亥 → 木
}


def three_harmony_coset(b: int) -> int:
    """三合局编号 = b mod 4 ∈ {0,1,2,3}。"""
    return b % 4


def three_harmony_members(b: int) -> tuple[int, int, int]:
    """b 所在三合局的三支 {b, b+4, b+8}（已排序呈现）。"""
    base = three_harmony_coset(b)
    return (base, (base + 4) % 12, (base + 8) % 12)


def three_harmony_huashen(b: int) -> int:
    """三合局化神行（土无局）。"""
    return _THREE_HARMONY_HUASHEN[three_harmony_coset(b)]


# 三会方 = 连续三位（docs/07 §3.1）
_DIRECTION_WUXING: dict[int, int] = {0: 0, 1: 1, 2: 3, 3: 4}  # 木火金水


def three_direction_group(b: int) -> int:
    """会方组号 ∈ {0,1,2,3}：东木/南火/西金/北水。组 0={寅卯辰}..."""
    return ((b - 2) % 12) // 3


def three_direction_members(group: int) -> tuple[int, int, int]:
    """会方组的三支。"""
    start = (2 + 3 * group) % 12
    return (start, (start + 1) % 12, (start + 2) % 12)


# 相刑（有向表 + 自刑，docs/07 §3.3；非群运算）
_XING_EDGES: set[tuple[int, int]] = {
    (2, 5), (5, 8), (8, 2),   # 寅巳申 无恩
    (1, 10), (10, 7), (7, 1),  # 丑戌未 恃势
    (0, 3), (3, 0),            # 子卯 无礼（双向）
    (4, 4), (6, 6), (9, 9), (11, 11),  # 辰午酉亥 自刑
}


def xing(a: int, b: int) -> bool:
    """a 是否刑 b。"""
    return (a % 12, b % 12) in _XING_EDGES


# 相破（无向对，docs/07 §3.3；非群运算）
_PO_PAIRS: frozenset[frozenset[int]] = frozenset(
    {frozenset(p) for p in [(0, 9), (1, 4), (2, 11), (3, 6), (5, 8), (7, 10)]}
)


def po(a: int, b: int) -> bool:
    """a 与 b 是否相破。"""
    return frozenset({a % 12, b % 12}) in _PO_PAIRS


# =========================================================================
# 三、纳音五行（docs/07 §4，30 项查表；k ∈ Z_60）
# =========================================================================
_NAYIN_NAMES: tuple[str, ...] = (
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
    "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土",
    "霹雳火", "松柏木", "长流水", "砂石金", "山下火", "平地木",
    "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
    "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水",
)
# 每个（两两甲子组）的五行索引
_NAYIN_WUXING: tuple[int, ...] = (
    3, 1, 0, 2, 3, 1, 4, 2, 3, 0, 4, 2, 1, 0, 4,
    3, 1, 0, 2, 3, 1, 4, 2, 3, 0, 4, 2, 1, 0, 4,
)


def nayin_name(k: int) -> str:
    """甲子序号 k 的纳音名（如 0 → '海中金'）。"""
    return _NAYIN_NAMES[(k % 60) // 2]


def nayin_wuxing(k: int) -> int:
    """甲子序号 k 的纳音五行索引。"""
    return _NAYIN_WUXING[(k % 60) // 2]


# =========================================================================
# 四、神煞（docs/07 §5；桃花/驿马复用三合局）
# =========================================================================
_PEACH: dict[int, int] = {0: 9, 1: 6, 2: 3, 3: 0}   # 三合局 → 四正
_HORSE: dict[int, int] = {0: 2, 1: 11, 2: 8, 3: 5}  # 三合局 → 四生


def peach_blossom(b: int) -> int:
    """桃花（咸池）：按 b 所在三合局指向四正之一。"""
    return _PEACH[three_harmony_coset(b)]


def horse(b: int) -> int:
    """驿马：按 b 所在三合局指向四生之一。"""
    return _HORSE[three_harmony_coset(b)]


def has_peach(branch: int, anchor: int) -> bool:
    """anchor 支（年/日支）的桃花是否落到 branch。"""
    return branch % 12 == peach_blossom(anchor)


def has_horse(branch: int, anchor: int) -> bool:
    return branch % 12 == horse(anchor)


# =========================================================================
# 五、旬空（docs/07 §6，群运算型）
# =========================================================================

def vacancy(k: int) -> tuple[int, int]:
    """日柱序号 k（Z_60）的两个空亡地支 = {(s-2) mod 12, (s-1) mod 12}，s = 旬首。"""
    s = ganzhi.xun_head(k)
    return ((s - 2) % 12, (s - 1) % 12)


def is_vacant(branch: int, day_index: int) -> bool:
    """branch 是否落入日柱的空亡。"""
    return branch % 12 in vacancy(day_index)
