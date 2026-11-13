# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 3: how much voltage must the PFE have? Question: for an opposing storm, how does the worst repeater current change depend
on the PFE voltage limit?

A step of -400 V against limits from 1.5 kV to 5 kV in total. Expect: while the headroom (limit - 1428.8 V) is below the storm, the PFE
saturates and the current falls by (storm - headroom) / 816.8 ohm (403 mA at 1.5 kV); above about 1829 V total the step is absorbed, leaving
only about 10 mA of charging current of the (placeholder) cable capacitance."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.plotting import style
from bolts.studies.sweep import sweep
from bolts.waveforms.step_ramp_sine import step

params = bolts.load_parameters()
# a deliberate stress case, not a forecast: a 400 V step OPPOSING the feed (negative = the induced voltage subtracts from the supply)
storm = step(-400.0, 120.0, 1.0, 20.0)
limits_kV_per_end = np.array([0.75, 0.85, 0.9, 0.95, 1.0, 1.25, 2.5])   # per end; the total is twice this


def run_one(p):
    """One run at one PFE limit: the worst current change and the share of time the PFE sat at its limit."""
    s = bolts.run_transient(bolts.build_network(p, storm), p).summary()
    return {"total_kV": 2 * p.get("pfe", "max_voltage_kV_per_end"), "di_min_mA": s["di_min_mA"], "frac_clamped": s["frac_pfe_clamped"]}


# sweep() re-runs run_one with the parameter changed, one value at a time, and collects the dictionaries
rows = sweep(params, "pfe.max_voltage_kV_per_end", limits_kV_per_end, run_one)
for r in rows:
    print(f"limit {r['total_kV']:.2f} kV total: worst current change {r['di_min_mA']:8.1f} mA, PFE clamped {100 * r['frac_clamped']:5.1f}% of the time")

plt = style.require_matplotlib()
style.apply()
fig, ax = plt.subplots(figsize=(style.SINGLE_COL_IN * 1.5, 2.8))
ax.plot([r["total_kV"] for r in rows], [r["di_min_mA"] for r in rows], "o-", color=style.TOL["blue"])
# the repeater tolerance: a current fall beyond 100 mA (10% of 1 A) begins to starve the pump lasers
ax.axhline(-100.0, color=style.TOL["red"], ls=(0, (4, 2)), lw=0.8)
ax.set_xlabel("PFE voltage limit, both ends (kV)")
ax.set_ylabel("Worst repeater current change (mA)")
print("wrote", style.save(fig, out_dir(__file__) / "pfe_limit"))
