"""Stage 7: figures for the Section 7 stages.

Usage
─────
  python -m dua.probing.stages.stage7_make_figures \\
      --in_dir  /scratch/$USER/scholar_qwen/followup_results \\
      --out_dir /scratch/$USER/scholar_qwen/followup_results/figures
"""

from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


MODEL_LABELS = {
    "qwen3_32b": "Qwen3-32B",
    "mistral_small_3_2_24b": "Mistral-Small-3.2-24B",
}


def model_label(name: str) -> str:
    return MODEL_LABELS.get(name, name.replace("_", " "))


def read_csv(in_dir: str, name: str) -> pd.DataFrame:
    path = os.path.join(in_dir, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def read_tsv(in_dir: str, name: str) -> pd.DataFrame:
    path = os.path.join(in_dir, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return pd.read_csv(path, sep="\t")


def plot_main_mechanistic_pathway(in_dir: str, out_dir: str) -> None:
    depth = read_csv(in_dir, "depth_trajectories.csv")
    med = read_csv(in_dir, "mediation_summary.csv")
    probe = read_csv(in_dir, "probe_hallucination_auc.csv")
    depth["layer_depth_pct"] = pd.to_numeric(depth["layer_depth_pct"])
    depth["r2_cv"] = pd.to_numeric(depth["r2_cv"])
    if "label_definition" in probe.columns:
        primary_probe = probe[probe["label_definition"].isin(["hr2_gt_0.5", "hr2_ge_0.5"])].copy()
        if primary_probe.empty:
            primary_probe = probe.copy()
    else:
        primary_probe = probe.copy()

    med_hr2 = med[(med["strategy"] == "p1") & (med["hr_metric"].str.lower() == "hr2")]
    med_by_model = {r["model"]: r for _, r in med_hr2.iterrows()}
    probe_by_model = {r["model"]: r for _, r in primary_probe.iterrows()}

    models = sorted(set(depth["model"]) | set(med_by_model))
    colors = plt.cm.Set2.colors
    color_by_model = {m: colors[i % len(colors)] for i, m in enumerate(models)}

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axes[0]
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    box_kw = dict(boxstyle="round,pad=0.35", fc="white", ec="#333333", lw=1.2)
    ax.text(0.12, 0.72, "Citation\nprevalence", ha="center", va="center", bbox=box_kw, fontsize=10)
    ax.text(0.50, 0.72, "P1 internal\nprevalence state", ha="center", va="center", bbox=box_kw, fontsize=10)
    ax.text(0.88, 0.72, "Hallucination\nrate", ha="center", va="center", bbox=box_kw, fontsize=10)

    arrow_kw = dict(arrowstyle="->", lw=1.5, color="#333333")
    ax.annotate("", xy=(0.38, 0.72), xytext=(0.23, 0.72), arrowprops=arrow_kw)
    ax.annotate("", xy=(0.76, 0.72), xytext=(0.62, 0.72), arrowprops=arrow_kw)
    ax.annotate("", xy=(0.80, 0.56), xytext=(0.20, 0.56), arrowprops=arrow_kw)
    ax.text(0.50, 0.50, "direct path after mediation", ha="center", va="top", fontsize=8, color="#555555")

    y0 = 0.30
    for i, model in enumerate(models):
        row = med_by_model.get(model)
        probe_row = probe_by_model.get(model)
        if row is None:
            continue
        pct = float(row["pct_mediated"])
        layer = int(row["layer_idx"])
        auroc = float(probe_row["auroc"]) if probe_row is not None else float("nan")
        label = f"{model_label(model)}: {pct:.1f}% mediated, P1 layer {layer}"
        if np.isfinite(auroc):
            label += f", probe AUROC {auroc:.3f}"
        ax.text(
            0.05,
            y0 - 0.08 * i,
            label,
            ha="left",
            va="center",
            color=color_by_model[model],
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("Mediation pathway", fontsize=12, fontweight="bold")

    ax = axes[1]
    sub = depth[depth["strategy"] == "p1"].copy()
    for model, grp in sub.groupby("model"):
        grp = grp.sort_values("layer_depth_pct")
        ax.plot(
            grp["layer_depth_pct"],
            grp["r2_cv"],
            marker="o",
            lw=2,
            label=model_label(model),
            color=color_by_model.get(model),
        )
    ax.set_xlabel("Normalized model depth (%)")
    ax.set_ylabel("Prevalence decoding CV R²")
    ax.set_title("P1 prevalence signal by depth", fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    fig.tight_layout()
    out = os.path.join(out_dir, "figure_main_mechanistic_pathway.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage7] wrote {out}")


def plot_hr_trends(in_dir: str, out_dir: str) -> None:
    df = read_csv(in_dir, "hr_by_citation_bin.csv")
    for col in ("mean_hr2", "mean_hr4", "mean_hr5"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    metrics = [("mean_hr2", "HR2"), ("mean_hr4", "HR4"), ("mean_hr5", "HR5")]
    models = sorted(df["model"].unique())
    colors = plt.cm.Set2.colors
    color_by_model = {m: colors[i % len(colors)] for i, m in enumerate(models)}

    # Preserve file order within each model; stage6 already sorts citation bins.
    bins = df["citation_bin"].drop_duplicates().tolist()
    x = np.arange(len(bins))
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharex=True)

    for ax, (col, label) in zip(axes, metrics):
        for model in models:
            sub = df[df["model"] == model].set_index("citation_bin").reindex(bins)
            ax.plot(x, sub[col], marker="o", lw=2, color=color_by_model[model], label=model_label(model))
        ax.set_title(label, fontweight="bold")
        ax.set_ylabel("Mean hallucination rate")
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.25)
        ax.set_xticks(x)
        ax.set_xticklabels(bins, rotation=35, ha="right", fontsize=8)

    axes[0].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    out = os.path.join(out_dir, "figure_appendix_hr_trends.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage7] wrote {out}")


def plot_strategy_comparison(in_dir: str, out_dir: str) -> None:
    df = read_csv(in_dir, "strategy_peak_r2.csv")
    df["peak_r2_cv"] = pd.to_numeric(df["peak_r2_cv"], errors="coerce")
    pivot = df.pivot(index="model", columns="strategy", values="peak_r2_cv")
    pivot = pivot.reindex(sorted(pivot.index))
    strategies = [s for s in ("p1", "p2", "p3", "p4", "p5") if s in pivot.columns]
    pivot = pivot[strategies]

    fig, ax = plt.subplots(figsize=(8, 3.8))
    im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
    ax.set_xticks(np.arange(len(strategies)))
    ax.set_xticklabels([s.upper() for s in strategies])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([model_label(m) for m in pivot.index])
    ax.set_title("Peak prevalence decoding CV R² by strategy", fontweight="bold")

    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", color="white" if val > np.nanmax(pivot.values) * 0.55 else "black", fontsize=9)

    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label("Peak CV R²")
    fig.tight_layout()
    out = os.path.join(out_dir, "figure_appendix_strategy_comparison.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage7] wrote {out}")


def _plot_p9_pca_mode(df: pd.DataFrame, out_dir: str, preprocessing: str, out_name: str) -> None:
    sub_df = df[df["preprocessing"] == preprocessing].copy()
    if sub_df.empty:
        print(f"[stage7] no P9 PCA rows for preprocessing={preprocessing}; skipping")
        return
    models = sorted(sub_df["model"].unique())
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 5), squeeze=False)
    axes = axes[0]

    for ax, model in zip(axes, models):
        sub = sub_df[sub_df["model"] == model]
        for label, name, color, alpha in [
            (0, "matched", "#2a9d8f", 0.45),
            (1, "hallucinated", "#e76f51", 0.55),
        ]:
            g = sub[sub["is_hallucinated"] == label]
            ax.scatter(g["pc1"], g["pc2"], s=8, alpha=alpha, c=color, label=name, linewidths=0)
        ax.set_title(model_label(model), fontweight="bold")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, markerscale=2)

    title_mode = "mean-centered" if preprocessing == "centered" else preprocessing
    fig.suptitle(f"P9 per-name entity geometry ({title_mode} PCA)", fontweight="bold")
    fig.tight_layout()
    out = os.path.join(out_dir, out_name)
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage7] wrote {out}")


def plot_p9_pca(in_dir: str, out_dir: str) -> None:
    df = read_tsv(in_dir, "p9_entity_pca.tsv")
    if df.empty:
        print("[stage7] p9_entity_pca.tsv is empty; skipping P9 PCA figure")
        return
    if "preprocessing" not in df.columns:
        df["preprocessing"] = "standardized"
    df["pc1"] = pd.to_numeric(df["pc1"], errors="coerce")
    df["pc2"] = pd.to_numeric(df["pc2"], errors="coerce")
    df["is_hallucinated"] = pd.to_numeric(df["is_hallucinated"], errors="coerce")
    _plot_p9_pca_mode(df, out_dir, "centered", "figure_appendix_p9_pca.png")
    _plot_p9_pca_mode(
        df,
        out_dir,
        "standardized",
        "figure_appendix_p9_pca_standardized.png",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 7: make follow-up figures")
    parser.add_argument("--in_dir", required=True)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    plot_main_mechanistic_pathway(args.in_dir, args.out_dir)
    plot_hr_trends(args.in_dir, args.out_dir)
    plot_strategy_comparison(args.in_dir, args.out_dir)
    plot_p9_pca(args.in_dir, args.out_dir)
    print(f"[stage7] All figures written to {args.out_dir}")


if __name__ == "__main__":
    main()
