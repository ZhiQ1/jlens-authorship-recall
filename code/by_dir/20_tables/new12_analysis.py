#!/usr/bin/env python3
"""Exploratory (post hoc, 2026-11-22; user order): New 1 = addendum 24 with matched replacement counts; New 2 = source of the
addendum 22 Part A K4c reversal. Results to the user only (not into docs). Reads stored outputs only, writes
391_groups/summary_tables_20261122/{new1,new2}/ (or $NEW12_OUT for the tiny test). Team bootstrap 2,000 (multinomial over
stage13_cpu.group_folds teams), seed 2211.
New 1: per-paper R_a (rare-only replaced), R_b (common-only replaced) from summary_a24/perpaper.csv; replaced counts n_a, n_b from
  raw/a24_freeze/variants.parquet. (i) paired papers with n_a == n_b: mean(R_a − R_b) per k and overall; (ii) per-k stratified
  across papers: mean R_a over papers with n_a = k minus mean R_b over papers with n_b = k, pooled with w_k = n_ak n_bk/(n_ak+n_bk);
  (iii) per replaced word: mean(R_a / n_a), mean(R_b / n_b). Common words were frequency-matched replacements, not synonyms.
New 2: per-paper y_l = p_orig(l) − p_fict(l) (mean log10(1/rank) of the true name tokens, final L63 after patching the variant's
  post-title tail at layer l; the a22A raw), y_F = mean over F = L24/32/40/44/48, plus y_L48. Regressors: log10(1+citations),
  k_rare (addendum 24 rare-word rule; a24 freeze), fict − true title log-prob (addendum 20 title_logprob_perpaper.csv),
  title length (words), target dummy, den = true − false_0 (E1) as a scale control, field fixed effects. OLS; team-bootstrap CIs.
  Models M0 cit(+den, FE), M1 +k_rare, M2 +Δlogprob, M3 all.
"""
import importlib.util, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); G = B / '391_groups'
OUT = Path(os.environ.get('NEW12_OUT', G / 'summary_tables_20261122')); TINY = int(os.environ.get('NEW12_TINY', '0'))
NB, SEED = (50 if TINY else 2000), 2211
NL = lambda r: -np.log10(np.asarray(r, float)); F_LAYERS = [24, 32, 40, 44, 48]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def teams():
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); papers = pd.read_parquet(B / '351_stage10/cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); return dict(zip(papers.paper_id, team)), papers


def weights(pids, TEAM, seed=SEED):
    codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in pids]))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def md(df, index=True):
    try: return df.to_markdown(index=index, floatfmt='+.4f')
    except ImportError: return '```\n' + df.to_string(index=index, float_format=lambda v: f'{v:+.4f}') + '\n```'


def ci(b): b = np.asarray(b, float); b = b[np.isfinite(b)]; return (np.percentile(b, 2.5), np.percentile(b, 97.5)) if len(b) else (np.nan, np.nan)


def wmean(x, w): ok = np.isfinite(x); return float(np.sum(w[ok] * x[ok]) / np.sum(w[ok])) if ok.any() and np.sum(w[ok]) > 0 else np.nan


def new1(TEAM):
    out = OUT / 'new1'; out.mkdir(parents=True, exist_ok=True)
    P = pd.read_csv(G / 'summary_a24/perpaper.csv'); V = pd.read_parquet(G / 'raw/a24_freeze/variants.parquet')
    na = V[V.variant == 'a'].set_index('paper_id').n_replaced; nb = V[V.variant == 'b'].set_index('paper_id').n_replaced
    P['n_a'] = P.paper_id.map(na); P['n_b'] = P.paper_id.map(nb)
    P = P[np.isfinite(P.R_a) & np.isfinite(P.R_b) & (P.n_a >= 1) & (P.n_b >= 1)].copy()
    if TINY: P = P.groupby('group').head(80)
    rows = []
    for grp in ['target', 'control', 'all']:
        S = P if grp == 'all' else P[P.group == grp]; pids = S.paper_id.to_numpy(); W = weights(pids, TEAM)
        Ra, Rb, ka, kb = S.R_a.to_numpy(), S.R_b.to_numpy(), S.n_a.to_numpy(), S.n_b.to_numpy(); one = np.ones(len(S))
        # (i) paired equal-k
        pair = ka == kb
        for k in sorted(set(ka[pair])) + ['all']:
            m = pair & ((ka == k) if k != 'all' else True)
            if m.sum() < 5: continue
            d = Ra - Rb; e = wmean(np.where(m, d, np.nan), one); bs = [wmean(np.where(m, d, np.nan), W[i]) for i in range(NB)]
            rows.append(dict(group=grp, analysis='paired n_a == n_b', k=k, n=int(m.sum()), est=e, lo=ci(bs)[0], hi=ci(bs)[1]))
        # (ii) per-k stratified across papers
        ks = sorted(set(ka) & set(kb)); pooled_e, pooled_b, wsum = 0.0, np.zeros(NB), 0.0
        for k in ks:
            ma, mb = ka == k, kb == k
            if ma.sum() < 5 or mb.sum() < 5: continue
            e = wmean(np.where(ma, Ra, np.nan), one) - wmean(np.where(mb, Rb, np.nan), one)
            bs = np.array([wmean(np.where(ma, Ra, np.nan), W[i]) - wmean(np.where(mb, Rb, np.nan), W[i]) for i in range(NB)])
            wk = ma.sum() * mb.sum() / (ma.sum() + mb.sum()); pooled_e += wk * e; pooled_b += wk * bs; wsum += wk
            rows.append(dict(group=grp, analysis='stratified by k', k=k, n=f'{int(ma.sum())}/{int(mb.sum())}', est=e, lo=ci(bs)[0], hi=ci(bs)[1],
                             Ra=wmean(np.where(ma, Ra, np.nan), one), Rb=wmean(np.where(mb, Rb, np.nan), one)))
        if wsum: rows.append(dict(group=grp, analysis='stratified by k', k='pooled', n=int(len(S)), est=pooled_e / wsum, lo=ci(pooled_b / wsum)[0], hi=ci(pooled_b / wsum)[1]))
        # (iii) per replaced word
        for lab, x in [('R_a per word', Ra / ka), ('R_b per word', Rb / kb), ('per-word difference', Ra / ka - Rb / kb)]:
            e = wmean(x, one); bs = [wmean(x, W[i]) for i in range(NB)]
            rows.append(dict(group=grp, analysis='per replaced word', k=lab, n=int(len(S)), est=e, lo=ci(bs)[0], hi=ci(bs)[1]))
        rows.append(dict(group=grp, analysis='mean replaced words', k='n_a / n_b', n=int(len(S)), est=float(ka.mean()), lo=float(kb.mean()), hi=np.nan))
    T = pd.DataFrame(rows); T.to_csv(out / 'new1_matched.csv', index=False)
    (out / 'report.md').write_text('# New 1 — addendum 24 with matched replacement counts (exploratory, post hoc)\n\nR = S_true − S_variant (final L63, all authors, all name tokens). '
        'Common words were replaced by frequency-matched words, NOT synonyms, so their meaning changes. Team bootstrap '
        f'{NB}.\n\n' + md(T, False) + '\n')
    return T


def new2(TEAM, papers):
    out = OUT / 'new2'; out.mkdir(parents=True, exist_ok=True)
    FZ = G / 'raw/a22A_freeze'; RAW = G / 'raw/a22A'; D = pd.read_parquet(FZ / 'freeze.parquet'); fz = json.loads((FZ / 'freeze.json').read_text())
    toks = pd.read_parquet(B / '351_stage10/cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    VARS = ['orig', 'case', 'para', 'shuf', 'fict', 'lexD']; pt, rf, rp, lay = [], [], [], None
    for k in (fz['shards'][:2] if TINY else fz['shards']):
        z = np.load(RAW / f'patch/shard_{k:03d}.npz'); lay = list(z['layers']); pt.append(z['row_id']); rf.append(z['rank_false']); rp.append(z['rank_patch'])
    row = np.concatenate(pt); rfa = np.concatenate(rf); rpa = np.concatenate(rp)
    e1 = {}
    for f in sorted((B / '361_stage11/raw/patch').glob('shard_*.npz')):
        z = np.load(f); e1.update({r: (t, fl) for r, t, fl in zip(z['row_id'], z['rank_true'], z['rank_false'])})
    has = np.array([r in e1 for r in row]); row, rfa, rpa = row[has], rfa[has], rpa[has]
    T = pd.DataFrame({'paper_id': toks.loc[row].to_numpy(), 'true': NL([e1[r][0] for r in row]), 'false_s': NL([e1[r][1] for r in row])})
    for v in ('orig', 'fict'):
        vi = VARS.index(v)
        for li, l in enumerate(lay):
            x = rpa[:, vi, li].astype(float); T[f'{v}_{l}'] = np.where(x > 0, NL(np.where(x > 0, x, 1)), np.nan)
    PP = T.groupby('paper_id').mean().join(D.set_index('paper_id')[['group', 'field', 'citations']])
    PP['den'] = PP.true - PP.false_s
    for l in lay: PP[f'y_{l}'] = PP[f'orig_{l}'] - PP[f'fict_{l}']
    PP['y_F'] = PP[[f'y_{l}' for l in F_LAYERS]].mean(1); PP['y_L48'] = PP['y_48']
    V = pd.read_parquet(G / 'raw/a24_freeze/variants.parquet'); kr = V.groupby('paper_id').k_rare.first()
    LP = pd.read_csv(G / 'summary_a20/title_logprob_perpaper.csv').set_index('paper_id')
    ti = papers.set_index('paper_id').title.astype(str)
    PP['lcit'] = np.log10(1 + pd.to_numeric(PP.citations, errors='coerce')); PP['k_rare'] = kr.reindex(PP.index).to_numpy()
    PP['dlp'] = (LP.fict - LP.true).reindex(PP.index).to_numpy()            # fict − true title log-prob (> 0: fict more likely)
    PP['tlen'] = ti.reindex(PP.index).map(lambda t: len(re.findall(r"[A-Za-z0-9]+", t))).to_numpy(); PP['target'] = (PP.group == 'target').astype(float)
    PP = PP[np.isfinite(PP[['y_F', 'y_L48', 'lcit', 'k_rare', 'dlp', 'tlen', 'den']]).all(1)].copy()
    pids = PP.index.to_numpy(); W = weights(pids, TEAM)
    FE = pd.get_dummies(PP.field, prefix='f', drop_first=True).astype(float)
    def z(c): x = PP[c].to_numpy(float); return (x - x.mean()) / x.std()
    models = {'M0': ['lcit'], 'M1': ['lcit', 'k_rare'], 'M2': ['lcit', 'dlp'], 'M3': ['lcit', 'k_rare', 'dlp', 'tlen', 'target']}
    rows = []
    for yname in ['y_F', 'y_L48']:
        y = PP[yname].to_numpy(float)
        for mname, cols in models.items():
            Xc = np.column_stack([z(c) for c in cols] + [z('den')]); X = np.column_stack([np.ones(len(PP)), Xc, FE.to_numpy()])
            def fit(w): sw = np.sqrt(w); return np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
            b0 = fit(np.ones(len(PP))); BB = np.array([fit(W[i]) for i in range(NB)])
            for j, c in enumerate(cols + ['den']):
                lo, hi = ci(BB[:, 1 + j]); rows.append(dict(y=yname, model=mname, term=c, coef_per_sd=b0[1 + j], lo=lo, hi=hi, n=len(PP)))
    R = pd.DataFrame(rows); R.to_csv(out / 'new2_regression.csv', index=False)
    # simple correlations + means by within-field citation half
    med = PP.groupby('field').citations.transform('median'); PP['half'] = np.where(PP.citations > med, 'high', 'low')
    desc = PP.groupby('half')[['y_F', 'y_L48', 'k_rare', 'dlp', 'tlen', 'target', 'den']].mean()
    cor = PP[['lcit', 'k_rare', 'dlp', 'tlen', 'target', 'den', 'y_F']].corr().round(3)
    desc.to_csv(out / 'new2_by_half.csv'); cor.to_csv(out / 'new2_correlations.csv')
    (out / 'report.md').write_text('# New 2 — source of the K4c reversal (exploratory, post hoc)\n\ny = p_orig − p_fict (log10(1/rank) of the true name tokens at the '
        'final layer after patching the variant\'s post-title tail at layer l); y_F = mean over L24/32/40/44/48. Coefficients per 1 SD of each '
        f'regressor (field fixed effects, den = true − false_0 as scale control). n = {len(PP)}; team bootstrap {NB}.\n\n'
        + md(R, False) + '\n\nMeans by within-field citation half:\n\n' + md(desc)
        + '\n\nCorrelations:\n\n' + md(cor) + '\n')
    return R, desc, cor


if __name__ == '__main__':
    TEAM, papers = teams()
    T1 = new1(TEAM); print(T1.to_string(), flush=True)
    R, desc, cor = new2(TEAM, papers); print(R.to_string()); print(desc.to_string()); print(cor.to_string()); print('DONE', OUT, flush=True)
