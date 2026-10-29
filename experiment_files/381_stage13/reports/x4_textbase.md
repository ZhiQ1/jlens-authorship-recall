# X4 text-only baseline (user request 2026-10-29, item 4)

1178 X4 papers. Text model: kNN (k=50) over the 9,108 cohort titles, excluding A's own author team; score = log10 p(A's first-author surname | title); D_text = own title - partner title. Units differ from Qwen's D, so compare win rates, standardised effects and correlations.

| measure | mean [team 95% CI] | sd | mean/sd | share self > partner |
|---|---|---|---|---|
| Qwen patchscope, title, L8 | +0.048 [+0.040, +0.058] | 0.155 | +0.31 | 0.615 |
| Qwen patchscope, title, L40 | +0.069 [+0.060, +0.078] | 0.155 | +0.45 | 0.677 |
| text kNN, TF-IDF | +0.007 [-0.013, +0.028] | 0.345 | +0.02 | 0.490 |
| text kNN, BERT | +0.006 [-0.025, +0.038] | 0.556 | +0.01 | 0.511 |

| Qwen | text | corr | share of Qwen mean explained by the text score (1 - intercept/mean) | Qwen mean where text gives no help (n) | Qwen mean where text helps |
|---|---|---|---|---|---|
| Qwen patchscope, title, L8 | text kNN, TF-IDF | +0.006 | 0.00 | +0.044 (601) | +0.053 |
| Qwen patchscope, title, L8 | text kNN, BERT | -0.040 | -0.00 | +0.057 (576) | +0.040 |
| Qwen patchscope, title, L40 | text kNN, TF-IDF | -0.002 | -0.00 | +0.069 (601) | +0.070 |
| Qwen patchscope, title, L40 | text kNN, BERT | -0.017 | -0.00 | +0.071 (576) | +0.068 |

| measure | target - control within citation bin |
|---|---|
| Qwen patchscope, title, L8 | +0.040 [+0.023, +0.058] |
| Qwen patchscope, title, L40 | +0.060 [+0.043, +0.077] |
| text kNN, TF-IDF | +0.003 [-0.036, +0.042] |
| text kNN, BERT | +0.019 [-0.045, +0.081] |
