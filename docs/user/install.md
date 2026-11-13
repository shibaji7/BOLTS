# Install

```bash
git clone <repository URL> BOLTS && cd BOLTS
make env                 # conda env "bolts": python 3.12, numpy, scipy
conda activate bolts
make dev                 # editable install + pytest, ruff, build, twine
make test
```

Without conda: `pip install .` in Python >= 3.11. Runtime dependencies are only **numpy** and **scipy**.

| Extra | Adds | For |
|---|---|---|
| `bolts[plots]` | matplotlib | `bolts run --plot`, `bolts.plotting` |
| `bolts[data]` | pandas | `Result.to_dataframe()` (planned) |
| `bolts[docs]` | mkdocs, mkdocs-material, mkdocstrings | `make docs` |
| `bolts[dev]` | pytest, pytest-cov, ruff, build, twine | development |

**ngspice** (system binary, optional) enables `bolts spice --run` and `make spice-check`. `bolts doctor` reports what is available.
