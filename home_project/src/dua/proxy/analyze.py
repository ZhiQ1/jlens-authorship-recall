"""Section 3: turning proxy counts into the figure and tables.

Produces Figure 1 (two log-scale panels: mean Google hits after outlier
filtering, and mean Infini-gram counts in the OLMo2 corpus) plus the appendix
tables ``google_hits_full``, ``google_hits_filtered_80``, ``query_length_full``,
and the four Infini-gram tables.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.analysis.style import apply_style, fmt, fmt_int, save_figure, save_table
from dua.config import load_config

SOURCE = "dua.proxy.analyze"


def filter_outliers(df: pd.DataFrame, *, percentile: int | None = None,
                    column: str = "hits") -> tuple[pd.DataFrame, dict]:
    """Drop papers above the Nth percentile of ``column`` *within their bin*.

    Per-bin rather than global, because hit counts span six orders of
    magnitude across bins; a global cutoff would remove most of the top bin
    and none of the bottom, which is exactly backwards -- the spurious matches
    are concentrated in the low-citation bins.
    """
    percentile = percentile or load_config()["proxy"]["outlier_percentile"]
    kept, report = [], []
    for label, group in df.groupby("citation_bin", observed=True, sort=False):
        valid = group[group[column].notna()]
        if valid.empty:
            continue
        cutoff = float(np.percentile(valid[column], percentile))
        survivors = valid[valid[column] <= cutoff]
        kept.append(survivors)
        report.append({"citation_bin": str(label), "before": int(len(valid)),
                       "after": int(len(survivors)), "cutoff": cutoff})
    out = pd.concat(kept, ignore_index=True) if kept else df.iloc[:0]
    return out, {"percentile": percentile, "per_bin": report,
                 "n_before": int(df[column].notna().sum()), "n_after": int(len(out))}


def summarize_by_bin(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Mean, median, and n per citation bin, in canonical order."""
    rows = []
    for label in load_config().bin_labels:
        group = df[df["citation_bin"] == label][column].dropna()
        if group.empty:
            continue
        rows.append({"citation_bin": label, "n": int(len(group)),
                     "mean": float(group.mean()), "median": float(group.median()),
                     "min": float(group.min()), "max": float(group.max())})
    return pd.DataFrame(rows)


def table_google_hits(df: pd.DataFrame, name: str, caption_source: str) -> dict:
    table = summarize_by_bin(df, "hits")
    rows = [[r["citation_bin"].replace("-", "--"), fmt_int(r["n"]),
             fmt_int(r["mean"]), fmt_int(r["median"]), fmt_int(r["max"])]
            for _, r in table.iterrows()]
    save_table(
        name,
        [r"\textbf{Citation Bin}", r"\textbf{N}", r"\textbf{Mean hits}",
         r"\textbf{Median hits}", r"\textbf{Max hits}"],
        rows, align="lrrrr", source=caption_source,
        values={"per_bin": table.to_dict(orient="records")},
    )
    return {"per_bin": table.to_dict(orient="records")}


def table_query_length(df: pd.DataFrame) -> dict:
    table = summarize_by_bin(df, "query_length")
    rows = [[r["citation_bin"].replace("-", "--"), fmt_int(r["n"]), fmt(r["mean"], 2),
             fmt(r["median"], 1), fmt_int(r["min"]), fmt_int(r["max"])]
            for _, r in table.iterrows()]
    overall = float(df["query_length"].mean())
    save_table(
        "query_length_full",
        [r"\textbf{Citation Bin}", r"\textbf{N}", r"\textbf{Mean}", r"\textbf{Median}",
         r"\textbf{Min}", r"\textbf{Max}"],
        rows, align="lrrrrr", source=SOURCE,
        values={"per_bin": table.to_dict(orient="records"), "overall_mean": overall},
    )
    return {"overall_mean_query_length": overall}


def table_infinigram(df: pd.DataFrame, corpus: str, variant: str) -> dict:
    sub = df[(df["corpus"] == corpus) & (df["variant"] == variant)]
    table = summarize_by_bin(sub, "count")
    rows = [[r["citation_bin"].replace("-", "--"), fmt_int(r["n"]), fmt(r["mean"], 2),
             fmt(r["median"], 1), fmt_int(r["max"])] for _, r in table.iterrows()]
    save_table(
        f"infinigram_{corpus}_{variant}",
        [r"\textbf{Citation Bin}", r"\textbf{N}", r"\textbf{Mean count}",
         r"\textbf{Median}", r"\textbf{Max}"],
        rows, align="lrrrr", source=SOURCE,
        values={"corpus": corpus, "variant": variant,
                "per_bin": table.to_dict(orient="records")},
    )
    return {"per_bin": table.to_dict(orient="records")}


def figure_proxy_means(google: pd.DataFrame, infinigram: pd.DataFrame,
                       corpus: str = "olmo2", variant: str = "capitalize") -> None:
    """Figure 1: both proxies against citation bin, on log axes."""
    apply_style()
    import matplotlib.pyplot as plt

    labels = load_config().bin_labels
    left = summarize_by_bin(google, "hits")
    right = summarize_by_bin(
        infinigram[(infinigram["corpus"] == corpus) & (infinigram["variant"] == variant)],
        "count",
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for ax, table, ylabel, colour in (
        (axes[0], left, "Mean Google search hits", "#1f77b4"),
        (axes[1], right, f"Mean Infini-gram count ({corpus})", "#d62728"),
    ):
        x = [labels.index(b) for b in table["citation_bin"]]
        # log(1 + y): the lowest bins have means at or near zero, which a plain
        # log axis would drop off the figure entirely.
        ax.plot(x, table["mean"] + 1, marker="o", markersize=4, linewidth=1.6, color=colour)
        ax.set_yscale("log")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_xlabel("Citation count")
        ax.set_ylabel(ylabel, fontsize=9)
    fig.tight_layout()
    save_figure(fig, "fig_proxy_means_by_citation_bin",
                {"google": left.to_dict(orient="records"),
                 "infinigram": right.to_dict(orient="records"),
                 "corpus": corpus, "variant": variant,
                 "note": "y values are plotted as mean + 1 on a log axis"},
                source=SOURCE)


def run_all(google: pd.DataFrame, infinigram: pd.DataFrame) -> dict:
    out = {"google_full": table_google_hits(google, "google_hits_full", SOURCE)}
    out["query_length"] = table_query_length(google)
    filtered, report = filter_outliers(google)
    out["outlier_filter"] = report
    out["google_filtered"] = table_google_hits(filtered, "google_hits_filtered_80", SOURCE)
    for corpus in ("olmo2", "redpajama"):
        for variant in ("capitalize", "camel"):
            out[f"infinigram_{corpus}_{variant}"] = table_infinigram(infinigram, corpus, variant)
    figure_proxy_means(filtered, infinigram)
    return out
