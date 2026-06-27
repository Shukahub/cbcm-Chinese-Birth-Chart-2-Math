"""app-personality 冒烟测试：端到端跑通 Chart → 画像。

注：日柱绝对值依赖 docs/06 §6 的 anchor 校准，故只测结构性，不断言具体日柱。
"""

from cbcm import compute_chart
from cbcm.schemas import BirthInput
from cbcm import notation

from cbcm_personality import interpret


def test_profile_structure():
    birth = BirthInput(1984, 2, 15, 12, gender="男")
    chart = compute_chart(birth)
    p = interpret.profile(chart)

    assert "day_master" in p
    dm = p["day_master"]
    assert dm["stem"] in notation.STEMS
    assert dm["wuxing"] in notation.WUXING
    # 一致性：偶序号干为阳
    assert dm["yinyang"] == ("阳" if notation.STEMS.index(dm["stem"]) % 2 == 0 else "阴")

    assert set(p["wuxing_balance"].keys()) == {"木", "火", "土", "金", "水"}
    assert sum(p["wuxing_balance"].values()) > 4.0  # 含藏干权重，故大于四天干数
    assert "disclaimer" in p and "统计验证" in p["disclaimer"]
    assert set(p["stem_gods"].keys()) == {"year", "month", "hour"}
    assert "strength_detail" in p
    assert set(p["full_gods"].keys()) == {"year", "month", "day", "hour"}


def test_to_text_contains_disclaimer():
    birth = BirthInput(1990, 6, 15, 8, gender="女")
    chart = compute_chart(birth)
    text = interpret.to_text(interpret.profile(chart))
    assert "探索性" in text
