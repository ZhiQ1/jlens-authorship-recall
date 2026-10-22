"""A7.2: P1 decoding fit separately inside each field.

Outputs ``within_field_prevalence_decoding.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    N_SVD_COMPONENTS,
    RunSpec,
    r2_from_predictions,
    spearman,
)
from dua.probing.stages.prevalence.decoders import (
    fold_safe_pca_ridge_oof,
    metadata_matrix,
    ridge_oof,
)


def run_within_field_decoding(
    spec: RunSpec,
    X_raw: np.ndarray,
    scored: pd.DataFrame,
    n_model_layers: int,
    min_n: int = 50,
) -> pd.DataFrame:
    """
    Test whether P1 decodes prevalence after holding field fixed.

    This addresses the topic/field confound: paper titles carry field signals,
    and field can correlate with citation count and hallucination rate. Each row
    fits and evaluates a decoder only within one field.
    """
    if "field" not in scored.columns:
        return pd.DataFrame([{
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "layer_depth_pct": round(100.0 * spec.optimal_layer / (n_model_layers - 1), 1),
            "field": "",
            "feature_set": "",
            "n": len(scored),
            "skip_reason": "missing field column",
        }])

    rows: list[dict] = []
    fields = scored["field"].fillna("unknown").astype(str)
    for field, field_idx in fields.groupby(fields).groups.items():
        idx = np.asarray(list(field_idx), dtype=np.int64)
        field_scored = scored.iloc[idx].reset_index(drop=True)
        y = np.log1p(
            pd.to_numeric(field_scored["citation_count"], errors="coerce")
            .fillna(0)
            .to_numpy(dtype=np.float32)
        )
        base = {
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "layer_depth_pct": round(100.0 * spec.optimal_layer / (n_model_layers - 1), 1),
            "field": field,
            "n": len(y),
            "log_citation_std": round(float(np.std(y)), 6),
            "protocol": "within_field_fold_safe_pca_scaler_ridge",
        }
        if len(y) < min_n:
            rows.append({**base, "feature_set": "all", "skip_reason": f"n < {min_n}"})
            continue
        if float(np.std(y)) == 0.0:
            rows.append({**base, "feature_set": "all", "skip_reason": "constant citation target"})
            continue

        X_field = X_raw[idx]
        X_meta = metadata_matrix(field_scored, include_field=False)
        feature_specs = [
            ("metadata_controls_no_field", "metadata_scaled_ridge", lambda: ridge_oof(X_meta, y)),
            ("p1_embedding_fold_safe_pca", "within_field_fold_safe_pca_scaler_ridge", lambda: fold_safe_pca_ridge_oof(X_field, y)),
            (
                "metadata_plus_p1_embedding_fold_safe_pca",
                "within_field_fold_safe_pca_scaler_ridge",
                lambda: fold_safe_pca_ridge_oof(X_field, y, X_meta=X_meta),
            ),
        ]
        metric_rows: dict[str, float] = {}
        for feature_set, protocol, fn in feature_specs:
            try:
                pred, alpha = fn()
                r2 = r2_from_predictions(y, pred)
                metric_rows[feature_set] = r2
                rows.append({
                    **base,
                    "feature_set": feature_set,
                    "n_features": X_meta.shape[1] if feature_set == "metadata_controls_no_field" else (
                        N_SVD_COMPONENTS + (X_meta.shape[1] if feature_set.startswith("metadata_plus") else 0)
                    ),
                    "r2_cv": round(r2, 6),
                    "spearman_rho_cv": round(spearman(y, pred), 6),
                    "best_alpha": alpha,
                    "protocol": protocol,
                    "skip_reason": "",
                })
            except ValueError as exc:
                rows.append({
                    **base,
                    "feature_set": feature_set,
                    "n_features": "",
                    "r2_cv": "",
                    "spearman_rho_cv": "",
                    "best_alpha": "",
                    "protocol": protocol,
                    "skip_reason": str(exc),
                })

        if {
            "metadata_controls_no_field",
            "metadata_plus_p1_embedding_fold_safe_pca",
        }.issubset(metric_rows):
            rows.append({
                **base,
                "feature_set": "incremental_p1_over_within_field_metadata",
                "n_features": N_SVD_COMPONENTS + X_meta.shape[1],
                "r2_cv": round(
                    metric_rows["metadata_plus_p1_embedding_fold_safe_pca"]
                    - metric_rows["metadata_controls_no_field"],
                    6,
                ),
                "spearman_rho_cv": "",
                "best_alpha": "",
                "protocol": "within_field_fold_safe_pca_scaler_ridge",
                "skip_reason": "",
            })

    return pd.DataFrame(rows)
