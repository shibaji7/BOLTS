# 12. Cable properties: R, L, G, C per kilometre

> **Status:** constant, section-table, depth-profile and temperature providers implemented (v0.2 round 1) · v0.5 frequency dependence · **Code:** `bolts.properties`

## The story

A span is described by four per-length numbers: series resistance R', series inductance L', shunt leakage G' and shunt capacitance C'. The solver never
reads them directly. It asks a **property provider** for them at a position, depth, temperature and frequency, so a better cable description never
changes the solver.

```python
class RLCG:                       # one answer
    r_ohm_per_km, l_mH_per_km, g_S_per_km, c_uF_per_km

provider.rlcg(x_km, depth_m=None, temperature_C=None, f_Hz=0.0) -> RLCG
```

The span model takes `G_l = G' l` and `C_l = C' l`.

## Providers

| Provider | Version | What it adds |
|---|---|---|
| `constant` | **v0.1** | per-km R and C from the parameter set; G = 0, L = 0 (flagged assumed or unknown) |
| `section_table` (`SectionTableRLCG`) | **v0.2** | a CSV from the cable design, one row per section: `x_start_km, x_end_km, r_ohm_per_km, c_uF_per_km` and optionally `g_S_per_km, l_mH_per_km`; sections must be contiguous |
| `depth_profile` (`DepthProfileRLCG`) | **v0.2** | a wrapper: water depth along the route (and optionally a depth-to-seabed-temperature table) is passed to the provider it wraps |
| `temperature_R` (`TemperatureRLCG`) | **v0.2** | a wrapper: `R(T) = R_ref (1 + alpha (T - T_ref))`, copper alpha 0.00393 per K, T_ref 20 C; about 6% lower at 4 C |
| `freq_dependent` | v0.5 | skin effect in the conductor, dielectric dispersion for G(f) |
| `catalog` | v0.5 | named cable types |

The wrappers compose: `DepthProfileRLCG(TemperatureRLCG(SectionTableRLCG.from_csv("cable.csv")), x_km, depth_m, depth_table_m, temperature_table_C)`. Pass the result to `bolts.build_network(params, record, provider=...)`; the builder asks the provider once per span, at the span's mid-point chainage and the seabed temperature `cable.seabed_temperature_C`, so a uniform table reproduces the constant provider exactly and a two-section table gives each half its own resistance and capacitance. Using a wrapper is opt-in: the default build still uses the constant provider, so the pfe_design regression does not move. The remaining stubs (`freq_dependent`, `catalog`) raise `NotImplementedYet` with the roadmap item, so the tree is complete and an unfinished provider can never be used by accident.

## Choosing a provider without writing Python

Four parameters in `[cable]` select the provider (`bolts.properties.provider_from_parameters`), so a TOML file, `--set` on the command line or
`load_parameters(overrides=...)` is enough:

| Parameter | Values | Effect |
|---|---|---|
| `cable.section_table_csv` | `"none"` or a path | per-section R, C, G, L (columns above); `none` keeps the uniform per-km values |
| `cable.temperature_model` | `"off"` or `"copper"` | scale R by `1 + alpha (T - T_ref)`; alpha, T_ref and the seabed temperature are parameters |
| `cable.depth_profile_csv` | `"none"` or a path | columns `x_km, depth_m` |
| `cable.depth_temperature_csv` | `"none"` or a path | columns `depth_m, temperature_C`; without it the constant `cable.seabed_temperature_C` is used |

```bash
bolts run --csv data/example_vind_1s.csv --set cable.temperature_model=copper --set cable.section_table_csv=data/example_cable_sections.csv
```

**Which file format:** TOML for scalars and for choosing a table, CSV for columns of numbers (the voltage records and these route tables), JSON only for
program-readable outputs (`summary.json`, `manifest.json`). `data/example_cable_sections.csv`, `example_route_depth.csv` and `example_depth_temperature.csv` are
**illustrations of the format, not a cable design**; replace them with the route's own values.

## What the properties do to the outputs (experiment 9)

`examples/gmd/09_cable_properties.py` runs the example record at the 1.5 kV what-if (headroom 71 V with the constant cable) and the sweeps below.

| Case | Static need | Headroom | PFE clamped | Worst repeater dip |
|---|---|---|---|---|
| constant 1 ohm/km | 1428.8 V | 71 V | 29.5% | -156 mA |
| copper at 4 C | 1381.6 V | 118 V | 16.4% | -104 mA |
| illustration section table (average 1.02 ohm/km) | 1446.1 V | 54 V | 52.2% | -173 mA |
| table + depth + temperature | 1389.2 V | 111 V | 16.8% | -113 mA |

* **R' and temperature** set the static voltage the PFE must supply. Copper changes by about 0.39% per kelvin, so 16 K of cold water takes about 47 V
  off the need, as much as the whole 71 V headroom: whether a given storm clamps the PFE depends on it. From 0 C to 30 C the need runs from 1370 V to 1458 V.
* **C'** does not change the static need, but when the PFE has room (5 kV basis) the repeater current change from a fast swing is the cable's charging current,
  growing about linearly with C': a 60 V swing at 1 Hz gives 4, 9 and 28 mA at 0.05, 0.2 and 0.8 uF/km, a 500 V swing 34, 77 and 236 mA. The placeholder 0.2 uF/km is
  therefore one of the parameters that most needs a vendor value. At the 1.5 kV what-if the worst dip of a 500 V swing is set by the clamp (-525 mA at every C').

### How much the cable properties shift stress and traffic

Same storms, only the cable properties change (1.5 kV what-if; output of experiment 9, drawn in `outputs/examples/09_cable_properties/cable_properties_shift.png` and written to `shift_table.csv` there):

| Storm | Cable | PFE clamped | Shortfall (V s) | Worst dip | Q margin | 250G delivered |
|---|---|---|---|---|---|---|
| example record | constant | 29.5% | 29,572 | -156 mA | 10.70 dB | 100% |
| | copper at 4 C | 16.4% | 12,219 | -104 mA | 10.80 dB | 100% |
| | section table | 52.2% | 42,433 | -173 mA | 10.66 dB | 100% |
| | table + depth + T | 16.8% | 14,499 | -113 mA | 10.78 dB | 100% |
| example x 3 | constant | 84.0% | 234,655 | -642 mA | 6.96 dB | 82.7% |
| | copper at 4 C | 62.0% | 172,331 | -620 mA | 7.55 dB | 83.4% |
| | section table | 89.3% | 261,685 | -649 mA | 6.72 dB | 82.6% |
| | table + depth + T | 64.9% | 180,987 | -624 mA | 7.46 dB | 83.2% |
| 500 V, 1 s sine | constant | 45.0% | 15,001 | -525 mA | 9.02 dB | 0.5% |
| | copper at 4 C | 40.0% | 12,551 | -496 mA | 9.29 dB | 0.5% |
| | section table | 45.0% | 15,988 | -535 mA | 8.91 dB | 0.5% |
| | table + depth + T | 40.0% | 12,940 | -501 mA | 9.25 dB | 0.5% |

* **Stress moves a lot:** time at the cap changes by 13 percentage points (example record) to 22 points (example x 3) between the warm-uniform and the cold cases, and the shortfall integral by 59% (example record), 27% (x 3) and 16% (500 V sine) between the constant and the cold cases.
* **The optical margin moves little:** 0.1 to 0.6 dB, because the dips are set by the cap and the loop resistance, and the margin falls slowly with current.
* **Traffic moves almost not at all:** light is never lost in these cases, the 250G delivered share changes by under one percentage point in the x 3 case (82.7 to 83.4%) and not at all for the sine, whose 250G loss is set by the 1.8 dB dips, not by the cable. Cable properties shift how close the PFE is to its cap, not whether the light survives, unless a storm sits near the edge of the range.

## Why the GMD band does not need L and G

At periods of seconds and slower, the series impedance is the conductor resistance (inductive reactance is ohms against 750 ohm of resistance) and the
leakage is negligible. Capacitance matters only for how fast the cable settles after a step. For lightning (microseconds) L' and C' set the wave speed
and impedance, and the provider interface already carries them.

## Assumptions and limits

- No measured per-length G or L for any real cable is held; defaults are placeholders with their status shown.
- Uniform cable along the route in v0.1.

Next: [13. Zener and protection devices](13_zener_protection.md).
