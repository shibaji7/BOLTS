# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""``python -m bolts`` is the same as the ``bolts`` command."""
import sys

from .cli import main

sys.exit(main())
