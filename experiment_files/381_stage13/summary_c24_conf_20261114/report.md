# C24 / 2-11b follow-up (plan_batch_20261114b item 1) — POST-HOC, exploratory

Written 2026-11-14 06:26 by `13_stage13/stage13_c24_conf_20261114.py` (CPU).

## Parity

probe L48 0.782 [0.754, 0.812] (published 0.782 [0.754, 0.812]); old combined 0.679 (published 0.679): OK

## 1a (shard 0, replay job 11836635)

```
{
 "replay": {
  "shard": 0,
  "papers": 143,
  "names": 640,
  "positions": 4566,
  "agree": 4469,
  "agreement": 0.9787560227770478,
  "h2_positions": 4118,
  "h2_agree": 4024,
  "agreement_vs_stored_final_argmax": 0.9771733851384167,
  "prompt_length_mismatch": 0,
  "wall_s": 11.885023564100266,
  "job": "11836635"
 },
 "stored": {
  "conf_parquet_columns": [
   "paper_id",
   "item_index",
   "status",
   "lp_first",
   "ent_pre",
   "lp_mean",
   "lp_sum",
   "n_tok",
   "tf_argmax_first_eq"
  ],
  "conf_rows": 640,
  "h2_columns": [
   "paper_id",
   "pos",
   "next_tok",
   "final_argmax",
   "step_logit_argmax"
  ],
  "npz_keys_sample": [
   "key",
   "last@16",
   "last@24",
   "last@32",
   "..."
  ],
  "npz_layers": "residuals L16-L56 only (name_mean / pred_first / last), no final layer, no logits"
 },
 "generation_time_logits_stored": false,
 "h2_next_tok_eq_stored_final_argmax": 1.0,
 "h2_positions_in_replay_range": true,
 "h2_duplicate_rows": 0,
 "mismatches_all": 97,
 "mismatches_on_name_predicting_positions": 94,
 "mismatches_other": 3,
 "base_share_name_predicting": 0.9018834866403854,
 "mismatch_share_name_predicting": 0.9690721649484536,
 "enrichment": 1.0744981799792714,
 "mismatch_rate_name_predicting": 0.022826614861583293,
 "mismatch_rate_other": 0.006696428571428571,
 "names": 640,
 "names_first_token_mismatch": 33,
 "first_mismatch_lp_gen": {
  "count": 33.0,
  "mean": -2.3183447556062178,
  "std": 0.5841677503516287,
  "min": -3.416288375854492,
  "25%": -2.62206768989563,
  "50%": -2.318875551223755,
  "75%": -2.091933250427246,
  "max": -0.8420356512069702
 },
 "first_mismatch_gap_upper": {
  "median": 2.2153088131528036,
  "max": 3.3829031631213278,
  "share_le_0p5": 0.030303030303030304,
  "share_le_1p0": 0.09090909090909091,
  "share_le_2p0": 0.2727272727272727
 },
 "names_affected_lower": 0.0515625,
 "names_affected_upper": 0.146875
}
```

## 1b name-feature frequency excluding the current paper

```
{
 "parity_incl_vs_stored": 1.0,
 "M_old_ge1": 0.16601307189542483,
 "H_old_ge1": 0.04227821795038317,
 "M_new_ge1": 0.05359477124183006,
 "H_new_ge1": 0.04227821795038317,
 "names_changed": 0.0034219448052976776,
 "M_changed": 0.1411764705882353,
 "H_changed": 0.0
}
```

| layer | probe | name old | name new | combined old | combined new | probe - comb old | probe - comb new | comb old - new | papers / pairs |
|---|---|---|---|---|---|---|---|---|---|
| L16 | 0.723 [0.696, 0.751] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.045 [+0.008, +0.081] | +0.087 [+0.048, +0.128] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L24 | 0.740 [0.715, 0.767] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.062 [+0.027, +0.094] | +0.104 [+0.067, +0.140] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L32 | 0.736 [0.708, 0.762] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.057 [+0.021, +0.090] | +0.100 [+0.063, +0.136] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L40 | 0.780 [0.750, 0.808] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.101 [+0.064, +0.135] | +0.143 [+0.106, +0.180] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L48 | 0.782 [0.754, 0.812] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.104 [+0.067, +0.139] | +0.146 [+0.108, +0.185] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L52 | 0.771 [0.742, 0.798] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.093 [+0.059, +0.127] | +0.135 [+0.100, +0.170] | +0.043 [+0.023, +0.064] | 518 / 3388 |
| L56 | 0.736 [0.706, 0.765] | 0.549 [0.509, 0.588] | 0.530 [0.499, 0.563] | 0.679 [0.645, 0.712] | 0.636 [0.603, 0.669] | +0.058 [+0.023, +0.092] | +0.100 [+0.063, +0.133] | +0.043 [+0.023, +0.064] | 518 / 3388 |

Position only: 0.632 [0.599, 0.666]; fame only: 0.548 [0.519, 0.576] (layer-independent).

## 1c (descriptive only: shard 0, replay confidence, raw scores, no fitting)

```
 layer  n_papers  n_pairs  n_M  probe  probe_lo  probe_hi  conf_lp_mean  conf_lp_mean_lo  conf_lp_mean_hi  conf_lp_first  conf_lp_first_lo  conf_lp_first_hi  conf_neg_entropy  conf_neg_entropy_lo  conf_neg_entropy_hi  comb_new  comb_new_lo  comb_new_hi  probe_minus_conf_lp_mean  pmc_lo  pmc_hi
    16        13       86   17  0.581     0.490     0.711         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.140  -0.333   0.126
    24        13       86   17  0.640     0.485     0.769         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.081  -0.266   0.156
    32        13       86   17  0.709     0.600     0.804         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.012  -0.229   0.290
    40        13       86   17  0.709     0.567     0.814         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.012  -0.133   0.149
    48        13       86   17  0.709     0.566     0.826         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.012  -0.169   0.184
    52        13       86   17  0.744     0.525     0.850         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                     0.023  -0.178   0.250
    56        13       86   17  0.709     0.558     0.819         0.721            0.452            0.913          0.651             0.357              0.86             0.651                0.367                0.858     0.651        0.354        0.857                    -0.012  -0.218   0.254
```

