# Stage 13 M2: team-cluster bootstrap vs per-paper bootstrap (TINY TEST)

Folds/table: team (summary_cpu_group); original: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_group/M2_probes.csv

Team interval: author teams (= probe fold groups) resampled with replacement, NB=50, seed 20261030; original: per-paper bootstrap, 200 draws. Held-out predictions recomputed with the same folds/alpha grid/features and saved under preds/. Null level: R^2 0, AUROC 0.5, field accuracy = majority-class share.

## Point-estimate check: 23 rows, max |new - original| = 6.08e-03; rows with |diff| > 1e-6: 23  **MISMATCH: see table**

condition           position  layer                         target  value_orig  value_new  value_diff  alpha  alpha_new
     true year-only baseline     -1                  log citations    0.047214   0.047557    0.000343    NaN       0.10
     true year-only baseline     -1   log citations | year removed   -0.000990  -0.000247    0.000744    NaN    1000.00
     true year-only baseline     -1 recognised (target vs control)    0.555248   0.561327    0.006079    NaN       0.10
     true              title     16                          field    0.698068   0.696421   -0.001647   1.00       1.00
     true              title     16                           year    0.383441   0.378590   -0.004851   1.00       1.00
     true              title     16                  log citations    0.286243   0.286960    0.000717   1.00       1.00
     true              title     16   log citations | year removed    0.275190   0.277006    0.001817   1.00       1.00
     true              title     16 recognised (target vs control)    0.620218   0.616688   -0.003530  10.00      10.00
     true              colon     16                          field    0.740119   0.741326    0.001208   1.00       1.00
     true              colon     16                           year    0.974253   0.974875    0.000622   0.01       0.01
     true              colon     16                  log citations    0.431498   0.433246    0.001749   0.10       1.00
     true              colon     16   log citations | year removed    0.400071   0.401266    0.001195   0.10       1.00
     true              colon     16 recognised (target vs control)    0.671089   0.675078    0.003989   1.00       1.00
  false_0 year-only baseline     -1                  log citations    0.048036   0.047337   -0.000699    NaN       0.10
  false_0 year-only baseline     -1   log citations | year removed   -0.000923  -0.000260    0.000663    NaN    1000.00
  false_0              title     16                          field    0.689065   0.688406   -0.000659   1.00       1.00
  false_0              title     16                           year    0.352677   0.351010   -0.001667   1.00       1.00
  false_0              title     16                  log citations    0.245764   0.244061   -0.001703   1.00       1.00
  false_0              title     16   log citations | year removed    0.232280   0.230343   -0.001937   1.00       1.00
  false_0              colon     16                          field    0.742644   0.742095   -0.000549   1.00       1.00
  false_0              colon     16                           year    0.937649   0.938084    0.000435   0.10       0.10
  false_0              colon     16                  log citations    0.407111   0.404368   -0.002742   1.00       1.00
  false_0              colon     16   log citations | year removed    0.371107   0.367039   -0.004069   1.00       1.00

## Interval width ratio (team / paper)

Over all 18 rows with an original interval: mean 0.94, median 0.95, min 0.65, max 1.38.

                                                   count  mean   min   max
condition position target                                                 
false_0   colon    field                               1  1.33  1.33  1.33
                   log citations                       1  1.02  1.02  1.02
                   log citations | year removed        1  0.98  0.98  0.98
                   year                                1  1.12  1.12  1.12
          title    field                               1  1.01  1.01  1.01
                   log citations                       1  0.98  0.98  0.98
                   log citations | year removed        1  0.99  0.99  0.99
                   year                                1  1.38  1.38  1.38
true      colon    field                               1  0.90  0.90  0.90
                   log citations                       1  0.71  0.71  0.71
                   log citations | year removed        1  0.75  0.75  0.75
                   recognised (target vs control)      1  0.92  0.92  0.92
                   year                                1  0.65  0.65  0.65
          title    field                               1  0.89  0.89  0.89
                   log citations                       1  0.66  0.66  0.66
                   log citations | year removed        1  0.66  0.66  0.66
                   recognised (target vs control)      1  0.88  0.88  0.88
                   year                                1  1.01  1.01  1.01

## Flips: "interval excludes 0": 0 rows; "interval above chance (null level)": 0 rows

None.

## All rows

| condition | position | layer | target | metric | value | null | paper CI (200) | team CI (2000) | width ratio | excl 0 paper/team | > null paper/team | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | year-only baseline | -1 | log citations | r2 | 0.048 | 0.000 | [-, -] | [0.041, 0.055] | - | -/Y | -/Y |  |
| true | year-only baseline | -1 | log citations | year removed | r2 | -0.000 | 0.000 | [-, -] | [-0.001, -0.000] | - | -/Y | -/N |  |
| true | year-only baseline | -1 | recognised (target vs control) | auc_bin | 0.561 | 0.500 | [-, -] | [0.540, 0.576] | - | -/Y | -/Y |  |
| true | title | 16 | field | acc | 0.696 | 0.135 | [0.689, 0.706] | [0.689, 0.704] | 0.895 | Y/Y | Y/Y |  |
| true | title | 16 | year | r2 | 0.379 | 0.000 | [0.364, 0.402] | [0.360, 0.398] | 1.008 | Y/Y | Y/Y |  |
| true | title | 16 | log citations | r2 | 0.287 | 0.000 | [0.268, 0.304] | [0.275, 0.299] | 0.663 | Y/Y | Y/Y |  |
| true | title | 16 | log citations | year removed | r2 | 0.277 | 0.000 | [0.255, 0.294] | [0.264, 0.289] | 0.657 | Y/Y | Y/Y |  |
| true | title | 16 | recognised (target vs control) | auc_bin | 0.617 | 0.500 | [0.602, 0.638] | [0.604, 0.635] | 0.877 | Y/Y | Y/Y |  |
| true | colon | 16 | field | acc | 0.741 | 0.135 | [0.731, 0.748] | [0.734, 0.749] | 0.895 | Y/Y | Y/Y |  |
| true | colon | 16 | year | r2 | 0.975 | 0.000 | [0.967, 0.979] | [0.972, 0.979] | 0.654 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations | r2 | 0.433 | 0.000 | [0.415, 0.449] | [0.419, 0.443] | 0.714 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations | year removed | r2 | 0.401 | 0.000 | [0.382, 0.415] | [0.387, 0.411] | 0.748 | Y/Y | Y/Y |  |
| true | colon | 16 | recognised (target vs control) | auc_bin | 0.675 | 0.500 | [0.651, 0.690] | [0.653, 0.689] | 0.919 | Y/Y | Y/Y |  |
| false_0 | year-only baseline | -1 | log citations | r2 | 0.047 | 0.000 | [-, -] | [0.037, 0.058] | - | -/Y | -/Y |  |
| false_0 | year-only baseline | -1 | log citations | year removed | r2 | -0.000 | 0.000 | [-, -] | [-0.001, -0.000] | - | -/Y | -/N |  |
| false_0 | title | 16 | field | acc | 0.688 | 0.135 | [0.679, 0.699] | [0.681, 0.700] | 1.007 | Y/Y | Y/Y |  |
| false_0 | title | 16 | year | r2 | 0.351 | 0.000 | [0.332, 0.371] | [0.323, 0.376] | 1.384 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations | r2 | 0.244 | 0.000 | [0.227, 0.263] | [0.226, 0.260] | 0.981 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations | year removed | r2 | 0.230 | 0.000 | [0.216, 0.251] | [0.215, 0.250] | 0.986 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | field | acc | 0.742 | 0.135 | [0.735, 0.751] | [0.732, 0.753] | 1.335 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | year | r2 | 0.938 | 0.000 | [0.931, 0.943] | [0.930, 0.943] | 1.119 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations | r2 | 0.404 | 0.000 | [0.392, 0.422] | [0.390, 0.421] | 1.023 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations | year removed | r2 | 0.367 | 0.000 | [0.355, 0.386] | [0.352, 0.383] | 0.984 | Y/Y | Y/Y |  |

Rows marked LEAK in the original note (year at the colon position) are positive controls only. Year-only baseline rows had no original interval.
