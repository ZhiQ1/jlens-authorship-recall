"""End-to-end test of the recognition scoring path (Section 6, Appendix A7).

The real multiple-choice run needs an API key, so the scoring path is
exercised on synthetic outcomes joined to the *real* recall rates. The
assertions are about the arithmetic and the joins, not about any result.
"""

import pandas as pd
import pytest

from dua.analysis.loaders import load_responses
from dua.recognition.analyze import (
    chance_corrected,
    gap_by_bin,
    merge_with_recall,
    residual_recognition,
)
from dua.seeds import rng


@pytest.fixture(scope="module")
def merged():
    recall = load_responses("gpt-4o")
    gen = rng(42, "test-mc")
    # Recognition improving with citation count, the shape the paper reports.
    p = 0.80 + 0.15 * (recall["bin_order"] / 12.0)
    mc = pd.DataFrame({
        "paper_id": recall["paper_id"],
        "citation_bin": recall["citation_bin"].astype(str),
        "correct": (gen.random(len(recall)) < p).astype(int),
    })
    return merge_with_recall(mc)


def test_chance_correction_is_equation_4():
    assert chance_corrected(0.25) == pytest.approx(0.0)
    assert chance_corrected(1.0) == pytest.approx(1.0)
    assert chance_corrected(0.625) == pytest.approx(0.5)


def test_merge_preserves_every_item():
    recall = load_responses("gpt-4o")
    mc = pd.DataFrame({"paper_id": recall["paper_id"],
                       "citation_bin": recall["citation_bin"].astype(str),
                       "correct": 1})
    assert len(merge_with_recall(mc)) == len(mc)


def test_merge_refuses_to_silently_drop_rows():
    """A join that loses items would inflate accuracy; it must raise instead."""
    mc = pd.DataFrame({"paper_id": ["not-a-real-paper-id"],
                       "citation_bin": ["0-2"], "correct": [1]})
    with pytest.raises(ValueError, match="join lost rows"):
        merge_with_recall(mc)


def test_gap_is_recognition_minus_recall(merged):
    table = gap_by_bin(merged)
    assert len(table) == 13
    for _, row in table.iterrows():
        assert row["gap"] == pytest.approx(row["mc_accuracy_cc"] - row["recall_accuracy"])
        assert row["mc_accuracy_cc"] == pytest.approx(chance_corrected(row["mc_accuracy_raw"]))
    assert table["n"].sum() == len(merged)


def test_recall_accuracy_comes_from_the_real_gpt4o_run(merged):
    """The recall column must be 1 - HR2, not anything synthetic."""
    table = gap_by_bin(merged).set_index("citation_bin")
    # Appendix A7.2 prints 0.009 for the lowest bin and 0.022 for the next.
    assert table.loc["0-2", "recall_accuracy"] == pytest.approx(0.009, abs=0.002)
    assert table.loc["3-4", "recall_accuracy"] == pytest.approx(0.022, abs=0.002)


def test_recall_is_monotone_in_citation_bin(merged):
    """The Section 5 finding, seen through the recognition join."""
    recall = gap_by_bin(merged)["recall_accuracy"].to_numpy()
    assert recall[-1] > recall[0]
    from scipy import stats
    rho, _ = stats.spearmanr(range(len(recall)), recall)
    assert rho > 0.95


def test_residual_recognition_strata_shrink_with_the_threshold(merged):
    strata = residual_recognition(merged)
    assert [s["threshold"] for s in strata] == [0.5, 0.75]
    assert strata[0]["papers"] > strata[1]["papers"]
    # Appendix A7.2: 8,342 papers have HR2 > 0.5.
    assert strata[0]["papers"] == pytest.approx(8342, abs=100)
    for s in strata:
        assert 0.0 <= s["residual_rate"] <= 1.0
        assert s["correct_recognitions"] <= s["papers"]


def test_gap_is_computable_under_every_hr_variant(merged):
    """Appendix A7.1 reports the gap under all five HR definitions."""
    for metric in ("hr1", "hr2", "hr3", "hr4", "hr5"):
        table = gap_by_bin(merged, metric)
        assert len(table) == 13
        assert table["recall_accuracy"].notna().all()
