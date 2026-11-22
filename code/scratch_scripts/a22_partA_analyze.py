#!/usr/bin/env python3
"""Addendum 22 Part A analysis (LOCKED prereg §2.2–2.4). Inputs raw/a22A/{patch,state}/, freeze, stored Stage 11 E1 (denominator).

R_v(l) = mean_S(nlr_patched,v(l) − nlr_false0) / mean_S(nlr_true − nlr_false0); nlr = log10(1/rank), tokens averaged within
paper first; numerator false_0 = this run's receiving run (paired), denominator true/false_0 = stored Stage 11 E1 ranks of the
same rows (prereg: 'denominator from the stored Stage 10/11 true and false_0 runs'); sensitivity: stored false_0 in both.
Contrasts per l (F = L24, 32, 40, 44, 48 judged; all 11 layers reported): K1 R_para − R_shuf, K2 R_orig − R_case (surface-robust
from the first l in F whose Holm CI lies in [−0.05, 0.05]), K3 R_para − R_lexD (K1–K3: all papers), K4 [R_orig − R_fict]_T −
[R_orig − R_fict]_C within citation bins (weights n_t n_c/(n_t+n_c)), K4c [R_orig − R_fict]_high − _low, halves = above /
at-or-below the within-field median citations, within field strata (weights n_h n_l/(n_h+n_l)). Within a stratum,
[R_orig − R_fict] = Σ(p_orig − p_fict) / Σ(true − false) over its papers. Team bootstrap: multinomial over author teams
(stage13_cpu.group_folds), 2,000 draws, seed 22; two-sided bootstrap p; Holm over the 5 layers of F per contrast;
Holm-adjusted CI = percentile CI at level 1 − alpha_i (alpha_i = 0.05 / (m − rank + 1) by ascending p).
Papers with a missing variant are dropped from contrasts that use that variant. Strata with < 3 papers in a cell are skipped.
Also: the recognition × citations 2×2 of [R_orig − R_fict](l) with CIs and the interaction; state similarity (secondary).
"""
import importlib.util, json, os, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); G = B / '391_groups'
RAW = Path(os.environ.get('A22A_RAW', G / 'raw/a22A')); FREEZE = G / 'raw/a22A_freeze'; OUT = Path(os.environ.get('A22A_SUMMARY', G / 'summary_a22_partA'))
F_LAYERS = [24, 32, 40, 44, 48]; NB, SEED, ALPHA = 2000, 22, 0.05
VARS = ['orig', 'case', 'para', 'shuf', 'fict', 'lexD']
NL = lambda r: -np.log10(np.asarray(r, float))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def holm_alpha(ps):
    o = np.argsort(ps); m = len(ps); a = np.empty(m); adj = np.empty(m); run = 0
    for r, i in enumerate(o): a[i] = ALPHA / (m - r); run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    return a, adj


def pval(b): b = b[np.isfinite(b)]; return float(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean()))) if len(b) else np.nan


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    D = pd.read_parquet(FREEZE / 'freeze.parquet'); fz = json.loads((FREEZE / 'freeze.json').read_text())
    toks = pd.read_parquet(B / '351_stage10/cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    pt, rf, rp, lay = [], [], [], None
    SH = [int(x) for x in os.environ['A22A_SHARDS'].split(',')] if os.environ.get('A22A_SHARDS') else fz['shards']
    for k in SH:
        z = np.load(RAW / f'patch/shard_{k:03d}.npz'); lay = list(z['layers'])
        pt.append(z['row_id']); rf.append(z['rank_false']); rp.append(z['rank_patch'])
    row = np.concatenate(pt); rfa = np.concatenate(rf); rpa = np.concatenate(rp)
    e1 = {}
    for f in sorted((B / '361_stage11/raw/patch').glob('shard_*.npz')):
        z = np.load(f); e1.update({r: (t, fl) for r, t, fl in zip(z['row_id'], z['rank_true'], z['rank_false'])})
    has = np.array([r in e1 for r in row]); print('rows', len(row), 'with E1', has.sum(), flush=True)
    row, rfa, rpa = row[has], rfa[has], rpa[has]
    st = np.array([e1[r][0] for r in row]); sf = np.array([e1[r][1] for r in row])
    T = pd.DataFrame({'paper_id': toks.loc[row].to_numpy(), 'true': NL(st), 'false_s': NL(sf), 'false': NL(rfa)})
    for vi, v in enumerate(VARS):
        for li, l in enumerate(lay):
            x = rpa[:, vi, li].astype(float); T[f'{v}_{l}'] = np.where(x > 0, NL(np.where(x > 0, x, 1)), np.nan)
    PP = T.groupby('paper_id').mean()
    PP = PP.join(D.set_index('paper_id')[['group', 'citation_bin', 'field', 'citations']])
    PP['den'] = PP['true'] - PP['false_s']
    # teams + bootstrap weights
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); papers = pd.read_parquet(B / '351_stage10/cohort/papers.parquet')
    _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
    pids = PP.index.to_numpy(); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in pids]))
    W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]   # [NB, n]
    # within-field citation halves (ties -> low)
    med = PP.groupby('field').citations.transform('median'); PP['half'] = np.where(PP.citations > med, 'high', 'low')
    n = len(PP); idx = np.arange(n)

    def ratio(num, den, mask):
        """point estimate and bootstrap draws of Σ num / Σ den over mask (weights W)."""
        ok = mask & np.isfinite(num) & np.isfinite(den)
        e = num[ok].sum() / den[ok].sum() if ok.any() else np.nan
        b = (W[:, ok] @ num[ok]) / (W[:, ok] @ den[ok]) if ok.any() else np.full(NB, np.nan)
        return e, b, int(ok.sum())

    def R(v, l, mask): return ratio((PP[f'{v}_{l}'] - PP['false']).to_numpy(), PP['den'].to_numpy(), mask)

    def diffR(v1, v2, l, mask):
        ok = np.isfinite(PP[f'{v1}_{l}']).to_numpy() & np.isfinite(PP[f'{v2}_{l}']).to_numpy()
        return ratio((PP[f'{v1}_{l}'] - PP[f'{v2}_{l}']).to_numpy(), PP['den'].to_numpy(), mask & ok)

    def strat(l, strata, a_mask, b_mask):
        """Σ_s w_s (D_a,s − D_b,s) / Σ w_s with D = Σ(p_orig − p_fict)/Σ den per cell; w = n_a n_b/(n_a+n_b); cells < 3 skipped."""
        num = (PP[f'orig_{l}'] - PP[f'fict_{l}']).to_numpy(); den = PP['den'].to_numpy(); fin = np.isfinite(num)
        est_n, est_d, bt = 0.0, 0.0, np.zeros(NB); used = 0
        for s in pd.unique(strata):
            ms = (strata == s) & fin; ma, mb = ms & a_mask, ms & b_mask
            na, nb = ma.sum(), mb.sum()
            if na < 3 or nb < 3: continue
            w = na * nb / (na + nb); used += 1
            da = num[ma].sum() / den[ma].sum(); db = num[mb].sum() / den[mb].sum()
            est_n += w * (da - db); est_d += w
            bt += w * ((W[:, ma] @ num[ma]) / (W[:, ma] @ den[ma]) - (W[:, mb] @ num[mb]) / (W[:, mb] @ den[mb]))
        if est_d == 0: return np.nan, np.full(NB, np.nan), 0
        return est_n / est_d, bt / est_d, used

    allm = np.ones(n, bool); Tm = (PP.group == 'target').to_numpy(); Cm = ~Tm
    Hm = (PP.half == 'high').to_numpy(); Lm = ~Hm
    rows = []
    for l in lay:
        for v in VARS:
            for g, m in (('all', allm), ('target', Tm), ('control', Cm)):
                e, b, k = R(v, l, m); rows.append(dict(kind='R', variant=v, layer=l, group=g, est=e, lo=np.nanpercentile(b, 2.5), hi=np.nanpercentile(b, 97.5), n=k))
    Rt = pd.DataFrame(rows); Rt.to_csv(OUT / 'R_curves.csv', index=False)
    con = {}
    for name, f in [('K1', lambda l: diffR('para', 'shuf', l, allm)), ('K2', lambda l: diffR('orig', 'case', l, allm)),
                    ('K3', lambda l: diffR('para', 'lexD', l, allm)),
                    ('K4', lambda l: strat(l, PP.citation_bin.to_numpy(), Tm, Cm)), ('K4c', lambda l: strat(l, PP.field.to_numpy(), Hm, Lm))]:
        con[name] = {l: f(l) for l in lay}
    crow = []
    for name, d in con.items():
        ps = np.array([pval(d[l][1]) for l in F_LAYERS]); al, adj = holm_alpha(ps)
        for l in lay:
            e, b, k = d[l]; r = dict(contrast=name, layer=l, est=e, lo=np.nanpercentile(b, 2.5), hi=np.nanpercentile(b, 97.5), p=pval(b), n_or_strata=k, in_F=l in F_LAYERS)
            if l in F_LAYERS:
                i = F_LAYERS.index(l); r.update(p_holm=adj[i], holm_lo=np.nanpercentile(b, 100 * al[i] / 2), holm_hi=np.nanpercentile(b, 100 * (1 - al[i] / 2)))
            crow.append(r)
    Ct = pd.DataFrame(crow); Ct.to_csv(OUT / 'contrasts.csv', index=False)
    F = Ct[Ct.in_F]
    sup = lambda c: bool(((F.contrast == c) & (F.holm_lo > 0)).any())
    rev = lambda c: bool(((F.contrast == c) & (F.holm_hi < 0)).any())
    border = lambda c: bool(((F.contrast == c) & (F.lo > 0)).any()) and not sup(c)
    k2 = F[(F.contrast == 'K2') & (F.holm_lo >= -0.05) & (F.holm_hi <= 0.05)]
    para_shuf = Rt[(Rt.group == 'all') & Rt.layer.isin(F_LAYERS)].pivot(index='layer', columns='variant', values='est')
    V = dict(K1=sup('K1'), K3=sup('K3'), K4=sup('K4'), K4c=sup('K4c'), K4_reversed=rev('K4'), K4c_reversed=rev('K4c'),
             K2_surface_robust_from=int(k2.layer.min()) if len(k2) else None,
             borderline={c: border(c) for c in ('K1', 'K3', 'K4', 'K4c')})
    read = []
    if V['K1'] and V['K3']: read.append('Meaning is encoded in the middle layers')
    if not V['K1'] and not V['K3'] and bool((para_shuf['shuf'] >= para_shuf['para']).all()): read.append('Middle layers mostly surface')
    read.append('Identity beyond meaning (recognised papers only)' if V['K4'] else ('Reversed identity' if V['K4_reversed'] else 'No identity beyond meaning'))
    read.append('Identity beyond meaning grows with exposure' if V['K4c'] else ('Reversed exposure dependence' if V['K4c_reversed'] else 'No exposure dependence of identity'))
    for c, bflag in V['borderline'].items():
        if bflag: read.append(f'Borderline: {c} supported only without Holm')
    # recognition x citations 2x2 of [R_orig - R_fict]
    tb = []
    for l in lay:
        cells = {}
        for gname, gm in (('T', Tm), ('C', Cm)):
            for hname, hm in (('high', Hm), ('low', Lm)):
                e, b, k = diffR('orig', 'fict', l, gm & hm); cells[f'{gname}-{hname}'] = (e, b)
                tb.append(dict(layer=l, cell=f'{gname}-{hname}', est=e, lo=np.nanpercentile(b, 2.5), hi=np.nanpercentile(b, 97.5), n=k))
        ie = (cells['T-high'][0] - cells['T-low'][0]) - (cells['C-high'][0] - cells['C-low'][0])
        ib = (cells['T-high'][1] - cells['T-low'][1]) - (cells['C-high'][1] - cells['C-low'][1])
        tb.append(dict(layer=l, cell='interaction (TH−TL)−(CH−CL)', est=ie, lo=np.nanpercentile(ib, 2.5), hi=np.nanpercentile(ib, 97.5), n=n))
    pd.DataFrame(tb).to_csv(OUT / 'recog_x_citations_2x2.csv', index=False)
    # state similarity (secondary): s_v = cos(h_orig, h_v) - cos(h_orig, h_false0), states centred on the layer mean
    sims = []
    try:
        S_last = []; S_pid = []
        for k in SH:
            z = np.load(RAW / f'state/shard_{k:03d}.npz'); S_last.append(z['last'].astype(np.float32)); S_pid += list(z['paper_id'])
        A = np.concatenate(S_last)                                         # [n, 7, L, d]
        mu = np.nanmean(A.reshape(-1, A.shape[2], A.shape[3]), axis=0)     # [L, d]
        A = A - mu[None, None]
        cos = lambda x, y: np.sum(x * y, -1) / (np.linalg.norm(x, axis=-1) * np.linalg.norm(y, axis=-1))
        grp = D.set_index('paper_id').loc[S_pid, 'group'].to_numpy()
        for vi, v in enumerate(VARS[1:], 1):
            s = cos(A[:, 0], A[:, vi]) - cos(A[:, 0], A[:, 6])             # [n, L]
            for li, l in enumerate(lay):
                for g in ('all', 'target', 'control'):
                    m = np.ones(len(grp), bool) if g == 'all' else grp == g
                    sims.append(dict(variant=v, layer=l, group=g, s=float(np.nanmean(s[m, li])), n=int(np.isfinite(s[m, li]).sum())))
        pd.DataFrame(sims).to_csv(OUT / 'state_similarity.csv', index=False)
    except Exception as e: print('state similarity skipped:', repr(e))
    res = dict(label='addendum 22 Part A (LOCKED)', n_papers=n, by_group=PP.group.value_counts().to_dict(), verdicts=V, readings=read)
    (OUT / 'a22A_results.json').write_text(json.dumps(res, indent=1, default=float))
    fmt = lambda r: f"{r.est:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}]" + (f" Holm [{r.holm_lo:+.3f}, {r.holm_hi:+.3f}] p_H {r.p_holm:.3f}" if r.in_F else '')
    L = ['# Addendum 22 Part A — invariance ladder (LOCKED confirmatory)', '', f'n = {n} papers {res["by_group"]}; team bootstrap {NB}, seed {SEED}; Holm over F = {F_LAYERS}.', '',
         '## Readings', ''] + [f'- {x}' for x in read] + ['', f'K2 surface-robust from: {V["K2_surface_robust_from"]}', '', '## Contrasts', '']
    for c in ('K1', 'K2', 'K3', 'K4', 'K4c'):
        L.append(f'### {c}'); L += [f'- L{int(r.layer)}: {fmt(r)}' for r in Ct[Ct.contrast == c].itertuples()]; L.append('')
    L += ['## R curves (all papers)', '', Rt[Rt.group == 'all'].pivot(index='layer', columns='variant', values='est').round(3).to_string(), '']
    (OUT / 'report.md').write_text('\n'.join(L) + '\n')
    print(json.dumps(res, indent=1, default=float)); print('DONE', OUT)


if __name__ == '__main__':
    main()
