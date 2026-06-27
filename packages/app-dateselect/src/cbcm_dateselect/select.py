"""择日：在日历中按干支/五行关系筛选吉日（消费者）。

⚠️ 含经验断法（择吉规则），未经统计验证，仅供玩乐探索。
所有关系运算复用 cbcm-core。
"""

from __future__ import annotations

import calendar
from datetime import date

from cbcm import notation, operators, wuxing
from cbcm.chart import ApproximateSolarTermResolver, SolarTermResolver, day_index_from_date
from cbcm.schemas import Chart, Pillar

_DISCLAIMER = "本择日基于传统断法的探索性映射，未经统计验证，仅供玩乐探索。"


def evaluate(d: date, anchor: Chart, resolver: SolarTermResolver) -> dict:
    """评某一日：日柱干支 vs 当事人年/日支 + 月建 + 日柱内部和谐。"""
    dp = Pillar.from_index(day_index_from_date(d))
    db = dp.branch
    stem_wx = wuxing.stem_wuxing(dp.stem)
    branch_wx = wuxing.stem_wuxing(operators.hidden_stems(db)[0][0])  # 日支本气五行

    mb = resolver.month_branch(d.year, d.month, d.day)  # 该日所在月令
    score = 0
    reasons: list[str] = []

    if operators.branch_clash(db) == mb:
        score -= 3
        reasons.append("日支冲月建（月破）")

    for ab, label in ((anchor.year.branch, "年支"), (anchor.day.branch, "日支")):
        coset_eq = operators.three_harmony_coset(db) == operators.three_harmony_coset(ab)
        if coset_eq:
            score += 2
            reasons.append(f"与当事人{label}三合")
        elif operators.branch_combine(db) == ab:
            score += 1
            reasons.append(f"与当事人{label}六合")
        if operators.branch_clash(db) == ab:
            score -= 2
            reasons.append(f"冲当事人{label}")
        if operators.xing(db, ab):
            score -= 1
            reasons.append(f"刑当事人{label}")

    r = wuxing.rel(stem_wx, branch_wx)
    if r in (wuxing.REL_SHENGI, wuxing.REL_BIHE):  # 日支生干 / 比和 → 得地
        score += 1
        reasons.append("日支生扶日干（得地）")
    elif r == wuxing.REL_KE:
        score -= 1
        reasons.append("日支克日干")

    return {
        "date": d.isoformat(),
        "pillar": dp.name,
        "zodiac": notation.ZODIAC[db],
        "score": score,
        "reasons": reasons or ["无显著吉凶标记"],
    }


def search(year: int, month: int, anchor: Chart, resolver: SolarTermResolver | None = None,
           top_n: int = 5) -> list[dict]:
    """在指定年月内逐日评分，返回分数最高的 top_n 日（降序）。"""
    resolver = resolver or ApproximateSolarTermResolver()
    n_days = calendar.monthrange(year, month)[1]
    results = [evaluate(date(year, month, d), anchor, resolver) for d in range(1, n_days + 1)]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def to_text(items: list[dict]) -> str:
    lines = ["== 择日（探索性）—— 分数高的日子 ==", f"⚠ {_DISCLAIMER}", ""]
    for it in items:
        lines.append(f"{it['date']}  {it['pillar']}（生肖日 {it['zodiac']}）  分 {it['score']}")
        for r in it["reasons"]:
            lines.append(f"    · {r}")
    return "\n".join(lines)
