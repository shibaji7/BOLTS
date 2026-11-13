# 09. Validation and tests

> **Status:** implemented · **Code:** `tests/`, `bolts.validation`, `bolts.spice` · **Commands:** `make test`, `bolts validate`, `make spice-check`

## The idea

Three layers, from "is each piece right" to "does an independent solver agree".

| Layer | What | Where |
|---|---|---|
| Unit tests | parameters, waveforms, stamps, formulas, metrics | `tests/test_*.py` |
| Analytic validation | closed-form circuits and the regulator's closed forms | `bolts.validation`, `tests/test_regulator.py` |
| Independent cross-check | every node voltage against ngspice | `bolts.spice`, `tests/test_spice.py` |

## Analytic cases (`bolts validate`)

| Case | Closed form | Tolerance | Typical error |
|---|---|---|---|
| `rc_step` | `v = V (1 - e^(-t/RC))` | 2 / steps-per-tau | 5e-4 |
| `rlc_ring` | under-damped series RLC | 2% | 2e-3 |
| `line_modes` | slowest mode of a pinned RC ladder, `R'C'L^2/pi^2` | 1% | 2e-4 |
| `zener_dc` | `I = (V - (Vz - rz I_nom)) / (R + rz)` | 1e-9 | 0 |
| `energy_balance` | source energy = resistor loss + capacitor energy | first-order | 6e-4 |

Two nonlinear cases were added in v0.2 (Newton iteration): `diode_clamp` (a clamp across a node, both segments and polarities, closed-form divider) and `zener_knee` (a source through
a resistor into the piecewise Zener, all three segments), both exact to rounding. The nonlinear devices and the current sources are also cross-checked with ngspice (the piecewise-Zener
network agrees to 1e-5 of the 750 V scale; a clamp plus capacitor plus current source agrees to 1e-4 once ngspice's start-up has decayed: its first few steps differ by about 1% after a sharp edge, a
time-stepping difference, not a circuit one).

## The regulator (`tests/test_regulator.py`)

* loop resistance 816.8 ohm and static need 1428.8 V (the numbers of [chapter 02](02_power_feeding.md));
* ramp error `tau x rate / R_loop` to 1% for `dt / tau` from 0.1 to 1000;
* step peak `(dV / R_loop)(tau / dt)(1 - exp(-dt / tau))`, tending to 122 mA as `dt` shrinks, and the PFE ending 100 V lower;
* sine gain equal to the analytic high-pass within 3%;
* clamping at the limit and the resulting current fall `(excess) / R_loop`; assisting storms driving the PFE to 0 V.

## Independent cross-check

`bolts spice --run` exports the circuit (series branches as source, resistor, inductor; shunts as C and R), replays the simulated PFE voltage, runs
`ngspice -b`, and compares every node voltage: the agreement is about **1e-9 of the largest voltage** for the point-to-point cable. The regulator itself
is covered by the analytic tests, because its voltage is replayed.

## Regression against the sibling study

`tests/test_api_cli.py::test_end_to_end_matches_the_pfe_design_example_summary` runs the legacy burst record (`data/legacy_pfe_design_burst_1s.csv`, the record the `pfe_design` study used) at the 1.5 kV what-if and compares with the
`pfe_design` study's numbers for it: repeater current down 139.83 mA, PFE clamped 1.915% of the time, minimum margin 10.733 dB,
jump bound 169.996 mA.

The v0.1 audit also ran the two models side by side on six records (the shipped example, the legacy burst, a 500 V / 1 s sine and a 3 kV / 120 s
sine at both limits). The worst repeater current agrees to within 0.05 mA on the realistic records and 0.4 mA on the slow 3 kV sine; the 500 V / 1 s
sine differs by up to 7 mA (1.4% of its 525 mA dip) at the fastest parts. The difference is not numerical (it does not shrink with the time step): BOLTS
puts half a span of cable capacitance on each side of a repeater, while `pfe_design` lumps it at the repeater node, so the repeater current in BOLTS lacks
the charging current of that half span, about 0.4 of the regulator's ramp term. `tests/test_audit_v01.py` pins the agreement.

## Quality gates

`make qa` runs **ruff** (lint), **pylint duplicate-code** (R0801), the **SPDX header check**, and the tests; `make cov` reports coverage (about 95%).
The pre-commit hooks run the same checks plus a **changelog guard** ([chapter 10](10_run_and_extend.md)).

## What is not validated

No comparison with a real power-feed record during a storm; nothing about the optics or the terminal beyond the book's formulas and worked numbers;
the lightning, branching-unit and nonlinear-device chapters are designs, not code.

Next: [10. Run and extend](10_run_and_extend.md).
