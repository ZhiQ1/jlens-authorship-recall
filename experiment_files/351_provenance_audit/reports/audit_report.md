# Audit 3 & 4 — Data leakage and fitting protocol

## Artifact authenticity / actual fitting count
- Self file SHA256: `268aba15f3377fff4dfa553cc67b782c23148f0aa7a7b7de3c34b6534d8d40e3`; schema `finished_lens`; recorded n=100.
- Public file SHA256: `0af5ccf2e1c251bedc202607a7ca214f3b9f60980bab73d67a3d0b887db213d8`; schema `finished_lens`; recorded n=557.
- CAUTION: historical Neuronpedia Qwen3-32B checkpoint (80 prompts) was replaced by a finalized 557-prompt artifact in 2026. Do not infer the actual local file version from its filename.
- The public fit version is confirmed only if local checkpoint schema/n_prompts and SHA256 are recorded. The comparison must be tied to this exact SHA256 used in prior tests.

## Audit 3 — Fitting / evaluation leakage
- Self fit corpus: `/scratch/zhang.zhiqi2/jlens/fitting_corpus/wikitext103_qwen32b_1000.jsonl`; SHA256 `1af8dbff1b6e5b9f5bdd55b31d2d7bfadf28c8ab256a47e69d45db6b5ebc0b06`; manifest integrity: `True`.
- Self fit selection is exactly indices 0–99 from the saved 1,000-row JSONL; there is no randomized selection in the 100-prompt fitting script.
- Available evaluation records: generic 20, paper 20.
- Self-fit vs evaluation: 0 exact prompt matches, 0 lexical review flags among 40 evaluation examples.
- Exact normalized-match test and 8-word lexical overlap only measure text reuse of the available fitted prompt strings. They do NOT establish distribution independence or absence of latent / source-document overlap.
- Public Neuronpedia: no 557 individual fitting prompt strings supplied by public checkpoint or config; per-prompt exact overlap **UNDETERMINED** until its original fitting text/indices are obtained.
- Training split shared provenance (WikiText-103) can create distribution overlap even with zero exact evaluation-prompt matches. Self fit uses WikiText and paper-title prompts represent different tasks; this is not necessarily direct leakage.

## Audit 4 — Protocol comparability
- See `summary/protocol_comparison.csv` for evidence-status rows; public config is read if present (otherwise marked unknown).
- `dim_batch` is a backward-pass vectorization/memory control, not a weighting hyperparameter in the released estimator; a different value is not by itself proof of a different mathematical estimator. Numerical equivalence still depends on implementation and floating-point behavior.
- A public `prompts_fitted` count from config cannot override local checkpoint metadata; verify artifact version and any refit provenance.
- The released `jlens.fitting.fit` accumulates a per-prompt Jacobian sum and divides by number of valid prompts. Reproducing the public wrapper may require checking its own implementation and library revision.
- Model revision in the self100 script was pinned via the fitting-corpus manifest; if the public fitting model revision is absent, model-name equality is insufficient to claim identical weights.

## Interpretation / restrictions
- Both audits are provenance checks, not GPU performance experiments. No original outputs or weights are overwritten.
- Do not infer that the 100-prompt fit outperforms a 557-prompt fit *because of* fitting size. Other protocol differences and fit-version effects remain confounded.
- Public 557-prompt training-text exact membership remains unavailable locally; record as unverifiable unless original prompt list is obtained.
