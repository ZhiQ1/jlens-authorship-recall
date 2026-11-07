# Addendum 10: deviations recorded BEFORE the item-4 results were computed

## D1 (2026-11-06 ~00:30 EST, user decision): title-reuse exclusion for "E4b / all-token probe minus five false titles"
Reason: under the locked 5-donor rule (drop a paper if ANY of its five donor titles is a training-fold paper) 0 target + control papers remain (1 of 9,108 overall), so the primary version cannot be computed. Known at writing: only these counts (from the archived folds and false_titles.parquet) and the residual hard check (new false_0 residuals bit-identical to Stage 11). No probe score, contrast or control of item 4 had been computed.
New primary rule ("per-donor exclusion"): for each test paper, average the title-specific signal only over those false titles k whose donor paper is NOT in a training fold of the probe (dropped_k = False): spec_pd = probe(true) - mean over usable k of probe(false_k). A paper is kept if at least one false title is usable. Report the number of false titles used per paper (distribution) and the number of papers kept.
Sensitivity (side by side): the five-title mean with the original false_0-only exclusion (spec5 among papers with dropped_0 = False). The published false_0-only E4b (spec0, false_0 exclusion) stays the reproduction reference (hard check L40 +0.061 +-0.005).
Controls: the two permutation controls are computed with the same per-donor averaging (per-title control scores are stored for this).
Everything else in addendum 10 item 4 is unchanged.
