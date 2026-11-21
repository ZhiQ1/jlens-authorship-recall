#!/usr/bin/env python3
"""Addendum 21 (DRAFT, not locked) — injection / sufficiency test. See 16_inject/prereg_addendum21_DRAFT.md.

Frozen code is imported by path, never edited: 14_groups/prereg16_a16.py (a16: sample, F0 generation, list cut, item split,
full-name matcher, model loader = 351_stage10_fix1), 11_stage11/361_stage11.py (title_positions, common_suffix, cohort,
contexts_of).

freeze   (CPU) A + B rows of the a16 B sample; aligned tail m_i (common suffix of the true and all 5 false prompts, bounded
         by the title positions); mismatched donor j (cohort, same field + citation bin, no shared surname, tail >= m_i,
         seed 21); meaning-only fict prompt for papers in the addendum 20 set -> raw/a21_freeze/{freeze.parquet,freeze.json}
precheck (CPU) freeze invariants + a16 helper asserts + condition table
work     (GPU) per a16 shard: Δ (block-l output, l in LAYERS, last m_i positions) from batch-1 forwards of true, false_0..4
         (+ donor, + fict); generation of all conditions of one paper in ONE batch of identical ids (no padding) with a
         prefill-only additive hook; teacher forcing (F0, every author, every name token, all conditions as copies) with
         final L63 rank as Stage 10 (model.unembed(h.float())) -> raw/a21/{gen,tf}/shard_KKK.parquet + meta/shard_KKK.json
         (meta written last = done marker; existing shards skipped)
tiny     (CPU) the whole work pipeline on a random 64-layer Qwen3 with the real tokenizer, 3 papers, + skip-if-done
"""
import argparse, hashlib, importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'
FREEZE = Path(os.environ.get('A21_FREEZE', G / 'raw/a21_freeze'))
OUT = Path(os.environ.get('A21_OUT', G / 'raw/a21'))
SAMPLE = G / 'config/prereg16_sample_B.parquet'; SAMPLE_SHA = '117a9127'
A20 = G / 'raw/a20v2_freeze/fict_titles.parquet'
LAYERS, BETAS, SOURCES, SEED = [48, 52], [1, 2, 4], ['own', 'mis', 'rand'], 21
FALSES = [f'false_{k}' for k in range(5)]


def _load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


a16 = _load(H / '14_groups/prereg16_a16.py', 'a16_frozen_for_a21')
s11 = _load(H / '11_stage11/361_stage11.py', 's11_frozen_for_a21')
s10 = a16.s10; R10 = a16.R10


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def conditions(has_fict):
    """ordered condition list of one paper: (name, source, layer, beta); 'zero' = own with beta 0 (hook-equality check)."""
    c = [('base', 'base', None, 0), ('zero', 'own', LAYERS[0], 0)]
    for l in LAYERS:
        for b in BETAS:
            for s in SOURCES + (['fict'] if has_fict else []): c.append((f'{s}_L{l}_b{b}', s, l, b))
    return c


# ------------------------------------------------------------------ freeze (CPU)
def surnames(auth): return {a16.words(a)[-1] for a in a16.authors_of(auth) if a16.words(a)}


def freeze(a):
    import pandas as pd
    if (FREEZE / 'freeze.parquet').exists() and not a.force: raise SystemExit(f'{FREEZE} exists (use --force)')
    if not hashlib.sha256(SAMPLE.read_bytes()).hexdigest().startswith(SAMPLE_SHA): raise SystemExit('a16 B sample changed')
    S = pd.read_parquet(SAMPLE); S = S[S.grp.isin(['A', 'B'])].copy()
    if a.limit: S = S.groupby('grp').head(a.limit)
    papers, _ = s11.cohort(); P = papers.set_index('paper_id')
    pr = {c: s10.condition_prompts(R10, papers, c)[0] for c in ['true'] + FALSES}
    tok = s10.tokenizer(); cache = {}

    def tail_of(pid):
        if pid in cache: return cache[pid]
        tx, ti = pr['true'][pid]; tp = s11.title_positions(tok, tx, ti); n = len(ti) - 1 - max(tp)
        for c in FALSES:
            fx, fi = pr[c][pid]; tf = s11.title_positions(tok, fx, fi)
            n = min(n, s11.common_suffix(ti, fi), len(fi) - 1 - max(tf))
        cache[pid] = int(n); return cache[pid]

    F = pd.read_parquet(A20) if A20.exists() else None
    fict = {} if F is None else {r.paper_id: r for r in F.itertuples()}
    P['_sur'] = P.authors.map(surnames)
    rng = np.random.default_rng(SEED); rows, excl = [], []
    for r in S.sort_values('paper_id').itertuples():
        m = tail_of(r.paper_id)
        if m < 3: excl.append(dict(paper_id=r.paper_id, grp=r.grp, reason=f'tail {m} < 3')); continue
        me = P.loc[r.paper_id]
        cand = P[(P.field == me.field) & (P.citation_bin == me.citation_bin) & (P.index != r.paper_id)]
        cand = cand[cand._sur.map(lambda s: not (s & me._sur))]
        donor, dt = None, None
        for j in rng.permutation(len(cand)):
            pid = cand.index[j]
            if tail_of(pid) >= m: donor, dt = pid, tail_of(pid); break
        if donor is None: excl.append(dict(paper_id=r.paper_id, grp=r.grp, reason='no donor')); continue
        fr = fict.get(r.paper_id); fids, ftail = None, 0
        if fr is not None:
            fids = json.loads(fr.prompt_ids); ti = pr['true'][r.paper_id][1]
            ftail = min(s11.common_suffix(fids, ti), len(fids) - 1 - max(json.loads(fr.title_pos)))
        rows.append(dict(paper_id=r.paper_id, grp=r.grp, shard=int(r.shard), team=int(r.team), field=me.field,
                         citation_bin=me.citation_bin, m_tail=m, donor_id=donor, donor_tail=dt,
                         has_fict=bool(fids is not None and ftail >= m), fict_ids=json.dumps(fids) if fids else '',
                         fict_tail=int(ftail)))
    D = pd.DataFrame(rows); FREEZE.mkdir(parents=True, exist_ok=True)
    D.to_parquet(FREEZE / 'freeze.parquet', index=False)
    info = dict(n=len(D), by_grp=D.grp.value_counts().to_dict(), excluded=excl, has_fict=D.groupby('grp').has_fict.sum().to_dict(),
                tail_counts=D.m_tail.value_counts().to_dict(), shards=sorted(D.shard.unique().tolist()),
                sample_sha256=hashlib.sha256(SAMPLE.read_bytes()).hexdigest(), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                time=time.strftime('%Y-%m-%dT%H:%M:%S'))
    json.dump(info, open(FREEZE / 'freeze.json', 'w'), indent=1, default=str)
    log('FREEZE', json.dumps({k: info[k] for k in ('n', 'by_grp', 'has_fict', 'tail_counts')}, default=str), 'excluded', len(excl))


def precheck(a):
    import pandas as pd
    D = pd.read_parquet(FREEZE / 'freeze.parquet'); ok = {}
    ok['n A, B'] = D.grp.value_counts().to_dict()
    ok['donor != self'] = bool((D.donor_id != D.paper_id).all())
    ok['donor tail >= m'] = bool((D.donor_tail >= D.m_tail).all())
    ok['m >= 3'] = bool((D.m_tail >= 3).all())
    ok['n conditions (no fict / fict)'] = (len(conditions(False)), len(conditions(True)))
    ok['gens total'] = int(sum(len(conditions(h)) for h in D.has_fict))
    assert a16.list_text(' L. Li, Y. Zhang, and W. X. Zheng. The paper was') == 'L. Li, Y. Zhang, and W. X. Zheng'
    assert a16.split_items('Smith, John, Doe, Jane', 'F1') == ['Smith John', 'Doe Jane']
    ok['a16 helper asserts'] = True
    log('PRECHECK', json.dumps(ok, default=str))
    return ok


# ------------------------------------------------------------------ GPU side
class Ctx:
    def __init__(self, tiny=None):
        import torch, pandas as pd
        self.torch = torch
        self.D = pd.read_parquet(FREEZE / 'freeze.parquet')
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
        self.P = self.papers.set_index('paper_id')
        self.pr = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in ['true'] + FALSES}
        if tiny is None: self.hf, self.model, self.tok = a16.load_model()
        else: self.hf, self.model, self.tok = tiny
        self.blocks = self.hf.model.layers
        if self.blocks[0] is not self.model.layers[0]: raise RuntimeError('jlens layers != hf layers')
        self.dev = next(self.hf.parameters()).device
        self.hooks, self.add = [], {}            # add[l] = (start, end, tensor[B, end-start, d]) for the prefill call

    def install(self):
        torch = self.torch
        for l in LAYERS:
            def hook(mod, inp, out, l=l):
                h = out if torch.is_tensor(out) else out[0]
                spec = self.add.get(l)
                if spec is not None:
                    st, en, t = spec
                    if h.shape[1] >= en: h[:, st:en] += t.to(h.device, h.dtype)
                return out
            self.hooks.append(self.blocks[l].register_forward_hook(hook))

    def remove(self):
        for hd in self.hooks: hd.remove()
        self.hooks = []

    def states(self, ids, m):
        """block-l outputs at the last m positions of a batch-1 forward of ids (hook disabled), float32 [m, d] per layer."""
        torch = self.torch; rec = {}
        hs = []
        for l in LAYERS:
            def grab(mod, inp, out, l=l):
                h = out if torch.is_tensor(out) else out[0]; rec[l] = h[0, -m:].detach().float().cpu(); return out
            hs.append(self.blocks[l].register_forward_hook(grab))
        saved, self.add = self.add, {}
        try:
            with torch.inference_mode(): self.hf(input_ids=torch.tensor([ids], device=self.dev))
        finally:
            for h in hs: h.remove()
            self.add = saved
        return rec

    def delta(self, pid, m, true_ids=None):
        t = self.states(true_ids or self.pr['true'][pid][1], m)
        fs = [self.states(self.pr[c][pid][1], m) for c in FALSES]
        return {l: t[l] - sum(f[l] for f in fs) / len(fs) for l in LAYERS}, fs


def vectors(C, r, conds):
    """per condition: (layer, tensor[m, d]) or None; plus norm check."""
    torch = C.torch; m = int(r.m_tail)
    own, fs = C.delta(r.paper_id, m)
    don, _ = C.delta(r.donor_id, m)
    fic = None
    if r.has_fict:
        tf = C.states(json.loads(r.fict_ids), m)
        fic = {l: tf[l] - sum(f[l] for f in fs) / len(fs) for l in LAYERS}
    g = torch.Generator().manual_seed(SEED + int(int(r.paper_id[:8], 16) % 100000))
    out, norms = {}, []
    for name, src, l, b in conds:
        if src == 'base': out[name] = None; continue
        o = own[l]; no = o.norm(dim=1, keepdim=True)
        if src == 'own': v = o
        elif src == 'mis': d = don[l]; v = d * (no / d.norm(dim=1, keepdim=True).clamp_min(1e-12))
        elif src == 'rand': z = torch.randn(o.shape, generator=g); v = z * (no / z.norm(dim=1, keepdim=True))
        elif src == 'fict': f = fic[l]; v = f * (no / f.norm(dim=1, keepdim=True).clamp_min(1e-12))
        if b > 0: norms.append(float(((v.norm(dim=1) - no[:, 0]).abs() / no[:, 0].clamp_min(1e-12)).max()))
        out[name] = (l, b * v)
    return out, (max(norms) if norms else 0.0), {l: float(own[l].norm(dim=1).mean()) for l in LAYERS}


def set_add(C, conds, vec, start, end):
    torch = C.torch; d = C.blocks[0].self_attn.o_proj.out_features if hasattr(C.blocks[0], 'self_attn') else None
    C.add = {}
    for l in LAYERS:
        rows = []
        for name, src, ll, b in conds:
            v = vec[name]
            rows.append(v[1] if (v is not None and v[0] == l) else None)
        if all(x is None for x in rows): continue
        ref = next(x for x in rows if x is not None)
        C.add[l] = (start, end, torch.stack([x if x is not None else torch.zeros_like(ref) for x in rows]))


def do_paper(C, r):
    torch = C.torch; conds = conditions(bool(r.has_fict)); vec, normdev, dnorm = vectors(C, r, conds)
    ids = C.pr['true'][r.paper_id][1]; m = int(r.m_tail); T = len(ids)
    # generation: all conditions in one batch of identical ids
    set_add(C, conds, vec, T - m, T)
    try: gens = a16.generate(C.hf, C.tok, [ids] * len(conds), torch, bs=len(conds))
    finally: C.add = {}
    true = a16.authors_of(C.P.loc[r.paper_id, 'authors']); ctrl = a16.authors_of(C.P.loc[r.donor_id, 'authors'])
    grows = []
    for (name, src, l, b), (gid, full, stop) in zip(conds, gens):
        txt = a16.list_text(full); items = a16.split_items(txt, 'F0')
        sc = a16.score_gen(items, true, ctrl)
        grows.append(dict(paper_id=r.paper_id, grp=r.grp, cond=name, source=src, layer=l if l is not None else -1, beta=b,
                          gen_ids=json.dumps(gid), full_text=full, text=txt, items=json.dumps(items), stop=stop, **sc))
    # teacher forcing: every author, every name token, all conditions as copies
    from jlens.hooks import ActivationRecorder
    LAST = C.model.n_layers - 1; trows = []
    for ai, rids, name in C.ctx[r.paper_id]:
        seq = ids + name[:-1]; pos = [T - 1 + j for j in range(len(name))]
        set_add(C, conds, vec, T - m, T)
        try:
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=[LAST]) as rec:
                C.model.forward(torch.tensor([seq] * len(conds), device=C.model.input_device))
                h = rec.activations[LAST][:, pos].detach()
        finally: C.add = {}
        gold = torch.tensor(name, device=h.device)
        for ci, (cn, src, l, b) in enumerate(conds):
            lg = C.model.unembed(h[ci].float()).float()
            rk, ti, lp, t1 = s10.score(lg, gold, torch)
            for t in range(len(name)):
                trows.append(dict(paper_id=r.paper_id, grp=r.grp, cond=cn, author_index=ai, token_index=t, row_id=int(rids[t]),
                                  rank=int(rk[t]), logprob=float(lp[t])))
    zero_eq = grows[0]['gen_ids'] == grows[1]['gen_ids']
    return grows, trows, dict(paper_id=r.paper_id, norm_dev=normdev, zero_equals_base=bool(zero_eq), delta_norm=dnorm)


def out_path(kind, k, ext='parquet'): return OUT / kind / f'shard_{k:03d}.{ext}'


def do_shard(C, k):
    import pandas as pd
    if out_path('meta', k, 'json').exists(): log(f'shard {k} skip (exists)'); return False
    rows = C.D[C.D.shard == k]; t0 = time.time(); G_, T_, K_ = [], [], []
    C.install()
    try:
        for r in rows.itertuples():
            g, t, kk = do_paper(C, r); G_ += g; T_ += t; K_.append(kk)
    finally: C.remove()
    gdf, tdf = pd.DataFrame(G_), pd.DataFrame(T_)
    for kind, df in (('gen', gdf), ('tf', tdf)):
        out_path(kind, k).parent.mkdir(parents=True, exist_ok=True); df.to_parquet(out_path(kind, k), index=False)
    chk = dict(papers=len(rows), zero_equals_base_share=float(np.mean([x['zero_equals_base'] for x in K_])) if K_ else None,
               max_norm_dev=float(max([x['norm_dev'] for x in K_] or [0])), norm_tol=1e-3)
    # base vs stored a16 F0 generations (WARN)
    try:
        a = pd.read_parquet(G / f'raw/a16_B/gen_v2/shard_{k:03d}.parquet'); a = a[a.cond == 'F0'].set_index('paper_id')
        b = gdf[gdf.cond == 'base'].set_index('paper_id'); com = b.index.intersection(a.index)
        chk['base_vs_a16_any_full_same_share'] = float((b.loc[com, 'any_full'].astype(bool) == a.loc[com, 'any_full'].astype(bool)).mean()) if len(com) else None
        chk['base_vs_a16_same_ids_share'] = float(np.mean([json.loads(b.loc[p, 'gen_ids']) == list(a.loc[p, 'gen_ids']) for p in com])) if len(com) else None
        chk['base_vs_a16_n'] = int(len(com)); chk['base_vs_a16_threshold'] = 0.95
    except Exception as e: chk['base_vs_a16_error'] = repr(e)
    # base TF vs stored Stage 10 final L63 ranks (WARN)
    try:
        tb = tdf[tdf.cond == 'base']; shards10 = C.P.loc[tb.paper_id.unique()]
        z = []
        for f in sorted((R10 / 'raw/final/L63').glob('shard_*.npz')):
            zz = np.load(f); z.append(pd.DataFrame({'row_id': zz['row_id'], 'rank10': zz['rank']}))
        ref = pd.concat(z).set_index('row_id').rank10
        rr = ref.reindex(tb.row_id).to_numpy(); okm = ~np.isnan(rr.astype(float))
        chk['tf_base_vs_stage10_equal_share'] = float((tb['rank'].to_numpy()[okm] == rr[okm]).mean())
        chk['tf_base_vs_stage10_mean_abs_dlog10rank'] = float(np.abs(np.log10(tb['rank'].to_numpy()[okm]) - np.log10(rr[okm].astype(float))).mean())
        chk['tf_thresholds'] = dict(equal_share=0.75, mean_abs_dlog10rank=0.05)
    except Exception as e: chk['tf_vs_stage10_error'] = repr(e)
    good = (chk.get('zero_equals_base_share') == 1.0 and chk['max_norm_dev'] <= 1e-3 and (chk.get('base_vs_a16_any_full_same_share') or 0) >= .95
            and (chk.get('tf_base_vs_stage10_equal_share') or 0) >= .75)
    chk['status'] = 'PASS' if good else 'WARN'
    meta = dict(shard=k, seconds=time.time() - t0, checks=chk, per_paper=K_, gens=len(gdf), tf_rows=len(tdf),
                host=os.uname().nodename, job=os.environ.get('SLURM_JOB_ID'), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out_path('meta', k, 'json').parent.mkdir(parents=True, exist_ok=True)
    json.dump(meta, open(out_path('meta', k, 'json'), 'w'), indent=1, default=float)
    log(f'shard {k} done papers={len(rows)} gens={len(gdf)} tf={len(tdf)} {time.time() - t0:.0f}s', json.dumps(chk, default=float))
    return True


def parse_shards(s):
    out = []
    for p in s.split(','):
        if '-' in p: a_, b_ = p.split('-'); out += list(range(int(a_), int(b_) + 1))
        elif p: out.append(int(p))
    return out


def work(a, C=None):
    C = C or Ctx(); t_start = time.time(); per = []
    for k in parse_shards(a.shards):
        if k not in set(C.D.shard): continue
        if a.max_minutes and per and (time.time() - t_start + 1.3 * max(per)) / 60 > a.max_minutes: log('budget stop before shard', k); break
        t0 = time.time()
        if do_shard(C, k): per.append(time.time() - t0)


def remaining(a):
    import pandas as pd
    D = pd.read_parquet(FREEZE / 'freeze.parquet'); miss = [k for k in sorted(D.shard.unique()) if not out_path('meta', k, 'json').exists()]
    print(len(miss), 'missing', miss)


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global OUT
    OUT = Path(a.root); OUT.mkdir(parents=True, exist_ok=True)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = Ctx(tiny=(hf, model, tok))
    keep = (C.D[(C.D.grp == 'A') & C.D.has_fict].head(1).paper_id.tolist() + C.D[C.D.grp == 'A'].head(1).paper_id.tolist()
            + C.D[C.D.grp == 'B'].head(1).paper_id.tolist())
    C.D = C.D[C.D.paper_id.isin(keep)].copy(); C.D['shard'] = [0, 0, 1][:len(C.D)]
    for k in (0, 1):
        for p in ('meta', 'gen', 'tf'): pass
    work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    work(argparse.Namespace(shards='0-1', max_minutes=None), C)                 # must only log 'skip (exists)'
    g = pd.concat([pd.read_parquet(out_path('gen', k)) for k in (0, 1)]); t = pd.concat([pd.read_parquet(out_path('tf', k)) for k in (0, 1)])
    m = [json.load(open(out_path('meta', k, 'json'))) for k in (0, 1)]
    ok = {}
    exp = sum(len(conditions(h)) for h in C.D.has_fict)
    ok['gen rows'] = len(g) == exp
    ok['zero == base (exact ids)'] = all(x['checks']['zero_equals_base_share'] == 1.0 for x in m)
    ok['norm match'] = all(x['checks']['max_norm_dev'] <= 1e-3 for x in m)
    ok['tf rows = conds x tokens'] = len(t) == sum(len(conditions(h)) * sum(len(n) for _, _, n in C.ctx[p]) for p, h in zip(C.D.paper_id, C.D.has_fict))
    by = g.groupby('cond').gen_ids.first()
    ok['injection changes output (own_L48_b4 != base, any paper)'] = bool((g[g.cond == 'own_L48_b4'].gen_ids.values != g[g.cond == 'base'].gen_ids.values).any())
    tb = t[t.cond == 'base'].set_index(['paper_id', 'row_id'])['rank']; to = t[t.cond == 'own_L52_b4'].set_index(['paper_id', 'row_id'])['rank']
    ok['injection changes tf ranks'] = bool((tb != to.reindex(tb.index)).any())
    ok['all shards written'] = all(out_path(k_, s, e).exists() for s in (0, 1) for k_, e in (('gen', 'parquet'), ('tf', 'parquet'), ('meta', 'json')))
    print('TINY CHECKS', json.dumps(ok), flush=True)
    return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['freeze', 'precheck', 'work', 'tiny', 'remaining'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=None)
    ap.add_argument('--root'); ap.add_argument('--force', action='store_true'); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'freeze': freeze, 'precheck': precheck, 'work': work, 'remaining': remaining}[a.cmd](a)


if __name__ == '__main__':
    main()
