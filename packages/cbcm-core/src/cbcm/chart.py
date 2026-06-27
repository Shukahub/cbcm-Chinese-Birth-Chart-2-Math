"""排盘 Φ（对应 docs/06-bazi.md）。

设计（docs/06 §6）：把"纯代数"与"历法量化"分离——
- 纯代数（年月时柱公式、五虎遁/五鼠遁、日柱连续推进）：完全可测、可证。
- 历法量化（节气精确时刻、日柱绝对锚点）：用可插拔 resolver + 明确标注的校准项。

默认 ApproximateSolarTermResolver 用平均节气日期，**精度有限**，仅用于骨架演示；
接入真实天文（ephem/skyfield/lunar_python）后可替换为 precise 实现。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from . import ganzhi, notation
from .schemas import BirthInput, Chart, Convention, Dayun, Pillar

# =========================================================================
# 工具：Julian Day Number（纯数学，可测；jdn(2000,1,1)=2451545）
# =========================================================================

def _jdn(y: int, m: int, d: int) -> int:
    a = (14 - m) // 12
    yy = y + 4800 - a
    mm = m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045


# =========================================================================
# 日柱（闭式：标准 JDN↔干支关系，已用权威算例验证）
# =========================================================================
# 干支日序（甲子=0）= (JDN(date) + 49) mod 60 —— 日历软件通用公式。
# 验证（Wikipedia "Sexagenary cycle" 算例，公历日期）：
#   1949-10-01 = 甲子(0)；1592-12-31 = 甲申(20)。见 test_chart。
# 注：1582-10-15 之前的日期原为儒略历；本式按公历（proleptic Gregorian），
# 现代生辰（均公历）不受影响。
_DAY_OFFSET = 49


def day_index_from_date(d: date) -> int:
    """日期（公历）→ 日柱在 Z_60 中的索引（甲子=0）。连续纪日。"""
    return (_jdn(d.year, d.month, d.day) + _DAY_OFFSET) % ganzhi.N_CYCLE


# =========================================================================
# 节气 resolver（可插拔协议）
# =========================================================================

class SolarTermResolver(Protocol):
    """节气 resolver 协议：把日期映射到月支 / 判断立春。"""

    def month_branch(self, year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> int: ...

    def lichun_passed(self, year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> bool: ...


@dataclass(frozen=True)
class ApproximateSolarTermResolver:
    """平均节气日期 resolver（精度有限）。返回各月支的近似开始 (month, day)。"""
    # 按 (month, day) 升序：小寒(丑)→立春(寅)→…→大雪(子)
    terms: tuple[tuple[int, int, int], ...] = (
        (1, 6, 1),    # 小寒 → 丑月
        (2, 4, 2),    # 立春 → 寅月（兼作年界 lichun）
        (3, 6, 3),    # 惊蛰 → 卯月
        (4, 5, 4),    # 清明 → 辰月
        (5, 6, 5),    # 立夏 → 巳月
        (6, 6, 6),    # 芒种 → 午月
        (7, 7, 7),    # 小暑 → 未月
        (8, 8, 8),    # 立秋 → 申月
        (9, 8, 9),    # 白露 → 酉月
        (10, 8, 10),  # 寒露 → 戌月
        (11, 7, 11),  # 立冬 → 亥月
        (12, 7, 0),   # 大雪 → 子月
    )

    def month_branch(self, year: int, m: int, d: int, hour: int = 12, minute: int = 0) -> int:
        """(year 忽略) → 月支（0..11）。"""
        branch = 0  # 1/6 之前属上一年子月
        for tm, td, tb in self.terms:
            if (m, d) >= (tm, td):
                branch = tb
            else:
                break
        return branch

    def lichun_passed(self, year: int, m: int, d: int, hour: int = 12, minute: int = 0) -> bool:
        return (m, d) >= (2, 4)


# =========================================================================
# 四柱计算
# =========================================================================

def _equation_of_time_min(d: date) -> float:
    """均时差（Equation of Time），分钟。NOAA 近似公式。"""
    import math
    doy = d.timetuple().tm_yday
    b = 2 * math.pi * (doy - 81) / 364
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def _true_solar_offset_min(birth: BirthInput) -> float:
    """真太阳时相对北京时（基准经度 120°）的分钟修正：经度 + 均时差。"""
    return (birth.longitude - 120.0) * 4 + _equation_of_time_min(date(birth.year, birth.month, birth.day))


def _normalized(birth: BirthInput, conv: Convention) -> tuple[date, int]:
    """真太阳时修正后的 (日期, 小时)。日期按日历 00:00 切换（子时跨日不影响日柱）。"""
    from datetime import timedelta
    total_min = birth.hour * 60 + birth.minute
    if conv.true_solar_time and birth.longitude is not None:
        total_min += round(_true_solar_offset_min(birth))
    d = date(birth.year, birth.month, birth.day)
    if total_min >= 24 * 60:
        d += timedelta(days=1); total_min -= 24 * 60
    elif total_min < 0:
        d -= timedelta(days=1); total_min += 24 * 60
    return d, total_min // 60


def year_pillar(birth: BirthInput, conv: Convention,
                resolver: ApproximateSolarTermResolver | None = None) -> Pillar:
    """年柱：以立春（默认）为年界。year干=(Y-4)%10, 支=(Y-4)%12。"""
    resolver = resolver or ApproximateSolarTermResolver()
    y = birth.year
    if conv.year_boundary == "lichun":
        if not resolver.lichun_passed(birth.year, birth.month, birth.day, birth.hour, birth.minute):
            y -= 1
    # lunar_newyear 边界需农历库，骨架里近似仍以立春处理（TODO）
    stem = (y - 4) % 10
    branch = (y - 4) % 12
    return Pillar.from_stem_branch(stem, branch)


def month_pillar(birth: BirthInput, conv: Convention, year_stem: int,
                 resolver: ApproximateSolarTermResolver | None = None) -> Pillar:
    """月柱：月支由节气定，月干由年干（五虎遁）定。docs/06 §4.2。"""
    resolver = resolver or ApproximateSolarTermResolver()
    mb = resolver.month_branch(birth.year, birth.month, birth.day, birth.hour, birth.minute)
    # 五虎遁：寅月起干；月干 = 寅月干 + (该月在 寅→丑 序列中的位置 0..11)
    yin_stem = (2 * (year_stem % 5) + 2) % 10
    month_pos = (mb - 2) % 12  # 寅=0, 卯=1, …, 丑=11
    ms = (yin_stem + month_pos) % 10
    return Pillar.from_stem_branch(ms, mb)


def day_pillar(birth: BirthInput, conv: Convention) -> Pillar:
    """日柱：连续纪日，按日历 00:00 切换（与 lunar_python 一致）。"""
    d, _ = _normalized(birth, conv)
    return Pillar.from_index(day_index_from_date(d))


def hour_pillar(birth: BirthInput, conv: Convention, day_index: int) -> Pillar:
    """时柱：时支由钟点定；时干由'子时所属日'之干（五鼠遁）定。docs/06 §4.4。

    子时(23:00–00:59)的时干：zi_hour_crossday=True 时，23:00–23:59 用次日干
    （早子时约定，与 lunar_python 一致）；日柱本身仍按日历 00:00。
    """
    _, hour = _normalized(birth, conv)
    hb = ((hour + 1) // 2) % 12  # docs/06 §4.4 时支公式
    gan_day_index = (day_index + 1) % 60 if (conv.zi_hour_crossday and hour >= 23) else day_index
    gan_day_stem = ganzhi.pillar_from_index(gan_day_index)[0]
    zi_stem = (2 * (gan_day_stem % 5)) % 10  # 五鼠遁：子时起干
    hs = (zi_stem + hb) % 10
    return Pillar.from_stem_branch(hs, hb)


# =========================================================================
# 主接口
# =========================================================================

def compute_chart(birth: BirthInput, conv: Convention | None = None,
                  resolver: ApproximateSolarTermResolver | None = None) -> Chart:
    """排盘 Φ：BirthInput → Chart。"""
    conv = conv or Convention()
    resolver = resolver or ApproximateSolarTermResolver()

    yp = year_pillar(birth, conv, resolver)
    mp = month_pillar(birth, conv, yp.stem, resolver)
    dp = day_pillar(birth, conv)
    hp = hour_pillar(birth, conv, dp.index)
    return Chart(year=yp, month=mp, day=dp, hour=hp)


def compute_dayun(chart: Chart, birth: BirthInput, conv: Convention | None = None,
                  n_steps: int = 8,
                  resolver: ApproximateSolarTermResolver | None = None) -> Dayun:
    """大运：从月柱派生（docs/06 §5）。方向由年干阴阳×性别定；起运岁按 resolver 精度。"""
    conv = conv or Convention()
    resolver = resolver or ApproximateSolarTermResolver()

    yang = (chart.year.stem % 2 == 0)
    male = (birth.gender == "男")
    forward = (yang == male)  # 顺行
    step = 1 if forward else -1

    seq = tuple(Pillar.from_index(chart.month.index + step * i) for i in range(1, n_steps + 1))

    start_age = _start_age(birth, forward, resolver, conv)
    return Dayun(start_age=start_age, sequence=seq)


def _start_age(birth: BirthInput, forward: bool,
               resolver: ApproximateSolarTermResolver, conv: Convention) -> int:
    """起运岁：出生到下一(顺)/上一(逆)节的天数 ÷ dayun_days_per_year。

    精确 resolver（lunar_python）给到分钟；近似 resolver 退化到按平均节气日。
    """
    days_fn = getattr(resolver, "days_to_jie", None)
    if callable(days_fn):
        days = days_fn(birth.year, birth.month, birth.day, birth.hour, birth.minute, forward)
        if days is not None:
            return max(0, round(days / conv.dayun_days_per_year))
    return _approx_start_age(birth, forward, resolver, conv)


def _approx_start_age(birth: BirthInput, forward: bool,
                      resolver: ApproximateSolarTermResolver, conv: Convention) -> int:
    """近似起运岁（用平均节气日，仅近似 resolver 使用）。"""
    terms_sorted = sorted(resolver.terms, key=lambda t: (t[0], t[1]))
    today_md = (birth.month, birth.day)
    next_term = next((t for t in terms_sorted if (t[0], t[1]) > today_md), None)
    days = (next_term[0] - birth.month) * 30 + (next_term[1] - birth.day) if next_term else 30
    return max(0, int(days // conv.dayun_days_per_year))


def compute_liunian(start_year: int, n: int = 8) -> list[tuple[int, Pillar]]:
    """流年：连续若干公历年的年柱（docs/06 §5 静态命盘之外的年度轴）。

    流年 = 该公历年立春后的年柱 = (year-4) 干支。
    """
    out = []
    for y in range(start_year, start_year + n):
        idx = ganzhi.index_from_pillar((y - 4) % 10, (y - 4) % 12)
        out.append((y, Pillar.from_index(idx)))
    return out
