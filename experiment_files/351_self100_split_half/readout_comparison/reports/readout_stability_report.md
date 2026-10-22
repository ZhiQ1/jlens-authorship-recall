# Self-fitted J-Lens — Split-half held-out readout stability

Both independently fitted 50-prompt lenses were evaluated on exact paired prompts using the original 351_self_jlens_validation.py scoring protocol.

Important: A/B differences are descriptive, not a test that either lens improves over Neuronpedia. The 95% percentile bootstrap intervals are unadjusted for multiple layers/metrics. The fit/eval dataset-independence audit remains separate.

| Distribution | Layer | KL A | KL B | Delta A-B [95% CI] | MRR A | MRR B |
|---|---:|---:|---:|---|---:|---:|
| generic | 24 | 9.2193 | 11.6657 | -2.4464 [-2.9764, -2.0165] | 0.013655 | 0.000840 |
| generic | 32 | 7.1802 | 9.3357 | -2.1555 [-3.2370, -1.0995] | 0.055638 | 0.034505 |
| generic | 40 | 14.3534 | 14.2815 | +0.0719 [-0.6714, +0.8115] | 0.004126 | 0.004224 |
| generic | 48 | 12.0431 | 12.3177 | -0.2746 [-0.5054, -0.0321] | 0.005188 | 0.005488 |
| generic | 56 | 6.7960 | 6.4007 | +0.3953 [+0.2436, +0.5641] | 0.224637 | 0.282868 |
| generic | 62 | 1.3334 | 1.2754 | +0.0581 [+0.0396, +0.0789] | 0.652500 | 0.652500 |
| paper | 24 | 7.2378 | 9.5091 | -2.2714 [-2.7799, -1.8082] | 0.001038 | 0.000025 |
| paper | 32 | 6.1802 | 8.1761 | -1.9960 [-2.1829, -1.7876] | 0.000388 | 0.000053 |
| paper | 40 | 6.6655 | 7.6969 | -1.0314 [-1.5207, -0.5846] | 0.006265 | 0.007242 |
| paper | 48 | 8.3833 | 9.0406 | -0.6573 [-0.7488, -0.5676] | 0.001028 | 0.001354 |
| paper | 56 | 5.0860 | 5.1653 | -0.0793 [-0.1682, +0.0010] | 0.011751 | 0.012380 |
| paper | 62 | 0.5882 | 0.5672 | +0.0210 [+0.0171, +0.0254] | 0.363431 | 0.367064 |

## Provenance

- Lens A SHA256: 167843e7358766b490d3384a30270e4ed63d858c2f420df6c26bb9660bfe7031
- Lens B SHA256: 1ccb36c498eacf98fb6e7bc39c19ed98ac77f6872049cc0edb7652308d9c61eb
- Model revision: 9216db5781bf21249d130ec9da846c4624c16137
- Corpus SHA256: 1af8dbff1b6e5b9f5bdd55b31d2d7bfadf28c8ab256a47e69d45db6b5ebc0b06
- n=20 independently scored prompts for each distribution; 6 common source layers.
- Missing or mismatched examples cause hard failure; no silent dropping.
