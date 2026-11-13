# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
#
# BOLTS developer entry points.  `make` (or `make help`) lists them.
# Override the interpreter with  make PY=/path/to/python  (default: the conda env named "bolts").

ENV      ?= bolts
CONDA    ?= conda
PY       ?= $(shell $(CONDA) run -n $(ENV) which python 2>/dev/null || echo python)
OUT      ?= outputs

# ---- colours (disabled with NO_COLOR=1) ----
ifeq ($(NO_COLOR),)
  C0 := \033[0m
  CB := \033[1m
  CR := \033[38;5;203m
  CO := \033[38;5;214m
  CG := \033[38;5;78m
  CC := \033[38;5;45m
  CP := \033[38;5;177m
  CD := \033[2m
endif

.DEFAULT_GOAL := help
.PHONY: help banner env install dev test cov lint fmt dupes spdx changelog-check pre-commit pre-commit-install qa api-docs example-docs doc-figures docs docs-serve build check publish-test publish spice-check examples tree validate doctor clean distclean

help: banner ## Show this list
	@printf "$(CB)Usage:$(C0) make $(CC)<target>$(C0)\n\n"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  \033[38;5;45m%-13s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf "\n$(CD)env: $(ENV)   python: $(PY)$(C0)\n"

banner:
	@printf "$(CO)$(CB)"
	@printf "  ____   ___  _   _____ ____\n"
	@printf " | __ ) / _ \\\\| | |_   _/ ___|\n"
	@printf " |  _ \\\\| | | | |   | | \\\\___ \\\\\n"
	@printf " | |_) | |_| | |___| |  ___) |\n"
	@printf " |____/ \\\\___/|_____|_| |____/\n"
	@printf "$(C0)$(CP)  Branching-unit and Optical-repeater power-feed Loop Transient Simulator$(C0)\n"
	@printf "$(CD)  GMD / space weather, lightning and surges  ->  loss of signal, failures, traffic$(C0)\n\n"

env: ## Create the conda environment (numpy, scipy only)
	@printf "$(CG)creating conda env '$(ENV)'$(C0)\n"
	$(CONDA) env create -f environment.yml -y

install: ## Install the package (runtime dependencies only)
	$(PY) -m pip install .

dev: ## Editable install with the dev extras (pytest, ruff, build, twine)
	$(PY) -m pip install -e ".[dev]"

test: ## Run the tests
	@printf "$(CG)pytest$(C0)\n"
	$(PY) -m pytest

cov: ## Tests with a coverage report
	$(PY) -m pytest --cov=bolts --cov-report=term-missing

lint: ## Lint with ruff
	@printf "$(CC)ruff check$(C0)\n"
	$(PY) -m ruff check src tests scripts examples

fmt: ## Auto-fix what ruff can fix
	$(PY) -m ruff check --fix src tests scripts examples

dupes: ## Duplicate-code check (pylint R0801, see .pylintrc)
	@printf "$(CP)pylint duplicate-code$(C0)\n"
	$(PY) -m pylint --rcfile=.pylintrc src/bolts tests

spdx: ## Check the SPDX license header on every Python file
	$(PY) scripts/check_spdx.py

changelog-check: ## CHANGELOG.md must change with src/bolts (staged files)
	$(PY) scripts/check_changelog.py

pre-commit-install: ## Install the git hooks (pre-commit and pre-push)
	$(PY) -m pre_commit install --hook-type pre-commit --hook-type pre-push

pre-commit: ## Run every pre-commit hook on all tracked and staged files
	$(PY) -m pre_commit run --all-files

qa: lint dupes spdx test ## Everything that should pass before a commit
	@printf "$(CG)$(CB)qa passed$(C0)\n"

validate: ## Run the analytic validation cases
	$(PY) -m bolts validate

spice-check: ## Cross-check BOLTS against ngspice (needs the ngspice binary)
	$(PY) -m pytest -m spice -v

doctor: ## Check the installation
	$(PY) -m bolts doctor

examples: ## Run the GMD experiments (examples/gmd)
	@for f in examples/gmd/[0-9]*.py; do printf "$(CC)%s$(C0)\n" $$f; $(PY) $$f || exit 1; done

api-docs: ## Regenerate the API reference pages from the package layout
	$(PY) scripts/gen_api_docs.py

example-docs: examples ## Run the experiments, then write docs/examples/ (pages and figures)
	$(PY) scripts/gen_example_docs.py

doc-figures: ## Run the GMD examples and copy the figures used by the docs
	$(PY) scripts/make_doc_figures.py

param-table: ## Refresh the parameter table in docs chapter 07
	$(PY) scripts/gen_param_table.py

docs: ## Build the documentation (mkdocs, strict)
	$(PY) -m mkdocs build --strict

docs-serve: ## Serve the documentation locally
	$(PY) -m mkdocs serve

build: ## Build sdist and wheel
	$(PY) -m build

check: build ## Check the built distributions (twine)
	$(PY) -m twine check dist/*

publish-test: check ## Upload dist/ to TestPyPI with twine (token: TWINE_USERNAME=__token__, TWINE_PASSWORD=pypi-...)
	$(PY) -m twine upload --repository testpypi --skip-existing dist/*

publish: check ## Upload dist/ to PyPI with twine (asks first; the normal route is the tag-triggered release workflow)
	@printf "Upload the files in dist/ to PyPI? [y/N] " && read a && [ "$$a" = y ]
	$(PY) -m twine upload dist/*

tree: ## Show the package layout
	@find src/bolts -name '*.py' -not -name '__init__.py' | sed 's|src/||' | sort | awk -F/ '{print "  " $$0}'

clean: ## Remove caches and build output
	rm -rf build dist .pytest_cache .ruff_cache .coverage coverage.xml htmlcov site $(OUT) src/*.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

distclean: clean ## clean, and the conda env too
	-$(CONDA) env remove -n $(ENV) -y
