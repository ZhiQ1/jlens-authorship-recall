#!/usr/bin/env python3
"""Check the ported matcher against the original evaluated CSVs.

The strongest reproducibility claim in the repository: re-scoring every
archived model response with ``dua.evaluate`` reproduces the published
``(M, H, U)`` triple exactly. README.md asserts it, so it should be checkable
by anyone who still has the original analysis tree.

Reviewers do not need this -- the released files already carry the counts. It
exists so the claim is falsifiable rather than merely stated.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dua.evaluate import Evaluator  # noqa: E402

csv.field_size_limit(2**31 - 1)

ARCHIVES = {
    "claude-sonnet-4.5":
        "outputs/test_enriched_2/api_results_anthropic_claude-sonnet-4.5_evaluated.csv",
    "deepseek-r1":
        "outputs/test_enriched_2/api_results_deepseek_deepseek-r1-0528_evaluated.csv",
    "gpt-4o":
        "sijia_results/10k/test_10k_eval_answers_version2_prompt_evaluated.csv",
}


def check(path: Path, max_examples: int = 5) -> dict:
    evaluator = Evaluator()
    n = identical = 0
    mismatches = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n += 1
            got = evaluator.evaluate_record(row).counts_str
            want = row["hard_code_evaluation"]
            if got == want:
                identical += 1
            elif len(mismatches) < max_examples:
                mismatches.append({
                    "paper_id": row.get("paperId") or row.get("record_id"),
                    "published": want, "recomputed": got,
                    "llm_answer": (row.get("llm_authors") or row.get("gpt_answer") or "")[:120],
                })
    return {"n": n, "identical": identical,
            "pct": 100 * identical / n if n else 0.0, "mismatches": mismatches}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, required=True,
                    help="path to the original hallucination_analysis_code tree")
    args = ap.parse_args()

    total = agreed = 0
    failed = False
    for model, rel in ARCHIVES.items():
        path = args.source / rel
        if not path.exists():
            print(f"{model:20s} SKIP  {rel} not found")
            continue
        result = check(path)
        total += result["n"]
        agreed += result["identical"]
        status = "OK" if result["identical"] == result["n"] else "MISMATCH"
        print(f"{model:20s} {status:9s} {result['identical']:,}/{result['n']:,} "
              f"({result['pct']:.3f}%)")
        for m in result["mismatches"]:
            failed = True
            print(f"    {m['paper_id']}: published {m['published']!r}, "
                  f"recomputed {m['recomputed']!r}")
            print(f"      answer: {m['llm_answer']}")

    if total:
        print(f"\n{agreed:,}/{total:,} triples reproduced "
              f"({100 * agreed / total:.3f}%)")
    return 1 if failed or not total else 0


if __name__ == "__main__":
    raise SystemExit(main())
