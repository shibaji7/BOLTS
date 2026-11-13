#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Pre-commit hook: every Python file under src/, tests/, examples/ and scripts/ must start with the SPDX header and the copyright line."""
from __future__ import annotations

import pathlib
import sys

SPDX = "# SPDX-License-Identifier: LGPL-3.0-or-later"
COPYRIGHT = "# Copyright (C) 2026 Shibaji Chakraborty"
SKIP = {"__main__.py"}


def main(argv: list[str]) -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    files = [pathlib.Path(a) for a in argv] or [p for d in ("src", "tests", "examples", "scripts") for p in (root / d).rglob("*.py")]
    bad = []
    for f in files:
        if f.suffix != ".py" or "egg-info" in str(f):
            continue
        lines = f.read_text().splitlines()
        # allow a shebang before the header
        head = [x for x in lines[:3] if not x.startswith("#!")][:2]
        if head != [SPDX, COPYRIGHT]:
            bad.append(f)
    for f in bad:
        print(f"missing SPDX / copyright header: {f}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
