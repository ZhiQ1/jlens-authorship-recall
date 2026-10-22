# Stage 4 — Gold-author readout benchmark

**Status:** COMPLETE · 20/20 planned papers completed.

## Research question
Can the pretrained public Jacobian Lens produce reproducible layer-wise candidate-token readouts on scientific-paper author prompts, before the formal A/B/C/D study?

## Methods
- Model: `Qwen/Qwen3-32B` · pinned revision `9216db5781bf21249d130ec9da846c4624c16137` · BF16.
- Lens: `/scratch/zhang.zhiqi2/jlens/public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt`; lens SHA-256 in `config/run_config.json`.
- Prompt: `Who are the authors of the paper titled "{title}" ({year})?
Authors:` with title/year substitution.
- Layers: [16, 24, 32, 40, 48, 56, 62]; device map uses 29 blocks on GPU and remaining blocks on CPU.
- Primary measure: first-listed author first-token RR at `Authors:` with no author prefix.
- Exploratory measure: all listed authors at the *same* list-start position (author-order confound).
- Auxiliary measure: teacher-forced mean per-token reciprocal rank of the complete name (not unprompted full-name recall).
- Aggregation: each paper has equal weight; author and token rows are not independent samples.
- Percentile bootstrap intervals resample papers within groups; suppressed for n < 2.

## Dataset and completion
- Group counts: {'A': 8, 'B': 8, 'C': 3, 'D': 1}.
- Authors scored: 93; skipped: 0; skip reasons: {}.
- Papers with no scored authors: 0.
- Mean observed wall time: 90.682 seconds per paper.

## Actual measured results
| Layer | J-Lens primary RR | Vanilla primary RR | J-Lens conditional MRR | Vanilla conditional MRR |
|---|---:|---:|---:|---:|
| 16 | 0.000221 | 0.000057 | 0.001819 | 0.000970 |
| 24 | 0.000046 | 0.000025 | 0.000895 | 0.000656 |
| 32 | 0.000219 | 0.000023 | 0.002404 | 0.002487 |
| 40 | 0.001442 | 0.000032 | 0.005481 | 0.009703 |
| 48 | 0.001333 | 0.000023 | 0.056041 | 0.012760 |
| 56 | 0.007040 | 0.000300 | 0.047070 | 0.052046 |
| 62 | 0.055923 | 0.196579 | 0.397721 | 0.401723 |

## Interpretation and limitations
- This is an exploratory pipeline benchmark, not a statistical test of the research hypothesis.
- Even a high gold-author RR cannot alone establish factual storage or causal knowledge accessibility.
- The probe position favors the first-listed author; all-author first-token probes are exploratory.
- Teacher forcing reveals candidate-name prefixes and must not be interpreted as free recall.
- The public average Jacobian is an approximation; generic/paper-prompt fidelity varies by layer and metric.
- A/B/C/D are unbalanced in small pilot samples; reported plots are descriptive, not confirmatory.
- Source CSV and lens version are recorded; exact pretrained fit model revision cannot be confirmed from lens provenance.
- Matched-false and title-shuffled controls have **NOT** been executed in this Stage 4 run; no control results/figures are claimed.
- Findings for omitted authors could be biased by strict tokenizer checks; see skipped_authors.csv.

## Conclusion
- Observed 20 completed papers with 93 scored authors. This establishes pipeline output coverage only.
- Do not claim an A-vs-B difference, tool reliability across all 63 layers, or validated author knowledge without additional controls and larger matched analysis.

## Reproducibility and figures
- `raw/results.jsonl`: raw per-paper checkpoint snapshot.
- `raw/token_scores.csv`: paper–author–token–layer scores.
- `raw/skipped_authors.csv`: omissions and reasons.
- `summary/paper_metrics.csv`: paper-level aggregates.
- `summary/layer_metrics.csv`: layer/group estimates with paper-bootstrap CI where estimable.
- `summary/a_vs_b_exploratory.csv`: descriptive A–B differences, not a formal test.
- `summary/summary.json`: completion and validation metadata.
- `config/run_config.json`: run settings and hashes.
- `figures/first_listed_first_rr.png` / `.pdf`: primary rank readout.
- `figures/conditional_token_mrr.png` / `.pdf`: conditional full-name diagnostic.
- `figures/abcd_descriptive.png` / `.pdf`: behavioral group description.
- `figures/sample_coverage.png` / `.pdf`: completed sample counts.

**No matched-false/title-shuffle control figure is generated because this run contains no control measurements.**
