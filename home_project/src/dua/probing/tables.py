"""Appendix A8: tables and figures from the hidden-state probing artifacts.

Reads the shipped CSVs under ``data/release/probing/`` -- the outputs of the
GPU stages in ``dua.probing.stages`` -- and turns them into the appendix
tables. Running this needs no GPU and no model weights; re-deriving the CSVs
themselves does. See ``README.md``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from dua.analysis.style import apply_style, fmt, fmt_int, save_figure, save_table
from dua.config import load_config

SOURCE = "dua.probing.tables"

MODEL_LABELS = {"qwen3_32b": "Qwen3-32B", "mistral_small_3_2_24b": "Mistral-24B"}
MODEL_ORDER = ("qwen3_32b", "mistral_small_3_2_24b")
# Keys as they appear in the shipped CSVs. Getting one wrong silently drops a
# row, so every lookup below goes through this table rather than a literal.
FEATURE_LABELS = {
    "metadata_controls": "Metadata controls",
    "metadata_controls_no_field": "Metadata controls (no field)",
    "p1_embedding_fold_safe_pca": "P1 embedding",
    "metadata_plus_p1_embedding_fold_safe_pca": "Metadata + P1",
}
ADJUSTED_ROWS = ["metadata_controls", "p1_embedding_fold_safe_pca",
                 "metadata_plus_p1_embedding_fold_safe_pca"]


def probing_dir() -> Path:
    return load_config().path("release") / "probing"


def _read(name: str) -> pd.DataFrame:
    path = probing_dir() / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. It is produced by the GPU stages in "
            "dua.probing.stages; see README.md for which stage writes it."
        )
    return pd.read_csv(path)


def _label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def table_prevalence_decoding() -> dict:
    """Table A18: P1 hidden states predict log(citations + 1)."""
    df = _read("validated_strategy_peak_r2.csv")
    p1 = df[df["strategy"] == "p1"].set_index("model")
    rows, values = [], {}
    for model in MODEL_ORDER:
        if model not in p1.index:
            continue
        r = p1.loc[model]
        rows.append([_label(model), fmt_int(r["peak_layer_idx"]),
                     f"{r['peak_layer_depth_pct']:.1f}\\%",
                     fmt(r["peak_r2_cv"]), fmt(r["peak_spearman_rho_cv"])])
        values[model] = {"layer": int(r["peak_layer_idx"]),
                         "depth_pct": float(r["peak_layer_depth_pct"]),
                         "cv_r2": float(r["peak_r2_cv"]),
                         "spearman_rho": float(r["peak_spearman_rho_cv"]),
                         "n": int(r["n"])}
    save_table(
        "prevalence_decoding",
        [r"\textbf{Model}", r"\textbf{Layer}", r"\textbf{Depth}", r"\textbf{CV $R^2$}",
         r"\textbf{Spearman $\rho$}"],
        rows, align="lrrrr", source=SOURCE, values={"p1_decoding": values},
    )
    return values


def table_adjusted_decoding() -> dict:
    """Table A19: decoding after metadata controls."""
    df = _read("adjusted_prevalence_decoding.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model].set_index("feature_set")
        missing = [f for f in ADJUSTED_ROWS if f not in sub.index]
        if missing:
            raise KeyError(
                f"{model}: adjusted_prevalence_decoding.csv is missing feature "
                f"sets {missing}. Present: {sorted(sub.index)}. Silently "
                "skipping them would drop the numbers Appendix A8.2 quotes."
            )
        for feature in ADJUSTED_ROWS:
            r = sub.loc[feature]
            rows.append([_label(model), FEATURE_LABELS[feature],
                         fmt(r["r2_cv"]), fmt(r["spearman_rho_cv"])])
            values.setdefault(model, {})[feature] = {
                "cv_r2": float(r["r2_cv"]), "spearman_rho": float(r["spearman_rho_cv"])}
    midrule = {len(ADJUSTED_ROWS)} if len(MODEL_ORDER) > 1 else set()
    save_table(
        "adjusted_decoding",
        [r"\textbf{Model}", r"\textbf{Feature set}", r"\textbf{CV $R^2$}",
         r"\textbf{Spearman $\rho$}"],
        rows, align="llrr", source=SOURCE, midrule_before=midrule,
        values={"adjusted_decoding": values},
    )
    return values


def table_negative_control() -> dict:
    """Table A20: shuffled-label controls collapse to zero."""
    df = _read("negative_controls.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model]
        if sub.empty:
            continue
        real = float(sub["real_embedding_r2_cv"].iloc[0])
        shuffled = float(sub["r2_cv"].mean())
        rows.append([_label(model), fmt(real), fmt(shuffled)])
        values[model] = {"real_cv_r2": real, "shuffled_mean_cv_r2": shuffled,
                         "n_shuffles": int(len(sub)),
                         "shuffled_max_cv_r2": float(sub["r2_cv"].max())}
    save_table(
        "negative_control",
        [r"\textbf{Model}", r"\textbf{Real-label CV $R^2$}",
         r"\textbf{Shuffled-label mean CV $R^2$}"],
        rows, align="lrr", source=SOURCE, values={"negative_controls": values},
    )
    return values


def table_title_residual() -> dict:
    """Appendix A8.2: P1 survives residualising on a title-only baseline."""
    df = _read("title_vs_p1_comparison.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model]
        if sub.empty:
            continue
        r = sub.iloc[0]
        rows.append([_label(model), fmt(r["title_only_r2_cv"]),
                     fmt(r["p1_on_raw_log_citation_r2_cv"]),
                     fmt(r["p1_on_title_residual_r2_cv"])])
        values[model] = {
            "title_only_cv_r2": float(r["title_only_r2_cv"]),
            "p1_cv_r2": float(r["p1_on_raw_log_citation_r2_cv"]),
            "p1_on_title_residual_cv_r2": float(r["p1_on_title_residual_r2_cv"]),
            "n": int(r["n"]),
        }
    save_table(
        "title_residual",
        [r"\textbf{Model}", r"\textbf{Title-only $R^2$}", r"\textbf{P1 $R^2$}",
         r"\textbf{P1 on title residual $R^2$}"],
        rows, align="lrrr", source=SOURCE, values={"title_residual": values},
    )
    return values


def table_within_field() -> dict:
    """Appendix A8.2: decoding within each field, so field identity is fixed."""
    df = _read("within_field_prevalence_decoding.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model]
        if sub.empty:
            continue
        record = {}
        for feature in ("p1_embedding_fold_safe_pca", "metadata_controls_no_field"):
            part = sub[sub["feature_set"] == feature]
            if part.empty:
                continue
            record[feature] = {"mean_cv_r2": float(part["r2_cv"].mean()),
                               "mean_spearman_rho": float(part["spearman_rho_cv"].mean()),
                               "n_fields": int(len(part))}
        values[model] = record
        p1 = record.get("p1_embedding_fold_safe_pca", {})
        meta = record.get("metadata_controls_no_field", {})
        rows.append([_label(model), fmt(p1.get("mean_cv_r2", float("nan"))),
                     fmt(p1.get("mean_spearman_rho", float("nan"))),
                     fmt(meta.get("mean_cv_r2", float("nan")))])
    save_table(
        "within_field_decoding",
        [r"\textbf{Model}", r"\textbf{Mean P1 CV $R^2$}", r"\textbf{Mean $\rho$}",
         r"\textbf{Mean metadata CV $R^2$}"],
        rows, align="lrrr", source=SOURCE, values={"within_field": values},
    )
    return values


def table_bucket_probe() -> dict:
    """Table A21: linear decodability across citation regimes."""
    df = _read("citation_bucket_probe.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model]
        for _, r in sub.iterrows():
            rows.append([_label(model), str(r["label_definition"]).replace("_", r"\_"),
                         fmt_int(r["n"]), fmt(r["auroc"]),
                         fmt(r["balanced_accuracy_at_0_5"]), fmt(r["auprc"])])
            values.setdefault(model, {})[str(r["label_definition"])] = {
                "n": int(r["n"]), "auroc": float(r["auroc"]),
                "balanced_accuracy": float(r["balanced_accuracy_at_0_5"]),
                "auprc": float(r["auprc"])}
    save_table(
        "bucket_probe",
        [r"\textbf{Model}", r"\textbf{Label}", r"\textbf{N}", r"\textbf{AUROC}",
         r"\textbf{Balanced acc.}", r"\textbf{AUPRC}"],
        rows, align="llrrrr", source=SOURCE, values={"bucket_probe": values},
    )
    return values


def table_internal_deciles() -> dict:
    """Table A22 and Figure 6: HR2 by P1-decoded prevalence decile."""
    df = _read("internal_prevalence_deciles.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model].sort_values("internal_prevalence_decile")
        if sub.empty:
            continue
        values[model] = sub.to_dict(orient="records")
        for _, r in sub.iterrows():
            rows.append([_label(model), fmt_int(r["internal_prevalence_decile"]),
                         fmt_int(r["n"]), fmt(r["mean_predicted_log_citation"], 2),
                         fmt_int(r["mean_citation_count"]), fmt(r["mean_hr2"])])
    save_table(
        "internal_prevalence_deciles",
        [r"\textbf{Model}", r"\textbf{Decile}", r"\textbf{N}",
         r"\textbf{Decoded $\log(c{+}1)$}", r"\textbf{Mean citations}",
         r"\textbf{Mean HR$_2$}"],
        rows, align="lrrrrr", source=SOURCE, values={"deciles": values},
    )

    apply_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    for model, colour in zip(MODEL_ORDER, ("#1f77b4", "#d62728"), strict=False):
        sub = df[df["model"] == model].sort_values("internal_prevalence_decile")
        if sub.empty:
            continue
        ax.plot(sub["internal_prevalence_decile"], sub["mean_hr2"], marker="o",
                markersize=4, linewidth=1.6, color=colour, label=_label(model))
    ax.set_xlabel("P1-decoded prevalence decile")
    ax.set_ylabel(r"Mean HR$_2$")
    ax.set_xticks(range(1, 11))
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "fig_internal_prevalence_deciles", {"deciles": values}, source=SOURCE)
    return values


def table_mediation() -> dict:
    """Table A23: how much of the citation-hallucination link runs through P1."""
    df = _read("modern_mediation_summary.csv")
    primary = df[(df["mediator"].str.startswith("p1_prevalence"))
                 & (df["method"] == "mediation_package")]
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = primary[primary["model"] == model]
        if sub.empty:
            continue
        r = sub.iloc[0]
        rows.append([_label(model), fmt(r["acme"], 4), fmt(r["ade"], 4),
                     fmt(r["total_effect"], 4),
                     f"{100 * r['prop_mediated']:.1f}\\%"])
        values[model] = {
            "acme": float(r["acme"]), "acme_ci": [float(r["acme_lo"]), float(r["acme_hi"])],
            "ade": float(r["ade"]), "total_effect": float(r["total_effect"]),
            "prop_mediated": float(r["prop_mediated"]),
            "prop_mediated_ci": [float(r["prop_lo"]), float(r["prop_hi"])],
            "n_sims": int(r["sims"]),
        }
    save_table(
        "mediation_summary",
        [r"\textbf{Model}", r"\textbf{ACME}", r"\textbf{ADE}", r"\textbf{Total}",
         r"\textbf{Prop.\ mediated}"],
        rows, align="lrrrr", source=SOURCE, values={"mediation": values},
    )
    return values


def _position_probe_summary(base: Path) -> dict | None:
    """Stage 24's ``eval_high`` arms: the control spread and the probe direction.

    Stage 15 draws *one* norm-matched control direction (a single seed, two
    alphas). Stage 24 re-runs that control arm at ``n_random_seeds`` seeds and
    adds a probe-direction arm, both at alpha = 2 on the same ``eval_high``
    pool. Appendix A8.8 and Table A25 quote these numbers -- the 30--48% and
    48--52% control ranges, and the 58% / 64% probe result -- not Stage 15's.

    Returns ``None`` when the Stage 24 artifact is absent, so a partial release
    still builds a table off Stage 15 alone.
    """
    path = base / "position_probe" / "position_probe_results_eval_high.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    # Every quoted arm writes the vector at every position; the p1_and_gen and
    # prompt_only variants are the E3 ablation and are not what A8.8 reports.
    at_all = df[df["positions"] == "all"]

    def induce_pct(vector: str) -> float:
        sub = at_all[(at_all["condition"] == "induce") & (at_all["vector"] == vector)]
        return float(sub["hallucination_rate_pct"].iloc[0]) if not sub.empty else float("nan")

    baseline = df[df["condition"] == "baseline"]
    controls = at_all[at_all["condition"] == "random_control"]
    by_seed = {int(s): float(v) for s, v in zip(
        controls["seed"], controls["hallucination_rate_pct"], strict=True)}
    return {
        "baseline_pct": float(baseline["hallucination_rate_pct"].iloc[0])
        if not baseline.empty else float("nan"),
        "steered_pct": induce_pct("diff_of_means"),
        "probe_pct": induce_pct("probe"),
        "random_pct_by_seed": by_seed,
        "random_pct_min": min(by_seed.values()) if by_seed else float("nan"),
        "random_pct_max": max(by_seed.values()) if by_seed else float("nan"),
        "n_control_seeds": len(by_seed),
        "alpha": float(at_all["alpha"].iloc[0]) if not at_all.empty else float("nan"),
        "n": int(df["n"].iloc[0]),
    }


def table_steering() -> dict:
    """Appendix A8.8 and Table A25: steering along the prevalence direction.

    The comparison that matters is against a norm-matched random direction, not
    against baseline: any large enough perturbation degrades generation, so the
    question is whether *this* direction does more damage than a random one of
    the same size.

    Both stages are reported. Stage 14/15 give the alpha dose curve against one
    control direction; Stage 24 gives the five-seed control spread and the
    probe arm, which is what the printed table quotes.
    """
    rows, values = [], {}
    for model in MODEL_ORDER:
        base = probing_dir() / "steering" / model
        if not (base / "steering_results.csv").exists():
            continue
        steer = pd.read_csv(base / "steering_results.csv")
        control = pd.read_csv(base / "steering_results_norm_matched_control.csv")
        meta = {}
        meta_path = base / "steering_meta.json"
        if meta_path.exists():
            import json as _json

            meta = _json.loads(meta_path.read_text(encoding="utf-8"))

        spread = _position_probe_summary(base)
        record: dict = {"n_control_shuffles_stage15": meta.get("n_control_shuffles"),
                        "n_control_seeds_stage24": spread["n_control_seeds"] if spread else 0,
                        "control_spread": spread, "pools": {}}
        for pool in ("eval_high", "eval_low"):
            s_pool = steer[steer["pool"] == pool]
            c_pool = control[control["pool"] == pool]
            if s_pool.empty:
                continue
            baseline = s_pool[s_pool["condition"] == "baseline"]
            steered = s_pool[s_pool["condition"] == "steering"]
            randoms = c_pool[c_pool["direction"] == "random"]
            entry = {
                "baseline_pct": float(baseline["hallucination_rate_pct"].iloc[0])
                if not baseline.empty else float("nan"),
                "steered_pct_by_alpha": dict(zip(
                    steered["alpha"].astype(float), steered["hallucination_rate_pct"].astype(float),
                    strict=True)),
                "random_pct_by_alpha": dict(zip(
                    randoms["alpha"].astype(float), randoms["hallucination_rate_pct"].astype(float),
                    strict=True)),
                "n": int(s_pool["n"].iloc[0]),
            }
            record["pools"][pool] = entry
            if pool != "eval_high":
                continue
            if spread:
                rows.append([_label(model), fmt_int(spread["n"]),
                             fmt(spread["baseline_pct"], 1), fmt(spread["steered_pct"], 1),
                             fmt(spread["probe_pct"], 1),
                             f'{fmt(spread["random_pct_min"], 1)}--{fmt(spread["random_pct_max"], 1)}'])
            else:
                # No Stage 24 artifact: fall back to the single Stage 15 control
                # at the strongest alpha, and say so by leaving the probe blank.
                worst_steer = max(entry["steered_pct_by_alpha"].values(), default=float("nan"))
                worst_random = max(entry["random_pct_by_alpha"].values(), default=float("nan"))
                rows.append([_label(model), fmt_int(entry["n"]),
                             fmt(entry["baseline_pct"], 1), fmt(worst_steer, 1),
                             fmt(None), fmt(worst_random, 1)])
        values[model] = record

    save_table(
        "steering",
        [r"\textbf{Model}", r"\textbf{N}", r"\textbf{Baseline \%}",
         r"\textbf{Steered \%}", r"\textbf{Probe dir.\ \%}",
         r"\textbf{Norm-matched random \%}"],
        rows, align="lrrrrr", source=SOURCE, values={"steering": values},
    )
    return values


def figure_strategy_comparison() -> dict:
    """Figure A7: peak decoding by extraction position, P1 through P5."""
    df = _read("validated_strategy_peak_r2.csv")
    apply_style()
    import matplotlib.pyplot as plt

    strategies = ["p1", "p2", "p3", "p4", "p5"]
    present = [s for s in strategies if s in set(df["strategy"])]
    x = np.arange(len(present))
    width = 0.38

    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    values = {}
    for i, (model, colour) in enumerate(zip(MODEL_ORDER, ("#1f77b4", "#d62728"), strict=False)):
        sub = df[df["model"] == model].set_index("strategy")
        heights = [float(sub.loc[s, "peak_r2_cv"]) if s in sub.index else np.nan
                   for s in present]
        ax.bar(x + (i - 0.5) * width, heights, width, color=colour, label=_label(model))
        values[model] = dict(zip(present, heights, strict=True))
    ax.set_xticks(x)
    ax.set_xticklabels([s.upper() for s in present])
    ax.set_xlabel("Extraction position")
    ax.set_ylabel(r"Peak CV $R^2$")
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "fig_strategy_comparison",
                {"peak_cv_r2_by_strategy": values}, source=SOURCE)
    return values


def figure_prevalence_depth() -> dict:
    """Figure A8: layer-wise decoding trajectory for P1 and P4."""
    df = _read("validated_strategy_layer_prevalence.csv")
    apply_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    values: dict = {}
    styles = {"p1": "-", "p4": "--"}
    for model, colour in zip(MODEL_ORDER, ("#1f77b4", "#d62728"), strict=False):
        for strategy, style in styles.items():
            sub = (df[(df["model"] == model) & (df["strategy"] == strategy)]
                   .sort_values("layer_idx"))
            if sub.empty:
                continue
            ax.plot(sub["layer_idx"], sub["r2_cv"], style, color=colour, linewidth=1.5,
                    label=f"{_label(model)} {strategy.upper()}")
            values.setdefault(model, {})[strategy] = {
                "layers": sub["layer_idx"].tolist(), "cv_r2": sub["r2_cv"].tolist()}
    ax.set_xlabel("Layer index")
    ax.set_ylabel(r"CV $R^2$")
    ax.legend(fontsize=7)
    fig.tight_layout()
    save_figure(fig, "fig_prevalence_depth_trajectory",
                {"layer_trajectory": values}, source=SOURCE)
    return values


def table_p9_entity() -> dict:
    """Table A24: the P9 entity-level probe, one row per model.

    The unit is a generated author name, and the imbalance is the point: ~48-51k
    hallucinated against ~1.3k matched. AUROC is high while AUPRC lift is barely
    above 1.0, because the base rate is already 97%.

    ``centroid_l2_over_pooled_rms`` is in units of within-class scatter, which
    makes it comparable across models with different activation norms.
    """
    df = _read("p9_robustness_summary.csv")
    rows, values = [], {}
    for model in MODEL_ORDER:
        sub = df[df["model"] == model]
        if sub.empty:
            continue
        r = sub.iloc[0]
        entry = {
            "layer_idx": int(r["layer_idx"]),
            "layer_depth_pct": float(r["layer_depth_pct"]),
            "n_names": int(r["n_names"]),
            "n_matched": int(r["n_matched"]),
            "n_hallucinated": int(r["n_hallucinated"]),
            "hallucinated_positive_rate": float(r["hallucinated_positive_rate"]),
            "probe_auroc": float(r["probe_auroc"]),
            "probe_auprc": float(r["probe_auprc"]),
            "probe_auprc_lift_over_baseline": float(r["probe_auprc_lift_over_baseline"]),
            "probe_balanced_accuracy": float(r["probe_balanced_accuracy"]),
            "centroid_l2_over_pooled_rms": float(r["centroid_l2_over_pooled_rms"]),
            "nearest_centroid_balanced_accuracy": float(r["nearest_centroid_balanced_accuracy"]),
        }
        values[model] = entry
        rows.append([_label(model), fmt_int(entry["n_matched"]),
                     fmt_int(entry["n_hallucinated"]),
                     fmt(entry["probe_auroc"]),
                     fmt(entry["probe_auprc_lift_over_baseline"]),
                     fmt(entry["centroid_l2_over_pooled_rms"]),
                     fmt(entry["nearest_centroid_balanced_accuracy"])])

    save_table(
        "p9_entity",
        [r"\textbf{Model}", r"\textbf{Matched}", r"\textbf{Halluc.}",
         r"\textbf{AUROC}", r"\textbf{AUPRC lift}", r"\textbf{Norm. centroid}",
         r"\textbf{NC bal.\ acc.}"],
        rows, align="lrrrrrr", source=SOURCE, values={"p9_entity": values},
    )
    return values


def run_all() -> dict:
    return {
        "prevalence_decoding": table_prevalence_decoding(),
        "adjusted_decoding": table_adjusted_decoding(),
        "negative_control": table_negative_control(),
        "title_residual": table_title_residual(),
        "within_field": table_within_field(),
        "bucket_probe": table_bucket_probe(),
        "internal_deciles": table_internal_deciles(),
        "mediation": table_mediation(),
        "steering": table_steering(),
        "p9_entity": table_p9_entity(),
        "strategy_comparison": figure_strategy_comparison(),
        "depth_trajectory": figure_prevalence_depth(),
    }
