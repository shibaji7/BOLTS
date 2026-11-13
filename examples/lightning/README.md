# Lightning and thunderstorm experiments (planned, v0.2 to v0.4)

Nothing runs here yet: `bolts.lightning` and the surge elements are documented slots. Planned experiments (see `docs/theory/lightning.md`):

| Planned script | Question |
|---|---|
| `01_station_gpr.py` | ground potential rise at a landing for a 10/350 us stroke, against the 20 V and 90 V earth limits |
| `02_land_cable_entry.py` | what reaches the PFE when a stroke hits the land cable near the grounding point |
| `03_protection_chain.py` | what the arrester, coil and Zener stages do to the surge that reaches a repeater |
| `04_monte_carlo_exceedance.py` | exceedance curve of repeater stress for a site's thunderstorm statistics |

Needs verified IEC 62305 / CIGRE parameters, cable inductance and nonlinear devices first.
