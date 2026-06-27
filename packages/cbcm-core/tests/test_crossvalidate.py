"""端到端交叉验证：我们的排盘 vs lunar_python（权威参考）。

逐柱（年/月/日/时）比对随机日期，验证 docs/06 排盘层正确性。
这是历法层"信任缺口"的最终补丁。
"""

import random

import pytest

lunar_python = pytest.importorskip("lunar_python")
from lunar_python import Solar

from cbcm import BirthInput, Convention, compute_chart
from cbcm.precise import PreciseSolarTermResolver


def _lunar_pillars(y, mo, d, h, mi):
    l = Solar.fromYmdHms(y, mo, d, h, mi, 0).getLunar()
    return (
        l.getYearInGanZhiExact(),
        l.getMonthInGanZhiExact(),
        l.getDayInGanZhi(),
        l.getTimeInGanZhi(),
    )


def _ours(y, mo, d, h, mi):
    birth = BirthInput(y, mo, d, h, mi)
    c = compute_chart(birth, Convention(), resolver=PreciseSolarTermResolver())
    return (c.year.name, c.month.name, c.day.name, c.hour.name)


@pytest.mark.parametrize("y,mo,d,h,mi", [
    (2024, 2, 4, 12, 0),   # 立春前：癸卯/乙丑
    (2024, 2, 4, 18, 0),   # 立春后：甲辰/丙寅
    (2024, 3, 15, 23, 30), # 子时跨日：归次日
    (1984, 2, 15, 12, 0),  # 甲子年丙寅月
])
def test_known_boundary_dates(y, mo, d, h, mi):
    assert _ours(y, mo, d, h, mi) == _lunar_pillars(y, mo, d, h,mi)


def test_random_dates_end_to_end():
    rng = random.Random(20240204)
    failures = []
    for _ in range(300):
        y = rng.randint(1960, 2030)
        mo = rng.randint(1, 12)
        d = rng.randint(1, 28)
        h = rng.randint(0, 23)
        mi = rng.randint(0, 59)
        got = _ours(y, mo, d, h, mi)
        exp = _lunar_pillars(y, mo, d, h, mi)
        if got != exp:
            failures.append((y, mo, d, h, mi, got, exp))
    assert not failures, f"{len(failures)} 处不符，前 3：{failures[:3]}"
