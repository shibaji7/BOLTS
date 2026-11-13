# GMD / space-weather experiments

Geomagnetic disturbances induce a slow voltage along the cable. The PFE cancels it unless it runs out of voltage range or the voltage moves
faster than its regulator. These experiments walk through that, from the quiet line to a map of amplitude against period.

| Script | Question | Expect |
|---|---|---|
| `01_p2p_baseline.py` | what does the quiet line need? | 12 repeaters, 1428.8 V, loop 816.8 ohm, no current change |
| `02_storm_record.py [csv]` | what does a voltage record do to the PFE, repeaters, light and traffic? | a stronger synthetic storm (about -200 V): PFE clamped about 29% of the time at the 1.5 kV what-if, current down about 156 mA, Q margin dips to 10.7 dB |
| `03_pfe_limit_sweep.py` | how much PFE voltage is enough? | the current falls by (storm - headroom) / R_loop (403 mA at 1.5 kV) until the limit exceeds ~1.83 kV total; then about 10 mA of cable charging current remains |
| `04_regulator_tau.py` | how much does the regulator time constant matter, and what does the sampling step hide? | ramp error tau x rate / R_loop; a 100 V jump peaks at 119 mA at 0.25 ms steps but 0.6 mA at 1 s |
| `05_amplitude_period_map.py` | how big, how fast? | headroom decides at 1.5 kV; the period barely matters |
| `06_spice_crosscheck.py` | does ngspice agree? | about 1e-9 relative |
| `07_swing_onset.py` | how large a 1-second swing disturbs traffic? | nothing below the headroom; 500 V hurts only 250G; 750 V and up lose the light |
| `08_pfe_beyond_range_study.py` | what if a slow storm takes the PFE beyond its range (and below 0 V)? | exploratory reduced loop model with protection placeholders |
| `09_cable_properties.py` | how do the cable properties change the outputs? | 4 C instead of 20 C lowers the static need by about 47 V (the whole headroom); C' sets the fast current change |
| `10_pfe_overrange.py` | the PFE beyond its range on the full circuit | slow storms, slew limit, converter failover and insulation life |
| `11_nonlinear_devices.py` | what do the Zener knee and the clamp devices do? | a knee makes the current fall far less when a storm outruns the PFE; clamps hold a surge |
| `12_earthing_gpr.py` | how much does the landing soil matter? | earth resistance, static need and GPR against the 20 V / 90 V recommendations |

Open questions these experiments are meant to sharpen: the real regulator loop shape (only a 200 Hz bandwidth is known), whether real storms have
sub-second content (our data are one value per minute), and the repeater's true current threshold. Add new experiments here as they come.
