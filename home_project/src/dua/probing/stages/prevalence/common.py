"""Shared constants, run-directory I/O, and small statistics helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

try:  # h5py is only needed to read embeddings.h5, not to import this package.
    import h5py
except ImportError:  # pragma: no cover
    h5py = None


class _LazyPyplot:
    """Import pyplot, on the Agg backend, the first time a plot is drawn."""

    def __getattr__(self, name):
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as _plt

        return getattr(_plt, name)


plt = _LazyPyplot()


RANDOM_SEED = 42


N_SVD_COMPONENTS = 100


STRATEGIES = ["p1", "p2", "p3", "p4", "p5"]


RIDGE_ALPHAS = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]


MODEL_LABELS = {
    "qwen3_32b": "Qwen3-32B",
    "mistral_small_3_2_24b": "Mistral-Small-3.2-24B",
}


MODEL_COLORS = {
    "qwen3_32b": "#1B7837",
    "mistral_small_3_2_24b": "#B35806",
}


CITATION_BUCKET_BINS = [-0.5, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, float("inf")]


CITATION_BUCKET_LABELS = [
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


@dataclass(frozen=True)
class RunSpec:
    model: str
    run_dir: Path
    optimal_layer: int


def model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model.replace("_", " "))


def parse_runs(items: list[str]) -> dict[str, Path]:
    runs: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--runs entry must be model=/path, got {item!r}")
        name, path = item.split("=", 1)
        if not name.strip() or not path.strip():
            raise ValueError(f"Invalid --runs entry: {item!r}")
        runs[name.strip()] = Path(path.strip()).expanduser().resolve()
    return runs


def parse_layers(items: list[str]) -> dict[str, int]:
    layers: dict[str, int] = {}
    for item in items:
        if ":" not in item:
            raise ValueError(f"--optimal_layers entry must be model:layer, got {item!r}")
        name, layer = item.split(":", 1)
        layers[name.strip()] = int(layer)
    return layers


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def decode_array(values) -> list[str]:
    return [v.decode("utf-8") if isinstance(v, bytes) else str(v) for v in values]


def write_df(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[stage8] wrote {path}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"[stage8] wrote {path}")


def find_scored_path(run_dir: Path) -> Path:
    candidates = [
        run_dir / "scored.tsv",
        run_dir.parent / "scored.tsv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Missing scored.tsv for run directory {run_dir}")


def find_h5_path(run_dir: Path) -> Path:
    candidates = [
        run_dir / "embeddings.h5",
        run_dir.parent / "embeddings.h5",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Missing embeddings.h5 for run directory {run_dir}")


def find_results_dir(run_dir: Path) -> Path:
    if (run_dir / "embedding_prevalence.csv").exists():
        return run_dir
    if (run_dir / "results" / "embedding_prevalence.csv").exists():
        return run_dir / "results"
    return run_dir / "results"


def load_layer_indices(h5: h5py.File) -> list[int]:
    raw = h5.attrs["layer_indices"]
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        return [int(x) for x in json.loads(raw)]
    return [int(x) for x in raw]


def layer_position(layers: list[int], layer_idx: int) -> int:
    if layer_idx not in layers:
        raise ValueError(f"Layer {layer_idx} is not in HDF5 layer_indices={layers}")
    return layers.index(layer_idx)


def align_rows(h5: h5py.File, scored: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    scored = scored.copy()
    scored["paper_id"] = scored["paper_id"].astype(str)
    by_pid = scored.set_index("paper_id", drop=False)
    valid_idx: list[int] = []
    rows: list[pd.Series] = []
    for i, pid in enumerate(decode_array(h5["paper_ids"][:])):
        if pid in by_pid.index:
            valid_idx.append(i)
            rows.append(by_pid.loc[pid])
    if not valid_idx:
        raise ValueError("No overlapping paper IDs between embeddings.h5 and scored.tsv")
    return np.array(valid_idx, dtype=np.int64), pd.DataFrame(rows).reset_index(drop=True)


def svd_reduce(X: np.ndarray, n_components: int = N_SVD_COMPONENTS) -> np.ndarray:
    from sklearn.utils.extmath import randomized_svd

    k = min(n_components, X.shape[0] - 1, X.shape[1])
    if k < 1:
        raise ValueError(f"Need at least 2 rows and 1 feature for SVD, got {X.shape}")
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, _ = randomized_svd(X_c, n_components=k, random_state=RANDOM_SEED)
    return U * S


def r2_from_predictions(y: np.ndarray, pred: np.ndarray) -> float:
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def spearman(y: np.ndarray, pred: np.ndarray) -> float:
    from scipy.stats import spearmanr

    return float(spearmanr(y, pred).statistic)


def add_citation_buckets(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["citation_bucket"] = pd.cut(
        pd.to_numeric(out["citation_count"], errors="coerce"),
        bins=CITATION_BUCKET_BINS,
        labels=CITATION_BUCKET_LABELS,
        include_lowest=True,
        right=True,
    )
    return out


def load_p1_embeddings(spec: RunSpec) -> tuple[np.ndarray, pd.DataFrame, int]:
    scored = pd.read_csv(find_scored_path(spec.run_dir), sep="\t")
    h5_path = find_h5_path(spec.run_dir)
    with h5py.File(h5_path, "r") as h5:
        if "per_query/p1" not in h5:
            raise KeyError(f"{h5_path} does not contain per_query/p1")
        layers = load_layer_indices(h5)
        pos = layer_position(layers, spec.optimal_layer)
        valid_idx, aligned = align_rows(h5, scored)
        X = h5["per_query/p1"][:, pos, :][valid_idx].astype(np.float32)
        n_model_layers = int(h5.attrs.get("n_model_layers", max(layers) + 1))
    return X, aligned, n_model_layers
