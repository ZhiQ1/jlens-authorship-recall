# Stage 7.2 — Candidate Construction (CPU; no GPU)

50 frozen papers, 20/20/7/3 A/B/C/D. Gold is first-listed author. Every paper has 50 unique matched and 50 unique random incorrect **real author names** drawn from frozen 6,841-paper source.

## Matching tier interpretation

- 0: same field, same Qwen name-token count, year difference <=2
- 1: same field, same token count, year difference <=5
- 2: same field, same token count, any year
- 3: same token count, any field/year
- 4: same field, any token count, year difference <=5
- 5: same field, any token count/year
- 6: remaining real authors

Tier counts across all 2,500 matched negatives: {0: 2159, 1: 182, 2: 135, 3: 24}.

## First-token collision

By group (matched + random): {'A': 79, 'B': 62, 'C': 9, 'D': 6}. Retain ties; do not reselect candidates based on score. In Gold Win Rate, tied first tokens contribute 0.5, and the same-token collision is reported separately.

## Boundaries

The same-field check is inferred from source papers, not author identity resolution. Checking author-name strings is not an external authorship registry. Candidate matching is based on field, year, Qwen token count, but cannot guarantee equal pretrained name priors. Stage 7.2 only freezes candidates; no J-Lens measurement has been run.
