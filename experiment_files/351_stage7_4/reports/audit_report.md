# Stage 7.4 — Cross-stage Measurement Validity Audit

CPU-only, read-only exploration over frozen Pilot50. All bootstrap CIs are paper-level (or pair-level for matched AB), 20,000 draws, percentile 95%, unadjusted. No causal claims.

## Main findings

Stage5 vs Stage7.3 L56 J-Lens same-paper Pearson r = 0.4453; Spearman rho = 0.4711. Both metrics use First-token but different contrasts, units and number of shuffled titles.

Integrated J-Lens minus Vanilla title advantage: +0.00221, 95% CI [-0.00753, +0.01241] over 50 papers. This is a **difference in title-specific advantage**, NOT J-Lens fidelity proof.

Matched 20-pair A-B difference of lens increment: -0.01387, 95% CI [-0.03320, +0.00358].

Bin 0-2 (6 papers) J-Lens L56 mean advantage +0.22412, 5/6 positive, 2/6 midrank percentile >=90%, 0/6 corrected empirical tail <=0.05. These six papers are NOT evidence of a population-wide floor.

## Caveats

* This cohort and L56 were inspected before Stage7.4. All conclusions exploratory; multiple comparisons and winner's curse apply.
* Stage5 has one crossed shuffled source; Stage7.3 has 20 metadata-matched sources and a 100-author win-rate outcome. Correlation can be modest without either being invalid.
* Matched shuffle titles are not exchangeable, so empirical tail fractions are reference fractions, not necessarily calibrated permutation p-values.
* Frozen Stage7.2 first-token pools have repeated token IDs; Gold Win Rate measures candidate token discrimination, NOT full-name identification.
* Source-author presence in false pool and lenient matched title tiers require sensitivity analysis.
* Paper sharing/authors/contexts create possible dependence; conventional bootstrap may understate uncertainty.

All derived CSVs and figures are in summary/ and figures/. Stage 5-7.3 inputs were read, never overwritten.
