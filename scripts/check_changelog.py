#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Pre-commit hook: a commit that changes the package (src/bolts) must also change CHANGELOG.md, and CHANGELOG.md must keep an
"Unreleased" section. Bypass for a commit with no user-visible change: ``SKIP=changelog git commit ...``."""
from __future__ import annotations

import pathlib
import subprocess
import sys


def staged() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True).stdout
    return [x for x in out.splitlines() if x]


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    text = (root / "CHANGELOG.md").read_text()
    if "## [Unreleased]" not in text:
        print("CHANGELOG.md must keep a '## [Unreleased]' section")
        return 1
    files = staged()
    touched_pkg = any(f.startswith("src/bolts/") for f in files)
    if touched_pkg and "CHANGELOG.md" not in files:
        print("src/bolts changed but CHANGELOG.md did not: add a line under '## [Unreleased]' (or SKIP=changelog)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
