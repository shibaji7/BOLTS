# Experiment 1: the quiet line

**Question:** what does it take to power the cable when nothing happens, and what is the loop?
 

**Expect:** 12 repeaters, a static need of 1428.8 V (cable 750.8 V + 12 x 56 V + 6 V), a loop resistance of 816.8 ohm (cable 750.8 + 12 x 5 + 2 x 3) so 1 V of induced voltage changes the current by 1.22 mA, and no change of current at all.

## Run it

```bash
python examples/gmd/01_p2p_baseline.py
```

The figures and tables are written to `outputs/examples/01_p2p_baseline/`. Source on GitHub: [examples/gmd/01_p2p_baseline.py](https://github.com/shibaji7/BOLTS/blob/main/examples/gmd/01_p2p_baseline.py).

??? note "Full source"

    ```python
    --8<-- "examples/gmd/01_p2p_baseline.py"
    ```
