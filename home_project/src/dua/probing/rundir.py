"""Materialise the ``--run_dir`` the Section 7 steering stages read.

Stages 14-24 take a ``--run_dir`` and look for ``scored.tsv`` inside it: the
per-paper output of Stage 1 (generation) and Stage 2 (scoring). The columns
that matter downstream are ``paper_id``, ``hr2``, and ``citation_count`` --
``hr2`` is what the eval pools are selected on.

The release ships it gzipped, and the stages hardcode the bare ``scored.tsv``
filename, so it is decompressed into a working directory rather than read in
place. This is the difference between a Stage 24 re-run needing one GPU-hour
and needing the full 6-12 hour extraction first.
"""

from __future__ import annotations

import gzip
import shutil
from pathlib import Path

MODELS = ("qwen3_32b", "mistral_small_3_2_24b")
SCORED = "scored.tsv"


def materialize_run_dir(release: Path, model: str, out_dir: Path) -> Path:
    if model not in MODELS:
        raise ValueError(f"unknown model {model!r}; expected one of {MODELS}")
    src = release / "probing" / "runs" / model / f"{SCORED}.gz"
    if not src.exists():
        raise FileNotFoundError(f"{src} is not in this release")
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / SCORED
    with gzip.open(src, "rb") as f_in, open(dst, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return dst
