# Stage 13 batch 1 item 1: X1-X4 for all authors (addendum 10)

Shards: ['shard_000', 'shard_001', 'shard_002', 'shard_003', 'shard_004', 'shard_005', 'shard_006', 'shard_007', 'shard_008', 'shard_009', 'shard_010', 'shard_011', 'shard_012', 'shard_013', 'shard_014', 'shard_015', 'shard_016', 'shard_017', 'shard_018', 'shard_019', 'shard_020', 'shard_021', 'shard_022', 'shard_023']. Contexts: xpatch 4271 (1178 pairs), x2 4271 (1178 pairs), pscope 4271 (1178 pairs), para 4039 (1137 pairs).
Pair-level value = mean over the paper's authors (all name tokens per author, teacher-forced mean log10(1/rank) at L63). Strata: all (primary), first (published scoring), others (author index >= 1, mean), last (n_authors >= 3). Same pairs, layers, partner B, random C, lexical neighbour D, team-cluster bootstrap (2,000 draws, same seeds) as published. Teacher-forced preference, not generation (addendum 4).

## Hard check (published; tolerance |diff| <= 0.005 on every point estimate): **PASS**

| item | against | value | cells | max abs diff | where / detail | CI ends max diff | ok |
|---|---|---|---|---|---|---|---|
| xpatch per-pair first-author scores | frozen raw | 30 score columns | 35340 | 0 | pairs new 1178 / frozen 1178 / common 1178; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| x2 per-pair first-author scores | frozen raw | 72 score columns | 84816 | 0 | pairs new 1178 / frozen 1178 / common 1178; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| pscope per-pair first-author scores | frozen raw | 29 score columns | 34162 | 0 | pairs new 1178 / frozen 1178 / common 1178; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| para per-pair first-author scores | frozen raw | 4 score columns | 4548 | 0 | pairs new 1137 / frozen 1137 / common 1137; exact share 1.000; mean |diff| 0.00e+00 | nan | yes |
| x1 (frozen raw, this code) | published | R_authors | 21 | 1.1e-16 | {'split': 'test', 'layer': 40} | 2.2e-16 | yes |
| x1 (frozen raw, this code) | published | R_year | 21 | 2.2e-16 | {'split': 'all', 'layer': 8} | 2.2e-16 | yes |
| x1 (frozen raw, this code) | published | R_field | 21 | 1.1e-16 | {'split': 'test', 'layer': 24} | 2.2e-16 | yes |
| x1 (frozen raw, this code) | published | R_random_c | 21 | 9.5e-17 | {'split': 'all', 'layer': 40} | 9.7e-17 | yes |
| x1 (frozen raw, this code) | published | a_minus_year | 21 | 9.4e-17 | {'split': 'test', 'layer': 32} | 9.9e-17 | yes |
| x1 (frozen raw, this code) | published | a_minus_field | 21 | 9.9e-17 | {'split': 'test', 'layer': 16} | 1e-16 | yes |
| x1 (frozen raw, this code) | published | a_minus_random_c | 21 | 2.2e-16 | {'split': 'test', 'layer': 24} | 2.2e-16 | yes |
| x2_curves_old (frozen raw, this code) | published | value | 20 | 1.1e-16 | {'split': 'test', 'arm': 'carry', 'S': 'full', 'layer': 40} | 1.1e-16 | yes |
| x3_recovery (frozen raw, this code) | published | ratio | 96 | 1.2e-15 | {'set': 'sensitivity', 'subset': 'd_matched', 'split': 'all', 'false': 'lexical_neighbour_D', 'group': 'target_minus_control'} | 3.1e-15 | yes |
| x3_behaviour (frozen raw, this code) | published | mean | 90 | 8.7e-17 | {'set': 'primary', 'subset': 'd_unmatched', 'split': 'test', 'contrast': 'orig_minus_para'} | 9.7e-17 | yes |
| x4_D (frozen raw, this code) | published | D | 42 | 9.4e-17 | {'split': 'all', 'answer': 'author', 'pos': 'title', 'layer': 48} | 9.5e-17 | yes |
| x4_recognition (frozen raw, this code) | published | target_minus_control | 14 | 9.7e-17 | {'answer': 'author', 'pos': 'title', 'layer': 56} | 9.9e-17 | yes |
| x2 verdict | published | id_layer | 1 | 0 | new 40 vs published 40 | nan | yes |
| x2 verdict | published | auth_layer | 1 | 0 | new 48 vs published 48 | nan | yes |
| x2 verdict | published | H2 | 1 | 0 | new False vs published False | nan | yes |
| x2 verdict | published | H3 | 1 | 0 | new True vs published True | nan | yes |
| x4 earliest author layer | published | title | 1 | nan | new 8 / confirmed True vs published 8.0 / True | nan | yes |
| x4 earliest author layer | published | colon | 1 | nan | new 24 / confirmed False vs published 24.0 / False | nan | yes |
| x1 | published | R_authors | 21 | 1.1e-16 | {'split': 'test', 'layer': 40} | 2.2e-16 | yes |
| x1 | published | R_year | 21 | 2.2e-16 | {'split': 'all', 'layer': 8} | 2.2e-16 | yes |
| x1 | published | R_field | 21 | 1.1e-16 | {'split': 'test', 'layer': 24} | 2.2e-16 | yes |
| x1 | published | R_random_c | 21 | 9.5e-17 | {'split': 'all', 'layer': 40} | 9.7e-17 | yes |
| x1 | published | a_minus_year | 21 | 9.4e-17 | {'split': 'test', 'layer': 32} | 9.9e-17 | yes |
| x1 | published | a_minus_field | 21 | 9.9e-17 | {'split': 'test', 'layer': 16} | 1e-16 | yes |
| x1 | published | a_minus_random_c | 21 | 2.2e-16 | {'split': 'test', 'layer': 24} | 2.2e-16 | yes |
| x2_curves_old | published | value | 20 | 1.1e-16 | {'split': 'test', 'arm': 'carry', 'S': 'full', 'layer': 40} | 1.1e-16 | yes |
| x3_recovery | published | ratio | 96 | 1.2e-15 | {'set': 'sensitivity', 'subset': 'd_matched', 'split': 'all', 'false': 'lexical_neighbour_D', 'group': 'target_minus_control'} | 3.1e-15 | yes |
| x3_behaviour | published | mean | 90 | 8.7e-17 | {'set': 'primary', 'subset': 'd_unmatched', 'split': 'test', 'contrast': 'orig_minus_para'} | 9.7e-17 | yes |
| x4_D | published | D | 42 | 9.4e-17 | {'split': 'all', 'answer': 'author', 'pos': 'title', 'layer': 48} | 9.5e-17 | yes |
| x4_recognition | published | target_minus_control | 14 | 9.7e-17 | {'answer': 'author', 'pos': 'title', 'layer': 56} | 9.9e-17 | yes |

## Pairs per stratum

| stratum | X1 | X2 | X3 (para) | X4 |
|---|---|---|---|---|
| all | 1178 | 1178 | 1137 | 1178 |
| first | 1178 | 1178 | 1137 | 1178 |
| others | 970 | 970 | 932 | 970 |
| last | 681 | 681 | 646 | 681 |

## X1: R (test, confirmatory) by stratum

| layer | all: R authors / R year / R field / R C / verdict | first: R authors / R year / R field / R C / verdict | others: R authors / R year / R field / R C / verdict | last: R authors / R year / R field / R C / verdict |
|---|---|---|---|---|
| L4 | +1.004 / +1.003 / +1.005 / -0.161 / text-replacement control (no conclusion) | +1.004 / +1.003 / +1.006 / -0.149 / text-replacement control (no conclusion) | +1.002 / +1.002 / +1.004 / -0.135 / text-replacement control (no conclusion) | +0.997 / +0.998 / +0.998 / -0.104 / text-replacement control (no conclusion) |
| L8 | +1.002 / +1.003 / +1.002 / -0.155 / text-replacement control (no conclusion) | +1.004 / +1.004 / +1.003 / -0.139 / text-replacement control (no conclusion) | +1.002 / +1.004 / +1.002 / -0.133 / text-replacement control (no conclusion) | +0.998 / +1.005 / +1.002 / -0.090 / text-replacement control (no conclusion) |
| L16 | +1.002 / +0.999 / +0.999 / -0.146 / text-replacement control (no conclusion) | +1.001 / +0.997 / +0.997 / -0.132 / text-replacement control (no conclusion) | +1.001 / +0.999 / +0.998 / -0.125 / text-replacement control (no conclusion) | +0.998 / +1.001 / +0.997 / -0.083 / text-replacement control (no conclusion) |
| L24 | +0.996 / +0.990 / +0.992 / -0.111 / task-independent | +0.991 / +0.985 / +0.992 / -0.097 / task-independent | +0.996 / +0.993 / +0.993 / -0.094 / task-independent | +0.995 / +0.994 / +0.994 / -0.060 / task-independent |
| L32 | +0.981 / +0.971 / +0.978 / -0.077 / task-independent | +0.971 / +0.966 / +0.969 / -0.065 / task-independent | +0.992 / +0.982 / +0.988 / -0.061 / task-independent | +0.987 / +0.982 / +0.982 / -0.033 / task-independent |
| L40 | +0.933 / +0.928 / +0.929 / -0.011 / task-independent | +0.921 / +0.917 / +0.915 / -0.007 / task-independent | +0.946 / +0.940 / +0.943 / +0.000 / task-independent | +0.932 / +0.934 / +0.934 / +0.031 / task-independent |
| L48 | +0.455 / +0.431 / +0.444 / +0.145 / task-independent | +0.424 / +0.405 / +0.417 / +0.122 / task-independent | +0.472 / +0.449 / +0.462 / +0.156 / task-independent | +0.455 / +0.432 / +0.444 / +0.185 / task-independent |

authors - year on test with CI (task-independence rule: both differences inside [-0.1, 0.1] and authors - C > 0):

| layer | all | first | others | last |
|---|---|---|---|---|
| L4 | +0.001 [-0.002, +0.004] | +0.001 [-0.005, +0.007] | -0.000 [-0.004, +0.003] | -0.001 [-0.007, +0.005] |
| L8 | -0.001 [-0.005, +0.003] | -0.000 [-0.006, +0.006] | -0.002 [-0.007, +0.003] | -0.008 [-0.015, -0.001] |
| L16 | +0.003 [-0.002, +0.008] | +0.004 [-0.003, +0.012] | +0.002 [-0.004, +0.008] | -0.003 [-0.010, +0.004] |
| L24 | +0.006 [-0.001, +0.013] | +0.006 [-0.004, +0.015] | +0.003 [-0.003, +0.009] | +0.001 [-0.009, +0.011] |
| L32 | +0.009 [+0.002, +0.017] | +0.005 [-0.006, +0.016] | +0.010 [+0.002, +0.018] | +0.005 [-0.006, +0.015] |
| L40 | +0.005 [-0.003, +0.012] | +0.003 [-0.008, +0.014] | +0.006 [-0.003, +0.014] | -0.002 [-0.015, +0.011] |
| L48 | +0.024 [+0.019, +0.030] | +0.019 [+0.012, +0.026] | +0.023 [+0.016, +0.031] | +0.023 [+0.013, +0.033] |

## X2: verdict (addendum 6 rule) by stratum and S_auth version

| stratum | S_auth | verdict | S_id layer | test R_id - R_rand | S_auth layer | test R_auth | test R_rand | test R_full | test R_auth - R_rand | test R_auth - R_id | H2 | H3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | old | H3 supported (S_auth carries more than S_id) | L40 | +0.003 [+0.000, +0.005] | L48 | +0.016 | +0.001 | +0.457 | +0.015 [+0.011, +0.019] | +0.013 [+0.008, +0.018] | False | True |
| all | new | H3 supported (S_auth carries more than S_id) | L40 | +0.003 [+0.000, +0.005] | L48 | +0.032 | +0.001 | +0.457 | +0.032 [+0.025, +0.038] | +0.030 [+0.023, +0.036] | False | True |
| first | old | H3 supported (S_auth carries more than S_id) | L40 | +0.002 [-0.001, +0.005] | L48 | +0.018 | +0.003 | +0.428 | +0.015 [+0.010, +0.020] | +0.014 [+0.008, +0.020] | False | True |
| first | new | H3 supported (S_auth carries more than S_id) | L40 | +0.002 [-0.001, +0.005] | L48 | +0.034 | +0.003 | +0.428 | +0.031 [+0.023, +0.039] | +0.031 [+0.023, +0.039] | False | True |
| others | old | H3 supported (S_auth carries more than S_id) | L48 | +0.002 [-0.000, +0.006] | L48 | +0.016 | -0.000 | +0.474 | +0.017 [+0.012, +0.022] | +0.014 [+0.009, +0.020] | False | True |
| others | new | H3 supported (S_auth carries more than S_id) | L48 | +0.002 [-0.000, +0.006] | L48 | +0.033 | -0.000 | +0.474 | +0.033 [+0.026, +0.042] | +0.031 [+0.023, +0.039] | False | True |
| last | old | H3 supported (S_auth carries more than S_id) | L32 | +0.001 [-0.005, +0.006] | L48 | +0.015 | +0.000 | +0.453 | +0.015 [+0.009, +0.022] | +0.013 [+0.006, +0.020] | False | True |
| last | new | H3 supported (S_auth carries more than S_id) | L32 | +0.001 [-0.005, +0.006] | L48 | +0.035 | +0.000 | +0.453 | +0.034 [+0.025, +0.045] | +0.032 [+0.022, +0.043] | False | True |

Table X2.1 analogue (test, carry): R per layer

| stratum | S_auth | layer | R_id | R_auth | R_rand | R_full |
|---|---|---|---|---|---|---|
| all | old | L16 | +0.001 [-0.002, +0.004] | +0.002 [-0.001, +0.005] | +0.001 [-0.001, +0.003] | +1.001 [+0.995, +1.008] |
| all | old | L24 | +0.002 [-0.001, +0.005] | +0.001 [-0.003, +0.004] | -0.000 [-0.003, +0.002] | +0.997 [+0.988, +1.007] |
| all | old | L32 | +0.002 [-0.002, +0.006] | +0.001 [-0.003, +0.005] | +0.001 [-0.001, +0.003] | +0.981 [+0.968, +0.993] |
| all | old | L40 | +0.004 [+0.001, +0.007] | +0.013 [+0.009, +0.017] | +0.002 [-0.001, +0.004] | +0.932 [+0.914, +0.950] |
| all | old | L48 | +0.003 [+0.000, +0.005] | +0.016 [+0.011, +0.020] | +0.001 [-0.002, +0.003] | +0.457 [+0.430, +0.485] |
| all | new | L16 | +0.001 [-0.002, +0.004] | +0.001 [-0.003, +0.005] | +0.001 [-0.001, +0.003] | +1.001 [+0.995, +1.008] |
| all | new | L24 | +0.002 [-0.001, +0.005] | +0.006 [+0.002, +0.010] | -0.000 [-0.003, +0.002] | +0.997 [+0.988, +1.007] |
| all | new | L32 | +0.002 [-0.002, +0.006] | +0.005 [+0.001, +0.009] | +0.001 [-0.001, +0.003] | +0.981 [+0.968, +0.993] |
| all | new | L40 | +0.004 [+0.001, +0.007] | +0.030 [+0.024, +0.036] | +0.002 [-0.001, +0.004] | +0.932 [+0.914, +0.950] |
| all | new | L48 | +0.003 [+0.000, +0.005] | +0.032 [+0.026, +0.039] | +0.001 [-0.002, +0.003] | +0.457 [+0.430, +0.485] |
| first | old | L16 | +0.003 [-0.000, +0.007] | +0.003 [-0.001, +0.007] | +0.002 [-0.001, +0.004] | +1.000 [+0.989, +1.010] |
| first | old | L24 | +0.002 [-0.001, +0.006] | +0.002 [-0.002, +0.007] | +0.002 [-0.001, +0.005] | +0.992 [+0.978, +1.005] |
| first | old | L32 | +0.005 [-0.000, +0.010] | +0.002 [-0.002, +0.007] | +0.002 [-0.001, +0.005] | +0.971 [+0.954, +0.988] |
| first | old | L40 | +0.005 [+0.001, +0.009] | +0.014 [+0.009, +0.019] | +0.003 [+0.001, +0.006] | +0.920 [+0.895, +0.945] |
| first | old | L48 | +0.004 [-0.000, +0.008] | +0.018 [+0.012, +0.024] | +0.003 [+0.000, +0.005] | +0.428 [+0.394, +0.462] |
| first | new | L16 | +0.003 [-0.000, +0.007] | +0.004 [-0.002, +0.008] | +0.002 [-0.001, +0.004] | +1.000 [+0.989, +1.010] |
| first | new | L24 | +0.002 [-0.001, +0.006] | +0.007 [+0.002, +0.012] | +0.002 [-0.001, +0.005] | +0.992 [+0.978, +1.005] |
| first | new | L32 | +0.005 [-0.000, +0.010] | +0.008 [+0.003, +0.013] | +0.002 [-0.001, +0.005] | +0.971 [+0.954, +0.988] |
| first | new | L40 | +0.005 [+0.001, +0.009] | +0.032 [+0.025, +0.040] | +0.003 [+0.001, +0.006] | +0.920 [+0.895, +0.945] |
| first | new | L48 | +0.004 [-0.000, +0.008] | +0.034 [+0.026, +0.043] | +0.003 [+0.000, +0.005] | +0.428 [+0.394, +0.462] |
| others | old | L16 | -0.001 [-0.005, +0.003] | -0.001 [-0.006, +0.003] | +0.000 [-0.002, +0.003] | +1.001 [+0.994, +1.009] |
| others | old | L24 | +0.001 [-0.004, +0.006] | +0.000 [-0.004, +0.005] | -0.002 [-0.005, +0.001] | +0.997 [+0.987, +1.008] |
| others | old | L32 | +0.002 [-0.002, +0.007] | +0.002 [-0.002, +0.007] | -0.000 [-0.003, +0.003] | +0.991 [+0.977, +1.005] |
| others | old | L40 | +0.004 [+0.000, +0.008] | +0.014 [+0.009, +0.019] | +0.001 [-0.002, +0.003] | +0.944 [+0.922, +0.965] |
| others | old | L48 | +0.002 [-0.001, +0.005] | +0.016 [+0.011, +0.022] | -0.000 [-0.004, +0.002] | +0.474 [+0.442, +0.506] |
| others | new | L16 | -0.001 [-0.005, +0.003] | +0.001 [-0.004, +0.006] | +0.000 [-0.002, +0.003] | +1.001 [+0.994, +1.009] |
| others | new | L24 | +0.001 [-0.004, +0.006] | +0.007 [+0.001, +0.013] | -0.002 [-0.005, +0.001] | +0.997 [+0.987, +1.008] |
| others | new | L32 | +0.002 [-0.002, +0.007] | +0.004 [-0.001, +0.009] | -0.000 [-0.003, +0.003] | +0.991 [+0.977, +1.005] |
| others | new | L40 | +0.004 [+0.000, +0.008] | +0.029 [+0.022, +0.037] | +0.001 [-0.002, +0.003] | +0.944 [+0.922, +0.965] |
| others | new | L48 | +0.002 [-0.001, +0.005] | +0.033 [+0.025, +0.041] | -0.000 [-0.004, +0.002] | +0.474 [+0.442, +0.506] |
| last | old | L16 | -0.001 [-0.006, +0.003] | -0.000 [-0.005, +0.004] | +0.000 [-0.003, +0.003] | +0.998 [+0.986, +1.010] |
| last | old | L24 | +0.003 [-0.002, +0.009] | +0.003 [-0.003, +0.010] | -0.000 [-0.003, +0.003] | +0.999 [+0.984, +1.014] |
| last | old | L32 | +0.002 [-0.004, +0.007] | +0.001 [-0.006, +0.007] | +0.001 [-0.003, +0.005] | +0.990 [+0.970, +1.009] |
| last | old | L40 | +0.004 [-0.002, +0.009] | +0.010 [+0.004, +0.017] | +0.002 [-0.002, +0.005] | +0.932 [+0.901, +0.963] |
| last | old | L48 | +0.003 [-0.001, +0.007] | +0.015 [+0.009, +0.022] | +0.000 [-0.003, +0.004] | +0.453 [+0.406, +0.497] |
| last | new | L16 | -0.001 [-0.006, +0.003] | +0.005 [-0.001, +0.010] | +0.000 [-0.003, +0.003] | +0.998 [+0.986, +1.010] |
| last | new | L24 | +0.003 [-0.002, +0.009] | +0.007 [+0.001, +0.014] | -0.000 [-0.003, +0.003] | +0.999 [+0.984, +1.014] |
| last | new | L32 | +0.002 [-0.004, +0.007] | +0.004 [-0.003, +0.011] | +0.001 [-0.003, +0.005] | +0.990 [+0.970, +1.009] |
| last | new | L40 | +0.004 [-0.002, +0.009] | +0.036 [+0.027, +0.045] | +0.002 [-0.002, +0.005] | +0.932 [+0.901, +0.963] |
| last | new | L48 | +0.003 [-0.001, +0.007] | +0.035 [+0.025, +0.045] | +0.000 [-0.003, +0.004] | +0.453 [+0.406, +0.497] |

## X3 behaviour: recovery (paraphrase - D) / (original - D), primary set, all subset

| stratum | split | group | n | ratio [CI] | para - D [CI] |
|---|---|---|---|---|---|
| all | test | all | 552 | +0.897 [+0.868, +0.926] | +0.229 [+0.208, +0.250] |
| all | test | target | 274 | +0.894 [+0.863, +0.924] |  |
| all | test | control | 278 | +0.901 [+0.841, +0.962] |  |
| all | test | target_minus_control | 552 | -0.007 [-0.075, +0.059] |  |
| all | all | all | 1110 | +0.903 [+0.882, +0.924] | +0.245 [+0.229, +0.260] |
| all | all | target | 561 | +0.905 [+0.881, +0.927] |  |
| all | all | control | 549 | +0.899 [+0.862, +0.936] |  |
| all | all | target_minus_control | 1110 | +0.006 [-0.035, +0.048] |  |
| first | test | all | 552 | +0.901 [+0.865, +0.937] | +0.239 [+0.212, +0.266] |
| first | test | target | 274 | +0.896 [+0.854, +0.936] |  |
| first | test | control | 278 | +0.909 [+0.838, +0.980] |  |
| first | test | target_minus_control | 552 | -0.012 [-0.094, +0.071] |  |
| first | all | all | 1110 | +0.898 [+0.874, +0.922] | +0.254 [+0.235, +0.272] |
| first | all | target | 561 | +0.898 [+0.868, +0.925] |  |
| first | all | control | 549 | +0.898 [+0.854, +0.941] |  |
| first | all | target_minus_control | 1110 | +0.000 [-0.052, +0.052] |  |
| others | test | all | 453 | +0.889 [+0.855, +0.923] | +0.223 [+0.200, +0.246] |
| others | test | target | 243 | +0.892 [+0.855, +0.928] |  |
| others | test | control | 210 | +0.882 [+0.812, +0.956] |  |
| others | test | target_minus_control | 453 | +0.010 [-0.072, +0.088] |  |
| others | all | all | 911 | +0.897 [+0.875, +0.919] | +0.237 [+0.220, +0.254] |
| others | all | target | 491 | +0.904 [+0.878, +0.930] |  |
| others | all | control | 420 | +0.884 [+0.841, +0.926] |  |
| others | all | target_minus_control | 911 | +0.020 [-0.029, +0.070] |  |
| last | test | all | 306 | +0.907 [+0.857, +0.954] | +0.245 [+0.212, +0.281] |
| last | test | target | 174 | +0.915 [+0.863, +0.963] |  |
| last | test | control | 132 | +0.886 [+0.779, +0.990] |  |
| last | test | target_minus_control | 306 | +0.029 [-0.088, +0.147] |  |
| last | all | all | 634 | +0.905 [+0.875, +0.935] | +0.261 [+0.236, +0.285] |
| last | all | target | 360 | +0.909 [+0.877, +0.942] |  |
| last | all | control | 274 | +0.894 [+0.836, +0.953] |  |
| last | all | target_minus_control | 634 | +0.015 [-0.050, +0.084] |  |

## X4 author answer: D = self - partner (test) by stratum

### title

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | +0.048 [+0.039, +0.058] | +0.046 [+0.035, +0.059] | +0.047 [+0.038, +0.058] | +0.046 [+0.031, +0.062] |
| L16 | +0.056 [+0.047, +0.066] | +0.056 [+0.043, +0.069] | +0.053 [+0.043, +0.064] | +0.049 [+0.033, +0.066] |
| L24 | +0.057 [+0.047, +0.066] | +0.056 [+0.043, +0.068] | +0.056 [+0.046, +0.066] | +0.049 [+0.035, +0.064] |
| L32 | +0.058 [+0.048, +0.068] | +0.058 [+0.045, +0.071] | +0.058 [+0.048, +0.069] | +0.053 [+0.039, +0.067] |
| L40 | +0.064 [+0.054, +0.074] | +0.068 [+0.056, +0.080] | +0.064 [+0.054, +0.075] | +0.063 [+0.048, +0.077] |
| L48 | +0.024 [+0.020, +0.028] | +0.024 [+0.018, +0.029] | +0.026 [+0.022, +0.030] | +0.024 [+0.017, +0.030] |
| L56 | +0.000 [-0.001, +0.001] | +0.001 [-0.000, +0.002] | -0.000 [-0.001, +0.001] | -0.000 [-0.002, +0.001] |

### colon

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | -0.001 [-0.002, +0.000] | -0.001 [-0.002, +0.001] | -0.001 [-0.002, +0.001] | -0.000 [-0.002, +0.002] |
| L16 | +0.001 [-0.000, +0.003] | +0.002 [-0.000, +0.005] | +0.000 [-0.002, +0.002] | -0.001 [-0.004, +0.002] |
| L24 | +0.002 [+0.000, +0.003] | +0.001 [-0.000, +0.003] | +0.002 [+0.000, +0.003] | +0.001 [-0.001, +0.003] |
| L32 | +0.002 [+0.001, +0.003] | +0.001 [-0.000, +0.003] | +0.002 [+0.001, +0.003] | +0.001 [-0.001, +0.003] |
| L40 | +0.002 [+0.001, +0.003] | +0.001 [-0.000, +0.003] | +0.002 [+0.000, +0.003] | +0.001 [-0.001, +0.003] |
| L48 | +0.011 [+0.009, +0.013] | +0.012 [+0.009, +0.015] | +0.012 [+0.010, +0.014] | +0.011 [+0.008, +0.014] |
| L56 | +0.006 [+0.005, +0.008] | +0.008 [+0.005, +0.010] | +0.006 [+0.004, +0.008] | +0.005 [+0.002, +0.008] |

Earliest layer with D > 0 on tune, confirmed on test:

| stratum | title | colon |
|---|---|---|
| all | L8 (confirmed, test +0.048 [+0.039, +0.058]) | L24 (confirmed, test +0.002 [+0.000, +0.003]) |
| first | L8 (confirmed, test +0.046 [+0.035, +0.059]) | L24 (not confirmed, test +0.001 [-0.000, +0.003]) |
| others | L8 (confirmed, test +0.047 [+0.038, +0.058]) | L40 (confirmed, test +0.002 [+0.000, +0.003]) |
| last | L8 (confirmed, test +0.046 [+0.031, +0.062]) | L24 (not confirmed, test +0.001 [-0.001, +0.003]) |

Recognition (target - control of self - partner within citation bin, all pairs), title position:

| layer | all | first | others | last |
|---|---|---|---|---|
| L8 | +0.031 [+0.017, +0.045] | +0.040 [+0.023, +0.057] | +0.025 [+0.010, +0.041] | +0.028 [+0.005, +0.051] |
| L16 | +0.032 [+0.018, +0.045] | +0.043 [+0.026, +0.061] | +0.027 [+0.013, +0.042] | +0.026 [+0.001, +0.049] |
| L24 | +0.040 [+0.027, +0.053] | +0.050 [+0.033, +0.066] | +0.033 [+0.018, +0.047] | +0.038 [+0.017, +0.060] |
| L32 | +0.048 [+0.033, +0.062] | +0.055 [+0.037, +0.073] | +0.038 [+0.023, +0.053] | +0.045 [+0.025, +0.066] |
| L40 | +0.052 [+0.038, +0.067] | +0.060 [+0.044, +0.078] | +0.041 [+0.027, +0.054] | +0.050 [+0.030, +0.068] |
| L48 | +0.021 [+0.015, +0.027] | +0.023 [+0.016, +0.031] | +0.016 [+0.009, +0.022] | +0.022 [+0.013, +0.031] |
| L56 | -0.000 [-0.001, +0.001] | +0.000 [-0.001, +0.002] | +0.001 [-0.001, +0.002] | -0.001 [-0.002, +0.001] |

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

- primary/d_matched/tune/partner_B/control: denominator <= 0 in 2.4% of draws (CI unreliable)
- primary/d_matched/test/lexical_neighbour_D/control: denominator <= 0 in 1.2% of draws (CI unreliable)
- primary/d_matched/test/partner_B/control: denominator <= 0 in 0.1% of draws (CI unreliable)
- primary/d_matched/all/lexical_neighbour_D/control: denominator <= 0 in 0.1% of draws (CI unreliable)
- sensitivity/d_matched/tune/lexical_neighbour_D/control: denominator <= 0 in 0.8% of draws (CI unreliable)
- sensitivity/d_matched/tune/partner_B/control: denominator <= 0 in 8.4% of draws (CI unreliable)
- sensitivity/d_matched/test/lexical_neighbour_D/control: denominator <= 0 in 0.5% of draws (CI unreliable)

