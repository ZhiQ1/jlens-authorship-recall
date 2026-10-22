"""A7.4: classifying citation regimes from P1 (Table A40).

Four binary tasks plus a 4-quartile multiclass probe, all with fold-safe
PCA and class-balanced logistic regression. Outputs
``citation_bucket_probe.csv``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import (
    MODEL_COLORS,
    N_SVD_COMPONENTS,
    RANDOM_SEED,
    RunSpec,
    model_label,
    plt,
)


def classify_with_cv(X_raw: np.ndarray, y: np.ndarray) -> dict[str, float]:
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        balanced_accuracy_score,
        roc_auc_score,
    )
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler

    classes, counts = np.unique(y, return_counts=True)
    if len(classes) < 2:
        raise ValueError("Classification target has only one class")
    n_splits = min(5, int(counts.min()))
    if n_splits < 2:
        raise ValueError("Classification target has fewer than two examples in one class")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    proba = np.empty(len(y), dtype=np.float64)
    for train_idx, test_idx in cv.split(X_raw, y):
        k = min(N_SVD_COMPONENTS, len(train_idx) - 1, X_raw.shape[1])
        pca = PCA(n_components=k, svd_solver="randomized", random_state=RANDOM_SEED)
        Z_train = pca.fit_transform(X_raw[train_idx])
        Z_test = pca.transform(X_raw[test_idx])
        scaler = StandardScaler()
        Z_train = scaler.fit_transform(Z_train)
        Z_test = scaler.transform(Z_test)
        clf = LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            solver="lbfgs",
            random_state=RANDOM_SEED,
        )
        clf.fit(Z_train, y[train_idx])
        proba[test_idx] = clf.predict_proba(Z_test)[:, 1]
    pred = (proba >= 0.5).astype(np.int32)
    return {
        "auroc": float(roc_auc_score(y, proba)),
        "auprc": float(average_precision_score(y, proba)),
        "accuracy_at_0_5": float(accuracy_score(y, pred)),
        "balanced_accuracy_at_0_5": float(balanced_accuracy_score(y, pred)),
    }


def multiclass_bucket_probe(X_raw: np.ndarray, y: np.ndarray) -> dict[str, float]:
    from sklearn.decomposition import PCA
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, balanced_accuracy_score
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler

    classes, counts = np.unique(y, return_counts=True)
    if len(classes) < 2:
        raise ValueError("Bucket target has only one class")
    n_splits = min(5, int(counts.min()))
    if n_splits < 2:
        raise ValueError("Bucket target has fewer than two examples in one class")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    pred = np.empty(len(y), dtype=np.int32)
    for train_idx, test_idx in cv.split(X_raw, y):
        k = min(N_SVD_COMPONENTS, len(train_idx) - 1, X_raw.shape[1])
        pca = PCA(n_components=k, svd_solver="randomized", random_state=RANDOM_SEED)
        Z_train = pca.fit_transform(X_raw[train_idx])
        Z_test = pca.transform(X_raw[test_idx])
        scaler = StandardScaler()
        Z_train = scaler.fit_transform(Z_train)
        Z_test = scaler.transform(Z_test)
        clf = LogisticRegression(
            class_weight="balanced",
            max_iter=3000,
            solver="lbfgs",
            random_state=RANDOM_SEED,
        )
        clf.fit(Z_train, y[train_idx])
        pred[test_idx] = clf.predict(Z_test)
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
    }


def run_citation_bucket_probe(
    spec: RunSpec,
    X_raw: np.ndarray,
    scored: pd.DataFrame,
) -> pd.DataFrame:
    citations = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0).to_numpy()
    rows: list[dict] = []

    definitions: list[tuple[str, np.ndarray, np.ndarray]] = []
    definitions.append(("zero_vs_cited", np.ones(len(citations), dtype=bool), (citations > 0).astype(int)))
    median = float(np.median(citations))
    definitions.append((f"above_median_gt_{median:g}", np.ones(len(citations), dtype=bool), (citations > median).astype(int)))

    q25, q75 = np.quantile(citations, [0.25, 0.75])
    mask = (citations <= q25) | (citations >= q75)
    definitions.append((f"head_tail_q25_{q25:g}_q75_{q75:g}", mask, (citations[mask] >= q75).astype(int)))

    q90 = float(np.quantile(citations, 0.90))
    definitions.append((f"top_decile_ge_{q90:g}", np.ones(len(citations), dtype=bool), (citations >= q90).astype(int)))

    for label, mask, y in definitions:
        try:
            metrics = classify_with_cv(X_raw[mask], y)
            rows.append({
                "model": spec.model,
                "strategy": "p1",
                "layer_idx": spec.optimal_layer,
                "label_definition": label,
                "n": int(mask.sum()),
                "positive_rate": round(float(y.mean()), 6),
                **{k: round(v, 6) for k, v in metrics.items()},
            })
        except ValueError as exc:
            rows.append({
                "model": spec.model,
                "strategy": "p1",
                "layer_idx": spec.optimal_layer,
                "label_definition": label,
                "n": int(mask.sum()),
                "positive_rate": "",
                "auroc": "",
                "auprc": "",
                "accuracy_at_0_5": "",
                "balanced_accuracy_at_0_5": "",
                "skip_reason": str(exc),
            })

    try:
        bucket_y = pd.qcut(citations, q=4, labels=False, duplicates="drop")
        bucket_y_arr = np.asarray(bucket_y)
        keep = ~pd.isna(bucket_y_arr)
        metrics = multiclass_bucket_probe(X_raw[keep], bucket_y_arr[keep].astype(int))
        rows.append({
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "label_definition": "citation_quartile_multiclass",
            "n": int(keep.sum()),
            "positive_rate": "",
            "auroc": "",
            "auprc": "",
            "accuracy_at_0_5": round(metrics["accuracy"], 6),
            "balanced_accuracy_at_0_5": round(metrics["balanced_accuracy"], 6),
        })
    except ValueError as exc:
        rows.append({
            "model": spec.model,
            "strategy": "p1",
            "layer_idx": spec.optimal_layer,
            "label_definition": "citation_quartile_multiclass",
            "n": len(citations),
            "skip_reason": str(exc),
        })

    return pd.DataFrame(rows)


def plot_bucket_probe(df: pd.DataFrame, fig_dir: Path) -> None:
    if df.empty or "auroc" not in df.columns:
        return
    sub = df[df["label_definition"].astype(str).str.startswith("head_tail")].copy()
    if sub.empty:
        sub = df[pd.to_numeric(df["auroc"], errors="coerce").notna()].copy()
    if sub.empty:
        return
    sub["auroc"] = pd.to_numeric(sub["auroc"], errors="coerce")
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    colors = [MODEL_COLORS.get(m, "#4D4D4D") for m in sub["model"]]
    ax.bar([model_label(m) for m in sub["model"]], sub["auroc"], color=colors)
    ax.axhline(0.5, color="#555555", lw=1, ls="--")
    ax.set_ylim(0.45, max(1.0, float(sub["auroc"].max()) + 0.05))
    ax.set_ylabel("AUROC")
    ax.set_title("P1 head-tail citation probe")
    fig.tight_layout()
    out = fig_dir / "figure_prevalence_bucket_probe.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"[stage8] wrote {out}")
