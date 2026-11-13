# spice: export and cross-check

`netlist` writes a netlist (linear and nonlinear branches, shunts, current sources), `run_ngspice` runs it in batch mode and reads the node voltages, `compare` measures the difference. Needs the `ngspice` binary.

Status: implemented. Chapter 09 (validation).

**Read first:** [Validation and tests](../chapters/09_validation_and_tests.md)

| Module | What it does |
|---|---|
| [`compare`](#bolts.spice.compare) | Compare two sets of node voltages. |
| [`netlist`](#bolts.spice.netlist) | Export a linear network to an ngspice netlist, so every circuit can be cross-checked by an independent solver. |
| [`run_ngspice`](#bolts.spice.run_ngspice) | Run ngspice in batch mode and read the node voltages it writes. |

::: bolts.spice.compare
    options:
      show_root_heading: true

::: bolts.spice.netlist
    options:
      show_root_heading: true

::: bolts.spice.run_ngspice
    options:
      show_root_heading: true
