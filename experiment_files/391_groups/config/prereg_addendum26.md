# Pre-registration addendum 26 — LOCKED 2026-11-22: does the question format at ":" interfere with the author signal downstream? (format flow after locking)

Status: LOCKED 2026-11-22 on the user's approval ("这些方案做细节敲定步骤定下来就直接排队写下，排队去跑", 2026-11-22). Written
before any real-model run. Depends on addendum 23 (H1 format-locking layer).

## 1. Question
Addendum 23 finds the layer X at which the answer format is fixed at the ":" position. After X, if the ":" state of the
authors question is replaced by the ":" state of the year / field question (same paper), does the author title-specific
signal (H2/H3 evidence) change, and does the year/field readout change? I.e. does H1's format carry or gate the paper
information downstream?

## 2. Definition of X (fixed now)
X = the format-locking layer reported by addendum 23's locked rule (earliest layer with retention K(l) ≥ 0.95, CI lower
bound ≥ 0.90), per task pair. If addendum 23 reports "never fully fixed at the colon", X = 48 (stated as such). Layers used:
{X, X + 4, X + 8} ∩ [X, 56] from the set {4, 8, 16, 24, 32, 40, 48, 52, 56}.

## 3. Sample
The addendum 23 sample (same papers, prompts and shards as its freeze; 3 questions: authors / year / field; the question
comes before the title, last token ":").

## 4. Manipulation and measures
(i) Authors prompt with true title (and with each of the 5 false titles), at layer l replace the last-position (":")
residual (block-l output) with the ":" residual of the year-question (or field-question) prompt of the same paper with the
same title; score every true-author name token (teacher forcing after "Authors:", Stage 10 scoring, final L63). Author
title-specific signal spec = S_true − mean_k S_false_k; Δspec(l) = spec_patched − spec_base.
(ii) Reverse: year / field prompt with the authors-question ":" state; year readout = log-probability of the true year
tokens, field readout = log-probability of the field label; Δ readout.

## 5. Primary test and decision rule (fixed before data)
Primary: Δspec at l = X (authors ← year and authors ← field, 2 tests, Holm), target and control pooled, team bootstrap 2,000
(seed 26). Also target − control of Δspec within citation bins (secondary).
| reading | condition |
|---|---|
| Format gates the author signal | Δspec Holm CI < 0 for at least one donor question (the author signal drops when the ":" carries another format) |
| Format independent of the author signal | Δspec Holm CI within ±0.02 for both (equivalence margin 0.02 log10-rank units) |
| Undecided | otherwise |
| Reversed | Δspec Holm CI > 0 (another format increases the author signal) |

## 6. Checks (WARN only)
Patch with the recipient's own state == base (exact); base spec vs stored Stage 10 spec (mean |Δ| ≤ 0.02).

## 7. Cost
Per paper: 3 layers × 2 donors × 6 titles teacher-forced forwards + base + reverse readouts; measured on 1 shard; expected
≤ 0.8 GPU-h.

## 8. Limitations stated in advance
Depends on addendum 23's X; ":" replacement only (other positions untouched); single model.
