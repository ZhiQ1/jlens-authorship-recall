# Addendum 9 (all-token probe): deviations and check notes

## 2026-11-05 22:45 EST: the 0.036 WARN in the permutation-control parity check (section 7 of e4b_alltok.md)

Check: the real-gold column recomputed by stage13_alltok_controls.py vs the per-paper spec of stage13_alltok_probe.py.
Finding: **floating-point, not a different ridge strength.**
- The ridge alpha chosen on fold 0 is identical in both runs for all 63 run x layer cells (e.g. alpha 1 for initial, given_first, surname_first, first_alltok, e4b_parity; 10 for given_cont, surname_cont).
- 5 of 7 runs (first_alltok, initial, given_first, surname_first, surname_cont) agree exactly (max |diff| 0) for every paper and layer.
- Differences occur only in e4b_parity (2-10 of 9,108 papers per layer; max 0.036 at L16, 0.029 at L44/L56) and given_cont (2-8 of 2,978 papers; max 0.0019). Mean difference per layer is at most 4e-6.
- Cause: a few gold tokens whose logits tie (or nearly tie) with other vocabulary rows; the rank (1 + number of strictly larger logits) flips by one between runs because the float32 matrix products were computed with a different thread count / summation order (controls job 16 threads, separate process). A one-step rank change for a single token moves a paper's mean log10(1/rank) by up to a few hundredths.
- Effect on reported numbers: none at the reported precision (all-paper means identical to 3 decimals).
Source: summary_alltok/probe/fit_*.json (alpha), logs/alltok_ctrl_11657421_*.log (alpha of the control runs), per-paper comparison of summary_alltok/controls vs summary_alltok/probe parquet files.
