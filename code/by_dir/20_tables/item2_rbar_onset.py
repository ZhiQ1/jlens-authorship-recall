#!/usr/bin/env python3
"""Exploratory (post hoc), 2026-11-22. Item 2: at which layer the real-title-only part R = S_true - S_fict forms.
Reuses the locked addendum-20 analysis code (15_h2fict/h2_main_analyze.py, imported read-only) and its stored outputs
(raw/a20v2_score, a20v2_patch; Stage 10 / Stage 11 stored raw). No forward pass.
(a) name-position readouts (logit, jlens_public at L24/32/40/48/56/62; final L63): Rbar per group (from the a20 code path)
    and within-bin target - control of R (Engine.within_bin, weights n_t n_c/(n_t+n_c)), team bootstrap 2,000, seed 20261120.
(b) E1 tail patching with the fictitious title as donor (L24..L63): d(l) = rec_true(l) - rec_fict(l) per group and plain
    target - control of d on the same team draws.
Onset rule: first measured layer whose CI lower bound > 0 and stays > 0 at every later measured layer.
--tiny: restrict to 2 shards (test).
"""
import argparse, importlib.util, sys
from pathlib import Path
import numpy as np, pandas as pd
H = Path.home() / 'jlens_work'
sp = importlib.util.spec_from_file_location('a20', H / '15_h2fict/h2_main_analyze.py'); a20 = importlib.util.module_from_spec(sp); sys.modules['a20'] = a20; sp.loader.exec_module(a20)
OUT = Path('/scratch/zhang.zhiqi2/jlens/391_groups/summary_tables_20261122/item2')

def onset(df, layer_col, lo_col):
    d = df.sort_values(layer_col); L = d[layer_col].to_list(); lo = d[lo_col].to_numpy()
    for i in range(len(L)):
        if np.all(lo[i:] > 0): return int(L[i])
    return None

def md(df, floatfmt='.4f'):
    cols=list(df.columns); f=lambda v: (format(v, floatfmt) if isinstance(v, float) else str(v))
    return '\n'.join(['| '+' | '.join(map(str,cols))+' |','|'+'---|'*len(cols)]+['| '+' | '.join(f(v) for v in r)+' |' for r in df.itertuples(index=False)])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    out = OUT / ('tiny' if a.tiny else ''); out.mkdir(parents=True, exist_ok=True)
    F = pd.read_parquet(a20.FREEZE / 'fict_titles.parquet')
    if a.tiny: F = F[F.shard.isin(sorted(F.shard.unique())[:2])]
    tok = a20.token_table(F); shards = sorted(F.shard.unique()); raw = a20.G391 / 'raw'
    SC = a20.load_units(raw, 'score', shards); PT = a20.load_units(raw, 'patch', shards)
    s10 = a20.load_stage10(tok.index.to_numpy())
    T = F[F.group == 'target'].paper_id.to_numpy(); C = F[F.group == 'control'].paper_id.to_numpy()
    BT = a20.Boot(); rows = []
    for r, l in a20.PAIRS:
        fict = pd.concat([pd.Series(z[f'rank@{r}@{l}'], index=z['row_id']) for z in SC.values()])
        d = pd.DataFrame({c: a20.paper_means(tok, s10[(c, r, l)]) for c in a20.CONDS}); d['fict'] = a20.paper_means(tok, fict)
        d = d.reindex(F.paper_id); D = pd.DataFrame(dict(R=d.true - d.fict))
        for grp, ids in (('target', T), ('control', C)):
            v = D.loc[ids, 'R'].dropna(); e, b = BT.mean(v.index.to_numpy(), v.to_numpy()); lo, hi = BT.ci(b)
            rows.append(dict(readout=r, layer=l, quantity='Rbar', set=grp, est=e, lo=lo, hi=hi, n=len(v)))
        e, lo, hi, nt, nc = a20.within_bin_tc(BT, D, F, 'R')
        rows.append(dict(readout=r, layer=l, quantity='Rbar', set='T-C within bin', est=e, lo=lo, hi=hi, n=nt + nc))
    A = pd.DataFrame(rows); A.to_csv(out / 'rbar_by_layer.csv', index=False)
    # (b) E1 fict donor
    pz = PT; nl = a20.nl; PL = a20.PATCH_LAYERS
    rowid = np.concatenate([z['row_id'] for z in pz.values()]); rp = np.concatenate([z['rank_patch'] for z in pz.values()])
    rfl = np.concatenate([z['rank_false'] for z in pz.values()])
    s11 = [np.load(a20.R11 / f'raw/patch/shard_{k:03d}.npz') for k in pz]
    st = pd.DataFrame(dict(row_id=np.concatenate([z['row_id'] for z in s11]), t=nl(np.concatenate([z['rank_true'] for z in s11])), f=nl(np.concatenate([z['rank_false'] for z in s11])))).set_index('row_id')
    st_p = pd.DataFrame(nl(np.concatenate([z['rank_patch'] for z in s11])), index=st.index, columns=[f'tp{l}' for l in PL])
    dd = pd.DataFrame(nl(rp), index=rowid, columns=[f'p{l}' for l in PL]); dd['fx'] = nl(rfl)
    dd = dd.join(st).join(st_p); dd['paper_id'] = tok.paper_id.reindex(dd.index).to_numpy(); pm = dd.groupby('paper_id').mean()
    rows, keepb = [], {}
    for grp, ids in (('target', T), ('control', C)):
        q = pm.reindex([p for p in ids if p in pm.index]); W = BT.W(q.index.to_numpy()); den = (q.t - q.f).to_numpy()
        for l in PL:
            num = (q[f'p{l}'] - q.fx).to_numpy(); numt = (q[f'tp{l}'] - q.f).to_numpy()
            dif = numt.mean() / den.mean() - num.mean() / den.mean(); b = (W @ numt) / (W @ den) - (W @ num) / (W @ den)
            keepb[(grp, l)] = b; lo, hi = BT.ci(b); rows.append(dict(layer=l, set=grp, quantity='rec_true - rec_fict', est=dif, lo=lo, hi=hi, n=len(q)))
    for l in PL:
        e = [r['est'] for r in rows if r['layer'] == l and r['set'] == 'target'][0] - [r['est'] for r in rows if r['layer'] == l and r['set'] == 'control'][0]
        b = keepb[('target', l)] - keepb[('control', l)]; lo, hi = BT.ci(b)
        rows.append(dict(layer=l, set='T-C plain', quantity='rec_true - rec_fict', est=e, lo=lo, hi=hi, n=None))
    B = pd.DataFrame(rows); B.to_csv(out / 'e1_fict_gap_by_layer.csv', index=False)
    on = []
    for (r, s), g in A.groupby(['readout', 'set']):
        if r != 'final': on.append(dict(source=f'{r} Rbar', set=s, onset_layer=onset(g, 'layer', 'lo')))
    for s, g in B.groupby('set'): on.append(dict(source='E1 rec_true - rec_fict', set=s, onset_layer=onset(g, 'layer', 'lo')))
    O = pd.DataFrame(on); O.to_csv(out / 'onset.csv', index=False)
    rep = ['# Item 2 — where the real-title-only part forms (exploratory, post hoc, stored data only)', '', md(O), '',
           '## Rbar by layer', md(A, '.4f'), '', '## E1 rec_true - rec_fict by layer', md(B, '.4f')]
    (out / 'report.md').write_text('\n'.join(rep) + '\n'); print(O.to_string()); print('DONE', out)

if __name__ == '__main__': main()
