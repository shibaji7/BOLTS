# Examples

Runnable experiments in `examples/gmd/`. Each page gives the question, the input, what to expect, the figures, the command and the full source. They need the `plots` extra for figures (`pip install bolts[plots]`) and, for experiment 6, the `ngspice` binary.

```bash
make examples            # run all of them; outputs go to outputs/examples/
```

| Experiment | What it answers |
|---|---|
| [01_p2p_baseline](01_p2p_baseline.md) | Experiment 1: the quiet line |
| [02_storm_record](02_storm_record.md) | Experiment 2: a voltage record through the whole chain |
| [03_pfe_limit_sweep](03_pfe_limit_sweep.md) | Experiment 3: how much voltage must the PFE have? |
| [04_regulator_tau](04_regulator_tau.md) | Experiment 4: the regulator time constant |
| [05_amplitude_period_map](05_amplitude_period_map.md) | Experiment 5: how big, how fast? |
| [06_spice_crosscheck](06_spice_crosscheck.md) | Experiment 6: independent check |
| [07_swing_onset](07_swing_onset.md) | Experiment 7: how large a swing within one second does it take to disturb the traffic? |
| [08_pfe_beyond_range_study](08_pfe_beyond_range_study.md) | Study 8 (exploratory): what happens when a SLOW induced voltage takes the PFE beyond its voltage range, and what could happen below 0 V?
 This is a study with a reduced loop model, not a validated PFE model |
| [09_cable_properties](09_cable_properties.md) | Experiment 9: how do the cable properties change the outputs? |
| [10_pfe_overrange](10_pfe_overrange.md) | Experiment 10: the PFE beyond its range, with the full circuit |
| [11_nonlinear_devices](11_nonlinear_devices.md) | Experiment 11: the nonlinear devices |
| [12_earthing_gpr](12_earthing_gpr.md) | Experiment 12: how much does the landing soil matter? |
| [13_storm_impact](13_storm_impact.md) | Experiment 13: a storm that does reach the light and the traffic |

```{toctree}
:hidden:
:maxdepth: 1

01_p2p_baseline
02_storm_record
03_pfe_limit_sweep
04_regulator_tau
05_amplitude_period_map
06_spice_crosscheck
07_swing_onset
08_pfe_beyond_range_study
09_cable_properties
10_pfe_overrange
11_nonlinear_devices
12_earthing_gpr
13_storm_impact
```

## Planned

Lightning experiments (`examples/lightning/`) and branching-unit experiments (`examples/branching_units/`) are documented slots: see [Lightning](../chapters/15_lightning.md) and [Branching units](../chapters/14_branching_units.md).
