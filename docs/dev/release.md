# Release

1. Update `src/bolts/_version.py`, `CHANGELOG.md`, `CITATION.cff`.
2. `make clean && make test lint docs && make check` (builds and runs `twine check`).
3. **Reserve the name** (once): `python -m twine upload --repository testpypi dist/*` for a 0.0.x placeholder; upload to PyPI only when the
   project is ready. The name `bolts` was unregistered on PyPI, TestPyPI and conda-forge when checked (2026-11-11); PyPI has no reservation
   API, so it is only secure after an upload.
4. Tag `vX.Y.Z`, push, and enable the Read the Docs project (`.readthedocs.yaml` is in the repository).
