# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 12: how much does the landing soil matter? Question: for a given soil resistivity and rod electrode, what is the earth resistance, what does it do to the
static voltage the PFEs must supply, and how far does the ground potential rise (GPR = I R) go against the 20 V and 90 V recommendations of Chesnoy p. 387?

Input: soil resistivity from 10 (wet) to 3000 ohm m (rock); a line of n buried rods (3 m long, 1 cm radius, 3 m apart, Chesnoy Eqs. 10.3 and 10.4 in the Sunde form) at each landing;
the example record at the 1.5 kV what-if. The electrode design is an illustration, not a station design.
Expect: the 3 ohm of the book needs a good soil or several rods: one 3 m rod in 100 ohm m soil is 32 ohm and 4 rods in a line about 11 ohm. Every ohm of earth resistance at both ends adds 2 I_set = 2 V
to the static need, so a poor soil eats the PFE headroom (71 V at the 1.5 kV what-if) and the GPR (about 1 V per ohm at the nominal 1 A, 2.9 A in a +3 kV storm) crosses 20 V near 20 ohm."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import EXAMPLE_CSV, out_dir
from bolts.earthing.electrode_resistance import rods_in_line_ohm, single_rod_ohm
from bolts.earthing.gpr import required_resistance_ohm
from bolts.earthing.soil import wenner_resistivity_ohm_m
from bolts.plotting import style
from bolts.waveforms.step_ramp_sine import ramp_hold

ROD = {"length": 3.0, "radius": 0.01, "spacing": 3.0}
RHOS = [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0]


def r_bank(rho, n):
    rs = single_rod_ohm(rho, ROD["length"], ROD["radius"])
    return rs if n == 1 else rods_in_line_ohm(rho, rs, ROD["spacing"], n)


def run(rho, n, kv, rec=None):
    ov = {"pfe.max_voltage_kV_per_end": kv, "earthing.soil_resistivity_ohm_m": rho, "earthing.rod_count": n, "earthing.rod_length_m": ROD["length"],
          "earthing.rod_radius_m": ROD["radius"], "earthing.rod_spacing_m": ROD["spacing"]}
    p = bolts.load_parameters(overrides=ov)
    r = rec if rec is not None else bolts.load_waveform(EXAMPLE_CSV, params=p)
    return bolts.assess(bolts.run_transient(bolts.build_network(p, r), p, dt_s=1.0 if rec is not None else None))


if __name__ == "__main__":
    out = out_dir(__file__)
    print("Wenner measurement to resistivity: a = 5 m, b = 0.3 m, R = 3.2 ohm ->", f"{wenner_resistivity_ohm_m(5.0, 0.3, 3.2):.1f} ohm m")
    print(f"\nlargest earth resistance for GPR <= 20 V / 90 V: at 1 A {required_resistance_ohm(1.0, 20):.0f} / {required_resistance_ohm(1.0, 90):.0f} ohm; at 2.9 A (+3 kV storm) {required_resistance_ohm(2.92, 20):.1f} / {required_resistance_ohm(2.92, 90):.1f} ohm")
    print("\nearth resistance (ohm) of a line of n rods, 3 m x 1 cm, 3 m apart")
    print(f"{'rho ohm m':>10} " + " ".join(f"{'n=' + str(n):>9}" for n in (1, 2, 3, 4)))
    for rho in RHOS:
        print(f"{rho:10.0f} " + " ".join(f"{r_bank(rho, n):9.1f}" for n in (1, 2, 3, 4)))
    print("\n4 rods, example record at the 1.5 kV what-if, and a +3 kV assisting storm (ramp 600 s, hold 600 s) for the GPR")
    print(f"{'rho':>6} {'R_e ohm':>8} {'need V':>8} {'headroom V':>11} {'clamped %':>10} {'GPR example V':>14} {'GPR +3 kV V':>12} {'t>20 V (3 kV) s':>16}")
    rows = []
    for rho in RHOS:
        s = run(rho, 4, 0.75)
        s3 = run(rho, 4, 2.5, ramp_hold(3000.0, 600.0, 600.0, 1.0))
        rows.append((rho, s["earth_resistance_ohm"], s["static_need_V"], s["v_tot_max_V"] - s["static_need_V"], 100 * s["frac_pfe_clamped"], s["earth_gpr_peak_V"], s3["earth_gpr_peak_V"]))
        print(f"{rho:6.0f} {s['earth_resistance_ohm']:8.1f} {s['static_need_V']:8.1f} {s['v_tot_max_V'] - s['static_need_V']:11.1f} {100 * s['frac_pfe_clamped']:10.2f} "
              f"{s['earth_gpr_peak_V']:14.1f} {s3['earth_gpr_peak_V']:12.1f} {s3['earth_time_above_nominal_s']:16.0f}")

    plt = style.require_matplotlib()
    style.apply()
    fig, axs = plt.subplots(1, 4, figsize=(style.DOUBLE_COL_IN, 2.45), gridspec_kw={"wspace": 0.85, "left": 0.085, "right": 0.985, "bottom": 0.33, "top": 0.88})
    rho_f = np.logspace(1, np.log10(3000), 40)
    for n in (1, 2, 3, 4):
        axs[0].loglog(rho_f, [r_bank(r, n) for r in rho_f], label=f"{n} rod" + ("s" if n > 1 else ""))
    axs[0].axhline(3.0, ls="--", c="k", lw=0.8)
    axs[0].set_xlabel("Soil resistivity (ohm m)")
    axs[0].set_ylabel("Earth resistance (ohm)")
    axs[0].set_ylim(0.7, 60000)                         # headroom above the lines for the legend
    axs[0].legend(loc="upper left", fontsize=5.5)
    rr = np.array(rows)
    axs[1].semilogx(rr[:, 0], rr[:, 2], "o-")
    axs[1].axhline(1500.0, ls="--", c="k", lw=0.8)
    axs[1].set_xlabel("Soil resistivity (ohm m)")
    axs[1].set_ylabel("Static need (V)")
    axs[2].loglog(rr[:, 0], rr[:, 5], "o-", label="example record")
    axs[2].loglog(rr[:, 0], rr[:, 6], "s-", label="+3 kV storm")
    axs[2].axhline(20.0, ls="--", c="k", lw=0.8)
    axs[2].axhline(90.0, ls=":", c="k", lw=0.8)
    axs[2].set_xlabel("Soil resistivity (ohm m)")
    axs[2].set_ylabel("Peak GPR (V)")
    axs[2].set_ylim(0.7, 6000)
    axs[2].legend(loc="upper left", fontsize=5.5)
    axs[3].semilogx(rr[:, 0], rr[:, 4], "o-")
    axs[3].set_xlabel("Soil resistivity (ohm m)")
    axs[3].set_ylabel(f"Time at the cap ({style.pct()})")
    for ax, lab in zip(axs, ("(a)", "(b)", "(c)", "(d)"), strict=True):
        style.panel_label(ax, lab, x=-0.02, y=1.02)
        ax.set_box_aspect(1)
        ax.set_anchor("S")
    print("wrote", style.save(fig, out / "earthing_gpr"))
