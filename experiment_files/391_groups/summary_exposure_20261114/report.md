# Exposure threshold by citation bin -- exploratory (探索性), post hoc

Not preregistered. CPU only, existing Stage 10 outputs. Script: ~/jlens_work/14_groups/exposure_20261114.py.

Cohort 9,108 papers, 13 Stage 10 citation bins. CI = author-team cluster bootstrap 95% (2,000 draws, 7247 teams, archived folds_own9108_k5s13 team ids, groups_core.Engine, seed 391).

Definitions: recognition = mc_team_outcome_tight == strong (pass rule behind A/C vs B/D; uncertain counted as not passed); recall = recall_level R1 or R2 (>=1 correct author written, m >= 1); spec = true - mean of 5 false titles, readout final L63, log10(1/rank); target/control = Stage 10 group_tight.

| bin | n | recognition [95% CI] | recog. excl. uncertain | mean orders right (0-4) | recall [95% CI] | n tgt/ctl | spec tgt | spec ctl | spec tgt-ctl [95% CI] | 1st-author tok0 tgt-ctl |
|---|---|---|---|---|---|---|---|---|---|---|
| 0-2 | 796 | 0.255 [0.226, 0.286] | 0.366 | 2.02 [1.92, 2.13] | 0.016 [0.006, 0.027] | 200/352 | 0.347 | 0.158 | 0.189 [0.153, 0.227] | 0.136 [0.053, 0.225] |
| 3-4 | 799 | 0.260 [0.229, 0.293] | 0.369 | 2.00 [1.90, 2.11] | 0.023 [0.012, 0.033] | 207/355 | 0.360 | 0.169 | 0.191 [0.152, 0.228] | 0.075 [-0.002, 0.158] |
| 5-8 | 800 | 0.296 [0.265, 0.330] | 0.417 | 2.13 [2.03, 2.23] | 0.020 [0.011, 0.031] | 237/332 | 0.366 | 0.179 | 0.187 [0.153, 0.220] | 0.151 [0.076, 0.230] |
| 9-16 | 800 | 0.360 [0.327, 0.396] | 0.512 | 2.37 [2.26, 2.48] | 0.024 [0.013, 0.036] | 288/275 | 0.377 | 0.202 | 0.175 [0.142, 0.209] | 0.060 [-0.014, 0.137] |
| 17-32 | 800 | 0.410 [0.377, 0.445] | 0.584 | 2.58 [2.48, 2.69] | 0.036 [0.024, 0.050] | 327/234 | 0.410 | 0.225 | 0.185 [0.151, 0.220] | 0.085 [0.015, 0.156] |
| 33-64 | 800 | 0.505 [0.471, 0.542] | 0.686 | 2.80 [2.71, 2.91] | 0.048 [0.034, 0.063] | 401/185 | 0.442 | 0.199 | 0.243 [0.208, 0.278] | 0.061 [-0.014, 0.137] |
| 65-128 | 800 | 0.554 [0.519, 0.588] | 0.729 | 2.95 [2.86, 3.05] | 0.056 [0.040, 0.072] | 441/165 | 0.456 | 0.249 | 0.207 [0.166, 0.244] | 0.075 [-0.008, 0.159] |
| 129-256 | 800 | 0.634 [0.597, 0.668] | 0.801 | 3.16 [3.06, 3.25] | 0.077 [0.059, 0.097] | 497/126 | 0.489 | 0.248 | 0.241 [0.201, 0.284] | 0.077 [-0.006, 0.157] |
| 257-512 | 800 | 0.689 [0.656, 0.723] | 0.840 | 3.30 [3.21, 3.39] | 0.111 [0.090, 0.134] | 533/105 | 0.510 | 0.274 | 0.237 [0.196, 0.278] | 0.079 [-0.007, 0.166] |
| 513-1024 | 800 | 0.800 [0.771, 0.827] | 0.922 | 3.59 [3.52, 3.66] | 0.176 [0.151, 0.204] | 603/53 | 0.548 | 0.250 | 0.298 [0.236, 0.358] | 0.170 [0.050, 0.286] |
| 1025-2048 | 665 | 0.887 [0.861, 0.910] | 0.953 | 3.76 [3.70, 3.81] | 0.248 [0.216, 0.281] | 539/29 | 0.570 | 0.225 | 0.345 [0.269, 0.422] (ctl<30, descr.) | 0.168 [-0.078, 0.372] |
| 2049-4096 | 326 | 0.936 [0.907, 0.960] | 0.971 | 3.86 [3.79, 3.92] | 0.322 [0.272, 0.376] | 264/9 | 0.618 | 0.270 | 0.348 [0.191, 0.499] (ctl<30, descr.) | 0.272 [-0.033, 0.531] |
| 4097+ | 122 | 0.992 [0.973, 1.000] | 1.000 | 3.98 [3.95, 4.00] | 0.574 [0.479, 0.661] | 84/0 | 0.644 | NA | NA [NA, NA] (ctl<30, descr.) | NA [NA, NA] |

Pooled within-bin target - control (bins with >= 30 per group: 0-2;129-256;17-32;257-512;3-4;33-64;5-8;513-1024;65-128;9-16): all tokens 0.207 [0.196, 0.220]; first author all tokens 0.222 [0.207, 0.238]; first author first token 0.093 [0.068, 0.120].

## Logistic fits (outcome ~ log10(1+citations) + year centred), 50% threshold at mean year

| outcome | n | slope per log10 [95% CI] | year slope | citations at 50% [95% CI] | in observed range |
|---|---|---|---|---|---|
| recognition | 9108 | 1.072 [1.020, 1.123] | 0.006 [0.003, 0.009] | 40 [36, 44] | True |
| recognition_excl_uncertain | 7046 | 1.201 [1.135, 1.264] | 0.009 [0.005, 0.013] | 9 [8, 11] | True |
| recall | 9108 | 1.260 [1.156, 1.372] | -0.000 [-0.006, 0.006] | 11038 [8172, 15607] | True |

## Checks

- spec all tokens: Stage 10 summary_title vs 391_groups paper_signal max |diff| = 5.95e-08.
- first author all tokens: recomputed from raw vs 391_groups author_signal max |diff| = 9.01e-08.

## Caveats

- Exploratory (探索性), post hoc; not preregistered; descriptive.
- Bins were built by stratified sampling (800 per bin, fewer at the top); rates are per-bin, not population rates.
- Group (target/control) is defined by recognition + recall, so recognition and target share move together by construction; spec target - control within a bin is the only group comparison.
- Control has < 30 papers in 1025-2048, 2049-4096 and 4097+ (none in 4097+): descriptive only.
- Recognition at the bottom bins includes the ~25% fixed-preference/guess floor of the 4-order multiple-choice rule.
- Logistic fit assumes a monotone logit-linear trend in log10 citations; thresholds outside the observed range are extrapolation.

Files: exposure_by_bin.csv, logistic_thresholds.csv, exposure_curves.png/.svg, run log in ~/jlens_work/14_groups/logs/.
