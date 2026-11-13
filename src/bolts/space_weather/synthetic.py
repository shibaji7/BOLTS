# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""A synthetic but physically shaped 1-second record of the net induced voltage along a long cable (the generator behind ``data/example_vind_1s.csv``).

What a real record looks like (and what this imitates). The voltage along a submarine cable is the line integral of the geoelectric field,
so it follows dB/dt of the ground magnetic field. During a storm it has three parts, all of which appear here:

1. a *slow backbone*, minutes to hours, tracking the storm phases (you pass it in: a model output or a measured trace);
2. *ULF pulsations* (Pc5 to Pc2, periods of roughly 2.5 to 600 s, four independent bands): random, band-limited, with power falling with
   frequency, and growing when the storm is active. They are NOT clean sinusoids: amplitude and phase wander from cycle to cycle;
3. a *substorm-onset impulse*: a short bipolar pulse (the derivative of a smooth bump in B), followed by enhanced pulsation activity.

The result is still synthetic: shaped for exercising the model, not a prediction for any event. A fixed seed makes it reproducible. A SCUBAS or
measured record needs no bridge: it is a CSV, read with :func:`bolts.load_waveform`."""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from ..waveforms.base import Record

SEED = 20240511           # the seed of the shipped example record
# Pulsation bands: (name, shortest period s, longest period s, rms in V at quiet time, spectral slope of the amplitude, ~f^-slope).
# Lower bands carry more voltage; the 2 to 10 s band (Pc2/Pc3 edge, near the 2 s Nyquist limit of a 1 s record) is the fast part that
# stresses the regulator. Real dB/dt spectra are close to f^-1 to f^-1.5 in amplitude over these bands.
PULSATION_BANDS = (
    ("Pc5", 150.0, 600.0, 3.0, 1.5),
    ("Pc4", 45.0, 150.0, 2.0, 1.2),
    ("Pc3", 10.0, 45.0, 1.5, 1.0),
    ("Pc2", 2.5, 10.0, 1.0, 0.8),
)


def storm_backbone(t_s: np.ndarray, source_t_s: np.ndarray, source_V: np.ndarray, t_peak_s: float, scale: float) -> np.ndarray:
    """A slow storm trace resampled to ``t_s`` with a monotone (PCHIP) interpolant, its largest swing moved to ``t_peak_s`` and scaled by ``scale``."""
    shift = t_peak_s - source_t_s[np.argmax(np.abs(source_V))]
    return scale * PchipInterpolator(source_t_s + shift, source_V, extrapolate=False)(t_s)


def coloured_noise(n: int, rng: np.random.Generator, band_s: tuple[float, float], slope: float) -> np.ndarray:
    """Zero-mean, unit-rms Gaussian noise with ``|spectrum| ~ f^-slope`` between the two periods, built in the Fourier domain (1 s sampling)."""
    f = np.fft.rfftfreq(n, d=1.0)
    amp = np.zeros_like(f)
    inband = (f >= 1.0 / band_s[1]) & (f <= 1.0 / band_s[0])
    amp[inband] = f[inband] ** -slope
    spec = amp * np.exp(2j * np.pi * rng.random(f.size))     # random phases make the cycles wander
    x = np.fft.irfft(spec, n)
    return x / x.std()


def onset_impulse(t_s: np.ndarray, t0_s: float, width_s: float, peak_V: float) -> np.ndarray:
    """Bipolar pulse: derivative of a Gaussian bump (dB/dt of a smooth field step), normalised to ``peak_V``."""
    u = (t_s - t0_s) / width_s
    p = -u * np.exp(-0.5 * u * u)
    return peak_V * p / np.abs(p).max()


def synthetic_vind(source_t_s, source_V, seed: int = SEED, n_sec: int = 1800, t_peak_s: float = 900.0, backbone_scale: float = 2.5,
                   activity_gain: float = 12.0, onset_peak_V: float = 70.0, onset_width_s: float = 25.0,
                   bands=PULSATION_BANDS, label: str = "synthetic V_ind") -> Record:
    """Backbone + four-band pulsations + onset impulse at 1 s steps for ``n_sec`` seconds.

    ``source_t_s`` and ``source_V`` are the slow storm trace (for the shipped record: the frozen 72 V May 2024 model output, 60 s steps).
    Pulsation power follows storm activity: a floor plus a term proportional to the 120 s-smoothed absolute slope of the backbone
    (``activity_gain`` volts of rms per V/s)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_sec + 1, dtype=float)
    slow = np.nan_to_num(storm_backbone(t, np.asarray(source_t_s, float), np.asarray(source_V, float), t_peak_s, backbone_scale), nan=0.0)
    slope = np.abs(np.gradient(slow))
    activity = bands[0][3] + activity_gain * np.convolve(slope, np.ones(120) / 120.0, mode="same")
    gain = activity / bands[0][3]       # each band's quiet-time rms scaled by how active the storm is
    pulsation = sum(rms * gain * coloured_noise(len(t), rng, (lo, hi), s) for _, lo, hi, rms, s in bands)
    onset = onset_impulse(t, t_peak_s - 240.0, onset_width_s, onset_peak_V)
    return Record(t, slow + pulsation + onset, label)
