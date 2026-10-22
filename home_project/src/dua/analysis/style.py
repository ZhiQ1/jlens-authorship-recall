"""Shared figure styling and LaTeX table emission.

Two rules this module enforces:

* Every figure writes a PDF **and** the values behind it as JSON, so a figure
  and the prose beside it can be checked against each other.
* Every table is emitted as a ``\\input``-able tabular with a provenance
  header. No number in the paper is typed by hand.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dua.config import load_config
from dua.io import write_json, write_latex_table

_STYLE_APPLIED = False


def apply_style() -> None:
    """Set the shared matplotlib defaults. Idempotent."""
    global _STYLE_APPLIED
    if _STYLE_APPLIED:
        return
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": load_config()["figures"]["dpi"],
        "savefig.bbox": "tight",
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": ":",
        "legend.frameon": False,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "pdf.fonttype": 42,   # embed TrueType, not Type 3; ACL requires it
        "ps.fonttype": 42,
    })
    _STYLE_APPLIED = True


def model_color(model: str) -> str:
    return load_config()["figures"]["model_colors"][model]


def figures_dir() -> Path:
    d = load_config().path("figures")
    d.mkdir(parents=True, exist_ok=True)
    return d


def tables_dir() -> Path:
    d = load_config().path("tables")
    d.mkdir(parents=True, exist_ok=True)
    return d


def metrics_dir() -> Path:
    d = load_config().path("metrics")
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_figure(fig, name: str, values: dict[str, Any], *, source: str) -> tuple[Path, Path]:
    """Save a figure and the numbers it plots, side by side.

    Returns ``(pdf_path, json_path)``.
    """
    cfg = load_config()
    pdf = figures_dir() / f"{name}.{cfg['figures']['format']}"
    fig.savefig(pdf)
    json_path = write_json(metrics_dir() / f"{name}.json", values, seed=cfg.seed, source=source)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return pdf, json_path


def fmt(value: float | None, places: int = 3, dash: str = "--") -> str:
    """Format a number for LaTeX, rendering NaN and None as an em dash."""
    import math

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return dash
    return f"{value:.{places}f}"


def fmt_int(value: float | None, dash: str = "--") -> str:
    import math

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return dash
    return f"{int(round(value)):,}"


def latex_tabular(
    header: list[str],
    rows: list[list[str]],
    *,
    align: str,
    midrule_before: set[int] | None = None,
) -> str:
    """Build a booktabs tabular body. Caption and label stay in the paper."""
    midrule_before = midrule_before or set()
    lines = [f"\\begin{{tabular}}{{@{{}}{align}@{{}}}}", "\\toprule",
             " & ".join(header) + r" \\", "\\midrule"]
    for i, row in enumerate(rows):
        if i in midrule_before:
            lines.append("\\midrule")
        lines.append(" & ".join(row) + r" \\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def save_table(name: str, header: list[str], rows: list[list[str]], *,
               align: str, source: str, midrule_before: set[int] | None = None,
               values: dict[str, Any] | None = None) -> Path:
    """Write ``results/tables/<name>.tex`` and, if given, its values as JSON."""
    body = latex_tabular(header, rows, align=align, midrule_before=midrule_before)
    path = write_latex_table(tables_dir() / f"{name}.tex", body,
                             source=source, seed=load_config().seed)
    if values is not None:
        write_json(metrics_dir() / f"{name}.json", values,
                   seed=load_config().seed, source=source)
    return path
