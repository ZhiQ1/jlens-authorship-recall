"""A7.3: shuffled-label negative controls (Table A39).

Outputs ``negative_controls.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    RANDOM_SEED,
    RunSpec,
    model_label,
    plt,
    r2_from_predictions,
    spearman,
)
from dua.probing.stages.prevalence.decoders import fold_safe_pca_ridge_oof


def run_negative_controls(
    spec: RunSpec,
    X_raw: np.ndarray,
    scored: pd.DataFrame,
    real_r2: float,
    n_shuffles: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    y = np.log1p(pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0).to_numpy(dtype=np.float32))
    rows: list[dict] = []
    for i in range(n_shuffles):
        y_perm = rng.permutation(y)
        pred, alpha = fold_safe_pca_ridge_oof(X_raw, y_perm)
        rows.append({
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "control": "shuffled_log_citation",
            "shuffle_idx": i + 1,
            "n": len(y),
            "r2_cv": round(r2_from_predictions(y_perm, pred), 6),
            "spearman_rho_cv": round(spearman(y_perm, pred), 6),
            "best_alpha": alpha,
            "real_embedding_r2_cv": round(real_r2, 6),
            "protocol": "fold_safe_pca_scaler_ridge",
        })
    return pd.DataFrame(rows)


def plot_negative_controls(df: pd.DataFrame, fig_dir: Path) -> None:
    if df.empty:
        return
    df = df.copy()
    df["r2_cv"] = pd.to_numeric(df["r2_cv"], errors="coerce")
    df["real_embedding_r2_cv"] = pd.to_numeric(df["real_embedding_r2_cv"], errors="coerce")
    models = sorted(df["model"].unique())
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    data = [df[df["model"] == m]["r2_cv"].dropna().to_numpy() for m in models]
    ax.boxplot(data, labels=[model_label(m) for m in models], showfliers=True)
    for i, model in enumerate(models, start=1):
        real = float(df[df["model"] == model]["real_embedding_r2_cv"].iloc[0])
        ax.scatter(i, real, color="#d62728", zorder=3, label="real labels" if i == 1 else None)
    ax.axhline(0, color="#555555", lw=1, ls="--")
    ax.set_ylabel("CV R2")
    ax.set_title("Shuffled citation-label negative controls")
    ax.legend(frameon=False)
    fig.tight_layout()
    out = fig_dir / "figure_negative_controls.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
