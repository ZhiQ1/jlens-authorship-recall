"""Stage C1: the 6,048-paper proxy sub-sample (Section 3).

Approximately 500 papers per citation bin, drawn from the 1.92M corpus, with
shortfalls in the top bins where the corpus itself runs out (the 2,049-4,096
bin holds 508 papers and the 4,097+ bin holds 178).

This is a *bin*-stratified draw, not a (field, bin) draw like Stage B: the
proxy analyses in Section 3 are about citation level, not discipline.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from dua.bins import bin_label
from dua.config import load_config
from dua.io import read_ndjson
from dua.sampling.stratified import citation_count, to_release_row
from dua.seeds import rng


def draw(corpus: str | Path, *, per_bin: int | None = None,
         seed: int | None = None) -> tuple[list[dict], dict]:
    """Draw the proxy sub-sample. Returns ``(rows, report)``."""
    cfg = load_config()
    per_bin = per_bin or cfg["proxy"]["per_bin"]
    seed = cfg.seed if seed is None else seed

    offsets_by_bin: dict[str, list[int]] = defaultdict(list)
    for offset, record in read_ndjson(corpus, with_index=True):
        offsets_by_bin[bin_label(citation_count(record))].append(offset)

    selected, report = set(), []
    for label in cfg.bin_labels:
        pool = sorted(offsets_by_bin.get(label, []))
        if len(pool) <= per_bin:
            picked = pool
        else:
            gen = rng(seed, "proxy_subsample", label)
            picked = [pool[i] for i in sorted(gen.choice(len(pool), per_bin, replace=False))]
        selected.update(picked)
        report.append({"citation_bin": label, "available": len(pool), "selected": len(picked)})

    from dua.sampling.stratified import collect_selected

    rows = [to_release_row(r) for r in collect_selected(corpus, selected)]
    return rows, {"per_bin": report, "n_selected": len(rows), "seed": seed,
                  "target_per_bin": per_bin}
