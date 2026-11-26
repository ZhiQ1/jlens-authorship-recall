#!/usr/bin/env python3
"""Addendum 25 (LOCKED 2026-11-22, 391_groups/config/prereg_addendum25.md): probe-direction injection.

dirs    (CPU) refit the published name-position ridge map at L48 and L52 (surname-first rows of the true runs, raw/b2_npprobe,
        target raw/allTok_L63, alpha = tr(G)/d, standardised X) and save q_l(t) = Q_l[:, t] for the gold / mismatched
        surname-first tokens of the a21 papers -> raw/a25_dirs/dirs.npz + dirs.json
work    (GPU) the addendum 21 pipeline (16_inject/inject_main.py imported read-only; its Ctx / hook / generation / teacher
        forcing / per-shard checks reused) with the vector source replaced: gold / mis / rand directions scaled to
        beta * ||Delta_i(l, p)|| per tail position -> raw/a25/{gen,tf,meta}/shard_k
tiny    (CPU) random 64-layer model, 3 papers, skip-if-done
analyze (CPU) S = rate(gold) - rate(mis), G = rate(gold) - rate(base), group A, any_full and first_sur, 6 cells, Holm over 12,
        team bootstrap 2,000 seed 25 -> 391_groups/summary_a25/
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); G = B / '391_groups'; R13 = B / '381_stage13'
ADD = G / 'config/prereg_addendum25.md'; ADD_SHA = 'c87a1cb49e48fe830c2f3d1a43f57f4ecca7127157d7a5008ca50769d1519769'
DIRS = Path(os.environ.get('A25_DIRS', G / 'raw/a25_dirs')); OUTD = Path(os.environ.get('A25_OUT', G / 'raw/a25'))
LAYERS, BETAS, SRC, SEED = [48, 52], [1, 2, 4], ['gold', 'mis', 'rand'], 25


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def check_lock():
    if sha(ADD) != ADD_SHA: raise SystemExit(f'ADDENDUM 25 CHANGED {sha(ADD)}')


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


def tokens_for(D, toks):
    sf = toks[toks.role == 'surname_first'].sort_values(['paper_id', 'author_index'])
    first = sf.groupby('paper_id').token_id.apply(list)
    gold, mis = {}, {}
    for r in D.itertuples():
        g = first.get(r.paper_id, []); d = first.get(r.donor_id, [])
        if not g or not d: continue
        gold[r.paper_id] = int(g[0]); alt = [t for t in d if t != g[0]]
        if alt: mis[r.paper_id] = int(alt[0])
    return gold, mis


def dirs(a):
    import pandas as pd
    check_lock(); R10 = B / '351_stage10'; RAW = R13 / 'raw/b2_npprobe'
    D = pd.read_parquet(G / 'raw/a21_freeze/freeze.parquet')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'role', 'token_id'])
    gold, mis = tokens_for(D, toks)
    need = sorted(set(gold.values()) | set(mis.values()))
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); nw = vr['norm_weight'].astype(np.float32)
    vpos = pd.Series(np.arange(len(vr['token_id'])), index=vr['token_id']); okt = [t for t in need if t in vpos.index]
    U = vr['lm_head_rows'][vpos.reindex(okt).astype(int).to_numpy()].astype(np.float32)
    T = toks.set_index('row_id'); shards = sorted((RAW / 'true').glob('shard_*.npz'))[: (3 if a.tiny else None)]
    out = dict(token_id=np.array(okt, np.int64)); Y = None
    for l in LAYERS:
        Xs, Ys = [], []
        for f in shards:
            z = np.load(f); rid = z['row_id']; sel = T.role.reindex(rid).to_numpy() == 'surname_first'
            Xs.append(z[f'resid_L{l}'][sel].astype(np.float32))
            if Y is None:
                zy = np.load(R13 / 'raw/allTok_L63' / f.name); yp = pd.Series(np.arange(len(zy['row_id'])), index=zy['row_id']).reindex(rid[sel]).to_numpy().astype(int)
                Ys.append(zy['resid'][yp].astype(np.float32))
        X = np.concatenate(Xs)
        if Y is None: Y = np.concatenate(Ys)
        mu, sd = X.mean(0), X.std(0) + 1e-6; A = (X - mu) / sd; Gm = A.T @ A
        Wm = np.linalg.solve(Gm + np.trace(Gm) / Gm.shape[0] * np.eye(Gm.shape[0], dtype=np.float32), A.T @ (Y - Y.mean(0))); del A, Gm
        out[f'q_L{l}'] = (((Wm / sd[:, None]) * nw[None, :]) @ U.T).T.astype(np.float32)      # [n_tok, d]
        log(f'L{l}: {len(X)} rows, q shape {out[f"q_L{l}"].shape}')
    DIRS.mkdir(parents=True, exist_ok=True); np.savez(DIRS / 'dirs.npz', **out)
    info = dict(n_papers=len(D), gold=len(gold), mis=len(mis), tokens=len(okt), tokens_missing=len(need) - len(okt), tiny=bool(a.tiny),
                gold_map=gold, mis_map=mis, addendum_sha=ADD_SHA, dirs_sha=sha(DIRS / 'dirs.npz'))
    (DIRS / 'dirs.json').write_text(json.dumps(info, default=int)); log('DIRS', {k: v for k, v in info.items() if not k.endswith('_map')})


# ------------------------------------------------------------------ GPU: reuse addendum 21 machinery, replace the vector source
def setup_im(out):
    im = load(H / '16_inject/inject_main.py', 'im_frozen_for_a25')
    info = json.loads((DIRS / 'dirs.json').read_text()); z = np.load(DIRS / 'dirs.npz')
    col = {int(t): i for i, t in enumerate(z['token_id'])}
    Q = {l: z[f'q_L{l}'] for l in LAYERS}
    gold = {k: int(v) for k, v in info['gold_map'].items()}; mis = {k: int(v) for k, v in info['mis_map'].items()}

    def conditions(has_fict=False):
        c = [('base', 'base', None, 0), ('zero', 'gold', LAYERS[0], 0)]
        for l in LAYERS:
            for b in BETAS:
                for s in SRC: c.append((f'{s}_L{l}_b{b}', s, l, b))
        return c

    def vectors(C, r, conds):
        torch = C.torch; m = int(r.m_tail)
        own, _ = C.delta(r.paper_id, m)
        g = torch.Generator().manual_seed(SEED + int(int(r.paper_id[:8], 16) % 100000))
        rnd = {l: torch.randn(own[l].shape[1], generator=g) for l in LAYERS}
        def unit(v): v = torch.as_tensor(v, dtype=torch.float32); return v / v.norm().clamp_min(1e-12)
        out, norms = {}, []
        for name, src, l, b in conds:
            if src == 'base': out[name] = None; continue
            no = own[l].norm(dim=1, keepdim=True)
            if src == 'gold': u = unit(Q[l][col[gold[r.paper_id]]])
            elif src == 'mis': u = unit(Q[l][col[mis[r.paper_id]]])
            else: u = unit(rnd[l])
            v = no * u[None, :]
            if b > 0: norms.append(float(((v.norm(dim=1) - no[:, 0]).abs() / no[:, 0].clamp_min(1e-12)).max()))
            out[name] = (l, b * v)
        return out, (max(norms) if norms else 0.0), {l: float(own[l].norm(dim=1).mean()) for l in LAYERS}

    im.conditions = conditions; im.vectors = vectors; im.OUT = Path(out); im.SEED = SEED
    keep = [p for p in gold if p in mis and gold[p] in col and mis[p] in col]
    return im, keep


def work(a, C=None):
    check_lock(); im, keep = setup_im(OUTD)
    C = C or im.Ctx(); C.D = C.D[C.D.paper_id.isin(keep)].copy()
    im.work(argparse.Namespace(shards=a.shards, max_minutes=a.max_minutes), C)


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    check_lock(); root = Path(a.root); root.mkdir(parents=True, exist_ok=True)
    im, keep = setup_im(root)
    s10 = im.s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = im.Ctx(tiny=(hf, model, tok))
    # tiny model has d=64: project the stored 5120-d directions onto the first 64 coordinates (test of the plumbing only)
    z = np.load(DIRS / 'dirs.npz'); col = {int(t): i for i, t in enumerate(z['token_id'])}
    pick = [p for p in keep][:3]; C.D = C.D[C.D.paper_id.isin(pick)].copy(); C.D['shard'] = [0, 0, 1][:len(C.D)]
    import types
    orig_vectors = im.vectors
    def vec64(Cx, r, conds):
        torch = Cx.torch; m = int(r.m_tail); own, _ = Cx.delta(r.paper_id, m); out, norms = {}, []
        for name, src, l, b in conds:
            if src == 'base': out[name] = None; continue
            no = own[l].norm(dim=1, keepdim=True); u = torch.randn(own[l].shape[1]); u = u / u.norm(); v = no * u[None, :]
            if b > 0: norms.append(float(((v.norm(dim=1) - no[:, 0]).abs() / no[:, 0]).max()))
            out[name] = (l, b * v)
        return out, (max(norms) if norms else 0.0), {}
    im.vectors = vec64
    im.work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    im.work(argparse.Namespace(shards='0-1', max_minutes=None), C)
    g = pd.concat([pd.read_parquet(root / 'gen' / f'shard_{k:03d}.parquet') for k in (0, 1)])
    m = [json.load(open(root / 'meta' / f'shard_{k:03d}.json')) for k in (0, 1)]
    ok = {'gen rows': len(g) == len(C.D) * len(im.conditions()), 'zero==base': all(x['checks']['zero_equals_base_share'] == 1.0 for x in m),
          'norm match': all(x['checks']['max_norm_dev'] <= 1e-3 for x in m), 'conds': sorted(g.cond.unique()) == sorted(c[0] for c in im.conditions()),
          'real dirs loaded': len(col) > 0 and z['q_L48'].shape[1] == 5120}
    print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def analyze(a):
    import pandas as pd
    check_lock(); D = pd.read_parquet(G / 'raw/a21_freeze/freeze.parquet').set_index('paper_id')
    sh = sorted(D.shard.unique()); fs = [OUTD / 'gen' / f'shard_{k:03d}.parquet' for k in sh]
    miss = [k for k, f in zip(sh, fs) if not (OUTD / 'meta' / f'shard_{k:03d}.json').exists()]
    if miss: raise SystemExit(f'missing shards {miss}')
    gen = pd.concat([pd.read_parquet(f) for f in fs])
    res, rows = {}, []
    for grp in ('A', 'B'):
        g = gen[gen.grp == grp]; teams = D.team.reindex(g.paper_id.unique())
        codes, uniq = pd.factorize(teams); W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=2000).astype(float)[:, codes]
        for oc in ('any_full', 'first_sur'):
            wide = g.pivot_table(index='paper_id', columns='cond', values=oc, aggfunc='first').reindex(teams.index).astype(float)
            for l in LAYERS:
                for b in BETAS:
                    for name, x in (('S gold - mis', wide[f'gold_L{l}_b{b}'] - wide[f'mis_L{l}_b{b}']), ('G gold - base', wide[f'gold_L{l}_b{b}'] - wide['base']),
                                    ('gold - rand', wide[f'gold_L{l}_b{b}'] - wide[f'rand_L{l}_b{b}'])):
                        x = x.to_numpy(); ok = np.isfinite(x); bt = (W[:, ok] @ x[ok]) / W[:, ok].sum(1)
                        p = float(min(1, 2 * min((bt <= 0).mean(), (bt >= 0).mean())))
                        rows.append(dict(grp=grp, outcome=oc, layer=l, beta=b, contrast=name, est=float(x[ok].mean()), lo=float(np.percentile(bt, 2.5)),
                                         hi=float(np.percentile(bt, 97.5)), p=p, n=int(ok.sum()), boot=bt))
    R = pd.DataFrame(rows)
    for con in ('S gold - mis', 'G gold - base'):
        m = (R.grp == 'A') & (R.contrast == con); ps = R.loc[m, 'p'].to_numpy(); order = np.argsort(ps); adj = np.empty(len(ps)); run = 0
        for r_, i in enumerate(order): run = max(run, min(1, (len(ps) - r_) * ps[i])); adj[i] = run
        R.loc[m, 'p_holm'] = adj
        a_i = np.empty(len(ps))
        for r_, i in enumerate(order): a_i[i] = 0.05 / (len(ps) - r_)
        R.loc[m, 'holm_lo'] = [float(np.percentile(b_, 100 * ai / 2)) for b_, ai in zip(R.loc[m, 'boot'], a_i)]
        R.loc[m, 'holm_hi'] = [float(np.percentile(b_, 100 * (1 - ai / 2))) for b_, ai in zip(R.loc[m, 'boot'], a_i)]
    A_ = R[R.grp == 'A']; S = A_[A_.contrast == 'S gold - mis'].set_index(['outcome', 'layer', 'beta']); Gc = A_[A_.contrast == 'G gold - base'].set_index(['outcome', 'layer', 'beta'])
    row1 = [k for k in S.index if S.loc[k, 'holm_lo'] > 0 and Gc.loc[k, 'holm_lo'] > 0]
    row1u = [k for k in S.index if S.loc[k, 'lo'] > 0 and Gc.loc[k, 'lo'] > 0]
    harmful = all(Gc.loc[k, 'holm_hi'] < 0 for k in Gc.index if k[2] >= 2)
    verdict = ('Probe direction usable, paper-specific' if row1 else 'Generic boost' if (Gc.holm_lo > 0).any()
               else 'Harmful' if harmful else 'Not usable')
    rates = gen.groupby(['grp', 'cond'])[['any_full', 'first_sur', 'n_fab_full', 'empty']].mean().reset_index() if 'empty' in gen else gen.groupby(['grp', 'cond'])[['any_full', 'first_sur']].mean().reset_index()
    out = G / 'summary_a25'; out.mkdir(parents=True, exist_ok=True)
    R.drop(columns='boot').to_csv(out / 'a25_contrasts.csv', index=False); rates.to_csv(out / 'a25_rates.csv', index=False)
    res = dict(verdict=verdict, borderline=bool(row1u and not row1), row1_cells=[list(map(str, k)) for k in row1], n_A=int(gen[gen.grp == 'A'].paper_id.nunique()),
               n_B=int(gen[gen.grp == 'B'].paper_id.nunique()), addendum_sha=ADD_SHA)
    (out / 'a25_results.json').write_text(json.dumps(res, indent=1))
    (out / 'report.md').write_text(f"# Addendum 25 (LOCKED) — probe-direction injection\n\nVerdict (locked rule): **{verdict}**\n\n"
                                   + R[R.grp == 'A'].drop(columns='boot').to_markdown(index=False, floatfmt='+.4f') + '\n\n## Rates\n\n' + rates.to_markdown(index=False, floatfmt='.4f') + '\n')
    log('VERDICT', verdict)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['dirs', 'work', 'tiny', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float); ap.add_argument('--root'); ap.add_argument('--tiny', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'dirs': dirs, 'work': work, 'analyze': analyze}[a.cmd](a)


if __name__ == '__main__':
    main()
