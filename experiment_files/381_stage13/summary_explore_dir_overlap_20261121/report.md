# Direction overlap at the name positions — exploratory (post hoc, not pre-registered)

Exploratory (post hoc, not pre-registered), 2026-11-21: does the name-position target - control shift point along attribute or
author-probe directions?  CPU only, stored states (raw/b2_npprobe, surname first token rows, L40 / L48).

Delta = mean_T d - mean_C d, d_i = paper mean of [h_true - mean usable h_false] (Vpd rule; = explore_pca_np_20261120.py).
Directions (all in the raw residual space at the name position):
  attribute  ridge on paper-mean TRUE states at the name position (surname first rows): year, log10(1+citations), field
             (one-vs-rest, fields with >= 200 papers). The published M2 probes read the TITLE position and their weights are
             not stored, so these are refits at the name position with the M2-style setup (standardised X, ridge alpha 1.0 x
             tr(G)/d, all 9,108 papers); direction = w / sd, unit-normalised.
  author     Q = diag(1/sd) W diag(norm_w) U_names^T, W = the published name-position ridge map (surname first, refit on all true
             rows, alpha 1.0 x tr(G)/d, target = stored L63 residual), U_names = lm_head rows of the cohort surname-first
             tokens. q_gold(row) = Q[:, gold token] = linear part of the probe's gold-token logit; author_gold = mean over target
             papers of the paper-mean q_gold (also over all papers); author_svd = top-5 left singular vectors of Q.
Reported per layer: cos(Delta, direction); share of each direction's squared norm in the top 10 / 50 PCs of the earlier PCA
(uncentered D_T, Vpd; random baseline k/5120); for subspaces (field one-vs-rest, author_svd top-5): share of Delta inside.


## L40 · n_T 3130 / n_C 1524 · |Delta| 2.965

| direction | cos(Δ, dir) | share in top-10 PCs | share in top-50 PCs |
|---|---|---|---|
| author_gold (target papers) | -0.127 | 0.045 | 0.113 |
| author_gold (all papers) | -0.130 | 0.045 | 0.113 |
| author_svd 1 | +0.123 | 0.035 | 0.098 |
| author_svd 2 | +0.019 | 0.068 | 0.153 |
| author_svd 3 | +0.055 | 0.034 | 0.238 |
| author_svd 4 | +0.003 | 0.024 | 0.162 |
| author_svd 5 | -0.124 | 0.032 | 0.147 |
| attr year | +0.012 | 0.000 | 0.003 |
| attr log citations | +0.064 | 0.017 | 0.109 |
| attr field=medicine | -0.040 | 0.031 | 0.096 |
| attr field=biology | +0.048 | 0.027 | 0.146 |
| attr field=computer science | -0.045 | 0.040 | 0.087 |
| attr field=psychology | -0.015 | 0.017 | 0.109 |
| attr field=chemistry | -0.019 | 0.013 | 0.106 |
| attr field=mathematics | +0.083 | 0.034 | 0.102 |
| attr field=physics | +0.037 | 0.040 | 0.109 |
| attr field=materials science | -0.043 | 0.013 | 0.086 |
| random direction (expected) | ±0.014 (1 sd) | 0.0020 | 0.0098 |

Share of Δ inside: field subspace (8 dims) 0.015; author SVD top-5 0.034; all directions above (17 dims) 0.071; random expectation 0.00020 per dimension. Δ in top-10 / top-50 PCs: 0.599 / 0.873.

## L48 · n_T 3130 / n_C 1524 · |Delta| 6.028

| direction | cos(Δ, dir) | share in top-10 PCs | share in top-50 PCs |
|---|---|---|---|
| author_gold (target papers) | -0.133 | 0.035 | 0.070 |
| author_gold (all papers) | -0.134 | 0.035 | 0.070 |
| author_svd 1 | -0.115 | 0.022 | 0.046 |
| author_svd 2 | +0.033 | 0.048 | 0.142 |
| author_svd 3 | -0.036 | 0.015 | 0.105 |
| author_svd 4 | -0.004 | 0.009 | 0.057 |
| author_svd 5 | +0.146 | 0.033 | 0.102 |
| attr year | +0.011 | 0.000 | 0.001 |
| attr log citations | +0.063 | 0.032 | 0.059 |
| attr field=medicine | -0.025 | 0.019 | 0.065 |
| attr field=biology | +0.030 | 0.014 | 0.069 |
| attr field=computer science | -0.020 | 0.017 | 0.062 |
| attr field=psychology | -0.005 | 0.017 | 0.078 |
| attr field=chemistry | -0.016 | 0.011 | 0.059 |
| attr field=mathematics | +0.055 | 0.011 | 0.058 |
| attr field=physics | +0.021 | 0.010 | 0.075 |
| attr field=materials science | -0.040 | 0.009 | 0.064 |
| random direction (expected) | ±0.014 (1 sd) | 0.0020 | 0.0098 |

Share of Δ inside: field subspace (8 dims) 0.007; author SVD top-5 0.037; all directions above (17 dims) 0.061; random expectation 0.00020 per dimension. Δ in top-10 / top-50 PCs: 0.808 / 0.929.

