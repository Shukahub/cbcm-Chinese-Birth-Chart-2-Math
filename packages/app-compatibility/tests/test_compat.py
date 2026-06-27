"""app-compatibility 冒烟 + 关系测试。"""

from cbcm import BirthInput
from cbcm_compat import compat


def test_branch_relation_cases():
    assert compat.branch_relation(0, 1) == "六合"   # 子丑合
    assert compat.branch_relation(0, 6) == "相冲"   # 子午冲
    assert compat.branch_relation(2, 6) == "三合"   # 寅午（寅午戌同局）
    assert compat.branch_relation(0, 7) == "相害"   # 子未害


def test_analyze_structure():
    a = BirthInput(1984, 2, 15, 12, gender="男")
    b = BirthInput(1986, 7, 20, 8, gender="女")
    r = compat.analyze(a, b)
    assert "disclaimer" in r and "统计验证" in r["disclaimer"]
    assert set(r["relations"].keys()) == {"zodiac", "spouse_palace", "day_master"}
    assert isinstance(r["score"], int)
    assert r["a"]["day_master"] and r["b"]["day_master"]
    assert "verdict" in r


def test_to_text_runs():
    a = BirthInput(1990, 1, 1, 6, gender="男")
    b = BirthInput(1992, 8, 8, 18, gender="女")
    txt = compat.to_text(compat.analyze(a, b))
    assert "合婚分析" in txt and "探索性" in txt
