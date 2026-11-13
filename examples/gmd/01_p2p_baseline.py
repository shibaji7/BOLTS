# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Experiment 1: the quiet line. Question: what does it take to power the cable when nothing happens, and what is the loop?

Expect: 12 repeaters, a static need of 1428.8 V (cable 750.8 V + 12 x 56 V + 6 V), a loop resistance of 816.8 ohm (cable 750.8 + 12 x 5 +
2 x 3) so 1 V of induced voltage changes the current by 1.22 mA, and no change of current at all."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))     # so that `_common` is found from any folder
import numpy as np

import bolts
from _common import out_dir
from bolts.io.writers import write_json

params = bolts.load_parameters()                      # shipped defaults; every value has a unit, a status and a source
net = bolts.build_network(params, None)             # no record = a quiet line: the PFE just supplies the static need
# a quiet network has no time axis of its own, so give it a minute at 1 s
result = bolts.run_transient(net, params, t_s=np.arange(0.0, 61.0))
s = result.summary()
print(f"repeaters {net.meta['n_repeaters']}, span {net.meta['span_km']:.1f} km, static need {net.meta['static_need_V']:.1f} V")
# 1 / R_loop is how many amps the loop current moves per volt of net induced voltage, if nobody corrects it
print(f"loop resistance {s['r_loop_ohm']:.1f} ohm -> {1e3 / s['r_loop_ohm']:.3f} mA per volt of induced voltage")
# headroom = what the PFE can still add; the storm must exceed it before the repeater current changes
print(f"headroom at the default limit: {s['v_tot_max_V'] - s['static_need_V']:.0f} V; largest current change {max(abs(s['di_min_mA']), abs(s['di_max_mA'])):.2e} mA")
write_json(out_dir(__file__) / "summary.json", s)
