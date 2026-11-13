# lines: transmission-line helpers

`lumped_ladder` and `sectioning` choose how many lumped sections a cable needs (section delay well below the signal rise time); `telegrapher` gives the characteristic impedance and delay. `bergeron` (travelling-wave line for microsecond surges) is a stub.

Status: implemented except `bergeron`. Chapter 03.

**Read first:** [The circuit model](../chapters/03_circuit_model.md)

| Module | What it does |
|---|---|
| [`bergeron`](#bolts.lines.bergeron) | Bergeron (method of characteristics) travelling-wave line model for microsecond surges. Planned for v0.3; see ROADMAP.md. *(stub)* |
| [`lumped_ladder`](#bolts.lines.lumped_ladder) | A uniform cable as a ladder of identical lumped sections (the point-to-point builder already does this, one section per repeater span). |
| [`sectioning`](#bolts.lines.sectioning) | How many lumped sections a cable needs. A lumped section is accurate for signals whose rise time is much longer than the delay across |
| [`telegrapher`](#bolts.lines.telegrapher) | Telegrapher's equations for a uniform line with per-length R, L, G, C (the cable seen as a transmission line). |

::: bolts.lines.bergeron
    options:
      show_root_heading: true

::: bolts.lines.lumped_ladder
    options:
      show_root_heading: true

::: bolts.lines.sectioning
    options:
      show_root_heading: true

::: bolts.lines.telegrapher
    options:
      show_root_heading: true
