# New 1 — addendum 24 with matched replacement counts (exploratory, post hoc)

R = S_true − S_variant (final L63, all authors, all name tokens). Common words were replaced by frequency-matched words, NOT synonyms, so their meaning changes. Team bootstrap 2000.

```
  group            analysis                   k       n     est      lo      hi      Ra      Rb
 target   paired n_a == n_b                   1     101 +0.0513 +0.0232 +0.0814     NaN     NaN
 target   paired n_a == n_b                   2      84 +0.0702 +0.0415 +0.0994     NaN     NaN
 target   paired n_a == n_b                   3      57 +0.0445 +0.0111 +0.0801     NaN     NaN
 target   paired n_a == n_b                   4      22 +0.1441 +0.0680 +0.2310     NaN     NaN
 target   paired n_a == n_b                   5       6 +0.0709 +0.0391 +0.0960     NaN     NaN
 target   paired n_a == n_b                 all     274 +0.0655 +0.0485 +0.0819     NaN     NaN
 target     stratified by k                   1 101/167 +0.0535 +0.0244 +0.0858 +0.0752 +0.0217
 target     stratified by k                   2  94/112 +0.0675 +0.0386 +0.0963 +0.0940 +0.0264
 target     stratified by k                   3   72/85 +0.0859 +0.0466 +0.1308 +0.1144 +0.0285
 target     stratified by k                   4   45/32 +0.1571 +0.1009 +0.2171 +0.1960 +0.0389
 target     stratified by k                   5   26/16 +0.2033 +0.0944 +0.3156 +0.2834 +0.0801
 target     stratified by k              pooled     418 +0.0832 +0.0660 +0.1009     NaN     NaN
 target   per replaced word        R_a per word     418 +0.0523 +0.0433 +0.0625     NaN     NaN
 target   per replaced word        R_b per word     418 +0.0155 +0.0093 +0.0212     NaN     NaN
 target   per replaced word per-word difference     418 +0.0368 +0.0284 +0.0460     NaN     NaN
 target mean replaced words           n_a / n_b     418 +3.5287 +2.1340     NaN     NaN     NaN
control   paired n_a == n_b                   1     103 +0.0204 -0.0022 +0.0435     NaN     NaN
control   paired n_a == n_b                   2      76 +0.0224 -0.0059 +0.0504     NaN     NaN
control   paired n_a == n_b                   3      50 +0.0437 +0.0051 +0.0784     NaN     NaN
control   paired n_a == n_b                   4      22 +0.0625 +0.0181 +0.1086     NaN     NaN
control   paired n_a == n_b                   5       6 +0.0951 -0.1038 +0.3366     NaN     NaN
control   paired n_a == n_b                 all     262 +0.0301 +0.0140 +0.0458     NaN     NaN
control     stratified by k                   1 103/177 +0.0254 +0.0057 +0.0471 +0.0334 +0.0081
control     stratified by k                   2  89/114 +0.0345 +0.0036 +0.0645 +0.0514 +0.0170
control     stratified by k                   3   76/74 +0.0412 +0.0075 +0.0730 +0.0396 -0.0015
control     stratified by k                   4   57/30 +0.0781 +0.0307 +0.1254 +0.0798 +0.0017
control     stratified by k                   5   26/11 +0.0962 +0.0091 +0.1831 +0.1131 +0.0169
control     stratified by k              pooled     413 +0.0400 +0.0263 +0.0535     NaN     NaN
control   per replaced word        R_a per word     413 +0.0230 +0.0168 +0.0293     NaN     NaN
control   per replaced word        R_b per word     413 +0.0058 +0.0004 +0.0114     NaN     NaN
control   per replaced word per-word difference     413 +0.0172 +0.0096 +0.0245     NaN     NaN
control mean replaced words           n_a / n_b     413 +3.2930 +2.0605     NaN     NaN     NaN
    all   paired n_a == n_b                   1     204 +0.0357 +0.0165 +0.0547     NaN     NaN
    all   paired n_a == n_b                   2     160 +0.0475 +0.0272 +0.0678     NaN     NaN
    all   paired n_a == n_b                   3     107 +0.0441 +0.0198 +0.0676     NaN     NaN
    all   paired n_a == n_b                   4      44 +0.1033 +0.0570 +0.1544     NaN     NaN
    all   paired n_a == n_b                   5      12 +0.0830 -0.0150 +0.2066     NaN     NaN
    all   paired n_a == n_b                   6       5 +0.0651 -0.2896 +0.2920     NaN     NaN
    all   paired n_a == n_b                 all     536 +0.0482 +0.0358 +0.0590     NaN     NaN
    all     stratified by k                   1 204/344 +0.0394 +0.0214 +0.0588 +0.0541 +0.0147
    all     stratified by k                   2 183/226 +0.0516 +0.0314 +0.0729 +0.0733 +0.0217
    all     stratified by k                   3 148/159 +0.0615 +0.0348 +0.0885 +0.0760 +0.0145
    all     stratified by k                   4  102/62 +0.1102 +0.0717 +0.1472 +0.1311 +0.0209
    all     stratified by k                   5   52/27 +0.1439 +0.0705 +0.2189 +0.1982 +0.0544
    all     stratified by k                   6    48/7 +0.1893 +0.0736 +0.2934 +0.1954 +0.0061
    all     stratified by k              pooled     831 +0.0623 +0.0510 +0.0738     NaN     NaN
    all   per replaced word        R_a per word     831 +0.0377 +0.0323 +0.0438     NaN     NaN
    all   per replaced word        R_b per word     831 +0.0107 +0.0067 +0.0149     NaN     NaN
    all   per replaced word per-word difference     831 +0.0271 +0.0210 +0.0331     NaN     NaN
    all mean replaced words           n_a / n_b     831 +3.4116 +2.0975     NaN     NaN     NaN
```
