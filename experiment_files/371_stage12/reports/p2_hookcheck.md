# Stage 12 P2 hook check (U40) - --real - shard 0

Created 2026-10-31T07:09:47. Script `12_stage12/stage12_p2_hookcheck.py` (imports 371_stage12.py unchanged). 50 papers, 117 author contexts, 516 name tokens. **Status: WARN** (WARN = a threshold missed; recorded, nothing stopped).

## Design

All component patches use the P2 hook body (forward hook on `self_attn` / `mlp`, writes the true run's output on the aligned tail of one batch element).
- `full_true`: attention + MLP outputs of every layer 0-63 replaced by the true run's on the tail. The tail tokens are identical, so the final hidden state at the scored positions must equal the true run's bit for bit; recovery must be 1 ("完全恢复").
- `r62c63_true`: block-62 residual output on the tail (Stage 11 residual patch) + attention and MLP of layer 63 (P2 hooks). Final residual = h62 + attn63 + mlp63 of the true run: same exact expectation. Replacing only the L63 components (`c63_true`) cannot be exact, because the residual from L62 still carries the false title.
- `full_false` (negative control): every layer's components replaced by the false run's own (from a batch-1 false run): must equal that run exactly and the false baseline up to batch noise; recovery 0.
- `attn56_true`, `mlp56_true`, `none`: reproduce the stored P2 columns of this shard.
- recovery = mean(patched - none) / mean(true - none); nlr = log10(1/rank) of the gold token at the model output; lp = gold-token log-prob.

Denominator (mean true - none): nlr 0.1528, log-prob 0.6207.

## Per element

| element | recovery nlr (pooled / paper means) | recovery log-prob | max abs nlr - true | max abs logit - true | max abs logit - false batch-1 | rank = true |
|---|---|---|---|---|---|---|
| none | 0.0000 / 0.0000 | 0.0000 | 2.009 | 17.72 | 0.6406 | 0.287 |
| full_true | 1.0000 / 1.0000 | 1.0000 | 0 | 0 | 17.84 | 1.000 |
| r62c63_true | 1.0000 / 1.0000 | 1.0000 | 0 | 0 | 17.84 | 1.000 |
| full_false | -0.0118 / -0.0201 | -0.0032 | 2.009 | 17.84 | 0 | 0.279 |
| r62_true | 1.0013 / 0.9940 | 0.9939 | 0.2218 | 1.562 | 17.88 | 0.700 |
| attn63_true | 0.0081 / 0.0032 | 0.0468 | 1.968 | 18.16 | 4.344 | 0.264 |
| mlp63_true | 0.0307 / 0.0003 | -0.0419 | 1.648 | 18.06 | 14.38 | 0.266 |
| c63_true | 0.0386 / 0.0018 | -0.0339 | 1.792 | 18.55 | 14.72 | 0.264 |
| attn56_true | 0.1801 / 0.2099 | 0.1341 | 1.968 | 17.61 | 3.562 | 0.281 |
| mlp56_true | 0.3396 / 0.2972 | 0.3897 | 1.889 | 17.97 | 12.05 | 0.291 |

## Checks

| check | value | threshold | status |
|---|---|---|---|
| full_true: recovery nlr (pooled) | 1 | |x-1|<=0.01 | PASS |
| full_true: recovery gold log-prob (pooled) | 1 | |x-1|<=0.01 | PASS |
| full_true: max |nlr - true| | 0 | <=0.05 | PASS |
| full_true: max |logit - true| (whole vocab) | 0 | <=1.0 (4 bf16 ulps at |logit| 32-64) | PASS |
| full_true: max |final residual - true| (tail) | 0 | ==0 (bitwise) | PASS |
| r62c63_true: recovery nlr (pooled) | 1 | |x-1|<=0.01 | PASS |
| r62c63_true: recovery gold log-prob (pooled) | 1 | |x-1|<=0.01 | PASS |
| r62c63_true: max |nlr - true| | 0 | <=0.05 | PASS |
| r62c63_true: max |logit - true| (whole vocab) | 0 | <=1.0 (4 bf16 ulps at |logit| 32-64) | PASS |
| r62c63_true: max |final residual - true| (tail) | 0 | ==0 (bitwise) | PASS |
| full_false: recovery nlr vs none (pooled) | -0.01183 | |x|<=0.01 | WARN |
| full_false: max |logit - false batch-1 run| | 0 | <=1.0 | PASS |
| full_false: max |final residual - false batch-1| (tail) | 0 | ==0 (bitwise) | PASS |
| none (batched) vs false batch-1: max |logit| | 0.6406 | <=1.0 (batch-size noise) | PASS |
| every hook fired exactly once per forward | [1, 1] | min=max=1 | PASS |
| c63_true (L63 components only) differs from true (sanity: not exact) | 18.55 | >0 | PASS |
| parity with stored P2 shard (rank_true equal fraction) | 1 | >=0.9 | PASS |
| parity with stored P2: none mean |dnlr| | 0.008836 | <=0.05 (bf16 batch noise) | PASS |
| parity with stored P2: attn56 mean |dnlr| | 0.009005 | <=0.05 (bf16 batch noise) | PASS |
| parity with stored P2: mlp56 mean |dnlr| | 0.00941 | <=0.05 (bf16 batch noise) | PASS |

Hooks: {'registered_per_forward': 264, 'calls_min': 1, 'calls_max': 1, 'total_calls': 30888, 'expected_total': 30888}

Final residual max abs diff on the tail: {"dres_full_true_vs_true": 0.0, "dres_r62c63_true_vs_true": 0.0, "dres_r62_true_vs_true": 284.0, "dres_c63_true_vs_true": 1760.0, "dres_none_vs_true": 3092.0, "dres_full_false_vs_false1": 0.0, "dres_none_vs_false1": 112.0}

Parity with stored `raw/patch_comp/shard_000.npz`: {"rows_matched": 516, "rows": 516, "rank_true_equal": 1.0, "none_rank_equal": 0.624031007751938, "none_mean_abs_dnlr": 0.008835571272808712, "attn56_rank_equal": 0.624031007751938, "attn56_mean_abs_dnlr": 0.009004696346929086, "mlp56_rank_equal": 0.6375968992248062, "mlp56_mean_abs_dnlr": 0.009409543755352771}
