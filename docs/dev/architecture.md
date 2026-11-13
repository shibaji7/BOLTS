# Architecture

One concern per module, small interfaces.

```
config -> waveforms / space_weather -> network.builder -> elements (stamp) -> mna (assemble, transient) -> Result
                                                                              -> metrics / impact / damage
                                                                              -> spice (export, compare)
```

* **`config`**: `Param(value, unit, status, source)`, `ParameterSet`, TOML defaults in `config/defaults/`.
* **`waveforms`**: `Record(t_s, values)` and constructors; `space_weather.gmd_source.GMDSource` spreads a record over the spans.
* **`properties`**: `PropertyProvider.rlcg(...)`.
* **`elements`**: every element has `stamp(st)`; `mna.stamp.Stamper` offers `add_series_branch`, `add_capacitance`, `add_conductance`,
  `add_current_source`. Sources are `ConstantSource`, `RecordSource`, or `ControlledSource` (set by the regulator).
* **`network`**: `Network` (elements + controller + meta), `build_p2p`, power modes, topology checks (every node must reach the sea).
* **`mna`**: `assemble` -> `System(G, C)`, `dc_op`, `integrators`, `transient.run_transient` (with the exact regulator step).
* **`metrics`, `impact`, `damage`**: consume a `TransientResult`.
* **`result.Result`** ties them together: `summary()`, `assess()`, `series()`, `save()`.
* **Plugins**: entry-point groups `bolts.elements` and `bolts.waveforms`; `bolts.register_element(name, factory)`.

Modules for later versions exist as documented slots that raise `NotImplementedYet("...", "ROADMAP vX.Y")`, so the tree and the docs are
complete and a contributor knows where a new capability goes.
