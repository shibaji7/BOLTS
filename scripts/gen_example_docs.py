#!/usr/bin/env python
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Write one documentation page per experiment (docs/examples/NN_name.md) and an index, from the example scripts' docstrings.

Each page has the experiment's question, input and expectation (its docstring), the figures it produced, how to run it, a link to the source on GitHub
and the full source (included from the script, so it cannot drift). Figures are copied from ``outputs/examples/<stem>/`` into ``docs/examples/img/`` and
committed, so the docs build does not need to run the experiments. Run by ``make example-docs`` (which runs the experiments first)."""
from __future__ import annotations

import ast
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "gmd"
OUTPUTS = ROOT / "outputs" / "examples"
DOCS = ROOT / "docs" / "examples"
IMG = DOCS / "img"
REPO = "https://github.com/shibaji7/BOLTS/blob/main"
LABELS = ("Question", "Input", "Expect", "Output", "Findings", "Finding", "Method", "Caveat")


def scripts() -> list[pathlib.Path]:
    """The numbered experiment scripts, in order."""
    return sorted(p for p in EXAMPLES.glob("[0-9][0-9]_*.py"))


def split_doc(doc: str) -> tuple[str, str]:
    """Title (the text before the first colon-labelled part) and the body of an experiment docstring, with the labels in bold."""
    flat = re.sub(r"[ \t]*\n[ \t]*(?!\n)", " ", doc.strip())            # a single newline inside a paragraph is a space
    head, _, rest = flat.partition(" Question:")
    if not rest:
        head, rest = flat.split(". ", 1) if ". " in flat else (flat, "")
        rest = rest.strip()
    else:
        rest = "Question:" + rest
    title = head.strip().rstrip(".")
    body = re.sub(r"(?<![\w`])(" + "|".join(LABELS) + r"):", r"\n\n**\1:**", rest).strip()
    return title, body


def page(script: pathlib.Path, images: list[str]) -> str:
    """The Markdown of one experiment page."""
    doc = ast.get_docstring(ast.parse(script.read_text())) or script.stem
    title, body = split_doc(doc)
    lines = [f"# {title}", "", body, ""]
    if images:
        lines += ["## Figures", ""]
        for name in images:
            alt = name.split("_", 2)[2].rsplit(".", 1)[0].replace("_", " ")          # the figure file name without the experiment prefix
            lines += [f"![{alt}](img/{name})", ""]
    rel = script.relative_to(ROOT).as_posix()
    lines += ["## Run it", "", "```bash", f"python {rel}", "```", "",
              f"The figures and tables are written to `outputs/examples/{script.stem}/`. Source on GitHub: [{rel}]({REPO}/{rel}).", "",
              '??? note "Full source"', "", "    ```python", f'    --8<-- "{rel}"', "    ```", ""]
    return "\n".join(lines)


def main() -> None:
    """Regenerate every page in docs/examples."""
    DOCS.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    for old in DOCS.glob("*.md"):
        old.unlink()
    rows = []
    for s in scripts():
        images = []
        for png in sorted((OUTPUTS / s.stem).glob("*.png")):
            name = f"{s.stem}_{png.name}"
            shutil.copy(png, IMG / name)
            images.append(name)
        for kept in IMG.glob(f"{s.stem}_*.png"):             # drop figures an experiment no longer makes
            if kept.name not in images:
                kept.unlink()
        if not images:
            images = [p.name for p in sorted(IMG.glob(f"{s.stem}_*.png"))]      # outputs not present: keep the committed ones
        (DOCS / f"{s.stem}.md").write_text(page(s, images))
        title, _ = split_doc(ast.get_docstring(ast.parse(s.read_text())) or s.stem)
        rows.append(f"| [{s.stem}]({s.stem}.md) | {title} |")
    index = ["# Examples", "",
             "Runnable experiments in `examples/gmd/`. Each page gives the question, the input, what to expect, the figures, the command and the full source. "
             "They need the `plots` extra for figures (`pip install bolts[plots]`) and, for experiment 6, the `ngspice` binary.", "",
             "```bash", "make examples            # run all of them; outputs go to outputs/examples/", "```", "",
             "| Experiment | What it answers |", "|---|---|", *rows, "",
             "## Planned", "",
             "Lightning experiments (`examples/lightning/`) and branching-unit experiments (`examples/branching_units/`) are documented slots: see "
             "[Lightning](../chapters/15_lightning.md) and [Branching units](../chapters/14_branching_units.md).", ""]
    (DOCS / "index.md").write_text("\n".join(index))
    print(f"wrote {len(list(DOCS.glob('*.md')))} pages in {DOCS}")


if __name__ == "__main__":
    main()
