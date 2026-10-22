"""Section 6 and Appendix A7: scoring the multiple-choice recognition run.

Chance-corrected accuracy removes the four-option guessing floor,
``(a - 0.25) / 0.75``. Recall accuracy is ``1 - HR2`` from the open-ended run.
Their difference is the paper's evidence that low-prevalence failures are a
retrieval bottleneck rather than missing knowledge: the model picks the right
team out of a lineup long after it can no longer produce it.

A binary perfect-recall variant is also reported, since ``1 - HR2`` gives
partial credit while MC accuracy does not.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from dua.analysis.loaders import load_responses
from dua.analysis.style import apply_style, fmt, fmt_int, save_figure, save_table
from dua.config import load_config
from dua.evaluate.metrics import ALL_METRICS

SOURCE = "dua.recognition.analyze"
MODE_LABELS = {"random_field": "Orig.", "same_field_swap": "S-F", "collaborator_swap": "Col."}


def chance_corrected(accuracy: float, chance: float | None = None) -> float:
    """Equation 4: remove the contribution of random guessing."""
    chance = load_config()["recognition"]["chance"] if chance is None else chance
    return (accuracy - chance) / (1 - chance)


def load_mc_results(path) -> pd.DataFrame:
    """Read a scored MC run: one row per item with ``correct`` in {0, 1}."""
    df = pd.read_csv(path)
    required = {"paper_id", "correct", "citation_bin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")
    return df


def merge_with_recall(mc: pd.DataFrame, model: str = "gpt-4o") -> pd.DataFrame:
    """Join MC outcomes to the open-ended rates for the same papers."""
    recall = load_responses(model)[
        ["paper_id", "citations", "citation_bin", "field", "perfect_recall", *ALL_METRICS]
    ]
    merged = mc.merge(recall, on="paper_id", suffixes=("", "_recall"))
    if len(merged) != len(mc):
        raise ValueError(f"join lost rows: {len(mc)} MC items -> {len(merged)} matched")
    return merged


def gap_by_bin(merged: pd.DataFrame, metric: str = "hr2") -> pd.DataFrame:
    """Per-bin recall accuracy, chance-corrected MC accuracy, and the gap."""
    rows = []
    for label in load_config().bin_labels:
        sub = merged[merged["citation_bin"] == label]
        if sub.empty:
            continue
        recall = float(1 - sub[metric].mean())
        raw = float(sub["correct"].mean())
        cc = chance_corrected(raw)
        rows.append({"citation_bin": label, "n": int(len(sub)), "recall_accuracy": recall,
                     "mc_accuracy_raw": raw, "mc_accuracy_cc": cc, "gap": cc - recall})
    return pd.DataFrame(rows)


def residual_recognition(merged: pd.DataFrame, thresholds=(0.5, 0.75)) -> list[dict]:
    """Among papers where open-ended recall fails, how many are recognised?"""
    out = []
    for threshold in thresholds:
        sub = merged[merged["hr2"] > threshold]
        n = int(len(sub))
        correct = int(sub["correct"].sum())
        out.append({"threshold": threshold, "papers": n, "correct_recognitions": correct,
                    "residual_rate": (correct / n) if n else float("nan")})
    return out


def table_mc_full_results(merged: pd.DataFrame) -> dict:
    table = gap_by_bin(merged)
    rows = [[r["citation_bin"].replace("-", "--"), fmt(r["recall_accuracy"]),
             fmt(r["mc_accuracy_cc"]), fmt(r["gap"])] for _, r in table.iterrows()]
    lowest = merged[merged["citation_bin"] == load_config().bin_labels[0]]
    t, p = stats.ttest_1samp(lowest["correct"], load_config()["recognition"]["chance"])
    rho, rho_p = stats.spearmanr(table.index, table["mc_accuracy_cc"])
    values = {
        "per_bin": table.to_dict(orient="records"),
        "lowest_bin_vs_chance": {"t": float(t), "p": float(p), "n": int(len(lowest))},
        "monotonicity_spearman": {"rho": float(rho), "p": float(rho_p)},
        "overall": {"recall_accuracy": float(1 - merged["hr2"].mean()),
                    "mc_accuracy_raw": float(merged["correct"].mean()),
                    "mc_accuracy_cc": chance_corrected(float(merged["correct"].mean()))},
    }
    save_table(
        "mc_full_results",
        [r"\textbf{Citation Bin}", r"\textbf{Recall acc.}", r"\textbf{MC acc. (CC)}",
         r"\textbf{Gap}"],
        rows, align="lrrr", source=SOURCE, values=values,
    )
    return values


def table_residual_knowledge(merged: pd.DataFrame) -> dict:
    records = residual_recognition(merged)
    rows = [[rf"$\text{{HR}}_2 > {r['threshold']}$", fmt_int(r["papers"]),
             fmt_int(r["correct_recognitions"]), f"{100 * r['residual_rate']:.1f}\\%"]
            for r in records]
    save_table(
        "residual_knowledge",
        [r"\textbf{Stratum}", r"\textbf{Papers}", r"\textbf{Correct recog.}",
         r"\textbf{Residual rate}"],
        rows, align="lrrr", source=SOURCE, values={"strata": records},
    )
    return {"strata": records}


def figure_recall_recognition_gap(merged: pd.DataFrame) -> None:
    apply_style()
    import matplotlib.pyplot as plt

    table = gap_by_bin(merged)
    x = np.arange(len(table))
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(x, table["mc_accuracy_cc"], marker="o", markersize=4, linewidth=1.6,
            color="#1f77b4", label="MC recognition (chance-corrected)")
    ax.plot(x, table["recall_accuracy"], marker="s", markersize=4, linewidth=1.6,
            color="#d62728", label=r"Recall accuracy ($1 - \mathrm{HR}_2$)")
    ax.fill_between(x, table["recall_accuracy"], table["mc_accuracy_cc"],
                    color="0.6", alpha=0.2, label="Gap")
    ax.set_xticks(x)
    ax.set_xticklabels(table["citation_bin"], rotation=45, ha="right")
    ax.set_xlabel("Citation count")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="center right")
    fig.tight_layout()
    save_figure(fig, "fig_recall_recognition_gap",
                {"per_bin": table.to_dict(orient="records")}, source=SOURCE)


def figure_hr_variants_gap(merged: pd.DataFrame) -> None:
    """Appendix A7.1: the gap is the same under all five HR definitions."""
    apply_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    values = {}
    for metric in ALL_METRICS:
        table = gap_by_bin(merged, metric)
        ax.plot(np.arange(len(table)), table["gap"], marker="o", markersize=3,
                linewidth=1.2, label=rf"HR$_{metric[-1]}$")
        values[metric] = table["gap"].tolist()
    labels = gap_by_bin(merged)["citation_bin"].tolist()
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Citation count")
    ax.set_ylabel("Recall--recognition gap")
    ax.legend(ncol=5, fontsize=8)
    fig.tight_layout()
    save_figure(fig, "fig_hr_variants_gap",
                {"citation_bins": labels, "gap_by_metric": values}, source=SOURCE)


def figure_perfect_recall_gap(merged: pd.DataFrame) -> None:
    """Appendix A7.4: the gap widens under the strict H = U = 0 criterion."""
    apply_style()
    import matplotlib.pyplot as plt

    rows = []
    for label in load_config().bin_labels:
        sub = merged[merged["citation_bin"] == label]
        if sub.empty:
            continue
        rows.append({
            "citation_bin": label,
            "perfect_recall": float(sub["perfect_recall"].mean()),
            "partial_recall": float(1 - sub["hr2"].mean()),
            "mc_accuracy_cc": chance_corrected(float(sub["correct"].mean())),
        })
    table = pd.DataFrame(rows)
    x = np.arange(len(table))

    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.plot(x, table["mc_accuracy_cc"], marker="o", markersize=4, color="#1f77b4",
            label="MC recognition (chance-corrected)")
    ax.plot(x, table["perfect_recall"], marker="s", markersize=4, color="#d62728",
            label="Binary perfect recall ($H = U = 0$)")
    ax.plot(x, table["partial_recall"], linestyle="--", color="0.5", linewidth=1.2,
            label=r"$1 - \mathrm{HR}_2$ (partial credit)")
    ax.set_xticks(x)
    ax.set_xticklabels(table["citation_bin"], rotation=45, ha="right")
    ax.set_xlabel("Citation count")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="center right")
    fig.tight_layout()
    save_figure(fig, "fig_perfect_recall_gap",
                {"per_bin": table.to_dict(orient="records")}, source=SOURCE)


def table_hard_distractors(runs: dict[str, pd.DataFrame]) -> dict:
    """Appendix A7.3: the three distractor constructions side by side.

    ``runs`` maps a mode name to its merged frame. Modes that were not run are
    simply absent from the table.
    """
    modes = [m for m in load_config()["recognition"]["distractor_modes"] if m in runs]
    tables = {m: gap_by_bin(runs[m]).set_index("citation_bin") for m in modes}
    base = tables[modes[0]]

    rows = []
    for label in base.index:
        cells = [label.replace("-", "--"), fmt(base.loc[label, "recall_accuracy"])]
        cells += [fmt(tables[m].loc[label, "mc_accuracy_cc"]) for m in modes]
        cells += [fmt(tables[m].loc[label, "gap"]) for m in modes]
        rows.append(cells)

    header = [r"\textbf{Bin}", r"\textbf{Recall}"]
    header += [MODE_LABELS[m] for m in modes] + [MODE_LABELS[m] for m in modes]
    save_table(
        "mc_hard_distractors", header, rows,
        align="lr" + "r" * (2 * len(modes)), source=SOURCE,
        values={m: tables[m].reset_index().to_dict(orient="records") for m in modes},
    )
    return {m: {"residual": residual_recognition(runs[m])} for m in modes}


def run_all(runs: dict[str, pd.DataFrame]) -> dict:
    """``runs`` maps distractor mode -> merged results frame."""
    primary = runs[load_config()["recognition"]["distractor_modes"][0]]
    out = {
        "full_results": table_mc_full_results(primary),
        "residual": table_residual_knowledge(primary),
    }
    figure_recall_recognition_gap(primary)
    figure_hr_variants_gap(primary)
    figure_perfect_recall_gap(primary)
    if len(runs) > 1:
        out["hard_distractors"] = table_hard_distractors(runs)
    return out
