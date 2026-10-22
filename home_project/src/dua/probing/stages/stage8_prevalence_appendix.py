"""Stage 8: the Appendix A7 prevalence-decoding battery.

Runs every experiment in :mod:`dua.probing.stages.prevalence` over each model's
P1 states and writes their tables, figures, and the appendix snippet. Each
experiment lives in its own module there; this file only wires them together.

Usage
─────
  python -m dua.probing.stages.stage8_prevalence_appendix \
    --runs qwen3_32b=results mistral_small_3_2_24b=results/run_mistral_small_3_2_24b \
    --optimal_layers qwen3_32b:48 mistral_small_3_2_24b:22 \
    --followup_dir results/followup_results \
    --out_dir results/prevalence_appendix
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.adjusted_decoding import run_adjusted_decoding
from dua.probing.stages.prevalence.bucket_probe import plot_bucket_probe, run_citation_bucket_probe
from dua.probing.stages.prevalence.common import (  # noqa: F401  (re-exported for stages 13 and 16)
    N_SVD_COMPONENTS,
    RANDOM_SEED,
    RIDGE_ALPHAS,
    RunSpec,
    align_rows,
    find_h5_path,
    find_scored_path,
    layer_position,
    load_layer_indices,
    load_p1_embeddings,
    parse_layers,
    parse_runs,
    r2_from_predictions,
    spearman,
    svd_reduce,
    write_df,
)
from dua.probing.stages.prevalence.deciles import plot_internal_deciles, run_internal_deciles
from dua.probing.stages.prevalence.decoders import fold_safe_pca_ridge_oof  # noqa: F401
from dua.probing.stages.prevalence.external_proxy import (
    discover_external_proxy,
    run_external_proxy_decoding,
)
from dua.probing.stages.prevalence.layer_sweep import (
    plot_prevalence_depth_trajectory,
    plot_strategy_comparison,
    run_validated_strategy_layer_sweep,
    strategy_peak_summary,
)
from dua.probing.stages.prevalence.negative_controls import (
    plot_negative_controls,
    run_negative_controls,
)
from dua.probing.stages.prevalence.protocol_comparison import (
    plot_protocol_comparison,
    run_protocol_comparison,
)
from dua.probing.stages.prevalence.residuals import (
    plot_prevalence_residuals,
    run_prevalence_residual_summary,
)
from dua.probing.stages.prevalence.summary import (
    collect_stage5_stage6_summary,
    write_appendix_snippet,
)
from dua.probing.stages.prevalence.within_field import run_within_field_decoding


def ensure_dependencies() -> None:
    """Fail early if h5py is missing, and put matplotlib on the Agg backend."""
    import h5py  # noqa: F401
    import matplotlib

    matplotlib.use("Agg")


@dataclass
class AnalysisBundle:
    citation_probe: pd.DataFrame
    adjusted_decoding: pd.DataFrame
    within_field_decoding: pd.DataFrame
    deciles: pd.DataFrame
    negative_controls: pd.DataFrame
    predictions: pd.DataFrame
    protocol_comparison: pd.DataFrame


def run_model_analyses(spec: RunSpec, n_shuffles: int) -> AnalysisBundle:
    X, scored, n_model_layers = load_p1_embeddings(spec)
    X_svd = svd_reduce(X)
    protocol_comparison = run_protocol_comparison(spec, X, X_svd, scored)
    citation_probe = run_citation_bucket_probe(spec, X, scored)
    adjusted, predictions = run_adjusted_decoding(spec, X, scored, n_model_layers)
    within_field = run_within_field_decoding(spec, X, scored, n_model_layers)
    deciles = run_internal_deciles(predictions)
    real_row = adjusted[adjusted["feature_set"] == "p1_embedding_fold_safe_pca"].iloc[0]
    negative = run_negative_controls(spec, X, scored, float(real_row["r2_cv"]), n_shuffles)
    return AnalysisBundle(citation_probe, adjusted, within_field, deciles, negative, predictions, protocol_comparison)


def _concat(parts: list[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 8: prevalence appendix tables, figures, and snippet")
    parser.add_argument("--runs", nargs="+", required=True, help="Entries like model_name=/path/to/run_dir")
    parser.add_argument("--optimal_layers", nargs="+", required=True, help="Entries like model_name:48")
    parser.add_argument("--followup_dir", default="results/followup_results")
    parser.add_argument("--out_dir", default="results/prevalence_appendix")
    parser.add_argument("--negative_control_shuffles", type=int, default=10)
    args = parser.parse_args()

    ensure_dependencies()

    runs = parse_runs(args.runs)
    layers = parse_layers(args.optimal_layers)
    missing = sorted(set(runs) - set(layers))
    if missing:
        raise ValueError(f"Missing --optimal_layers entries for: {missing}")
    specs = [RunSpec(name, path, layers[name]) for name, path in runs.items()]
    out_dir = Path(args.out_dir).expanduser().resolve()
    fig_dir = out_dir / "figures"
    followup_dir = Path(args.followup_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    bundles: list[AnalysisBundle] = []
    validated_layer_parts: list[pd.DataFrame] = []
    for spec in specs:
        print(f"[stage8] {spec.model}: running P1 prevalence appendix analyses")
        bundles.append(run_model_analyses(spec, args.negative_control_shuffles))
        print(f"[stage8] {spec.model}: running validated strategy/layer prevalence sweep")
        validated_layer_parts.append(run_validated_strategy_layer_sweep(spec))

    citation_probe = _concat([b.citation_probe for b in bundles])
    adjusted = _concat([b.adjusted_decoding for b in bundles])
    within_field = _concat([b.within_field_decoding for b in bundles])
    deciles = _concat([b.deciles for b in bundles])
    negative = _concat([b.negative_controls for b in bundles])
    predictions = _concat([b.predictions for b in bundles])
    protocol_comparison = _concat([b.protocol_comparison for b in bundles])
    validated_layers = _concat(validated_layer_parts)
    validated_peaks = strategy_peak_summary(validated_layers)
    residual_summary = run_prevalence_residual_summary(predictions)
    summary = collect_stage5_stage6_summary(specs, followup_dir)

    write_df(out_dir / "citation_bucket_probe.csv", citation_probe)
    write_df(out_dir / "adjusted_prevalence_decoding.csv", adjusted)
    write_df(out_dir / "within_field_prevalence_decoding.csv", within_field)
    write_df(out_dir / "p1_prevalence_predictions.csv", predictions)
    write_df(out_dir / "internal_prevalence_deciles.csv", deciles)
    write_df(out_dir / "prevalence_residual_summary.csv", residual_summary)
    write_df(out_dir / "negative_controls.csv", negative)
    write_df(out_dir / "prevalence_decoding_protocol_comparison.csv", protocol_comparison)
    write_df(out_dir / "validated_strategy_layer_prevalence.csv", validated_layers)
    write_df(out_dir / "validated_strategy_peak_r2.csv", validated_peaks)
    write_df(out_dir / "appendix_summary_tables.csv", summary)

    proxy_path = discover_external_proxy([spec.run_dir for spec in specs])
    run_external_proxy_decoding(proxy_path, predictions, out_dir)

    plot_prevalence_depth_trajectory(validated_layers, fig_dir)
    plot_strategy_comparison(validated_peaks, fig_dir)
    plot_bucket_probe(citation_probe, fig_dir)
    plot_internal_deciles(deciles, fig_dir)
    plot_prevalence_residuals(predictions, fig_dir)
    plot_negative_controls(negative, fig_dir)
    plot_protocol_comparison(protocol_comparison, fig_dir)

    write_appendix_snippet(
        out_dir / "appendix_section_snippet.md",
        summary=summary,
        adjusted=adjusted,
        within_field=within_field,
        deciles=deciles,
        negative=negative,
    )
    print(f"[stage8] Wrote prevalence appendix outputs to {out_dir}")


if __name__ == "__main__":
    main()
