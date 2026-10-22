"""Appendix A6.3: splitting HR2 into fabrication (HR4) and omission (HR5).

The question this answers is whether the citation trend in HR2 hides two
opposing trends. It does not: the two components track each other to within
0.022 at every citation bin.

Produces ``spearman_hr.tex`` (A8), ``pearson_hr.tex`` (A9), and
``hr4_hr5_binwise.tex`` (A10).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from dua.analysis.loaders import MODEL_LABELS, MODELS, load_all_responses, load_responses
from dua.analysis.style import fmt, save_table
from dua.config import load_config

SOURCE = "dua.analysis.hr_decomposition"


def table_spearman_hr() -> dict:
    """Spearman rho between citation count and HR2 / HR4 / HR5, per model."""
    values, rows = {}, []
    for model in MODELS:
        df = load_responses(model)
        record = {}
        for metric in ("hr2", "hr4", "hr5"):
            sub = df[["citations", metric]].dropna()
            rho, p = stats.spearmanr(sub["citations"], sub[metric])
            record[metric] = {"rho": float(rho), "p": float(p), "n": int(len(sub))}
        values[model] = record
        rows.append([MODEL_LABELS[model], *(fmt(record[m]["rho"]) for m in ("hr2", "hr4", "hr5"))])
    save_table(
        "spearman_hr",
        [r"\textbf{LLM}", r"\textbf{HR$_2$ (Total)}", r"\textbf{HR$_4$ (Halluc.)}",
         r"\textbf{HR$_5$ (Omiss.)}"],
        rows, align="lccc", source=SOURCE, values={"spearman_by_model": values},
    )
    return values


def table_pearson_hr() -> dict:
    """Pearson r between each component and the composite HR2, per model."""
    values, rows = {}, []
    for model in MODELS:
        df = load_responses(model)
        record = {}
        for metric in ("hr4", "hr5"):
            sub = df[["hr2", metric]].dropna()
            r, p = stats.pearsonr(sub["hr2"], sub[metric])
            record[metric] = {"r": float(r), "p": float(p), "n": int(len(sub))}
        values[model] = record
        rows.append([MODEL_LABELS[model], fmt(record["hr4"]["r"]), fmt(record["hr5"]["r"])])
    save_table(
        "pearson_hr",
        [r"\textbf{LLM}", r"\textbf{HR$_4$ vs.\ HR$_2$}", r"\textbf{HR$_5$ vs.\ HR$_2$}"],
        rows, align="lcc", source=SOURCE, values={"pearson_by_model": values},
    )
    return values


def table_hr4_hr5_binwise() -> dict:
    """HR4 and HR5 per citation bin, averaged across models.

    Averaged over the pooled rows, so a bin where one model has more valid
    rows than another is not double-weighted; HR4 is undefined when a model
    returns nothing at all, which happens 168 times for DeepSeek-R1.
    """
    df = load_all_responses()
    rows, records = [], []
    for label in load_config().bin_labels:
        sub = df[df["citation_bin"] == label]
        h4, h5 = float(sub["hr4"].mean()), float(sub["hr5"].mean())
        records.append({"citation_bin": label, "hr4": h4, "hr5": h5,
                        "abs_diff": abs(h4 - h5), "n": int(len(sub))})
        rows.append([label.replace("-", "--"), fmt(h4), fmt(h5), fmt(abs(h4 - h5))])
    diffs = np.array([r["abs_diff"] for r in records])
    summary = {"mean_abs_diff": float(diffs.mean()), "max_abs_diff": float(diffs.max())}
    save_table(
        "hr4_hr5_binwise",
        [r"\textbf{Citation Bin}", r"\textbf{HR$_4$}", r"\textbf{HR$_5$}", r"$|\Delta|$"],
        rows, align="lccc", source=SOURCE,
        values={"per_bin": records, "summary": summary},
    )
    return {"per_bin": records, "summary": summary}


def run_all() -> dict:
    return {
        "spearman": table_spearman_hr(),
        "pearson": table_pearson_hr(),
        "binwise": table_hr4_hr5_binwise(),
    }
