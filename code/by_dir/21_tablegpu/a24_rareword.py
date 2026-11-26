#!/usr/bin/env python3
"""Addendum 24 (LOCKED 2026-11-22, 391_groups/config/prereg_addendum24.md): rare-word vs common-word replacement.

freeze  (CPU) build variants (a) rare-replaced, (b) common-replaced (same k) from the TRUE title of each addendum 20 paper
        (a20v2 freeze), seed 24 -> raw/a24_freeze/variants.parquet + freeze.json
work    (GPU) Stage 10 scoring of every name token under each variant prompt, using the frozen a20 scorer
        (15_h2fict/h2_main_gpu.score_condition, imported read-only) -> raw/a24_score/<v>/shard_k.npz; shard 0 also rescoring
        of the TRUE prompt for the parity check (WARN only)
tiny    (CPU) whole pipeline on a random 64-layer model, 3 papers, skip-if-done
analyze (CPU) R_v = S_true - S_v (S_true, F from addendum 20 perpaper_final63.csv), D = Rbar_a - Rbar_b (target, eligible),
        team bootstrap 2,000 seed 24 -> 391_groups/summary_a24/
"""
import argparse, hashlib, importlib.util, json, os, re, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); G = B / '391_groups'
ADD = G / 'config/prereg_addendum24.md'; ADD_SHA = '270f2157171bc5889d0dc9469dc63cf5f695628aafdcfd6bf0113be92a8ed917'
FZ = Path(os.environ.get('A24_FREEZE', G / 'raw/a24_freeze')); OUT = Path(os.environ.get('A24_OUT', G / 'raw/a24_score'))
A20F = G / 'raw/a20v2_freeze/fict_titles.parquet'; SEED = 24; VARS = ['a', 'b']
STOP = set('a an the of in on for to and or with by from at as is are be via using use based into over under between among '
           'its their this that these those than about against without within through toward towards new study analysis'.split())
WORD = re.compile(r"[A-Za-z0-9]+")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def check_lock():
    if sha(ADD) != ADD_SHA: raise SystemExit(f'ADDENDUM 24 CHANGED {sha(ADD)}')


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def cat(w, first):
    if sum(c.isupper() for c in w) >= 2 or (any(c.isdigit() for c in w) and any(c.isalpha() for c in w)): return 'acr'
    if w[0].isupper() and not first: return 'cap'
    return 'oth'


def freeze(a):
    import pandas as pd
    check_lock(); h2g = load(H / '15_h2fict/h2_main_gpu.py', 'h2g'); s10 = h2g.s10; R10 = h2g.R10
    tok = s10.tokenizer(); papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'title', 'year']).set_index('paper_id')
    F = pd.read_parquet(A20F)
    df = {}; spans = []
    for t in papers.title.astype(str):
        ws = WORD.findall(t); spans.append(ws)
        for w in set(x.lower() for x in ws): df[w] = df.get(w, 0) + 1
    ntok = lambda w: len(tok(' ' + w, add_special_tokens=False).input_ids)
    def is_rare(w, first): return w.lower() not in STOP and (df.get(w.lower(), 0) <= 3 or cat(w, first) in ('acr', 'cap'))
    def is_common(w, first): return w.lower() not in STOP and not is_rare(w, first) and df.get(w.lower(), 0) >= 20 and w.isalpha()
    pool_r, pool_c = {}, {}
    # build pools keyed by (category, token length) / (token length, df band); token lengths computed lazily on unique words
    uniq_r, uniq_c = set(), set()
    for ws in spans:
        for i, w in enumerate(ws):
            if is_rare(w, i == 0): uniq_r.add((w, cat(w, i == 0)))
            elif is_common(w, i == 0): uniq_c.add(w.lower())
    for w, c in uniq_r: pool_r.setdefault((c, ntok(w)), []).append(w)
    for w in uniq_c: pool_c.setdefault(ntok(w), []).append(w)
    pool_r = {k: sorted(v) for k, v in pool_r.items() if k[1] is not None}; pool_c = {k: sorted(v) for k, v in pool_c.items()}
    rows = []
    for r in F.itertuples():
        title = str(papers.loc[r.paper_id, 'title']); year = papers.loc[r.paper_id, 'year']
        rng = np.random.default_rng(SEED + int(r.paper_id[:8], 16) % 100000)
        toks_ = [(m.start(), m.end(), m.group()) for m in WORD.finditer(title)]
        own = set(w.lower() for _, _, w in toks_)
        rare = [i for i, (_, _, w) in enumerate(toks_) if is_rare(w, i == 0)]
        comm = [i for i, (_, _, w) in enumerate(toks_) if is_common(w, i == 0)]
        k = len(rare); kc = min(k, len(comm)); elig = k >= 1 and len(comm) >= 1
        def rebuild(rep):
            out, last = [], 0
            for i, (s, e, w) in enumerate(toks_):
                out.append(title[last:s]); out.append(rep.get(i, w)); last = e
            out.append(title[last:]); return ''.join(out)
        rep_a = {}
        for i in rare:
            w = toks_[i][2]; key = (cat(w, i == 0), ntok(w)); cand = [x for x in pool_r.get(key, []) if x.lower() not in own]
            if not cand:
                for d in (1, -1, 2, -2):
                    cand = [x for x in pool_r.get((key[0], key[1] + d), []) if x.lower() not in own]
                    if cand: break
            if cand: rep_a[i] = cand[int(rng.integers(len(cand)))]
        rep_b = {}
        for i in (sorted(rng.choice(comm, kc, replace=False).tolist()) if kc else []):
            w = toks_[i][2]; d0 = df.get(w.lower(), 0); L = ntok(w)
            cand = [x for x in pool_c.get(L, []) if x not in own and 0.5 * d0 <= df.get(x, 0) <= 2 * d0]
            if cand:
                x = cand[int(rng.integers(len(cand)))]; rep_b[i] = x.capitalize() if w[0].isupper() else x
        for v, rep in (('a', rep_a), ('b', rep_b)):
            vt = rebuild(rep); prompt = s10.PROMPT.format(title=vt, year=year); ids = tok(prompt).input_ids
            rows.append(dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, shard=int(r.shard), variant=v,
                             title=vt, n_replaced=len(rep), k_rare=k, n_common=len(comm), eligible=bool(elig and len(rep) >= 1),
                             changed=vt != title, prompt=prompt, prompt_ids=json.dumps(ids), n_prompt_tokens=len(ids)))
    V = pd.DataFrame(rows); FZ.mkdir(parents=True, exist_ok=True); V.to_parquet(FZ / 'variants.parquet', index=False)
    E = V[V.variant == 'a'].eligible
    info = dict(n_papers=int(F.shape[0]), eligible=int(E.sum()), eligible_by_group=V[(V.variant == 'a') & V.eligible].group.value_counts().to_dict(),
                changed_share={v: float(V[(V.variant == v) & V.eligible].changed.mean()) for v in VARS},
                mean_replaced={v: float(V[(V.variant == v) & V.eligible].n_replaced.mean()) for v in VARS},
                addendum_sha=ADD_SHA, variants_sha=sha(FZ / 'variants.parquet'), script_sha=sha(__file__))
    (FZ / 'freeze.json').write_text(json.dumps(info, indent=1, default=str)); log('FREEZE', json.dumps(info, default=str))
    ex = V[V.eligible].groupby('paper_id').head(2).head(16)[['paper_id', 'variant', 'title']]
    log('EXAMPLES\n' + ex.to_string())


def out_path(v, k): return OUT / v / f'shard_{k:03d}.npz'


def work(a, C=None):
    import pandas as pd
    check_lock(); h2g = load(H / '15_h2fict/h2_main_gpu.py', 'h2g')
    V = pd.read_parquet(FZ / 'variants.parquet'); shards = [int(x) for x in a.shards.split(',') if x != '']
    todo = [(v, k) for k in shards for v in VARS if not out_path(v, k).exists()]
    if a.parity and not (OUT / 'parity_000.npz').exists(): todo = [('true', shards[0])] + todo
    if not todo: log('nothing to do'); return
    t0 = time.monotonic(); C = C or h2g.Ctx(); log(f'model loaded {(time.monotonic() - t0) / 60:.1f} min')
    last = 0
    for v, k in todo:
        if a.max_minutes and (time.monotonic() - t0 + 1.5 * last) / 60 > a.max_minutes: log('budget stop before', v, k); break
        t1 = time.monotonic()
        if v == 'true':
            rows = V[(V.shard == k) & (V.variant == 'a')]
            d = h2g.score_condition(C, rows, 'true'); f = OUT / 'parity_000.npz'
        else:
            rows = V[(V.shard == k) & (V.variant == v)]
            d = h2g.score_condition(C, rows, 'fict'); f = out_path(v, k)
        meta = dict(variant=v, shard=k, n_papers=int(len(rows)), seconds=time.monotonic() - t1, job=os.environ.get('SLURM_JOB_ID'), host=os.uname().nodename)
        h2g.save(f, d, meta); last = time.monotonic() - t1; log(f'{v} shard {k} papers={len(rows)} rows={len(d["row_id"])} {last:.0f}s')
    log(f'job done {(time.monotonic() - t0) / 60:.1f} min')


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global OUT, FZ
    OUT = Path(a.root); OUT.mkdir(parents=True, exist_ok=True)
    h2g = load(H / '15_h2fict/h2_main_gpu.py', 'h2g'); s10 = h2g.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = h2g.Ctx(tiny_model=(model, tok, {'public': h2g.IdLens()}))
    V = pd.read_parquet(FZ / 'variants.parquet'); keep = V[V.eligible & (V.shard == 0)].paper_id.unique()[:2].tolist()
    Vt = V[V.paper_id.isin(keep)]; tmp = Path(a.root) / 'variants.parquet'; Vt.to_parquet(tmp, index=False)
    FZ = Path(a.root)
    work(argparse.Namespace(shards='0', parity=True, max_minutes=None), C)
    work(argparse.Namespace(shards='0', parity=True, max_minutes=None), C)      # must say nothing to do
    ok = {v: out_path(v, 0).exists() for v in VARS}; ok['parity'] = (OUT / 'parity_000.npz').exists()
    z = np.load(out_path('a', 0)); ok['rows>0'] = len(z['row_id']) > 0; ok['final key'] = 'rank@final@63' in z.files
    print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def analyze(a):
    import pandas as pd
    check_lock(); h2g = load(H / '15_h2fict/h2_main_gpu.py', 'h2g'); R10 = h2g.R10
    V = pd.read_parquet(FZ / 'variants.parquet'); fz = json.loads((FZ / 'freeze.json').read_text())
    shards = sorted(V.shard.unique()); miss = [(v, k) for v in VARS for k in shards if not out_path(v, k).exists()]
    if miss: raise SystemExit(f'missing shards {miss}')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    S = {}
    for v in VARS:
        z = [np.load(out_path(v, k)) for k in shards]
        rid = np.concatenate([x['row_id'] for x in z]); rk = np.concatenate([x['rank@final@63'] for x in z])
        S[v] = pd.Series(-np.log10(rk.astype(float)), index=toks.reindex(rid).values).groupby(level=0).mean()
    P = pd.read_csv(G / 'summary_a20/perpaper_final63.csv', dtype={'paper_id': str}).set_index('paper_id')
    el = V[(V.variant == 'a') & V.eligible].set_index('paper_id')
    elb = V[(V.variant == 'b') & V.eligible].set_index('paper_id')
    ids = el.index.intersection(elb.index).intersection(P.index)
    D = P.loc[ids].copy(); D['S_a'] = S['a'].reindex(ids); D['S_b'] = S['b'].reindex(ids)
    D['R_a'] = D.S_true - D.S_a; D['R_b'] = D.S_true - D.S_b; D['R_f'] = D.S_true - D.S_fict
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id']).paper_id.to_numpy()
    c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); _, team = c13.group_folds(papers); TEAM = dict(zip(papers, team))
    def boot(sub, f):
        codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in sub.index]))
        W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=2000).astype(float)[:, codes]
        est = f(sub, np.ones(len(sub))); b = np.array([f(sub, w) for w in W]); lo, hi = np.percentile(b, [2.5, 97.5]); return est, lo, hi
    wm = lambda col: (lambda s, w: float(np.sum(w * s[col].to_numpy()) / np.sum(w)))
    def diff(s, w): return float(np.sum(w * (s.R_a - s.R_b).to_numpy()) / np.sum(w))
    def kept(v): return lambda s, w: float(np.sum(w * (s[f'S_{v}'] - s.F)) / np.sum(w * (s.S_true - s.F)))
    rows = []
    for g in ('target', 'control'):
        sub = D[D.group == g]
        for name, f in [('Rbar_a', wm('R_a')), ('Rbar_b', wm('R_b')), ('Rbar_fict', wm('R_f')), ('D = Rbar_a - Rbar_b', diff), ('K_a', kept('a')), ('K_b', kept('b'))]:
            e, lo, hi = boot(sub, f); rows.append(dict(group=g, quantity=name, n=len(sub), est=e, lo=lo, hi=hi))
    R = pd.DataFrame(rows); out = G / 'summary_a24'; out.mkdir(parents=True, exist_ok=True); R.to_csv(out / 'a24_results.csv', index=False)
    D.to_csv(out / 'perpaper.csv')
    p = R[(R.group == 'target') & (R.quantity == 'D = Rbar_a - Rbar_b')].iloc[0]
    verdict = 'Rare words carry more of the real-title part' if p.lo > 0 else ('Common words carry more' if p.hi < 0 else 'No difference between word classes')
    res = dict(verdict=verdict, primary=p.to_dict(), freeze=fz, addendum_sha=ADD_SHA)
    (out / 'a24_results.json').write_text(json.dumps(res, indent=1, default=float))
    (out / 'report.md').write_text(f'# Addendum 24 (LOCKED) — rare vs common word replacement\n\nVerdict (locked rule): **{verdict}**\n\n' + R.to_markdown(index=False, floatfmt='+.4f') + '\n\nFreeze: ' + json.dumps(fz, default=str) + '\n')
    log('VERDICT', verdict); print(R.to_string())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['freeze', 'work', 'tiny', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--parity', action='store_true'); ap.add_argument('--max-minutes', type=float)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'freeze': freeze, 'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
