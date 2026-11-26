# H3 same-scale comparison at the name positions — post hoc (strengthening 2), descriptive

**TINY TEST (shard 0 only): numbers meaningless.**
Plan 2026-11-14b item 2. Name-position probe (addendum 11 A, Vpd per-donor version, surname first token) vs the logit lens and the public J-lens, with both lenses now ranking the gold token ONLY among the same 9,137 name token ids the probe ranks within (nlr = log10(1/rank)). Per paper: mean over the surname-first-token positions of all authors; spec = true − mean of the usable false titles (the probe's per-donor rule, same papers); target − control within citation bin (Stage 10 definition, ≥ 30 per cell); author-team cluster bootstrap 2,000 draws (archived teams). Probe, lenses and probe − lens use the same draws. Lens decoder: b16 = Stage 10 model.unembed (bf16 final norm + bf16 lm_head, bf16 logits, ties count as not greater) — main; f32 = the probe's own fp32 decoder (sensitivity). * = CI excludes 0.

## L40  (target + control papers kept: 74)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.071 [+0.040, +0.104]* | +0.000 [+0.000, +0.000] |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.024 [-0.010, +0.055] | +0.000 [+0.000, +0.000] |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.023 [-0.011, +0.054] | +0.000 [+0.000, +0.000] |
| public J-lens, full vocab (published) | full vocabulary | +0.036 [+0.000, +0.072]* | +0.000 [+0.000, +0.000] |
| logit lens, restricted (b16, main) | 9137 name ids | +0.006 [-0.028, +0.042] | +0.000 [+0.000, +0.000] |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.006 [-0.027, +0.042] | +0.000 [+0.000, +0.000] |
| logit lens, full vocab (published) | full vocabulary | +0.002 [-0.031, +0.038] | +0.000 [+0.000, +0.000] |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | +0.047 [+0.008, +0.093]* | +0.000 [+0.000, +0.000] | 1.000 |
| probe − public J-lens, restricted (f32 probe decoder) | +0.048 [+0.009, +0.094]* | +0.000 [+0.000, +0.000] | 1.000 |
| probe − logit lens, restricted (b16, main) | +0.065 [+0.020, +0.110]* | +0.000 [+0.000, +0.000] | 1.000 |
| probe − logit lens, restricted (f32 probe decoder) | +0.065 [+0.020, +0.111]* | +0.000 [+0.000, +0.000] | 1.000 |

## Parity / self-checks (WARN only)

- (1) full-vocab rank recomputed on the parity shard from the stored fp16 residual (b16 decoder) vs stored rank: jlens_public L40 0.9250 (WARN), logit L40 0.9069 (WARN) (logit: vs stored rank_logit_L; J-lens: vs Stage 10 raw jlens_public rank).
- (2) restricted rank ≤ stored full-vocab rank, every surname-first row, all conditions/layers/lenses: violations b16 0, f32 0 (details parity_rows.csv).
- (3) published values reproduced (probe Vpd surname_first spec/T−C/CI/n, full-vocab lens spec/T−C/CI): max |diff| 4.58e+03 (WARN); details parity3_published.csv.
- vocab_rows.npz lm_head rows vs HF bf16 lm_head: max |diff| 2.98e-08; J dtype torch.float16; published-function recomputation identical: False.

