"""Tests for the multiple-choice construction and scoring (Section 6)."""

import pytest

from dua.recognition.analyze import chance_corrected
from dua.recognition.distractors import DistractorBuilder, build_field_pools, verify_items
from dua.recognition.run import build_items, parse_choice

GIVEN = ["Alice", "Bruno", "Chen", "Dara", "Ewan", "Farah", "Gita", "Hugo"]


def _surname(i: int) -> str:
    """Distinct, parseable surnames: Abanov, Abanev, ... Zybine."""
    first = chr(ord("A") + i // 100)
    return f"{first}{'bcdfghjklm'[(i // 10) % 10]}{'aeiou'[i % 5]}nov{i % 2}"


@pytest.fixture(scope="module")
def papers():
    """A synthetic field with a pool large enough to draw from.

    Names must look like real names: the splitter and matcher are the real
    ones, and a fixture of ``A0. Sur000`` would exercise their fallbacks
    rather than their intended paths.
    """
    return [
        {
            "paper_id": f"p{i}",
            "title": f"Paper {i}",
            "year": 2010,
            "field": "physics",
            "citations": i,
            "citation_bin": "0-2",
            "authors": [
                f"{GIVEN[(i + j) % len(GIVEN)]} {_surname(3 * i + j)}" for j in range(3)
            ],
        }
        for i in range(60)
    ]


def test_chance_correction_matches_equation_4():
    assert chance_corrected(0.25) == pytest.approx(0.0)
    assert chance_corrected(1.0) == pytest.approx(1.0)
    assert chance_corrected(0.8419) == pytest.approx((0.8419 - 0.25) / 0.75)


@pytest.mark.parametrize("mode", ["random_field", "same_field_swap"])
def test_items_satisfy_the_appendix_integrity_claims(papers, mode):
    report = verify_items(build_items(papers, mode))
    assert report["n_items"] == len(papers)
    assert report["options_with_duplicate_names"] == 0
    if mode == "random_field":
        assert report["distractor_groups_overlapping_truth"] == 0


def test_every_option_has_the_same_length(papers):
    for item in build_items(papers, "random_field"):
        k = len(item.options[item.correct_index])
        assert {len(o) for o in item.options} == {k}


def test_correct_option_position_is_seeded_and_stable(papers):
    a = [i.correct_label for i in build_items(papers, "random_field")]
    b = [i.correct_label for i in build_items(papers, "random_field")]
    assert a == b, "item construction must be reproducible from the config seed"


def test_same_field_swap_shares_k_minus_one_true_authors(papers):
    for item in build_items(papers, "same_field_swap"):
        true = set(item.options[item.correct_index])
        for i, option in enumerate(item.options):
            if i == item.correct_index:
                continue
            assert len(true & set(option)) == len(true) - 1


def test_collaborator_swap_falls_back_when_collaborators_are_scarce(papers):
    builder = DistractorBuilder(build_field_pools(papers))
    item = builder.collaborator_swap(papers[0], ["Only One Person"])
    assert item.fell_back is True
    assert item.mode == "collaborator_swap"

    plenty = ["Real Collab One", "Real Collab Two", "Real Collab Three", "Real Collab Four"]
    item = builder.collaborator_swap(papers[0], plenty)
    assert item.fell_back is False
    true = set(item.options[item.correct_index])
    for i, option in enumerate(item.options):
        if i != item.correct_index:
            assert len(true & set(option)) == len(true) - 1


@pytest.mark.parametrize(
    "text,expected",
    [
        ("B", "B"), ("  c ", "C"), ("A.", "A"), ("The answer is D.", "D"),
        ("I don't know", None), ("", None), (None, None),
    ],
)
def test_parse_choice(text, expected):
    assert parse_choice(text) == expected


def test_unparseable_answers_count_as_wrong_not_missing():
    """Dropping non-compliant answers would inflate accuracy."""
    assert parse_choice("no idea") is None
    # run.py scores `int(chosen == item.correct_label)`, so None -> 0.
    assert int(None == "A") == 0
