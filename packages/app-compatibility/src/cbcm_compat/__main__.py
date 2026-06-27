"""cbcm-compatibility CLI：读 TOML（两人）→ 合婚分析。"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from cbcm.schemas import BirthInput, Convention

from . import compat


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("用法：python -m cbcm_compat <input.toml> [--json]", file=sys.stderr)
        return 2

    with open(Path(argv[0]), "rb") as f:
        data = tomllib.load(f)
    a = BirthInput.from_dict(data["person_a"])
    b = BirthInput.from_dict(data["person_b"])
    conv = Convention.from_dict(data.get("convention"))

    r = compat.analyze(a, b, conv)
    if "--json" in argv:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(compat.to_text(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
