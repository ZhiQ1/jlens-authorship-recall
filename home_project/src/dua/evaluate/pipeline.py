"""The hard-coded evaluation pipeline (Section 4.5).

One record in, one ``(M, H, U)`` triple out. This is where the paper's
threshold is applied: :class:`~dua.evaluate.matcher.NameMatcher` reports a
match level per pair, and this module decides which levels count.

A pair at level L5 -- same surname, no contradicting initial, but no matching
initial either -- is *not* a match under Section 4.5. It is demoted: the
ground-truth author goes to ``U`` and the LLM name goes to ``H``, so a single
weak pair costs the model twice. That is deliberate; it is the conservative
reading, and it is what produced the published numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dua.config import load_config
from dua.evaluate.ground_truth import ground_truth_list, llm_answer
from dua.evaluate.matcher import NameMatcher


def match_level_value(label: str) -> float:
    """``"L3.5_full_component_swapped"`` -> ``3.5``."""
    return float(label.split("_")[0][1:])


@dataclass
class EvaluationResult:
    """Per-paper evaluation output."""

    matched: list[str] = field(default_factory=list)        # M
    hallucinated: list[str] = field(default_factory=list)   # H
    unretrieved: list[str] = field(default_factory=list)    # U
    match_levels: list[str] = field(default_factory=list)

    # Positions, for the positional analysis in Appendix A6.8.
    matched_gt_positions: list[int] = field(default_factory=list)
    unretrieved_gt_positions: list[int] = field(default_factory=list)
    hallucinated_llm_positions: list[int] = field(default_factory=list)
    n_llm_names: int = 0

    @property
    def counts(self) -> tuple[int, int, int]:
        return len(self.matched), len(self.hallucinated), len(self.unretrieved)

    @property
    def counts_str(self) -> str:
        """The ``"M, H, U"`` form stored in ``hard_code_evaluation``."""
        m, h, u = self.counts
        return f"{m}, {h}, {u}"

    def as_columns(self) -> dict[str, str]:
        """The four evaluation columns appended to every released CSV."""
        return {
            "hard_code_evaluation": self.counts_str,
            "matched_gt_authors(X)": "; ".join(self.matched),
            "hallucinated_llm_authors(Y)": "; ".join(self.hallucinated),
            "unmatched_gt_authors(Z)": "; ".join(self.unretrieved),
        }


class Evaluator:
    """Stateless scorer. Construct once, reuse across a whole file."""

    def __init__(self, match_level_threshold: float | None = None):
        cfg = load_config()
        self.threshold = (
            float(cfg["evaluation"]["match_level_threshold"])
            if match_level_threshold is None
            else float(match_level_threshold)
        )
        self.matcher = NameMatcher()

    def evaluate(self, gt_authors: list[str], llm_string: str) -> EvaluationResult:
        raw = self.matcher.find_matches(gt_authors, llm_string)

        strong, weak = [], []
        for pair in raw["matches"]:
            (strong if match_level_value(pair["match_level"]) <= self.threshold else weak).append(pair)

        return EvaluationResult(
            matched=[p["gt_author"] for p in strong],
            # A weak pair is demoted on both sides.
            hallucinated=list(raw["hallucinated_llm"]) + [p["llm_author"] for p in weak],
            unretrieved=[u["gt_author"] for u in raw["unmatched_gt"]] + [p["gt_author"] for p in weak],
            match_levels=[p["match_level"] for p in strong],
            matched_gt_positions=[p["gt_index"] for p in strong],
            unretrieved_gt_positions=(
                [u["gt_index"] for u in raw["unmatched_gt"]] + [p["gt_index"] for p in weak]
            ),
            hallucinated_llm_positions=(
                [d["llm_index"] for d in raw["hallucinated_llm_detail"]]
                + [p["llm_index"] for p in weak]
            ),
            n_llm_names=raw["n_llm_names"],
        )

    def evaluate_record(self, record: dict[str, Any]) -> EvaluationResult:
        """Evaluate a record in any of the shipped schemas."""
        return self.evaluate(
            ground_truth_list(record, self.matcher.splitter),
            llm_answer(record),
        )
