# Roadmap

Status key: **done** = implemented and tested, **slot** = module exists and raises `NotImplementedYet`, **later** = not started.

| Version | Scope | Status |
|---|---|---|
| **v0.1** | package skeleton, config with provenance, waveforms (CSV, step, ramp, sine, double-exponential, Heidler), constant RLCG provider, cable ladder, linear repeater, PFE with the exact first-order regulator, earth electrode, point-to-point builder, MNA with backward Euler, current-dip and headroom metrics, optical and terminal chain, API and CLI, analytic validation, ngspice export and compare, Makefile, docs | **done** |
| v0.2 | `properties`: section table, depth and temperature dependence; `elements`: piecewise Zener, diode chain, coil, arrester, pump laser, land cable, beach joint, PFE output filter; `lightning`: stroke parameters (IEC 62305 values verified from the standard) and coupling into the station earth; `earthing`: ground potential rise with measured resistivity; PFE over-range stress (converter bank with per-module voltage rating, regulator saturation, `metrics/pfe_stress`, `V^n t` insulation life from Chesnoy Eq. 10.1); `mna.newton`: nonlinear solver; SPICE for nonlinear parts; `space_weather` bridges to SCUBAS and gmd_synth | **released as 0.2.0 (not yet committed), feature-complete except the deferred items**: rounds 1 to 4 done (cable providers, coil, land cable, beach joint, PFE filter, synthetic-record library, PFE stress metrics, slew limit, converter bank, pump laser, insulation life); Newton solver, piecewise Zener, diode chain, arrester, SPICE for nonlinear parts; ground potential rise with soil and rod electrodes; **deferred out of v0.2:** IEC 62305 stroke values and lightning coupling, the microsecond window run; plan in `docs/dev/` and the project plan |
| v0.3 | `network`: trunk-and-branch topologies, branching-unit circuit and relays, switching sequences (zero-potential, current-limiting resistors), powering modes and polarity (electrode elution), powering segments; shunt faults; `lines.bergeron` travelling-wave line; adaptive time step; trapezoid integrator ; PFE protection trips (over-voltage, over-current, open circuit), discharge and slow-ramp restart as a state machine in the transient loop | slot |
| v0.4 | thunderstorm statistics and Monte Carlo (flash density, peak-current distribution, exceedance curves), protection staging, `damage` criteria (insulation withstand, I2t, arrester energy) | slot |
| v0.5 | frequency-dependent cable (skin effect, dielectric dispersion), impulse earth impedance with soil ionisation, electro-thermal Zener, converter failover | slot |
| v1.0 | validation report, API freeze, full documentation, PyPI release | later |

## Open questions that block data-driven work

Vendor data for the repeater protection circuit (Zener voltage, knee, rating, surge rating), the PFE output filter and converter failover,
the branching-unit architecture, measured soil resistivity at the landings, and a real power-feed record during a storm to validate against.
`bolts params --status unknown` lists every such parameter.
