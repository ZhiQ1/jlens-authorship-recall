# Stage 13 V42: paper-bootstrap vs team-cluster intervals (X1, X4, X6, X7, M3) and X4 recognition on tune / test

Scripts `~/jlens_work/13_stage13/stage13_v42_paper_vs_team.py` and `stage13_v42_m3_paperboot.py`, run 2026-11-05 02:42. CPU only, existing raw outputs.
Rules: prereg.json general rule (95% bootstrap over papers, 2,000 draws) and addendum 2 (team-cluster bootstrap too; both shown; team is primary; list every place where "interval excludes 0" changes). Estimators and team seeds unchanged from the original analysis scripts; the paper bootstrap treats each paper as its own cluster.
Combined table: `/scratch/zhang.zhiqi2/jlens/381_stage13/summary_v42/v42_paper_vs_team.csv` (1155 rows: analysis, split / group / position, quantity, layer, estimate, team CI, paper CI, width ratio paper/team, excludes-0 flags). X4 recognition by split: `/scratch/zhang.zhiqi2/jlens/381_stage13/summary_v42/x4_recognition_split.csv`.

## 1. Width of the intervals (paper CI width / team CI width)

| analysis | rows | median ratio | min | max | rows where "excludes 0" changes |
|---|---|---|---|---|---|
| X1 | 147 | 0.99 | 0.92 | 1.08 | 0 |
| X4 D | 126 | 1.00 | 0.94 | 1.07 | 1 |
| X4 recognition | 84 | 1.00 | 0.93 | 1.08 | 0 |
| X6 | 270 | 1.00 | 0.90 | 1.08 | 0 |
| X7 | 108 | 1.00 | 0.93 | 1.09 | 1 |
| M3 | 240 | 0.97 | 0.71 | 1.06 | 0 |
| M3 retrieval (V56) | 180 | 0.99 | 0.89 | 1.08 | 0 |

Team intervals are wider than paper intervals when papers of one author team are correlated (ratio < 1); a ratio near 1 means team clustering hardly matters.

## 2. Every place where "interval excludes 0" changes (team is primary)

| analysis | split / group / pos | quantity | layer | estimate | team CI | paper CI | team | paper |
|---|---|---|---|---|---|---|---|---|
| X4 D | test | D_year_title | L16 | +0.0044 | [-0.0003, +0.0094] | [+0.0001, +0.0092] | includes 0 | > 0 |
| X7 | target | T | L60 | +0.0029 | [+0.0000, +0.0056] | [-0.0000, +0.0056] | > 0 | includes 0 |

## 3. X4 recognition on the tune / test split (target - control of self - partner, within citation bin; min_n = 10)

Prereg X4: "D_year and D_author larger for target than control within citation bin (interval excludes 0)"; prereg general rule: layer chosen on tune, confirmatory number on test. Layer on tune = first layer with team interval > 0 (the X4 earliest-layer rule; the prereg does not name a layer rule for this contrast, so this choice is the X4 analogue).

| answer | pos | layer chosen on tune | test estimate | test team CI | test paper CI | confirmed (team) | confirmed (paper) |
|---|---|---|---|---|---|---|---|
| year | title | none on tune | - | - | - | - | - |
| year | colon | L8 | +0.0020 | [-0.0030, +0.0067] | [-0.0028, +0.0068] | no | no |
| author | title | L8 | +0.0231 | [-0.0006, +0.0478] | [-0.0014, +0.0478] | no | no |
| author | colon | L16 | +0.0006 | [-0.0043, +0.0052] | [-0.0042, +0.0052] | no | no |

### Every layer

| answer, pos | layer | all (team CI) | tune (team CI) | test (team CI) | test (paper CI) | bins all/tune/test |
|---|---|---|---|---|---|---|
| year, title | L8 | +0.000 [-0.006, +0.007] | +0.005 [-0.003, +0.014] | -0.004 [-0.014, +0.006] | -0.004 [-0.014, +0.006] | 10/10/10 |
| year, title | L16 | +0.003 [-0.004, +0.009] | +0.006 [-0.003, +0.015] | -0.000 [-0.010, +0.009] | -0.000 [-0.010, +0.010] | 10/10/10 |
| year, title | L24 | +0.004 [-0.002, +0.011] | +0.008 [-0.002, +0.018] | +0.002 [-0.008, +0.011] | +0.002 [-0.008, +0.011] | 10/10/10 |
| year, title | L32 | +0.004 [-0.003, +0.011] | +0.001 [-0.009, +0.012] | +0.008 [-0.002, +0.017] | +0.008 [-0.001, +0.018] | 10/10/10 |
| year, title | L40 | +0.002 [-0.005, +0.009] | +0.004 [-0.005, +0.013] | +0.001 [-0.008, +0.011] | +0.001 [-0.009, +0.011] | 10/10/10 |
| year, title | L48 | -0.002 [-0.008, +0.003] | +0.000 [-0.007, +0.008] | -0.005 [-0.012, +0.002] | -0.005 [-0.012, +0.002] | 10/10/10 |
| year, title | L56 | +0.001 [-0.001, +0.003] | +0.001 [-0.002, +0.004] | +0.002 [-0.001, +0.004] | +0.002 [-0.001, +0.004] | 10/10/10 |
| year, colon | L8 | +0.004 [+0.000, +0.007] | +0.005 [+0.001, +0.009] | +0.002 [-0.003, +0.007] | +0.002 [-0.003, +0.007] | 10/10/10 |
| year, colon | L16 | -0.001 [-0.004, +0.001] | -0.003 [-0.006, +0.001] | +0.000 [-0.003, +0.003] | +0.000 [-0.003, +0.003] | 10/10/10 |
| year, colon | L24 | -0.003 [-0.008, +0.001] | -0.005 [-0.012, +0.001] | -0.002 [-0.007, +0.005] | -0.002 [-0.008, +0.005] | 10/10/10 |
| year, colon | L32 | -0.000 [-0.004, +0.003] | -0.003 [-0.008, +0.003] | +0.002 [-0.004, +0.007] | +0.002 [-0.004, +0.007] | 10/10/10 |
| year, colon | L40 | +0.003 [-0.001, +0.008] | +0.001 [-0.006, +0.007] | +0.005 [-0.001, +0.012] | +0.005 [-0.001, +0.012] | 10/10/10 |
| year, colon | L48 | -0.000 [-0.003, +0.003] | -0.002 [-0.007, +0.003] | +0.003 [-0.002, +0.007] | +0.003 [-0.002, +0.007] | 10/10/10 |
| year, colon | L56 | -0.000 [-0.002, +0.002] | +0.001 [-0.002, +0.004] | -0.002 [-0.005, +0.001] | -0.002 [-0.005, +0.001] | 10/10/10 |
| author, title | L8 | +0.040 [+0.023, +0.057] | +0.057 [+0.033, +0.081] | +0.023 [-0.001, +0.048] | +0.023 [-0.001, +0.048] | 10/10/10 |
| author, title | L16 | +0.043 [+0.026, +0.061] | +0.051 [+0.027, +0.075] | +0.034 [+0.008, +0.059] | +0.034 [+0.007, +0.059] | 10/10/10 |
| author, title | L24 | +0.050 [+0.033, +0.066] | +0.055 [+0.031, +0.079] | +0.044 [+0.020, +0.070] | +0.044 [+0.020, +0.070] | 10/10/10 |
| author, title | L32 | +0.055 [+0.037, +0.073] | +0.061 [+0.037, +0.087] | +0.050 [+0.024, +0.075] | +0.050 [+0.023, +0.076] | 10/10/10 |
| author, title | L40 | +0.060 [+0.044, +0.078] | +0.061 [+0.037, +0.085] | +0.060 [+0.035, +0.084] | +0.060 [+0.034, +0.083] | 10/10/10 |
| author, title | L48 | +0.023 [+0.016, +0.031] | +0.021 [+0.011, +0.032] | +0.025 [+0.014, +0.035] | +0.025 [+0.014, +0.035] | 10/10/10 |
| author, title | L56 | +0.000 [-0.001, +0.002] | +0.000 [-0.001, +0.002] | +0.000 [-0.002, +0.002] | +0.000 [-0.002, +0.002] | 10/10/10 |
| author, colon | L8 | +0.001 [-0.002, +0.003] | +0.001 [-0.003, +0.004] | +0.001 [-0.003, +0.004] | +0.001 [-0.003, +0.004] | 10/10/10 |
| author, colon | L16 | +0.003 [-0.000, +0.006] | +0.006 [+0.002, +0.010] | +0.001 [-0.004, +0.005] | +0.001 [-0.004, +0.005] | 10/10/10 |
| author, colon | L24 | +0.001 [-0.001, +0.003] | +0.000 [-0.002, +0.003] | +0.002 [-0.001, +0.005] | +0.002 [-0.001, +0.005] | 10/10/10 |
| author, colon | L32 | +0.001 [-0.001, +0.004] | +0.001 [-0.002, +0.005] | +0.001 [-0.002, +0.005] | +0.001 [-0.002, +0.005] | 10/10/10 |
| author, colon | L40 | +0.003 [+0.001, +0.005] | +0.004 [+0.001, +0.007] | +0.002 [-0.001, +0.005] | +0.002 [-0.001, +0.005] | 10/10/10 |
| author, colon | L48 | +0.007 [+0.003, +0.011] | +0.007 [+0.002, +0.013] | +0.007 [+0.001, +0.012] | +0.007 [+0.001, +0.012] | 10/10/10 |
| author, colon | L56 | +0.004 [+0.001, +0.008] | +0.005 [+0.000, +0.010] | +0.003 [-0.002, +0.007] | +0.003 [-0.002, +0.007] | 10/10/10 |

## 4. Key rows side by side

| analysis | split | quantity | layer | estimate | team CI | paper CI |
|---|---|---|---|---|---|---|
| X1 | test | authors_minus_year | L24 | +0.0056 | [-0.0038, +0.0151] | [-0.0029, +0.0151] |
| X1 | test | authors_minus_year | L32 | +0.0047 | [-0.0062, +0.0159] | [-0.0059, +0.0152] |
| X1 | test | authors_minus_year | L40 | +0.0035 | [-0.0079, +0.0142] | [-0.0079, +0.0139] |
| X1 | test | authors_minus_year | L48 | +0.0192 | [+0.0120, +0.0265] | [+0.0122, +0.0261] |
| X1 | test | authors_minus_random_c | L24 | +1.0882 | [+1.0123, +1.1692] | [+1.0113, +1.1682] |
| X1 | test | authors_minus_random_c | L48 | +0.3018 | [+0.2563, +0.3489] | [+0.2571, +0.3498] |
| X4 D | test | D_author_title | L8 | +0.0465 | [+0.0350, +0.0587] | [+0.0348, +0.0588] |
| X4 D | test | D_author_title | L40 | +0.0683 | [+0.0559, +0.0802] | [+0.0560, +0.0813] |
| X4 D | test | D_author_title | L48 | +0.0235 | [+0.0183, +0.0289] | [+0.0184, +0.0291] |
| X4 D | test | D_year_title | L8 | +0.0077 | [+0.0026, +0.0126] | [+0.0026, +0.0128] |
| X4 D | test | D_year_title | L40 | +0.0129 | [+0.0082, +0.0176] | [+0.0082, +0.0176] |
| X6 | all | R_average | L24 | +0.0805 | [+0.0753, +0.0855] | [+0.0755, +0.0857] |
| X6 | all | R_average | L48 | +0.8211 | [+0.8059, +0.8352] | [+0.8055, +0.8363] |
| X6 | all | R_average | L52 | +0.9955 | [+0.9898, +1.0008] | [+0.9895, +1.0010] |
| X7 | all | S | L0 | +1.0037 | [+0.9975, +1.0101] | [+0.9977, +1.0099] |
| X7 | all | S | L48 | +0.1432 | [+0.1258, +0.1611] | [+0.1254, +0.1602] |
| X7 | all | S | L52 | +0.0293 | [+0.0206, +0.0377] | [+0.0210, +0.0379] |
| X7 | all | S | L54 | +0.0064 | [+0.0010, +0.0117] | [+0.0012, +0.0118] |
| X7 | all | S | L56 | -0.0038 | [-0.0076, +0.0001] | [-0.0081, +0.0002] |
| M3 | title_last | I_minus_L4 | L8 | -0.0050 | [-0.0052, -0.0049] | [-0.0052, -0.0049] |
| M3 | title_last | I_minus_L4 | L24 | -0.0111 | [-0.0114, -0.0109] | [-0.0114, -0.0109] |
| M3 | title_last | I_minus_L4 | L40 | -0.0138 | [-0.0142, -0.0135] | [-0.0142, -0.0135] |
| M3 | title_last | T_year | L16 | +0.9443 | [+0.9390, +0.9491] | [+0.9391, +0.9491] |
| M3 | title_last | T_year | L24 | +0.9463 | [+0.9421, +0.9500] | [+0.9421, +0.9503] |
| M3 | title_last | T_year | L40 | +0.9383 | [+0.9332, +0.9428] | [+0.9332, +0.9430] |
| M3 | title_last | T_year_minus_L4 | L16 | -0.0390 | [-0.0462, -0.0316] | [-0.0468, -0.0318] |
| M3 | title_last | T_year_minus_L4 | L24 | -0.0369 | [-0.0454, -0.0291] | [-0.0449, -0.0297] |
| M3 | title_last | T_year_minus_L4 | L40 | -0.0449 | [-0.0537, -0.0366] | [-0.0535, -0.0368] |

## Notes

- Team values reproduce the existing CSVs (x1_recovery, x4_decodability, x4_recognition, x6_recovery average, x7_knockout S, m3_identity / m3_transfer) unless listed under WARN.
- M3 transfer ratios: probes are fitted once (5 group folds) and the held-out predictions are resampled; the paper interval does not include probe refitting variance.
- X4 recognition on tune / test halves each citation bin; bins with < 10 target or < 10 control papers are dropped (n_bins column).
- X6 / X7 group = Stage 11 sample group (target / control); "all" = both.

## WARN

- none
