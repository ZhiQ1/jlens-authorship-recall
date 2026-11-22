# Pre-registration addendum 24 — LOCKED 2026-11-22: which title words carry the real-title-only part? (rare-word vs common-word replacement)

Status: LOCKED 2026-11-22 on the user's approval ("这些方案做细节敲定步骤定下来就直接排队写下，排队去跑", 2026-11-22). Written
before any real-model run of these variants. Builds on addendum 20 (locked; φ_T 0.751, R̄_T +0.106).

## 1. Question
Addendum 20: a same-meaning fictitious title recovers 75% of the true − false gap; the real title adds R̄_T = +0.106. Which
words of the real title carry that real-title-only part: the rare words (proper nouns, acronyms, technical terms, person
names) or the common content words?

## 2. Sample
The addendum 20 set: 1,127 papers (566 target, 561 control), `391_groups/raw/a20v2_freeze/fict_titles.parquet`, same
Stage 11 shards (24). A paper enters the primary contrast only if its true title has ≥ 1 rare word AND ≥ 1 common content
word (rule below); the counts are reported. No Crossref check: the variants are perturbed real titles, not new titles.

## 3. Variants (built from the TRUE title, fixed rule, seed 24)
Words = maximal alphanumeric runs (hyphenated parts split); stopwords = a fixed English function-word list (in the code).
Document frequency df(w) = number of the 9,108 cohort titles containing w (lower-cased).
- **rare word**: not a stopword and (df ≤ 3, or an acronym: ≥ 2 upper-case letters / letters+digits, or capitalised and not
  the first word of the title).
- **common content word**: not a stopword, not rare, df ≥ 20.
- (a) **rare-replaced**: every rare word replaced by a rare word from another cohort title (same category: acronym ↔ acronym,
  capitalised ↔ capitalised, other ↔ other), with the same number of Qwen tokens for " w" where available (else ±1), not
  present in the paper's own title, drawn with seed 24.
- (b) **common-replaced**: the SAME NUMBER k of common content words as rare words replaced in (a) (k capped at the number
  of common words), chosen at random (seed 24), each replaced by another common content word of the same Qwen token length
  and df within ×0.5–×2, not present in the title. (No WordNet is available offline, so (b) is frequency-matched, not a
  synonym replacement; both variants change meaning — the contrast is which word class, at equal word counts, matters more.)
- (c) the addendum 20 fictitious title (existing scores).
Prompt = Stage 10 PROMPT with the variant title and the true year; context limit 512 (else excluded, reported).

## 4. Measures (exactly as addendum 20)
S_v = mean over all name tokens of all authors of log10(1/rank) at the final output (L63), per paper; S_true and F̄ (mean of
5 false titles) from the stored Stage 10 values (as in addendum 20). R_v = S_true − S_v; kept share K_v = Σ(S_v − F̄)/Σ(S_true − F̄).

## 5. Primary test and decision rule (fixed before data)
Target group, eligible papers: D = R̄_a − R̄_b (paired), team bootstrap 2,000 draws (seed 24), 95% percentile CI.
| reading | condition |
|---|---|
| Rare words carry more of the real-title part | CI of D entirely > 0 |
| Common words carry more | CI of D entirely < 0 |
| No difference between word classes | CI includes 0 |
Secondary (descriptive, no verdict): R̄_a, R̄_b, K_a, K_b per group; within-bin T − C of R_a and R_b; comparison with R_fict
(addendum 20) on the same papers; dose by k (1, 2, ≥ 3 replaced words).

## 6. Checks (WARN only)
Variant ≠ true title for 100% of eligible papers; prompt ids reproducible; true-title rescoring of shard 0 vs stored Stage 10
final L63 (exact-rank share ≥ 0.75, mean |Δlog10 rank| ≤ 0.05).

## 7. Cost
2 prompts × 1,127 papers, Stage 10 scoring (one forward per author): measured on 1 shard; expected ≈ 0.3 GPU-h.

## 8. Limitations stated in advance
Single model; frequency-matched (not synonym) replacement; rare-word class mixes names, acronyms and terms; S_true / F̄
from stored A100 runs vs S_v on the current GPU (as addendum 20).
