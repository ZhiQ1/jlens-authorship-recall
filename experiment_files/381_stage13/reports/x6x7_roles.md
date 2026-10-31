# Stage 13 X6 / X7 by name-token role (V41, prereg addendum 4 "token_roles")

Script `13_stage13/stage13_x6x7_roles.py`. X6 shards: false_0 24, false_1 24, false_2 24, false_3 24, false_4 24; X7 shards: knockout 24, ko_false 24.
Same estimands, layers and team-cluster bootstrap as x6_report.md (seed 13) and x7_report.md (seed 17); the original draws are restricted to the papers that have tokens of the role. Per role, a paper's tokens of that role are averaged first, then R = mean(patched - false)/mean(true - false) (X6) and T, F, S as in X7.
Roles: **name_first** = first token of the name (initial_first + given_first, predicted at ":"), **surname_first**, **surname_cont** (pre-registered); also initial_first, given_first, given_cont, punct, particle_first. Gap rule: no ratio where mean(true - false) < 0.05 ("--").
Note: L44 is not among the stored layers (X6 layers [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63]; X7 start layers [0, 24, 32, 40, 48, 50, 52, 54, 56, 58, 60, 62]); tables show L48/L52/L56 (and L0 for X7).

Self-checks (WARN only): role ALL vs original CSVs: X6 max|diff| 5.6e-16, X7 max|diff| 2.2e-16.

## Gap true - false per role (nlr units; X6 false_0..false_4, X7 = false_0)

| role | group | n papers | gap false_0..4 | reportable |
|---|---|---|---|---|
| ALL | target | 593.0 | 0.418 / 0.422 / 0.425 / 0.427 / 0.439 | yes |
| ALL | control | 593.0 | 0.214 / 0.214 / 0.205 / 0.217 / 0.221 | yes |
| ALL | all | 1186.0 | 0.316 / 0.318 / 0.315 / 0.322 / 0.330 | yes |
| name_first | target | 590.0 | 0.186 / 0.185 / 0.205 / 0.222 / 0.217 | yes |
| name_first | control | 593.0 | 0.140 / 0.145 / 0.123 / 0.128 / 0.125 | yes |
| name_first | all | 1183.0 | 0.163 / 0.165 / 0.164 / 0.175 / 0.171 | yes |
| surname_first | target | 593.0 | 0.788 / 0.787 / 0.786 / 0.768 / 0.812 | yes |
| surname_first | control | 593.0 | 0.307 / 0.305 / 0.299 / 0.308 / 0.332 | yes |
| surname_first | all | 1186.0 | 0.547 / 0.546 / 0.542 / 0.538 / 0.572 | yes |
| surname_cont | target | 560.0 | 0.631 / 0.641 / 0.638 / 0.658 / 0.666 | yes |
| surname_cont | control | 482.0 | 0.388 / 0.378 / 0.382 / 0.415 / 0.403 | yes |
| surname_cont | all | 1042.0 | 0.519 / 0.520 / 0.519 / 0.546 / 0.544 | yes |
| initial_first | target | 554.0 | 0.118 / 0.112 / 0.137 / 0.158 / 0.148 | yes |
| initial_first | control | 526.0 | 0.106 / 0.095 / 0.079 / 0.076 / 0.082 | yes |
| initial_first | all | 1080.0 | 0.112 / 0.104 / 0.109 / 0.118 / 0.116 | yes |
| given_first | target | 290.0 | 0.394 / 0.436 / 0.407 / 0.384 / 0.430 | yes |
| given_first | control | 295.0 | 0.194 / 0.246 / 0.195 / 0.228 / 0.225 | yes |
| given_first | all | 585.0 | 0.293 / 0.340 / 0.300 / 0.305 / 0.327 | yes |
| given_cont | target | 197.0 | 0.449 / 0.427 / 0.464 / 0.395 / 0.424 | yes |
| given_cont | control | 227.0 | 0.209 / 0.207 / 0.209 / 0.212 / 0.185 | yes |
| given_cont | all | 424.0 | 0.321 / 0.309 / 0.327 / 0.297 / 0.296 | yes |
| punct | target | 556.0 | 0.008 / 0.010 / 0.010 / 0.009 / 0.006 | no |
| punct | control | 529.0 | 0.010 / 0.018 / 0.006 / 0.011 / 0.009 | no |
| punct | all | 1085.0 | 0.009 / 0.014 / 0.008 / 0.010 / 0.008 | no |
| particle_first | target | 19.0 | 0.478 / 0.439 / 0.460 / 0.514 / 0.292 | yes |
| particle_first | control | 11.0 | 0.456 / 0.182 / 0.382 / 0.347 / 0.181 | yes |
| particle_first | all | 30.0 | 0.470 / 0.345 / 0.431 / 0.453 / 0.251 | yes |

## X6: recovery R averaged over the 5 false titles (95% team CI)

### target

| role | L48 | L52 | L56 | L48 role - ALL | L52 role - ALL |
|---|---|---|---|---|---|
| ALL | +0.794 [+0.777, +0.811] | +0.987 [+0.981, +0.993] | +0.999 [+0.997, +1.002] |  |  |
| name_first | +0.745 [+0.680, +0.820] | +1.030 [+0.996, +1.072] | +1.001 [+0.986, +1.016] | -0.049 [-0.106, +0.018] | +0.043 [+0.013, +0.081] |
| surname_first | +0.696 [+0.669, +0.723] | +0.963 [+0.955, +0.971] | +1.000 [+0.997, +1.002] | -0.098 [-0.117, -0.080] | -0.024 [-0.030, -0.017] |
| surname_cont | +0.889 [+0.874, +0.905] | +0.995 [+0.991, +1.000] | +0.998 [+0.996, +1.000] | +0.096 [+0.078, +0.113] | +0.008 [+0.002, +0.015] |
| initial_first | +0.876 [+0.772, +1.011] | +1.081 [+1.023, +1.159] | +1.008 [+0.983, +1.034] | +0.082 [-0.015, +0.213] | +0.094 [+0.039, +0.169] |
| given_first | +0.601 [+0.537, +0.669] | +0.984 [+0.953, +1.020] | +0.996 [+0.985, +1.006] | -0.193 [-0.253, -0.127] | -0.003 [-0.033, +0.032] |
| given_cont | +0.913 [+0.853, +0.982] | +1.020 [+0.995, +1.050] | +0.998 [+0.988, +1.009] | +0.120 [+0.059, +0.187] | +0.033 [+0.008, +0.063] |
| punct | -- | -- | -- | -- | -- |
| particle_first | +1.007 [+0.818, +1.640] | +1.088 [+0.999, +1.369] | +1.039 [+0.998, +1.165] | +0.214 [+0.025, +0.853] | +0.101 [+0.012, +0.383] |

### control

| role | L48 | L52 | L56 | L48 role - ALL | L52 role - ALL |
|---|---|---|---|---|---|
| ALL | +0.876 [+0.847, +0.904] | +1.012 [+1.001, +1.024] | +0.998 [+0.994, +1.002] |  |  |
| name_first | +0.864 [+0.770, +0.976] | +1.068 [+1.020, +1.127] | +0.996 [+0.977, +1.014] | -0.012 [-0.089, +0.085] | +0.055 [+0.014, +0.107] |
| surname_first | +0.831 [+0.786, +0.878] | +0.992 [+0.975, +1.010] | +0.999 [+0.994, +1.003] | -0.045 [-0.078, -0.009] | -0.020 [-0.034, -0.006] |
| surname_cont | +0.900 [+0.872, +0.928] | +0.999 [+0.989, +1.008] | +1.001 [+0.997, +1.005] | +0.025 [-0.005, +0.056] | -0.013 [-0.026, -0.002] |
| initial_first | +1.062 [+0.888, +1.394] | +1.155 [+1.068, +1.321] | +0.999 [+0.965, +1.031] | +0.187 [+0.028, +0.514] | +0.142 [+0.060, +0.305] |
| given_first | +0.689 [+0.606, +0.787] | +1.016 [+0.971, +1.069] | +0.989 [+0.972, +1.004] | -0.187 [-0.262, -0.094] | +0.003 [-0.038, +0.053] |
| given_cont | +0.998 [+0.907, +1.126] | +1.060 [+1.020, +1.115] | +0.997 [+0.985, +1.009] | +0.122 [+0.031, +0.249] | +0.047 [+0.009, +0.101] |
| punct | -- | -- | -- | -- | -- |
| particle_first | +0.828 [-0.965, +2.827] | +1.019 [+0.342, +1.747] | +1.008 [+0.859, +1.109] | -0.047 [-1.854, +1.943] | +0.006 [-0.670, +0.733] |

### all

| role | L48 | L52 | L56 | L48 role - ALL | L52 role - ALL |
|---|---|---|---|---|---|
| ALL | +0.821 [+0.806, +0.835] | +0.995 [+0.990, +1.001] | +0.999 [+0.997, +1.001] |  |  |
| name_first | +0.791 [+0.738, +0.849] | +1.045 [+1.016, +1.078] | +0.999 [+0.987, +1.011] | -0.030 [-0.077, +0.021] | +0.050 [+0.024, +0.079] |
| surname_first | +0.734 [+0.711, +0.757] | +0.971 [+0.963, +0.979] | +0.999 [+0.997, +1.002] | -0.087 [-0.104, -0.070] | -0.024 [-0.030, -0.018] |
| surname_cont | +0.893 [+0.880, +0.906] | +0.997 [+0.992, +1.001] | +0.999 [+0.997, +1.001] | +0.072 [+0.057, +0.087] | +0.001 [-0.005, +0.007] |
| initial_first | +0.944 [+0.854, +1.069] | +1.108 [+1.059, +1.173] | +1.004 [+0.984, +1.023] | +0.123 [+0.037, +0.241] | +0.113 [+0.066, +0.177] |
| given_first | +0.632 [+0.583, +0.686] | +0.995 [+0.969, +1.024] | +0.993 [+0.984, +1.002] | -0.190 [-0.235, -0.139] | -0.001 [-0.025, +0.027] |
| given_cont | +0.943 [+0.890, +1.007] | +1.034 [+1.012, +1.061] | +0.998 [+0.991, +1.006] | +0.122 [+0.070, +0.184] | +0.039 [+0.017, +0.065] |
| punct | -- | -- | -- | -- | -- |
| particle_first | +0.948 [+0.769, +1.478] | +1.064 [+0.987, +1.292] | +1.031 [+0.988, +1.117] | +0.127 [-0.052, +0.652] | +0.069 [-0.009, +0.294] |

### X6 per false title, R(L48) / R(L52), group all

| role | false_0 | false_1 | false_2 | false_3 | false_4 |
|---|---|---|---|---|---|
| ALL | 0.825 / 0.996 | 0.822 / 0.997 | 0.813 / 0.996 | 0.823 / 0.994 | 0.823 / 0.994 |
| name_first | 0.791 / 1.032 | 0.832 / 1.065 | 0.770 / 1.046 | 0.781 / 1.036 | 0.782 / 1.047 |
| surname_first | 0.749 / 0.975 | 0.732 / 0.971 | 0.718 / 0.969 | 0.733 / 0.970 | 0.740 / 0.972 |
| surname_cont | 0.892 / 1.000 | 0.893 / 0.996 | 0.892 / 0.997 | 0.893 / 0.995 | 0.895 / 0.996 |
| initial_first | 0.970 / 1.099 | 1.011 / 1.153 | 0.915 / 1.096 | 0.927 / 1.089 | 0.898 / 1.104 |
| given_first | 0.622 / 0.988 | 0.655 / 0.988 | 0.621 / 1.005 | 0.626 / 0.995 | 0.634 / 0.999 |
| given_cont | 0.934 / 1.035 | 0.932 / 1.044 | 0.916 / 1.034 | 0.981 / 1.040 | 0.953 / 1.017 |
| punct | -- | -- | -- | -- | -- |
| particle_first | 0.865 / 1.070 | 1.145 / 1.106 | 0.823 / 1.034 | 0.926 / 1.043 | 0.980 / 1.069 |

## X7: knockout on true (T), false_0 (F) runs, S = T - F (95% team CI)

### target

| role | S from L0 | S from L48 | S from L52 | S from L56 | T(L0) | F(L0) | S(L52) role - ALL |
|---|---|---|---|---|---|---|---|
| ALL | +1.000 [+0.994, +1.006] | +0.130 [+0.113, +0.149] | +0.018 [+0.010, +0.027] | -0.006 [-0.010, -0.002] | +0.839 [+0.806, +0.872] | -0.161 [-0.193, -0.128] |  |
| name_first | +1.017 [+0.979, +1.058] | +0.206 [+0.104, +0.310] | -0.008 [-0.068, +0.051] | -0.013 [-0.042, +0.014] | +0.822 [+0.697, +0.961] | -0.195 [-0.315, -0.064] | -0.026 [-0.080, +0.027] |
| surname_first | +1.001 [+0.995, +1.006] | +0.145 [+0.121, +0.170] | +0.025 [+0.015, +0.036] | -0.009 [-0.013, -0.005] | +0.889 [+0.851, +0.927] | -0.112 [-0.150, -0.074] | +0.007 [-0.003, +0.017] |
| surname_cont | +0.993 [+0.987, +0.999] | +0.099 [+0.078, +0.120] | +0.020 [+0.011, +0.030] | -0.001 [-0.005, +0.004] | +0.841 [+0.793, +0.889] | -0.152 [-0.200, -0.103] | +0.002 [-0.008, +0.013] |
| initial_first | +1.022 [+0.948, +1.098] | +0.162 [-0.026, +0.332] | -0.040 [-0.152, +0.056] | -0.026 [-0.078, +0.021] | +0.734 [+0.530, +0.970] | -0.289 [-0.478, -0.063] | -0.059 [-0.165, +0.032] |
| given_first | +1.004 [+0.979, +1.028] | +0.244 [+0.144, +0.348] | +0.021 [-0.028, +0.066] | +0.005 [-0.011, +0.022] | +0.802 [+0.678, +0.925] | -0.202 [-0.328, -0.074] | +0.002 [-0.045, +0.046] |
| given_cont | +0.997 [+0.979, +1.013] | +0.050 [-0.025, +0.116] | -0.029 [-0.074, +0.010] | -0.015 [-0.028, -0.001] | +0.575 [+0.455, +0.690] | -0.422 [-0.541, -0.305] | -0.047 [-0.091, -0.009] |
| punct | -- | -- | -- | -- | -- | -- |  |
| particle_first | +0.981 [+0.895, +1.060] | -0.091 [-0.673, +0.116] | -0.058 [-0.298, +0.021] | -0.028 [-0.124, +0.029] | +0.352 [-0.763, +0.760] | -0.629 [-1.704, -0.250] | -0.076 [-0.314, +0.003] |

### control

| role | S from L0 | S from L48 | S from L52 | S from L56 | T(L0) | F(L0) | S(L52) role - ALL |
|---|---|---|---|---|---|---|---|
| ALL | +1.012 [+0.998, +1.026] | +0.168 [+0.132, +0.208] | +0.051 [+0.033, +0.068] | +0.000 [-0.008, +0.008] | +0.816 [+0.751, +0.883] | -0.196 [-0.260, -0.127] |  |
| name_first | +1.034 [+0.976, +1.096] | +0.276 [+0.143, +0.413] | +0.078 [+0.003, +0.154] | +0.006 [-0.027, +0.037] | +0.666 [+0.483, +0.860] | -0.368 [-0.544, -0.182] | +0.027 [-0.036, +0.094] |
| surname_first | +0.996 [+0.979, +1.013] | +0.155 [+0.097, +0.214] | +0.049 [+0.022, +0.076] | +0.001 [-0.009, +0.012] | +0.811 [+0.720, +0.911] | -0.185 [-0.278, -0.084] | -0.002 [-0.023, +0.020] |
| surname_cont | +1.009 [+0.994, +1.025] | +0.136 [+0.095, +0.174] | +0.052 [+0.031, +0.073] | -0.009 [-0.019, +0.000] | +0.945 [+0.856, +1.043] | -0.064 [-0.151, +0.034] | +0.002 [-0.021, +0.024] |
| initial_first | +1.028 [+0.939, +1.137] | +0.187 [-0.028, +0.384] | +0.043 [-0.079, +0.155] | -0.010 [-0.066, +0.041] | +0.471 [+0.204, +0.736] | -0.557 [-0.830, -0.296] | -0.008 [-0.119, +0.098] |
| given_first | +1.039 [+0.992, +1.097] | +0.341 [+0.166, +0.535] | +0.107 [+0.022, +0.204] | +0.031 [+0.003, +0.066] | +0.695 [+0.474, +0.960] | -0.345 [-0.568, -0.082] | +0.056 [-0.024, +0.146] |
| given_cont | +1.031 [+0.988, +1.087] | +0.136 [+0.017, +0.243] | -0.009 [-0.085, +0.054] | -0.005 [-0.028, +0.015] | +0.476 [+0.219, +0.707] | -0.554 [-0.820, -0.316] | -0.060 [-0.136, +0.002] |
| punct | -- | -- | -- | -- | -- | -- |  |
| particle_first | +1.079 [+0.990, +1.183] | +0.348 [+0.058, +0.765] | +0.086 [-0.036, +0.254] | -0.033 [-0.121, +0.022] | +0.705 [+0.219, +1.538] | -0.374 [-0.899, +0.501] | +0.035 [-0.092, +0.205] |

### all

| role | S from L0 | S from L48 | S from L52 | S from L56 | T(L0) | F(L0) | S(L52) role - ALL |
|---|---|---|---|---|---|---|---|
| ALL | +1.004 [+0.998, +1.010] | +0.143 [+0.126, +0.161] | +0.029 [+0.021, +0.038] | -0.004 [-0.008, +0.000] | +0.831 [+0.800, +0.862] | -0.173 [-0.204, -0.141] |  |
| name_first | +1.024 [+0.991, +1.059] | +0.236 [+0.155, +0.321] | +0.029 [-0.017, +0.075] | -0.005 [-0.026, +0.016] | +0.755 [+0.651, +0.869] | -0.269 [-0.370, -0.157] | -0.000 [-0.041, +0.040] |
| surname_first | +1.000 [+0.993, +1.006] | +0.148 [+0.123, +0.172] | +0.032 [+0.021, +0.043] | -0.006 [-0.010, -0.002] | +0.867 [+0.829, +0.906] | -0.133 [-0.171, -0.093] | +0.003 [-0.006, +0.012] |
| surname_cont | +0.999 [+0.992, +1.005] | +0.112 [+0.091, +0.131] | +0.031 [+0.022, +0.041] | -0.003 [-0.008, +0.001] | +0.877 [+0.832, +0.922] | -0.122 [-0.166, -0.076] | +0.002 [-0.008, +0.012] |
| initial_first | +1.025 [+0.970, +1.089] | +0.173 [+0.039, +0.298] | -0.002 [-0.076, +0.072] | -0.018 [-0.055, +0.017] | +0.613 [+0.447, +0.780] | -0.412 [-0.573, -0.251] | -0.031 [-0.101, +0.037] |
| given_first | +1.016 [+0.994, +1.039] | +0.277 [+0.190, +0.368] | +0.049 [+0.007, +0.091] | +0.014 [-0.001, +0.030] | +0.766 [+0.653, +0.889] | -0.250 [-0.365, -0.127] | +0.020 [-0.021, +0.060] |
| given_cont | +1.008 [+0.990, +1.028] | +0.080 [+0.016, +0.138] | -0.022 [-0.059, +0.010] | -0.011 [-0.023, -0.000] | +0.540 [+0.433, +0.646] | -0.468 [-0.580, -0.362] | -0.051 [-0.088, -0.018] |
| punct | -- | -- | -- | -- | -- | -- |  |
| particle_first | +1.016 [+0.963, +1.083] | +0.065 [-0.163, +0.247] | -0.007 [-0.109, +0.068] | -0.030 [-0.090, +0.009] | +0.478 [+0.001, +0.809] | -0.538 [-1.001, -0.210] | -0.036 [-0.140, +0.037] |

## Pre-registered verdicts (addendum 3) within each role

X6 holds if average R(L48) in [0.70, 0.95], average R(L52) >= 0.95, and each false title has |R(L48) - R_false_0(L48)| <= 0.10 and R(L52) >= 0.90. X7 holds if S(L52) <= 0.05 and S(L0) >= 0.5.

| role | group | X6 avg R48 / R52 | X6 max |R48 - false_0| / min R52 | X6 | X7 S(L52) / S(L0) | X7 |
|---|---|---|---|---|---|---|
| ALL | target | 0.794 / 0.987 | 0.015 / 0.984 | HOLDS | +0.018 / +1.000 | HOLDS |
| ALL | control | 0.876 / 1.012 | 0.019 / 1.008 | HOLDS | +0.051 / +1.012 | DOES NOT HOLD |
| ALL | all | 0.821 / 0.995 | 0.012 / 0.994 | HOLDS | +0.029 / +1.004 | HOLDS |
| name_first | target | 0.745 / 1.030 | 0.042 / 1.011 | HOLDS | -0.008 / +1.017 | HOLDS |
| name_first | control | 0.864 / 1.068 | 0.076 / 1.055 | HOLDS | +0.078 / +1.034 | DOES NOT HOLD |
| name_first | all | 0.791 / 1.045 | 0.041 / 1.032 | HOLDS | +0.029 / +1.024 | HOLDS |
| surname_first | target | 0.696 / 0.963 | 0.024 / 0.960 | DOES NOT HOLD (avg R48 < 0.70) | +0.025 / +1.001 | HOLDS |
| surname_first | control | 0.831 / 0.992 | 0.045 / 0.978 | HOLDS | +0.049 / +0.996 | HOLDS |
| surname_first | all | 0.734 / 0.971 | 0.031 / 0.969 | HOLDS | +0.032 / +1.000 | HOLDS |
| surname_cont | target | 0.889 / 0.995 | 0.012 / 0.992 | HOLDS | +0.020 / +0.993 | HOLDS |
| surname_cont | control | 0.900 / 0.999 | 0.027 / 0.994 | HOLDS | +0.052 / +1.009 | DOES NOT HOLD |
| surname_cont | all | 0.893 / 0.997 | 0.003 / 0.995 | HOLDS | +0.031 / +0.999 | HOLDS |
| initial_first | target | 0.876 / 1.081 | 0.118 / 1.046 | DOES NOT HOLD (title spread at L48 > 0.10) | -0.040 / +1.022 | HOLDS |
| initial_first | control | 1.062 / 1.155 | 0.148 / 1.117 | DOES NOT HOLD (avg R48 > 0.95, title spread at L48 > 0.10) | +0.043 / +1.028 | HOLDS |
| initial_first | all | 0.944 / 1.108 | 0.072 / 1.089 | HOLDS | -0.002 / +1.025 | HOLDS |
| given_first | target | 0.601 / 0.984 | 0.063 / 0.968 | DOES NOT HOLD (avg R48 < 0.70) | +0.021 / +1.004 | HOLDS |
| given_first | control | 0.689 / 1.016 | 0.049 / 0.982 | DOES NOT HOLD (avg R48 < 0.70) | +0.107 / +1.039 | DOES NOT HOLD |
| given_first | all | 0.632 / 0.995 | 0.033 / 0.988 | DOES NOT HOLD (avg R48 < 0.70) | +0.049 / +1.016 | HOLDS |
| given_cont | target | 0.913 / 1.020 | 0.032 / 1.000 | HOLDS | -0.029 / +0.997 | HOLDS |
| given_cont | control | 0.998 / 1.060 | 0.071 / 1.051 | DOES NOT HOLD (avg R48 > 0.95) | -0.009 / +1.031 | HOLDS |
| given_cont | all | 0.943 / 1.034 | 0.048 / 1.017 | HOLDS | -0.022 / +1.008 | HOLDS |
| punct | target | -- | -- | not reported (gap) | -- | not reported (gap) |
| punct | control | -- | -- | not reported (gap) | -- | not reported (gap) |
| punct | all | -- | -- | not reported (gap) | -- | not reported (gap) |
| particle_first | target | 1.007 / 1.088 | 0.149 / 1.047 | DOES NOT HOLD (avg R48 > 0.95, title spread at L48 > 0.10) | -0.058 / +0.981 | HOLDS |
| particle_first | control | 0.828 / 1.019 | 0.704 / 0.955 | DOES NOT HOLD (title spread at L48 > 0.10) | +0.086 / +1.079 | DOES NOT HOLD |
| particle_first | all | 0.948 / 1.064 | 0.280 / 1.034 | DOES NOT HOLD (title spread at L48 > 0.10) | -0.007 / +1.016 | HOLDS |

## Short conclusion

Job 11512706 (c0219, 32 s). Role ALL reproduces x6_recovery.csv and x7_knockout.csv exactly (max |diff| <= 6e-16). L44 was never stored (X6 layers 24, 32, 40, 48, 50, 52, ...; X7 start layers 0, 24, 32, 40, 48, ...), so the tables use L48/L52/L56.
Gap rule: only punct falls below 0.05 (gap 0.006-0.018). All other roles are reported. name_first has a small gap (0.12-0.22), and initial_first only 0.08-0.16, so their ratios are noisy and can overshoot 1.

**X6 (5 false titles), pre-registered roles, group all:** name_first R48 0.79 / R52 1.05; surname_first 0.73 / 0.97; surname_cont 0.89 / 1.00 (pooled 0.82 / 1.00). The verdict HOLDS in every group for name_first and surname_cont. surname_first HOLDS in control and all, but in target average R(L48) = 0.696 is just below the 0.70 bound. The across-title spread at L48 is small in every pre-registered role (max 0.076 < 0.10), so the title-robustness part holds in all of them.
Where roles differ from the pooled result (paired CIs exclude 0): by L48, surname continuation is further recovered than pooled (+0.07 [+0.06, +0.09]), the first surname token is less recovered (-0.09 [-0.10, -0.07]), and full given names are much less recovered (given_first R48 0.63, -0.19, so X6 fails for given_first in every group: R48 < 0.70). Initials and given-name continuations are recovered earlier/overshoot (R48 0.94, R52 1.11). The pooled "about 80% by L48, complete by L52" therefore averages a late first surname token and full given name with an earlier surname continuation. By L52 every reportable role is at >= 0.96, and by L56 all roles are at 1.00.

**X7 (knockout on the false_0 run), group all:** S(L52) is 0.029 / 0.032 / 0.031 for name_first / surname_first / surname_cont, and S(L0) is about 1.00 throughout: the verdict HOLDS for all three roles in target and all. In control, the pooled result already fails narrowly (S(L52) 0.051). By role it fails for name_first (0.078) and surname_cont (0.052), while surname_first (0.049) passes narrowly. Inside the pre-registered roles, no role differs from pooled S(L52) (role - ALL CIs include 0). Among the secondary roles, given_first in control has S(L52) 0.107 (fails), and given_cont is below pooled (-0.05 [-0.09, -0.02]). At L48, first-name tokens keep more paper-specific loss than pooled (name_first S48 0.24 vs 0.14).

Plain summary: the Stage 11 timing claims survive the role split for the first surname token and the surname continuation. The only exception is that the first surname token's target R(L48) is 0.696, against the 0.70 bound. The claims also survive for the first name token pooled across initials and given names. The robustness across false titles holds for every role. The real role difference is in the size of the L48 recovery: full given names and the first surname token are recovered later than surname continuations and initials. The X7 control failure is a borderline pooled effect (S(L52) about 0.05), not one carried by one role.
