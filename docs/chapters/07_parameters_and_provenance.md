# 07. Where the numbers come from

> **Status:** implemented · **Code:** `bolts.config` (provenance, schema, loader, overrides, validate), `src/bolts/config/defaults/*.toml`

## The story

A model is only as honest as its inputs. In BOLTS **every parameter is a table** `{ value, unit, status, source }`, so you can always ask where a number
came from, and the code **refuses to guess** a number that nobody knows.

| Status | Meaning | Behaviour |
|---|---|---|
| **sourced** | taken from a document; the source names it (book and printed page, standard, paper) | used as is |
| **assumed** | an illustrative placeholder, to be replaced or swept | used, and flagged in every result |
| **unknown** | `"TBD"`: nobody has the value | asking for it raises `MissingParameter` with the reason |
| **override** | changed for one run (`--set`, `overrides=`, or a bare value in your own TOML) | used; the old source is kept in the new one |

```python
params = bolts.load_parameters("my.toml", overrides={"cable.length_km": 400.0})
params.param("cable", "resistance_ohm_per_km")     # value, unit, status, source
params.get("cable", "inductance_mH_per_km")        # MissingParameter: cable inductance is unknown
```

A user file may use bare values; keys must already exist in the defaults (a typo is an error, not a silent new setting). Every run writes a **manifest**
with the parameter fingerprint, so a result can be traced to its inputs.

## Which numbers matter

| Parameter | Status | Why it matters |
|---|---|---|
| the voltage record | input | everything follows from it ([01](01_storm_to_volts.md)) |
| `pfe.max_voltage_kV_per_end` | assumed (design basis) | the headroom decides whether a storm gets through ([02](02_power_feeding.md)) |
| `pfe.regulator_response_s` | assumed (from the 200 Hz bandwidth) | the ramp error and the response to fast swings ([03](03_circuit_model.md)) |
| `repeater.dynamic_resistance_ohm` | assumed | sets `R_loop`, so the current change per volt |
| `optical.laser_threshold_fraction` | assumed | where the pump starves |
| `optical.relock_time_s`, `adaptation_delay_s` | assumed | traffic loss for fast dips ([05](05_terminal_and_traffic.md)) |
| `cable.capacitance_uF_per_km`, `leakage_S_per_km` | assumed | cable settling and charging currents ([12](12_cable_properties.md)) |
| the `unknown` Zener, BU, lightning and filter parameters | unknown | needed for v0.2 to v0.4 |

`bolts params --status unknown` lists what is still missing. The practical conclusion for a vendor or designer is a short list of what to ask for:
the PFE regulator's step response, the repeater's protection circuit and current thresholds, the terminal's relock time, the cable's per-length G, C and L,
and a real power-feed record during a storm.

## Every parameter (generated)

<!-- PARAMS:START -->
| key | value | unit | status | source |
|---|---|---|---|---|
| `bu.sea_earth_resistance_ohm` | TBD | ohm | unknown | BU sea-earth electrode; design data |
| `bu.relay_on_resistance_ohm` | TBD | ohm | unknown | power-switching relay in the closed state |
| `bu.current_limiting_ohm` | TBD | ohm | unknown | resistor bank used against hot switching (Chesnoy p. 395) |
| `bu.electrode_mass_kg` | 25.0 | kg | sourced | Chesnoy p. 395: a copper BU sea-earth electrode has a mass of about 25 kg |
| `cable.length_km` | 750.8 | km | assumed | Point Hope to Gambell link of the pfe_design study (route chainage 5601.2 to 6352.0 km); replace for another link |
| `cable.resistance_ohm_per_km` | 1.0 | ohm/km | sourced | Chesnoy ch.13 (printed p. 479): typical linear ohmic resistance about 1 ohm/km |
| `cable.capacitance_uF_per_km` | 0.2 | uF/km | assumed | placeholder, conductor to sea; vendor value unknown. Provider: bolts.properties (constant now, section table in v0.2) |
| `cable.leakage_S_per_km` | 0.0 | S/km | assumed | placeholder (G' = 0); vendor value unknown. Provider: bolts.properties |
| `cable.inductance_mH_per_km` | TBD | mH/km | unknown | needed for microsecond surges (v0.2); not used by the slow GMD runs. A few tenths of a henry over 750 km is the pfe_design estimate |
| `cable.emf_share_of_loop` | 1.0 |  | assumed | fraction of the record's net end-to-end voltage applied along the cable (spread evenly over every span) |
| `cable.seabed_temperature_C` | 4.0 | C | assumed | deep-sea water temperature (about 2 to 4 C); used only by the temperature-dependent provider (bolts.properties.temperature_R), which is opt-in. Replace with the route's measured seabed temperature |
| `cable.conductor_tempco_per_K` | 0.00393 | 1/K | assumed | textbook temperature coefficient of copper resistance at 20 C; check against the cable vendor's conductor datasheet |
| `cable.resistance_reference_temperature_C` | 20.0 | C | assumed | temperature at which resistance_ohm_per_km is taken to apply when the temperature-dependent provider is used; the sourced 1 ohm/km does not state one |
| `cable.temperature_model` | off |  | assumed | 'off' keeps the constant resistance_ohm_per_km; 'copper' scales it by 1 + alpha (T - T_ref) at the seabed temperature (bolts.properties.temperature_R). Off by default so the pfe_design regression holds |
| `cable.section_table_csv` | none |  | assumed | path to a per-section table (x_start_km, x_end_km, r_ohm_per_km, c_uF_per_km[, g_S_per_km, l_mH_per_km]) from the cable design; 'none' = uniform values above. data/example_cable_sections.csv is an illustration only |
| `cable.depth_profile_csv` | none |  | assumed | path to the route's water depth (columns x_km, depth_m); 'none' = depth ignored. data/example_route_depth.csv is an illustration only |
| `cable.depth_temperature_csv` | none |  | assumed | path to seabed temperature by depth (columns depth_m, temperature_C); 'none' = the constant seabed_temperature_C. data/example_depth_temperature.csv is an illustration only |
| `cable.insulation_exponent_n` | TBD |  | unknown | exponent n of the insulation life law V^n t = constant (Chesnoy Eq. 10.1, from Dakin 1983); device-specific, unpublished. Sweep 10 to 40 in studies |
| `cable.design_life_years` | 25.0 | years | assumed | typical design life of submerged plant; used with the nominal end voltage as the reference point of the life law. Confirm with the operator |
| `earthing.landing_earth_resistance_ohm` | 3.0 | ohm | sourced | Chesnoy Sec. 10.2.4 (p. 387): system earth electrodes typically below 3 ohm (upper bound used) |
| `earthing.station_vs_system_earth_V_nominal` | 20.0 | V | sourced | Chesnoy Sec. 10.2.4 (p. 387): recommended nominal difference between system earth and station earth, at most 20 V (reference) |
| `earthing.station_vs_system_earth_V_lightning` | 90.0 | V | sourced | Chesnoy Sec. 10.2.4 (p. 387): exceptional increase to 90 V in a lightning environment (reference) |
| `earthing.soil_resistivity_ohm_m` | TBD | ohm m | unknown | soil resistivity at the landing; measure with the Wenner method (bolts.earthing.soil.wenner_resistivity_ohm_m). With the four rod_* parameters it sets the landing earth resistance instead of the 3 ohm bound. Typical range 10 (wet) to 3000 ohm m (rock) |
| `earthing.rod_count` | TBD |  | unknown | number of buried rods in a line at each landing (1 to 4; Chesnoy Eq. 10.4 tabulates lambda for 2, 3 and 4); station design |
| `earthing.rod_length_m` | TBD | m | unknown | buried length b of each rod (Chesnoy Eq. 10.3); station design |
| `earthing.rod_radius_m` | TBD | m | unknown | radius r of each rod; station design |
| `earthing.rod_spacing_m` | TBD | m | unknown | spacing a between rods in the line (needed for n >= 2); station design |
| `forcing.csv_path` | data/example_vind_1s.csv |  | assumed | path to the voltage CSV, relative to the current directory (or absolute). The shipped file is SYNTHETIC (storm backbone (peak about -200 V), random 2.5 to 600 s pulsations, one onset impulse; scripts/make_synthetic_vind.py); replace it with your 1-second or sub-second record |
| `forcing.time_column` | t_s |  | assumed | name of the time column |
| `forcing.time_format` | seconds |  | assumed | 'seconds' (any origin; the run starts at 0) or 'iso' (ISO-8601 timestamps) |
| `forcing.voltage_column` | v_ind_V |  | assumed | name of the voltage column (volts) |
| `forcing.scale` | 1.0 |  | assumed | multiplies every voltage in the file |
| `forcing.window_start_s` | 0.0 | s | assumed | start of the window, seconds from the first row |
| `forcing.window_end_s` | -1.0 | s | assumed | end of the window, seconds from the first row; negative means the end of the file |
| `forcing.model_dt_s` | 0.0 | s | assumed | step of the run; 0 = the file's own spacing; otherwise resampled by linear interpolation |
| `lightning.peak_current_median_kA` | TBD | kA | unknown | median first-stroke peak current (log-normal statistics); verify against CIGRE / IEEE |
| `lightning.ground_flash_density_per_km2_yr` | TBD | 1/(km2 yr) | unknown | site thunderstorm statistics (keraunic level) |
| `lightning.rod_to_pfe_earth_separation_m` | TBD | m | unknown | Chesnoy p. 390: the influence is roughly inversely proportional to the separation of the two earths |
| `optical.laser_threshold_fraction` | 0.2 |  | assumed | pump threshold as a fraction of the nominal laser current; vendor unknown (swept 0, 0.2, 0.4 in pfe_design) |
| `optical.noise_figure_dB` | 4.5 | dB | sourced | Chesnoy Sec. 4.4.5 (printed p. 143): noise figure 4.5 dB in the worked example |
| `optical.output_power_per_channel_dBm` | -2.5 | dBm | assumed | repeater output per channel; from the Chesnoy p. 143 example (does not reproduce with its own formula) |
| `optical.fiber_attenuation_dB_per_km` | 0.2 | dB/km | sourced | Chesnoy Sec. 5.4.2.2 (printed p. 191) |
| `optical.extra_span_loss_dB` | 0.0 | dB | assumed | splices, connectors, repairs (repairs 3 dB deep water, 0.5 dB shallow, p. 191) |
| `optical.osnr_constant_dB` | 58.0 | dB | sourced | Chesnoy Eq. 5.23 (printed p. 189): OSNR = P_in - 10 log10 k - NF + 58 (P_in = repeater INPUT power per wavelength) |
| `optical.optical_bandwidth_GHz` | 12.5 | GHz | sourced | Chesnoy Sec. 3.4.6 (printed p. 88): 0.1 nm = 12.5 GHz at 1550 nm |
| `optical.baud_rate_GBd` | 25.0 | GBd | sourced | Chesnoy Fig. 5.25 (printed p. 190): theoretical 25 GBd PDM-QPSK transponder (the ITU table implies about 44 GBd) |
| `optical.channel_rate_Gbps` | 100.0 | Gbit/s | assumed | reference channel for the Shannon-gap calibration |
| `optical.penalties_total_dB` | 3.5 | dB | sourced | Chesnoy Table 5.1 (p. 199): 3.5 dB of impairments of the ITU-T G.977 example (10 000 km; conservative for a short link) |
| `optical.terminal_back_to_back_Q_dB` | 17.1 | dB | sourced | Chesnoy Table 5.1 (p. 199) line 4; combined by Eq. 5.29 (p. 200) |
| `optical.q2_limit_dB` | 5.0 | dB | sourced | Chesnoy Table 5.1 (p. 199) line 6 'Q limit compliance with ITU after FEC' = 5.0 dB (defined p. 201) |
| `optical.bits_per_symbol_ladder` | [2, 3, 4, 5, 6] |  | sourced | Chesnoy Sec. 5.7.2 (printed pp. 225-227): QPSK 2, 8QAM 3, 16QAM 4, 32QAM 5, 64QAM 6 bits per symbol |
| `optical.relock_time_s` | 10.0 | s | assumed | receiver relock after an outage; not given by Chesnoy (cycle slips corrupt symbols until the next pilot frame, p. 187); vendor. Swept 0 to 30 s in pfe_design |
| `optical.adaptation_delay_s` | 5.0 | s | assumed | outage time before the terminal steps down a format; vendor unknown |
| `optical.upshift_hold_s` | 60.0 | s | assumed | margin must hold this long before stepping back up |
| `optical.switch_margin_dB` | 0.5 | dB | assumed | spare SNR required when stepping to another format |
| `pfe.feed_current_A` | 1.0 | A | assumed | inside the sourced 0.5 to 1.5 A repeater range (Chesnoy ch.12) |
| `pfe.max_voltage_kV_per_end` | 2.5 | kV | assumed | operator basis of pfe_design: 5 kV in total, 2.5 kV per end with the 50/50 split. Override for what-ifs (pfe_design also ran 0.75 kV per end = 1.5 kV total) |
| `pfe.split_fraction_end_A` | 0.5 |  | sourced | NEC / Chesnoy p. 392: each end normally feeds half of the system voltage, with opposite signs |
| `pfe.feed_configuration` | double_end |  | sourced | Chesnoy pp. 392-393: double-end feeding; single_end after one PFE fails |
| `pfe.feed_direction` | 1 |  | assumed | +1: feed current flows toward increasing chainage; an induced voltage along +chainage then assists the PFEs |
| `pfe.regulator_bandwidth_Hz` | 200.0 | Hz | sourced | Chesnoy Sec. 10.3.2 (p. 390): a PFE current controller typically operates on a control loop of around 200 Hz bandwidth (stated in a lightning discussion; no loop shape given) |
| `pfe.regulator_response_s` | 0.005 | s | assumed | tau = 1 / regulator_bandwidth_Hz = 5 ms (convention of the pfe_design study, no 2 pi); the 1/(2 pi 200 Hz) = 0.8 ms reading is a sensitivity. First-order loop, integrated exactly over each step |
| `pfe.converter_modules` | TBD |  | unknown | series converter modules per PFE (n+1 redundancy); a vendor catalogue shows 6 with 5 needed, Chesnoy p. 398: N:1 protected |
| `pfe.failover_time_s` | TBD | s | unknown | converter transfer time; a web claim of under 50 ms is unverified and is NOT used |
| `pfe.output_filter_L_mH` | TBD | mH | unknown | PFE output filter inductance (v0.2 surges); vendor |
| `pfe.output_filter_C_uF` | TBD | uF | unknown | PFE output filter capacitance (v0.2 surges); vendor |
| `pfe.converter_module_rating_V` | TBD | V | unknown | voltage rating of one series converter module (the PFE cap is about modules x rating); vendor. For studies the cap is max_voltage_kV_per_end |
| `pfe.output_slew_limit_V_per_s` | TBD | V/s | unknown | fastest rate at which the PFE can change its output (slow ramp-up/down, Chesnoy p. 397); vendor. Sweep 10 V/s to 1 kV/s in studies |
| `pfe.overcurrent_trip_fraction` | TBD |  | unknown | line current, as a multiple of the set current, above which the PFE shuts itself down (Chesnoy p. 397: 'a specified threshold'); vendor. Study 08 sweeps 1.2, 1.5 and 2.0 |
| `pfe.overcurrent_trip_delay_s` | TBD | s | unknown | how long the current must stay above the trip level before the PFE shuts down; vendor. Study 08 uses 1 s |
| `pfe.trip_hold_s` | TBD | s | unknown | time from a trip to a restart attempt, including discharge of the cable (resistive, then short, Chesnoy p. 397); operator procedure. Study 08 uses 30 s |
| `pfe.restart_ramp_V_per_s` | TBD | V/s | unknown | voltage ramp-up rate of a restart; vendor. Study 08 uses 20 V/s |
| `pfe.converter_spare_modules` | 1 |  | assumed | N:1 protection (Chesnoy p. 397): one spare module per bank; a vendor catalogue shows 6 modules with 5 needed |
| `pfe.converter_failed_modules` | 0 |  | assumed | modules out of service in a what-if; 0 = healthy. Used only when converter_modules and converter_module_rating_V are given |
| `repeater.spacing_km` | 60.0 | km | assumed | typical spacing; Chesnoy examples use 50 to 70 km (p. 191) |
| `repeater.voltage_drop_V` | 56.0 | V | sourced | Chesnoy ch.12 (pp. 430-431): about 56 V for an 8 amp-pair unipolar repeater (Zener stack) |
| `repeater.dynamic_resistance_ohm` | 5.0 | ohm | assumed | placeholder slope of the Zener stack; vendor value unknown (pfe_design swept 0 to 60 ohm) |
| `repeater.current_margin_fraction` | 0.1 |  | sourced | Chesnoy Table 10.1 (p. 385): 10% electroding margin |
| `repeater.pump_current_fraction` | 0.8 |  | sourced | Chesnoy Table 10.1 (p. 385): laser current 80% of the line current |
| `repeater.control_current_fraction` | 0.1 |  | sourced | Chesnoy Table 10.1 (p. 385): control circuit 10% |
| `repeater.zener_knee_current_A` | TBD | A | unknown | v0.2 piecewise Zener: current where the stack starts to conduct; vendor datasheet |
| `repeater.zener_power_rating_W` | TBD | W | unknown | continuous power rating of the shunt stack (damage criterion); vendor |
| `repeater.zener_surge_rating_A` | TBD | A | unknown | 8/20 us surge rating of the clamp; the book gives only the repeater bypass (200 A long pulses, 450 A at 15 kV short pulses, p. 392) |
| `repeater.zener_temp_coeff_mV_per_K` | TBD | mV/K | unknown | temperature coefficient of the stack voltage (v0.5 electro-thermal Zener); vendor |
| `repeater.housing_capacitance_nF` | TBD | nF | unknown | repeater housing to sea, the surge path to earth (v0.2); vendor |
| `repeater.zener_below_knee_fraction` | TBD |  | unknown | voltage across the repeater at zero current as a fraction of its value at the knee: 0 = the repeater circuit is resistive below the knee (the voltage falls to zero with the current), 1 = the voltage stays put (laser-diode-like). Used with zener_knee_current_A; if only the knee is given the model uses 0, the strongest effect. Study range 0 to 0.9 |
| `solver.dt_s` | 0.1 | s | assumed | time step of the transient. The regulator is integrated exactly, so any dt / tau is accepted; a jump between two samples is a ramp over dt |
| `solver.integrator` | backward_euler |  | assumed | backward_euler (stable for the stiff ladder); trapezoid is planned |
<!-- PARAMS:END -->

## Assumptions and limits of this chapter

- **Sweeps are one at a time** (`bolts.studies.sensitivity`); combinations need `map2d` or your own loop.
- **Placeholders inside scenarios**: the stress waves of the examples are made up and sized for this link.
- A parameter's `source` is a citation, not a verification: values marked "to be verified" really are.

Next: [08. Limits and what is left out](08_limitations_and_not_implemented.md).
