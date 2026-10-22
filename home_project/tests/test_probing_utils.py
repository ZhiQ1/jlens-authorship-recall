"""
test_scholar_utils.py
─────────────────────────────────────────────────────────────────────────────
Tests for scholar_utils.py — run standalone:
    python test_scholar_utils.py

Covers:
  - NameSplitter.split(): semicolons, commas, reversed, biblio, particles, suffixes
  - NameMatcher.find_matches(): match levels L1–L5, swapped rescue, unicode
  - score_authors(): HR2 formula, real CSV rows
  - per_name_is_hallucinated(): correct/hallucinated/initial-match
  - compute_auroc / spearman_r: edge cases
"""

import sys
import traceback

sys.path.insert(0, __file__.rsplit("/", 1)[0])

from dua.probing.scholar_utils import (
    NameSplitter,
    NameMatcher,
    score_authors,
    per_name_is_hallucinated,
    compute_auroc,
    spearman_r,
    MATCH_LEVEL_THRESHOLD,
    _match_level_value,
)

MATCHER = NameMatcher()
SPLITTER = NameSplitter()

_pass = 0
_fail = 0


def check(name, condition, detail=""):
    global _pass, _fail
    if condition:
        print(f"  PASS  {name}")
        _pass += 1
    else:
        print(f"  FAIL  {name}" + (f"  →  {detail}" if detail else ""))
        _fail += 1


def section(title):
    print(f"\n{'─'*60}\n{title}\n{'─'*60}")


# ─────────────────────────────────────────────────────────────────────────────
# NameSplitter
# ─────────────────────────────────────────────────────────────────────────────

def test_splitter_empty():
    section("NameSplitter — empty / whitespace")
    check("empty string",     SPLITTER.split("") == [])
    check("whitespace only",  SPLITTER.split("   ") == [])
    check("None-like empty",  SPLITTER.split("") == [])


def test_splitter_simple():
    section("NameSplitter — plain comma / 'and' lists")
    r = SPLITTER.split("Alice Smith, Bob Jones, Carol Lee")
    check("3-name comma list", r == ["Alice Smith", "Bob Jones", "Carol Lee"], r)

    r = SPLITTER.split("Alice Smith and Bob Jones")
    check("'and' converted to comma", r == ["Alice Smith", "Bob Jones"], r)

    r = SPLITTER.split("Clare Dyer")
    check("single name", r == ["Clare Dyer"], r)


def test_splitter_semicolons():
    section("NameSplitter — semicolon-separated (model follows instruction)")
    r = SPLITTER.split("Alice Smith; Bob Jones; Carol Lee")
    check("3-name semicolon list", r == ["Alice Smith", "Bob Jones", "Carol Lee"], r)

    # Reversed-format names inside semicolon chunks
    r = SPLITTER.split("Wurman, Peter; Mountz, Mick")
    check("semicolon + reversed chunks → ['Peter Wurman', 'Mick Mountz']",
          r == ["Peter Wurman", "Mick Mountz"], r)

    # Mixed semicolons and 'and' inside a chunk
    r = SPLITTER.split("Alice Smith; Bob Jones and Carol Lee")
    # 'and' is inside the second chunk, so it becomes 2 names in that chunk
    check("semicolon + 'and' inside chunk → 3 names", len(r) == 3, r)


def test_splitter_reversed_format():
    section("NameSplitter — reversed (Surname, Firstname) format")
    r = SPLITTER.split("Smith, John, Doe, Jane")
    check("2-person reversed → ['John Smith', 'Jane Doe']",
          r == ["John Smith", "Jane Doe"], r)

    # Real case from the paper prompt format
    r = SPLITTER.split("Wurman, Peter, Mountz, Mick")
    check("Wurman/Mountz reversed → ['Peter Wurman', 'Mick Mountz']",
          r == ["Peter Wurman", "Mick Mountz"], r)

    # Initials in reversed format: "Bree, S., Snoek, S."
    r = SPLITTER.split("Bree, S., Snoek, S.")
    check("initial reversed format → ['S. Bree', 'S. Snoek']",
          r == ["S. Bree", "S. Snoek"], r)


def test_splitter_suffixes():
    section("NameSplitter — Jr./Sr. suffix merging")
    r = SPLITTER.split("Robert Smith, Jr., Tom Jones")
    check("Jr. merged with preceding name",
          any("Jr." in n for n in r) and len(r) == 2, r)

    r = SPLITTER.split("William Brown, III, Alice Kim")
    check("III suffix merged", len(r) == 2, r)


def test_splitter_particles():
    section("NameSplitter — surname particles (van, de, …)")
    # Normal order — particles should stay in last name
    r = SPLITTER.split("Jan van der Berg, Marie de Groot")
    check("particles in normal order", len(r) == 2, r)
    check("particle preserved in first name", any("van der Berg" in n for n in r), r)


def test_splitter_real_csv_rows():
    section("NameSplitter — real CSV 'answer' column strings")

    # Row 1 GT: initial-format comma list (not reversed — odd count)
    gt1 = ("S. Bree, S. Snoek, S. V. Diest, L. Elbers, F. Hilbers, "
           "Suzanne Duijst, J. Vliet, R. V. D. Wijngaard, C. Cailotto, "
           "W. Jonge, G. Boeckxstaens")
    r = SPLITTER.split(gt1)
    check("row1 GT: 11 authors", len(r) == 11, f"got {len(r)}: {r}")

    # Row 2 GT: single author
    r = SPLITTER.split("J. Hollifield")
    check("row2 GT: single author", r == ["J. Hollifield"], r)

    # Rijnbout row GT: 4 authors with initials
    gt_r = "Pepijn Rijnbout, M. D. Graaf, M. M. Bekker, B. Schouten"
    r = SPLITTER.split(gt_r)
    check("rijnbout GT: 4 authors", len(r) == 4, f"got {len(r)}: {r}")


# ─────────────────────────────────────────────────────────────────────────────
# NameMatcher — find_matches and match levels
# ─────────────────────────────────────────────────────────────────────────────

def _match_level(gt_list, llm_str):
    """Return list of (gt, level) tuples from find_matches."""
    res = MATCHER.find_matches(gt_list, llm_str)
    return [(m["gt_author"], m["match_level"]) for m in res["matches"]]


def test_matcher_l1_exact():
    section("NameMatcher — L1 exact match")
    res = MATCHER.find_matches(["Clare Dyer"], "Clare Dyer")
    check("Clare Dyer exact",
          len(res["matches"]) == 1 and "L1" in res["matches"][0]["match_level"],
          res)
    check("no hallucinations", res["hallucinated_llm"] == [], res)
    check("no unmatched GT",   res["unmatched_gt"]     == [], res)


def test_matcher_l2_normalized():
    section("NameMatcher — L2 unicode normalization")
    # ä → a via unidecode
    res = MATCHER.find_matches(["Mika Kivimäki"], "Mika Kivimaki")
    ml = res["matches"][0]["match_level"] if res["matches"] else "none"
    check("Kivimäki vs Kivimaki matched", bool(res["matches"]), res)
    check("matched at L2 or L3", _match_level_value(ml) <= 3.0 if res["matches"] else False, ml)


def test_matcher_l3_alpha():
    section("NameMatcher — L3 alpha-only normalization")
    # Periods stripped: "Mary St.Clair" vs "Mary StClair" — both alpha-only → "Mary StClair"
    # L1 fails (strings differ), L2 may fail (normalized_full keeps period), L3 passes
    res = MATCHER.find_matches(["Mary St.Clair"], "Mary StClair")
    check("St.Clair vs StClair matched at ≤ L3 or via component",
          bool(res["matches"]), res)


def test_matcher_l4_initial():
    section("NameMatcher — L4 last name + first initial")
    res = MATCHER.find_matches(["J. Pentti"], "Jaana Pentti")
    check("J. Pentti matches Jaana Pentti",
          bool(res["matches"]), res)
    ml = res["matches"][0]["match_level"] if res["matches"] else "none"
    check("matched at L4", _match_level_value(ml) == 4.0, ml)

    # Initial in LLM output, full name in GT
    res = MATCHER.find_matches(["Jaana Pentti"], "J. Pentti")
    check("Jaana Pentti matches J. Pentti (reverse direction)",
          bool(res["matches"]), res)


def test_matcher_l5_lastname_only():
    section("NameMatcher — L5 weak (last name only, no first info)")
    # Two full names sharing a last name but differing first names (neither is an initial):
    # no L4 possible, no contradicting initials → falls to L5 weak match
    res = MATCHER.find_matches(["John Smith"], "Alice Smith")
    has_match = bool(res["matches"])
    check("John Smith vs Alice Smith → L5 weak match", has_match, res)
    if has_match:
        ml = res["matches"][0]["match_level"]
        check("matched at L5", _match_level_value(ml) == 5.0, ml)

    # L5 weak appears as BOTH hallucinated and missed in score_authors
    r = score_authors("John Smith", "Alice Smith", MATCHER)
    check("L5 weak: n_hal==1 and n_unretr==1 (double-penalty)", r["n_hal"] == 1 and r["n_unretr"] == 1, r)
    check("L5 weak: n_match==0 (not counted as strong)", r["n_match"] == 0, r)

    # Contradicting initial → should NOT match even at L5
    res = MATCHER.find_matches(["M. Bekker"], "Tilde Bekker")
    check("M. Bekker vs Tilde Bekker → no match (contradicting initial)",
          len(res["matches"]) == 0, res)


def test_matcher_hallucination():
    section("NameMatcher — fully hallucinated LLM output")
    gt  = ["S. Bree", "S. Snoek"]
    llm = "Amanda Jensen, Amanda Drucker"
    res = MATCHER.find_matches(gt, llm)
    check("no matches",        len(res["matches"])          == 0, res)
    check("2 GT unmatched",    len(res["unmatched_gt"])     == 2, res)
    check("2 LLM hallucinated",len(res["hallucinated_llm"]) == 2, res)


def test_matcher_swap_rescue():
    section("NameMatcher — first/last swap rescue")
    # GT: "Jensen Amanda" (reversed), LLM: "Amanda Jensen"
    res = MATCHER.find_matches(["Jensen Amanda"], "Amanda Jensen")
    check("reversed GT matched with swap rescue", bool(res["matches"]), res)


def test_matcher_particle_match():
    section("NameMatcher — particle stripping (van/de)")
    # GT: "M. D. Graaf" (initial), LLM: "Marc de Graaf" (full with particle)
    res = MATCHER.find_matches(["M. D. Graaf"], "Marc de Graaf")
    check("M. D. Graaf matches Marc de Graaf",
          bool(res["matches"]), res)
    if res["matches"]:
        ml = res["matches"][0]["match_level"]
        check("matched at ≤ L4", _match_level_value(ml) <= 4.0, ml)

    # GT: "B. Schouten", LLM: "Ben Schouten"
    res = MATCHER.find_matches(["B. Schouten"], "Ben Schouten")
    check("B. Schouten matches Ben Schouten", bool(res["matches"]), res)


# ─────────────────────────────────────────────────────────────────────────────
# score_authors — HR2 arithmetic and real CSV rows
# ─────────────────────────────────────────────────────────────────────────────

def test_score_perfect():
    section("score_authors — perfect match")
    r = score_authors("Clare Dyer", "Clare Dyer", MATCHER)
    check("hr2 == 0.0",       r["hr2"]      == 0.0,  r)
    check("hr4 == 0.0",       r["hr4"]      == 0.0,  r)
    check("hr5 == 0.0",       r["hr5"]      == 0.0,  r)
    check("n_match == 1",     r["n_match"]  == 1,    r)
    check("n_hal == 0",       r["n_hal"]    == 0,    r)
    check("n_unretr == 0",    r["n_unretr"] == 0,    r)
    check("is_hallucinated 0",r["is_hallucinated"] == 0, r)


def test_score_total_hallucination():
    section("score_authors — total hallucination (CSV row 1)")
    gt  = ("S. Bree, S. Snoek, S. V. Diest, L. Elbers, F. Hilbers, "
           "Suzanne Duijst, J. Vliet, R. V. D. Wijngaard, C. Cailotto, "
           "W. Jonge, G. Boeckxstaens")
    llm = ("Amanda R. Jensen, Amanda M. Drucker, Kathryn A. Friel, Jun Guo, "
           "Christopher M. Skufca, Jun Lin, Gene F. Coppa, "
           "Gerard A. Baltazar, Lixin Liu")
    r = score_authors(gt, llm, MATCHER)
    check("n_match == 0",        r["n_match"]  == 0,   r)
    check("n_hal == 9",          r["n_hal"]    == 9,   r)
    check("n_unretr == 11",      r["n_unretr"] == 11,  r)
    check("hr2 == 1.0",          r["hr2"]      == 1.0, r)
    check("hr4 == 1.0",          r["hr4"]      == 1.0, r)  # all predicted are wrong
    check("hr5 == 1.0",          r["hr5"]      == 1.0, r)  # all GT missed
    check("is_hallucinated == 1",r["is_hallucinated"] == 1, r)


def test_score_single_author_hallucinated():
    section("score_authors — single author, total hallucination (CSV row 2)")
    r = score_authors("J. Hollifield", "Robert E. Slavin", MATCHER)
    check("n_match == 0",  r["n_match"]  == 0,   r)
    check("n_hal == 1",    r["n_hal"]    == 1,   r)
    check("n_unretr == 1", r["n_unretr"] == 1,   r)
    check("hr2 == 1.0",    r["hr2"]      == 1.0, r)


def test_score_partial_match():
    section("score_authors — partial match (Rijnbout CSV row: 2 match, 3 hal, 2 unretr)")
    gt  = "Pepijn Rijnbout, M. D. Graaf, M. M. Bekker, B. Schouten"
    llm = "Ben Schouten, Tilde Bekker, Alissa N. Antle, Marc de Graaf, Peter Sturm"
    r = score_authors(gt, llm, MATCHER)
    # expected: M. D. Graaf→Marc de Graaf (L4), B. Schouten→Ben Schouten (L4)
    # M. M. Bekker vs Tilde Bekker → contradicting initial → unmatched
    check("n_match == 2",  r["n_match"]  == 2,  r)
    check("n_hal == 3",    r["n_hal"]    == 3,  r)
    check("n_unretr == 2", r["n_unretr"] == 2,  r)
    expected_hr2 = round(5 / 7, 6)
    check(f"hr2 ≈ {expected_hr2}", r["hr2"] == expected_hr2, r["hr2"])
    # HR4 = 3/(2+3) = 0.6, HR5 = 2/(2+2) = 0.5
    check("hr4 == 0.6",  r["hr4"] == round(3/5, 6), r["hr4"])
    check("hr5 == 0.5",  r["hr5"] == round(2/4, 6), r["hr5"])


def test_score_kivimaki_row():
    section("score_authors — unicode + initial GT (Kivimäki CSV row: 2 match, 10 hal, 1 unretr)")
    gt  = "M. Kivimäki, J. Pentti, J. Deanfield"
    llm = ("Mika Kivimäki, G. David Batty, Solja T. Nyberg, "
           "Archana Singh-Manoux, Markus Jokela, Ichiro Kawachi, "
           "Marianna Virtanen, Martin J. Shipley, Mark Hamer, "
           "Töres Theorell, Jaana Pentti, Jussi Vahtera")
    r = score_authors(gt, llm, MATCHER)
    # M. Kivimäki → Mika Kivimäki (L4), J. Pentti → Jaana Pentti (L4)
    # J. Deanfield → not in LLM list → unmatched
    check("n_match == 2",  r["n_match"]  == 2,  r)
    check("n_unretr == 1", r["n_unretr"] == 1,  r)
    check("n_hal == 10",   r["n_hal"]    == 10, r)


def test_score_empty_llm():
    section("score_authors — empty LLM output")
    r = score_authors("Alice Smith, Bob Jones", "", MATCHER)
    check("n_match == 0",  r["n_match"]  == 0, r)
    check("n_hal == 0",    r["n_hal"]    == 0, r)
    check("n_unretr == 2", r["n_unretr"] == 2, r)
    check("hr2 == 1.0",    r["hr2"]      == 1.0, r)


def test_score_semicolon_llm():
    section("score_authors — LLM uses semicolon separator")
    r = score_authors("Clare Dyer", "Clare Dyer", MATCHER)
    check("semicolon single-name perfect", r["hr2"] == 0.0, r)

    r = score_authors("Alice Smith, Bob Jones", "Alice Smith; Bob Jones", MATCHER)
    check("semicolon list: both match", r["n_match"] == 2 and r["hr2"] == 0.0, r)


# ─────────────────────────────────────────────────────────────────────────────
# per_name_is_hallucinated
# ─────────────────────────────────────────────────────────────────────────────

def test_per_name():
    section("per_name_is_hallucinated")
    gt = "Clare Dyer"
    check("exact match → not hallucinated",
          per_name_is_hallucinated("Clare Dyer", gt, MATCHER) == False)

    check("different name → hallucinated",
          per_name_is_hallucinated("Amanda Jensen", gt, MATCHER) == True)

    gt2 = "M. Kivimäki, J. Pentti, J. Deanfield"
    check("Mika Kivimäki matches M. Kivimäki → not hallucinated",
          per_name_is_hallucinated("Mika Kivimäki", gt2, MATCHER) == False)

    check("Jaana Pentti matches J. Pentti → not hallucinated",
          per_name_is_hallucinated("Jaana Pentti", gt2, MATCHER) == False)

    check("Solja Nyberg not in GT → hallucinated",
          per_name_is_hallucinated("Solja T. Nyberg", gt2, MATCHER) == True)

    # L5 only (last name alone with no first-name info to confirm)
    # "Deanfield" alone is L5, which is > threshold → hallucinated
    check("last-name-only L5 → hallucinated (above threshold)",
          per_name_is_hallucinated("Deanfield", gt2, MATCHER) == True)

    # But initial + last at L4 is strong enough
    check("J. Deanfield (L4) → not hallucinated",
          per_name_is_hallucinated("J. Deanfield", gt2, MATCHER) == False)


# ─────────────────────────────────────────────────────────────────────────────
# compute_auroc / spearman_r
# ─────────────────────────────────────────────────────────────────────────────

def test_auroc():
    section("compute_auroc")
    import math
    try:
        import sklearn  # noqa: F401
    except ImportError:
        print("  SKIP  sklearn not installed — skipping compute_auroc tests")
        return

    auc = compute_auroc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1])
    check("perfect AUROC == 1.0", auc == 1.0, auc)

    auc = compute_auroc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1])
    check("inverted AUROC == 0.0", auc == 0.0, auc)

    auc = compute_auroc([0.5, 0.6], [1, 1])
    check("single class → nan", math.isnan(auc), auc)


def test_spearman():
    section("spearman_r")
    import math
    try:
        import scipy  # noqa: F401
    except ImportError:
        print("  SKIP  scipy not installed — skipping spearman_r tests")
        return

    r = spearman_r([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    check("monotone increasing → r == 1.0", abs(r - 1.0) < 1e-9, r)

    r = spearman_r([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    check("monotone decreasing → r == -1.0", abs(r + 1.0) < 1e-9, r)

    r = spearman_r([1, 2], [3, 4])
    check("too few points → nan", math.isnan(r), r)


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def main():
    tests = [
        test_splitter_empty,
        test_splitter_simple,
        test_splitter_semicolons,
        test_splitter_reversed_format,
        test_splitter_suffixes,
        test_splitter_particles,
        test_splitter_real_csv_rows,
        test_matcher_l1_exact,
        test_matcher_l2_normalized,
        test_matcher_l3_alpha,
        test_matcher_l4_initial,
        test_matcher_l5_lastname_only,
        test_matcher_hallucination,
        test_matcher_swap_rescue,
        test_matcher_particle_match,
        test_score_perfect,
        test_score_total_hallucination,
        test_score_single_author_hallucinated,
        test_score_partial_match,
        test_score_kivimaki_row,
        test_score_empty_llm,
        test_score_semicolon_llm,
        test_per_name,
        test_auroc,
        test_spearman,
    ]

    for test_fn in tests:
        try:
            test_fn()
        except Exception:
            global _fail
            _fail += 1
            print(f"\n  EXCEPTION in {test_fn.__name__}:")
            traceback.print_exc()

    total = _pass + _fail
    print(f"\n{'═'*60}")
    print(f"  {_pass}/{total} passed  |  {_fail} failed")
    print(f"{'═'*60}")
    sys.exit(0 if _fail == 0 else 1)


if __name__ == "__main__":
    main()
