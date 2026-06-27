"""cbcm-personality CLI：读取 TOML → 排盘 → 性格画像。"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from cbcm import compute_chart
from cbcm.schemas import BirthInput, Convention

from . import interpret


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("用法：python -m cbcm_personality <input.toml> [--json]", file=sys.stderr)
        return 2

    toml_path = Path(argv[0])
    as_json = "--json" in argv

    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    birth = BirthInput.from_dict(data["birth"])
    conv = Convention.from_dict(data.get("convention"))

    chart = compute_chart(birth, conv)
    p = interpret.profile(chart)

    if as_json:
        print(json.dumps(p, ensure_ascii=False, indent=2))
    else:
        print(interpret.to_text(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
