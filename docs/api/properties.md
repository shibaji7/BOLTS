# properties: cable R, L, G, C

Cable property providers: how R, L, G and C along the route are known. A provider answers ``rlcg(x_km, ...)``; the wrappers compose.

**Read first:** [Cable properties](../chapters/12_cable_properties.md)

| Module | What it does |
|---|---|
| [`base`](#bolts.properties.base) | Cable per-length properties. A *provider* answers ``rlcg(x_km, ...)``, so how R, L, G and C are known (constant, a section |
| [`catalog`](#bolts.properties.catalog) | Property provider: named cable types from a catalogue. Planned for v0.5; see ROADMAP.md. *(stub)* |
| [`constant`](#bolts.properties.constant) | Constant per-km R, C, G (L only if known): the v0.1 provider. |
| [`depth_profile`](#bolts.properties.depth_profile) | Depth along the route, and the temperature that goes with it: a wrapper that tells another provider where it is. |
| [`factory`](#bolts.properties.factory) | Pick the cable-property provider from the ``[cable]`` parameters, so a TOML file, ``--set`` on the command line or ``load_parameters(overrides=...)`` |
| [`freq_dependent`](#bolts.properties.freq_dependent) | Property provider: frequency-dependent R(f), G(f) (skin effect, dielectric dispersion). Planned for v0.5; see ROADMAP.md. *(stub)* |
| [`section_table`](#bolts.properties.section_table) | Property provider from a section table: R, C (and optionally G and L) that change along the route, as a cable design lists them. |
| [`temperature_R`](#bolts.properties.temperature_R) | Temperature-dependent conductor resistance: a wrapper around any other provider. |

::: bolts.properties.base
    options:
      show_root_heading: true

::: bolts.properties.catalog
    options:
      show_root_heading: true

::: bolts.properties.constant
    options:
      show_root_heading: true

::: bolts.properties.depth_profile
    options:
      show_root_heading: true

::: bolts.properties.factory
    options:
      show_root_heading: true

::: bolts.properties.freq_dependent
    options:
      show_root_heading: true

::: bolts.properties.section_table
    options:
      show_root_heading: true

::: bolts.properties.temperature_R
    options:
      show_root_heading: true
