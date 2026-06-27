"""排盘测试（验证 docs/06-bazi.md）。

注：日柱绝对值依赖 anchor 校准（docs/06 §6），这里只测**机制正确性**与
纯代数部分（年/月/时柱公式），不测日柱绝对值。
"""

from datetime import date, timedelta

import pytest

from cbcm import chart, compute_chart, compute_dayun
from cbcm.schemas import BirthInput, Convention, Pillar


# ---- JDN（纯数学基准）----

def test_jdn_epoch():
    assert chart._jdn(2000, 1, 1) == 2451545


# ---- 日柱机制（绝对值不测，测连续性）----

def test_day_pillar_advances_one_per_day():
    d0 = date(1990, 5, 15)
    d1 = d0 + timedelta(days=1)
    assert (chart.day_index_from_date(d1) - chart.day_index_from_date(d0)) % 60 == 1


def test_day_pillar_60_day_cycle():
    d0 = date(1990, 5, 15)
    d60 = d0 + timedelta(days=60)
    assert chart.day_index_from_date(d0) == chart.day_index_from_date(d60)


def test_day_pillar_in_range_and_valid():
    for d in [date(1950, 1, 1), date(2000, 6, 15), date(2024, 2, 4)]:
        k = chart.day_index_from_date(d)
        assert 0 <= k < 60
        s, b = chart.ganzhi.pillar_from_index(k)
        assert s % 2 == b % 2


def test_day_pillar_absolute_wikipedia_anchors():
    # 闭式 (JDN+49)%60 已用 Wikipedia "Sexagenary cycle" 算例验证（公历日期）
    assert chart.day_index_from_date(date(1949, 10, 1)) == 0    # 甲子（开国大典）
    assert chart.day_index_from_date(date(1592, 12, 31)) == 20  # 甲申
    assert Pillar.from_index(chart.day_index_from_date(date(1949, 10, 1))).name == "甲子"


# ---- 年柱（docs/06 §4.1）----

def test_year_pillar_1984_is_jiazi():
    # 1984 立春后 → 甲子年
    birth = BirthInput(1984, 3, 1, 12)
    yp = chart.year_pillar(birth, Convention())
    assert (yp.stem, yp.branch) == (0, 0)
    assert yp.name == "甲子"


def test_year_boundary_before_lichun():
    # 1984-01-15 立春前 → 归上一年 1983 癸亥
    birth = BirthInput(1984, 1, 15, 12)
    yp = chart.year_pillar(birth, Convention())
    assert (yp.stem, yp.branch) == (9, 11)  # 癸亥


# ---- 月柱 五虎遁（docs/06 §4.2）----

def test_month_pillar_wuhu_dun():
    # 1984 甲年，立春后寅月 → 丙寅（甲己之年丙作首）
    birth = BirthInput(1984, 2, 15, 12)
    yp = chart.year_pillar(birth, Convention())
    mp = chart.month_pillar(birth, Convention(), yp.stem)
    assert (mp.stem, mp.branch) == (2, 2)  # 丙寅

    # 辰月（清明后）：年干甲 → 寅月起丙，辰月干 = (丙 + 2) = 戊
    birth2 = BirthInput(1984, 4, 10, 12)
    mp2 = chart.month_pillar(birth2, Convention(), 0)
    assert (mp2.stem, mp2.branch) == (4, 4)  # 戊辰


# ---- 时柱 五鼠遁 + 时支（docs/06 §4.4）----

def test_hour_branch_formula():
    # 23→子(0), 0→子(0), 12→午(6), 6→卯(3)
    cases = {23: 0, 0: 0, 12: 6, 6: 3}
    for hour, expected_b in cases.items():
        birth = BirthInput(2000, 1, 1, hour)
        hp = chart.hour_pillar(birth, Convention(), day_index=0)
        assert hp.branch == expected_b


def test_hour_stem_wuzi_dun():
    # 甲日子时 → 甲子（甲己还加甲）；day_index=0 即甲子日
    birth = BirthInput(2000, 1, 1, 0)
    hp = chart.hour_pillar(birth, Convention(), day_index=0)
    assert (hp.stem, hp.branch) == (0, 0)
    # 甲日午时(hb=6)：子时干0甲 + 6 = 庚
    birth_noon = BirthInput(2000, 1, 1, 12)
    hp_noon = chart.hour_pillar(birth_noon, Convention(), day_index=0)
    assert hp_noon.stem == 6  # 庚


# ---- 端到端 ----

def test_compute_chart_end_to_end():
    birth = BirthInput(1984, 2, 15, 12, gender="男")
    c = compute_chart(birth)
    assert c.year.name == "甲子"
    assert c.month.name == "丙寅"
    # 所有柱合法
    for p in c.pillars:
        s, b = p.stem, p.branch
        assert s % 2 == b % 2
    assert c.day_master == c.day.stem


# ---- 大运方向（docs/06 §5）----

def test_dayun_direction_yang_male_forward():
    # 甲子年（阳年）男 → 顺行：从月柱 +1
    birth = BirthInput(1984, 2, 15, 12, gender="男")
    c = compute_chart(birth)
    dy = compute_dayun(c, birth)
    # 顺行第一步 = month.index + 1
    assert dy.sequence[0].index == (c.month.index + 1) % 60
    assert len(dy.sequence) == 8


def test_dayun_direction_yin_male_backward():
    # 乙丑年（阴年）男 → 逆行：月柱 -1
    birth = BirthInput(1985, 2, 15, 12, gender="男")
    c = compute_chart(birth)
    # 1985 立春后 → 乙丑年（干1阴）
    assert c.year.stem == 1
    dy = compute_dayun(c, birth)
    assert dy.sequence[0].index == (c.month.index - 1) % 60


# ---- 起运岁（精确）与流年（docs/06 §5）----

def test_precise_start_age(monkeypatch):
    pytest.importorskip("lunar_python")
    from cbcm.precise import PreciseSolarTermResolver
    r = PreciseSolarTermResolver()
    # 1984-02-15 12:00 男：甲子年阳男顺行，下一节为惊蛰(~3/5)，约 18-19 天 → ~6 岁
    birth = BirthInput(1984, 2, 15, 12, gender="男")
    c = compute_chart(birth, resolver=r)
    dy = compute_dayun(c, birth, resolver=r)
    assert 4 <= dy.start_age <= 8
    assert isinstance(dy.start_age, int)


def test_liunian_sequence():
    from cbcm import compute_liunian
    seq = compute_liunian(2024, 4)
    assert [y for y, _ in seq] == [2024, 2025, 2026, 2027]
    # 2024 甲辰, 2025 乙巳, 2026 丙午, 2027 丁未
    assert [p.name for _, p in seq] == ["甲辰", "乙巳", "丙午", "丁未"]
