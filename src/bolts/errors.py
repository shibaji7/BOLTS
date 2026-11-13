# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Exceptions used across BOLTS. Every error names the setting or module the user has to look at."""
from __future__ import annotations


class BoltsError(Exception):
    """Base class of all BOLTS errors."""


class ConfigError(BoltsError):
    """A parameter file or an override is malformed."""


class MissingParameter(BoltsError, KeyError):
    """A parameter is still ``TBD`` (status ``unknown``): the code refuses to guess its value."""


class NotImplementedYet(BoltsError, NotImplementedError):
    """A planned capability that exists only as a documented slot. The message names the roadmap item."""

    def __init__(self, what: str, roadmap: str = "see ROADMAP.md"):
        super().__init__(f"{what} is not implemented yet ({roadmap}).")


class TopologyError(BoltsError):
    """The network is not a valid circuit (floating node, missing ground, dangling element)."""


class ConvergenceError(BoltsError):
    """The Newton iteration of a nonlinear circuit did not converge within the iteration limit."""

