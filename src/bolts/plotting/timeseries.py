# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The standard figure of a run, in the polar_connect paper style: five stacked panels on one time axis.

(a) input voltage; (b) PFE total voltage against its limit and the static need; (c) current change at the repeaters (band: lowest to
highest repeater) against the margin; (d) Q margin above the pre-FEC limit; (e) delivered rate of adaptive terminals."""
from __future__ import annotations

import pathlib

from ..result import Result
from . import style


def plot_result(result: Result, path, targets=(100, 200, 250)) -> pathlib.Path:
    """Draw and save the five-panel run figure (PNG and PDF); returns the PNG path."""
    plt = style.require_matplotlib()
    style.apply()
    C = style.TOL
    s, m, ev = result.series(), result.meta, result.optical()
    t = s["t_s"]
    fig, axs = plt.subplots(5, 1, figsize=(style.DOUBLE_COL_IN, 7.2), sharex=True, gridspec_kw={"height_ratios": [2, 2, 2, 1.5, 1.5]})
    a, b, c, d, e = axs      # shorthand: (a) record, (b) PFE, (c) repeater current, (d) Q margin, (e) delivered rate
    if "v_in_V" in s:
        a.plot(t, s["v_in_V"], color=C["red"], lw=0.8)
    a.set_ylabel("Induced voltage (V)")
    b.plot(t, s["v_pfe_total_V"], color=C["blue"], lw=0.8)
    b.axhline(m["v_tot_max_V"], color=C["red"], lw=0.8, ls=(0, (4, 2)))
    b.axhline(m["static_need_V"], color=style.DARK_GREY, lw=0.6, ls=":")
    b.text(t[-1], m["v_tot_max_V"], "PFE limit ", color=C["red"], fontsize=6.5, ha="right", va="bottom")
    b.text(t[-1], m["static_need_V"], "static need ", color=style.DARK_GREY, fontsize=6.5, ha="right", va="top")
    b.set_ylabel("PFE total (V)")
    # (c) the grey band spans lowest to highest repeater current; the black line is the worst (lowest) one, which drives the optics
    c.fill_between(t, s["di_min_mA"], s["di_max_mA"], color="0.7", lw=0)
    c.plot(t, s["di_min_mA"], color="k", lw=0.6)
    # the light band is the tolerance (+/- margin): a fall below its lower edge starts to starve the pump lasers
    c.axhspan(-1e3 * m["margin_A"], 1e3 * m["margin_A"], color="0.93", zorder=0)
    c.axhline(-1e3 * m["margin_A"], color=C["red"], lw=0.8, ls=(0, (4, 2)))
    c.set_ylabel("Repeater current\nchange (mA)")
    d.plot(t, ev["margin_dB"], color=C["teal"], lw=0.9)
    d.axhline(0.0, color=C["red"], lw=0.8, ls=(0, (4, 2)))
    d.set_ylabel("Q margin\n(dB)")
    for tg in targets:      # one trace per terminal target rate (adaptive terminals)
        e.plot(t, result.terminal(tg)["rate_Gbps"], lw=0.9, label=f"{tg}G")
    e.set_ylabel("Delivered rate\n(Gbit/s)")
    e.legend(frameon=False, fontsize=6.5, ncol=len(targets), loc="lower left")
    e.set_xlabel("Time from the start of the window (s)")
    for ax, lab in zip(axs, "abcde", strict=True):
        style.panel_label(ax, f"({lab})", x=-0.07, y=1.0)
        ax.tick_params(top=False)
    fig.subplots_adjust(left=0.11, right=0.985, top=0.985, bottom=0.07, hspace=0.18)
    out = style.save(fig, path)
    plt.close(fig)
    return out
