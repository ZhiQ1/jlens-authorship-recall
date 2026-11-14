# Group A: E1 recovery vs MC true-option probability (item 5a, 2026-11-14)

**Post hoc, descriptive.** Addendum 7 / 8 pre-specify no trend test for E1 recovery; no multiplicity correction.

Written 2026-11-14 05:36 by `~/jlens_work/14_groups/summary_A_prob_20261114.py` (CPU; stored per-paper outputs; logic copied from `rerun_plot_summary_20261112.py`; frozen `rerun_analyze.py` / `groups_core.py` loaded unchanged). E1 = Stage 11 title patching true -> false_0, unwritten authors, final output; R(l) = mean(patched_l - false_0) / mean(true - false_0). Predictor: `mc_team_p_true` (mean probability of the true option over MC orders). 95% team-cluster bootstrap (2,000 draws, seed 391, archived author teams).

Binning: **deciles** of `mc_team_p_true`, fixed cut points from the full group-A sample (n = 557); cut points 0.5044, 0.8309, 0.8946, 0.9556, 0.9812, 0.9905, 0.9972, 0.9991, 0.9998, 0.9999, 1.0000. Within each team draw: R_k per bin (ratio of weighted sums), slope = WLS slope of R_k on the bin's full-sample median probability with weights n_k (team-draw paper count). Note group A = MC "strong" by definition, so p_true is concentrated near the top (range 0.504 to 1.000); the slope is per unit probability, extrapolated far beyond the observed spread - read it with the bin table.

## Parity (WARN only)

- group A overall E1 R(L48) vs rerun_plot_summary_20261112 curves.csv: n_papers = 557 (expected 557.0) OK
- group A overall E1 R(L48) vs rerun_plot_summary_20261112 curves.csv: R(L48) = 0.811 (expected 0.811) OK
- group A overall E1 R(L48) vs rerun_plot_summary_20261112 curves.csv: R(L48) lo = 0.7902 (expected 0.79) OK
- group A overall E1 R(L48) vs rerun_plot_summary_20261112 curves.csv: R(L48) hi = 0.8323 (expected 0.832) OK
- exact vs stored curves.csv (A, L48): max|diff| R, lo, hi = 0 (expected 0.0) OK

## Slopes

| quantity | estimate [95% CI] | p | CI includes 0 |
|---|---|---|---|
| slope R(L48) per unit mc_team_p_true | +0.031 [-0.312, +0.413] | 0.9280 | yes |
| slope R(L52) per unit mc_team_p_true | +0.004 [-0.133, +0.149] | 0.9600 | yes |
| slope denominator (true - false_0) per unit mc_team_p_true | +0.690 [+0.391, +0.992] | 0.0005 | no |
| slope R(L24) per unit mc_team_p_true (extra layer) | -0.048 [-0.207, +0.108] | 0.5500 | yes |
| slope R(L32) per unit mc_team_p_true (extra layer) | -0.223 [-0.488, +0.012] | 0.0670 | yes |
| slope R(L40) per unit mc_team_p_true (extra layer) | -0.094 [-0.399, +0.200] | 0.5250 | yes |
| slope R(L48) unweighted (sensitivity) | +0.032 [-0.313, +0.406] | 0.9110 | yes |
| R(L48) top bin minus bottom bin (sensitivity) | -0.049 [-0.157, +0.063] | 0.3660 | yes |
| slope R(L52) unweighted (sensitivity) | +0.004 [-0.131, +0.150] | 0.9650 | yes |
| R(L52) top bin minus bottom bin (sensitivity) | -0.004 [-0.041, +0.036] | 0.8040 | yes |
| denominator top bin minus bottom bin (sensitivity) | +0.204 [+0.109, +0.297] | 0.0005 | no |

## Per bin

| bin | p range | n | median p | R(L48) [CI] | R(L52) [CI] | denominator [CI] |
|---|---|---|---|---|---|---|
| 1 | 0.504-0.830 | 56 | 0.7821 | +0.823 [+0.718, +0.911] | +0.987 [+0.950, +1.022] | +0.316 [+0.257, +0.384] |
| 2 | 0.831-0.894 | 56 | 0.8648 | +0.813 [+0.752, +0.879] | +0.998 [+0.973, +1.024] | +0.378 [+0.304, +0.454] |
| 3 | 0.895-0.954 | 55 | 0.9239 | +0.739 [+0.653, +0.835] | +0.960 [+0.928, +0.991] | +0.308 [+0.248, +0.367] |
| 4 | 0.956-0.981 | 56 | 0.9727 | +0.902 [+0.825, +1.004] | +1.018 [+0.987, +1.058] | +0.305 [+0.236, +0.378] |
| 5 | 0.981-0.990 | 55 | 0.9858 | +0.825 [+0.759, +0.893] | +0.992 [+0.965, +1.020] | +0.387 [+0.317, +0.470] |
| 6 | 0.990-0.997 | 56 | 0.9951 | +0.882 [+0.800, +0.967] | +0.982 [+0.955, +1.008] | +0.352 [+0.295, +0.407] |
| 7 | 0.997-0.999 | 56 | 0.9986 | +0.762 [+0.709, +0.817] | +0.979 [+0.957, +1.000] | +0.513 [+0.442, +0.582] |
| 8 | 0.999-1.000 | 55 | 0.9996 | +0.830 [+0.782, +0.874] | +0.990 [+0.971, +1.008] | +0.478 [+0.412, +0.548] |
| 9 | 1.000-1.000 | 56 | 0.9999 | +0.802 [+0.750, +0.859] | +0.991 [+0.966, +1.017] | +0.513 [+0.441, +0.585] |
| 10 | 1.000-1.000 | 56 | 1.0000 | +0.774 [+0.713, +0.829] | +0.983 [+0.970, +0.997] | +0.520 [+0.449, +0.597] |

## Files

- `bins.csv`: per bin n, cut points, median p, R at L24/32/40/48/52 [CI], numerator L48 [CI], denominator [CI]
- `slopes.csv`: slopes (L48, L52, denominator; extra layers; sensitivities) with CI, p, CI-includes-0
- `parity.csv`
