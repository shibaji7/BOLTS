# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 2: a voltage record through the whole chain. Question: what does a 1-second record do to the PFE, the repeaters, the light
and the traffic?

Input: the shipped SYNTHETIC record (``scripts/make_synthetic_vind.py``: the frozen 72 V storm backbone, random ULF pulsations and one
onset impulse, 1800 s at 1 s; peak about -200 V, pulsation bands from 600 s down to 2.5 s), run against the 1.5 kV what-if limit. Replace ``data/example_vind_1s.csv`` (or pass another path as the first
argument) to run your own record.
Expect: with the 1.5 kV what-if limit the PFE sits at its limit for about 29% of the window and the repeater current falls by about 156 mA
(margin 100 mA, exceeded about 11% of the time); the Q margin only dips to about 10.7 dB and no terminal loses traffic. At the 5 kV design basis the
same record is absorbed (run it with ``--set pfe.max_voltage_kV_per_end=2.5`` through the CLI). The old 120 V burst is in
``data/legacy_pfe_design_burst_1s.csv``."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder

import bolts
from _common import EXAMPLE_CSV, out_dir, tight_limit_params
from bolts.plotting.network import plot_node_profile
from bolts.plotting.timeseries import plot_result

params = tight_limit_params()      # the 1.5 kV total what-if, so that the storm can actually reach the limit
record = bolts.load_waveform(sys.argv[1] if len(sys.argv) > 1 else EXAMPLE_CSV, params=params)
# build the circuit around the record, run it, then turn currents into optics and traffic
result = bolts.run_transient(bolts.build_network(params, record), params)
s = bolts.assess(result)
out = result.save(out_dir(__file__))
print(f"{record.label}: PFE total up to {s['v_pfe_max_V']:.0f} V, clamped {100 * s['frac_pfe_clamped']:.2f}% of the time")
print(f"repeater current {s['di_min_mA']:.1f} to {s['di_max_mA']:+.1f} mA; below the margin {100 * s['frac_time_below_margin']:.2f}% of the time")
print(f"Q margin down to {s['min_margin_dB']:.2f} dB; instantaneous-jump bound {s['jump_bound_mA']:.0f} mA (the data are sampled at {s['dt_s']:g} s)")
print("wrote", out, plot_result(result, out / "run"), plot_node_profile(result, out / "node_profile"))
