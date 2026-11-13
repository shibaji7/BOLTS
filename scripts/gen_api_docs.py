#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Write one API page per subpackage (docs/api/<subpackage>.md) with a mkdocstrings block for each module.

Run by ``make api-docs``; the generated pages are committed so the docs build needs no extra plugin."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "src" / "bolts"
OUT = ROOT / "docs" / "api"

TITLES = {"": "Top level", "config": "config: parameters with provenance", "waveforms": "waveforms: records and pulses",
          "space_weather": "space_weather: GMD forcing", "properties": "properties: cable R, L, G, C",
          "elements": "elements: devices that stamp into the circuit", "network": "network: topology and power modes",
          "mna": "mna: the circuit solver", "lines": "lines: transmission-line helpers", "earthing": "earthing: soil, electrodes, GPR",
          "lightning": "lightning (planned)", "metrics": "metrics: what a run is judged by", "damage": "damage: life laws",
          "impact": "impact: optics and terminal", "spice": "spice: export and cross-check", "io": "io: reading and writing",
          "plotting": "plotting: figures in the paper style", "studies": "studies: sweeps and maps",
          "validation": "validation: analytic cases"}


def modules(sub: str) -> list[str]:
    base = PKG / sub if sub else PKG
    pattern = "*.py"
    mods = []
    for f in sorted(base.glob(pattern)):
        if f.name.startswith("_") and f.name != "__init__.py":
            continue
        if f.name == "__init__.py":
            continue
        if not sub and f.name in {"__main__.py"}:
            continue
        mods.append(f"bolts.{sub + '.' if sub else ''}{f.stem}")
    return mods


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    subs = ["", *sorted(p.name for p in PKG.iterdir() if p.is_dir() and not p.name.startswith(("_", "__")) and (p / "__init__.py").exists())]
    index = ["# API reference", "", "The public API is `bolts.api` (re-exported from `bolts`). Every module has its own entry below, grouped by subpackage; "
             "the generated pages are produced by `make api-docs` from the docstrings.", "", "| Subpackage | Modules |", "|---|---|"]
    for sub in subs:
        mods = modules(sub)
        if not mods:
            continue
        name = sub or "core"
        lines = [f"# {TITLES.get(sub, sub)}", ""]
        for m in mods:
            lines += [f"::: {m}", "    options:", "      show_root_heading: true", ""]
        (OUT / f"{name}.md").write_text("\n".join(lines))
        index.append(f"| [{TITLES.get(sub, sub)}]({name}.md) | {len(mods)} |")
    (OUT / "index.md").write_text("\n".join(index) + "\n")
    print(f"wrote {len(list(OUT.glob('*.md')))} pages in {OUT}")


if __name__ == "__main__":
    main()
