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
| [`Result`](core.md#bolts.api) | A finished run. Holds the inputs (network, parameters) and the raw transient; every derived quantity is computed on request. |
| [`assess`](core.md#bolts.api) | Electrical, optical and traffic metrics of a run; `targets` are the terminal rates (Gbit/s) to evaluate. |
| [`build_network`](core.md#bolts.api) | Entry point for building a network. `record` is the net induced voltage in volts (`None` = a quiet line). `provider` is a cable-property prov... |
| [`export_spice`](core.md#bolts.api) | Write an ngspice netlist of the circuit, for an independent cross-check. Imported lazily: the SPICE code is optional. |
| [`load_parameters`](core.md#bolts.api) | Shipped defaults, then the optional user TOML `path`, then `overrides` ({"section.name": value}). |
| [`load_waveform`](core.md#bolts.api) | Read a voltage record. With `params` the columns, time format, window, scale and step come from its `[forcing]` section |
| [`register_element`](core.md#bolts.api) | Register an element factory under `name` (a class or a function returning an element). |
| [`register_waveform`](core.md#bolts.api) | Register a waveform factory under `name` (a function returning a :class:`~bolts.waveforms.base.Record`). |
| [`run_transient`](core.md#bolts.api) | Run a built network. The time axis is `t_s` if given, else the record's duration at `dt_s` (default: the record's own spacing, |

## By subpackage

Each page opens with what the subpackage is for, the chapters that explain it, a table of its modules (stubs are flagged) and the full reference.

| Subpackage | Modules | Purpose |
|---|---|---|
| [Top level](core.md) | 7 | The API, the result object, the registry, units, constants and errors. |
| [config: parameters with provenance](config.md) | 5 | Parameters with provenance: load, override and validate the parameter set. |
| [damage: life laws](damage.md) | 4 | Life laws and failure criteria for the devices a surge or storm loads. |
| [earthing: soil, electrodes, GPR](earthing.md) | 4 | Soil, electrodes and ground potential rise at the landing stations. |
| [elements: devices that stamp into the circuit](elements.md) | 20 | Circuit elements. Each is a small class with ``stamp(st)``; register your own with :func:`bolts.registry.register_element`. |
| [impact: optics and terminal](impact.md) | 2 | From line current to the consequences: light, bit errors and traffic. |
| [io: reading and writing](io.md) | 3 | Reading and writing results: CSV for time series, JSON for numbers, a manifest for provenance. |
| [lightning (planned)](lightning.md) | 5 | Lightning strokes and their coupling into the station, the land cable and the line. |
| [lines: transmission-line helpers](lines.md) | 4 | Transmission-line helpers: lumped ladders, sectioning and the telegrapher's equations. |
| [metrics: what a run is judged by](metrics.md) | 6 | What a run is judged by: current dip, PFE headroom and stress, device heating, voltage extremes. |
| [mna: the circuit solver](mna.md) | 9 | The circuit solver: modified nodal analysis, backward Euler, cached LU and Newton iteration. |
| [network: topology and power modes](network.md) | 8 | Topology: the element list, the point-to-point builder and the (planned) branching-unit topologies. |
| [plotting: figures in the paper style](plotting.md) | 3 | Figures in the polar_connect paper style (matplotlib and SciencePlots, optional). |
| [properties: cable R, L, G, C](properties.md) | 8 | Cable property providers: how R, L, G and C along the route are known. A provider answers ``rlcg(x_km, ...)``; the wrappers compose. |
| [space_weather: GMD forcing](space_weather.md) | 3 | GMD forcing: turn a voltage record or a geoelectric field into a source on every span. |
| [spice: export and cross-check](spice.md) | 3 | Export to ngspice and compare, so every circuit has an independent check. |
| [studies: sweeps and maps](studies.md) | 3 | Sweeps, one-at-a-time sensitivity and two-parameter maps. |
| [validation: analytic cases](validation.md) | 7 | Analytic validation cases. Each module has ``run() -> ValidationCase``; ``run_all()`` runs them (``bolts validate``). |
| [waveforms: records and pulses](waveforms.md) | 8 | Waveforms. The built-in constructors are registered by name (``bolts.registry.get_waveform("sine")``); register your own with |

## Conventions

- Quantities carry their unit in the name (`r_ohm_per_km`, `dt_s`, `v_tot_V`); no unit objects are used.
- Every parameter is a `Param` with a status (`sourced`, `assumed`, `unknown`, `override`); using an `unknown` one raises `MissingParameter`.
- Stubs raise `NotImplementedYet` with a pointer to the roadmap and are flagged *(stub)* in the module tables.
- Equations and sources are in each module docstring; the chapters give the story around them.
