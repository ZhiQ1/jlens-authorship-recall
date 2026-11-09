"""Tests for D11-1 report v2 (stage13_b2_np_report_v2.py / stage13_b2_np_vpd.py). CPU.
  --unit          Vpd on a synthetic case with hand-computed answers + an independent loop; E4b formula agreement when no NaN.
  --tiny-compare  on the tiny root (b2_np_tiny): V0 and V5x0 rows of np_role_layer_v2.csv equal the original report's
                  np_role_layer.csv; V5x0 lens rows equal the original (lens spec5); V5x0 H3 rows equal; V5x0 group split equals
                  the original (it ran with the false_0 rule on tiny); Vpd rows present for every (run, layer).
Writes b2_np_tiny/summary_b2_np/v2_test.json for --tiny-compare. Exit 1 on FAIL.
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


VP = load(H / '13_stage13/stage13_b2_np_vpd.py', 'b2np_vpd')


def unit():
    # 4 papers; spec_k columns and dropped flags; expected Vpd by hand
    d = pd.DataFrame({'paper_id': ['a', 'b', 'c', 'd'],
                      **{f'spec_k{k}': v for k, v in enumerate([[1.0, 0.5, 2.0, 9.0], [2.0, 0.5, 4.0, 9.0], [3.0, 0.5, 6.0, 9.0], [4.0, 0.5, np.nan, 9.0], [5.0, 0.5, 8.0, 9.0]])},
                      **{f'dropped_{k}': v for k, v in enumerate([[False, True, True, True], [False, True, False, True], [True, True, False, True],
                                                                  [True, True, False, True], [False, False, True, True]])}})
    # a: usable k0,k1,k4 -> (1+2+5)/3 = 8/3 ; b: usable k4 -> 0.5 ; c: usable k1,k2 (k3 NaN usable -> left out) -> (4+6)/2 = 5 ; d: none -> NaN
    exp_v = np.array([8 / 3, 0.5, 5.0, np.nan]); exp_n = np.array([3, 1, 3, 0])
    out, bad = VP.perdonor(d)
    ok1 = np.allclose(out.spec_pd.to_numpy(), exp_v, equal_nan=True) and (out.n_used.to_numpy() == exp_n).all() and bad == 1
    # independent loop on random data
    rng = np.random.default_rng(0); S = rng.standard_normal((500, 5)); Dm = rng.random((500, 5)) < 0.6
    loop = np.array([S[i][~Dm[i]].mean() if (~Dm[i]).any() else np.nan for i in range(500)])
    v, n, b = VP.pd_mean(S, ~Dm)
    ok2 = np.allclose(v, loop, equal_nan=True) and b == 0
    # E4b formula (stage13_b1_e4b5_perdonor.py): nansum(spec * use) / n_used, NaN if n_used = 0 -> equal when no NaN
    use = (~Dm).astype(float); nu = use.sum(1); e4b = np.nansum(S * use, 1) / np.where(nu > 0, nu, np.nan)
    ok3 = np.allclose(v, e4b, equal_nan=True)
    # from_scores: true - false
    T_ = rng.standard_normal(500); F_ = rng.standard_normal((500, 5)); v2 = VP.from_scores(T_, F_, ~Dm)[0]
    ok4 = np.allclose(v2, np.array([(T_[i] - F_[i][~Dm[i]]).mean() if (~Dm[i]).any() else np.nan for i in range(500)]), equal_nan=True)
    r = dict(synthetic_known_answer=ok1, got=[None if np.isnan(x) else float(x) for x in out.spec_pd], n_used=out.n_used.tolist(), nan_usable=bad,
             random_vs_loop=ok2, equals_e4b_formula_without_nan=ok3, from_scores=ok4)
    r['status'] = 'PASS' if all([ok1, ok2, ok3, ok4]) else 'FAIL'
    return r


def cmp(a, b, keys, cols, tol=1e-12):
    m = a.merge(b, on=keys, suffixes=('_o', '_n'), how='outer', indicator=True)
    miss = int((m._merge != 'both').sum()); worst = 0.0
    for c in cols:
        x, y = m[f'{c}_o'].to_numpy(float), m[f'{c}_n'].to_numpy(float)
        both_nan = np.isnan(x) & np.isnan(y); dif = np.where(both_nan, 0, np.abs(x - y)); worst = max(worst, float(np.nanmax(np.where(np.isnan(dif), np.inf, dif))) if len(dif) else 0.0)
    return dict(n=len(m), unmatched=miss, max_abs_diff=worst, status='PASS' if miss == 0 and worst <= tol else 'FAIL')


def tiny_compare():
    O = R13 / 'b2_np_tiny/summary_b2_np'; res = {}
    to, tn = pd.read_csv(O / 'np_role_layer.csv'), pd.read_csv(O / 'np_role_layer_v2.csv')
    num = [c for c in to.columns if c not in ('version', 'run', 'layer')]
    for v in ('V0', 'V5x0'):
        res[f'role_layer_{v}'] = cmp(to[to.version == v], tn[tn.version == v], ['version', 'run', 'layer'], num)
    pairs = set(map(tuple, to[['run', 'layer']].drop_duplicates().to_numpy()))
    vp = tn[tn.version == 'Vpd']
    res['Vpd_rows_present'] = dict(n=len(vp), expected=len(pairs), finite_spec=int(np.isfinite(vp.spec).sum()),
                                   status='PASS' if set(map(tuple, vp[['run', 'layer']].to_numpy())) == pairs else 'FAIL')
    lo, ln = pd.read_csv(O / 'np_lens_compare.csv'), pd.read_csv(O / 'np_lens_compare_v2.csv')
    res['lens_V5x0'] = cmp(lo[lo.version == 'V5x0'], ln[ln.version == 'V5x0'], ['version', 'run', 'layer', 'readout'],
                           [c for c in lo.columns if c not in ('version', 'run', 'layer', 'readout')])
    ho, hn = pd.read_csv(O / 'np_h3_primary.csv'), pd.read_csv(O / 'np_h3_primary_v2.csv')
    res['h3_V5x0'] = cmp(ho[ho.version == 'V5x0'], hn[hn.version == 'V5x0'], ['version', 'run', 'layer', 'readout'], ['probe', 'probe_lo', 'probe_hi', 'lens', 'lens_lo', 'lens_hi'])
    if (O / 'np_groups_unwritten.csv').exists():
        go, gn = pd.read_csv(O / 'np_groups_unwritten.csv'), pd.read_csv(O / 'np_groups_unwritten_v2.csv')
        # original tiny report used V5x0 (false_0 exclusion) for the group split when V5 kept < 1,000 papers
        res['groups_V5x0'] = cmp(go, gn[gn.version == 'V5x0'].drop(columns='version'), ['run', 'layer', 'group'], ['est', 'lo', 'hi', 'n'])
    # V0 in v2 = the false_0-only numbers of the original (probe columns); the original lens V0 rows used lens spec5 (not compared)
    res['status'] = 'PASS' if all(r['status'] == 'PASS' for r in res.values() if isinstance(r, dict)) else 'FAIL'
    (O / 'v2_test.json').write_text(json.dumps(res, indent=1)); return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--unit', action='store_true'); ap.add_argument('--tiny-compare', action='store_true'); a = ap.parse_args()
    ok = True
    if a.unit: r = unit(); print('UNIT', json.dumps(r)); ok &= r['status'] == 'PASS'
    if a.tiny_compare: r = tiny_compare(); print('TINY-COMPARE', json.dumps(r, indent=1)); ok &= r['status'] == 'PASS'
    print('V2 TEST', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
