# Pre-registration addendum 31 — LOCKED 2026-11-22: direct logit attribution and per-paper late trajectories (H6 subgroup check, C29)

Status: LOCKED 2026-11-22 under the standing rule (new GPU experiment ≤ 5 GPU-h, user informed 2026-11-22). Written before any data of this design. Code: ~/jlens_work/24_gpubatch/a31_dla.py.

## 1. Question
Averages show the true author's rank rising steadily to the output (no late suppression; exploratory 2026-11-22). The user's point: an average can hide a subgroup of papers whose true-name rank rises and then falls in the last layers (cf. "From Early Encoding to Late Suppression", arXiv 2604.00778). (a) How many papers show such a rise-then-fall, and is it more frequent for recognised (target) papers? (b) Which components drive any fall? (c) Consistency with C29 (late MLPs write the name).

## 2. Sample
Stage 11 sample (361_stage11/config/sample.parquet): 1,186 papers, 593 target / 593 control, 24 shards. All authors, all name tokens; TRUE Stage 10 prompt + teacher-forced author name (Stage 10 format).

## 3. Measurements (Qwen3-32B, bf16)
At each name-token position: final rank of the true token t; logit-lens rank of t at L40–L62 (the model's final RMSNorm + lm_head on the block output); for every layer 0–63, the direct contribution of the attention output and of the MLP output to the final logit of t and to the margin logit(t) − logit(c*), c* = top competitor at the output: DLA = r · ⟨component, g ⊙ W_U[t] (− W_U[c*])⟩, r = rsqrt(mean(h63²) + ε) (exact linearisation of the final RMSNorm for fixed r).

## 4. Primary quantity and rule (fixed before data)
Token set (primary): the first author's surname-first token (role surname_first, author 0); secondary: all name tokens (paper mean).
y_l = log10(1/rank_l); l = 56…62 logit lens, l = 63 the model output. **Rise-then-fall (RTF)** for a token: max_{57≤l≤62} y_l − y_56 ≥ 0.301 AND max_{57≤l≤62} y_l − y_63 ≥ 0.301 (the rank first improves at least 2× after L56 and then worsens at least 2× by the output). Paper value = share of its tokens with RTF (primary: 0/1).
Shares in target and control (team-bootstrap CIs, 2,000 draws, seed 31, teams = archived author-team ids), and T − C within citation bins (weights n_t n_c / (n_t + n_c)).

| Reading | Condition |
|---|---|
| Late-suppression subgroup specific to recognised papers | target share ≥ 0.10, its CI lower bound > 0.05, and T − C CI > 0 |
| Late-suppression subgroup present, not specific | target share CI lower bound > 0.05, T − C CI includes 0 |
| Small / absent | target share CI lower bound ≤ 0.05 |
| Reversed | T − C CI < 0 |

## 5. Secondary (descriptive)
Components of the fall: for primary RTF tokens, sums over layers after the peak to L63 of attention vs MLP DLA (margin). Per-layer DLA means by group (L40–L63). C29 consistency: per paper Σ_{L57–L61}(MLP − attention) DLA on the logit, mean with team CI (expected > 0). All-token RTF shares.

## 6. Checks (WARN only)
Exactness: Σ of all component DLAs (embedding + 64 × (attention + MLP)) vs the actual final logit, relative error ≤ 2% for ≥ 99% of tokens; final ranks vs stored Stage 10 L63 ranks equal for ≥ 0.75 (bf16 batch shapes).

## 7. Cost
≈ 0.2–0.4 GPU-h (one hooked forward per author). Tiny random-model test → shard 0 trial → rest under a CPU gate over all 24 shards.

## 8. Limitations
Single model; logit lens is one readout of intermediate layers (the J-lens version is not run here); DLA is a linearisation for fixed r; teacher forcing, not free generation.
