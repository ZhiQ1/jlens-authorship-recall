"""Fixture tests for the name splitter and matcher.

Section 4.5 describes the matcher in prose only. This file turns that prose
into assertions, one case per behaviour a reviewer would reasonably poke at.
"""

import pytest

from dua.evaluate.matcher import NameMatcher
from dua.evaluate.pipeline import Evaluator, match_level_value
from dua.evaluate.splitter import NameSplitter


@pytest.fixture(scope="module")
def splitter():
    return NameSplitter()


@pytest.fixture(scope="module")
def matcher():
    return NameMatcher()


@pytest.fixture(scope="module")
def evaluator():
    return Evaluator()


# ---------------------------------------------------------------------------
# splitting
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        # Normal format must survive untouched, including the shapes that
        # superficially resemble the reversed format.
        ("Simon C. Harris, Matthew I. Roberts", ["Simon C. Harris", "Matthew I. Roberts"]),
        ("Qing-Guo Huang, Miao Li", ["Qing-Guo Huang", "Miao Li"]),
        ("C. Tutin, M. Fernandez", ["C. Tutin", "M. Fernandez"]),
        ("W. F. Tinney, C. E. Hart", ["W. F. Tinney", "C. E. Hart"]),
        ("W. Tinney, Clifford E. Hart", ["W. Tinney", "Clifford E. Hart"]),
        # Repeated names must not be read as surname/given-name alternation.
        ("J. Wang, J. Wang, J. Wang, J. Wang", ["J. Wang"] * 4),
        # Genuine alternating format.
        ("Wurman, Peter, Mountz, Mick", ["Peter Wurman", "Mick Mountz"]),
        ("Donoho, David, Johnstone, Iain", ["David Donoho", "Iain Johnstone"]),
        # Genuine bibliographic format.
        ("Posner George J., Strike Kenneth A., Hewson Peter W.",
         ["George J. Posner", "Kenneth A. Strike", "Peter W. Hewson"]),
        # Separator normalisation and suffix re-attachment.
        ("A. Smith and B. Jones", ["A. Smith", "B. Jones"]),
        ("Elliott Ward Cheney, Jr., Ronald A. DeVore",
         ["Elliott Ward Cheney, Jr.", "Ronald A. DeVore"]),
        ("", []),
    ],
)
def test_split(splitter, raw, expected):
    assert splitter.split(raw) == expected


# ---------------------------------------------------------------------------
# matching levels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "gt,llm,level",
    [
        ("A. Smith", "A. Smith", 1.0),                      # exact
        ("Émile Durkheim", "Emile Durkheim", 2.0),          # diacritic folding
        ("A. Smith", "A Smith", 3.0),                       # punctuation
        ("John Smith", "John Smith Jr.", 3.5),              # full given name
        ("J. Smith", "John Smith", 4.0),                    # initial expansion
        ("John Smith", "J. Smith", 4.0),                    # initial contraction
        ("Alexander van Oudenaarden", "Alexander Oudenaarden", 3.5),   # particle
        ("Alexander Oudenaarden", "Alexander van Oudenaarden", 3.5),
        ("Peter Wurman", "Adam Wurman", 5.0),               # surname only, weak
    ],
)
def test_match_level(matcher, gt, llm, level):
    result = matcher.find_matches([gt], llm)
    assert result["matches"], f"{gt!r} vs {llm!r} did not match at all"
    assert match_level_value(result["matches"][0]["match_level"]) == level


@pytest.mark.parametrize(
    "gt,llm",
    [
        ("R. Keefe", "Eve Keefe"),      # contradicting initial against an initial
        ("A. Smith", "B. Jones"),       # different surname
    ],
)
def test_non_matches(matcher, gt, llm):
    assert matcher.find_matches([gt], llm)["matches"] == []


def test_swap_and_bibliographic_rescues(matcher):
    """A single name given surname-first is still recovered."""
    assert matcher.find_matches(["Alexander van Oudenaarden"], "van Oudenaarden Alexander")["matches"]
    assert matcher.find_matches(["Paul E. Dimotakis"], "Dimotakis Paul E.")["matches"]


def test_duplicate_names_are_consumed_one_for_one(matcher):
    """Two identical ground-truth authors need two identical LLM names."""
    result = matcher.find_matches(["J. Wang", "J. Wang"], "J. Wang")
    assert len(result["matches"]) == 1
    assert len(result["unmatched_gt"]) == 1
    assert result["hallucinated_llm"] == []


# ---------------------------------------------------------------------------
# the Section 4.5 threshold
# ---------------------------------------------------------------------------

def test_weak_match_is_demoted_on_both_sides(evaluator):
    """L5 is not a match: it costs one omission AND one hallucination.

    Section 4.5 requires both the surname and the first initial to match.
    "Peter Wurman" vs "Adam Wurman" shares only the surname.
    """
    result = evaluator.evaluate(["Peter Wurman"], "Adam Wurman")
    assert result.counts == (0, 1, 1)
    assert result.counts_str == "0, 1, 1"


def test_venn_example_from_figure_1(evaluator):
    """Figure 1: GT {A. Smith, B. Jones}, LLM {A. Smith, C. Brown}."""
    result = evaluator.evaluate(["A. Smith", "B. Jones"], "A. Smith, C. Brown")
    assert result.counts == (1, 1, 1)
    assert result.matched == ["A. Smith"]
    assert result.hallucinated == ["C. Brown"]
    assert result.unretrieved == ["B. Jones"]


def test_empty_answer_is_all_omission(evaluator):
    assert evaluator.evaluate(["A. Smith", "B. Jones"], "").counts == (0, 0, 2)


def test_evaluate_record_handles_every_shipped_schema(evaluator):
    """The four ground-truth shapes in README.md all score identically."""
    expected = (1, 0, 1)
    records = [
        {"ground_truth_authors": "A. Smith, B. Jones", "llm_authors": "A. Smith"},
        {"ground_truth_authors": ["A. Smith", "B. Jones"], "llm_authors": "A. Smith"},
        {"ground_truth_authors": [{"authorId": "1", "name": "A. Smith"},
                                  {"authorId": "2", "name": "B. Jones"}],
         "llm_authors": "A. Smith"},
        # The CSV-shredded shape, as it appears in the released files.
        {"ground_truth_authors": '["[{\'authorId\': \'1\'", "\'name\': \'A. Smith\'}", '
                                 '"{\'authorId\': \'2\'", "\'name\': \'B. Jones\'}]"]',
         "llm_authors": "A. Smith"},
        {"answer": "A. Smith, B. Jones", "gpt_answer": "A. Smith"},
    ]
    for record in records:
        assert evaluator.evaluate_record(record).counts == expected, record
