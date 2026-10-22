"""Loading the released artifacts into analysis-ready frames.

Every analysis in this package starts here, so that "the data" means one
thing. Loading is memoised: a Makefile target that runs six analyses reads
each file once.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from dua.bins import bin_index
from dua.config import load_config
from dua.evaluate.metrics import ALL_METRICS, perfect_recall

MODELS = ("gpt-4o", "deepseek-r1", "claude-sonnet-4.5")
MODEL_LABELS = {
    "gpt-4o": "GPT-4o",
    "deepseek-r1": "DeepSeek-R1",
    "claude-sonnet-4.5": "Claude Sonnet 4.5",
}


class ReleaseMissingError(FileNotFoundError):
    """Raised with an actionable message when a shipped artifact is absent."""

    def __init__(self, path: Path):
        super().__init__(
            f"{path} is missing.\n"
            "The released artifacts live in data/release/ and are tracked in git.\n"
            "If you are working from a partial clone, run `git lfs pull` or "
            "re-clone; if you are rebuilding them, see tools/build_release.py."
        )


def _require(path: Path) -> Path:
    if not path.exists():
        raise ReleaseMissingError(path)
    return path


def _add_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Attach HR1..HR5 and the binary perfect-recall flag.

    Rates are recomputed from (m, h, u) on every load rather than stored, so
    a change to a metric definition propagates to every table at once and
    cannot go stale in a cached column.
    """
    for name, fn in ALL_METRICS.items():
        df[name] = [fn(m, h, u) for m, h, u in zip(df["m"], df["h"], df["u"], strict=True)]
    df["perfect_recall"] = [
        perfect_recall(m, h, u) for m, h, u in zip(df["m"], df["h"], df["u"], strict=True)
    ]
    return df


def _order_bins(df: pd.DataFrame) -> pd.DataFrame:
    cfg = load_config()
    df["bin_order"] = df["citation_bin"].map(bin_index)
    df["citation_bin"] = pd.Categorical(df["citation_bin"], categories=cfg.bin_labels, ordered=True)
    return df


@lru_cache(maxsize=1)
def load_sample() -> pd.DataFrame:
    """The 9,108-paper stratified evaluation sample (Section 4.1)."""
    cfg = load_config()
    path = _require(cfg.path("release") / "eval_sample_9108.csv.gz")
    df = pd.read_csv(path)
    df["authors"] = df["authors"].map(json.loads)
    df["title_length"] = df["title"].fillna("").str.len()
    return _order_bins(df)


@lru_cache(maxsize=len(MODELS))
def load_responses(model: str) -> pd.DataFrame:
    """One model's 9,108 scored responses, with all five rates attached."""
    if model not in MODELS:
        raise KeyError(f"unknown model {model!r}; expected one of {MODELS}")
    cfg = load_config()
    path = _require(cfg.path("release") / "responses" / f"{model}.csv.gz")
    df = pd.read_csv(path)
    df["model_label"] = MODEL_LABELS[model]
    df["n_authors"] = df["m"] + df["u"]        # |ground truth| = M + U
    df["n_generated"] = df["m"] + df["h"]      # |LLM answer|  = M + H
    df["title_length"] = df["title"].fillna("").str.len()
    df = _order_bins(_add_rates(df))
    return _add_judge_rates(df)


def _add_judge_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Attach ``judge_hr*`` from the LLM-as-judge counts, where present.

    Only GPT-4o was judged (Appendix A6.5). For the other two models the
    columns are empty and every rate is NaN, which is what the agreement
    analysis expects.
    """
    cols = ["llm_eval_m", "llm_eval_h", "llm_eval_u"]
    if not all(c in df.columns for c in cols):
        for name in ALL_METRICS:
            df[f"judge_{name}"] = float("nan")
        return df
    triples = df[cols].apply(pd.to_numeric, errors="coerce")
    ok = triples.notna().all(axis=1)
    for name, fn in ALL_METRICS.items():
        out = pd.Series(float("nan"), index=df.index, dtype=float)
        out.loc[ok] = [
            fn(m, h, u)
            for m, h, u in zip(triples.loc[ok, cols[0]], triples.loc[ok, cols[1]],
                               triples.loc[ok, cols[2]], strict=True)
        ]
        df[f"judge_{name}"] = out
    df["has_judge"] = ok
    return df


@lru_cache(maxsize=1)
def load_all_responses() -> pd.DataFrame:
    """All three models stacked, 27,324 rows, one row per (paper, model)."""
    return pd.concat([load_responses(m) for m in MODELS], ignore_index=True)


def check_expected_size(df: pd.DataFrame, expected: int, what: str) -> None:
    """Fail loudly rather than silently reporting a number from a partial file."""
    if len(df) != expected:
        raise ValueError(f"{what}: expected {expected:,} rows, found {len(df):,}")
