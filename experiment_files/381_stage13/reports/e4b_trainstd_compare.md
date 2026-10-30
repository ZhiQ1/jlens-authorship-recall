# E4b with training-fold standardisation vs the original (full-sample standardisation)


Change: E4b probe (stage10_extra_r0r1.probe, the version re-run by stage13_e4b_group.py) used mu, sd = X.mean(0), X.std(0) over all 9,108 papers, test folds included (stage10_extra_r0r1.py:244; same line in stage11_analyze.probe_section:176). Here mu, sd are fitted on the training folds of each fold (also for the fold-0 alpha search). Folds, exclusion rule, alpha grid, scoring and bootstrap seeds unchanged.
The X1 controls (stage12_cpu.probe_controls) already standardised on the training fold (stage12_cpu.py:143); they are re-run unchanged and should reproduce the original exactly.

Max |new - orig|: E4b pooled target - control 0.0020; E4b all-paper signal 0.0075; X1 spec_all 0.0000; X1 target - control 0.0000.
Rows where "CI contains 0" changed: E4b tc_pooled 1/36, tc_R0 0, tc_R1 0, C - A 0; E4b all-paper 0/36; X1 spec_all 0/48, X1 tc 0/48.
Alpha changed in 0/36 (config, layer) cells.

## Confirmatory configuration (author-team folds + title-reuse exclusion)

### E4b probe: title-specific signal, all papers (target + control; mean of per-paper spec, paper bootstrap)

| layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|
| L16 | +0.0415 | +0.0415 | -0.0000 | [+0.028, +0.054] | [+0.028, +0.054] | no -> no |
| L24 | +0.0508 | +0.0504 | -0.0003 | [+0.039, +0.062] | [+0.037, +0.063] | no -> no |
| L32 | +0.0467 | +0.0467 | +0.0000 | [+0.033, +0.061] | [+0.034, +0.061] | no -> no |
| L40 | +0.0664 | +0.0609 | -0.0055 | [+0.053, +0.079] | [+0.047, +0.076] | no -> no |
| L44 | +0.0577 | +0.0581 | +0.0003 | [+0.043, +0.072] | [+0.044, +0.073] | no -> no |
| L48 | +0.0626 | +0.0619 | -0.0007 | [+0.047, +0.078] | [+0.046, +0.077] | no -> no |
| L52 | +0.0691 | +0.0692 | +0.0001 | [+0.053, +0.084] | [+0.054, +0.085] | no -> no |
| L56 | +0.0802 | +0.0753 | -0.0048 | [+0.067, +0.094] | [+0.060, +0.090] | no -> no |
| L60 | +0.0670 | +0.0672 | +0.0001 | [+0.053, +0.081] | [+0.053, +0.082] | no -> no |

### E4b probe: target - control within citation bin (pooled)

| layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|
| L16 | +0.0213 | +0.0216 | +0.0002 | [-0.011, +0.054] | [-0.011, +0.055] | yes -> yes |
| L24 | +0.0518 | +0.0522 | +0.0004 | [+0.017, +0.088] | [+0.017, +0.089] | no -> no |
| L32 | +0.0702 | +0.0702 | +0.0001 | [+0.032, +0.109] | [+0.032, +0.109] | no -> no |
| L40 | +0.0652 | +0.0642 | -0.0010 | [+0.027, +0.102] | [+0.026, +0.101] | no -> no |
| L44 | +0.0359 | +0.0345 | -0.0015 | [+0.001, +0.072] | [+0.000, +0.071] | no -> no |
| L48 | +0.0777 | +0.0778 | +0.0001 | [+0.038, +0.117] | [+0.038, +0.117] | no -> no |
| L52 | +0.0638 | +0.0638 | +0.0000 | [+0.023, +0.103] | [+0.023, +0.103] | no -> no |
| L56 | +0.0753 | +0.0766 | +0.0012 | [+0.038, +0.115] | [+0.039, +0.116] | no -> no |
| L60 | +0.0777 | +0.0782 | +0.0004 | [+0.037, +0.116] | [+0.037, +0.116] | no -> no |

### Controls (X1), all papers: spec_all

| layer | control | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|
| L24 | probe (as in Stage 11) | +0.0505 | +0.0505 | +0.0000 | [+0.039, +0.062] | [+0.039, +0.062] | no -> no |
| L24 | gold = random other paper | -0.0020 | -0.0020 | +0.0000 | [-0.014, +0.009] | [-0.014, +0.009] | yes -> yes |
| L24 | gold = random paper of the same field | +0.0011 | +0.0011 | +0.0000 | [-0.010, +0.012] | [-0.010, +0.012] | yes -> yes |
| L24 | probe trained on FALSE-title pairs | +0.0501 | +0.0501 | +0.0000 | [+0.039, +0.062] | [+0.039, +0.062] | no -> no |
| L40 | probe (as in Stage 11) | +0.0661 | +0.0661 | +0.0000 | [+0.053, +0.079] | [+0.053, +0.079] | no -> no |
| L40 | gold = random other paper | -0.0035 | -0.0035 | +0.0000 | [-0.015, +0.008] | [-0.015, +0.008] | yes -> yes |
| L40 | gold = random paper of the same field | +0.0065 | +0.0065 | +0.0000 | [-0.006, +0.019] | [-0.006, +0.019] | yes -> yes |
| L40 | probe trained on FALSE-title pairs | +0.0573 | +0.0573 | +0.0000 | [+0.045, +0.071] | [+0.045, +0.071] | no -> no |
| L56 | probe (as in Stage 11) | +0.0801 | +0.0801 | +0.0000 | [+0.068, +0.094] | [+0.068, +0.094] | no -> no |
| L56 | gold = random other paper | -0.0032 | -0.0032 | +0.0000 | [-0.016, +0.009] | [-0.016, +0.009] | yes -> yes |
| L56 | gold = random paper of the same field | -0.0045 | -0.0045 | +0.0000 | [-0.017, +0.008] | [-0.017, +0.008] | yes -> yes |
| L56 | probe trained on FALSE-title pairs | +0.0744 | +0.0744 | +0.0000 | [+0.060, +0.088] | [+0.060, +0.088] | no -> no |

### Controls (X1): target - control within citation bin

| layer | control | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|
| L24 | probe (as in Stage 11) | +0.0522 | +0.0522 | +0.0000 | [+0.016, +0.086] | [+0.016, +0.086] | no -> no |
| L24 | gold = random other paper | +0.0034 | +0.0034 | +0.0000 | [-0.029, +0.036] | [-0.029, +0.036] | yes -> yes |
| L24 | gold = random paper of the same field | -0.0064 | -0.0064 | +0.0000 | [-0.037, +0.025] | [-0.037, +0.025] | yes -> yes |
| L24 | probe trained on FALSE-title pairs | +0.0400 | +0.0400 | +0.0000 | [+0.006, +0.076] | [+0.006, +0.076] | no -> no |
| L40 | probe (as in Stage 11) | +0.0642 | +0.0642 | +0.0000 | [+0.025, +0.103] | [+0.025, +0.103] | no -> no |
| L40 | gold = random other paper | -0.0003 | -0.0003 | +0.0000 | [-0.034, +0.035] | [-0.034, +0.035] | yes -> yes |
| L40 | gold = random paper of the same field | -0.0102 | -0.0102 | +0.0000 | [-0.046, +0.025] | [-0.046, +0.025] | yes -> yes |
| L40 | probe trained on FALSE-title pairs | +0.0352 | +0.0352 | +0.0000 | [-0.003, +0.074] | [-0.003, +0.074] | yes -> yes |
| L56 | probe (as in Stage 11) | +0.0766 | +0.0766 | +0.0000 | [+0.038, +0.117] | [+0.038, +0.117] | no -> no |
| L56 | gold = random other paper | -0.0110 | -0.0110 | +0.0000 | [-0.048, +0.026] | [-0.048, +0.026] | yes -> yes |
| L56 | gold = random paper of the same field | -0.0007 | -0.0007 | +0.0000 | [-0.035, +0.036] | [-0.035, +0.036] | yes -> yes |
| L56 | probe trained on FALSE-title pairs | +0.0716 | +0.0716 | +0.0000 | [+0.030, +0.114] | [+0.030, +0.114] | no -> no |

## All 4 configurations: E4b pooled target - control

| split | excl | layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|---|
| paper | none | L16 | +0.0189 | +0.0185 | -0.0003 | [+0.005, +0.032] | [+0.005, +0.032] | no -> no |
| paper | none | L24 | +0.0244 | +0.0244 | +0.0001 | [+0.010, +0.038] | [+0.010, +0.039] | no -> no |
| paper | none | L32 | +0.0352 | +0.0355 | +0.0003 | [+0.020, +0.050] | [+0.020, +0.050] | no -> no |
| paper | none | L40 | +0.0324 | +0.0320 | -0.0004 | [+0.017, +0.047] | [+0.017, +0.047] | no -> no |
| paper | none | L44 | +0.0239 | +0.0243 | +0.0004 | [+0.010, +0.039] | [+0.010, +0.040] | no -> no |
| paper | none | L48 | +0.0316 | +0.0315 | -0.0001 | [+0.016, +0.047] | [+0.016, +0.047] | no -> no |
| paper | none | L52 | +0.0366 | +0.0371 | +0.0004 | [+0.021, +0.053] | [+0.021, +0.053] | no -> no |
| paper | none | L56 | +0.0388 | +0.0385 | -0.0004 | [+0.022, +0.054] | [+0.022, +0.054] | no -> no |
| paper | none | L60 | +0.0367 | +0.0360 | -0.0007 | [+0.020, +0.053] | [+0.020, +0.052] | no -> no |
| paper | title-reuse | L16 | +0.0103 | +0.0083 | -0.0020 | [-0.019, +0.040] | [-0.021, +0.038] | yes -> yes |
| paper | title-reuse | L24 | +0.0179 | +0.0180 | +0.0001 | [-0.012, +0.049] | [-0.012, +0.049] | yes -> yes |
| paper | title-reuse | L32 | +0.0444 | +0.0448 | +0.0004 | [+0.013, +0.074] | [+0.013, +0.075] | no -> no |
| paper | title-reuse | L40 | +0.0286 | +0.0282 | -0.0004 | [-0.004, +0.060] | [-0.004, +0.060] | yes -> yes |
| paper | title-reuse | L44 | +0.0069 | +0.0073 | +0.0004 | [-0.023, +0.037] | [-0.023, +0.038] | yes -> yes |
| paper | title-reuse | L48 | +0.0165 | +0.0164 | -0.0001 | [-0.015, +0.048] | [-0.015, +0.049] | yes -> yes |
| paper | title-reuse | L52 | +0.0264 | +0.0272 | +0.0008 | [-0.009, +0.062] | [-0.008, +0.063] | yes -> yes |
| paper | title-reuse | L56 | +0.0310 | +0.0295 | -0.0015 | [-0.003, +0.066] | [-0.005, +0.065] | yes -> yes |
| paper | title-reuse | L60 | +0.0304 | +0.0291 | -0.0013 | [-0.004, +0.065] | [-0.006, +0.063] | yes -> yes |
| group | none | L16 | +0.0140 | +0.0136 | -0.0004 | [+0.000, +0.028] | [-0.000, +0.028] | no -> yes **CHANGED** |
| group | none | L24 | +0.0262 | +0.0267 | +0.0005 | [+0.012, +0.040] | [+0.013, +0.041] | no -> no |
| group | none | L32 | +0.0327 | +0.0325 | -0.0002 | [+0.018, +0.046] | [+0.018, +0.046] | no -> no |
| group | none | L40 | +0.0276 | +0.0270 | -0.0006 | [+0.013, +0.042] | [+0.012, +0.041] | no -> no |
| group | none | L44 | +0.0185 | +0.0186 | +0.0002 | [+0.004, +0.034] | [+0.004, +0.034] | no -> no |
| group | none | L48 | +0.0320 | +0.0319 | -0.0000 | [+0.018, +0.048] | [+0.017, +0.047] | no -> no |
| group | none | L52 | +0.0342 | +0.0340 | -0.0001 | [+0.018, +0.050] | [+0.019, +0.050] | no -> no |
| group | none | L56 | +0.0347 | +0.0345 | -0.0002 | [+0.019, +0.051] | [+0.018, +0.050] | no -> no |
| group | none | L60 | +0.0298 | +0.0301 | +0.0003 | [+0.014, +0.045] | [+0.014, +0.046] | no -> no |
| group | title-reuse | L16 | +0.0213 | +0.0216 | +0.0002 | [-0.011, +0.054] | [-0.011, +0.055] | yes -> yes |
| group | title-reuse | L24 | +0.0518 | +0.0522 | +0.0004 | [+0.017, +0.088] | [+0.017, +0.089] | no -> no |
| group | title-reuse | L32 | +0.0702 | +0.0702 | +0.0001 | [+0.032, +0.109] | [+0.032, +0.109] | no -> no |
| group | title-reuse | L40 | +0.0652 | +0.0642 | -0.0010 | [+0.027, +0.102] | [+0.026, +0.101] | no -> no |
| group | title-reuse | L44 | +0.0359 | +0.0345 | -0.0015 | [+0.001, +0.072] | [+0.000, +0.071] | no -> no |
| group | title-reuse | L48 | +0.0777 | +0.0778 | +0.0001 | [+0.038, +0.117] | [+0.038, +0.117] | no -> no |
| group | title-reuse | L52 | +0.0638 | +0.0638 | +0.0000 | [+0.023, +0.103] | [+0.023, +0.103] | no -> no |
| group | title-reuse | L56 | +0.0753 | +0.0766 | +0.0012 | [+0.038, +0.115] | [+0.039, +0.116] | no -> no |
| group | title-reuse | L60 | +0.0777 | +0.0782 | +0.0004 | [+0.037, +0.116] | [+0.037, +0.116] | no -> no |

## All 4 configurations: E4b all-paper signal

| split | excl | layer | orig | new | new - orig | orig CI | new CI | CI contains 0: orig -> new |
|---|---|---|---|---|---|---|---|---|
| group | none | L16 | +0.0403 | +0.0403 | -0.0000 | [+0.035, +0.046] | [+0.035, +0.046] | no -> no |
| group | none | L24 | +0.0461 | +0.0450 | -0.0011 | [+0.041, +0.051] | [+0.039, +0.051] | no -> no |
| group | none | L32 | +0.0496 | +0.0496 | +0.0000 | [+0.044, +0.055] | [+0.044, +0.055] | no -> no |
| group | none | L40 | +0.0624 | +0.0624 | -0.0000 | [+0.057, +0.068] | [+0.056, +0.069] | no -> no |
| group | none | L44 | +0.0565 | +0.0564 | -0.0002 | [+0.051, +0.063] | [+0.050, +0.062] | no -> no |
| group | none | L48 | +0.0654 | +0.0652 | -0.0002 | [+0.059, +0.072] | [+0.059, +0.071] | no -> no |
| group | none | L52 | +0.0756 | +0.0755 | -0.0001 | [+0.069, +0.082] | [+0.068, +0.082] | no -> no |
| group | none | L56 | +0.0804 | +0.0790 | -0.0015 | [+0.075, +0.086] | [+0.072, +0.085] | no -> no |
| group | none | L60 | +0.0756 | +0.0756 | -0.0000 | [+0.069, +0.082] | [+0.069, +0.082] | no -> no |
| group | title-reuse | L16 | +0.0415 | +0.0415 | -0.0000 | [+0.028, +0.054] | [+0.028, +0.054] | no -> no |
| group | title-reuse | L24 | +0.0508 | +0.0504 | -0.0003 | [+0.039, +0.062] | [+0.037, +0.063] | no -> no |
| group | title-reuse | L32 | +0.0467 | +0.0467 | +0.0000 | [+0.033, +0.061] | [+0.034, +0.061] | no -> no |
| group | title-reuse | L40 | +0.0664 | +0.0609 | -0.0055 | [+0.053, +0.079] | [+0.047, +0.076] | no -> no |
| group | title-reuse | L44 | +0.0577 | +0.0581 | +0.0003 | [+0.043, +0.072] | [+0.044, +0.073] | no -> no |
| group | title-reuse | L48 | +0.0626 | +0.0619 | -0.0007 | [+0.047, +0.078] | [+0.046, +0.077] | no -> no |
| group | title-reuse | L52 | +0.0691 | +0.0692 | +0.0001 | [+0.053, +0.084] | [+0.054, +0.085] | no -> no |
| group | title-reuse | L56 | +0.0802 | +0.0753 | -0.0048 | [+0.067, +0.094] | [+0.060, +0.090] | no -> no |
| group | title-reuse | L60 | +0.0670 | +0.0672 | +0.0001 | [+0.053, +0.081] | [+0.053, +0.082] | no -> no |
| paper | none | L16 | +0.0407 | +0.0409 | +0.0002 | [+0.035, +0.046] | [+0.035, +0.046] | no -> no |
| paper | none | L24 | +0.0452 | +0.0441 | -0.0011 | [+0.040, +0.050] | [+0.038, +0.050] | no -> no |
| paper | none | L32 | +0.0501 | +0.0501 | -0.0000 | [+0.044, +0.056] | [+0.044, +0.056] | no -> no |
| paper | none | L40 | +0.0619 | +0.0605 | -0.0013 | [+0.056, +0.067] | [+0.054, +0.067] | no -> no |
| paper | none | L44 | +0.0572 | +0.0570 | -0.0002 | [+0.051, +0.063] | [+0.051, +0.063] | no -> no |
| paper | none | L48 | +0.0635 | +0.0637 | +0.0002 | [+0.057, +0.070] | [+0.057, +0.070] | no -> no |
| paper | none | L52 | +0.0752 | +0.0752 | -0.0000 | [+0.068, +0.082] | [+0.068, +0.082] | no -> no |
| paper | none | L56 | +0.0808 | +0.0777 | -0.0031 | [+0.075, +0.087] | [+0.071, +0.084] | no -> no |
| paper | none | L60 | +0.0734 | +0.0735 | +0.0000 | [+0.067, +0.080] | [+0.067, +0.080] | no -> no |
| paper | title-reuse | L16 | +0.0355 | +0.0359 | +0.0004 | [+0.024, +0.047] | [+0.024, +0.048] | no -> no |
| paper | title-reuse | L24 | +0.0426 | +0.0388 | -0.0037 | [+0.032, +0.053] | [+0.027, +0.051] | no -> no |
| paper | title-reuse | L32 | +0.0465 | +0.0464 | -0.0002 | [+0.034, +0.059] | [+0.034, +0.059] | no -> no |
| paper | title-reuse | L40 | +0.0630 | +0.0601 | -0.0029 | [+0.052, +0.075] | [+0.048, +0.072] | no -> no |
| paper | title-reuse | L44 | +0.0619 | +0.0613 | -0.0006 | [+0.049, +0.074] | [+0.049, +0.073] | no -> no |
| paper | title-reuse | L48 | +0.0625 | +0.0626 | +0.0001 | [+0.050, +0.077] | [+0.049, +0.077] | no -> no |
| paper | title-reuse | L52 | +0.0736 | +0.0736 | +0.0000 | [+0.060, +0.088] | [+0.060, +0.088] | no -> no |
| paper | title-reuse | L56 | +0.0838 | +0.0763 | -0.0075 | [+0.071, +0.096] | [+0.063, +0.090] | no -> no |
| paper | title-reuse | L60 | +0.0712 | +0.0714 | +0.0003 | [+0.058, +0.084] | [+0.058, +0.084] | no -> no |

## Per-paper agreement of the E4b spec (before exclusion): Pearson r and mean |new - orig|

split        excl  layer      r    mad      n
group        none     16 0.9986 0.0028 6841.0
group        none     24 0.9991 0.0026 6841.0
group        none     32 0.9989 0.0028 6841.0
group        none     40 0.9991 0.0030 6841.0
group        none     44 0.9988 0.0030 6841.0
group        none     48 0.9993 0.0029 6841.0
group        none     52 0.9990 0.0032 6841.0
group        none     56 0.9992 0.0032 6841.0
group        none     60 0.9987 0.0034 6841.0
group title-reuse     16 0.9986 0.0028 6841.0
group title-reuse     24 0.9991 0.0026 6841.0
group title-reuse     32 0.9989 0.0028 6841.0
group title-reuse     40 0.9991 0.0030 6841.0
group title-reuse     44 0.9988 0.0030 6841.0
group title-reuse     48 0.9993 0.0029 6841.0
group title-reuse     52 0.9990 0.0032 6841.0
group title-reuse     56 0.9992 0.0032 6841.0
group title-reuse     60 0.9987 0.0034 6841.0
paper        none     16 0.9990 0.0025 6841.0
paper        none     24 0.9987 0.0029 6841.0
paper        none     32 0.9987 0.0031 6841.0
paper        none     40 0.9991 0.0030 6841.0
paper        none     44 0.9993 0.0025 6841.0
paper        none     48 0.9994 0.0025 6841.0
paper        none     52 0.9993 0.0027 6841.0
paper        none     56 0.9992 0.0029 6841.0
paper        none     60 0.9989 0.0031 6841.0
paper title-reuse     16 0.9990 0.0025 6841.0
paper title-reuse     24 0.9987 0.0029 6841.0
paper title-reuse     32 0.9987 0.0031 6841.0
paper title-reuse     40 0.9991 0.0030 6841.0
paper title-reuse     44 0.9993 0.0025 6841.0
paper title-reuse     48 0.9994 0.0025 6841.0
paper title-reuse     52 0.9993 0.0027 6841.0
paper title-reuse     56 0.9992 0.0029 6841.0
paper title-reuse     60 0.9989 0.0031 6841.0

Full comparison tables: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_trainstd/compare_E4b.csv (also tc_R0, tc_R1, C - A, alpha), compare_E4b_allpapers.csv, compare_X1.csv.
