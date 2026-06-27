"""数据结构：BirthInput / Convention / Pillar / Chart（对应 docs/06-bazi.md）。

内核与应用共享的 schema。应用读取 TOML → 构造 BirthInput → 交给 chart.py 排盘。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from . import ganzhi, notation


# ---- 干支柱 ----

@dataclass(frozen=True)
class Pillar:
    """一柱：Z_60 中的一个元素。"""
    index: int  # 0..59（甲子=0，癸亥=59）

    def __post_init__(self) -> None:
        object.__setattr__(self, "index", self.index % ganzhi.N_CYCLE)

    @property
    def stem(self) -> int:
        return ganzhi.pillar_from_index(self.index)[0]

    @property
    def branch(self) -> int:
        return ganzhi.pillar_from_index(self.index)[1]

    @property
    def name(self) -> str:
        s, b = ganzhi.pillar_from_index(self.index)
        return notation.pillar_name(s, b)

    @classmethod
    def from_stem_branch(cls, stem: int, branch: int) -> "Pillar":
        return cls(ganzhi.index_from_pillar(stem, branch))

    @classmethod
    def from_index(cls, index: int) -> "Pillar":
        return cls(index)


@dataclass(frozen=True)
class Chart:
    """八字命盘 = 四柱（年月日时各一柱）。"""
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar

    @property
    def day_master(self) -> int:
        """日主 = 日柱天干。"""
        return self.day.stem

    @property
    def pillars(self) -> tuple[Pillar, Pillar, Pillar, Pillar]:
        return (self.year, self.month, self.day, self.hour)


# ---- 大运 ----

@dataclass(frozen=True)
class Dayun:
    """大运：从月柱派生的时间轴（docs/06 §5）。"""
    start_age: int
    sequence: tuple[Pillar, ...]  # 沿 Z_60 顺序或逆序的各步


# ---- 输入与约定 ----

Gender = Literal["男", "女"]


@dataclass(frozen=True)
class BirthInput:
    """出生时空坐标（docs/06 §3 输入空间 I）。"""
    year: int
    month: int
    day: int
    hour: int
    minute: int = 0
    longitude: float | None = None  # 经度，用于真太阳时修正；None=不平移
    gender: Gender = "男"

    @classmethod
    def from_dict(cls, d: dict) -> "BirthInput":
        return cls(
            year=int(d["year"]),
            month=int(d["month"]),
            day=int(d["day"]),
            hour=int(d["hour"]),
            minute=int(d.get("minute", 0)),
            longitude=d.get("longitude"),
            gender=d.get("gender", "男"),
        )

    @classmethod
    def from_toml(cls, path: str | Path) -> "BirthInput":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls.from_dict(data.get("birth", data))


@dataclass(frozen=True)
class Convention:
    """排盘的开放约定开关（docs/06 §6）。便于敏感性分析。"""
    year_boundary: Literal["lichun", "lunar_newyear"] = "lichun"
    solar_term_precision: Literal["approximate", "precise"] = "approximate"
    zi_hour_crossday: bool = True  # True: 23:00 后算次日（早子时）
    true_solar_time: bool = False  # True: 按经度做真太阳时修正
    dayun_step_years: int = 10
    dayun_days_per_year: float = 3.0  # 起运折算：3 日 = 1 岁

    @classmethod
    def from_dict(cls, d: dict | None) -> "Convention":
        if not d:
            return cls()
        kwargs = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**kwargs)
