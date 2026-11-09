# M2 with five false titles (false_0 … false_4)

Titles: false_0, false_1, false_2, false_3, false_4. Labels = the paper whose title is in the prompt (donor of false_k). Same probes, folds rule, intervals as the published false_0 run (stage13_m2_f5.py; hard check: reports/m2_f5_hardcheck.md). Five-title mean = plain mean of the 5 per-title values (each title has its own donor-team folds and intervals).
Rule used for "unchanged / weaker / stronger": |five-title mean − false_0| ≤ 0.02 → unchanged; otherwise stronger if the readout is higher (more readable), weaker if lower. For "above chance" claims: count of titles whose team-cluster interval lower bound is above the null level.

Tables: summary_m2_f5/M2_f5_mean.csv (per title, mean, min, max, true-title value), M2_probes_f5_all.csv, M2_teamci_f5_all.csv.

## Published conclusions vs five-title mean

| # | published conclusion (false_0) | false_0 | five-title mean [min, max] | titles with team CI above null | verdict |
|---|---|---|---|---|---|
| 1 | false-title runs read the donor (title paper) year: title L48 R² 0.535 | 0.535 | 0.527 [0.506, 0.537] | 5/5 | unchanged |
| 2 | donor citations: title L48 R² 0.488 | 0.488 | 0.507 [0.488, 0.521] | 5/5 | unchanged |
| 3 | donor citations with year removed: title L48 | 0.471 | 0.491 [0.471, 0.506] | 5/5 | stronger |
| 4 | donor year, title L16 | 0.353 | 0.341 [0.319, 0.353] | 5/5 | unchanged |
| 5 | donor field accuracy, title L48 | 0.716 | 0.712 [0.703, 0.718] | 5/5 | unchanged |
| 6 | donor year, title L52 (true-title peak layer) | 0.538 | 0.529 [0.509, 0.545] | 5/5 | unchanged |
| 7 | "still readable, comparable to the true-title run": max |true − false| over title-position rows | 0.051 | 0.049 | - | unchanged (smaller gap = stronger) |
| 8 | all title-position false rows above chance (team CI) | 36/36 rows | 36/36 rows above null for all titles | - | unchanged |

True-title conclusions are not recomputed here (true-title runs only): year R² 0.56 (Qwen) vs 0.24 (BERT), recognisable AUROC 0.67 vs 0.63 (BERT), field accuracy 0.69–0.72, citations 0.28–0.53 → **unchanged by construction**. The M2c BERT baseline and M2b use true-title text only.

## Title position: five-title mean (false_0) per layer

- field: L16 0.682 (0.689); L24 0.711 (0.715); L32 0.712 (0.716); L40 0.706 (0.708); L44 0.699 (0.702); L48 0.712 (0.716); L52 0.712 (0.718); L56 0.715 (0.723); L60 0.713 (0.715)
- year: L16 0.341 (0.353); L24 0.407 (0.421); L32 0.422 (0.446); L40 0.467 (0.480); L44 0.489 (0.498); L48 0.527 (0.535); L52 0.529 (0.538); L56 0.525 (0.532); L60 0.516 (0.526)
- log citations: L16 0.255 (0.246); L24 0.336 (0.333); L32 0.336 (0.326); L40 0.422 (0.405); L44 0.485 (0.473); L48 0.507 (0.488); L52 0.499 (0.484); L56 0.497 (0.478); L60 0.479 (0.468)
- log citations | year removed: L16 0.245 (0.232); L24 0.322 (0.315); L32 0.319 (0.313); L40 0.405 (0.390); L44 0.468 (0.455); L48 0.491 (0.471); L52 0.482 (0.470); L56 0.480 (0.463); L60 0.463 (0.453)

## Colon position (year is in the prompt; year row = positive control only)

- field: L16 0.737 (0.743); L24 0.737 (0.743); L32 0.739 (0.741); L40 0.742 (0.740); L44 0.738 (0.737); L48 0.749 (0.749); L52 0.746 (0.747); L56 0.743 (0.746); L60 0.740 (0.741); L63 0.741 (0.743)
- year: L16 0.912 (0.938); L24 0.918 (0.945); L32 0.917 (0.944); L40 0.921 (0.946); L44 0.919 (0.937); L48 0.922 (0.943); L52 0.918 (0.946); L56 0.901 (0.924); L60 0.889 (0.909); L63 0.881 (0.901)
- log citations: L16 0.412 (0.407); L24 0.485 (0.480); L32 0.493 (0.484); L40 0.554 (0.542); L44 0.594 (0.582); L48 0.617 (0.609); L52 0.601 (0.595); L56 0.571 (0.557); L60 0.552 (0.538); L63 0.556 (0.539)
- log citations | year removed: L16 0.376 (0.371); L24 0.453 (0.449); L32 0.462 (0.453); L40 0.524 (0.512); L44 0.567 (0.555); L48 0.591 (0.577); L52 0.576 (0.566); L56 0.540 (0.524); L60 0.520 (0.503); L63 0.522 (0.502)

## Year-only baseline

- log citations: 0.045 (0.048)
- log citations | year removed: -0.001 (-0.001)

## Team vs per-paper interval flips (all titles): 0 rows (false_0 published: 0)


No interpretation beyond unchanged / weaker / stronger (user instruction 2026-11-08).
