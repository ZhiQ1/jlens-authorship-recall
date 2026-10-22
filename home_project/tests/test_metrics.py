"""Metric identity tests against the worked examples in the paper.

Every row of Table A6 (``tab:hr_example``, Appendix A6.1) is asserted here.
If a metric definition drifts, this fails before any table is regenerated.
"""

import math

import pytest

from dua.evaluate.metrics import (
    add_rates,
    hr1,
    hr2,
    hr3,
    hr4,
    hr5,
    mean_ci,
    parse_counts,
    perfect_recall,
)

# (scenario, M, H, U, HR1, HR2, HR3) -- Appendix A6.1, Table A6.
#
# Five of the six rows are asserted as printed. The "balanced errors" row is
# asserted at the values the Section 4.4 equations actually produce, because
# the printed HR1 and HR3 for that row are arithmetically wrong: the paper
# shows HR1 = 0.571 (which is HR2) where 1 - 3/max(5,5) = 0.400, and HR3 =
# 0.444 where 2*2*2 / (5*2 + 5*2) = 0.400. The row is illustrative only; no
# result in the paper depends on it.
PAPER_EXAMPLES = [
    ("perfect match",       5, 0, 0, 0.000, 0.000, 0.000),
    ("only hallucinations", 3, 5, 0, 0.625, 0.625, 0.000),
    ("only omissions",      3, 0, 2, 0.400, 0.400, 0.000),
    ("balanced errors",     3, 2, 2, 0.400, 0.571, 0.400),
    ("severe confusion",    2, 5, 5, 0.714, 0.833, 0.714),
    ("complete failure",    0, 5, 5, 1.000, 1.000, 1.000),
]


@pytest.mark.parametrize("scenario,m,h,u,e1,e2,e3", PAPER_EXAMPLES)
def test_paper_worked_examples(scenario, m, h, u, e1, e2, e3):
    assert hr1(m, h, u) == pytest.approx(e1, abs=5e-4), scenario
    assert hr2(m, h, u) == pytest.approx(e2, abs=5e-4), scenario
    assert hr3(m, h, u) == pytest.approx(e3, abs=5e-4), scenario


def test_all_metrics_are_bounded():
    for m in range(0, 8):
        for h in range(0, 8):
            for u in range(0, 8):
                for fn in (hr1, hr2, hr3, hr4, hr5):
                    value = fn(m, h, u)
                    if not math.isnan(value):
                        assert 0.0 <= value <= 1.0, (fn.__name__, m, h, u, value)


def test_hr2_dominates_both_one_sided_rates():
    """HR2 normalises over the union, so it is never below HR4 or HR5.

    This is why the paper reports HR2 as primary: it cannot hide an error mode
    the way a one-sided rate can.
    """
    for m in range(1, 6):
        for h in range(0, 6):
            for u in range(0, 6):
                assert hr2(m, h, u) >= max(hr4(m, h, u), hr5(m, h, u)) - 1e-9


def test_degenerate_denominators_follow_the_published_convention():
    # HR1/HR2/HR4/HR5 are undefined when nothing was predicted and nothing
    # was expected; HR3 reports 0 (no co-occurring error).
    assert math.isnan(hr1(0, 0, 0))
    assert math.isnan(hr2(0, 0, 0))
    assert hr3(0, 0, 0) == 0.0
    assert math.isnan(hr4(0, 0, 0))
    assert math.isnan(hr5(0, 0, 0))
    # An empty answer against a real author list: omission is total,
    # fabrication is undefined rather than zero.
    assert hr5(0, 0, 3) == 1.0
    assert math.isnan(hr4(0, 0, 3))


def test_perfect_recall_is_stricter_than_one_minus_hr2():
    assert perfect_recall(5, 0, 0) == 1.0
    assert perfect_recall(4, 0, 1) == 0.0
    assert 1 - hr2(4, 0, 1) == pytest.approx(0.8)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2, 1, 9", (2, 1, 9)),
        ("  0,0,0 ", (0, 0, 0)),
        ("None, None, None", None),
        ("", None),
        (None, None),
        ("medicine", None),  # a column-shifted row in a malformed CSV
    ],
)
def test_parse_counts(raw, expected):
    got = parse_counts(raw)
    assert (tuple(got) if got else None) == expected


def test_add_rates_reports_dropped_rows():
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"hard_code_evaluation": ["1, 2, 3", "bad", "0, 0, 0"]})
    out, dropped = add_rates(df)
    assert dropped == 1
    assert len(out) == 2
    assert list(out["m"]) == [1, 0]


def test_mean_ci_ignores_nan():
    mean, half, n = mean_ci([0.0, 1.0, float("nan")])
    assert n == 2
    assert mean == pytest.approx(0.5)
    assert half > 0
