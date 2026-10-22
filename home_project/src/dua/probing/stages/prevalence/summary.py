"""Collects Stage 5/6 results and writes the appendix prose snippet.

Outputs ``appendix_summary_tables.csv`` and ``appendix_section_snippet.md``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    RunSpec,
    find_results_dir,
    model_label,
    read_csv_if_exists,
    write_text,
)


def collect_stage5_stage6_summary(specs: list[RunSpec], followup_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for spec in specs:
        results_dir = find_results_dir(spec.run_dir)
        prev = read_csv_if_exists(results_dir / "embedding_prevalence.csv")
        if not prev.empty:
            p1 = prev[prev["strategy"] == "p1"].copy()
            if not p1.empty:
                best = p1.loc[p1["r2_cv"].astype(float).idxmax()]
                rows.append({
                    "model": spec.model,
                    "evidence": "stage5_best_p1_prevalence_decoding",
                    "metric": "r2_cv",
                    "value": round(float(best["r2_cv"]), 6),
                    "detail": f"layer {int(best['layer_idx'])}, rho {float(best.get('spearman_rho_cv', np.nan)):.3f}",
                })
        med = read_csv_if_exists(results_dir / "mediation_results.csv")
        if not med.empty:
            sub = med[(med["strategy"] == "p1") & (med["hr_metric"].str.lower() == "hr2")]
            if not sub.empty:
                row = sub.iloc[0]
                rows.append({
                    "model": spec.model,
                    "evidence": "stage5_p1_hr2_mediation",
                    "metric": "pct_mediated",
                    "value": round(float(row["pct_mediated"]), 6),
                    "detail": f"indirect_ab {float(row['indirect_ab']):.4g}",
                })

    for filename, evidence, metric_col in [
        ("probe_hallucination_auc.csv", "stage6_p1_hallucination_probe", "auroc"),
        ("probe_hr2_regression.csv", "stage6_p1_hr2_regression_probe", "r2_cv"),
        ("p9_entity_geometry.csv", "stage6_p9_entity_geometry", "probe_auroc"),
    ]:
        df = read_csv_if_exists(followup_dir / filename)
        if df.empty or metric_col not in df.columns:
            continue
        if "label_definition" in df.columns:
            preferred = df[df["label_definition"].isin(["hr2_gt_0.5", "hr2_ge_0.5"])]
            if not preferred.empty:
                df = preferred
        for _, row in df.iterrows():
            rows.append({
                "model": row["model"],
                "evidence": evidence,
                "metric": metric_col,
                "value": round(float(row[metric_col]), 6),
                "detail": f"layer {row.get('layer_idx', '')}",
            })
    return pd.DataFrame(rows)


def write_appendix_snippet(
    path: Path,
    summary: pd.DataFrame,
    adjusted: pd.DataFrame,
    within_field: pd.DataFrame,
    deciles: pd.DataFrame,
    negative: pd.DataFrame,
) -> None:
    lines = [
        "# Mechanistic Evidence for Prevalence Encoding",
        "",
        "## Setup",
        "",
        "We treat citation prevalence as the primary latent quantity and ask whether it is recoverable from the model's P1 hidden state at each model's pre-specified optimal layer. The appendix tables report cross-validated decoding from embeddings, metadata-adjusted decoding, shuffled-label negative controls, and downstream hallucination summaries.",
        "",
        "## Internal Prevalence Encoding",
        "",
    ]
    best = adjusted[adjusted["feature_set"] == "p1_embedding_fold_safe_pca"] if not adjusted.empty else pd.DataFrame()
    for _, row in best.iterrows():
        lines.append(
            f"- {model_label(row['model'])}: P1 embeddings decode log citations with CV R2={float(row['r2_cv']):.3f} "
            f"and Spearman rho={float(row['spearman_rho_cv']):.3f} at layer {int(row['layer_idx'])}."
        )
    inc = adjusted[adjusted["feature_set"] == "incremental_embedding_over_metadata"] if not adjusted.empty else pd.DataFrame()
    if not inc.empty:
        lines += ["", "The metadata-adjusted rows show the incremental contribution of P1 embeddings beyond field, year, author count, and title length controls:"]
        for _, row in inc.iterrows():
            lines.append(f"- {model_label(row['model'])}: incremental CV R2={float(row['r2_cv']):.3f}.")

    p1_within = (
        within_field[within_field["feature_set"] == "p1_embedding_fold_safe_pca"]
        if not within_field.empty and "feature_set" in within_field.columns
        else pd.DataFrame()
    )
    if not p1_within.empty:
        lines += [
            "",
            "Within-field decoding tests the field/topic confound by fitting separate P1 decoders inside each discipline. If P1 only encoded coarse field identity, these within-field rows should collapse toward zero.",
        ]
        for model, grp in p1_within.groupby("model", sort=True):
            vals = pd.to_numeric(grp["r2_cv"], errors="coerce").dropna()
            rhos = pd.to_numeric(grp["spearman_rho_cv"], errors="coerce").dropna()
            if vals.empty:
                continue
            lines.append(
                f"- {model_label(model)}: within-field P1 decoding mean CV R2={float(vals.mean()):.3f} "
                f"across {len(vals)} fields; mean Spearman rho={float(rhos.mean()):.3f}."
            )

    lines += [
        "",
        "## Robustness Checks",
        "",
        "Citation-bucket probes test whether the same hidden state separates low-prevalence from high-prevalence papers. Negative controls shuffle citation labels before fitting the same decoding pipeline.",
    ]
    if not negative.empty:
        ctrl = negative.groupby("model").agg(mean_shuffle_r2=("r2_cv", "mean"), real_r2=("real_embedding_r2_cv", "first")).reset_index()
        for _, row in ctrl.iterrows():
            lines.append(
                f"- {model_label(row['model'])}: shuffled-label mean CV R2={float(row['mean_shuffle_r2']):.3f}, "
                f"real-label CV R2={float(row['real_r2']):.3f}."
            )

    lines += [
        "",
        "## Hallucination Connection",
        "",
        "The prevalence-score grouping table sorts papers by out-of-fold P1-decoded prevalence and then reports mean HR2. A monotone decrease in HR2 across these groups supports the interpretation that the prevalence state is behaviorally relevant rather than merely correlational.",
    ]
    if not deciles.empty:
        for model, grp in deciles.groupby("model"):
            lo = grp.sort_values("internal_prevalence_decile").iloc[0]
            hi = grp.sort_values("internal_prevalence_decile").iloc[-1]
            lines.append(
                f"- {model_label(model)}: mean HR2 changes from {float(lo['mean_hr2']):.3f} in the lowest-scoring group "
                f"to {float(hi['mean_hr2']):.3f} in the highest-scoring group."
            )

    lines += [
        "",
        "## P9 Entity-Level Supplement",
        "",
        "Stage 6 P9 entity-geometry results are included as supporting evidence: they test whether matched and hallucinated author-name entities occupy separable regions in per-name hidden-state space. This is a downstream supplement to the prevalence-first P1 analysis, not the main mechanism.",
        "",
        "## Summary Tables",
        "",
        "The generated CSVs are intended to map directly to appendix tables and figures: `validated_strategy_layer_prevalence.csv`, `validated_strategy_peak_r2.csv`, `citation_bucket_probe.csv`, `adjusted_prevalence_decoding.csv`, `within_field_prevalence_decoding.csv`, `p1_prevalence_predictions.csv`, `internal_prevalence_deciles.csv`, `prevalence_residual_summary.csv`, `negative_controls.csv`, `prevalence_decoding_protocol_comparison.csv`, and `appendix_summary_tables.csv`.",
        "",
    ]
    if not summary.empty:
        lines += ["Key reused Stage 5/6 evidence:"]
        for _, row in summary.iterrows():
            lines.append(f"- {model_label(row['model'])}, {row['evidence']}: {row['metric']}={float(row['value']):.3f} ({row['detail']}).")
    write_text(path, "\n".join(lines))
