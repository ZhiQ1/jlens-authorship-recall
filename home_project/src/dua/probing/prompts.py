"""Rebuild the prompt CSV the Section 7 stages take as ``--data_csv``.

The stages read ``paperId, question, answer, citation, citation_bin, field`` --
a *view* of the released evaluation sample, rebuilt here rather than shipped
twice. Without it no GPU stage can be re-run, because the release uses
different column names and holds authors as JSON.

The question is a fixed template, so prompts reproduce exactly. The ``answer``
column differs for 68 of the 9,108 papers: the original stripped apostrophes
from surnames and the release keeps them. Scoring is unaffected -- the matcher
normalises them away on both sides.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

QUESTION_TEMPLATE = (
    "Who are the authors of the paper titled '{title}' which was published in {year}?"
)

# The column order the stages' ``load_ground_truth`` expects to find.
PROMPT_COLUMNS = ["paperId", "citation", "citation_bin", "field", "question", "answer"]


def _authors_to_answer(raw: str) -> str:
    """The release stores authors as a JSON list; the stages want one string."""
    try:
        names = json.loads(raw)
    except (TypeError, ValueError):
        return str(raw)
    return ", ".join(str(n) for n in names)


def build_prompt_frame(sample: pd.DataFrame) -> pd.DataFrame:
    missing = {"paper_id", "title", "year", "authors", "citations",
               "citation_bin", "field"} - set(sample.columns)
    if missing:
        raise ValueError(f"evaluation sample is missing columns: {sorted(missing)}")
    years = sample["year"].astype("Int64").astype(str)
    return pd.DataFrame({
        "paperId": sample["paper_id"].astype(str),
        "citation": sample["citations"].astype("Int64"),
        "citation_bin": sample["citation_bin"].astype(str),
        "field": sample["field"].astype(str),
        "question": [QUESTION_TEMPLATE.format(title=t, year=y)
                     for t, y in zip(sample["title"].astype(str), years, strict=True)],
        "answer": sample["authors"].map(_authors_to_answer),
    })[PROMPT_COLUMNS]


def build_prompt_csv(sample_path: Path, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frame = build_prompt_frame(pd.read_csv(sample_path))
    frame.to_csv(out_path, index=False)
    return len(frame)
