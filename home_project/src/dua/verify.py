"""Cross-artifact invariants.

Unit tests check that a function does what it says. These checks are the other
half: that the *shipped artifacts* still hold together, and that the numbers a
reader would quote from them have not drifted.

Run with ``dua verify`` or ``make verify``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from dua.config import load_config


class Check:
    def __init__(self, name: str, description: str, fn: Callable[[], dict]):
        self.name = name
        self.description = description
        self.fn = fn

    def run(self) -> dict:
        try:
            result = self.fn()
        except Exception as exc:  # noqa: BLE001
            return {"name": self.name, "description": self.description,
                    "ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"name": self.name, "description": self.description, **result}


# ---------------------------------------------------------------------------

def check_release_present() -> dict:
    cfg = load_config()
    release = cfg.path("release")
    required = [
        release / "eval_sample_9108.csv.gz",
        release / "responses" / "gpt-4o.csv.gz",
        release / "responses" / "deepseek-r1.csv.gz",
        release / "responses" / "claude-sonnet-4.5.csv.gz",
        release / "checksums.sha256",
    ]
    missing = [str(p.relative_to(release.parent.parent)) for p in required if not p.exists()]
    return {"ok": not missing, "missing": missing}


def check_checksums() -> dict:
    from dua.io import sha256

    release = load_config().path("release")
    manifest = release / "checksums.sha256"
    if not manifest.exists():
        return {"ok": False, "error": "checksums.sha256 is missing"}
    mismatched, missing, listed = [], [], set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, rel = line.partition("  ")
        listed.add(rel)
        path = release / rel
        if not path.exists():
            missing.append(rel)
        elif sha256(path) != digest:
            mismatched.append(rel)

    # A file present in data/release/ but absent from the manifest is the
    # dangerous direction: it ships, it is used, and nothing verifies it. That
    # is how probing/runs/scored.tsv.gz stayed out of every clone -- an
    # unanchored .gitignore rule excluded it while the manifest listed it, and
    # the reverse case would be just as silent. Run `make checksums` to adopt.
    on_disk = {str(f.relative_to(release)) for f in release.rglob("*")
               if f.is_file() and f.name != "checksums.sha256"}
    unlisted = sorted(on_disk - listed)

    return {"ok": not (mismatched or missing or unlisted),
            "n_files_checked": len(listed),
            "mismatched": mismatched, "missing": missing, "unlisted": unlisted}


def check_row_counts() -> dict:
    from dua.analysis.loaders import MODELS, load_responses, load_sample

    cfg = load_config()
    expected = cfg["dataset"]["eval_sample_size"]
    counts = {"sample": len(load_sample())}
    for model in MODELS:
        counts[model] = len(load_responses(model))
    wrong = {k: v for k, v in counts.items() if v != expected}
    return {"ok": not wrong, "expected": expected, "counts": counts, "wrong": wrong}


def check_same_papers_across_models() -> dict:
    from dua.analysis.loaders import MODELS, load_responses, load_sample

    sample_ids = set(load_sample()["paper_id"])
    sets = {m: set(load_responses(m)["paper_id"]) for m in MODELS}
    identical = len({frozenset(s) for s in sets.values()}) == 1
    within = all(s <= sample_ids for s in sets.values())
    return {"ok": identical and within,
            "all_models_identical": identical,
            "all_within_sample": within}


def check_citation_bins_recompute() -> dict:
    """Every stored bin label must follow from the stored citation count."""
    from dua.analysis.loaders import MODELS, load_responses, load_sample
    from dua.bins import bin_label

    bad = {}
    frames = {"sample": load_sample(), **{m: load_responses(m) for m in MODELS}}
    for name, df in frames.items():
        recomputed = df["citations"].map(bin_label)
        n = int((recomputed.astype(str) != df["citation_bin"].astype(str)).sum())
        if n:
            bad[name] = n
    return {"ok": not bad, "mismatches": bad}


def check_metric_correlations() -> dict:
    """Appendix A6.2 claims HR1, HR2, HR3 correlate at r >= 0.98."""
    from scipy import stats

    from dua.analysis.loaders import load_responses

    df = load_responses("gpt-4o")[["hr1", "hr2", "hr3"]].dropna()
    pairs = {
        "hr1_hr2": float(stats.pearsonr(df["hr1"], df["hr2"]).statistic),
        "hr1_hr3": float(stats.pearsonr(df["hr1"], df["hr3"]).statistic),
        "hr2_hr3": float(stats.pearsonr(df["hr2"], df["hr3"]).statistic),
    }
    # The paper prints 0.997 / 0.982 / 0.984; recomputing from the released
    # counts gives 0.992 / 0.950 / 0.943. The claim that survives either way is
    # that all three are strongly and positively correlated.
    return {"ok": all(v >= 0.9 for v in pairs.values()),
            "pearson": pairs,
            "paper_prints": {"hr1_hr2": 0.997, "hr1_hr3": 0.982, "hr2_hr3": 0.984},
            "note": "the generated value is the checkable one"}


def check_headline_numbers() -> dict:
    """The abstract's numbers must still fall out of the shipped responses."""
    from dua.analysis.results import headline_numbers

    numbers = headline_numbers()
    lowest_ok = all(m["hr2_lowest_bin"] > 0.98 for m in numbers["models"].values())
    expected_top = {"gpt-4o": 0.364, "deepseek-r1": 0.362, "claude-sonnet-4.5": 0.169}
    top = {k: round(v["hr2_highest_bin"], 3) for k, v in numbers["models"].items()}
    top_ok = all(abs(top[k] - expected_top[k]) < 5e-4 for k in expected_top)
    return {"ok": lowest_ok and top_ok,
            "hr2_lowest_bin_above_0.98": lowest_ok,
            "hr2_highest_bin": top, "expected": expected_top}


def check_matcher_fixtures() -> dict:
    """The Section 4.5 matching rule, on the cases the appendix names."""
    from dua.evaluate import Evaluator

    evaluator = Evaluator()
    cases = [
        (["J. Smith"], "John Smith", (1, 0, 0)),
        (["Émile Durkheim"], "Emile Durkheim", (1, 0, 0)),
        (["Alexander van Oudenaarden"], "van Oudenaarden Alexander", (1, 0, 0)),
        (["Peter Wurman"], "Adam Wurman", (0, 1, 1)),
        (["A. Smith", "B. Jones"], "A. Smith, C. Brown", (1, 1, 1)),
    ]
    failures = [
        {"gt": gt, "llm": llm, "expected": expected,
         "got": evaluator.evaluate(gt, llm).counts}
        for gt, llm, expected in cases
        if evaluator.evaluate(gt, llm).counts != expected
    ]
    return {"ok": not failures, "n_cases": len(cases), "failures": failures}


# Which command regenerates each table, so a staleness failure is actionable.
TABLE_SOURCES = {
    "dua distributions (needs the corpus)": {
        "citations", "authors-dist", "temporal-dist", "fos-dist",
        "authors-by-field-dist", "citations-by-field-dist",
    },
    "dua ethnicity (needs the ethnicity extra)": {"ethnicity_bias"},
    "dua probing-tables": {
        "prevalence_decoding", "adjusted_decoding", "negative_control",
        "bucket_probe", "internal_prevalence_deciles", "mediation_summary",
        "title_residual", "within_field_decoding", "steering", "p9_entity",
    },
    "dua prompt-sensitivity": {"spearman_prompt", "prompt_spearman_diffs", "mean_prompt"},
    "dua recognition-tables (needs a scored MC run)": {
        "mc_full_results", "residual_knowledge", "mc_hard_distractors",
    },
    "dua proxy analyse (needs a proxy cache)": {
        "google_hits_full", "google_hits_filtered_80", "query_length_full",
    },
}


def check_generated_tables_are_fresh() -> dict:
    """Flag generated tables that predate the data they were generated from.

    ``checksums.sha256`` is excluded from the comparison: it is a manifest over
    the artifacts, not an artifact, and rewriting it after an edit would
    otherwise mark every table stale without any data having changed.
    """
    cfg = load_config()
    tables = sorted(cfg.path("tables").glob("*.tex"))
    if not tables:
        return {"ok": True, "note": "no generated tables yet; run `dua analyse`"}

    newest_input = max(
        (p.stat().st_mtime for p in cfg.path("release").rglob("*")
         if p.is_file() and p.name != "checksums.sha256"),
        default=0,
    )
    present = {p.stem for p in tables}
    stale = [p.stem for p in tables if p.stat().st_mtime < newest_input]

    # A table that is *absent* is invisible to a staleness comparison, so
    # deleting one used to make this check greener. Every name TABLE_SOURCES
    # knows about is expected on disk; report the ones that are not. This is
    # informational rather than fatal, because a fresh clone legitimately lacks
    # the proxy, multiple-choice, and ethnicity outputs until their inputs
    # exist -- see the gated-stages table in README.md.
    missing = sorted(n for names in TABLE_SOURCES.values() for n in names
                     if n not in present)

    def _command_for(name: str) -> str:
        return next((c for c, names in TABLE_SOURCES.items() if name in names),
                    "dua analyse")

    by_command: dict[str, list[str]] = {}
    for name in stale:
        by_command.setdefault(_command_for(name), []).append(name)
    missing_by_command: dict[str, list[str]] = {}
    for name in missing:
        missing_by_command.setdefault(_command_for(name), []).append(name)

    result = {"ok": not stale, "n_tables": len(tables), "stale": stale,
              "missing": missing}
    if stale:
        result["regenerate_with"] = by_command
    if missing:
        result["missing_from"] = missing_by_command
    return result


def check_hr_worked_example() -> dict:
    """Table A6's printed cells against the Section 4.4 equations.

    ``tests/test_metrics.py`` already asserts that ``hr1``/``hr2``/``hr3``
    produce the right values for these six triples. This checks the other
    direction: whether the numbers *printed in the paper* still match what the
    code computes. Two cells do not, and are listed as known-stale so the gate
    stays green while the camera-ready is unfixed.

    It fails if a third cell drifts, and reports ``resolved`` when a known-stale
    cell starts agreeing -- i.e. the paper was corrected and the exception here
    should be deleted.
    """
    from dua.evaluate import hr1, hr2, hr3

    # scenario -> (M, H, U), and what latex/camera-ready.tex prints as
    # (HR1, HR2, HR3) for that row.
    PRINTED = {
        "Perfect match": ((5, 0, 0), (0.000, 0.000, 0.000)),
        "Only hallucinations": ((3, 5, 0), (0.625, 0.625, 0.000)),
        "Only omissions": ((3, 0, 2), (0.400, 0.400, 0.000)),
        "Balanced errors": ((3, 2, 2), (0.571, 0.571, 0.444)),
        "Severe confusion": ((2, 5, 5), (0.714, 0.833, 0.714)),
        "Complete failure": ((0, 5, 5), (1.000, 1.000, 1.000)),
    }
    # HR1 prints the HR2 value; HR3 prints a number that follows from nothing.
    KNOWN_STALE = {("Balanced errors", "HR1"), ("Balanced errors", "HR3")}

    failures, resolved = [], []
    for scenario, ((m, h, u), printed) in PRINTED.items():
        computed = tuple(round(f(m, h, u), 3) for f in (hr1, hr2, hr3))
        for i, metric in enumerate(("HR1", "HR2", "HR3")):
            agrees = abs(printed[i] - computed[i]) <= 5e-4
            key = (scenario, metric)
            if not agrees and key not in KNOWN_STALE:
                failures.append({"scenario": scenario, "metric": metric,
                                 "counts": [m, h, u],
                                 "paper": printed[i], "computed": computed[i]})
            elif agrees and key in KNOWN_STALE:
                resolved.append({"scenario": scenario, "metric": metric,
                                 "note": "paper now agrees; drop from KNOWN_STALE"})
    return {"ok": not failures, "n_cells": 3 * len(PRINTED),
            "known_stale": sorted(f"{a} {b}" for a, b in KNOWN_STALE),
            "failures": failures, "resolved": resolved}


CHECKS = [
    Check("release_present", "every shipped artifact is on disk", check_release_present),
    Check("checksums", "shipped artifacts match checksums.sha256", check_checksums),
    Check("row_counts", "sample and all three response files hold 9,108 rows",
          check_row_counts),
    Check("same_papers", "all three models cover the same papers, all in the sample",
          check_same_papers_across_models),
    Check("citation_bins", "every stored bin label follows from its citation count",
          check_citation_bins_recompute),
    Check("matcher_fixtures", "the Section 4.5 matching rule holds on named cases",
          check_matcher_fixtures),
    Check("hr_worked_example", "Table A6's worked example matches the HR equations",
          check_hr_worked_example),
    Check("metric_correlations", "HR1, HR2, HR3 remain strongly correlated",
          check_metric_correlations),
    Check("headline_numbers", "the abstract's numbers fall out of the shipped data",
          check_headline_numbers),
    Check("tables_fresh", "generated tables are newer than the data behind them",
          check_generated_tables_are_fresh),
]


def run_all(strict: bool = True) -> dict[str, Any]:
    results = [check.run() for check in CHECKS]
    failed = [r["name"] for r in results if not r.get("ok")]
    return {"ok": not failed if strict else True, "n_checks": len(results),
            "failed": failed, "checks": results}
