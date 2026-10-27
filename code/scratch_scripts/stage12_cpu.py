"""Stage 12 CPU analyses (2026-10-27): name-prior decomposition (A), prior vs recognition (B), name commonness (C), and
controls for the Stage 11 title-position probe (X1). Inputs: frozen Stage 10 summaries / cohort and Stage 11 raw titlepos.
Writes /scratch/$USER/jlens/371_stage12/summary_cpu/*.csv and reports/stage12_cpu_report.md."""
import json, os, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

R10 = Path('/scratch') / os.environ['USER'] / 'jlens/351_stage10'; R11 = R10.parent / '361_stage11'; ROOT = R10.parent / '371_stage12'
S = ROOT / 'summary_cpu'; S.mkdir(parents=True, exist_ok=True); (ROOT / 'reports').mkdir(exist_ok=True)
rng = np.random.default_rng(3712); B = 2000
ROLES = ['', '_surname_first', '_surname_cont', '_given_first', '_initial_first', '_punct']


def boot(v):
    v = np.asarray(v, float); v = v[~np.isnan(v)]; mm = v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    return v.mean(), *np.percentile(mm, [2.5, 97.5])


def strat(df, col, g='group_tight', min_n=30):
    cells = []
    for b, x in df.groupby('citation_bin'):
        A = x[x[g] == 'target'][col].dropna().to_numpy(); C = x[x[g] == 'control'][col].dropna().to_numpy()
        if len(A) >= min_n and len(C) >= min_n: cells.append((A, C))
    w = np.array([len(A) * len(C) / (len(A) + len(C)) for A, C in cells]); w /= w.sum()
    est = sum(wi * (A.mean() - C.mean()) for wi, (A, C) in zip(w, cells))
    bt = sum(wi * (A[rng.integers(0, len(A), (B, len(A)))].mean(1) - C[rng.integers(0, len(C), (B, len(C)))].mean(1)) for wi, (A, C) in zip(w, cells))
    return est, *np.percentile(bt, [2.5, 97.5])


def f(v, lo, hi): return f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'


def main():
    L = ['# Stage 12 CPU analyses: name prior and probe controls', '']
    d = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'authors', 'field', 'mc_team_a', 'recall_level'])
    # ---------------- A. decomposition: no title (prior) -> false title (topic) -> true title (paper-specific)
    rows = []
    for (r, l), x in d.groupby(['readout', 'layer']):
        for role in ROLES:
            m = f'mean_nlr{role}'
            if f'true_{m}' not in x: continue
            x = x.assign(prior=x[f'delete_{m}'], topic=x[f'false_{m}'] - x[f'delete_{m}'], spec=x[f'true_{m}'] - x[f'false_{m}'], true=x[f'true_{m}'])
            for g in ['all', 'target', 'control']:
                s = x if g == 'all' else x[x.group_tight == g]
                row = dict(readout=r, layer=l, role=role.strip('_') or 'all_tokens', group=g, n=len(s))
                for k in ['prior', 'topic', 'spec', 'true']: row[k] = s[k].mean()
                rows.append(row)
            for k in ['prior', 'topic', 'spec', 'true']:
                e = strat(x, k); rows.append(dict(readout=r, layer=l, role=role.strip('_') or 'all_tokens', group=f'tc_{k}', n=len(x), **{k: e[0], f'{k}_lo': e[1], f'{k}_hi': e[2]}))
    A = pd.DataFrame(rows); A.to_csv(S / 'A_prior_decomposition.csv', index=False)
    fo = A[(A.readout == 'final')]
    L += ['## A. Name prior vs title, model output (log10(1/rank))', '', 'prior = no title; topic = false - no title; paper-specific = true - false.', '',
          '| token role | group | prior (no title) | topic | paper-specific | true |', '|---|---|---|---|---|---|']
    for role in ['all_tokens', 'surname_first', 'surname_cont', 'given_first', 'initial_first', 'punct']:
        for g in ['target', 'control']:
            x = fo[(fo.role == role) & (fo.group == g)]
            if len(x): x = x.iloc[0]; L.append(f'| {role} | {g} | {x.prior:+.3f} | {x.topic:+.3f} | {x.spec:+.3f} | {x.true:+.3f} |')
    L += ['', '| token role | target - control (within bin): prior | topic | paper-specific | true |', '|---|---|---|---|---|']
    for role in ['all_tokens', 'surname_first', 'surname_cont', 'given_first', 'initial_first']:
        cells = []
        for k in ['prior', 'topic', 'spec', 'true']:
            x = fo[(fo.role == role) & (fo.group == f'tc_{k}')].iloc[0]; cells.append(f(x[k], x[f'{k}_lo'], x[f'{k}_hi']))
        L.append(f'| {role} | ' + ' | '.join(cells) + ' |')
    # by citation bin (output, all tokens)
    xb = d[(d.readout == 'final')].assign(prior=lambda z: z.delete_mean_nlr, spec=lambda z: z.true_mean_nlr - z.false_mean_nlr)
    bb = xb[xb.group_tight.isin(['target', 'control'])].groupby(['citation_bin', 'group_tight'])[['prior', 'spec']].mean().unstack().round(3)
    bb.to_csv(S / 'A_prior_by_bin.csv')
    # layer profile of the prior (logit / public, all tokens, all papers)
    lp = A[(A.role == 'all_tokens') & (A.group == 'all') & (A.readout.isin(['logit', 'jlens_public']))][['readout', 'layer', 'prior', 'topic', 'spec']]
    lp.to_csv(S / 'A_prior_by_layer.csv', index=False)
    # ---------------- B. does the prior explain recognition?
    x = xb.merge(papers[['paper_id', 'mc_team_a', 'recall_level']], on='paper_id', suffixes=('', '_p'))
    x['mc_team_a_p'] = pd.to_numeric(x.mc_team_a_p, errors='coerce'); x = x[x.recall_level_p.isin(['R0', 'R1']) & x.mc_team_a_p.notna()].copy()
    for k in ['prior', 'spec']: x[k + '_c'] = x[k] - x.groupby('citation_bin')[k].transform('mean')
    rb = []
    for k in ['prior', 'spec']:
        rho = spearmanr(x.mc_team_a_p, x[k + '_c']).statistic
        bs = [spearmanr(x.mc_team_a_p.to_numpy()[i], x[k + '_c'].to_numpy()[i]).statistic for i in [rng.integers(0, len(x), len(x)) for _ in range(500)]]
        rb.append(dict(metric=k, n=len(x), rho=rho, lo=np.percentile(bs, 2.5), hi=np.percentile(bs, 97.5),
                       **{f'mean_a{a}': x[x.mc_team_a_p == a][k + '_c'].mean() for a in range(5)}))
    RB = pd.DataFrame(rb); RB.to_csv(S / 'B_prior_vs_recognition.csv', index=False)
    L += ['', '## B. Does the name prior explain recognition? (R0/R1 papers, centred within citation bin)', '',
          '| metric | Spearman with multiple-choice orders right (0-4) | mean at 0 / 1 / 2 / 3 / 4 right |', '|---|---|---|']
    for _, r in RB.iterrows():
        L.append(f'| {r.metric} | {r.rho:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}] | ' + ' / '.join(f'{r[f"mean_a{a}"]:+.3f}' for a in range(5)) + ' |')
    # ---------------- C. name commonness (surname frequency in the cohort)
    sur = [a.strip().split()[-1].lower() for s_ in papers.authors.astype(str) for a in s_.split(';') if a.strip()]
    cnt = pd.Series(sur).value_counts()
    papers['log_surname_freq'] = [np.mean([np.log10(cnt.get(a.strip().split()[-1].lower(), 1)) for a in str(s_).split(';') if a.strip()] or [np.nan]) for s_ in papers.authors]
    xc = xb.merge(papers[['paper_id', 'log_surname_freq']], on='paper_id')
    rc = []
    for g in ['all', 'target', 'control']:
        s = xc if g == 'all' else xc[xc.group_tight == g]
        for k in ['prior', 'spec']:
            rc.append(dict(group=g, metric=k, n=len(s), rho=spearmanr(s.log_surname_freq, s[k], nan_policy='omit').statistic))
    e = strat(xc, 'log_surname_freq'); rc.append(dict(group='target-control (within bin)', metric='log_surname_freq', n=len(xc), rho=np.nan, diff=e[0], lo=e[1], hi=e[2]))
    RC = pd.DataFrame(rc); RC.to_csv(S / 'C_surname_commonness.csv', index=False)
    L += ['', '## C. Name commonness: log10 count of the surname among all cohort authors (per-paper mean)', '',
          '| group | Spearman with prior | Spearman with paper-specific |', '|---|---|---|']
    for g in ['all', 'target', 'control']:
        a_ = RC[(RC.group == g) & (RC.metric == 'prior')].rho.iloc[0]; b_ = RC[(RC.group == g) & (RC.metric == 'spec')].rho.iloc[0]
        L.append(f'| {g} | {a_:+.3f} | {b_:+.3f} |')
    L.append(f'\ntarget - control in surname commonness (within bin): {f(e[0], e[1], e[2])}')
    # ---------------- X1. probe controls
    L += ['', '## X1. Controls for the Stage 11 title-position probe (E4b)', ''] + probe_controls(papers)
    (ROOT / 'reports/stage12_cpu_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('STAGE12 CPU DONE')


def probe_controls(papers, folds=5, alpha=1.0):
    pv = np.load(sorted((R11 / 'raw/probe_vocab').glob('shard_*.npz'))[0])
    W = pv['lm_head_rows'].astype(np.float32); nw = pv['norm_weight'].astype(np.float32); eps = float(pv['eps']); vid = {int(t): i for i, t in enumerate(pv['token_id'])}
    def loadc(c):
        zs = [np.load(f) for f in sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))]
        return (np.concatenate([z['resid_title'] for z in zs]), np.concatenate([z['resid_colon'] for z in zs]), np.concatenate([z['resid_paper_id'] for z in zs]),
                pd.concat([pd.DataFrame({'paper_id': z['paper_id'], 'kind': z['kind'], 'gold': z['gold']}) for z in zs]), zs[0]['probe_layers'])
    Xt, Ct, pid, gold, players = loadc('true'); Xf, Cf, pidf, _, _ = loadc('false_0')
    o = {p: i for i, p in enumerate(pidf)}; ix = [o[p] for p in pid]; Xf, Cf = Xf[ix], Cf[ix]
    g = gold[gold.kind == 'first'].groupby('paper_id').gold.apply(list).to_dict()
    meta = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'field']).set_index('paper_id').loc[pid]
    fields = meta.field.to_numpy()
    # permutations: any other paper / another paper of the same field
    perm_any = rng.permutation(len(pid))
    perm_field = np.arange(len(pid))
    for fl in np.unique(fields):
        idx = np.where(fields == fl)[0]; perm_field[idx] = idx[rng.permutation(len(idx))]
    fold = np.random.default_rng(11).integers(0, folds, len(pid))
    def score(pred, gidx):
        h = pred / np.sqrt((pred ** 2).mean(1, keepdims=True) + eps) * nw; lg = h @ W.T; out = np.full(len(gidx), np.nan)
        for n, i in enumerate(gidx):
            gi = [vid[x] for x in g.get(pid[i], []) if x in vid]
            if gi: out[n] = np.mean([-np.log10(1 + (lg[n] > lg[n, j]).sum()) for j in gi])
        return out
    rows = []
    for li, l in enumerate(players):
        if l not in (24, 40, 56): continue
        X = Xt[:, li].astype(np.float32); XF = Xf[:, li].astype(np.float32); Y = Ct[:, -1].astype(np.float32); YF = Cf[:, -1].astype(np.float32)
        res = {k: np.full(len(pid), np.nan) for k in ['true', 'false', 'true_gold_any', 'false_gold_any', 'true_gold_field', 'false_gold_field', 'ftrain_true', 'ftrain_false']}
        for k in range(folds):
            tr, te = fold != k, np.where(fold == k)[0]
            for tag, Xtr, Ytr in (('', X[tr], Y[tr]), ('ftrain_', XF[tr], YF[tr])):
                mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6; A = (Xtr - mu) / sd; ym = Ytr.mean(0); G = A.T @ A
                Wp = np.linalg.solve(G + alpha * np.trace(G) / G.shape[0] * np.eye(G.shape[0]), A.T @ (Ytr - ym))
                pt_ = (X[te] - mu) / sd @ Wp + ym; pf_ = (XF[te] - mu) / sd @ Wp + ym
                if tag:
                    res['ftrain_true'][te] = score(pt_, te); res['ftrain_false'][te] = score(pf_, te)
                else:
                    res['true'][te] = score(pt_, te); res['false'][te] = score(pf_, te)
                    res['true_gold_any'][te] = score(pt_, perm_any[te]); res['false_gold_any'][te] = score(pf_, perm_any[te])
                    res['true_gold_field'][te] = score(pt_, perm_field[te]); res['false_gold_field'][te] = score(pf_, perm_field[te])
        df = pd.DataFrame(res, index=pid).join(meta[['group_tight', 'citation_bin']])
        for name, a, b in (('probe (as in Stage 11)', 'true', 'false'), ('gold = random other paper', 'true_gold_any', 'false_gold_any'),
                           ('gold = random paper of the same field', 'true_gold_field', 'false_gold_field'), ('probe trained on FALSE-title pairs', 'ftrain_true', 'ftrain_false')):
            df['spec'] = df[a] - df[b]; e = strat(df.reset_index().rename(columns={'index': 'paper_id'}), 'spec')
            row = dict(layer=int(l), control=name, spec_all=boot(df.spec)[0], spec_all_lo=boot(df.spec)[1], spec_all_hi=boot(df.spec)[2], tc=e[0], tc_lo=e[1], tc_hi=e[2])
            rows.append(row)
    P = pd.DataFrame(rows); P.to_csv(S / 'X1_probe_controls.csv', index=False)
    L = ['spec = probe(true-title residual) - probe(false_0-title residual); a real paper-specific signal should vanish when the gold authors are those of another paper.', '',
         '| layer | control | spec, all papers | target - control (within bin) |', '|---|---|---|---|']
    for _, r in P.iterrows(): L.append(f'| L{r.layer} | {r.control} | {f(r.spec_all, r.spec_all_lo, r.spec_all_hi)} | {f(r.tc, r.tc_lo, r.tc_hi)} |')
    return L


if __name__ == '__main__':
    main()
