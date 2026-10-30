# E4b with training-fold standardisation vs the original (full-sample standardisation)

**TINY TEST RUN (16 shards = 2,048 papers, layer 24 only): numbers are NOT comparable with the full-cohort original.**

Change: E4b probe (stage10_extra_r0r1.probe, the version re-run by stage13_e4b_group.py) used mu, sd = X.mean(0), X.std(0) over all 9,108 papers, test folds included (stage10_extra_r0r1.py:244; same line in stage11_analyze.probe_section:176). Here mu, sd are fitted on the training folds of each fold (also for the fold-0 alpha search). Folds, exclusion rule, alpha grid, scoring and bootstrap seeds unchanged.
The X1 controls (stage12_cpu.probe_controls) already standardised on the training fold (stage12_cpu.py:143); they are re-run unchanged and should reproduce the original exactly.

Max |new - orig|: E4b pooled target - control 0.0204; E4b all-paper signal 0.0318; X1 spec_all 0.0157; X1 target - control 0.0490.
Rows where "CI contains 0" changed: E4b tc_pooled 1/4, tc_R0 1, tc_R1 2, C - A 2; E4b all-paper 0/4; X1 spec_all 0/16, X1 tc 1/16.
Alpha changed in 4/4 (config, layer) cells.

## Confirmatory configuration (author-team folds + title-reuse exclusion)

### E4b probe: title-specific signal, all papers (target + control; mean of per-paper spec, paper bootstrap)

| layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|
| L24 | +0.0508 | +0.0189 | -0.0318 | [+0.039, +0.062] | [+0.012, +0.027] | no -> no |

### E4b probe: target - control within citation bin (pooled)

| layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|
| L24 | +0.0518 | +0.0314 | -0.0204 | [+0.017, +0.088] | [+0.008, +0.055] | no -> no |

### Controls (X1), all papers: spec_all

| layer | control | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|
| L24 | probe (as in Stage 11) | +0.0505 | +0.0387 | -0.0117 | [+0.039, +0.062] | [+0.026, +0.052] | no -> no |
| L24 | gold = random other paper | -0.0020 | -0.0041 | -0.0021 | [-0.014, +0.009] | [-0.017, +0.009] | yes -> yes |
| L24 | gold = random paper of the same field | +0.0011 | -0.0021 | -0.0032 | [-0.010, +0.012] | [-0.015, +0.010] | yes -> yes |
| L24 | probe trained on FALSE-title pairs | +0.0501 | +0.0419 | -0.0082 | [+0.039, +0.062] | [+0.029, +0.055] | no -> no |

### Controls (X1): target - control within citation bin

| layer | control | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|
| L24 | probe (as in Stage 11) | +0.0522 | +0.0843 | +0.0321 | [+0.016, +0.086] | [+0.038, +0.129] | no -> no |
| L24 | gold = random other paper | +0.0034 | +0.0394 | +0.0360 | [-0.029, +0.036] | [-0.005, +0.083] | yes -> yes |
| L24 | gold = random paper of the same field | -0.0064 | -0.0081 | -0.0017 | [-0.037, +0.025] | [-0.050, +0.034] | yes -> yes |
| L24 | probe trained on FALSE-title pairs | +0.0400 | +0.0597 | +0.0197 | [+0.006, +0.076] | [+0.008, +0.111] | no -> no |

## All 4 configurations: E4b pooled target - control

| split | excl | layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|---|
| paper | none | L24 | +0.0244 | +0.0233 | -0.0011 | [+0.010, +0.038] | [+0.005, +0.041] | no -> no |
| paper | title-reuse | L24 | +0.0179 | +0.0244 | +0.0065 | [-0.012, +0.049] | [+0.002, +0.047] | yes -> no **CHANGED** |
| group | none | L24 | +0.0262 | +0.0212 | -0.0050 | [+0.012, +0.040] | [+0.004, +0.039] | no -> no |
| group | title-reuse | L24 | +0.0518 | +0.0314 | -0.0204 | [+0.017, +0.088] | [+0.008, +0.055] | no -> no |

## All 4 configurations: E4b all-paper signal

| split | excl | layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|---|
| group | none | L24 | +0.0461 | +0.0207 | -0.0254 | [+0.041, +0.051] | [+0.014, +0.027] | no -> no |
| group | title-reuse | L24 | +0.0508 | +0.0189 | -0.0318 | [+0.039, +0.062] | [+0.012, +0.027] | no -> no |
| paper | none | L24 | +0.0452 | +0.0176 | -0.0275 | [+0.040, +0.050] | [+0.011, +0.025] | no -> no |
| paper | title-reuse | L24 | +0.0426 | +0.0160 | -0.0266 | [+0.032, +0.053] | [+0.008, +0.024] | no -> no |

## Per-paper agreement of the E4b spec (before exclusion): Pearson r and mean |new - orig|

split        excl  layer      r    mad      n
group        none     24 0.5655 0.1322 1532.0
group title-reuse     24 0.5655 0.1322 1532.0
paper        none     24 0.5857 0.1326 1532.0
paper title-reuse     24 0.5857 0.1326 1532.0

Full comparison tables: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_trainstd_tiny/compare_E4b.csv (also tc_R0, tc_R1, C - A, alpha), compare_E4b_allpapers.csv, compare_X1.csv.
