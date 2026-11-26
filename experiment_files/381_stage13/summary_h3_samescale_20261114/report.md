# H3 same-scale comparison at the name positions — post hoc (strengthening 2), descriptive

Plan 2026-11-14b item 2. Name-position probe (addendum 11 A, Vpd per-donor version, surname first token) vs the logit lens and the public J-lens, with both lenses now ranking the gold token ONLY among the same 9,137 name token ids the probe ranks within (nlr = log10(1/rank)). Per paper: mean over the surname-first-token positions of all authors; spec = true − mean of the usable false titles (the probe's per-donor rule, same papers); target − control within citation bin (Stage 10 definition, ≥ 30 per cell); author-team cluster bootstrap 2,000 draws (archived teams). Probe, lenses and probe − lens use the same draws. Lens decoder: b16 = Stage 10 model.unembed (bf16 final norm + bf16 lm_head, bf16 logits, ties count as not greater) — main; f32 = the probe's own fp32 decoder (sensitivity). * = CI excludes 0.

## L32  (target + control papers kept: 4654)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.062 [+0.058, +0.067]* | +0.030 [+0.018, +0.042]* |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.020 [+0.016, +0.023]* | +0.005 [-0.004, +0.013] |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.020 [+0.016, +0.023]* | +0.004 [-0.005, +0.013] |
| public J-lens, full vocab (published) | full vocabulary | +0.038 [+0.032, +0.044]* | +0.005 [-0.010, +0.020] |
| logit lens, restricted (b16, main) | 9137 name ids | +0.016 [+0.013, +0.020]* | +0.015 [+0.007, +0.025]* |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.016 [+0.013, +0.020]* | +0.015 [+0.006, +0.025]* |
| logit lens, full vocab (published) | full vocabulary | +0.014 [+0.011, +0.018]* | +0.013 [+0.005, +0.023]* |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | +0.043 [+0.037, +0.048]* | +0.025 [+0.012, +0.038]* | 0.000 |
| probe − public J-lens, restricted (f32 probe decoder) | +0.043 [+0.037, +0.048]* | +0.026 [+0.012, +0.039]* | 0.000 |
| probe − logit lens, restricted (b16, main) | +0.046 [+0.041, +0.051]* | +0.014 [+0.001, +0.027]* | 0.018 |
| probe − logit lens, restricted (f32 probe decoder) | +0.046 [+0.041, +0.051]* | +0.014 [+0.001, +0.027]* | 0.017 |

## L40  (target + control papers kept: 4654)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.069 [+0.064, +0.074]* | +0.031 [+0.019, +0.044]* |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.034 [+0.029, +0.039]* | +0.010 [-0.000, +0.021] |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.034 [+0.029, +0.038]* | +0.010 [-0.000, +0.021] |
| public J-lens, full vocab (published) | full vocabulary | +0.048 [+0.042, +0.054]* | +0.014 [+0.000, +0.029]* |
| logit lens, restricted (b16, main) | 9137 name ids | +0.015 [+0.010, +0.019]* | +0.017 [+0.005, +0.028]* |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.015 [+0.010, +0.019]* | +0.017 [+0.005, +0.028]* |
| logit lens, full vocab (published) | full vocabulary | +0.010 [+0.005, +0.014]* | +0.013 [+0.002, +0.024]* |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | +0.035 [+0.030, +0.040]* | +0.021 [+0.008, +0.034]* | 0.002 |
| probe − public J-lens, restricted (f32 probe decoder) | +0.035 [+0.030, +0.041]* | +0.021 [+0.008, +0.034]* | 0.001 |
| probe − logit lens, restricted (b16, main) | +0.054 [+0.048, +0.060]* | +0.015 [-0.001, +0.030] | 0.032 |
| probe − logit lens, restricted (f32 probe decoder) | +0.054 [+0.048, +0.060]* | +0.015 [-0.001, +0.030] | 0.032 |

## L48  (target + control papers kept: 4654)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.103 [+0.097, +0.110]* | +0.053 [+0.038, +0.067]* |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.030 [+0.022, +0.037]* | -0.009 [-0.027, +0.009] |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.029 [+0.022, +0.037]* | -0.009 [-0.027, +0.009] |
| public J-lens, full vocab (published) | full vocabulary | +0.030 [+0.017, +0.043]* | -0.040 [-0.067, -0.011]* |
| logit lens, restricted (b16, main) | 9137 name ids | +0.021 [+0.016, +0.026]* | +0.021 [+0.009, +0.035]* |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.021 [+0.016, +0.026]* | +0.021 [+0.009, +0.034]* |
| logit lens, full vocab (published) | full vocabulary | +0.010 [+0.005, +0.014]* | +0.012 [+0.001, +0.023]* |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | +0.073 [+0.065, +0.083]* | +0.062 [+0.041, +0.081]* | 0.000 |
| probe − public J-lens, restricted (f32 probe decoder) | +0.074 [+0.065, +0.083]* | +0.062 [+0.042, +0.081]* | 0.000 |
| probe − logit lens, restricted (b16, main) | +0.082 [+0.075, +0.090]* | +0.031 [+0.013, +0.048]* | 0.001 |
| probe − logit lens, restricted (f32 probe decoder) | +0.082 [+0.075, +0.090]* | +0.032 [+0.014, +0.049]* | 0.000 |

## L52  (target + control papers kept: 4654)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.133 [+0.125, +0.140]* | +0.073 [+0.057, +0.089]* |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.075 [+0.066, +0.084]* | +0.020 [-0.000, +0.042] |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.075 [+0.065, +0.084]* | +0.021 [+0.001, +0.043]* |
| public J-lens, full vocab (published) | full vocabulary | +0.078 [+0.063, +0.092]* | -0.028 [-0.061, +0.006] |
| logit lens, restricted (b16, main) | 9137 name ids | +0.072 [+0.063, +0.080]* | +0.045 [+0.028, +0.063]* |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.071 [+0.063, +0.079]* | +0.044 [+0.027, +0.062]* |
| logit lens, full vocab (published) | full vocabulary | +0.061 [+0.054, +0.069]* | +0.039 [+0.023, +0.056]* |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | +0.057 [+0.049, +0.066]* | +0.053 [+0.032, +0.072]* | 0.000 |
| probe − public J-lens, restricted (f32 probe decoder) | +0.058 [+0.049, +0.067]* | +0.052 [+0.031, +0.071]* | 0.000 |
| probe − logit lens, restricted (b16, main) | +0.061 [+0.053, +0.070]* | +0.029 [+0.010, +0.046]* | 0.001 |
| probe − logit lens, restricted (f32 probe decoder) | +0.061 [+0.053, +0.070]* | +0.029 [+0.010, +0.047]* | 0.001 |

## L56  (target + control papers kept: 4654)

| readout | scale | spec | target − control |
|---|---|---|---|
| probe (Vpd) | 9137 name ids | +0.233 [+0.223, +0.243]* | +0.127 [+0.107, +0.145]* |
| public J-lens, restricted (b16, main) | 9137 name ids | +0.235 [+0.222, +0.248]* | +0.119 [+0.093, +0.147]* |
| public J-lens, restricted (f32 probe decoder) | 9137 name ids | +0.235 [+0.221, +0.247]* | +0.119 [+0.093, +0.148]* |
| public J-lens, full vocab (published) | full vocabulary | +0.270 [+0.252, +0.288]* | +0.081 [+0.041, +0.124]* |
| logit lens, restricted (b16, main) | 9137 name ids | +0.260 [+0.245, +0.274]* | +0.169 [+0.143, +0.197]* |
| logit lens, restricted (f32 probe decoder) | 9137 name ids | +0.259 [+0.244, +0.273]* | +0.169 [+0.142, +0.196]* |
| logit lens, full vocab (published) | full vocabulary | +0.283 [+0.267, +0.299]* | +0.180 [+0.150, +0.212]* |

| probe − lens (same draws) | spec diff | T − C diff | share of draws with T − C diff ≤ 0 |
|---|---|---|---|
| probe − public J-lens, restricted (b16, main) | -0.002 [-0.012, +0.008] | +0.008 [-0.016, +0.031] | 0.257 |
| probe − public J-lens, restricted (f32 probe decoder) | -0.002 [-0.012, +0.009] | +0.008 [-0.016, +0.031] | 0.260 |
| probe − logit lens, restricted (b16, main) | -0.027 [-0.038, -0.016]* | -0.042 [-0.066, -0.018]* | 1.000 |
| probe − logit lens, restricted (f32 probe decoder) | -0.026 [-0.037, -0.015]* | -0.042 [-0.066, -0.018]* | 1.000 |

## Parity / self-checks (WARN only)

- (1) full-vocab rank recomputed on the parity shard from the stored fp16 residual (b16 decoder) vs stored rank: jlens_public L32 0.8873 (WARN), jlens_public L40 0.9236 (WARN), jlens_public L48 0.9172 (WARN), jlens_public L52 0.8920 (WARN), jlens_public L56 0.8749 (WARN), logit L32 0.9076 (WARN), logit L40 0.9062 (WARN), logit L48 0.8888 (WARN), logit L52 0.8987 (WARN), logit L56 0.9115 (WARN) (logit: vs stored rank_logit_L; J-lens: vs Stage 10 raw jlens_public rank).
- (2) restricted rank ≤ stored full-vocab rank, every surname-first row, all conditions/layers/lenses: violations b16 5, f32 1907 (details parity_rows.csv).
- (3) published values reproduced (probe Vpd surname_first spec/T−C/CI/n, full-vocab lens spec/T−C/CI): max |diff| 9.89e-17 (OK); details parity3_published.csv.
- vocab_rows.npz lm_head rows vs HF bf16 lm_head: max |diff| 2.98e-08; J dtype torch.float16; published-function recomputation identical: True.

