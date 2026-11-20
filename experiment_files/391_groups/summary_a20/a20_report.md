# Addendum 20 (LOCKED) — H2 test with fictitious titles: main result

Generated 2026-11-20 13:56 by `~/jlens_work/15_h2fict/h2_main_analyze.py` (sha256 95399102aa16d360…). Addendum: `391_groups/config/prereg_addendum20.md` (sha256 fee691de801c7c0e…, verified); title set `h2_fictitious/v3/selected_v3b.csv` (sha256 7b8dd31da3611359…, verified). Exploratory status: none — this is the locked confirmatory analysis; everything outside §3 of the addendum is secondary / descriptive.

## 1. Primary result (target group, `final` L63, mean log10(1/rank) per name token)

| quantity | estimate [95 % team-bootstrap CI] |
|---|---|
| φ_T = ΣA / ΣG (fictitious share of the true − false gap) | **+0.751 [+0.723, +0.778]** |
| R̄_T = mean(S_true − S_fict) | **+0.106 [+0.094, +0.118]** |
| Ḡ_T = mean(S_true − F̄) | +0.425 [+0.406, +0.445] |
| Ā_T = mean(S_fict − F̄) | +0.319 [+0.301, +0.338] |
| n target papers | 566 |

**Decision-rule row:** Rbar_T CI > 0 and phi_T >= 0.5 → **H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal** (not borderline: φ_T CI does not cross 0.3 or 0.5).

Rule (addendum 20 §3, fixed before the run): verdict by the point estimate φ̂_T, read only when R̄_T's 95 % CI lies entirely above 0; φ̂_T < 0.3 → strongly supported; 0.3 ≤ φ̂_T < 0.5 → partly supported (limited weight); φ̂_T ≥ 0.5 → partly supported (meaning explains most); R̄_T CI includes 0 → not supported; R̄_T CI entirely below 0 → refuted (reversed). Borderline = φ_T CI crosses 0.3 or 0.5.

**Sensitivity analyses that would change the verdict:** none (the verdict is unchanged in every sensitivity analysis a–f).

## 2. Secondary comparisons (CIs; no verdict of their own)

**S1 control group:** φ_C = +0.770 [+0.727, +0.814], R̄_C = +0.050 [+0.039, +0.061], Ḡ_C = +0.217 [+0.201, +0.234], n = 561.

**S2 recognition and identity (within-bin target − control, weights n_t·n_c/(n_t+n_c)):** R_T − R_C = +0.056 [+0.039, +0.072] (n 566 T / 561 C); φ_T − φ_C (per-bin ratio of sums, bin-weighted) = -0.022 [-0.081, +0.033]; plain φ_T − φ_C (pooled ratios, descriptive) = -0.019 [-0.071, +0.030]; G_T − G_C = +0.208 [+0.184, +0.234]; A_T − A_C = +0.152 [+0.130, +0.174]. H2 predicts R_T − R_C > 0.

**S3 layer profile (name positions):**

| readout | layer | φ target | R̄ target | φ control | R̄ control |
|---|---|---|---|---|---|
| final | L63 | +0.751 [+0.723, +0.778] | +0.106 [+0.094, +0.118] | +0.770 [+0.727, +0.814] | +0.050 [+0.039, +0.061] |
| logit | L24 | +1.378 [+0.489, +4.814] | -0.002 [-0.006, +0.002] | +5.702 [-14.839, +22.643] | -0.003 [-0.007, +0.001] |
| logit | L32 | +0.641 [-0.217, +1.260] | +0.004 [-0.001, +0.009] | +0.611 [-0.966, +2.114] | +0.003 [-0.002, +0.008] |
| logit | L40 | +1.134 [-1.295, +4.915] | -0.001 [-0.006, +0.004] | +2.324 [-7.391, +12.536] | -0.001 [-0.006, +0.004] |
| logit | L48 | +1.596 [-5.314, +8.124] | -0.003 [-0.008, +0.002] | +0.451 [-4.259, +5.493] | +0.002 [-0.003, +0.007] |
| logit | L56 | +0.809 [+0.729, +0.898] | +0.032 [+0.016, +0.048] | +0.754 [+0.639, +0.883] | +0.027 [+0.012, +0.041] |
| logit | L62 | +0.825 [+0.795, +0.855] | +0.089 [+0.073, +0.105] | +0.839 [+0.792, +0.888] | +0.045 [+0.030, +0.060] |
| jlens_public | L24 | +1.167 [+0.823, +1.741] | -0.003 [-0.009, +0.004] | +1.754 [+1.218, +3.226] | -0.010 [-0.017, -0.004] |
| jlens_public | L32 | +1.494 [+1.182, +1.974] | -0.016 [-0.025, -0.007] | +2.519 [+1.623, +6.859] | -0.023 [-0.031, -0.014] |
| jlens_public | L40 | +0.367 [-0.270, +0.819] | +0.023 [+0.004, +0.041] | +0.281 [-2.085, +1.752] | +0.015 [-0.003, +0.034] |
| jlens_public | L48 | +5.905 [-42.381, +48.793] | -0.036 [-0.054, -0.017] | +0.890 [+0.568, +1.352] | +0.005 [-0.010, +0.020] |
| jlens_public | L56 | +0.913 [+0.782, +1.071] | +0.012 [-0.009, +0.033] | +0.725 [+0.589, +0.871] | +0.035 [+0.015, +0.056] |
| jlens_public | L62 | +0.766 [+0.736, +0.795] | +0.115 [+0.101, +0.131] | +0.763 [+0.718, +0.812] | +0.061 [+0.048, +0.075] |

φ at early layers is a ratio of small numbers (Ḡ near 0) and can be unstable; see S3_layer_profile.csv for Ḡ and Ā.

**S4 E1 tail patching, fict donor (false_0 run, aligned post-title tail replaced by the fict run at layer l):** rec_fict(l) = mean(patched − false_0) / mean(true − false_0) (denominator and rec_true(l) from the stored Stage 11 E1 run on the same papers; numerator baseline = this run's false_0).

| layer | rec_fict target | rec_true target | rec_true − rec_fict target | rec_fict control | rec_true control |
|---|---|---|---|---|---|
| L24 | +0.050 [+0.041, +0.059] | +0.070 [+0.061, +0.081] | +0.021 [+0.014, +0.028] | +0.085 [+0.067, +0.103] | +0.095 [+0.078, +0.115] |
| L32 | +0.099 [+0.087, +0.112] | +0.126 [+0.113, +0.140] | +0.027 [+0.019, +0.035] | +0.163 [+0.140, +0.185] | +0.176 [+0.153, +0.201] |
| L40 | +0.196 [+0.180, +0.213] | +0.264 [+0.245, +0.284] | +0.068 [+0.054, +0.082] | +0.295 [+0.265, +0.327] | +0.334 [+0.302, +0.368] |
| L48 | +0.626 [+0.598, +0.653] | +0.798 [+0.777, +0.818] | +0.172 [+0.149, +0.197] | +0.724 [+0.683, +0.768] | +0.862 [+0.827, +0.899] |
| L50 | +0.691 [+0.661, +0.718] | +0.907 [+0.891, +0.923] | +0.216 [+0.191, +0.244] | +0.776 [+0.732, +0.821] | +0.968 [+0.942, +0.995] |
| L52 | +0.743 [+0.715, +0.770] | +0.985 [+0.977, +0.992] | +0.241 [+0.215, +0.270] | +0.799 [+0.755, +0.843] | +1.015 [+1.000, +1.030] |
| L54 | +0.746 [+0.717, +0.774] | +1.001 [+0.997, +1.004] | +0.255 [+0.227, +0.284] | +0.780 [+0.735, +0.826] | +1.002 [+0.994, +1.010] |
| L56 | +0.744 [+0.714, +0.773] | +1.000 [+0.996, +1.003] | +0.255 [+0.227, +0.286] | +0.774 [+0.727, +0.820] | +0.996 [+0.991, +1.001] |
| L57 | +0.743 [+0.712, +0.771] | +1.000 [+0.997, +1.003] | +0.257 [+0.229, +0.288] | +0.772 [+0.726, +0.818] | +0.998 [+0.993, +1.003] |
| L58 | +0.745 [+0.714, +0.773] | +1.001 [+0.999, +1.004] | +0.256 [+0.229, +0.287] | +0.768 [+0.721, +0.813] | +0.997 [+0.992, +1.001] |
| L59 | +0.745 [+0.715, +0.773] | +1.001 [+0.999, +1.004] | +0.257 [+0.229, +0.287] | +0.770 [+0.723, +0.816] | +0.997 [+0.993, +1.001] |
| L60 | +0.743 [+0.713, +0.771] | +0.999 [+0.997, +1.002] | +0.256 [+0.228, +0.286] | +0.770 [+0.724, +0.816] | +0.997 [+0.993, +1.001] |
| L61 | +0.744 [+0.714, +0.772] | +1.000 [+0.997, +1.002] | +0.256 [+0.228, +0.286] | +0.767 [+0.720, +0.812] | +1.001 [+0.997, +1.004] |
| L62 | +0.745 [+0.715, +0.773] | +0.999 [+0.998, +1.001] | +0.254 [+0.226, +0.284] | +0.765 [+0.719, +0.811] | +1.003 [+1.000, +1.006] |
| L63 | +0.745 [+0.716, +0.773] | +1.000 [+1.000, +1.000] | +0.255 [+0.227, +0.284] | +0.767 [+0.720, +0.813] | +1.000 [+1.000, +1.000] |

L63 sanity: rec_fict(63) = 0.7453 vs (fict − false_0)/(true − false_0) = 0.7453 (target); max |paper mean patched L63 − fict| = 0.00e+00.

**S5 title-position probe (E4b setup refitted on the 9,108 true runs: ridge title residual → true L63 ":" residual, team folds (archived folds_own9108_k5s13), training-fold standardisation, alpha ∈ {0.1, 1, 10} on fold 0; each held-out paper's fold model applied to its fict (and stored false_0) title residual; gold author first tokens ranked among the cohort name-first-token vocabulary):**

| layer | group | probe(true) | probe(fict) | true − fict | true − false_0 |
|---|---|---|---|---|---|
| L16 | target | -1.124 [-1.169, -1.081] | -1.148 [-1.195, -1.104] | +0.024 [+0.009, +0.037] | +0.058 [+0.040, +0.075] |
| L16 | control | -1.243 [-1.297, -1.189] | -1.253 [-1.307, -1.200] | +0.010 [-0.006, +0.026] | +0.055 [+0.035, +0.074] |
| L16 | T − C (within bin) | | | +0.014 [-0.008, +0.036] | |
| L24 | target | -1.121 [-1.165, -1.079] | -1.146 [-1.192, -1.102] | +0.025 [+0.011, +0.039] | +0.069 [+0.052, +0.087] |
| L24 | control | -1.245 [-1.297, -1.192] | -1.261 [-1.314, -1.207] | +0.016 [-0.000, +0.031] | +0.050 [+0.031, +0.071] |
| L24 | T − C (within bin) | | | +0.009 [-0.012, +0.030] | |
| L32 | target | -1.125 [-1.169, -1.084] | -1.144 [-1.189, -1.100] | +0.019 [+0.004, +0.033] | +0.062 [+0.044, +0.081] |
| L32 | control | -1.252 [-1.303, -1.197] | -1.245 [-1.299, -1.193] | -0.007 [-0.024, +0.010] | +0.052 [+0.032, +0.074] |
| L32 | T − C (within bin) | | | +0.026 [+0.003, +0.050] | |
| L40 | target | -1.117 [-1.162, -1.073] | -1.133 [-1.179, -1.089] | +0.016 [-0.001, +0.033] | +0.078 [+0.058, +0.097] |
| L40 | control | -1.252 [-1.303, -1.200] | -1.261 [-1.311, -1.211] | +0.009 [-0.008, +0.025] | +0.048 [+0.025, +0.072] |
| L40 | T − C (within bin) | | | +0.008 [-0.016, +0.031] | |
| L44 | target | -1.121 [-1.165, -1.079] | -1.138 [-1.185, -1.095] | +0.017 [+0.001, +0.033] | +0.070 [+0.052, +0.089] |
| L44 | control | -1.250 [-1.300, -1.199] | -1.254 [-1.306, -1.202] | +0.004 [-0.013, +0.020] | +0.053 [+0.031, +0.076] |
| L44 | T − C (within bin) | | | +0.013 [-0.009, +0.036] | |
| L48 | target | -1.114 [-1.158, -1.071] | -1.139 [-1.186, -1.094] | +0.025 [+0.007, +0.042] | +0.087 [+0.067, +0.107] |
| L48 | control | -1.250 [-1.299, -1.197] | -1.258 [-1.311, -1.205] | +0.008 [-0.009, +0.026] | +0.053 [+0.031, +0.077] |
| L48 | T − C (within bin) | | | +0.017 [-0.008, +0.040] | |
| L52 | target | -1.104 [-1.149, -1.062] | -1.143 [-1.190, -1.100] | +0.039 [+0.022, +0.057] | +0.101 [+0.079, +0.122] |
| L52 | control | -1.245 [-1.295, -1.192] | -1.264 [-1.316, -1.212] | +0.018 [+0.000, +0.036] | +0.063 [+0.040, +0.084] |
| L52 | T − C (within bin) | | | +0.021 [-0.004, +0.046] | |
| L56 | target | -1.107 [-1.151, -1.066] | -1.148 [-1.194, -1.105] | +0.041 [+0.024, +0.058] | +0.100 [+0.079, +0.122] |
| L56 | control | -1.249 [-1.299, -1.197] | -1.268 [-1.321, -1.215] | +0.019 [+0.001, +0.036] | +0.067 [+0.043, +0.090] |
| L56 | T − C (within bin) | | | +0.022 [-0.004, +0.046] | |
| L60 | target | -1.109 [-1.154, -1.068] | -1.141 [-1.186, -1.097] | +0.032 [+0.015, +0.048] | +0.098 [+0.077, +0.119] |
| L60 | control | -1.247 [-1.296, -1.195] | -1.264 [-1.318, -1.211] | +0.017 [+0.000, +0.033] | +0.070 [+0.047, +0.093] |
| L60 | T − C (within bin) | | | +0.014 [-0.010, +0.039] | |

**S6 M2 attribute readouts (ridge probes refitted on the 9,108 true title-position residuals with the published setup: team folds, ridge_cv alpha grid; applied to the fict residual; scored against the TRUE paper's labels; all 1,127 papers unless stated):**

| layer | group | field acc true | field acc fict | year R² true | year R² fict | log-cit R² true | log-cit R² fict | Δ cit R² (true − fict) |
|---|---|---|---|---|---|---|---|---|
| L16 | target | 0.693 | 0.703 | 0.288 | 0.082 | 0.100 | 0.022 | +0.078 [-0.019, +0.176] |
| L16 | control | 0.699 | 0.706 | 0.462 | 0.203 | 0.163 | -0.004 | +0.167 [+0.070, +0.265] |
| L16 | all | 0.696 | 0.705 | 0.403 | 0.164 | 0.131 | 0.009 | +0.122 [+0.051, +0.196] |
| L24 | target | 0.726 | 0.708 | 0.394 | 0.140 | 0.220 | 0.028 | +0.192 [+0.093, +0.297] |
| L24 | control | 0.731 | 0.750 | 0.501 | 0.258 | 0.222 | 0.043 | +0.179 [+0.085, +0.271] |
| L24 | all | 0.728 | 0.729 | 0.466 | 0.220 | 0.221 | 0.035 | +0.185 [+0.116, +0.254] |
| L32 | target | 0.719 | 0.724 | 0.441 | 0.127 | 0.171 | 0.065 | +0.106 [+0.009, +0.204] |
| L32 | control | 0.717 | 0.754 | 0.500 | 0.257 | 0.223 | 0.027 | +0.196 [+0.108, +0.290] |
| L32 | all | 0.718 | 0.739 | 0.482 | 0.215 | 0.197 | 0.046 | +0.150 [+0.083, +0.218] |
| L40 | target | 0.719 | 0.698 | 0.450 | 0.138 | 0.315 | 0.079 | +0.236 [+0.143, +0.328] |
| L40 | control | 0.729 | 0.736 | 0.505 | 0.284 | 0.284 | 0.066 | +0.219 [+0.130, +0.308] |
| L40 | all | 0.724 | 0.717 | 0.488 | 0.236 | 0.300 | 0.072 | +0.227 [+0.160, +0.294] |
| L44 | target | 0.723 | 0.700 | 0.489 | 0.104 | 0.351 | 0.073 | +0.277 [+0.182, +0.369] |
| L44 | control | 0.725 | 0.722 | 0.501 | 0.279 | 0.340 | 0.056 | +0.284 [+0.200, +0.374] |
| L44 | all | 0.724 | 0.711 | 0.499 | 0.220 | 0.345 | 0.065 | +0.280 [+0.215, +0.348] |
| L48 | target | 0.714 | 0.723 | 0.567 | 0.132 | 0.370 | 0.106 | +0.264 [+0.166, +0.357] |
| L48 | control | 0.742 | 0.727 | 0.545 | 0.331 | 0.356 | 0.096 | +0.260 [+0.176, +0.345] |
| L48 | all | 0.728 | 0.725 | 0.555 | 0.264 | 0.363 | 0.101 | +0.262 [+0.196, +0.327] |
| L52 | target | 0.723 | 0.705 | 0.558 | 0.144 | 0.372 | 0.114 | +0.258 [+0.164, +0.351] |
| L52 | control | 0.738 | 0.736 | 0.544 | 0.320 | 0.371 | 0.088 | +0.282 [+0.200, +0.369] |
| L52 | all | 0.730 | 0.720 | 0.551 | 0.261 | 0.371 | 0.101 | +0.270 [+0.207, +0.335] |
| L56 | target | 0.721 | 0.723 | 0.563 | 0.155 | 0.374 | 0.119 | +0.255 [+0.161, +0.354] |
| L56 | control | 0.733 | 0.750 | 0.543 | 0.307 | 0.383 | 0.116 | +0.267 [+0.187, +0.348] |
| L56 | all | 0.727 | 0.736 | 0.552 | 0.257 | 0.379 | 0.118 | +0.261 [+0.197, +0.323] |
| L60 | target | 0.728 | 0.717 | 0.526 | 0.140 | 0.360 | 0.098 | +0.262 [+0.170, +0.356] |
| L60 | control | 0.724 | 0.749 | 0.514 | 0.283 | 0.336 | 0.102 | +0.234 [+0.157, +0.312] |
| L60 | all | 0.726 | 0.733 | 0.521 | 0.236 | 0.348 | 0.100 | +0.248 [+0.188, +0.309] |

CIs for every cell: S6_M2_attributes.csv. R² is computed on the subset (1 − SS_res/SS_tot within the subset).

**S7 meaning dose (target, tertiles of the fict–true mpnet cosine, cut points on target papers):**

| tertile | cosine range | φ_T | R̄_T | n |
|---|---|---|---|---|
| 1 | 0.32–0.60 | +0.722 [+0.672, +0.768] | +0.121 [+0.099, +0.145] | 189 |
| 2 | 0.60–0.69 | +0.740 [+0.693, +0.786] | +0.115 [+0.092, +0.138] | 188 |
| 3 | 0.69–0.85 | +0.794 [+0.746, +0.839] | +0.082 [+0.063, +0.102] | 189 |

φ(tertile 3) − φ(tertile 1) = +0.072 [+0.002, +0.140]. Title-text similarity predicts φ rising with cosine; H2 predicts a low, flat φ.

## 3. Sensitivity analyses (verdict by the same rule)

| analysis | φ_T | R̄_T | n | verdict (rule) | borderline |
|---|---|---|---|---|---|
| primary | +0.751 [+0.723, +0.778] | +0.106 [+0.094, +0.118] | 566 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (a) false_0 instead of the 5-title mean | +0.745 [+0.715, +0.773] | +0.106 [+0.094, +0.118] | 566 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (b) without fict titles with Crossref jaccard2 >= 0.4 | +0.735 [+0.703, +0.765] | +0.110 [+0.097, +0.124] | 460 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (c) true titles >= 6 words | +0.747 [+0.719, +0.775] | +0.107 [+0.094, +0.120] | 543 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (d1) first author only | +0.736 [+0.699, +0.772] | +0.117 [+0.100, +0.136] | 566 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (d2) surname first token only | +0.719 [+0.683, +0.754] | +0.217 [+0.185, +0.250] | 566 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (e) R0 papers only | +0.751 [+0.722, +0.780] | +0.103 [+0.091, +0.117] | 531 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (f) title log-prob true - fict, target tertile 1 | +0.708 [+0.650, +0.764] | +0.114 [+0.091, +0.139] | 189 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (f) title log-prob true - fict, target tertile 2 | +0.758 [+0.707, +0.809] | +0.093 [+0.073, +0.114] | 188 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |
| (f) title log-prob true - fict, target tertile 3 | +0.778 [+0.741, +0.816] | +0.111 [+0.090, +0.133] | 189 | H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal | False |

**(f) Title likelihood** (mean per-token log-probability of the title tokens under the model, prompt prefix only):

| group | true | fict | false_0 | mean false_0..4 | true − fict |
|---|---|---|---|---|---|
| target | -3.317 | -3.193 | -3.310 | -3.348 | -0.124 |
| control | -3.526 | -3.275 | -3.548 | -3.492 | -0.251 |

CIs: Sf_title_logprob.csv. φ_T by tertile of (true − fict) title log-prob: rows (f) above.

## 4. Exclusions

- Fixed by the generation rule (before the run): 59 papers without a valid fictitious title (27 target, 32 control); reasons: {'no valid fictitious title (generation rule, v3/excluded.csv)': 59}. List: raw/a20v2_freeze/exclusions.csv (= h2_fictitious/v3/excluded.csv).
- Prompt context > 512 tokens (or aligned tail < 3): 0 (max context of the kept fict prompts 78 tokens).
- Run-time (scoring failure / missing rows): 0.
- Analysed: 1127 papers (566 target, 561 control); within-bin weights use these papers.

## 5. Parity and in-job self-checks (WARN = threshold missed; work continued under the project tolerance rule)

Parity (shard 0, 44 papers, GPU ['NVIDIA H200']; true and false_0..4 re-scored with the Stage 10 code vs the stored Stage 10 files; thresholds {'rank_equal_share': 0.75, 'mean_abs_dlog10rank': 0.05, 'max_abs_dlogprob': 1.0}): **WARN**.

| condition | readout@layer | tokens | rank equal | mean abs Δlog10 rank | max abs Δlogprob | max abs Δ paper mean_nlr |
|---|---|---|---|---|---|---|
| true | final@63 | 464 | 0.655 | 0.0095 | 0.218 | 0.0587 |
| true | logit@24 | 464 | 0.004 | 0.0052 | 0.103 | 0.0062 |
| true | logit@32 | 464 | 0.017 | 0.0059 | 0.156 | 0.0100 |
| true | logit@40 | 464 | 0.022 | 0.0066 | 0.138 | 0.0158 |
| true | logit@48 | 464 | 0.026 | 0.0056 | 0.187 | 0.0103 |
| true | logit@56 | 464 | 0.114 | 0.0084 | 0.285 | 0.0098 |
| true | logit@62 | 464 | 0.614 | 0.0093 | 0.319 | 0.0285 |
| true | jlens_public@24 | 464 | 0.011 | 0.0076 | 0.278 | 0.0219 |
| true | jlens_public@32 | 464 | 0.017 | 0.0092 | 0.424 | 0.0185 |
| true | jlens_public@40 | 464 | 0.060 | 0.0128 | 0.336 | 0.0358 |
| true | jlens_public@48 | 464 | 0.170 | 0.0103 | 0.246 | 0.0424 |
| true | jlens_public@56 | 464 | 0.123 | 0.0111 | 0.239 | 0.0326 |
| true | jlens_public@62 | 464 | 0.509 | 0.0123 | 0.252 | 0.0638 |
| false_0 | final@63 | 464 | 0.582 | 0.0107 | 0.281 | 0.0633 |
| false_0 | logit@56 | 464 | 0.093 | 0.0096 | 0.172 | 0.0141 |
| false_0 | jlens_public@56 | 464 | 0.127 | 0.0112 | 0.275 | 0.0702 |
| false_1 | final@63 | 464 | 0.550 | 0.0093 | 0.327 | 0.0296 |
| false_1 | logit@56 | 464 | 0.101 | 0.0080 | 0.203 | 0.0241 |
| false_1 | jlens_public@56 | 464 | 0.125 | 0.0115 | 0.301 | 0.0159 |
| false_2 | final@63 | 464 | 0.595 | 0.0103 | 0.303 | 0.0508 |
| false_2 | logit@56 | 464 | 0.110 | 0.0078 | 0.402 | 0.0115 |
| false_2 | jlens_public@56 | 464 | 0.121 | 0.0104 | 0.465 | 0.0496 |
| false_3 | final@63 | 464 | 0.593 | 0.0108 | 0.273 | 0.0384 |
| false_3 | logit@56 | 464 | 0.103 | 0.0085 | 0.296 | 0.0132 |
| false_3 | jlens_public@56 | 464 | 0.136 | 0.0100 | 0.281 | 0.0188 |
| false_4 | final@63 | 464 | 0.584 | 0.0111 | 0.437 | 0.0237 |
| false_4 | logit@56 | 464 | 0.095 | 0.0098 | 0.225 | 0.0383 |
| false_4 | jlens_public@56 | 464 | 0.125 | 0.0112 | 0.469 | 0.0224 |

WARN pairs: ['true|final@63', 'true|logit@24', 'true|logit@32', 'true|logit@40', 'true|logit@48', 'true|logit@56', 'true|logit@62', 'true|jlens_public@24', 'true|jlens_public@32', 'true|jlens_public@40', 'true|jlens_public@48', 'true|jlens_public@56', 'true|jlens_public@62', 'false_0|final@63', 'false_0|logit@24', 'false_0|logit@32', 'false_0|logit@40', 'false_0|logit@48', 'false_0|logit@56', 'false_0|logit@62', 'false_0|jlens_public@24', 'false_0|jlens_public@32', 'false_0|jlens_public@40', 'false_0|jlens_public@48', 'false_0|jlens_public@56', 'false_0|jlens_public@62', 'false_1|final@63', 'false_1|logit@24', 'false_1|logit@32', 'false_1|logit@40', 'false_1|logit@48', 'false_1|logit@56', 'false_1|logit@62', 'false_1|jlens_public@24', 'false_1|jlens_public@32', 'false_1|jlens_public@40', 'false_1|jlens_public@48', 'false_1|jlens_public@56', 'false_1|jlens_public@62', 'false_2|final@63', 'false_2|logit@24', 'false_2|logit@32', 'false_2|logit@40', 'false_2|logit@48', 'false_2|logit@56', 'false_2|logit@62', 'false_2|jlens_public@24', 'false_2|jlens_public@32', 'false_2|jlens_public@40', 'false_2|jlens_public@48', 'false_2|jlens_public@56', 'false_2|jlens_public@62', 'false_3|final@63', 'false_3|logit@24', 'false_3|logit@32', 'false_3|logit@40', 'false_3|logit@48', 'false_3|logit@56', 'false_3|logit@62', 'false_3|jlens_public@24', 'false_3|jlens_public@32', 'false_3|jlens_public@40', 'false_3|jlens_public@48', 'false_3|jlens_public@56', 'false_3|jlens_public@62', 'false_4|final@63', 'false_4|logit@24', 'false_4|logit@32', 'false_4|logit@40', 'false_4|logit@48', 'false_4|logit@56', 'false_4|logit@62', 'false_4|jlens_public@24', 'false_4|jlens_public@32', 'false_4|jlens_public@40', 'false_4|jlens_public@48', 'false_4|jlens_public@56', 'false_4|jlens_public@62'] (all pairs in raw/a20v2_checks/parity_000.json).

Unit self-checks: 73 units, 25 WARN. WARN units: parity_000: {"status": "WARN", "thresholds": {"rank_equal_share": 0.75, "mean_abs_dlog10rank": 0.05, "max_abs_dlogprob": 1.0}, "warn_pairs": ["true|final@63", "true|logit@24", "true|logit@32", "true|logit@40", "true|logit@48", "true|logit@56", "true|logit@62", "true|jlens_public@24", "true|jlens_public@32", "tr; patch_000: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.5818965517241379, "false_vs_stage11_mean_abs_dlog10rank": 0.010680326070288309, "false_vs_stage11_n": 464, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_001: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.6592765460910152, "false_vs_stage11_mean_abs_dlog10rank": 0.007269834833392531, "false_vs_stage11_n": 857, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_002: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.563165905631659, "false_vs_stage11_mean_abs_dlog10rank": 0.009743432079051465, "false_vs_stage11_n": 657, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_sh; patch_003: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.6002691790040376, "false_vs_stage11_mean_abs_dlog10rank": 0.009490543783621378, "false_vs_stage11_n": 743, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_004: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.6105820105820106, "false_vs_stage11_mean_abs_dlog10rank": 0.010273679154360033, "false_vs_stage11_n": 945, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_005: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.5742705570291777, "false_vs_stage11_mean_abs_dlog10rank": 0.01008354671413312, "false_vs_stage11_n": 754, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_sh; patch_006: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.585812356979405, "false_vs_stage11_mean_abs_dlog10rank": 0.009837408247548052, "false_vs_stage11_n": 874, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_sh; patch_007: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.5899390243902439, "false_vs_stage11_mean_abs_dlog10rank": 0.013603595202675865, "false_vs_stage11_n": 656, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_008: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.5849297573435505, "false_vs_stage11_mean_abs_dlog10rank": 0.010726070901290694, "false_vs_stage11_n": 783, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s; patch_009: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.6118326118326118, "false_vs_stage11_mean_abs_dlog10rank": 0.01127130840149461, "false_vs_stage11_n": 693, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_sh; patch_010: {"L63_equals_fict_share": 1.0, "L63_threshold": 0.99, "false_vs_stage11_rank_equal_share": 0.5957142857142858, "false_vs_stage11_mean_abs_dlog10rank": 0.009572140447423041, "false_vs_stage11_n": 700, "false_thresholds": {"equal_share": 0.75, "mean_abs_dlog10rank": 0.05}, "fict_vs_score_final_equal_s
Patch checks over 24 shards: L63 == fict share min 1.0000 (threshold 0.99); false_0 rank equal to stored Stage 11 E1 min 0.562 (threshold 0.75), mean abs Δlog10 rank max 0.0136 (threshold 0.05); fict rank (patch run) = score unit final@63 share min 1.000.
Titlepos checks over 24 shards: true title residual vs stored Stage 11 (fp16) relative L2 max 0.0334 (threshold 0.05).

## 6. GPU cost

Measured: **0.53 GPU-h** (sacct ElapsedRaw × GPUs, all addendum-20 main-run GPU jobs). Addendum estimate ≈ 1.2–1.8 GPU-h (allocated ≤ 3; hard cap 5).
- 12015462 gpu-interactive d4053 COMPLETED 16.5 min x 1 GPU
- 12015463 gpu-interactive d4053 COMPLETED 15.2 min x 1 GPU
- Plus the INVALID v1 run (freeze bug: fict prompt = true title; outputs raw/a20_*, summary_a20_INVALID_v1_fict_eq_true/): 0.55 GPU-h (12014065 6.8 min; 12014453 13.2 min; 12014454 13.1 min). Total addendum-20 main-run GPU incl. v1: 1.08 GPU-h.

## 7. Implementation notes (choices the addendum did not spell out)

- S_true and S_false_k are the stored Stage 10 values (A100); S_fict is from this run (see §5 for the hardware parity of re-scored true/false_k).
- φ within-bin T − C (S2): per-bin ratio of sums, bin weights n_t·n_c/(n_t+n_c) fixed at the point counts; the plain pooled φ_T − φ_C is shown beside it.
- S4: rec_fict numerator uses this run's false_0 baseline (same forward pass as the patched runs); denominator (true − false_0) and rec_true(l) come from the stored Stage 11 E1 run (paper means of token log10(1/rank), then mean over papers).
- S5/S6: the published probes were not stored as weights, so they are refitted with the published setup on the 9,108 true runs (team folds; training-fold standardisation; same alpha grids); the fict residual of a paper is scored by the model of the fold that held that paper out. S5 probe(false_0) uses the stored Stage 11 false_0 residual.
- S7 and (f): tertile cut points on the target papers.
- (d1) first author = the lowest scored author index of the paper. Probe layers used: [16, 24, 32, 40, 44, 48, 52, 56, 60].

Files: E4b_perpaper.csv, M2_perpaper.csv, S3_layer_profile.csv, S4_E1_fict_donor.csv, S5_E4b_probe.csv, S6_M2_attributes.csv, Sf_title_logprob.csv, perpaper_final63.csv, primary_secondary_sensitivity.csv, title_logprob_perpaper.csv, a20_results.json.
