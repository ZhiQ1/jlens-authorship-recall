"""Plan 2026-11-14b item 2 (H3 same-scale comparison at the name positions) -- post hoc (strengthening 2), descriptive.
CPU compute step, one job per title condition (true, false_0..false_4).

Input: raw/b2_npprobe/<cond>/shard_*.npz (addendum 11 A GPU step: fp16 residuals at every name-token-predicting position,
rank_logit_L{l} = full-vocab logit-lens gold rank from the unrounded bf16 state). Rows: surname_first role only (the probe
run used for the published Vpd numbers), all 72 shards.
For each layer in 32/40/48/52/56 and lens in {logit, jlens_public}:
  logit         h = residual (fp16 -> fp32; bf16 states are exact in fp16)
  jlens_public  h = residual @ J_l.T  (jlens.JacobianLens.transport, public lens of 351_stage10.DEFAULT_LENSES['public'])
  then two decoders, ranking the TRUE gold token ONLY among the 9,137 name token ids (summary_alltok/vocab_rows.npz order):
    'b16' (MAIN; = Stage 10 model.unembed): bf16 cast, Qwen3RMSNorm (fp32 stats, bf16 output, bf16 weight product),
          bf16 lm_head rows from the HF checkpoint, logits rounded to bf16; rank = 1 + #(name-id logits strictly greater)
    'f32' (sensitivity; = the probe's decoder P9.Vocab.logits): fp32 RMS norm with the final-norm weight, fp32 lm_head rows
          of vocab_rows.npz
Parity (WARN only, written to parity/<cond>.json):
  (1) shard 0 (all surname_first rows; --parity-shards): full-vocabulary logit-lens rank recomputed (b16) from the stored fp16
      residual vs stored rank_logit_L{l}: exact-match share, and the same for the public J-lens vs Stage 10 raw jlens_public;
  (2) every row: restricted rank <= stored full-vocab rank (logit: rank_logit_L{l}; J-lens: Stage 10 raw jlens_public rank),
      and on the parity shard restricted <= recomputed full rank;
  vocab rows: vocab_rows.npz lm_head rows vs HF lm_head rows at the same ids (max |diff|).
Output: summary_h3_samescale_20261114/ranks/<cond>.parquet (row_id, rr_<lens>_<dec>_L<l>), skip-if-exists.
Usage: ... --cond true [--tiny]   (tiny: shard 0 only, L40 only, output under ranks_tiny/ parity_tiny/)
"""
import argparse, json, time, sys, os
from pathlib import Path
import numpy as np, pandas as pd, torch

B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
OUT = R13 / 'summary_h3_samescale_20261114'
PUBLIC = B / 'public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/Qwen3-32B_jacobian_lens.pt'
HFDIR = Path('/scratch/zhang.zhiqi2/hf/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137')
LAYERS = [32, 40, 48, 52, 56]; LENSES = ['logit', 'jlens_public']; EPS = 1e-6
T0 = time.time()
def log(*a):
    try: print(f'[{time.time() - T0:7.0f}s]', *a, flush=True)
    except Exception: pass


def rank_of(lg, gidx):
    g = lg.gather(1, gidx[:, None])
    return ((lg > g).sum(1) + 1).numpy().astype(np.int64)


def norm_b16(h, nw16):
    x = h.to(torch.bfloat16).float()
    xn = (x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + EPS)).to(torch.bfloat16)
    return (nw16 * xn).float()                                                   # bf16 * bf16 product, as HF


def norm_f32(h, nw32):
    return h / torch.sqrt(h.pow(2).mean(1, keepdim=True) + EPS) * nw32


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cond', required=True); ap.add_argument('--tiny', action='store_true')
    ap.add_argument('--parity-shards', default='0'); ap.add_argument('--threads', type=int, default=int(os.environ.get('SLURM_CPUS_PER_TASK', 8)))
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    sfx = '_tiny' if a.tiny else ''
    fo = OUT / f'ranks{sfx}' / f'{a.cond}.parquet'; fp = OUT / f'parity{sfx}' / f'{a.cond}.json'
    fo.parent.mkdir(parents=True, exist_ok=True); fp.parent.mkdir(parents=True, exist_ok=True)
    if fo.exists() and fp.exists(): log('exists', fo); return
    layers = [40] if a.tiny else LAYERS; pshards = [int(x) for x in a.parity_shards.split(',')]
    tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'token_id', 'role']).set_index('row_id')
    # ---- residuals (surname_first rows)
    files = sorted((R13 / 'raw/b2_npprobe' / a.cond).glob('shard_*.npz'))
    if a.tiny: files = files[:1]
    if not a.tiny and len(files) != 72: raise SystemExit(f'{a.cond}: {len(files)}/72 shards')
    rid, X, RL, shard = [], {l: [] for l in layers}, {l: [] for l in layers}, []
    for f in files:
        z = np.load(f); r = z['row_id']; m = (tok.role.reindex(r) == 'surname_first').to_numpy()
        rid.append(r[m]); shard.append(np.full(m.sum(), int(f.stem.split('_')[1])))
        for l in layers: X[l].append(z[f'resid_L{l}'][m]); RL[l].append(z[f'rank_logit_L{l}'][m])
    rid = np.concatenate(rid); shard = np.concatenate(shard)
    X = {l: np.concatenate(X[l]) for l in layers}; RL = {l: np.concatenate(RL[l]).astype(np.int64) for l in layers}
    log(a.cond, 'surname_first rows', len(rid), 'shards', len(files))
    # ---- vocab + weights
    vr = np.load(R13 / 'summary_alltok/vocab_rows.npz'); ids = vr['token_id'].astype(np.int64); vid = {int(t): i for i, t in enumerate(ids)}
    W32 = torch.from_numpy(vr['lm_head_rows'].astype(np.float32)); nw32 = torch.from_numpy(vr['norm_weight'].astype(np.float32))
    from safetensors import safe_open
    with safe_open(str(HFDIR / 'model-00017-of-00017.safetensors'), framework='pt') as sf:
        LM = sf.get_tensor('lm_head.weight'); nw16 = sf.get_tensor('model.norm.weight')
    assert LM.dtype == torch.bfloat16 and nw16.dtype == torch.bfloat16, (LM.dtype, nw16.dtype)
    W16 = LM[torch.from_numpy(ids)].float(); LMf = LM.float(); del LM
    par = dict(cond=a.cond, tiny=a.tiny, n_rows=int(len(rid)), label='post hoc (strengthening 2), descriptive',
               vocab_rows_vs_hf_maxabs=float((W16 - W32).abs().max()), norm_weight_vs_hf_maxabs=float((nw16.float() - nw32).abs().max()))
    gold = tok.token_id.reindex(rid).to_numpy()
    gidx = torch.from_numpy(np.array([vid[int(t)] for t in gold], np.int64)); gfull = torch.from_numpy(gold.astype(np.int64))
    # ---- J-lens
    ck = torch.load(str(PUBLIC), map_location='cpu', weights_only=True); Jall = ck['J']
    par['J_dtype'] = str(next(iter(Jall.values())).dtype); J = {l: Jall[l].float() for l in layers}; del ck, Jall
    log('weights loaded; J dtype', par['J_dtype'])
    # ---- Stage 10 stored full-vocab J-lens ranks for these rows
    s10 = {}
    for l in layers:
        d = R10 / 'raw' / ('' if a.cond == 'true' else f'cond_{a.cond}') / 'jlens_public' / f'L{l}'
        rr, kk = [], []
        for s in sorted(set(shard.tolist())):
            z = np.load(d / f'shard_{s:03d}.npz'); rr.append(z['row_id']); kk.append(z['rank'])
        s10[l] = pd.Series(np.concatenate(kk), index=np.concatenate(rr)).reindex(rid).to_numpy()
    res = {'row_id': rid}; CH = 4096; pmask = np.isin(shard, pshards)
    for l in layers:
        for lens in LENSES:
            out16 = np.zeros(len(rid), np.int64); out32 = np.zeros(len(rid), np.int64)
            pf = np.where(pmask)[0]; full16 = {}
            for i in range(0, len(rid), CH):
                h = torch.from_numpy(X[l][i:i + CH].astype(np.float32))
                if lens == 'jlens_public': h = h @ J[l].T
                gi = gidx[i:i + CH]
                y16 = norm_b16(h, nw16)
                out16[i:i + CH] = rank_of((y16 @ W16.T).to(torch.bfloat16).float(), gi)
                out32[i:i + CH] = rank_of(norm_f32(h, nw32) @ W32.T, gi)
                # parity rows in this chunk: full-vocab b16 rank
                sel = np.where(pmask[i:i + CH])[0]
                for j0 in range(0, len(sel), 512):
                    sj = torch.from_numpy(sel[j0:j0 + 512])
                    lg = (y16[sj] @ LMf.T).to(torch.bfloat16).float()
                    fr = rank_of(lg, gfull[i:i + CH][sj])
                    for q, v in zip(sel[j0:j0 + 512], fr): full16[i + int(q)] = int(v)
            res[f'rr_{lens}_b16_L{l}'] = out16; res[f'rr_{lens}_f32_L{l}'] = out32
            ref = RL[l] if lens == 'logit' else s10[l]
            key = f'{lens}_L{l}'
            pr = np.array(sorted(full16)); fv = np.array([full16[q] for q in pr])
            par[f'p1_full_exact_share_{key}'] = float((fv == ref[pr]).mean()) if len(pr) else None
            par[f'p1_full_within1pct_share_{key}'] = float((np.abs(fv - ref[pr]) <= np.maximum(1, 0.01 * ref[pr])).mean()) if len(pr) else None
            par[f'p1_n_{key}'] = int(len(pr))
            par[f'p1_ref_{key}'] = 'stored rank_logit_L (b2_npprobe)' if lens == 'logit' else 'Stage 10 raw jlens_public rank'
            for dec, o in (('b16', out16), ('f32', out32)):
                ok = np.isfinite(ref.astype(float))
                par[f'p2_restricted_le_storedfull_share_{key}_{dec}'] = float((o[ok] <= ref[ok]).mean())
                par[f'p2_n_violations_{key}_{dec}'] = int((o[ok] > ref[ok]).sum())
            if len(pr): par[f'p2_restricted_le_recomputedfull_share_{key}_b16'] = float((out16[pr] <= fv).mean())
            if lens == 'jlens_public' or True:
                par[f'stored_logit_vs_s10_logit_note'] = 'stored rank_logit_L already compared with Stage 10 logit in addendum 11 A WARN R'
            par[f'status_{key}'] = 'OK' if (par[f'p1_full_exact_share_{key}'] or 0) >= 0.95 and par[f'p2_n_violations_{key}_b16'] == 0 else 'WARN'
            log(a.cond, key, 'median rr b16', int(np.median(out16)), 'f32', int(np.median(out32)), 'p1 exact', par[f'p1_full_exact_share_{key}'],
                'p2 viol b16/f32', par[f'p2_n_violations_{key}_b16'], par[f'p2_n_violations_{key}_f32'], par[f'status_{key}'])
    pd.DataFrame(res).to_parquet(fo, index=False); fp.write_text(json.dumps(par, indent=1)); log('wrote', fo)


if __name__ == '__main__':
    main()
