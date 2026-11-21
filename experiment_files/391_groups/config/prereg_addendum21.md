# Pre-registration addendum 21 — LOCKED 2026-11-21: is the arrived information sufficient to say the author? (injection test)

Status: LOCKED 2026-11-21 (user: "赶紧跑实验" after reviewing the draft; defaults kept: meaning-only control secondary, "substantial" = G_c ≥ +0.05, layers L48/L52, β 1/2/4). Written before any real-model injection run.
After locking, this file is copied to `391_groups/config/prereg_addendum21.md` and its sha256 recorded in `addendum21_lock.json`.

## 1. Question

By ~L50 the title's paper-specific information has arrived at the post-title positions (E1/X6: R(L50) 0.929, R(L52) 0.995),
but the model writes no true author for recognised papers (group A, R0). The author name is written only by the late MLPs
(L57–L61, C29). **If the already-arrived paper-specific component is made stronger before the late layers, does the model
then write a true author more often — and only when it is this paper's own component?** A yes means the failure to say is at
least partly a *strength* (conversion-threshold) bottleneck; a no means more of the same information does not unlock the name.

The manipulation never adds the gold name's unembedding or a probe direction trained on the gold author (that would inject the
answer). It only amplifies a difference the model itself computed from the real title.

## 2. Sample

The addendum 16 B sample (`391_groups/config/prereg16_sample_B.parquet`, sha 117a9127…): groups **A (600, R0 × recognised)**
and **B (600, R0 × not recognised)**; C is not used. 24 shards of 50 papers (the a16 shard ids, C rows dropped).
Exclusions fixed now: aligned tail < 3 tokens; no eligible donor (§3). Expected exclusions ≈ 0.

## 3. Manipulation

Prompt = the Stage 10 F0 prompt `Who are the authors of the paper titled "{title}" ({year})?\nAuthors:` (true title).
Tail = the aligned post-title positions shared by the true and all five false-title prompts (Stage 11 rule: common suffix,
bounded by the title positions; m_i tokens, typically ` (YYYY)?\nAuthors:`).

For layer l ∈ {48, 52} (output of block l), per tail position p:

    Δ_i(l, p) = h_true,i(l, p) − mean_k h_false_k,i(l, p)        (k = 0..4, the Stage 10 matched false titles)

Injection: in the true-title forward, h(l, p) ← h(l, p) + β · v(l, p) at the m_i tail positions only (prompt prefill; generated
tokens are not touched), β ∈ {1, 2, 4}. Sources v:

| source | v(l, p) | role |
|---|---|---|
| **own** | Δ_i(l, p) | this paper's own title-specific component |
| **mismatched** (c1) | Δ_j(l, p) · ‖Δ_i(l, p)‖ / ‖Δ_j(l, p)‖ | donor j: another cohort paper, same field and citation bin, no shared surname with i, aligned tail ≥ m_i (last m_i positions); seed 21 |
| **random** (c3) | g(p) · ‖Δ_i(l, p)‖ / ‖g(p)‖, g ~ N(0, I) | norm-matched random direction; seed 21 + paper index |
| **meaning only** (c2, secondary) | Δ_fict,i = h_fict − mean_k h_false_k, same norm rule | only papers in the addendum 20 set (A 94, B 210); fict title from `a20v2_freeze` |
| base | — (β = 0) | the unmodified true-title run |

Per paper: 1 base + 2 layers × 3 β × 3 sources = 19 generations (+ 6 meaning-only for the overlap papers).

## 4. Outcomes

Primary: **open generation**, a16 F0 settings (greedy, max 80 new tokens, EOS stop, list cut by the a16 v2b rule, items split
by the a16 rule), scored by the a16 full-name matcher: `any_full` = at least one true author written in full.
All conditions of one paper are generated in **one batch with identical input ids** (no padding), so batch-shape rounding is
the same for every condition of a paper.
Secondary: `first_sur` (first author's surname), `any_sur`; fabrication `n_fab_full`; empty answer; teacher-forced
log10(1/rank) of every true name token at the output (F0, all authors, same injections).

## 5. Primary test and decision rule (fixed before any real-model data)

Group A, outcome `any_full`, six cells c = (l, β), l ∈ {48, 52}, β ∈ {1, 2, 4}.
Per cell: **S_c = rate(own) − rate(mismatched)** (paper-specific gain) and **G_c = rate(own) − rate(base)** (gain over no
injection). Paired over papers; CI = 95% percentile, 2,000 multinomial draws over author teams (a16 `team`), seed 21;
two-sided bootstrap p; **Holm over the 6 cells**, separately for S and G.

| reading | condition |
|---|---|
| **Supported: sufficiency, paper-specific** | some cell with S_c Holm CI > 0 **and** G_c Holm CI > 0. Size: "substantial" if that cell's G_c ≥ +0.05 (more than doubles the a16 F0 rate 0.04), else "small". |
| Generic boost, not paper-specific | no cell meets row 1, but some cell has G_c Holm CI > 0 (own helps, but no more than another paper's component) |
| Not supported | no cell with G_c Holm CI > 0, and row 5 does not apply |
| Borderline | a cell meets row 1 with unadjusted CIs but not with Holm-adjusted CIs (reported, verdict = the row it meets with Holm) |
| Harmful (reversed) | G_c Holm CI < 0 in every cell with β ≥ 2 and no cell positive: amplifying the arrived information breaks the answer |

Guard (reported with the verdict, does not change it): if the cell that meets row 1 raises the empty-answer rate or the mean
`n_fab_full` by more than 0.20 (absolute) over base, the verdict carries "with output damage".

## 6. Secondary (descriptive, no verdict)

1. Same S_c, G_c in group B, and A − B difference of G_c (prediction of the strength reading: A gains more, because its
   arrived signal is larger).
2. Own − random per cell; own − meaning-only on the addendum 20 overlap (does the real-title part matter beyond meaning?).
3. `first_sur`, `any_sur`; fabrication and empty rates per condition.
4. Teacher-forced output log10(1/rank) of the true name tokens: own − base, own − mismatched, per cell, A and B.
5. Dose: rate(own) over β = 0, 1, 2, 4 per layer.

## 7. Checks (WARN only, never stop; values and thresholds reported)

- base generations vs the stored a16 F0 generations (`raw/a16_B/gen_v2`): share of papers with the same `any_full` outcome
  ≥ 0.95 (batch composition differs from a16).
- Δ recompute: h_true at L63 last position reproduces the Stage 10 final L63 first-token rank of the first author for ≥ 0.75
  of papers (bf16 batch shapes; mean |Δ log10 rank| ≤ 0.05).
- β = 0 with the hook installed == base without the hook (exact token ids).
- ‖v‖ per position equal across own / mismatched / random within 1e-3 relative.

## 8. Cost and order

CPU precheck and tiny random-model test of the whole pipeline → 1-shard real-model trial (50 papers) → rest.
Estimate (a16 B measured 0.35 s per F0 generation at batch 16 on H200; 19 gens per paper in one batch):
generation 24,600 gens ≈ 2.4 GPU-h; Δ forwards (≈ 14,700 short prompts, recording L48/L52) ≈ 0.25 h;
teacher forcing (19 copies per author sequence) ≈ 0.2 h; model loading (≈ 6 jobs × 4 min) ≈ 0.4 h; 1-shard trial + parity
≈ 0.3 h. **Total ≈ 3.5 GPU-h (range 3–4.5)**, below the 5 GPU-h threshold. Jobs ≤ 45 min, save per shard, skip if done.

## 9. Limitations stated in advance

Single model; adding to the residual can push states off-distribution (hence the norm-matched mismatched and random
controls); only two layers and three β; injection only at the prompt tail (generated tokens not touched); the meaning-only
control covers only the addendum 20 overlap; greedy decoding only.
