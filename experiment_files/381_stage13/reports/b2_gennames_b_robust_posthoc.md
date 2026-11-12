# 2-11b post-hoc robustness (事后，探索性) — primary position (ii) name_mean

Written 2026-11-12 14:09 by `13_stage13/stage13_b2_gennames_b_robust.py` (CPU). Does not change the addendum-15 verdict. Same names, vectors, folds, probe and team-cluster bootstrap (2,000 draws) as the locked analysis.

Probe reproduction vs summary/probe_within.csv: max |diff| 0.0e+00.

Fame baseline = log1p(number of OTHER cohort papers with an author of the same full name / same surname + initial) and log1p(their summed citations); C = 0.01. Share of names with >= 1 other paper (exact / rule): M 0.058 / 0.426, H 0.045 / 0.478. Combined = position + string + fame features in one logistic model.

| layer | probe | fame baseline | probe - fame | combined baseline | probe - combined | shuffled (CI) | papers / pairs |
|---|---|---|---|---|---|---|---|
| L16 | 0.723 [0.696, 0.751] | 0.548 [0.519, 0.576] | +0.175 [+0.136, +0.215] | 0.679 [0.645, 0.712] | +0.045 [+0.008, +0.081] | 0.470 [0.434, 0.506] (480 papers) | 518 / 3388 |
| L24 | 0.740 [0.715, 0.767] | 0.548 [0.519, 0.576] | +0.192 [+0.156, +0.229] | 0.679 [0.645, 0.712] | +0.062 [+0.027, +0.094] | 0.483 [0.449, 0.516] (480 papers) | 518 / 3388 |
| L32 | 0.736 [0.708, 0.762] | 0.548 [0.519, 0.576] | +0.188 [+0.153, +0.223] | 0.679 [0.645, 0.712] | +0.057 [+0.021, +0.090] | 0.455 [0.420, 0.490] (480 papers) | 518 / 3388 |
| L40 | 0.780 [0.750, 0.808] | 0.548 [0.519, 0.576] | +0.231 [+0.193, +0.269] | 0.679 [0.645, 0.712] | +0.101 [+0.064, +0.135] | 0.466 [0.434, 0.496] (480 papers) | 518 / 3388 |
| L48 | 0.782 [0.754, 0.812] | 0.548 [0.519, 0.576] | +0.234 [+0.200, +0.269] | 0.679 [0.645, 0.712] | +0.104 [+0.067, +0.139] | 0.489 [0.456, 0.525] (480 papers) | 518 / 3388 |
| L52 | 0.771 [0.742, 0.798] | 0.548 [0.519, 0.576] | +0.223 [+0.186, +0.259] | 0.679 [0.645, 0.712] | +0.093 [+0.059, +0.127] | 0.477 [0.443, 0.513] (480 papers) | 518 / 3388 |
| L56 | 0.736 [0.706, 0.765] | 0.548 [0.519, 0.576] | +0.188 [+0.149, +0.227] | 0.679 [0.645, 0.712] | +0.058 [+0.023, +0.092] | 0.510 [0.478, 0.543] (480 papers) | 518 / 3388 |

Shuffled: labels permuted within training folds (rng 1212, as the locked analysis); AUROC against the shuffled labels on the papers that qualify under them.
Generation log-probability / entropy baseline: not computable from stored data (no logits or final-layer states saved); needs a GPU replay.

