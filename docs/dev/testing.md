# Testing and validation

`make test`, `make cov`, `make lint`. Tests mirror the source tree. Three layers:

1. **Unit tests** per module (parameters, waveforms, stamps, metrics, formulas).
2. **Analytic validation** (`bolts validate`): RC step, RLC ringing, the RC-ladder slowest mode, a DC Zener, energy balance; the regulator
   against its closed forms for dt/tau from 0.1 to 1000 (`tests/test_regulator.py`).
3. **Independent cross-check**: `make spice-check` compares every node voltage with ngspice (needs the `ngspice` binary).

A regression test ties the point-to-point result to the numbers of the `pfe_design` study for the legacy burst record (current down 139.83 mA,
PFE clamped 1.915% of the time, minimum margin 10.733 dB). When physics changes, change the analytic expectation, never just the snapshot.
