# Stage 13 M2: team-cluster bootstrap vs per-paper bootstrap

Folds/table: team (summary_cpu_group); original: /scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_group/M2_probes.csv

Team interval: author teams (= probe fold groups) resampled with replacement, NB=2000, seed 20261030; original: per-paper bootstrap, 200 draws. Held-out predictions recomputed with the same folds/alpha grid/features and saved under preds/. Null level: R^2 0, AUROC 0.5, field accuracy = majority-class share.

## Point-estimate check: 176 rows, max |new - original| = 1.11e-16; rows with |diff| > 1e-6: 0 (all match)

## Interval width ratio (team / paper)

Over all 171 rows with an original interval: mean 1.15, median 1.10, min 0.86, max 1.58.

                                                   count  mean   min   max
condition position target                                                 
false_0   colon    field                              10  1.32  1.20  1.49
                   log citations                      10  1.33  1.14  1.45
                   log citations | year removed       10  1.33  1.17  1.46
                   year                               10  1.15  0.99  1.29
          title    field                               9  1.42  1.25  1.56
                   log citations                       9  1.39  1.29  1.58
                   log citations | year removed        9  1.32  1.18  1.48
                   year                                9  1.30  1.21  1.42
true      colon    field                              10  1.05  0.94  1.17
                   log citations                      10  1.03  0.90  1.16
                   log citations | year removed       10  1.02  0.95  1.08
                   recognised (target vs control)     10  1.01  0.91  1.09
                   year                               10  0.98  0.91  1.08
          title    field                               9  1.08  0.93  1.16
                   log citations                       9  0.97  0.86  1.07
                   log citations | year removed        9  1.00  0.88  1.12
                   recognised (target vs control)      9  0.99  0.89  1.06
                   year                                9  1.07  0.96  1.19

## Flips: "interval excludes 0": 0 rows; "interval above chance (null level)": 0 rows

None.

## All rows

| condition | position | layer | target | metric | value | null | paper CI (200) | team CI (2000) | width ratio | excl 0 paper/team | > null paper/team | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| true | year-only baseline | -1 | log citations | r2 | 0.047 | 0.000 | [-, -] | [0.038, 0.056] | - | -/Y | -/Y |  |
| true | year-only baseline | -1 | log citations &#124; year removed | r2 | -0.001 | 0.000 | [-, -] | [-0.002, -0.001] | - | -/Y | -/N |  |
| true | year-only baseline | -1 | recognised (target vs control) | auc_bin | 0.555 | 0.500 | [-, -] | [0.534, 0.573] | - | -/Y | -/Y |  |
| true | title | 16 | field | acc | 0.698 | 0.135 | [0.689, 0.706] | [0.688, 0.708] | 1.139 | Y/Y | Y/Y |  |
| true | title | 16 | year | r2 | 0.383 | 0.000 | [0.364, 0.402] | [0.362, 0.403] | 1.079 | Y/Y | Y/Y |  |
| true | title | 16 | log citations | r2 | 0.286 | 0.000 | [0.268, 0.304] | [0.269, 0.302] | 0.931 | Y/Y | Y/Y |  |
| true | title | 16 | log citations &#124; year removed | r2 | 0.275 | 0.000 | [0.255, 0.294] | [0.258, 0.292] | 0.883 | Y/Y | Y/Y |  |
| true | title | 16 | recognised (target vs control) | auc_bin | 0.620 | 0.500 | [0.602, 0.638] | [0.602, 0.637] | 0.989 | Y/Y | Y/Y |  |
| true | title | 24 | field | acc | 0.722 | 0.135 | [0.712, 0.729] | [0.712, 0.731] | 1.102 | Y/Y | Y/Y |  |
| true | title | 24 | year | r2 | 0.451 | 0.000 | [0.435, 0.468] | [0.432, 0.469] | 1.105 | Y/Y | Y/Y |  |
| true | title | 24 | log citations | r2 | 0.370 | 0.000 | [0.351, 0.389] | [0.353, 0.386] | 0.859 | Y/Y | Y/Y |  |
| true | title | 24 | log citations &#124; year removed | r2 | 0.356 | 0.000 | [0.341, 0.372] | [0.339, 0.373] | 1.116 | Y/Y | Y/Y |  |
| true | title | 24 | recognised (target vs control) | auc_bin | 0.632 | 0.500 | [0.613, 0.652] | [0.613, 0.650] | 0.942 | Y/Y | Y/Y |  |
| true | title | 32 | field | acc | 0.719 | 0.135 | [0.711, 0.729] | [0.710, 0.729] | 1.020 | Y/Y | Y/Y |  |
| true | title | 32 | year | r2 | 0.471 | 0.000 | [0.453, 0.489] | [0.450, 0.489] | 1.074 | Y/Y | Y/Y |  |
| true | title | 32 | log citations | r2 | 0.365 | 0.000 | [0.347, 0.382] | [0.349, 0.381] | 0.905 | Y/Y | Y/Y |  |
| true | title | 32 | log citations &#124; year removed | r2 | 0.350 | 0.000 | [0.333, 0.366] | [0.333, 0.366] | 1.010 | Y/Y | Y/Y |  |
| true | title | 32 | recognised (target vs control) | auc_bin | 0.638 | 0.500 | [0.619, 0.655] | [0.620, 0.656] | 0.981 | Y/Y | Y/Y |  |
| true | title | 40 | field | acc | 0.716 | 0.135 | [0.708, 0.726] | [0.707, 0.726] | 1.068 | Y/Y | Y/Y |  |
| true | title | 40 | year | r2 | 0.503 | 0.000 | [0.480, 0.521] | [0.482, 0.522] | 0.957 | Y/Y | Y/Y |  |
| true | title | 40 | log citations | r2 | 0.453 | 0.000 | [0.439, 0.468] | [0.438, 0.468] | 1.029 | Y/Y | Y/Y |  |
| true | title | 40 | log citations &#124; year removed | r2 | 0.441 | 0.000 | [0.426, 0.458] | [0.425, 0.456] | 0.968 | Y/Y | Y/Y |  |
| true | title | 40 | recognised (target vs control) | auc_bin | 0.652 | 0.500 | [0.633, 0.668] | [0.633, 0.670] | 1.064 | Y/Y | Y/Y |  |
| true | title | 44 | field | acc | 0.709 | 0.135 | [0.700, 0.717] | [0.699, 0.719] | 1.156 | Y/Y | Y/Y |  |
| true | title | 44 | year | r2 | 0.516 | 0.000 | [0.497, 0.533] | [0.496, 0.535] | 1.071 | Y/Y | Y/Y |  |
| true | title | 44 | log citations | r2 | 0.509 | 0.000 | [0.494, 0.523] | [0.493, 0.523] | 1.067 | Y/Y | Y/Y |  |
| true | title | 44 | log citations &#124; year removed | r2 | 0.497 | 0.000 | [0.481, 0.513] | [0.482, 0.512] | 0.980 | Y/Y | Y/Y |  |
| true | title | 44 | recognised (target vs control) | auc_bin | 0.662 | 0.500 | [0.643, 0.678] | [0.644, 0.680] | 1.042 | Y/Y | Y/Y |  |
| true | title | 48 | field | acc | 0.716 | 0.135 | [0.707, 0.727] | [0.707, 0.726] | 0.931 | Y/Y | Y/Y |  |
| true | title | 48 | year | r2 | 0.555 | 0.000 | [0.537, 0.573] | [0.534, 0.575] | 1.138 | Y/Y | Y/Y |  |
| true | title | 48 | log citations | r2 | 0.530 | 0.000 | [0.515, 0.543] | [0.515, 0.544] | 0.994 | Y/Y | Y/Y |  |
| true | title | 48 | log citations &#124; year removed | r2 | 0.521 | 0.000 | [0.506, 0.537] | [0.505, 0.535] | 0.952 | Y/Y | Y/Y |  |
| true | title | 48 | recognised (target vs control) | auc_bin | 0.671 | 0.500 | [0.651, 0.688] | [0.653, 0.689] | 0.957 | Y/Y | Y/Y |  |
| true | title | 52 | field | acc | 0.719 | 0.135 | [0.711, 0.729] | [0.710, 0.729] | 1.074 | Y/Y | Y/Y |  |
| true | title | 52 | year | r2 | 0.561 | 0.000 | [0.541, 0.582] | [0.538, 0.582] | 1.055 | Y/Y | Y/Y |  |
| true | title | 52 | log citations | r2 | 0.520 | 0.000 | [0.504, 0.535] | [0.506, 0.535] | 0.940 | Y/Y | Y/Y |  |
| true | title | 52 | log citations &#124; year removed | r2 | 0.510 | 0.000 | [0.495, 0.526] | [0.495, 0.524] | 0.957 | Y/Y | Y/Y |  |
| true | title | 52 | recognised (target vs control) | auc_bin | 0.669 | 0.500 | [0.654, 0.688] | [0.651, 0.687] | 1.052 | Y/Y | Y/Y |  |
| true | title | 56 | field | acc | 0.716 | 0.135 | [0.708, 0.725] | [0.707, 0.726] | 1.122 | Y/Y | Y/Y |  |
| true | title | 56 | year | r2 | 0.559 | 0.000 | [0.538, 0.581] | [0.536, 0.579] | 0.996 | Y/Y | Y/Y |  |
| true | title | 56 | log citations | r2 | 0.517 | 0.000 | [0.502, 0.532] | [0.502, 0.532] | 0.973 | Y/Y | Y/Y |  |
| true | title | 56 | log citations &#124; year removed | r2 | 0.507 | 0.000 | [0.492, 0.521] | [0.493, 0.522] | 1.022 | Y/Y | Y/Y |  |
| true | title | 56 | recognised (target vs control) | auc_bin | 0.658 | 0.500 | [0.641, 0.677] | [0.641, 0.678] | 1.030 | Y/Y | Y/Y |  |
| true | title | 60 | field | acc | 0.717 | 0.135 | [0.708, 0.725] | [0.707, 0.726] | 1.150 | Y/Y | Y/Y |  |
| true | title | 60 | year | r2 | 0.547 | 0.000 | [0.528, 0.566] | [0.524, 0.569] | 1.188 | Y/Y | Y/Y |  |
| true | title | 60 | log citations | r2 | 0.498 | 0.000 | [0.481, 0.511] | [0.484, 0.514] | 1.018 | Y/Y | Y/Y |  |
| true | title | 60 | log citations &#124; year removed | r2 | 0.488 | 0.000 | [0.473, 0.500] | [0.473, 0.503] | 1.098 | Y/Y | Y/Y |  |
| true | title | 60 | recognised (target vs control) | auc_bin | 0.656 | 0.500 | [0.636, 0.676] | [0.640, 0.676] | 0.895 | Y/Y | Y/Y |  |
| true | colon | 16 | field | acc | 0.740 | 0.135 | [0.731, 0.748] | [0.731, 0.749] | 1.104 | Y/Y | Y/Y |  |
| true | colon | 16 | year | r2 | 0.974 | 0.000 | [0.967, 0.979] | [0.968, 0.979] | 0.926 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations | r2 | 0.431 | 0.000 | [0.415, 0.449] | [0.415, 0.448] | 0.953 | Y/Y | Y/Y |  |
| true | colon | 16 | log citations &#124; year removed | r2 | 0.400 | 0.000 | [0.382, 0.415] | [0.383, 0.417] | 1.060 | Y/Y | Y/Y |  |
| true | colon | 16 | recognised (target vs control) | auc_bin | 0.671 | 0.500 | [0.651, 0.690] | [0.650, 0.686] | 0.906 | Y/Y | Y/Y |  |
| true | colon | 24 | field | acc | 0.736 | 0.135 | [0.727, 0.747] | [0.726, 0.745] | 0.989 | Y/Y | Y/Y |  |
| true | colon | 24 | year | r2 | 0.981 | 0.000 | [0.977, 0.984] | [0.977, 0.984] | 0.992 | Y/Y | Y/Y |  |
| true | colon | 24 | log citations | r2 | 0.506 | 0.000 | [0.491, 0.520] | [0.490, 0.520] | 1.036 | Y/Y | Y/Y |  |
| true | colon | 24 | log citations &#124; year removed | r2 | 0.478 | 0.000 | [0.464, 0.494] | [0.461, 0.492] | 1.024 | Y/Y | Y/Y |  |
| true | colon | 24 | recognised (target vs control) | auc_bin | 0.671 | 0.500 | [0.653, 0.686] | [0.653, 0.687] | 1.021 | Y/Y | Y/Y |  |
| true | colon | 32 | field | acc | 0.740 | 0.135 | [0.731, 0.749] | [0.730, 0.749] | 1.030 | Y/Y | Y/Y |  |
| true | colon | 32 | year | r2 | 0.982 | 0.000 | [0.977, 0.985] | [0.977, 0.985] | 0.928 | Y/Y | Y/Y |  |
| true | colon | 32 | log citations | r2 | 0.515 | 0.000 | [0.501, 0.530] | [0.500, 0.529] | 1.033 | Y/Y | Y/Y |  |
| true | colon | 32 | log citations &#124; year removed | r2 | 0.488 | 0.000 | [0.474, 0.503] | [0.473, 0.503] | 1.060 | Y/Y | Y/Y |  |
| true | colon | 32 | recognised (target vs control) | auc_bin | 0.675 | 0.500 | [0.658, 0.689] | [0.657, 0.691] | 1.092 | Y/Y | Y/Y |  |
| true | colon | 40 | field | acc | 0.739 | 0.135 | [0.730, 0.747] | [0.730, 0.749] | 1.095 | Y/Y | Y/Y |  |
| true | colon | 40 | year | r2 | 0.980 | 0.000 | [0.974, 0.984] | [0.974, 0.984] | 0.989 | Y/Y | Y/Y |  |
| true | colon | 40 | log citations | r2 | 0.579 | 0.000 | [0.566, 0.594] | [0.566, 0.592] | 0.936 | Y/Y | Y/Y |  |
| true | colon | 40 | log citations &#124; year removed | r2 | 0.554 | 0.000 | [0.540, 0.567] | [0.540, 0.567] | 0.983 | Y/Y | Y/Y |  |
| true | colon | 40 | recognised (target vs control) | auc_bin | 0.688 | 0.500 | [0.667, 0.701] | [0.668, 0.703] | 1.031 | Y/Y | Y/Y |  |
| true | colon | 44 | field | acc | 0.737 | 0.135 | [0.729, 0.745] | [0.727, 0.746] | 1.175 | Y/Y | Y/Y |  |
| true | colon | 44 | year | r2 | 0.975 | 0.000 | [0.967, 0.981] | [0.966, 0.981] | 1.081 | Y/Y | Y/Y |  |
| true | colon | 44 | log citations | r2 | 0.621 | 0.000 | [0.611, 0.632] | [0.608, 0.633] | 1.162 | Y/Y | Y/Y |  |
| true | colon | 44 | log citations &#124; year removed | r2 | 0.597 | 0.000 | [0.584, 0.611] | [0.584, 0.610] | 0.974 | Y/Y | Y/Y |  |
| true | colon | 44 | recognised (target vs control) | auc_bin | 0.699 | 0.500 | [0.682, 0.714] | [0.679, 0.713] | 1.044 | Y/Y | Y/Y |  |
| true | colon | 48 | field | acc | 0.747 | 0.135 | [0.738, 0.755] | [0.738, 0.756] | 1.054 | Y/Y | Y/Y |  |
| true | colon | 48 | year | r2 | 0.979 | 0.000 | [0.973, 0.985] | [0.972, 0.985] | 1.077 | Y/Y | Y/Y |  |
| true | colon | 48 | log citations | r2 | 0.645 | 0.000 | [0.632, 0.656] | [0.632, 0.657] | 1.063 | Y/Y | Y/Y |  |
| true | colon | 48 | log citations &#124; year removed | r2 | 0.623 | 0.000 | [0.611, 0.636] | [0.610, 0.636] | 1.040 | Y/Y | Y/Y |  |
| true | colon | 48 | recognised (target vs control) | auc_bin | 0.711 | 0.500 | [0.693, 0.728] | [0.693, 0.726] | 0.959 | Y/Y | Y/Y |  |
| true | colon | 52 | field | acc | 0.748 | 0.135 | [0.739, 0.758] | [0.739, 0.757] | 1.000 | Y/Y | Y/Y |  |
| true | colon | 52 | year | r2 | 0.982 | 0.000 | [0.976, 0.986] | [0.976, 0.986] | 1.037 | Y/Y | Y/Y |  |
| true | colon | 52 | log citations | r2 | 0.630 | 0.000 | [0.619, 0.642] | [0.617, 0.644] | 1.158 | Y/Y | Y/Y |  |
| true | colon | 52 | log citations &#124; year removed | r2 | 0.607 | 0.000 | [0.595, 0.624] | [0.594, 0.621] | 0.948 | Y/Y | Y/Y |  |
| true | colon | 52 | recognised (target vs control) | auc_bin | 0.720 | 0.500 | [0.703, 0.736] | [0.703, 0.736] | 0.997 | Y/Y | Y/Y |  |
| true | colon | 56 | field | acc | 0.745 | 0.135 | [0.737, 0.754] | [0.736, 0.754] | 1.118 | Y/Y | Y/Y |  |
| true | colon | 56 | year | r2 | 0.968 | 0.000 | [0.961, 0.972] | [0.961, 0.972] | 0.962 | Y/Y | Y/Y |  |
| true | colon | 56 | log citations | r2 | 0.602 | 0.000 | [0.588, 0.619] | [0.588, 0.616] | 0.901 | Y/Y | Y/Y |  |
| true | colon | 56 | log citations &#124; year removed | r2 | 0.577 | 0.000 | [0.561, 0.591] | [0.562, 0.591] | 0.975 | Y/Y | Y/Y |  |
| true | colon | 56 | recognised (target vs control) | auc_bin | 0.713 | 0.500 | [0.694, 0.730] | [0.694, 0.729] | 0.951 | Y/Y | Y/Y |  |
| true | colon | 60 | field | acc | 0.743 | 0.135 | [0.734, 0.753] | [0.734, 0.752] | 0.959 | Y/Y | Y/Y |  |
| true | colon | 60 | year | r2 | 0.937 | 0.000 | [0.922, 0.948] | [0.924, 0.948] | 0.933 | Y/Y | Y/Y |  |
| true | colon | 60 | log citations | r2 | 0.589 | 0.000 | [0.573, 0.603] | [0.575, 0.603] | 0.953 | Y/Y | Y/Y |  |
| true | colon | 60 | log citations &#124; year removed | r2 | 0.563 | 0.000 | [0.550, 0.577] | [0.548, 0.578] | 1.077 | Y/Y | Y/Y |  |
| true | colon | 60 | recognised (target vs control) | auc_bin | 0.714 | 0.500 | [0.696, 0.728] | [0.695, 0.729] | 1.059 | Y/Y | Y/Y |  |
| true | colon | 63 | field | acc | 0.744 | 0.135 | [0.734, 0.754] | [0.735, 0.753] | 0.935 | Y/Y | Y/Y |  |
| true | colon | 63 | year | r2 | 0.927 | 0.000 | [0.912, 0.940] | [0.913, 0.938] | 0.907 | Y/Y | Y/Y |  |
| true | colon | 63 | log citations | r2 | 0.594 | 0.000 | [0.581, 0.608] | [0.580, 0.608] | 1.075 | Y/Y | Y/Y |  |
| true | colon | 63 | log citations &#124; year removed | r2 | 0.566 | 0.000 | [0.553, 0.581] | [0.551, 0.581] | 1.065 | Y/Y | Y/Y |  |
| true | colon | 63 | recognised (target vs control) | auc_bin | 0.723 | 0.500 | [0.707, 0.738] | [0.705, 0.740] | 1.077 | Y/Y | Y/Y |  |
| false_0 | year-only baseline | -1 | log citations | r2 | 0.048 | 0.000 | [-, -] | [0.037, 0.059] | - | -/Y | -/Y |  |
| false_0 | year-only baseline | -1 | log citations &#124; year removed | r2 | -0.001 | 0.000 | [-, -] | [-0.002, -0.000] | - | -/Y | -/N |  |
| false_0 | title | 16 | field | acc | 0.689 | 0.135 | [0.679, 0.699] | [0.677, 0.701] | 1.264 | Y/Y | Y/Y |  |
| false_0 | title | 16 | year | r2 | 0.353 | 0.000 | [0.332, 0.371] | [0.328, 0.377] | 1.271 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations | r2 | 0.246 | 0.000 | [0.227, 0.263] | [0.222, 0.269] | 1.339 | Y/Y | Y/Y |  |
| false_0 | title | 16 | log citations &#124; year removed | r2 | 0.232 | 0.000 | [0.216, 0.251] | [0.208, 0.256] | 1.358 | Y/Y | Y/Y |  |
| false_0 | title | 24 | field | acc | 0.715 | 0.135 | [0.707, 0.723] | [0.702, 0.727] | 1.561 | Y/Y | Y/Y |  |
| false_0 | title | 24 | year | r2 | 0.421 | 0.000 | [0.404, 0.440] | [0.394, 0.445] | 1.423 | Y/Y | Y/Y |  |
| false_0 | title | 24 | log citations | r2 | 0.333 | 0.000 | [0.315, 0.348] | [0.310, 0.355] | 1.362 | Y/Y | Y/Y |  |
| false_0 | title | 24 | log citations &#124; year removed | r2 | 0.315 | 0.000 | [0.296, 0.335] | [0.292, 0.338] | 1.182 | Y/Y | Y/Y |  |
| false_0 | title | 32 | field | acc | 0.716 | 0.135 | [0.708, 0.725] | [0.704, 0.728] | 1.414 | Y/Y | Y/Y |  |
| false_0 | title | 32 | year | r2 | 0.446 | 0.000 | [0.429, 0.464] | [0.421, 0.470] | 1.396 | Y/Y | Y/Y |  |
| false_0 | title | 32 | log citations | r2 | 0.326 | 0.000 | [0.308, 0.341] | [0.303, 0.349] | 1.415 | Y/Y | Y/Y |  |
| false_0 | title | 32 | log citations &#124; year removed | r2 | 0.313 | 0.000 | [0.294, 0.327] | [0.290, 0.335] | 1.373 | Y/Y | Y/Y |  |
| false_0 | title | 40 | field | acc | 0.708 | 0.135 | [0.699, 0.715] | [0.695, 0.720] | 1.489 | Y/Y | Y/Y |  |
| false_0 | title | 40 | year | r2 | 0.480 | 0.000 | [0.458, 0.497] | [0.454, 0.506] | 1.324 | Y/Y | Y/Y |  |
| false_0 | title | 40 | log citations | r2 | 0.405 | 0.000 | [0.388, 0.423] | [0.382, 0.427] | 1.310 | Y/Y | Y/Y |  |
| false_0 | title | 40 | log citations &#124; year removed | r2 | 0.390 | 0.000 | [0.374, 0.408] | [0.367, 0.411] | 1.288 | Y/Y | Y/Y |  |
| false_0 | title | 44 | field | acc | 0.702 | 0.135 | [0.695, 0.712] | [0.690, 0.715] | 1.496 | Y/Y | Y/Y |  |
| false_0 | title | 44 | year | r2 | 0.498 | 0.000 | [0.480, 0.517] | [0.474, 0.521] | 1.264 | Y/Y | Y/Y |  |
| false_0 | title | 44 | log citations | r2 | 0.473 | 0.000 | [0.457, 0.489] | [0.451, 0.493] | 1.290 | Y/Y | Y/Y |  |
| false_0 | title | 44 | log citations &#124; year removed | r2 | 0.455 | 0.000 | [0.438, 0.471] | [0.433, 0.476] | 1.268 | Y/Y | Y/Y |  |
| false_0 | title | 48 | field | acc | 0.716 | 0.135 | [0.708, 0.724] | [0.704, 0.728] | 1.509 | Y/Y | Y/Y |  |
| false_0 | title | 48 | year | r2 | 0.535 | 0.000 | [0.515, 0.556] | [0.510, 0.559] | 1.208 | Y/Y | Y/Y |  |
| false_0 | title | 48 | log citations | r2 | 0.488 | 0.000 | [0.473, 0.502] | [0.467, 0.508] | 1.429 | Y/Y | Y/Y |  |
| false_0 | title | 48 | log citations &#124; year removed | r2 | 0.471 | 0.000 | [0.454, 0.487] | [0.449, 0.491] | 1.267 | Y/Y | Y/Y |  |
| false_0 | title | 52 | field | acc | 0.718 | 0.135 | [0.710, 0.726] | [0.706, 0.730] | 1.459 | Y/Y | Y/Y |  |
| false_0 | title | 52 | year | r2 | 0.538 | 0.000 | [0.517, 0.558] | [0.510, 0.564] | 1.294 | Y/Y | Y/Y |  |
| false_0 | title | 52 | log citations | r2 | 0.484 | 0.000 | [0.468, 0.499] | [0.464, 0.505] | 1.358 | Y/Y | Y/Y |  |
| false_0 | title | 52 | log citations &#124; year removed | r2 | 0.470 | 0.000 | [0.456, 0.486] | [0.449, 0.490] | 1.384 | Y/Y | Y/Y |  |
| false_0 | title | 56 | field | acc | 0.723 | 0.135 | [0.713, 0.732] | [0.710, 0.734] | 1.247 | Y/Y | Y/Y |  |
| false_0 | title | 56 | year | r2 | 0.532 | 0.000 | [0.509, 0.550] | [0.505, 0.557] | 1.257 | Y/Y | Y/Y |  |
| false_0 | title | 56 | log citations | r2 | 0.478 | 0.000 | [0.465, 0.491] | [0.456, 0.498] | 1.582 | Y/Y | Y/Y |  |
| false_0 | title | 56 | log citations &#124; year removed | r2 | 0.463 | 0.000 | [0.448, 0.476] | [0.442, 0.483] | 1.478 | Y/Y | Y/Y |  |
| false_0 | title | 60 | field | acc | 0.715 | 0.135 | [0.707, 0.725] | [0.703, 0.727] | 1.385 | Y/Y | Y/Y |  |
| false_0 | title | 60 | year | r2 | 0.526 | 0.000 | [0.504, 0.546] | [0.500, 0.552] | 1.219 | Y/Y | Y/Y |  |
| false_0 | title | 60 | log citations | r2 | 0.468 | 0.000 | [0.455, 0.483] | [0.448, 0.487] | 1.397 | Y/Y | Y/Y |  |
| false_0 | title | 60 | log citations &#124; year removed | r2 | 0.453 | 0.000 | [0.439, 0.468] | [0.433, 0.473] | 1.327 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | field | acc | 0.743 | 0.135 | [0.735, 0.751] | [0.731, 0.755] | 1.492 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | year | r2 | 0.938 | 0.000 | [0.931, 0.943] | [0.930, 0.944] | 1.160 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations | r2 | 0.407 | 0.000 | [0.392, 0.422] | [0.387, 0.426] | 1.247 | Y/Y | Y/Y |  |
| false_0 | colon | 16 | log citations &#124; year removed | r2 | 0.371 | 0.000 | [0.355, 0.386] | [0.350, 0.390] | 1.271 | Y/Y | Y/Y |  |
| false_0 | colon | 24 | field | acc | 0.743 | 0.135 | [0.733, 0.751] | [0.730, 0.754] | 1.332 | Y/Y | Y/Y |  |
| false_0 | colon | 24 | year | r2 | 0.945 | 0.000 | [0.941, 0.949] | [0.941, 0.950] | 1.129 | Y/Y | Y/Y |  |
| false_0 | colon | 24 | log citations | r2 | 0.480 | 0.000 | [0.465, 0.494] | [0.461, 0.499] | 1.282 | Y/Y | Y/Y |  |
| false_0 | colon | 24 | log citations &#124; year removed | r2 | 0.449 | 0.000 | [0.432, 0.465] | [0.428, 0.467] | 1.172 | Y/Y | Y/Y |  |
| false_0 | colon | 32 | field | acc | 0.741 | 0.135 | [0.732, 0.752] | [0.729, 0.753] | 1.201 | Y/Y | Y/Y |  |
| false_0 | colon | 32 | year | r2 | 0.944 | 0.000 | [0.940, 0.948] | [0.939, 0.949] | 1.210 | Y/Y | Y/Y |  |
| false_0 | colon | 32 | log citations | r2 | 0.484 | 0.000 | [0.471, 0.497] | [0.465, 0.503] | 1.436 | Y/Y | Y/Y |  |
| false_0 | colon | 32 | log citations &#124; year removed | r2 | 0.453 | 0.000 | [0.439, 0.470] | [0.431, 0.471] | 1.316 | Y/Y | Y/Y |  |
| false_0 | colon | 40 | field | acc | 0.740 | 0.135 | [0.732, 0.750] | [0.729, 0.752] | 1.265 | Y/Y | Y/Y |  |
| false_0 | colon | 40 | year | r2 | 0.946 | 0.000 | [0.942, 0.950] | [0.941, 0.950] | 1.090 | Y/Y | Y/Y |  |
| false_0 | colon | 40 | log citations | r2 | 0.542 | 0.000 | [0.527, 0.556] | [0.523, 0.561] | 1.328 | Y/Y | Y/Y |  |
| false_0 | colon | 40 | log citations &#124; year removed | r2 | 0.512 | 0.000 | [0.496, 0.524] | [0.492, 0.530] | 1.362 | Y/Y | Y/Y |  |
| false_0 | colon | 44 | field | acc | 0.737 | 0.135 | [0.728, 0.745] | [0.725, 0.749] | 1.389 | Y/Y | Y/Y |  |
| false_0 | colon | 44 | year | r2 | 0.937 | 0.000 | [0.930, 0.943] | [0.929, 0.944] | 1.119 | Y/Y | Y/Y |  |
| false_0 | colon | 44 | log citations | r2 | 0.582 | 0.000 | [0.568, 0.593] | [0.564, 0.599] | 1.450 | Y/Y | Y/Y |  |
| false_0 | colon | 44 | log citations &#124; year removed | r2 | 0.555 | 0.000 | [0.541, 0.567] | [0.536, 0.572] | 1.425 | Y/Y | Y/Y |  |
| false_0 | colon | 48 | field | acc | 0.749 | 0.135 | [0.741, 0.760] | [0.737, 0.761] | 1.217 | Y/Y | Y/Y |  |
| false_0 | colon | 48 | year | r2 | 0.943 | 0.000 | [0.937, 0.950] | [0.936, 0.950] | 1.113 | Y/Y | Y/Y |  |
| false_0 | colon | 48 | log citations | r2 | 0.609 | 0.000 | [0.596, 0.622] | [0.591, 0.627] | 1.357 | Y/Y | Y/Y |  |
| false_0 | colon | 48 | log citations &#124; year removed | r2 | 0.577 | 0.000 | [0.561, 0.588] | [0.559, 0.595] | 1.353 | Y/Y | Y/Y |  |
| false_0 | colon | 52 | field | acc | 0.747 | 0.135 | [0.738, 0.755] | [0.736, 0.758] | 1.341 | Y/Y | Y/Y |  |
| false_0 | colon | 52 | year | r2 | 0.946 | 0.000 | [0.942, 0.949] | [0.941, 0.950] | 1.290 | Y/Y | Y/Y |  |
| false_0 | colon | 52 | log citations | r2 | 0.595 | 0.000 | [0.579, 0.609] | [0.575, 0.613] | 1.240 | Y/Y | Y/Y |  |
| false_0 | colon | 52 | log citations &#124; year removed | r2 | 0.566 | 0.000 | [0.550, 0.581] | [0.546, 0.585] | 1.274 | Y/Y | Y/Y |  |
| false_0 | colon | 56 | field | acc | 0.746 | 0.135 | [0.740, 0.756] | [0.734, 0.759] | 1.493 | Y/Y | Y/Y |  |
| false_0 | colon | 56 | year | r2 | 0.924 | 0.000 | [0.914, 0.933] | [0.914, 0.933] | 0.985 | Y/Y | Y/Y |  |
| false_0 | colon | 56 | log citations | r2 | 0.557 | 0.000 | [0.541, 0.572] | [0.535, 0.576] | 1.353 | Y/Y | Y/Y |  |
| false_0 | colon | 56 | log citations &#124; year removed | r2 | 0.524 | 0.000 | [0.508, 0.538] | [0.502, 0.545] | 1.413 | Y/Y | Y/Y |  |
| false_0 | colon | 60 | field | acc | 0.741 | 0.135 | [0.730, 0.749] | [0.729, 0.753] | 1.266 | Y/Y | Y/Y |  |
| false_0 | colon | 60 | year | r2 | 0.909 | 0.000 | [0.900, 0.919] | [0.897, 0.920] | 1.185 | Y/Y | Y/Y |  |
| false_0 | colon | 60 | log citations | r2 | 0.538 | 0.000 | [0.523, 0.553] | [0.516, 0.558] | 1.438 | Y/Y | Y/Y |  |
| false_0 | colon | 60 | log citations &#124; year removed | r2 | 0.503 | 0.000 | [0.487, 0.517] | [0.480, 0.524] | 1.456 | Y/Y | Y/Y |  |
| false_0 | colon | 63 | field | acc | 0.743 | 0.135 | [0.732, 0.752] | [0.731, 0.755] | 1.196 | Y/Y | Y/Y |  |
| false_0 | colon | 63 | year | r2 | 0.901 | 0.000 | [0.891, 0.910] | [0.889, 0.912] | 1.204 | Y/Y | Y/Y |  |
| false_0 | colon | 63 | log citations | r2 | 0.539 | 0.000 | [0.521, 0.557] | [0.518, 0.558] | 1.144 | Y/Y | Y/Y |  |
| false_0 | colon | 63 | log citations &#124; year removed | r2 | 0.502 | 0.000 | [0.485, 0.517] | [0.480, 0.522] | 1.301 | Y/Y | Y/Y |  |

Rows marked LEAK in the original note (year at the colon position) are positive controls only. Year-only baseline rows had no original interval.
