# Stage 7.3B/C empirical shuffled-title null

Contexts: 1000/1000; full papers 50/50; full A/B pairs 20/20.

This is **first-token** candidate discrimination, not full-author knowledge. Null contexts use the target paper year and original false-author pools.

## Seven-layer matched A−B title advantage (exploratory)

| Lens | Pool | A−B | 95% pair-bootstrap CI | n pairs |
|---|---|---:|---|---:|
| jlens | random | +0.01794 | [-0.02223,+0.06328] | 20 |
| jlens | matched | +0.01737 | [-0.02116,+0.06254] | 20 |
| jlens | combined | +0.01766 | [-0.02112,+0.06255] | 20 |
| vanilla | random | +0.02950 | [-0.01249,+0.07516] | 20 |
| vanilla | matched | +0.03356 | [-0.00638,+0.07675] | 20 |
| vanilla | combined | +0.03153 | [-0.00902,+0.07572] | 20 |

## Scientific limitations

- 20 metadata-optimized shuffled titles per paper are not exchangeable under a formal randomization test. Empirical tail fractions are **descriptive**, not calibrated p-values.
- 19.9% of frozen sources overlap at least one false-author candidate (as earlier audit); use per-paper no-source-overlap sensitivity.
- Multiple layers and pools have been examined; individual CIs are exploratory and unadjusted.
- Citation Bin 0–2 has only six pilot papers and cannot establish a population-wide accessibility floor.
- Do not report a complete or confirmatory result until all 1,000 contexts score successfully.
