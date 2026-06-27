"""app-dateselect 冒烟 + 排序测试。"""

from datetime import date

from cbcm import BirthInput, compute_chart
from cbcm.chart import ApproximateSolarTermResolver
from cbcm_dateselect import select


def _anchor():
    return compute_chart(BirthInput(1984, 2, 15, 12, gender="男"))


def test_evaluate_structure():
    r = select.evaluate(date(2026, 6, 6), _anchor(), ApproximateSolarTermResolver())
    assert {"date", "pillar", "zodiac", "score", "reasons"} <= set(r.keys())
    assert isinstance(r["score"], int)


def test_search_sorted_descending_and_length():
    res = select.search(2026, 6, _anchor(), top_n=5)
    assert len(res) == 5
    scores = [r["score"] for r in res]
    assert scores == sorted(scores, reverse=True)


def test_search_custom_top_n():
    res = select.search(2026, 1, _anchor(), top_n=3)
    assert len(res) == 3


def test_to_text_runs():
    res = select.search(2026, 6, _anchor(), top_n=3)
    txt = select.to_text(res)
    assert "择日" in txt and "探索性" in txt
