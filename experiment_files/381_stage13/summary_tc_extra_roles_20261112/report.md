# Target - control at L40: extra roles and all name tokens pooled (post hoc, descriptive (not in the pre-registered main comparison))

Written 2026-11-12 by `~/jlens_work/13_stage13/stage13_tc_extra_roles_20261112.py` (CPU only, stored per-paper scores of summary_b1_e4b5/probe, no new fit).
Estimators are the exact functions of stage13_b1_e4b5_perdonor.py (team-cluster bootstrap, 2,000 draws, archived author teams; citation bins with >= 30 papers in both groups, weights n_t n_c / (n_t + n_c)).

## Parity (all existing L40 rows of perdonor_by_run_layer.csv recomputed)

21 / 21 rows identical (max |diff| 9.7e-17). given_first V0: +0.049 [+0.005, +0.095]*.

## L40, target - control within citation bin [team CI] (n = target + control papers after exclusion)

| role | V0 (pre-registered rule) | Vpd (per-donor) | V5x0 (contains leakage) |
|---|---|---|---|
| initial | +0.031 [-0.001, +0.062] (n 1,590) | +0.014 [-0.002, +0.030] (n 4,812) | +0.021 [-0.002, +0.043] (n 1,590) |
| given_first | +0.049 [+0.005, +0.095]* (n 1,706) | +0.048 [+0.021, +0.076]* (n 3,046) | +0.047 [+0.012, +0.081]* (n 1,706) |
| given_cont | +0.036 [+0.011, +0.061]* (n 1,409) | +0.017 [+0.000, +0.035]* (n 2,156) | +0.034 [+0.014, +0.055]* (n 1,409) |
| surname_first | +0.012 [-0.026, +0.048] (n 1,395) | +0.030 [+0.013, +0.048]* (n 4,654) | +0.024 [-0.006, +0.052] (n 1,395) |
| surname_cont | +0.025 [+0.007, +0.043]* (n 1,754) | +0.016 [+0.007, +0.024]* (n 4,913) | +0.019 [+0.005, +0.034]* (n 1,754) |
| **all name tokens pooled (post hoc)** | +0.027 [+0.008, +0.045]* (n 3,352) | +0.024 [+0.015, +0.034]* (n 6,188) | +0.028 [+0.014, +0.042]* (n 3,352) |

Role rows: copied from summary_b1_e4b5/perdonor_by_run_layer.csv (already computed). Pooled row: new, this script.

## All name tokens pooled, L40: title-specific signal and permutation controls (all target + control papers)

| version | spec [team CI] | gold = random other paper | gold = random paper, same field | n |
|---|---|---|---|---|
| V0 | +0.067 [+0.060, +0.074]* | +0.009 [+0.002, +0.016]* | +0.007 [+0.001, +0.014]* | 3,352 |
| Vpd | +0.061 [+0.057, +0.066]* | +0.008 [+0.005, +0.012]* | +0.008 [+0.004, +0.011]* | 6,188 |
| V5x0 | +0.063 [+0.058, +0.069]* | +0.006 [+0.000, +0.011]* | +0.004 [-0.000, +0.010] | 3,352 |

## All name tokens pooled, target - control by layer

| version | L16 | L24 | L32 | L40 | L44 | L48 | L52 | L56 | L60 |
|---|---|---|---|---|---|---|---|---|---|
| V0 | +0.020 [+0.004, +0.037]* | +0.023 [+0.005, +0.041]* | +0.033 [+0.015, +0.049]* | +0.027 [+0.008, +0.045]* | +0.023 [+0.006, +0.040]* | +0.038 [+0.019, +0.056]* | +0.040 [+0.021, +0.059]* | +0.043 [+0.023, +0.062]* | +0.041 [+0.021, +0.060]* |
| Vpd | +0.017 [+0.008, +0.026]* | +0.022 [+0.013, +0.031]* | +0.027 [+0.018, +0.036]* | +0.024 [+0.015, +0.034]* | +0.022 [+0.013, +0.032]* | +0.030 [+0.020, +0.041]* | +0.034 [+0.023, +0.045]* | +0.037 [+0.025, +0.048]* | +0.032 [+0.021, +0.044]* |
| V5x0 | +0.019 [+0.006, +0.032]* | +0.020 [+0.006, +0.034]* | +0.026 [+0.013, +0.041]* | +0.028 [+0.014, +0.042]* | +0.023 [+0.010, +0.037]* | +0.035 [+0.020, +0.049]* | +0.042 [+0.027, +0.056]* | +0.041 [+0.027, +0.056]* | +0.038 [+0.023, +0.053]* |

## Definition and caveats

- Pooled paper score = mean over all of the paper's tokens of the five addendum-9 roles (punctuation / particles excluded, as in addendum 9), each token scored by its own ROLE probe (five separate ridge maps), not by one probe fitted on all tokens. A role's tokens are left out of the pooled score for false title k when that role probe flags title reuse for k (V0 / V5x0: false_0 flag; Vpd: flag of each k).
- Papers are therefore kept if at least one role is usable; the paper set is larger than any single role's, and roles are mixed in different proportions across papers (73% of names start with an initial).
- The five role rows share papers and team clusters, so the pooled row is not independent of them.
- V5x0 contains title-reuse leakage (false_1..4 donors not excluded); sensitivity only.
- Teacher-forced preference, not generation.
