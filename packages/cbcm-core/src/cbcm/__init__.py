"""cbcm-core：中国传统生辰八字/天干地支/五行/易经的代数内核（应用无关）。

对应文档 docs/03~07。一切"经验断言"应留在应用层，本内核只提供纯代数对象与排盘。
"""

from . import notation, ganzhi, wuxing, yijing, operators, chart, schemas, precise
from .schemas import BirthInput, Chart, Convention, Dayun, Pillar
from .chart import compute_chart, compute_dayun, compute_liunian, ApproximateSolarTermResolver, SolarTermResolver

__all__ = [
    "notation", "ganzhi", "wuxing", "yijing", "operators", "chart", "schemas", "precise",
    "BirthInput", "Chart", "Convention", "Dayun", "Pillar",
    "compute_chart", "compute_dayun", "compute_liunian",
    "ApproximateSolarTermResolver", "SolarTermResolver",
]

__version__ = "0.1.0"
