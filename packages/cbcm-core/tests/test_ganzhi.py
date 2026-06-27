"""干支代数属性测试（验证 docs/03-ganzhi.md）。"""

import pytest

from cbcm import ganzhi, notation


def test_sixty_cycle_has_60_elements():
    pillars = ganzhi.all_pillars()
    assert len(pillars) == 60
    assert len(set(pillars)) == 60  # 无重复


def test_all_pillars_valid_parity():
    # 合法干支对：干支同奇偶
    for s, b in ganzhi.all_pillars():
        assert s % 2 == b % 2


def test_generator_order_is_60():
    # 生成元 (1,1)（甲子前进一）阶 = lcm(10,12) = 60
    seen = set()
    k = 0
    for _ in range(60):
        seen.add(ganzhi.pillar_from_index(k))
        k = ganzhi.advance(k)
    assert len(seen) == 60


def test_cycle_endpoints():
    s0, b0 = ganzhi.pillar_from_index(0)
    assert notation.stem_name(s0) == "甲"
    assert notation.branch_name(b0) == "子"

    s59, b59 = ganzhi.pillar_from_index(59)
    assert notation.stem_name(s59) == "癸"
    assert notation.branch_name(b59) == "亥"


def test_index_pillar_roundtrip():
    for k in range(60):
        s, b = ganzhi.pillar_from_index(k)
        assert ganzhi.index_from_pillar(s, b) == k


def test_invalid_pillar_raises():
    # 甲(0,阳类) 与 丑(1,阴类) 不同阴阳 → 非法
    with pytest.raises(ValueError):
        ganzhi.index_from_pillar(0, 1)
    assert not ganzhi.is_valid_pillar(0, 1)
    assert ganzhi.is_valid_pillar(0, 0)  # 甲子合法


def test_advance_wraps_mod_60():
    assert ganzhi.advance(59) == 0
    assert ganzhi.advance(0, -1) == 59


def test_xun_heads():
    assert ganzhi.XUN_HEADS == [0, 10, 20, 30, 40, 50]
    for k in range(60):
        assert ganzhi.xun_head(k) in {0, 10, 20, 30, 40, 50}
    assert ganzhi.xun_head(7) == 0   # 甲子旬
    assert ganzhi.xun_head(15) == 10  # 甲戌旬
