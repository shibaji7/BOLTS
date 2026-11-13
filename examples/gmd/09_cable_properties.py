# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 9: how do the cable properties change the outputs? Question: what do the section table, the depth profile and the temperature model
do to the static voltage the PFEs must supply, the PFE headroom, the repeater current dip and the fast response?

Input: the shipped example record at the 1.5 kV what-if (headroom about 71 V with the constant cable), the three illustration tables in ``data/``,
and sweeps of the seabed temperature and the cable capacitance. The tables are illustrations (see ``data/README.md``), not a cable design.
Expect: copper resistance is about 0.4% per kelvin, so cold water lowers the cable's share of the static need by about 6% (about 47 V at 4 C instead
of 20 C) and that is as large as the whole 71 V headroom: temperature alone changes whether the PFE clamps. The capacitance matters only for fast
changes. With room at the PFE (5 kV basis) the repeater current change from a fast swing grows about linearly with C' (60 V swing at 1 Hz: 4 mA at
0.05 uF/km, 9 mA at 0.2, 28 mA at 0.8), because the cable's charging current C dV/dt flows through the repeaters while the PFE regulates the end current.
At the 1.5 kV what-if the worst dip of a 500 V swing is set by the clamp and does not depend on C'.

How much the cable properties shift the results (the second table and ``cable_properties_shift.png``)
three storms (the example record, the example record scaled x3, and the 500 V 1 s sine) through four cable cases (constant 1 ohm/km, copper at 4 C,
the section table, and table + depth + temperature) at the 1.5 kV what-if:

* PFE stress: it moves a lot.
   * Time at the cap: for the example record, 29.5% constant, 16.4% at 4 C and 52.2% with the section table. For x3, 84% falls to 62% in the cold case.
   * Shortfall integral: lower in the cold cases, by 59% for the example record (29,572 V s falling to 12,219 V s), 27% for x3 and 16% for the sine.
   * Worst dip: 100 mA to 600 mA scale, changing by 3 to 52 mA across cases (for example -156 vs -104 mA).
* Optical margin: it moves little, 0.1 to 0.6 dB (for example 6.96 vs 7.55 dB at x3, and 9.02 vs 9.29 dB for the 500 V sine).
* Traffic: it barely moves.
   * Light and 100G/200G: the light is never lost in these cases, and 100G and 200G are unchanged.
   * 250G: for x3 it changes from 82.7% to 83.4%. For the 500 V sine it stays at 0.5% in all four cases, because the 1.8 dB dips set that loss, not the cable.

The section table is an illustration of the format (``data/README.md``); only the temperature shift (about 47 V of static need) is grounded in physics."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np
from matplotlib.ticker import NullFormatter

import bolts
from _common import EXAMPLE_CSV, out_dir
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import sine

DATA = pathlib.Path(EXAMPLE_CSV).parent
CAP = {"pfe.max_voltage_kV_per_end": 0.75}          # the 1.5 kV what-if: the cap is close enough to the need for the cable properties to matter

SCENARIOS = {
    "constant (1 ohm/km)": {},
    "copper at 4 C": {"cable.temperature_model": "copper"},
    "section table": {"cable.section_table_csv": str(DATA / "example_cable_sections.csv")},
    "table + depth + temperature": {"cable.section_table_csv": str(DATA / "example_cable_sections.csv"), "cable.temperature_model": "copper",
                                    "cable.depth_profile_csv": str(DATA / "example_route_depth.csv"),
                                    "cable.depth_temperature_csv": str(DATA / "example_depth_temperature.csv")},
}


SHORT = dict(zip(SCENARIOS, ("constant", "copper, 4 C", "table", "table+depth+T"), strict=True))


def run(overrides, record_path=None, record=None, dt=None):
    p = bolts.load_parameters(overrides={**CAP, **overrides})
    rec = record if record is not None else bolts.load_waveform(record_path or EXAMPLE_CSV, params=p)
    net = bolts.build_network(p, rec)
    return net, bolts.assess(bolts.run_transient(net, p, dt_s=dt))


if __name__ == "__main__":
    out = out_dir(__file__)
    print(f"{'scenario':30s} {'R_cable ohm':>11s} {'need V':>8s} {'headroom V':>11s} {'clamped %':>10s} {'dI min mA':>10s} {'Q margin dB':>12s}")
    base = {}
    for name, ov in SCENARIOS.items():
        net, s = run(ov)
        r_cable = (net.meta["static_need_V"] - 12 * 56.0 - 6.0)      # need = I (R_cable + 2 R_earth) + 12 V_z, I = 1 A
        base.setdefault("need", s["static_need_V"])
        print(f"{name:30s} {r_cable:11.1f} {s['static_need_V']:8.1f} {s['v_tot_max_V'] - s['static_need_V']:11.1f} {100 * s['frac_pfe_clamped']:10.2f} "
              f"{s['di_min_mA']:10.1f} {s['min_margin_dB']:12.2f}")
    print("\nshift of stress and traffic, 1.5 kV what-if (same storms, only the cable properties change)")
    storms = {"example record": None, "example x3": "x3", "500 V 1 s sine": "sine"}
    keys = ("frac_pfe_clamped", "pfe_shortfall_integral_Vs", "di_min_mA", "min_margin_dB", "frac_time_outage", "max_zener_power_ratio",
            "fixed_250G_mean_rate_fraction", "fixed_250G_lost_Gbit")
    print(f"{'storm':16s} {'scenario':30s} {'clamp %':>8s} {'shortfall V s':>14s} {'dI min':>8s} {'Q dB':>7s} {'light lost %':>13s} {'250G %':>7s} {'250G lost Gbit':>15s}")
    shift = []                                            # one row per (storm, cable case), also written to shift_table.csv
    for storm, kind in storms.items():
        for name, ov in SCENARIOS.items():
            if kind == "sine":
                _, s = run(ov, record=sine(500.0, 1.0, duration_s=120.0, dt_s=0.025), dt=0.025)
            elif kind == "x3":
                p_ = bolts.load_parameters(overrides={**CAP, **ov})
                r0 = bolts.load_waveform(EXAMPLE_CSV, params=p_)
                _, s = run(ov, record=r0.__class__(r0.t_s, 3.0 * r0.values, "x3"))
            else:
                _, s = run(ov)
            shift.append({"storm": storm, "cable": name, "clamped_pct": 100 * s[keys[0]], "shortfall_Vs": s[keys[1]], "di_min_mA": s[keys[2]],
                          "q_margin_dB": s[keys[3]], "light_lost_pct": 100 * s[keys[4]], "fixed_250G_delivered_pct": 100 * s[keys[6]],
                          "fixed_250G_lost_Gbit": s[keys[7]], "zener_power_ratio_max": s[keys[5]]})
            print(f"{storm:16s} {name:30s} {100 * s[keys[0]]:8.2f} {s[keys[1]]:14.0f} {s[keys[2]]:8.1f} {s[keys[3]]:7.2f} {100 * s[keys[4]]:13.2f} "
                  f"{100 * s[keys[6]]:7.1f} {s[keys[7]]:15.0f}")
    print("\nseabed temperature (copper model on), example record, 1.5 kV what-if")
    temps = [0.0, 4.0, 10.0, 20.0, 30.0]
    need_t, clamp_t = [], []
    print(f"{'T C':>6s} {'need V':>8s} {'headroom V':>11s} {'clamped %':>10s} {'dI min mA':>10s}")
    for t in temps:
        _, s = run({"cable.temperature_model": "copper", "cable.seabed_temperature_C": t})
        need_t.append(s["static_need_V"]), clamp_t.append(100 * s["frac_pfe_clamped"])
        print(f"{t:6.1f} {s['static_need_V']:8.1f} {s['v_tot_max_V'] - s['static_need_V']:11.1f} {100 * s['frac_pfe_clamped']:10.2f} {s['di_min_mA']:10.1f}")
    print("\ncable capacitance, 5 kV design basis (the PFE has room, so the dip is the cable's charging current), 1 Hz swings")
    cs = [0.05, 0.1, 0.2, 0.4, 0.8]
    fast, slow = [], []
    print(f"{'C uF/km':>8s} {'60 V swing: dI max mA':>22s} {'500 V swing: dI max mA':>23s} {'500 V swing, 1.5 kV: dI min mA':>31s}")
    for c in cs:
        ov = {"cable.capacitance_uF_per_km": c}
        _, s60 = run({**ov, "pfe.max_voltage_kV_per_end": 2.5}, record=sine(60.0, 1.0, duration_s=60.0, dt_s=0.025), dt=0.025)
        _, s500 = run({**ov, "pfe.max_voltage_kV_per_end": 2.5}, record=sine(500.0, 1.0, duration_s=60.0, dt_s=0.025), dt=0.025)
        _, sclamp = run(ov, record=sine(500.0, 1.0, duration_s=60.0, dt_s=0.025), dt=0.025)
        fast.append(s500["di_max_mA"]), slow.append(s60["di_max_mA"])
        print(f"{c:8.2f} {s60['di_max_mA']:22.1f} {s500['di_max_mA']:23.1f} {sclamp['di_min_mA']:31.1f}")

    plt = style.require_matplotlib()
    style.apply()
    fig, axs = plt.subplots(1, 3, figsize=(style.DOUBLE_COL_IN, 2.5), gridspec_kw={"wspace": 0.5, "left": 0.075, "right": 0.97, "bottom": 0.22, "top": 0.88})
    p0 = bolts.load_parameters(overrides=CAP)
    x = np.linspace(0.0, 750.8, 400)
    for name, ov in SCENARIOS.items():
        from bolts.properties import provider_from_parameters
        prov = provider_from_parameters(bolts.load_parameters(overrides={**CAP, **ov}))
        axs[0].plot(x, [prov.rlcg(xi, 0.0, 4.0).r_ohm_per_km for xi in x], label=SHORT[name])
    axs[0].set_xlabel("Chainage (km)")
    axs[0].set_ylabel("R' (ohm/km)")
    axs[0].set_ylim(0.50, 1.08)                      # leave room under the curves for the legend
    axs[0].legend(loc="lower left", fontsize=5.5, borderaxespad=0.3)
    axs[1].plot(temps, need_t, "o-", label="static need")
    axs[1].axhline(1500.0, ls="--", c="k", lw=0.8, label="1.5 kV cap")
    axs[1].set_xlabel("Seabed temperature (C)")
    axs[1].set_ylabel("Static need (V)")
    axs[1].legend()
    axs[2].loglog(cs, fast, "o-", label="500 V swing, 1 Hz")
    axs[2].loglog(cs, slow, "s-", label="60 V swing, 1 Hz")
    axs[2].set_xlabel("C' (uF/km)")
    axs[2].set_ylabel("Current change (mA)")
    axs[2].set_xticks(cs, [f"{c:g}" for c in cs])         # plain tick labels: the default log labels overlap
    axs[2].xaxis.set_minor_formatter(NullFormatter())
    axs[2].set_ylim(2.5, 900)                         # headroom above the curves for the legend
    axs[2].legend(loc="upper left", fontsize=5.5)
    for ax, lab in zip(axs, ("(a)", "(b)", "(c)"), strict=True):
        style.panel_label(ax, lab, x=-0.02, y=1.02)
        ax.set_box_aspect(1)                              # square panels
        ax.set_anchor("S")
    del p0
    print("wrote", style.save(fig, out / "cable_properties"))

    # the table behind the second figure, for reuse
    import csv
    with open(out / "shift_table.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(shift[0]))
        w.writeheader()
        w.writerows(shift)
    # second figure: the shift of stress, optics and traffic, one group of bars per storm and one bar colour per cable case
    fig2, ax2 = plt.subplots(1, 4, figsize=(style.DOUBLE_COL_IN, 2.35), gridspec_kw={"wspace": 0.68, "bottom": 0.34, "top": 0.88, "left": 0.085, "right": 0.985})
    panels = (("clamped_pct", f"Time at the cap ({style.pct()})", 1.0), ("shortfall_Vs", "Shortfall integral (kV s)", 1e-3),
              ("q_margin_dB", "Minimum Q margin (dB)", 1.0), ("fixed_250G_delivered_pct", f"250G delivered ({style.pct()})", 1.0))
    width = 0.2
    for ax, (key, label, scale), tag in zip(ax2, panels, ("(a)", "(b)", "(c)", "(d)"), strict=True):
        for j, name in enumerate(SCENARIOS):
            vals = [next(r[key] for r in shift if r["storm"] == st and r["cable"] == name) * scale for st in storms]
            ax.bar(np.arange(len(storms)) + (j - 1.5) * width, vals, width, label=SHORT[name])
        ax.set_xticks(np.arange(len(storms)), ["1x", "3x", "sine"])
        ax.set_ylabel(label)
        style.panel_label(ax, tag, x=-0.02, y=1.02)
        ax.set_box_aspect(1)                              # square panels
        ax.set_anchor("S")
    handles, labels = ax2[0].get_legend_handles_labels()
    fig2.legend(handles, labels, loc="lower center", ncol=4, fontsize=6, bbox_to_anchor=(0.5, -0.02))
    fig2.supxlabel("Storm: example record at 1x and 3x, and a 500 V 1 s sine", fontsize=6.5, y=0.14)
    print("wrote", style.save(fig2, out / "cable_properties_shift"), "and", out / "shift_table.csv")
