# Changelog

All notable changes are listed here. Format: [Keep a Changelog](https://keepachangelog.com/), versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-11-12
### Changed
- Removed the stub modules `space_weather/from_scubas.py` and `from_gmd_synth.py`: a SCUBAS or synthetic record is a CSV read by `load_waveform`.
- `make lint` and the ruff check now also cover `scripts/` and `examples/`; the `stamp` docstrings of working elements no longer say "not implemented".
- The shipped example record is now a physically shaped synthetic 1 s series (`scripts/make_synthetic_vind.py`: storm backbone scaled to a peak of about -200 V, four bands of random Pc5 to Pc2 pulsations from 600 s down to 2.5 s, one onset impulse) instead of a clean sinusoidal burst; the old record is kept as `data/legacy_pfe_design_burst_1s.csv` for the regression test.
- Run figure: shorter panels for the optical and traffic traces.
- Docstrings for every public function and class, and step-by-step inline comments in the solver, builder, optics, terminal, CLI and examples.
### Added
- v0.2 round 4: landing earth resistance from the soil and a rod electrode (`landing_resistance_from_parameters`; parameters `earthing.rod_count`, `rod_length_m`, `rod_radius_m`, `rod_spacing_m`, all unknown, used with `earthing.soil_resistivity_ohm_m`); ground potential rise metrics (`bolts.earthing.gpr`: `gpr_metrics`, `required_resistance_ohm`) reported by `assess` (`earth_gpr_peak_V`, `earth_time_above_nominal_s`, `earth_time_above_exceptional_s`, `earth_resistance_ohm`); `meta["r_earth_ohm"]`; example 12 (`examples/gmd/12_earthing_gpr.py`).
- v0.2 round 3: Newton iteration for nonlinear circuits (`bolts.mna.newton`, `run_transient(..., newton=True)`, `ConvergenceError`; the regulator, clamp, slew limit and loop resistance work on the Newton path and agree with the linear path to 1e-8); `PiecewiseZener` (knee current and below-knee fraction, selected by `repeater.zener_knee_current_A` and `repeater.zener_below_knee_fraction`, both unknown); `DiodeChain` and `Arrester` nonlinear shunts; SPICE export of nonlinear branches (behavioural sources), nonlinear shunts and independent current sources; validation cases `diode_clamp` and `zener_knee`; example 11 (`examples/gmd/11_nonlinear_devices.py`).
- v0.2 round 2: PFE output slew limit and limit-state series in the regulator loop (`pfe.output_slew_limit_V_per_s`, off by default; `assess` reports `pfe_time_slew_limited_s`); `PfeConverterBank` (range with N:1 failover) used by the builder when `pfe.converter_modules` and `pfe.converter_module_rating_V` are given; `PumpLaser` (the optical chain now uses it, results unchanged); insulation life (`constant_from_reference`, `life_consumed`, `assess` key `insulation_life_consumed_max` when `cable.insulation_exponent_n` is set); parameters `converter_spare_modules`, `converter_failed_modules`, `insulation_exponent_n`, `design_life_years`; example 10 (`examples/gmd/10_pfe_overrange.py`); `plotting.style.pct()` for a percent sign that survives LaTeX.
- Provider selection from the parameters (`cable.section_table_csv`, `cable.temperature_model`, `cable.depth_profile_csv`, `cable.depth_temperature_csv`, `bolts.properties.provider_from_parameters`); the providers are re-exported from `bolts.properties`; illustration tables `data/example_cable_sections.csv`, `example_route_depth.csv`, `example_depth_temperature.csv`; example 09 (`examples/gmd/09_cable_properties.py`) with sweeps of the seabed temperature and the cable capacitance, a table and figure (`cable_properties_shift.png`, `shift_table.csv`) of how the cable properties shift PFE stress, Q margin and traffic, and the findings in the script docstring.
- v0.2 round 1: cable property providers `SectionTableRLCG`, `DepthProfileRLCG`, `TemperatureRLCG` (the network builder now asks the provider per span; `build_network(..., provider=...)`); elements `Coil`, `LandCable`, `BeachJoint`, `PfeFilter` (registered); `bolts.space_weather.synthetic.synthetic_vind` (the generator of the example record, which `scripts/make_synthetic_vind.py` now calls; the output is byte-identical); `bolts.metrics.pfe_stress` (shortfall, excess, dwell, over-current exposure) reported by `assess`; new parameters `cable.seabed_temperature_C`, `cable.conductor_tempco_per_K`, `cable.resistance_reference_temperature_C` and the unknown PFE protection parameters (`converter_module_rating_V`, `output_slew_limit_V_per_s`, `overcurrent_trip_fraction`, `overcurrent_trip_delay_s`, `trip_hold_s`, `restart_ramp_V_per_s`).
- Study 08 (`examples/gmd/08_pfe_beyond_range_study.py`): reduced loop model of a slow storm beyond the PFE range, with ride-through and over-current-trip policies (placeholders).
- Stub `bolts.mna.window_run` and `docs/dev/future_microsecond_windows.md`: the deferred microsecond-window work.
- `tests/test_audit_v01.py`: side-by-side agreement with `pfe_design` on sine records, and tests for the CLI `spice` command, `python -m bolts`, the earth electrode, user-TOML errors and the constants.
- Example 07 (`examples/gmd/07_swing_onset.py`): amplitude scan of 1 s voltage swings showing where the current, Q margin and terminal traffic start to be disturbed.
- Documentation restructured as chapters 00 to 16 (status line, story, equations, code locations, assumptions, next link), developer tooling page, generated parameter table (`make param-table`).
- Changelog guard, ruff and pylint duplicate-code configuration, pre-commit hooks; plot style aligned with the polar_connect papers; GMD experiments under `examples/gmd/`.

## [0.1.0] - 2026-11-11
### Added
- Package skeleton (`src/` layout, setuptools), LGPL-3.0-or-later license, Makefile, Read the Docs configuration, CI workflow.
- Parameter store with unit, status and source (`sourced`, `assumed`, `unknown`, `override`); shipped defaults in TOML.
- Waveforms: CSV records (seconds or ISO time, window, scale, step), step, ramp, sine, ramp-hold, double-exponential, Heidler.
- Modified nodal analysis with backward Euler, DC operating point, cached LU; elements: cable segment, repeater with a linear Zener, PFE,
  earth electrode, lumped R, L, C and voltage source.
- PFE regulator as a first-order loop integrated exactly over each step (any dt / tau).
- Point-to-point network builder; GMD source; metrics (repeater current dip, PFE headroom, conductor-to-sea voltage, Zener heat).
- Optical chain (OSNR, Q, margin, Shannon-gap rate) and terminal state machine with ES / SES / UAS counters, ported from the `pfe_design` study.
- ngspice netlist export, batch run and comparison; analytic validation cases (RC, RLC, line modes, Zener DC, energy balance).
- Earthing formulas (Wenner resistivity, rod resistance, ground potential rise), insulation life law.
- CLI (`bolts run | params | validate | spice | doctor`) and public API (`bolts.api`).
- Documented slots for branching units, nonlinear protection devices, lightning, adaptive stepping (raise `NotImplementedYet`).
