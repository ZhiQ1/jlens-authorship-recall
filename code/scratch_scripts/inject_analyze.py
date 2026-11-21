#!/usr/bin/env python3
"""Addendum 21 (DRAFT) analysis: primary S_c = rate(own) - rate(mis), G_c = rate(own) - rate(base) in group A, outcome
any_full, 6 cells (L48/L52 x beta 1/2/4); team bootstrap (multinomial over a16 teams, 2,000 draws, seed 21), two-sided
bootstrap p, Holm over the 6 cells separately for S and G; reading per prereg_addendum21_DRAFT.md section 5; secondary
tables (B, A-B, random, fict, first_sur, donor-author writing, fabrication, empty, TF output ranks, dose).
Usage: inject_analyze.py [--raw DIR] [--out DIR] | --synthetic DIR (self-test on simulated data, checks the rule rows)
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

G = Path('/scratch/zhang.zhiqi2/jlens/391_groups'); NB, SEED, ALPHA = 2000, 21, 0.05
LAYERS, BETAS = [48, 52], [1, 2, 4]
CELLS = [(l, b) for l in LAYERS for b in BETAS]


def team_weights(teams, nb=NB, seed=SEED):
    codes, uniq = pd.factorize(pd.Series(teams))
    cnt = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=nb).astype(float)
    return cnt[:, codes]                                   # [nb, n_papers]


def wdiff(x, W):
    """paired mean of x (per paper) and its bootstrap distribution."""
    ok = np.isfinite(x); x = x[ok]; W = W[:, ok]
    return x.mean(), (W @ x) / W.sum(1)


def pval(b): return float(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean())))


def holm(ps):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(order): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    alpha_i = np.empty(m)
    for r, i in enumerate(order): alpha_i[i] = ALPHA / (m - r)
    return adj, alpha_i


def wide(gen, outcome):
    x = gen.pivot_table(index='paper_id', columns='cond', values=outcome, aggfunc='first').astype(float)
    return x


def contrasts(gen, grp, outcome, teams, a_cond, b_cond_of):
    g = gen[gen.grp == grp]; x = wide(g, outcome); W = team_weights(teams.reindex(x.index).to_numpy())
    rows = []
    for l, b in CELLS:
        a = f'{a_cond}_L{l}_b{b}'; c = b_cond_of(l, b)
        if a not in x or c not in x: continue
        est, bs = wdiff((x[a] - x[c]).to_numpy(), W)
        rows.append(dict(grp=grp, outcome=outcome, layer=l, beta=b, contrast=f'{a_cond} - {c.split("_")[0]}', est=est,
                         lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5), p=pval(bs), n=int(np.isfinite((x[a] - x[c]).to_numpy()).sum()), _b=bs))
    return rows


def with_holm(rows):
    if not rows: return rows
    adj, al = holm(np.array([r['p'] for r in rows]))
    for r, p, a in zip(rows, adj, al):
        r['p_holm'] = float(p); r['holm_lo'] = float(np.percentile(r['_b'], 100 * a / 2)); r['holm_hi'] = float(np.percentile(r['_b'], 100 * (1 - a / 2)))
    return rows


def verdict(S, Gr, gen):
    sig = lambda r, lo='holm_lo', hi='holm_hi': r[lo] > 0
    key = lambda r: (r['layer'], r['beta'])
    Sd = {key(r): r for r in S}; Gd = {key(r): r for r in Gr}
    row1 = [c for c in CELLS if c in Sd and c in Gd and Sd[c]['holm_lo'] > 0 and Gd[c]['holm_lo'] > 0]
    row1_unadj = [c for c in CELLS if c in Sd and c in Gd and Sd[c]['lo'] > 0 and Gd[c]['lo'] > 0]
    anyG = [c for c in CELLS if c in Gd and Gd[c]['holm_lo'] > 0]
    harm = all(Gd[c]['holm_hi'] < 0 for c in CELLS if c in Gd and c[1] >= 2) and not anyG
    if row1:
        best = max(row1, key=lambda c: Gd[c]['est'])
        v = 'Supported: sufficiency, paper-specific (' + ('substantial' if Gd[best]['est'] >= 0.05 else 'small') + ')'
        a = gen[gen.grp == 'A']; base = a[a.cond == 'base']; cell = a[a.cond == f'own_L{best[0]}_b{best[1]}']
        dmg = (cell.n_items.eq(0).mean() - base.n_items.eq(0).mean() > 0.20) or (cell.n_fab_full.mean() - base.n_fab_full.mean() > 0.20)
        if dmg: v += ' — with output damage'
    elif harm: v, best = 'Harmful (reversed): amplifying the arrived information breaks the answer', None
    elif anyG: v, best = 'Generic boost, not paper-specific', max(anyG, key=lambda c: Gd[c]['est'])
    else: v, best = 'Not supported', None
    border = bool(row1_unadj and not row1)
    return dict(verdict=v, cells_row1=row1, cells_row1_unadjusted=row1_unadj, borderline=border, best_cell=best)


def analyze(raw, out):
    gen = pd.concat([pd.read_parquet(f) for f in sorted((raw / 'gen').glob('shard_*.parquet'))])
    fr = pd.read_parquet(Path(str(raw) + '_freeze') / 'freeze.parquet') if (Path(str(raw) + '_freeze') / 'freeze.parquet').exists() else None
    teams = (fr.set_index('paper_id').team if fr is not None else gen.groupby('paper_id').paper_id.first().map(hash))
    gen['empty'] = gen.n_items.eq(0).astype(float)
    S = with_holm(contrasts(gen, 'A', 'any_full', teams, 'own', lambda l, b: f'mis_L{l}_b{b}'))
    Gr = with_holm(contrasts(gen, 'A', 'any_full', teams, 'own', lambda l, b: 'base'))
    V = verdict(S, Gr, gen)
    sec = []
    for grp in ('A', 'B'):
        for oc in ('any_full', 'first_sur', 'any_sur', 'c_any_full', 'n_fab_full', 'empty'):
            for src, ref in (('own', 'base'), ('own', 'mis'), ('own', 'rand'), ('own', 'fict'), ('mis', 'base'), ('rand', 'base')):
                f = (lambda l, b: 'base') if ref == 'base' else (lambda l, b, ref=ref: f'{ref}_L{l}_b{b}')
                if grp == 'A' and oc == 'any_full' and src == 'own' and ref in ('base', 'mis'): continue
                sec += contrasts(gen, grp, oc, teams, src, f)
    # A - B of G_c
    for l, b in CELLS:
        x = wide(gen, 'any_full'); a = f'own_L{l}_b{b}'
        if a not in x: continue
        g = (x[a] - x['base']); grp = gen.groupby('paper_id').grp.first().reindex(x.index)
        W = team_weights(teams.reindex(x.index).to_numpy()); v = g.to_numpy()
        ia, ib = (grp == 'A').to_numpy(), (grp == 'B').to_numpy()
        ba = (W[:, ia] @ v[ia]) / W[:, ia].sum(1); bb = (W[:, ib] @ v[ib]) / W[:, ib].sum(1); d = ba - bb
        sec.append(dict(grp='A-B', outcome='any_full', layer=l, beta=b, contrast='G (own - base)', est=v[ia].mean() - v[ib].mean(),
                        lo=np.percentile(d, 2.5), hi=np.percentile(d, 97.5), p=pval(d), n=int(ia.sum() + ib.sum())))
    rates = gen.groupby(['grp', 'cond'])[['any_full', 'first_sur', 'any_sur', 'c_any_full', 'n_fab_full', 'empty']].mean().reset_index()
    tf_rows = []
    tfs = sorted((raw / 'tf').glob('shard_*.parquet'))
    if tfs:
        tf = pd.concat([pd.read_parquet(f) for f in tfs]); tf['nlr'] = -np.log10(tf['rank'].astype(float))
        pp = tf.groupby(['paper_id', 'grp', 'cond']).nlr.mean().unstack('cond')
        for grp in ('A', 'B'):
            x = pp.xs(grp, level='grp'); W = team_weights(teams.reindex(x.index).to_numpy())
            for l, b in CELLS:
                for ref in ('base', 'mis'):
                    a = f'own_L{l}_b{b}'; c = 'base' if ref == 'base' else f'mis_L{l}_b{b}'
                    if a not in x or c not in x: continue
                    est, bs = wdiff((x[a] - x[c]).to_numpy(), W)
                    tf_rows.append(dict(grp=grp, layer=l, beta=b, contrast=f'own - {ref}', est=est, lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5)))
    out.mkdir(parents=True, exist_ok=True)
    clean = lambda rows: pd.DataFrame([{k: v for k, v in r.items() if k != '_b'} for r in rows])
    P = pd.concat([clean(S).assign(role='primary S'), clean(Gr).assign(role='primary G')]); P.to_csv(out / 'primary.csv', index=False)
    clean(sec).to_csv(out / 'secondary.csv', index=False); rates.to_csv(out / 'rates.csv', index=False); pd.DataFrame(tf_rows).to_csv(out / 'tf.csv', index=False)
    res = dict(label='addendum 21 (DRAFT rule)', n_papers=gen.paper_id.nunique(), by_grp=gen.groupby('grp').paper_id.nunique().to_dict(), **V)
    json.dump(res, open(out / 'a21_results.json', 'w'), indent=1, default=str)
    print(json.dumps(res, default=str)); print(P[['role', 'layer', 'beta', 'est', 'lo', 'hi', 'p_holm', 'holm_lo', 'holm_hi']].to_string(index=False))
    return res


def synthetic(root):
    """simulate three worlds and check that the rule returns the intended row."""
    rng = np.random.default_rng(0); ok = {}
    for world, eff_own, eff_mis in (('supported', .12, .0), ('generic', .10, .10), ('null', 0, 0)):
        rows = []
        for i in range(1200):
            grp = 'A' if i < 600 else 'B'; base = rng.random() < .04
            for cond in ['base'] + [f'{s}_L{l}_b{b}' for l, b in CELLS for s in ('own', 'mis', 'rand')]:
                p = .04 + (eff_own if cond.startswith('own') else eff_mis if cond.startswith('mis') else 0) * (grp == 'A')
                v = base if cond == 'base' else rng.random() < p
                rows.append(dict(paper_id=f'p{i}', grp=grp, cond=cond, any_full=v, first_sur=v, any_sur=v, c_any_full=False, n_fab_full=2, n_items=3))
        d = Path(root) / world / 'gen'; d.mkdir(parents=True, exist_ok=True); pd.DataFrame(rows).to_parquet(d / 'shard_000.parquet')
        r = analyze(Path(root) / world, Path(root) / world / 'summary')
        ok[world] = r['verdict']
    exp = dict(supported='Supported', generic='Generic', null='Not supported')
    good = all(ok[w].startswith(exp[w]) for w in exp)
    print('SYNTHETIC', json.dumps(ok), 'PASS' if good else 'FAIL'); return good


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--raw', default=str(G / 'raw/a21')); ap.add_argument('--out', default=str(G / 'summary_a21'))
    ap.add_argument('--synthetic'); a = ap.parse_args()
    if a.synthetic: sys.exit(0 if synthetic(a.synthetic) else 1)
    analyze(Path(a.raw), Path(a.out))
