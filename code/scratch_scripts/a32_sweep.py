#!/usr/bin/env python3
"""Addendum 32 (Geva-style single-layer edge knockout sweep). Locked prereg: 391_groups/config/prereg_addendum32.md.

Reuses the frozen addendum 18b item 2 code by path (13_stage13/a18b_item2.py with the window-assignment fix of a18b_item2_fix.py,
both unchanged): same 600-paper sample, 5 edges (name<-title, name<-tail, tail<-title, colon<-title, name<-colon), S = true - mean
of 5 false titles at the final output, loss = S(none) - S(config). Only the window set differs: single layers L40, L42, ..., L56
(9 windows x 5 edges + none = 46 configs). Outputs raw/a32/main/shard_XXX.npz, summary_a32/.
Commands: work [--shards] | remaining | tiny | analyze
"""
import argparse, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path.home() / 'jlens_work/13_stage13'))
import a18b_common as A
import a18b_item2 as I2
import a18b_item2_fix as FIX      # installs the fixed mask (every window's layers fully blocked)

G = Path('/scratch/zhang.zhiqi2/jlens/391_groups')
W_SINGLE = [(l, l) for l in range(40, 57, 2)]
RAW = Path(os.environ.get('A32_RAW', G / 'raw/a32')); SUMM = Path(os.environ.get('A32_SUM', G / 'summary_a32'))


def lock_check():
    import hashlib
    lk = json.load(open(G / 'config/addendum32_lock.json')); h = hashlib.sha256((G / 'config/prereg_addendum32.md').read_bytes()).hexdigest()
    if h != lk['sha256']: raise SystemExit(f'addendum 32 changed after lock: {h}')
    return h


def select(): FIX.use(W_SINGLE, RAW, SUMM, 'single')


def work(a, C=None):
    if C is None: lock_check()
    select(); return I2.work(a, C=C)


def analyze(a=None):
    import pandas as pd
    h = lock_check(); select(); I2.analyze()       # frozen per-window rule + all cells (item2_table.csv / item2_criterion.csv)
    T = pd.read_csv(SUMM / 'item2_table.csv')
    # Holm over the 45 (layer, edge) loss tests: two-sided bootstrap p from the same team draws as the frozen analysis
    B = A.Boot(); have = [I2.out_path(u) for u in I2.all_units() if I2.out_path(u).exists()]; Z = [np.load(f) for f in have]
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    rid = np.concatenate([z['row_id'] for z in Z]); pid = tk.reindex(rid).to_numpy()
    PM = {c: pd.DataFrame(A.nlr(np.concatenate([z[f'rank_{c}'] for z in Z])), columns=I2.CONFIGS).groupby(pid).mean() for c in A.CONDS}
    S = PM['true'] - sum(PM[c] for c in A.FALSES) / 5; pids = S.index.to_numpy()
    ps = []
    for r in T.itertuples():
        _, b = B.mean(pids, (S['none'] - S[f'{r.edge}@{r.window}']).to_numpy()); b = b[np.isfinite(b)]
        ps.append(float(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))))
    ps = np.array(ps); order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(order): run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
    T['p'] = ps; T['p_holm'] = adj
    T['reading'] = np.where((T.p_holm < 0.05) & (T.loss > 0), 'carries information (loss > 0, Holm)',
                            np.where((T.p_holm < 0.05) & (T.loss < 0), 'reversed (blocking helps, Holm)', 'no detectable loss'))
    T.to_csv(SUMM / 'a32_table.csv', index=False)
    CR = pd.read_csv(SUMM / 'item2_criterion.csv')
    res = dict(addendum_sha256=h, n_shards=len(have), carries=T[T.reading.str.startswith('carries')][['window', 'edge', 'loss', 'share_of_S', 'p_holm']].to_dict(orient='records'),
               reversed=T[T.reading.str.startswith('reversed')][['window', 'edge', 'loss', 'p_holm']].to_dict(orient='records'),
               dominant_edge_rule=CR[['window', 'top_edge', 'verdict']].to_dict(orient='records'))
    json.dump(res, open(SUMM / 'a32_results.json', 'w'), indent=1, default=float)
    print('A32 ANALYSIS', json.dumps({'carries': len(res['carries']), 'reversed': len(res['reversed'])}), flush=True); return res


def tiny(a):
    global RAW, SUMM
    import tempfile, pandas as pd
    root = Path(tempfile.mkdtemp(prefix='a32_tiny_', dir=os.environ.get('TMPDIR', '/tmp'))); RAW, SUMM = root / 'raw', root / 'summary'
    C = A.make_ctx(tiny=True); select()
    sm = A.sample(); I2._SMP['m'] = pd.concat([sm[sm.shard == k].head(2) for k in range(24)])
    ns = argparse.Namespace(shards='0-1', max_minutes=600); I2.work(ns, C=C)
    z = np.load(I2.out_path(('main', 0))); ok = {'46 configs': z['rank_true'].shape[1] == 46 and list(z['configs']) == FIX.configs_for(W_SINGLE),
                                               'blocking changes ranks': bool((z['rank_true'][:, 1:] != z['rank_true'][:, :1]).any())}
    pid0 = A.sample().paper_id.iloc[0]; ai, rids, name = C.ctx[pid0][0]; L = C.layout(pid0, 'true'); T_len = len(L['ids']) + len(name) - 1
    bl = FIX.blocked_layers(FIX.mask_fn_for_fixed, C, T_len, L, len(name) - 1)
    ok['each config blocks exactly its single layer'] = all(v == [int(c.split('@L')[1].split('-')[0])] for c, v in bl.items() if c != 'none') and bl['none'] == []
    mt = I2.out_path(('main', 0)).stat().st_mtime; I2.work(ns, C=C); ok['skip-if-done'] = I2.out_path(('main', 0)).stat().st_mtime == mt
    print('tiny root', root); print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    select()
    if a.cmd == 'remaining':
        mm = [u for u in I2.all_units(a.shards) if not I2.out_path(u).exists()]; print(len(mm), 'missing', [u[1] for u in mm]); return
    {'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
