# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""Circuit elements. Each is a small class with ``stamp(st)``; register your own with :func:`bolts.registry.register_element`."""
from ..registry import register_element
from .arrester import Arrester
from .beach_joint import BeachJoint
from .cable_segment import CableSegment
from .coil import Coil
from .diode_chain import DiodeChain
from .earth_electrode import EarthElectrode
from .land_cable import LandCable
from .lumped import Capacitor, Inductor, Resistor, VSource
from .pfe import PFE
from .pfe_filter import PfeFilter
from .pfe_regulator import PowerFeedController
from .repeater import Repeater
from .zener import LinearZener, PiecewiseZener

for _name, _cls in {"cable_segment": CableSegment, "repeater": Repeater, "pfe": PFE, "earth_electrode": EarthElectrode,
                    "resistor": Resistor, "capacitor": Capacitor, "inductor": Inductor, "vsource": VSource,
                    "coil": Coil, "land_cable": LandCable, "beach_joint": BeachJoint, "pfe_filter": PfeFilter, "arrester": Arrester, "diode_chain": DiodeChain}.items():
    register_element(_name, _cls)

__all__ = [
    "PFE",
    "Arrester",
    "BeachJoint",
    "CableSegment",
    "Capacitor",
    "Coil",
    "DiodeChain",
    "EarthElectrode",
    "Inductor",
    "LandCable",
    "LinearZener",
    "PfeFilter",
    "PiecewiseZener",
    "PowerFeedController",
    "Repeater",
    "Resistor",
    "VSource",
]
