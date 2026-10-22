"""Optional: correlate the P1 score with an external prevalence proxy. Not in the paper.

Runs only when a joinable proxy file sits next to a run directory; otherwise
writes ``external_proxy_decoding_SKIPPED.txt``.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import spearman, write_df, write_text


def discover_external_proxy(root_dirs: Iterable[Path]) -> Path | None:
    names = {
        "external_proxy.csv",
        "external_proxy.tsv",
        "paper_external_proxy.csv",
        "paper_external_proxy.tsv",
        "semantic_scholar_proxy.csv",
        "semantic_scholar_proxy.tsv",
    }
    for root in root_dirs:
        for path in [root, root.parent]:
            if not path.exists():
                continue
            for child in path.iterdir():
                if child.name in names:
                    return child
    return None


def run_external_proxy_decoding(
    proxy_path: Path | None,
    predictions: pd.DataFrame,
    out_dir: Path,
) -> None:
    if proxy_path is None:
        write_text(
            out_dir / "external_proxy_decoding_SKIPPED.txt",
            "Skipped external proxy decoding: no local joinable proxy file was discovered.\n"
            "Expected one of external_proxy.csv/.tsv, paper_external_proxy.csv/.tsv, or "
            "semantic_scholar_proxy.csv/.tsv with a paper_id column and numeric proxy column.\n",
        )
        return

    sep = "\t" if proxy_path.suffix == ".tsv" else ","
    proxy = pd.read_csv(proxy_path, sep=sep)
    if "paper_id" not in proxy.columns:
        write_text(
            out_dir / "external_proxy_decoding_SKIPPED.txt",
            f"Skipped external proxy decoding: {proxy_path} has no paper_id column.\n",
        )
        return
    numeric_cols = [
        c for c in proxy.columns
        if c != "paper_id" and pd.api.types.is_numeric_dtype(proxy[c])
    ]
    if not numeric_cols:
        write_text(
            out_dir / "external_proxy_decoding_SKIPPED.txt",
            f"Skipped external proxy decoding: {proxy_path} has no numeric proxy column.\n",
        )
        return
    proxy_col = numeric_cols[0]
    merged = predictions.merge(proxy[["paper_id", proxy_col]], on="paper_id", how="inner")
    rows: list[dict] = []
    for model, grp in merged.groupby("model"):
        if len(grp) < 50:
            continue
        y = pd.to_numeric(grp[proxy_col], errors="coerce").to_numpy()
        pred = pd.to_numeric(grp["p1_prevalence_pred_oof"], errors="coerce").to_numpy()
        mask = np.isfinite(y) & np.isfinite(pred)
        if mask.sum() < 50:
            continue
        rows.append({
            "model": model,
            "proxy_file": str(proxy_path),
            "proxy_column": proxy_col,
            "n_joined": int(mask.sum()),
            "spearman_rho": round(spearman(y[mask], pred[mask]), 6),
        })
    if rows:
        write_df(out_dir / "external_proxy_decoding.csv", pd.DataFrame(rows))
    else:
        write_text(
            out_dir / "external_proxy_decoding_SKIPPED.txt",
            f"Skipped external proxy decoding: {proxy_path} did not join to at least 50 rows per model.\n",
        )
