"""Reading and writing project artifacts.

Two rules this module exists to enforce:

* **Every generated artifact carries provenance.** JSON and LaTeX outputs get
  a header naming the script, the git commit, the seed, and the UTC time they
  were produced. That is what makes a figure and the prose beside it
  checkable against each other months later.
* **Writes are atomic.** A killed job leaves the previous artifact intact
  rather than a truncated file that looks valid.
"""

from __future__ import annotations

import csv
import gzip
import json
import os
import subprocess
import sys
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


# --------------------------------------------------------------------------
# provenance
# --------------------------------------------------------------------------

def git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=Path(__file__).resolve().parents[2],
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def provenance(seed: int | None = None, **extra: Any) -> dict[str, Any]:
    """The header block embedded in every generated artifact."""
    meta = {
        "generated_by": Path(sys.argv[0]).name if sys.argv and sys.argv[0] else "python",
        "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_commit": git_commit(),
    }
    if seed is not None:
        meta["seed"] = seed
    meta.update(extra)
    return meta


# --------------------------------------------------------------------------
# atomic writes
# --------------------------------------------------------------------------

def _atomic_write_text(path: Path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return path


def write_json(path: str | Path, payload: Any, *, seed: int | None = None, **extra: Any) -> Path:
    """Write a JSON artifact with a ``_meta`` provenance header."""
    body = {"_meta": provenance(seed, **extra)}
    if isinstance(payload, dict):
        body.update(payload)
    else:
        body["data"] = payload
    return _atomic_write_text(Path(path), json.dumps(body, indent=2, ensure_ascii=False) + "\n")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_latex_table(path: str | Path, body: str, *, source: str, seed: int | None = None) -> Path:
    """Write a generated LaTeX table for the paper to ``\\input``.

    ``body`` is the tabular environment only, so the caption and label stay
    in the paper where an author can edit them.
    """
    meta = provenance(seed, source=source)
    header = "\n".join(f"% {k}: {v}" for k, v in meta.items())
    return _atomic_write_text(
        Path(path),
        f"% GENERATED FILE -- do not edit by hand.\n{header}\n{body.rstrip()}\n",
    )


# --------------------------------------------------------------------------
# streaming readers
# --------------------------------------------------------------------------

def _open(path: Path, mode: str = "rt"):
    return gzip.open(path, mode, encoding="utf-8") if path.suffix == ".gz" else open(
        path, mode, encoding="utf-8", newline="" if "b" not in mode else None
    )


def read_ndjson(path: str | Path, *, with_index: bool = False) -> Iterator[Any]:
    """Stream an NDJSON or NDJSON.GZ file. Malformed lines are skipped.

    The 1.92M-paper corpus is 7.3 GB gzipped; nothing in this package loads it
    into memory.
    """
    path = Path(path)
    with _open(path) as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            yield (i, record) if with_index else record


def write_ndjson(path: str | Path, records: Iterable[Any]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    n = 0
    with _open(tmp, "wt") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
    os.replace(tmp, path)
    return n


def read_csv_rows(path: str | Path) -> Iterator[dict[str, str]]:
    """Stream a CSV (optionally gzipped) as dicts, tolerating huge fields."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def write_csv_rows(path: str | Path, rows: Iterable[dict[str, Any]],
                   fieldnames: list[str] | None = None) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = iter(rows)
    try:
        first = next(rows)
    except StopIteration:
        return 0
    fieldnames = fieldnames or list(first.keys())
    tmp = path.with_suffix(path.suffix + ".tmp")
    opener = gzip.open if path.suffix == ".gz" else open
    n = 0
    with opener(tmp, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in (first, *rows):
            writer.writerow(row)
            n += 1
    os.replace(tmp, path)
    return n


def sha256(path: str | Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
