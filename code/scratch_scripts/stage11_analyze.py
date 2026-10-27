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


def patch_section(name, title, d, layers, toks, smp, S):
    t = toks.set_index('row_id').loc[d['row_id']].reset_index()
    df = pd.DataFrame({'paper_id': t.paper_id, 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])})
    for i, l in enumerate(layers): df[f'p{l}'] = nlr(d['rank_patch'][:, i])
    if name == 'E1t' and 63 in list(layers):
        # 2026-10-27 GPU smoke: the batched patched forward rounds differently from the batch-1 false run (L63 element
        # matched the false run on 70% of ranks, mean |dlog10 rank| ~0.01). The L63 element of the SAME batch is an
        # unpatched false run (nothing downstream of block 63 at the title position), so it is the baseline here.
        df['false_batch1'] = df['false']; df['false'] = df['p63']
    pp = df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    rows, td = [], []
    for g in ['target', 'control', 'all']:
        s = pp if g == 'all' else pp[pp.group == g]; den = (s['true'] - s['false']).to_numpy()
        for l in layers:
            num = (s[f'p{l}'] - s['false']).to_numpy(); r = boot_ratio(num, den); dm = boot_mean(num)
            rows.append(dict(group=g, layer=int(l), n_papers=r[3], recovery=r[0], rec_lo=r[1], rec_hi=r[2], gain=dm[0], gain_lo=dm[1], gain_hi=dm[2], true_minus_false=den.mean()))
    e = pd.DataFrame(rows)
    for l in layers:
        a = pp[pp.group == 'target']; c = pp[pp.group == 'control']
        r = boot_ratio_diff((a[f'p{l}'] - a['false']).to_numpy(), (a['true'] - a['false']).to_numpy(), (c[f'p{l}'] - c['false']).to_numpy(), (c['true'] - c['false']).to_numpy())
        pp[f'g{l}'] = pp[f'p{l}'] - pp['false']; gd = strat_diff(pp, f'g{l}')
        td.append(dict(layer=int(l), recovery_tc=r[0], lo=r[1], hi=r[2], gain_tc=gd[0], gain_lo=gd[1], gain_hi=gd[2]))
    etc = pd.DataFrame(td); e.to_csv(S / f'{name}_recovery.csv', index=False); etc.to_csv(S / f'{name}_target_minus_control.csv', index=False)
    L = [f'## {name}. {title}', '', 'recovery = mean(patched - false) / mean(true - false) at the model output; 1 = fully rescued, 0 = nothing.', '',
         '| layer | target | control | all | target - control (recovery) | target - control (gain, within bin) |', '|---|---|---|---|---|---|']
    for l in layers:
        f = lambda g: e[(e.group == g) & (e.layer == l)].iloc[0]; x = etc[etc.layer == l].iloc[0]
        L.append(f'| L{l} | ' + ' | '.join(fmt(f(g).recovery, f(g).rec_lo, f(g).rec_hi) for g in ['target', 'control', 'all']) + f' | {fmt(x.recovery_tc, x.lo, x.hi)} | {fmt(x.gain_tc, x.gain_lo, x.gain_hi)} |')
    return L + ['', f'true - false (denominator): target {e[e.group == "target"].true_minus_false.iloc[0]:.3f}, control {e[e.group == "control"].true_minus_false.iloc[0]:.3f}.', '']


def ko_section(name, title, k, kl, d, toks, smp, S):
    t = toks.set_index('row_id').loc[k['row_id']].reset_index()
    kd = pd.DataFrame({'row_id': k['row_id'], 'paper_id': t.paper_id})
    for i, l in enumerate(kl): kd[f'k{l}'] = nlr(k['rank_ko'][:, i])
    kd = kd.merge(pd.DataFrame({'row_id': d['row_id'], 'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])}), on='row_id')
    kp = kd.drop(columns='row_id').groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
    rows, td = [], []
    for g in ['target', 'control', 'all']:
        s = kp if g == 'all' else kp[kp.group == g]; den = (s['true'] - s['false']).to_numpy()
        for l in kl:
            if l == 64: continue
            num = (s['k64'] - s[f'k{l}']).to_numpy(); r = boot_ratio(num, den); dm = boot_mean(num)
            rows.append(dict(group=g, start_layer=int(l), n_papers=r[3], loss_fraction=r[0], lo=r[1], hi=r[2], drop=dm[0], drop_lo=dm[1], drop_hi=dm[2]))
    e = pd.DataFrame(rows); e.to_csv(S / f'{name}_knockout.csv', index=False)
    for l in kl:
        if l == 64: continue
        a = kp[kp.group == 'target']; c = kp[kp.group == 'control']
        r = boot_ratio_diff((a['k64'] - a[f'k{l}']).to_numpy(), (a['true'] - a['false']).to_numpy(), (c['k64'] - c[f'k{l}']).to_numpy(), (c['true'] - c['false']).to_numpy())
        td.append(dict(start_layer=int(l), loss_tc=r[0], lo=r[1], hi=r[2]))
    etc = pd.DataFrame(td); etc.to_csv(S / f'{name}_target_minus_control.csv', index=False)
    L = [f'## {name}. {title} (true title)', '', 'loss = mean(baseline - knocked) / mean(true - false_0); 1 = all title-specific signal lost.', '',
         '| from layer | target | control | all | target - control |', '|---|---|---|---|---|']
    for l in kl:
        if l == 64: continue
        f = lambda g: e[(e.group == g) & (e.start_layer == l)].iloc[0]; x = etc[etc.start_layer == l].iloc[0]
        L.append(f'| L{l} | ' + ' | '.join(fmt(f(g).loss_fraction, f(g).lo, f(g).hi) for g in ['target', 'control', 'all']) + f' | {fmt(x.loss_tc, x.lo, x.hi)} |')
    return L + ['']


def titlepos_section(ROOT, R10, s10, papers, S):
    conds = [c for c in s10.condition_names() if c != 'delete']; fk = [c for c in conds if c.startswith('false_')]
    pm = {}
    for c in conds:
        z, _ = load_unit_dir(ROOT / 'raw/titlepos' / c)
        keys = [k for k in z if k.count('@') == 2]
        df = pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], **{k: nlr(z[k]) for k in keys}})
        pm[c] = df.groupby(['paper_id', 'kind'])[keys].mean()
    common = pm['true'].index
    for c in conds: common = common.intersection(pm[c].index)
    spec = pm['true'].loc[common] - sum(pm[c].loc[common] for c in fk) / len(fk)
    lev = pm['true'].loc[common]
    meta = papers.rename(columns={'group_tight': 'group'}).set_index('paper_id')
    rows = []
    for kind in ['first', 'surname']:
        for key in spec.columns:
            r, l, pos = key.split('@')
            s = spec.xs(kind, level='kind')[key].rename('v').to_frame().join(meta[['group', 'citation_bin']])
            v = lev.xs(kind, level='kind')[key].rename('v').to_frame().join(meta[['group']])
            row = dict(kind=kind, readout=r, layer=int(l), position=pos)
            for g in ['target', 'control']:
                m = boot_mean(s[s.group == g].v); row |= {f'spec_{g}': m[0], f'spec_{g}_lo': m[1], f'spec_{g}_hi': m[2], f'level_{g}': v[v.group == g].v.mean()}
            e = strat_diff(s, 'v'); row |= dict(spec_tc=e[0], spec_tc_lo=e[1], spec_tc_hi=e[2])
            rows.append(row)
    e4 = pd.DataFrame(rows); e4.to_csv(S / 'E4_titlepos_lens.csv', index=False)
    L = ['## E4. Is the author already at the TITLE position? Lens readout at the last title token (vs the ":" position)', '',
         'Gold = each author\'s first name token; title-specific = true - mean(5 false titles), same gold tokens; target - control within bin.', '',
         '| readout | layer | title pos: spec target | spec control | target - control | ":" pos: target - control |', '|---|---|---|---|---|---|']
    f4 = e4[e4.kind == 'first']
    for r in ['logit', 'jlens_public', 'final']:
        for l in sorted(f4[f4.readout == r].layer.unique()):
            a = f4[(f4.readout == r) & (f4.layer == l) & (f4.position == 'title')].iloc[0]; b = f4[(f4.readout == r) & (f4.layer == l) & (f4.position == 'colon')].iloc[0]
            L.append(f'| {r} | L{l} | {fmt(a.spec_target, a.spec_target_lo, a.spec_target_hi)} | {fmt(a.spec_control, a.spec_control_lo, a.spec_control_hi)} | {fmt(a.spec_tc, a.spec_tc_lo, a.spec_tc_hi)} | {fmt(b.spec_tc, b.spec_tc_lo, b.spec_tc_hi)} |')
    L += ['']
    L += probe_section(ROOT, papers, S)
    return L


def probe_section(ROOT, papers, S, folds=5, alphas=(0.1, 1.0, 10.0)):
    """Ridge probe: residual at the last title token (layer l) -> the model's own L63 residual at ':' (true run), trained on
    the other folds' papers; the prediction is final-normed and scored against the lm_head rows of the cohort's author
    first tokens. Applied to the true-title and to the false_0-title residual of held-out papers."""
    pv = np.load(sorted((ROOT / 'raw/probe_vocab').glob('shard_*.npz'))[0])
    W = pv['lm_head_rows'].astype(np.float32); nw = pv['norm_weight'].astype(np.float32); eps = float(pv['eps']); vid = {int(t): i for i, t in enumerate(pv['token_id'])}
    def loadc(c):
        zs = [np.load(f) for f in sorted((ROOT / 'raw/titlepos' / c).glob('shard_*.npz'))]
        return (np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]),
                pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zs]), zs[0]['probe_layers'])
    Xt, Ct, pid, gold, players = loadc('true'); Xf, _, pidf, _, _ = loadc('false_0')
    order = {p: i for i, p in enumerate(pidf)}; Xf = Xf[[order[p] for p in pid]]
    Y = Ct[:, -1].astype(np.float32)
    g = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict()
    rng_ = np.random.default_rng(11); fold = rng_.integers(0, folds, len(pid))
    def score(pred, idx):
        h = pred / np.sqrt((pred ** 2).mean(1, keepdims=True) + eps) * nw; lg = h @ W.T
        out = np.full(len(idx), np.nan)
        for n, i in enumerate(idx):
            gi = [vid[x] for x in g.get(pid[i], []) if x in vid]
            if gi: out[n] = np.mean([-np.log10(1 + (lg[n] > lg[n, j]).sum()) for j in gi])
        return out
    meta = papers.rename(columns={'group_tight': 'group'}).set_index('paper_id')
    rows = []
    for li, l in enumerate(players):
        X = Xt[:, li].astype(np.float32); XF = Xf[:, li].astype(np.float32)
        mu, sd = X.mean(0), X.std(0) + 1e-6
        nt, nf = np.full(len(pid), np.nan), np.full(len(pid), np.nan)
        best = None
        for k in range(folds):
            tr, te = fold != k, np.where(fold == k)[0]
            A = (X[tr] - mu) / sd; ym = Y[tr].mean(0); G = A.T @ A; B = A.T @ (Y[tr] - ym)
            if best is None:                                  # alpha chosen once, on the first fold's held-out MSE
                errs = []
                for a_ in alphas:
                    Wp = np.linalg.solve(G + a_ * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), B)
                    errs.append((((X[te] - mu) / sd @ Wp + ym - Y[te]) ** 2).mean())
                best = alphas[int(np.argmin(errs))]
            Wp = np.linalg.solve(G + best * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), B)
            nt[te] = score((X[te] - mu) / sd @ Wp + ym, te); nf[te] = score((XF[te] - mu) / sd @ Wp + ym, te)
        df = pd.DataFrame({'paper_id': pid, 'true': nt, 'false': nf}).set_index('paper_id').join(meta[['group', 'citation_bin']])
        df['spec'] = df['true'] - df['false']
        row = dict(layer=int(l), alpha=best)
        for gname in ['target', 'control']:
            m = boot_mean(df[df.group == gname].spec); row |= {f'spec_{gname}': m[0], f'spec_{gname}_lo': m[1], f'spec_{gname}_hi': m[2], f'true_{gname}': df[df.group == gname]['true'].mean()}
        e = strat_diff(df.reset_index(), 'spec'); row |= dict(spec_tc=e[0], spec_tc_lo=e[1], spec_tc_hi=e[2]); rows.append(row)
    pr = pd.DataFrame(rows); pr.to_csv(S / 'E4_probe.csv', index=False)
    L = ['## E4b. Linear probe from the last title token (5-fold ridge to the L63 ":" residual; gold first token ranked within the cohort\'s author first tokens)', '',
         'spec = probe(true-title residual) - probe(false_0-title residual) for the same paper; target - control within bin.', '',
         '| layer | spec target | spec control | target - control |', '|---|---|---|---|']
    for _, x in pr.iterrows():
        L.append(f'| L{int(x.layer)} | {fmt(x.spec_target, x.spec_target_lo, x.spec_target_hi)} | {fmt(x.spec_control, x.spec_control_lo, x.spec_control_hi)} | {fmt(x.spec_tc, x.spec_tc_lo, x.spec_tc_hi)} |')
    return L + ['']


def main(ROOT, R10, s10):
    S = ROOT / 'summary'; S.mkdir(exist_ok=True); (ROOT / 'reports').mkdir(exist_ok=True)
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index'])
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'shard'])
    smp = pd.read_parquet(ROOT / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
    L = ['# Stage 11 - causal and context follow-ups', '', f'Sample for E1/E2: {len(smp)} papers ({(smp.group == "target").sum()} target, {(smp.group == "control").sum()} control), balanced within citation bin.', '']

    # ---------------- E1 / E1t patching, E2 / E2n knockout
    d = None
    for name, sub, title in (('E1', 'patch', 'Activation patching of the aligned tail (tokens after the title + name positions), true -> false_0, one layer at a time'),
                             ('E1t', 'patch_title', 'Activation patching of the LAST TITLE TOKEN only, true -> false_0, one layer at a time')):
        dd, layers = load_unit_dir(ROOT / 'raw' / sub)
        if name == 'E1': d = dd
        L += patch_section(name, title, dd, layers, toks, smp, S)
    for name, sub, title in (('E2', 'knockout', 'Attention knockout: every position after the title blocked from the title tokens, from layer l to the end'),
                             ('E2n', 'knockout_name', 'Attention knockout: only the name positions (":" and names) blocked from the title tokens, from layer l to the end')):
        k, kl = load_unit_dir(ROOT / 'raw' / sub)
        L += ko_section(name, title, k, kl, d, toks, smp, S)
    # ---------------- E4 title position: lens readout and linear probe
    L += titlepos_section(ROOT, R10, s10, papers, S)

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
    L += ['', 'Files: summary/E1*_recovery.csv, E1*_target_minus_control.csv, E2*_knockout.csv, E2*_target_minus_control.csv, E3_chain.csv, E4_titlepos_lens.csv, E4_probe.csv.']
    (ROOT / 'reports/stage11_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('STAGE11 ANALYZED')
