# Experiment 6: independent check

**Question:** does an independent circuit solver (ngspice) agree with BOLTS on every node voltage?
 Needs the ngspice binary. Expect agreement to about 1e-9 of the largest voltage for the point-to-point cable (the regulator itself is checked by the analytic tests, because the PFE voltage is replayed in SPICE).

## Run it

```bash
python examples/gmd/06_spice_crosscheck.py
```

The figures and tables are written to `outputs/examples/06_spice_crosscheck/`. Source on GitHub: [examples/gmd/06_spice_crosscheck.py](https://github.com/shibaji7/BOLTS/blob/main/examples/gmd/06_spice_crosscheck.py).

??? note "Full source"

    ```python
    --8<-- "examples/gmd/06_spice_crosscheck.py"
    ```
