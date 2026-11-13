# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Study 8 (exploratory): what happens when a SLOW induced voltage takes the PFE beyond its voltage range, and what could happen below 0 V?

This is a study with a reduced loop model, not a validated PFE model. Every protection number is a placeholder to be swept, because no vendor
data are available yet (see ``bolts params --status unknown``).

Physics used (all from the BOLTS network, which for a slow storm behaves as one loop):
  loop:    V_p + E(t) = V_rep + R_loop I          while the loop conducts (I > 0)
           V_p     PFE total voltage, V_rep = static need - R_loop I_set (sum of the repeater drops), E induced voltage (+ assists the feed)
  PFE:     the regulator wants I = I_set, i.e. V_p = V_need - E, but V_p can only be inside [0, V_max]
           below 0 V: the converter output is rectified, so it cannot go negative and cannot take current backwards:
           * assisting E large: V_p = 0 (the PFE is a short in the loop) and I = (E - V_rep) / R_loop rises above I_set
           * opposing E large:  V_p = V_max and I = (V_max + E - V_rep) / R_loop falls; when it reaches 0 the rectifier blocks (I = 0, loop open)
  trip:    over-current trip when I > k_trip I_set for t_delay seconds: breaker opens, the line sits at I = 0 for t_hold seconds,
           then a slow voltage ramp-up (rate r_up) restarts the feed; if the loop is still above the trip level the PFE trips again
  light:   the optical chain of ``bolts.impact.optical`` on the line current (light is lost when the Q margin is below 0)
  heat:    surplus line current runs through each repeater's Zener shunt; the overload is the time integral of (shunt power ratio - 1)+ in
           units of nominal-shunt-power seconds (a proxy for thermal stress; no thermal model yet)
Output: a table over induced-voltage peaks and over protection policies, and a figure of the time evolution for one assisting case."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.impact.optical import q_chain, repeater_state
from bolts.plotting import style

DT = 0.5
T_END = 3600.0
RAMP_S, HOLD_S = 600.0, 1800.0              # E rises for 10 min, holds for 30 min, falls for 10 min: a slow storm


def induced(e_peak: float) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(0.0, T_END + DT / 2, DT)
    e = np.interp(t, [0, RAMP_S, RAMP_S + HOLD_S, 2 * RAMP_S + HOLD_S, T_END], [0, e_peak, e_peak, 0, 0])
    return t, e


def run_loop(p, e: np.ndarray, v_max: float, k_trip: float | None, t_delay: float = 1.0, t_hold: float = 30.0, r_up: float = 20.0):
    """Evolve the reduced loop in time. ``k_trip`` None = ride through (no protection trip)."""
    r_loop = 816.8
    i_set = float(p.get("pfe", "feed_current_A"))
    v_rep = 1428.8 - r_loop * i_set
    v_need = 1428.8
    n = len(e)
    i = np.zeros(n)
    vp = np.zeros(n)
    state = "run"
    over_s = hold_left = 0.0
    trips = 0
    v_ramp = 0.0
    for k in range(n):
        if state == "tripped":
            vp[k], i[k] = 0.0, 0.0              # breaker open: nothing flows; the line is discharged while we wait
            hold_left -= DT
            if hold_left <= 0.0:
                state, v_ramp, over_s = "restart", 0.0, 0.0
            continue
        v_reg = min(max(v_need - e[k], 0.0), v_max)            # what the regulator would like, inside [0, V_max]
        if state == "restart":
            v_ramp = min(v_ramp + r_up * DT, v_reg)            # slow voltage ramp-up after a trip
            v_cmd = v_ramp
            if v_ramp >= v_reg:
                state = "run"
        else:
            v_cmd = v_reg
        vp[k] = v_cmd
        i[k] = max((v_cmd + e[k] - v_rep) / r_loop, 0.0)         # the rectifier blocks any reverse current
        if k_trip is not None and i[k] > k_trip * i_set:
            over_s += DT
            if over_s >= t_delay:
                state, hold_left, trips = "tripped", t_hold, trips + 1
                i[k] = 0.0
        else:
            over_s = 0.0
    return i, vp, trips


def score(p, i: np.ndarray, trips: int) -> dict:
    rs = repeater_state(p, i)
    light = q_chain(p, 28.2 + 10.0 * np.log10(np.maximum(rs["pump_ratio"], 1e-9)))["margin_dB"] > 0.0
    over = np.maximum(rs["zener_power_ratio"] - 1.0, 0.0)
    return {"light_on_pct": 100.0 * light.mean(), "i_max_A": float(i.max()), "zener_overload_s": float(over.sum() * DT), "trips": trips}


if __name__ == "__main__":
    out = out_dir(__file__)
    policies = [("ride through", None), ("trip 1.2 x I_set", 1.2), ("trip 1.5 x I_set", 1.5), ("trip 2.0 x I_set", 2.0)]
    for kv in (0.75, 2.5):
        p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": kv})
        print(f"\nPFE limit {2 * kv:.1f} kV total; slow storm: ramp {RAMP_S:g} s, hold {HOLD_S:g} s (E > 0 assists the feed)")
        print(f"{'E peak V':>9} {'policy':>18} {'light on %':>11} {'I max A':>8} {'trips':>6} {'Zener overload s':>17}")
        for e_peak in (-3000.0, -2000.0, -1000.0, 1000.0, 2000.0, 3000.0):
            t, e = induced(e_peak)
            for name, kt in policies:
                if e_peak < 0 and kt is not None and name != policies[1][0]:
                    continue                           # an opposing storm lowers the current: a high-current trip never fires, so one policy shows it
                i, _, trips = run_loop(p, e, 2 * kv * 1e3, kt)
                s = score(p, i, trips)
                print(f"{e_peak:9.0f} {name:>18} {s['light_on_pct']:11.1f} {s['i_max_A']:8.2f} {s['trips']:6d} {s['zener_overload_s']:17.0f}")

    plt = style.require_matplotlib()
    style.apply()
    p = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": 2.5})
    t, e = induced(3000.0)
    fig, axs = plt.subplots(3, 1, figsize=(style.DOUBLE_COL_IN, 6.0), sharex=True)
    axs[0].plot(t / 60, e, label="induced E")
    axs[0].set_ylabel("E (V)")
    for name, kt in (("ride through", None), ("trip 1.5 x I_set", 1.5)):
        i, vp, trips = run_loop(p, e, 5000.0, kt)
        axs[1].plot(t / 60, vp, label=name)
        axs[2].plot(t / 60, i, label=f"{name} ({trips} trips)")
    axs[1].set_ylabel("PFE voltage (V)")
    axs[2].set_ylabel("Line current (A)")
    axs[2].set_xlabel("Time (min)")
    for ax, lab in zip(axs, ("(a)", "(b)", "(c)"), strict=True):
        ax.legend()
        style.panel_label(ax, lab, x=-0.02, y=1.02)
    print("wrote", style.save(fig, out / "pfe_beyond_range"))
