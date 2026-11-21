# Pre-registration addendum 22 — FINAL DRAFT (not locked): surface → meaning → identity at the title position (invariance ladder + variance decomposition)

Status: FINAL DRAFT 2026-11-21 (revision 2, user decisions of 2026-11-21 applied), written before any new model run and
before Part B is computed. Not locked. On the user's confirmation, Parts A and B are locked together: copy to
`391_groups/config/prereg_addendum22.md`, record sha256 in `addendum22_lock.json`; Part B (CPU) runs immediately after
the lock, Part A (GPU) follows the usual CPU precheck → tiny model → 1 shard → rest.

## 0. Why (what earlier tests could not separate)

- M3 / X1 / X5 change the QUESTION, not the title. The question precedes the title (`381_stage13.py` TASKS, 9 prefix tokens
  each), so title-token states differ across questions, but only slightly: raw cosine of the same paper's last-title-token
  state under two questions is 0.9976 at L4, 0.9832 at L24 (`x1_similarity.md`), against ≈ 0.45 for two papers under the
  same question. X5 cross-question top-1 retrieval is 1.000 at every layer L4–L44 (`x5_retrieval.md`). M3 / X5 / X1 are
  therefore at the ceiling at the title position from L4 on (audit: `381_stage13/summary_explore_l4audit_20261121/`) and
  cannot separate meaning from identity. To separate surface, meaning and identity the TITLE TEXT must change in controlled
  ways while the question stays fixed (Part A), and title states must be explained by text vs non-text features (Part B).

## 1. Sample (Part A)

The 1,083 papers that have all three existing ingredients: Stage 11 sample (E1 infrastructure, false_0 run), X3 paraphrase +
lexical neighbour D (`381_stage13/raw/para_run`, 1,137 papers), addendum 20 fictitious title v3b (1,127 papers).
Target 554, control 529 (Stage 11 `group`). Exclusions fixed now: a variant whose tokenised title equals the original (case
variant on all-lowercase titles → whitespace variant, §2.1); an aligned tail < 3 tokens (Stage 11 rule).

## 2. Part A — invariance ladder (GPU)

### 2.1 Variants of the title (prompt = the Stage 10 F0 authors prompt `Who are the authors of the paper titled "{title}" ({year})?\nAuthors:`, true year)

| code | rewrite | surface | meaning | identity (this real paper) | source |
|---|---|---|---|---|---|
| `orig` | original title | — | — | — | Stage 10 |
| `case` | lower-case all words (if already lower-case: double the spaces between words) | changes (new tokens) | same | same | new, deterministic |
| `para` | Qwen paraphrase (X3, judged same meaning) | changes | same | same paper described | X3 `para_gen` |
| `shuf` | words shuffled (seed 22 + paper index; must differ from orig; first word not kept in place) | bag of words same | changes | — | new, deterministic |
| `fict` | same-meaning fictitious title, checked not to exist (Crossref) | changes | same | none (no such paper) | addendum 20 v3b |
| `lexD` | a different REAL paper's title with high word overlap (X3 lexical neighbour D, jaccard2-matched) | near | changes | other paper | X3 |

### 2.2 Patching (exactly the E1 / X6 procedure, `361_stage11.do_patch`, frozen code imported by path)

- **Receiving run:** the false_0 prompt of the paper (Stage 10 matched false title), one run per author context
  (prompt + that true author's name, teacher forcing), as in E1.
- **Donor run:** the same author context with the variant-v title in place of the false title (orig = the true-title run).
- **Copied positions:** at layer l, the residual stream (output of decoder block l) at ALL aligned post-title positions —
  the common token suffix of the donor and the receiving prompt, cut so that it never reaches into either title
  (Stage 11 freeze rule: suffix length = min(common suffix, len − 1 − last title position) in both prompts; ≥ 3 tokens),
  plus the teacher-forced name-prefix positions — is copied from the donor run into the receiving run. Nothing else is
  changed; one layer per patched element.
- **Scored:** every name token of every true author of THIS paper (the receiving paper), rank over the full vocabulary at
  the output (final L63), nlr = log10(1/rank); tokens averaged within paper.
- **Recovery (as X6):** R_v(l) = mean_S(nlr_patched,v(l) − nlr_false0) / mean_S(nlr_true − nlr_false0) over the papers S of a
  group (ratio of means; denominator from the stored Stage 10/11 true and false_0 runs of the same author contexts);
  R_orig(l) = the stored E1 R (recomputed on shard 0 as a check).
- **Layers:** L4, L8, L16, L24, L32, L40, L44, L48, L52, L56, L60 (11 layers; L4 added as the text-level reference).

State similarity (secondary): at the last title token and as the mean over title tokens of the donor runs,
s_v(l) = cos(h_orig, h_v) − cos(h_orig, h_false0), states centred on the layer mean over all papers.

### 2.3 Predicted curve shapes

| if layers ≥ l encode… | R_case | R_para | R_fict | R_shuf | R_lexD |
|---|---|---|---|---|---|
| surface (tokens / string) | low | low | low | high (same words) | high-ish (shared words) |
| meaning | high | high | high | low | low |
| identity of THIS paper (beyond meaning) | high | high or lower | lower than para, and lower in target than in control | low | low |

Identity is read only from the target − control contrast (papers the model recognises vs not), because meaning-level effects
are expected in both groups. L4 is reported for every curve as the text-level reference; no contrast is judged at L4.

### 2.4 Primary contrasts and decision rules (fixed before any data)

Middle-layer family F = {L24, L32, L40, L44, L48}. Team bootstrap, 2,000 multinomial draws over author teams, seed 22;
two-sided bootstrap p; Holm over the 5 layers of F, separately for each contrast. Target and control reported separately;
K1–K3 use all 1,083 papers.

| contrast | definition | supported if |
|---|---|---|
| K1 meaning > bag of words | Δ_M(l) = R_para(l) − R_shuf(l) | Holm CI > 0 at some l ∈ F |
| K2 surface robustness | Δ_S(l) = R_orig(l) − R_case(l) | "surface-robust from l" = first l ∈ F with Holm CI inside [−0.05, +0.05] |
| K3 meaning, not shared words | Δ_L(l) = R_para(l) − R_lexD(l) | Holm CI > 0 at some l ∈ F |
| K4 identity beyond meaning | Δ_I(l) = [R_orig − R_fict]_target(l) − [R_orig − R_fict]_control(l), within citation bins (weights n_t·n_c/(n_t+n_c)) | Holm CI > 0 at some l ∈ F |

| reading | condition |
|---|---|
| Meaning is encoded in the middle layers | K1 and K3 supported |
| Middle layers mostly surface | K1 not supported and R_shuf ≥ R_para at every l ∈ F (point estimates), K3 not supported |
| Identity beyond meaning (recognised papers only) | K4 supported |
| No identity beyond meaning | K4 Holm CI includes 0 at every l ∈ F |
| Reversed identity | K4 Holm CI < 0 at some l ∈ F (control loses more than target) |
| Borderline | a contrast supported only without Holm (reported; reading follows the Holm result) |

Guards (WARN only, never stop): `case` changes the token ids for ≥ 90% of papers; R_orig recomputed on shard 0 equals the
stored E1 R within 0.02 (bf16 batch shapes); the fict donor reproduces addendum 20 S4 rec_fict at L52 within 0.02.

### 2.5 Cost (estimate; measured in the tiny test and the 1-shard trial)

Per paper: 5 variant donor runs + 5 variants × 11 layers patched receiving runs, per author context. Addendum 20 (1 donor,
10 patch layers + scores, 1,127 papers) took 0.53 GPU-h on H200. Scaling: ≈ 5 × 0.48 ≈ 2.4 H200-h ≈ 3.2 A100-h, + loading /
parity 0.5 h → **≈ 3.2 GPU-h (range 2.5–4.5)**, below 5 GPU-h. Jobs ≤ 45 min, save per shard, skip if done.

## 3. Part B — variance decomposition on existing caches (CPU only)

### 3.1 States

`381_stage13/raw/task/shard_*.npz` (cache `summary_m3/resid_cache.f16`): 9,108 papers × 3 questions × 15 layers (4, 8, 16,
24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63) × {last title token, colon}, fp16 5,120-dim. **Input: the AUTHORS question
only, last title token, one row per paper** (never 9,108 × 3 rows). Choice: the authors prompt is the prompt of every other
analysis in this study; the three question versions of a paper's title state are nearly identical (raw cosine 0.998 at L4,
0.983 at L24), so averaging them would add almost no information while mixing in question-specific shifts; treating them as
separate rows would triple-count papers. Layers analysed: L4, L8, L16, L24, L32, L40, L48 (L4 = text-level reference).

### 3.2 Feature groups

- **Surface S:** TF-IDF of word unigrams+bigrams and character 3–5-grams of the title, reduced to 256 dims by SVD fitted on
  training folds only.
- **Meaning M (two separate decompositions, both reported):**
  - M_bert = `bert-base-uncased` mean-pooled title embedding (pretraining data: BooksCorpus + English Wikipedia; no paper-pair
    training) — PRIMARY for the surface / meaning split.
  - M_mpnet = `sentence-transformers/all-mpnet-base-v2` (fine-tuned on > 1 B pairs incl. S2ORC citation / title-abstract pairs
    and SPECTER pairs, so it may encode paper identity) — SECONDARY; conservative for identity (it can absorb identity, which
    lowers the identity group's unique R²).
  - A third model with training data confirmed free of scholarly citation/title pairs: none is available offline under
    HF_HOME (present: bert-base-uncased, all-mpnet-base-v2, cross-encoder/nli-deberta-v3-large — a cross-encoder, and its
    DeBERTa-v3 pretraining corpus is not documented as excluding scholarly text), so no third model is added; nothing is
    downloaded.
- **Identity I (only what the title text cannot predict):**
  - year, log(1 + citations), field (one-hot) — each replaced by its out-of-fold residual after a ridge regression on S ∪ M
    (cross-fitted with the same team folds; the same M as the decomposition it enters);
  - author features: the paper's author names (all authors, "First Last; …" string) encoded with the same text-only model as
    M (mean-pooled), then residualised on S ∪ M out of fold — only the part of the author-name embedding the title text
    cannot predict is kept;
  - excluded: recognition / recall labels (they define target / control: circular), team ids, any Qwen output.

### 3.3 Model and quantities

Target y = the last-title-token state at layer l, projected on its top 256 PCs (PCA fitted on training folds; the variance
share covered is reported). Ridge, alpha by inner CV on training folds; 5 outer folds BY AUTHOR TEAM (stage13_cpu.group_folds:
papers sharing any author are in one fold; no paper in two folds). Out-of-fold R², variance-weighted over the 256 targets.
unique R²(G) = R²(S ∪ M ∪ I) − R²(full model without G), for G ∈ {S, M, I}. Reported per layer for all papers, target,
control and target − control (one model fitted on all papers per fold; R² evaluated per group on held-out papers), separately
for the BERT and the MPNet decompositions. CI: team bootstrap over held-out papers, 2,000 draws, seed 22.

### 3.4 Decision rules (fixed before computing; analysis of already stored states — the quantities have not been computed)

Layer family B = {L8, L16, L24, L32, L40, L48}; Holm over the 6 layers, per contrast.

| contrast | supported if |
|---|---|
| D1 meaning beyond surface | unique R²(M_bert) Holm CI > 0 at some l ∈ B (BERT primary; MPNet reported) |
| D2 identity beyond text | unique R²(I) Holm CI > 0 at some l ∈ B in the BERT decomposition **and** in the MPNet decomposition |
| D3 identity larger for recognised papers | [unique R²(I)]_target − [unique R²(I)]_control Holm CI > 0 at some l, in BOTH decompositions |
| reversed | D3 Holm CI < 0 at some l in either decomposition |
| borderline | D2 or D3 met with BERT but not with MPNet, or only without Holm (reported; not counted as supported) |

Expected cost: CPU only, ≈ 30–60 min on `short` (9,108 × 256 targets × 7 layers × 2 decompositions; features ≤ 2,100 dims).

## 4. Limitations stated in advance

Single model; one variant of each kind per paper; paraphrases and fictitious titles are generated by the model under study;
the lexical neighbour is a real paper and also changes identity; R is a ratio of means (denominator effects as in E1);
the meaning features depend on the embedding model (hence two models and the conservative rule); author-name embeddings are
a coarse identity proxy; Part B uses states that earlier analyses already used (the quantities here have not been computed).
