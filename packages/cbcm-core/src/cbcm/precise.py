"""精确节气 resolver（对应 docs/06 §6 的 precise 选项）。

仅用 lunar_python 提供**节气精确时刻**这一外部数据源；月支判定与五虎遁仍由
我们的 chart.py 代数完成（不绕过内核）。需要 `pip install cbcm-core[precise]`。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# 12 节（非中气）→ 月支。寅月起于立春。
_JIE_TO_BRANCH: dict[str, int] = {
    "立春": 2, "惊蛰": 3, "清明": 4, "立夏": 5, "芒种": 6,
    "小暑": 7, "立秋": 8, "白露": 9, "寒露": 10, "立冬": 11,
    "大雪": 0, "小寒": 1,
}


@dataclass(frozen=True)
class PreciseSolarTermResolver:
    """用 lunar_python 的精确节气时刻判定月支与立春年界。"""

    def _terms(self, year: int) -> list[tuple[datetime, int]]:
        """某年 12 节的 (时刻, 月支) 列表。"""
        from lunar_python import Solar  # 延迟导入，保持 core 默认精简
        table = Solar.fromYmd(year, 6, 1).getLunar().getJieQiTable()
        out: list[tuple[datetime, int]] = []
        for name, branch in _JIE_TO_BRANCH.items():
            s = table[name]
            out.append((datetime(s.getYear(), s.getMonth(), s.getDay(), s.getHour(), s.getMinute()), branch))
        return out

    def _sorted_terms(self, year: int) -> list[tuple[datetime, int]]:
        terms = self._terms(year - 1) + self._terms(year) + self._terms(year + 1)
        terms.sort(key=lambda x: x[0])
        return terms

    def month_branch(self, year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> int:
        """精确判定月支：取不晚于目标时刻的最近一个节。"""
        target = datetime(year, month, day, hour, minute)
        branch = 0  # 早于小寒属上年子月
        for inst, b in self._sorted_terms(year):
            if inst <= target:
                branch = b
            else:
                break
        return branch

    def lichun_passed(self, year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> bool:
        """是否已过本年立春（精确时刻）。"""
        terms = self._terms(year)
        lichun = next(inst for inst, b in terms if b == 2)  # 月支 2 = 寅月 = 立春
        return lichun <= datetime(year, month, day, hour, minute)

    def days_to_jie(self, year: int, month: int, day: int, hour: int, minute: int, forward: bool) -> float | None:
        """到下一个(forward)或上一个(逆向)节的天数（精确）。用于起运岁。"""
        target = datetime(year, month, day, hour, minute)
        terms = self._sorted_terms(year)
        if forward:
            nxt = next((inst for inst, _ in terms if inst > target), None)
            return (nxt - target).total_seconds() / 86400 if nxt else None
        prev = None
        for inst, _ in terms:
            if inst < target:
                prev = inst
            else:
                break
        return (target - prev).total_seconds() / 86400 if prev else None
