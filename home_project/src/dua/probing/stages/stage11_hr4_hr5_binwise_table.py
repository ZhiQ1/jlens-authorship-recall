"""Stage 11: per-model, per-citation-bin HR4, HR5, and |HR4 - HR5| means.

Usage
-----
  python -m dua.probing.stages.stage11_hr4_hr5_binwise_table \
    --inputs \
      gpt4o=/path/to/gpt4o_evaluated.csv \
      deepseek_r1=/path/to/deepseek_evaluated.csv \
      claude_sonnet_4_5=/path/to/claude_evaluated.csv \
    --out_dir results/hr4_hr5_binwise
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


BIN_ORDER = [
    "0-2",
    "3-4",
    "5-8",
    "9-16",
    "17-32",
    "33-64",
    "65-128",
    "129-256",
    "257-512",
    "513-1024",
    "1025-2048",
    "2049-4096",
    "4097+",
]
MODEL_LABELS = {
    "gpt4o": "GPT-4o",
    "deepseek_r1": "DeepSeek-R1",
    "claude_sonnet_4_5": "Claude Sonnet 4.5",
}


def parse_inputs(items: list[str]) -> dict[str, Path]:
    inputs: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--inputs entries must be name=/path, got {item!r}")
        name, path = item.split("=", 1)
        name = name.strip()
        path = path.strip()
        if not name or not path:
            raise ValueError(f"Invalid --inputs entry: {item!r}")
        inputs[name] = Path(path).expanduser().resolve()
    if not inputs:
        raise ValueError("No inputs supplied")
    return inputs


def parse_counts(row: dict) -> tuple[float, float, float] | None:
    if row.get("hard_code_evaluation"):
        parts = [p.strip() for p in str(row["hard_code_evaluation"]).split(",")]
        if len(parts) == 3:
            try:
                return float(parts[0]), float(parts[1]), float(parts[2])
            except ValueError:
                pass
    for keys in [
        ("matched_gt_authors(X)", "hallucinated_llm_authors(Y)", "unmatched_gt_authors(Z)"),
        ("X", "Y", "Z"),
        ("n_match", "n_hal", "n_unretr"),
    ]:
        if all(k in row for k in keys):
            try:
                return tuple(float(row[k] or 0.0) for k in keys)  # type: ignore[return-value]
            except ValueError:
                return None
    return None


def hr4(matched: float, hallucinated: float) -> float:
    denom = matched + hallucinated
    return math.nan if denom == 0 else hallucinated / denom


def hr5(matched: float, unmatched: float) -> float:
    denom = matched + unmatched
    return math.nan if denom == 0 else unmatched / denom


def mean(values: list[float]) -> float:
    clean = [v for v in values if not math.isnan(v)]
    return math.nan if not clean else sum(clean) / len(clean)


def read_model_rows(model: str, path: Path) -> list[dict]:
    by_bin: dict[str, dict[str, list[float] | int]] = {
        b: {"hr4": [], "hr5": [], "citation": [], "n": 0}
        for b in BIN_ORDER
    }
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "citation_bin" not in (reader.fieldnames or []):
            raise ValueError(f"{path} missing citation_bin")
        for row in reader:
            citation_bin = str(row.get("citation_bin", "")).strip()
            if citation_bin not in by_bin:
                continue
            counts = parse_counts(row)
            if counts is None:
                continue
            matched, hallucinated, unmatched = counts
            h4 = hr4(matched, hallucinated)
            h5 = hr5(matched, unmatched)
            by_bin[citation_bin]["hr4"].append(h4)  # type: ignore[index,union-attr]
            by_bin[citation_bin]["hr5"].append(h5)  # type: ignore[index,union-attr]
            if row.get("citation") not in (None, ""):
                try:
                    by_bin[citation_bin]["citation"].append(float(row["citation"]))  # type: ignore[index,union-attr]
                except ValueError:
                    pass
            by_bin[citation_bin]["n"] = int(by_bin[citation_bin]["n"]) + 1

    rows: list[dict] = []
    for citation_bin in BIN_ORDER:
        vals = by_bin[citation_bin]
        mean_hr4 = mean(vals["hr4"])  # type: ignore[arg-type]
        mean_hr5 = mean(vals["hr5"])  # type: ignore[arg-type]
        rows.append({
            "model": model,
            "model_label": MODEL_LABELS.get(model, model),
            "citation_bin": citation_bin,
            "n": vals["n"],
            "mean_citation": mean(vals["citation"]),  # type: ignore[arg-type]
            "mean_hr4": mean_hr4,
            "mean_hr5": mean_hr5,
            "abs_hr4_hr5_diff": abs(mean_hr4 - mean_hr5),
        })
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_latex(path: Path, rows: list[dict]) -> None:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\captionsetup{font=small}",
        "\\footnotesize",
        "\\setlength{\\tabcolsep}{4pt}",
        "\\begin{tabular}{llrrrr}",
        "\\toprule",
        "\\textbf{Model} & \\textbf{Citation bin} & \\textbf{$n$} & \\textbf{HR$_4$} & \\textbf{HR$_5$} & \\textbf{$|\\Delta|$} \\\\",
        "\\midrule",
    ]
    last_model = None
    for row in rows:
        if last_model is not None and row["model_label"] != last_model:
            lines.append("\\midrule")
        lines.append(
            f"{row['model_label']} & {str(row['citation_bin']).replace('-', '--')} & "
            f"{int(row['n'])} & "
            f"{float(row['mean_hr4']):.3f} & "
            f"{float(row['mean_hr5']):.3f} & "
            f"{float(row['abs_hr4_hr5_diff']):.3f} \\\\"
        )
        last_model = row["model_label"]
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Per-model HR$_4$ and HR$_5$ by citation bin. HR$_4$ measures fabricated-name rate among generated authors; HR$_5$ measures omitted-name rate among ground-truth authors. $|\\Delta|$ is the absolute difference between the two bin means.}",
        "\\label{tab:hr4_hr5_binwise_by_model}",
        "\\end{table*}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary(path: Path, rows: list[dict]) -> None:
    by_model: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if int(row["n"]) > 0:
            by_model[row["model_label"]].append(row)

    lines = ["# HR4/HR5 Per-Model Bin-Wise Summary", ""]
    for model, group in by_model.items():
        diffs = [float(r["abs_hr4_hr5_diff"]) for r in group]
        lines.append(f"- {model}: mean |HR4-HR5| = {sum(diffs) / len(diffs):.3f}; max = {max(diffs):.3f}.")
    all_diffs = [float(r["abs_hr4_hr5_diff"]) for r in rows if int(r["n"]) > 0]
    if all_diffs:
        lines.append("")
        lines.append(f"Overall across model-bin cells: mean |HR4-HR5| = {sum(all_diffs) / len(all_diffs):.3f}; max = {max(all_diffs):.3f}.")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 11: per-model HR4/HR5 bin-wise appendix table")
    parser.add_argument("--inputs", nargs="+", required=True, help="Evaluated CSVs as model=/path")
    parser.add_argument("--out_dir", required=True, help="Output directory")
    args = parser.parse_args()

    inputs = parse_inputs(args.inputs)
    rows: list[dict] = []
    for model, path in inputs.items():
        if not path.exists():
            raise FileNotFoundError(path)
        model_rows = read_model_rows(model, path)
        rows.extend(model_rows)
        valid = [r for r in model_rows if int(r["n"]) > 0]
        max_diff = max(float(r["abs_hr4_hr5_diff"]) for r in valid)
        mean_diff = sum(float(r["abs_hr4_hr5_diff"]) for r in valid) / len(valid)
        print(f"[stage11] {MODEL_LABELS.get(model, model)}: {sum(int(r['n']) for r in valid)} rows; mean |diff|={mean_diff:.3f}; max={max_diff:.3f}")

    out_dir = Path(args.out_dir).expanduser().resolve()
    fields = ["model", "model_label", "citation_bin", "n", "mean_citation", "mean_hr4", "mean_hr5", "abs_hr4_hr5_diff"]
    write_csv(out_dir / "hr4_hr5_binwise_by_model.csv", rows, fields)
    write_latex(out_dir / "hr4_hr5_binwise_by_model.tex", rows)
    write_summary(out_dir / "hr4_hr5_binwise_by_model_summary.md", rows)
    print(f"[stage11] Wrote outputs to {out_dir}")


if __name__ == "__main__":
    main()
