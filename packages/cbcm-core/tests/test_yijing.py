"""易经代数属性测试（验证 docs/05-yijing.md）。"""

from cbcm import yijing


def test_counts():
    assert len(yijing.trigrams()) == 8        # F_2^3
    assert len(yijing.hexagrams()) == 64      # F_2^6
    assert yijing.ALL_ONES_HEX == 63


def test_bits_roundtrip():
    for h in range(64):
        bits = yijing.to_bits(h)
        assert yijing.from_bits(bits) == h
        assert len(bits) == 6


def test_cuogua_is_involution():
    # 错卦 = 全翻，作用两次还原
    for h in range(64):
        assert yijing.cuogua(yijing.cuogua(h)) == h
    # 乾(63) ↔ 坤(0)
    assert yijing.cuogua(63) == 0
    assert yijing.cuogua(0) == 63


def test_zonggua_is_involution():
    # 综卦 = 位序反转，作用两次还原
    for h in range(64):
        assert yijing.zonggua(yijing.zonggua(h)) == h


def test_change_yao_flips_one_bit():
    for h in range(64):
        for pos in range(6):
            changed = yijing.change_yao(h, pos)
            # 仅该位不同
            diff = h ^ changed
            assert diff == (1 << pos)
            assert yijing.change_yao(changed, pos) == h  # 再变回来


def test_trigram_composition():
    # 六十四卦 = 下卦(低3位) ⊕ 上卦(高3位)
    for h in range(64):
        lo = yijing.lower_trigram(h)
        up = yijing.upper_trigram(h)
        assert (up << 3) | lo == h
