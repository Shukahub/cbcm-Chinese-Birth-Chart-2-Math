"""算子层属性测试（验证 docs/07-operators.md）。"""

import pytest

from cbcm import ganzhi, operators, wuxing
from cbcm.schemas import Chart, Pillar


# ---- 十神（docs/07 §2）----

def test_ten_gods_for_jia_day_master():
    # 日主甲(0,阳木)：全盘十神对应表（docs/07 §2 校验表）
    expected = {
        0: "比肩", 1: "劫财", 2: "食神", 3: "伤官", 4: "偏财",
        5: "正财", 6: "七杀", 7: "正官", 8: "偏印", 9: "正印",
    }
    for other, god in expected.items():
        assert operators.ten_god(0, other) == god


def test_ten_god_is_symmetric_in_category():
    assert operators.ten_god(2, 2) == "比肩"  # 丙对丙
    assert operators.ten_god(2, 3) == "劫财"  # 丙对丁


def test_ten_gods_count_is_10():
    all_gods = set()
    for a in range(10):
        for b in range(10):
            all_gods.add(operators.ten_god(a, b))
    assert all_gods == set(operators.TEN_GODS)
    assert len(all_gods) == 10


# ---- 地支关系：群运算型（docs/07 §3.1, §3.2）----

@pytest.mark.parametrize("fn", [operators.branch_clash, operators.branch_combine, operators.branch_harm])
def test_branch_relations_are_involutions(fn):
    for b in range(12):
        assert fn(fn(b)) == b


def test_branch_clash_pairs():
    expected = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11}  # 子午丑未寅申卯酉辰戌巳亥
    for b, target in expected.items():
        assert operators.branch_clash(b) == target


def test_branch_combine_pairs():
    expected = {0: 1, 2: 11, 3: 10, 4: 9, 5: 8, 6: 7}  # 和≡1
    for b, target in expected.items():
        assert operators.branch_combine(b) == target


def test_branch_harm_pairs():
    expected = {0: 7, 1: 6, 2: 5, 3: 4, 8: 11, 9: 10}  # 和≡7
    for b, target in expected.items():
        assert operators.branch_harm(b) == target


def test_three_harmony_cosets_partition_z12():
    cosets = {}
    for b in range(12):
        cosets.setdefault(operators.three_harmony_coset(b), set()).add(b)
    assert set(cosets.keys()) == {0, 1, 2, 3}
    for members in cosets.values():
        assert len(members) == 3
    union = set().union(*cosets.values())
    assert union == set(range(12))


def test_three_harmony_members_and_huashen():
    assert set(operators.three_harmony_members(0)) == {0, 4, 8}   # 申子辰 → 水
    assert operators.three_harmony_huashen(0) == 4
    assert set(operators.three_harmony_members(2)) == {2, 6, 10}  # 寅午戌 → 火
    assert operators.three_harmony_huashen(2) == 1
    assert operators.three_harmony_huashen(1) == 3   # 巳酉丑 → 金
    assert operators.three_harmony_huashen(3) == 0   # 亥卯未 → 木


def test_three_direction_groups_partition_z12():
    groups = {}
    for b in range(12):
        groups.setdefault(operators.three_direction_group(b), set()).add(b)
    assert len(groups) == 4
    for g in groups.values():
        assert len(g) == 3


def test_three_direction_members():
    assert operators.three_direction_members(0) == (2, 3, 4)  # 寅卯辰 东方木
    assert operators.three_direction_members(3) == (11, 0, 1)  # 亥子丑 北方水


# ---- 刑/破（查表型，docs/07 §3.3）----

def test_xing_edges():
    assert operators.xing(2, 5) and operators.xing(5, 8) and operators.xing(8, 2)  # 寅巳申
    assert operators.xing(0, 3) and operators.xing(3, 0)  # 子卯互刑
    assert operators.xing(4, 4) and operators.xing(6, 6)  # 自刑
    assert not operators.xing(1, 2)


def test_po_pairs():
    assert operators.po(0, 9)   # 子酉破
    assert operators.po(5, 8)   # 巳申破
    assert operators.po(9, 0)   # 无向
    assert not operators.po(0, 6)


# ---- 纳音（docs/07 §4）----

def test_nayin_covers_all_60():
    names = set()
    wxs = set()
    for k in range(60):
        names.add(operators.nayin_name(k))
        wxs.add(operators.nayin_wuxing(k))
    assert len(names) == 30
    assert operators.nayin_name(0) == "海中金"
    assert operators.nayin_name(58) == "大海水"
    assert wxs == {0, 1, 2, 3, 4}


def test_nayin_wuxing_values():
    assert operators.nayin_wuxing(0) == 3   # 海中金
    assert operators.nayin_wuxing(2) == 1   # 炉中火
    assert operators.nayin_wuxing(4) == 0   # 大林木


# ---- 神煞（docs/07 §5）----

def test_peach_blossom_lands_on_four_upright():
    targets = {operators.peach_blossom(b) for b in range(12)}
    assert targets == {0, 3, 6, 9}  # 四正


def test_horse_lands_on_four_birth():
    targets = {operators.horse(b) for b in range(12)}
    assert targets == {2, 5, 8, 11}  # 四生


def test_peach_horse_table():
    assert operators.peach_blossom(0) == 9   # 水→酉
    assert operators.horse(0) == 2           # 水→寅
    assert operators.peach_blossom(2) == 3   # 火→卯
    assert operators.horse(2) == 8           # 火→申


# ---- 旬空（docs/07 §6）----

def test_vacancy_by_xun():
    assert set(operators.vacancy(7)) == {10, 11}    # 甲子旬 → 戌亥
    assert set(operators.vacancy(15)) == {8, 9}     # 甲戌旬 → 申酉
    assert set(operators.vacancy(55)) == {0, 1}     # 甲寅旬 → 子丑


def test_vacancy_two_distinct_branches():
    for k in range(60):
        a, b = operators.vacancy(k)
        assert a != b
        assert 0 <= a < 12 and 0 <= b < 12


# ---- 藏干 + 完整十神（docs/07 §2 扩展）----

def _sample_chart():
    # 甲子 / 丙寅 / 己卯 / 庚午
    return Chart(
        year=Pillar.from_stem_branch(0, 0),
        month=Pillar.from_stem_branch(2, 2),
        day=Pillar.from_stem_branch(5, 3),
        hour=Pillar.from_stem_branch(6, 6),
    )


def test_hidden_stems_table():
    assert operators.hidden_stems(0) == ((9, 1.0),)               # 子：癸
    assert [s for s, _ in operators.hidden_stems(2)] == [0, 2, 4]  # 寅：甲丙戊
    assert [s for s, _ in operators.hidden_stems(1)] == [5, 7, 9]  # 丑：己辛癸
    assert [s for s, _ in operators.hidden_stems(11)] == [8, 0]    # 亥：壬甲


def test_hidden_stems_cover_all_branches():
    for b in range(12):
        hs = operators.hidden_stems(b)
        assert len(hs) >= 1
        assert hs[0][1] == 1.0  # 首项恒为本气


def test_wuxing_strength_total():
    chart = _sample_chart()
    s = operators.wuxing_strength(chart)
    expected = 4.0 + sum(w for p in chart.pillars for _, w in operators.hidden_stems(p.branch))
    assert abs(sum(s) - expected) < 1e-9


def test_strength_split_sums_to_total():
    chart = _sample_chart()
    h, d = operators.strength_split(chart)
    assert abs((h + d) - sum(operators.wuxing_strength(chart))) < 1e-9
    assert h > 0 and d > 0


def test_chart_full_gods_day_master_is_self():
    chart = _sample_chart()
    gods = operators.chart_full_gods(chart)
    # 日柱天干对自身 = 比肩
    assert gods["day"][0]["god"] == "比肩"
    # 每柱至少含天干 + 本气藏干
    for label in ("year", "month", "day", "hour"):
        assert len(gods[label]) >= 2
        assert gods[label][0]["part"] == "天干"
