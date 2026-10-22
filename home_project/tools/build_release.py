#!/usr/bin/env python3
"""Repackage the private working trees into ``data/release/``.

A maintainer tool, not part of the reviewer path: it runs once on a machine
holding the original analysis repository and produces the schema-normalised,
checksummed artifacts that ship here.

The evaluation sample drops SPECTER embeddings, abstracts, and reference lists,
none of which any analysis touches, taking 674 MB to a few MB. The three
response files are normalised onto one schema; the originals used two, because
GPT-4o came from a separate pipeline.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dua.bins import bin_label, normalize_field  # noqa: E402
from dua.config import load_config  # noqa: E402
from dua.io import read_csv_rows, sha256, write_csv_rows, write_json  # noqa: E402

csv.field_size_limit(2**31 - 1)

SAMPLE_REL = "sijia/sampled_raw_data_100x13x8.csv"

RESPONSE_SOURCES = {
    "gpt-4o": ("sijia_results/10k/test_10k_eval_answers_version2_prompt_evaluated.csv", "csv"),
    "deepseek-r1": ("outputs/test_enriched_2/api_results_deepseek_deepseek-r1-0528_evaluated.csv", "ndjson-derived"),
    "claude-sonnet-4.5": ("outputs/test_enriched_2/api_results_anthropic_claude-sonnet-4.5_evaluated.csv", "ndjson-derived"),
}

RESPONSE_FIELDS = [
    "paper_id", "model", "title", "year", "field", "citations", "citation_bin",
    "ground_truth_authors", "llm_answer",
    "m", "h", "u", "matched", "hallucinated", "unretrieved",
    "llm_eval_m", "llm_eval_h", "llm_eval_u",
    "api_success", "api_response_time_ms", "api_timestamp", "api_provider",
]

SAMPLE_FIELDS = [
    "paper_id", "record_id", "title", "year", "field", "citations", "citation_bin",
    "n_authors", "authors", "doi", "venue", "doc_type",
]


def _author_names(raw: str) -> list[str]:
    """Semantic Scholar's author list -> plain names, tolerating CSV damage."""
    if not raw:
        return []
    try:
        parsed = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        import re

        return re.findall(r"'name':\s*'([^']+)'", raw) or re.findall(r'"name":\s*"([^"]+)"', raw)
    if isinstance(parsed, list):
        return [a["name"] for a in parsed if isinstance(a, dict) and "name" in a]
    return []


def _int(value, default=0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def build_sample(source: Path, out: Path) -> dict:
    rows, bin_mismatch = [], 0
    with open(source / SAMPLE_REL, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            citations = _int(r["semantic_scholar.citationCount"])
            derived = bin_label(citations)
            if derived != r["citation_bin"]:
                bin_mismatch += 1
            authors = _author_names(r["semantic_scholar.authors"])
            rows.append({
                "paper_id": r["semantic_scholar.paperId"],
                "record_id": r["row_id"],
                "title": r["semantic_scholar.title"] or r["original.title"],
                # Semantic Scholar year: this is what went into the prompt.
                # See dua.sampling.stratified.to_release_row.
                "year": _int(r["semantic_scholar.year"], default=""),
                "field": normalize_field(r["field"]) or r["field"],
                "citations": citations,
                "citation_bin": derived,
                "n_authors": len(authors),
                "authors": json.dumps(authors, ensure_ascii=False),
                "doi": r.get("original.doi", ""),
                "venue": r.get("semantic_scholar.venue") or r.get("original.venue", ""),
                "doc_type": r.get("original.doc_type", ""),
            })
    n = write_csv_rows(out, rows, SAMPLE_FIELDS)
    return {"rows": n, "citation_bin_recomputed_mismatches": bin_mismatch}


def build_responses(source: Path, outdir: Path, sample_index: dict) -> dict:
    from dua.evaluate.ground_truth import extract_author_names
    from dua.evaluate.metrics import parse_counts

    summary = {}
    for model, (rel, origin) in RESPONSE_SOURCES.items():
        rows, unparsable, judge_unparsable = [], 0, 0
        with open(source / rel, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                counts = parse_counts(r.get("hard_code_evaluation"))
                if counts is None:
                    unparsable += 1
                    continue
                judge = parse_counts(r.get("evaluation"))
                if r.get("evaluation") is not None and judge is None:
                    judge_unparsable += 1
                gt = extract_author_names(r.get("ground_truth_authors") or r.get("answer") or [])
                if isinstance(gt, str):
                    gt = [a.strip() for a in gt.split(",") if a.strip()]
                citations = _int(r.get("citation"))
                provider = ""
                envelope = r.get("api_response_full")
                if envelope:
                    try:
                        provider = ast.literal_eval(envelope).get("provider", "")
                    except (ValueError, SyntaxError):
                        provider = ""
                # GPT-4o rows carry a rendered question instead of title/year
                # columns. Backfill both from the evaluation sample, keyed by
                # paper_id, so all three models ship on one schema.
                fallback = sample_index.get(r["paperId"], {})
                title = r.get("title") or fallback.get("title", "")
                if not title and r.get("question", "").find("titled '") >= 0:
                    title = r["question"].split("titled '", 1)[1].rsplit("' which was published", 1)[0]
                year = _int(r.get("year"), default="") or fallback.get("year", "")
                rows.append({
                    "paper_id": r["paperId"],
                    "model": model,
                    "title": title,
                    "year": year,
                    "field": normalize_field(r.get("field")) or r.get("field", ""),
                    "citations": citations,
                    "citation_bin": bin_label(citations),
                    "ground_truth_authors": json.dumps(gt, ensure_ascii=False),
                    "llm_answer": r.get("llm_authors") or r.get("gpt_answer") or "",
                    "m": counts.m, "h": counts.h, "u": counts.u,
                    # LLM-as-judge counts, present only for GPT-4o (Appendix A6.5).
                    "llm_eval_m": judge.m if judge else "",
                    "llm_eval_h": judge.h if judge else "",
                    "llm_eval_u": judge.u if judge else "",
                    "matched": r.get("matched_gt_authors(X)", ""),
                    "hallucinated": r.get("hallucinated_llm_authors(Y)", ""),
                    "unretrieved": r.get("unmatched_gt_authors(Z)", ""),
                    "api_success": r.get("api_success", ""),
                    "api_response_time_ms": r.get("api_response_time_ms", ""),
                    "api_timestamp": r.get("timestamp", ""),
                    "api_provider": provider,
                })
        n = write_csv_rows(outdir / f"{model}.csv.gz", rows, RESPONSE_FIELDS)
        summary[model] = {"rows": n, "unparsable_dropped": unparsable,
                          "llm_judge_unparsable": judge_unparsable, "origin": origin}
    return summary


SURNAME_FREQ_SOURCES = {
    "dataset": "name_frequency_outputs/name_frequencies_overall_20251030_141002.json",
    "gpt-4o": "llm_name_frequency_outputs/openai_gpt-4o_hallucinated_frequencies_overall_20251120_140336.json",
    "claude-sonnet-4.5": "llm_name_frequency_outputs/anthropic_claude-4.5-sonnet_hallucinated_frequencies_overall_20251120_140336.json",
    "deepseek-r1": "llm_name_frequency_outputs/deepseek_deepseek-r1-0528_hallucinated_frequencies_overall_20251120_140336.json",
}


def build_surname_tallies(source: Path, outdir: Path) -> dict:
    """Slim the surname-frequency JSONs down to what Appendix A6.10 uses.

    The originals are 71 MB and 18 MB and carry per-name lists of every paper
    id the name appeared in. Only the last-name tallies are used, so the
    per-paper spread is dropped -- which also means no per-name paper trail
    ships alongside an inferred protected attribute.
    """
    from dua.analysis.name_frequency import write_counts

    outdir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for key, rel in SURNAME_FREQ_SOURCES.items():
        path = source / rel
        if not path.exists():
            summary[key] = {"status": "source missing", "path": rel}
            continue
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        last = payload.get("last", {})
        if key == "dataset":
            counts = {k: int(v) for k, v in last.items()}
            write_counts(outdir / "dataset_surnames.json.gz", counts)
            summary[key] = {"unique_surnames": len(counts),
                            "total_occurrences": sum(counts.values())}
            continue
        population = {k: int(v["paper_count"]) for k, v in last.items()
                      if isinstance(v, dict) and v.get("paper_count", 0) > 0}
        diversity = dict.fromkeys(population, 1)
        write_counts(outdir / f"{key}_hallucinated_population.json.gz", population)
        write_counts(outdir / f"{key}_hallucinated_diversity.json.gz", diversity)
        summary[key] = {"unique_surnames": len(population),
                        "total_paper_appearances": sum(population.values())}
    return summary


def write_checksums(release: Path) -> int:
    """(Re)write checksums.sha256 over everything in the release directory.

    Any edit to a shipped artifact -- even sanitising a path out of a metadata
    file -- invalidates the manifest, and `dua verify` will fail on a fresh
    clone. Rebuilding it is a separate entry point so that is a one-liner
    rather than an ad-hoc script.
    """
    lines = [
        f"{sha256(p)}  {p.relative_to(release)}"
        for p in sorted(release.rglob("*"))
        if p.is_file() and p.name != "checksums.sha256"
    ]
    (release / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path,
                    help="path to the original hallucination_analysis_code tree")
    ap.add_argument("--checksums-only", action="store_true",
                    help="only rewrite checksums.sha256 over the existing release")
    args = ap.parse_args()

    cfg = load_config()
    release = cfg.path("release")
    release.mkdir(parents=True, exist_ok=True)

    if args.checksums_only:
        print(f"wrote {write_checksums(release)} checksums")
        return 0
    if args.source is None:
        ap.error("--source is required unless --checksums-only is given")

    print("building evaluation sample ...")
    sample_stats = build_sample(args.source, release / "eval_sample_9108.csv.gz")
    print(f"  {sample_stats['rows']:,} rows")

    sample_index = {
        row["paper_id"]: {"title": row["title"], "year": row["year"]}
        for row in read_csv_rows(release / "eval_sample_9108.csv.gz")
    }

    print("building model responses ...")
    response_stats = build_responses(args.source, release / "responses", sample_index)
    for model, s in response_stats.items():
        print(f"  {model:20s} {s['rows']:,} rows")

    print("building surname tallies ...")
    surname_stats = build_surname_tallies(args.source, release / "name_frequency")
    for key, s in surname_stats.items():
        print(f"  {key:20s} {s}")

    manifest = {"sample": sample_stats, "responses": response_stats,
                "surname_tallies": surname_stats,
                "expected_rows": cfg["dataset"]["eval_sample_size"]}
    write_json(release / "manifest.json", manifest, seed=cfg.seed)

    print(f"wrote {write_checksums(release)} checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
