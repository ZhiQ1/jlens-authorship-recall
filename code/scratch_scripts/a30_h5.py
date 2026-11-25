#!/usr/bin/env python3
"""Addendum 30 (H5 direction asymmetry, "reversal curse" for paper authors). Locked prereg: 391_groups/config/prereg_addendum30.md.

freeze   (CPU) A + B rows of the a16 B sample; citation prefix from the true authors and from a mismatched paper (same field and
         citation bin, no shared surname, seed 30); 5 matched false titles = the Stage 10 false_0..4 titles -> raw/a30_freeze/
precheck (CPU) freeze invariants
work     (GPU) per a16 shard: teacher-forced mean log-prob per title token for 12 sequences per paper (true prefix x {true, false_0..4},
         mismatched prefix x {true, false_0..4}) + greedy title generation after the true prefix -> raw/a30/{tf,gen}/shard_KKK.parquet,
         meta/shard_KKK.json (written last = done marker; existing shards skipped)
tiny     (CPU) whole pipeline on a random 64-layer Qwen3 with the real tokenizer, 2 shards x 2 papers, + skip-if-done
analyze  R1 (A - B within bins of F_id), R2 (A: forward success - reverse success), R3 (A: F_id -> mc p_true | log citations),
         Holm over R1, R2; team bootstrap 2,000 (seed 30) -> 391_groups/summary_a30/
"""
import argparse, hashlib, importlib.util, json, os, re, sys, time, unicodedata
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'
PREREG = G / 'config/prereg_addendum30.md'
FREEZE = Path(os.environ.get('A30_FREEZE', G / 'raw/a30_freeze')); OUT = Path(os.environ.get('A30_OUT', G / 'raw/a30'))
SUMM = Path(os.environ.get('A30_SUM', G / 'summary_a30'))
SAMPLE = G / 'config/prereg16_sample_B.parquet'; SAMPLE_SHA = '117a9127'
FALSES = [f'false_{k}' for k in range(5)]; SEED = 30; NB = 2000; MAX_TITLE_TOK = 40; MAX_AUTH = 10; MAX_NEW = 48


def _load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


a16 = _load(H / '14_groups/prereg16_a16.py', 'a16_frozen_for_a30'); s10 = a16.s10; R10 = a16.R10
s11 = _load(H / '11_stage11/361_stage11.py', 's11_frozen_for_a30')


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def lock_check():
    lk = json.load(open(G / 'config/addendum30_lock.json'))
    h = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    if h != lk['sha256']: raise SystemExit(f'addendum 30 changed after lock: {h}')
    return h


def cite_author(a):
    w = a.split()
    if not w: return ''
    sur = w[-1]; ini = ' '.join(x[0] + '.' for x in w[:-1] if x and x[0].isalpha())
    return f'{sur}, {ini}' if ini else sur


def cite_prefix(authors, year):
    au = a16.authors_of(authors); parts = [cite_author(a) for a in au[:MAX_AUTH]]
    s = ', '.join(p for p in parts if p) + (', et al.' if len(au) > MAX_AUTH else '')
    return f'{s} ({year}).'


def title_of_prompt(text):
    m = re.search(r'titled "(.*)" \(', text, flags=re.S)
    return m.group(1) if m else None


def norm_words(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.findall(r'[a-z0-9]+', s)


def token_f1(gen, true):
    g, t = norm_words(gen), norm_words(true)
    if not g or not t: return 0.0
    from collections import Counter
    c = Counter(g) & Counter(t); k = sum(c.values())
    if k == 0: return 0.0
    p, r = k / len(g), k / len(t); return 2 * p * r / (p + r)


def gen_title(full):
    t = a16.cut_text(full).strip()
    m = re.search(r'\.\s', t + ' ')
    t = t[:m.start()] if m else t
    return t.strip().strip('"“”\'').strip()


# ------------------------------------------------------------------ freeze (CPU)
def freeze(a):
    import pandas as pd
    if (FREEZE / 'freeze.parquet').exists() and not a.force: raise SystemExit(f'{FREEZE} exists (use --force)')
    if not hashlib.sha256(SAMPLE.read_bytes()).hexdigest().startswith(SAMPLE_SHA): raise SystemExit('a16 B sample changed')
    S = pd.read_parquet(SAMPLE); S = S[S.grp.isin(['A', 'B'])].copy()
    papers, _ = s11.cohort(); P = papers.set_index('paper_id')
    pr = {c: s10.condition_prompts(R10, papers, c)[0] for c in FALSES}
    P['_sur'] = P.authors.map(lambda s: {a16.words(x)[-1] for x in a16.authors_of(s) if a16.words(x)})
    rng = np.random.default_rng(SEED); rows, excl = [], []
    for r in S.sort_values('paper_id').itertuples():
        me = P.loc[r.paper_id]
        fts = [title_of_prompt(pr[c][r.paper_id][0]) for c in FALSES]
        if any(t is None for t in fts): excl.append(dict(paper_id=r.paper_id, reason='false title not parsed')); continue
        cand = P[(P.field == me.field) & (P.citation_bin == me.citation_bin) & (P.index != r.paper_id)]
        cand = cand[cand._sur.map(lambda s: not (s & me._sur))]
        if not len(cand): excl.append(dict(paper_id=r.paper_id, reason='no mismatched donor')); continue
        d = cand.index[int(rng.integers(len(cand)))]
        rows.append(dict(paper_id=r.paper_id, grp=r.grp, shard=int(r.shard), team=int(r.team), field=me.field, citation_bin=me.citation_bin,
                         citations=float(me.citations), mc_p_true=float(me.mc_team_p_true), year=str(me.year), title=me.title,
                         prefix=cite_prefix(me.authors, me.year), donor_id=d, prefix_mis=cite_prefix(P.loc[d, 'authors'], me.year),
                         false_titles=json.dumps(fts), n_authors=len(a16.authors_of(me.authors))))
    D = pd.DataFrame(rows); FREEZE.mkdir(parents=True, exist_ok=True); D.to_parquet(FREEZE / 'freeze.parquet', index=False)
    info = dict(n=len(D), by_grp=D.grp.value_counts().to_dict(), excluded=excl, shards=sorted(D.shard.unique().tolist()),
                sample_sha256=hashlib.sha256(SAMPLE.read_bytes()).hexdigest(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                prereg_sha256=lock_check() if PREREG.exists() and (G / 'config/addendum30_lock.json').exists() else None,
                time=time.strftime('%Y-%m-%dT%H:%M:%S'))
    json.dump(info, open(FREEZE / 'freeze.json', 'w'), indent=1, default=str)
    log('FREEZE', json.dumps({k: info[k] for k in ('n', 'by_grp', 'shards')}, default=str), 'excluded', len(excl))


def precheck(a):
    import pandas as pd
    D = pd.read_parquet(FREEZE / 'freeze.parquet'); ok = {}
    ok['n by grp'] = D.grp.value_counts().to_dict(); ok['donor != self'] = bool((D.donor_id != D.paper_id).all())
    ok['prefix differs from mismatched'] = float((D.prefix != D.prefix_mis).mean())
    ok['5 false titles each'] = bool(D.false_titles.map(lambda s: len(json.loads(s)) == 5).all())
    ok['false != true title'] = float(np.mean([r.title not in json.loads(r.false_titles) for r in D.itertuples()]))
    ok['example'] = D.iloc[0][['prefix', 'title', 'prefix_mis']].to_dict()
    assert cite_author('Wei Xing Zheng') == 'Zheng, W. X.' and token_f1('A b c', 'a B d') > 0.6
    log('PRECHECK', json.dumps(ok, default=str)); return ok


# ------------------------------------------------------------------ GPU side
class Ctx:
    def __init__(self, tiny=False):
        import torch, pandas as pd
        self.torch = torch; self.D = pd.read_parquet(FREEZE / 'freeze.parquet')
        self.hf, self.model, self.tok = a16.load_model(tiny=tiny); self.dev = next(self.hf.parameters()).device

    def enc(self, s): return self.tok(s, add_special_tokens=False)['input_ids']


def tf_scores(C, seqs, starts):
    """mean log-prob per continuation token for each (ids, start) with right padding in one batch."""
    torch = C.torch; T = max(len(s) for s in seqs); pad = C.tok.pad_token_id
    x = torch.full((len(seqs), T), pad, dtype=torch.long); m = torch.zeros((len(seqs), T), dtype=torch.long)
    for i, s in enumerate(seqs): x[i, :len(s)] = torch.tensor(s); m[i, :len(s)] = 1
    with torch.inference_mode():
        lg = C.hf(input_ids=x.to(C.dev), attention_mask=m.to(C.dev)).logits
    out = []
    for i, (s, st) in enumerate(zip(seqs, starts)):
        pos = torch.arange(st - 1, len(s) - 1, device=lg.device); tgt = torch.tensor(s[st:], device=lg.device)
        lp = torch.log_softmax(lg[i, pos].float(), dim=-1).gather(1, tgt[:, None])[:, 0]
        out.append((float(lp.mean()), int(len(tgt))))
    return out


def do_paper(C, r):
    fts = json.loads(r.false_titles); titles = [r.title] + fts
    rows = []
    for which, pre in (('true', r.prefix), ('mis', r.prefix_mis)):
        p_ids = C.enc(pre); seqs, starts = [], []
        for t in titles:
            c_ids = C.enc(' ' + t)[:MAX_TITLE_TOK]; seqs.append(p_ids + c_ids); starts.append(len(p_ids))
        sc = tf_scores(C, seqs, starts)
        joint_eq = C.enc(pre + ' ' + r.title)[:len(p_ids) + MAX_TITLE_TOK] == seqs[0]
        for k, (t, (lp, n)) in enumerate(zip(['true'] + FALSES, sc)):
            rows.append(dict(paper_id=r.paper_id, grp=r.grp, prefix=which, title_cond=t, lp=lp, n_tok=n, joint_tokenisation_equal=bool(joint_eq)))
    g = a16.generate(C.hf, C.tok, [C.enc(r.prefix)], C.torch, bs=1, max_new=MAX_NEW, stop_nl=True)[0]
    gt = gen_title(g[1])
    grow = dict(paper_id=r.paper_id, grp=r.grp, gen_text=g[1], gen_title=gt, stop=g[2], f1=token_f1(gt, r.title),
                exact=norm_words(gt) == norm_words(r.title))
    return rows, grow


def out_path(kind, k, ext='parquet'): return OUT / kind / f'shard_{k:03d}.{ext}'


def do_shard(C, k):
    import pandas as pd
    if out_path('meta', k, 'json').exists(): log(f'shard {k} skip (exists)'); return False
    rows = C.D[C.D.shard == k]; t0 = time.time(); T_, G_ = [], []
    for r in rows.itertuples():
        t, g = do_paper(C, r); T_ += t; G_.append(g)
    tdf, gdf = pd.DataFrame(T_), pd.DataFrame(G_)
    for kind, df in (('tf', tdf), ('gen', gdf)):
        out_path(kind, k).parent.mkdir(parents=True, exist_ok=True); df.to_parquet(out_path(kind, k), index=False)
    chk = dict(papers=len(rows), joint_tokenisation_equal_share=float(tdf.joint_tokenisation_equal.mean()) if len(tdf) else None)
    meta = dict(shard=k, seconds=time.time() - t0, checks=chk, host=os.uname().nodename, job=os.environ.get('SLURM_JOB_ID'),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out_path('meta', k, 'json').parent.mkdir(parents=True, exist_ok=True); json.dump(meta, open(out_path('meta', k, 'json'), 'w'), indent=1)
    log(f'shard {k} done papers={len(rows)} {time.time() - t0:.0f}s', json.dumps(chk)); return True


def parse_shards(s):
    out = []
    for p in str(s).split(','):
        if '-' in p: a_, b_ = p.split('-'); out += list(range(int(a_), int(b_) + 1))
        elif p: out.append(int(p))
    return out


def work(a, C=None):
    if C is None: lock_check(); C = Ctx()
    t_start = time.time(); per = []
    for k in parse_shards(a.shards):
        if k not in set(C.D.shard): continue
        if a.max_minutes and per and (time.time() - t_start + 1.3 * max(per)) / 60 > a.max_minutes: log('budget stop before shard', k); break
        t0 = time.time()
        if do_shard(C, k): per.append(time.time() - t0)


def missing():
    import pandas as pd
    D = pd.read_parquet(FREEZE / 'freeze.parquet'); return [k for k in sorted(D.shard.unique()) if not out_path('meta', k, 'json').exists()]


# ------------------------------------------------------------------ analysis
def team_W(teams, nb=NB, seed=SEED):
    import pandas as pd
    codes, uniq = pd.factorize(pd.Series(teams))
    cnt = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=nb).astype(float)
    return cnt[:, codes]


def ci(b):
    b = b[np.isfinite(b)]
    return (float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))) if len(b) else (float('nan'), float('nan'))
def pval(b):
    b = b[np.isfinite(b)]
    return float(min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))) if len(b) else float('nan')


def within_bin(df, val, W):
    """sum_bins w_b (mean_A - mean_B), w_b = nA nB / (nA + nB) normalised; point + bootstrap (team weights W over df rows)."""
    est_num = 0.0; est_den = 0.0; bnum = np.zeros(W.shape[0]); bden = 0.0
    for b, g in df.groupby('citation_bin'):
        ia = (g.grp == 'A').to_numpy(); ib = (g.grp == 'B').to_numpy()
        if ia.sum() == 0 or ib.sum() == 0: continue
        idx = g.index.to_numpy(); x = g[val].to_numpy(float); w = ia.sum() * ib.sum() / (ia.sum() + ib.sum())
        est_num += w * (x[ia].mean() - x[ib].mean()); est_den += w
        Wa = W[:, idx[ia]]; Wb = W[:, idx[ib]]
        with np.errstate(invalid='ignore', divide='ignore'):
            ma = (Wa @ x[ia]) / Wa.sum(1); mb = (Wb @ x[ib]) / Wb.sum(1)
        bnum += w * (ma - mb); bden += w
    if est_den == 0: return float('nan'), np.full(W.shape[0], np.nan)
    return est_num / est_den, bnum / bden


def analyze(a=None):
    import pandas as pd
    h = lock_check()
    D = pd.read_parquet(FREEZE / 'freeze.parquet').set_index('paper_id')
    miss = missing()
    tf = pd.concat([pd.read_parquet(f) for f in sorted((OUT / 'tf').glob('shard_*.parquet'))])
    gen = pd.concat([pd.read_parquet(f) for f in sorted((OUT / 'gen').glob('shard_*.parquet'))]).set_index('paper_id')
    piv = tf.pivot_table(index=['paper_id', 'prefix'], columns='title_cond', values='lp')
    spec = (piv['true'] - piv[FALSES].mean(1)).unstack('prefix')
    P = D.loc[spec.index].copy(); P['F_spec'] = spec['true']; P['F_spec_mis'] = spec['mis']; P['F_id'] = P.F_spec - P.F_spec_mis
    P['fwd_success'] = (gen.reindex(P.index).f1 >= 0.8).astype(float); P['fwd_f1'] = gen.reindex(P.index).f1; P['fwd_exact'] = gen.reindex(P.index).exact.astype(float)
    rev = pd.concat([pd.read_parquet(f) for f in sorted((G / 'raw/a16_B/gen_v2').glob('shard_*.parquet'))])
    rev = rev[rev.cond == 'F0'].drop_duplicates('paper_id').set_index('paper_id')
    P['rev_success'] = rev.reindex(P.index).any_full.astype(float)
    P = P.reset_index().rename(columns={'index': 'paper_id'})
    W = team_W(P.team.to_numpy())
    rows = []
    # R1
    e1, b1 = within_bin(P, 'F_id', W); rows.append(dict(test='R1 A - B within bins of F_id', est=e1, lo=ci(b1)[0], hi=ci(b1)[1], p=pval(b1), n=len(P)))
    # R2
    A_ = P[P.grp == 'A']; WA = W[:, A_.index.to_numpy()]; d = (A_.fwd_success - A_.rev_success).to_numpy(float); ok = np.isfinite(d)
    e2 = float(d[ok].mean()); b2 = (WA[:, ok] @ d[ok]) / WA[:, ok].sum(1)
    rows.append(dict(test='R2 A: forward success - reverse success', est=e2, lo=ci(b2)[0], hi=ci(b2)[1], p=pval(b2), n=int(ok.sum())))
    ps = np.array([rows[0]['p'], rows[1]['p']]); order = np.argsort(ps); adj = np.empty(2); run = 0
    for r_, i in enumerate(order): run = max(run, min(1, (2 - r_) * ps[i])); adj[i] = run
    for i in range(2): rows[i]['p_holm'] = float(adj[i])
    # Holm CIs at alpha/(m - rank)
    for r_, i in enumerate(order):
        al = 0.05 / (2 - r_); b = b1 if i == 0 else b2; b = b[np.isfinite(b)]
        rows[i]['holm_lo'] = float(np.percentile(b, 100 * al / 2)) if len(b) else float('nan'); rows[i]['holm_hi'] = float(np.percentile(b, 100 * (1 - al / 2))) if len(b) else float('nan')
    # R3 (secondary): A, z(p_true) ~ z(F_id) + z(log10(1+cit)), weighted LS per draw
    A3 = A_.dropna(subset=['F_id', 'mc_p_true']); z = lambda v: (v - v.mean()) / v.std()
    X = np.column_stack([np.ones(len(A3)), z(A3.F_id), z(np.log10(1 + A3.citations))]); y = z(A3.mc_p_true).to_numpy(float)
    beta = np.linalg.lstsq(X, y, rcond=None)[0][1]; W3 = W[:, A3.index.to_numpy()]; bs = []
    for w in W3:
        sw = np.sqrt(w); bs.append(np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0][1])
    bs = np.array(bs); rows.append(dict(test='R3 (secondary) A: F_id -> p_true | log citations (std slope)', est=float(beta), lo=ci(bs)[0], hi=ci(bs)[1], p=pval(bs), n=len(A3)))
    R = pd.DataFrame(rows); SUMM.mkdir(parents=True, exist_ok=True); R.to_csv(SUMM / 'a30_tests.csv', index=False)
    desc = P.groupby('grp')[['F_spec', 'F_spec_mis', 'F_id', 'fwd_success', 'fwd_f1', 'fwd_exact', 'rev_success']].mean()
    desc.to_csv(SUMM / 'a30_descriptive.csv'); P.to_csv(SUMM / 'a30_perpaper.csv', index=False)
    r1 = R.iloc[0]; r2 = R.iloc[1]
    s1 = r1.holm_lo > 0; s2 = r2.holm_lo > 0; u1 = r1.lo > 0; u2 = r2.lo > 0
    if r2.holm_hi < 0: verdict = 'Reversed (reverse direction easier than forward)'
    elif s1 and s2: verdict = 'H5 supported (asymmetry, recognition-linked)'
    elif s2: verdict = 'Asymmetry without recognition link'
    elif s1: verdict = 'Recognition-linked but symmetric'
    elif u1 or u2: verdict = 'Borderline (met only without the Holm correction)'
    else: verdict = 'Not supported'
    res = dict(verdict=verdict, n=len(P), by_grp=P.grp.value_counts().to_dict(), missing_shards=miss, addendum_sha256=h,
               tests=R.to_dict(orient='records'), descriptive=desc.to_dict())
    json.dump(res, open(SUMM / 'a30_results.json', 'w'), indent=1, default=float)
    L = [f'# Addendum 30 (LOCKED) — H5 direction asymmetry: {verdict}', '', f'Papers {len(P)} ({res["by_grp"]}); missing shards {miss}; prereg sha256 {h}.', '',
         R.to_string(index=False), '', '## Descriptive (group means)', '', desc.to_string()]
    (SUMM / 'a30_report.md').write_text('\n'.join(L) + '\n'); log('A30 ANALYSIS', verdict)
    return res


# ------------------------------------------------------------------ tiny
def tiny(a):
    import pandas as pd
    global OUT, SUMM
    root = Path(a.root); OUT = root / 'raw'; SUMM = root / 'summary'
    C = Ctx(tiny=True)
    keep = C.D[C.D.grp == 'A'].head(2).paper_id.tolist() + C.D[C.D.grp == 'B'].head(2).paper_id.tolist()
    C.D = C.D[C.D.paper_id.isin(keep)].copy(); C.D['shard'] = [0, 1, 0, 1]
    work(argparse.Namespace(shards='0-1', max_minutes=None), C); work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    tf = pd.concat([pd.read_parquet(out_path('tf', k)) for k in (0, 1)]); gen = pd.concat([pd.read_parquet(out_path('gen', k)) for k in (0, 1)])
    ok = {'tf rows = 12 per paper': len(tf) == 12 * 4, 'gen rows': len(gen) == 4, 'lp finite': bool(np.isfinite(tf.lp).all()),
          'joint tokenisation share reported': 'joint_tokenisation_equal' in tf}
    print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['freeze', 'precheck', 'work', 'tiny', 'remaining', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=None)
    ap.add_argument('--root'); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'remaining': m = missing(); print(len(m), 'missing', m); return
    {'freeze': freeze, 'precheck': precheck, 'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
