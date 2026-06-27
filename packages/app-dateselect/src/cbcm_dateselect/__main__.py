"""cbcm-dateselect CLI：读 TOML（当事人 + 范围）→ 吉日排序。"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from cbcm import compute_chart
from cbcm.schemas import BirthInput, Convention

from . import select


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("用法：python -m cbcm_dateselect <input.toml> [--json]", file=sys.stderr)
        return 2

    with open(Path(argv[0]), "rb") as f:
        data = tomllib.load(f)
    birth = BirthInput.from_dict(data["anchor"])
    conv = Convention.from_dict(data.get("convention"))
    rng = data["range"]
    top_n = data.get("options", {}).get("top_n", 5)

    chart = compute_chart(birth, conv)
    results = select.search(rng["year"], rng["month"], chart, top_n=top_n)

    if "--json" in argv:
        print(json.dumps({"disclaimer": select._DISCLAIMER, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        print(select.to_text(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
