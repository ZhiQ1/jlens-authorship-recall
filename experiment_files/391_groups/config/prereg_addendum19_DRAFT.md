# Addendum 19 — DRAFT, NOT LOCKED (2026-11-17): exposure threshold (bottleneck F)

Status: draft for the user; not locked, no sha256. No new experiment: the data already exist (391_groups/summary_exposure_20261114/, script ~/jlens_work/14_groups/exposure_20261114.py). This addendum only fixes the decision rule and the analysis before the ratio CI and the trend slope are computed.

## Known before locking (stated honestly)
The exploratory run of 2026-11-14 (report.md in the folder above) already gave: recognition 50% threshold 40 citations [36, 44]; recall (≥ 1 correct author written) 50% threshold 11,038 citations [8,172, 15,607]; the point ratio is therefore known (≈ 276); per-bin recognition, recall and target − control are known (pooled within-bin target − control +0.207 [0.196, 0.220]). Not yet computed: the bootstrap CI of the threshold ratio, and the trend slope of target − control across bins. Because the point values are known, results of this addendum are labelled "confirmatory analysis of already-seen data (post hoc lock)", not a blind confirmatory test.

## Data
- Cohort 9,108 papers, 13 Stage 10 citation bins (stratified sampling, 800 per bin, fewer at the top), as in summary_exposure_20261114.
- Recognition = mc_team_outcome_tight == strong (uncertain counted as not passed); recall = recall_level R1 or R2 (≥ 1 correct author written).
- Bootstrap: author-team cluster bootstrap, 2,000 draws, archived team ids folds_own9108_k5s13.npz, groups_core.Engine, seed 391 (same as the exploratory run).

## Main comparison
- For each outcome y ∈ {recognition, recall}: logistic regression y ~ log10(1 + citations) + (year − mean year), fit on all 9,108 papers. The 50% threshold c50 is the citation count at which the fitted probability is 0.5 at the mean year: log10(1 + c50) = −(β0) / β1.
- Main quantity: ratio ρ = c50(recall) / c50(recognition), also reported as log10 ρ = log10(1 + c50_recall) − log10(1 + c50_recog) (difference of thresholds on the log scale).
- CI: refit both models on each bootstrap draw (same draws for both outcomes) → percentile 95% CI of ρ (and of log10 ρ).
- Decision rule: if the 95% CI of ρ lies entirely above 1 → "writing needs more exposure than recognising" (confirmed); if it includes 1 → not shown. The size of ρ is reported as estimated; no fixed effect-size threshold.
- Sensitivity (descriptive): recognition excluding uncertain papers (n 7,046); thresholds within the observed citation range flagged as in the exploratory run.

## Secondary comparison
- Within-bin target − control (spec = true − mean of 5 false titles, final readout L63, log10(1/rank), all tokens; bins with ≥ 30 papers per group, as in the exploratory pooled estimate).
- Trend: weighted least-squares slope of the per-bin target − control on the bin's log10(1 + median citations), weights = 1 / variance of each bin estimate; CI from the same 2,000 team draws (recompute per-bin estimates and the slope on each draw).
- Rule: slope CI above 0 → "the recognised − not recognised gap grows with exposure"; includes 0 → "flat"; below 0 → stated.

## What will be reported
c50 for each outcome with CI; ρ and log10 ρ with CI; the trend slope with CI; per-bin table (unchanged from the exploratory run). Labels: confirmatory analysis of already-seen data; single model; bins are stratified samples, not population rates; recognition at the bottom bins includes the ~25% guess floor of the 4-order multiple-choice rule.

## Code
A new script (not yet written) 14_groups/prereg19_exposure_ratio.py will reuse exposure_20261114.py functions read-only, add the per-draw refits, and write 391_groups/summary_exposure_prereg19/. CPU only.
