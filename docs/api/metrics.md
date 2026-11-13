# metrics: what a run is judged by

Each module turns time series from a run into numbers: how far the current falls (`current_dip`), how much PFE range is left and for how long it sat at a limit (`headroom`, `pfe_stress`), the Zener heat against normal (`device_stress`), the conductor-to-sea voltage (`voltage_extremes`) and energy (`energy`). `Result.assess` collects them.

Status: implemented. Chapters 02 and 04.

**Read first:** [Power feeding](../chapters/02_power_feeding.md), [Repeater and optics](../chapters/04_repeater_and_optics.md)

| Module | What it does |
|---|---|
| [`current_dip`](#bolts.metrics.current_dip) | The line current at the repeaters and how far it falls below the nominal: the quantity that starves the pump lasers. |
| [`device_stress`](#bolts.metrics.device_stress) | Stress on a device: the heat in a repeater's Zener shunt, relative to normal running. |
| [`energy`](#bolts.metrics.energy) | Energy dissipated in a device from its power series (trapezoid rule). |
| [`headroom`](#bolts.metrics.headroom) | PFE voltage headroom: how much more voltage the PFEs can still supply, and how often they sit at a limit. |
| [`pfe_stress`](#bolts.metrics.pfe_stress) | Stress on the PFE itself when the induced voltage takes it toward or beyond its voltage range. |
| [`voltage_extremes`](#bolts.metrics.voltage_extremes) | Conductor-to-sea voltage along the cable (what loads the insulation). |

::: bolts.metrics.current_dip
    options:
      show_root_heading: true

::: bolts.metrics.device_stress
    options:
      show_root_heading: true

::: bolts.metrics.energy
    options:
      show_root_heading: true

::: bolts.metrics.headroom
    options:
      show_root_heading: true

::: bolts.metrics.pfe_stress
    options:
      show_root_heading: true

::: bolts.metrics.voltage_extremes
    options:
      show_root_heading: true
