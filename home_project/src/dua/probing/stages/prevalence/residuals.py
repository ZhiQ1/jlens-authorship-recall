"""P1 decoder error by citation bucket. Not reported in the paper.

Outputs ``prevalence_residual_summary.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    CITATION_BUCKET_LABELS,
    MODEL_COLORS,
    add_citation_buckets,
    model_label,
    plt,
)


def run_prevalence_residual_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for model, grp in predictions.groupby("model", sort=True):
        grp = add_citation_buckets(grp)
        grp["residual"] = grp["p1_prevalence_pred_oof"] - grp["log_citation"]
        grp["abs_residual"] = grp["residual"].abs()
        for bucket, sub in grp.dropna(subset=["citation_bucket"]).groupby("citation_bucket", observed=True):
            q25, q75 = sub["residual"].quantile([0.25, 0.75]).to_numpy()
            rows.append({
                "model": model,
                "citation_bucket": str(bucket),
                "n": int(len(sub)),
                "mean_log_citation": round(float(sub["log_citation"].mean()), 6),
                "mean_citation_count": round(float(sub["citation_count"].mean()), 6),
                "mean_predicted_log_citation": round(float(sub["p1_prevalence_pred_oof"].mean()), 6),
                "mean_residual_pred_minus_true": round(float(sub["residual"].mean()), 6),
                "median_residual_pred_minus_true": round(float(sub["residual"].median()), 6),
                "q25_residual": round(float(q25), 6),
                "q75_residual": round(float(q75), 6),
                "mean_abs_residual": round(float(sub["abs_residual"].mean()), 6),
                "rmse": round(float(np.sqrt(np.mean(np.square(sub["residual"])))), 6),
            })
    return pd.DataFrame(rows)


def plot_prevalence_residuals(predictions: pd.DataFrame, fig_dir: Path) -> None:
    if predictions.empty:
        return
    df = add_citation_buckets(predictions)
    df["residual"] = pd.to_numeric(df["p1_prevalence_pred_oof"], errors="coerce") - pd.to_numeric(
        df["log_citation"], errors="coerce"
    )
    df = df.dropna(subset=["citation_bucket", "residual"])
    if df.empty:
        return
    df["abs_residual"] = df["residual"].abs()
    summary = df.groupby(["model", "citation_bucket"], observed=True).agg(
        mean_abs_residual=("abs_residual", "mean"),
        q25=("abs_residual", lambda x: x.quantile(0.25)),
        q75=("abs_residual", lambda x: x.quantile(0.75)),
        n=("abs_residual", "size"),
    ).reset_index()

    models = sorted(df["model"].unique())
    fig, axes = plt.subplots(
        nrows=len(models),
        ncols=1,
        figsize=(8.8, 3.8 * len(models)),
        sharex=True,
        sharey=True,
    )
    if len(models) == 1:
        axes = [axes]

    for ax, model in zip(axes, models):
        grp = summary[summary["model"] == model].copy()
        grp["citation_bucket"] = pd.Categorical(
            grp["citation_bucket"],
            categories=CITATION_BUCKET_LABELS,
            ordered=True,
        )
        grp = grp.sort_values("citation_bucket")
        color = MODEL_COLORS.get(model, "#4D4D4D")
        x = np.arange(len(grp))
        y = grp["mean_abs_residual"].to_numpy(dtype=float)
        yerr = np.vstack([
            y - grp["q25"].to_numpy(dtype=float),
            grp["q75"].to_numpy(dtype=float) - y,
        ])
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            fmt="o-",
            lw=2,
            markersize=5,
            capsize=3,
            color=color,
            label="mean with IQR",
        )
        ax.set_title(model_label(model))
        ax.set_ylabel("Absolute prediction error")
        ax.grid(alpha=0.25)
        ax.legend(frameon=False, loc="upper right")
        ax.set_xticks(x)
        ax.set_xticklabels(grp["citation_bucket"].astype(str), rotation=35, ha="right")

    axes[-1].set_xlabel("Citation bucket")
    fig.suptitle("P1 prevalence-decoder error by citation bucket", y=1.0)
    fig.tight_layout()
    out = fig_dir / "figure_prevalence_residuals.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
