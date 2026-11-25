# New 1 — addendum 24 with matched replacement counts (exploratory, post hoc)

R = S_true − S_variant (final L63, all authors, all name tokens). Common words were replaced by frequency-matched words, NOT synonyms, so their meaning changes. Team bootstrap 50.

```
  group            analysis                   k     n     est      lo      hi      Ra      Rb
 target   paired n_a == n_b                   1    19 +0.0044 -0.0622 +0.0634     NaN     NaN
 target   paired n_a == n_b                   2    16 +0.0711 +0.0210 +0.1332     NaN     NaN
 target   paired n_a == n_b                   3    11 +0.0404 -0.0170 +0.1038     NaN     NaN
 target   paired n_a == n_b                 all    49 +0.0384 +0.0097 +0.0710     NaN     NaN
 target     stratified by k                   1 19/34 +0.0106 -0.0592 +0.0713 +0.0341 +0.0235
 target     stratified by k                   2 18/24 +0.0342 -0.0448 +0.1059 +0.0627 +0.0285
 target     stratified by k                   3 14/16 +0.1218 +0.0137 +0.2774 +0.1506 +0.0288
 target     stratified by k                   4  10/5 +0.0625 -0.0493 +0.1505 +0.1393 +0.0769
 target     stratified by k              pooled    80 +0.0480 +0.0160 +0.0886     NaN     NaN
 target   per replaced word        R_a per word    80 +0.0411 +0.0202 +0.0657     NaN     NaN
 target   per replaced word        R_b per word    80 +0.0174 -0.0044 +0.0379     NaN     NaN
 target   per replaced word per-word difference    80 +0.0237 +0.0056 +0.0420     NaN     NaN
 target mean replaced words           n_a / n_b    80 +3.5500 +1.9375     NaN     NaN     NaN
control   paired n_a == n_b                   1    22 +0.0298 -0.0178 +0.0764     NaN     NaN
control   paired n_a == n_b                   2    14 -0.0046 -0.0406 +0.0419     NaN     NaN
control   paired n_a == n_b                   3     8 +0.0678 +0.0263 +0.1175     NaN     NaN
control   paired n_a == n_b                   4     5 +0.0606 +0.0210 +0.0928     NaN     NaN
control   paired n_a == n_b                 all    51 +0.0319 -0.0001 +0.0676     NaN     NaN
control     stratified by k                   1 22/38 +0.0373 -0.0078 +0.0790 +0.0467 +0.0093
control     stratified by k                   2 18/21 +0.0319 -0.0157 +0.0798 +0.0252 -0.0067
control     stratified by k                   3 13/12 +0.0569 +0.0185 +0.1473 +0.0312 -0.0257
control     stratified by k                   4  12/5 +0.0760 -0.0367 +0.2344 +0.0502 -0.0258
control     stratified by k              pooled    80 +0.0435 +0.0207 +0.0746     NaN     NaN
control   per replaced word        R_a per word    80 +0.0209 +0.0055 +0.0367     NaN     NaN
control   per replaced word        R_b per word    80 +0.0018 -0.0103 +0.0125     NaN     NaN
control   per replaced word per-word difference    80 +0.0191 +0.0044 +0.0346     NaN     NaN
control mean replaced words           n_a / n_b    80 +3.2250 +1.9625     NaN     NaN     NaN
    all   paired n_a == n_b                   1    41 +0.0180 -0.0177 +0.0713     NaN     NaN
    all   paired n_a == n_b                   2    30 +0.0358 -0.0030 +0.0823     NaN     NaN
    all   paired n_a == n_b                   3    19 +0.0519 +0.0171 +0.0822     NaN     NaN
    all   paired n_a == n_b                   4     8 +0.0650 +0.0056 +0.1175     NaN     NaN
    all   paired n_a == n_b                 all   100 +0.0351 +0.0178 +0.0645     NaN     NaN
    all     stratified by k                   1 41/72 +0.0248 -0.0224 +0.0781 +0.0408 +0.0160
    all     stratified by k                   2 36/45 +0.0319 -0.0061 +0.0809 +0.0440 +0.0121
    all     stratified by k                   3 27/28 +0.0877 +0.0255 +0.1386 +0.0931 +0.0054
    all     stratified by k                   4 22/10 +0.0652 -0.0780 +0.1442 +0.0907 +0.0256
    all     stratified by k              pooled   160 +0.0440 +0.0224 +0.0682     NaN     NaN
    all   per replaced word        R_a per word   160 +0.0310 +0.0207 +0.0454     NaN     NaN
    all   per replaced word        R_b per word   160 +0.0096 +0.0031 +0.0163     NaN     NaN
    all   per replaced word per-word difference   160 +0.0214 +0.0095 +0.0342     NaN     NaN
    all mean replaced words           n_a / n_b   160 +3.3875 +1.9500     NaN     NaN     NaN
```
