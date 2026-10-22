"""Ridge decoders from hidden states to log(citations+1), and the metadata features.

``fold_safe_pca_ridge_oof`` is the decoder the paper reports: PCA, scaling,
and RidgeCV are refit inside every training fold.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dua.probing.stages.prevalence.common import N_SVD_COMPONENTS, RANDOM_SEED, RIDGE_ALPHAS


def ridge_oof(X: np.ndarray, y: np.ndarray, cv_splits: int = 5) -> tuple[np.ndarray, float]:
    from sklearn.linear_model import Ridge, RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    n_splits = min(cv_splits, len(y))
    if n_splits < 2:
        raise ValueError("Need at least two rows for cross-validation")
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    selector = make_pipeline(StandardScaler(), RidgeCV(alphas=RIDGE_ALPHAS, cv=cv))
    selector.fit(X, y)
    alpha = float(selector.named_steps["ridgecv"].alpha_)
    model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    pred = cross_val_predict(model, X, y, cv=cv)
    return pred, alpha


def ridge_oof_unscaled_stage5_style(
    X: np.ndarray,
    y: np.ndarray,
    cv_splits: int = 5,
) -> tuple[np.ndarray, float]:
    """Stage5-style ridge: global SVD features, no scaling, non-shuffled folds."""
    from sklearn.linear_model import Ridge, RidgeCV
    from sklearn.model_selection import cross_val_predict

    n_splits = min(cv_splits, len(y))
    selector = RidgeCV(alphas=RIDGE_ALPHAS, cv=n_splits)
    selector.fit(X, y)
    alpha = float(selector.alpha_)
    pred = cross_val_predict(Ridge(alpha=alpha), X, y, cv=n_splits)
    return pred, alpha


def fold_safe_pca_ridge_oof(
    X_raw: np.ndarray,
    y: np.ndarray,
    X_meta: np.ndarray | None = None,
    cv_splits: int = 5,
) -> tuple[np.ndarray, float]:
    """
    Leakage-safe prevalence decoder. PCA, scaling, and RidgeCV are fit only on
    each training fold before predicting the held-out fold.
    """
    from sklearn.decomposition import PCA
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler

    n_splits = min(cv_splits, len(y))
    cv = KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
    pred = np.empty(len(y), dtype=np.float64)
    alphas: list[float] = []

    for train_idx, test_idx in cv.split(X_raw):
        k = min(N_SVD_COMPONENTS, len(train_idx) - 1, X_raw.shape[1])
        pca = PCA(n_components=k, svd_solver="randomized", random_state=RANDOM_SEED)
        Z_train = pca.fit_transform(X_raw[train_idx])
        Z_test = pca.transform(X_raw[test_idx])

        z_scaler = StandardScaler()
        Z_train = z_scaler.fit_transform(Z_train)
        Z_test = z_scaler.transform(Z_test)

        if X_meta is not None:
            m_scaler = StandardScaler()
            M_train = m_scaler.fit_transform(X_meta[train_idx])
            M_test = m_scaler.transform(X_meta[test_idx])
            Z_train = np.hstack([M_train, Z_train])
            Z_test = np.hstack([M_test, Z_test])

        inner_cv = min(5, len(train_idx))
        model = RidgeCV(alphas=RIDGE_ALPHAS, cv=inner_cv)
        model.fit(Z_train, y[train_idx])
        alphas.append(float(model.alpha_))
        pred[test_idx] = model.predict(Z_test)

    return pred, float(np.median(alphas))


def metadata_matrix(scored: pd.DataFrame, include_field: bool = True) -> np.ndarray:
    meta = pd.DataFrame(index=scored.index)
    meta["year"] = pd.to_numeric(scored.get("year"), errors="coerce")
    meta["author_count"] = pd.to_numeric(
        scored.get("n_gt_authors", scored.get("n_pred_authors")), errors="coerce"
    )
    title = scored.get("title", pd.Series([""] * len(scored), index=scored.index)).fillna("")
    meta["title_length"] = title.astype(str).str.len()
    meta["title_tokens"] = title.astype(str).str.split().str.len()
    parts = [meta]
    if include_field:
        field = scored.get("field", pd.Series(["unknown"] * len(scored), index=scored.index))
        field_dummies = pd.get_dummies(field.fillna("unknown").astype(str), prefix="field")
        parts.append(field_dummies)
    out = pd.concat(parts, axis=1).fillna(meta.median(numeric_only=True))
    out = out.fillna(0.0)
    return out.to_numpy(dtype=np.float32)
