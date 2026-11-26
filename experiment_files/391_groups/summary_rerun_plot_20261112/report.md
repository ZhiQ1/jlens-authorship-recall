# E1 recovery by group and by MC orders right: plot-ready summary (2026-11-12)

Written 2026-11-12 23:34 by `~/jlens_work/14_groups/rerun_plot_summary_20261112.py` (CPU; stored per-paper outputs; frozen `rerun_analyze.py` / `groups_core.py` functions loaded unchanged). E1 = Stage 11 title patching true -> false_0; R(l) = mean(patched_l - false_0) / mean(true - false_0) over papers, unwritten authors (addendum 7). 95% team-cluster bootstrap (2,000 draws, seed 391, archived author teams, one shared draw). n < 30 papers: descriptive only. R2 = upper reference only.

## Pre-specification

- Addendum 8 (`config/prereg_addendum8_groups.json` line 24): "same estimands as Stage 11/12 ... with team-cluster CIs; R2 is a reference (addendum 7); R0-uncertain is compared with A and B descriptively and through the continuous-recognition curves". No test, trend or decision rule for E1.
- Addendum 7 line 18 defines a trend test (P3: slope on mc_team_a within R0, regression with citation-bin FE, Holm) only for the primary measure (Stage 10 output title-specific signal, line 14). Line 23 lists "Stage 11 E1/E2 ... split by A/B/C/D" and "signal curves against mc_team_a" as exploratory, no multiplicity correction.
- Therefore every slope below is **post hoc, descriptive**.

## Parity

36 checks vs stored summaries (cd_group_values.csv, rerun_group_values.csv, e1_e2_num_den.csv, rerun_curves_R0.csv) and the slide numbers: all OK.
Max |diff| vs stored CSVs: 2.2e-16. Slide: denominator k=0 0.1854 (OK), denominator k=4 0.407 (OK), R(L48) k=0 0.9041 (OK), R(L48) k=4 0.811 (OK), n k=0 241 (OK), n k=4 557 (OK)

## Per MC orders right (R0 = A + U0 + B)

| k | n (A / U0 / B) | denominator [CI] | R(L48) [CI] | R(L52) [CI] |
|---|---|---|---|---|
| 0 | 241 (0 / 0 / 241) | +0.185 [+0.157, +0.215] | +0.904 [+0.848, +0.965] | +1.020 [+0.996, +1.048] |
| 1 | 345 (0 / 0 / 345) | +0.234 [+0.209, +0.260] | +0.850 [+0.806, +0.897] | +1.014 [+0.997, +1.033] |
| 2 | 271 (0 / 271 / 0) | +0.269 [+0.240, +0.300] | +0.850 [+0.802, +0.904] | +1.007 [+0.988, +1.028] |
| 3 | 328 (0 / 328 / 0) | +0.313 [+0.283, +0.346] | +0.839 [+0.801, +0.881] | +0.995 [+0.980, +1.009] |
| 4 | 557 (557 / 0 / 0) | +0.407 [+0.386, +0.430] | +0.811 [+0.790, +0.832] | +0.988 [+0.980, +0.996] |

Note: k is fully nested in group here: k = 0, 1 are all B, k = 2, 3 all U0, k = 4 all A (by the strong / uncertain / fail definition from MC orders). The "curve" is therefore also a B -> U0 -> A comparison, and the three groups were sampled at different rates (A 557 of 4,110; U0 600 of 2,002; B 588 of 2,186) and U0 came from a separate GPU run (same driver). Not a within-group dose-response.

## Trend (post hoc, descriptive)

Definition: R_k = ratio of paper means within cell k; slope = weighted least-squares slope of the five R_k on k with weights n_k (cell paper count in that draw); recomputed in every team draw. Denominator slope with n_k weights = paper-level OLS slope.

| quantity | estimate [95% CI] | p | CI includes 0 |
|---|---|---|---|
| slope R(L24) per MC order right | -0.005 [-0.012, +0.001] | 0.0960 | yes |
| slope R(L32) per MC order right | -0.011 [-0.020, -0.003] | 0.0070 | no |
| slope R(L40) per MC order right | -0.017 [-0.029, -0.006] | 0.0020 | no |
| slope R(L48) per MC order right | -0.019 [-0.032, -0.007] | 0.0040 | no |
| slope R(L52) per MC order right | -0.008 [-0.014, -0.004] | 0.0005 | no |
| slope denominator (true - false_0) per MC order right | +0.055 [+0.046, +0.063] | 0.0005 | no |
| slope R(L48) unweighted (sensitivity) | -0.020 [-0.034, -0.006] | 0.0100 | no |
| R(L48) k=4 minus k=0 (sensitivity) | -0.093 [-0.160, -0.032] | 0.0030 | no |
| slope R(L52) unweighted (sensitivity) | -0.008 [-0.014, -0.003] | 0.0010 | no |
| R(L52) k=4 minus k=0 (sensitivity) | -0.032 [-0.060, -0.007] | 0.0040 | no |
| denominator k=4 minus k=0 (sensitivity) | +0.222 [+0.183, +0.258] | 0.0005 | no |
| slope denominator, paper-level WLS with citation-bin FE (sensitivity; addendum 7 P3 form) | +0.055 [+0.047, +0.063] | 0.0005 | no |

## Group curves at selected layers (unwritten authors)

| group | n | L40 R | L48 R [CI] | L52 R [CI] | denominator [CI] |
|---|---|---|---|---|---|
| A | 557 | +0.276 | +0.811 [+0.790, +0.832] | +0.988 [+0.980, +0.996] | +0.407 [+0.386, +0.430] |
| B | 586 | +0.338 | +0.869 [+0.835, +0.906] | +1.016 [+1.002, +1.031] | +0.214 [+0.196, +0.234] |
| U0 | 599 | +0.340 | +0.844 [+0.814, +0.877] | +1.000 [+0.988, +1.012] | +0.293 [+0.271, +0.316] |
| C | 462 | +0.198 | +0.731 [+0.705, +0.757] | +0.985 [+0.977, +0.994] | +0.559 [+0.529, +0.590] |
| D | 33 | +0.316 | +0.786 [+0.674, +0.952] | +0.968 [+0.917, +1.041] | +0.197 [+0.122, +0.277] |
| R2 (reference) | 28 (n<30) | +0.262 | +0.792 [+0.662, +0.944] | +1.027 [+0.958, +1.114] | +0.634 [+0.453, +0.816] |

## Files

- `curves.csv`: group x layer -> R, R_lo, R_hi, n_papers (groups A, B, C, D, U0, R2, plus C_stage11 / D_stage11 parity subsets)
- `numden.csv`: group x layer -> numerator, denominator with CIs (and R)
- `recog.csv`: k = 0..4 -> n (and group split), denominator [CI], R(L48), R(L52) [CI], point R at L24/32/40
- `trend.csv`: slopes and sensitivities with CI, p, CI-includes-0
- `parity.csv`: reproduction checks
