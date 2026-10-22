"""Stage E: deterministic name matching and hallucination metrics."""

from dua.evaluate.matcher import NameMatcher
from dua.evaluate.metrics import (
    ALL_METRICS,
    Counts,
    add_rates,
    all_rates,
    hr1,
    hr2,
    hr3,
    hr4,
    hr5,
    mean_ci,
    parse_counts,
    perfect_recall,
)
from dua.evaluate.pipeline import EvaluationResult, Evaluator
from dua.evaluate.splitter import NameSplitter

__all__ = [
    "ALL_METRICS", "Counts", "EvaluationResult", "Evaluator", "NameMatcher",
    "NameSplitter", "add_rates", "all_rates", "hr1", "hr2", "hr3", "hr4",
    "hr5", "mean_ci", "parse_counts", "perfect_recall",
]
