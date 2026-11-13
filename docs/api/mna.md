# mna: the circuit solver

`stamp` and `assemble` build the matrices, `dc_op` the starting state, `transient` marches in time (with the PFE regulator integrated exactly over each step), `newton` handles nonlinear devices, `integrators` and `linear_solve` are the numerical parts. `window_run` (microsecond windows) is deferred.

Status: implemented except `window_run`. Chapter 03 (the circuit model).

**Read first:** [The circuit model](../chapters/03_circuit_model.md)

| Module | What it does |
|---|---|
| [`assemble`](#bolts.mna.assemble) | Build the MNA matrices from a stamped network. |
| [`dc_op`](#bolts.mna.dc_op) | DC operating point: capacitors open, inductors short. Used as the initial condition of a transient (a window that starts away from |
| [`integrators`](#bolts.mna.integrators) | Time integration of ``G x + C dx/dt = b``. |
| [`linear_solve`](#bolts.mna.linear_solve) | LU factorisation with caching: the matrix of a linear circuit with a fixed step is factored once and reused every step. |
| [`newton`](#bolts.mna.newton) | Newton iteration for nonlinear elements (piecewise Zener, diode chains, arresters). |
| [`stamp`](#bolts.mna.stamp) | Stamps for modified nodal analysis (MNA). |
| [`timestep`](#bolts.mna.timestep) | Time axis of a run. v0.1 uses a fixed step; adaptive stepping is planned (roadmap v0.3). *(stub)* |
| [`transient`](#bolts.mna.transient) | The transient run: backward Euler on the MNA system, with an optional PFE regulator integrated exactly over each step. |
| [`window_run`](#bolts.mna.window_run) | Microsecond window around a fast event, started from the state of a slow run. Deferred: not in v0.2, see ``docs/dev/future_microsecond_windows.md``. *(stub)* |

::: bolts.mna.assemble
    options:
      show_root_heading: true

::: bolts.mna.dc_op
    options:
      show_root_heading: true

::: bolts.mna.integrators
    options:
      show_root_heading: true

::: bolts.mna.linear_solve
    options:
      show_root_heading: true

::: bolts.mna.newton
    options:
      show_root_heading: true

::: bolts.mna.stamp
    options:
      show_root_heading: true

::: bolts.mna.timestep
    options:
      show_root_heading: true

::: bolts.mna.transient
    options:
      show_root_heading: true

::: bolts.mna.window_run
    options:
      show_root_heading: true
