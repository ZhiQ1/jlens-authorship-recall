"""A7.1: the same P1 decoder under three fitting protocols.

Shows why Stage 8's fold-safe decoder replaces Stage 5's, whose SVD is fit
on the full set. Outputs ``prevalence_decoding_protocol_comparison.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    MODEL_COLORS,
    RunSpec,
    model_label,
    plt,
    r2_from_predictions,
    spearman,
)
from dua.probing.stages.prevalence.decoders import (
    fold_safe_pca_ridge_oof,
    ridge_oof,
    ridge_oof_unscaled_stage5_style,
)


def run_protocol_comparison(spec: RunSpec, X_raw: np.ndarray, X_svd: np.ndarray, scored: pd.DataFrame) -> pd.DataFrame:
    y = np.log1p(pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0).to_numpy(dtype=np.float32))
    rows: list[dict] = []
    protocol_specs = [
        ("stage5_global_svd_unscaled", lambda: ridge_oof_unscaled_stage5_style(X_svd, y)),
        ("stage8_global_svd_scaled", lambda: ridge_oof(X_svd, y)),
        ("fold_safe_pca_scaled", lambda: fold_safe_pca_ridge_oof(X_raw, y)),
    ]
    for protocol, fn in protocol_specs:
        pred, alpha = fn()
        rows.append({
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "protocol": protocol,
            "n": len(y),
            "r2_cv": round(r2_from_predictions(y, pred), 6),
            "spearman_rho_cv": round(spearman(y, pred), 6),
            "best_alpha": alpha,
        })
    return pd.DataFrame(rows)


def plot_protocol_comparison(df: pd.DataFrame, fig_dir: Path) -> None:
    if df.empty:
        return
    df = df.copy()
    df["r2_cv"] = pd.to_numeric(df["r2_cv"], errors="coerce")
    order = ["stage5_global_svd_unscaled", "stage8_global_svd_scaled", "fold_safe_pca_scaled"]
    labels = {
        "stage5_global_svd_unscaled": "Stage5-style\nSVD+ridge",
        "stage8_global_svd_scaled": "Global SVD\n+ scaling",
        "fold_safe_pca_scaled": "Fold-safe\nPCA+scaling",
    }
    models = sorted(df["model"].unique())
    x = np.arange(len(order))
    width = 0.35 if len(models) <= 2 else 0.8 / max(len(models), 1)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for i, model in enumerate(models):
        sub = df[df["model"] == model].set_index("protocol").reindex(order)
        offset = (i - (len(models) - 1) / 2) * width
        ax.bar(
            x + offset,
            sub["r2_cv"],
            width=width,
            label=model_label(model),
            color=MODEL_COLORS.get(model, None),
        )
    ax.set_xticks(x)
    ax.set_xticklabels([labels[p] for p in order])
    ax.set_ylabel("Prevalence decoding CV R2")
    ax.set_title("Prevalence decoding protocol comparison")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    out = fig_dir / "figure_prevalence_protocol_comparison.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
