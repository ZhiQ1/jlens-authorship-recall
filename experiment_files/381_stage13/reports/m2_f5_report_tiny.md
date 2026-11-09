# M2 with five false titles (false_0 … false_4) — TINY TEST

Titles: false_0, false_1, false_2, false_3, false_4. Labels = the paper whose title is in the prompt (donor of false_k). Same probes, folds rule, intervals as the published false_0 run (stage13_m2_f5.py; hard check: reports/m2_f5_hardcheck.md). Five-title mean = plain mean of the 5 per-title values (each title has its own donor-team folds and intervals).
Rule used for "unchanged / weaker / stronger": |five-title mean − false_0| ≤ 0.02 → unchanged; otherwise stronger if the readout is higher (more readable), weaker if lower. For "above chance" claims: count of titles whose team-cluster interval lower bound is above the null level.

Tables: summary_m2_f5/M2_f5_mean.csv (per title, mean, min, max, true-title value), M2_probes_f5_all.csv, M2_teamci_f5_all.csv.

## Published conclusions vs five-title mean

| # | published conclusion (false_0) | false_0 | five-title mean [min, max] | titles with team CI above null | verdict |
|---|---|---|---|---|---|
| 1 | false-title runs read the donor (title paper) year: title L48 R² 0.535 | - | (layer not run) | - | n/a |
| 2 | donor citations: title L48 R² 0.488 | - | (layer not run) | - | n/a |
| 3 | donor citations with year removed: title L48 | - | (layer not run) | - | n/a |
| 4 | donor year, title L16 | 0.116 | 0.138 [0.034, 0.260] | 3/5 | stronger |
| 5 | donor field accuracy, title L48 | - | (layer not run) | - | n/a |
| 6 | donor year, title L52 (true-title peak layer) | - | (layer not run) | - | n/a |
| 7 | "still readable, comparable to the true-title run": max |true − false| over title-position rows | 0.267 | 0.245 | - | stronger (smaller gap = stronger) |
| 8 | all title-position false rows above chance (team CI) | 4/4 rows | 1/4 rows above null for all titles | - | weaker |

True-title conclusions are not recomputed here (true-title runs only): year R² 0.56 (Qwen) vs 0.24 (BERT), recognisable AUROC 0.67 vs 0.63 (BERT), field accuracy 0.69–0.72, citations 0.28–0.53 → **unchanged by construction**. The M2c BERT baseline and M2b use true-title text only.

## Title position: five-title mean (false_0) per layer

- field: L16 0.493 (0.473)
- year: L16 0.138 (0.116)
- log citations: L16 0.139 (0.131)
- log citations | year removed: L16 0.137 (0.141)

## Colon position (year is in the prompt; year row = positive control only)

- field: L16 0.659 (0.656)
- year: L16 0.830 (0.838)
- log citations: L16 0.217 (0.224)
- log citations | year removed: L16 0.196 (0.185)

## Year-only baseline

- log citations: 0.015 (0.020)
- log citations | year removed: -0.018 (-0.018)

## Team vs per-paper interval flips (all titles): 1 rows (false_0 published: 0)

  title condition position  layer        target  value_new  null  lo_paper  hi_paper  lo_team  hi_team
false_1   false_1    title     16 log citations      0.117   0.0     0.006     0.201   -0.006    0.182

No interpretation beyond unchanged / weaker / stronger (user instruction 2026-11-08).
