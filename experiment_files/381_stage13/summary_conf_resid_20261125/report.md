# Output confidence after removing name commonness / string features (POST-HOC, exploratory)

Written 2026-11-25 15:09 by `13_stage13/stage13_b2_gennames_b_conf_resid_20261125.py`. Names used 31561; target papers / pairs 518 / 3388.

## OOF R² of each confidence feature on name features

| feature | R² on Z (length, frequency, fame) | R² on Z + position |
|---|---|---|
| lp_mean | 0.061 | 0.089 |
| lp_first | 0.018 | 0.037 |
| neg_entropy | 0.042 | 0.067 |

## Within-paper AUROC (target papers, team bootstrap 2,000)

| score | AUROC [95% CI] |
|---|---|
| conf3 | 0.711 [0.678, 0.740] |
| lp_mean_raw | 0.698 [0.666, 0.728] |
| lp_mean_resid | 0.693 [0.658, 0.723] |
| conf3_resid | 0.695 [0.661, 0.725] |
| conf3_residP | 0.700 [0.667, 0.730] |
| names_Z | 0.560 [0.528, 0.592] |
| probe16 | 0.723 [0.696, 0.751] |
| probe24 | 0.740 [0.715, 0.767] |
| probe32 | 0.736 [0.708, 0.762] |
| probe40 | 0.780 [0.750, 0.808] |
| probe48 | 0.782 [0.754, 0.812] |
| probe52 | 0.771 [0.742, 0.798] |
| probe56 | 0.736 [0.706, 0.765] |

## Paired differences

| difference | est [95% CI] |
|---|---|
| conf3 − conf3_resid | +0.016 [+0.003, +0.029] |
| conf3 − conf3_residP | +0.011 [-0.002, +0.024] |
| lp_mean_raw − lp_mean_resid | +0.005 [-0.006, +0.016] |
| probe16 − conf3_resid | +0.028 [-0.009, +0.068] |
| probe16 − conf3 | +0.012 [-0.024, +0.052] |
| probe24 − conf3_resid | +0.045 [+0.011, +0.083] |
| probe24 − conf3 | +0.029 [-0.005, +0.067] |
| probe32 − conf3_resid | +0.041 [+0.008, +0.077] |
| probe32 − conf3 | +0.024 [-0.009, +0.060] |
| probe40 − conf3_resid | +0.084 [+0.051, +0.121] |
| probe40 − conf3 | +0.068 [+0.035, +0.105] |
| probe48 − conf3_resid | +0.087 [+0.049, +0.128] |
| probe48 − conf3 | +0.071 [+0.035, +0.109] |
| probe52 − conf3_resid | +0.076 [+0.042, +0.113] |
| probe52 − conf3 | +0.060 [+0.027, +0.095] |
| probe56 − conf3_resid | +0.041 [+0.006, +0.077] |
| probe56 − conf3 | +0.025 [-0.008, +0.059] |
