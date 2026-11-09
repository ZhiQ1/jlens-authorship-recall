"""D11-1 v2 hard check (config/prereg_addendum11_deviations_v2.json): the new probe / report reproduce the old pipeline EXACTLY
(max |diff| = 0) for every V0 and V5x0 table including the control rows. CPU. Nothing existing is edited.

  --tiny        root b2_np_tiny: old probe (summary_b2_np/probe) vs probe v2 (summary_b2_np/probe_v2): every old perpaper column,
                pertoken file and fit json; then old report csvs vs report v2 csvs (V0, V5x0 rows of role_layer incl. controls,
                V5x0 lens, V5x0 H3, V5x0 group split).
  --real-shard0 test roots 381_stage13/b2_np_v2check/{old,new} with symlinks to the completed real GPU unit shard_000 of true and
                false_0..4, the real raw/allTok_L63, real vocab rows and real summary_b2_np/{checks,hardcheck2.json,lens_perpaper.parquet}.
                The old probe (imported; its R13 pointed at the test root and its 72-shard count check bypassed - no computation changed)
                and probe v2 run on those papers at all 5 layers with the same seeds / folds; the old report is executed from its source
                with only its `root = ...` line pointed at the test root; report v2 runs with --root. Both reports exit 3 there
                (hard check 1 needs 72 shards) - expected; their csvs are compared.
Writes <root>/v2_check.json; exit 1 on any mismatch.
"""
import argparse, importlib.util, json, os, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; W = H / '13_stage13'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); PY = str(Path.home() / 'conda-envs/jlens/bin/python')
LAYERS = [32, 40, 48, 52, 56]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def maxdiff(x, y):
    """exact comparison: NaN pattern must agree; returns max |diff| (inf if NaN patterns or shapes differ)."""
    x, y = np.asarray(x), np.asarray(y)
    if x.shape != y.shape: return float('inf')
    if x.dtype.kind in 'fc' or y.dtype.kind in 'fc':
        x, y = x.astype(float), y.astype(float)
        if not np.array_equal(np.isnan(x), np.isnan(y)): return float('inf')
        m = ~np.isnan(x); return float(np.abs(x[m] - y[m]).max()) if m.any() else 0.0
    return 0.0 if np.array_equal(x, y) else float('inf')


def cmp_probe(po, pn):
    res = dict(perpaper=0.0, pertoken=0.0, fit_equal=True, files=0, missing=[], ctrl_recompute=0.0)
    for fo in sorted(po.glob('perpaper_*.parquet')):
        fn = pn / fo.name
        if not fn.exists(): res['missing'].append(fn.name); continue
        a, b = pd.read_parquet(fo), pd.read_parquet(fn); res['files'] += 1
        for c in a.columns:
            res['perpaper'] = max(res['perpaper'], maxdiff(a[c].to_numpy(), b[c].to_numpy()) if c in b else float('inf'))
        # stored per-title controls reproduce the old collapsed columns (same float operations as the probe)
        for tag in ('any', 'field'):
            t = b[f'ctrl_{tag}_t'].to_numpy(); f = [b[f'ctrl_{tag}_f{k}'].to_numpy() for k in range(5)]
            res['ctrl_recompute'] = max(res['ctrl_recompute'], maxdiff(t - f[0], a[f'ctrl_{tag}0']), maxdiff(t - np.mean(f, 0), a[f'ctrl_{tag}5']))
        to, tn = pd.read_parquet(po / fo.name.replace('perpaper', 'pertoken')), pd.read_parquet(pn / fo.name.replace('perpaper', 'pertoken'))
        for c in to.columns: res['pertoken'] = max(res['pertoken'], maxdiff(to[c].to_numpy(), tn[c].to_numpy()))
        jo = json.loads((po / fo.name.replace('perpaper', 'fit').replace('.parquet', '.json')).read_text())
        jn = json.loads((pn / fo.name.replace('perpaper', 'fit').replace('.parquet', '.json')).read_text())
        res['fit_equal'] &= jo == jn
    res['status'] = 'PASS' if res['files'] > 0 and not res['missing'] and res['perpaper'] == 0 and res['pertoken'] == 0 and res['fit_equal'] and res['ctrl_recompute'] == 0 else 'FAIL'
    return res


def cmp_tab(a, b, keys, cols):
    m = a.merge(b, on=keys, suffixes=('_o', '_n'), how='outer', indicator=True)
    un = int((m._merge != 'both').sum()); mm = max([maxdiff(m[f'{c}_o'].to_numpy(float), m[f'{c}_n'].to_numpy(float)) for c in cols] or [0.0])
    return dict(n=len(m), unmatched=un, max_abs_diff=mm, status='PASS' if len(m) and un == 0 and mm == 0 else 'FAIL')


def cmp_reports(Oo, On):
    res = {}
    to, tn = pd.read_csv(Oo / 'np_role_layer.csv'), pd.read_csv(On / 'np_role_layer_v2.csv')
    num = [c for c in to.columns if c not in ('version', 'run', 'layer')]          # includes any_*/field_* control rows
    for v in ('V0', 'V5x0'): res[f'role_layer_{v}_incl_controls'] = cmp_tab(to[to.version == v], tn[tn.version == v], ['version', 'run', 'layer'], num)
    if (Oo / 'np_lens_compare.csv').exists() and (Oo / 'np_lens_compare.csv').stat().st_size > 1:
        lo, ln = pd.read_csv(Oo / 'np_lens_compare.csv'), pd.read_csv(On / 'np_lens_compare_v2.csv')
        res['lens_V5x0'] = cmp_tab(lo[lo.version == 'V5x0'], ln[ln.version == 'V5x0'], ['version', 'run', 'layer', 'readout'], [c for c in lo.columns if c not in ('version', 'run', 'layer', 'readout')])
        ho, hn = pd.read_csv(Oo / 'np_h3_primary.csv'), pd.read_csv(On / 'np_h3_primary_v2.csv')
        res['h3_V5x0'] = cmp_tab(ho[ho.version == 'V5x0'], hn[hn.version == 'V5x0'], ['version', 'run', 'layer', 'readout'], ['probe', 'probe_lo', 'probe_hi', 'lens', 'lens_lo', 'lens_hi'])
    if (Oo / 'np_groups_unwritten.csv').exists():
        go, gn = pd.read_csv(Oo / 'np_groups_unwritten.csv'), pd.read_csv(On / 'np_groups_unwritten_v2.csv')
        res['groups_V5x0'] = cmp_tab(go, gn[gn.version == 'V5x0'].drop(columns='version'), ['run', 'layer', 'group'], ['est', 'lo', 'hi', 'n'])
    idf = On / 'np_vpd_title_identity_v2.csv'
    if idf.exists():
        I = pd.read_csv(idf); res['vpd_title_identity'] = dict(cells=int(len(I) // 3), status='PASS' if len(I) and I.identical.all() else 'FAIL')
    return res


def link(dst, src):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() and not dst.is_symlink(): dst.symlink_to(src)


def run_probe(mod_path, name, root, layer):
    m = load(mod_path, name); m.R13 = root; orig = m.load_layer
    m.load_layer = lambda raw, cond, l, rows_ref=None: (lambda r: (r[0], r[1], 72))(orig(raw, cond, l, rows_ref))   # 1 shard: bypass the 72-shard count only
    sys.argv = [name, '--layer', str(layer)]; m.main()


def run_old_report(root):
    src = (W / 'stage13_b2_np_report.py').read_text(); o = "root = R13 / 'b2_np_tiny' if a.tiny else R13\n"
    if src.count(o) != 1: raise SystemExit('old report root line not found')
    src = src.replace(o, f"root = Path({str(root)!r})\n")
    sys.argv = ['stage13_b2_np_report.py']
    try: exec(compile(src, str(W / 'stage13_b2_np_report.py'), 'exec'), {'__name__': '__main__', '__file__': str(W / 'stage13_b2_np_report.py')})
    except SystemExit as e: return e.code
    return 0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); ap.add_argument('--real-shard0', action='store_true')
    ap.add_argument('--step', default='all', choices=['all', 'old_probe', 'new_probe', 'reports', 'compare']); ap.add_argument('--layer', type=int)
    a = ap.parse_args(); res = {}
    if a.tiny:
        O = R13 / 'b2_np_tiny/summary_b2_np'
        res['probe'] = cmp_probe(O / 'probe', O / 'probe_v2'); res.update(cmp_reports(O, O)); out = R13 / 'b2_np_tiny/v2_check.json'
    else:
        T = R13 / 'b2_np_v2check'; RO, RN = T / 'old', T / 'new'
        if a.step in ('all', 'old_probe', 'new_probe', 'reports'):
            for r in (RO, RN):
                for c in ['true'] + [f'false_{k}' for k in range(5)]: link(r / f'raw/b2_npprobe/{c}/shard_000.npz', R13 / f'raw/b2_npprobe/{c}/shard_000.npz')
                link(r / 'raw/allTok_L63', R13 / 'raw/allTok_L63'); link(r / 'summary_alltok/vocab_rows.npz', R13 / 'summary_alltok/vocab_rows.npz')
                link(r / 'summary_b2_np/checks', R13 / 'summary_b2_np/checks'); link(r / 'summary_b2_np/hardcheck2.json', R13 / 'summary_b2_np/hardcheck2.json')
                link(r / 'summary_b2_np/lens_perpaper.parquet', R13 / 'summary_b2_np/lens_perpaper.parquet')
        ls = [a.layer] if a.layer else LAYERS
        if a.step in ('all', 'old_probe'):
            for l in ls: run_probe(W / 'stage13_b2_np_probe.py', 'np_probe_old', RO, l)
        if a.step in ('all', 'new_probe'):
            for l in ls: run_probe(W / 'stage13_b2_np_probe_v2.py', 'np_probe_new', RN, l)
        if a.step in ('all', 'reports'):
            res['old_report_exit'] = run_old_report(RO)
            res['report_v2_exit'] = subprocess.run([PY, '-u', str(W / 'stage13_b2_np_report_v2.py'), '--root', str(RN)], cwd=W).returncode
            res['report_exit_note'] = 'exit 3 expected on 1 shard (hard check 1 needs 72 true shards)'
        if a.step in ('all', 'compare'):
            res['probe'] = cmp_probe(RO / 'summary_b2_np/probe', RN / 'summary_b2_np/probe_v2')
            res.update(cmp_reports(RO / 'summary_b2_np', RN / 'summary_b2_np'))
            res['n_papers_shard0'] = {f.stem: int(len(pd.read_parquet(f))) for f in sorted((RN / 'summary_b2_np/probe_v2').glob('perpaper_*_L40.parquet'))}
        out = T / f'v2_check_{a.step}.json'
    st = [v['status'] for v in res.values() if isinstance(v, dict) and 'status' in v]
    res['status'] = 'PASS' if st and all(s == 'PASS' for s in st) else ('FAIL' if st else 'n/a')
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(res, indent=1, default=str)); print(json.dumps(res, indent=1, default=str))
    print('V2 CHECK', res['status']); sys.exit(1 if res['status'] == 'FAIL' else 0)


if __name__ == '__main__':
    main()
