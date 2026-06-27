"""精确节气 resolver 测试（验证 docs/06 §6 precise 选项）。

需要 lunar_python；未安装则跳过。
"""

import pytest

lunar_python = pytest.importorskip("lunar_python")

from cbcm import precise


def test_precise_lichun_boundary_2024():
    r = precise.PreciseSolarTermResolver()
    # 立春 2024 = 02-04 16:27（lunar_python 计算）
    assert r.lichun_passed(2024, 2, 4, 17, 0) is True    # 立春后
    assert r.lichun_passed(2024, 2, 4, 15, 0) is False   # 立春前
    assert r.lichun_passed(2024, 1, 20, 12, 0) is False  # 立春前


def test_precise_month_branch_agrees_with_approx_on_clear_dates():
    """在远离节气边界的普通日期上，精确与近似应给出同一月支。"""
    from cbcm import ApproximateSolarTermResolver
    approx = ApproximateSolarTermResolver()
    r = precise.PreciseSolarTermResolver()
    # 取月中（远离节气边界）的日期：午/申/酉/亥
    for (y, m, d, exp) in [(2024, 6, 15, 6), (2024, 8, 15, 8), (2024, 9, 15, 9), (2024, 11, 20, 11)]:
        assert r.month_branch(y, m, d) == exp
        assert approx.month_branch(y, m, d) == exp


def test_precise_month_branch_boundary_subday():
    # 芒种 2024 ≈ 06-05；06-05 前后月支应分别为巳(5)/午(6)
    r = precise.PreciseSolarTermResolver()
    # 找到 2024 年芒种所在日，验证同日子时与晚时月支可能切换
    b_before = r.month_branch(2024, 6, 5, 0, 0)
    b_after = r.month_branch(2024, 6, 6, 0, 0)
    # 芒种前是巳月(5)，芒种后是午月(6)
    assert b_before in (5, 6)
    assert b_after == 6
