# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Shibaji Chakraborty
"""What a run is judged by: current dip, PFE headroom and stress, device heating, voltage extremes.

Each module turns time series from a run into numbers: how far the current falls (`current_dip`), how much PFE range is left and for how long it sat at a limit (`headroom`, `pfe_stress`), the Zener heat against normal (`device_stress`), the conductor-to-sea voltage (`voltage_extremes`) and energy (`energy`). `Result.assess` collects them.

Status: implemented. Chapters 02 and 04.
"""
