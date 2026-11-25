# Addendum 33 (LOCKED 2026-11-23, sha256 7a28ae2d…) — plain explanation

**Question:** at the title position (L8), is the first author's surname signal specific to THIS paper, beyond (a) the topic,
(b) literal overlap and (c) what a text-only model reads from the same title? And is it larger for recognised papers?

**Design:** fresh sample, frozen before any run. It takes all target/control papers outside the Stage 11 sample that have all partners (6,674).
- 626 are excluded for literal overlap: surname in the title (11), surname token in the title (30), eponym (596).
- That leaves 6,048 primary papers: 4,577 target, 1,471 control.

Patchscope method: the state of the last title token is injected into "Paper: X / The first author of the paper is", and we score the true first author's surname-first token.
- D_topic = score from the paper's own state − score from a same-field, most similar title (all-mpnet; other author team, no shared surname).
- Team bootstrap with 2,000 draws; Holm correction over T1–T3.

**Results (surname_first, L8):**
| test | estimate | 95% CI | Holm CI | locked reading |
|---|---|---|---|---|
| T1 D_topic > 0 | +0.0457 | [+0.0353, +0.0559] | [+0.0329, +0.0583] | passes |
| T2 Qwen − BERT text model (standardised) | +0.045 (0.114 vs 0.069) | [+0.008, +0.082] | [+0.002, +0.087] | passes (narrowly) |
| T3 target − control of D_topic (within citation bins) | +0.0246 | [+0.0030, +0.0470] | same (last Holm rank) | passes |

**Verdicts (locked rule):**
- Paper-specific surname signal confirmed.
- Recognition-specific (T3 Holm CI > 0).

**Secondary (descriptive):**
- D vs a random same-field partner: +0.103 [0.092, 0.114]. Share remaining after the topic match: P = ΣD_topic/ΣD_random = 0.44 [0.36, 0.52]. So about half of the X4 surname signal is topic.
- BERT-topic partner: +0.067.
- Embedding-only (L0) source: +0.001 [−0.001, +0.004], so the title tokens alone (no context) give nothing.
- With the exclusions lifted: +0.044 (n = 6,674).
- All first-author tokens: D_topic +0.024, T−C +0.022 [0.013, 0.030].
- Year at L8: ≈ 0.
- Field at L8: D_topic −0.021, negative because the topic partner shares the field.

**Caveats:**
- The text-only baseline is weak. The BERT logistic regression's held-out log-likelihood is BELOW the frequency prior (gain −0.24 log10), as in the 2026-11-21 baseline. T2 beats a weak baseline, and its Holm lower bound is only +0.002.
- T3 is close to the pre-stated decision bound (we said T3 could only decide differences of about ≥ 0.02); its lower bound is +0.003.
- Single model; title source only; X4 asks for the first author by design.
- The protocol check reproduced the stored X4 scores exactly on 50 Stage 11 papers (exact share 1.0).
