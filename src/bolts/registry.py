# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Plugin registry. Elements and waveforms register by name; third-party packages can add their own through the entry-point
groups ``bolts.elements`` and ``bolts.waveforms`` without touching this repository."""
from __future__ import annotations

from collections.abc import Callable
from importlib import metadata
from typing import Any

_ELEMENTS: dict[str, Callable[..., Any]] = {}
_WAVEFORMS: dict[str, Callable[..., Any]] = {}
_LOADED = False


def register_element(name: str, factory: Callable[..., Any]) -> None:
    """Register an element factory under ``name`` (a class or a function returning an element)."""
    _ELEMENTS[name] = factory


def register_waveform(name: str, factory: Callable[..., Any]) -> None:
    """Register a waveform factory under ``name`` (a function returning a :class:`~bolts.waveforms.base.Record`)."""
    _WAVEFORMS[name] = factory


def _load_entry_points() -> None:
    """Import third-party plugins once, on first lookup, so ``import bolts`` stays fast. Built-ins win over a plugin of the same name."""
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    for group, table in (("bolts.elements", _ELEMENTS), ("bolts.waveforms", _WAVEFORMS)):
        for ep in metadata.entry_points(group=group):
            table.setdefault(ep.name, ep.load())


def get_element(name: str) -> Callable[..., Any]:
    """The registered element factory; an unknown name lists what is available."""
    _load_entry_points()
    try:
        return _ELEMENTS[name]
    except KeyError as e:
        raise KeyError(f"no element {name!r}; known: {sorted(_ELEMENTS)}") from e


def get_waveform(name: str) -> Callable[..., Any]:
    """The registered waveform factory; an unknown name lists what is available."""
    _load_entry_points()
    try:
        return _WAVEFORMS[name]
    except KeyError as e:
        raise KeyError(f"no waveform {name!r}; known: {sorted(_WAVEFORMS)}") from e


def element_names() -> list[str]:
    """Sorted names of all registered elements."""
    _load_entry_points()
    return sorted(_ELEMENTS)


def waveform_names() -> list[str]:
    """Sorted names of all registered waveforms."""
    _load_entry_points()
    return sorted(_WAVEFORMS)
