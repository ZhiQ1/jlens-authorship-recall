"""Stage 21: does localization predict editing efficacy (Hase et al.)?

Joins the two localization curves -- probe decodability R2 from Stage 8 and
causal-tracing recovery from Stage 19 -- against the editing-efficacy curves
from Stages 18 and 20, and reports Spearman correlations per model. With only
4-5 layers these are descriptive, not significance tests; the sign and the
overlay carry the story. Reads result CSVs only, no GPU.

Usage
─────
  python -m dua.probing.stages.analyze_localization_vs_editing \
      --results_root results \
      --probe_csv results/prevalence_appendix/validated_strategy_layer_prevalence.csv \
      --models qwen3_32b mistral_small_3_2_24b \
      --out_dir results/localization_vs_editing
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import spearmanr
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover - scipy expected in .venv, but degrade gracefully
    _HAVE_SCIPY = False


def _spearman(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    """Spearman rho over paired finite values. Returns (rho, p, n)."""
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan"), float("nan"), n
    if _HAVE_SCIPY:
        rho, p = spearmanr(x, y)
        return float(rho), float(p), n
    # Fallback: Pearson on ranks, no p-value.
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    rho = float(np.corrcoef(rx, ry)[0, 1])
    return rho, float("nan"), n


def load_probe_r2(probe_csv: Path, model: str) -> pd.DataFrame:
    df = pd.read_csv(probe_csv)
    sub = df[(df["model"] == model) & (df["strategy"] == "p1")]
    if sub.empty:
        return pd.DataFrame(columns=["layer", "probe_r2"])
    return sub[["layer_idx", "r2_cv"]].rename(
        columns={"layer_idx": "layer", "r2_cv": "probe_r2"}).reset_index(drop=True)


def load_causal_tracing(results_dir: Path) -> pd.DataFrame:
    p = results_dir / "causal_tracing_results.csv"
    if not p.exists():
        return pd.DataFrame(columns=["layer", "ct_recovery"])
    df = pd.read_csv(p)
    return df[["layer", "mean_recovery"]].rename(columns={"mean_recovery": "ct_recovery"})


def load_induce_effect(results_dir: Path) -> pd.DataFrame:
    """Stage 18: HR raise vs baseline, per layer (single-alpha induce sweep)."""
    p = results_dir / "layer_sweep_results.csv"
    if not p.exists():
        return pd.DataFrame(columns=["layer", "induce_effect"])
    df = pd.read_csv(p)
    base = df[df["condition"] == "baseline"]["hallucination_rate_pct"]
    baseline_hr = float(base.iloc[0]) if len(base) else float("nan")
    steer = df[df["condition"] == "steering"][["layer", "hallucination_rate_pct"]].copy()
    steer["induce_effect"] = steer["hallucination_rate_pct"] - baseline_hr
    return steer[["layer", "induce_effect"]].reset_index(drop=True)


def load_fix_effect(results_dir: Path, band_tag: str) -> pd.DataFrame:
    """Stage 20: best HR reduction any alpha achieves vs baseline, per layer.

    Also carries the norm-matched control's best reduction so a per-layer fix
    'effect' can be read against chance."""
    cands = sorted(results_dir.glob(f"fix_layer_sweep_results_{band_tag}*.csv"))
    if not cands:
        cands = sorted(results_dir.glob("fix_layer_sweep_results_*.csv"))
    if not cands:
        return pd.DataFrame(columns=["layer", "fix_effect", "control_effect"])
    df = pd.read_csv(cands[0])
    base = df[df["condition"] == "baseline"]["hallucination_rate_pct"]
    baseline_hr = float(base.iloc[0]) if len(base) else float("nan")
    out = []
    for L, g in df[df["condition"] == "fix"].groupby("layer"):
        best_fix_hr = float(g["hallucination_rate_pct"].min())  # lowest HR = best repair
        ctrl = df[(df["condition"] == "control_norm_matched") & (df["layer"] == L)]
        best_ctrl_hr = float(ctrl["hallucination_rate_pct"].min()) if len(ctrl) else float("nan")
        out.append({"layer": int(L),
                    "fix_effect": baseline_hr - best_fix_hr,
                    "control_effect": baseline_hr - best_ctrl_hr})
    return pd.DataFrame(out)


def analyze_model(model: str, results_dir: Path, probe_csv: Path, band_tag: str,
                  exclude_layers: set[int] | None = None) -> dict | None:
    exclude_layers = exclude_layers or set()
    probe = load_probe_r2(probe_csv, model)
    ct = load_causal_tracing(results_dir)
    induce = load_induce_effect(results_dir)
    fix = load_fix_effect(results_dir, band_tag)

    if ct.empty and induce.empty and fix.empty:
        print(f"[stage21] {model}: no result CSVs found under {results_dir} — skipping")
        return None

    # Shared layer axis = layers that appear in the editing sweeps, minus any
    # excluded layers. The final decoder layer is excluded by default for the
    # correlation because restoring/steering the P1 state there degenerates to
    # an output-readout nudge (no layer L+1 to cache/attend), inflating causal-
    # tracing "recovery" without telling you where the fact lives — the same
    # last-layer artifact Stage 18 documents. See --exclude_layers.
    edit_layers = sorted((set(induce["layer"]).union(set(fix["layer"]))) - set(exclude_layers))
    if exclude_layers:
        print(f"[stage21] {model}: excluding layers {sorted(exclude_layers)} from the "
              f"correlation (last-layer / degeneracy quarantine)")
    if not edit_layers:
        print(f"[stage21] {model}: no swept layers in editing results — skipping")
        return None
    merged = pd.DataFrame({"layer": edit_layers})
    for part in (probe, ct, induce, fix):
        if not part.empty:
            merged = merged.merge(part, on="layer", how="left")

    for col in ["probe_r2", "ct_recovery", "induce_effect", "fix_effect", "control_effect"]:
        if col not in merged.columns:
            merged[col] = np.nan
    merged = merged.sort_values("layer").reset_index(drop=True)

    corrs = []
    for loc_name, loc_col in [("probe_r2", "probe_r2"), ("ct_recovery", "ct_recovery")]:
        for eff_name, eff_col in [("induce_effect", "induce_effect"), ("fix_effect", "fix_effect")]:
            rho, p, n = _spearman(merged[loc_col].to_numpy(dtype=float),
                                  merged[eff_col].to_numpy(dtype=float))
            corrs.append({"localization": loc_name, "editing": eff_name,
                          "spearman_rho": round(rho, 4) if np.isfinite(rho) else np.nan,
                          "p_value": round(p, 4) if np.isfinite(p) else np.nan,
                          "n_layers": n})
    corr_df = pd.DataFrame(corrs)
    return {"model": model, "merged": merged, "corr": corr_df}


def maybe_plot(all_results: list[dict], out_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        print("[stage21] matplotlib unavailable — skipping overlay figure (tables still written)")
        return

    def z(v):
        v = np.asarray(v, dtype=float)
        m = np.isfinite(v)
        if m.sum() < 2 or np.nanstd(v[m]) == 0:
            return v
        out = np.full_like(v, np.nan)
        out[m] = (v[m] - np.nanmean(v[m])) / np.nanstd(v[m])
        return out

    n = len(all_results)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 4.2), squeeze=False)
    for ax, res in zip(axes[0], all_results):
        d = res["merged"]
        x = d["layer"].to_numpy()
        for col, lab, mk in [("probe_r2", "probe R² (loc)", "o"),
                             ("ct_recovery", "causal-tracing (loc)", "s"),
                             ("induce_effect", "induce Δ (edit)", "^"),
                             ("fix_effect", "fix Δ (edit)", "v")]:
            if col in d and np.isfinite(d[col].to_numpy(dtype=float)).any():
                ax.plot(x, z(d[col]), marker=mk, label=lab)
        ax.set_title(res["model"])
        ax.set_xlabel("decoder layer")
        ax.set_ylabel("z-scored")
        ax.axhline(0, color="grey", lw=0.6)
        ax.legend(fontsize=8)
    fig.suptitle("Localization vs. editing efficacy across layers (z-scored)")
    fig.tight_layout()
    p = out_dir / "localization_vs_editing.png"
    fig.savefig(p, dpi=140)
    print(f"[stage21] wrote {p}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 21: localization-vs-editing analysis")
    parser.add_argument("--results_root", default="results")
    parser.add_argument("--probe_csv",
                        default="results/prevalence_appendix/validated_strategy_layer_prevalence.csv")
    parser.add_argument("--models", nargs="+", default=["qwen3_32b", "mistral_small_3_2_24b"])
    parser.add_argument("--band_tag", default="hr2_0.35_0.65",
                        help="Stage 20 mid-HR2 band tag to read the fix sweep from")
    parser.add_argument("--exclude_layers", type=int, nargs="*", default=None,
                        help="Per-run layers to drop from the correlation (e.g. a degenerate "
                             "last decoder layer). Applies to all --models; the merged table "
                             "still shows every swept layer, only the Spearman is recomputed.")
    parser.add_argument("--out_dir", default="results/localization_vs_editing")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    probe_csv = Path(args.probe_csv)

    all_results = []
    for model in args.models:
        results_dir = Path(args.results_root) / f"steering_{model}"
        res = analyze_model(model, results_dir, probe_csv, args.band_tag,
                            exclude_layers=set(args.exclude_layers or []))
        if res is None:
            continue
        res["merged"].to_csv(out_dir / f"{model}_layer_curves.csv", index=False)
        res["corr"].to_csv(out_dir / f"{model}_localization_vs_editing_corr.csv", index=False)
        print(f"\n[stage21] === {model}: per-layer curves ===")
        print(res["merged"].to_string(index=False))
        print(f"[stage21] === {model}: Spearman (localization vs editing; DESCRIPTIVE, {len(res['merged'])} layers) ===")
        print(res["corr"].to_string(index=False))
        all_results.append(res)

    if not all_results:
        print("[stage21] nothing to analyze — run Stages 18-20 and sync results first")
        return

    with open(out_dir / "summary.json", "w") as f:
        json.dump({r["model"]: {"corr": r["corr"].to_dict(orient="records"),
                                "layers": r["merged"]["layer"].tolist()}
                   for r in all_results}, f, indent=2)
    maybe_plot(all_results, out_dir)
    print(f"\n[stage21] wrote outputs to {out_dir}/")


if __name__ == "__main__":
    main()
