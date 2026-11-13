#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Refresh the parameter table inside docs/chapters/07_parameters_and_provenance.md from the shipped defaults (``make param-table``)."""
from __future__ import annotations

import pathlib
import re

import bolts

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "chapters" / "07_parameters_and_provenance.md"
START, END = "<!-- PARAMS:START -->", "<!-- PARAMS:END -->"


def main() -> None:
    ps = bolts.load_parameters()
    text = DOC.read_text()
    block = f"{START}\n{ps.table_md()}\n{END}"
    DOC.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S))
    print(f"updated {DOC.name}: {ps.counts()}")


if __name__ == "__main__":
    main()
