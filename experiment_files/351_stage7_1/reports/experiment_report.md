# Stage 7.1 — Token-position Decomposition (CPU Only)

- Stage6 raw: `/scratch/zhang.zhiqi2/jlens/351_stage6/raw/pilot50_full_author.jsonl` (SHA256 `89551cf92010e18d1ceace496421b6e3355be06dee9edf24b8e47896747a215a`)
- Matching: `/scratch/zhang.zhiqi2/jlens/351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv` (SHA256 `9ebfc7e27163020fd00881a96d59d226aecbedf6d5a9ae6af8ca50fc12521537`)
- Papers: 50, raw scored rows: 14580, matched pairs: 20
- Equal-weight Token→Author→Paper; 7-layer integrated; 10000 pair-bootstrap replicates (seed 35171).
- Historical Stage6 JMRR reconciliation: `{'rows_checked': 750, 'max_abs_difference': 1.1102230246251565e-16}`.

## Main matched effects

| Readout | Position | n paired | Integrated A−B | 95% bootstrap CI | Positive pairs |
|---|---|---:|---:|---|---:|
| jlens | first_jmrr | 20 | 0.001366 | [-0.011430, 0.014861] | 12 |
| jlens | continuation_jmrr | 20 | 0.020644 | [0.002232, 0.038503] | 17 |
| jlens | all_jmrr | 20 | 0.016620 | [0.002640, 0.029887] | 15 |
| vanilla | first_jmrr | 20 | 0.014693 | [-0.002449, 0.033563] | 12 |
| vanilla | continuation_jmrr | 20 | 0.016844 | [-0.002067, 0.033707] | 16 |
| vanilla | all_jmrr | 20 | 0.016674 | [0.001422, 0.030784] | 14 |

## L62 effects

| Readout | Position | n paired | A−B | 95% bootstrap CI | Positive pairs |
|---|---|---:|---:|---|---:|
| jlens | first_jmrr | 20 | 0.014112 | [-0.071572, 0.109842] | 12 |
| jlens | continuation_jmrr | 20 | 0.121454 | [0.043441, 0.197383] | 15 |
| jlens | all_jmrr | 20 | 0.096579 | [0.028582, 0.161619] | 17 |
| vanilla | first_jmrr | 20 | 0.100734 | [-0.018404, 0.235321] | 12 |
| vanilla | continuation_jmrr | 20 | 0.084787 | [-0.005352, 0.167944] | 15 |
| vanilla | all_jmrr | 20 | 0.090748 | [0.013590, 0.165925] | 13 |

## Interpretation boundaries

- First-token score is measured without any revealed tokens of the *current* author, but for later listed authors the surrounding prompt may still contain earlier author names if that is how Stage4/6 constructed it; inspect the frozen prompt protocol before making a truly unconditioned claim.
- Continuation scores condition on a revealed correct-name prefix. They do not establish free recall of the full author identity.
- A/B comparisons are observational; split and integrated layer results are exploratory.
- Multi-token and one-token authors differ: continuation JMRR excludes authors with no continuation; each paper records the eligible count.
- A large JMRR at L62 and positive A−B, if found, does not by itself prove factual title–author association. Stage 7.2 matched false-author and title-shuffle controls are needed.
- Bootstrap CIs are paper-pair resampling. Pair dependence through shared authors/candidate sources has not been corrected.

## Files

- `summary/layer_and_integrated_effects.csv`: full effects and bootstrap CIs
- `summary/matched_pair_position_differences.csv`: per-pair per-layer differences
- `summary/paper_layer_decomposition.csv`: per-paper all/first/continuation metrics
- `raw/author_token_position_scores.csv`: per-author metrics
- `figures/`: PNG/PDF trajectory figures
