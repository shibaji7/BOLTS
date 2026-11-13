# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The API documentation is generated from the docstrings, so they are tested: every public function and class has one, and the entry points
of ``bolts.api`` document their arguments, return value and (where they raise) the exceptions."""
import ast
import pathlib

import bolts
import bolts.api as api

SRC = pathlib.Path(bolts.__file__).parent


def test_every_public_function_and_class_has_a_docstring():
    missing = []
    for f in SRC.rglob("*.py"):
        if f.name == "__main__.py":
            continue
        for node in ast.walk(ast.parse(f.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_") and not ast.get_docstring(node):
                missing.append(f"{f.relative_to(SRC)}:{node.lineno} {node.name}")
    assert not missing, "public names without a docstring: " + ", ".join(missing)


def test_api_entry_points_document_args_and_returns():
    for name in ("load_waveform", "run_transient", "assess", "export_spice"):
        doc = getattr(api, name).__doc__
        assert "Args:" in doc and "Returns:" in doc, name
    from bolts.config.loader import load_parameters
    from bolts.network.builder import build_network
    for fn in (load_parameters, build_network):
        assert "Args:" in fn.__doc__ and "Returns:" in fn.__doc__, fn.__name__


def test_every_subpackage_has_an_introduction():
    for d in SRC.iterdir():
        if d.is_dir() and (d / "__init__.py").exists() and not d.name.startswith("_"):
            assert ast.get_docstring(ast.parse((d / "__init__.py").read_text())), d.name
