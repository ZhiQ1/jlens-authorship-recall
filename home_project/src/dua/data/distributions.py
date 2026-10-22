"""Stage A5: the corpus distribution tables (Section 2.2, Appendix A2.2).

Produces Tables A1–A9: the citation distribution, author-count distribution,
field-of-study distribution, temporal distribution, and the two per-field
breakdowns.

Streaming, not pandas. The original implementation loaded chunks of the 7.3 GB
corpus into DataFrames; this makes one pass and holds only counters, so it
runs on a laptop.

Requires the curated corpus, which is not in this repository. Point at it with
``DUA_CORPUS`` or ``config/config.local.yaml``; see ``README.md``.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from dua.analysis.style import fmt, fmt_int, save_table
from dua.bins import bin_label
from dua.config import load_config
from dua.data.filters import enriched_of
from dua.io import read_ndjson
from dua.sampling.stratified import citation_count, primary_field

SOURCE = "dua.data.distributions"

AUTHOR_GROUPS = [("1", 1, 1), ("2", 2, 2), ("3", 3, 3), ("4", 4, 4), ("5", 5, 5),
                 ("6-10", 6, 10), ("11-20", 11, 20)]
YEAR_GROUPS = [("<1950", 0, 1949), ("1950-1979", 1950, 1979), ("1980-1989", 1980, 1989),
               ("1990-1999", 1990, 1999), ("2000-2009", 2000, 2009),
               ("2010-2019", 2010, 2019)]


def _group(value: int, groups) -> str:
    for label, lo, hi in groups:
        if lo <= value <= hi:
            return label
    return groups[-1][0]


class CorpusStats:
    """Accumulates every distribution in one pass over the corpus."""

    def __init__(self):
        self.n = 0
        self.citation_bins: Counter[str] = Counter()
        self.author_groups: Counter[str] = Counter()
        self.year_groups: Counter[str] = Counter()
        self.fields: Counter[str] = Counter()
        self.all_fields: Counter[str] = Counter()
        # Totals over every primary field, not just the analysed eight, so the
        # 20-row Tables A8/A9 regenerate too.
        self.primary_citations: Counter[str] = Counter()
        self.primary_authors: Counter[str] = Counter()
        self.citations_total = 0
        self.authors_total = 0
        self.citations_by_field: Counter[str] = Counter()
        self.authors_by_field: Counter[str] = Counter()
        self.papers_by_field: Counter[str] = Counter()
        # Exact median needs the whole distribution; citation counts are small
        # integers with a long tail, so a histogram is exact and bounded.
        self.citation_histogram: Counter[int] = Counter()
        self.min_year: int | None = None
        self.max_year: int | None = None

    def add(self, record: dict) -> None:
        enriched = enriched_of(record)
        citations = citation_count(record)
        authors = enriched.get("authors") or []
        n_authors = len(authors) if isinstance(authors, list) else 0

        self.n += 1
        self.citation_bins[bin_label(citations)] += 1
        self.citation_histogram[min(citations, 100_000)] += 1
        self.citations_total += citations
        self.authors_total += n_authors
        if n_authors:
            self.author_groups[_group(n_authors, AUTHOR_GROUPS)] += 1

        # OAG's year first; see the note in dua.sampling.stratified.to_release_row.
        year = (record.get("original") or {}).get("year") or enriched.get("year")
        try:
            year = int(float(year))
        except (TypeError, ValueError):
            year = None
        if year:
            self.year_groups[_group(year, YEAR_GROUPS)] += 1
            self.min_year = year if self.min_year is None else min(self.min_year, year)
            self.max_year = year if self.max_year is None else max(self.max_year, year)

        # The primary field only -- Semantic Scholar's first fieldsOfStudy
        # entry. This is a strict partition over all 1,921,209 papers, which is
        # what Tables A8 and A9 report and what makes the eight fields cover
        # exactly 76.95%. See dua.sampling.stratified.paper_field.
        primary = primary_field(record) or "unknown"
        self.all_fields[primary] += 1
        self.primary_citations[primary] += citations
        self.primary_authors[primary] += n_authors
        field = primary if primary in load_config().field_keys else None
        if field:
            self.fields[field] += 1
            self.papers_by_field[field] += 1
            self.citations_by_field[field] += citations
            self.authors_by_field[field] += n_authors

    # -- derived --------------------------------------------------------
    def median_citations(self) -> float:
        target = self.n / 2
        seen = 0
        for value in sorted(self.citation_histogram):
            seen += self.citation_histogram[value]
            if seen >= target:
                return float(value)
        return float("nan")

    def summary(self) -> dict:
        eight = sum(self.fields.values())
        return {
            "n_papers": self.n,
            "mean_citations": self.citations_total / self.n if self.n else 0.0,
            "median_citations": self.median_citations(),
            "mean_authors": self.authors_total / self.n if self.n else 0.0,
            "single_author_pct": 100 * self.author_groups["1"] / self.n if self.n else 0.0,
            "year_range": [self.min_year, self.max_year],
            "n_disciplines": len(self.all_fields),
            "eight_field_coverage_pct": 100 * eight / self.n if self.n else 0.0,
            "citation_bins": dict(self.citation_bins),
            "author_groups": dict(self.author_groups),
            "year_groups": dict(self.year_groups),
            "primary_field_counts": dict(self.all_fields),
            "per_field": {
                f: {"papers": self.papers_by_field[f],
                    "mean_citations": self.citations_by_field[f] / self.papers_by_field[f],
                    "mean_authors": self.authors_by_field[f] / self.papers_by_field[f]}
                for f in self.papers_by_field
            },
        }


def _tex_label(label: str) -> str:
    """Bin labels are written for humans, not for LaTeX.

    Ranges use an ASCII hyphen and become en-dashes. ``<1950`` carries a bare
    ``<``, which is legal in text mode but renders as an inverted exclamation
    mark under OT1 encoding rather than a less-than sign, so it goes into math
    mode instead.
    """
    return label.replace("-", "--").replace("<", r"$<$").replace(">", r"$>$")


def _cumulative_table(name: str, counts: Counter[str], order: list[str],
                      header: str) -> None:
    total = sum(counts.values()) or 1
    rows, cumulative = [], 0.0
    for label in order:
        count = counts.get(label, 0)
        pct = 100 * count / total
        cumulative += pct
        rows.append([_tex_label(label), fmt_int(count), fmt(pct, 1), fmt(cumulative, 1)])
    rows.append([r"\textbf{Total}", rf"\textbf{{{total:,}}}", r"\textbf{100.0}", ""])
    save_table(name, [rf"\textbf{{{header}}}", r"\textbf{Count}", r"\%",
                      r"\textbf{Cumulative} \%"],
               rows, align="lrrr", source=SOURCE, midrule_before={len(rows) - 1})


def run(corpus: str | Path | None = None, limit: int | None = None) -> dict:
    """One pass over the corpus; writes every distribution table."""
    from itertools import islice

    cfg = load_config()
    corpus = corpus or cfg.path("corpus")
    if not Path(corpus).exists():
        raise FileNotFoundError(
            f"{corpus} is not present. The curated corpus is 7.3 GB gzipped and "
            "is not shipped with this repository; see README.md."
        )

    stats = CorpusStats()
    stream = read_ndjson(corpus)
    for record in (islice(stream, limit) if limit else stream):
        stats.add(record)

    _cumulative_table("citations", stats.citation_bins, cfg.bin_labels, "Citation Range")
    _cumulative_table("authors-dist", stats.author_groups,
                      [g[0] for g in AUTHOR_GROUPS], "Authors")
    _cumulative_table("temporal-dist", stats.year_groups,
                      [g[0] for g in YEAR_GROUPS], "Period")

    summary = stats.summary()

    # Tables A8/A9 cover every primary field, not just the analysed eight, and
    # their rows sum to the corpus exactly. Reporting only the eight would hide
    # the denominator the 76.95% coverage figure is computed against.
    total = stats.n or 1
    fos_rows, author_rows, citation_rows = [], [], []
    for field, papers in stats.all_fields.most_common():
        label = field.title()
        fos_rows.append([label, fmt_int(papers), fmt(100 * papers / total, 2)])
        author_rows.append([label, fmt_int(papers),
                            fmt(stats.primary_authors[field] / papers, 1)])
        citation_rows.append([label, fmt_int(papers),
                              fmt(stats.primary_citations[field] / papers, 1)])

    save_table("fos-dist", [r"\textbf{Field}", r"\textbf{Papers}", r"\%"],
               fos_rows, align="lrr", source=SOURCE)
    for name, rows, header in (
        ("authors-by-field-dist", author_rows, "Mean Authors"),
        ("citations-by-field-dist", citation_rows, "Mean Citations"),
    ):
        ordered = sorted(rows, key=lambda r: -float(r[2]))
        save_table(name, [r"\textbf{Field}", r"\textbf{Papers}", rf"\textbf{{{header}}}"],
                   ordered, align="lrr", source=SOURCE)

    from dua.io import write_json

    write_json(cfg.path("metrics") / "corpus_distributions.json", summary,
               seed=cfg.seed, source=SOURCE)
    return summary
