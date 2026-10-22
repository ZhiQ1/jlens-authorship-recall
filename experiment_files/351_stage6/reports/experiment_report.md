# Stage 6 · Full-author Conditional JMRR Pilot

**Completion:** 50/50; groups: {'A': 20, 'B': 20, 'C': 7, 'D': 3}; Stage4 verified reused: 20; new GPU measured: 30.

## Research question
How do per-paper full-author conditional JMRR trajectories vary by fixed A/B/C/D labels and citation bins?

## Frozen protocol
- Original group labels preserved (A=4110, B=2186, C=511, D=34 in source full cohort; no relabeling).
- Seven source layers: [16, 24, 32, 40, 48, 56, 62]; final model output excluded from integrated score.
- Each author: mean reciprocal rank over all forced gold-name tokens; each paper: mean over authors; integrated: mean across 7 layers.
- Log10 rank is averaged at the token level before author- and paper-level averaging.
- Teacher forcing supplies each true author prefix; this does not measure unaided retrieval.
- Stage5 title/author controls are a separate measurement, and were not implicitly applied to these full-name scores.

## Actual group estimates
| Group | Lens | Papers | Mean integrated JMRR | 95% paper-bootstrap CI |
|---|---|---:|---:|---|
| A | jlens | 20 | 0.084931 | [0.075009, 0.095752] |
| B | jlens | 20 | 0.068310 | [0.056929, 0.079632] |
| C | jlens | 7 | 0.105820 | [0.079544, 0.137856] |
| D | jlens | 3 | 0.050166 | [0.032803, 0.082428] |
| A | vanilla | 20 | 0.072809 | [0.062748, 0.084547] |
| B | vanilla | 20 | 0.056135 | [0.043561, 0.070468] |
| C | vanilla | 7 | 0.097412 | [0.069307, 0.128504] |
| D | vanilla | 3 | 0.029478 | [0.014644, 0.045304] |

## Matching

20 complete A/B pairs of 20 planned pairs. Pair-bootstrap summaries are in `summary/matched_ab_bootstrap.csv`.
The 50-paper pilot is exploratory; no causal inference, no A>B claim from an uncorrected Layer result.

## Known limitations
- Matched bin/year/field observational comparison still has unobserved confounders.
- Small within-bin sample sizes give imprecise estimates; empty group/bin combinations are reported as NA.
- Whole-name rank is conditional on name prefixes; any stronger claim requires negative controls.
- Stage4 reuse depends on exact prompt and token/rank parity; records failing checks are recomputed.
- All 100-incorrect-author and empirical-null controls belong to planned Stage7 (NOT RUN).

## Files
- `raw/pilot50_full_author.jsonl` — incremental per-paper results
- `raw/token_layer_scores.csv` — complete paper×author×token×layer scores
- `summary/paper_layer_trajectories.csv` — equal-author paper JMRR and log10 Rank
- `summary/paper_integrated.csv` — seven-layer paper score
- `summary/stage5_stage6_paper_join.csv` — aligned but distinct conditional and title-control measures
- `summary/group_bin_layer.csv` — A/B/C/D and citation-bin bootstrap summaries
- `summary/a_minus_b_bin_layer.csv` — unmatched differences
- `summary/matched_pair_layer.csv` and `matched_ab_bootstrap.csv` — matched comparisons
- `figures/*.png`, `figures/*.pdf` — observed trajectories; no invented control charts
