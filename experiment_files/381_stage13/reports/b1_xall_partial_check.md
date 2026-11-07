# Stage 13 batch 1 item 1: X1-X4 for all authors (addendum 10)  **PARTIAL (gate)**

Shards: ['shard_000']. Contexts: xpatch 117 (50 pairs), x2 117 (50 pairs), pscope 117 (50 pairs), para 112 (49 pairs).
Pair-level value = mean over the paper's authors (all name tokens per author, teacher-forced mean log10(1/rank) at L63). Strata: all (primary), first (published scoring), others (author index >= 1, mean), last (n_authors >= 3). Same pairs, layers, partner B, random C, lexical neighbour D, team-cluster bootstrap (2,000 draws, same seeds) as published. Teacher-forced preference, not generation (addendum 4).

## Hard check (frozen raw, same shards, same code; tolerance |diff| <= 0.005 on every point estimate): **PASS**

| item | against | value | cells | max abs diff | where / detail | CI ends max diff | ok |
|---|---|---|---|---|---|---|---|
| xpatch per-pair first-author scores | frozen raw | 30 score columns | 1500 | 0 | pairs new 50 / frozen 50 / common 50; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| x2 per-pair first-author scores | frozen raw | 72 score columns | 3600 | 0 | pairs new 50 / frozen 50 / common 50; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| pscope per-pair first-author scores | frozen raw | 29 score columns | 1450 | 0 | pairs new 50 / frozen 50 / common 50; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| para per-pair first-author scores | frozen raw | 4 score columns | 196 | 0 | pairs new 49 / frozen 49 / common 49; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| x1 | frozen raw, same shards, same code | R_authors | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | R_year | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | R_field | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | R_random_c | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | a_minus_year | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | a_minus_field | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x1 | frozen raw, same shards, same code | a_minus_random_c | 21 | 0 | {'split': 'test', 'layer': 4} | 0 | yes |
| x2_curves_old | frozen raw, same shards, same code | value | 240 | 0 | {'split': 'test', 'arm': 'carry', 'S': 'id', 'layer': 16} | 0 | yes |
| x3_recovery | frozen raw, same shards, same code | ratio | 40 | 0 | {'set': 'primary', 'subset': 'all', 'split': 'tune', 'false': 'lexical_neighbour_D', 'group': 'control'} | 0 | yes |
| x3_behaviour | frozen raw, same shards, same code | mean | 80 | 0 | {'set': 'primary', 'subset': 'all', 'split': 'tune', 'contrast': 'para_minus_lex'} | 0 | yes |
| x4_D | frozen raw, same shards, same code | D | 42 | 0 | {'split': 'tune', 'answer': 'author', 'pos': 'title', 'layer': 8} | 0 | yes |
| x4_recognition | frozen raw, same shards, same code | target_minus_control | 14 | 0 | {'answer': 'author', 'pos': 'title', 'layer': 8} | nan | yes |

## Pairs per stratum

| stratum | X1 | X2 | X3 (para) | X4 |
|---|---|---|---|---|
| all | 50 | 50 | 49 | 50 |
| first | 50 | 50 | 49 | 50 |
| others | 32 | 32 | 31 | 32 |
| last | 18 | 18 | 17 | 18 |

## X1: R (test, confirmatory) by stratum

| layer | all: R authors / R year / R field / R C / verdict | first: R authors / R year / R field / R C / verdict | others: R authors / R year / R field / R C / verdict | last: R authors / R year / R field / R C / verdict |
|---|---|---|---|---|
| L4 | +1.020 / +1.005 / +1.015 / +0.261 / text-replacement control (no conclusion) | +1.034 / +1.034 / +1.030 / +0.282 / text-replacement control (no conclusion) | +0.984 / +0.958 / +0.985 / +0.275 / text-replacement control (no conclusion) | +0.996 / +1.001 / +1.001 / +0.328 / text-replacement control (no conclusion) |
| L8 | +0.996 / +0.996 / +1.012 / +0.253 / text-replacement control (no conclusion) | +1.033 / +1.026 / +1.060 / +0.322 / text-replacement control (no conclusion) | +0.954 / +0.957 / +0.964 / +0.218 / text-replacement control (no conclusion) | +0.981 / +0.996 / +0.999 / +0.349 / text-replacement control (no conclusion) |
| L16 | +0.980 / +0.978 / +0.976 / +0.254 / text-replacement control (no conclusion) | +1.001 / +1.002 / +1.011 / +0.323 / text-replacement control (no conclusion) | +0.940 / +0.930 / +0.924 / +0.217 / text-replacement control (no conclusion) | +1.008 / +0.997 / +0.995 / +0.360 / text-replacement control (no conclusion) |
| L24 | +0.948 / +0.961 / +0.964 / +0.337 / task-independent | +0.963 / +0.978 / +0.988 / +0.417 / task-independent | +0.920 / +0.929 / +0.929 / +0.296 / task-independent | +1.019 / +1.008 / +1.024 / +0.414 / task-independent |
| L32 | +1.010 / +1.001 / +1.001 / +0.352 / task-independent | +1.021 / +1.003 / +1.022 / +0.437 / task-independent | +0.967 / +0.956 / +0.961 / +0.309 / task-independent | +1.014 / +1.016 / +1.013 / +0.415 / task-independent |
| L40 | +0.906 / +0.887 / +0.903 / +0.406 / task-independent | +0.976 / +0.933 / +0.959 / +0.493 / task-independent | +0.850 / +0.848 / +0.871 / +0.322 / task-independent | +0.904 / +0.864 / +0.918 / +0.455 / task-independent |
| L48 | +0.513 / +0.473 / +0.513 / +0.398 / task-independent | +0.579 / +0.511 / +0.548 / +0.529 / undecided | +0.517 / +0.503 / +0.546 / +0.289 / task-independent | +0.522 / +0.483 / +0.526 / +0.328 / task-independent |

authors - year on test with CI (task-independence rule: both differences inside [-0.1, 0.1] and authors - C > 0):

| layer | all | first | others | last |
|---|---|---|---|---|
| L4 | +0.014 [-0.003, +0.036] | +0.000 [-0.025, +0.026] | +0.026 [+0.002, +0.052] | -0.005 [-0.019, +0.004] |
| L8 | -0.000 [-0.022, +0.021] | +0.007 [-0.019, +0.035] | -0.003 [-0.024, +0.024] | -0.015 [-0.036, -0.001] |
| L16 | +0.002 [-0.026, +0.026] | -0.001 [-0.043, +0.033] | +0.010 [-0.017, +0.034] | +0.010 [-0.010, +0.031] |
| L24 | -0.013 [-0.058, +0.023] | -0.015 [-0.089, +0.033] | -0.010 [-0.034, +0.018] | +0.011 [-0.030, +0.058] |
| L32 | +0.009 [-0.025, +0.038] | +0.018 [-0.027, +0.062] | +0.011 [-0.027, +0.041] | -0.003 [-0.088, +0.050] |
| L40 | +0.019 [-0.022, +0.059] | +0.042 [+0.003, +0.091] | +0.002 [-0.059, +0.048] | +0.040 [-0.003, +0.081] |
| L48 | +0.041 [+0.008, +0.087] | +0.068 [+0.024, +0.149] | +0.014 [-0.024, +0.055] | +0.038 [+0.012, +0.072] |

## X2: verdict (addendum 6 rule) by stratum and S_auth version

| stratum | S_auth | verdict | S_id layer | test R_id - R_rand | S_auth layer | test R_auth | test R_rand | test R_full | test R_auth - R_rand | test R_auth - R_id | H2 | H3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | old | no pre-registered support for H2 or H3 | L48 | -0.002 [-0.014, +0.010] | L48 | +0.029 | +0.009 | +0.519 | +0.020 [-0.009, +0.049] | +0.022 [-0.005, +0.050] | False | False |
| all | new | no pre-registered support for H2 or H3 | L48 | -0.002 [-0.014, +0.010] | L48 | +0.043 | +0.009 | +0.519 | +0.033 [-0.000, +0.067] | +0.035 [+0.005, +0.068] | False | False |
| first | old | no pre-registered support for H2 or H3 | L48 | -0.001 [-0.021, +0.018] | L48 | +0.042 | +0.017 | +0.574 | +0.025 [-0.015, +0.066] | +0.026 [-0.018, +0.073] | False | False |
| first | new | no pre-registered support for H2 or H3 | L48 | -0.001 [-0.021, +0.018] | L48 | +0.048 | +0.017 | +0.574 | +0.031 [-0.008, +0.072] | +0.033 [-0.010, +0.077] | False | False |
| others | old | H3 supported (S_auth carries more than S_id) | L32 | +0.019 [-0.002, +0.044] | L48 | +0.027 | +0.001 | +0.529 | +0.026 [+0.006, +0.047] | +0.027 [+0.005, +0.059] | False | True |
| others | new | H3 supported (S_auth carries more than S_id) | L32 | +0.019 [-0.002, +0.044] | L48 | +0.039 | +0.001 | +0.529 | +0.038 [+0.011, +0.068] | +0.039 [+0.010, +0.077] | False | True |
| last | old | H3 supported (S_auth carries more than S_id) | L16 | -0.006 [-0.020, +0.006] | L48 | +0.036 | -0.001 | +0.519 | +0.038 [+0.012, +0.079] | +0.033 [+0.006, +0.073] | False | True |
| last | new | H3 supported (S_auth carries more than S_id) | L16 | -0.006 [-0.020, +0.006] | L48 | +0.044 | -0.001 | +0.519 | +0.046 [+0.021, +0.078] | +0.041 [+0.016, +0.071] | False | True |

Table X2.1 analogue (test, carry): R per layer

| stratum | S_auth | layer | R_id | R_auth | R_rand | R_full |
|---|---|---|---|---|---|---|
| all | old | L16 | +0.023 [+0.007, +0.045] | +0.031 [+0.006, +0.069] | +0.009 [-0.001, +0.023] | +0.987 [+0.952, +1.032] |
| all | old | L24 | +0.024 [+0.007, +0.046] | +0.013 [-0.008, +0.035] | +0.005 [-0.007, +0.016] | +0.950 [+0.889, +1.018] |
| all | old | L32 | +0.036 [+0.007, +0.077] | -0.001 [-0.026, +0.023] | +0.011 [-0.000, +0.028] | +1.018 [+0.940, +1.133] |
| all | old | L40 | +0.018 [-0.000, +0.040] | +0.021 [-0.010, +0.054] | +0.010 [+0.001, +0.025] | +0.912 [+0.793, +1.056] |
| all | old | L48 | +0.007 [-0.007, +0.026] | +0.029 [+0.001, +0.062] | +0.009 [+0.001, +0.021] | +0.519 [+0.399, +0.671] |
| all | new | L16 | +0.023 [+0.007, +0.045] | +0.026 [-0.004, +0.063] | +0.009 [-0.001, +0.023] | +0.987 [+0.952, +1.032] |
| all | new | L24 | +0.024 [+0.007, +0.046] | +0.025 [+0.008, +0.043] | +0.005 [-0.007, +0.016] | +0.950 [+0.889, +1.018] |
| all | new | L32 | +0.036 [+0.007, +0.077] | +0.015 [+0.002, +0.029] | +0.011 [-0.000, +0.028] | +1.018 [+0.940, +1.133] |
| all | new | L40 | +0.018 [-0.000, +0.040] | +0.046 [+0.008, +0.084] | +0.010 [+0.001, +0.025] | +0.912 [+0.793, +1.056] |
| all | new | L48 | +0.007 [-0.007, +0.026] | +0.043 [+0.011, +0.077] | +0.009 [+0.001, +0.021] | +0.519 [+0.399, +0.671] |
| first | old | L16 | +0.038 [+0.011, +0.089] | +0.049 [+0.015, +0.114] | +0.019 [+0.005, +0.049] | +1.021 [+0.958, +1.119] |
| first | old | L24 | +0.029 [+0.002, +0.074] | +0.023 [-0.008, +0.065] | +0.016 [+0.001, +0.041] | +0.964 [+0.882, +1.059] |
| first | old | L32 | +0.060 [+0.012, +0.159] | +0.007 [-0.026, +0.048] | +0.025 [+0.008, +0.059] | +1.041 [+0.938, +1.202] |
| first | old | L40 | +0.020 [-0.005, +0.058] | +0.031 [-0.008, +0.096] | +0.018 [+0.006, +0.043] | +0.980 [+0.829, +1.168] |
| first | old | L48 | +0.016 [-0.004, +0.046] | +0.042 [+0.005, +0.090] | +0.017 [+0.006, +0.041] | +0.574 [+0.409, +0.827] |
| first | new | L16 | +0.038 [+0.011, +0.089] | +0.034 [-0.004, +0.092] | +0.019 [+0.005, +0.049] | +1.021 [+0.958, +1.119] |
| first | new | L24 | +0.029 [+0.002, +0.074] | +0.041 [+0.013, +0.086] | +0.016 [+0.001, +0.041] | +0.964 [+0.882, +1.059] |
| first | new | L32 | +0.060 [+0.012, +0.159] | +0.028 [+0.009, +0.065] | +0.025 [+0.008, +0.059] | +1.041 [+0.938, +1.202] |
| first | new | L40 | +0.020 [-0.005, +0.058] | +0.056 [+0.011, +0.127] | +0.018 [+0.006, +0.043] | +0.980 [+0.829, +1.168] |
| first | new | L48 | +0.016 [-0.004, +0.046] | +0.048 [+0.013, +0.095] | +0.017 [+0.006, +0.041] | +0.574 [+0.409, +0.827] |
| others | old | L16 | +0.009 [-0.006, +0.027] | +0.008 [-0.017, +0.030] | -0.004 [-0.016, +0.007] | +0.940 [+0.868, +1.004] |
| others | old | L24 | +0.017 [-0.001, +0.041] | +0.018 [+0.001, +0.036] | -0.001 [-0.017, +0.012] | +0.929 [+0.827, +1.016] |
| others | old | L32 | +0.014 [-0.004, +0.038] | +0.005 [-0.012, +0.024] | -0.005 [-0.021, +0.011] | +0.964 [+0.877, +1.045] |
| others | old | L40 | +0.018 [+0.003, +0.035] | +0.022 [+0.000, +0.049] | +0.000 [-0.012, +0.012] | +0.854 [+0.715, +0.993] |
| others | old | L48 | -0.000 [-0.027, +0.018] | +0.027 [+0.003, +0.052] | +0.001 [-0.011, +0.012] | +0.529 [+0.398, +0.710] |
| others | new | L16 | +0.009 [-0.006, +0.027] | +0.015 [-0.010, +0.036] | -0.004 [-0.016, +0.007] | +0.940 [+0.868, +1.004] |
| others | new | L24 | +0.017 [-0.001, +0.041] | +0.014 [-0.007, +0.031] | -0.001 [-0.017, +0.012] | +0.929 [+0.827, +1.016] |
| others | new | L32 | +0.014 [-0.004, +0.038] | +0.001 [-0.018, +0.018] | -0.005 [-0.021, +0.011] | +0.964 [+0.877, +1.045] |
| others | new | L40 | +0.018 [+0.003, +0.035] | +0.044 [+0.022, +0.067] | +0.000 [-0.012, +0.012] | +0.854 [+0.715, +0.993] |
| others | new | L48 | -0.000 [-0.027, +0.018] | +0.039 [+0.012, +0.071] | +0.001 [-0.011, +0.012] | +0.529 [+0.398, +0.710] |
| last | old | L16 | -0.006 [-0.020, +0.012] | +0.016 [-0.018, +0.051] | +0.000 [-0.016, +0.022] | +0.994 [+0.963, +1.018] |
| last | old | L24 | +0.005 [-0.022, +0.035] | +0.008 [-0.020, +0.037] | +0.003 [-0.008, +0.020] | +1.030 [+0.958, +1.108] |
| last | old | L32 | -0.005 [-0.023, +0.014] | +0.009 [-0.016, +0.031] | -0.007 [-0.024, +0.009] | +1.015 [+0.941, +1.084] |
| last | old | L40 | +0.026 [+0.007, +0.051] | +0.020 [-0.005, +0.060] | -0.001 [-0.015, +0.013] | +0.905 [+0.819, +1.006] |
| last | old | L48 | +0.003 [-0.015, +0.018] | +0.036 [+0.006, +0.080] | -0.001 [-0.019, +0.014] | +0.519 [+0.402, +0.724] |
| last | new | L16 | -0.006 [-0.020, +0.012] | +0.025 [-0.007, +0.060] | +0.000 [-0.016, +0.022] | +0.994 [+0.963, +1.018] |
| last | new | L24 | +0.005 [-0.022, +0.035] | +0.017 [-0.023, +0.054] | +0.003 [-0.008, +0.020] | +1.030 [+0.958, +1.108] |
| last | new | L32 | -0.005 [-0.023, +0.014] | +0.014 [-0.014, +0.041] | -0.007 [-0.024, +0.009] | +1.015 [+0.941, +1.084] |
| last | new | L40 | +0.026 [+0.007, +0.051] | +0.055 [+0.025, +0.111] | -0.001 [-0.015, +0.013] | +0.905 [+0.819, +1.006] |
| last | new | L48 | +0.003 [-0.015, +0.018] | +0.044 [+0.012, +0.082] | -0.001 [-0.019, +0.014] | +0.519 [+0.402, +0.724] |

## X3 behaviour: recovery (paraphrase - D) / (original - D), primary set, all subset

| stratum | split | group | n | ratio [CI] | para - D [CI] |
|---|---|---|---|---|---|
| all | test | all | 32 | +0.815 [+0.641, +0.965] | +0.137 [+0.068, +0.212] |
| all | test | control | 32 | +0.815 [+0.641, +0.965] |  |
| all | all | all | 48 | +0.807 [+0.636, +0.970] | +0.127 [+0.067, +0.184] |
| all | all | control | 48 | +0.807 [+0.636, +0.970] |  |
| first | test | all | 32 | +0.921 [+0.747, +1.175] | +0.171 [+0.084, +0.269] |
| first | test | control | 32 | +0.921 [+0.747, +1.175] |  |
| first | all | all | 48 | +0.855 [+0.653, +1.062] | +0.138 [+0.065, +0.213] |
| first | all | control | 48 | +0.855 [+0.653, +1.062] |  |
| others | test | all | 22 | +0.770 [+0.590, +0.975] | +0.156 [+0.079, +0.237] |
| others | test | control | 22 | +0.770 [+0.590, +0.975] |  |
| others | all | all | 31 | +0.793 [+0.642, +0.933] | +0.172 [+0.105, +0.237] |
| others | all | control | 31 | +0.793 [+0.642, +0.933] |  |
| last | test | all | 11 | +0.832 [+0.696, +0.928] | +0.285 [+0.111, +0.445] |
| last | test | control | 11 | +0.832 [+0.696, +0.928] |  |
| last | all | all | 17 | +0.826 [+0.688, +0.933] | +0.259 [+0.147, +0.376] |
| last | all | control | 17 | +0.826 [+0.688, +0.933] |  |

## X4 author answer: D = self - partner (test) by stratum

### title

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | +0.013 [-0.026, +0.050] | +0.013 [-0.033, +0.055] | -0.008 [-0.036, +0.020] | -0.021 [-0.075, +0.036] |
| L16 | +0.024 [-0.006, +0.053] | +0.014 [-0.023, +0.049] | +0.009 [-0.013, +0.031] | +0.009 [-0.043, +0.068] |
| L24 | +0.011 [-0.009, +0.031] | -0.011 [-0.040, +0.017] | +0.019 [-0.008, +0.045] | +0.017 [-0.039, +0.074] |
| L32 | +0.013 [-0.009, +0.033] | -0.010 [-0.036, +0.015] | +0.026 [-0.000, +0.052] | +0.017 [-0.029, +0.065] |
| L40 | +0.016 [-0.002, +0.034] | +0.003 [-0.021, +0.026] | +0.027 [-0.001, +0.055] | +0.009 [-0.031, +0.054] |
| L48 | +0.015 [+0.003, +0.028] | +0.005 [-0.009, +0.020] | +0.031 [+0.017, +0.048] | +0.013 [-0.002, +0.031] |
| L56 | +0.000 [-0.002, +0.002] | -0.000 [-0.003, +0.003] | -0.000 [-0.003, +0.002] | +0.002 [-0.005, +0.011] |

### colon

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | +0.002 [-0.002, +0.007] | +0.008 [+0.000, +0.016] | -0.001 [-0.006, +0.004] | +0.009 [-0.003, +0.023] |
| L16 | +0.000 [-0.009, +0.009] | -0.003 [-0.018, +0.011] | +0.001 [-0.007, +0.012] | -0.016 [-0.033, -0.003] |
| L24 | +0.000 [-0.005, +0.005] | -0.001 [-0.008, +0.006] | +0.002 [-0.004, +0.007] | -0.005 [-0.019, +0.007] |
| L32 | -0.000 [-0.005, +0.004] | -0.004 [-0.015, +0.005] | +0.002 [-0.005, +0.009] | -0.004 [-0.026, +0.015] |
| L40 | -0.002 [-0.008, +0.004] | -0.007 [-0.016, +0.001] | -0.000 [-0.011, +0.010] | -0.001 [-0.010, +0.011] |
| L48 | +0.009 [+0.000, +0.019] | +0.006 [-0.005, +0.017] | +0.009 [-0.003, +0.019] | +0.010 [-0.001, +0.023] |
| L56 | +0.008 [+0.003, +0.013] | +0.013 [+0.004, +0.023] | +0.007 [-0.003, +0.017] | +0.011 [+0.001, +0.018] |

Earliest layer with D > 0 on tune, confirmed on test:

| stratum | title | colon |
|---|---|---|
| all | L48 (confirmed, test +0.015 [+0.003, +0.028]) | L56 (confirmed, test +0.008 [+0.003, +0.013]) |
| first | none | none |
| others | none | L16 (not confirmed, test +0.001 [-0.007, +0.012]) |
| last | L56 (not confirmed, test +0.002 [-0.005, +0.011]) | L16 (not confirmed, test -0.016 [-0.033, -0.003]) |

Recognition (target - control of self - partner within citation bin, all pairs), title position:

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L16 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L24 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L32 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L40 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L48 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |
| L56 | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] | +nan [+nan, +nan] |

Note: the X4 target prompt asks for "the first author" (frozen design); for the other strata the score is the model's preference for that author's name under the same prompt.

## New S_auth (all authors' tokens) fit

```
 layer  n_train  alpha_auth  authall_r2  cos_old_max  cos_old_mean  cos_id_max  sv_top10_share  capture_auth_all  capture_auth_old
    16     5041       100.0    0.004115     0.818027      0.504878    0.411355        0.360339          0.013393          0.009679
    24     5041       100.0    0.005325     0.831243      0.516271    0.404269        0.388170          0.012967          0.011034
    32     5041       100.0    0.004644     0.809942      0.501920    0.410117        0.355750          0.010387          0.008678
    40     5041       100.0    0.006493     0.838470      0.531520    0.395885        0.391305          0.010112          0.007744
    48     5041       100.0    0.009177     0.876722      0.545666    0.355864        0.460822          0.012848          0.009587
```

## WARN

- primary/all/tune/lexical_neighbour_D/control: denominator <= 0 in 3.0% of draws (CI unreliable)
- primary/all/tune/lexical_neighbour_D/all: denominator <= 0 in 3.0% of draws (CI unreliable)
- primary/all/tune/partner_B/control: denominator <= 0 in 0.1% of draws (CI unreliable)
- primary/all/tune/partner_B/all: denominator <= 0 in 0.1% of draws (CI unreliable)
- primary/d_matched/test/lexical_neighbour_D/control: denominator <= 0 in 40.2% of draws (CI unreliable)
- primary/d_matched/test/lexical_neighbour_D/all: denominator <= 0 in 40.2% of draws (CI unreliable)
- primary/d_matched/test/partner_B/control: denominator <= 0 in 0.4% of draws (CI unreliable)
- primary/d_matched/test/partner_B/all: denominator <= 0 in 0.4% of draws (CI unreliable)
- primary/d_matched/all/lexical_neighbour_D/control: denominator <= 0 in 59.5% of draws (CI unreliable)
- primary/d_matched/all/lexical_neighbour_D/all: denominator <= 0 in 59.5% of draws (CI unreliable)
- primary/d_matched/all/partner_B/control: denominator <= 0 in 0.1% of draws (CI unreliable)
- primary/d_matched/all/partner_B/all: denominator <= 0 in 0.1% of draws (CI unreliable)
- sensitivity/all/tune/lexical_neighbour_D/control: denominator <= 0 in 2.4% of draws (CI unreliable)
- sensitivity/all/tune/lexical_neighbour_D/all: denominator <= 0 in 2.4% of draws (CI unreliable)
- sensitivity/all/test/lexical_neighbour_D/control: denominator <= 0 in 0.1% of draws (CI unreliable)
- sensitivity/all/test/lexical_neighbour_D/all: denominator <= 0 in 0.1% of draws (CI unreliable)
- sensitivity/d_matched/test/lexical_neighbour_D/control: denominator <= 0 in 85.5% of draws (CI unreliable)
- sensitivity/d_matched/test/lexical_neighbour_D/all: denominator <= 0 in 85.5% of draws (CI unreliable)
- sensitivity/d_matched/test/partner_B/control: denominator <= 0 in 4.0% of draws (CI unreliable)
- sensitivity/d_matched/test/partner_B/all: denominator <= 0 in 4.0% of draws (CI unreliable)
- sensitivity/d_matched/all/lexical_neighbour_D/control: denominator <= 0 in 98.2% of draws (CI unreliable)
- sensitivity/d_matched/all/lexical_neighbour_D/all: denominator <= 0 in 98.2% of draws (CI unreliable)
- sensitivity/d_matched/all/partner_B/control: denominator <= 0 in 0.4% of draws (CI unreliable)
- sensitivity/d_matched/all/partner_B/all: denominator <= 0 in 0.4% of draws (CI unreliable)

