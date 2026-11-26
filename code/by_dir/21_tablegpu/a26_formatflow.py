#!/usr/bin/env python3
"""Addendum 26 (LOCKED 2026-11-22, 391_groups/config/prereg_addendum26.md): does the ':' format interfere downstream?

Sample = the addendum 23 freeze (391_groups/raw/a23_freeze/freeze.parquet, 582 papers, 12 shards), M3/X1 templates.
Layers: {X, X+4, X+8} ∩ {4,8,16,24,32,40,48,52,56}, X = addendum 23's locked format-locking layer per pair
(authors<-year, authors<-field), given as A26_X="year:L,field:L" (read from summary_a23 by the submitter; 48 if addendum 23
reports 'never fixed at the colon').
work  (GPU) per paper and title (true + 5 Stage 10 false titles): donor ':' residuals (year / field prompt, same title) at the
      layers; authors prompt teacher-forced for every true author, batch = [base, (donor, layer) patches]; the last prompt
      position (':') residual at block l replaced by the donor's -> ranks of every name token (final logits).
      Reverse (true title only): year / field prompt with the authors ':' residual; readout = mean log-prob of the true year /
      field label tokens. -> raw/a26/shard_KKK.parquet (+ .json marker written last)
tiny  (CPU) random 64-layer model, 2 papers, checks (patch with own state == base), skip-if-done
analyze (CPU) spec = S_true - mean_k S_false_k per paper; dspec(l) per donor; Holm over the 2 primary tests at l = X; team
      bootstrap 2,000 seed 26 -> 391_groups/summary_a26/
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'
ADD = G / 'config/prereg_addendum26.md'; ADD_SHA = '83b27d54c9745226b7dcb3c2afa45a64305550e7c935f84414b7bfd38fa2092c'
FZ = G / 'raw/a23_freeze'; OUT = Path(os.environ.get('A26_OUT', G / 'raw/a26')); SEED = 26
GRID = [4, 8, 16, 24, 32, 40, 48, 52, 56]
TASKS = {'authors': 'Who are the authors of the paper titled "{t}"?\nAuthors:',
         'year': 'In what year was the research paper titled "{t}" published?\nYear:',
         'field': 'In what research field is the paper titled "{t}"?\nField:'}
DONORS = ['year', 'field']


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check_lock():
    if sha(ADD) != ADD_SHA: raise SystemExit(f'ADDENDUM 26 CHANGED {sha(ADD)}')
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def xlayers():
    spec = os.environ.get('A26_X')
    if not spec: raise SystemExit('A26_X not set: read X from 391_groups/summary_a23 first (prereg §2)')
    X = {k: int(v) for k, v in (p.split(':') for p in spec.split(','))}
    return {d: [l for l in GRID if l in (X[d], X[d] + 4, X[d] + 8) and l <= 56] for d in DONORS}, X


class Ctx:
    def __init__(self, tiny=None):
        import torch, pandas as pd
        self.torch = torch; s11 = load(H / '11_stage11/361_stage11.py', 's11_a26'); self.s10 = s10 = s11.s10
        self.D = pd.read_parquet(FZ / 'freeze.parquet')
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        ft = pd.read_parquet(s11.R10 / 'cohort/conditions/false_titles.parquet')
        self.false = ft.sort_values('k').groupby('paper_id').donor_title.apply(list).to_dict()
        if tiny is None:
            a16 = load(H / '14_groups/prereg16_a16.py', 'a16_a26'); self.hf, self.model, self.tok = a16.load_model()
        else: self.hf, self.model, self.tok = tiny
        self.blocks = self.hf.model.layers; self.dev = next(self.hf.parameters()).device; self.rep = {}
        self.hooks = []
        for l in GRID:
            def hook(mod, inp, out, l=l):
                h = out if torch.is_tensor(out) else out[0]
                r = self.rep.get(l)
                if r is not None:
                    pos, vec, rows = r
                    for i in rows: h[i, pos] = vec[i].to(h.device, h.dtype)
                return out
            self.hooks.append(self.blocks[l].register_forward_hook(hook))

    def enc(self, s): return self.tok(s).input_ids

    def colon_states(self, ids, layers):
        torch = self.torch; rec = {}
        hs = []
        for l in layers:
            def grab(mod, inp, out, l=l):
                h = out if torch.is_tensor(out) else out[0]; rec[l] = h[0, len(ids) - 1].detach().clone(); return out
            hs.append(self.blocks[l].register_forward_hook(grab))
        try:
            with torch.inference_mode(): self.hf(input_ids=torch.tensor([ids], device=self.dev))
        finally:
            for h in hs: h.remove()
        return rec

    def batch_logits(self, seqs, pos_list, rep):
        torch = self.torch; self.rep = rep
        try:
            with torch.inference_mode(): lg = self.hf(input_ids=torch.tensor(seqs, device=self.dev)).logits
        finally: self.rep = {}
        return [lg[i, p].float() for i, p in enumerate(pos_list)]


def do_paper(C, r, LS, own_check=False):
    torch = C.torch; s10 = C.s10; rows = []
    titles = [('true', r.title)] + [(f'false_{k}', t) for k, t in enumerate(C.false.get(r.paper_id, [])[:5])]
    layers = sorted({l for d in DONORS for l in LS[d]})
    for tname, t in titles:
        pa = C.enc(TASKS['authors'].format(t=t)); T = len(pa)
        don = {d: C.colon_states(C.enc(TASKS[d].format(t=t)), LS[d]) for d in DONORS}
        conds = [('base', None, None)] + [(f'{d}_L{l}', d, l) for d in DONORS for l in LS[d]]
        if own_check: own = C.colon_states(pa, layers[:1]); conds.append(('own', 'own', layers[0]))
        for ai, rids, name in C.ctx[r.paper_id]:
            seq = pa + name[:-1]; pos = [T - 1 + j for j in range(len(name))]
            rep = {}
            for i, (cn, d, l) in enumerate(conds):
                if d is None: continue
                vec = own[l] if d == 'own' else don[d][l]
                rep.setdefault(l, [T - 1, {}, []]); rep[l][1][i] = vec; rep[l][2].append(i)
            rep = {l: (v[0], v[1], v[2]) for l, v in rep.items()}
            lgs = C.batch_logits([seq] * len(conds), [pos] * len(conds), rep)
            gold = torch.tensor(name, device=lgs[0].device)
            for (cn, d, l), lg in zip(conds, lgs):
                rk, ti, lp, t1 = s10.score(lg, gold, torch)
                for j in range(len(name)):
                    rows.append(dict(paper_id=r.paper_id, title=tname, cond=cn, author_index=ai, token_index=j, row_id=int(rids[j]), rank=int(rk[j])))
    # reverse readouts (true title)
    p = C.P.loc[r.paper_id]; ca = C.colon_states(C.enc(TASKS['authors'].format(t=r.title)), layers)
    rev = []
    for d, ans in (('year', str(p.year)), ('field', str(p.field))):
        pd_ = C.enc(TASKS[d].format(t=r.title)); g = C.tok(' ' + ans, add_special_tokens=False).input_ids
        seq = pd_ + g[:-1]; pos = [len(pd_) - 1 + j for j in range(len(g))]
        conds = [('base', None)] + [(f'authors_L{l}', l) for l in LS[d]]
        rep = {}
        for i, (cn, l) in enumerate(conds):
            if l is None: continue
            rep.setdefault(l, [len(pd_) - 1, {}, []]); rep[l][1][i] = ca[l]; rep[l][2].append(i)
        lgs = C.batch_logits([seq] * len(conds), [pos] * len(conds), {l: tuple(v) for l, v in rep.items()})
        for (cn, l), lg in zip(conds, lgs):
            lp = torch.log_softmax(lg, -1).gather(1, torch.tensor(g, device=lg.device)[:, None])[:, 0]
            rev.append(dict(paper_id=r.paper_id, recipient=d, cond=cn, mean_logprob=float(lp.mean())))
    return rows, rev


def work(a, C=None):
    import pandas as pd
    check_lock(); LS, X = xlayers(); C = C or Ctx(); t0 = time.time(); last = 0
    for k in [int(x) for x in a.shards.split(',')]:
        mk = OUT / f'shard_{k:03d}.json'
        if mk.exists(): log(f'shard {k} skip (exists)'); continue
        if a.max_minutes and (time.time() - t0 + 1.3 * last) / 60 > a.max_minutes: log('budget stop before', k); break
        t1 = time.time(); R, V = [], []
        for r in C.D[C.D.shard == k].itertuples():
            x, y = do_paper(C, r, LS, own_check=(k == 0)); R += x; V += y
        OUT.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(R).to_parquet(OUT / f'shard_{k:03d}.parquet', index=False); pd.DataFrame(V).to_parquet(OUT / f'rev_{k:03d}.parquet', index=False)
        df = pd.DataFrame(R); chk = {}
        if (df.cond == 'own').any():
            b = df[df.cond == 'base'].set_index(['paper_id', 'title', 'row_id'])['rank']; o = df[df.cond == 'own'].set_index(['paper_id', 'title', 'row_id'])['rank']
            chk['own_equals_base_share'] = float((o == b.reindex(o.index)).mean())
        last = time.time() - t1
        json.dump(dict(shard=k, seconds=last, X=X, layers=LS, checks=chk, job=os.environ.get('SLURM_JOB_ID'), host=os.uname().nodename), open(mk, 'w'))
        log(f'shard {k} done {last:.0f}s', chk)


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global OUT
    check_lock(); OUT = Path(a.root); OUT.mkdir(parents=True, exist_ok=True); os.environ['A26_X'] = 'year:48,field:48'
    s11 = load(H / '11_stage11/361_stage11.py', 's11_a26t'); s10 = s11.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = Ctx(tiny=(hf, model, tok)); C.D = C.D[C.D.shard == 0].head(2).copy()
    work(argparse.Namespace(shards='0', max_minutes=None), C); work(argparse.Namespace(shards='0', max_minutes=None), C)
    m = json.load(open(OUT / 'shard_000.json')); df = pd.read_parquet(OUT / 'shard_000.parquet')
    ok = {'own==base (>=0.95, numerics)': (m['checks'].get('own_equals_base_share') or 0) >= 0.95, 'conds': set(df.cond) >= {'base', 'year_L48', 'field_L48'},
          'titles 6': df.title.nunique() == 6, 'patch changes ranks': bool((df[df.cond == 'year_L48']['rank'].to_numpy() != df[df.cond == 'base']['rank'].to_numpy()).any()),
          'rev written': (OUT / 'rev_000.parquet').exists()}
    print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def analyze(a):
    import pandas as pd
    check_lock(); LS, X = xlayers(); D = pd.read_parquet(FZ / 'freeze.parquet').set_index('paper_id')
    miss = [k for k in sorted(D.shard.unique()) if not (OUT / f'shard_{k:03d}.json').exists()]
    if miss: raise SystemExit(f'missing shards {miss}')
    df = pd.concat([pd.read_parquet(OUT / f'shard_{k:03d}.parquet') for k in sorted(D.shard.unique())])
    df['nlr'] = -np.log10(df['rank'].astype(float))
    pp = df.groupby(['paper_id', 'title', 'cond']).nlr.mean().unstack('title')
    fcols = [c for c in pp.columns if c.startswith('false_')]
    spec = (pp['true'] - pp[fcols].mean(1)).unstack('cond')
    codes, uniq = pd.factorize(D.team.reindex(spec.index)); W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=2000).astype(float)[:, codes]
    rows = []
    for d in DONORS:
        for l in LS[d]:
            x = (spec[f'{d}_L{l}'] - spec['base']).to_numpy(); ok = np.isfinite(x); bt = (W[:, ok] @ x[ok]) / W[:, ok].sum(1)
            rows.append(dict(donor=d, layer=l, primary=l == X[d], dspec=float(x[ok].mean()), lo=float(np.percentile(bt, 2.5)), hi=float(np.percentile(bt, 97.5)),
                             p=float(min(1, 2 * min((bt <= 0).mean(), (bt >= 0).mean()))), boot=bt, n=int(ok.sum())))
    R = pd.DataFrame(rows); pr = R[R.primary].copy()
    pr['p_holm'] = np.minimum(1, pr.p.rank(method='first').map({1: 2, 2: 1}) * pr.p) if len(pr) == 2 else pr.p
    al = {1: 0.025, 2: 0.05}; ranks = pr.p.rank(method='first').astype(int)
    pr['holm_lo'] = [float(np.percentile(b, 100 * al[rk] / 2)) for b, rk in zip(pr.boot, ranks)]
    pr['holm_hi'] = [float(np.percentile(b, 100 * (1 - al[rk] / 2))) for b, rk in zip(pr.boot, ranks)]
    if (pr.holm_hi < 0).any(): verdict = 'Format gates the author signal'
    elif (pr.holm_lo > 0).any(): verdict = 'Reversed'
    elif ((pr.holm_lo >= -0.02) & (pr.holm_hi <= 0.02)).all(): verdict = 'Format independent of the author signal'
    else: verdict = 'Undecided'
    rev = pd.concat([pd.read_parquet(OUT / f'rev_{k:03d}.parquet') for k in sorted(D.shard.unique())])
    rv = rev.pivot_table(index=['paper_id', 'recipient'], columns='cond', values='mean_logprob')
    out = G / 'summary_a26'; out.mkdir(parents=True, exist_ok=True)
    R.drop(columns='boot').to_csv(out / 'a26_dspec.csv', index=False); pr.drop(columns='boot').to_csv(out / 'a26_primary.csv', index=False)
    rvs = rv.sub(rv['base'], axis=0).groupby(level='recipient').mean(); rvs.to_csv(out / 'a26_reverse.csv')
    (out / 'a26_results.json').write_text(json.dumps(dict(verdict=verdict, X=X, layers=LS, addendum_sha=ADD_SHA, n=int(len(spec))), indent=1))
    (out / 'report.md').write_text(f'# Addendum 26 (LOCKED) — format flow after locking\n\nVerdict: **{verdict}** (X = {X})\n\n' + pr.drop(columns='boot').to_markdown(index=False, floatfmt='+.4f')
                                   + '\n\n## All layers\n\n' + R.drop(columns='boot').to_markdown(index=False, floatfmt='+.4f') + '\n\n## Reverse readouts (patched − base)\n\n' + rvs.to_markdown(floatfmt='+.4f') + '\n')
    log('VERDICT', verdict)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['work', 'tiny', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float); ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
