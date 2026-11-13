# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Plot style shared by every BOLTS figure: the same look as the polar_connect paper figures.

SciencePlots ``science`` + ``vibrant`` (Paul Tol's colour-blind-safe palette), LaTeX text when a TeX toolchain exists (otherwise
``no-latex``), two-column journal widths (AGU/JGR 190 mm), bold ``(a)`` panel labels. Matplotlib and SciencePlots are optional
(``pip install bolts[plots]``); without SciencePlots the same sizes and the same palette are set by hand.
"""
from __future__ import annotations

import shutil

# Paul Tol "vibrant", the cycle SciencePlots ships (colour-blind safe)
TOL = {"blue": "#0077BB", "cyan": "#33BBEE", "teal": "#009988", "orange": "#EE7733",
       "red": "#CC3311", "magenta": "#EE3377", "grey": "#BBBBBB"}
DARK_GREY = "0.35"             # for reference lines and annotations

_USETEX = False               # set by apply(): is LaTeX text on?

DOUBLE_COL_IN = 7.48           # 190 mm
SINGLE_COL_IN = 3.54           # 90 mm


def require_matplotlib():
    """Import pyplot (Agg backend for scripts) or explain how to install it."""
    try:
        import matplotlib
        matplotlib.use("Agg", force=False)
        import matplotlib.pyplot as plt
    except ImportError as e:                      # pragma: no cover
        raise ImportError("plotting needs matplotlib: pip install bolts[plots]") from e
    return plt


def apply() -> bool:
    """Activate the BOLTS figure style. Returns True if LaTeX text rendering is on."""
    global _USETEX
    plt = require_matplotlib()
    import matplotlib as mpl
    # LaTeX text only if the toolchain is there; otherwise SciencePlots' no-latex variant keeps the same look without it
    have_tex = shutil.which("latex") is not None and shutil.which("dvipng") is not None
    try:
        import scienceplots  # noqa: F401  (registers the styles)
        plt.style.use(["science", "vibrant"] + ([] if have_tex else ["no-latex"]))
    except (ImportError, OSError):                # SciencePlots missing: set the essentials by hand
        have_tex = False
        mpl.rcParams.update({"axes.prop_cycle": mpl.cycler(color=[TOL[k] for k in ("blue", "orange", "teal", "red", "cyan", "magenta", "grey")]),
                             "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
                             "legend.frameon": False, "font.family": "serif"})
    # sizes tuned for a 190 mm double-column figure: 8 pt labels, 7 pt ticks, 600 dpi saved files
    mpl.rcParams.update({
        "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 7, "axes.titlesize": 8,
        "savefig.dpi": 600, "figure.dpi": 150,
        "savefig.bbox": "standard",
        "pdf.fonttype": 42, "ps.fonttype": 42,    # embeddable TrueType in journals
    })
    _USETEX = have_tex
    return have_tex


def pct() -> str:
    """The percent sign for axis labels and text: ``\\%`` when LaTeX renders the text (a bare ``%`` starts a LaTeX comment and cuts the label), ``%`` otherwise. Call after :func:`apply`."""
    return "\\%" if _USETEX else "%"


def panel_label(ax, text: str, x: float = 0.0, y: float = 1.0, fontsize: float = 9, **kw) -> None:
    """Bold '(a)'-style panel label just outside the top-left of an axes."""
    ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize, fontweight="bold", va="bottom", ha="left", **kw)


def save(fig, path, formats=("png", "pdf")):
    """Save ``fig`` next to ``path`` in each format (the extension of ``path`` is replaced); returns the PNG path."""
    import pathlib
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(p.with_suffix(f".{ext}"), **({"dpi": 300} if ext == "png" else {}))
    return p.with_suffix(".png")
