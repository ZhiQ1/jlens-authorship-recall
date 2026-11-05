"""Addendum 9 (2026-11-05), GPU data step: the model's own L63 residual at the position that PREDICTS each name token.

Plan (frozen): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum9.json (sha256 a9896357...).
For all 9,108 papers (Stage 10 shards, 72 x 128 papers), true-title prompts, every author context exactly as Stage 10 `run`:
    ids = prompt_ids + name_ids[:-1], one context per forward (batch 1), position len(prompt)-1+j predicts name token j,
    ActivationRecorder at block 63 (= the residual Stage 10 'final' unembeds). Nothing else changes.
The frozen Stage 10 script is imported by path (through 351_stage10_fix1.py, which only fixes load_model for transformers 5.x).

Output per shard: 381_stage13/raw/allTok_L63/shard_XXX.npz
    row_id [n] (= cohort/name_tokens.parquet row_id, contiguous), resid [n, d] fp16, rank_bf16 (rank of the gold token from the
    unrounded state, = Stage 10 final@63), rank_fp16 (rank from the stored fp16 state), meta.
Checks (WARN only, written to summary_alltok/checks/shard_XXX.json; never stop the job):
    C1  token_index 0 rows (predicted at ':') vs Stage 11 titlepos resid_colon L63 (fp16) of the same paper: max / mean |diff|,
        relative norm diff; WARN if relative norm diff > 0.02 (bf16 noise from the different context length is far below that).
    C2  rank of the gold token decoded from the stored state vs Stage 10 raw/final/L63 rank: exact-match share, mean |dlog10 rank|;
        WARN if match share < 0.95 or mean |dlog10| > 0.02.  Also fp16 overflow count (|x| > 65504) and NaN/inf.
Skip-if-exists per shard; stops before --max-minutes.

Usage: stage13_alltok_gpu.py --shards 0 [--max-minutes 40]       (GPU)
       stage13_alltok_gpu.py --tiny --shards 0,1                   (CPU: random 64-layer Qwen3 with the real tokenizer,
                                                                    root 381_stage13/alltok_tiny; whole code path)
"""
import argparse, importlib.util, json, os, sys, time, datetime, hashlib
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
PLAN = B / '381_stage13/config/prereg_addendum9.json'
PLAN_SHA = 'a98963579aa2c4af0e0f266a97407c8f171d9dd47116ca7d1cac90e198d262c7'
LAYER = 63
T0 = time.monotonic()
def log(*a): print(f'[{datetime.datetime.now().isoformat(timespec="seconds")} {time.monotonic() - T0:6.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


fix1 = load(H / '10_stage10/351_stage10_fix1.py', 's10fix1'); s10 = fix1.s10


def roots(tiny):
    r = B / '381_stage13' / ('alltok_tiny' if tiny else '')
    return dict(raw=r / 'raw/allTok_L63', chk=r / 'summary_alltok/checks')


def tiny_model():
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()   # 64 layers, bf16 like the real run
    tok = s10.tokenizer(); return jlens.from_hf(hf, tok), tok


def record(model, ids, positions, torch):
    """Stage 10 fast_readout for plan [('final', 63)]: same input tensor, same recorder (need = [63]), same forward."""
    from jlens.hooks import ActivationRecorder
    x = torch.tensor([ids], device=model.input_device)
    with torch.inference_mode():
        with ActivationRecorder(model.layers, at=[LAYER]) as rec:
            model.forward(x)
            act = rec.activations[LAYER].detach()
        h = act[0][positions]                                  # bf16 [n_pos, d]
        lg = model.unembed(h.float()).float()                  # = Stage 10 'final' logits
        h16 = h.float().cpu().numpy().astype(np.float16)
        lg16 = model.unembed(torch.from_numpy(h16.astype(np.float32)).to(h.device)).float()   # decoded from the STORED state
    return h16, lg, lg16


def rank_of(logits, gold, torch):
    gold = gold.to(logits.device); g = logits.gather(1, gold[:, None])
    return ((logits > g).sum(1) + 1).int().cpu().numpy()


def titlepos_colon(shard):
    f = R11 / f'raw/titlepos/true/shard_{shard:03d}.npz'
    if not f.exists(): return {}
    z = np.load(f); return dict(zip(z['resid_paper_id'], z['resid_colon'][:, -1]))


def checks(shard, d, tk, tiny):
    out = dict(shard=shard, n_rows=int(len(d['row_id'])))
    R = d['resid'].astype(np.float32)
    out['n_nonfinite'] = int((~np.isfinite(R)).sum()); out['max_abs_resid'] = float(np.abs(R[np.isfinite(R)]).max())
    out['n_fp16_overflow_risk'] = int((np.abs(R) >= 65504).sum())
    # C1: ':' state vs Stage 11 titlepos L63
    tc = titlepos_colon(shard); first = tk.token_index.to_numpy() == 0
    diffs, rel = [], []
    for i in np.where(first)[0]:
        p = tk.paper_id.iloc[i]
        if p in tc and tc[p].shape == R[i].shape:
            ref = tc[p].astype(np.float32); x = R[i]
            diffs.append(np.abs(x - ref).max()); rel.append(np.linalg.norm(x - ref) / max(np.linalg.norm(ref), 1e-9))
    out['C1_n'] = len(diffs)
    if diffs:
        out |= dict(C1_max_abs=float(np.max(diffs)), C1_mean_maxabs=float(np.mean(diffs)), C1_rel_norm_max=float(np.max(rel)), C1_rel_norm_mean=float(np.mean(rel)))
        out['C1_status'] = 'OK' if out['C1_rel_norm_max'] <= 0.02 else 'WARN'
    else: out['C1_status'] = 'WARN (no titlepos reference)'
    # C2: rank vs Stage 10 final@63
    f = R10 / f'raw/final/L63/shard_{shard:03d}.npz'
    if f.exists():
        z = np.load(f); ref = pd.Series(z['rank'], index=z['row_id']).reindex(d['row_id']).to_numpy()
        nl = lambda r: -np.log10(r.astype(float))
        for k in ('rank_bf16', 'rank_fp16'):
            out[f'C2_{k}_match'] = float((d[k] == ref).mean()); out[f'C2_{k}_mean_abs_dlog10'] = float(np.abs(nl(d[k]) - nl(ref)).mean())
        out['C2_fp16_vs_bf16_match'] = float((d['rank_fp16'] == d['rank_bf16']).mean())
        out['C2_status'] = 'OK' if (out['C2_rank_fp16_match'] >= 0.95 and out['C2_rank_fp16_mean_abs_dlog10'] <= 0.02) else 'WARN'
    else: out['C2_status'] = 'WARN (no Stage 10 final file)'
    if out['n_nonfinite'] or out['n_fp16_overflow_risk']: out['fp16_status'] = 'WARN'
    else: out['fp16_status'] = 'OK'
    if tiny: out['note'] = 'TINY random model: C1/C2 are expected to WARN (different model); only the code path is tested'
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=None)
    ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    import torch
    R = roots(a.tiny); R['raw'].mkdir(parents=True, exist_ok=True); R['chk'].mkdir(parents=True, exist_ok=True)
    m, _ = s10.verify(R10)
    shards = list(range(m['n_shards'])) if a.shards == 'all' else s10.parse_shards(a.shards, m['n_shards'])
    todo = [k for k in shards if not (R['raw'] / f'shard_{k:03d}.npz').exists()]
    log('shards requested', len(shards), 'todo', len(todo), 'tiny' if a.tiny else '')
    if not todo: return
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    ctx = pd.read_parquet(R10 / 'cohort/contexts.parquet')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'token_id'])
    prompts, _ = s10.condition_prompts(R10, papers, 'true')
    model, tok = tiny_model() if a.tiny else s10.load_model()
    env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), stage10_sha256=s10.sha_file(s10.__file__),
               plan_sha256=PLAN_SHA, protocol_sha256=m['protocol_sha256'], tiny=a.tiny, job=os.environ.get('SLURM_JOB_ID'))
    t_start = time.monotonic()
    for k in todo:
        t0 = time.monotonic()
        cs = ctx[ctx.shard == k].sort_values('context_id')
        tk = toks[toks.context_id.isin(cs.context_id)].sort_values('row_id').reset_index(drop=True)
        rows = tk.row_id.to_numpy(); n = len(rows); off = rows[0]
        if not np.array_equal(rows, np.arange(off, off + n)): raise RuntimeError('row ids not contiguous in shard')
        resid = None; rb = np.zeros(n, np.int32); rf = np.zeros(n, np.int32); filled = np.zeros(n, bool)
        enc_checked = set()
        for _, c in cs.iterrows():
            prompt, pids = prompts[c.paper_id]
            if c.paper_id not in enc_checked:
                if model.encode(prompt, max_length=s10.MAX_CONTEXT).reshape(-1).tolist() != pids:
                    raise RuntimeError(f'prompt encoding differs from frozen ids: {c.paper_id}')
                enc_checked.add(c.paper_id)
            t = tk[tk.context_id == c.context_id]
            name = t.token_id.tolist(); idx = t.row_id.to_numpy() - off
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]
            h16, lg, lg16 = record(model, ids, pos, torch)
            if resid is None: resid = np.zeros((n, h16.shape[1]), np.float16)
            gold = torch.tensor(name)
            resid[idx] = h16; rb[idx] = rank_of(lg, gold, torch); rf[idx] = rank_of(lg16, gold, torch); filled[idx] = True
        if not filled.all(): raise RuntimeError(f'unfilled rows shard {k}')
        d = dict(row_id=rows, resid=resid, rank_bf16=rb, rank_fp16=rf)
        ck = checks(k, d, tk, a.tiny)
        meta = dict(shard=k, layer=LAYER, row_start=int(off), n_rows=n, condition='true', created=datetime.datetime.now().isoformat(timespec='seconds'), **env)
        f = R['raw'] / f'shard_{k:03d}.npz'; tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
        np.savez(tmp, meta=np.array(json.dumps(meta, sort_keys=True)), **d); os.replace(tmp, f)
        (R['chk'] / f'shard_{k:03d}.json').write_text(json.dumps(ck, indent=1))
        el = time.monotonic() - t0
        log(f'shard {k:03d} contexts={len(cs)} tokens={n} {el:.0f}s total={(time.monotonic() - t_start) / 60:.1f}min',
            'C1', ck['C1_status'], f"rel_max={ck.get('C1_rel_norm_max', float('nan')):.4g}", 'C2', ck['C2_status'],
            f"match={ck.get('C2_rank_fp16_match', float('nan')):.4f}", 'fp16', ck['fp16_status'])
        if a.max_minutes and (time.monotonic() - T0) / 60 + 1.5 * el / 60 > a.max_minutes:
            log('time budget reached; remaining shards left for the next job'); return
    log('done')


if __name__ == '__main__':
    main()
