#!/usr/bin/env python3
"""Exploratory (post hoc, 2026-11-22): addendum 25 'unlock' vs 'write channel'. CPU, stored a25 outputs only.

(1) gain of the gold-author probe direction over base and over the mismatched-author direction, A vs B, per cell
    (L48/L52 x beta 1/2/4), outcomes any_full and first_sur (a16 matcher, stored), A - B with team CIs.
(2) symmetric write test: P(gold surname written | gold dir) - P(gold | base) vs P(donor surname written | donor dir)
    - P(donor | base), in A and B. 'written' = the surname appears as a word in the generated answer text (same rule for
    gold and donor). donor = the author whose surname-first token was used for the mismatched direction (a25 tokens_for:
    first donor-paper surname-first token != the gold token).
(3) teacher forcing: stored TF scores only the paper's TRUE authors, so the donor's rank under the donor direction is not
    available (reported as such).
Team bootstrap 2,000 (multinomial over a21-freeze teams), seed 2511. Usage: a25_unlock.py [--tiny]
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

G = Path('/scratch/zhang.zhiqi2/jlens/391_groups'); R10 = Path('/scratch/zhang.zhiqi2/jlens/351_stage10')
OUT = G / 'summary_a25_unlock'; NB = 2000; LAYERS, BETAS = [48, 52], [1, 2, 4]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def _tab(df):
    try: return df.to_markdown(index=False, floatfmt='+.3f')
    except Exception: return df.round(3).to_string(index=False)


def main(a):
    a16 = load(Path.home() / 'jlens_work/14_groups/prereg16_a16.py', 'a16_ro')
    out = OUT / ('tiny' if a.tiny else ''); out.mkdir(parents=True, exist_ok=True)
    fs = sorted((G / 'raw/a25/gen').glob('shard_*.parquet'))[: (2 if a.tiny else None)]
    gen = pd.concat([pd.read_parquet(f, columns=['paper_id', 'grp', 'cond', 'text', 'any_full', 'first_sur']) for f in fs])
    D = pd.read_parquet(G / 'raw/a21_freeze/freeze.parquet').set_index('paper_id')
    P = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'authors']).set_index('paper_id').authors
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'role', 'token_id'])
    sf = toks[toks.role == 'surname_first'].sort_values(['paper_id', 'author_index'])
    first = {p: list(zip(g.author_index, g.token_id)) for p, g in sf.groupby('paper_id')}
    sur = lambda name: (a16.words(name) or [''])[-1]
    rows = []
    for p in gen.paper_id.unique():
        if p not in D.index: continue
        donor = D.loc[p, 'donor_id']; g = first.get(p, []); d = first.get(donor, [])
        if not g or not d: continue
        alt = [(ai, t) for ai, t in d if t != g[0][1]]
        if not alt: continue
        ga = a16.authors_of(P[p]); da = a16.authors_of(P[donor])
        gs, ds = sur(ga[g[0][0]]), sur(da[alt[0][0]])
        if not gs or not ds or gs == ds: continue
        rows.append(dict(paper_id=p, gold_sur=gs, donor_sur=ds, team=int(D.loc[p, 'team'])))
    M = pd.DataFrame(rows).set_index('paper_id')
    gen = gen[gen.paper_id.isin(M.index)].copy()
    W = gen.text.fillna('').map(lambda t: set(a16.words(t)))
    gen['w_gold'] = [M.loc[p, 'gold_sur'] in w for p, w in zip(gen.paper_id, W)]
    gen['w_donor'] = [M.loc[p, 'donor_sur'] in w for p, w in zip(gen.paper_id, W)]
    wide = {o: gen.pivot_table(index='paper_id', columns='cond', values=o, aggfunc='first').astype(float) for o in ('any_full', 'first_sur', 'w_gold', 'w_donor')}
    grp = gen.groupby('paper_id').grp.first()
    pids = wide['any_full'].index; codes, uniq = pd.factorize(M.loc[pids, 'team'])
    Wt = np.random.default_rng(2511).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    gA = (grp.reindex(pids) == 'A').to_numpy(); gB = ~gA

    def stat(x, mask):
        ok = mask & np.isfinite(x); est = x[ok].mean(); b = (Wt[:, ok] @ x[ok]) / Wt[:, ok].sum(1)
        return est, b

    def ci(b): return np.percentile(b, 2.5), np.percentile(b, 97.5)
    R = []
    for l in LAYERS:
        for be in BETAS:
            c = f'L{l}_b{be}'
            items = {}
            for o in ('any_full', 'first_sur'):
                w = wide[o]
                items[f'{o}: gold - base'] = (w[f'gold_{c}'] - w['base']).to_numpy()
                items[f'{o}: gold - mis'] = (w[f'gold_{c}'] - w[f'mis_{c}']).to_numpy()
            items['write gold: gold dir - base'] = (wide['w_gold'][f'gold_{c}'] - wide['w_gold']['base']).to_numpy()
            items['write donor: donor dir - base'] = (wide['w_donor'][f'mis_{c}'] - wide['w_donor']['base']).to_numpy()
            items['write donor: donor dir - rand'] = (wide['w_donor'][f'mis_{c}'] - wide['w_donor'][f'rand_{c}']).to_numpy()
            items['write donor: donor dir - gold dir'] = (wide['w_donor'][f'mis_{c}'] - wide['w_donor'][f'gold_{c}']).to_numpy()
            items['symmetry: (gold dir - base)[gold] - (donor dir - base)[donor]'] = items['write gold: gold dir - base'] - items['write donor: donor dir - base']
            for name, x in items.items():
                eA, bA = stat(x, gA); eB, bB = stat(x, gB)
                R.append(dict(layer=l, beta=be, quantity=name, A=eA, A_lo=ci(bA)[0], A_hi=ci(bA)[1], B=eB, B_lo=ci(bB)[0], B_hi=ci(bB)[1],
                              A_minus_B=eA - eB, AmB_lo=ci(bA - bB)[0], AmB_hi=ci(bA - bB)[1]))
    T = pd.DataFrame(R); T.to_csv(out / 'unlock_table.csv', index=False)
    base = {g: {o: float(np.nanmean(wide[o]['base'].to_numpy()[m])) for o in ('w_gold', 'w_donor', 'any_full', 'first_sur')} for g, m in (('A', gA), ('B', gB))}
    info = dict(label='exploratory (post hoc)', n_A=int(gA.sum()), n_B=int(gB.sum()), base_rates=base,
                tf_note='stored TF scores only the true authors; donor-name rank under the donor direction is not available',
                offdist_note='beta 4 is outside the natural norm range at L48/L52 (23_methods/a25_offdist_check.json); beta 1-2 within')
    json.dump(info, open(out / 'unlock_info.json', 'w'), indent=1)
    keyq = ['first_sur: gold - base', 'first_sur: gold - mis', 'any_full: gold - base', 'write gold: gold dir - base', 'write donor: donor dir - base',
            'symmetry: (gold dir - base)[gold] - (donor dir - base)[donor]']
    lines = ['# addendum 25: unlock vs write channel (exploratory, post hoc)', '', json.dumps(info), '']
    for q in keyq:
        lines += [f'## {q}', '', _tab(T[T.quantity == q].drop(columns='quantity')), '']
    (out / 'report.md').write_text('\n'.join(lines))
    print('\n'.join(lines)[:6000])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--tiny', action='store_true'); main(ap.parse_args())
