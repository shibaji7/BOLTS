# Top level

**Read first:** [Overview](../chapters/00_overview.md), [Run and extend](../chapters/10_run_and_extend.md)

| Module | What it does |
|---|---|
| [`api`](#bolts.api) | The public API: a few functions that cover a whole study. Everything here is also re-exported from ``bolts``. |
| [`cli`](#bolts.cli) | Command line: ``bolts run \| params \| validate \| spice \| doctor``. |
| [`constants`](#bolts.constants) | Physical constants (SI). |
| [`errors`](#bolts.errors) | Exceptions used across BOLTS. Every error names the setting or module the user has to look at. |
| [`registry`](#bolts.registry) | Plugin registry. Elements and waveforms register by name; third-party packages can add their own through the entry-point |
| [`result`](#bolts.result) | The result of a run: the network, the transient, the parameters and the record, with the quantities people ask for. |
| [`units`](#bolts.units) | Unit conversions. Quantities in code carry their unit in the name (``r_ohm_per_km``); these helpers are the only place |

::: bolts.api
    options:
      show_root_heading: true

::: bolts.cli
    options:
      show_root_heading: true

::: bolts.constants
    options:
      show_root_heading: true

::: bolts.errors
    options:
      show_root_heading: true

::: bolts.registry
    options:
      show_root_heading: true

::: bolts.result
    options:
      show_root_heading: true

::: bolts.units
    options:
      show_root_heading: true
