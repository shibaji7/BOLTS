# API reference

The whole study fits in a handful of functions, `bolts.api`, all re-exported from `bolts`:

```python
import bolts

params = bolts.load_parameters()                                   # shipped defaults, every value with unit, status and source
record = bolts.load_waveform("data/example_vind_1s.csv", params=params)
net = bolts.build_network(params, record)
result = bolts.run_transient(net, params)
summary = bolts.assess(result)                                    # electrical, optical and traffic metrics
```

## Public API at a glance

| Name | What it does |
|---|---|
| {py:class}`Result <bolts.result.Result>` | A finished run. Holds the inputs (network, parameters) and the raw transient; every derived quantity is computed on request. |
| {py:func}`assess <bolts.api.assess>` | Electrical, optical and traffic metrics of a run, in one flat dictionary. |
| {py:func}`build_network <bolts.network.builder.build_network>` | Build the circuit of a power-feed line: PFE A, cable spans with a repeater after each, PFE B, and the sea return through the landing earths. |
| {py:func}`export_spice <bolts.api.export_spice>` | Write an ngspice netlist of the circuit, for an independent cross-check. |
| {py:func}`load_parameters <bolts.config.loader.load_parameters>` | Load the parameter set: shipped defaults, then an optional user TOML file, then explicit overrides. |
| {py:func}`load_waveform <bolts.api.load_waveform>` | Read a voltage record: the net induced voltage along the cable as a function of time. |
| {py:func}`register_element <bolts.registry.register_element>` | Register an element factory under `name` so a network can create it by name (see "Adding an element" in the developer guide). |
| {py:func}`register_waveform <bolts.registry.register_waveform>` | Register a waveform factory under `name`. |
| {py:func}`run_transient <bolts.api.run_transient>` | Run a built network through time (backward Euler on the modified-nodal-analysis system, the PFE regulator integrated exactly over each step). |

Each section below opens with what the subpackage is for and the chapters that explain it. Click a module for its page: a summary table of its classes and
functions, then every entry with its signature, parameters, return value and a `[source]` link.

## Top level

**Read first:** [Overview](../chapters/00_overview.md), [Run and extend](../chapters/10_run_and_extend.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.api
   bolts.cli
   bolts.constants
   bolts.errors
   bolts.registry
   bolts.result
   bolts.units
```

## config: parameters with provenance

Every number in a run is a `Param` (value, unit, status = sourced / assumed / unknown / override, source). `load_parameters` merges the shipped TOML defaults, an optional user file and `--set section.key=value` overrides; an `unknown` value raises `MissingParameter` when it is used.

Status: implemented. Chapter 07 (parameters and provenance).

**Read first:** [Parameters and provenance](../chapters/07_parameters_and_provenance.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.config.loader
   bolts.config.overrides
   bolts.config.provenance
   bolts.config.schema
   bolts.config.validate
```

## damage: life laws

`insulation_withstand` implements V^n t = constant (Chesnoy Eq. 10.1) with Miner's rule over a record. `arrester_energy`, `thermal_i2t` and `criteria` are documented stubs for v0.4.

Status: insulation life implemented; the rest planned. Chapter 16 (earthing and damage).

**Read first:** [Earthing and damage](../chapters/16_earthing_damage.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `arrester_energy`, `criteria`, `thermal_i2t`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.damage.arrester_energy
   bolts.damage.criteria
   bolts.damage.insulation_withstand
   bolts.damage.thermal_i2t
```

## earthing: soil, electrodes, GPR

Wenner resistivity (Eq. 10.2), a single rod (Eq. 10.3), rods in a line (Eq. 10.4, Sunde form) and the ground potential rise GPR = I R against the 20 V / 90 V recommendations. `impulse_impedance` (soil ionisation, frequency dependence) is a stub for v0.5.

Status: implemented except the impulse impedance. Chapter 16.

**Read first:** [Earthing and damage](../chapters/16_earthing_damage.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `impulse_impedance`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.earthing.electrode_resistance
   bolts.earthing.gpr
   bolts.earthing.impulse_impedance
   bolts.earthing.soil
```

## elements: devices that stamp into the circuit

Circuit elements. Each is a small class with ``stamp(st)``; register your own with :func:`bolts.registry.register_element`.

**Read first:** [Zener and protection](../chapters/13_zener_protection.md), [Repeater and optics](../chapters/04_repeater_and_optics.md), [Power feeding](../chapters/02_power_feeding.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `beach_joint`, `branching_unit`, `fit_zener`, `relay`, `shunt_fault`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.elements.arrester
   bolts.elements.base
   bolts.elements.beach_joint
   bolts.elements.branching_unit
   bolts.elements.cable_segment
   bolts.elements.coil
   bolts.elements.diode_chain
   bolts.elements.earth_electrode
   bolts.elements.fit_zener
   bolts.elements.land_cable
   bolts.elements.lumped
   bolts.elements.pfe
   bolts.elements.pfe_converter_bank
   bolts.elements.pfe_filter
   bolts.elements.pfe_regulator
   bolts.elements.pump_laser
   bolts.elements.relay
   bolts.elements.repeater
   bolts.elements.shunt_fault
   bolts.elements.zener
```

## impact: optics and terminal

`optical` turns the current at each repeater into pump power, OSNR, Q and bit-error margin; `terminal` turns the Q margin into link state and lost traffic with placeholder timings. Ported from the pfe_design study.

Status: implemented. Chapters 04 and 05.

**Read first:** [Repeater and optics](../chapters/04_repeater_and_optics.md), [Terminal and traffic](../chapters/05_terminal_and_traffic.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.impact.optical
   bolts.impact.terminal
```

## io: reading and writing

`writers` and `readers` handle `series.csv` and `summary.json`; `manifest` records the version, the parameter fingerprint and the time of a run so a result can be traced back.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.io.manifest
   bolts.io.readers
   bolts.io.writers
```

## lightning (planned)

Documented stubs only: stroke parameters (IEC 62305), statistics, Monte Carlo, coupling and protection staging. They raise `NotImplementedYet` until the standard's values are in hand; deferred by decision.

Status: planned. Chapter 15 (lightning).

**Read first:** [Lightning](../chapters/15_lightning.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `coupling`, `monte_carlo`, `protection_stage`, `statistics`, `stroke_parameters`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.lightning.coupling
   bolts.lightning.monte_carlo
   bolts.lightning.protection_stage
   bolts.lightning.statistics
   bolts.lightning.stroke_parameters
```

## lines: transmission-line helpers

`lumped_ladder` and `sectioning` choose how many lumped sections a cable needs (section delay well below the signal rise time); `telegrapher` gives the characteristic impedance and delay. `bergeron` (travelling-wave line for microsecond surges) is a stub.

Status: implemented except `bergeron`. Chapter 03.

**Read first:** [The circuit model](../chapters/03_circuit_model.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `bergeron`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.lines.bergeron
   bolts.lines.lumped_ladder
   bolts.lines.sectioning
   bolts.lines.telegrapher
```

## metrics: what a run is judged by

Each module turns time series from a run into numbers: how far the current falls (`current_dip`), how much PFE range is left and for how long it sat at a limit (`headroom`, `pfe_stress`), the Zener heat against normal (`device_stress`), the conductor-to-sea voltage (`voltage_extremes`) and energy (`energy`). `Result.assess` collects them.

Status: implemented. Chapters 02 and 04.

**Read first:** [Power feeding](../chapters/02_power_feeding.md), [Repeater and optics](../chapters/04_repeater_and_optics.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.metrics.current_dip
   bolts.metrics.device_stress
   bolts.metrics.energy
   bolts.metrics.headroom
   bolts.metrics.pfe_stress
   bolts.metrics.voltage_extremes
```

## mna: the circuit solver

`stamp` and `assemble` build the matrices, `dc_op` the starting state, `transient` marches in time (with the PFE regulator integrated exactly over each step), `newton` handles nonlinear devices, `integrators` and `linear_solve` are the numerical parts. `window_run` (microsecond windows) is deferred.

Status: implemented except `window_run`. Chapter 03 (the circuit model).

**Read first:** [The circuit model](../chapters/03_circuit_model.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `timestep`, `window_run`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.mna.assemble
   bolts.mna.dc_op
   bolts.mna.integrators
   bolts.mna.linear_solve
   bolts.mna.newton
   bolts.mna.stamp
   bolts.mna.timestep
   bolts.mna.transient
   bolts.mna.window_run
```

## network: topology and power modes

`build_network` turns a parameter set and a record into a `Network`: PFE A, cable spans with repeaters, PFE B and the sea return. `graph` holds the container, `validate` checks connectivity. Trunk-and-branch topologies, power modes, segments and switch states are stubs for v0.3.

Status: point-to-point implemented. Chapters 03 and 14.

**Read first:** [The circuit model](../chapters/03_circuit_model.md), [Branching units](../chapters/14_branching_units.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `segments`, `switch_states`, `topology_trunk_branch`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.network.builder
   bolts.network.graph
   bolts.network.power_modes
   bolts.network.segments
   bolts.network.switch_states
   bolts.network.topology_p2p
   bolts.network.topology_trunk_branch
   bolts.network.validate
```

## plotting: figures in the paper style

`style` sets the shared look (including `pct()`, a percent sign that survives LaTeX), `timeseries` draws the standard five-panel run figure and `network` the conductor-to-sea voltage along the cable. Install the `plots` extra.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.plotting.network
   bolts.plotting.style
   bolts.plotting.timeseries
```

## properties: cable R, L, G, C

Cable property providers: how R, L, G and C along the route are known. A provider answers ``rlcg(x_km, ...)``; the wrappers compose.

**Read first:** [Cable properties](../chapters/12_cable_properties.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `catalog`, `freq_dependent`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.properties.base
   bolts.properties.catalog
   bolts.properties.constant
   bolts.properties.depth_profile
   bolts.properties.factory
   bolts.properties.freq_dependent
   bolts.properties.section_table
   bolts.properties.temperature_R
```

## space_weather: GMD forcing

`gmd_source` spreads a net end-to-end induced voltage V_ind(t) over the spans, `from_efield` computes V = E L from a uniform field, `synthetic` generates the shipped physically-shaped example record. A SCUBAS or measured series is read as CSV through `load_waveform`.

Status: implemented. Chapters 01 and 06.

**Read first:** [From storm to volts](../chapters/01_storm_to_volts.md), [Field along the link](../chapters/06_field_along_the_link.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.space_weather.from_efield
   bolts.space_weather.gmd_source
   bolts.space_weather.synthetic
```

## spice: export and cross-check

`netlist` writes a netlist (linear and nonlinear branches, shunts, current sources), `run_ngspice` runs it in batch mode and reads the node voltages, `compare` measures the difference. Needs the `ngspice` binary.

Status: implemented. Chapter 09 (validation).

**Read first:** [Validation and tests](../chapters/09_validation_and_tests.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.spice.compare
   bolts.spice.netlist
   bolts.spice.run_ngspice
```

## studies: sweeps and maps

`sweep` runs a study function over a list of values of one parameter, `sensitivity` changes each listed parameter up and down, `map2d` fills a grid of one metric. The GMD experiments use them.

Status: implemented. Chapter 10.

**Read first:** [Run and extend](../chapters/10_run_and_extend.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.studies.map2d
   bolts.studies.sensitivity
   bolts.studies.sweep
```

## validation: analytic cases

Analytic validation cases. Each module has ``run() -> ValidationCase``; ``run_all()`` runs them (``bolts validate``).

**Read first:** [Validation and tests](../chapters/09_validation_and_tests.md)

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.validation.diode_clamp
   bolts.validation.energy_balance
   bolts.validation.line_step
   bolts.validation.rc_step
   bolts.validation.rlc_ring
   bolts.validation.zener_dc
   bolts.validation.zener_knee
```

## waveforms: records and pulses

Waveforms. The built-in constructors are registered by name (``bolts.registry.get_waveform("sine")``); register your own with
:func:`bolts.registry.register_waveform` or the ``bolts.waveforms`` entry-point group.

**Read first:** [From storm to volts](../chapters/01_storm_to_volts.md)

*Stubs (documented slots that raise `NotImplementedYet`):* `iec62305`

```{eval-rst}
.. autosummary::
   :toctree: generated
   :recursive:

   bolts.waveforms.base
   bolts.waveforms.combine
   bolts.waveforms.csv_record
   bolts.waveforms.double_exp
   bolts.waveforms.heidler
   bolts.waveforms.iec62305
   bolts.waveforms.step_ramp_sine
   bolts.waveforms.window
```

## Conventions

- Quantities carry their unit in the name (`r_ohm_per_km`, `dt_s`, `v_tot_V`); no unit objects are used.
- Every parameter is a `Param` with a status (`sourced`, `assumed`, `unknown`, `override`); using an `unknown` one raises `MissingParameter`.
- Stubs raise `NotImplementedYet` with a pointer to the roadmap.
- Equations and sources are in each module docstring; the chapters give the story around them.
