# M2 five false titles: hard check (false_0 recomputed vs published) (TINY: mismatches expected)

## M2_probes: published false_0 rows 78, recomputed 10, unmatched keys 68

| column | max abs diff | rows equal bit-for-bit | rows > 1e-9 |
|---|---|---|---|
| value | 2.365e-01 | 0/10 | 10 |
| lo | 2.752e-01 | 2/10 | 8 |
| hi | 2.053e-01 | 2/10 | 8 |
| shuffled | 3.836e-02 | 2/10 | 8 |
| alpha | 9.900e+01 | 2/10 | 8 |
| n | 8.852e+03 | 0/10 | 10 |
| metric (text) | - | 10/10 | 0 |
| year_in_context (text) | - | 10/10 | 0 |
| note (text) | - | 10/10 | 0 |

## M2_teamci: published false_0 rows 78, recomputed 10, unmatched keys 68

| column | max abs diff | rows equal bit-for-bit | rows > 1e-9 |
|---|---|---|---|
| value_new | 2.365e-01 | 0/10 | 10 |
| lo_team | 2.616e-01 | 0/10 | 10 |
| hi_team | 2.121e-01 | 0/10 | 10 |
| null | 2.902e-02 | 8/10 | 2 |
| n | 8.852e+03 | 0/10 | 10 |
| n_teams | 5.116e+03 | 0/10 | 10 |
| alpha_new | 9.900e+01 | 1/10 | 9 |
| value_orig | 2.365e-01 | 0/10 | 10 |
| lo_paper | 2.752e-01 | 2/10 | 8 |
| hi_paper | 2.053e-01 | 2/10 | 8 |
| shuffled | 3.836e-02 | 2/10 | 8 |
| alpha | 9.900e+01 | 2/10 | 8 |
| n_orig | 8.852e+03 | 0/10 | 10 |
| width_paper | 1.332e-01 | 2/10 | 8 |
| width_team | 1.122e-01 | 0/10 | 10 |
| width_ratio | 5.715e-01 | 2/10 | 8 |
| metric (text) | - | 10/10 | 0 |
| note (text) | - | 10/10 | 0 |
| excl0_paper (text) | - | 10/10 | 0 |
| excl0_team (text) | - | 9/10 | 1 |
| above_null_paper (text) | - | 10/10 | 0 |
| above_null_team (text) | - | 9/10 | 1 |
| flip_excl0 (text) | - | 10/10 | 0 |
| flip_above_null (text) | - | 10/10 | 0 |

**Result: FAIL** (tolerance 1e-09 on every numeric column, exact on text/boolean columns).
