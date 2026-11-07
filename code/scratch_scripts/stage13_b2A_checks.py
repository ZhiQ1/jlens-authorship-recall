"""Batch 2 group A: hard-check functions (pure; unit-tested in stage13_b2A_hcunit.py). Each returns a dict with 'status' PASS/FAIL
and the measured values + tolerance. Callers write the dict to a json and exit non-zero on FAIL (plan: a hard-check miss stops
that item)."""
import numpy as np, pandas as pd


def rel_norm_check(new, ref, tol, name='rel_norm'):
    """row-wise relative L2 difference ||new - ref|| / ||ref|| (float32), PASS if max <= tol. Shapes must agree."""
    new = np.asarray(new, np.float32); ref = np.asarray(ref, np.float32)
    if new.shape != ref.shape or new.size == 0:
        return dict(check=name, status='FAIL', reason=f'shape mismatch / empty {new.shape} vs {ref.shape}', tol=tol)
    r = np.linalg.norm(new - ref, axis=-1) / np.maximum(np.linalg.norm(ref, axis=-1), 1e-9)
    ok = bool(np.isfinite(r).all() and r.max() <= tol)
    return dict(check=name, status='PASS' if ok else 'FAIL', rel_max=float(np.nanmax(r)), rel_mean=float(np.nanmean(r)),
                bitexact_share=float((new == ref).all(-1).mean()), n=int(r.size), tol=tol)


def value_table_check(new, ref, keys, val, tol, name='values', ref_val=None):
    """join two tables on keys; PASS if every reference row is present and |new - ref| <= tol for all rows."""
    ref_val = ref_val or val
    m = ref[keys + [ref_val]].rename(columns={ref_val: '_ref'}).merge(new[keys + [val]].rename(columns={val: '_new'}), on=keys, how='left')
    miss = int(m._new.isna().sum() - m._ref.isna().sum()) if len(m) else 0
    d = (m._new - m._ref).abs()
    ok = bool(len(m) > 0 and miss == 0 and (d.dropna() <= tol).all())
    worst = m.loc[d.idxmax()].to_dict() if len(m) and d.notna().any() else {}
    return dict(check=name, status='PASS' if ok else 'FAIL', n=int(len(m)), n_missing=miss, max_abs_diff=float(d.max()) if len(m) else np.nan,
                tol=tol, worst={k: (v if isinstance(v, (str, int)) else float(v)) for k, v in worst.items()})


def scalar_check(new, ref, tol, name='scalar'):
    ok = bool(np.isfinite(new) and abs(new - ref) <= tol)
    return dict(check=name, status='PASS' if ok else 'FAIL', new=float(new), ref=float(ref), abs_diff=float(abs(new - ref)), tol=tol)


def combine(*checks, name='hard'):
    return dict(check=name, status='PASS' if checks and all(c['status'] == 'PASS' for c in checks) else 'FAIL', parts=list(checks))
