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
 "40": {
  "n_a20_target": 566,
  "n_a20_control": 561,
  "n_name_T": 3130,
  "n_name_C": 1524,
  "norm_ID_T": 41.22610855102539,
  "norm_ID_TC": 14.904692649841309,
  "random_sd": 0.013975424859373685
 },
 "48": {
  "n_a20_target": 566,
  "n_a20_control": 561,
  "n_name_T": 3130,
  "n_name_C": 1524,
  "norm_ID_T": 62.72549057006836,
  "norm_ID_TC": 18.507089614868164,
  "random_sd": 0.013975424859373685
 }
}

| layer | vector | direction | cos | lo | hi | share_top10PC_name | share_top50PC_name |
|---|---|---|---|---|---|---|---|
| 40 | ID_title target (true − fict) | author_gold_name (H3 probe, name pos) | 0.001 | -0.004 | 0.006 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_gold_title (E4b-style, title pos) | -0.028 | -0.036 | -0.019 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | Delta_name (T−C shift, name pos) | 0.022 | 0.005 | 0.040 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_name 1 | 0.003 | -0.003 | 0.008 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_name 2 | -0.011 | -0.016 | -0.005 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_name 3 | -0.010 | -0.015 | -0.003 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_title 1 | -0.036 | -0.042 | -0.028 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_title 2 | 0.011 | 0.001 | 0.020 | 0.014 | 0.052 |
| 40 | ID_title target (true − fict) | author_svd_title 3 | -0.012 | -0.021 | -0.004 | 0.014 | 0.052 |
| 40 | ID_title control | author_gold_name (H3 probe, name pos) | 0.004 | -0.001 | 0.008 | 0.009 | 0.047 |
| 40 | ID_title control | author_gold_title (E4b-style, title pos) | -0.020 | -0.027 | -0.012 | 0.009 | 0.047 |
| 40 | ID_title control | Delta_name (T−C shift, name pos) | 0.004 | -0.014 | 0.019 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_name 1 | -0.001 | -0.005 | 0.004 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_name 2 | -0.011 | -0.015 | -0.005 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_name 3 | -0.016 | -0.020 | -0.010 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_title 1 | -0.026 | -0.033 | -0.018 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_title 2 | 0.005 | -0.004 | 0.013 | 0.009 | 0.047 |
| 40 | ID_title control | author_svd_title 3 | 0.000 | -0.008 | 0.007 | 0.009 | 0.047 |
| 40 | ID_title T−C | author_gold_name (H3 probe, name pos) | -0.009 | -0.020 | 0.007 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_gold_title (E4b-style, title pos) | -0.021 | -0.039 | 0.011 | 0.021 | 0.063 |
| 40 | ID_title T−C | Delta_name (T−C shift, name pos) | 0.052 | -0.011 | 0.083 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_name 1 | 0.009 | -0.007 | 0.020 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_name 2 | 0.002 | -0.014 | 0.015 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_name 3 | 0.020 | -0.002 | 0.031 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_title 1 | -0.024 | -0.040 | 0.008 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_title 2 | 0.016 | -0.013 | 0.037 | 0.021 | 0.063 |
| 40 | ID_title T−C | author_svd_title 3 | -0.035 | -0.047 | -0.001 | 0.021 | 0.063 |
| 40 | (direction itself) | author_gold_name (H3 probe, name pos) | nan | nan | nan | 0.045 | 0.114 |
| 40 | (direction itself) | author_gold_title (E4b-style, title pos) | nan | nan | nan | 0.026 | 0.047 |
| 40 | (direction itself) | Delta_name (T−C shift, name pos) | nan | nan | nan | 0.551 | 0.845 |
| 40 | (direction itself) | author_svd_name 1 | nan | nan | nan | 0.033 | 0.100 |
| 40 | (direction itself) | author_svd_name 2 | nan | nan | nan | 0.074 | 0.160 |
| 40 | (direction itself) | author_svd_name 3 | nan | nan | nan | 0.032 | 0.232 |
| 40 | (direction itself) | author_svd_title 1 | nan | nan | nan | 0.019 | 0.041 |
| 40 | (direction itself) | author_svd_title 2 | nan | nan | nan | 0.034 | 0.079 |
| 40 | (direction itself) | author_svd_title 3 | nan | nan | nan | 0.032 | 0.096 |
| 48 | ID_title target (true − fict) | author_gold_name (H3 probe, name pos) | -0.018 | -0.022 | -0.013 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_gold_title (E4b-style, title pos) | -0.031 | -0.038 | -0.023 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | Delta_name (T−C shift, name pos) | -0.059 | -0.076 | -0.037 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_name 1 | -0.020 | -0.024 | -0.015 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_name 2 | -0.019 | -0.024 | -0.013 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_name 3 | -0.009 | -0.015 | -0.004 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_title 1 | -0.036 | -0.042 | -0.028 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_title 2 | -0.007 | -0.015 | 0.002 | 0.022 | 0.085 |
| 48 | ID_title target (true − fict) | author_svd_title 3 | -0.015 | -0.023 | -0.007 | 0.022 | 0.085 |
| 48 | ID_title control | author_gold_name (H3 probe, name pos) | -0.010 | -0.014 | -0.006 | 0.024 | 0.066 |
| 48 | ID_title control | author_gold_title (E4b-style, title pos) | -0.017 | -0.023 | -0.009 | 0.024 | 0.066 |
| 48 | ID_title control | Delta_name (T−C shift, name pos) | -0.059 | -0.073 | -0.041 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_name 1 | -0.014 | -0.017 | -0.009 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_name 2 | -0.020 | -0.025 | -0.014 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_name 3 | -0.005 | -0.010 | 0.000 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_title 1 | -0.023 | -0.030 | -0.016 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_title 2 | -0.009 | -0.016 | -0.001 | 0.024 | 0.066 |
| 48 | ID_title control | author_svd_title 3 | -0.006 | -0.013 | 0.001 | 0.024 | 0.066 |
| 48 | ID_title T−C | author_gold_name (H3 probe, name pos) | -0.024 | -0.031 | -0.002 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_gold_title (E4b-style, title pos) | -0.046 | -0.061 | -0.004 | 0.024 | 0.081 |
| 48 | ID_title T−C | Delta_name (T−C shift, name pos) | 0.005 | -0.070 | 0.075 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_name 1 | -0.019 | -0.027 | 0.000 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_name 2 | 0.005 | -0.016 | 0.023 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_name 3 | -0.014 | -0.029 | 0.008 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_title 1 | -0.039 | -0.055 | -0.001 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_title 2 | 0.006 | -0.025 | 0.032 | 0.024 | 0.081 |
| 48 | ID_title T−C | author_svd_title 3 | -0.029 | -0.045 | 0.004 | 0.024 | 0.081 |
| 48 | (direction itself) | author_gold_name (H3 probe, name pos) | nan | nan | nan | 0.037 | 0.069 |
| 48 | (direction itself) | author_gold_title (E4b-style, title pos) | nan | nan | nan | 0.008 | 0.024 |
| 48 | (direction itself) | Delta_name (T−C shift, name pos) | nan | nan | nan | 0.789 | 0.910 |
| 48 | (direction itself) | author_svd_name 1 | nan | nan | nan | 0.021 | 0.047 |
| 48 | (direction itself) | author_svd_name 2 | nan | nan | nan | 0.053 | 0.146 |
| 48 | (direction itself) | author_svd_name 3 | nan | nan | nan | 0.016 | 0.120 |
| 48 | (direction itself) | author_svd_title 1 | nan | nan | nan | 0.006 | 0.028 |
| 48 | (direction itself) | author_svd_title 2 | nan | nan | nan | 0.025 | 0.094 |
| 48 | (direction itself) | author_svd_title 3 | nan | nan | nan | 0.035 | 0.097 |

Random direction: ±0.014 (1 sd); random share in top 10 / 50 PCs: 0.0020 / 0.0098.
