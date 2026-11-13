# Quick start

```python
import bolts

params = bolts.load_parameters(overrides={"pfe.max_voltage_kV_per_end": 0.75})   # 1.5 kV total (a what-if)
record = bolts.load_waveform("data/example_vind_1s.csv", params=params)           # SYNTHETIC 1-second record
net    = bolts.build_network(params, record)       # PFE A, 13 cable spans, 12 repeaters, PFE B, return through the sea
result = bolts.run_transient(net, params)
s = bolts.assess(result)

print(s["v_pfe_max_V"], s["frac_pfe_clamped"])     # the PFE touches its 1.5 kV limit
print(s["di_min_mA"], s["frac_time_below_margin"]) # worst repeater current change, and how often it exceeds the 100 mA margin
print(s["min_margin_dB"], s["adaptive_250G_mean_rate_fraction"])
result.save("outputs/run")                          # series.csv, summary.json, manifest.json
```

With the shipped example this prints a PFE total up to 1500 V, a repeater current change down to about -156 mA, and a Q margin of
10.7 dB: the synthetic storm holds the PFE at its 1.5 kV what-if limit about 29% of the time and the current falls below the 100 mA margin, but the optical margin barely moves.

Command line equivalent: `bolts run --set pfe.max_voltage_kV_per_end=0.75 --out outputs/run --plot`.
