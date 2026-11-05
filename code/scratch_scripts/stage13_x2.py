"""Stage 13 X2: subspace patching (rules frozen in config/prereg_addendum6.json, 2026-11-05).

Question: is the paper information that carries the first author through the title positions (X1) contained in a
10-dim 'paper attribute' subspace S_id (H2), a 10-dim 'author' subspace S_auth (H3), or neither?
Subspaces are fitted on CPU by stage13_x2_fit.py -> summary_x2/subspaces_L{l}.npz (S_id, S_auth, S_rand x3, mu).

Per pair (A, B) of config/pairs.parquet with equal title token length (as X1, 381_stage13.do_xpatch), at layer l in
LAYERS, every title position is patched (block output, X1 hook format (batch_index, ('at', pos), vector)):
  carry : B's authors prompt, h_B -> h_B + P_S (h_A - h_B)        score = A's first-author teacher-forced score
  remove: A's authors prompt, h_A -> h_A - P_S (h_A - mu_l)       score = A's first-author teacher-forced score
for S in VARIANTS = zero (S = 0, identity check), id, auth, rand61, rand62, rand63, full (identity map: carry = X1
full replacement h_A, remove = mu at every title position). All variants x layers of one arm run in ONE batched forward
(7 x 5 = 35 batch elements). Projections in fp32, written back in the model dtype. Also stored per pair: the share of
||h_A - h_B||^2 (title positions) captured by each subspace (cap_S@l).

Usage: python stage13_x2.py --tiny                (CPU, 2-layer random Qwen3, real tokenizer; temp root x2_tiny)
       python stage13_x2.py --shards 0 [1 2 ...]  (GPU; skips existing outputs)
       python stage13_x2.py --all [--max-minutes M]
Outputs: raw/x2/shard_XXX.npz (one row per pair)."""
import importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
LAYERS = [16, 24, 32, 40, 48]
VARIANTS = ['zero', 'id', 'auth', 'rand61', 'rand62', 'rand63', 'full']
RAND_SEEDS = [61, 62, 63]


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


s13 = load(H / '13_stage13/381_stage13.py', 's13'); s10, s11 = s13.s10, s13.s11


def roots(tiny):
    r = ROOT / 'x2_tiny' if tiny else ROOT
    return dict(root=r, sub=r / 'summary_x2', raw=r / 'raw/x2', rep=r / 'reports')


def tiny_ctx():
    """the 2-layer random Qwen3 of 381_stage13.dry (seed 0) with the real tokenizer and the jlens wrapper"""
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); tok = s10.tokenizer()
    class Tiny(s13.Ctx):
        def __init__(self):
            self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
            self.model = jlens.from_hf(hf, tok); self.tok = tok; self.env = dict(script_sha256='tiny'); self.hf = hf
    return Tiny()


def load_subspaces(C, sub_dir, layers):
    """{layer: {variant: Q [d, k] fp32 tensor or None (full)}, mu: {layer: tensor}}"""
    torch = C.torch; out, mu = {}, {}
    for l in layers:
        z = np.load(sub_dir / f'subspaces_L{l}.npz'); d = z['mu'].shape[0]
        Q = dict(zero=np.zeros((d, 0), np.float32), id=z['S_id'], auth=z['S_auth'], full=None)
        for i, s in enumerate(RAND_SEEDS): Q[f'rand{s}'] = z['S_rand'][i]
        for k, v in Q.items():
            if v is not None:
                v = np.asarray(v, np.float32); assert v.shape[0] == d and (v.shape[1] == 0 or np.allclose(v.T @ v, np.eye(v.shape[1]), atol=1e-4)), (l, k, v.shape)
        out[l] = {k: (None if v is None else torch.tensor(np.asarray(v, np.float32))) for k, v in Q.items()}
        mu[l] = torch.tensor(z['mu'].astype(np.float32))
    return out, mu


def proj(x, Q):
    """P_S x for rows of x (fp32); Q orthonormal [d, k] on x's device"""
    if Q.shape[1] == 0: return x * 0
    return (x @ Q) @ Q.T


def do_x2(C, shard, layers, SUB, MU, limit=None):
    torch = C.torch; smp, pairs = s13.sample(); P = C.papers.set_index('paper_id'); rows = []
    for r in smp[smp.shard == shard].itertuples():
        if limit is not None and len(rows) >= limit: break
        if r.paper_id not in pairs.index or r.paper_id not in C.ctx: continue
        q = pairs.loc[r.paper_id].partner; A, Bt = P.loc[r.paper_id].title, P.loc[q].title
        name = C.ctx[r.paper_id][0][2]
        spanA, fullA = s13.title_span(C.tok, A); spanB, fullB = s13.title_span(C.tok, Bt)
        if spanA != spanB: continue                                            # equal length (as X1)
        clean = s13.score_tf(C, fullA, name)[0]; corrupt = s13.score_tf(C, fullB, name)[0]
        aA = C.record(fullA, layers); aB = C.record(fullB, layers)
        row = dict(paper_id=r.paper_id, partner=q, split=pairs.loc[r.paper_id].split, clean=clean, corrupt=corrupt, n_title_tokens=len(spanA))
        pc, pr = {}, {}
        for li, l in enumerate(layers):
            hA = aA[l][spanA[0]:spanA[-1] + 1]; hB = aB[l][spanB[0]:spanB[-1] + 1]; dt = hA.dtype; dev = hA.device
            dAB = (hA.float() - hB.float()); dAm = hA.float() - MU[l].to(dev)[None]; e2 = float((dAB ** 2).sum())
            for vi, v in enumerate(VARIANTS):
                Q = SUB[l][v]; i = vi * len(layers) + li
                if v == 'full':
                    newB, newA = hA, MU[l].to(dev)[None].expand_as(hA).to(dt); row[f'cap_{v}@{l}'] = 1.0
                else:
                    Q = Q.to(dev); pAB = proj(dAB, Q)
                    newB = (hB.float() + pAB).to(dt); newA = (hA.float() - proj(dAm, Q)).to(dt)
                    row[f'cap_{v}@{l}'] = float((pAB ** 2).sum()) / max(e2, 1e-30)
                pc.setdefault(l, []).extend([(i, ('at', p), newB[j]) for j, p in enumerate(spanA)])
                pr.setdefault(l, []).extend([(i, ('at', p), newA[j]) for j, p in enumerate(spanA)])
        nb = len(VARIANTS) * len(layers)
        vc = s13.score_tf(C, fullB, name, patch=pc, batch=nb); vr = s13.score_tf(C, fullA, name, patch=pr, batch=nb)
        for vi, v in enumerate(VARIANTS):
            for li, l in enumerate(layers):
                row[f'carry_{v}@{l}'] = vc[vi * len(layers) + li]; row[f'remove_{v}@{l}'] = vr[vi * len(layers) + li]
        rows.append(row)
    return {k: np.array([x[k] for x in rows]) for k in rows[0]} if rows else dict(paper_id=np.array([]))


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def run(shards, tiny=False, max_minutes=None, limit=None):
    R = roots(tiny); t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    budget = max_minutes
    left = s11.slurm_minutes_left()
    if left is not None and (budget is None or left - 6 < budget): budget = left - 6
    todo = [k for k in shards if not (R['raw'] / f'shard_{k:03d}.npz').exists()]
    log(f'x2: job {me}, {len(todo)} of {len(shards)} shards to do, budget {budget} min')
    if not todo: return
    C = tiny_ctx() if tiny else s13.Ctx()
    layers = [0, 1] if tiny else LAYERS
    SUB, MU = load_subspaces(C, R['sub'], layers)
    sub_sha = {l: s10.sha_file(R['sub'] / f'subspaces_L{l}.npz') for l in layers}
    env = dict(getattr(C, 'env', {}), x2_script_sha256=s10.sha_file(__file__), subspace_sha256=sub_sha, layers=layers, variants=VARIANTS, job=me)
    last = 0.0
    for k in todo:
        f = R['raw'] / f'shard_{k:03d}.npz'
        if f.exists(): continue
        if budget is not None and (time.monotonic() - t0) / 60 + 1.5 * max(last, 60) / 60 > budget: log('time budget reached; stop before shard', k); break
        t1 = time.monotonic()
        try:
            d = do_x2(C, k, layers, SUB, MU, limit=limit)
            save(f, d, dict(env, unit=['x2', None, k], created=time.strftime('%Y-%m-%dT%H:%M:%S')))
        except Exception as e:                                                  # non-fatal: log and go on
            (R['root'] / 'logs').mkdir(parents=True, exist_ok=True)
            (R['root'] / f'logs/x2_error_shard{k:03d}_{me}.txt').write_text(traceback.format_exc()); log('SHARD ERROR (logged, continue):', k, repr(e)); continue
        last = time.monotonic() - t1; log(f'x2 shard {k:03d} rows={len(d["paper_id"])} {last:.0f}s total={(time.monotonic() - t0) / 60:.1f}min')
    return C


def main():
    a = sys.argv[1:]
    mm = float(a[a.index('--max-minutes') + 1]) if '--max-minutes' in a else None
    if '--tiny' in a:
        smp, pairs = s13.sample(); sh = int(smp.shard.iloc[0]); s = smp[(smp.shard == sh) & smp.paper_id.isin(pairs.index)]
        sp = pairs.loc[s.paper_id].split.to_numpy(); s13._CACHE['smp'] = pd.concat([s[sp == 'tune'].head(3), s[sp == 'test'].head(3)])   # both splits
        C = run([sh], tiny=True)
        f = roots(True)['root'] / f'raw/xpatch/shard_{sh:03d}.npz'                 # X1 reference for the S_full check
        if not f.exists():
            s13.XP_LAYERS = [0, 1]; C = C or tiny_ctx(); d = s13.do_xpatch(C, sh); save(f, d, dict(unit=['xpatch', None, sh], tiny=True)); log('tiny X1 reference saved', f)
        z = np.load(roots(True)['raw'] / f'shard_{sh:03d}.npz'); log('reload ok:', len(z['paper_id']), 'rows,', len(z.files) - 1, 'arrays')
        return
    if '--all' in a:
        smp, _ = s13.sample(); run(sorted(int(x) for x in smp.shard.unique()), max_minutes=mm); return
    if '--shards' in a:
        ks = []
        for x in a[a.index('--shards') + 1:]:
            if x.startswith('--'): break
            ks.append(int(x))
        run(ks, max_minutes=mm); return
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
