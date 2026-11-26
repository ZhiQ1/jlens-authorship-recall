#!/usr/bin/env python3
"""Addendum 28 (TODO #6): X4 with topic-matched partners. How much of the L8 surname signal is a topic prior?
Pre-registration: 391_groups/config/prereg_addendum28.md (sha256 checked by work/analyze).

Everything is the published X4 title source (381_stage13.do_pscope / stage13_b2_ps_gpu.tok_scores, imported by path, not
edited): source = last title token of the X4 authors prompt (no year) of a paper; injected (block output) at the X placeholder
of the three PS_TARGETS prompts, the 7 PS_LAYERS (8..56) in ONE forward of batch 7 (element i = layer i); scores = per-token
log10(1/rank) of A's answer tokens (year, first author's Stage 10 name tokens with roles, field).
Sources per paper A: self (A), partner (the published X4 partner: same field, same title length, no shared surname),
topic_mpnet / topic_bert (same field, nearest title under all-mpnet-base-v2 / bert-base-uncased mean-pooled, not A's team,
no shared surname; frozen from summary_explore_x4_source_20261121/partners.csv).
  freeze   (CPU) -> raw/a28_freeze/pairs.parquet + freeze.json (shard list = Stage 11 sample shards holding these papers)
  work     (GPU) --shards 0,1 | --all ; per shard raw/a28/shard_XXX.parquet (+ meta_XXX.json written last = done marker)
  tiny     (CPU) random 2-layer Qwen3 with the real tokenizer, 3 papers, -> raw/a28_test_tiny
  analyze  (CPU) -> summary_a28/
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'; R13 = J / '381_stage13'
PREREG = G / 'config/prereg_addendum28.md'
FREEZE = G / 'raw/a28_freeze'; OUT = Path(os.environ.get('A28_OUT', G / 'raw/a28')); SUMM = G / 'summary_a28'
SRC_PARTNERS = R13 / 'summary_explore_x4_source_20261121/partners.csv'
SOURCES = ['self', 'partner', 'topic_mpnet', 'topic_bert']
NB, SEED = 2000, 27


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lock_sha():
    lj = G / 'config/addendum28_lock.json'
    if not lj.exists(): return None
    want = json.loads(lj.read_text())['sha256']
    if sha(PREREG) != want: raise SystemExit('ADDENDUM 28 CHANGED since lock')
    return want


def mods():
    b2 = load(H / '13_stage13/stage13_b2_ps_gpu.py', 'b2ps_frozen_for_a28')
    return b2, b2.s13, b2.x2


def freeze(a):
    b2, s13, _ = mods()
    if (FREEZE / 'pairs.parquet').exists() and not a.force: raise SystemExit('freeze exists')
    p = pd.read_csv(SRC_PARTNERS)
    smp, pairs = s13.sample()
    p = p[p.paper_id.isin(pairs.index)].copy()
    assert (p.partner.values == pairs.loc[p.paper_id].partner.values).all(), 'cached partner differs from config/pairs.parquet'
    p = p.merge(smp[['paper_id', 'group', 'citation_bin', 'shard']], on='paper_id', how='left')
    papers = pd.read_parquet(J / '351_stage10/cohort/papers.parquet', columns=['paper_id', 'citations'])
    sys.path.insert(0, str(H / '13_stage13')); import stage13_cpu as c13
    _, team = c13.group_folds(papers.paper_id.to_numpy()); p['team'] = p.paper_id.map(dict(zip(papers.paper_id, team)))
    for c in ('topic_mpnet', 'topic_bert'):
        assert p[c].notna().all(), c
        assert (p[c] != p.paper_id).all()
    FREEZE.mkdir(parents=True, exist_ok=True); p.to_parquet(FREEZE / 'pairs.parquet', index=False)
    info = dict(n=len(p), by_group=p.group.value_counts().to_dict(), shards=sorted(int(x) for x in p.shard.unique()),
                cos_mean={c: float(p[c].mean()) for c in ('cos_bert_cur', 'cos_mpnet_cur', 'cos_bert_topic', 'cos_mpnet_topic')},
                same_topic_partner_share=float((p.topic_mpnet == p.topic_bert).mean()),
                source_sha256=sha(SRC_PARTNERS), pairs_sha256=sha(FREEZE / 'pairs.parquet'), script_sha256=sha(__file__))
    (FREEZE / 'freeze.json').write_text(json.dumps(info, indent=1)); log('FREEZE', json.dumps(info))


def do_shard(C, k, P, b2, s13, PL, F, papers_subset=None):
    tgt = b2.targets(C); rows = []
    sub = F[F.shard == k] if papers_subset is None else papers_subset
    for r in sub.itertuples():
        A = r.paper_id
        if A not in C.ctx: continue
        ans = s13.ps_answers(C, A, P)
        arole = {'author': b2.first_author_roles(A, len(ans['author'])), 'year': ['na'] * len(ans['year']), 'field': ['na'] * len(ans['field'])}
        src_ids = {'self': A, 'partner': r.partner, 'topic_mpnet': r.topic_mpnet, 'topic_bert': r.topic_bert}
        for who in SOURCES:
            title = P.loc[src_ids[who]].title
            ids0, it, ic = s13.build(C.tok, title, 'authors', []); acts = C.record(ids0, PL)
            st = {l: acts[l][it] for l in PL}
            for t, (ids, xi) in tgt.items():
                V = b2.tok_scores(C, ids, xi, ans[t], st, PL)
                for bi, l in enumerate(PL):
                    for aj, x in enumerate(V[bi]): rows.append((A, src_ids[who], who, t, l, aj, arole[t][aj], float(x)))
    T = pd.DataFrame(rows, columns=['paper_id', 'src_paper', 'who', 'target', 'layer', 'ans_j', 'ans_role', 'nlr'])
    return T


def work(a):
    b2, s13, x2 = mods()
    if not a.tiny: lock_sha()
    F = pd.read_parquet(FREEZE / 'pairs.parquet'); fz = json.loads((FREEZE / 'freeze.json').read_text())
    shards = fz['shards'] if a.all else [int(x) for x in a.shards.split(',')]
    out = OUT if not a.tiny else G / 'raw/a28_test_tiny'; out.mkdir(parents=True, exist_ok=True)
    left = b2.s11.slurm_minutes_left(); budget = a.max_minutes if left is None else min(a.max_minutes, left - 6)
    t0 = time.monotonic(); C = None; last = 0.0
    todo = [k for k in shards if not (out / f'meta_{k:03d}.json').exists()]
    log(f'a28 work: {len(todo)} of {len(shards)} shards to do, budget {budget} min')
    for k in todo:
        if (out / f'meta_{k:03d}.json').exists(): continue
        if (time.monotonic() - t0) / 60 + 1.5 * max(last, 240) / 60 > budget: log('time budget reached before shard', k); break
        if C is None:
            if a.tiny: s13.PS_LAYERS = [0, 1]
            C = x2.tiny_ctx() if a.tiny else s13.Ctx()
        P = C.papers.set_index('paper_id'); PL = list(s13.PS_LAYERS)
        t1 = time.monotonic()
        sub = None
        if a.tiny: sub = F[F.paper_id.isin(P.index) & F.partner.isin(P.index) & F.topic_mpnet.isin(P.index) & F.topic_bert.isin(P.index)].head(3)
        T = do_shard(C, k, P, b2, s13, PL, F, sub)
        f = out / f'shard_{k:03d}.parquet'; tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.parquet'); T.to_parquet(tmp, index=False); os.replace(tmp, f)
        chk = check_vs_b2(T, k) if not a.tiny else {}
        meta = dict(shard=k, n_papers=int(T.paper_id.nunique()), n_rows=len(T), secs=time.monotonic() - t1, created=time.strftime('%Y-%m-%dT%H:%M:%S'),
                    job=os.environ.get('SLURM_JOB_ID', 'local'), script_sha256=sha(__file__), check=chk, env=getattr(C, 'env', {}))
        (out / f'meta_{k:03d}.json').write_text(json.dumps(meta, indent=1, default=str)); last = time.monotonic() - t1
        log(f'a28 shard {k:03d} papers={meta["n_papers"]} rows={len(T)} {last:.0f}s check={chk.get("status")}', json.dumps(chk)[:300])
        if a.tiny: break
    return C


def check_vs_b2(T, k):
    """WARN only: self and partner title-source per-token scores vs the stored b2_pscope shard (same protocol, other job)."""
    try:
        f = R13 / f'raw/b2_pscope/shard_{k:03d}.parquet'
        if not f.exists(): return dict(status='WARN (no b2 shard)')
        b = pd.read_parquet(f); b = b[b.src_kind == 'title'].set_index(['paper_id', 'who', 'target', 'layer', 'ans_j']).nlr
        t = T[T.who.isin(['self', 'partner'])].set_index(['paper_id', 'who', 'target', 'layer', 'ans_j']).nlr
        j = t.to_frame('n').join(b.rename('o'), how='inner'); d = (j.n - j.o).abs()
        out = dict(rows=int(len(j)), exact_share=float((d < 1e-12).mean()), max_abs=float(d.max()), mean_abs=float(d.mean()))
        out['status'] = 'OK' if out['exact_share'] >= 0.75 and out['mean_abs'] <= 0.05 else 'WARN'
        return out
    except Exception as e:
        return dict(status=f'WARN (check failed {e!r})')


# ------------------------------------------------------------------ analysis
def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    return adj


def analyze(a):
    want = lock_sha()
    F = pd.read_parquet(FREEZE / 'pairs.parquet'); fz = json.loads((FREEZE / 'freeze.json').read_text())
    src = Path(a.raw) if a.raw else OUT
    miss = [k for k in fz['shards'] if not (src / f'meta_{k:03d}.json').exists()]
    if miss and not a.allow_missing: raise SystemExit(f'missing shards {miss}')
    T = pd.concat([pd.read_parquet(src / f'shard_{k:03d}.parquet') for k in fz['shards'] if (src / f'shard_{k:03d}.parquet').exists()])
    out = Path(a.out) if a.out else SUMM; out.mkdir(parents=True, exist_ok=True)
    # per paper x source x layer x answer: mean nlr over answer tokens
    def agg(df, name):
        g = df.groupby(['paper_id', 'who', 'layer']).nlr.mean().unstack('who'); g.columns.name = None; g['ans'] = name; return g.reset_index()
    parts = [agg(T[T.target == 'author'], 'first_author'), agg(T[(T.target == 'author') & (T.ans_role == 'surname_first')], 'surname_first'),
             agg(T[T.target == 'year'], 'year'), agg(T[T.target == 'field'], 'field')]
    D = pd.concat(parts)
    for s in ('partner', 'topic_mpnet', 'topic_bert'): D[f'D_{s}'] = D['self'] - D[s]
    D = D.merge(F[['paper_id', 'team', 'group', 'citation_bin']], on='paper_id', how='left')
    D.to_csv(out / 'D_per_paper.csv', index=False)
    teams = F.drop_duplicates('paper_id').set_index('paper_id').team
    pids = sorted(D.paper_id.unique()); codes, uniq = pd.factorize(teams.reindex(pids))
    W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]; pos = {p: i for i, p in enumerate(pids)}
    rows = []
    for (ans, l), d in D.groupby(['ans', 'layer']):
        idx = np.array([pos[p] for p in d.paper_id]); Wd = W[:, idx]
        for s in ('partner', 'topic_mpnet', 'topic_bert'):
            x = d[f'D_{s}'].to_numpy(float); ok = np.isfinite(x); b = (Wd[:, ok] @ x[ok]) / Wd[:, ok].sum(1)
            p = float(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean())))
            rows.append(dict(ans=ans, layer=int(l), contrast=f'D_{s}', n=int(ok.sum()), est=float(x[ok].mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), p=p))
        for s in ('topic_mpnet', 'topic_bert'):
            xt, xr = d[f'D_{s}'].to_numpy(float), d['D_partner'].to_numpy(float); ok = np.isfinite(xt) & np.isfinite(xr)
            bt, br = Wd[:, ok] @ xt[ok], Wd[:, ok] @ xr[ok]
            with np.errstate(divide='ignore', invalid='ignore'): b = bt / br
            rows.append(dict(ans=ans, layer=int(l), contrast=f'P_{s} = D_{s} / D_partner', n=int(ok.sum()), est=float(xt[ok].sum() / xr[ok].sum()),
                             lo=float(np.nanpercentile(b, 2.5)), hi=float(np.nanpercentile(b, 97.5)), p=np.nan))
    R = pd.DataFrame(rows)
    for s in ('topic_mpnet', 'topic_bert'):
        m = (R.contrast == f'D_{s}') & (R.ans == 'surname_first'); R.loc[m, 'p_holm_layers'] = holm(R.loc[m, 'p'].to_numpy())
    R.to_csv(out / 'contrasts.csv', index=False)
    # target - control within citation bins (Stage 10 weights)
    tc = []
    for (ans, l), d in D.groupby(['ans', 'layer']):
        for s in ('partner', 'topic_mpnet'):
            est = 0; wsum = 0; bs = np.zeros(NB)
            for cb, e in d.groupby('citation_bin'):
                t_, c_ = e[e.group == 'target'], e[e.group == 'control']
                if len(t_) < 3 or len(c_) < 3: continue
                w = len(t_) * len(c_) / (len(t_) + len(c_)); it = np.array([pos[p] for p in t_.paper_id]); ic = np.array([pos[p] for p in c_.paper_id])
                xt, xc = t_[f'D_{s}'].to_numpy(float), c_[f'D_{s}'].to_numpy(float)
                est += w * (xt.mean() - xc.mean()); bs += w * ((W[:, it] @ xt) / W[:, it].sum(1) - (W[:, ic] @ xc) / W[:, ic].sum(1)); wsum += w
            if wsum: tc.append(dict(ans=ans, layer=int(l), contrast=f'T-C of D_{s}', est=est / wsum, lo=float(np.percentile(bs / wsum, 2.5)), hi=float(np.percentile(bs / wsum, 97.5))))
    TC = pd.DataFrame(tc); TC.to_csv(out / 'target_minus_control.csv', index=False)
    # verdict (prereg): primary P = D_topic_mpnet / D_partner, surname_first @ L8
    L0 = 8 if (R.layer == 8).any() else int(R.layer.min())   # 8 in the real run; tiny model has layers 0/1
    pr = R[(R.contrast.str.startswith('P_topic_mpnet')) & (R.ans == 'surname_first') & (R.layer == L0)].iloc[0]
    dt = R[(R.contrast == 'D_topic_mpnet') & (R.ans == 'surname_first') & (R.layer == L0)].iloc[0]
    if dt.hi < 0: verdict = 'reversed (D_topic < 0)'
    elif pr.lo >= 0.7: verdict = 'mostly paper-specific (P lower CI >= 0.7)'
    elif pr.hi <= 0.3: verdict = 'mostly topic prior (P upper CI <= 0.3)'
    else: verdict = 'mixed (P reported with CI)'
    sens = R[(R.contrast.str.startswith('P_topic_bert')) & (R.ans == 'surname_first') & (R.layer == L0)].iloc[0]
    res = dict(label='addendum 28 (LOCKED)', addendum_sha256=want, n_papers=int(D.paper_id.nunique()), missing_shards=miss, verdict=verdict,
               primary=dict(P=float(pr.est), lo=float(pr.lo), hi=float(pr.hi), D_topic=float(dt.est), D_topic_lo=float(dt.lo), D_topic_hi=float(dt.hi)),
               sensitivity_bert=dict(P=float(sens.est), lo=float(sens.lo), hi=float(sens.hi)))
    (out / 'a28_results.json').write_text(json.dumps(res, indent=1, default=float))
    L = ['# Addendum 28 — X4 with topic-matched partners', '', f'verdict: **{verdict}**', '', json.dumps(res, indent=1, default=float), '',
         '## Contrasts (team bootstrap 2,000, seed 27)', '', R.to_string(index=False, float_format=lambda v: f'{v:.4f}'), '', '## Target − control within citation bins', '', TC.to_string(index=False, float_format=lambda v: f'{v:.4f}')]
    (out / 'report.md').write_text('\n'.join(L) + '\n'); log('ANALYSIS', json.dumps(res, default=float))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['freeze', 'work', 'tiny', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--all', action='store_true'); ap.add_argument('--max-minutes', type=float, default=38)
    ap.add_argument('--force', action='store_true'); ap.add_argument('--raw'); ap.add_argument('--out'); ap.add_argument('--allow-missing', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': a.tiny = True; a.all = False; a.shards = '0'; work(a)
    else: a.tiny = False; {'freeze': freeze, 'work': work, 'analyze': analyze}[a.cmd](a)
