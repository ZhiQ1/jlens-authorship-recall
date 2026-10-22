"""A7.2: P1 decoding against metadata controls (Table A38).

Also produces the out-of-fold P1 prevalence score, ``p1_prevalence_pred_oof``,
that the deciles (A7.5) and mediation (Stage 9) are built on. Outputs
``adjusted_prevalence_decoding.csv`` and ``p1_prevalence_predictions.csv``.
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


def run_adjusted_decoding(
    spec: RunSpec,
    X_raw: np.ndarray,
    scored: pd.DataFrame,
    n_model_layers: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = np.log1p(pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0).to_numpy(dtype=np.float32))
    X_meta = metadata_matrix(scored)

    rows: list[dict] = []
    predictions: dict[str, np.ndarray] = {}

    pred, alpha = ridge_oof(X_meta, y)
    predictions["metadata_controls"] = pred
    rows.append({
        "model": spec.model,
        "strategy": "p1",
        "layer_idx": spec.optimal_layer,
        "layer_depth_pct": round(100.0 * spec.optimal_layer / (n_model_layers - 1), 1),
        "feature_set": "metadata_controls",
        "n": len(y),
        "n_features": X_meta.shape[1],
        "r2_cv": round(r2_from_predictions(y, pred), 6),
        "spearman_rho_cv": round(spearman(y, pred), 6),
        "best_alpha": alpha,
        "protocol": "metadata_scaled_ridge",
    })

    for feature_set, meta in [
        ("p1_embedding_fold_safe_pca", None),
        ("metadata_plus_p1_embedding_fold_safe_pca", X_meta),
    ]:
        pred, alpha = fold_safe_pca_ridge_oof(X_raw, y, X_meta=meta)
        predictions[feature_set] = pred
        rows.append({
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "layer_depth_pct": round(100.0 * spec.optimal_layer / (n_model_layers - 1), 1),
            "feature_set": feature_set,
            "n": len(y),
            "n_features": (N_SVD_COMPONENTS + (X_meta.shape[1] if meta is not None else 0)),
            "r2_cv": round(r2_from_predictions(y, pred), 6),
            "spearman_rho_cv": round(spearman(y, pred), 6),
            "best_alpha": alpha,
            "protocol": "fold_safe_pca_scaler_ridge",
        })

    meta_r2 = float([r for r in rows if r["feature_set"] == "metadata_controls"][0]["r2_cv"])
    emb_r2 = float([r for r in rows if r["feature_set"] == "p1_embedding_fold_safe_pca"][0]["r2_cv"])
    comb_r2 = float([r for r in rows if r["feature_set"] == "metadata_plus_p1_embedding_fold_safe_pca"][0]["r2_cv"])
    rows.append({
        "model": spec.model,
        "strategy": "p1",
        "layer_idx": spec.optimal_layer,
        "layer_depth_pct": round(100.0 * spec.optimal_layer / (n_model_layers - 1), 1),
        "feature_set": "incremental_embedding_over_metadata",
        "n": len(y),
        "n_features": N_SVD_COMPONENTS + X_meta.shape[1],
        "r2_cv": round(comb_r2 - meta_r2, 6),
        "spearman_rho_cv": "",
        "best_alpha": "",
        "metadata_r2_cv": meta_r2,
        "embedding_only_r2_cv": emb_r2,
        "combined_r2_cv": comb_r2,
        "protocol": "fold_safe_pca_scaler_ridge",
    })

    pred_df = pd.DataFrame({
        "model": spec.model,
        "paper_id": scored["paper_id"].astype(str),
        "citation_count": pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0),
        "log_citation": y,
        "hr2": pd.to_numeric(scored["hr2"], errors="coerce"),
        "p1_prevalence_pred_oof": predictions["p1_embedding_fold_safe_pca"],
        "metadata_prevalence_pred_oof": predictions["metadata_controls"],
        "combined_prevalence_pred_oof": predictions["metadata_plus_p1_embedding_fold_safe_pca"],
    })
    return pd.DataFrame(rows), pred_df
