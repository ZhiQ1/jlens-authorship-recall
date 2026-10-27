"""Stage 11 analysis (CPU): E1 patching recovery, E2 knockout loss, E3 author chain vs isolated scoring.
Per token nlr = log10(1/rank); paper means; 95% bootstrap CIs over papers (B = 2000). Writes summary/*.csv and
reports/stage11_report.md under the Stage 11 root."""
import json
from pathlib import Path
import numpy as np, pandas as pd

B = 2000
rng = np.random.default_rng(3611)


def nlr(r): return -np.log10(np.asarray(r, float))


def boot_mean(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]
    mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1); return v.mean(), *np.percentile(mm, [2.5, 97.5]), len(v)


def boot_ratio(num, den):
    """mean(num)/mean(den) over papers, bootstrap of papers (paired)."""
    num, den = np.asarray(num, float), np.asarray(den, float); n = len(num); ix = rng.integers(0, n, (B, n))
    r = num[ix].mean(1) / den[ix].mean(1); return num.mean() / den.mean(), *np.percentile(r, [2.5, 97.5]), n


def boot_ratio_diff(na, da, nb, db):
    ia = rng.integers(0, len(na), (B, len(na))); ib = rng.integers(0, len(nb), (B, len(nb)))
    d = na[ia].mean(1) / da[ia].mean(1) - nb[ib].mean(1) / db[ib].mean(1)
    return na.mean() / da.mean() - nb.mean() / db.mean(), *np.percentile(d, [2.5, 97.5])


def strat_diff(df, col, min_n=30):
    """target - control of df[col] pooled within citation bin (weights n_t n_c / (n_t + n_c))."""
    cells = []
    for b, g in df.groupby('citation_bin'):
        A = g[g.group == 'target'][col].dropna().to_numpy(); C = g[g.group == 'control'][col].dropna().to_numpy()
        if len(A) >= min_n and len(C) >= min_n: cells.append((A, C))
    w = np.array([len(A) * len(C) / (len(A) + len(C)) for A, C in cells]); w /= w.sum()
    est = sum(wi * (A.mean() - C.mean()) for wi, (A, C) in zip(w, cells))
    bt = sum(wi * (A[rng.integers(0, len(A), (B, len(A)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A, C) in zip(w, cells))
    return est, *np.percentile(bt, [2.5, 97.5])


def load_unit_dir(d):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
    return {k: np.concatenate([z[k] for z in zs]) for k in zs[0].files if k not in ('meta', 'layers')}, (zs[0]['layers'] if 'layers' in zs[0].files else None)


def fmt(v, lo, hi): return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def main(ROOT, R10, s10):
    S = ROOT / 'summary'; S.mkdir(exist_ok=True); (ROOT / 'reports').mkdir(exist_ok=True)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'shard'])
    smp = pd.read_parquet(ROOT / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    L = ['# Stage 11 - causal and context follow-ups', '', f'Sample for E1/E2: {len(smp)} papers ({(smp.group == "target").sum()} target, {(smp.group == "control").sum()} control), balanced within citation bin.', '']

    # ---------------- E1 patching
    d, layers = load_unit_dir(ROOT / 'raw/patch')
    t = toks.set_index('row_id').loc[d['row_id']].reset_index()
    df = pd.DataFrame({'paper_id': t.paper_id, 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])})
    for i, l in enumerate(layers): df[f'p{l}'] = nlr(d['rank_patch'][:, i])
    pp = df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    rows = []
    for g in ['target', 'control', 'all']:
        s = pp if g == 'all' else pp[pp.group == g]
        den = (s['true'] - s['false']).to_numpy()
        for l in layers:
            num = (s[f'p{l}'] - s['false']).to_numpy(); r = boot_ratio(num, den); dm = boot_mean(num)
            rows.append(dict(group=g, layer=int(l), n_papers=r[3], recovery=r[0], rec_lo=r[1], rec_hi=r[2], gain=dm[0], gain_lo=dm[1], gain_hi=dm[2],
                             true_minus_false=den.mean()))
    e1 = pd.DataFrame(rows)
    td = []
    for l in layers:
        a = pp[pp.group == 'target']; c = pp[pp.group == 'control']
        r = boot_ratio_diff((a[f'p{l}'] - a['false']).to_numpy(), (a['true'] - a['false']).to_numpy(), (c[f'p{l}'] - c['false']).to_numpy(), (c['true'] - c['false']).to_numpy())
        pp[f'g{l}'] = pp[f'p{l}'] - pp['false']; gd = strat_diff(pp, f'g{l}')
        td.append(dict(layer=int(l), recovery_tc=r[0], lo=r[1], hi=r[2], gain_tc=gd[0], gain_lo=gd[1], gain_hi=gd[2]))
    e1tc = pd.DataFrame(td); e1.to_csv(S / 'E1_recovery.csv', index=False); e1tc.to_csv(S / 'E1_target_minus_control.csv', index=False)
    L += ['## E1. Activation patching (true -> false_0 title, aligned tail, one layer at a time)', '',
          'recovery = mean(patched - false) / mean(true - false) at the model output; 1 = fully rescued.', '',
          '| layer | target | control | all | target - control (recovery) | target - control (gain, within bin) |', '|---|---|---|---|---|---|']
    for l in layers:
        f = lambda g: e1[(e1.group == g) & (e1.layer == l)].iloc[0]
        x = e1tc[e1tc.layer == l].iloc[0]
        L.append(f'| L{l} | ' + ' | '.join(fmt(f(g).recovery, f(g).rec_lo, f(g).rec_hi) for g in ['target', 'control', 'all']) + f' | {fmt(x.recovery_tc, x.lo, x.hi)} | {fmt(x.gain_tc, x.gain_lo, x.gain_hi)} |')
    L += ['', f'true - false (denominator): target {e1[e1.group == "target"].true_minus_false.iloc[0]:.3f}, control {e1[e1.group == "control"].true_minus_false.iloc[0]:.3f}.', '']

    # ---------------- E2 knockout
    k, kl = load_unit_dir(ROOT / 'raw/knockout')
    t = toks.set_index('row_id').loc[k['row_id']].reset_index()
    kd = pd.DataFrame({'row_id': k['row_id'], 'paper_id': t.paper_id})
    for i, l in enumerate(kl): kd[f'k{l}'] = nlr(k['rank_ko'][:, i])
    kd = kd.merge(pd.DataFrame({'row_id': d['row_id'], 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])}), on='row_id')
    kp = kd.drop(columns='row_id').groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    rows = []
    for g in ['target', 'control', 'all']:
        s = kp if g == 'all' else kp[kp.group == g]; den = (s['true'] - s['false']).to_numpy()
        for l in kl:
            if l == 64: continue
            num = (s['k64'] - s[f'k{l}']).to_numpy(); r = boot_ratio(num, den); dm = boot_mean(num)
            rows.append(dict(group=g, start_layer=int(l), n_papers=r[3], loss_fraction=r[0], lo=r[1], hi=r[2], drop=dm[0], drop_lo=dm[1], drop_hi=dm[2]))
    e2 = pd.DataFrame(rows); e2.to_csv(S / 'E2_knockout.csv', index=False)
    td = []
    for l in kl:
        if l == 64: continue
        a = kp[kp.group == 'target']; c = kp[kp.group == 'control']
        r = boot_ratio_diff((a['k64'] - a[f'k{l}']).to_numpy(), (a['true'] - a['false']).to_numpy(), (c['k64'] - c[f'k{l}']).to_numpy(), (c['true'] - c['false']).to_numpy())
        td.append(dict(start_layer=int(l), loss_tc=r[0], lo=r[1], hi=r[2]))
    e2tc = pd.DataFrame(td); e2tc.to_csv(S / 'E2_target_minus_control.csv', index=False)
    L += ['## E2. Attention knockout of the title tokens from layer l to the end (true title)', '',
          'loss = mean(baseline - knocked) / mean(true - false_0); 1 = all title-specific signal lost.', '',
          '| from layer | target | control | all | target - control |', '|---|---|---|---|---|']
    for l in kl:
        if l == 64: continue
        f = lambda g: e2[(e2.group == g) & (e2.start_layer == l)].iloc[0]; x = e2tc[e2tc.start_layer == l].iloc[0]
        L.append(f'| L{l} | ' + ' | '.join(fmt(f(g).loss_fraction, f(g).lo, f(g).hi) for g in ['target', 'control', 'all']) + f' | {fmt(x.loss_tc, x.lo, x.hi)} |')
    L.append('')

    # ---------------- E3 chain vs isolated
    m, _ = s10.verify(R10)
    recs = [(cond, load_unit_dir(ROOT / 'raw/chain' / cond)[0]) for cond in s10.condition_names()]
    # isolated Stage 10 ranks for the same rows, per readout/layer
    keys = [k for k in recs[0][1] if '@' in k]
    out = []
    for cond, c in recs:
        for key in keys:
            r, l = key.split('@'); l = int(l)
            zs = [np.load(s10.out_file(R10, r, l, sh, cond)) for sh in range(m['n_shards'])]
            ref = pd.Series(np.concatenate([z['rank'] for z in zs]), index=np.concatenate([z['row_id'] for z in zs]))
            out.append(pd.DataFrame({'row_id': c['row_id'], 'chain_index': c['chain_index'], 'cond': cond, 'readout': r, 'layer': l,
                                     'chain': nlr(c[key]), 'iso': nlr(ref.loc[c['row_id']].to_numpy())}))
    ch = pd.concat(out).merge(toks[['row_id', 'paper_id']], on='row_id').merge(papers.rename(columns={'group_tight': 'group'}), on='paper_id')
    ch['pos'] = np.minimum(ch.chain_index, 3)
    pm = ch.groupby(['paper_id', 'group', 'citation_bin', 'readout', 'layer', 'pos', 'cond'])[['chain', 'iso']].mean().reset_index()
    wide = pm.pivot_table(index=['paper_id', 'group', 'citation_bin', 'readout', 'layer', 'pos'], columns='cond', values=['chain', 'iso']).reset_index()
    fk = [f'false_{i}' for i in range(5)]
    wide.columns = [c if isinstance(c, str) else (c[0] if c[1] == '' else f'{c[0]}__{c[1]}') for c in wide.columns]
    for v in ('chain', 'iso'):
        wide[f'{v}_true'] = wide[f'{v}__true']; wide[f'{v}_spec'] = wide[f'{v}__true'] - wide[[f'{v}__{f}' for f in fk]].mean(1)
    wide['gain_true'] = wide.chain_true - wide.iso_true; wide['gain_spec'] = wide.chain_spec - wide.iso_spec
    rows = []
    for (r, l, pos), s in wide.groupby(['readout', 'layer', 'pos']):
        for g in ['target', 'control', 'all']:
            ss = s if g == 'all' else s[s.group == g]
            row = dict(readout=r, layer=l, author_pos=int(pos) + 1, group=g, n_papers=len(ss))
            for mt in ['chain_true', 'iso_true', 'gain_true', 'chain_spec', 'iso_spec', 'gain_spec']:
                v = boot_mean(ss[mt]); row |= {mt: v[0], f'{mt}_lo': v[1], f'{mt}_hi': v[2]}
            rows.append(row)
        row = dict(readout=r, layer=l, author_pos=int(pos) + 1, group='target-control', n_papers=len(s))
        for mt in ['chain_spec', 'iso_spec', 'gain_spec']:
            e = strat_diff(s, mt); row |= {mt: e[0], f'{mt}_lo': e[1], f'{mt}_hi': e[2]}
        rows.append(row)
    e3 = pd.DataFrame(rows); e3.to_csv(S / 'E3_chain.csv', index=False)
    L += ['## E3. Author chain ("Authors: A1, A2, ...") vs Stage 10 isolated scoring, model output', '',
          'gain = chain - isolated on the same tokens; spec = true title - mean(5 false titles). Author position 4 = 4th and later.', '',
          '| author | group | chain (true) | isolated (true) | gain (true) | spec chain | spec isolated | gain in spec |', '|---|---|---|---|---|---|---|---|']
    f3 = e3[(e3.readout == 'final')]
    for pos in sorted(f3.author_pos.unique()):
        for g in ['target', 'control']:
            x = f3[(f3.author_pos == pos) & (f3.group == g)].iloc[0]
            L.append(f'| {pos} | {g} | ' + ' | '.join(fmt(x[m_], x[m_ + "_lo"], x[m_ + "_hi"]) for m_ in ['chain_true', 'iso_true', 'gain_true', 'chain_spec', 'iso_spec', 'gain_spec']) + ' |')
        x = f3[(f3.author_pos == pos) & (f3.group == 'target-control')].iloc[0]
        L.append(f'| {pos} | target - control (within bin) | | | | {fmt(x.chain_spec, x.chain_spec_lo, x.chain_spec_hi)} | {fmt(x.iso_spec, x.iso_spec_lo, x.iso_spec_hi)} | {fmt(x.gain_spec, x.gain_spec_lo, x.gain_spec_hi)} |')
    L += ['', 'Files: summary/E1_recovery.csv, E1_target_minus_control.csv, E2_knockout.csv, E2_target_minus_control.csv, E3_chain.csv (all readouts and layers).']
    (ROOT / 'reports/stage11_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('STAGE11 ANALYZED')
