# Addendum 12 item 2-4: E1 batch rounding noise

Written 2026-11-09 04:55 by `13_stage13/stage13_b2B_analyze.py e1noise`. Plan: `381_stage13/config/prereg_addendum12.json` (sha256 OK). Raw: `/scratch/zhang.zhiqi2/jlens/381_stage13/raw`.

Two original Stage 11 shards (rule: lowest-index shard with the highest target share, and with the highest control share): shard 0, shard 6. Original arms = 361_stage11.do_patch unchanged (true / false_0 batch 1, patched at 15 layers in one batch of 15). New: patched at L40 / L48 / L52 alone (batch 1); true and false_0 as 15 identical copies in one batch (element 0). The original unpatched runs were batch 1, so for them "original batch size" = batch 1 and the 15-copy batch is the comparison (stated deviation).

Hard check (original arms == stored raw/patch shard; rows identical, recovery per layer |diff| <= 0.005): shard 0: PASS (rank equality 1.0000, max |diff| 0.0e+00; 15 copies identical: true 1.000, false 1.000); shard 6: PASS (rank equality 1.0000, max |diff| 0.0e+00; 15 copies identical: true 1.000, false 1.000) -> **PASS**.

## Per name token: |delta log10(1/rank)|, batch 1 vs 15-element batch

| shard | arm | tokens | share equal | mean | median | p90 | p99 | max |
|---|---|---|---|---|---|---|---|---|
| 0 | true | 516 | 0.634 | 0.0114 | 0.0000 | 0.0320 | 0.1761 | 0.3979 |
| 0 | false_0 | 516 | 0.589 | 0.0111 | 0.0000 | 0.0300 | 0.1249 | 0.3010 |
| 0 | patch_L40 | 516 | 0.636 | 0.0087 | 0.0000 | 0.0236 | 0.0860 | 0.3010 |
| 0 | patch_L48 | 516 | 0.667 | 0.0087 | 0.0000 | 0.0235 | 0.1249 | 0.3010 |
| 0 | patch_L52 | 516 | 0.653 | 0.0093 | 0.0000 | 0.0227 | 0.1684 | 0.3010 |
| 6 | true | 903 | 0.721 | 0.0103 | 0.0000 | 0.0280 | 0.2209 | 0.3010 |
| 6 | false_0 | 903 | 0.591 | 0.0112 | 0.0000 | 0.0300 | 0.1249 | 0.3010 |
| 6 | patch_L40 | 903 | 0.614 | 0.0091 | 0.0000 | 0.0288 | 0.1046 | 0.3010 |
| 6 | patch_L48 | 903 | 0.713 | 0.0089 | 0.0000 | 0.0223 | 0.1249 | 0.3010 |
| 6 | patch_L52 | 903 | 0.750 | 0.0086 | 0.0000 | 0.0210 | 0.1761 | 0.3010 |

## Paper-level E1 recovery by batch size

b15 = original (patched in the 15-batch, true / false batch 1); b1 = all batch 1; b15 all = patched, true and false all in 15-batches. Per-paper: |patched b15 - patched b1| (paper means of log10(1/rank)); per-paper recovery |diff| on papers with |true - false| >= 0.1.

| shard | group | layer | papers | R b15 (orig) | R b1 | R b15 all | b15 - b1 | b15all - b1 | paper num mean / p90 / max abs diff | paper R median / p90 abs diff (n) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | all | L40 | 50 | +0.7077 | +0.6929 | +0.7045 | +0.0148 | +0.0116 | 0.0065 / 0.0108 / 0.0610 | 0.0189 / 0.0787 (30) |
| 0 | all | L48 | 50 | +1.0515 | +1.0642 | +1.0516 | -0.0128 | -0.0126 | 0.0057 / 0.0138 / 0.0259 | 0.0169 / 0.0823 (30) |
| 0 | all | L52 | 50 | +1.0642 | +1.0663 | +1.0645 | -0.0021 | -0.0018 | 0.0065 / 0.0151 / 0.0376 | 0.0162 / 0.0883 (30) |
| 0 | control | L40 | 50 | +0.7077 | +0.6929 | +0.7045 | +0.0148 | +0.0116 | 0.0065 / 0.0108 / 0.0610 | 0.0189 / 0.0787 (30) |
| 0 | control | L48 | 50 | +1.0515 | +1.0642 | +1.0516 | -0.0128 | -0.0126 | 0.0057 / 0.0138 / 0.0259 | 0.0169 / 0.0823 (30) |
| 0 | control | L52 | 50 | +1.0642 | +1.0663 | +1.0645 | -0.0021 | -0.0018 | 0.0065 / 0.0151 / 0.0376 | 0.0162 / 0.0883 (30) |
| 6 | all | L40 | 50 | +0.2809 | +0.2790 | +0.2766 | +0.0020 | -0.0024 | 0.0045 / 0.0111 / 0.0187 | 0.0073 / 0.0266 (42) |
| 6 | all | L48 | 50 | +0.8438 | +0.8506 | +0.8451 | -0.0068 | -0.0055 | 0.0066 / 0.0132 / 0.0525 | 0.0070 / 0.0381 (42) |
| 6 | all | L52 | 50 | +1.0090 | +1.0109 | +1.0120 | -0.0020 | +0.0010 | 0.0054 / 0.0136 / 0.0362 | 0.0048 / 0.0164 (42) |
| 6 | target | L40 | 50 | +0.2809 | +0.2790 | +0.2766 | +0.0020 | -0.0024 | 0.0045 / 0.0111 / 0.0187 | 0.0073 / 0.0266 (42) |
| 6 | target | L48 | 50 | +0.8438 | +0.8506 | +0.8451 | -0.0068 | -0.0055 | 0.0066 / 0.0132 / 0.0525 | 0.0070 / 0.0381 (42) |
| 6 | target | L52 | 50 | +1.0090 | +1.0109 | +1.0120 | -0.0020 | +0.0010 | 0.0054 / 0.0136 / 0.0362 | 0.0048 / 0.0164 (42) |

Noise floor (for tolerances): the largest |b15 - b1| group-level recovery difference above, and the token p99 above.

