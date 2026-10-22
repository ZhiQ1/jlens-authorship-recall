"""Stage 6: follow-up analyses over a completed run.

Usage
─────
  python -m dua.probing.stages.stage6_followup_analyses \\
    --runs qwen3_32b=/scratch/$USER/scholar_qwen/run_qwen3_32b \\
           mistral_small_3_2_24b=/scratch/$USER/scholar_qwen/run_mistral_small_3_2_24b \\
    --optimal_layers qwen3_32b:48 mistral_small_3_2_24b:22 \\
    --out_dir /scratch/$USER/scholar_qwen/followup_results
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from typing import Iterable

import h5py
import numpy as np


RANDOM_SEED = 42
STRATEGIES = ("p1", "p2", "p3", "p4", "p5")
HR_METRICS = ("hr2", "hr4", "hr5")


@dataclass(frozen=True)
class RunSpec:
    model: str
    run_dir: str
    optimal_layer: int


def parse_runs(items: list[str]) -> dict[str, str]:
    runs = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--runs entry must be name=/path, got {item!r}")
        name, path = item.split("=", 1)
        name = name.strip()
        path = path.strip()
        if not name or not path:
            raise ValueError(f"Invalid --runs entry: {item!r}")
        runs[name] = path
    return runs


def parse_layers(items: list[str]) -> dict[str, int]:
    layers = {}
    for item in items:
        if ":" not in item:
            raise ValueError(f"--optimal_layers entry must be name:layer, got {item!r}")
        name, layer = item.split(":", 1)
        layers[name.strip()] = int(layer)
    return layers


def load_tsv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tsv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def decode_array(values) -> list[str]:
    return [
        v.decode("utf-8") if isinstance(v, bytes) else str(v)
        for v in values
    ]


def citation_bin_sort_key(value: str) -> tuple[float, str]:
    b = str(value)
    first = b.split("-")[0].replace(",", "").rstrip("+>").strip()
    try:
        return (float(first), b)
    except ValueError:
        return (float("inf"), b)


def load_layer_indices(h5: h5py.File) -> list[int]:
    raw = h5.attrs["layer_indices"]
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        return [int(x) for x in json.loads(raw)]
    return [int(x) for x in raw]


def layer_position(target_layers: list[int], layer_idx: int) -> int:
    if layer_idx not in target_layers:
        raise ValueError(
            f"Requested layer {layer_idx} is not in HDF5 layer_indices={target_layers}"
        )
    return target_layers.index(layer_idx)


def align_query_rows(h5: h5py.File, scored_rows: list[dict]) -> tuple[np.ndarray, list[dict]]:
    scored_by_pid = {r["paper_id"]: r for r in scored_rows}
    h5_pids = decode_array(h5["paper_ids"][:])
    valid_idx = []
    rows = []
    for i, pid in enumerate(h5_pids):
        if pid in scored_by_pid:
            valid_idx.append(i)
            rows.append(scored_by_pid[pid])
    return np.array(valid_idx, dtype=np.int64), rows


def compute_auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    from sklearn.metrics import roc_auc_score

    if len(np.unique(labels)) < 2:
        return float("nan")
    return float(roc_auc_score(labels, scores))


def _classification_probe(
    X: np.ndarray,
    hr2: np.ndarray,
    aligned_rows: list[dict],
    spec: RunSpec,
    label_definition: str,
    low_cutoff: float,
    high_cutoff: float,
    keep_mask: np.ndarray,
    inclusive_high: bool = False,
    emit_predictions: bool = False,
) -> tuple[dict, list[dict]]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        balanced_accuracy_score,
        roc_auc_score,
    )
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X_sub = X[keep_mask]
    hr2_sub = hr2[keep_mask]
    rows_sub = [r for r, keep in zip(aligned_rows, keep_mask) if keep]
    if inclusive_high:
        y = (hr2_sub >= high_cutoff).astype(np.int32)
    else:
        y = (hr2_sub > high_cutoff).astype(np.int32)
    if len(np.unique(y)) < 2:
        raise ValueError(f"{spec.model}: {label_definition} label has only one class")

    min_class = int(min((y == 0).sum(), (y == 1).sum()))
    n_splits = min(5, min_class)
    if n_splits < 2:
        raise ValueError(f"{spec.model}: {label_definition} has fewer than 2 samples in one class")
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            solver="lbfgs",
            random_state=RANDOM_SEED,
        ),
    )
    proba = cross_val_predict(clf, X_sub, y, cv=cv, method="predict_proba")[:, 1]
    pred = (proba >= 0.5).astype(np.int32)

    metric = {
        "model": spec.model,
        "strategy": "p1",
        "layer_idx": spec.optimal_layer,
        "label_definition": label_definition,
        "hr2_low_cutoff": low_cutoff,
        "hr2_high_cutoff": high_cutoff,
        "n": len(y),
        "n_excluded": int((~keep_mask).sum()),
        "positive_rate": round(float(y.mean()), 6),
        "auroc": round(float(roc_auc_score(y, proba)), 6),
        "auprc": round(float(average_precision_score(y, proba)), 6),
        "accuracy_at_0_5": round(float(accuracy_score(y, pred)), 6),
        "balanced_accuracy_at_0_5": round(float(balanced_accuracy_score(y, pred)), 6),
    }

    pred_rows = []
    if emit_predictions:
        for row, label, score in zip(rows_sub, y, proba):
            pred_rows.append({
                "model": spec.model,
                "paper_id": row["paper_id"],
                "citation_count": row.get("citation_count", ""),
                "citation_bin": row.get("citation_bin", ""),
                "hr2": row.get("hr2", ""),
                "is_hallucinated": int(label),
                "p_hallucinated_oof": round(float(score), 8),
            })

    return metric, pred_rows


def run_probe(
    spec: RunSpec,
    out_dir: str,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    from scipy.stats import pearsonr, spearmanr
    from sklearn.linear_model import RidgeCV
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    h5_path = os.path.join(spec.run_dir, "embeddings.h5")
    scored_path = os.path.join(spec.run_dir, "scored.tsv")
    scored_rows = load_tsv(scored_path)

    with h5py.File(h5_path, "r") as h5:
        target_layers = load_layer_indices(h5)
        l_pos = layer_position(target_layers, spec.optimal_layer)
        valid_idx, aligned_rows = align_query_rows(h5, scored_rows)
        X = h5["per_query/p1"][:, l_pos, :][valid_idx].astype(np.float32)

    hr2 = np.array([float(r["hr2"]) for r in aligned_rows], dtype=np.float32)
    all_mask = np.ones(len(hr2), dtype=bool)
    probe_metrics = []
    primary_predictions = []

    for threshold in (0.25, 0.5, 0.75):
        metric, predictions = _classification_probe(
            X=X,
            hr2=hr2,
            aligned_rows=aligned_rows,
            spec=spec,
            label_definition=f"hr2_gt_{threshold:g}",
            low_cutoff=threshold,
            high_cutoff=threshold,
            keep_mask=all_mask,
            inclusive_high=False,
            emit_predictions=(threshold == 0.5),
        )
        probe_metrics.append(metric)
        primary_predictions.extend(predictions)

    borderline_mask = (hr2 <= 0.25) | (hr2 >= 0.75)
    metric, _ = _classification_probe(
        X=X,
        hr2=hr2,
        aligned_rows=aligned_rows,
        spec=spec,
        label_definition="hr2_le_0.25_vs_ge_0.75",
        low_cutoff=0.25,
        high_cutoff=0.75,
        keep_mask=borderline_mask,
        inclusive_high=True,
        emit_predictions=False,
    )
    probe_metrics.append(metric)

    ridge_alphas = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]
    ridge_cv = make_pipeline(
        StandardScaler(),
        RidgeCV(alphas=ridge_alphas, cv=5),
    )
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    hr2_pred = cross_val_predict(ridge_cv, X, hr2, cv=cv)
    ridge_cv.fit(X, hr2)
    best_alpha = float(ridge_cv.named_steps["ridgecv"].alpha_)

    regression_metrics = [{
        "model": spec.model,
        "strategy": "p1",
        "layer_idx": spec.optimal_layer,
        "n": len(hr2),
        "best_alpha": best_alpha,
        "r2_cv": round(float(r2_score(hr2, hr2_pred)), 6),
        "spearman_rho": round(float(spearmanr(hr2, hr2_pred).statistic), 6),
        "pearson_r": round(float(pearsonr(hr2, hr2_pred).statistic), 6),
        "mae": round(float(mean_absolute_error(hr2, hr2_pred)), 6),
    }]
    regression_predictions = []
    for row, pred in zip(aligned_rows, hr2_pred):
        regression_predictions.append({
            "model": spec.model,
            "paper_id": row["paper_id"],
            "citation_count": row.get("citation_count", ""),
            "citation_bin": row.get("citation_bin", ""),
            "hr2": row.get("hr2", ""),
            "hr2_pred_oof": round(float(pred), 8),
        })

    return probe_metrics, primary_predictions, regression_metrics, regression_predictions


def standardize(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def centroid_metrics(
    X: np.ndarray,
    y: np.ndarray,
    n_perm: int = 1000,
    compute_probe: bool = True,
) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if len(np.unique(y)) < 2:
        nan = float("nan")
        return {
            "n_names": len(y),
            "n_matched": int((y == 0).sum()),
            "n_hallucinated": int((y == 1).sum()),
            "centroid_cosine": nan,
            "centroid_l2": nan,
            "within_matched_cosine_to_centroid": nan,
            "within_hallucinated_cosine_to_centroid": nan,
            "probe_auroc": nan,
            "centroid_perm_p": nan,
        }

    Xs = standardize(X.astype(np.float32))
    X0 = Xs[y == 0]
    X1 = Xs[y == 1]
    c0 = X0.mean(axis=0)
    c1 = X1.mean(axis=0)

    c0_norm = float(np.linalg.norm(c0))
    c1_norm = float(np.linalg.norm(c1))
    centroid_cos = float(np.dot(c0, c1) / (c0_norm * c1_norm)) if c0_norm and c1_norm else float("nan")
    centroid_l2 = float(np.linalg.norm(c1 - c0))

    def mean_cos_to_centroid(A: np.ndarray, c: np.ndarray) -> float:
        denom = np.linalg.norm(A, axis=1) * np.linalg.norm(c)
        mask = denom > 0
        if not mask.any():
            return float("nan")
        return float(np.mean((A[mask] @ c) / denom[mask]))

    if compute_probe:
        # Class-balanced logistic probe.  Use 5 folds unless minority class is small.
        min_class = int(min((y == 0).sum(), (y == 1).sum()))
        n_splits = min(5, min_class)
        if n_splits >= 2:
            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
            clf = make_pipeline(
                StandardScaler(),
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    solver="lbfgs",
                    random_state=RANDOM_SEED,
                ),
            )
            proba = cross_val_predict(clf, X, y, cv=cv, method="predict_proba")[:, 1]
            probe_auroc = float(roc_auc_score(y, proba))
        else:
            probe_auroc = float("nan")
    else:
        probe_auroc = float("nan")

    rng = np.random.default_rng(RANDOM_SEED)
    ge_count = 0
    for _ in range(n_perm):
        yp = rng.permutation(y)
        d = np.linalg.norm(Xs[yp == 1].mean(axis=0) - Xs[yp == 0].mean(axis=0))
        if d >= centroid_l2:
            ge_count += 1
    perm_p = (ge_count + 1) / (n_perm + 1)

    return {
        "n_names": len(y),
        "n_matched": int((y == 0).sum()),
        "n_hallucinated": int((y == 1).sum()),
        "centroid_cosine": round(centroid_cos, 6),
        "centroid_l2": round(centroid_l2, 6),
        "within_matched_cosine_to_centroid": round(mean_cos_to_centroid(X0, c0), 6),
        "within_hallucinated_cosine_to_centroid": round(mean_cos_to_centroid(X1, c1), 6),
        "probe_auroc": round(probe_auroc, 6),
        "centroid_perm_p": round(float(perm_p), 6),
    }


def run_p9_geometry(spec: RunSpec) -> tuple[list[dict], list[dict], list[dict]]:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    h5_path = os.path.join(spec.run_dir, "embeddings.h5")
    labels_path = os.path.join(spec.run_dir, "per_name_labels.tsv")
    label_rows = load_tsv(labels_path)

    with h5py.File(h5_path, "r") as h5:
        if "per_name/hidden" not in h5 or h5["per_name/hidden"].shape[0] == 0:
            return [], [], []
        target_layers = load_layer_indices(h5)
        l_pos = layer_position(target_layers, spec.optimal_layer)
        pids = decode_array(h5["per_name/paper_id"][:])
        name_strs = decode_array(h5["per_name/name_str"][:])
        author_pos = h5["per_name/author_pos"][:].astype(int)

        n = min(len(label_rows), len(pids))
        keep = [
            i for i in range(n)
            if label_rows[i].get("paper_id") == pids[i]
            and label_rows[i].get("is_hallucinated", "") != ""
        ]
        if not keep:
            return [], [], []

        keep_idx = np.array(keep, dtype=np.int64)
        y = np.array([int(label_rows[i]["is_hallucinated"]) for i in keep], dtype=np.int32)

        summary_rows = []
        layer_rows = []
        for pos, layer in enumerate(target_layers):
            X_layer = h5["per_name/hidden"][:, pos, :][keep_idx].astype(np.float32)
            is_optimal = layer == spec.optimal_layer
            met = centroid_metrics(
                X_layer,
                y,
                n_perm=1000 if is_optimal else 200,
                compute_probe=is_optimal,
            )
            row = {
                "model": spec.model,
                "layer_idx": layer,
                "layer_depth_pct": round(
                    100.0 * layer / (int(h5.attrs.get("n_model_layers", max(target_layers) + 1)) - 1),
                    1,
                ),
                **met,
            }
            layer_rows.append(row)
            if is_optimal:
                summary_rows.append(row)

        X_opt = h5["per_name/hidden"][:, l_pos, :][keep_idx].astype(np.float32)

    pca_rows = []
    pca_inputs = {
        "standardized": StandardScaler().fit_transform(X_opt),
        "centered": X_opt - X_opt.mean(axis=0, keepdims=True),
    }
    for preprocessing, X_pca in pca_inputs.items():
        pcs = PCA(n_components=2, random_state=RANDOM_SEED).fit_transform(X_pca)
        for out_i, src_i in enumerate(keep):
            lab = label_rows[src_i]
            pca_rows.append({
                "model": spec.model,
                "preprocessing": preprocessing,
                "paper_id": pids[src_i],
                "name_str": name_strs[src_i],
                "author_pos": int(author_pos[src_i]),
                "is_hallucinated": int(y[out_i]),
                "citation_count": lab.get("citation_count", ""),
                "citation_bin": lab.get("citation_bin", ""),
                "field": lab.get("field", ""),
                "pc1": round(float(pcs[out_i, 0]), 8),
                "pc2": round(float(pcs[out_i, 1]), 8),
            })

    return summary_rows, layer_rows, pca_rows


def collect_depth_trajectories(spec: RunSpec) -> list[dict]:
    path = os.path.join(spec.run_dir, "results", "embedding_prevalence.csv")
    rows = []
    for r in load_csv(path):
        if r["strategy"] not in ("p1", "p4"):
            continue
        rows.append({
            "model": spec.model,
            "strategy": r["strategy"],
            "layer_idx": r["layer_idx"],
            "layer_depth_pct": r["layer_depth_pct"],
            "r2_cv": r["r2_cv"],
            "spearman_rho_cv": r.get("spearman_rho_cv", ""),
            "best_alpha": r.get("best_alpha", ""),
            "n": r.get("n", ""),
        })
    return rows


def collect_strategy_peak_r2(spec: RunSpec) -> list[dict]:
    path = os.path.join(spec.run_dir, "results", "embedding_prevalence.csv")
    best = {}
    for r in load_csv(path):
        strat = r["strategy"]
        if strat not in STRATEGIES:
            continue
        val = float(r["r2_cv"])
        if strat not in best or val > float(best[strat]["r2_cv"]):
            best[strat] = r
    return [{
        "model": spec.model,
        "strategy": strat,
        "peak_layer_idx": row["layer_idx"],
        "peak_layer_depth_pct": row["layer_depth_pct"],
        "peak_r2_cv": row["r2_cv"],
        "peak_spearman_rho_cv": row.get("spearman_rho_cv", ""),
        "best_alpha": row.get("best_alpha", ""),
        "n": row.get("n", ""),
    } for strat, row in sorted(best.items())]


def collect_hr_by_bin(spec: RunSpec) -> list[dict]:
    rows = load_tsv(os.path.join(spec.run_dir, "scored.tsv"))
    buckets: dict[str, list[dict]] = {}
    for r in rows:
        buckets.setdefault(r.get("citation_bin", "unknown") or "unknown", []).append(r)

    out = []
    for bucket in sorted(buckets, key=citation_bin_sort_key):
        group = buckets[bucket]
        row = {
            "model": spec.model,
            "citation_bin": bucket,
            "n": len(group),
            "mean_citation_count": round(
                float(np.mean([float(g.get("citation_count", 0) or 0) for g in group])),
                6,
            ),
        }
        for metric in HR_METRICS:
            vals = [float(g[metric]) for g in group if g.get(metric, "") != ""]
            row[f"mean_{metric}"] = round(float(np.mean(vals)), 6) if vals else ""
        out.append(row)
    return out


def collect_mediation_summary(spec: RunSpec) -> list[dict]:
    path = os.path.join(spec.run_dir, "results", "mediation_results.csv")
    rows = []
    for r in load_csv(path):
        if r.get("strategy") != "p1":
            continue
        rows.append({
            "model": spec.model,
            **r,
        })
    return rows


def validate_inputs(specs: Iterable[RunSpec]) -> None:
    required = [
        "embeddings.h5",
        "scored.tsv",
        "per_name_labels.tsv",
        os.path.join("results", "embedding_prevalence.csv"),
        os.path.join("results", "mediation_results.csv"),
    ]
    for spec in specs:
        for rel in required:
            path = os.path.join(spec.run_dir, rel)
            if not os.path.exists(path):
                raise FileNotFoundError(f"{spec.model}: missing {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 6: follow-up mechanistic analyses")
    parser.add_argument("--runs", nargs="+", required=True, help="Entries like model_name=/path/to/run_dir")
    parser.add_argument("--optimal_layers", nargs="+", required=True, help="Entries like model_name:48")
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    runs = parse_runs(args.runs)
    layers = parse_layers(args.optimal_layers)
    missing_layers = sorted(set(runs) - set(layers))
    if missing_layers:
        raise ValueError(f"Missing --optimal_layers entries for: {missing_layers}")

    specs = [
        RunSpec(model=name, run_dir=os.path.abspath(path), optimal_layer=layers[name])
        for name, path in runs.items()
    ]
    validate_inputs(specs)
    os.makedirs(args.out_dir, exist_ok=True)

    probe_metrics, probe_predictions = [], []
    regression_metrics, regression_predictions = [], []
    p9_summary, p9_by_layer, p9_pca = [], [], []
    depth_rows, peak_rows, hr_rows, med_rows = [], [], [], []

    for spec in specs:
        print(f"[stage6] {spec.model}: running P1 early-warning probe")
        m, p, rm, rp = run_probe(spec, args.out_dir)
        probe_metrics.extend(m)
        probe_predictions.extend(p)
        regression_metrics.extend(rm)
        regression_predictions.extend(rp)

        print(f"[stage6] {spec.model}: running P9 entity geometry")
        s, b, pca = run_p9_geometry(spec)
        p9_summary.extend(s)
        p9_by_layer.extend(b)
        p9_pca.extend(pca)

        print(f"[stage6] {spec.model}: collecting figure/table data")
        depth_rows.extend(collect_depth_trajectories(spec))
        peak_rows.extend(collect_strategy_peak_r2(spec))
        hr_rows.extend(collect_hr_by_bin(spec))
        med_rows.extend(collect_mediation_summary(spec))

    write_csv(
        os.path.join(args.out_dir, "probe_hallucination_auc.csv"),
        probe_metrics,
        [
            "model", "strategy", "layer_idx", "label_definition",
            "hr2_low_cutoff", "hr2_high_cutoff", "n", "n_excluded",
            "positive_rate", "auroc", "auprc", "accuracy_at_0_5",
            "balanced_accuracy_at_0_5",
        ],
    )
    write_tsv(
        os.path.join(args.out_dir, "probe_hallucination_predictions.tsv"),
        probe_predictions,
        [
            "model", "paper_id", "citation_count", "citation_bin", "hr2",
            "is_hallucinated", "p_hallucinated_oof",
        ],
    )
    p9_fields = [
        "model", "layer_idx", "layer_depth_pct", "n_names", "n_matched",
        "n_hallucinated", "centroid_cosine", "centroid_l2",
        "within_matched_cosine_to_centroid",
        "within_hallucinated_cosine_to_centroid", "probe_auroc",
        "centroid_perm_p",
    ]
    write_csv(os.path.join(args.out_dir, "p9_entity_geometry.csv"), p9_summary, p9_fields)
    write_csv(os.path.join(args.out_dir, "p9_entity_geometry_by_layer.csv"), p9_by_layer, p9_fields)
    write_tsv(
        os.path.join(args.out_dir, "probe_hr2_regression_predictions.tsv"),
        regression_predictions,
        [
            "model", "paper_id", "citation_count", "citation_bin", "hr2",
            "hr2_pred_oof",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "probe_hr2_regression.csv"),
        regression_metrics,
        [
            "model", "strategy", "layer_idx", "n", "best_alpha", "r2_cv",
            "spearman_rho", "pearson_r", "mae",
        ],
    )
    write_tsv(
        os.path.join(args.out_dir, "p9_entity_pca.tsv"),
        p9_pca,
        [
            "model", "preprocessing", "paper_id", "name_str", "author_pos",
            "is_hallucinated", "citation_count", "citation_bin", "field",
            "pc1", "pc2",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "depth_trajectories.csv"),
        depth_rows,
        [
            "model", "strategy", "layer_idx", "layer_depth_pct", "r2_cv",
            "spearman_rho_cv", "best_alpha", "n",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "strategy_peak_r2.csv"),
        peak_rows,
        [
            "model", "strategy", "peak_layer_idx", "peak_layer_depth_pct",
            "peak_r2_cv", "peak_spearman_rho_cv", "best_alpha", "n",
        ],
    )
    write_csv(
        os.path.join(args.out_dir, "hr_by_citation_bin.csv"),
        hr_rows,
        [
            "model", "citation_bin", "n", "mean_citation_count",
            "mean_hr2", "mean_hr4", "mean_hr5",
        ],
    )
    med_fields = ["model"]
    if med_rows:
        med_fields += [k for k in med_rows[0].keys() if k != "model"]
    write_csv(os.path.join(args.out_dir, "mediation_summary.csv"), med_rows, med_fields)

    print(f"[stage6] Wrote follow-up outputs to {args.out_dir}")


if __name__ == "__main__":
    main()
