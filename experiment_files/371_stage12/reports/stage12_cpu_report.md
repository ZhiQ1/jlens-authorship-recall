# Stage 12 CPU analyses: name prior and probe controls

## A. Name prior vs title, model output (log10(1/rank))

prior = no title; topic = false - no title; paper-specific = true - false.

| token role | group | prior (no title) | topic | paper-specific | true |
|---|---|---|---|---|---|
| all_tokens | target | -1.061 | -0.128 | +0.481 | -0.708 |
| all_tokens | control | -1.150 | -0.053 | +0.200 | -1.004 |
| surname_first | target | -2.164 | -0.138 | +0.921 | -1.380 |
| surname_first | control | -2.169 | -0.039 | +0.291 | -1.917 |
| surname_cont | target | -0.812 | -0.148 | +0.718 | -0.242 |
| surname_cont | control | -0.890 | -0.053 | +0.336 | -0.607 |
| given_first | target | -2.235 | -0.183 | +0.412 | -2.005 |
| given_first | control | -2.246 | -0.078 | +0.236 | -2.089 |
| initial_first | target | -0.871 | -0.199 | +0.146 | -0.924 |
| initial_first | control | -0.884 | -0.120 | +0.081 | -0.923 |
| punct | target | -0.020 | -0.012 | +0.003 | -0.029 |
| punct | control | -0.038 | -0.010 | +0.007 | -0.041 |

| token role | target - control (within bin): prior | topic | paper-specific | true |
|---|---|---|---|---|
| all_tokens | +0.087 [+0.070, +0.103] | -0.047 [-0.055, -0.038] | +0.207 [+0.195, +0.220] | +0.247 [+0.229, +0.265] |
| surname_first | +0.022 [-0.019, +0.063] | -0.055 [-0.072, -0.038] | +0.423 [+0.393, +0.454] | +0.391 [+0.345, +0.435] |
| surname_cont | +0.063 [+0.028, +0.096] | -0.076 [-0.094, -0.058] | +0.279 [+0.254, +0.305] | +0.266 [+0.236, +0.296] |
| given_first | +0.036 [-0.021, +0.090] | -0.060 [-0.086, -0.035] | +0.180 [+0.141, +0.220] | +0.156 [+0.096, +0.217] |
| initial_first | +0.010 [-0.011, +0.031] | -0.028 [-0.045, -0.012] | +0.052 [+0.033, +0.070] | +0.033 [+0.010, +0.057] |

## B. Does the name prior explain recognition? (R0/R1 papers, centred within citation bin)

| metric | Spearman with multiple-choice orders right (0-4) | mean at 0 / 1 / 2 / 3 / 4 right |
|---|---|---|
| prior | +0.085 [+0.063, +0.106] | -0.040 / -0.048 / -0.008 / -0.006 / +0.024 |
| spec | +0.329 [+0.312, +0.346] | -0.131 / -0.086 / -0.059 / -0.019 / +0.068 |

## C. Name commonness: log10 count of the surname among all cohort authors (per-paper mean)

| group | Spearman with prior | Spearman with paper-specific |
|---|---|---|
| all | -0.215 | -0.091 |
| target | -0.209 | -0.099 |
| control | -0.168 | -0.008 |

target - control in surname commonness (within bin): -0.199 [-0.233, -0.166]

## X1. Controls for the Stage 11 title-position probe (E4b)

spec = probe(true-title residual) - probe(false_0-title residual); a real paper-specific signal should vanish when the gold authors are those of another paper.

| layer | control | spec, all papers | target - control (within bin) |
|---|---|---|---|
| L24 | probe (as in Stage 11) | +0.045 [+0.040, +0.050] | +0.024 [+0.010, +0.038] |
| L24 | gold = random other paper | -0.002 [-0.007, +0.003] | -0.012 [-0.025, +0.002] |
| L24 | gold = random paper of the same field | +0.002 [-0.003, +0.007] | -0.003 [-0.017, +0.011] |
| L24 | probe trained on FALSE-title pairs | +0.068 [+0.063, +0.073] | +0.050 [+0.034, +0.065] |
| L40 | probe (as in Stage 11) | +0.062 [+0.056, +0.067] | +0.032 [+0.017, +0.048] |
| L40 | gold = random other paper | -0.003 [-0.008, +0.003] | -0.009 [-0.024, +0.007] |
| L40 | gold = random paper of the same field | -0.004 [-0.010, +0.002] | -0.001 [-0.016, +0.013] |
| L40 | probe trained on FALSE-title pairs | +0.081 [+0.076, +0.087] | +0.051 [+0.034, +0.067] |
| L56 | probe (as in Stage 11) | +0.081 [+0.075, +0.087] | +0.038 [+0.021, +0.055] |
| L56 | gold = random other paper | +0.001 [-0.005, +0.006] | -0.006 [-0.024, +0.010] |
| L56 | gold = random paper of the same field | +0.000 [-0.006, +0.006] | -0.009 [-0.025, +0.008] |
| L56 | probe trained on FALSE-title pairs | +0.094 [+0.088, +0.100] | +0.052 [+0.035, +0.069] |
