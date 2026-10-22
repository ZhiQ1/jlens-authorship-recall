#!/usr/bin/env python3
"""Compile every generated table in isolation.

The paper's hand-typed tables are meant to be replaced with
`\input{results/tables/<name>.tex}`. That is only safe if the generated files
actually compile, so this checks each one in a minimal document with the same
packages the paper loads.

Catches the failure modes that matter: a `\multicolumn` whose span does not
match the cells around it, an unescaped `_` or `%` from a data value, a column
count that drifts from the `\begin{tabular}` preamble.

    python tools/check_tables_compile.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dua.config import load_config  # noqa: E402

PREAMBLE = r"""
\documentclass[11pt]{article}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{multirow}
\usepackage{graphicx}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\begin{document}
"""


def compile_one(table: Path, workdir: Path, engine: str) -> tuple[bool, str]:
    tex = workdir / "check.tex"
    tex.write_text(
        PREAMBLE + f"\\input{{{table.resolve()}}}\n\\end{{document}}\n", encoding="utf-8"
    )
    result = subprocess.run(
        [engine, "-interaction=nonstopmode", "-halt-on-error", "check.tex"],
        cwd=workdir, capture_output=True, text=True, timeout=120,
    )
    if result.returncode == 0:
        return True, ""
    log = (workdir / "check.log")
    text = log.read_text(encoding="utf-8", errors="ignore") if log.exists() else result.stdout
    errors = [ln for ln in text.splitlines() if ln.startswith("!")]
    return False, errors[0] if errors else "unknown LaTeX error"


def main() -> int:
    engine = next((e for e in ("pdflatex", "lualatex", "xelatex") if shutil.which(e)), None)
    if engine is None:
        print("no LaTeX engine found; skipping", file=sys.stderr)
        return 0

    tables = sorted(load_config().path("tables").glob("*.tex"))
    if not tables:
        print("no generated tables; run `dua analyse` first", file=sys.stderr)
        return 1

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for table in tables:
            ok, error = compile_one(table, workdir, engine)
            if not ok:
                failures.append((table.name, error))
                print(f"FAIL  {table.name}\n        {error}")

    print(f"\n{len(tables) - len(failures)}/{len(tables)} tables compile with {engine}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
