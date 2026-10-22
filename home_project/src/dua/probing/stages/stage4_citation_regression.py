"""Stage 4: regress citation count on hidden states, per strategy and layer.

Usage
─────
  python -m dua.probing.stages.stage4_citation_regression \\
      --scored_tsv /scratch/$USER/scholar_qwen/run1/scored.tsv \\
      --out_dir    /scratch/$USER/scholar_qwen/run1
"""

import os
import csv
import argparse

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_scored(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


# ─────────────────────────────────────────────────────────────────────────────
# Array extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_arrays(rows: list[dict]) -> dict[str, np.ndarray]:
    """
    Pull every column we need from rows into float64 numpy arrays.
    HR4/HR5 are recomputed from raw counts if not present in scored.tsv.
    """
    hr2, hr4, hr5 = [], [], []
    log_cit, n_gt = [], []

    for r in rows:
        _cit_raw = str(r.get("citation_count", 0) or 0).rstrip("+")
        cit = float(_cit_raw) if _cit_raw else 0.0
        log_cit.append(np.log1p(cit))
        n_gt.append(float(r.get("n_gt_authors", 0) or 0))
        hr2.append(float(r["hr2"]))

        if "hr4" in r and r["hr4"] not in ("", None):
            hr4.append(float(r["hr4"]))
            hr5.append(float(r["hr5"]))
        else:
            M = float(r.get("n_match",  0) or 0)
            H = float(r.get("n_hal",    0) or 0)
            U = float(r.get("n_unretr", 0) or 0)
            hr4.append(H / (M + H) if (M + H) > 0 else 0.0)
            hr5.append(U / (M + U) if (M + U) > 0 else 0.0)

    return {
        "HR2":     np.array(hr2,     dtype=np.float64),
        "HR4":     np.array(hr4,     dtype=np.float64),
        "HR5":     np.array(hr5,     dtype=np.float64),
        "log_cit": np.array(log_cit, dtype=np.float64),
        "n_gt":    np.array(n_gt,    dtype=np.float64),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Unadjusted OLS (bivariate)
# ─────────────────────────────────────────────────────────────────────────────

def simple_ols(x: np.ndarray, y: np.ndarray) -> dict:
    """
    OLS: y = β₀ + β₁·x.  Returns slope, intercept, R², p-value, Spearman ρ.
    """
    from scipy.stats import linregress, spearmanr
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 5:
        nan = float("nan")
        return dict(slope=nan, intercept=nan, r2=nan, p_value=nan,
                    stderr=nan, spearman_rho=nan, n=len(x))
    res = linregress(x, y)
    rho, _ = spearmanr(x, y)
    return {
        "slope":        round(float(res.slope),     6),
        "intercept":    round(float(res.intercept), 6),
        "r2":           round(float(res.rvalue**2), 6),
        "p_value":      float(res.pvalue),
        "stderr":       round(float(res.stderr),    6),
        "spearman_rho": round(float(rho),           4),
        "n":            int(len(x)),
    }


SIMPLE_FIELDS = ["metric", "slope", "intercept", "r2", "p_value", "stderr",
                 "spearman_rho", "n"]


# ─────────────────────────────────────────────────────────────────────────────
# Adjusted OLS (multiple regression)
# ─────────────────────────────────────────────────────────────────────────────

def build_design_matrix(
    rows: list[dict],
    log_cit: np.ndarray,
    n_gt: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    """
    X = [intercept, log_cit, n_gt_authors, field_dummies (ref = most common)]

    Returns (X float64, feature_names).
    """
    fields      = [r.get("field", "") or "unknown" for r in rows]
    field_counts: dict[str, int] = {}
    for f in fields:
        field_counts[f] = field_counts.get(f, 0) + 1
    ref_field   = max(field_counts, key=field_counts.get)
    dummy_names = sorted(set(fields) - {ref_field})

    cols  = [np.ones(len(rows)), log_cit, n_gt]
    names = ["intercept", "log_cit", "n_gt_authors"]
    for fname in dummy_names:
        cols.append(np.array([1.0 if f == fname else 0.0 for f in fields]))
        names.append(f"field_{fname}")

    return np.column_stack(cols).astype(np.float64), names


def multiple_ols(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list[str],
) -> dict | None:
    """
    OLS with analytic t-tests (no external dependencies beyond scipy).
    X must include an intercept column.

    Returns per-feature stats (coef, SE, t-stat, p-value) plus R² and R²_adj.
    Returns None if fewer than k+5 valid observations.
    """
    from scipy.stats import t as t_dist

    mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    X, y = X[mask], y[mask]
    N, k = X.shape
    if N < k + 5:
        return None

    # β via least-squares (numerically better than explicit inverse)
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof   = N - k
    s2    = (resid @ resid) / dof

    cov     = s2 * np.linalg.inv(X.T @ X)
    se      = np.sqrt(np.clip(np.diag(cov), 0, None))
    t_stats = beta / np.where(se > 0, se, np.nan)
    p_vals  = 2 * (1 - t_dist.cdf(np.abs(t_stats), df=dof))

    ss_res = resid @ resid
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2     = 1 - ss_res / ss_tot            if ss_tot > 0 else float("nan")
    r2_adj = 1 - (ss_res / dof) / (ss_tot / (N - 1)) if ss_tot > 0 else float("nan")

    return {
        "n":      N,
        "r2":     round(r2,     4),
        "r2_adj": round(r2_adj, 4),
        "features": {
            name: {
                "coef":    round(float(beta[i]),    6),
                "se":      round(float(se[i]),      6),
                "t_stat":  round(float(t_stats[i]), 4),
                "p_value": float(p_vals[i]),
            }
            for i, name in enumerate(feature_names)
        },
    }


def partial_regression_residuals(
    X: np.ndarray,
    y: np.ndarray,
    col_idx: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Frisch-Waugh-Lovell: partial out all columns except col_idx from both
    y and X[:, col_idx].  Returns (e_x, e_y) — the residuals — whose OLS
    slope equals the coefficient on X[:, col_idx] in the full model.
    """
    mask    = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    X, y    = X[mask], y[mask]
    other   = np.delete(X, col_idx, axis=1)
    x_focus = X[:, col_idx]

    def resid(Z, v):
        b, _, _, _ = np.linalg.lstsq(Z, v, rcond=None)
        return v - Z @ b

    return resid(other, x_focus), resid(other, y)


ADJUSTED_FIELDS = [
    "metric", "model",
    "coef_log_cit", "se_log_cit", "t_log_cit", "p_log_cit",
    "coef_n_gt_authors", "p_n_gt_authors",
    "r2", "r2_adj", "n",
]


# ─────────────────────────────────────────────────────────────────────────────
# Binned analysis
# ─────────────────────────────────────────────────────────────────────────────

def binned_means(rows: list[dict], arrays: dict[str, np.ndarray]) -> dict:
    """Mean HR2/HR4/HR5 per citation_bin."""
    bins: dict[str, dict[str, list]] = {}
    for i, r in enumerate(rows):
        b = r.get("citation_bin", "unknown") or "unknown"
        if b not in bins:
            bins[b] = {"HR2": [], "HR4": [], "HR5": []}
        for m in ("HR2", "HR4", "HR5"):
            v = arrays[m][i]
            if np.isfinite(v):
                bins[b][m].append(float(v))
    return {b: {m: (np.mean(vs) if vs else float("nan")) for m, vs in d.items()}
            for b, d in bins.items()}


def _sort_bins(bin_keys):
    def key(b):
        b = str(b)
        if b[0].isdigit():
            return float(b.split("-")[0].rstrip("+>"))
        return 1e9 if (">" in b or "+" in b) else -1.0
    return sorted(bin_keys, key=key)


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def plot_unadjusted(arrays, simple_results, bin_means_data, out_png):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        metrics = ["HR2", "HR4", "HR5"]
        labels  = {"HR2": "HR2 (Jaccard)",
                   "HR4": "HR4 (1−Precision)",
                   "HR5": "HR5 (1−Recall)"}
        log_cit = arrays["log_cit"]
        fig, axes = plt.subplots(2, 3, figsize=(15, 9))

        for col, metric in enumerate(metrics):
            ax   = axes[0, col]
            y    = arrays[metric]
            mask = np.isfinite(y) & np.isfinite(log_cit)
            ax.scatter(log_cit[mask], y[mask], alpha=0.2, s=4, color="steelblue")
            res = simple_results[metric]
            if np.isfinite(res["slope"]):
                xs = np.linspace(log_cit[mask].min(), log_cit[mask].max(), 200)
                ax.plot(xs, res["intercept"] + res["slope"] * xs,
                        color="crimson", linewidth=1.5,
                        label=f"β={res['slope']:.3f}  R²={res['r2']:.3f}\n"
                              f"ρ={res['spearman_rho']:.3f}  p={res['p_value']:.2e}")
                ax.legend(fontsize=7)
            ax.set_xlabel("log(citation + 1)")
            ax.set_ylabel(metric)
            ax.set_title(f"{labels[metric]}\nunadjusted")
            ax.grid(alpha=0.3)

        sorted_bins = _sort_bins(bin_means_data.keys())
        for col, metric in enumerate(metrics):
            ax    = axes[1, col]
            means = [bin_means_data[b][metric] for b in sorted_bins]
            ax.bar(range(len(sorted_bins)), means,
                   color="steelblue", alpha=0.7, edgecolor="white")
            ax.set_xticks(range(len(sorted_bins)))
            ax.set_xticklabels(sorted_bins, rotation=30, ha="right", fontsize=8)
            ax.set_ylabel(f"Mean {metric}")
            ax.set_title(f"Mean {labels[metric]} by citation bin")
            ax.grid(axis="y", alpha=0.3)

        fig.suptitle("Hallucination rate vs factual prevalence — unadjusted",
                     fontsize=13, fontweight="bold")
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage4] Unadjusted plot → {out_png}")
    except Exception as e:
        print(f"[stage4] Unadjusted plot failed: {e}")


def plot_adjusted(arrays, rows, adj_results, out_png):
    """
    3×1 partial regression plots (added-variable plots) — one per HR metric.
    x-axis = log_cit residualised on n_gt_authors + field.
    y-axis = HR residualised on n_gt_authors + field.
    Slope = adjusted log_cit coefficient (FWL theorem).
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from scipy.stats import linregress

        metrics = ["HR2", "HR4", "HR5"]
        labels  = {"HR2": "HR2 (Jaccard)",
                   "HR4": "HR4 (1−Precision)",
                   "HR5": "HR5 (1−Recall)"}

        log_cit = arrays["log_cit"]
        n_gt    = arrays["n_gt"]
        X, feat_names = build_design_matrix(rows, log_cit, n_gt)
        logcit_col    = feat_names.index("log_cit")

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for col, metric in enumerate(metrics):
            ax   = axes[col]
            y    = arrays[metric]
            mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)

            e_x, e_y = partial_regression_residuals(X, y, logcit_col)
            ax.scatter(e_x, e_y, alpha=0.2, s=4, color="steelblue")

            if len(e_x) > 5:
                res = linregress(e_x, e_y)
                xs  = np.linspace(e_x.min(), e_x.max(), 200)
                ax.plot(xs, res.intercept + res.slope * xs,
                        color="crimson", linewidth=1.5)

            r = adj_results.get(metric)
            if r:
                f   = r["features"].get("log_cit", {})
                coef, pval = f.get("coef", float("nan")), f.get("p_value", float("nan"))
                ax.set_title(
                    f"{labels[metric]} — adjusted\n"
                    f"β_log_cit={coef:.4f}  p={pval:.2e}  R²_adj={r['r2_adj']:.3f}"
                )
            ax.set_xlabel("log(citation + 1)  |  n_gt_authors, field")
            ax.set_ylabel(f"{metric}  |  n_gt_authors, field")
            ax.grid(alpha=0.3)

        fig.suptitle(
            "Partial regression: prevalence → hallucination (net of author count & field)",
            fontsize=12, fontweight="bold",
        )
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage4] Adjusted plot → {out_png}")
    except Exception as e:
        print(f"[stage4] Adjusted plot failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Stage 4: Citation regression vs hallucination rates"
    )
    parser.add_argument("--scored_tsv", required=True)
    parser.add_argument("--out_dir",    required=True)
    parser.add_argument("--skip_plots", action="store_true")
    args = parser.parse_args()

    results_dir = os.path.join(args.out_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    print(f"[stage4] Loading: {args.scored_tsv}")
    rows   = load_scored(args.scored_tsv)
    arrays = extract_arrays(rows)
    print(f"[stage4] {len(rows)} papers")

    log_cit = arrays["log_cit"]
    n_gt    = arrays["n_gt"]
    X, feat_names = build_design_matrix(rows, log_cit, n_gt)
    print(f"[stage4] Design matrix: {X.shape[1]} features "
          f"({len([f for f in feat_names if f.startswith('field_')])} field dummies, "
          f"ref = most common field)")

    # ── Unadjusted OLS ────────────────────────────────────────────────────────
    simple_results: dict[str, dict] = {}
    simple_csv = os.path.join(results_dir, "citation_regression.csv")
    with open(simple_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SIMPLE_FIELDS)
        writer.writeheader()
        for metric in ("HR2", "HR4", "HR5"):
            res = simple_ols(log_cit, arrays[metric])
            simple_results[metric] = res
            writer.writerow({"metric": metric, **res})
            print(f"  [unadjusted] {metric}: β={res['slope']:+.4f}  "
                  f"R²={res['r2']:.4f}  ρ={res['spearman_rho']:+.4f}  "
                  f"p={res['p_value']:.2e}")
    print(f"[stage4] Unadjusted results → {simple_csv}")

    # ── Adjusted OLS ─────────────────────────────────────────────────────────
    adj_results: dict[str, dict | None] = {}
    adj_csv = os.path.join(results_dir, "citation_regression_adjusted.csv")
    with open(adj_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ADJUSTED_FIELDS)
        writer.writeheader()
        for metric in ("HR2", "HR4", "HR5"):
            res = multiple_ols(X, arrays[metric], feat_names)
            adj_results[metric] = res
            if res is None:
                print(f"  [adjusted]   {metric}: insufficient data")
                continue
            lc = res["features"]["log_cit"]
            ng = res["features"]["n_gt_authors"]
            print(f"  [adjusted]   {metric}: β_log_cit={lc['coef']:+.4f}  "
                  f"SE={lc['se']:.4f}  t={lc['t_stat']:+.2f}  p={lc['p_value']:.2e}  "
                  f"R²_adj={res['r2_adj']:.4f}")
            writer.writerow({
                "metric":            metric,
                "model":             "HR ~ log_cit + n_gt_authors + field",
                "coef_log_cit":      round(lc["coef"],    6),
                "se_log_cit":        round(lc["se"],      6),
                "t_log_cit":         round(lc["t_stat"],  4),
                "p_log_cit":         lc["p_value"],
                "coef_n_gt_authors": round(ng["coef"],    6),
                "p_n_gt_authors":    ng["p_value"],
                "r2":                res["r2"],
                "r2_adj":            res["r2_adj"],
                "n":                 res["n"],
            })
    print(f"[stage4] Adjusted results → {adj_csv}")

    # ── Binned means ──────────────────────────────────────────────────────────
    bin_data = binned_means(rows, arrays)

    # ── Plots ─────────────────────────────────────────────────────────────────
    if not args.skip_plots:
        plot_unadjusted(
            arrays, simple_results, bin_data,
            os.path.join(results_dir, "citation_regression.png"),
        )
        plot_adjusted(
            arrays, rows, adj_results,
            os.path.join(results_dir, "citation_regression_adjusted.png"),
        )

    print("[stage4] Done.")


if __name__ == "__main__":
    main()
