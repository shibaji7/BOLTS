# Release

1. Update `src/bolts/_version.py`, `CHANGELOG.md`, `CITATION.cff`.
2. `make clean && make test lint docs && make check` (builds and runs `twine check`).
3. **Reserve the name** (once): `python -m twine upload --repository testpypi dist/*` for a 0.0.x placeholder; upload to PyPI only when the
   project is ready. The name `bolts` was unregistered on PyPI, TestPyPI and conda-forge when checked (2026-11-11); PyPI has no reservation
   API, so it is only secure after an upload.
4. Tag `vX.Y.Z`, push, and enable the Read the Docs project (`.readthedocs.yaml` is in the repository).

## Publishing

The normal route is the tag-triggered workflow `.github/workflows/release.yml`: build, TestPyPI, then PyPI after a manual approval of the
`pypi` environment, using PyPI trusted publishing (no stored token). It needs a trusted publisher on pypi.org and test.pypi.org
(project `bolts`, owner `shibaji7`, repository `BOLTS`, workflow `release.yml`, environment `pypi` / `testpypi`).

Fallback by hand with twine (also how to reserve the name before the workflow is configured). Create an API token on the site, then:

```bash
export TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-...   # token for the matching site
make publish-test    # check + twine upload --repository testpypi
make publish         # check + twine upload to PyPI, asks for confirmation
```

`--repository testpypi` needs a `[testpypi]` section in `~/.pypirc` (`repository = https://test.pypi.org/legacy/`) or `TWINE_REPOSITORY_URL`.
