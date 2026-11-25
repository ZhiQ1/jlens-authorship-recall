#!/usr/bin/env python3
"""Addendum 33 (LOCKED): X4 surname signal — confirmatory test of the paper-specific part beyond topic.
Prereg: 391_groups/config/prereg_addendum33.md (sha256 checked by work/analyze); notes: config/addendum33_notes.json.
Built on 19_todo/a28_x4topic.py (addendum 28) and 13_stage13/explore_x4_source_20261121.py (partners, flags, text model),
imported by path, not edited.
  freeze   (CPU) -> raw/a33_freeze/pairs.parquet + freeze.json   (eligible sample, partners, exclusion flags, shards)
  text     (CPU) -> raw/a33_freeze/text_D.parquet                (BERT text-only baseline, D_text per paper)
  work     (GPU) --shards 0,999 | --task i --ntask n            per shard raw/a33/shard_XXX.parquet + meta_XXX.json (done marker)
  tiny     (CPU) 2-layer random Qwen3, real tokenizer, 3 papers -> raw/a33_test_tiny
  analyze  (CPU) -> summary_a33/
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'; R13 = J / '381_stage13'; R10 = J / '351_stage10'
PREREG = G / 'config/prereg_addendum33.md'; LOCK = G / 'config/addendum33_lock.json'
FREEZE = Path(os.environ.get('A33_FREEZE', G / 'raw/a33_freeze')); OUT = Path(os.environ.get('A33_OUT', G / 'raw/a33'))
SUMM = Path(os.environ.get('A33_SUMM', G / 'summary_a33'))
SOURCES = ['self', 'partner', 'topic_mpnet', 'topic_bert']; L0_SOURCES = ['self', 'topic_mpnet']
NB, SEED, SHARD_N, CHECK_SHARD = 2000, 33, 64, 999
DELTA12, DELTA3 = 0.010, 0.020


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lock_sha():
    want = json.loads(LOCK.read_text())['sha256']
    if sha(PREREG) != want: raise SystemExit('ADDENDUM 33 CHANGED since lock')
    return want


def mods():
    b2 = load(H / '13_stage13/stage13_b2_ps_gpu.py', 'b2ps_frozen_for_a33')
    return b2, b2.s13, b2.x2


def explorer():
    os.environ.pop('TINY', None)
    return load(H / '13_stage13/explore_x4_source_20261121.py', 'x4src_frozen_for_a33')


# ------------------------------------------------------------------ freeze
def freeze(a):
    lock_sha()
    if (FREEZE / 'pairs.parquet').exists() and not a.force: raise SystemExit('freeze exists')
    b2, s13, _ = mods(); X = explorer()
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13_for_a33')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').reset_index(drop=True)
    folds, team_all = c13.group_folds(papers.paper_id.to_numpy())
    smp11 = pd.read_parquet(J / '361_stage11/config/sample.parquet')
    tok = s10_tok(s13); _, toks = s13.s11.cohort(); ctx = s13.s11.contexts_of(toks)
    cnt = dict(cohort=len(papers))
    E = papers[~papers.paper_id.isin(smp11.paper_id)]; cnt['outside_stage11_sample'] = len(E)
    E = E[E.group.isin(['target', 'control'])]; cnt['target_or_control'] = len(E)
    E = E[E.paper_id.isin(ctx.keys()) & E.field.notna()]; cnt['with_context_and_field'] = len(E)
    ids = E.paper_id.tolist(); pos = {p: i for i, p in enumerate(papers.paper_id)}
    Eb, Em = X.embeddings(papers); Ub, Um = X.unit(Eb), Em / (np.linalg.norm(Em, axis=1, keepdims=True) + 1e-9)
    tp = {'bert': X.topic_partners(papers, team_all, Ub, ids), 'mpnet': X.topic_partners(papers, team_all, Um, ids)}
    log('topic partners done')
    P = papers.set_index('paper_id')
    L = {pid: len(s13.title_span(tok, P.loc[pid].title)[0]) for pid in papers.paper_id}
    sur = {pid: X.surnames(P.loc[pid].authors) for pid in papers.paper_id}
    rng = np.random.default_rng(SEED); by_field = papers.groupby('field').paper_id.apply(list).to_dict(); rows = []
    for pid in ids:
        f = P.loc[pid].field
        cand = [q for q in by_field[f] if q != pid and L[q] == L[pid] and not (sur[q] & sur[pid]) and q in ctx]
        q = cand[rng.integers(len(cand))] if cand else None
        rows.append(dict(paper_id=pid, partner=q, topic_mpnet=tp['mpnet'].get(pid, (None, np.nan))[0], cos_mpnet_topic=tp['mpnet'].get(pid, (None, np.nan))[1],
                         topic_bert=tp['bert'].get(pid, (None, np.nan))[0], cos_bert_topic=tp['bert'].get(pid, (None, np.nan))[1], n_title_tokens=L[pid]))
    d = pd.DataFrame(rows)
    cnt['no_partner_any'] = int(d[['partner', 'topic_mpnet', 'topic_bert']].isna().any(axis=1).sum())
    d = d.dropna(subset=['partner', 'topic_mpnet', 'topic_bert']).reset_index(drop=True); cnt['with_all_partners'] = len(d)
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'role', 'token_id'])
    first = nt[nt.author_index == 0]; sf = first[first.role == 'surname_first'].drop_duplicates('paper_id').set_index('paper_id').token_id.to_dict()
    import transformers
    qtok = transformers.AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
    F = X.flags(papers, d.paper_id.tolist(), qtok, sf).reindex(d.paper_id)
    d['flag_a'] = F.a_surname_in_title.to_numpy(bool); d['flag_b'] = F.b_surname_token_in_title.to_numpy(bool); d['flag_c'] = F.c_eponym.to_numpy(bool)
    d['excluded'] = d.flag_a | d.flag_b | d.flag_c; d['has_surname_first'] = d.paper_id.isin(sf.keys())
    cnt.update(flag_a=int(d.flag_a.sum()), flag_b=int(d.flag_b.sum()), flag_c=int(d.flag_c.sum()), excluded_any=int(d.excluded.sum()),
               primary_n=int((~d.excluded).sum()), primary_with_surname_first=int((~d.excluded & d.has_surname_first).sum()))
    d = d.merge(papers[['paper_id', 'group', 'citation_bin', 'field']], on='paper_id', how='left')
    d['team'] = d.paper_id.map(dict(zip(papers.paper_id, team_all)))
    order = np.random.default_rng(SEED).permutation(len(d)); d = d.iloc[order].reset_index(drop=True); d['shard'] = np.arange(len(d)) // SHARD_N
    cnt['by_group_all'] = d.group.value_counts().to_dict(); cnt['by_group_primary'] = d[~d.excluded].group.value_counts().to_dict()
    FREEZE.mkdir(parents=True, exist_ok=True); d.to_parquet(FREEZE / 'pairs.parquet', index=False)
    info = dict(counts=cnt, shards=sorted(int(x) for x in d.shard.unique()), check_shard=CHECK_SHARD, pairs_sha256=sha(FREEZE / 'pairs.parquet'),
                script_sha256=sha(__file__), prereg_sha256=lock_sha(), frozen_at=time.strftime('%Y-%m-%dT%H:%M:%S'),
                cos_mean=dict(mpnet=float(d.cos_mpnet_topic.mean()), bert=float(d.cos_bert_topic.mean())), same_topic_partner_share=float((d.topic_mpnet == d.topic_bert).mean()))
    (FREEZE / 'freeze.json').write_text(json.dumps(info, indent=1, default=int)); log('FREEZE', json.dumps(info, default=int))


def s10_tok(s13): return s13.s10.tokenizer()


# ------------------------------------------------------------------ text baseline (CPU)
def text(a):
    lock_sha(); X = explorer(); c13 = load(H / '13_stage13/stage13_cpu.py', 'c13_for_a33')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet').reset_index(drop=True)
    folds, _ = c13.group_folds(papers.paper_id.to_numpy()); pos = {p: i for i, p in enumerate(papers.paper_id)}
    d = pd.read_parquet(FREEZE / 'pairs.parquet')
    if a.limit: d = d.head(a.limit)
    Eb, _ = X.embeddings(papers); feats = {'bert': (Eb - Eb.mean(0)) / (Eb.std(0) + 1e-6)}
    nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'role', 'token_id']); first = nt[nt.author_index == 0]
    sf = first[first.role == 'surname_first'].drop_duplicates('paper_id').set_index('paper_id').token_id
    targets = [('surname_first', papers.paper_id.map(sf).fillna(-2).astype(int).to_numpy(), 0.03)]
    ia = np.array([pos[p] for p in d.paper_id]); kinds = {k: np.array([pos[q] for q in d[k]]) for k in ('topic_mpnet', 'partner', 'topic_bert')}
    TX, PC = X.text_models(papers, folds, feats, targets, kinds, ia)
    out = pd.DataFrame({'paper_id': d.paper_id, **{f'Dtext_{k}': TX[('bert', 'surname_first', k)] for k in kinds}})
    out.to_parquet(FREEZE / ('text_D.parquet' if not a.limit else 'text_D_test.parquet'), index=False); PC.to_csv(FREEZE / 'text_posctrl.csv', index=False)
    log('TEXT', PC.to_dict(orient='records'), out.drop(columns='paper_id').mean().to_dict())


# ------------------------------------------------------------------ GPU work
def emb_state(C, ids, it):
    """input hidden state of block 0 (token embedding, no context) at position it"""
    torch = C.torch; got = {}
    def pre(mod, args, kwargs):
        h = args[0] if args else kwargs['hidden_states']; got['h'] = h[0, it].detach().clone()
    hd = C.model.layers[0].register_forward_pre_hook(pre, with_kwargs=True)
    try:
        with torch.inference_mode(): C.model.forward(torch.tensor([ids], device=C.model.input_device))
    finally: hd.remove()
    return got['h']


def do_papers(C, sub, P, b2, s13, PL, sources, with_l0=True):
    tgt = b2.targets(C); rows = []
    for r in sub.itertuples():
        A = r.paper_id
        if A not in C.ctx: continue
        ans = s13.ps_answers(C, A, P)
        arole = {'author': b2.first_author_roles(A, len(ans['author'])), 'year': ['na'] * len(ans['year']), 'field': ['na'] * len(ans['field'])}
        src_ids = {'self': A, 'partner': r.partner, 'topic_mpnet': getattr(r, 'topic_mpnet', None), 'topic_bert': getattr(r, 'topic_bert', None)}
        for who in sources:
            title = P.loc[src_ids[who]].title
            ids0, it, ic = s13.build(C.tok, title, 'authors', []); acts = C.record(ids0, PL)
            st = {l: acts[l][it] for l in PL}
            for t, (ids, xi) in tgt.items():
                V = b2.tok_scores(C, ids, xi, ans[t], st, PL)
                for bi, l in enumerate(PL):
                    for aj, x in enumerate(V[bi]): rows.append((A, src_ids[who], who, t, l, aj, arole[t][aj], float(x)))
            if with_l0 and who in L0_SOURCES:
                e = emb_state(C, ids0, it); st0 = {l: e for l in PL}; ids, xi = tgt['author']
                V = b2.tok_scores(C, ids, xi, ans['author'], st0, PL)
                for bi, l in enumerate(PL):
                    for aj, x in enumerate(V[bi]): rows.append((A, src_ids[who], who + '_L0', 'author', l, aj, arole['author'][aj], float(x)))
    return pd.DataFrame(rows, columns=['paper_id', 'src_paper', 'who', 'target', 'layer', 'ans_j', 'ans_role', 'nlr'])


def check_vs_b2(T):
    """WARN only: self/partner title-source per-token scores vs stored raw/b2_pscope shard 0 (published X4 protocol)."""
    try:
        b = pd.read_parquet(R13 / 'raw/b2_pscope/shard_000.parquet'); b = b[b.src_kind == 'title'].set_index(['paper_id', 'who', 'target', 'layer', 'ans_j']).nlr
        t = T[T.who.isin(['self', 'partner'])].set_index(['paper_id', 'who', 'target', 'layer', 'ans_j']).nlr
        j = t.to_frame('n').join(b.rename('o'), how='inner'); dd = (j.n - j.o).abs()
        out = dict(rows=int(len(j)), papers=int(j.reset_index().paper_id.nunique()), exact_share=float((dd < 1e-12).mean()), max_abs=float(dd.max()), mean_abs=float(dd.mean()))
        out['status'] = 'OK' if out['exact_share'] >= 0.75 and out['mean_abs'] <= 0.05 else 'WARN'
        return out
    except Exception as e:
        return dict(status=f'WARN (check failed {e!r})')


def work(a):
    b2, s13, x2 = mods()
    if not a.tiny: lock_sha()
    F = pd.read_parquet(FREEZE / 'pairs.parquet'); fz = json.loads((FREEZE / 'freeze.json').read_text())
    if a.ntask: shards = [k for k in fz['shards'] if k % a.ntask == a.task] + ([CHECK_SHARD] if a.task == 0 else [])
    else: shards = [int(x) for x in a.shards.split(',')]
    out = OUT if not a.tiny else G / 'raw/a33_test_tiny'; out.mkdir(parents=True, exist_ok=True)
    left = b2.s11.slurm_minutes_left(); budget = a.max_minutes if left is None else min(a.max_minutes, left - 6)
    t0 = time.monotonic(); C = None; last = 0.0
    todo = [k for k in shards if not (out / f'meta_{k:03d}.json').exists()]
    log(f'a33 work: {len(todo)} of {len(shards)} shards to do {todo}, budget {budget} min')
    for k in todo:
        if (out / f'meta_{k:03d}.json').exists(): continue
        if (time.monotonic() - t0) / 60 + 1.5 * max(last, 240) / 60 > budget: log('time budget reached before shard', k); break
        if C is None:
            if a.tiny: s13.PS_LAYERS = [0, 1]
            C = x2.tiny_ctx() if a.tiny else s13.Ctx()
        P = C.papers.set_index('paper_id'); PL = list(s13.PS_LAYERS); t1 = time.monotonic()
        if k == CHECK_SHARD:
            smp, pairs = s13.sample(); s0 = smp[smp.shard == 0].paper_id; s0 = [p for p in s0 if p in pairs.index][:50]
            sub = pd.DataFrame(dict(paper_id=s0, partner=pairs.loc[s0].partner.values))
            T = do_papers(C, sub, P, b2, s13, PL, ['self', 'partner'], with_l0=False)
            chk = check_vs_b2(T) if not a.tiny else {}
        else:
            sub = F[F.shard == k]
            if a.tiny: sub = sub[sub.paper_id.isin(P.index)].head(3)
            T = do_papers(C, sub, P, b2, s13, PL, SOURCES)
            chk = {}
        f = out / f'shard_{k:03d}.parquet'; tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.parquet'); T.to_parquet(tmp, index=False); os.replace(tmp, f)
        meta = dict(shard=k, n_papers=int(T.paper_id.nunique()), n_rows=len(T), secs=time.monotonic() - t1, created=time.strftime('%Y-%m-%dT%H:%M:%S'),
                    job=os.environ.get('SLURM_JOB_ID', 'local'), script_sha256=sha(__file__), check=chk, env=getattr(C, 'env', {}))
        (out / f'meta_{k:03d}.json').write_text(json.dumps(meta, indent=1, default=str)); last = time.monotonic() - t1
        log(f'a33 shard {k:03d} papers={meta["n_papers"]} rows={len(T)} {last:.0f}s check={chk.get("status")}', json.dumps(chk)[:300])
        if a.tiny: break
    return C


# ------------------------------------------------------------------ analysis
def team_W(teams):
    codes, uniq = pd.factorize(pd.Series(teams))
    return np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def pval(b): b = b[np.isfinite(b)]; return float(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean()))) if len(b) else np.nan


def bmean(W, x):
    ok = np.isfinite(x); return float(x[ok].mean()), (W[:, ok] @ x[ok]) / W[:, ok].sum(1), int(ok.sum())


def bz(W, x):
    n = W.sum(1); m = (W @ x) / n; sd = np.sqrt(np.maximum((W @ x ** 2) / n - m ** 2, 1e-12)); return float(x.mean() / x.std()), m / sd


def btc(W, x, grp, cbin):
    ok = np.isfinite(x); x, grp, cbin, W = x[ok], grp[ok], cbin[ok], W[:, ok]; num = np.zeros(NB); den = np.zeros(NB); pnum = pden = 0.0
    for b in np.unique(cbin):
        it, ic = (cbin == b) & (grp == 'target'), (cbin == b) & (grp == 'control')
        if it.sum() < 3 or ic.sum() < 3: continue
        nt, nc = W[:, it].sum(1), W[:, ic].sum(1); mt = (W[:, it] @ x[it]) / np.maximum(nt, 1e-9); mc = (W[:, ic] @ x[ic]) / np.maximum(nc, 1e-9)
        w = nt * nc / np.maximum(nt + nc, 1e-9); num += w * (mt - mc); den += w
        w0 = it.sum() * ic.sum() / (it.sum() + ic.sum()); pnum += w0 * (x[it].mean() - x[ic].mean()); pden += w0
    return (pnum / pden if pden else np.nan), num / np.maximum(den, 1e-9), int(ok.sum())


def analyze(a):
    want = lock_sha() if not a.tiny_analysis else 'tiny'
    F = pd.read_parquet(FREEZE / 'pairs.parquet'); fz = json.loads((FREEZE / 'freeze.json').read_text())
    src = Path(a.raw) if a.raw else OUT; out = Path(a.out) if a.out else SUMM; out.mkdir(parents=True, exist_ok=True)
    need = fz['shards'] + [CHECK_SHARD]; miss = [k for k in need if not (src / f'meta_{k:03d}.json').exists()]
    if miss and not a.allow_missing: raise SystemExit(f'missing shards {miss}')
    T = pd.concat([pd.read_parquet(src / f'shard_{k:03d}.parquet') for k in fz['shards'] if (src / f'shard_{k:03d}.parquet').exists()])
    chk = json.loads((src / f'meta_{CHECK_SHARD:03d}.json').read_text()).get('check', {}) if (src / f'meta_{CHECK_SHARD:03d}.json').exists() else {'status': 'WARN (check shard missing)'}
    def agg(df, name):
        g = df.groupby(['paper_id', 'who', 'layer']).nlr.mean().unstack('who'); g.columns.name = None; g['ans'] = name; return g.reset_index()
    au = T[T.target == 'author']
    D = pd.concat([agg(au, 'first_author'), agg(au[au.ans_role == 'surname_first'], 'surname_first'), agg(T[T.target == 'year'], 'year'), agg(T[T.target == 'field'], 'field')])
    for s in ('partner', 'topic_mpnet', 'topic_bert'): D[f'D_{s}'] = D['self'] - D[s]
    if 'self_L0' in D and 'topic_mpnet_L0' in D: D['D_topic_mpnet_L0'] = D['self_L0'] - D['topic_mpnet_L0']
    D = D.merge(F[['paper_id', 'team', 'group', 'citation_bin', 'excluded']], on='paper_id', how='left'); D.to_csv(out / 'D_per_paper.csv', index=False)
    TX = pd.read_parquet(FREEZE / 'text_D.parquet') if (FREEZE / 'text_D.parquet').exists() else None
    L0 = 8 if (D.layer == 8).any() else int(D.layer.min())
    def sel(ans, l, excl=False):
        d = D[(D.ans == ans) & (D.layer == l)]
        return d if excl else d[~d.excluded.astype(bool)]
    # ---------------- primaries
    d = sel('surname_first', L0).reset_index(drop=True); W = team_W(d.team.to_numpy())
    rows = []
    e1, b1, n1 = bmean(W, d.D_topic_mpnet.to_numpy(float)); rows.append(dict(test='T1 D_topic_mpnet (surname_first, L8)', est=e1, b=b1, n=n1))
    if TX is not None:
        dm = d.merge(TX[['paper_id', 'Dtext_topic_mpnet']], on='paper_id', how='left'); q = dm.D_topic_mpnet.to_numpy(float); t = dm.Dtext_topic_mpnet.to_numpy(float)
        ok = np.isfinite(q) & np.isfinite(t); Wk = W[:, ok]; zq, bq = bz(Wk, q[ok]); zt, bt = bz(Wk, t[ok])
        rows.append(dict(test='T2 standardised Qwen D_topic − BERT text D_topic', est=zq - zt, b=bq - bt, n=int(ok.sum()), z_qwen=zq, z_text=zt))
    else:
        rows.append(dict(test='T2 standardised Qwen D_topic − BERT text D_topic', est=np.nan, b=np.full(NB, np.nan), n=0))
    e3, b3, n3 = btc(W, d.D_topic_mpnet.to_numpy(float), d.group.to_numpy(), d.citation_bin.astype(str).to_numpy())
    rows.append(dict(test='T3 target − control of D_topic_mpnet within citation bins', est=e3, b=b3, n=n3))
    ps = np.array([pval(r['b']) for r in rows]); order = np.argsort(np.where(np.isfinite(ps), ps, 1)); m = 3; adj = np.empty(m); run = 0
    for rk, i in enumerate(order): run = max(run, min(1, (m - rk) * (ps[i] if np.isfinite(ps[i]) else 1))); adj[i] = run
    for rk, i in enumerate(order):
        al = 0.05 / (m - rk); b = rows[i]['b']; b = b[np.isfinite(b)]
        rows[i].update(p=float(ps[i]), p_holm=float(adj[i]), lo=float(np.percentile(b, 2.5)) if len(b) else np.nan, hi=float(np.percentile(b, 97.5)) if len(b) else np.nan,
                       holm_lo=float(np.percentile(b, 100 * al / 2)) if len(b) else np.nan, holm_hi=float(np.percentile(b, 100 * (1 - al / 2))) if len(b) else np.nan)
    R = pd.DataFrame([{k: v for k, v in r.items() if k != 'b'} for r in rows]); R.to_csv(out / 'a33_tests.csv', index=False)
    t1, t2, t3 = R.iloc[0], R.iloc[1], R.iloc[2]
    if t1.holm_hi < 0: v1 = 'reversed (T1 Holm CI entirely < 0)'
    elif t1.holm_lo > 0 and t2.holm_lo > 0: v1 = 'paper-specific surname signal confirmed (T1 and T2 Holm CI > 0)'
    elif t1.holm_lo > 0: v1 = 'beyond topic, but not beyond a text model (T1 > 0, T2 CI includes 0)'
    elif t1.holm_lo > -DELTA12 and t1.holm_hi < DELTA12: v1 = 'topic prior explains it (decided: T1 Holm CI within ±0.010)'
    else: v1 = 'inconclusive (T1 CI includes 0 but extends beyond ±0.010)'
    if t3.holm_lo > 0: v3 = 'recognition-specific (T3 Holm CI > 0)'
    elif t3.holm_lo > -DELTA3 and t3.holm_hi < DELTA3: v3 = 'no recognition difference ≥ 0.02 (T3 Holm CI within ±0.02)'
    else: v3 = 'recognition: inconclusive'
    # ---------------- secondary (descriptive)
    sec = []
    for ans in ('surname_first', 'first_author', 'year', 'field'):
        for l in sorted(D.layer.unique()):
            dd = sel(ans, l).reset_index(drop=True); Wd = team_W(dd.team.to_numpy())
            for s in ('partner', 'topic_mpnet', 'topic_bert', 'topic_mpnet_L0'):
                if f'D_{s}' not in dd or dd[f'D_{s}'].notna().sum() == 0: continue
                e, b, n = bmean(Wd, dd[f'D_{s}'].to_numpy(float)); sec.append(dict(ans=ans, layer=int(l), contrast=f'D_{s}', n=n, est=e, lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5)))
            xt, xr = dd.D_topic_mpnet.to_numpy(float), dd.D_partner.to_numpy(float); ok = np.isfinite(xt) & np.isfinite(xr)
            if ok.sum():
                with np.errstate(divide='ignore', invalid='ignore'): bb = (Wd[:, ok] @ xt[ok]) / (Wd[:, ok] @ xr[ok])
                sec.append(dict(ans=ans, layer=int(l), contrast='P = ΣD_topic_mpnet / ΣD_random', n=int(ok.sum()), est=xt[ok].sum() / xr[ok].sum(), lo=np.nanpercentile(bb, 2.5), hi=np.nanpercentile(bb, 97.5)))
            e, b, n = btc(Wd, dd.D_topic_mpnet.to_numpy(float), dd.group.to_numpy(), dd.citation_bin.astype(str).to_numpy())
            sec.append(dict(ans=ans, layer=int(l), contrast='T−C of D_topic_mpnet', n=n, est=e, lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5)))
    dl = sel('surname_first', L0, excl=True).reset_index(drop=True); Wl = team_W(dl.team.to_numpy()); e, b, n = bmean(Wl, dl.D_topic_mpnet.to_numpy(float))
    sec.append(dict(ans='surname_first', layer=L0, contrast='T1 with exclusions lifted', n=n, est=e, lo=np.percentile(b, 2.5), hi=np.percentile(b, 97.5)))
    S = pd.DataFrame(sec); S.to_csv(out / 'a33_secondary.csv', index=False)
    res = dict(label='addendum 33 (LOCKED)', addendum_sha256=want, freeze_counts=fz['counts'], missing_shards=miss, check_50paper=chk,
               verdict_paper_specific=v1, verdict_recognition=v3, tests=R.to_dict(orient='records'))
    (out / 'a33_results.json').write_text(json.dumps(res, indent=1, default=float))
    fmt = lambda v: f'{v:.4f}'
    Lr = ['# Addendum 33 (LOCKED) — X4 surname signal, confirmatory', '', f'**Paper-specific:** {v1}', f'**Recognition:** {v3}', '',
          f'prereg sha256 {want}; missing shards {miss}; 50-paper protocol check {json.dumps(chk)}', '', '## Sample (frozen before any run)', '', json.dumps(fz['counts'], indent=1, default=int), '',
          '## Primary tests (team bootstrap 2,000, seed 33; Holm over T1–T3; Holm CI at α/(m − rank))', '', R.to_string(index=False, float_format=fmt), '',
          '## Secondary (descriptive)', '', S.to_string(index=False, float_format=fmt)]
    (out / 'report.md').write_text('\n'.join(Lr) + '\n'); log('ANALYSIS', json.dumps(res, default=float)[:2000])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['freeze', 'text', 'work', 'tiny', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--task', type=int, default=0); ap.add_argument('--ntask', type=int, default=0)
    ap.add_argument('--max-minutes', type=float, default=38); ap.add_argument('--force', action='store_true'); ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--raw'); ap.add_argument('--out'); ap.add_argument('--allow-missing', action='store_true'); ap.add_argument('--tiny-analysis', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': a.tiny = True; a.ntask = 0; a.shards = a.shards if a.shards != '0' else '0'; work(a)
    else: a.tiny = False; {'freeze': freeze, 'text': text, 'work': work, 'analyze': analyze}[a.cmd](a)
