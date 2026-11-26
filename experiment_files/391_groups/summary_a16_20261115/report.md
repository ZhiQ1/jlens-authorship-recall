# Addendum 16, items B (output format) and D (name chain): pre-registered analysis

Run 2026-11-15T14:57:49 (job 11879060); plan sha256 c78daad0... (verified), deviations sha256 a1512fda... (verified). B: 1500 papers / shards 0-29 (30); D: 1428 papers / shards 0-28 (29). Intervals: archived author-team cluster bootstrap, 2,000 draws, one shared draw for B and D (groups_core.Engine, seed 391). NOT PUBLISHED.

## 1. Confirmatory tests (Holm over 5)

| test | quantity | estimate | 95% CI | Holm level | Holm-adj. CI | Bonferroni (0.01) CI | p (test) | p Holm | rejected |
|---|---|---|---|---|---|---|---|---|---|
| B_F4 | Delta_A | +0.103 | [+0.078, +0.129] | 0.0100 | [+0.072, +0.133] | [+0.072, +0.133] | 0.0005 | 0.0025 | True |
| B_F4 | DiD_A-B | +0.085 | [+0.055, +0.115] | 0.0100 | [+0.047, +0.124] | [+0.047, +0.124] | 0.0005 | 0.0025 | True |
| D_GA1 | G_A(1) | +0.167 | [+0.147, +0.185] | 0.0125 | [+0.141, +0.189] | [+0.140, +0.190] | 0.0005 | 0.0025 | True |
| B_F2 | Delta_A | +0.047 | [+0.016, +0.077] | 0.0167 | [+0.008, +0.084] | [+0.005, +0.088] | 0.0790 | 0.2370 | False |
| B_F2 | DiD_A-B | +0.032 | [-0.004, +0.067] | 0.0167 | [-0.012, +0.076] | [-0.017, +0.078] | 0.0790 | 0.2370 | False |
| B_F1 | Delta_A | +0.033 | [+0.008, +0.058] | 0.0250 | [+0.003, +0.062] | [-0.003, +0.066] | 0.1640 | 0.3280 | False |
| B_F1 | DiD_A-B | +0.022 | [-0.008, +0.052] | 0.0250 | [-0.012, +0.055] | [-0.019, +0.060] | 0.1640 | 0.3280 | False |
| B_F3 | Delta_A | -0.013 | [-0.027, +0.000] | 0.0500 | [-0.027, +0.000] | [-0.030, +0.003] | 0.4430 | 0.4430 | False |
| B_F3 | DiD_A-B | -0.007 | [-0.024, +0.011] | 0.0500 | [-0.024, +0.011] | [-0.029, +0.015] | 0.4430 | 0.4430 | False |

Verdicts:
- B F1 (any_full): Delta_A = +0.033 [Holm CI +0.003, +0.062], DiD = +0.022 [Holm CI -0.012, +0.055]; p_test 0.1640, Holm p 0.3280; fabrication change A -0.338 -> interpretable; criterion not met.
- B F2 (any_sur): Delta_A = +0.047 [Holm CI +0.008, +0.084], DiD = +0.032 [Holm CI -0.012, +0.076]; p_test 0.0790, Holm p 0.2370; fabrication change A -0.033 -> interpretable; criterion not met.
- B F3 (first_sur): Delta_A = -0.013 [Holm CI -0.027, +0.000], DiD = -0.007 [Holm CI -0.024, +0.011]; p_test 0.4430, Holm p 0.4430; fabrication change A -0.032 -> interpretable; criterion not met.
- B F4 (first_sur): Delta_A = +0.103 [Holm CI +0.072, +0.133], DiD = +0.085 [Holm CI +0.047, +0.124]; p_test 0.0005, Holm p 0.0025; fabrication change A -0.007 -> interpretable; criterion met.
- B overall: SUPPORTED via F4 (rule: >= 1 c with Delta_A > 0 and DiD > 0, Holm-adjusted CIs excluding 0).
- D G_A(1) = +0.167 [95% +0.147, +0.185; Holm CI +0.141, +0.189], p 0.0005, Holm p 0.0025: chain effect SUPPORTED, direction helps (rule: Holm-adjusted 95% CI of G_A(1) excludes 0; two-sided).

## 2. B: rates per condition (true, chance, true - chance), all papers of each group

### outcome any_full

| group | cond | n | true | chance | true - chance [95% CI] |
|---|---|---|---|---|---|
| A | F0 | 600 | 0.040 | 0.003 | +0.037 [+0.020, +0.054] |
| A | F1 | 600 | 0.070 | 0.000 | +0.070 [+0.049, +0.091] |
| A | F2 | 600 | 0.008 | 0.000 | +0.008 [+0.002, +0.016] |
| A | F3 | 600 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| A | F4 | 600 | 0.152 | 0.002 | +0.150 [+0.123, +0.178] |
| B | F0 | 600 | 0.005 | 0.002 | +0.003 [-0.003, +0.010] |
| B | F1 | 600 | 0.017 | 0.002 | +0.015 [+0.003, +0.029] |
| B | F2 | 600 | 0.002 | 0.000 | +0.002 [+0.000, +0.005] |
| B | F3 | 600 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| B | F4 | 600 | 0.032 | 0.005 | +0.027 [+0.012, +0.042] |
| C | F0 | 300 | 0.413 | 0.000 | +0.413 [+0.356, +0.469] |
| C | F1 | 300 | 0.380 | 0.000 | +0.380 [+0.326, +0.435] |
| C | F2 | 300 | 0.040 | 0.000 | +0.040 [+0.019, +0.065] |
| C | F3 | 300 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| C | F4 | 300 | 0.543 | 0.000 | +0.543 [+0.486, +0.600] |

### outcome any_sur

| group | cond | n | true | chance | true - chance [95% CI] |
|---|---|---|---|---|---|
| A | F0 | 600 | 0.070 | 0.012 | +0.058 [+0.036, +0.081] |
| A | F1 | 600 | 0.095 | 0.005 | +0.090 [+0.067, +0.113] |
| A | F2 | 600 | 0.118 | 0.013 | +0.105 [+0.078, +0.133] |
| A | F3 | 600 | 0.028 | 0.002 | +0.027 [+0.014, +0.042] |
| A | F4 | 600 | 0.177 | 0.018 | +0.158 [+0.128, +0.190] |
| B | F0 | 600 | 0.042 | 0.013 | +0.028 [+0.009, +0.048] |
| B | F1 | 600 | 0.045 | 0.017 | +0.028 [+0.010, +0.048] |
| B | F2 | 600 | 0.063 | 0.020 | +0.043 [+0.022, +0.064] |
| B | F3 | 600 | 0.008 | 0.000 | +0.008 [+0.002, +0.016] |
| B | F4 | 600 | 0.067 | 0.023 | +0.043 [+0.019, +0.067] |
| C | F0 | 300 | 0.507 | 0.000 | +0.507 [+0.448, +0.560] |
| C | F1 | 300 | 0.427 | 0.010 | +0.417 [+0.359, +0.473] |
| C | F2 | 300 | 0.527 | 0.017 | +0.510 [+0.452, +0.568] |
| C | F3 | 300 | 0.163 | 0.000 | +0.163 [+0.119, +0.206] |
| C | F4 | 300 | 0.580 | 0.003 | +0.577 [+0.520, +0.632] |

### outcome first_sur

| group | cond | n | true | chance | true - chance [95% CI] |
|---|---|---|---|---|---|
| A | F0 | 600 | 0.027 | 0.003 | +0.023 [+0.010, +0.037] |
| A | F1 | 600 | 0.048 | 0.005 | +0.043 [+0.026, +0.061] |
| A | F2 | 600 | 0.058 | 0.005 | +0.053 [+0.034, +0.073] |
| A | F3 | 600 | 0.010 | 0.000 | +0.010 [+0.003, +0.019] |
| A | F4 | 600 | 0.130 | 0.003 | +0.127 [+0.099, +0.153] |
| B | F0 | 600 | 0.013 | 0.005 | +0.008 [-0.002, +0.019] |
| B | F1 | 600 | 0.020 | 0.003 | +0.017 [+0.005, +0.029] |
| B | F2 | 600 | 0.027 | 0.007 | +0.020 [+0.006, +0.035] |
| B | F3 | 600 | 0.002 | 0.000 | +0.002 [+0.000, +0.005] |
| B | F4 | 600 | 0.030 | 0.003 | +0.027 [+0.012, +0.042] |
| C | F0 | 300 | 0.233 | 0.000 | +0.233 [+0.187, +0.280] |
| C | F1 | 300 | 0.220 | 0.000 | +0.220 [+0.174, +0.267] |
| C | F2 | 300 | 0.270 | 0.003 | +0.267 [+0.218, +0.318] |
| C | F3 | 300 | 0.083 | 0.000 | +0.083 [+0.053, +0.116] |
| C | F4 | 300 | 0.403 | 0.003 | +0.400 [+0.343, +0.457] |

### outcome first_sur_pos1

| group | cond | n | true | chance | true - chance [95% CI] |
|---|---|---|---|---|---|
| A | F0 | 600 | 0.017 | 0.000 | +0.017 [+0.007, +0.028] |
| A | F1 | 600 | 0.020 | 0.002 | +0.018 [+0.007, +0.031] |
| A | F2 | 600 | 0.027 | 0.000 | +0.027 [+0.015, +0.041] |
| A | F3 | 600 | 0.010 | 0.000 | +0.010 [+0.003, +0.019] |
| A | F4 | 600 | 0.122 | 0.002 | +0.120 [+0.094, +0.147] |
| B | F0 | 600 | 0.007 | 0.002 | +0.005 [-0.002, +0.013] |
| B | F1 | 600 | 0.007 | 0.002 | +0.005 [-0.002, +0.013] |
| B | F2 | 600 | 0.003 | 0.003 | +0.000 [-0.007, +0.006] |
| B | F3 | 600 | 0.002 | 0.000 | +0.002 [+0.000, +0.005] |
| B | F4 | 600 | 0.025 | 0.002 | +0.023 [+0.011, +0.037] |
| C | F0 | 300 | 0.180 | 0.000 | +0.180 [+0.138, +0.223] |
| C | F1 | 300 | 0.150 | 0.000 | +0.150 [+0.112, +0.190] |
| C | F2 | 300 | 0.167 | 0.000 | +0.167 [+0.130, +0.210] |
| C | F3 | 300 | 0.083 | 0.000 | +0.083 [+0.053, +0.116] |
| C | F4 | 300 | 0.377 | 0.000 | +0.377 [+0.320, +0.436] |

### outcome first_full

| group | cond | n | true | chance | true - chance [95% CI] |
|---|---|---|---|---|---|
| A | F0 | 600 | 0.015 | 0.000 | +0.015 [+0.007, +0.025] |
| A | F1 | 600 | 0.037 | 0.000 | +0.037 [+0.023, +0.053] |
| A | F2 | 600 | 0.003 | 0.000 | +0.003 [+0.000, +0.009] |
| A | F3 | 600 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| A | F4 | 600 | 0.123 | 0.002 | +0.122 [+0.096, +0.148] |
| B | F0 | 600 | 0.000 | 0.002 | -0.002 [-0.005, +0.000] |
| B | F1 | 600 | 0.007 | 0.002 | +0.005 [-0.002, +0.012] |
| B | F2 | 600 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| B | F3 | 600 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| B | F4 | 600 | 0.027 | 0.002 | +0.025 [+0.012, +0.039] |
| C | F0 | 300 | 0.180 | 0.000 | +0.180 [+0.137, +0.225] |
| C | F1 | 300 | 0.200 | 0.000 | +0.200 [+0.156, +0.246] |
| C | F2 | 300 | 0.020 | 0.000 | +0.020 [+0.007, +0.037] |
| C | F3 | 300 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] |
| C | F4 | 300 | 0.390 | 0.000 | +0.390 [+0.334, +0.447] |

## 3. B: Delta (condition - F0, chance-corrected) and DiD A - B, with fabrication change (interpretability rule)

| fa_type | cond | outcome | contrast | estimate [95% CI] | n | fabrication change [95% CI] | flag |
|---|---|---|---|---|---|---|---|
| all | F1 | any_full (primary) | Delta_A | +0.033 [+0.008, +0.058] | 600 | -0.338 [-0.381, -0.297] |  |
| all | F1 | any_full (primary) | Delta_B | +0.012 [+0.002, +0.023] | 600 | -0.418 [-0.461, -0.376] |  |
| all | F1 | any_full (primary) | Delta_C | -0.033 [-0.103, +0.034] | 300 | -0.177 [-0.230, -0.129] |  |
| all | F1 | any_full (primary) | DiD_A-B | +0.022 [-0.008, +0.052] | 600 |  |  |
| all | F2 | any_sur (primary) | Delta_A | +0.047 [+0.016, +0.077] | 600 | -0.033 [-0.051, -0.017] |  |
| all | F2 | any_sur (primary) | Delta_B | +0.015 [-0.002, +0.034] | 600 | -0.038 [-0.054, -0.024] |  |
| all | F2 | any_sur (primary) | Delta_C | +0.003 [-0.061, +0.074] | 300 | -0.013 [-0.047, +0.020] |  |
| all | F2 | any_sur (primary) | DiD_A-B | +0.032 [-0.004, +0.067] | 600 |  |  |
| all | F3 | first_sur (primary) | Delta_A | -0.013 [-0.027, +0.000] | 600 | -0.032 [-0.049, -0.015] |  |
| all | F3 | first_sur (primary) | Delta_B | -0.007 [-0.018, +0.004] | 600 | -0.017 [-0.027, -0.007] |  |
| all | F3 | first_sur (primary) | Delta_C | -0.150 [-0.201, -0.101] | 300 | -0.120 [-0.171, -0.070] |  |
| all | F3 | first_sur (primary) | DiD_A-B | -0.007 [-0.024, +0.011] | 600 |  |  |
| all | F4 | first_sur (primary) | Delta_A | +0.103 [+0.078, +0.129] | 600 | -0.007 [-0.017, +0.003] |  |
| all | F4 | first_sur (primary) | Delta_B | +0.018 [+0.003, +0.035] | 600 | -0.002 [-0.005, +0.000] |  |
| all | F4 | first_sur (primary) | Delta_C | +0.167 [+0.112, +0.224] | 300 | -0.050 [-0.087, -0.015] |  |
| all | F4 | first_sur (primary) | DiD_A-B | +0.085 [+0.055, +0.115] | 600 |  |  |
| all | F3 | first_sur_pos1 | Delta_A | -0.007 [-0.019, +0.005] | 600 | -0.032 [-0.049, -0.015] |  |
| all | F3 | first_sur_pos1 | Delta_B | -0.003 [-0.012, +0.005] | 600 | -0.017 [-0.027, -0.007] |  |
| all | F3 | first_sur_pos1 | Delta_C | -0.097 [-0.144, -0.052] | 300 | -0.120 [-0.171, -0.070] |  |
| all | F3 | first_sur_pos1 | DiD_A-B | -0.003 [-0.018, +0.011] | 600 |  |  |
| all | F4 | first_sur_pos1 | Delta_A | +0.103 [+0.080, +0.128] | 600 | -0.007 [-0.017, +0.003] |  |
| all | F4 | first_sur_pos1 | Delta_B | +0.018 [+0.005, +0.033] | 600 | -0.002 [-0.005, +0.000] |  |
| all | F4 | first_sur_pos1 | Delta_C | +0.197 [+0.137, +0.253] | 300 | -0.050 [-0.087, -0.015] |  |
| all | F4 | first_sur_pos1 | DiD_A-B | +0.085 [+0.057, +0.113] | 600 |  |  |
| all | F1 | first_full | Delta_A | +0.022 [+0.007, +0.037] | 600 | -0.338 [-0.381, -0.297] |  |
| all | F1 | first_full | Delta_B | +0.007 [+0.000, +0.015] | 600 | -0.418 [-0.461, -0.376] |  |
| all | F1 | first_full | Delta_C | +0.020 [-0.026, +0.065] | 300 | -0.177 [-0.230, -0.129] |  |
| all | F1 | first_full | DiD_A-B | +0.015 [-0.002, +0.032] | 600 |  |  |
| all | F2 | first_sur | Delta_A | +0.030 [+0.011, +0.050] | 600 | -0.033 [-0.051, -0.017] |  |
| all | F2 | first_sur | Delta_B | +0.012 [+0.000, +0.025] | 600 | -0.038 [-0.054, -0.024] |  |
| all | F2 | first_sur | Delta_C | +0.033 [-0.014, +0.079] | 300 | -0.013 [-0.047, +0.020] |  |
| all | F2 | first_sur | DiD_A-B | +0.018 [-0.005, +0.042] | 600 |  |  |
| initial_first | F1 | any_full | Delta_A | +0.031 [+0.004, +0.058] | 453 | -0.380 [-0.429, -0.332] |  |
| initial_first | F1 | any_full | Delta_B | +0.007 [-0.003, +0.018] | 413 | -0.407 [-0.456, -0.359] |  |
| initial_first | F1 | any_full | Delta_C | -0.041 [-0.117, +0.037] | 222 | -0.158 [-0.220, -0.101] |  |
| initial_first | F1 | any_full | DiD_A-B | +0.024 [-0.005, +0.053] | 413 |  |  |
| initial_first | F2 | any_sur | Delta_A | +0.042 [+0.011, +0.073] | 453 | -0.042 [-0.065, -0.020] |  |
| initial_first | F2 | any_sur | Delta_B | +0.002 [-0.015, +0.021] | 413 | -0.034 [-0.052, -0.018] |  |
| initial_first | F2 | any_sur | Delta_C | -0.036 [-0.116, +0.044] | 222 | -0.009 [-0.052, +0.034] |  |
| initial_first | F2 | any_sur | DiD_A-B | +0.040 [+0.003, +0.075] | 413 |  |  |
| initial_first | F3 | first_sur | Delta_A | -0.011 [-0.025, +0.002] | 453 | -0.029 [-0.049, -0.010] |  |
| initial_first | F3 | first_sur | Delta_B | -0.002 [-0.011, +0.005] | 413 | -0.007 [-0.017, +0.000] |  |
| initial_first | F3 | first_sur | Delta_C | -0.153 [-0.218, -0.093] | 222 | -0.108 [-0.168, -0.048] |  |
| initial_first | F3 | first_sur | DiD_A-B | -0.009 [-0.025, +0.007] | 413 |  |  |
| initial_first | F4 | first_sur | Delta_A | +0.124 [+0.094, +0.155] | 453 | -0.007 [-0.020, +0.006] |  |
| initial_first | F4 | first_sur | Delta_B | +0.027 [+0.010, +0.044] | 413 | +0.000 [+0.000, +0.000] |  |
| initial_first | F4 | first_sur | Delta_C | +0.180 [+0.116, +0.241] | 222 | -0.059 [-0.102, -0.017] |  |
| initial_first | F4 | first_sur | DiD_A-B | +0.097 [+0.062, +0.132] | 413 |  |  |
| initial_first | F3 | first_sur_pos1 | Delta_A | -0.009 [-0.022, +0.005] | 453 | -0.029 [-0.049, -0.010] |  |
| initial_first | F3 | first_sur_pos1 | Delta_B | -0.002 [-0.008, +0.000] | 413 | -0.007 [-0.017, +0.000] |  |
| initial_first | F3 | first_sur_pos1 | Delta_C | -0.108 [-0.167, -0.053] | 222 | -0.108 [-0.168, -0.048] |  |
| initial_first | F3 | first_sur_pos1 | DiD_A-B | -0.006 [-0.020, +0.008] | 413 |  |  |
| initial_first | F4 | first_sur_pos1 | Delta_A | +0.124 [+0.094, +0.153] | 453 | -0.007 [-0.020, +0.006] |  |
| initial_first | F4 | first_sur_pos1 | Delta_B | +0.024 [+0.011, +0.039] | 413 | +0.000 [+0.000, +0.000] |  |
| initial_first | F4 | first_sur_pos1 | Delta_C | +0.221 [+0.151, +0.286] | 222 | -0.059 [-0.102, -0.017] |  |
| initial_first | F4 | first_sur_pos1 | DiD_A-B | +0.099 [+0.067, +0.132] | 413 |  |  |
| initial_first | F1 | first_full | Delta_A | +0.026 [+0.010, +0.045] | 453 | -0.380 [-0.429, -0.332] |  |
| initial_first | F1 | first_full | Delta_B | +0.002 [-0.005, +0.011] | 413 | -0.407 [-0.456, -0.359] |  |
| initial_first | F1 | first_full | Delta_C | +0.018 [-0.039, +0.072] | 222 | -0.158 [-0.220, -0.101] |  |
| initial_first | F1 | first_full | DiD_A-B | +0.024 [+0.004, +0.044] | 413 |  |  |
| initial_first | F2 | first_sur | Delta_A | +0.029 [+0.009, +0.049] | 453 | -0.042 [-0.065, -0.020] |  |
| initial_first | F2 | first_sur | Delta_B | +0.005 [-0.007, +0.016] | 413 | -0.034 [-0.052, -0.018] |  |
| initial_first | F2 | first_sur | Delta_C | +0.014 [-0.042, +0.066] | 222 | -0.009 [-0.052, +0.034] |  |
| initial_first | F2 | first_sur | DiD_A-B | +0.024 [+0.001, +0.048] | 413 |  |  |
| given_first | F1 | any_full | Delta_A | +0.043 [-0.022, +0.103] | 141 | -0.220 [-0.291, -0.153] |  |
| given_first | F1 | any_full | Delta_B | +0.016 [-0.006, +0.042] | 183 | -0.443 [-0.519, -0.366] |  |
| given_first | F1 | any_full | Delta_C | -0.013 [-0.143, +0.129] | 78 | -0.231 [-0.338, -0.130] |  |
| given_first | F1 | any_full | DiD_A-B | +0.026 [-0.044, +0.092] | 141 |  |  |
| given_first | F2 | any_sur | Delta_A | +0.064 [-0.014, +0.142] | 141 | -0.007 [-0.023, +0.000] |  |
| given_first | F2 | any_sur | Delta_B | +0.044 [+0.005, +0.089] | 183 | -0.049 [-0.085, -0.020] |  |
| given_first | F2 | any_sur | Delta_C | +0.115 [+0.000, +0.237] | 78 | -0.026 [-0.080, +0.023] |  |
| given_first | F2 | any_sur | DiD_A-B | +0.020 [-0.076, +0.115] | 141 |  |  |
| given_first | F3 | first_sur | Delta_A | -0.021 [-0.053, +0.007] | 141 | -0.043 [-0.078, -0.014] |  |
| given_first | F3 | first_sur | Delta_B | -0.016 [-0.048, +0.015] | 183 | -0.038 [-0.065, -0.013] |  |
| given_first | F3 | first_sur | Delta_C | -0.141 [-0.225, -0.059] | 78 | -0.154 [-0.261, -0.053] |  |
| given_first | F3 | first_sur | DiD_A-B | -0.005 [-0.049, +0.038] | 141 |  |  |
| given_first | F4 | first_sur | Delta_A | +0.043 [-0.008, +0.097] | 141 | -0.007 [-0.024, +0.000] |  |
| given_first | F4 | first_sur | Delta_B | +0.000 [-0.035, +0.033] | 183 | +0.000 [+0.000, +0.000] |  |
| given_first | F4 | first_sur | Delta_C | +0.128 [+0.014, +0.242] | 78 | -0.026 [-0.087, +0.034] |  |
| given_first | F4 | first_sur | DiD_A-B | +0.043 [-0.019, +0.107] | 141 |  |  |
| given_first | F3 | first_sur_pos1 | Delta_A | +0.000 [-0.020, +0.021] | 141 | -0.043 [-0.078, -0.014] |  |
| given_first | F3 | first_sur_pos1 | Delta_B | -0.005 [-0.030, +0.018] | 183 | -0.038 [-0.065, -0.013] |  |
| given_first | F3 | first_sur_pos1 | Delta_C | -0.064 [-0.138, +0.013] | 78 | -0.154 [-0.261, -0.053] |  |
| given_first | F3 | first_sur_pos1 | DiD_A-B | +0.005 [-0.025, +0.037] | 141 |  |  |
| given_first | F4 | first_sur_pos1 | Delta_A | +0.043 [+0.007, +0.082] | 141 | -0.007 [-0.024, +0.000] |  |
| given_first | F4 | first_sur_pos1 | Delta_B | +0.005 [-0.022, +0.034] | 183 | +0.000 [+0.000, +0.000] |  |
| given_first | F4 | first_sur_pos1 | Delta_C | +0.128 [+0.030, +0.231] | 78 | -0.026 [-0.087, +0.034] |  |
| given_first | F4 | first_sur_pos1 | DiD_A-B | +0.037 [-0.010, +0.086] | 141 |  |  |
| given_first | F1 | first_full | Delta_A | +0.007 [-0.022, +0.040] | 141 | -0.220 [-0.291, -0.153] |  |
| given_first | F1 | first_full | Delta_B | +0.016 [+0.000, +0.039] | 183 | -0.443 [-0.519, -0.366] |  |
| given_first | F1 | first_full | Delta_C | +0.026 [-0.041, +0.101] | 78 | -0.231 [-0.338, -0.130] |  |
| given_first | F1 | first_full | DiD_A-B | -0.009 [-0.044, +0.028] | 141 |  |  |
| given_first | F2 | first_sur | Delta_A | +0.035 [-0.016, +0.092] | 141 | -0.007 [-0.023, +0.000] |  |
| given_first | F2 | first_sur | Delta_B | +0.027 [-0.005, +0.061] | 183 | -0.049 [-0.085, -0.020] |  |
| given_first | F2 | first_sur | Delta_C | +0.090 [+0.013, +0.178] | 78 | -0.026 [-0.080, +0.023] |  |
| given_first | F2 | first_sur | DiD_A-B | +0.008 [-0.051, +0.070] | 141 |  |  |

## 4. B: fabrication beside every condition (share of papers with >= 1 unmatched item; empty-answer share)

| group | cond | fab_any_full | fab_any_sur | empty | mean items |
|---|---|---|---|---|---|
| A | F0 | 0.993 | 0.993 | 0.003 | 4.00 |
| A | F1 | 0.655 | 0.653 | 0.338 | 4.49 |
| A | F2 | 0.968 | 0.960 | 0.032 | 6.98 |
| A | F3 | 0.990 | 0.962 | 0.010 | 0.99 |
| A | F4 | 0.987 | 0.987 | 0.000 | 3.60 |
| B | F0 | 1.000 | 1.000 | 0.000 | 3.87 |
| B | F1 | 0.582 | 0.582 | 0.418 | 4.11 |
| B | F2 | 0.962 | 0.962 | 0.038 | 6.89 |
| B | F3 | 0.992 | 0.983 | 0.008 | 1.10 |
| B | F4 | 0.998 | 0.998 | 0.002 | 3.87 |
| C | F0 | 0.953 | 0.950 | 0.000 | 4.28 |
| C | F1 | 0.777 | 0.767 | 0.187 | 5.09 |
| C | F2 | 0.980 | 0.937 | 0.017 | 7.33 |
| C | F3 | 0.993 | 0.830 | 0.007 | 1.06 |
| C | F4 | 0.900 | 0.900 | 0.000 | 4.28 |

## 5. B: first-token-type split (descriptive; chance-corrected rate on the comparable outcome)

| group | fa_type | n | F0 any_full | F1 any_full | F0 any_sur | F2 any_sur | F0 first_sur | F3 first_sur | F4 first_sur |
|---|---|---|---|---|---|---|---|---|---|
| A | initial_first | 453 | +0.035 | +0.066 | +0.051 | +0.093 | +0.020 | +0.009 | +0.143 |
| A | given_first | 141 | +0.043 | +0.085 | +0.085 | +0.149 | +0.035 | +0.014 | +0.078 |
| B | initial_first | 413 | +0.000 | +0.007 | +0.007 | +0.010 | +0.002 | +0.000 | +0.029 |
| B | given_first | 183 | +0.011 | +0.027 | +0.077 | +0.120 | +0.022 | +0.005 | +0.022 |
| C | initial_first | 222 | +0.423 | +0.383 | +0.514 | +0.477 | +0.252 | +0.099 | +0.432 |
| C | given_first | 78 | +0.385 | +0.372 | +0.487 | +0.603 | +0.179 | +0.038 | +0.308 |

## 6. B: teacher forcing (descriptive): all-token paper score, spec = true - mean of 5 false titles

| group | cond | true | spec [95% CI] | true - delete | first-author first token spec | median rank first token (true) | share rank<=5 |
|---|---|---|---|---|---|---|---|
| A | F0 | -0.766 | +0.440 [+0.420, +0.461] | +0.333 | +0.187 | 13 | 0.307 |
| A | F1 | -0.707 | +0.330 [+0.316, +0.345] | +0.252 | +0.449 | 155 | 0.058 |
| A | F2 | -1.257 | +0.727 [+0.690, +0.770] | +0.554 | +0.651 | 84 | 0.133 |
| A | F3 | -1.256 | +0.681 [+0.638, +0.728] | +0.556 | +0.510 | 94 | 0.120 |
| A | F4 | -0.926 | +0.775 [+0.719, +0.830] | +0.647 | +0.771 | 27 | 0.250 |
| B | F0 | -1.020 | +0.205 [+0.189, +0.220] | +0.147 | +0.123 | 15 | 0.248 |
| B | F1 | -0.897 | +0.148 [+0.135, +0.160] | +0.101 | +0.156 | 358 | 0.037 |
| B | F2 | -1.738 | +0.319 [+0.290, +0.348] | +0.204 | +0.226 | 273 | 0.062 |
| B | F3 | -1.745 | +0.299 [+0.268, +0.329] | +0.210 | +0.173 | 295 | 0.058 |
| B | F4 | -1.469 | +0.322 [+0.289, +0.356] | +0.249 | +0.254 | 75 | 0.130 |
| C | F0 | -0.721 | +0.527 [+0.494, +0.562] | +0.394 | +0.359 | 10 | 0.390 |
| C | F1 | -0.668 | +0.395 [+0.370, +0.420] | +0.297 | +0.832 | 37 | 0.197 |
| C | F2 | -1.179 | +0.884 [+0.825, +0.940] | +0.647 | +1.141 | 18 | 0.363 |
| C | F3 | -1.124 | +0.882 [+0.799, +0.968] | +0.699 | +0.897 | 27 | 0.270 |
| C | F4 | -0.734 | +0.974 [+0.883, +1.073] | +0.804 | +1.171 | 5 | 0.517 |

## 7. D: contrasts (all tokens of the scored set; group C low power, 228 papers)

| group | version | contrast | estimate [95% CI] | p | n |
|---|---|---|---|---|---|
| A | true | G1 (PRIMARY) | +0.167 [+0.147, +0.185] | 0.0005 | 600 |
| A | true | G2 | +0.284 [+0.260, +0.308] | 0.0005 | 600 |
| A | true | true1_minus_none | +0.086 [+0.071, +0.100] | 0.0005 | 600 |
| A | true | other1_minus_none | -0.080 [-0.093, -0.067] | 0.0005 | 600 |
| A | true | true2_minus_none | +0.147 [+0.127, +0.167] | 0.0005 | 600 |
| A | true | other2_minus_none | -0.136 [-0.155, -0.119] | 0.0005 | 600 |
| A | true | shuffle2_minus_true2 | -0.009 [-0.014, -0.004] | 0.0005 | 600 |
| A | true | shuffle2x_minus_true2 | -0.016 [-0.023, -0.009] | 0.0005 | 600 |
| A | true | reverse_minus_none_first | +0.053 [+0.034, +0.070] | 0.0005 | 600 |
| A | spec | G1 | +0.012 [-0.001, +0.025] | 0.0620 | 600 |
| A | spec | G2 | +0.032 [+0.015, +0.047] | 0.0005 | 600 |
| A | spec | true1_minus_none | -0.082 [-0.094, -0.070] | 0.0005 | 600 |
| A | spec | other1_minus_none | -0.094 [-0.104, -0.083] | 0.0005 | 600 |
| A | spec | true2_minus_none | -0.116 [-0.132, -0.101] | 0.0005 | 600 |
| A | spec | other2_minus_none | -0.148 [-0.164, -0.133] | 0.0005 | 600 |
| A | spec | shuffle2_minus_true2 | -0.006 [-0.011, -0.001] | 0.0110 | 600 |
| A | spec | shuffle2x_minus_true2 | -0.009 [-0.016, -0.002] | 0.0120 | 600 |
| A | spec | reverse_minus_none_first | -0.212 [-0.232, -0.193] | 0.0005 | 600 |
| A | delete | G1 | +0.223 [+0.201, +0.247] | 0.0005 | 600 |
| A | delete | G2 | +0.329 [+0.304, +0.357] | 0.0005 | 600 |
| A | delete | true1_minus_none | +0.145 [+0.125, +0.166] | 0.0005 | 600 |
| A | delete | other1_minus_none | -0.079 [-0.091, -0.066] | 0.0005 | 600 |
| A | delete | true2_minus_none | +0.239 [+0.216, +0.264] | 0.0005 | 600 |
| A | delete | other2_minus_none | -0.090 [-0.107, -0.074] | 0.0005 | 600 |
| A | delete | shuffle2_minus_true2 | -0.001 [-0.008, +0.005] | 0.6850 | 600 |
| A | delete | shuffle2x_minus_true2 | -0.009 [-0.020, +0.001] | 0.0780 | 600 |
| A | delete | reverse_minus_none_first | +0.244 [+0.219, +0.267] | 0.0005 | 600 |
| A | true_minus_delete | G1 | -0.057 [-0.073, -0.040] | 0.0005 | 600 |
| A | true_minus_delete | G2 | -0.045 [-0.065, -0.027] | 0.0005 | 600 |
| A | true_minus_delete | true1_minus_none | -0.058 [-0.074, -0.043] | 0.0005 | 600 |
| A | true_minus_delete | other1_minus_none | -0.002 [-0.014, +0.011] | 0.8250 | 600 |
| A | true_minus_delete | true2_minus_none | -0.092 [-0.112, -0.074] | 0.0005 | 600 |
| A | true_minus_delete | other2_minus_none | -0.046 [-0.065, -0.029] | 0.0005 | 600 |
| A | true_minus_delete | shuffle2_minus_true2 | -0.007 [-0.014, -0.000] | 0.0500 | 600 |
| A | true_minus_delete | shuffle2x_minus_true2 | -0.007 [-0.017, +0.003] | 0.1720 | 600 |
| A | true_minus_delete | reverse_minus_none_first | -0.191 [-0.214, -0.166] | 0.0005 | 600 |
| B | true | G1 | +0.186 [+0.168, +0.204] | 0.0005 | 600 |
| B | true | G2 | +0.274 [+0.252, +0.297] | 0.0005 | 600 |
| B | true | true1_minus_none | +0.101 [+0.086, +0.117] | 0.0005 | 600 |
| B | true | other1_minus_none | -0.084 [-0.097, -0.072] | 0.0005 | 600 |
| B | true | true2_minus_none | +0.154 [+0.133, +0.174] | 0.0005 | 600 |
| B | true | other2_minus_none | -0.120 [-0.137, -0.103] | 0.0005 | 600 |
| B | true | shuffle2_minus_true2 | -0.002 [-0.005, +0.001] | 0.1740 | 600 |
| B | true | shuffle2x_minus_true2 | -0.004 [-0.009, +0.000] | 0.0710 | 600 |
| B | true | reverse_minus_none_first | +0.125 [+0.105, +0.146] | 0.0005 | 600 |
| B | spec | G1 | +0.010 [+0.001, +0.019] | 0.0230 | 600 |
| B | spec | G2 | +0.030 [+0.018, +0.043] | 0.0005 | 600 |
| B | spec | true1_minus_none | -0.057 [-0.067, -0.045] | 0.0005 | 600 |
| B | spec | other1_minus_none | -0.067 [-0.076, -0.058] | 0.0005 | 600 |
| B | spec | true2_minus_none | -0.067 [-0.080, -0.053] | 0.0005 | 600 |
| B | spec | other2_minus_none | -0.097 [-0.110, -0.085] | 0.0005 | 600 |
| B | spec | shuffle2_minus_true2 | -0.001 [-0.004, +0.002] | 0.5330 | 600 |
| B | spec | shuffle2x_minus_true2 | -0.001 [-0.006, +0.003] | 0.6470 | 600 |
| B | spec | reverse_minus_none_first | -0.114 [-0.130, -0.098] | 0.0005 | 600 |
| B | delete | G1 | +0.212 [+0.193, +0.233] | 0.0005 | 600 |
| B | delete | G2 | +0.290 [+0.267, +0.313] | 0.0005 | 600 |
| B | delete | true1_minus_none | +0.137 [+0.120, +0.155] | 0.0005 | 600 |
| B | delete | other1_minus_none | -0.075 [-0.088, -0.062] | 0.0005 | 600 |
| B | delete | true2_minus_none | +0.199 [+0.179, +0.219] | 0.0005 | 600 |
| B | delete | other2_minus_none | -0.091 [-0.108, -0.075] | 0.0005 | 600 |
| B | delete | shuffle2_minus_true2 | -0.001 [-0.005, +0.003] | 0.7170 | 600 |
| B | delete | shuffle2x_minus_true2 | +0.001 [-0.005, +0.008] | 0.6400 | 600 |
| B | delete | reverse_minus_none_first | +0.226 [+0.201, +0.251] | 0.0005 | 600 |
| B | true_minus_delete | G1 | -0.026 [-0.040, -0.013] | 0.0005 | 600 |
| B | true_minus_delete | G2 | -0.016 [-0.031, -0.000] | 0.0440 | 600 |
| B | true_minus_delete | true1_minus_none | -0.036 [-0.050, -0.023] | 0.0005 | 600 |
| B | true_minus_delete | other1_minus_none | -0.010 [-0.021, +0.002] | 0.0950 | 600 |
| B | true_minus_delete | true2_minus_none | -0.045 [-0.061, -0.028] | 0.0005 | 600 |
| B | true_minus_delete | other2_minus_none | -0.029 [-0.045, -0.014] | 0.0005 | 600 |
| B | true_minus_delete | shuffle2_minus_true2 | -0.001 [-0.006, +0.004] | 0.6080 | 600 |
| B | true_minus_delete | shuffle2x_minus_true2 | -0.006 [-0.013, +0.001] | 0.0930 | 600 |
| B | true_minus_delete | reverse_minus_none_first | -0.101 [-0.121, -0.082] | 0.0005 | 600 |
| C (low power) | true | G1 | +0.124 [+0.090, +0.156] | 0.0005 | 227 |
| C (low power) | true | G2 | +0.280 [+0.239, +0.320] | 0.0005 | 201 |
| C (low power) | true | true1_minus_none | +0.058 [+0.026, +0.089] | 0.0005 | 227 |
| C (low power) | true | other1_minus_none | -0.066 [-0.093, -0.041] | 0.0005 | 227 |
| C (low power) | true | true2_minus_none | +0.169 [+0.135, +0.211] | 0.0005 | 201 |
| C (low power) | true | other2_minus_none | -0.110 [-0.143, -0.076] | 0.0005 | 201 |
| C (low power) | true | shuffle2_minus_true2 | -0.013 [-0.030, -0.001] | 0.0330 | 201 |
| C (low power) | true | shuffle2x_minus_true2 | -0.028 [-0.049, -0.012] | 0.0005 | 201 |
| C (low power) | true | reverse_minus_none_first | +0.026 [-0.006, +0.058] | 0.1190 | 174 |
| C (low power) | spec | G1 | -0.030 [-0.057, -0.000] | 0.0490 | 227 |
| C (low power) | spec | G2 | +0.004 [-0.031, +0.041] | 0.8470 | 201 |
| C (low power) | spec | true1_minus_none | -0.120 [-0.148, -0.093] | 0.0005 | 227 |
| C (low power) | spec | other1_minus_none | -0.090 [-0.110, -0.070] | 0.0005 | 227 |
| C (low power) | spec | true2_minus_none | -0.135 [-0.175, -0.094] | 0.0005 | 201 |
| C (low power) | spec | other2_minus_none | -0.139 [-0.166, -0.111] | 0.0005 | 201 |
| C (low power) | spec | shuffle2_minus_true2 | -0.003 [-0.014, +0.008] | 0.5710 | 201 |
| C (low power) | spec | shuffle2x_minus_true2 | -0.013 [-0.030, +0.003] | 0.1150 | 201 |
| C (low power) | spec | reverse_minus_none_first | -0.365 [-0.415, -0.318] | 0.0005 | 174 |
| C (low power) | delete | G1 | +0.260 [+0.214, +0.304] | 0.0005 | 227 |
| C (low power) | delete | G2 | +0.402 [+0.345, +0.461] | 0.0005 | 201 |
| C (low power) | delete | true1_minus_none | +0.169 [+0.128, +0.212] | 0.0005 | 227 |
| C (low power) | delete | other1_minus_none | -0.091 [-0.114, -0.067] | 0.0005 | 227 |
| C (low power) | delete | true2_minus_none | +0.317 [+0.268, +0.369] | 0.0005 | 201 |
| C (low power) | delete | other2_minus_none | -0.086 [-0.117, -0.055] | 0.0005 | 201 |
| C (low power) | delete | shuffle2_minus_true2 | -0.012 [-0.028, +0.002] | 0.0840 | 201 |
| C (low power) | delete | shuffle2x_minus_true2 | -0.033 [-0.052, -0.014] | 0.0005 | 201 |
| C (low power) | delete | reverse_minus_none_first | +0.358 [+0.308, +0.408] | 0.0005 | 174 |
| C (low power) | true_minus_delete | G1 | -0.136 [-0.171, -0.100] | 0.0005 | 227 |
| C (low power) | true_minus_delete | G2 | -0.123 [-0.167, -0.079] | 0.0005 | 201 |
| C (low power) | true_minus_delete | true1_minus_none | -0.111 [-0.147, -0.076] | 0.0005 | 227 |
| C (low power) | true_minus_delete | other1_minus_none | +0.025 [+0.002, +0.048] | 0.0330 | 227 |
| C (low power) | true_minus_delete | true2_minus_none | -0.147 [-0.187, -0.107] | 0.0005 | 201 |
| C (low power) | true_minus_delete | other2_minus_none | -0.025 [-0.054, +0.007] | 0.1270 | 201 |
| C (low power) | true_minus_delete | shuffle2_minus_true2 | -0.001 [-0.013, +0.010] | 0.8970 | 201 |
| C (low power) | true_minus_delete | shuffle2x_minus_true2 | +0.005 [-0.011, +0.021] | 0.5490 | 201 |
| C (low power) | true_minus_delete | reverse_minus_none_first | -0.332 [-0.384, -0.284] | 0.0005 | 174 |
| all | true | G1 | +0.168 [+0.156, +0.180] | 0.0005 | 1427 |
| all | true | G2 | +0.279 [+0.264, +0.295] | 0.0005 | 1401 |
| all | true | true1_minus_none | +0.088 [+0.078, +0.099] | 0.0005 | 1427 |
| all | true | other1_minus_none | -0.080 [-0.088, -0.071] | 0.0005 | 1427 |
| all | true | true2_minus_none | +0.153 [+0.139, +0.168] | 0.0005 | 1401 |
| all | true | other2_minus_none | -0.126 [-0.137, -0.114] | 0.0005 | 1401 |
| all | true | shuffle2_minus_true2 | -0.006 [-0.010, -0.004] | 0.0005 | 1401 |
| all | true | shuffle2x_minus_true2 | -0.013 [-0.017, -0.008] | 0.0005 | 1401 |
| all | true | reverse_minus_none_first | +0.081 [+0.068, +0.094] | 0.0005 | 1374 |
| all | spec | G1 | +0.005 [-0.003, +0.013] | 0.2700 | 1427 |
| all | spec | G2 | +0.027 [+0.017, +0.037] | 0.0005 | 1401 |
| all | spec | true1_minus_none | -0.077 [-0.085, -0.069] | 0.0005 | 1427 |
| all | spec | other1_minus_none | -0.082 [-0.088, -0.075] | 0.0005 | 1427 |
| all | spec | true2_minus_none | -0.098 [-0.108, -0.087] | 0.0005 | 1401 |
| all | spec | other2_minus_none | -0.125 [-0.134, -0.115] | 0.0005 | 1401 |
| all | spec | shuffle2_minus_true2 | -0.003 [-0.006, -0.001] | 0.0130 | 1401 |
| all | spec | shuffle2x_minus_true2 | -0.006 [-0.010, -0.002] | 0.0040 | 1401 |
| all | spec | reverse_minus_none_first | -0.189 [-0.202, -0.175] | 0.0005 | 1374 |
| all | delete | G1 | +0.224 [+0.210, +0.240] | 0.0005 | 1427 |
| all | delete | G2 | +0.323 [+0.306, +0.341] | 0.0005 | 1401 |
| all | delete | true1_minus_none | +0.146 [+0.132, +0.159] | 0.0005 | 1427 |
| all | delete | other1_minus_none | -0.079 [-0.088, -0.070] | 0.0005 | 1427 |
| all | delete | true2_minus_none | +0.233 [+0.217, +0.250] | 0.0005 | 1401 |
| all | delete | other2_minus_none | -0.090 [-0.101, -0.079] | 0.0005 | 1401 |
| all | delete | shuffle2_minus_true2 | -0.003 [-0.007, +0.001] | 0.1690 | 1401 |
| all | delete | shuffle2x_minus_true2 | -0.008 [-0.014, -0.002] | 0.0060 | 1401 |
| all | delete | reverse_minus_none_first | +0.250 [+0.234, +0.265] | 0.0005 | 1374 |
| all | true_minus_delete | G1 | -0.057 [-0.067, -0.046] | 0.0005 | 1427 |
| all | true_minus_delete | G2 | -0.044 [-0.056, -0.032] | 0.0005 | 1401 |
| all | true_minus_delete | true1_minus_none | -0.058 [-0.068, -0.047] | 0.0005 | 1427 |
| all | true_minus_delete | other1_minus_none | -0.001 [-0.009, +0.008] | 0.8300 | 1427 |
| all | true_minus_delete | true2_minus_none | -0.080 [-0.092, -0.068] | 0.0005 | 1401 |
| all | true_minus_delete | other2_minus_none | -0.036 [-0.047, -0.025] | 0.0005 | 1401 |
| all | true_minus_delete | shuffle2_minus_true2 | -0.004 [-0.008, +0.000] | 0.0660 | 1401 |
| all | true_minus_delete | shuffle2x_minus_true2 | -0.005 [-0.010, +0.001] | 0.0960 | 1401 |
| all | true_minus_delete | reverse_minus_none_first | -0.169 [-0.184, -0.154] | 0.0005 | 1374 |
| A-B | true | G1 | -0.019 [-0.045, +0.007] | 0.1460 | 600 |
| C-A (low power) | true | G1 | -0.042 [-0.081, -0.005] | 0.0280 | 227 |
| A-B | true | G2 | +0.010 [-0.022, +0.042] | 0.5460 | 600 |
| C-A (low power) | true | G2 | -0.004 [-0.050, +0.042] | 0.8700 | 201 |
| A-B | true | reverse_minus_none_first | -0.072 [-0.100, -0.044] | 0.0005 | 600 |
| C-A (low power) | true | reverse_minus_none_first | -0.027 [-0.065, +0.010] | 0.1480 | 174 |
| A-B | true | true1_minus_none | -0.015 [-0.036, +0.006] | 0.1570 | 600 |
| C-A (low power) | true | true1_minus_none | -0.028 [-0.063, +0.006] | 0.1080 | 227 |
| A-B | spec | G1 | +0.001 [-0.013, +0.017] | 0.8460 | 600 |
| C-A (low power) | spec | G1 | -0.042 [-0.072, -0.010] | 0.0080 | 227 |
| A-B | spec | G2 | +0.002 [-0.018, +0.021] | 0.8640 | 600 |
| C-A (low power) | spec | G2 | -0.028 [-0.067, +0.013] | 0.1700 | 201 |
| A-B | spec | reverse_minus_none_first | -0.098 [-0.123, -0.073] | 0.0005 | 600 |
| C-A (low power) | spec | reverse_minus_none_first | -0.153 [-0.205, -0.101] | 0.0005 | 174 |
| A-B | spec | true1_minus_none | -0.025 [-0.042, -0.009] | 0.0010 | 600 |
| C-A (low power) | spec | true1_minus_none | -0.038 [-0.069, -0.008] | 0.0090 | 227 |
| A-B | delete | G1 | +0.011 [-0.018, +0.041] | 0.4280 | 600 |
| C-A (low power) | delete | G1 | +0.037 [-0.015, +0.086] | 0.1550 | 227 |
| A-B | delete | G2 | +0.040 [+0.007, +0.075] | 0.0100 | 600 |
| C-A (low power) | delete | G2 | +0.073 [+0.005, +0.138] | 0.0350 | 201 |
| A-B | delete | reverse_minus_none_first | +0.018 [-0.018, +0.052] | 0.3300 | 600 |
| C-A (low power) | delete | reverse_minus_none_first | +0.114 [+0.056, +0.171] | 0.0005 | 174 |
| A-B | delete | true1_minus_none | +0.007 [-0.018, +0.033] | 0.5750 | 600 |
| C-A (low power) | delete | true1_minus_none | +0.025 [-0.020, +0.070] | 0.2890 | 227 |
| A-B | true_minus_delete | G1 | -0.030 [-0.051, -0.010] | 0.0060 | 600 |
| C-A (low power) | true_minus_delete | G1 | -0.079 [-0.118, -0.039] | 0.0005 | 227 |
| A-B | true_minus_delete | G2 | -0.030 [-0.055, -0.006] | 0.0150 | 600 |
| C-A (low power) | true_minus_delete | G2 | -0.077 [-0.125, -0.027] | 0.0010 | 201 |
| A-B | true_minus_delete | reverse_minus_none_first | -0.090 [-0.120, -0.058] | 0.0005 | 600 |
| C-A (low power) | true_minus_delete | reverse_minus_none_first | -0.141 [-0.197, -0.089] | 0.0005 | 174 |
| A-B | true_minus_delete | true1_minus_none | -0.022 [-0.042, -0.001] | 0.0420 | 600 |
| C-A (low power) | true_minus_delete | true1_minus_none | -0.053 [-0.092, -0.015] | 0.0050 | 227 |

### D first scored author, first token (beside the main score)

| group | version | contrast | estimate [95% CI] | n |
|---|---|---|---|---|
| A | true | G1 | +0.207 [+0.155, +0.262] | 600 |
| A | spec | G1 | +0.029 [+0.001, +0.059] | 600 |
| A | true | G2 | +0.271 [+0.228, +0.314] | 600 |
| A | spec | G2 | +0.028 [+0.004, +0.053] | 600 |
| A | true | true1_minus_none | +0.128 [+0.082, +0.173] | 600 |
| A | spec | true1_minus_none | -0.054 [-0.095, -0.014] | 600 |
| B | true | G1 | +0.315 [+0.262, +0.370] | 600 |
| B | spec | G1 | +0.001 [-0.022, +0.025] | 600 |
| B | true | G2 | +0.375 [+0.324, +0.430] | 600 |
| B | spec | G2 | +0.010 [-0.008, +0.028] | 600 |
| B | true | true1_minus_none | +0.135 [+0.086, +0.181] | 600 |
| B | spec | true1_minus_none | -0.120 [-0.152, -0.086] | 600 |
| C | true | G1 | +0.272 [+0.179, +0.363] | 228 |
| C | spec | G1 | +0.058 [+0.004, +0.111] | 228 |
| C | true | G2 | +0.402 [+0.322, +0.484] | 228 |
| C | spec | G2 | +0.072 [+0.021, +0.124] | 228 |
| C | true | true1_minus_none | +0.175 [+0.085, +0.266] | 228 |
| C | spec | true1_minus_none | -0.061 [-0.141, +0.020] | 228 |
| all | true | G1 | +0.263 [+0.229, +0.299] | 1428 |
| all | spec | G1 | +0.022 [+0.004, +0.041] | 1428 |
| all | true | G2 | +0.336 [+0.304, +0.369] | 1428 |
| all | spec | G2 | +0.027 [+0.011, +0.043] | 1428 |
| all | true | true1_minus_none | +0.138 [+0.107, +0.170] | 1428 |
| all | spec | true1_minus_none | -0.083 [-0.110, -0.056] | 1428 |

### D first-token-type split of G(1) and G(2), true title

| group | fa_type | contrast | estimate [95% CI] | n |
|---|---|---|---|---|
| A | initial_first | G1 | +0.209 [+0.189, +0.229] | 431 |
| A | initial_first | G2 | +0.296 [+0.270, +0.324] | 431 |
| B | initial_first | G1 | +0.210 [+0.191, +0.231] | 350 |
| B | initial_first | G2 | +0.275 [+0.250, +0.303] | 350 |
| C | initial_first | G1 | +0.172 [+0.142, +0.203] | 168 |
| C | initial_first | G2 | +0.289 [+0.246, +0.333] | 154 |
| A-B | initial_first | G1 | -0.001 [-0.029, +0.027] | 350 |
| A-B | initial_first | G2 | +0.021 [-0.016, +0.060] | 350 |
| A | given_first | G1 | +0.055 [+0.016, +0.093] | 167 |
| A | given_first | G2 | +0.247 [+0.194, +0.300] | 167 |
| B | given_first | G1 | +0.147 [+0.115, +0.181] | 245 |
| B | given_first | G2 | +0.265 [+0.226, +0.303] | 245 |
| C | given_first | G1 | -0.011 [-0.093, +0.064] | 59 |
| C | given_first | G2 | +0.247 [+0.146, +0.346] | 47 |
| A-B | given_first | G1 | -0.092 [-0.142, -0.043] | 167 |
| A-B | given_first | G2 | -0.018 [-0.083, +0.048] | 167 |

### D levels (paper score, true title)

| group | P_true1 | P_true2 | P_other1 | P_other2 | P_none | P_shuffle2 | P_shuffle2x | P_reverse | P_none_from2 | P_none_from3 | P_none_first |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | -0.745 | -0.678 | -0.911 | -0.961 | -0.825 | -0.686 | -0.693 | -0.747 | -0.831 | -0.825 | -0.800 |
| B | -0.931 | -0.872 | -1.117 | -1.146 | -1.038 | -0.874 | -0.876 | -0.929 | -1.032 | -1.025 | -1.054 |
| C | -0.692 | -0.619 | -0.816 | -0.898 | -0.741 | -0.632 | -0.647 | -0.631 | -0.750 | -0.788 | -0.656 |

## 8. D generation check (secondary): true vs control first author given, greedy rest, authors 2..n

| group | measure | G_true1 | G_other1 | difference [95% CI] |
|---|---|---|---|---|
| A | any_rest_full | 0.118 | 0.015 | +0.103 [+0.076, +0.130] |
| A | recall_rest | 0.058 | 0.005 | +0.053 [+0.039, +0.068] |
| A | any_rest_sur | 0.172 | 0.023 | +0.148 [+0.116, +0.180] |
| A | fab_any | 0.982 | 0.998 | -0.017 [-0.028, -0.006] |
| B | any_rest_full | 0.025 | 0.003 | +0.022 [+0.010, +0.034] |
| B | recall_rest | 0.009 | 0.001 | +0.008 [+0.003, +0.014] |
| B | any_rest_sur | 0.105 | 0.020 | +0.085 [+0.056, +0.112] |
| B | fab_any | 0.997 | 1.000 | -0.003 [-0.009, +0.000] |
| C | any_rest_full | 0.487 | 0.127 | +0.360 [+0.282, +0.436] |
| C | recall_rest | 0.221 | 0.036 | +0.185 [+0.143, +0.230] |
| C | any_rest_sur | 0.557 | 0.145 | +0.412 [+0.337, +0.488] |
| C | fab_any | 0.890 | 0.991 | -0.101 [-0.149, -0.058] |

## 9. D16-5 control exclusion (share of the eligible control pool removed because it shares an author surname)

| item | rule | group | papers | mean share excluded | pooled share | papers with >=1 excluded | chosen controls sharing a surname |
|---|---|---|---|---|---|---|---|
| B | ctrl | A | 600 | 0.0074 | 0.0035 | 0.317 | 0 |
| B | ctrl | B | 600 | 0.0203 | 0.0077 | 0.363 | 0 |
| B | ctrl | C | 300 | 0.0155 | 0.0088 | 0.467 | 0 |
| B | ctrl_f4 | A | 600 | 0.0095 | 0.0056 | 0.157 | 0 |
| B | ctrl_f4 | B | 600 | 0.0165 | 0.0128 | 0.207 | 0 |
| B | ctrl_f4 | C | 300 | 0.0162 | 0.0118 | 0.293 | 0 |
| D | ctrl | A | 600 | 0.0100 | 0.0065 | 0.440 | 0 |
| D | ctrl | B | 600 | 0.0334 | 0.0179 | 0.530 | 0 |
| D | ctrl | C | 228 | 0.0230 | 0.0142 | 0.522 | 0 |
| B | ctrl | all | 1500 | 0.0142 | 0.0061 | 0.365 | 0 |
| B | ctrl_f4 | all | 1500 | 0.0136 | 0.0097 | 0.204 | 0 |
| D | ctrl | all | 1428 | 0.0219 | 0.0125 | 0.491 | 0 |

## 10. Exploratory R0 check (F0, all B shards; not confirmatory)

| group | measure | estimate [95% CI] | n |
|---|---|---|---|
| A | any_full | 0.040 [0.025, 0.056] | 600 |
| A | first_full | 0.015 [0.007, 0.025] | 600 |
| A | co_only_full | 0.025 [0.013, 0.038] | 600 |
| A | c_any_full | 0.003 [0.000, 0.009] | 600 |
| A | corr_any_full | 0.037 [0.020, 0.054] | 600 |
| A | any_fs | 0.070 [0.050, 0.092] | 600 |
| A | first_fs | 0.027 [0.014, 0.041] | 600 |
| A | co_only_fs | 0.043 [0.028, 0.061] | 600 |
| A | c_any_fs | 0.012 [0.004, 0.020] | 600 |
| A | corr_any_fs | 0.058 [0.036, 0.081] | 600 |
| B | any_full | 0.005 [0.000, 0.011] | 600 |
| B | first_full | 0.000 [0.000, 0.000] | 600 |
| B | co_only_full | 0.005 [0.000, 0.011] | 600 |
| B | c_any_full | 0.002 [0.000, 0.005] | 600 |
| B | corr_any_full | 0.003 [-0.003, 0.010] | 600 |
| B | any_fs | 0.042 [0.024, 0.063] | 600 |
| B | first_fs | 0.013 [0.005, 0.023] | 600 |
| B | co_only_fs | 0.028 [0.013, 0.046] | 600 |
| B | c_any_fs | 0.013 [0.005, 0.023] | 600 |
| B | corr_any_fs | 0.028 [0.009, 0.048] | 600 |
| A+B (R0) | any_full | 0.022 [0.014, 0.031] | 1200 |
| A+B (R0) | first_full | 0.007 [0.003, 0.012] | 1200 |
| A+B (R0) | co_only_full | 0.015 [0.008, 0.022] | 1200 |
| A+B (R0) | c_any_full | 0.003 [0.000, 0.006] | 1200 |
| A+B (R0) | corr_any_full | 0.020 [0.011, 0.029] | 1200 |
| A+B (R0) | any_fs | 0.056 [0.041, 0.073] | 1200 |
| A+B (R0) | first_fs | 0.020 [0.012, 0.029] | 1200 |
| A+B (R0) | co_only_fs | 0.036 [0.025, 0.048] | 1200 |
| A+B (R0) | c_any_fs | 0.013 [0.006, 0.019] | 1200 |
| A+B (R0) | corr_any_fs | 0.043 [0.028, 0.059] | 1200 |
| C (R1, reference) | any_full | 0.413 [0.356, 0.469] | 300 |
| C (R1, reference) | first_full | 0.180 [0.137, 0.225] | 300 |
| C (R1, reference) | co_only_full | 0.233 [0.181, 0.283] | 300 |
| C (R1, reference) | c_any_full | 0.000 [0.000, 0.000] | 300 |
| C (R1, reference) | corr_any_full | 0.413 [0.356, 0.469] | 300 |
| C (R1, reference) | any_fs | 0.507 [0.448, 0.560] | 300 |
| C (R1, reference) | first_fs | 0.233 [0.187, 0.280] | 300 |
| C (R1, reference) | co_only_fs | 0.273 [0.223, 0.323] | 300 |
| C (R1, reference) | c_any_fs | 0.000 [0.000, 0.000] | 300 |
| C (R1, reference) | corr_any_fs | 0.507 [0.448, 0.560] | 300 |

full = full-name matcher (surname + first initial); fs = full-name OR surname-only match (old r0_prompt.py "any"); co_only = >= 1 co-author but not the first author; c_ = same output vs the fixed control paper; corr = true - chance.

## 11. Open choices (not specified by the plan; most literal reading used)
- Holm-adjusted CI: percentile interval at level alpha/(5 - j) for the test at Holm step j (ascending p, step-down); each B condition is one test with intersection-union p = max(p Delta_A, p DiD). Bonferroni (0.01) CIs and plain 95% CIs reported beside.
- Percentile p-value (two-sided) = groups_core.Engine.pval, floor 1/2000; bootstrap = the archived Engine draw (seed 391), shared by B and D.
- Fabrication for the interpretability rule: share of papers with >= 1 generated item matching no true author, matcher comparable to the outcome (full for F1, surname for F2/F3/F4, same matcher for F0); rule applied as Delta fabrication_A(c) > 0 and > Delta_A(c) (point estimates; 'raises fabrication' read as a positive change). Item shares and empty-answer shares reported beside.
- F0 comparison outcomes: F2 vs F0 any_sur (surname-only matcher on the F0 list); F3/F4 vs F0 first_sur (first author surname anywhere in the F0 list, D16-6); chance column of the same rule (F4 uses the same-initial control, F0 the +-1-author control).
- Group C: TF scores use unwritten authors only (plan section 1); C generation outcomes use all authors (generation is not split by written status). C in B/D is reported, not part of any decision.
- D "first-author first-token version": the first SCORED author (author 2 for k = 1, author 3 for k = 2), first token, since prefix authors are never scored.
- D "P_reverse vs forward": reverse_minus_none_first = score(author 1 | prefix authors 2..n) - score(author 1 | no prefix); forward comparator = true1_minus_none = score(authors 2..n | author 1) - score(authors 2..n | no prefix) (both relative to P_none; the plan names no baseline).
- D title-specific version = (true - mean of 5 false titles) of P_true1 minus the same of P_other1; deleted-title version = G on the deleted-title prompts; true_minus_delete reported as well.
- fa_type "other" (B 10, D 7 papers) is included in the pooled analysis and omitted from the split.
- Paper with a nan cell (e.g. F4 TF when the first author has no given name) is dropped from that cell only.

## 12. Parse / shard checks

```
item  shard   gen_script  rows  cells_differing_parsed_vs_gen                                                                   parity batch_vs_single
   B      0 a0f8dd8320c4   250                            157 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B      1 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   B      2 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B      3 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B      4 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B      5 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B      6 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B      7 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B      8 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B      9 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   B     10 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             4/4
   B     11 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     12 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     13 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     14 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B     15 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B     16 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             4/4
   B     17 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     18 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     19 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B     20 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   B     21 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     22 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B     23 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B     24 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     25 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B     26 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   B     27 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     28 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   B     29 db7c73863595   250                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   D      0 a0f8dd8320c4   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D      1 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D      2 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D      3 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D      4 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D      5 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D      6 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D      7 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   D      8 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D      9 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     10 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   D     11 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     12 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D     13 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     14 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     15 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     16 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     17 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D     18 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D     19 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     20 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     21 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             2/4
   D     22 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     23 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   D     24 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     25 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             0/4
   D     26 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
   D     27 db7c73863595   100                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             3/4
   D     28 db7c73863595    56                              0 true:OK;false_0:OK;false_1:OK;false_2:OK;false_3:OK;false_4:OK;delete:OK             1/4
```
