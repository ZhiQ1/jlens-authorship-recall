"""Stage 5: the layer x strategy sweep behind Figures A7 and A8.

Cross-validated ridge from hidden states to log(citations+1), fold safe: PCA
and scaler are refit inside each training fold, never on the full set.

Usage
─────
  python -m dua.probing.stages.stage5_embedding_prevalence \\
      --h5_path    /scratch/$USER/scholar_qwen/run1/embeddings.h5 \\
      --scored_tsv /scratch/$USER/scholar_qwen/run1/scored.tsv \\
      --svd_csv    /scratch/$USER/scholar_qwen/run1/results/svd_results.csv \\
      --out_dir    /scratch/$USER/scholar_qwen/run1
"""

import os
import csv
import json
import argparse

import numpy as np
import h5py
from scipy.stats import spearmanr, t as t_dist

STRATEGIES      = ["p1", "p2", "p3", "p4", "p5"]
HR_METRICS      = ["hr2", "hr4", "hr5"]
N_SVD_COMPONENTS = 100
CV_FOLDS        = 5
N_BOOTSTRAP     = 2000
RIDGE_ALPHAS    = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def load_scored_tsv(path: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows[row["paper_id"]] = row
    return rows


def align_scored_to_h5(h5: h5py.File, scored: dict) -> tuple[np.ndarray, list[str]]:
    h5_pids = [
        b.decode("utf-8") if isinstance(b, bytes) else str(b)
        for b in h5["paper_ids"][:]
    ]
    valid_idx, valid_pids = [], []
    for i, pid in enumerate(h5_pids):
        if pid in scored:
            valid_idx.append(i)
            valid_pids.append(pid)
    return np.array(valid_idx, dtype=np.int64), valid_pids


def load_svd_results(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# SVD reduction + cross-validated ridge regression
# ─────────────────────────────────────────────────────────────────────────────

def svd_reduce(X: np.ndarray, n_components: int = N_SVD_COMPONENTS) -> np.ndarray:
    """Center X, randomized SVD, return score matrix U*S of shape (N, k)."""
    from sklearn.utils.extmath import randomized_svd
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, _ = randomized_svd(X_c, n_components=n_components, random_state=42)
    return U * S  # (N, k) — actual coordinates in principal-component space


def fit_prevalence_cv(
    X_svd: np.ndarray,
    log_cit: np.ndarray,
) -> tuple[float, float, float, np.ndarray]:
    """
    Select best ridge alpha via 5-fold CV, then get OOS predictions via
    cross_val_predict with that alpha.

    Returns (r2_cv, spearman_rho_cv, best_alpha, oos_predictions).
    """
    from sklearn.linear_model import RidgeCV, Ridge
    from sklearn.model_selection import cross_val_predict

    rcv = RidgeCV(alphas=RIDGE_ALPHAS, cv=CV_FOLDS)
    rcv.fit(X_svd, log_cit)
    best_alpha = float(rcv.alpha_)

    preds = cross_val_predict(
        Ridge(alpha=best_alpha), X_svd, log_cit, cv=CV_FOLDS
    )

    ss_res = float(np.sum((log_cit - preds) ** 2))
    ss_tot = float(np.sum((log_cit - log_cit.mean()) ** 2))
    r2_cv  = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    rho_cv = float(spearmanr(preds, log_cit).statistic)

    return r2_cv, rho_cv, best_alpha, preds


# ─────────────────────────────────────────────────────────────────────────────
# Part A: prevalence decoding loop
# ─────────────────────────────────────────────────────────────────────────────

PREV_FIELDS = [
    "strategy", "layer_idx", "layer_depth_pct",
    "r2_cv", "spearman_rho_cv", "best_alpha", "n",
]


def run_prevalence_decoding(
    h5: h5py.File,
    valid_idx: np.ndarray,
    pids: list[str],
    scored: dict[str, dict],
    target_layers: list[int],
    n_model_layers: int,
    out_csv: str,
) -> tuple[dict, np.ndarray]:
    """
    Iterate all (strategy × layer) pairs.
    Returns (oos_preds, log_cit_array) where oos_preds is keyed
    (strategy, layer_idx) → np.ndarray of shape (N,).
    """
    log_cit = np.array(
        [np.log1p(float(scored[p]["citation_count"])) for p in pids],
        dtype=np.float32,
    )
    oos_preds: dict[tuple, np.ndarray] = {}

    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=PREV_FIELDS)
        writer.writeheader()

        for strategy in STRATEGIES:
            key = f"per_query/{strategy}"
            if key not in h5:
                print(f"  [skip] {strategy} not in HDF5")
                continue
            print(f"  Strategy {strategy} ...")

            for l_idx, layer in enumerate(target_layers):
                # Load one layer at a time: (N_h5, D) float16 → slice valid rows
                X = h5[key][:, l_idx, :][valid_idx].astype(np.float32)
                depth_pct = round(100.0 * layer / (n_model_layers - 1), 1)

                X_svd = svd_reduce(X)
                r2_cv, rho_cv, best_alpha, preds = fit_prevalence_cv(X_svd, log_cit)
                oos_preds[(strategy, layer)] = preds

                writer.writerow({
                    "strategy":         strategy,
                    "layer_idx":        layer,
                    "layer_depth_pct":  depth_pct,
                    "r2_cv":            round(r2_cv,  4),
                    "spearman_rho_cv":  round(rho_cv, 4),
                    "best_alpha":       best_alpha,
                    "n":                len(pids),
                })
                print(f"    layer={layer:2d} ({depth_pct:5.1f}%)  "
                      f"R²_cv={r2_cv:.4f}  ρ={rho_cv:.4f}  α={best_alpha}")

    print(f"[stage5] Prevalence decoding results → {out_csv}")
    return oos_preds, log_cit


# ─────────────────────────────────────────────────────────────────────────────
# Part B: mediation analysis
# ─────────────────────────────────────────────────────────────────────────────

def _ols(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """OLS: y ~ X. Returns (coefficients, residuals)."""
    coefs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    return coefs, y - X @ coefs


def _linregress(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, float]:
    """Simple OLS y ~ x. Returns (slope, intercept, r2, p_value)."""
    X = np.column_stack([np.ones_like(x), x])
    coefs, resid = _ols(X, y)
    intercept, slope = coefs
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2     = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    n      = len(y)
    denom  = float(np.sum((x - x.mean()) ** 2))
    se     = float(np.sqrt(ss_res / (n - 2) / denom)) if denom > 0 else 0.0
    t_stat = slope / se if se > 0 else 0.0
    p_val  = float(2 * t_dist.sf(abs(t_stat), df=n - 2))
    return slope, intercept, r2, p_val


def _joint_ols_pvalues(
    log_cit: np.ndarray, M_hat: np.ndarray, y: np.ndarray
) -> tuple[float, float, float, float, float]:
    """
    OLS: y ~ [1, log_cit, M_hat].
    Returns (c_prime, c_prime_p, b, b_p, r2_joint).
    """
    n = len(y)
    X = np.column_stack([np.ones(n), log_cit, M_hat])
    coefs, resid = _ols(X, y)
    _, c_prime, b = coefs

    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2_joint = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    s2     = ss_res / (n - 3)
    XtX_inv = np.linalg.pinv(X.T @ X)
    ses    = np.sqrt(s2 * np.diag(XtX_inv))

    t_cp   = c_prime / ses[1] if ses[1] > 0 else 0.0
    t_b    = b       / ses[2] if ses[2] > 0 else 0.0
    c_prime_p = float(2 * t_dist.sf(abs(t_cp), df=n - 3))
    b_p       = float(2 * t_dist.sf(abs(t_b),  df=n - 3))

    return c_prime, c_prime_p, b, b_p, r2_joint


def bootstrap_indirect(
    log_cit: np.ndarray,
    M_hat: np.ndarray,
    y: np.ndarray,
    n_boot: int = N_BOOTSTRAP,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Percentile bootstrap 95% CI for the indirect effect a×b.
    Resamples (log_cit, M_hat, y) jointly to preserve covariance structure.
    """
    rng = np.random.default_rng(seed)
    n   = len(log_cit)
    ab_samples = np.empty(n_boot, dtype=np.float64)

    for i in range(n_boot):
        idx  = rng.integers(0, n, size=n)
        lc_b = log_cit[idx]
        m_b  = M_hat[idx]
        y_b  = y[idx]

        a, *_ = _linregress(lc_b, m_b)

        X_joint = np.column_stack([np.ones(n), lc_b, m_b])
        coefs, _ = _ols(X_joint, y_b)
        b = coefs[2]

        ab_samples[i] = a * b

    lo, hi = np.percentile(ab_samples, [2.5, 97.5])
    return float(lo), float(hi)


MEDIATION_FIELDS = [
    "hr_metric", "strategy", "layer_idx", "layer_depth_pct",
    "c",         "c_p",        # total effect: log_cit → HR
    "a",         "r2_a",       # stage path:   log_cit → M_hat
    "b",         "b_p",        # outcome path: M_hat → HR | log_cit
    "c_prime",   "c_prime_p",  # direct effect: log_cit → HR | M_hat
    "r2_joint",                # R² of joint model
    "indirect_ab",
    "indirect_lo_95", "indirect_hi_95",
    "pct_mediated",
]


def run_mediation(
    log_cit: np.ndarray,
    oos_preds: dict,
    scored: dict,
    pids: list[str],
    prev_csv: str,
    out_csv: str,
) -> list[dict]:
    """
    For each HR metric × each strategy (at that strategy's best layer),
    run Baron & Kenny path decomposition + bootstrap CI on the indirect effect.
    """
    # Find best layer per strategy from prevalence decoding results
    best_per_strategy: dict[str, dict] = {}
    with open(prev_csv, newline="") as f:
        for row in csv.DictReader(f):
            strat = row["strategy"]
            r2    = float(row["r2_cv"])
            if strat not in best_per_strategy or r2 > best_per_strategy[strat]["r2_cv"]:
                best_per_strategy[strat] = {
                    "r2_cv":           r2,
                    "layer_idx":       int(row["layer_idx"]),
                    "layer_depth_pct": float(row["layer_depth_pct"]),
                }

    # Only use metrics present in the scored.tsv (older runs may lack hr4/hr5)
    sample = next(iter(scored.values()))
    available_metrics = [m for m in HR_METRICS if m in sample]
    if len(available_metrics) < len(HR_METRICS):
        missing = set(HR_METRICS) - set(available_metrics)
        print(f"  [warn] scored.tsv missing columns {missing} — skipping those metrics")

    hr_arrays = {
        m: np.array([float(scored[p][m]) for p in pids], dtype=np.float32)
        for m in available_metrics
    }

    rows_out = []

    for metric in available_metrics:
        y = hr_arrays[metric]
        c, _, _, c_p = _linregress(log_cit, y)

        for strategy, best in best_per_strategy.items():
            layer     = best["layer_idx"]
            depth_pct = best["layer_depth_pct"]
            M_hat     = oos_preds[(strategy, layer)]

            # Path a: log_cit → M_hat
            a, _, r2_a, _ = _linregress(log_cit, M_hat)

            # Joint model: HR ~ log_cit + M_hat → paths b and c'
            c_prime, c_prime_p, b, b_p, r2_joint = _joint_ols_pvalues(log_cit, M_hat, y)

            # Indirect effect + bootstrap CI
            indirect_ab   = a * b
            lo95, hi95    = bootstrap_indirect(log_cit, M_hat, y)
            pct_mediated  = 100.0 * indirect_ab / c if c != 0 else float("nan")

            row = {
                "hr_metric":       metric,
                "strategy":        strategy,
                "layer_idx":       layer,
                "layer_depth_pct": depth_pct,
                "c":               round(c,            6),
                "c_p":             round(c_p,          6),
                "a":               round(a,            6),
                "r2_a":            round(r2_a,         4),
                "b":               round(b,            6),
                "b_p":             round(b_p,          6),
                "c_prime":         round(c_prime,      6),
                "c_prime_p":       round(c_prime_p,    6),
                "r2_joint":        round(r2_joint,     4),
                "indirect_ab":     round(indirect_ab,  6),
                "indirect_lo_95":  round(lo95,         6),
                "indirect_hi_95":  round(hi95,         6),
                "pct_mediated":    round(pct_mediated, 2),
            }
            rows_out.append(row)

            print(f"  [{metric}, {strategy}, layer={layer}]  "
                  f"c={c:.4f}  a={a:.4f}  b={b:.4f}  c'={c_prime:.4f}  "
                  f"ab={indirect_ab:.4f} [{lo95:.4f}, {hi95:.4f}]  "
                  f"%med={pct_mediated:.1f}%")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MEDIATION_FIELDS)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"[stage5] Mediation results → {out_csv}")
    return rows_out


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def plot_prevalence_by_layer(prev_csv: str, out_png: str) -> None:
    """R²_cv vs layer depth — analogue of layer_auroc.png."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd

        df  = pd.read_csv(prev_csv)
        fig, ax = plt.subplots(figsize=(8, 5))

        for strategy, grp in df.groupby("strategy"):
            grp = grp.sort_values("layer_depth_pct")
            ax.plot(grp["layer_depth_pct"], grp["r2_cv"], marker="o", label=strategy)

        ax.set_xlabel("Layer depth (%)")
        ax.set_ylabel("Prevalence decoding R² (5-fold CV)")
        ax.set_title("How much citation count is encoded in each layer")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage5] Prevalence-by-layer plot → {out_png}")
    except Exception as e:
        print(f"[stage5] plot_prevalence_by_layer failed: {e}")


def plot_embedding_vs_hallucination(prev_csv: str, svd_csv: str, out_png: str) -> None:
    """
    Scatter: R²_cv (prevalence decoding) vs AUROC_top1 (hallucination detection)
    for all 70 (strategy × layer) points.
    Tests whether layers that detect hallucination also encode citation prevalence.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd

        prev   = pd.read_csv(prev_csv)
        svd    = pd.read_csv(svd_csv)
        merged = prev.merge(svd, on=["strategy", "layer_idx", "layer_depth_pct"])

        fig, ax = plt.subplots(figsize=(7, 6))
        colors  = plt.cm.tab10.colors

        for i, (strategy, grp) in enumerate(merged.groupby("strategy")):
            ax.scatter(
                grp["auroc_top1"], grp["r2_cv"],
                label=strategy, color=colors[i], alpha=0.8, s=60,
            )
            for _, row in grp.iterrows():
                ax.annotate(
                    f"{int(row['layer_depth_pct'])}%",
                    (row["auroc_top1"], row["r2_cv"]),
                    fontsize=6, alpha=0.6,
                    xytext=(3, 3), textcoords="offset points",
                )

        ax.set_xlabel("Hallucination detection AUROC (unsupervised SVD)")
        ax.set_ylabel("Prevalence decoding R² (5-fold CV ridge)")
        ax.set_title("Prevalence encoding vs hallucination detection by layer")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage5] Embedding-vs-hallucination plot → {out_png}")
    except Exception as e:
        print(f"[stage5] plot_embedding_vs_hallucination failed: {e}")


def plot_mediation(med_rows: list[dict], out_png: str) -> None:
    """
    1×3 panel (one per HR metric): bar chart of % mediated per strategy,
    with bootstrap 95% CI error bars.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd

        df      = pd.DataFrame(med_rows)
        metrics = df["hr_metric"].unique().tolist()
        fig, axes = plt.subplots(1, len(metrics), figsize=(14, 5), sharey=True)
        if len(metrics) == 1:
            axes = [axes]

        for ax, metric in zip(axes, metrics):
            sub = df[df["hr_metric"] == metric].sort_values("strategy")

            strategies = sub["strategy"].tolist()
            pct        = sub["pct_mediated"].tolist()
            c_vals     = sub["c"].tolist()
            lo_ab      = sub["indirect_lo_95"].tolist()
            hi_ab      = sub["indirect_hi_95"].tolist()

            # Convert bootstrap CI on ab to % scale (divide by c)
            pct_lo = [100.0 * l / c if c != 0 else 0.0 for l, c in zip(lo_ab, c_vals)]
            pct_hi = [100.0 * h / c if c != 0 else 0.0 for h, c in zip(hi_ab, c_vals)]
            yerr_lo = [max(p - pl, 0) for p, pl in zip(pct, pct_lo)]
            yerr_hi = [max(ph - p, 0) for ph, p in zip(pct_hi, pct)]

            ax.bar(strategies, pct, color="steelblue", alpha=0.75)
            ax.errorbar(
                strategies, pct,
                yerr=[yerr_lo, yerr_hi],
                fmt="none", color="black", capsize=4,
            )
            ax.axhline(0, color="black", lw=0.8)
            ax.set_title(metric.upper())
            ax.set_xlabel("Extraction strategy")
            if ax is axes[0]:
                ax.set_ylabel("% of citation→hallucination effect\nmediated by embedding")
            ax.grid(axis="y", alpha=0.3)

        fig.suptitle(
            "Mediation: how much of the citation → hallucination effect\n"
            "passes through the model's internal representations",
            fontsize=11,
        )
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage5] Mediation plot → {out_png}")
    except Exception as e:
        print(f"[stage5] plot_mediation failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Stage 5: Embedding prevalence regression + mediation"
    )
    parser.add_argument("--h5_path",    required=True, help="embeddings.h5 from stage1")
    parser.add_argument("--scored_tsv", required=True, help="scored.tsv from stage2")
    parser.add_argument("--svd_csv",    required=True, help="svd_results.csv from stage3")
    parser.add_argument("--out_dir",    required=True, help="Output directory")
    parser.add_argument("--skip_plots", action="store_true")
    args = parser.parse_args()

    results_dir = os.path.join(args.out_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # ── Load metadata ─────────────────────────────────────────────────────────
    print(f"[stage5] Opening HDF5: {args.h5_path}")
    with h5py.File(args.h5_path, "r") as h5:
        target_layers  = json.loads(h5.attrs["layer_indices"])
        n_model_layers = int(h5.attrs.get("n_model_layers", 64))
        print(f"[stage5] target_layers={target_layers}  "
              f"n_model_layers={n_model_layers}  "
              f"hidden_dim={int(h5.attrs['hidden_dim'])}")

        print(f"[stage5] Loading scored.tsv: {args.scored_tsv}")
        scored = load_scored_tsv(args.scored_tsv)
        valid_idx, pids = align_scored_to_h5(h5, scored)
        print(f"[stage5] {len(pids)} papers aligned between HDF5 and scored.tsv")

        # ── Part A: Prevalence decoding ───────────────────────────────────────
        prev_csv = os.path.join(results_dir, "embedding_prevalence.csv")
        print(f"\n[stage5] Part A: Prevalence decoding "
              f"({len(STRATEGIES)} strategies × {len(target_layers)} layers, "
              f"k={N_SVD_COMPONENTS}, {CV_FOLDS}-fold CV) ...")
        oos_preds, log_cit = run_prevalence_decoding(
            h5=h5,
            valid_idx=valid_idx,
            pids=pids,
            scored=scored,
            target_layers=target_layers,
            n_model_layers=n_model_layers,
            out_csv=prev_csv,
        )

    # HDF5 closed — mediation needs only scored data + oos_preds
    # ── Part B: Mediation analysis ────────────────────────────────────────────
    med_csv = os.path.join(results_dir, "mediation_results.csv")
    print(f"\n[stage5] Part B: Mediation analysis "
          f"(n_boot={N_BOOTSTRAP}, {len(HR_METRICS)} metrics × "
          f"{len(oos_preds) // len(target_layers)} strategies) ...")
    med_rows = run_mediation(
        log_cit=log_cit,
        oos_preds=oos_preds,
        scored=scored,
        pids=pids,
        prev_csv=prev_csv,
        out_csv=med_csv,
    )

    # ── Plots ─────────────────────────────────────────────────────────────────
    if not args.skip_plots:
        plot_prevalence_by_layer(
            prev_csv,
            out_png=os.path.join(results_dir, "embedding_prevalence_by_layer.png"),
        )
        plot_embedding_vs_hallucination(
            prev_csv,
            svd_csv=args.svd_csv,
            out_png=os.path.join(results_dir, "embedding_vs_hallucination.png"),
        )
        plot_mediation(
            med_rows,
            out_png=os.path.join(results_dir, "mediation_plot.png"),
        )

    print(f"\n[stage5] All results written to {results_dir}/")


if __name__ == "__main__":
    main()
