# Self-fitted Qwen3-32B J-Lens: Split-half Matrix Stability

## Experimental design
Original WikiText fitting corpus verified against manifest SHA-256. Split A uses even indices 0..98, Split B uses odd indices 1..99. Each half was independently fit with exactly the original 100-prompt script settings (BF16 Qwen3-32B, source layers 24/32/40/48/56/62, target L63, dim_batch=8, max_seq_len=128, skip_first=16).

## Matrix numerical checks and stability

| Layer | Cosine(A,B) | Relative Frobenius Difference | Norm A | Norm B |
|---|---:|---:|---:|---:|
| 24 | 0.677628 | 0.807244 | 41.43 | 45.37 |
| 32 | 0.849494 | 0.548749 | 51.48 | 52.05 |
| 40 | 0.939470 | 0.348196 | 88.61 | 87.41 |
| 48 | 0.980337 | 0.198336 | 105.86 | 105.49 |
| 56 | 0.995710 | 0.092652 | 93.33 | 93.13 |
| 62 | 0.999846 | 0.017654 | 80.83 | 80.69 |

## Conclusions and limitations
This is a MATRIX-LEVEL split-half check, not yet a complete readout-stability validation. Neither high cosine nor low norm difference proves the two lenses agree on vocabulary ranks, KL, or gold author readouts. Those require the same held-out 20 generic and 20 paper prompts, and the same output-scoring code.
Do not use the fitting prompts for held-out assessment. The selection rule is interleaved, not random; it is predeclared for reproducibility.

## Artifacts
`fits/lens_A.pt`, `fits/lens_B.pt`, `summary/matrix_stability.csv`, `figures/matrix_cosine.{png,pdf}`, `figures/matrix_relative_difference.{png,pdf}`.
