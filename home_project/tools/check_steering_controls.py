#!/usr/bin/env python3
"""Compare a Stage 24 re-run against the shipped Table A25 artifact.

Table A25 quotes Stage 24's `eval_high` arms: the diff-of-means steer, the
probe-direction steer, and the spread over five norm-matched random control
directions. `make steering-controls` regenerates them on a GPU; this says
whether the regenerated numbers agree with what is in `data/release/`.

    python tools/check_steering_controls.py <rerun_out_dir> [--model qwen3_32b]

The model is inferred from the re-run's meta when `--model` is omitted. Exit
status is 1 on any disagreement beyond `--tol` percentage points, so this is
usable as a CI gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dua.config import load_config  # noqa: E402

RESULTS_CSV = "position_probe_results_eval_high.csv"
META_JSON = "position_probe_meta_eval_high.json"
# Every steered arm A8.8 quotes writes the vector at every position; the
# p1_and_gen and prompt_only rows are the E3 ablation and are not compared.
KEY = ["condition", "vector", "positions", "seed"]


def infer_model(rerun: Path) -> str | None:
    meta_path = rerun / META_JSON
    if not meta_path.exists():
        return None
    model_path = json.loads(meta_path.read_text(encoding="utf-8")).get("model_path", "")
    name = Path(model_path).name.lower()
    if "qwen" in name:
        return "qwen3_32b"
    if "mistral" in name:
        return "mistral_small_3_2_24b"
    return None


def load_arms(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Baseline carries positions="none"; every steered arm A8.8 quotes is "all".
    df = df[(df["positions"] == "all") | (df["condition"] == "baseline")].copy()
    df["seed"] = df["seed"].astype(int)
    return df.set_index(KEY)["hallucination_rate_pct"].astype(float)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rerun_dir", type=Path, help="--out_dir of the Stage 24 re-run")
    ap.add_argument("--model", default=None, choices=["qwen3_32b", "mistral_small_3_2_24b"])
    ap.add_argument("--tol", type=float, default=0.0,
                    help="allowed disagreement in percentage points (default: exact)")
    args = ap.parse_args()

    model = args.model or infer_model(args.rerun_dir)
    if model is None:
        print("Could not infer the model; pass --model.", file=sys.stderr)
        return 2

    shipped_path = (load_config().path("release") / "probing" / "steering" / model
                    / "position_probe" / RESULTS_CSV)
    rerun_path = args.rerun_dir / RESULTS_CSV
    for p in (shipped_path, rerun_path):
        if not p.exists():
            print(f"Missing: {p}", file=sys.stderr)
            return 2

    shipped, rerun = load_arms(shipped_path), load_arms(rerun_path)
    print(f"Stage 24 eval_high arms, {model}: re-run vs data/release/\n")

    only_shipped = shipped.index.difference(rerun.index)
    only_rerun = rerun.index.difference(shipped.index)
    failures = 0
    for arm in shipped.index.union(rerun.index):
        label = " ".join(str(x) for x in arm)
        if arm in only_shipped or arm in only_rerun:
            where = "shipped only" if arm in only_shipped else "re-run only"
            print(f"  MISSING  {label:<48s} ({where})")
            failures += 1
            continue
        a, b = shipped[arm], rerun[arm]
        ok = abs(a - b) <= args.tol
        failures += not ok
        print(f"  {'ok  ' if ok else 'DIFF'}     {label:<48s} {a:6.1f}  vs {b:6.1f}")

    controls = [i for i in shipped.index if i[0] == "random_control"]
    if controls:
        lo, hi = min(shipped[i] for i in controls), max(shipped[i] for i in controls)
        rlo, rhi = min(rerun.get(i, float("nan")) for i in controls), \
            max(rerun.get(i, float("nan")) for i in controls)
        print(f"\n  control range: shipped {lo:.1f}--{hi:.1f}  re-run {rlo:.1f}--{rhi:.1f}")

    print(f"\n{'FAIL' if failures else 'OK'}: {failures} disagreement(s) at tol={args.tol}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
