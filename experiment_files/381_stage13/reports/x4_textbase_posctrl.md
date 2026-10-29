# X4 text-only baseline (user request 2026-10-29, item 4) -- POSITIVE CONTROL: own author team NOT excluded

1178 X4 papers. Text model: kNN (k=50) over the 9,108 cohort titles, excluding A's own author team; score = log10 p(A's first-author surname | title); D_text = own title - partner title. Units differ from Qwen's D, so compare win rates, standardised effects and correlations.

| measure | mean [team 95% CI] | sd | mean/sd | share self > partner |
|---|---|---|---|---|
| Qwen patchscope, title, L8 | +0.048 [+0.040, +0.058] | 0.155 | +0.31 | 0.615 |
| Qwen patchscope, title, L40 | +0.069 [+0.060, +0.078] | 0.155 | +0.45 | 0.677 |
| text kNN, TF-IDF | -0.025 [-0.055, +0.003] | 0.531 | -0.05 | 0.486 |
| text kNN, BERT | -0.159 [-0.213, -0.107] | 0.938 | -0.17 | 0.503 |

| Qwen | text | corr | share of Qwen mean explained by the text score (1 - intercept/mean) | Qwen mean where text gives no help (n) | Qwen mean where text helps |
|---|---|---|---|---|---|
| Qwen patchscope, title, L8 | text kNN, TF-IDF | +0.037 | -0.01 | +0.042 (605) | +0.055 |
| Qwen patchscope, title, L8 | text kNN, BERT | -0.061 | 0.03 | +0.057 (585) | +0.040 |
| Qwen patchscope, title, L40 | text kNN, TF-IDF | +0.028 | -0.00 | +0.067 (605) | +0.071 |
| Qwen patchscope, title, L40 | text kNN, BERT | -0.023 | 0.01 | +0.071 (585) | +0.068 |

| measure | target - control within citation bin |
|---|---|
| Qwen patchscope, title, L8 | +0.040 [+0.023, +0.058] |
| Qwen patchscope, title, L40 | +0.060 [+0.043, +0.077] |
| text kNN, TF-IDF | +0.008 [-0.053, +0.070] |
| text kNN, BERT | +0.026 [-0.082, +0.136] |
