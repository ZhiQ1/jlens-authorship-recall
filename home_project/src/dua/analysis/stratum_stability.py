"""Section 4.1: is 100 papers per stratum enough?

The sampling design puts up to 100 papers in each of 104 (field, citation
bin) strata. This module computes the within-stratum standard deviation and
95% confidence interval of HR2, which is the evidence behind the claim that
the design has enough power to detect the citation trend.

Produces ``stratum_stability.tex`` and ``stratum_stability.json``.
"""

from __future__ import annotations

import numpy as np

from dua.analysis.loaders import MODEL_LABELS, MODELS, load_responses
from dua.analysis.style import fmt, fmt_int, save_table
from dua.config import load_config
from dua.evaluate.metrics import mean_ci

SOURCE = "dua.analysis.stratum_stability"


def stratum_table(model: str = "gpt-4o", metric: str = "hr2") -> dict:
    """Per-stratum mean, SD, CI half-width, and n."""
    cfg = load_config()
    df = load_responses(model)
    strata = []
    for field in cfg.field_keys:
        for label in cfg.bin_labels:
            sub = df[(df["field"] == field) & (df["citation_bin"] == label)]
            if sub.empty:
                continue
            mean, half, n = mean_ci(sub[metric])
            strata.append({
                "field": field, "citation_bin": label, "n": int(n),
                "mean": float(mean), "sd": float(np.std(sub[metric], ddof=1)) if n > 1 else 0.0,
                "ci95_half_width": float(half),
            })
    sds = np.array([s["sd"] for s in strata])
    cis = np.array([s["ci95_half_width"] for s in strata])
    return {
        "model": model, "metric": metric,
        "n_populated_strata": len(strata),
        "n_full_strata": int(sum(1 for s in strata if s["n"] >= cfg["sampling"]["per_stratum"])),
        "mean_sd": float(sds.mean()),
        "mean_ci95_half_width": float(cis.mean()),
        "max_sd": float(sds.max()),
        "strata": strata,
    }


def shortfall_table() -> dict:
    """Where the sample fell short of 100 per stratum, and by how much."""
    from dua.analysis.loaders import load_sample

    cfg = load_config()
    sample = load_sample()
    target = cfg["sampling"]["per_stratum"]
    rows, shortfalls = [], []
    for label in cfg.bin_labels:
        sub = sample[sample["citation_bin"] == label]
        achieved = int(len(sub))
        expected = target * len(cfg.field_keys)
        shortfalls.append({"citation_bin": label, "achieved": achieved,
                           "target": expected, "shortfall": expected - achieved})
        rows.append([label.replace("-", "--"), fmt_int(achieved), fmt_int(expected),
                     fmt_int(expected - achieved)])
    total_achieved = sum(s["achieved"] for s in shortfalls)
    total_target = cfg["sampling"]["theoretical_max"]
    rows.append([r"\textbf{Total}", rf"\textbf{{{total_achieved:,}}}",
                 rf"\textbf{{{total_target:,}}}",
                 rf"\textbf{{{total_target - total_achieved:,}}}"])
    save_table(
        "sampling_shortfall",
        [r"\textbf{Citation Bin}", r"\textbf{Sampled}", r"\textbf{Target}",
         r"\textbf{Shortfall}"],
        rows, align="lrrr", source=SOURCE, midrule_before={len(rows) - 1},
        values={"per_bin": shortfalls, "total_achieved": total_achieved,
                "total_target": total_target},
    )
    return {"per_bin": shortfalls, "total_achieved": total_achieved,
            "total_target": total_target}


def run_all() -> dict:
    per_model = {m: stratum_table(m) for m in MODELS}
    rows = [[MODEL_LABELS[m], fmt_int(per_model[m]["n_populated_strata"]),
             fmt(per_model[m]["mean_sd"]), fmt(per_model[m]["mean_ci95_half_width"])]
            for m in MODELS]
    save_table(
        "stratum_stability",
        [r"\textbf{Model}", r"\textbf{Populated strata}", r"\textbf{Mean SD}",
         r"\textbf{Mean 95\% CI ($\pm$)}"],
        rows, align="lrrr", source=SOURCE,
        values={"per_model": {m: {k: v for k, v in per_model[m].items() if k != "strata"}
                              for m in MODELS},
                "strata_gpt4o": per_model["gpt-4o"]["strata"]},
    )
    return {"stability": per_model, "shortfall": shortfall_table()}
