"""A7.1: prevalence decoding for every position (P1-P5) and layer.

Outputs ``validated_strategy_layer_prevalence.csv`` and
``validated_strategy_peak_r2.csv``; Figures A11 and A12.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    MODEL_COLORS,
    STRATEGIES,
    RunSpec,
    align_rows,
    find_h5_path,
    find_scored_path,
    h5py,
    load_layer_indices,
    model_label,
    plt,
    r2_from_predictions,
    spearman,
)
from dua.probing.stages.prevalence.decoders import fold_safe_pca_ridge_oof


def run_validated_strategy_layer_sweep(spec: RunSpec) -> pd.DataFrame:
    scored = pd.read_csv(find_scored_path(spec.run_dir), sep="\t")
    h5_path = find_h5_path(spec.run_dir)
    rows: list[dict] = []
    with h5py.File(h5_path, "r") as h5:
        layers = load_layer_indices(h5)
        valid_idx, aligned = align_rows(h5, scored)
        n_model_layers = int(h5.attrs.get("n_model_layers", max(layers) + 1))
        y = np.log1p(
            pd.to_numeric(aligned["citation_count"], errors="coerce")
            .fillna(0)
            .to_numpy(dtype=np.float32)
        )

        for strategy in STRATEGIES:
            key = f"per_query/{strategy}"
            if key not in h5:
                print(f"[stage8] {spec.model}: skipping missing {key}")
                continue
            print(f"[stage8] {spec.model}: validated prevalence sweep for {strategy}")
            for pos, layer_idx in enumerate(layers):
                X = h5[key][:, pos, :][valid_idx].astype(np.float32)
                pred, alpha = fold_safe_pca_ridge_oof(X, y)
                rows.append({
                    "model": spec.model,
                    "strategy": strategy,
                    "layer_idx": int(layer_idx),
                    "layer_depth_pct": round(100.0 * int(layer_idx) / (n_model_layers - 1), 1),
                    "r2_cv": round(r2_from_predictions(y, pred), 6),
                    "spearman_rho_cv": round(spearman(y, pred), 6),
                    "best_alpha": alpha,
                    "n": len(y),
                    "protocol": "fold_safe_pca_scaler_ridge",
                })
    return pd.DataFrame(rows)


def strategy_peak_summary(layer_df: pd.DataFrame) -> pd.DataFrame:
    if layer_df.empty:
        return pd.DataFrame()
    df = layer_df.copy()
    df["r2_cv"] = pd.to_numeric(df["r2_cv"], errors="coerce")
    rows: list[pd.Series] = []
    for _, grp in df.dropna(subset=["r2_cv"]).groupby(["model", "strategy"], sort=True):
        rows.append(grp.loc[grp["r2_cv"].idxmax()])
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).reset_index(drop=True)
    return out.rename(columns={
        "layer_idx": "peak_layer_idx",
        "layer_depth_pct": "peak_layer_depth_pct",
        "r2_cv": "peak_r2_cv",
        "spearman_rho_cv": "peak_spearman_rho_cv",
    })


def plot_prevalence_depth_trajectory(df: pd.DataFrame, fig_dir: Path) -> None:
    from matplotlib.lines import Line2D

    if df.empty:
        return
    df = df[df["strategy"].isin(["p1", "p4"])].copy()
    if df.empty:
        return
    df["layer_depth_pct"] = pd.to_numeric(df["layer_depth_pct"], errors="coerce")
    df["r2_cv"] = pd.to_numeric(df["r2_cv"], errors="coerce")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    models = sorted(df["model"].unique())
    fallback_colors = ["#1B7837", "#B35806", "#4D4D4D", "#542788"]
    color_by_model = {
        model: MODEL_COLORS.get(model, fallback_colors[i % len(fallback_colors)])
        for i, model in enumerate(models)
    }
    dash_by_strategy = {"p1": "-", "p4": (0, (6, 3))}
    for (model, strategy), grp in df.groupby(["model", "strategy"]):
        grp = grp.sort_values("layer_depth_pct")
        ax.plot(
            grp["layer_depth_pct"],
            grp["r2_cv"],
            marker="o",
            lw=2,
            ls=dash_by_strategy.get(strategy, "-"),
            color=color_by_model[model],
            label=f"{model_label(model)} {strategy.upper()}",
        )
    ax.set_xlabel("Normalized model depth (%)")
    ax.set_ylabel("Prevalence decoding CV R2")
    ax.set_title("Prevalence signal across depth")
    ax.grid(alpha=0.25)
    model_handles = [
        Line2D([0], [0], color=color_by_model[model], lw=2, marker="o", label=model_label(model))
        for model in models
    ]
    strategy_handles = [
        Line2D([0], [0], color="#333333", lw=2.4, ls="-", label="P1: prompt-end state"),
        Line2D([0], [0], color="#333333", lw=2.4, ls=(0, (3, 1.5, 3, 1.5, 3)), label="P4: prompt-mean state"),
    ]
    handles = model_handles + strategy_handles
    ax.legend(handles=handles, frameon=False, fontsize=8, handlelength=3.2, ncol=2)
    fig.tight_layout()
    out = fig_dir / "figure_prevalence_depth_trajectory.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")


def plot_strategy_comparison(df: pd.DataFrame, fig_dir: Path) -> None:
    if df.empty:
        return
    df["peak_r2_cv"] = pd.to_numeric(df["peak_r2_cv"], errors="coerce")
    pivot = df.pivot(index="model", columns="strategy", values="peak_r2_cv")
    strategies = [s for s in ["p1", "p2", "p3", "p4", "p5"] if s in pivot.columns]
    pivot = pivot.reindex(sorted(pivot.index))[strategies]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x = np.arange(len(strategies))
    marker_by_model = {
        "mistral_small_3_2_24b": "s",
        "qwen3_32b": "o",
    }
    label_offsets = {
        "mistral_small_3_2_24b": {
            "p1": (0, -12),
            "p2": (-4, -12),
            "p3": (0, 15),
            "p4": (4, -12),
            "p5": (0, 10),
        },
        "qwen3_32b": {
            "p1": (0, 8),
            "p2": (0, 8),
            "p3": (0, -10),
            "p4": (0, 8),
            "p5": (0, -10),
        },
    }
    fallback_colors = ["#1B7837", "#B35806", "#4D4D4D", "#542788"]
    for i, model in enumerate(pivot.index):
        y = pivot.loc[model].to_numpy(dtype=float)
        color = MODEL_COLORS.get(model, fallback_colors[i % len(fallback_colors)])
        ax.plot(
            x,
            y,
            lw=2.4,
            marker=marker_by_model.get(model, "o"),
            markersize=6.5,
            color=color,
            label=model_label(model),
        )
        for xi, yi, strategy in zip(x, y, strategies):
            if not np.isfinite(yi):
                continue
            dx, dy = label_offsets.get(model, {}).get(strategy, (0, 10))
            va = "bottom" if dy >= 0 else "top"
            ax.annotate(
                f"{yi:.3f}",
                xy=(xi, yi),
                xytext=(dx, dy),
                textcoords="offset points",
                ha="center",
                va=va,
                fontsize=8,
                color=color,
            )

    ax.axhline(0, color="#555555", lw=1, ls="--", alpha=0.75)
    ax.set_xticks(x)
    ax.set_xticklabels([s.upper() for s in strategies])
    ax.set_ylabel("Peak prevalence decoding CV R2")
    ax.set_title("Peak prevalence decoding by prompt strategy")
    ymin = min(-0.18, float(np.nanmin(pivot.to_numpy())) - 0.05)
    ymax = max(0.70, float(np.nanmax(pivot.to_numpy())) + 0.07)
    ax.set_ylim(ymin, ymax)
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    out = fig_dir / "figure_strategy_comparison.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
