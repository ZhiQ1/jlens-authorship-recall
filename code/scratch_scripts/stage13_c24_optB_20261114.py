"""C24 option B (user go 2026-11-14, ~3.6-3.8 A100 h; POST-HOC, exploratory). New file; nothing existing is edited.
Option A (stage13_c24_regen_20261114.py, shard 0) gave verdict NOT MET (median |d name lp_mean| 0.0124 > 0.01), so replay
confidence is not used. Option B regenerates EVERY shard with the frozen 2-11b generation call (B.gen_one: greedy, 96 new tokens,
batch 1, KV cache, same chat prompt) and keeps the generation-time logits statistics; the stored tokens are also replayed
(teacher-forced) so the replay-vs-generation difference is measured on all shards. Code path = option A's run_shard / evaluate,
called per shard with module K set to the shard number (no change to the option A file).
Shard 0: option A output (c24_regen_20261114/, same code, job 11871528) is reused, not regenerated again.
Per shard K -> /scratch/zhang.zhiqi2/jlens/381_stage13/c24_optB_20261114/shard_KKK/ (positions_KKK.parquet, names_KKK.parquet with
gen_lp_mean / gen_lp_first / gen_ent_pre / gen_lp_min, regen_KKK.json, decision.json). Skips shards whose names_KKK.parquet exists.
All checks are WARN only. Commands: gpu --shards 1,2,3 | tiny --out DIR
"""
import argparse, importlib.util, json, sys, time
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('c24a', H / '13_stage13/stage13_c24_regen_20261114.py'); A = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(A)
OUTB = A.R13 / 'c24_optB_20261114'


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def one(k, src, root, d, hf, tok, torch, max_new=None):
    A.K = k; sd = root / f'shard_{k:03d}'
    if (sd / f'names_{k:03d}.parquet').exists(): log('skip done shard', k); return None
    if not (sd / f'regen_{k:03d}.json').exists():
        A.run_shard(src, sd, d, hf, tok, torch, max_new=max_new)
    r = A.evaluate(sd, src=src)
    log('shard', k, json.dumps(dict(regen=r['meta']['regen_identical_share'], decision=r['decision']), default=float)); return r


def gpu(a):
    import torch
    ks = [int(x) for x in a.shards.split(',')]; A.G.check_plan(); OUTB.mkdir(parents=True, exist_ok=True)
    todo = [k for k in ks if not (OUTB / f'shard_{k:03d}' / f'names_{k:03d}.parquet').exists()]
    if not todo: log('all requested shards done', ks); return
    d = A.paper_table(); s12 = A.B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t1 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model
    log(f'model load {time.perf_counter() - t1:.1f} s')
    for k in todo:
        t1 = time.perf_counter()
        try: one(k, A.SRC, OUTB, d, hf, tok, torch)
        except Exception as e:  # a crash in one shard must not lose the others; logged, rerun picks it up
            log('SHARD ERROR', k, repr(e)); import traceback; traceback.print_exc()
        log(f'shard {k} wall {time.perf_counter() - t1:.1f} s; peak GiB {torch.cuda.max_memory_allocated() / 2**30:.1f}')


def tiny(a):
    """CPU: random 4-layer Qwen3-shaped bf16 model, 2 real shards (0, 1) cut to 2 papers each with M/H names, max 24 new tokens.
    Checks: both shard dirs written with names_KKK.parquet; skip-if-done on second call; regen check WARN not stop."""
    import torch, transformers, pandas as pd
    out = Path(a.out); src = out / 'src'; d = A.paper_table()
    for sub in ('papers', 'names'): (src / sub).mkdir(parents=True, exist_ok=True)
    for k in (0, 1):
        PP = pd.read_csv(A.SRC / f'papers/shard_{k:03d}.csv'); N = pd.read_parquet(A.SRC / f'names/shard_{k:03d}.parquet')
        keep = PP[PP.n_M + PP.n_H > 0].paper_id.head(2)
        PP[PP.paper_id.isin(keep)].to_csv(src / f'papers/shard_{k:03d}.csv', index=False); N[N.paper_id.isin(keep)].to_parquet(src / f'names/shard_{k:03d}.parquet', index=False)
    s10 = A.B.load_mod(H / '12_stage12/371_stage12.py', 's12').s10; tok = s10.tokenizer()
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
    rs = [one(k, src, out / 'o', d, hf, tok, torch, max_new=24) for k in (0, 1)]
    again = [one(k, src, out / 'o', d, hf, tok, torch, max_new=24) for k in (0, 1)]
    checks = {'two shard dirs with names files': all((out / 'o' / f'shard_{k:03d}' / f'names_{k:03d}.parquet').exists() for k in (0, 1)),
              'decision per shard': all(r is not None and 'verdict' in r['decision'] for r in rs),
              'skip-if-done': all(x is None for x in again),
              'regen WARN allowed (no stop)': all(r['meta']['regen_check'] in ('OK', 'WARN') for r in rs)}
    for k_, v in checks.items(): print('C24 OPTB TINY CHECK', 'PASS' if v else 'FAIL', k_, flush=True)
    ok = all(checks.values()); print('C24 OPTB TINY', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['gpu', 'tiny']); ap.add_argument('--shards'); ap.add_argument('--out'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    gpu(a)


if __name__ == '__main__':
    main()
