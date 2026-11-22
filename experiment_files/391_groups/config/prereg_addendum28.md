# Pre-registration addendum 28 — LOCKED 2026-11-22: X4 with topic-matched partners (TODO #6)

Status: LOCKED 2026-11-22 (user approval 2026-11-22: "锁定并提交 #9、#3、#6、#11"). Written before any real-model run of this design.
Code: ~/jlens_work/19_todo/a28_x4topic.py (freeze / work / tiny / analyze). Frozen code imported by path, never edited
(13_stage13/stage13_b2_ps_gpu.py: targets, tok_scores, first_author_roles; 381_stage13.py: build, ps_answers, PS_LAYERS, Ctx).

## Question
How much of X4's L8 surname signal (C21; exploratory source check 2026-11-21: literal overlap ≈ 0, Qwen − BERT +0.104) is a
topic prior, i.e. would also be produced by the state of another paper on the same topic?

## Sample and partners (frozen: 391_groups/raw/a28_freeze/pairs.parquet, freeze.json)
The 1,178 Stage 11 sample papers that have an X4 partner (589 target, 589 control; 24 shards). Per paper A:
- partner (published X4 partner, config/pairs.parquet): same field, same title token count, no shared surname (mean title cosine
  bert-base 0.22, all-mpnet 0.10);
- topic_mpnet (primary): same field, nearest title under all-mpnet-base-v2, not A's author team, no shared surname (mean cos 0.53);
- topic_bert (sensitivity): the same under bert-base-uncased mean-pooled (mean cos 0.63).
Partners frozen from 381_stage13/summary_explore_x4_source_20261121/partners.csv (rule above, computed 2026-11-21).

## Measurement (published X4 title source)
Source = last title token of the X4 authors prompt (no year) of A / partner / topic partners; injected (block-output replacement)
at the X placeholder of the three PS_TARGETS prompts at the 7 PS_LAYERS (8, 16, 24, 32, 40, 48, 56) in one forward of batch 7;
score = per-token log10(1/rank) of A's answer tokens (year; the first author's Stage 10 name tokens with roles; field).
D_s(l) = paper mean of [score(A's answer | A's state) − score(A's answer | source s)], per answer: first author (all tokens),
surname_first tokens, year, field.

## Primary contrast and rule (team bootstrap 2,000 over author teams, seed 27)
P = Σ D_topic_mpnet / Σ D_partner for surname_first at L8 (ratio of sums; CI = percentile of the per-draw ratio).
| reading | condition |
|---|---|
| mostly paper-specific | P lower CI ≥ 0.7 |
| mostly topic prior | P upper CI ≤ 0.3 |
| mixed | otherwise; P reported with CI |
| reversed | D_topic_mpnet(surname_first, L8) CI entirely < 0 |
Holm over the 7 layers for "D_topic_mpnet > 0" (surname_first), reported.

## Secondary (descriptive)
P with topic_bert; D_s for first author / year / field at all layers; target − control of D_partner and D_topic_mpnet within citation
bins (Stage 10 weights n_t·n_c/(n_t+n_c), bins with ≥ 3 per group).

## Checks (WARN only)
self and partner title-source per-token scores vs the stored raw/b2_pscope shard (same protocol): exact share ≥ 0.75 and mean
|Δ| ≤ 0.05.

## Cost and order
CPU freeze + tiny random-model test (done) → 1 real-model shard (A100-80GB) → rest + gate (full shard list from freeze.json) →
analysis → 391_groups/summary_a28/. Estimate ≈ 0.5 GPU-h (4 sources × 3 targets × 7 layers per paper).

## Limitations stated in advance
Single model; topic partners are the nearest titles under two text models (topic similarity is approximate); X4 asks for the
first author by design; title source only.
