# Self-100 vs Neuronpedia — matched author pilot

- Matched papers completed: 20/20
- **Same gold/false authors, same paper prompts, tokenizer protocol and model revision as original Neuronpedia pilot.**
- This is a task-specific discrimination pilot, not a standalone causal proof of factual knowledge.
- Primary metric: paired author full-name mean conditional log-probability difference (gold minus false).
- Tokens after first are teacher-forced. Name-frequency and first-listed position confounds remain.

## Layer-wise results

| Layer | Self full win | Public full win | Vanilla full win | Self ΔlogP | Public ΔlogP |
|---|---:|---:|---:|---:|---:|
| L24 | 0.700 | 0.650 | 0.650 | +0.478 | +0.642 |
| L32 | 0.550 | 0.550 | 0.550 | +0.283 | +0.453 |
| L40 | 0.550 | 0.450 | 0.550 | +0.169 | +0.128 |
| L48 | 0.700 | 0.700 | 0.450 | +0.733 | +0.766 |
| L56 | 0.550 | 0.500 | 0.650 | +0.354 | +0.344 |
| L62 | 0.550 | 0.550 | 0.600 | +1.257 | +1.274 |

## Interpretation
- A higher gold-win rate on this small, selected set is suggestive but not a fidelity certificate.
- Bootstrap intervals pair the **same papers**; compare their deltas with uncertainty.
- The Public lens original task pilot must NOT be confused with the 20-paper Paper-Prompt Fidelity test.
- This archive does not perform title shuffle or independent split-half stability.
- Outputs: raw JSONL/CSV, per-paper metrics, layer summary, paired bootstrap CI, PNG/PDF plots.
