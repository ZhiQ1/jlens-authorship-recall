# X4 stronger text-only baseline (supervised; user request 2026-10-29)

Logistic regression from the title text to the first author's Qwen name tokens (first given-name token, first surname token), 5 folds by author team.

## Positive control: does the text model beat the frequency prior on held-out papers?

| features | role | C | papers | mean log10 p, model | mean log10 p, prior | gain | share of papers where model > prior |
|---|---|---|---|---|---|---|---|
| bert | given_first | 0.03 | 2442 | -2.950 | -2.974 | +0.025 | 0.552 |
| bert | surname_first | 0.03 | 9108 | -3.290 | -3.127 | -0.163 | 0.470 |
| tfidf_svd | given_first | 0.03 | 2442 | -2.883 | -2.974 | +0.091 | 0.537 |
| tfidf_svd | surname_first | 0.03 | 9108 | -3.231 | -3.127 | -0.104 | 0.455 |

## X4 papers: own title vs partner title (D, log10 p units for the text model)

| measure | mean [team 95% CI] | mean/sd | share self > partner | corr with Qwen D(L8) | Qwen D(L8) where text gives no help |
|---|---|---|---|---|---|
| Qwen patchscope L8 | +0.048 [+0.039, +0.057] | +0.31 | 0.615 | - | - |
| Qwen patchscope L40 | +0.069 [+0.061, +0.078] | +0.45 | 0.677 | - | - |
| text LR, BERT | +0.048 [+0.025, +0.072] | +0.12 | 0.559 | +0.003 | +0.049 (n=519) |
| text LR, TF-IDF+SVD | +0.013 [-0.006, +0.034] | +0.04 | 0.498 | +0.005 | +0.047 (n=591) |

Regression of Qwen D(L8) on Dt2_bert: slope +0.001, intercept +0.048 -> share of the Qwen mean explained by the text score 0.00

Regression of Qwen D(L8) on Dt2_tfidf_svd: slope +0.002, intercept +0.048 -> share of the Qwen mean explained by the text score 0.00
