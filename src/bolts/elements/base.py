# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""The element protocol. An element has a name and one method, ``stamp(st)``, that adds its branches, shunts and sources to a
:class:`~bolts.mna.stamp.Stamper`. Adding a device never touches the solver."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..mna.stamp import Stamper


class Element(ABC):
    """Base class of every device. Subclasses set ``name`` in ``__init__`` and implement :meth:`stamp`; they never touch the solver."""

    name: str

    @abstractmethod
    def stamp(self, st: Stamper) -> None:
        """Add this device's series branches, shunt conductances / capacitances and sources to the stamper."""

    @property
    def nodes(self) -> tuple[str, ...]:
        """Names of the nodes this element connects (used by topology checks). Ground is not listed."""
        return ()
