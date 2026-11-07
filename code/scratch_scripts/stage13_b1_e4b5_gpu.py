"""Addendum 10 item 4 (batch 1), GPU data step: title-last and ':' residuals for the false_1..false_4 titles.

Plan (locked): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum10.json (sha256 8243a4ed...).
Exactly Stage 11 E4 titlepos (11_stage11/361_stage11.py do_titlepos, imported by path, not edited) restricted to the residual
part: for every paper of a Stage 10 shard (128 papers) that has author contexts, prompt-only forward (batch 1) of the
condition prompt, ActivationRecorder at the same layer set as Stage 11, then
    resid_title [n, 9, d]  = block outputs at PROBE_LAYERS (16..60) at the last title token        (fp16)
    resid_colon [n, 10, d] = block outputs at PROBE_LAYERS + [63] at the last prompt token ':'        (fp16)
    resid_paper_id [n], probe_layers [9]   (same keys as 361_stage11/raw/titlepos/{true,false_0})
plus rank_colon63 (rank of each author's first name token from the L63 ':' state, unembedded as Stage 11 final@63@colon)
with gold_paper_id / gold, for a check against the stored Stage 11 rank of the same condition.

Checks per (condition, shard) -> 381_stage13/summary_b1_e4b5/checks/<cond>_shard_XXX.json
    R  rank_colon63 vs Stage 11 raw/titlepos/<cond> final@63@colon (kind 'first'): exact-match share (WARN if < 0.95).
    H  (false_0 only) HARD CHECK: residuals vs stored Stage 11 false_0 residuals, relative norm diff per (paper, position,
       layer); PASS if max <= 0.05. A FAIL writes HARD_CHECK_FAILED and the job stops submitting further work.
Output: 381_stage13/raw/b1_titlepos5/<cond>/shard_XXX.npz (skip-if-exists).
Usage:  --conds false_1,false_2,false_3,false_4 --shards 0 [--max-minutes 40]      (GPU)
        --conds false_0 --shards 0      (hard check)
        --tiny --conds true,false_0,false_1,false_2,false_3,false_4 --shards 0,1   (CPU, random 64-layer Qwen3, root b1_tiny)
"""
import argparse, importlib.util, json, os, time, datetime, hashlib, types
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; R13 = B / '381_stage13'
PLAN = R13 / 'config/prereg_addendum10.json'; PLAN_SHA = '8243a4edebcc4da00933c7647eb4e322b0e8831dbac632622e52a8316f9e7e05'
HARD_TOL = 0.05
T0 = time.monotonic()
def log(*a): print(f'[{datetime.datetime.now().isoformat(timespec="seconds")} {time.monotonic() - T0:6.0f}s]', *a, flush=True)


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


S11 = load(H / '11_stage11/361_stage11.py', 's11'); s10 = S11.s10


def roots(tiny):
    r = R13 / 'b1_tiny' if tiny else R13
    return dict(raw=r / 'raw/b1_titlepos5', chk=r / 'summary_b1_e4b5/checks', root=r)


def tiny_model():
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
    tok = s10.tokenizer(); return jlens.from_hf(hf, tok), tok


def do_shard(C, prompts, cond, shard):
    """= S11.do_titlepos residual part (+ final@63@colon rank of the first name tokens for the check)."""
    torch = C.torch; layers = sorted({l for _, l in S11.TP_PLAN} | set(S11.PROBE_LAYERS) | {63})
    res_t, res_c, res_pid, gp, gg, gr = [], [], [], [], [], []
    for pid in C.papers[C.papers.shard == shard].paper_id:
        if pid not in C.ctx: continue
        ptx, ids = prompts[pid]; it = S11.title_positions(C.tok, ptx, ids)[-1]; ic = len(ids) - 1
        acts = S11.record(C, ids, layers)
        firsts = [name[0] for ai, rids, name in C.ctx[pid]]
        lg = C.model.unembed(acts[63][ic:ic + 1].float()).float().expand(len(firsts), -1)
        gr.append(S11.ranks(lg, torch.tensor(firsts, device=C.model.input_device), torch)); gp += [pid] * len(firsts); gg += firsts
        res_t.append(np.stack([acts[l][it].float().cpu().numpy() for l in S11.PROBE_LAYERS]).astype(np.float16))
        res_c.append(np.stack([acts[l][ic].float().cpu().numpy() for l in S11.PROBE_LAYERS + [63]]).astype(np.float16)); res_pid.append(pid)
    return dict(resid_title=np.stack(res_t), resid_colon=np.stack(res_c), resid_paper_id=np.array(res_pid), probe_layers=np.array(S11.PROBE_LAYERS),
                gold_paper_id=np.array(gp), gold=np.array(gg), rank_colon63=np.concatenate(gr))


def checks(cond, shard, d, tiny):
    out = dict(cond=cond, shard=shard, n_papers=int(len(d['resid_paper_id'])), tiny=tiny)
    R = np.concatenate([d['resid_title'].reshape(-1), d['resid_colon'].reshape(-1)]).astype(np.float32)
    out['n_nonfinite'] = int((~np.isfinite(R)).sum()); out['max_abs_resid'] = float(np.abs(R[np.isfinite(R)]).max()); del R
    f = R11 / f'raw/titlepos/{cond}/shard_{shard:03d}.npz'
    if not f.exists(): out['R_status'] = 'WARN (no Stage 11 file)'; return out
    z = np.load(f); m = z['kind'] == 'first'
    ref = pd.DataFrame({'paper_id': z['paper_id'][m], 'gold': z['gold'][m], 'rank': z['final@63@colon'][m]})
    new = pd.DataFrame({'paper_id': d['gold_paper_id'], 'gold': d['gold'], 'rank_new': d['rank_colon63']})
    if len(ref) == len(new) and (ref.paper_id.to_numpy() == new.paper_id.to_numpy()).all() and (ref.gold.to_numpy() == new.gold.to_numpy()).all():
        out['R_match'] = float((ref['rank'].to_numpy() == new.rank_new.to_numpy()).mean())
        out['R_mean_abs_dlog10'] = float(np.abs(np.log10(ref['rank'].to_numpy().astype(float)) - np.log10(new.rank_new.to_numpy().astype(float))).mean())
        out['R_status'] = 'OK' if out['R_match'] >= 0.95 else 'WARN'
    else: out['R_status'] = 'WARN (row mismatch)'
    if 'resid_title' in z.files:                                   # true / false_0: residual comparison (HARD for false_0)
        if (z['resid_paper_id'] == d['resid_paper_id']).all() and z['resid_title'].shape == d['resid_title'].shape:
            rel = []
            for key in ('resid_title', 'resid_colon'):
                a_ = d[key].astype(np.float32); b_ = z[key].astype(np.float32)
                rel.append((np.linalg.norm(a_ - b_, axis=-1) / np.maximum(np.linalg.norm(b_, axis=-1), 1e-9)).reshape(-1))
                out[f'H_{key}_rel_max'] = float(rel[-1].max()); out[f'H_{key}_rel_mean'] = float(rel[-1].mean())
                out[f'H_{key}_bitexact_share'] = float((d[key] == z[key]).all(-1).mean())
            mx = float(np.concatenate(rel).max()); out['H_rel_max'] = mx
            out['H_status'] = 'PASS' if mx <= HARD_TOL else 'FAIL'
        else: out['H_status'] = 'FAIL (shape / paper mismatch)'
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shards', default='0'); ap.add_argument('--conds', default='false_1,false_2,false_3,false_4')
    ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--tiny', action='store_true'); a = ap.parse_args()
    if hashlib.sha256(PLAN.read_bytes()).hexdigest() != PLAN_SHA: raise SystemExit('PLAN CHANGED')
    R = roots(a.tiny)
    if (R['root'] / 'summary_b1_e4b5/HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    import torch
    m, _ = s10.verify(R10)
    shards = list(range(m['n_shards'])) if a.shards == 'all' else s10.parse_shards(a.shards, m['n_shards'])
    conds = a.conds.split(',')
    todo = [(c, k) for k in shards for c in conds if not (R['raw'] / c / f'shard_{k:03d}.npz').exists()]
    log('units requested', len(shards) * len(conds), 'todo', len(todo), 'tiny' if a.tiny else '')
    if not todo: return
    R['chk'].mkdir(parents=True, exist_ok=True)
    papers, toks = S11.cohort()
    model, tok = tiny_model() if a.tiny else s10.load_model()
    C = types.SimpleNamespace(torch=torch, model=model, tok=tok, papers=papers, ctx=S11.contexts_of(toks))
    prompts = {c: s10.condition_prompts(R10, papers, c)[0] for c in conds}
    env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), stage11_sha256=S11.sha_file(S11.__file__),
               plan_sha256=PLAN_SHA, protocol_sha256=m['protocol_sha256'], tiny=a.tiny, job=os.environ.get('SLURM_JOB_ID'))
    for c, k in todo:
        t0 = time.monotonic()
        d = do_shard(C, prompts[c], c, k)
        ck = checks(c, k, d, a.tiny)
        f = R['raw'] / c / f'shard_{k:03d}.npz'; f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
        meta = dict(unit=['titlepos', c, k], created=datetime.datetime.now().isoformat(timespec='seconds'), **env)
        np.savez(tmp, meta=np.array(json.dumps(meta, sort_keys=True)), **d); os.replace(tmp, f)
        (R['chk'] / f'{c}_shard_{k:03d}.json').write_text(json.dumps(ck, indent=1))
        el = time.monotonic() - t0
        log(f'{c} shard {k:03d} papers={ck["n_papers"]} {el:.0f}s', 'R', ck.get('R_status'), f"match={ck.get('R_match', float('nan')):.4f}",
            'H', ck.get('H_status', '-'), f"rel_max={ck.get('H_rel_max', float('nan')):.3g}")
        if c == 'false_0' and ck.get('H_status') != 'PASS' and not a.tiny:
            (R['root'] / 'summary_b1_e4b5/HARD_CHECK_FAILED').write_text(json.dumps(ck, indent=1)); raise SystemExit('HARD CHECK FAILED (false_0 residuals)')
        if a.max_minutes and (time.monotonic() - T0) / 60 + 1.5 * el / 60 > a.max_minutes:
            log('time budget reached; remaining units left for the next job'); return
    log('done')


if __name__ == '__main__':
    main()
