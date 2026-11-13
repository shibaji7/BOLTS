# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Microsecond window around a fast event, started from the state of a slow run. Deferred: not in v0.2, see ``docs/dev/future_microsecond_windows.md``.

The GMD runs use seconds-scale steps; a lightning or switching surge needs steps of about a microsecond over a few milliseconds. The plan is
to run the surge in a short window whose initial state is the slow run's state at the event time, with the cable sectioned by
:func:`bolts.lines.sectioning.sections_for_rise_time` so that the section delay stays below a tenth of the pulse front."""
from __future__ import annotations

from ..errors import NotImplementedYet


def run_window(*args, **kwargs):
    """Not implemented yet: raises ``NotImplementedYet`` naming the roadmap item."""
    raise NotImplementedYet("microsecond window run from a slow-run state", "docs/dev/future_microsecond_windows.md (after v0.2)")
