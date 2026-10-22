"""Stage 8 experiments, one module each.

Run them all with ``python -m dua.probing.stages.stage8_prevalence_appendix``.

    common               constants, run-directory I/O, h5 loading, small stats helpers
    decoders             fold-safe PCA + ridge decoder, metadata features
    layer_sweep          A7.1  every position and layer; Figures A11-A12
    protocol_comparison  A7.1  fold-safe vs. global-SVD fitting
    adjusted_decoding    A7.2  P1 vs. metadata (Table A38); the out-of-fold P1 score
    within_field         A7.2  P1 decoding inside each field
    negative_controls    A7.3  shuffled labels (Table A39)
    bucket_probe         A7.4  citation-regime classification (Table A40)
    deciles              A7.5  HR2 by P1-score decile (Table A41, Figure 7)
    residuals            decoder error by citation bucket; not in the paper
    external_proxy       optional external-proxy check; not in the paper
    summary              Stage 5/6 roll-up and the appendix prose snippet
"""
