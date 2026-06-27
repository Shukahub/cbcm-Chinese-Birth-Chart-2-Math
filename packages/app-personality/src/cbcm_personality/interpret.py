"""性格/情志解读层（消费者）。

⚠️ 本模块包含经验断言（五行偏旺→五志倾向等传统对应），未经统计验证，仅供玩乐探索。
按 docs/01 边界：经验断言只活在本应用层，绝不进 cbcm-core。
"""

from __future__ import annotations

from cbcm import notation, operators, wuxing
from cbcm.schemas import Chart

# 五志：五行 → 情志（docs/04 §8 传统对应；经验断言，非验证）
_WUZHI: dict[int, str] = {0: "怒", 1: "喜", 2: "思", 3: "悲", 4: "恐"}

_DISCLAIMER = "本画像为基于传统断法的探索性映射，未经统计验证，仅供玩乐探索。"


def profile(chart: Chart) -> dict:
    """命盘 → 性格/情志画像（dict，可序列化）。"""
    dm = chart.day_master
    dm_wx = wuxing.stem_wuxing(dm)

    # 五行强度（含地支藏干，见 core operators.wuxing_strength）
    strength = operators.wuxing_strength(chart)
    balance = {notation.wuxing_name(i): round(strength[i], 2) for i in range(5)}

    # 日主旺弱：帮身(比劫+印) vs 耗身(食伤+财+官杀)
    help_power, drain_power = operators.strength_split(chart)
    if help_power > drain_power * 1.1:
        dm_strength = "偏旺"
    elif drain_power > help_power * 1.1:
        dm_strength = "偏弱"
    else:
        dm_strength = "中和"

    # 最旺行 → 五志倾向（传统对应，经验断言）
    max_wx = max(range(5), key=lambda i: strength[i])
    wuzhi = _WUZHI[max_wx]

    return {
        "disclaimer": _DISCLAIMER,
        "day_master": {
            "stem": notation.stem_name(dm),
            "wuxing": notation.wuxing_name(dm_wx),
            "yinyang": notation.yinyang_of(dm),
        },
        "chart": {
            "year": chart.year.name,
            "month": chart.month.name,
            "day": chart.day.name,
            "hour": chart.hour.name,
        },
        "wuxing_balance": balance,  # 含藏干权重
        "day_master_strength": dm_strength,
        "strength_detail": {"help_power": round(help_power, 2), "drain_power": round(drain_power, 2)},
        "stem_gods": operators.chart_stem_gods(chart),   # 四天干十神
        "full_gods": operators.chart_full_gods(chart),   # 含藏干十神
        "wuzhi_tendency": f"{notation.wuxing_name(max_wx)}（{wuzhi}）",
    }


def to_text(p: dict) -> str:
    lines = [
        f"== 性格/情志画像（探索性）==",
        f"日主：{p['day_master']['stem']}（{p['day_master']['wuxing']}·{p['day_master']['yinyang']}）",
        f"四柱：{p['chart']['year']} / {p['chart']['month']} / {p['chart']['day']} / {p['chart']['hour']}",
        f"日主旺弱：{p['day_master_strength']}（帮身 {p['strength_detail']['help_power']} : 耗身 {p['strength_detail']['drain_power']}）",
        f"五行强度（含藏干）：{p['wuxing_balance']}",
        f"天干十神：年={p['stem_gods']['year']} 月={p['stem_gods']['month']} 日=日主 时={p['stem_gods']['hour']}",
        f"五志倾向（传统对应，非验证）：{p['wuzhi_tendency']}",
        f"",
        f"⚠ {p['disclaimer']}",
    ]
    return "\n".join(lines)
