# Pre-registration addendum 25 — LOCKED 2026-11-22: can the late layers use the H3 probe direction? (probe-direction injection)

Status: LOCKED 2026-11-22 on the user's approval ("这些方案做细节敲定步骤定下来就直接排队写下，排队去跑", 2026-11-22). Written
before any real-model run. Same framework, sample and outcomes as addendum 21 (locked; verdict "Not supported").

## 1. Question
Addendum 21 amplified the paper's own title-specific vector and found no gain. Here we inject instead the direction the H3
name-position probe uses to read the paper's TRUE first author. **Caveat stated in advance:** this direction is derived from
the gold author, so it partly injects the answer. The confirmatory contrast is therefore gold-author direction − mismatched-
author direction (same norm): does the model write THIS paper's author more when given its probe direction than when given
another author's probe direction? Both are also compared with base.

## 2. Sample and framework
Addendum 16 B sample, groups A (600) and B (600), the addendum 21 freeze (`391_groups/raw/a21_freeze/freeze.parquet`: 30
shards, donor = another paper of the same field and citation bin with no shared surname). Prompt = Stage 10 F0 prompt, true
title. Injection at the prompt tail (the a21 aligned tail positions, prefill only) at the output of block l ∈ {48, 52}.

## 3. Directions
Probe map at layer l (l = 48, 52): the published name-position ridge (surname-first rows, true runs, all papers; standardised
X, alpha = tr(G)/d, target = stored L63 residual), Q_l = diag(1/sd) W diag(final-norm weight) U^T over the cohort surname-
first token vocabulary; q_l(t) = Q_l[:, t] = the linear part of the probe's logit for token t in residual coordinates
(computed on CPU from `381_stage13/raw/b2_npprobe/true` resid_L48 / resid_L52, `raw/allTok_L63`).
- **gold**: unit(q_l(t_gold)), t_gold = surname-first token of the paper's first author.
- **mis**: unit(q_l(t_donor)), t_donor = surname-first token of the a21 donor paper's first author (≠ t_gold; if equal, the
  donor's next author).
- **rand**: unit Gaussian direction (seed 25 + paper index).
Scale per tail position p: v(p) = β · ‖Δ_i(l, p)‖ · unit direction, Δ_i = h_true − mean_k h_false_k as in addendum 21
(recomputed in-run), β ∈ {1, 2, 4}: the same norms as addendum 21, so effects are comparable.
Papers whose t_gold is not in the probe vocabulary are excluded (reported).

## 4. Outcomes
Primary: group A open generation (a16 F0 settings), `any_full` and `first_sur` (first author's surname written).
Secondary: teacher-forced output log10(1/rank) of the true name tokens (and of the gold surname-first token separately),
fabrication, empty answers, group B, A − B.

## 5. Primary test and decision rule (fixed before data)
Family: 2 outcomes × 6 cells (l × β) = 12 tests, Holm over the 12, separately for S and G.
S_c = rate(gold) − rate(mis); G_c = rate(gold) − rate(base). Team bootstrap 2,000 (seed 25), paired over papers.
| reading | condition |
|---|---|
| Probe direction usable, paper-specific | some cell/outcome with S Holm CI > 0 and G Holm CI > 0 |
| Generic boost | no row 1, but some G Holm CI > 0 (gold no better than another author's direction) |
| Not usable | no G Holm CI > 0 and no harmful row |
| Harmful | G Holm CI < 0 in every β ≥ 2 cell of both outcomes |
| Borderline | row 1 met only with unadjusted CIs |
Guard: empty answers or mean fabricated names +0.20 over base in the row-1 cell → "with output damage".

## 6. Checks (WARN only)
β = 0 hook == base (exact ids); norms equal across gold / mis / rand per position (≤ 1e-3 relative); base vs stored a16 F0
any_full agreement ≥ 0.95; base TF vs Stage 10 exact-rank share ≥ 0.75.

## 7. Cost
As addendum 21: 1 base + 1 zero + 18 injected generations per paper, plus teacher forcing; measured on 1 shard;
expected ≈ 2.4 GPU-h on A100.

## 8. Limitations stated in advance
The gold direction contains answer information (hence the mismatched-author contrast); a linear probe direction may be
off-distribution for the residual stream; two layers, three β, prompt tail only, greedy decoding.
