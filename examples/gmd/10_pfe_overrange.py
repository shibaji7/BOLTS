# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 10: the PFE beyond its range, with the full circuit. Question: what do slow storms bigger than the PFE's range, a slow PFE, a failed
converter module and an overvoltage do to the repeater current, the light and the insulation?

Four parts, all on the real network (study 08 used a reduced loop with trips; this one has no trip logic, which is roadmap v0.3):
  1. slow ramp-and-hold storms of -3 to +3 kV (10 min up, 20 min hold) at the 1.5 kV what-if and the 5 kV design basis;
  2. a slow PFE: the same 300 V, 10 s-period swing (peak rate 188 V/s) with the output slew rate limited to infinity, 300, 100, 50 and 25 V/s;
  3. converter failover: 6 modules of 500 V per end with one spare, 0 to 4 modules failed, against an opposing storm of 2 kV;
  4. insulation life: the conductor-to-sea voltage of the opposing storms in the life law V^n t = constant (Chesnoy Eq. 10.1), swept over the unknown
     exponent n, with 25 years as the life at half the static need (the nominal end voltage).
Expect: an opposing storm beyond the cap makes the current fall by (V_ind - headroom) / R_loop, an assisting one beyond 0 V makes it rise by (V_ind - V_need) /
R_loop; a slower PFE lets a fast swing through (the dip grows as the slew rate falls below the swing's rate); every module lost beyond the spare removes 500 V
per end of range; and the insulation life used by the storm depends enormously on the unknown exponent n: with the 5 kV basis the opposing 3 kV storm uses 13% of the
25-year life at n = 10 and many lifetimes at n = 20, the 1 kV storm 6% at n = 20. These are results of a steep power law applied to an overvoltage of up to 3x
the nominal end voltage, so treat them as a reason to get n and the withstand ratings, not as a prediction. All protection and life-law values are placeholders
(``bolts params --status unknown``)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np
from matplotlib.ticker import NullFormatter

import bolts
from _common import out_dir
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import ramp_hold, sine

NEED = 1428.8


def assess(overrides, rec, dt):
    p = bolts.load_parameters(overrides=overrides)
    return bolts.assess(bolts.run_transient(bolts.build_network(p, rec), p, dt_s=dt))


if __name__ == "__main__":
    out = out_dir(__file__)
    # ---- 1. slow storms beyond the range ----
    print("1. slow storms (ramp 600 s, hold 1200 s): E > 0 assists the feed")
    print(f"{'limit kV':>8} {'E V':>6} {'dI min':>8} {'dI max':>8} {'V_pfe':>11} {'at cap %':>9} {'at 0 V %':>9} {'I/I_set':>8} {'light lost %':>13} {'Zener x':>8}")
    ramps = {}
    for kv in (0.75, 2.5):
        for e in (-3000.0, -2000.0, -1000.0, 1000.0, 2000.0, 3000.0):
            s = assess({"pfe.max_voltage_kV_per_end": kv}, ramp_hold(e, 600.0, 1200.0, 1.0), 1.0)
            ramps[(kv, e)] = s
            dur = s["duration_s"]
            print(f"{2 * kv:8.1f} {e:6.0f} {s['di_min_mA']:8.0f} {s['di_max_mA']:8.0f} {s['v_pfe_min_V']:5.0f}-{s['v_pfe_max_V']:5.0f} {100 * s['pfe_time_at_upper_limit_s'] / dur:9.1f} "
                  f"{100 * s['pfe_time_at_zero_s'] / dur:9.1f} {s['pfe_i_max_over_set']:8.2f} {100 * s['frac_time_outage']:13.1f} {s['max_zener_power_ratio']:8.1f}")
    # ---- 2. slew rate ----
    print("\n2. slow PFE: 300 V, 10 s period swing (peak rate 188 V/s), 5 kV basis")
    slews = [None, 300.0, 100.0, 50.0, 25.0]
    dips = []
    print(f"{'slew V/s':>9} {'dI min':>8} {'dI max':>8} {'Q margin dB':>12} {'time slew-limited s':>20}")
    for sl in slews:
        ov = {"pfe.max_voltage_kV_per_end": 2.5} | ({} if sl is None else {"pfe.output_slew_limit_V_per_s": sl})
        s = assess(ov, sine(300.0, 0.1, duration_s=120.0, dt_s=0.05), 0.05)
        dips.append(max(abs(s["di_min_mA"]), abs(s["di_max_mA"])))
        print(f"{'none' if sl is None else f'{sl:g}':>9} {s['di_min_mA']:8.1f} {s['di_max_mA']:8.1f} {s['min_margin_dB']:12.2f} {s.get('pfe_time_slew_limited_s', 0.0):20.1f}")
    # ---- 3. converter failover ----
    print("\n3. converter failover: 6 x 500 V per end, 1 spare; opposing storm of -2 kV (ramp 600 s, hold 1200 s)")
    print(f"{'failed':>7} {'cap kV total':>13} {'dI min':>8} {'at cap %':>9} {'light lost %':>13} {'250G %':>7}")
    lost = []
    failed_list = [0, 1, 2, 3, 4]
    for fm in failed_list:
        s = assess({"pfe.converter_modules": 6, "pfe.converter_module_rating_V": 500.0, "pfe.converter_failed_modules": fm}, ramp_hold(-2000.0, 600.0, 1200.0, 1.0), 1.0)
        lost.append(100 * s["frac_time_outage"])
        print(f"{fm:7d} {s['v_tot_max_V'] / 1e3:13.1f} {s['di_min_mA']:8.0f} {100 * s['pfe_time_at_upper_limit_s'] / s['duration_s']:9.1f} "
              f"{lost[-1]:13.1f} {100 * s['fixed_250G_mean_rate_fraction']:7.1f}")
    # ---- 4. insulation life ----
    print("\n4. insulation life used, worst node (25-year life at half the static need), 5 kV basis, ramp 600 s + hold 1200 s")
    exps = [5.0, 10.0, 20.0, 30.0, 40.0]
    life = {}
    print(f"{'E V':>6} " + " ".join(f"{'n=' + f'{n:g}':>10}" for n in exps))
    for e in (-1000.0, -2000.0, -3000.0):
        life[e] = [assess({"pfe.max_voltage_kV_per_end": 2.5, "cable.insulation_exponent_n": n}, ramp_hold(e, 600.0, 1200.0, 1.0), 1.0)["insulation_life_consumed_max"] for n in exps]
        print(f"{e:6.0f} " + " ".join(f"{v:10.2e}" for v in life[e]))

    plt = style.require_matplotlib()
    style.apply()
    fig, axs = plt.subplots(1, 4, figsize=(style.DOUBLE_COL_IN, 2.2), gridspec_kw={"wspace": 0.68, "left": 0.085, "right": 0.985, "bottom": 0.27, "top": 0.88})
    es = np.array([-3000.0, -2000.0, -1000.0, 1000.0, 2000.0, 3000.0])
    for kv, mk in ((0.75, "o"), (2.5, "s")):
        axs[0].plot(es / 1e3, [ramps[(kv, e)]["di_min_mA"] + ramps[(kv, e)]["di_max_mA"] for e in es], mk + "-", label=f"limit {2 * kv:.1f} kV")
    axs[0].set_xlabel("Storm peak $E$ (kV)")
    axs[0].set_ylabel("Net current change (mA)")
    axs[0].legend(loc="upper left", fontsize=5.5)
    axs[1].semilogx([1e3 if sl is None else sl for sl in slews], dips, "o-")
    axs[1].set_xticks([25, 100, 300, 1000], ["25", "100", "300", "none"])
    axs[1].xaxis.set_minor_formatter(NullFormatter())
    axs[1].set_xlabel("Slew limit (V/s)")
    axs[1].set_ylabel("Worst current change (mA)")
    axs[2].plot(failed_list, lost, "o-")
    axs[2].set_xlabel("Failed modules")
    axs[2].set_ylabel(f"Light lost ({style.pct()} of time)")
    for e, mk in zip(life, "ods", strict=True):
        axs[3].semilogy(exps, life[e], mk + "-", label=f"{e / 1e3:g} kV")
    axs[3].set_xlabel("Life-law exponent $n$")
    axs[3].set_ylabel("Life used (fraction)")
    axs[3].legend(loc="upper left", fontsize=5.5)
    for ax, lab in zip(axs, ("(a)", "(b)", "(c)", "(d)"), strict=True):
        style.panel_label(ax, lab, x=-0.02, y=1.02)
        ax.set_box_aspect(1)                              # square panels
        ax.set_anchor("S")
    print("wrote", style.save(fig, out / "pfe_overrange"))
