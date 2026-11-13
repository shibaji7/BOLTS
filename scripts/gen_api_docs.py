#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Write the API reference pages (docs/api/*.md) from the package layout and its docstrings.

Each subpackage page has the subpackage docstring as its introduction, links to the matching chapters, a table of its modules (one line each, stubs
flagged) and an autosummary of its modules (Sphinx writes the page of each module at build time). ``docs/api/index.md`` has the public API at a glance. Run by ``make api-docs``; the generated pages are
committed so the docs build needs no extra plugin."""
from __future__ import annotations

import ast
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

# the chapters that explain each subpackage (file name, title)
CHAPTERS = {
    "": [("00_overview", "Overview"), ("10_run_and_extend", "Run and extend")],
    "config": [("07_parameters_and_provenance", "Parameters and provenance")],
    "waveforms": [("01_storm_to_volts", "From storm to volts")],
    "space_weather": [("01_storm_to_volts", "From storm to volts"), ("06_field_along_the_link", "Field along the link")],
    "properties": [("12_cable_properties", "Cable properties")],
    "elements": [("13_zener_protection", "Zener and protection"), ("04_repeater_and_optics", "Repeater and optics"), ("02_power_feeding", "Power feeding")],
    "network": [("03_circuit_model", "The circuit model"), ("14_branching_units", "Branching units")],
    "mna": [("03_circuit_model", "The circuit model")],
    "lines": [("03_circuit_model", "The circuit model")],
    "earthing": [("16_earthing_damage", "Earthing and damage")],
    "lightning": [("15_lightning", "Lightning")],
    "metrics": [("02_power_feeding", "Power feeding"), ("04_repeater_and_optics", "Repeater and optics")],
    "damage": [("16_earthing_damage", "Earthing and damage")],
    "impact": [("04_repeater_and_optics", "Repeater and optics"), ("05_terminal_and_traffic", "Terminal and traffic")],
    "spice": [("09_validation_and_tests", "Validation and tests")],
    "io": [("10_run_and_extend", "Run and extend")],
    "plotting": [("10_run_and_extend", "Run and extend")],
    "studies": [("10_run_and_extend", "Run and extend")],
    "validation": [("09_validation_and_tests", "Validation and tests")],
}
STUB_WORDS = ("planned", "deferred", "not implemented")


def doc_of(path: pathlib.Path) -> str:
    """The module docstring of a Python file ('' if none)."""
    return ast.get_docstring(ast.parse(path.read_text())) or ""


def first_sentence(doc: str) -> str:
    """The first line of a docstring, shortened to a table cell."""
    line = doc.strip().splitlines()[0].strip() if doc.strip() else ""
    line = line.replace("|", "\\|")
    return line if len(line) <= 150 else line[:147].rstrip() + "..."


def is_stub(doc: str) -> bool:
    """A module whose first words say it is planned, deferred or not implemented."""
    head = " ".join(doc.split()[:40]).lower()
    return any(w in head for w in STUB_WORDS)


def modules(sub: str) -> list[pathlib.Path]:
    """The public module files of a subpackage (or of the top level), sorted by name."""
    base = PKG / sub if sub else PKG
    out = []
    for f in sorted(base.glob("*.py")):
        if f.name.startswith("_") or (not sub and f.name == "__main__.py"):
            continue
        out.append(f)
    return out


def dotted(sub: str, f: pathlib.Path) -> str:
    """Dotted module name of a file."""
    return f"bolts.{sub + '.' if sub else ''}{f.stem}"


def package_section(sub: str) -> str:
    """The Markdown of one subpackage section of the API page: introduction, chapters, stubs and an autosummary of its modules."""
    mods = modules(sub)
    intro = doc_of(PKG / sub / "__init__.py") if sub else ""
    lines = [f"## {TITLES.get(sub, sub)}", ""]
    if intro:
        parts = intro.split("\n\n")
        lines += ["\n\n".join(parts[1:]) if len(parts) > 1 else parts[0], ""]
    chapters = CHAPTERS.get(sub, [])
    if chapters:
        lines += ["**Read first:** " + ", ".join(f"[{t}](../chapters/{c}.md)" for c, t in chapters), ""]
    stubs = [f"`{f.stem}`" for f in mods if is_stub(doc_of(f))]
    if stubs:
        lines += ["*Stubs (documented slots that raise `NotImplementedYet`):* " + ", ".join(stubs), ""]
    # an RST directive inside an eval-rst block: autosummary's stub generator only recognises the RST spelling, not the MyST one
    lines += ["```{eval-rst}", ".. autosummary::", "   :toctree: generated", "   :recursive:", ""]
    lines += [f"   {dotted(sub, f)}" for f in mods]
    lines += ["```", ""]
    return "\n".join(lines)


def api_functions() -> list[tuple[str, str, str]]:
    """The names in ``bolts.api.__all__`` as (name, dotted path of where they are defined, first line of their docstring)."""
    tree = ast.parse((PKG / "api.py").read_text())
    names: list[str] = []
    docs: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "__all__" for t in node.targets):
            names = [e.value for e in node.value.elts]
        if isinstance(node, ast.FunctionDef):
            docs[node.name] = ("bolts.api", ast.get_docstring(node) or "")
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:      # a re-exported name: document it where it is defined
            src = PKG / (node.module.replace(".", "/") + ".py")
            if src.exists():
                for sub in ast.parse(src.read_text()).body:
                    if isinstance(sub, (ast.FunctionDef, ast.ClassDef)) and any(a.name == sub.name for a in node.names):
                        docs[sub.name] = (f"bolts.{node.module}", ast.get_docstring(sub) or "")
    return [(n, docs[n][0], first_sentence(docs[n][1]).replace("``", "`")) for n in names]


INDEX_HEAD = """# API reference

The whole study fits in a handful of functions, `bolts.api`, all re-exported from `bolts`:

```python
import bolts

params = bolts.load_parameters()                                   # shipped defaults, every value with unit, status and source
record = bolts.load_waveform("data/example_vind_1s.csv", params=params)
net = bolts.build_network(params, record)
result = bolts.run_transient(net, params)
summary = bolts.assess(result)                                    # electrical, optical and traffic metrics
```

## Public API at a glance

| Name | What it does |
|---|---|"""


def main() -> None:
    """Regenerate docs/api/index.md (Sphinx autosummary writes the per-module pages at build time)."""
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    subs = ["", *sorted(p.name for p in PKG.iterdir() if p.is_dir() and not p.name.startswith("_") and (p / "__init__.py").exists())]
    out = [INDEX_HEAD]
    for name, where, summary in api_functions():
        role = "py:class" if name[0].isupper() else "py:func"
        out.append(f"| {{{role}}}`{name} <{where}.{name}>` | {summary} |")
    out += ["", "Each section below opens with what the subpackage is for and the chapters that explain it. Click a module for its page: a summary table of its classes and",
            "functions, then every entry with its signature, parameters, return value and a `[source]` link.", ""]
    for sub in subs:
        if modules(sub):
            out.append(package_section(sub))
    out += ["## Conventions", "",
            "- Quantities carry their unit in the name (`r_ohm_per_km`, `dt_s`, `v_tot_V`); no unit objects are used.",
            "- Every parameter is a `Param` with a status (`sourced`, `assumed`, `unknown`, `override`); using an `unknown` one raises `MissingParameter`.",
            "- Stubs raise `NotImplementedYet` with a pointer to the roadmap.",
            "- Equations and sources are in each module docstring; the chapters give the story around them.", ""]
    (OUT / "index.md").write_text("\n".join(out))
    print(f"wrote {OUT / 'index.md'}")


if __name__ == "__main__":
    main()
