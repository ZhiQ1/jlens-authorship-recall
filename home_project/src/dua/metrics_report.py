"""Collect every number the paper quotes in prose into one file.

The rule this exists to enforce: no number is typed into the LaTeX by hand.
Tables are generated ``.tex`` files the paper ``\\input``s; the values that
appear mid-sentence come from ``results/metrics/metrics.json``.

Each entry records the value, where it appears in the paper, and what the
paper currently prints, so a camera-ready refresh is a diff rather than a
manual re-read.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dua.config import load_config
from dua.io import write_json


def _safe(fn, default=None):
    """Run a collector, returning a recorded error instead of aborting.

    A missing optional artifact -- the probing CSVs, the surname tallies --
    should leave a hole in the report, not stop the other forty numbers from
    being collected.
    """
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}", "value": default}


def collect() -> dict[str, Any]:
    from dua.analysis import (
        author_count,
        eval_agreement,
        hr_decomposition,
        regression,
        results,
        stratum_stability,
        title_length,
    )
    from dua.analysis.loaders import load_all_responses, load_sample

    report: dict[str, Any] = {}

    # -- Section 2: the corpus ------------------------------------------
    cfg = load_config()
    report["dataset"] = {
        "oag_pool_size": {"value": cfg["dataset"]["oag_pool_size"],
                          "paper": "Sec 2.1", "printed": "9,999,863"},
        "curated_size": {"value": cfg["dataset"]["curated_size"],
                         "paper": "Sec 2.1", "printed": "1,921,209"},
        "note": "These are config constants, not recomputed. Recompute them "
                "with `dua filter` against the OAG pool; see README.md.",
    }

    # -- Section 4.1: the evaluation sample -----------------------------
    sample = load_sample()
    report["evaluation_sample"] = {
        "n_papers": {"value": int(len(sample)), "paper": "Sec 4.1", "printed": "9,108"},
        "theoretical_max": {"value": cfg["sampling"]["theoretical_max"],
                            "paper": "Sec 4.1", "printed": "10,400"},
        "mean_authors": {"value": float(sample["n_authors"].mean()),
                         "paper": "Table 2 total / Sec 4.4",
                         "printed": "3.8 in Table 2, 3.7 in Sec 4.4"},
        "mean_citations": {"value": float(sample["citations"].mean()),
                           "paper": "Table 2 total", "printed": "457"},
        "median_citations": {"value": float(sample["citations"].median())},
    }
    report["stratum_stability"] = _safe(stratum_stability.run_all)

    # -- Section 5: results ---------------------------------------------
    report["headline"] = _safe(results.headline_numbers)
    report["headline_paper_values"] = {
        "hr2_lowest_bin_all_models": "> 0.98",
        "hr2_highest_bin": {"gpt-4o": 0.364, "deepseek-r1": 0.362,
                            "claude-sonnet-4.5": 0.169},
        "abstract_range": "over 98% -> under 36.4%",
        "conclusion_range": "16.9-36.4%",
    }
    report["spearman_by_field"] = _safe(
        lambda: results.spearman_by_field("hr2").to_dict(orient="records"))

    # -- Section 4.5 / Appendix A6 --------------------------------------
    report["evaluator_agreement"] = _safe(eval_agreement.agreement_stats)
    report["evaluator_agreement_paper_values"] = {
        "hr2_pearson_r": 0.969, "hr2_rmse": 0.067, "hr2_mae": 0.010,
        "hr2_agreement_within_0.1": 0.969, "hr3_pearson_r": 0.963,
    }
    report["hr_decomposition"] = _safe(hr_decomposition.table_hr4_hr5_binwise)
    report["author_count"] = _safe(author_count.output_scaling)
    report["title_length"] = _safe(title_length.table_title_length)
    report["regression"] = _safe(
        lambda: {
            "fits": [{k: v for k, v in f.items() if k != "summary_text"}
                     for f in regression.table_regression_summary()["fits"]],
            "paper_values": {"glm_hr2_beta": -0.440, "glm_hr2_z": -26.6,
                             "glm_hr4_beta": -0.414, "glm_hr4_z": -28.1,
                             "lmm_hr2_beta": -0.030, "lmm_hr2_z": -40.4,
                             "icc": 0.02, "var_field": 0.001, "n": 9107},
        })

    # -- Section 7 -------------------------------------------------------
    def probing():
        from dua.probing import tables

        return {
            "prevalence_decoding": tables.table_prevalence_decoding(),
            "title_residual": tables.table_title_residual(),
            "mediation": tables.table_mediation(),
            "paper_values": {"qwen_r2": 0.615, "mistral_r2": 0.585,
                             "title_only_r2": 0.13, "metadata_r2": 0.039,
                             "mediated_qwen": 0.673, "mediated_mistral": 0.519},
        }

    report["probing"] = _safe(probing)

    # -- integrity --------------------------------------------------------
    responses = load_all_responses()
    report["integrity"] = {
        "n_response_rows": int(len(responses)),
        "n_models": int(responses["model"].nunique()),
        "papers_per_model": responses.groupby("model").size().to_dict(),
        "all_models_cover_same_papers": bool(
            responses.groupby("model")["paper_id"].apply(frozenset).nunique() == 1),
    }
    return report


def build(path: str | Path | None = None) -> Path:
    cfg = load_config()
    path = Path(path) if path else cfg.path("metrics") / "metrics.json"
    return write_json(path, collect(), seed=cfg.seed, source="dua.metrics_report")
