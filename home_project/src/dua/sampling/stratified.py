"""Stage B: the 9,108-paper stratified evaluation sample (Section 4.1).

The original draw lived in a collector notebook with ``RANDOM_SEED = None``,
which left the paper's most load-bearing object unreproducible. This is a
seeded, standalone draw: two passes over the corpus, recording then re-reading
line offsets so the 1.92M papers never load into memory, taking up to
``sampling.per_stratum`` papers per (field, bin) stratum without replacement.
Short strata contribute everything, which is the 9,108 against 10,400 gap.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from dua.bins import bin_label
from dua.config import load_config
from dua.io import read_ndjson
from dua.seeds import rng


def citation_count(record: dict) -> int:
    """Citation count, from Semantic Scholar only.

    **No fallback to OAG's ``n_citation``.** Falling back on zero moves 9,975
    papers out of the 0-2 bin and breaks all thirteen bin counts in Table 1;
    Semantic Scholar alone reproduces all thirteen exactly. OAG also stopped
    updating in 2019, so mixing the two makes the citation axis mean different
    things from row to row.
    """
    enriched = record.get("semantic_scholar") or record.get(record.get("source") or "", {})
    if not isinstance(enriched, dict):
        enriched = {}
    return int(enriched.get("citationCount") or 0)


def primary_field(record: dict) -> str | None:
    """Semantic Scholar's primary field: the first ``fieldsOfStudy`` entry.

    A strict partition, and what Section 2.2 is computed over: it places
    1,478,297 of 1,921,209 papers in the eight fields -- the 76.95% the paper
    quotes -- and reproduces the per-field counts in Tables A8 and A9.
    """
    enriched = record.get("semantic_scholar") or record.get(record.get("source") or "", {})
    if not isinstance(enriched, dict):
        return None
    fields = enriched.get("fieldsOfStudy")
    if not isinstance(fields, list) or not fields:
        return None
    return str(fields[0]).strip().lower() or None


def paper_field(record: dict) -> str | None:
    """The field a paper is *stratified* under, or None.

    The first ``fieldsOfStudy`` entry among the eight analysed fields, in the
    order Semantic Scholar lists them -- not config order, and not strictly the
    first entry.

    Deliberately not :func:`primary_field`. This rule reproduces the released
    sample's stored field for 100.00% of locatable papers, against 98.31% for
    strict primary field and 68.87% for config order, where whichever field is
    listed first absorbs every multi-field paper. Corpus statistics use
    ``primary_field`` instead, because Section 2.2 needs a strict partition.
    """
    enriched = record.get("semantic_scholar") or record.get(record.get("source") or "", {})
    if not isinstance(enriched, dict):
        return None
    fields = enriched.get("fieldsOfStudy")
    if not isinstance(fields, list):
        return None
    keys = set(load_config().field_keys)
    for raw in fields:
        key = str(raw).strip().lower()
        if key in keys:
            return key
    return None


def index_strata(corpus: str | Path) -> dict[tuple[str, str], list[int]]:
    """Pass 1: line offsets of every eligible paper, per stratum."""
    strata: dict[tuple[str, str], list[int]] = defaultdict(list)
    for offset, record in read_ndjson(corpus, with_index=True):
        field = paper_field(record)
        if field is None:
            continue
        strata[(field, bin_label(citation_count(record)))].append(offset)
    return dict(strata)


def select_offsets(strata: dict[tuple[str, str], list[int]], *,
                   per_stratum: int | None = None, seed: int | None = None) -> dict:
    """Choose which offsets to keep. Deterministic given the strata and seed."""
    cfg = load_config()
    per_stratum = per_stratum or cfg["sampling"]["per_stratum"]
    seed = cfg.seed if seed is None else seed

    selected: set[int] = set()
    report = []
    # Iterate in canonical order so the report is stable, not dict-ordered.
    for field in cfg.field_keys:
        for label in cfg.bin_labels:
            available = strata.get((field, label), [])
            if not available:
                report.append({"field": field, "citation_bin": label,
                               "available": 0, "selected": 0})
                continue
            pool = sorted(available)  # sort so the draw cannot depend on file order
            if len(pool) <= per_stratum:
                picked = pool
            else:
                gen = rng(seed, "sample", field, label)
                picked = [pool[i] for i in sorted(gen.choice(len(pool), per_stratum,
                                                             replace=False))]
            selected.update(picked)
            report.append({"field": field, "citation_bin": label,
                           "available": len(pool), "selected": len(picked)})

    return {
        "offsets": sorted(selected),
        "strata": report,
        "n_selected": len(selected),
        "n_populated_strata": sum(1 for r in report if r["available"] > 0),
        "theoretical_max": cfg["sampling"]["theoretical_max"],
        "seed": seed,
        "per_stratum": per_stratum,
    }


def collect_selected(corpus: str | Path, offsets: set[int]) -> Iterator[dict]:
    """Pass 2: re-read only the selected lines, in corpus order."""
    remaining = set(offsets)
    for offset, record in read_ndjson(corpus, with_index=True):
        if offset in remaining:
            remaining.discard(offset)
            yield record
            if not remaining:
                return


def to_release_row(record: dict) -> dict[str, Any]:
    """Reduce a corpus record to the released sample schema."""
    import json

    enriched = record.get("semantic_scholar") or record.get(record.get("source") or "", {})
    enriched = enriched if isinstance(enriched, dict) else {}
    original = record.get("original") or {}
    authors = [a["name"] for a in enriched.get("authors", []) if isinstance(a, dict) and "name" in a]
    citations = citation_count(record)
    return {
        "paper_id": enriched.get("paperId"),
        "record_id": record.get("row_id"),
        "title": enriched.get("title") or original.get("title"),
        # Semantic Scholar's year, not OAG's, because THIS year goes into the
        # prompt ("...which was published in {year}?"). The archived responses
        # were collected with it, so a fresh draw must use the same source or
        # re-collection would send different prompts.
        #
        # The two disagree for about 0.02% of the corpus: OAG stopped in 2019,
        # while Semantic Scholar sometimes carries a later re-publication or
        # record-update date. One paper in the 9,108-sample is affected (S2
        # says 2020, OAG says 2019), and the archived prompt used 2020.
        # dua.data.distributions prefers OAG for the Section 2.2 temporal
        # table, where the paper's 1800-2019 range is the claim being made.
        "year": enriched.get("year") or original.get("year"),
        "field": paper_field(record),
        "citations": citations,
        "citation_bin": bin_label(citations),
        "n_authors": len(authors),
        "authors": json.dumps(authors, ensure_ascii=False),
        "doi": original.get("doi", ""),
        "venue": enriched.get("venue") or original.get("venue", ""),
        "doc_type": original.get("doc_type", ""),
    }


def draw(corpus: str | Path, *, per_stratum: int | None = None,
         seed: int | None = None) -> tuple[list[dict], dict]:
    """Draw the evaluation sample. Returns ``(rows, report)``."""
    strata = index_strata(corpus)
    selection = select_offsets(strata, per_stratum=per_stratum, seed=seed)
    rows = [to_release_row(r) for r in collect_selected(corpus, set(selection["offsets"]))]
    selection.pop("offsets")
    return rows, selection


def verify_against(rows: list[dict], released: str | Path) -> dict:
    """Compare a fresh draw against the released sample, by paper id.

    Reports overlap rather than asserting equality: the released sample was
    drawn from an earlier build of this pipeline, whose pool is not the corpus
    built here -- 81 of its papers are rejected by the filter in
    ``dua.data.filters``, and its high-citation strata are thinner. Checks that
    strata sizes and marginal distributions agree.
    """
    import pandas as pd

    fresh = pd.DataFrame(rows)
    published = pd.read_csv(released)
    fresh_ids, published_ids = set(fresh["paper_id"]), set(published["paper_id"])
    return {
        "n_fresh": len(fresh),
        "n_published": len(published),
        "n_shared_paper_ids": len(fresh_ids & published_ids),
        "jaccard": len(fresh_ids & published_ids) / len(fresh_ids | published_ids)
        if fresh_ids | published_ids else 0.0,
        "per_bin_counts_match": (
            fresh["citation_bin"].value_counts().sort_index().to_dict()
            == published["citation_bin"].value_counts().sort_index().to_dict()
        ),
        "per_field_counts_match": (
            fresh["field"].value_counts().sort_index().to_dict()
            == published["field"].value_counts().sort_index().to_dict()
        ),
    }
