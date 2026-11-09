"""Addendum 11 A, deviation D11-1 (config/prereg_addendum11_deviations.json, written 2026-11-08 00:13:52 EST before any probe
result): per-donor exclusion (Vpd) for the name-position probe. Pure functions, unit-tested in stage13_b2_np_report_v2_test.py.

usable_k = not dropped_k (the false_k donor is not a paper of this run in another training fold; probe column dropped_k).
Vpd per paper = true - mean over the USABLE k of false_k = mean over usable k of spec_k (spec_k = true - false_k), as the E4b
deviation D1 implementation (stage13_b1_e4b5_perdonor.py: nansum(spec_k * use) / n_used). A paper with n_used = 0 is dropped (NaN).
Difference to the E4b line, stated here: a usable spec_k that is NaN is left out of the mean (nanmean over usable k) instead of
counting as 0; the number of such cells is returned so the report can show it (probe: expected 0, then both formulas agree).
"""
import numpy as np

KS = [0, 1, 2, 3, 4]


def use_matrix(d):
    """[n, 5] bool: false_k usable for the paper (not dropped_k)."""
    return np.stack([~d[f'dropped_{k}'].to_numpy(bool) for k in KS], 1)


def pd_mean(spec_k, use):
    """spec_k [n, 5] float, use [n, 5] bool -> (vpd [n], n_used [n], n_usable_nan). vpd NaN when no usable finite title."""
    spec_k = np.asarray(spec_k, float); use = np.asarray(use, bool)
    n_used = use.sum(1)
    m = use & np.isfinite(spec_k)
    cnt = m.sum(1)
    s = np.where(m, spec_k, 0.0).sum(1)
    vpd = np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)
    return vpd, n_used, int((use & ~np.isfinite(spec_k)).sum())


def perdonor(d):
    """probe perpaper frame -> adds n_used, spec_pd; returns (d, n_usable_nan)."""
    sk = np.stack([d[f'spec_k{k}'].to_numpy(float) for k in KS], 1)
    v, n, bad = pd_mean(sk, use_matrix(d))
    d = d.copy(); d['n_used'] = n; d['spec_pd'] = v
    return d, bad


def from_scores(true, false_k, use):
    """true [n], false_k [n, 5] -> Vpd of (true - false_k) over usable k (lens and token-level group split)."""
    true = np.asarray(true, float)
    return pd_mean(true[:, None] - np.asarray(false_k, float), use)


def eff_count(spec_k, use):
    """per paper: number of false titles that actually enter the Vpd mean (usable and finite) - for the D11-1 v2 identity check."""
    return (np.asarray(use, bool) & np.isfinite(np.asarray(spec_k, float))).sum(1)


def perdonor_ctrl(d, tags=('any', 'field')):
    """D11-1 v2: control rows averaged over the SAME usable mask as the main Vpd result (per-title control columns of
    stage13_b2_np_probe_v2.py: ctrl_<tag>_t, ctrl_<tag>_f0..f4). Adds ctrl_<tag>_pd and n_eff_ctrl_<tag>; adds n_eff_main.
    Missing per-title columns -> NaN (and n_eff 0), so the identity check fails visibly."""
    d = d.copy(); use = use_matrix(d)
    sk = np.stack([d[f'spec_k{k}'].to_numpy(float) for k in KS], 1); d['n_eff_main'] = eff_count(sk, use)
    for tag in tags:
        if f'ctrl_{tag}_t' in d and all(f'ctrl_{tag}_f{k}' in d for k in KS):
            ck = d[f'ctrl_{tag}_t'].to_numpy(float)[:, None] - np.stack([d[f'ctrl_{tag}_f{k}'].to_numpy(float) for k in KS], 1)
        else:
            ck = np.full(sk.shape, np.nan)
        d[f'ctrl_{tag}_pd'] = pd_mean(ck, use)[0]; d[f'n_eff_ctrl_{tag}'] = eff_count(ck, use)
    return d
