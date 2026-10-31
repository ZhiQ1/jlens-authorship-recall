# Stage 13 X1 relative to random paper C (V31)

Shards 24; papers: test 582, tune 596. Same data, estimator and team-cluster bootstrap as `x1_report.md` (seed 101, 2,000 draws, per split), so each draw is the same draw as there.
R'(t) = R(t) - R(C) = mean(t - C) / mean(clean - corrupt), paired per pair. N(t) = (R(t) - R(C)) / (1 - R(C)) = mean(t - C) / mean(clean - C), i.e. C instead of B as the baseline.
Rule (addendum 2, L24+): task-independent if R'(a) - R'(year) and R'(a) - R'(field) both have intervals inside [-b, b] and R'(authors) > 0; task-specific if R'(a) - R'(year) > b. Written bound b = 0.1; b = 0.02 shown as a stricter variant. L4-L16: text-replacement control only.

## Reproduction / identity checks

- R(authors/year/field/C) and the original difference intervals reproduced from `x1_recovery.csv`: all match to 1e-9.
- R'(a) - R'(t) equals the uncorrected R(a) - R(t) in every bootstrap draw (max |difference| over draws, layers, splits: 3.8e-15). Because the same C is subtracted from both tasks in each pair, C cancels: **correcting for C does not change the authors - year / authors - field differences or their intervals.**
- Hence the addendum-2 verdict on the C-corrected curves (R') is identical to the original verdict at every layer; the R'(authors) > 0 condition is the original R(authors) - R(C) > 0.

## test (confirmatory)

clean - corrupt 0.347

### C-corrected recoveries R'(t) = R(t) - R(C)

| layer | R(C) | R'(authors) | R'(year) | R'(field) | R'(a) - R'(year) | R'(a) - R'(field) | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|
| L4 | -0.149 [-0.233, -0.069] | +1.153 [+1.074, +1.238] | +1.152 [+1.074, +1.237] | +1.155 [+1.077, +1.241] | +0.001 [-0.005, +0.007] | -0.002 [-0.007, +0.002] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | -0.139 [-0.224, -0.058] | +1.143 [+1.063, +1.228] | +1.143 [+1.064, +1.229] | +1.142 [+1.062, +1.228] | -0.000 [-0.006, +0.006] | +0.001 [-0.005, +0.007] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | -0.132 [-0.217, -0.054] | +1.133 [+1.053, +1.218] | +1.129 [+1.049, +1.213] | +1.130 [+1.050, +1.213] | +0.004 [-0.003, +0.012] | +0.004 [-0.003, +0.011] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | -0.097 [-0.178, -0.024] | +1.088 [+1.012, +1.169] | +1.083 [+1.008, +1.164] | +1.090 [+1.015, +1.170] | +0.006 [-0.004, +0.015] | -0.001 [-0.010, +0.007] | task-independent | task-independent |
| L32 | -0.065 [-0.140, +0.004] | +1.035 [+0.962, +1.114] | +1.031 [+0.959, +1.108] | +1.034 [+0.960, +1.110] | +0.005 [-0.006, +0.016] | +0.001 [-0.006, +0.009] | task-independent | task-independent |
| L40 | -0.007 [-0.077, +0.056] | +0.928 [+0.859, +1.002] | +0.924 [+0.857, +0.999] | +0.922 [+0.850, +0.997] | +0.003 [-0.008, +0.014] | +0.006 [-0.003, +0.015] | task-independent | task-independent |
| L48 | +0.122 [+0.084, +0.160] | +0.302 [+0.256, +0.349] | +0.283 [+0.239, +0.328] | +0.294 [+0.249, +0.341] | +0.019 [+0.012, +0.026] | +0.008 [+0.001, +0.014] | task-independent | undecided |

### Normalised N(t) = (R(t) - R(C)) / (1 - R(C)), and share R'(t) / R'(authors)

| layer | clean - C | N(authors) | N(year) | N(field) | N(a) - N(year) | N(a) - N(field) | share year | share field | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|---|---|
| L4 | 0.399 | +1.004 [+0.998, +1.010] | +1.003 [+0.996, +1.010] | +1.006 [+0.999, +1.012] | +0.001 [-0.004, +0.006] | -0.002 [-0.006, +0.002] | +0.999 [+0.994, +1.004] | +1.002 [+0.998, +1.006] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | 0.396 | +1.004 [+0.996, +1.011] | +1.004 [+0.995, +1.012] | +1.003 [+0.995, +1.011] | -0.000 [-0.005, +0.005] | +0.001 [-0.005, +0.006] | +1.000 [+0.995, +1.005] | +0.999 [+0.994, +1.005] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | 0.393 | +1.001 [+0.992, +1.010] | +0.997 [+0.987, +1.007] | +0.998 [+0.988, +1.007] | +0.004 [-0.002, +0.011] | +0.003 [-0.003, +0.009] | +0.996 [+0.989, +1.002] | +0.997 [+0.991, +1.003] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | 0.381 | +0.992 [+0.979, +1.004] | +0.986 [+0.972, +1.001] | +0.993 [+0.978, +1.006] | +0.005 [-0.003, +0.014] | -0.001 [-0.009, +0.006] | +0.995 [+0.986, +1.003] | +1.001 [+0.994, +1.009] | task-independent | task-independent |
| L32 | 0.370 | +0.972 [+0.955, +0.988] | +0.968 [+0.949, +0.986] | +0.971 [+0.953, +0.988] | +0.004 [-0.006, +0.015] | +0.001 [-0.006, +0.009] | +0.995 [+0.985, +1.006] | +0.999 [+0.991, +1.006] | task-independent | task-independent |
| L40 | 0.350 | +0.921 [+0.897, +0.947] | +0.918 [+0.893, +0.944] | +0.915 [+0.890, +0.942] | +0.003 [-0.008, +0.014] | +0.006 [-0.003, +0.015] | +0.996 [+0.985, +1.008] | +0.993 [+0.984, +1.003] | task-independent | task-independent |
| L48 | 0.305 | +0.344 [+0.301, +0.386] | +0.322 [+0.280, +0.364] | +0.335 [+0.292, +0.379] | +0.022 [+0.014, +0.030] | +0.009 [+0.001, +0.016] | +0.936 [+0.911, +0.960] | +0.974 [+0.951, +0.996] | task-independent | undecided |

## tune

clean - corrupt 0.390

### C-corrected recoveries R'(t) = R(t) - R(C)

| layer | R(C) | R'(authors) | R'(year) | R'(field) | R'(a) - R'(year) | R'(a) - R'(field) | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|
| L4 | -0.091 [-0.161, -0.027] | +1.091 [+1.026, +1.160] | +1.090 [+1.026, +1.161] | +1.090 [+1.025, +1.160] | +0.001 [-0.003, +0.005] | +0.001 [-0.003, +0.005] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | -0.083 [-0.153, -0.018] | +1.081 [+1.016, +1.151] | +1.079 [+1.015, +1.151] | +1.077 [+1.013, +1.148] | +0.001 [-0.003, +0.006] | +0.004 [-0.001, +0.008] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | -0.077 [-0.147, -0.014] | +1.074 [+1.011, +1.145] | +1.072 [+1.008, +1.142] | +1.069 [+1.005, +1.139] | +0.002 [-0.004, +0.008] | +0.006 [+0.000, +0.011] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | -0.059 [-0.126, +0.002] | +1.054 [+0.991, +1.123] | +1.044 [+0.982, +1.112] | +1.050 [+0.988, +1.118] | +0.009 [+0.002, +0.017] | +0.004 [-0.002, +0.010] | task-independent | task-independent |
| L32 | -0.034 [-0.098, +0.025] | +1.012 [+0.952, +1.079] | +1.005 [+0.945, +1.073] | +1.010 [+0.949, +1.077] | +0.007 [-0.002, +0.016] | +0.002 [-0.006, +0.010] | task-independent | task-independent |
| L40 | +0.026 [-0.032, +0.079] | +0.891 [+0.835, +0.954] | +0.882 [+0.826, +0.944] | +0.884 [+0.828, +0.947] | +0.009 [-0.000, +0.018] | +0.007 [-0.001, +0.016] | task-independent | task-independent |
| L48 | +0.123 [+0.090, +0.157] | +0.293 [+0.257, +0.328] | +0.272 [+0.237, +0.307] | +0.276 [+0.241, +0.311] | +0.021 [+0.014, +0.028] | +0.017 [+0.010, +0.023] | task-independent | undecided |

### Normalised N(t) = (R(t) - R(C)) / (1 - R(C)), and share R'(t) / R'(authors)

| layer | clean - C | N(authors) | N(year) | N(field) | N(a) - N(year) | N(a) - N(field) | share year | share field | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|---|---|
| L4 | 0.425 | +1.000 [+0.995, +1.004] | +0.999 [+0.994, +1.004] | +0.999 [+0.994, +1.004] | +0.001 [-0.003, +0.004] | +0.001 [-0.002, +0.004] | +0.999 [+0.996, +1.003] | +0.999 [+0.996, +1.002] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | 0.422 | +0.998 [+0.992, +1.004] | +0.997 [+0.990, +1.003] | +0.995 [+0.988, +1.001] | +0.001 [-0.003, +0.005] | +0.003 [-0.001, +0.007] | +0.999 [+0.995, +1.003] | +0.997 [+0.993, +1.001] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | 0.420 | +0.997 [+0.990, +1.004] | +0.995 [+0.987, +1.004] | +0.992 [+0.984, +1.000] | +0.002 [-0.004, +0.008] | +0.005 [+0.000, +0.010] | +0.998 [+0.992, +1.004] | +0.995 [+0.990, +1.000] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | 0.413 | +0.995 [+0.985, +1.005] | +0.986 [+0.974, +0.998] | +0.991 [+0.981, +1.002] | +0.009 [+0.002, +0.016] | +0.004 [-0.002, +0.009] | +0.991 [+0.984, +0.998] | +0.996 [+0.991, +1.002] | task-independent | task-independent |
| L32 | 0.403 | +0.979 [+0.963, +0.994] | +0.972 [+0.956, +0.989] | +0.977 [+0.962, +0.993] | +0.007 [-0.002, +0.015] | +0.002 [-0.006, +0.010] | +0.993 [+0.984, +1.002] | +0.998 [+0.990, +1.006] | task-independent | task-independent |
| L40 | 0.379 | +0.915 [+0.893, +0.938] | +0.906 [+0.883, +0.930] | +0.908 [+0.885, +0.930] | +0.009 [-0.000, +0.018] | +0.007 [-0.001, +0.016] | +0.990 [+0.980, +1.000] | +0.992 [+0.982, +1.002] | task-independent | task-independent |
| L48 | 0.342 | +0.334 [+0.299, +0.370] | +0.310 [+0.275, +0.345] | +0.315 [+0.280, +0.351] | +0.024 [+0.016, +0.032] | +0.019 [+0.011, +0.027] | +0.928 [+0.904, +0.951] | +0.943 [+0.919, +0.967] | task-independent | undecided |

## all

clean - corrupt 0.369

### C-corrected recoveries R'(t) = R(t) - R(C)

| layer | R(C) | R'(authors) | R'(year) | R'(field) | R'(a) - R'(year) | R'(a) - R'(field) | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|
| L4 | -0.118 [-0.170, -0.067] | +1.120 [+1.068, +1.173] | +1.119 [+1.068, +1.172] | +1.120 [+1.068, +1.172] | +0.001 [-0.002, +0.004] | -0.001 [-0.003, +0.003] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | -0.109 [-0.162, -0.059] | +1.109 [+1.058, +1.162] | +1.109 [+1.057, +1.162] | +1.107 [+1.055, +1.160] | +0.001 [-0.003, +0.004] | +0.002 [-0.001, +0.006] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | -0.103 [-0.156, -0.053] | +1.102 [+1.052, +1.154] | +1.099 [+1.047, +1.150] | +1.097 [+1.047, +1.149] | +0.003 [-0.001, +0.008] | +0.005 [+0.000, +0.009] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | -0.077 [-0.128, -0.030] | +1.070 [+1.021, +1.120] | +1.062 [+1.014, +1.112] | +1.069 [+1.020, +1.119] | +0.008 [+0.002, +0.013] | +0.001 [-0.004, +0.006] | task-independent | task-independent |
| L32 | -0.048 [-0.095, -0.003] | +1.023 [+0.974, +1.072] | +1.017 [+0.968, +1.065] | +1.021 [+0.972, +1.070] | +0.006 [-0.001, +0.013] | +0.002 [-0.004, +0.007] | task-independent | task-independent |
| L40 | +0.011 [-0.034, +0.054] | +0.908 [+0.863, +0.955] | +0.902 [+0.857, +0.949] | +0.901 [+0.856, +0.948] | +0.006 [-0.000, +0.014] | +0.007 [+0.001, +0.013] | task-independent | task-independent |
| L48 | +0.123 [+0.097, +0.148] | +0.297 [+0.268, +0.327] | +0.277 [+0.248, +0.306] | +0.285 [+0.254, +0.315] | +0.020 [+0.015, +0.025] | +0.013 [+0.008, +0.018] | task-independent | undecided |

### Normalised N(t) = (R(t) - R(C)) / (1 - R(C)), and share R'(t) / R'(authors)

| layer | clean - C | N(authors) | N(year) | N(field) | N(a) - N(year) | N(a) - N(field) | share year | share field | verdict b=0.1 | verdict b=0.02 |
|---|---|---|---|---|---|---|---|---|---|---|
| L4 | 0.412 | +1.002 [+0.998, +1.005] | +1.001 [+0.997, +1.005] | +1.002 [+0.998, +1.006] | +0.001 [-0.002, +0.004] | -0.000 [-0.003, +0.002] | +0.999 [+0.996, +1.002] | +1.000 [+0.998, +1.003] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L8 | 0.409 | +1.001 [+0.996, +1.005] | +1.000 [+0.994, +1.006] | +0.999 [+0.993, +1.004] | +0.000 [-0.003, +0.004] | +0.002 [-0.001, +0.005] | +1.000 [+0.996, +1.003] | +0.998 [+0.995, +1.001] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L16 | 0.407 | +0.999 [+0.993, +1.005] | +0.996 [+0.989, +1.002] | +0.995 [+0.989, +1.001] | +0.003 [-0.001, +0.007] | +0.004 [+0.000, +0.008] | +0.997 [+0.993, +1.001] | +0.996 [+0.992, +1.000] | text-replacement control (no conclusion) | text-replacement control (no conclusion) |
| L24 | 0.397 | +0.993 [+0.985, +1.002] | +0.986 [+0.977, +0.996] | +0.992 [+0.983, +1.001] | +0.007 [+0.002, +0.013] | +0.001 [-0.003, +0.006] | +0.993 [+0.987, +0.998] | +0.999 [+0.994, +1.004] | task-independent | task-independent |
| L32 | 0.387 | +0.976 [+0.964, +0.987] | +0.970 [+0.958, +0.983] | +0.974 [+0.962, +0.986] | +0.006 [-0.001, +0.012] | +0.002 [-0.004, +0.007] | +0.994 [+0.988, +1.001] | +0.998 [+0.993, +1.004] | task-independent | task-independent |
| L40 | 0.365 | +0.918 [+0.902, +0.934] | +0.912 [+0.895, +0.929] | +0.911 [+0.894, +0.929] | +0.006 [-0.000, +0.014] | +0.007 [+0.001, +0.013] | +0.993 [+0.985, +1.001] | +0.993 [+0.986, +0.999] | task-independent | task-independent |
| L48 | 0.323 | +0.339 [+0.310, +0.368] | +0.316 [+0.288, +0.344] | +0.324 [+0.295, +0.354] | +0.023 [+0.018, +0.029] | +0.014 [+0.009, +0.020] | +0.932 [+0.915, +0.948] | +0.958 [+0.941, +0.973] | task-independent | undecided |

## Verdict changes (L24+)

- test L48: original "task-independent" -> verdict_Rc_b0.02 "undecided"
- test L48: original "task-independent" -> verdict_N_b0.02 "undecided"
- tune L48: original "task-independent" -> verdict_Rc_b0.02 "undecided"
- tune L48: original "task-independent" -> verdict_N_b0.02 "undecided"
- all L48: original "task-independent" -> verdict_Rc_b0.02 "undecided"
- all L48: original "task-independent" -> verdict_N_b0.02 "undecided"

Every change listed above comes from the bound b = 0.02, not from the C correction: under b = 0.02 the uncorrected curves give the same verdicts, because the differences are identical.

## Conclusion

1. Subtracting random C per pair changes the level of every recovery (by -R(C): on test up by 0.07-0.15 at L4-L32, down by 0.122 at L48) but not the authors - year / authors - field differences: C cancels exactly (checked per bootstrap draw).
2. With the written addendum-2 bound (0.1) every verdict is unchanged: L24-L48 stay task-independent on test, tune and all, including L48, which was flagged.
3. At L48 on test, R'(authors) = 0.302, R'(year) = 0.283, R'(field) = 0.294; normalised to C as the baseline, year keeps 93.6% [91.1%, 96.0%] and field 97.4% [95.1%, 99.6%] of the authors effect: a small but non-zero task dependence (interval of authors - year excludes 0).
4. With a stricter bound of 0.02, L48 becomes 'undecided' in every split, because the upper end of authors - year is above 0.02 (test 0.026; normalised 0.030). L24-L40 stay task-independent even with 0.02.

