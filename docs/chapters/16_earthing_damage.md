# 16. Earthing and damage

> **Status:** earth electrode, ground potential rise and insulation life law implemented · impulse earth impedance v0.5 · arrester, I2t and pass/fail criteria v0.4 · **Code:** `bolts.elements.earth_electrode`, `bolts.earthing`, `bolts.damage`

## The story

Every PFE reaches the sea through an earth electrode. In v0.1 that is a **3 ohm resistance in series with the sea** (Chesnoy: system earth electrodes below 3 ohm).
For surges the earth is also where the damage is made: a strike lifts the electrode potential (GPR) and the cable end sees it.

| Piece | Version |
|---|---|
| Electrode resistance, sea earth | **v0.1** |
| Soil resistivity (Wenner), electrode formulas, GPR (Chesnoy Eq. 10.2 to 10.4) | v0.2 (Eq. 10.4 uses the standard Sunde form with the spacing) |
| Lightning-rod separation (influence about inversely proportional to distance, p. 390) | v0.2 |
| Impulse impedance | v0.5 |
| Insulation withstand `V^n t = const` (Eq. 10.1), I2t heating, arrester energy | v0.4 |

Damage criteria turn waveforms into a verdict (survives, degraded, failed) with the margin, so the traffic consequences in
[chapter 05](05_terminal_and_traffic.md) can be attached to a failure.

Back to [the overview](00_overview.md).

## Insulation life (implemented in v0.2 round 2)

`bolts.damage.insulation_withstand` applies the life law `V^n t = constant` (Chesnoy Eq. 10.1, p. 383): `constant_from_reference` fixes the constant from one point (the
design life at the nominal voltage) and `life_consumed` sums `dt / t_f(V)` over a voltage record (Miner's rule; 1.0 = end of life). When `cable.insulation_exponent_n` is given
(it is unknown by default), `assess` reports `insulation_life_consumed_max`: the worst node's fraction of the 25-year design life (`cable.design_life_years`, assumed) used by the run, with the
reference voltage at half the static need, the nominal conductor-to-sea voltage at a PFE end. Experiment 10 sweeps n: at the 5 kV basis an opposing 3 kV storm of 30 minutes uses 13% of the
life at n = 10 and many lifetimes at n = 20, a 1 kV storm 6% at n = 20. These follow from a steep power law applied to an overvoltage up to three times nominal, so they say that n and the
component withstand ratings are the data to get, not that the cable would fail.

## Ground potential rise and the landing earth (implemented in v0.2 round 4)

The electrode of a PFE carries the line current, so its potential above remote earth is `GPR = I R`. Chesnoy Sec. 10.2.4 (p. 387) recommends at most 20 V between the system earth and the
station earth (90 V as an exceptional rise in a lightning environment) and electrodes below about 3 ohm. `bolts.earthing` now chains the pieces:

* `soil.wenner_resistivity_ohm_m` turns a four-terminal measurement (Eq. 10.2) into a resistivity;
* `electrode_resistance.single_rod_ohm` and `rods_in_line_ohm` (Eqs. 10.3 and 10.4, Sunde form: the printed Eq. 10.4 lacks the spacing and is dimensionally inconsistent) give the resistance of one rod or of 2 to 4 rods in a line;
* `electrode_resistance.landing_resistance_from_parameters` uses them **when** `earthing.soil_resistivity_ohm_m` and the four `earthing.rod_*` parameters are all given (all unknown by default), and otherwise keeps the sourced 3 ohm bound; the builder takes the landing resistance from it, so
  every ohm of earth at both ends adds `2 I_set` volts to the static need;
* `gpr.gpr_metrics` and `required_resistance_ohm` compare a current record with the two limits, and `assess` reports `earth_gpr_peak_V`, `earth_time_above_nominal_s`, `earth_time_above_exceptional_s` and `earth_resistance_ohm`.

The GPR reported is that of the electrode at the larger-current end, an upper bound on the system-to-station difference (the mutual coupling of the two electrodes is not modelled).

**Experiment 12** (`examples/gmd/12_earthing_gpr.py`, an illustrative electrode of 3 m x 1 cm rods 3 m apart): one rod in 100 ohm m soil is 32 ohm and four rods about 11 ohm; at the 1.5 kV what-if the headroom is 75 V at 10 ohm m soil, 55 V at 100 ohm m, 12 V at 300 ohm m and
negative (the PFE cannot supply even the static need) at 1000 ohm m, so a poor soil can matter as much as the cable. At the nominal 1 A the GPR is about 1 V per ohm; in a +3 kV assisting storm (2.9 A) it exceeds 20 V above about 7 ohm and 90 V above about 31 ohm. The 3 ohm of the book therefore needs
a good soil or a larger electrode (a mesh or plate), which this module does not design. The impulse (lightning) earth impedance with soil ionisation stays a v0.5 stub.

