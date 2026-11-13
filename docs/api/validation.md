# validation: analytic cases

Analytic validation cases. Each module has ``run() -> ValidationCase``; ``run_all()`` runs them (``bolts validate``).

**Read first:** [Validation and tests](../chapters/09_validation_and_tests.md)

| Module | What it does |
|---|---|
| [`diode_clamp`](#bolts.validation.diode_clamp) | DC solution of a source through a resistor into a clamp (a piecewise-linear nonlinear shunt), solved by Newton iteration. Above the clamp voltage t... |
| [`energy_balance`](#bolts.validation.energy_balance) | Energy balance of an RC step: the source delivers E = V Q, the capacitor stores C V^2/2 and the resistor dissipates the rest |
| [`line_step`](#bolts.validation.line_step) | Slowest mode of a lumped RC cable ladder against the distributed RC line: tau = R' C' L^2 / pi^2 for a line pinned to the sea at both |
| [`rc_step`](#bolts.validation.rc_step) | RC step: v_out(t) = V (1 - exp(-t/RC)). Checks the capacitor stamp and backward Euler (first-order accurate: error ~ dt/RC). |
| [`rlc_ring`](#bolts.validation.rlc_ring) | Series RLC step (under-damped): v_c(t) = V [1 - e^(-a t) (cos wd t + (a/wd) sin wd t)], a = R/2L, wd = sqrt(1/LC - a^2). |
| [`zener_dc`](#bolts.validation.zener_dc) | DC solution of a source through a resistor into a linear Zener stack. The stack is the branch ``drop = Vz + rz (I - I_nom)``, i.e. an |
| [`zener_knee`](#bolts.validation.zener_knee) | DC solution of a source through a resistor into a piecewise Zener stack (Newton iteration), checked on its three segments: |

::: bolts.validation.diode_clamp
    options:
      show_root_heading: true

::: bolts.validation.energy_balance
    options:
      show_root_heading: true

::: bolts.validation.line_step
    options:
      show_root_heading: true

::: bolts.validation.rc_step
    options:
      show_root_heading: true

::: bolts.validation.rlc_ring
    options:
      show_root_heading: true

::: bolts.validation.zener_dc
    options:
      show_root_heading: true

::: bolts.validation.zener_knee
    options:
      show_root_heading: true
