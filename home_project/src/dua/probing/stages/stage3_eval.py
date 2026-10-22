"""Stage 3: SVD-based hallucination detection and citation correlation.

Per strategy and layer: centre the hidden states, take the top singular vector
as an unsupervised direction, and report AUROC against the binary
hallucination label, Spearman against HR2, and Spearman against
log(citations+1). A linear probe gives the supervised upper bound.

Usage
─────
  python -m dua.probing.stages.stage3_eval \\
      --h5_path      /scratch/$USER/scholar_qwen/run1/embeddings.h5 \\
      --scored_tsv   /scratch/$USER/scholar_qwen/run1/scored.tsv \\
      --per_name_tsv /scratch/$USER/scholar_qwen/run1/per_name_labels.tsv \\
      --out_dir      /scratch/$USER/scholar_qwen/run1
"""

import os
import csv
import json
import argparse
import warnings

import numpy as np
import h5py

import sys
sys.path.insert(0, os.path.dirname(__file__))
from dua.probing.scholar_utils import compute_auroc, spearman_r


# ─────────────────────────────────────────────────────────────────────────────
# Loading helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_scored_tsv(path: str) -> dict[str, dict]:
    """Load scored.tsv → {paper_id: row_dict}."""
    rows: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows[row["paper_id"]] = row
    return rows


def load_per_name_tsv(path: str) -> list[dict]:
    """Load per_name_labels.tsv → list of row dicts."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            rows.append(row)
    return rows


def load_per_query_embeddings(h5: h5py.File, strategy: str) -> np.ndarray:
    """
    Load (N, n_layers, D) float16 array for one strategy key (p1–p5).
    Returns float32 for numerical stability.
    """
    return h5[f"per_query/{strategy}"][:].astype(np.float32)


def align_scored_to_h5(h5: h5py.File, scored: dict[str, dict]) -> tuple[np.ndarray, dict]:
    """
    Build a sorted index array so that embeddings[i] corresponds to scored[paper_id].
    Returns (valid_indices, paper_id_list) where valid_indices indexes into the HDF5.
    """
    h5_pids = [
        b.decode("utf-8") if isinstance(b, bytes) else str(b)
        for b in h5["paper_ids"][:]
    ]
    valid_idx     = []
    valid_pids    = []
    for i, pid in enumerate(h5_pids):
        if pid in scored:
            valid_idx.append(i)
            valid_pids.append(pid)
    return np.array(valid_idx, dtype=np.int64), valid_pids


# ─────────────────────────────────────────────────────────────────────────────
# SVD analysis
# ─────────────────────────────────────────────────────────────────────────────

def center(X: np.ndarray) -> np.ndarray:
    return X - X.mean(axis=0, keepdims=True)


def truncated_svd(X: np.ndarray, n_components: int = 20) -> np.ndarray:
    """
    Randomized SVD of centered matrix X (N, D).
    Returns U of shape (N, n_components) — the per-sample score matrix.
    """
    from sklearn.utils.extmath import randomized_svd
    U, S, Vt = randomized_svd(X, n_components=n_components, random_state=42)
    return U  # (N, n_components)


def analyze_layer(
    X_layer: np.ndarray,         # (N, D) float32 — one layer's embeddings
    hr2:     np.ndarray,         # (N,)  float32
    log_cit: np.ndarray,         # (N,)  float32
    labels:  np.ndarray,         # (N,)  int — binary (hr2 > 0.5)
) -> dict:
    """
    Run SVD on one layer and return the hallucination-detection metrics
    for the top singular vector (unsupervised) and best linear probe (supervised).
    """
    Xc = center(X_layer)
    U  = truncated_svd(Xc, n_components=20)  # (N, 20)

    # Top singular vector metrics (unsupervised — no labels used to select component)
    top_scores = U[:, 0]
    auroc_top  = max(compute_auroc(top_scores, labels),
                     compute_auroc(-top_scores, labels))   # sign-agnostic
    rho_hr2    = spearman_r(top_scores, hr2)
    rho_cit    = spearman_r(top_scores, log_cit)

    # Best component across top-20 (upper bound — uses labels on full set)
    best_auroc_k = max(
        max(compute_auroc(U[:, k], labels),
            compute_auroc(-U[:, k], labels))
        for k in range(U.shape[1])
    )

    # Linear probe AUROC (supervised upper bound)
    probe_auroc = _linear_probe_auroc(Xc, labels)

    return {
        "auroc_top1":    round(auroc_top,     4),
        "auroc_best_k":  round(best_auroc_k,  4),
        "auroc_probe":   round(probe_auroc,   4),
        "rho_hr2":       round(rho_hr2,       4),
        "rho_log_cit":   round(rho_cit,       4),
    }


def _linear_probe_auroc(Xc: np.ndarray, labels: np.ndarray, test_frac: float = 0.2) -> float:
    """Logistic regression probe: 80/20 split, returns test AUROC."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    N = len(labels)
    rng  = np.random.default_rng(42)
    idx  = rng.permutation(N)
    cut  = int(N * (1 - test_frac))
    tr, te = idx[:cut], idx[cut:]

    scaler = StandardScaler().fit(Xc[tr])
    Xtr = scaler.transform(Xc[tr])
    Xte = scaler.transform(Xc[te])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lr = LogisticRegression(max_iter=500, C=1.0).fit(Xtr, labels[tr])

    proba = lr.predict_proba(Xte)[:, 1]
    return compute_auroc(proba, labels[te])


# ─────────────────────────────────────────────────────────────────────────────
# Per-query analysis loop
# ─────────────────────────────────────────────────────────────────────────────

STRATEGIES = ["p1", "p2", "p3", "p4", "p5"]

RESULT_FIELDS = [
    "strategy", "layer_idx", "layer_depth_pct",
    "auroc_top1", "auroc_best_k", "auroc_probe",
    "rho_hr2", "rho_log_cit",
]


def run_per_query_analysis(
    h5: h5py.File,
    valid_idx: np.ndarray,
    pids: list[str],
    scored: dict[str, dict],
    target_layers: list[int],
    n_model_layers: int,
    out_csv: str,
) -> None:
    """Iterate strategies × layers, compute metrics, append to CSV."""
    hr2_arr     = np.array([float(scored[p]["hr2"])           for p in pids], dtype=np.float32)
    cit_arr     = np.array([float(scored[p]["citation_count"]) for p in pids], dtype=np.float32)
    log_cit_arr = np.log1p(cit_arr)
    labels      = (hr2_arr > 0.5).astype(np.int32)

    write_header = not os.path.exists(out_csv)
    f_out = open(out_csv, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f_out, fieldnames=RESULT_FIELDS)
    if write_header:
        writer.writeheader()

    for strategy in STRATEGIES:
        if f"per_query/{strategy}" not in h5:
            print(f"  [skip] strategy {strategy} not in HDF5")
            continue
        print(f"  Strategy {strategy} ...")
        embeddings = load_per_query_embeddings(h5, strategy)  # (N_h5, n_L, D)
        X_all      = embeddings[valid_idx]                     # (N_valid, n_L, D)

        for l_idx, layer in enumerate(target_layers):
            depth_pct = round(100 * layer / (n_model_layers - 1), 1)
            metrics   = analyze_layer(X_all[:, l_idx, :], hr2_arr, log_cit_arr, labels)
            writer.writerow({
                "strategy":       strategy,
                "layer_idx":      layer,
                "layer_depth_pct":depth_pct,
                **metrics,
            })

        del embeddings, X_all

    f_out.close()
    print(f"[stage3] Per-query results → {out_csv}")


# ─────────────────────────────────────────────────────────────────────────────
# P9 per-name analysis
# ─────────────────────────────────────────────────────────────────────────────

PER_NAME_RESULT_FIELDS = [
    "layer_idx", "layer_depth_pct",
    "auroc_top1", "auroc_best_k", "auroc_probe",
    "rho_hr2", "rho_log_cit",
    "author_pos_rho",   # Spearman between SVD score and author_position
]


def run_per_name_analysis(
    h5:             h5py.File,
    per_name_rows:  list[dict],
    scored:         dict[str, dict],
    target_layers:  list[int],
    n_model_layers: int,
    out_csv:        str,
) -> None:
    """
    P9 analysis: same SVD metrics but at per-name granularity.
    Also reports correlation between SVD score and author position.
    """
    if "per_name/hidden" not in h5 or h5["per_name/hidden"].shape[0] == 0:
        print("[stage3] No per-name data found — skipping P9 analysis")
        return

    # Align per_name_rows with the HDF5 flat array (same order)
    # The HDF5 per_name/paper_id matches per_name_rows order
    pids_in_h5 = [
        b.decode("utf-8") if isinstance(b, bytes) else str(b)
        for b in h5["per_name/paper_id"][:]
    ]
    # Filter to rows that have a scored paper
    valid_mask = np.array([pid in scored for pid in pids_in_h5], dtype=bool)
    if valid_mask.sum() == 0:
        print("[stage3] No per-name rows overlap with scored papers — skipping")
        return

    valid_flat_idx = np.where(valid_mask)[0]
    pids_valid     = [pids_in_h5[i] for i in valid_flat_idx]

    labels_name    = np.array(
        [int(per_name_rows[i]["is_hallucinated"]) for i in valid_flat_idx],
        dtype=np.int32,
    )
    author_pos     = np.array(
        [int(per_name_rows[i]["author_pos"]) for i in valid_flat_idx],
        dtype=np.float32,
    )
    log_cit        = np.log1p(np.array(
        [float(scored[p]["citation_count"]) for p in pids_valid],
        dtype=np.float32,
    ))
    hr2_name       = np.array(
        [float(scored[p]["hr2"]) for p in pids_valid],
        dtype=np.float32,
    )

    # Load hidden states for valid rows
    all_hidden = h5["per_name/hidden"][valid_flat_idx].astype(np.float32)  # (M, n_L, D)

    write_header = not os.path.exists(out_csv)
    f_out = open(out_csv, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(f_out, fieldnames=PER_NAME_RESULT_FIELDS)
    if write_header:
        writer.writeheader()

    print(f"  P9: {valid_mask.sum()} names, "
          f"{labels_name.mean()*100:.1f}% hallucinated ...")

    for l_idx, layer in enumerate(target_layers):
        depth_pct = round(100 * layer / (n_model_layers - 1), 1)
        X_layer   = all_hidden[:, l_idx, :]
        metrics   = analyze_layer(X_layer, hr2_name, log_cit, labels_name)

        # Extra: correlation of top SVD projection with author position
        Xc  = center(X_layer)
        U   = truncated_svd(Xc, n_components=1)
        top = U[:, 0]
        pos_rho = max(spearman_r(top, author_pos), spearman_r(-top, author_pos),
                      key=abs)

        writer.writerow({
            "layer_idx":       layer,
            "layer_depth_pct": depth_pct,
            **metrics,
            "author_pos_rho":  round(pos_rho, 4),
        })

    f_out.close()
    print(f"[stage3] P9 per-name results → {out_csv}")


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def plot_layer_auroc(csv_path: str, out_png: str, n_model_layers: int) -> None:
    """
    Layer-AUROC curves: one line per strategy.
    x-axis: layer depth (%), y-axis: unsupervised top-1 AUROC.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd

        df = pd.read_csv(csv_path)
        fig, ax = plt.subplots(figsize=(8, 5))

        for strategy, grp in df.groupby("strategy"):
            grp = grp.sort_values("layer_depth_pct")
            ax.plot(grp["layer_depth_pct"], grp["auroc_top1"],
                    marker="o", label=strategy)

        ax.set_xlabel("Layer depth (%)")
        ax.set_ylabel("AUROC (top-1 SVD, unsupervised)")
        ax.set_title("Hallucination detection AUROC by layer — all strategies")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage3] Layer-AUROC plot → {out_png}")
    except Exception as e:
        print(f"[stage3] Plotting failed (likely headless server): {e}")


def plot_citation_correlation(
    h5: h5py.File,
    valid_idx: np.ndarray,
    pids: list[str],
    scored: dict[str, dict],
    best_strategy: str,
    best_layer_idx: int,
    out_png: str,
) -> None:
    """Scatter: top SVD projection score vs log(citation_count+1) for best layer."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        X = h5[f"per_query/{best_strategy}"][valid_idx, best_layer_idx, :].astype(np.float32)
        Xc = center(X)
        U  = truncated_svd(Xc, n_components=1)
        scores  = U[:, 0]
        log_cit = np.log1p([float(scored[p]["citation_count"]) for p in pids])
        hr2     = np.array([float(scored[p]["hr2"]) for p in pids])

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].scatter(log_cit, scores, c=hr2, cmap="RdYlGn_r", alpha=0.4, s=8)
        axes[0].set_xlabel("log(citation_count + 1)")
        axes[0].set_ylabel("Top SVD component score")
        axes[0].set_title(f"SVD score vs citation count  [{best_strategy}, layer {best_layer_idx}]")

        axes[1].scatter(hr2, scores, alpha=0.4, s=8, c="steelblue")
        axes[1].set_xlabel("HR2 (Jaccard hallucination rate)")
        axes[1].set_ylabel("Top SVD component score")
        axes[1].set_title("SVD score vs hallucination rate")

        fig.tight_layout()
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        print(f"[stage3] Citation correlation plot → {out_png}")
    except Exception as e:
        print(f"[stage3] Scatter plot failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stage 3: SVD + AUROC + citation correlation")
    parser.add_argument("--h5_path",       required=True)
    parser.add_argument("--scored_tsv",    required=True,
                        help="scored.tsv from stage2")
    parser.add_argument("--per_name_tsv",  default=None,
                        help="per_name_labels.tsv from stage2 (optional)")
    parser.add_argument("--out_dir",       required=True)
    parser.add_argument("--skip_plots",    action="store_true",
                        help="Skip matplotlib plots (useful on headless nodes)")
    args = parser.parse_args()

    results_dir = os.path.join(args.out_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # ── Load metadata from HDF5 ───────────────────────────────────────────────
    print(f"[stage3] Opening HDF5: {args.h5_path}")
    h5 = h5py.File(args.h5_path, "r")

    target_layers   = json.loads(h5.attrs["layer_indices"])
    n_model_layers  = int(h5.attrs.get("n_model_layers", 64))  # fallback; overridden below
    hidden_dim      = int(h5.attrs["hidden_dim"])

    # Load n_model_layers from meta.json if available
    meta_path = os.path.join(args.out_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        n_model_layers = meta.get("n_model_layers", 64)

    print(f"[stage3] target_layers={target_layers}  n_model_layers={n_model_layers}")

    # ── Load scoring results ──────────────────────────────────────────────────
    print(f"[stage3] Loading scored.tsv: {args.scored_tsv}")
    scored = load_scored_tsv(args.scored_tsv)
    print(f"[stage3] {len(scored)} scored papers")

    valid_idx, pids = align_scored_to_h5(h5, scored)
    print(f"[stage3] {len(pids)} papers aligned between HDF5 and scored.tsv")

    # ── Per-query analysis ────────────────────────────────────────────────────
    svd_csv = os.path.join(results_dir, "svd_results.csv")
    print(f"\n[stage3] Running per-query SVD analysis ...")
    run_per_query_analysis(
        h5=h5,
        valid_idx=valid_idx,
        pids=pids,
        scored=scored,
        target_layers=target_layers,
        n_model_layers=n_model_layers,
        out_csv=svd_csv,
    )

    # ── P9 per-name analysis ──────────────────────────────────────────────────
    if args.per_name_tsv and os.path.exists(args.per_name_tsv):
        per_name_rows = load_per_name_tsv(args.per_name_tsv)
        per_name_csv  = os.path.join(results_dir, "per_name_results.csv")
        print(f"\n[stage3] Running P9 per-name SVD analysis ...")
        run_per_name_analysis(
            h5=h5,
            per_name_rows=per_name_rows,
            scored=scored,
            target_layers=target_layers,
            n_model_layers=n_model_layers,
            out_csv=per_name_csv,
        )

    # ── Plots ─────────────────────────────────────────────────────────────────
    if not args.skip_plots:
        plot_layer_auroc(
            csv_path=svd_csv,
            out_png=os.path.join(results_dir, "layer_auroc.png"),
            n_model_layers=n_model_layers,
        )
        # Pick best strategy/layer for scatter plot (highest auroc_top1)
        import csv as _csv
        best_row, best_auroc = None, -1.0
        with open(svd_csv, newline="") as f:
            for row in _csv.DictReader(f):
                a = float(row["auroc_top1"]) if row["auroc_top1"] else -1.0
                if a > best_auroc:
                    best_auroc = a
                    best_row = row
        if best_row:
            best_strategy = best_row["strategy"]
            best_l_idx    = target_layers.index(int(best_row["layer_idx"]))
            plot_citation_correlation(
                h5=h5,
                valid_idx=valid_idx,
                pids=pids,
                scored=scored,
                best_strategy=best_strategy,
                best_layer_idx=best_l_idx,
                out_png=os.path.join(results_dir, "citation_correlation.png"),
            )

    h5.close()
    print(f"\n[stage3] All results written to {results_dir}/")


if __name__ == "__main__":
    main()
