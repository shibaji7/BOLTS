# Command line

| Command | What it does |
|---|---|
| `bolts run` | run a voltage record through the whole chain; writes `series.csv`, `summary.json`, `manifest.json`, `node_peaks_V.csv` (and a figure with `--plot`) |
| `bolts params` | list parameters with unit, status and source (`--filter`, `--status`) |
| `bolts validate` | run the analytic validation cases |
| `bolts spice` | write an ngspice netlist; `--run` also runs ngspice and compares node voltages |
| `bolts doctor` | check the installation and optional tools |

Common input options: `--params FILE`, `--set section.key=value` (repeatable), `--csv FILE`, `--start S`, `--end S`, `--scale K`, `--dt S`.
`python -m bolts ...` is the same command.
