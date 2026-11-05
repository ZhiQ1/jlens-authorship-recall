# Stage 12 N2 by readout and layer (V21, POST-HOC)

Script `~/jlens_work/13_stage13/stage12_n2_layers.py`, run 2026-11-05 01:43. CPU only, saved ranks (371_stage12/raw/prior_pure, 72 shards; Stage 10 true / delete raw at the same readout and layer). **Post-hoc: Stage 12 analysed only final@63.**
Pure prompt: "The following is the name of a researcher.\nName:" (no paper). Score = log10(1/rank) of the gold name tokens, averaged within paper. year_prompt = no-title prompt (with year) - pure; title_gain = true - no title.
Groups: cohort group_tight (target 4,621, control 2,220). Target - control within citation bin, bins with >= 30 papers per group (Stage 10/12 rule). 95% intervals: team-cluster (addendum 2, primary) and paper bootstrap (as Stage 12), 2,000 draws each.
CSV: `/scratch/zhang.zhiqi2/jlens/371_stage12/summary/N2_prior_pure_layers.csv`.

Self-check: final@63 reproduces summary/N2_prior_pure.csv exactly.

## Group means (team CI)

| readout | layer | group | pure prior | no title (year) | true title | no title - pure | true - no title |
|---|---|---|---|---|---|---|---|
| final | L63 | all | -1.229 [-1.235, -1.222] | -1.089 [-1.097, -1.082] | -0.812 [-0.821, -0.802] | +0.139 [+0.135, +0.143] | +0.278 [+0.273, +0.283] |
| final | L63 | target | -1.215 [-1.223, -1.208] | -1.061 [-1.069, -1.052] | -0.708 [-0.719, -0.698] | +0.155 [+0.151, +0.158] | +0.353 [+0.346, +0.360] |
| final | L63 | control | -1.261 [-1.273, -1.248] | -1.150 [-1.163, -1.135] | -1.004 [-1.018, -0.989] | +0.111 [+0.104, +0.118] | +0.146 [+0.137, +0.155] |
| logit | L48 | all | -4.566 [-4.572, -4.560] | -4.498 [-4.503, -4.492] | -4.418 [-4.424, -4.412] | +0.068 [+0.066, +0.070] | +0.080 [+0.078, +0.083] |
| logit | L48 | target | -4.576 [-4.584, -4.569] | -4.505 [-4.512, -4.498] | -4.428 [-4.435, -4.421] | +0.071 [+0.069, +0.074] | +0.077 [+0.073, +0.080] |
| logit | L48 | control | -4.558 [-4.571, -4.545] | -4.492 [-4.504, -4.481] | -4.408 [-4.421, -4.395] | +0.065 [+0.061, +0.070] | +0.085 [+0.080, +0.090] |
| logit | L56 | all | -3.779 [-3.791, -3.767] | -3.493 [-3.503, -3.482] | -3.496 [-3.511, -3.481] | +0.286 [+0.281, +0.291] | -0.003 [-0.011, +0.004] |
| logit | L56 | target | -3.803 [-3.816, -3.789] | -3.502 [-3.514, -3.491] | -3.520 [-3.534, -3.505] | +0.301 [+0.295, +0.306] | -0.017 [-0.026, -0.009] |
| logit | L56 | control | -3.766 [-3.794, -3.740] | -3.501 [-3.525, -3.480] | -3.505 [-3.536, -3.476] | +0.264 [+0.253, +0.275] | -0.004 [-0.018, +0.011] |
| logit | L62 | all | -1.565 [-1.572, -1.558] | -1.226 [-1.233, -1.219] | -1.021 [-1.030, -1.011] | +0.339 [+0.333, +0.345] | +0.206 [+0.199, +0.212] |
| logit | L62 | target | -1.560 [-1.569, -1.551] | -1.198 [-1.207, -1.190] | -0.931 [-0.943, -0.920] | +0.362 [+0.356, +0.368] | +0.267 [+0.258, +0.276] |
| logit | L62 | control | -1.592 [-1.609, -1.577] | -1.291 [-1.307, -1.276] | -1.205 [-1.223, -1.189] | +0.301 [+0.289, +0.313] | +0.086 [+0.074, +0.098] |
| jlens_public | L48 | all | -3.731 [-3.740, -3.721] | -2.711 [-2.720, -2.702] | -2.950 [-2.962, -2.939] | +1.020 [+1.011, +1.030] | -0.239 [-0.247, -0.232] |
| jlens_public | L48 | target | -3.762 [-3.771, -3.753] | -2.711 [-2.722, -2.699] | -3.039 [-3.053, -3.025] | +1.051 [+1.041, +1.060] | -0.328 [-0.337, -0.318] |
| jlens_public | L48 | control | -3.691 [-3.708, -3.676] | -2.714 [-2.733, -2.695] | -2.824 [-2.845, -2.803] | +0.978 [+0.958, +0.997] | -0.110 [-0.122, -0.099] |
| jlens_public | L56 | all | -3.476 [-3.491, -3.458] | -3.096 [-3.108, -3.082] | -3.178 [-3.196, -3.158] | +0.380 [+0.373, +0.386] | -0.082 [-0.092, -0.072] |
| jlens_public | L56 | target | -3.518 [-3.531, -3.504] | -3.123 [-3.136, -3.112] | -3.295 [-3.312, -3.278] | +0.394 [+0.388, +0.401] | -0.172 [-0.184, -0.160] |
| jlens_public | L56 | control | -3.433 [-3.462, -3.405] | -3.075 [-3.098, -3.053] | -3.057 [-3.090, -3.022] | +0.358 [+0.344, +0.371] | +0.018 [-0.001, +0.036] |
| jlens_public | L62 | all | -1.537 [-1.544, -1.531] | -1.365 [-1.371, -1.359] | -1.085 [-1.093, -1.075] | +0.172 [+0.168, +0.176] | +0.280 [+0.274, +0.286] |
| jlens_public | L62 | target | -1.535 [-1.544, -1.527] | -1.347 [-1.355, -1.339] | -1.002 [-1.012, -0.991] | +0.188 [+0.184, +0.193] | +0.345 [+0.337, +0.354] |
| jlens_public | L62 | control | -1.559 [-1.573, -1.546] | -1.414 [-1.427, -1.401] | -1.257 [-1.273, -1.242] | +0.144 [+0.136, +0.152] | +0.157 [+0.146, +0.168] |

## Target - control within citation bin

| readout | layer | estimand | estimate | team CI | paper CI | bins |
|---|---|---|---|---|---|---|
| final | L63 | pure | +0.0471 | [+0.0312, +0.0616] | [+0.0318, +0.0625] | 10 |
| final | L63 | delete | +0.0866 | [+0.0692, +0.1027] | [+0.0696, +0.1037] | 10 |
| final | L63 | true | +0.2473 | [+0.2280, +0.2647] | [+0.2290, +0.2654] | 10 |
| final | L63 | title_gain | +0.1607 | [+0.1483, +0.1730] | [+0.1482, +0.1725] | 10 |
| logit | L48 | pure | -0.0090 | [-0.0249, +0.0077] | [-0.0254, +0.0077] | 10 |
| logit | L48 | delete | -0.0045 | [-0.0194, +0.0110] | [-0.0196, +0.0104] | 10 |
| logit | L48 | true | -0.0113 | [-0.0274, +0.0055] | [-0.0271, +0.0050] | 10 |
| logit | L48 | title_gain | -0.0068 | [-0.0133, -0.0004] | [-0.0127, -0.0007] | 10 |
| logit | L56 | pure | -0.0147 | [-0.0453, +0.0182] | [-0.0429, +0.0143] | 10 |
| logit | L56 | delete | +0.0122 | [-0.0134, +0.0390] | [-0.0119, +0.0367] | 10 |
| logit | L56 | true | +0.0351 | [+0.0009, +0.0706] | [+0.0065, +0.0657] | 10 |
| logit | L56 | title_gain | +0.0229 | [+0.0048, +0.0421] | [+0.0051, +0.0412] | 10 |
| logit | L62 | pure | +0.0388 | [+0.0190, +0.0572] | [+0.0211, +0.0572] | 10 |
| logit | L62 | delete | +0.0835 | [+0.0643, +0.1018] | [+0.0647, +0.1026] | 10 |
| logit | L62 | true | +0.2473 | [+0.2244, +0.2694] | [+0.2261, +0.2685] | 10 |
| logit | L62 | title_gain | +0.1638 | [+0.1481, +0.1792] | [+0.1484, +0.1791] | 10 |
| jlens_public | L48 | pure | -0.0696 | [-0.0865, -0.0525] | [-0.0868, -0.0526] | 10 |
| jlens_public | L48 | delete | -0.0246 | [-0.0496, -0.0004] | [-0.0475, -0.0009] | 10 |
| jlens_public | L48 | true | -0.1334 | [-0.1609, -0.1074] | [-0.1593, -0.1061] | 10 |
| jlens_public | L48 | title_gain | -0.1089 | [-0.1261, -0.0915] | [-0.1264, -0.0924] | 10 |
| jlens_public | L56 | pure | -0.0755 | [-0.1032, -0.0449] | [-0.1016, -0.0478] | 10 |
| jlens_public | L56 | delete | -0.0584 | [-0.0810, -0.0341] | [-0.0806, -0.0355] | 10 |
| jlens_public | L56 | true | -0.1075 | [-0.1427, -0.0704] | [-0.1400, -0.0772] | 10 |
| jlens_public | L56 | title_gain | -0.0491 | [-0.0762, -0.0227] | [-0.0721, -0.0268] | 10 |
| jlens_public | L62 | pure | +0.0271 | [+0.0103, +0.0428] | [+0.0114, +0.0430] | 10 |
| jlens_public | L62 | delete | +0.0611 | [+0.0444, +0.0764] | [+0.0450, +0.0774] | 10 |
| jlens_public | L62 | true | +0.2249 | [+0.2045, +0.2453] | [+0.2061, +0.2449] | 10 |
| jlens_public | L62 | title_gain | +0.1638 | [+0.1486, +0.1791] | [+0.1491, +0.1781] | 10 |

## Reading (post-hoc)

- Stage 12 N2 (final@63): target papers' authors are slightly more expected even with no paper at all (pure prior target - control), which is the name-prior part of the target - control output difference. The table above shows how much of that prior, of the no-title (year) level and of the true-title level is already readable by the logit / public J-lens at L48, L56 and L62.
- Compare the pure-prior target - control with the true-title target - control at the same layer: the share of the true-title difference that a paper-free prior already gives is the prior-only part at that layer.
- The logit lens at L48 is near the floor for every prompt (about -4.5); the public J-lens at L48 / L56 is not at the floor, but there the true title scores BELOW the no-title prompt (true - no title < 0, more so for target papers), so at those layers its target - control values are negative and do not show the output-level pattern; only L62 (both lenses) reproduces the output pattern (pure prior +0.03-0.04, true title +0.22-0.25).
- The pure prompt differs from the paper prompts in everything before the name, so "pure" vs "no title" compares two prompts, not a single intervention.
