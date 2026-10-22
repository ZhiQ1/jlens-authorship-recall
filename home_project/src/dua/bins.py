"""Citation binning and field normalisation.

Both operations appear in every stage, and both are places where an
inconsistency would silently shift results, so they live in one module.
"""

from __future__ import annotations

from dua.config import CitationBin, load_config


def bin_label(citations: int, bins: list[CitationBin] | None = None) -> str:
    """Map a citation count to its bin label. Raises on a negative count."""
    if citations < 0:
        raise ValueError(f"negative citation count: {citations}")
    bins = bins or load_config().citation_bins
    for b in bins:
        if b.contains(citations):
            return b.label
    raise ValueError(f"no bin covers {citations} citations; check config.yaml")


def bin_index(label: str, bins: list[CitationBin] | None = None) -> int:
    """Position of a bin label in the canonical ordering, for sorting."""
    bins = bins or load_config().citation_bins
    for i, b in enumerate(bins):
        if b.label == label:
            return i
    raise KeyError(f"unknown citation bin label: {label!r}")


def normalize_field(raw: str | None) -> str | None:
    """Normalise a field-of-study string to a canonical key.

    The corpus stores Semantic Scholar's title-case labels ("Computer
    Science"); the evaluation artifacts store lowercase ("computer science").
    Returns ``None`` for anything outside the eight analysed disciplines.
    """
    if not raw:
        return None
    key = " ".join(str(raw).strip().lower().split())
    return key if key in load_config().fields else None


def field_label(key: str) -> str:
    """Canonical key -> display label used in figures and LaTeX tables."""
    return load_config().fields[key]
