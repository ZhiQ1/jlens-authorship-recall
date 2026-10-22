"""A7.5: mean HR2 by decile of the P1-decoded prevalence score (Table A41, Figure 7).

Outputs ``internal_prevalence_deciles.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import model_label, plt


def run_internal_deciles(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for model, grp in predictions.groupby("model", sort=True):
        grp = grp.copy()
        grp["internal_prevalence_decile"] = pd.qcut(
            grp["p1_prevalence_pred_oof"],
            q=10,
            labels=False,
            duplicates="drop",
        )
        sub = grp.dropna(subset=["internal_prevalence_decile"])
        if sub.empty:
            continue
        out = sub.groupby("internal_prevalence_decile", as_index=False).agg(
            n=("paper_id", "size"),
            mean_predicted_log_citation=("p1_prevalence_pred_oof", "mean"),
            mean_log_citation=("log_citation", "mean"),
            mean_citation_count=("citation_count", "mean"),
            mean_hr2=("hr2", "mean"),
        )
        out["internal_prevalence_decile"] = out["internal_prevalence_decile"].astype(int) + 1
        out.insert(0, "model", model)
        rows.append(out)
    if not rows:
        return pd.DataFrame()
    df = pd.concat(rows, ignore_index=True)
    for col in ["mean_predicted_log_citation", "mean_log_citation", "mean_citation_count", "mean_hr2"]:
        df[col] = df[col].round(6)
    return df


def plot_internal_deciles(df: pd.DataFrame, fig_dir: Path) -> None:
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for model, grp in df.groupby("model"):
        grp = grp.sort_values("internal_prevalence_decile")
        ax.plot(
            grp["internal_prevalence_decile"],
            grp["mean_hr2"],
            marker="o",
            lw=2,
            label=model_label(model),
        )
    ax.set_xlabel("P1-decoded prevalence-score group")
    ax.set_ylabel("Mean HR2")
    ax.set_title("Hallucination rate by internal prevalence state")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    out = fig_dir / "figure_internal_prevalence_deciles.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
