#!/usr/bin/env python3
"""Addendum 27 (TODO #3): why does amplifying the arrived information hurt? Norm vs direction vs depth.
Pre-registration: 391_groups/config/prereg_addendum27.md (sha256 checked by work/analyze).

Reuses the addendum 21 machinery (16_inject/inject_main.py, imported by path, NOT edited): same frozen sample
(raw/a21_freeze/freeze.parquet: a16 B sample, A 600 / B 600, 30 shards), same prompt-tail definition (m_i aligned tail), same
prefill-only additive hook, same teacher forcing (every author, every name token, final L63 rank as Stage 10) and same a16 F0
generation. Overridden here (module attributes): the layer list, the condition list, the vector sources and which conditions
are generated.
Sources (added at the tail positions, block-l output, β ∈ {1, 2, 4}, all with per-position norm ‖Δ_i(l,p)‖):
  own   Δ_i = h_true − mean_k h_false_k                                    (as addendum 21)
  mis   donor's Δ_j renormalised to ‖Δ_i‖                                  (as addendum 21)
  scale ‖Δ_i‖ · h/‖h‖  (pure norm increase along the state's own direction)
  orth  Δ_i projected orthogonal to h, renormalised to ‖Δ_i‖
Layers: L48 (scale, orth), L56 and L57 (own, mis, scale, orth). Primary outcome: teacher-forced log10(1/rank) of every true
name token (paper mean); generation only for base, zero, own at L56/L57 and scale at L57 β4.
Commands: tiny (CPU, random 64-layer Qwen3, 3 papers) | work --shards 0 | --shards all | analyze
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'
os.environ.setdefault('A21_OUT', str(G / 'raw/a27'))
H = Path.home() / 'jlens_work'
PREREG = G / 'config/prereg_addendum27.md'; SUMM = G / 'summary_a27'
LAYERS27, BETAS = [48, 56, 57], [1, 2, 4]
SEED, NB = 27, 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


im = load(H / '16_inject/inject_main.py', 'inject_main_frozen_for_a27')
im.LAYERS = LAYERS27
log = im.log


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lock_sha():
    lj = G / 'config/addendum27_lock.json'
    if not lj.exists(): raise SystemExit('addendum 27 not locked')
    want = json.loads(lj.read_text())['sha256']
    if sha(PREREG) != want: raise SystemExit('ADDENDUM 27 CHANGED since lock')
    return want


def conditions(has_fict=False):
    c = [('base', 'base', None, 0), ('zero', 'own', 56, 0)]
    for b in BETAS:
        for s in ('scale', 'orth'): c.append((f'{s}_L48_b{b}', s, 48, b))
    for l in (56, 57):
        for b in BETAS:
            for s in ('own', 'mis', 'scale', 'orth'): c.append((f'{s}_L{l}_b{b}', s, l, b))
    return c


GEN = {'base', 'zero', 'own_L56_b1', 'own_L56_b2', 'own_L56_b4', 'own_L57_b1', 'own_L57_b2', 'own_L57_b4', 'scale_L57_b4'}


def vectors(C, r, conds):
    torch = C.torch; m = int(r.m_tail)
    t = C.states(C.pr['true'][r.paper_id][1], m); fs = [C.states(C.pr[c][r.paper_id][1], m) for c in im.FALSES]
    own = {l: t[l] - sum(f[l] for f in fs) / len(fs) for l in im.LAYERS}
    don, _ = C.delta(r.donor_id, m)
    out, norms = {}, []
    for name, src, l, b in conds:
        if src == 'base': out[name] = None; continue
        o = own[l]; no = o.norm(dim=1, keepdim=True)
        h = t[l]; hn = h / h.norm(dim=1, keepdim=True).clamp_min(1e-12)
        if src == 'own': v = o
        elif src == 'mis': d = don[l]; v = d * (no / d.norm(dim=1, keepdim=True).clamp_min(1e-12))
        elif src == 'scale': v = hn * no
        elif src == 'orth':
            p = o - (o * hn).sum(1, keepdim=True) * hn; v = p * (no / p.norm(dim=1, keepdim=True).clamp_min(1e-12))
        if b > 0: norms.append(float(((v.norm(dim=1) - no[:, 0]).abs() / no[:, 0].clamp_min(1e-12)).max()))
        out[name] = (l, b * v)
    # orth really orthogonal to h (check value)
    orth_cos = max([float(((out[n][1] / out[n][1].norm(dim=1, keepdim=True)) * (t[l] / t[l].norm(dim=1, keepdim=True))).sum(1).abs().max())
                    for n, s, l, b in conds if s == 'orth' and b > 0] or [0.0])
    C._orth_cos = max(getattr(C, '_orth_cos', 0.0), orth_cos)
    return out, (max(norms) if norms else 0.0), {l: float(own[l].norm(dim=1).mean()) for l in im.LAYERS}


def do_paper(C, r):
    torch = C.torch; a16 = im.a16; s10 = im.s10
    conds = conditions(); vec, normdev, dnorm = vectors(C, r, conds)
    ids = C.pr['true'][r.paper_id][1]; m = int(r.m_tail); T = len(ids)
    gc = [c for c in conds if c[0] in GEN]
    im.set_add(C, gc, vec, T - m, T)
    try: gens = a16.generate(C.hf, C.tok, [ids] * len(gc), torch, bs=len(gc))
    finally: C.add = {}
    true = a16.authors_of(C.P.loc[r.paper_id, 'authors']); ctrl = a16.authors_of(C.P.loc[r.donor_id, 'authors'])
    grows = []
    for (name, src, l, b), (gid, full, stop) in zip(gc, gens):
        txt = a16.list_text(full); items = a16.split_items(txt, 'F0'); sc = a16.score_gen(items, true, ctrl)
        grows.append(dict(paper_id=r.paper_id, grp=r.grp, cond=name, source=src, layer=l if l is not None else -1, beta=b,
                          gen_ids=json.dumps(gid), full_text=full, text=txt, items=json.dumps(items), stop=stop, **sc))
    from jlens.hooks import ActivationRecorder
    LAST = C.model.n_layers - 1; trows = []
    for ai, rids, name in C.ctx[r.paper_id]:
        seq = ids + name[:-1]; pos = [T - 1 + j for j in range(len(name))]
        im.set_add(C, conds, vec, T - m, T)
        try:
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=[LAST]) as rec:
                C.model.forward(torch.tensor([seq] * len(conds), device=C.model.input_device))
                h = rec.activations[LAST][:, pos].detach()
        finally: C.add = {}
        gold = torch.tensor(name, device=h.device)
        for ci, (cn, src, l, b) in enumerate(conds):
            lg = C.model.unembed(h[ci].float()).float(); rk, ti, lp, t1 = s10.score(lg, gold, torch)
            for t in range(len(name)):
                trows.append(dict(paper_id=r.paper_id, grp=r.grp, cond=cn, author_index=ai, token_index=t, row_id=int(rids[t]), rank=int(rk[t]), logprob=float(lp[t])))
    zero_eq = grows[0]['gen_ids'] == grows[1]['gen_ids']
    return grows, trows, dict(paper_id=r.paper_id, norm_dev=normdev, zero_equals_base=bool(zero_eq), delta_norm=dnorm, orth_max_abs_cos=getattr(C, '_orth_cos', None))


im.conditions = conditions; im.vectors = vectors; im.do_paper = do_paper


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    out = Path(a.root); out.mkdir(parents=True, exist_ok=True); im.OUT = out
    cfg = transformers.AutoConfig.from_pretrained(im.s10.MODEL, revision=im.s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = im.s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = im.Ctx(tiny=(hf, model, tok))
    keep = C.D[C.D.grp == 'A'].head(2).paper_id.tolist() + C.D[C.D.grp == 'B'].head(1).paper_id.tolist()
    C.D = C.D[C.D.paper_id.isin(keep)].copy(); C.D['shard'] = [0, 0, 1][:len(C.D)]
    im.work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    im.work(argparse.Namespace(shards='0-1', max_minutes=None), C)        # must only log 'skip (exists)'
    g = pd.concat([pd.read_parquet(out / 'gen' / f'shard_{k:03d}.parquet') for k in (0, 1)])
    t = pd.concat([pd.read_parquet(out / 'tf' / f'shard_{k:03d}.parquet') for k in (0, 1)])
    m = [json.load(open(out / 'meta' / f'shard_{k:03d}.json')) for k in (0, 1)]
    nc = len(conditions()); ok = {}
    ok['gen rows = 9 per paper'] = len(g) == len(GEN) * g.paper_id.nunique()
    ok['tf conds per token'] = int(t.groupby(['paper_id', 'row_id']).cond.nunique().min()) == nc
    ok['zero == base'] = all(x['checks']['zero_equals_base_share'] == 1.0 for x in m)
    ok['norm match'] = all(x['checks']['max_norm_dev'] <= 1e-3 for x in m)
    oc = [pp['orth_max_abs_cos'] for x in m for pp in x['per_paper']]
    ok['orth orthogonal to h (|cos| < 1e-3)'] = max(oc) < 1e-3
    tb = t[t.cond == 'base'].set_index(['paper_id', 'row_id'])['rank']
    for c in ('scale_L57_b4', 'orth_L57_b4', 'own_L56_b4'):
        ok[f'{c} changes tf ranks'] = bool((tb != t[t.cond == c].set_index(['paper_id', 'row_id'])['rank'].reindex(tb.index)).any())
    ok['all shards written'] = all((out / k_ / f'shard_{s:03d}.{e}').exists() for s in (0, 1) for k_, e in (('gen', 'parquet'), ('tf', 'parquet'), ('meta', 'json')))
    print('A27 TINY CHECKS', json.dumps(ok), flush=True)
    sys.exit(0 if all(ok.values()) else 1)


def work(a):
    lock_sha()
    shards = a.shards
    if shards == 'all':
        import pandas as pd
        shards = ','.join(str(int(x)) for x in sorted(pd.read_parquet(im.FREEZE / 'freeze.parquet').shard.unique()))
    im.work(argparse.Namespace(shards=shards, max_minutes=a.max_minutes))


def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); mm = len(ps); adj = np.empty(mm); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (mm - r) * ps[i])); adj[i] = run
    return adj


def analyze(a):
    import pandas as pd
    want = lock_sha()
    D = pd.read_parquet(im.FREEZE / 'freeze.parquet'); raw = Path(a.raw) if a.raw else im.OUT
    miss = [int(k) for k in sorted(D.shard.unique()) if not (raw / 'meta' / f'shard_{int(k):03d}.json').exists()]
    if miss and not a.allow_missing: raise SystemExit(f'missing shards {miss}')
    t = pd.concat([pd.read_parquet(f) for f in sorted((raw / 'tf').glob('shard_*.parquet'))])
    g = pd.concat([pd.read_parquet(f) for f in sorted((raw / 'gen').glob('shard_*.parquet'))])
    t['nlr'] = -np.log10(t['rank'].astype(float))
    P = t.groupby(['paper_id', 'grp', 'cond']).nlr.mean().unstack('cond')
    team = D.set_index('paper_id').team.reindex(P.index.get_level_values(0))
    out = Path(a.out) if a.out else SUMM; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for grp in ('A', 'B'):
        S = P.xs(grp, level='grp'); tm = D.set_index('paper_id').team.reindex(S.index)
        codes, uniq = pd.factorize(tm); W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
        def ci(x):
            ok = np.isfinite(x); b = (W[:, ok] @ x[ok]) / W[:, ok].sum(1)
            return float(x[ok].mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)), float(min(1, 2 * min((b <= 0).mean(), (b >= 0).mean()))), int(ok.sum())
        for fam, (src, ref, layers) in {'N': ('scale', 'base', [48, 56, 57]), 'O': ('orth', 'base', [48, 56, 57]), 'P': ('own', 'mis', [56, 57]),
                                       'own-base': ('own', 'base', [56, 57]), 'mis-base': ('mis', 'base', [56, 57])}.items():
            for l in layers:
                for b in BETAS:
                    x = (S[f'{src}_L{l}_b{b}'] - S[ref if ref == 'base' else f'{ref}_L{l}_b{b}']).to_numpy(float)
                    e, lo, hi, p, n = ci(x); rows.append(dict(grp=grp, family=fam, layer=l, beta=b, est=e, lo=lo, hi=hi, p=p, n=n))
    R = pd.DataFrame(rows); R['p_holm'] = np.nan; R['holm_lo'] = np.nan; R['holm_hi'] = np.nan
    for (grp, fam), idx in R.groupby(['grp', 'family']).groups.items():
        R.loc[idx, 'p_holm'] = holm(R.loc[idx, 'p'].to_numpy())
    R.to_csv(out / 'contrasts.csv', index=False)
    A = R[R.grp == 'A']
    neg = lambda f: A[(A.family == f) & (A.hi < 0) & (A.p_holm < 0.05)]
    pos = lambda f: A[(A.family == f) & (A.lo > 0) & (A.p_holm < 0.05)]
    Nn, On = neg('N'), neg('O')
    cellsN = set(zip(Nn.layer, Nn.beta)); cellsO = set(zip(On.layer, On.beta))
    readings = []
    if cellsN and cellsN - cellsO: readings.append('damage is norm-driven (N < 0 where O is not)')
    if cellsO and cellsO - cellsN: readings.append('damage is direction-driven (O < 0 where N is not)')
    if cellsN & cellsO: readings.append('both norm and direction damage (N and O < 0 in the same cells)')
    if not cellsN and not cellsO: readings.append('no Holm-significant norm or direction damage')
    if len(pos('P')): readings.append('paper-specific help near the writer (P > 0 at L56/L57)')
    if len(neg('P')): readings.append('reversed: own hurts more than mismatched at L56/L57')
    if not len(pos('P')) and not len(neg('P')): readings.append('no paper-specific difference near the writer (P includes 0)')
    gr = g.groupby(['grp', 'cond'])[['any_full', 'first_sur']].mean().reset_index(); gr.to_csv(out / 'gen_rates.csv', index=False)
    res = dict(label='addendum 27 (LOCKED)', addendum_sha256=want, n_papers=int(P.index.get_level_values(0).nunique()), missing_shards=miss, readings=readings,
               N_cells_neg=sorted(cellsN), O_cells_neg=sorted(cellsO))
    (out / 'a27_results.json').write_text(json.dumps(res, indent=1, default=str))
    (out / 'report.md').write_text('# Addendum 27 results\n\n' + json.dumps(res, indent=1, default=str) + '\n\n' + R.to_string(index=False, float_format=lambda v: f'{v:.4f}') + '\n\n## Generation rates\n\n' + gr.to_string(index=False, float_format=lambda v: f'{v:.3f}') + '\n')
    log('A27 ANALYSIS', json.dumps(res, default=str))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['tiny', 'work', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=38); ap.add_argument('--root', default=str(G / 'raw/a27_test_tiny'))
    ap.add_argument('--raw'); ap.add_argument('--out'); ap.add_argument('--allow-missing', action='store_true')
    a = ap.parse_args(); {'tiny': tiny, 'work': work, 'analyze': analyze}[a.cmd](a)
