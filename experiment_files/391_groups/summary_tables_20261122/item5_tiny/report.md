# Item 5 — H2 × H3 direction overlap (exploratory, post hoc)

Item 5 (L40, L48): H2 x H3 direction overlap.
  ID_title = mean over addendum-20 target papers of (h_true - h_fict) at the LAST TITLE TOKEN (a20v2_titlepos resid_title_*;
  name-position fict states are not stored), also control and target - control.
  author_gold_name / author_svd_name = H3 name-position probe read-out directions (as explore_dir_overlap_20261121.py).
  author_gold_title = title-position author probe (E4b-style ridge: Stage 11 true title residual -> stored L63 colon residual,
  read through lm_head rows x final-norm weight of the gold first tokens), mean over target papers.
  Delta_name = name-position target - control mean shift of d_i.
  Cosines with random baseline 1/sqrt(5120); team-bootstrap CIs (1,000 draws, seed 22) for cosines of the mean vectors
  (ID_title, Delta_name) with fixed probe directions; shares in the top-10 / top-50 PCs of the item-4 pooled PCA (name
  position; for title-position vectors this is a cross-position comparison in the same residual basis).


{
 "48": {
  "n_a20_target": 566,
  "n_a20_control": 561,
  "n_name_T": 144,
  "n_name_C": 56,
  "norm_ID_T": 62.72549057006836,
  "norm_ID_TC": 18.507089614868164,
  "random_sd": 0.013975424859373685
 }
}

| layer | vector | direction | cos | lo | hi | share_top10PC_name | share_top50PC_name |
|---|---|---|---|---|---|---|---|
| 48 | ID_title target (true − fict) | author_gold_name (H3 probe, name pos) | 0.000 | -0.005 | 0.005 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_gold_title (E4b-style, title pos) | -0.034 | -0.042 | -0.026 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | Delta_name (T−C shift, name pos) | -0.037 | -0.048 | -0.025 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_name 1 | -0.002 | -0.007 | 0.003 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_name 2 | 0.018 | 0.012 | 0.023 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_name 3 | -0.002 | -0.007 | 0.003 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_title 1 | -0.038 | -0.045 | -0.030 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_title 2 | -0.003 | -0.009 | 0.004 | 0.023 | 0.073 |
| 48 | ID_title target (true − fict) | author_svd_title 3 | -0.012 | -0.020 | -0.004 | 0.023 | 0.073 |
| 48 | ID_title control | author_gold_name (H3 probe, name pos) | 0.007 | 0.002 | 0.012 | 0.026 | 0.060 |
| 48 | ID_title control | author_gold_title (E4b-style, title pos) | -0.023 | -0.030 | -0.016 | 0.026 | 0.060 |
| 48 | ID_title control | Delta_name (T−C shift, name pos) | -0.034 | -0.044 | -0.024 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_name 1 | 0.005 | -0.000 | 0.009 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_name 2 | 0.017 | 0.012 | 0.021 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_name 3 | 0.001 | -0.004 | 0.005 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_title 1 | -0.028 | -0.035 | -0.020 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_title 2 | 0.002 | -0.005 | 0.009 | 0.026 | 0.060 |
| 48 | ID_title control | author_svd_title 3 | -0.009 | -0.016 | -0.002 | 0.026 | 0.060 |
| 48 | ID_title T−C | author_gold_name (H3 probe, name pos) | -0.025 | -0.034 | -0.001 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_gold_title (E4b-style, title pos) | -0.035 | -0.053 | 0.005 | 0.023 | 0.074 |
| 48 | ID_title T−C | Delta_name (T−C shift, name pos) | -0.007 | -0.048 | 0.039 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_name 1 | -0.022 | -0.032 | 0.001 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_name 2 | 0.002 | -0.018 | 0.023 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_name 3 | -0.008 | -0.023 | 0.012 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_title 1 | -0.030 | -0.049 | 0.005 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_title 2 | -0.017 | -0.034 | 0.013 | 0.023 | 0.074 |
| 48 | ID_title T−C | author_svd_title 3 | -0.009 | -0.035 | 0.021 | 0.023 | 0.074 |
| 48 | (direction itself) | author_gold_name (H3 probe, name pos) | nan | nan | nan | 0.021 | 0.044 |
| 48 | (direction itself) | author_gold_title (E4b-style, title pos) | nan | nan | nan | 0.007 | 0.023 |
| 48 | (direction itself) | Delta_name (T−C shift, name pos) | nan | nan | nan | 0.242 | 0.617 |
| 48 | (direction itself) | author_svd_name 1 | nan | nan | nan | 0.010 | 0.029 |
| 48 | (direction itself) | author_svd_name 2 | nan | nan | nan | 0.040 | 0.121 |
| 48 | (direction itself) | author_svd_name 3 | nan | nan | nan | 0.010 | 0.096 |
| 48 | (direction itself) | author_svd_title 1 | nan | nan | nan | 0.006 | 0.025 |
| 48 | (direction itself) | author_svd_title 2 | nan | nan | nan | 0.012 | 0.038 |
| 48 | (direction itself) | author_svd_title 3 | nan | nan | nan | 0.016 | 0.040 |

Random direction: ±0.014 (1 sd); random share in top 10 / 50 PCs: 0.0020 / 0.0098.
