# Stage 13 M2: team-cluster bootstrap vs per-paper bootstrap (TINY TEST)

Folds/table: team (summary_cpu_group); original: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_group/M2_probes.csv

Team interval: author teams (= probe fold groups) resampled with replacement, NB=50, seed 20261030; original: per-paper bootstrap, 200 draws. Held-out predictions recomputed with the same folds/alpha grid/features and saved under preds/. Null level: R^2 0, AUROC 0.5, field accuracy = majority-class share.

## Point-estimate check: 23 rows, max |new - original| = 6.25e-17; rows with |diff| > 1e-6: 0 (all match)

## Interval width ratio (team / paper)

Over all 18 rows with an original interval: mean 1.00, median 0.99, min 0.74, max 1.43.

                                                   count  mean   min   max
condition position target                                                 
false_0   colon    field                               1  1.43  1.43  1.43
                   log citations                       1  1.09  1.09  1.09
                   log citations | year removed        1  1.05  1.05  1.05
                   year                                1  1.11  1.11  1.11
          title    field                               1  1.16  1.16  1.16
                   log citations                       1  1.19  1.19  1.19
                   log citations | year removed        1  1.12  1.12  1.12
                   year                                1  1.29  1.29  1.29
true      colon    field                               1  0.88  0.88  0.88
                   log citations                       1  0.82  0.82  0.82
                   log citations | year removed        1  0.84  0.84  0.84
                   recognised (target vs control)      1  0.94  0.94  0.94
                   year                                1  0.74  0.74  0.74
          title    field                               1  1.04  1.04  1.04
                   log citations                       1  0.83  0.83  0.83
                   log citations | year removed        1  0.77  0.77  0.77
                   recognised (target vs control)      1  0.88  0.88  0.88
                   year                                1  0.86  0.86  0.86

## Flips: "interval excludes 0": 0 rows; "interval above chance (null level)": 0 rows

None.

## All rows

| condition | position | layer | target | metric | value | null | paper CI (200) | team CI (2000) | width ratio | excl 0 paper/team | > null paper/team | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | year-only baseline | -1 | log citations | r2 | 0.047 | 0.000 | [-, -] | [0.041, 0.054] | - | -/Y | -/Y |  |
| true | year-only baseline | -1 | log citations &#124; year removed | r2 | -0.001 | 0.000 | [-, -] | [-0.002, -0.000] | - | -/Y | -/N |  |
| true | year-only baseline | -1 | recognised (target vs control) | auc_bin | 0.555 | 0.500 | [-, -] | [0.533, 0.572] | - | -/Y | -/Y |  |
| true | title | 16 | field | acc | 0.698 | 0.135 | [0.689, 0.706] | [0.689, 0.707] | 1.044 | Y/Y | Y/Y |  |
| true | title | 16 | year | r2 | 0.383 | 0.000 | [0.364, 0.402] | [0.369, 0.401] | 0.858 | Y/Y | Y/Y |  |
| true | title | 16 | log citations | r2 | 0.286 | 0.000 | [0.268, 0.304] | [0.270, 0.300] | 0.834 | Y/Y | Y/Y |  |
| true | title | 16 | log citations &#124; year removed | r2 | 0.275 | 0.000 | [0.255, 0.294] | [0.259, 0.289] | 0.773 | Y/Y | Y/Y |  |
| true | title | 16 | recognised (target vs control) | auc_bin | 0.620 | 0.500 | [0.602, 0.638] | [0.606, 0.638] | 0.885 | Y/Y | Y/Y |  |
| true | colon | 16 | field | acc | 0.740 | 0.135 | [0.731, 0.748] | [0.733, 0.747] | 0.876 | Y/Y | Y/Y |  |
| true | colon | 16 | year | r2 | 0.974 | 0.000 | [0.967, 0.979] | [0.971, 0.979] | 0.736 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations | r2 | 0.431 | 0.000 | [0.415, 0.449] | [0.416, 0.445] | 0.825 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations &#124; year removed | r2 | 0.400 | 0.000 | [0.382, 0.415] | [0.384, 0.411] | 0.845 | Y/Y | Y/Y |  |
| true | colon | 16 | recognised (target vs control) | auc_bin | 0.671 | 0.500 | [0.651, 0.690] | [0.650, 0.687] | 0.938 | Y/Y | Y/Y |  |
| false_0 | year-only baseline | -1 | log citations | r2 | 0.048 | 0.000 | [-, -] | [0.038, 0.061] | - | -/Y | -/Y |  |
| false_0 | year-only baseline | -1 | log citations &#124; year removed | r2 | -0.001 | 0.000 | [-, -] | [-0.002, -0.000] | - | -/Y | -/N |  |
| false_0 | title | 16 | field | acc | 0.689 | 0.135 | [0.679, 0.699] | [0.680, 0.703] | 1.156 | Y/Y | Y/Y |  |
| false_0 | title | 16 | year | r2 | 0.353 | 0.000 | [0.332, 0.371] | [0.329, 0.379] | 1.294 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations | r2 | 0.246 | 0.000 | [0.227, 0.263] | [0.226, 0.267] | 1.187 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations &#124; year removed | r2 | 0.232 | 0.000 | [0.216, 0.251] | [0.217, 0.256] | 1.123 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | field | acc | 0.743 | 0.135 | [0.735, 0.751] | [0.732, 0.755] | 1.433 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | year | r2 | 0.938 | 0.000 | [0.931, 0.943] | [0.930, 0.943] | 1.111 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations | r2 | 0.407 | 0.000 | [0.392, 0.422] | [0.389, 0.423] | 1.089 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations &#124; year removed | r2 | 0.371 | 0.000 | [0.355, 0.386] | [0.352, 0.385] | 1.054 | Y/Y | Y/Y |  |

Rows marked LEAK in the original note (year at the colon position) are positive controls only. Year-only baseline rows had no original interval.
