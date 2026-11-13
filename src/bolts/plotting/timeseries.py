# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The standard figure of a run, in the polar_connect paper style: five stacked panels on one time axis.

(a) input voltage; (b) PFE total voltage against its limit and the static need; (c) current change at the repeaters (band: lowest to
highest repeater) against the margin; (d) Q margin above the pre-FEC limit; (e) delivered rate of adaptive terminals."""
from __future__ import annotations

import pathlib

from ..result import Result
from . import style

Q_FLOOR_DB = -12.0     # the Q-margin axis is clipped here: a dark line has no meaningful margin (the model returns a -103 dB "no light" floor)


def _draw(axs, result: Result, targets, label: str = "", legend: bool = True) -> None:
    """Draw the five panels of one run onto five axes (shared by :func:`plot_result` and :func:`plot_compare`)."""
    import numpy as np
    C = style.TOL
    s, m, ev = result.series(), result.meta, result.optical()
    t = s["t_s"]
    a, b, c, d, e = axs      # shorthand: (a) record, (b) PFE, (c) repeater current, (d) Q margin, (e) delivered rate
    if "v_in_V" in s:
        a.plot(t, s["v_in_V"], color=C["red"], lw=0.8)
    if label:
        a.set_title(label, fontsize=8)
    b.plot(t, s["v_pfe_total_V"], color=C["blue"], lw=0.8)
    b.axhline(m["v_tot_max_V"], color=C["red"], lw=0.8, ls=(0, (4, 2)))
    b.axhline(m["static_need_V"], color=style.DARK_GREY, lw=0.6, ls=":")
    b.text(t[-1], m["v_tot_max_V"], "PFE limit ", color=C["red"], fontsize=6.5, ha="right", va="bottom")
    b.text(t[-1], m["static_need_V"], "static need ", color=style.DARK_GREY, fontsize=6.5, ha="right", va="top")
    # (c) the grey band spans lowest to highest repeater current; the black line is the worst (lowest) one, which drives the optics
    c.fill_between(t, s["di_min_mA"], s["di_max_mA"], color="0.7", lw=0)
    c.plot(t, s["di_min_mA"], color="k", lw=0.6)
    # the light band is the tolerance (+/- margin): a fall below its lower edge starts to starve the pump lasers
    c.axhspan(-1e3 * m["margin_A"], 1e3 * m["margin_A"], color="0.93", zorder=0)
    c.axhline(-1e3 * m["margin_A"], color=C["red"], lw=0.8, ls=(0, (4, 2)))
    q = np.asarray(ev["margin_dB"], dtype=float)
    d.plot(t, np.maximum(q, Q_FLOOR_DB), color=C["teal"], lw=0.9)
    d.axhline(0.0, color=C["red"], lw=0.8, ls=(0, (4, 2)))
    if q.min() < Q_FLOOR_DB:      # the line runs along the bottom edge wherever the light is gone
        d.set_ylim(bottom=Q_FLOOR_DB - 1.5)
        d.text(t[0], Q_FLOOR_DB - 0.5, " clipped: no light", color=style.DARK_GREY, fontsize=6.5, ha="left", va="bottom")
    for tg in targets:      # one trace per terminal target rate (adaptive terminals)
        e.plot(t, result.terminal(tg)["rate_Gbps"], lw=0.9, label=f"{tg}G")
    if legend:
        e.legend(frameon=False, fontsize=6.5, ncol=len(targets), loc="lower left")
    e.set_xlabel("Time from the start of the window (s)")


_YLABELS = ("Induced voltage (V)", "PFE total (V)", "Repeater current\nchange (mA)", "Q margin\n(dB)", "Delivered rate\n(Gbit/s)")


def plot_result(result: Result, path, targets=(100, 200, 250)) -> pathlib.Path:
    """Draw and save the five-panel run figure (PNG and PDF); returns the PNG path.

    The Q-margin panel is clipped at ``Q_FLOOR_DB``: below it the light is gone and the margin has no meaning.

    Args:
        result: A finished run.
        path: Output path without extension.
        targets: Terminal rates (Gbit/s) drawn in the last panel.

    Returns:
        The PNG path.
    """
    plt = style.require_matplotlib()
    style.apply()
    fig, axs = plt.subplots(5, 1, figsize=(style.DOUBLE_COL_IN, 7.2), sharex=True, gridspec_kw={"height_ratios": [2, 2, 2, 1.5, 1.5]})
    _draw(axs, result, targets)
    for ax, lab, yl in zip(axs, "abcde", _YLABELS, strict=True):
        ax.set_ylabel(yl)
        style.panel_label(ax, f"({lab})", x=-0.07, y=1.0)
        ax.tick_params(top=False)
    fig.subplots_adjust(left=0.11, right=0.985, top=0.985, bottom=0.07, hspace=0.18)
    out = style.save(fig, path)
    plt.close(fig)
    return out


def plot_compare(results, labels, path, targets=(100, 200, 250)) -> pathlib.Path:
    """Draw several runs side by side, one column each, with the rows sharing their axes (for example the same storm at two strengths).

    Args:
        results: The finished runs, left to right.
        labels: A title for each column.
        path: Output path without extension.
        targets: Terminal rates (Gbit/s) drawn in the last row.

    Returns:
        The PNG path.
    """
    plt = style.require_matplotlib()
    style.apply()
    n = len(results)
    fig, grid = plt.subplots(5, n, figsize=(style.DOUBLE_COL_IN, 7.6), sharex=True, sharey="row", squeeze=False,
                             gridspec_kw={"height_ratios": [2, 2, 2, 1.5, 1.5]})
    for j, (res, lab) in enumerate(zip(results, labels, strict=True)):
        _draw(grid[:, j], res, targets, label=lab, legend=(j == 0))
    for i, yl in enumerate(_YLABELS):
        grid[i, 0].set_ylabel(yl)
    for i, lab in enumerate("abcde"):
        for j in range(n):
            style.panel_label(grid[i, j], f"({lab}{j + 1})", x=-0.07 if j == 0 else -0.03, y=1.0)
            grid[i, j].tick_params(top=False)
    fig.subplots_adjust(left=0.11, right=0.985, top=0.96, bottom=0.07, hspace=0.18, wspace=0.05)
    out = style.save(fig, path)
    plt.close(fig)
    return out
