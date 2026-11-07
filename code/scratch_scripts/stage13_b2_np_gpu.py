"""Batch 2, addendum 11 part A (name-position probe), GPU data step.

Plan (locked): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum11.json (sha256 checked below), part A "GPU step".
For all 9,108 papers (Stage 10 shards, 72 x 128 papers) and each title condition (true, false_0..false_4), every author context
exactly as Stage 10 `run` / addendum 9 (stage13_alltok_gpu.py):
    ids = prompt_ids(cond) + name_ids[:-1], one context per forward (batch 1); position len(prompt)-1+j predicts name token j
    (j = 0 is the ':' position), ActivationRecorder at blocks L32, L40, L48, L52, L56 (+ L63 for the true title only).
Stored per (condition, shard): raw/b2_npprobe/<cond>/shard_XXX.npz
    row_id [n] (= cohort/name_tokens.parquet row_id), resid_L{l} [n, d] fp16 for l in 32/40/48/52/56,
    rank_logit_L{l} [n] int32 = full-vocabulary rank of the gold token from the unrounded bf16 state through final norm + lm_head
    (= Stage 10 'logit' readout), meta. The L63 targets are NOT stored (plan: reuse raw/allTok_L63).
Checks -> summary_b2_np/checks/<cond>_shard_XXX.json
    HARD 1 (true title, every true shard): recomputed L63 states (fp16) vs raw/allTok_L63 of the same rows, relative norm
       diff per row; PASS if max <= 0.05 (plan). FAIL -> summary_b2_np/HARD_CHECK1_FAILED, exit code 3, no further units.
    WARN R: rank_logit_L{l} vs Stage 10 raw/[cond_<cond>/]logit/L{l} rank: exact-match share (WARN if < 0.95).
    WARN fp16: overflow (|x| >= 65504) / non-finite counts.
Units: (cond, shard); skip-if-exists; claims (mkdir) in --all mode; stops cleanly before the time budget.
Usage: stage13_b2_np_gpu.py --shards 0 [--conds true,false_0,...] [--max-minutes 40]     (single-shard gate: all 6 conds)
       stage13_b2_np_gpu.py --all [--max-minutes 40]                                      (claim mode, all 432 units)
       stage13_b2_np_gpu.py --tiny --shards 0,1                                           (CPU: random 64-layer Qwen3, real
                                                         tokenizer, root 381_stage13/b2_np_tiny; same seed/config as the
                                                         addendum-9 tiny model so hard check 1 runs against alltok_tiny)
"""
import argparse, importlib.util, json, os, sys, time, datetime, hashlib, traceback, subprocess
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0]
T0 = time.monotonic()
def log(*a):
    try: print(f'[{datetime.datetime.now().isoformat(timespec="seconds")} {time.monotonic() - T0:6.0f}s]', *a, flush=True)
    except Exception: pass


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols'); CK = load(H / '13_stage13/stage13_b2A_checks.py', 'b2A_checks')
fix1 = load(H / '10_stage10/351_stage10_fix1.py', 's10fix1'); s10 = fix1.s10
REC_LAYERS = K.NP_LAYERS + [K.NP_CHECK_LAYER]


def roots(tiny):
    r = R13 / 'b2_np_tiny' if tiny else R13
    return dict(root=r, raw=r / 'raw/b2_npprobe', chk=r / 'summary_b2_np/checks', claims=r / 'logs/claims_b2_np', logs=r / 'logs',
                ref63=(R13 / 'alltok_tiny' if tiny else R13) / 'raw/allTok_L63', fail=r / 'summary_b2_np/HARD_CHECK1_FAILED')


def tiny_model():
    """= stage13_alltok_gpu.tiny_model (same config, seed and dtype -> the same random weights)"""
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
    tok = s10.tokenizer(); return jlens.from_hf(hf, tok), tok


def record(model, ids, positions, gold, torch, want63):
    from jlens.hooks import ActivationRecorder
    layers = REC_LAYERS if want63 else K.NP_LAYERS
    x = torch.tensor([ids], device=model.input_device)
    out, ranks = {}, {}
    with torch.inference_mode():
        with ActivationRecorder(model.layers, at=layers) as rec:
            model.forward(x)
            acts = {l: rec.activations[l].detach() for l in layers}
        g = torch.tensor(gold, device=model.input_device)
        for l in layers:
            h = acts[l][0][positions]                                          # bf16 [n_pos, d]
            out[l] = h.float().cpu().numpy().astype(np.float16)
            if l in K.NP_LAYERS:                                               # Stage 10 'logit' readout = model.unembed(h.float())
                lg = model.unembed(h.float()).float(); gg = g.to(lg.device)
                ranks[l] = ((lg > lg.gather(1, gg[:, None])).sum(1) + 1).int().cpu().numpy()
    return out, ranks


def unit_path(R, cond, k): return R['raw'] / cond / f'shard_{k:03d}.npz'


def claim(R, cond, k, me):
    R['claims'].mkdir(parents=True, exist_ok=True); d = R['claims'] / f'{cond}_{k:03d}'
    try: d.mkdir(); (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")}\n'); return True
    except FileExistsError:
        try: o = (d / 'owner').read_text().split()[0]
        except Exception: o = ''
        if o and o.isdigit():                                                  # reclaim if the owner job is gone
            try: st = subprocess.run(['squeue', '-h', '-j', o, '-o', '%T'], capture_output=True, text=True, timeout=60).stdout.strip()
            except Exception: st = 'UNKNOWN'
            if st == '':
                (d / 'owner').write_text(f'{me} {time.strftime("%Y-%m-%dT%H:%M:%S")} (reclaimed from {o})\n'); return True
        return False


def checks(R, cond, k, rows, d, h63, tiny):
    out = dict(cond=cond, shard=k, n_rows=int(len(rows)), tiny=tiny)
    for l in K.NP_LAYERS:
        x = d[K.np_resid_key(l)].astype(np.float32)
        out[f'nonfinite_L{l}'] = int((~np.isfinite(x)).sum()); out[f'overflow_L{l}'] = int((np.abs(x) >= 65504).sum())
    out['fp16_status'] = 'WARN' if any(out[f'nonfinite_L{l}'] or out[f'overflow_L{l}'] for l in K.NP_LAYERS) else 'OK'
    # WARN: logit-lens ranks vs Stage 10
    st = []
    for l in K.NP_LAYERS:
        f = R10 / 'raw' / ('' if cond == 'true' else f'cond_{cond}') / 'logit' / f'L{l}' / f'shard_{k:03d}.npz'
        if not f.exists(): out[f'R_L{l}'] = None; st.append('WARN'); continue
        z = np.load(f); ref = pd.Series(z['rank'], index=z['row_id']).reindex(rows).to_numpy()
        m = float((ref == d[K.np_rank_key(l)]).mean()); out[f'R_match_L{l}'] = m
        out[f'R_mean_abs_dlog10_L{l}'] = float(np.nanmean(np.abs(np.log10(ref.astype(float)) - np.log10(d[K.np_rank_key(l)].astype(float)))))
        st.append('OK' if m >= 0.95 else 'WARN')
    out['R_status'] = 'OK' if all(s == 'OK' for s in st) else 'WARN'
    out['R_threshold'] = 0.95
    if tiny: out['note'] = 'TINY random model: R (vs Stage 10) is expected to WARN; hard check 1 runs against the tiny addendum-9 states'
    # HARD 1: L63 vs allTok_L63
    if cond == 'true':
        f = R['ref63'] / f'shard_{k:03d}.npz'
        if f.exists():
            z = np.load(f); pos = pd.Series(np.arange(len(z['row_id'])), index=z['row_id']).reindex(rows)
            if pos.isna().any(): out['H1'] = dict(check='hard1_L63', status='FAIL', reason=f'{int(pos.isna().sum())} rows missing in allTok_L63', tol=K.NP_HARD1_TOL)
            else: out['H1'] = CK.rel_norm_check(h63, z['resid'][pos.to_numpy().astype(int)], K.NP_HARD1_TOL, 'hard1_L63')
        else: out['H1'] = dict(check='hard1_L63', status='FAIL', reason=f'missing {f}', tol=K.NP_HARD1_TOL)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shards', default=None); ap.add_argument('--conds', default=','.join(K.CONDS))
    ap.add_argument('--all', action='store_true'); ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--tiny', action='store_true')
    a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    R = roots(a.tiny)
    if R['fail'].exists(): log('HARD_CHECK1_FAILED present:', R['fail']); sys.exit(3)
    me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    budget = a.max_minutes; left = None
    try: left = s10_minutes_left()
    except Exception: pass
    if left is not None and (budget is None or left - 5 < budget): budget = left - 5
    m, _ = s10.verify(R10)
    shards = list(range(m['n_shards'])) if (a.all or a.shards == 'all') else s10.parse_shards(a.shards or '0', m['n_shards'])
    conds = a.conds.split(',')
    todo = [(c, k) for c in conds for k in shards if not unit_path(R, c, k).exists()]
    log(f'b2_np_gpu job {me}: {len(todo)} of {len(conds) * len(shards)} units to do, budget {budget} min', 'TINY' if a.tiny else '')
    if not todo: return
    import torch
    for x in ('raw', 'chk', 'logs'): R[x].mkdir(parents=True, exist_ok=True)
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    ctx = pd.read_parquet(R10 / 'cohort/contexts.parquet')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'token_id'])
    prompts = {c: s10.condition_prompts(R10, papers, c)[0] for c in conds}
    model, tok = tiny_model() if a.tiny else s10.load_model()
    env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), stage10_sha256=s10.sha_file(s10.__file__),
               plan_sha256=PLAN_SHA, protocol_sha256=m['protocol_sha256'], tiny=a.tiny, job=me, layers=K.NP_LAYERS)
    t_start = time.monotonic(); last = 0.0; n_done = 0
    for c, k in todo:
        f = unit_path(R, c, k)
        if f.exists(): continue
        est = 1.5 * max(last, 20 if a.tiny else 45) / 60
        if budget is not None and (time.monotonic() - T0) / 60 + est > budget: log('time budget reached; stop before', c, k); break
        if (a.all or not a.tiny) and not claim(R, c, k, me): log('claimed by another job, skip', c, k); continue
        t0 = time.monotonic()
        try:
            cs = ctx[ctx.shard == k].sort_values('context_id')
            tk = toks[toks.context_id.isin(cs.context_id)].sort_values('row_id').reset_index(drop=True)
            rows = tk.row_id.to_numpy(); n = len(rows); off = rows[0]
            if not np.array_equal(rows, np.arange(off, off + n)): raise RuntimeError('row ids not contiguous in shard')
            res = {l: None for l in K.NP_LAYERS}; rk = {l: np.zeros(n, np.int32) for l in K.NP_LAYERS}; h63 = None
            filled = np.zeros(n, bool); enc_checked = set(); want63 = (c == 'true')
            for _, cx in cs.iterrows():
                prompt, pids = prompts[c][cx.paper_id]
                if cx.paper_id not in enc_checked:
                    if model.encode(prompt, max_length=s10.MAX_CONTEXT).reshape(-1).tolist() != pids:
                        raise RuntimeError(f'prompt encoding differs from frozen ids: {c} {cx.paper_id}')
                    enc_checked.add(cx.paper_id)
                t = tk[tk.context_id == cx.context_id]
                name = t.token_id.tolist(); idx = t.row_id.to_numpy() - off
                ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]
                hs, ranks = record(model, ids, pos, name, torch, want63)
                for l in K.NP_LAYERS:
                    if res[l] is None: res[l] = np.zeros((n, hs[l].shape[1]), np.float16)
                    res[l][idx] = hs[l]; rk[l][idx] = ranks[l]
                if want63:
                    if h63 is None: h63 = np.zeros((n, hs[63].shape[1]), np.float16)
                    h63[idx] = hs[63]
                filled[idx] = True
            if not filled.all(): raise RuntimeError(f'unfilled rows {c} shard {k}')
            d = {K.ROW_ID: rows} | {K.np_resid_key(l): res[l] for l in K.NP_LAYERS} | {K.np_rank_key(l): rk[l] for l in K.NP_LAYERS}
            ck = checks(R, c, k, rows, d, h63, a.tiny)
            meta = dict(cond=c, shard=k, row_start=int(off), n_rows=n, created=datetime.datetime.now().isoformat(timespec='seconds'), **env)
            f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
            np.savez(tmp, meta=np.array(json.dumps(meta, sort_keys=True)), **d); os.replace(tmp, f)
            try: (R['chk'] / f'{c}_shard_{k:03d}.json').write_text(json.dumps(ck, indent=1, default=str))
            except Exception as e: log('WARN: could not write check json', repr(e))
        except Exception as e:                                                 # a crashing unit is logged and skipped (claim kept)
            try: (R['logs'] / f'b2_np_error_{c}_{k:03d}_{me}.txt').write_text(traceback.format_exc())
            except Exception: pass
            log('UNIT ERROR (logged, continue):', c, k, repr(e)); continue
        last = time.monotonic() - t0; n_done += 1
        h1 = ck.get('H1', {})
        log(f'{c} shard {k:03d} contexts={len(cs)} tokens={n} {last:.0f}s total={(time.monotonic() - t_start) / 60:.1f}min',
            'R', ck.get('R_status'), 'match_L40=%s' % ck.get('R_match_L40'), 'fp16', ck.get('fp16_status'),
            ('HARD1 %s rel_max=%.3g bitexact=%.3f' % (h1.get('status'), h1.get('rel_max', float('nan')), h1.get('bitexact_share', float('nan')))) if h1 else '')
        if h1 and h1.get('status') != 'PASS':
            R['fail'].parent.mkdir(parents=True, exist_ok=True); R['fail'].write_text(json.dumps(ck, indent=1, default=str))
            log('HARD CHECK 1 FAILED (true-title L63 vs raw/allTok_L63) -> stop, exit 3'); sys.exit(3)
    log(f'done: {n_done} units this job')


def s10_minutes_left():
    jid = os.environ.get('SLURM_JOB_ID')
    if not jid: return None
    s = subprocess.run(['squeue', '-h', '-j', jid, '-o', '%L'], capture_output=True, text=True, timeout=90).stdout.strip()
    d, _, hms = s.rpartition('-'); parts = [int(x) for x in hms.split(':')]
    while len(parts) < 3: parts.insert(0, 0)
    return (int(d or 0) * 1440) + parts[0] * 60 + parts[1] + parts[2] / 60


if __name__ == '__main__':
    main()
