# Qwen3-32B — Self-fitted J-Lens (100 prompts) vs Neuronpedia

- Model: Qwen/Qwen3-32B, pinned revision `9216db5781bf21249d130ec9da846c4624c16137`
- Source layers: 24, 32, 40, 48, 56, 62; target layer: 63.
- Self lens fitted on 100 generic WikiText prompts. Comparison uses only common 6 source layers.
- Only matched evaluation items, prompts, model and metric definitions are compared.
- Split-half stability: **NOT RUN**; requires independent 50+50 fits.
- Gold-vs-False Author Pilot: **NOT PART OF THIS SCRIPT** (requires matched task scorer; do not mislabel Fidelity).

## Generic Fidelity
- Self evaluated items: 20; public records available: 20

- Exact matched public comparison items: 20 (out of 20)

## Paper Fidelity
- Self evaluated items: 20; public records available: 20

- Exact matched public comparison items: 20 (out of 20)

## Gold-vs-False task pilot: NOT RUN for both lenses yet. Use `351_validate_public_lens_offload_fixed.py` with the same seed, names, prompts and six shared layers for the self-fit lens.
## Interpretation boundaries
- Numerical finite matrices do not prove readout fidelity.
- Compare only six shared layers and exact same examples. Generic and Paper are separately evaluated.
- MRR and KL may disagree; neither certifies hidden factual knowledge.
- 20 prompts per task yield exploratory rather than conclusive uncertainty estimates.
- A gold-vs-false author pilot is not an independent fidelity standard.
- Published Neuronpedia fitting dataset overlaps WikiText provenance; exact fit/eval overlap is unverified, so do not claim universally held-out evaluation.

## Outputs
- `numerical/matrices.csv`, `numerical/matrices.json`
- `raw/generic.jsonl`, `raw/paper.jsonl`
- `summary/metrics.csv`, `summary/paired_self_vs_public.csv`, `summary/paired_bootstrap_ci.csv`
- `figures/*.png`, `figures/*.pdf`
