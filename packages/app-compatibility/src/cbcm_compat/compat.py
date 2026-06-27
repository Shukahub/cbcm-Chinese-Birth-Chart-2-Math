"""合婚：两张命盘的关系分析（消费者）。

⚠️ 含经验断言（生肖/五行合婚断法），未经统计验证，仅供玩乐探索。
按 docs/01：经验断言只在本应用层。所有关系运算复用 cbcm-core（无新公理）。
"""

from __future__ import annotations

from cbcm import compute_chart, notation, operators, wuxing
from cbcm.schemas import BirthInput, Chart, Convention

_DISCLAIMER = "本合婚分析基于传统断法的探索性映射，未经统计验证，仅供玩乐探索。"


def branch_relation(b1: int, b2: int) -> str:
    """两地支关系（复用 07 算子）：三合 > 六合 > 相冲 > 相害 > 相刑 > 无。"""
    if operators.three_harmony_coset(b1) == operators.three_harmony_coset(b2):
        return "三合"
    if operators.branch_combine(b1) == b2:
        return "六合"
    if operators.branch_clash(b1) == b2:
        return "相冲"
    if operators.branch_harm(b1) == b2:
        return "相害"
    if operators.xing(b1, b2) or operators.xing(b2, b1):
        return "相刑"
    return "无明显刑冲合害"


def _daymaster_relation(a: Chart, b: Chart) -> tuple[int, str]:
    wa = wuxing.stem_wuxing(a.day_master)
    wb = wuxing.stem_wuxing(b.day_master)
    r = wuxing.rel(wa, wb)
    return r, wuxing.relation_name(r)


def _complement(a: Chart, b: Chart) -> dict:
    """五行互补：A 之缺行是否为 B 之旺行。"""
    sa = operators.wuxing_strength(a)
    sb = operators.wuxing_strength(b)
    a_lack = sa.index(min(sa))
    b_lack = sb.index(min(sb))
    a_strong = sa.index(max(sa))
    b_strong = sb.index(max(sb))
    notes = []
    if a_lack == b_strong:
        notes.append(f"A 缺 {notation.wuxing_name(a_lack)} 而 B 旺之 → B 补 A")
    if b_lack == a_strong:
        notes.append(f"B 缺 {notation.wuxing_name(b_lack)} 而 A 旺之 → A 补 B")
    if a_strong == b_strong:
        notes.append(f"双方同旺 {notation.wuxing_name(a_strong)}（可能争旺）")
    return {
        "a_balance": {notation.wuxing_name(i): round(sa[i], 2) for i in range(5)},
        "b_balance": {notation.wuxing_name(i): round(sb[i], 2) for i in range(5)},
        "notes": notes or ["无明显互补或争旺"],
    }


# 关系 → 分值（粗略断法权重）
_REL_SCORE: dict[str, int] = {
    "三合": 3, "六合": 2, "无明显刑冲合害": 0, "相刑": -2, "相害": -2, "相冲": -3,
}
# 日主五行关系 → 分值（相生/比和为吉，相克为忌）
_DM_SCORE: dict[int, int] = {
    wuxing.REL_BIHE: 2, wuxing.REL_SHENG: 2, wuxing.REL_SHENGI: 1,
    wuxing.REL_KE: -1, wuxing.REL_KEI: -1,
}


def analyze(a: BirthInput, b: BirthInput, conv: Convention | None = None) -> dict:
    """两张命盘 → 合婚分析。"""
    conv = conv or Convention()
    ca = compute_chart(a, conv)
    cb = compute_chart(b, conv)

    zodiac = branch_relation(ca.year.branch, cb.year.branch)        # 生肖（年支）
    spouse = branch_relation(ca.day.branch, cb.day.branch)          # 日支（夫妻宫）
    dm_r, dm_name = _daymaster_relation(ca, cb)                     # 日主五行

    score = _REL_SCORE.get(zodiac, 0) + _REL_SCORE.get(spouse, 0) + _DM_SCORE.get(dm_r, 0)

    return {
        "disclaimer": _DISCLAIMER,
        "a": _person(ca), "b": _person(cb),
        "relations": {
            "zodiac": {"relation": zodiac, "detail": f"{notation.branch_name(ca.year.branch)} ↔ {notation.branch_name(cb.year.branch)}"},
            "spouse_palace": {"relation": spouse, "detail": f"日支 {notation.branch_name(ca.day.branch)} ↔ {notation.branch_name(cb.day.branch)}"},
            "day_master": {"relation": dm_name, "detail": f"{notation.stem_name(ca.day_master)} ↔ {notation.stem_name(cb.day_master)}"},
        },
        "complement": _complement(ca, cb),
        "score": score,  # 越高越合（断法占位，非验证）
        "verdict": _verdict(score),
    }


def _person(c: Chart) -> dict:
    return {
        "chart": f"{c.year.name} {c.month.name} {c.day.name} {c.hour.name}",
        "day_master": f"{notation.stem_name(c.day_master)}（{notation.wuxing_name(wuxing.stem_wuxing(c.day_master))}）",
        "zodiac": notation.ZODIAC[c.year.branch],
    }


def _verdict(score: int) -> str:
    if score >= 5:
        return "传统断法看：较为相合"
    if score >= 2:
        return "传统断法看：中等，可处"
    if score >= -1:
        return "传统断法看：平平"
    return "传统断法看：刑冲较多，需磨合"


def to_text(r: dict) -> str:
    lines = [
        "== 合婚分析（探索性）==",
        f"A：{r['a']['chart']}  日主{r['a']['day_master']}  生肖{r['a']['zodiac']}",
        f"B：{r['b']['chart']}  日主{r['b']['day_master']}  生肖{r['b']['zodiac']}",
        f"生肖（年支）：{r['relations']['zodiac']['relation']}　{r['relations']['zodiac']['detail']}",
        f"夫妻宫（日支）：{r['relations']['spouse_palace']['relation']}　{r['relations']['spouse_palace']['detail']}",
        f"日主五行：{r['relations']['day_master']['relation']}　{r['relations']['day_master']['detail']}",
        f"五行互补：{'; '.join(r['complement']['notes'])}",
        f"综合评分：{r['score']}（断法占位）　{r['verdict']}",
        "",
        f"⚠ {r['disclaimer']}",
    ]
    return "\n".join(lines)
