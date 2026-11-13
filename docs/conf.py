# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Sphinx configuration for the BOLTS documentation (same stack as GeoPulse: autosummary pages, napoleon, viewcode, intersphinx, MyST Markdown)."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "src"))                       # the src/ layout is importable without installing

project = "BOLTS"
author = "Shibaji Chakraborty"
copyright = "2026, Shibaji Chakraborty"                      # noqa: A001  (the name Sphinx expects)

# The version comes from the package, so the docs always match the release. No fallback: a failed import must fail the build.
from bolts._version import __version__ as release            # noqa: E402

version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",             # pull docstrings in
    "sphinx.ext.autosummary",         # a summary table and a page per module
    "sphinx.ext.napoleon",            # Google and NumPy docstring sections
    "sphinx.ext.intersphinx",         # links into Python, NumPy, SciPy and matplotlib
    "sphinx.ext.mathjax",             # equations
    "sphinx.ext.viewcode",            # [source] link on every entry
    "sphinx_autodoc_typehints",       # types in the parameter descriptions
    "sphinx_copybutton",              # copy button on code blocks
    "myst_parser",                    # the chapters are Markdown
]

autosummary_generate = True
autosummary_imported_members = False
autodoc_default_options = {"members": True, "undoc-members": False, "show-inheritance": True, "member-order": "bysource"}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_use_param = True
default_role = "code"                                        # a single backtick is code, as in the Markdown chapters

myst_enable_extensions = ["colon_fence", "deflist", "amsmath", "dollarmath", "attrs_inline"]
myst_heading_anchors = 3

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
master_doc = "index"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {"logo_only": False, "navigation_depth": 3, "collapse_navigation": False, "sticky_navigation": True}
html_context = {"display_github": True, "github_user": "shibaji7", "github_repo": "BOLTS", "github_version": "main", "conf_py_path": "/docs/"}

nitpicky = False
nitpick_ignore_regex = [("py:class", r"numpy\..*"), ("py:class", r".*\.T$")]
suppress_warnings = ["myst.header"]
