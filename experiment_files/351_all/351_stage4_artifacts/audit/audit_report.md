# Stage 4 Result Audit

Input: /scratch/zhang.zhiqi2/jlens/351_all/351_stage4_artifacts/summary/paper_metrics.csv
Papers: 20 (A=8, B=8, C=3, D=1); paper/mode/layer rows: 300; raw author skips: 0.

## First-listed first-token rank & outlier check
|Layer|Mean J-Lens|Median|Largest-paper share|Leave-top-one-out mean|
|---|---:|---:|---:|---:|
|L16|0.000221015|7.14959e-05|0.325979|0.000156809|
|L24|4.56861e-05|3.0261e-05|0.25223|3.59607e-05|
|L32|0.000219249|6.07938e-05|0.552181|0.000103351|
|L40|0.00144154|0.001291|0.116785|0.0013402|
|L48|0.00133323|0.000886814|0.180302|0.00115037|
|L56|0.00703961|0.000920041|0.710267|0.00214696|
|L62|0.0559234|0.0244898|0.298027|0.0413229|

The largest-paper share diagnoses dominance by an extreme rank. No data were dropped.

## A/B descriptive comparison (NOT MATCHED)
|Layer|A mean|B mean|A-B|95% paper-bootstrap CI|
|---|---:|---:|---:|---:|
|L16|8.79668e-05|0.000237497|-0.00014953|[-0.000498891, 6.2465e-05]|
|L24|3.11527e-05|3.8357e-05|-7.20426e-06|[-3.33904e-05, 1.42729e-05]|
|L32|7.31258e-05|0.0001209|-4.77743e-05|[-0.000180763, 3.73199e-05]|
|L40|0.0018953|0.00100383|0.000891466|[-9.23656e-05, 0.00185105]|
|L48|0.00195702|0.000901386|0.00105563|[-0.000243656, 0.00238596]|
|L56|0.00238629|0.00215491|0.000231379|[-0.00348736, 0.00295006]|
|L62|0.0519105|0.0374763|0.0144342|[-0.0443915, 0.104506]|

These CIs resample A and B papers independently; they are NOT matched-pair or causal estimates.

## First-token versus full-name teacher forcing
See `figures/first_vs_teacher_forced.png`; the second endpoint conditions on preceding gold-name tokens and does not measure unassisted recall.

## Artifacts and integrity
Original JSONL and 300 paper-level rows checked; audit figures are regenerated from saved records without GPU.
Saved additional numerical CSV tables, plots in PNG+PDF, and a protocol candidate JSON.

## Stage 5 protocol (CANDIDATE, not scientifically validated)
Primary: first-listed author first-token reciprocal rank, paper-level equal weight.
Auxiliary: all-author first-token RR and teacher-forced full-name MRR, explicitly separate.
Required: exact citation-bin + field matched A/B where feasible; nearest year and author count; no silent relaxation.
Matching feasibility: Max theoretical A/B same citation_bin+field candidates before additional restrictions: 1682. Not an executed matching.
Negative controls: matched false authors, title shuffle, and unrelated-title name-prior. These have **NOT RUN**.
A future matched-pair bootstrap and multiplicity policy are required before inferential conclusions.

## Conclusion
Stage4 demonstrated end-to-end execution and saved outputs. It cannot by itself establish internal gold-author knowledge or an A>B accessibility difference.
Plots are descriptions of the existing 20-paper pilot, not independent validation of J-Lens fidelity.
