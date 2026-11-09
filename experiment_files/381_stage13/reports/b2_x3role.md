# Addendum 12 item 2-3: X3 behaviour by token role and for all authors

Written 2026-11-09 04:56 by `13_stage13/stage13_b2B_analyze.py x3role`. Plan: `381_stage13/config/prereg_addendum12.json` (sha256 OK). Raw: `/scratch/zhang.zhiqi2/jlens/381_stage13/raw`.

Per-token batch-1 scores of every author (original / paraphrase / partner B / lexical neighbour D title; batch-1 all-author rows of raw/b1_xall/para). Role tokens averaged within (pair, author); strata as stage13_b1_xall_analyze (first author; all = mean over the paper's authors; others = authors >= 2); frozen X3 statistics (stage13_x3_recovery.recovery, stage13_x3_analyze.beh_rows; same seeds / team draws). Pairs without a token of the role drop out.

HARD CHECK (first author, role ALL vs published x3_behaviour.csv / x3_recovery.csv; threshold 0.005): behaviour max |diff| 1.1e-16 (90/90 cells), recovery max |diff| 1.8e-15 (96/96 cells) -> **PASS**.
Per-author check (WARN only): 4039 author rows vs raw/b1_xall/para: mean |d| 7.39e-17, max |d| 8.88e-16, exact 1.000.

## Primary set, subset all, split test: recovery (P - D)/(O - D) vs D and behaviour P - D

| stratum | role | group | n | O - D | recovery [CI] | P - D [CI] |
|---|---|---|---|---|---|---|
| first | ALL | all | 552 | +0.265 | +0.901 [+0.865, +0.937] | +0.239 [+0.212, +0.266] |
| first | ALL | target | 274 | +0.350 | +0.896 [+0.854, +0.936] | +0.313 [+0.274, +0.355] |
| first | ALL | control | 278 | +0.182 | +0.909 [+0.838, +0.980] | +0.165 [+0.134, +0.199] |
| first | ALL | target_minus_control | 552 |  | -0.012 [-0.094, +0.071] |  |
| first | initial | all | 418 | +0.170 | +0.881 [+0.731, +1.035] | +0.150 [+0.103, +0.203] |
| first | initial | target | 217 | +0.235 | +0.862 [+0.684, +1.022] | +0.202 [+0.127, +0.278] |
| first | initial | control | 201 | +0.101 | +0.928 [+0.543, +1.467] | +0.093 [+0.030, +0.162] |
| first | initial | target_minus_control | 418 |  | -0.066 [-0.644, +0.358] |  |
| first | given_first | all | 158 | +0.301 | +0.855 [+0.706, +1.004] | +0.257 [+0.160, +0.360] |
| first | given_first | target | 68 | +0.472 | +0.901 [+0.748, +1.052] | +0.425 [+0.249, +0.622] |
| first | given_first | control | 90 | +0.172 | +0.759 [+0.349, +1.151] | +0.131 [+0.034, +0.231] |
| first | given_first | target_minus_control | 158 |  | +0.142 [-0.284, +0.575] |  |
| first | given_cont | all | 98 | +0.229 | +0.939 [+0.724, +1.182] | +0.215 [+0.119, +0.317] |
| first | given_cont | target | 44 | +0.323 | +0.826 [+0.591, +0.996] | +0.267 [+0.112, +0.436] |
| first | given_cont | control | 54 | +0.152 | +1.135 [+0.620, +2.675] | +0.172 [+0.047, +0.303] |
| first | given_cont | target_minus_control | 98 |  | -0.309 [-1.871, +0.213] |  |
| first | surname_first | all | 552 | +0.394 | +0.901 [+0.849, +0.951] | +0.355 [+0.292, +0.418] |
| first | surname_first | target | 274 | +0.551 | +0.885 [+0.824, +0.938] | +0.488 [+0.383, +0.598] |
| first | surname_first | control | 278 | +0.239 | +0.938 [+0.829, +1.052] | +0.224 [+0.158, +0.292] |
| first | surname_first | target_minus_control | 552 |  | -0.053 [-0.180, +0.065] |  |
| first | surname_cont | all | 402 | +0.401 | +0.929 [+0.886, +0.972] | +0.373 [+0.316, +0.434] |
| first | surname_cont | target | 215 | +0.454 | +0.927 [+0.876, +0.981] | +0.421 [+0.345, +0.505] |
| first | surname_cont | control | 187 | +0.340 | +0.931 [+0.849, +1.012] | +0.317 [+0.233, +0.405] |
| first | surname_cont | target_minus_control | 402 |  | -0.004 [-0.105, +0.095] |  |
| all | ALL | all | 552 | +0.256 | +0.897 [+0.868, +0.926] | +0.229 [+0.208, +0.250] |
| all | ALL | target | 274 | +0.340 | +0.894 [+0.863, +0.924] | +0.304 [+0.275, +0.333] |
| all | ALL | control | 278 | +0.173 | +0.901 [+0.841, +0.962] | +0.155 [+0.131, +0.182] |
| all | ALL | target_minus_control | 552 |  | -0.007 [-0.075, +0.059] |  |
| all | initial | all | 511 | +0.144 | +0.851 [+0.723, +0.978] | +0.123 [+0.088, +0.159] |
| all | initial | target | 255 | +0.197 | +0.828 [+0.689, +0.953] | +0.163 [+0.114, +0.215] |
| all | initial | control | 256 | +0.091 | +0.900 [+0.558, +1.294] | +0.082 [+0.029, +0.133] |
| all | initial | target_minus_control | 511 |  | -0.072 [-0.482, +0.285] |  |
| all | given_first | all | 253 | +0.302 | +0.887 [+0.800, +0.980] | +0.268 [+0.201, +0.340] |
| all | given_first | target | 130 | +0.414 | +0.897 [+0.810, +0.979] | +0.371 [+0.272, +0.479] |
| all | given_first | control | 123 | +0.184 | +0.865 [+0.640, +1.146] | +0.159 [+0.079, +0.241] |
| all | given_first | target_minus_control | 253 |  | +0.032 [-0.252, +0.280] |  |
| all | given_cont | all | 176 | +0.237 | +0.806 [+0.677, +0.927] | +0.191 [+0.133, +0.255] |
| all | given_cont | target | 80 | +0.278 | +0.743 [+0.555, +0.881] | +0.207 [+0.116, +0.306] |
| all | given_cont | control | 96 | +0.202 | +0.878 [+0.677, +1.115] | +0.178 [+0.102, +0.261] |
| all | given_cont | target_minus_control | 176 |  | -0.135 [-0.433, +0.124] |  |
| all | surname_first | all | 552 | +0.422 | +0.900 [+0.863, +0.935] | +0.380 [+0.333, +0.428] |
| all | surname_first | target | 274 | +0.588 | +0.894 [+0.854, +0.931] | +0.526 [+0.452, +0.600] |
| all | surname_first | control | 278 | +0.258 | +0.913 [+0.832, +0.995] | +0.236 [+0.186, +0.286] |
| all | surname_first | target_minus_control | 552 |  | -0.019 [-0.109, +0.071] |  |
| all | surname_cont | all | 491 | +0.388 | +0.924 [+0.888, +0.959] | +0.359 [+0.319, +0.399] |
| all | surname_cont | target | 266 | +0.475 | +0.916 [+0.873, +0.953] | +0.435 [+0.381, +0.493] |
| all | surname_cont | control | 225 | +0.286 | +0.939 [+0.868, +1.014] | +0.269 [+0.211, +0.335] |
| all | surname_cont | target_minus_control | 491 |  | -0.023 [-0.108, +0.059] |  |
| others | ALL | all | 453 | +0.250 | +0.889 [+0.855, +0.923] | +0.223 [+0.200, +0.246] |
| others | ALL | target | 243 | +0.323 | +0.892 [+0.855, +0.928] | +0.289 [+0.258, +0.320] |
| others | ALL | control | 210 | +0.166 | +0.882 [+0.812, +0.956] | +0.146 [+0.117, +0.176] |
| others | ALL | target_minus_control | 453 |  | +0.010 [-0.072, +0.088] |  |
| others | initial | all | 413 | +0.138 | +0.829 [+0.686, +0.977] | +0.114 [+0.076, +0.153] |
| others | initial | target | 229 | +0.161 | +0.875 [+0.711, +1.040] | +0.141 [+0.089, +0.196] |
| others | initial | control | 184 | +0.109 | +0.744 [+0.398, +1.067] | +0.081 [+0.026, +0.134] |
| others | initial | target_minus_control | 413 |  | +0.131 [-0.228, +0.519] |  |
| others | given_first | all | 187 | +0.331 | +0.873 [+0.771, +0.971] | +0.289 [+0.203, +0.375] |
| others | given_first | target | 100 | +0.426 | +0.890 [+0.784, +0.975] | +0.379 [+0.251, +0.509] |
| others | given_first | control | 87 | +0.222 | +0.835 [+0.565, +1.112] | +0.185 [+0.080, +0.295] |
| others | given_first | target_minus_control | 187 |  | +0.055 [-0.228, +0.352] |  |
| others | given_cont | all | 129 | +0.240 | +0.754 [+0.600, +0.887] | +0.181 [+0.112, +0.248] |
| others | given_cont | target | 60 | +0.264 | +0.728 [+0.467, +0.904] | +0.192 [+0.085, +0.299] |
| others | given_cont | control | 69 | +0.219 | +0.782 [+0.567, +0.953] | +0.171 [+0.087, +0.265] |
| others | given_cont | target_minus_control | 129 |  | -0.054 [-0.359, +0.228] |  |
| others | surname_first | all | 453 | +0.435 | +0.888 [+0.846, +0.930] | +0.387 [+0.333, +0.443] |
| others | surname_first | target | 243 | +0.603 | +0.881 [+0.834, +0.927] | +0.532 [+0.450, +0.616] |
| others | surname_first | control | 210 | +0.241 | +0.907 [+0.818, +0.998] | +0.218 [+0.159, +0.277] |
| others | surname_first | target_minus_control | 453 |  | -0.025 [-0.128, +0.074] |  |
| others | surname_cont | all | 383 | +0.377 | +0.932 [+0.887, +0.972] | +0.352 [+0.304, +0.402] |
| others | surname_cont | target | 224 | +0.468 | +0.924 [+0.875, +0.967] | +0.433 [+0.367, +0.499] |
| others | surname_cont | control | 159 | +0.249 | +0.954 [+0.851, +1.043] | +0.237 [+0.166, +0.312] |
| others | surname_cont | target_minus_control | 383 |  | -0.030 [-0.132, +0.078] |  |

## Primary set, subset all, split all: recovery (P - D)/(O - D) vs D and behaviour P - D

| stratum | role | group | n | O - D | recovery [CI] | P - D [CI] |
|---|---|---|---|---|---|---|
| first | ALL | all | 1110 | +0.282 | +0.898 [+0.874, +0.922] | +0.254 [+0.235, +0.272] |
| first | ALL | target | 561 | +0.362 | +0.898 [+0.868, +0.925] | +0.325 [+0.298, +0.353] |
| first | ALL | control | 549 | +0.201 | +0.898 [+0.854, +0.941] | +0.181 [+0.157, +0.206] |
| first | ALL | target_minus_control | 1110 |  | +0.000 [-0.052, +0.052] |  |
| first | initial | all | 839 | +0.161 | +0.858 [+0.744, +0.975] | +0.138 [+0.103, +0.171] |
| first | initial | target | 444 | +0.201 | +0.868 [+0.731, +0.998] | +0.174 [+0.126, +0.222] |
| first | initial | control | 395 | +0.116 | +0.837 [+0.592, +1.068] | +0.097 [+0.048, +0.145] |
| first | initial | target_minus_control | 839 |  | +0.031 [-0.246, +0.288] |  |
| first | given_first | all | 328 | +0.286 | +0.830 [+0.730, +0.924] | +0.237 [+0.168, +0.312] |
| first | given_first | target | 144 | +0.381 | +0.873 [+0.761, +0.985] | +0.332 [+0.216, +0.460] |
| first | given_first | control | 184 | +0.211 | +0.770 [+0.555, +0.944] | +0.163 [+0.083, +0.248] |
| first | given_first | target_minus_control | 328 |  | +0.103 [-0.106, +0.348] |  |
| first | given_cont | all | 200 | +0.230 | +0.930 [+0.811, +1.055] | +0.213 [+0.148, +0.283] |
| first | given_cont | target | 86 | +0.297 | +0.919 [+0.797, +1.031] | +0.273 [+0.172, +0.388] |
| first | given_cont | control | 114 | +0.179 | +0.943 [+0.717, +1.203] | +0.168 [+0.078, +0.258] |
| first | given_cont | target_minus_control | 200 |  | -0.024 [-0.311, +0.234] |  |
| first | surname_first | all | 1110 | +0.458 | +0.882 [+0.847, +0.920] | +0.404 [+0.362, +0.451] |
| first | surname_first | target | 561 | +0.629 | +0.874 [+0.830, +0.916] | +0.549 [+0.480, +0.626] |
| first | surname_first | control | 549 | +0.283 | +0.902 [+0.836, +0.972] | +0.255 [+0.205, +0.306] |
| first | surname_first | target_minus_control | 1110 |  | -0.029 [-0.110, +0.049] |  |
| first | surname_cont | all | 797 | +0.436 | +0.942 [+0.915, +0.969] | +0.411 [+0.369, +0.455] |
| first | surname_cont | target | 433 | +0.501 | +0.940 [+0.909, +0.971] | +0.471 [+0.413, +0.534] |
| first | surname_cont | control | 364 | +0.358 | +0.946 [+0.893, +0.998] | +0.339 [+0.281, +0.401] |
| first | surname_cont | target_minus_control | 797 |  | -0.006 [-0.068, +0.052] |  |
| all | ALL | all | 1110 | +0.271 | +0.903 [+0.882, +0.924] | +0.245 [+0.229, +0.260] |
| all | ALL | target | 561 | +0.345 | +0.905 [+0.881, +0.927] | +0.313 [+0.291, +0.334] |
| all | ALL | control | 549 | +0.195 | +0.899 [+0.862, +0.936] | +0.175 [+0.156, +0.195] |
| all | ALL | target_minus_control | 1110 |  | +0.006 [-0.035, +0.048] |  |
| all | initial | all | 1016 | +0.134 | +0.848 [+0.747, +0.949] | +0.114 [+0.088, +0.139] |
| all | initial | target | 523 | +0.158 | +0.851 [+0.738, +0.960] | +0.135 [+0.101, +0.170] |
| all | initial | control | 493 | +0.108 | +0.844 [+0.658, +1.041] | +0.091 [+0.054, +0.128] |
| all | initial | target_minus_control | 1016 |  | +0.007 [-0.211, +0.226] |  |
| all | given_first | all | 533 | +0.312 | +0.864 [+0.801, +0.922] | +0.270 [+0.223, +0.317] |
| all | given_first | target | 268 | +0.381 | +0.875 [+0.808, +0.943] | +0.334 [+0.266, +0.408] |
| all | given_first | control | 265 | +0.243 | +0.848 [+0.731, +0.967] | +0.206 [+0.143, +0.266] |
| all | given_first | target_minus_control | 533 |  | +0.027 [-0.101, +0.163] |  |
| all | given_cont | all | 380 | +0.268 | +0.855 [+0.783, +0.920] | +0.229 [+0.179, +0.277] |
| all | given_cont | target | 179 | +0.312 | +0.848 [+0.755, +0.924] | +0.265 [+0.188, +0.340] |
| all | given_cont | control | 201 | +0.228 | +0.863 [+0.746, +0.983] | +0.197 [+0.132, +0.256] |
| all | given_cont | target_minus_control | 380 |  | -0.015 [-0.166, +0.127] |  |
| all | surname_first | all | 1110 | +0.455 | +0.897 [+0.869, +0.924] | +0.408 [+0.374, +0.445] |
| all | surname_first | target | 561 | +0.626 | +0.891 [+0.857, +0.925] | +0.558 [+0.505, +0.613] |
| all | surname_first | control | 549 | +0.281 | +0.910 [+0.856, +0.960] | +0.255 [+0.216, +0.297] |
| all | surname_first | target_minus_control | 1110 |  | -0.019 [-0.079, +0.044] |  |
| all | surname_cont | all | 983 | +0.418 | +0.942 [+0.920, +0.962] | +0.394 [+0.362, +0.426] |
| all | surname_cont | target | 533 | +0.496 | +0.940 [+0.916, +0.962] | +0.466 [+0.420, +0.510] |
| all | surname_cont | control | 450 | +0.327 | +0.945 [+0.902, +0.989] | +0.309 [+0.264, +0.355] |
| all | surname_cont | target_minus_control | 983 |  | -0.005 [-0.056, +0.043] |  |
| others | ALL | all | 911 | +0.264 | +0.897 [+0.875, +0.919] | +0.237 [+0.220, +0.254] |
| others | ALL | target | 491 | +0.321 | +0.904 [+0.878, +0.930] | +0.291 [+0.268, +0.315] |
| others | ALL | control | 420 | +0.197 | +0.884 [+0.841, +0.926] | +0.174 [+0.152, +0.197] |
| others | ALL | target_minus_control | 911 |  | +0.020 [-0.029, +0.070] |  |
| others | initial | all | 811 | +0.141 | +0.794 [+0.687, +0.896] | +0.112 [+0.084, +0.140] |
| others | initial | target | 448 | +0.140 | +0.804 [+0.664, +0.929] | +0.112 [+0.073, +0.149] |
| others | initial | control | 363 | +0.143 | +0.781 [+0.603, +0.950] | +0.111 [+0.072, +0.153] |
| others | initial | target_minus_control | 811 |  | +0.023 [-0.189, +0.244] |  |
| others | given_first | all | 404 | +0.341 | +0.876 [+0.806, +0.944] | +0.298 [+0.243, +0.355] |
| others | given_first | target | 207 | +0.392 | +0.890 [+0.811, +0.967] | +0.348 [+0.264, +0.435] |
| others | given_first | control | 197 | +0.287 | +0.857 [+0.721, +0.983] | +0.246 [+0.173, +0.322] |
| others | given_first | target_minus_control | 404 |  | +0.033 [-0.114, +0.187] |  |
| others | given_cont | all | 283 | +0.286 | +0.831 [+0.750, +0.902] | +0.238 [+0.184, +0.301] |
| others | given_cont | target | 134 | +0.333 | +0.842 [+0.729, +0.931] | +0.280 [+0.192, +0.378] |
| others | given_cont | control | 149 | +0.245 | +0.818 [+0.693, +0.933] | +0.200 [+0.137, +0.267] |
| others | given_cont | target_minus_control | 283 |  | +0.023 [-0.136, +0.170] |  |
| others | surname_first | all | 911 | +0.435 | +0.896 [+0.865, +0.927] | +0.390 [+0.351, +0.432] |
| others | surname_first | target | 491 | +0.584 | +0.889 [+0.853, +0.922] | +0.519 [+0.461, +0.582] |
| others | surname_first | control | 420 | +0.262 | +0.915 [+0.851, +0.976] | +0.239 [+0.193, +0.286] |
| others | surname_first | target_minus_control | 911 |  | -0.025 [-0.098, +0.047] |  |
| others | surname_cont | all | 777 | +0.394 | +0.938 [+0.910, +0.963] | +0.369 [+0.333, +0.404] |
| others | surname_cont | target | 450 | +0.466 | +0.947 [+0.916, +0.974] | +0.441 [+0.391, +0.491] |
| others | surname_cont | control | 327 | +0.294 | +0.919 [+0.856, +0.979] | +0.270 [+0.217, +0.323] |
| others | surname_cont | target_minus_control | 777 |  | +0.028 [-0.041, +0.095] |  |

Full tables (all sets / subsets / splits / contrasts): summary_b2B/x3role_recovery.csv, x3role_behaviour.csv.

## WARN

- none

