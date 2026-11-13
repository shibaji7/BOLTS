# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""GMD / space-weather forcing: a net end-to-end induced voltage V_ind(t) spread over every span of the cable.

Sign convention: V_ind > 0 drives current toward increasing chainage. With the feed direction ``s`` (+1 along increasing
chainage) the loop source is ``s * V_ind``, so an induced voltage along the feed direction ASSISTS the PFEs and one against it
OPPOSES them (the PFE must then supply more voltage)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..waveforms.base import Record


@dataclass(frozen=True)
class GMDSource:
    """A net induced-voltage record with the feed direction and the share of it that acts on the loop."""
    record: Record
    feed_direction: int = 1
    emf_share: float = 1.0

    def span_emf_V(self, n_spans: int, weights: np.ndarray | None = None) -> np.ndarray:
        """EMF in each span, shape (n_samples, n_spans), V. ``weights`` (sum 1) distributes the voltage along the cable;
        the default is even (one EMF per span proportional to its length when ``weights`` comes from the span lengths)."""
        w = np.full(n_spans, 1.0 / n_spans) if weights is None else np.asarray(weights, float) / np.sum(weights)
        return np.outer(self.feed_direction * self.emf_share * self.record.values, w)
