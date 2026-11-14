# Title-position probe with a fully clean donor set (plan 2026-11-14b item 3)

**Post hoc, descriptive.**

Method: addendum-9 probe (title-last residual -> ridge -> own L63 state at the name-token positions -> final norm + lm_head rows of 9,137 name token ids -> log10(1/rank)); archived author-team folds; training-fold standardisation; alpha on fold 0. **clean**: when testing fold f, every paper that donates any of the 5 false titles of any paper in fold f is removed from the training set; ridge refit; spec = probe(true) - mean of the 5 false titles; every target / control paper kept. **randsize** (added after the tiny run): same number of training papers per fold as clean, drawn at random from the original training set (donors may remain), so it separates the effect of training-set size from leakage. V0 / Vpd / V5x0 come from the original fit, rerun in the same job (parity below). target - control: within citation bin (bins >= 30 per group, weights n_t n_c/(n_t+n_c)); team-cluster bootstrap 95% CI, 2,000 draws; * = CI excludes 0. all_tokens = a new run: all tokens of the five roles in one target / gold set per paper (punctuation and particles excluded); its V0 / Vpd are computed here and have no published counterpart.

## Training-set sizes per fold

| run | fold | test papers | train original | train clean | removed |
|---|---|---|---|---|---|
| surname_first | 0 | 1822 | 7286 | 2489 | 4797 |
| surname_first | 1 | 1822 | 7286 | 2558 | 4728 |
| surname_first | 2 | 1822 | 7286 | 2547 | 4739 |
| surname_first | 3 | 1821 | 7287 | 2526 | 4761 |
| surname_first | 4 | 1821 | 7287 | 2543 | 4744 |
| given_first | 0 | 864 | 3338 | 1162 | 2176 |
| given_first | 1 | 854 | 3348 | 1201 | 2147 |
| given_first | 2 | 828 | 3374 | 1212 | 2162 |
| given_first | 3 | 811 | 3391 | 1193 | 2198 |
| given_first | 4 | 845 | 3357 | 1183 | 2174 |
| initial | 0 | 1693 | 6771 | 2317 | 4454 |
| initial | 1 | 1683 | 6781 | 2403 | 4378 |
| initial | 2 | 1700 | 6764 | 2352 | 4412 |
| initial | 3 | 1682 | 6782 | 2342 | 4440 |
| initial | 4 | 1706 | 6758 | 2359 | 4399 |
| given_cont | 0 | 601 | 2377 | 840 | 1537 |
| given_cont | 1 | 603 | 2375 | 845 | 1530 |
| given_cont | 2 | 595 | 2383 | 856 | 1527 |
| given_cont | 3 | 582 | 2396 | 858 | 1538 |
| given_cont | 4 | 597 | 2381 | 838 | 1543 |
| surname_cont | 0 | 1634 | 6475 | 2205 | 4270 |
| surname_cont | 1 | 1609 | 6500 | 2296 | 4204 |
| surname_cont | 2 | 1618 | 6491 | 2260 | 4231 |
| surname_cont | 3 | 1625 | 6484 | 2249 | 4235 |
| surname_cont | 4 | 1623 | 6486 | 2265 | 4221 |
| all_tokens | 0 | 1822 | 7286 | 2489 | 4797 |
| all_tokens | 1 | 1822 | 7286 | 2558 | 4728 |
| all_tokens | 2 | 1822 | 7286 | 2547 | 4739 |
| all_tokens | 3 | 1821 | 7287 | 2526 | 4761 |
| all_tokens | 4 | 1821 | 7287 | 2543 | 4744 |

## Usable (clean) false titles per test paper

| run | papers | 0 / 1 / 2 / 3 / 4 / 5 usable |
|---|---|---|
| surname_first | 9108 | 0 / 0 / 0 / 0 / 0 / 9108 |
| given_first | 4202 | 0 / 0 / 0 / 0 / 0 / 4202 |
| initial | 8464 | 0 / 0 / 0 / 0 / 0 / 8464 |
| given_cont | 2978 | 0 / 0 / 0 / 0 / 0 / 2978 |
| surname_cont | 8109 | 0 / 0 / 0 / 0 / 0 / 8109 |
| all_tokens | 9108 | 0 / 0 / 0 / 0 / 0 / 9108 |

## L40: spec and target - control

| role | version | n (T / C) | spec | target - control (bins) |
|---|---|---|---|---|
| surname first token | clean | 6841 (4621 / 2220) | +0.037 [+0.033, +0.040]* | +0.014 [+0.006, +0.021]* (10) |
| surname first token | randsize_5mean | 6841 (4621 / 2220) | +0.036 [+0.033, +0.040]* | +0.016 [+0.008, +0.023]* (10) |
| surname first token | Vpd | 4654 (3130 / 1524) | +0.076 [+0.068, +0.083]* | +0.030 [+0.013, +0.048]* (10) |
| surname first token | V0 | 1395 (896 / 499) | +0.071 [+0.058, +0.085]* | +0.012 [-0.026, +0.048] (8) |
| surname first token | V5x0 | 1395 (896 / 499) | +0.072 [+0.061, +0.084]* | +0.024 [-0.006, +0.052] (8) |
| surname first token | clean_f0only | 6841 (4621 / 2220) | +0.037 [+0.033, +0.041]* | +0.012 [+0.003, +0.020]* (10) |
| given first token | clean | 3163 (2149 / 1014) | +0.073 [+0.066, +0.079]* | +0.028 [+0.013, +0.043]* (9) |
| given first token | randsize_5mean | 3163 (2149 / 1014) | +0.072 [+0.065, +0.078]* | +0.024 [+0.010, +0.039]* (9) |
| given first token | Vpd | 3046 (2069 / 977) | +0.138 [+0.126, +0.149]* | +0.048 [+0.021, +0.075]* (9) |
| given first token | V0 | 1706 (1142 / 564) | +0.124 [+0.108, +0.142]* | +0.049 [+0.005, +0.095]* (8) |
| given first token | V5x0 | 1706 (1142 / 564) | +0.129 [+0.115, +0.143]* | +0.047 [+0.012, +0.081]* (8) |
| given first token | clean_f0only | 3163 (2149 / 1014) | +0.071 [+0.064, +0.079]* | +0.027 [+0.009, +0.045]* (9) |
| initial | clean | 6385 (4413 / 1972) | +0.011 [+0.009, +0.013]* | +0.007 [+0.002, +0.013]* (10) |
| initial | randsize_5mean | 6385 (4413 / 1972) | +0.012 [+0.009, +0.014]* | +0.007 [+0.001, +0.013]* (10) |
| initial | Vpd | 4812 (3298 / 1514) | +0.043 [+0.037, +0.049]* | +0.014 [-0.002, +0.030] (10) |
| initial | V0 | 1590 (1022 / 568) | +0.044 [+0.030, +0.057]* | +0.031 [-0.001, +0.062] (8) |
| initial | V5x0 | 1590 (1022 / 568) | +0.035 [+0.025, +0.045]* | +0.021 [-0.002, +0.043] (8) |
| initial | clean_f0only | 6385 (4413 / 1972) | +0.009 [+0.005, +0.012]* | +0.010 [+0.003, +0.018]* (10) |
| given rest | clean | 2195 (1433 / 762) | +0.040 [+0.032, +0.049]* | +0.022 [+0.003, +0.042]* (9) |
| given rest | randsize_5mean | 2195 (1433 / 762) | +0.044 [+0.036, +0.052]* | +0.018 [-0.002, +0.037] (9) |
| given rest | Vpd | 2156 (1411 / 745) | +0.043 [+0.036, +0.050]* | +0.017 [+0.000, +0.035]* (9) |
| given rest | V0 | 1409 (922 / 487) | +0.045 [+0.035, +0.056]* | +0.036 [+0.011, +0.061]* (8) |
| given rest | V5x0 | 1409 (922 / 487) | +0.043 [+0.036, +0.052]* | +0.034 [+0.014, +0.055]* (8) |
| given rest | clean_f0only | 2195 (1433 / 762) | +0.044 [+0.033, +0.054]* | +0.025 [-0.001, +0.050] (9) |
| surname rest | clean | 6134 (4312 / 1822) | +0.025 [+0.021, +0.028]* | +0.013 [+0.004, +0.022]* (10) |
| surname rest | randsize_5mean | 6134 (4312 / 1822) | +0.024 [+0.021, +0.027]* | +0.013 [+0.005, +0.021]* (10) |
| surname rest | Vpd | 4913 (3424 / 1489) | +0.027 [+0.023, +0.030]* | +0.016 [+0.007, +0.024]* (10) |
| surname rest | V0 | 1754 (1165 / 589) | +0.030 [+0.023, +0.036]* | +0.025 [+0.007, +0.043]* (8) |
| surname rest | V5x0 | 1754 (1165 / 589) | +0.030 [+0.025, +0.035]* | +0.019 [+0.005, +0.034]* (8) |
| surname rest | clean_f0only | 6134 (4312 / 1822) | +0.023 [+0.019, +0.026]* | +0.014 [+0.004, +0.024]* (10) |
| all tokens pooled (new run) | clean | 6841 (4621 / 2220) | +0.022 [+0.020, +0.024]* | +0.009 [+0.004, +0.013]* (10) |
| all tokens pooled (new run) | randsize_5mean | 6841 (4621 / 2220) | +0.021 [+0.019, +0.023]* | +0.008 [+0.004, +0.012]* (10) |
| all tokens pooled (new run) | Vpd | 4654 (3130 / 1524) | +0.046 [+0.042, +0.050]* | +0.017 [+0.007, +0.027]* (10) |
| all tokens pooled (new run) | V0 | 1395 (896 / 499) | +0.043 [+0.036, +0.050]* | +0.029 [+0.008, +0.049]* (8) |
| all tokens pooled (new run) | V5x0 | 1395 (896 / 499) | +0.044 [+0.038, +0.050]* | +0.027 [+0.010, +0.043]* (8) |
| all tokens pooled (new run) | clean_f0only | 6841 (4621 / 2220) | +0.022 [+0.020, +0.024]* | +0.008 [+0.003, +0.013]* (10) |

## L48: spec and target - control

| role | version | n (T / C) | spec | target - control (bins) |
|---|---|---|---|---|
| surname first token | clean | 6841 (4621 / 2220) | +0.044 [+0.040, +0.048]* | +0.019 [+0.011, +0.027]* (10) |
| surname first token | randsize_5mean | 6841 (4621 / 2220) | +0.044 [+0.040, +0.048]* | +0.019 [+0.011, +0.028]* (10) |
| surname first token | Vpd | 4654 (3130 / 1524) | +0.085 [+0.077, +0.092]* | +0.042 [+0.025, +0.060]* (10) |
| surname first token | V0 | 1395 (896 / 499) | +0.091 [+0.077, +0.106]* | +0.016 [-0.025, +0.056] (8) |
| surname first token | V5x0 | 1395 (896 / 499) | +0.088 [+0.077, +0.099]* | +0.031 [+0.001, +0.059]* (8) |
| surname first token | clean_f0only | 6841 (4621 / 2220) | +0.044 [+0.040, +0.048]* | +0.019 [+0.009, +0.029]* (10) |
| given first token | clean | 3163 (2149 / 1014) | +0.086 [+0.079, +0.094]* | +0.034 [+0.018, +0.050]* (9) |
| given first token | randsize_5mean | 3163 (2149 / 1014) | +0.084 [+0.077, +0.092]* | +0.030 [+0.015, +0.047]* (9) |
| given first token | Vpd | 3046 (2069 / 977) | +0.149 [+0.136, +0.161]* | +0.051 [+0.023, +0.081]* (9) |
| given first token | V0 | 1706 (1142 / 564) | +0.140 [+0.122, +0.157]* | +0.073 [+0.027, +0.122]* (8) |
| given first token | V5x0 | 1706 (1142 / 564) | +0.140 [+0.125, +0.153]* | +0.065 [+0.029, +0.101]* (8) |
| given first token | clean_f0only | 3163 (2149 / 1014) | +0.085 [+0.076, +0.094]* | +0.039 [+0.019, +0.059]* (9) |
| initial | clean | 6385 (4413 / 1972) | +0.013 [+0.010, +0.016]* | +0.012 [+0.006, +0.019]* (10) |
| initial | randsize_5mean | 6385 (4413 / 1972) | +0.013 [+0.011, +0.016]* | +0.008 [+0.001, +0.014]* (10) |
| initial | Vpd | 4812 (3298 / 1514) | +0.043 [+0.036, +0.049]* | +0.031 [+0.014, +0.048]* (10) |
| initial | V0 | 1590 (1022 / 568) | +0.030 [+0.016, +0.045]* | +0.056 [+0.025, +0.089]* (8) |
| initial | V5x0 | 1590 (1022 / 568) | +0.031 [+0.021, +0.042]* | +0.043 [+0.020, +0.067]* (8) |
| initial | clean_f0only | 6385 (4413 / 1972) | +0.011 [+0.008, +0.015]* | +0.016 [+0.007, +0.024]* (10) |
| given rest | clean | 2195 (1433 / 762) | +0.049 [+0.040, +0.058]* | +0.010 [-0.009, +0.030] (9) |
| given rest | randsize_5mean | 2195 (1433 / 762) | +0.050 [+0.040, +0.059]* | +0.018 [-0.002, +0.037] (9) |
| given rest | Vpd | 2156 (1411 / 745) | +0.048 [+0.041, +0.056]* | +0.015 [-0.002, +0.033] (9) |
| given rest | V0 | 1409 (922 / 487) | +0.050 [+0.039, +0.061]* | +0.023 [-0.002, +0.047] (8) |
| given rest | V5x0 | 1409 (922 / 487) | +0.047 [+0.038, +0.056]* | +0.026 [+0.006, +0.046]* (8) |
| given rest | clean_f0only | 2195 (1433 / 762) | +0.052 [+0.040, +0.063]* | +0.017 [-0.008, +0.043] (9) |
| surname rest | clean | 6134 (4312 / 1822) | +0.029 [+0.026, +0.033]* | +0.016 [+0.007, +0.026]* (10) |
| surname rest | randsize_5mean | 6134 (4312 / 1822) | +0.031 [+0.027, +0.034]* | +0.012 [+0.003, +0.021]* (10) |
| surname rest | Vpd | 4913 (3424 / 1489) | +0.033 [+0.030, +0.037]* | +0.016 [+0.007, +0.026]* (10) |
| surname rest | V0 | 1754 (1165 / 589) | +0.038 [+0.031, +0.045]* | +0.022 [+0.004, +0.041]* (8) |
| surname rest | V5x0 | 1754 (1165 / 589) | +0.038 [+0.032, +0.043]* | +0.023 [+0.008, +0.038]* (8) |
| surname rest | clean_f0only | 6134 (4312 / 1822) | +0.028 [+0.024, +0.032]* | +0.019 [+0.008, +0.029]* (10) |
| all tokens pooled (new run) | clean | 6841 (4621 / 2220) | +0.047 [+0.043, +0.051]* | +0.023 [+0.015, +0.031]* (10) |
| all tokens pooled (new run) | randsize_5mean | 6841 (4621 / 2220) | +0.046 [+0.042, +0.050]* | +0.023 [+0.016, +0.031]* (10) |
| all tokens pooled (new run) | Vpd | 4654 (3130 / 1524) | +0.048 [+0.044, +0.052]* | +0.024 [+0.014, +0.034]* (10) |
| all tokens pooled (new run) | V0 | 1395 (896 / 499) | +0.045 [+0.037, +0.054]* | +0.028 [+0.006, +0.051]* (8) |
| all tokens pooled (new run) | V5x0 | 1395 (896 / 499) | +0.046 [+0.040, +0.052]* | +0.031 [+0.014, +0.048]* (8) |
| all tokens pooled (new run) | clean_f0only | 6841 (4621 / 2220) | +0.048 [+0.043, +0.052]* | +0.022 [+0.013, +0.031]* (10) |

## Parity (original fit rerun vs stored addendum-10 per-paper files and published perdonor_by_run_layer.csv; WARN only)

```
          run  layer  max_abs_spec0_diff  mean_abs_spec0_diff  dropped_agree  V0_spec_diff  V0_tc_diff  V0_tclo_diff  V0_tchi_diff  Vpd_spec_diff  Vpd_tc_diff  Vpd_tclo_diff  Vpd_tchi_diff
surname_first     40             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
surname_first     48             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
  given_first     40             0.06695              0.00002            1.0       0.00004     -0.0001      -0.00019      -0.00009        0.00002     -0.00005       -0.00005       -0.00011
  given_first     48             0.00039              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
      initial     40             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
      initial     48             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
   given_cont     40             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
   given_cont     48             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
 surname_cont     40             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
 surname_cont     48             0.00000              0.00000            1.0       0.00000      0.0000       0.00000       0.00000        0.00000      0.00000        0.00000        0.00000
   all_tokens     40                 NaN                  NaN            NaN           NaN         NaN           NaN           NaN            NaN          NaN            NaN            NaN
   all_tokens     48                 NaN                  NaN            NaN           NaN         NaN           NaN           NaN            NaN          NaN            NaN            NaN
```

## Key answer

surname first token, L40, clean: target - control +0.014 [+0.006, +0.021]* -> CI excludes 0.
