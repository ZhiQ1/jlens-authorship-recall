# Item 2-1 D12-1 gate outcome (B_stopped)

Prompt 66 re-run with the original frozen Fit B code reproduces the 2026-10-21 log (4.366808 vs 4.367), but the D12-1 gate code gives 4.378043 (|diff| 0.0110 > threshold 0.004867). Per D12-1 item 2-1 is stopped: Fit B stays at 66/100; no Fit A vs Fit B holdout comparison and no Fit B Stage 10 readout.

**Superseded 2026-11-12 by D12-5** (config/prereg_addendum12_deviations_D12-5.json, sha256 68fa74cdcf65d8e8a9c05d99ca659c43d8d8a0bdab6dd4cb296e9a1e365e9f07): the 4.378043 was the gate recomputing the norm in f64 (stage9_b2_fitb.py:162) against an fp32-logged reference (jlens/fitting.py:352); in fp32 the same J gives 4.366808. Gate v4 (fp32 vs fp32, same thresholds) re-run as job 11836319; 2-1 resumes if it passes.
