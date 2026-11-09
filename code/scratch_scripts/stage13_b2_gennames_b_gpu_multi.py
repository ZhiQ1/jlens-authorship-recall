"""2-11b (addendum 15, locked) multi-shard GPU worker: runs a given list of shards in one job with one model load.
Imports stage13_b2_gennames_b_gpu.py by path (not edited) and reuses its plan check, H3, final-state decision and do_shard
(skip-if-done, atomic saves, H2 HARD stop -> exit 2). H1 was done in the shard-0 job (summary/h1.json); not repeated.
Budget: before each shard, stop if elapsed + 1.5 x (last shard time) + 2 min > --minutes (default 41 of a 45-min job).
Usage: python stage13_b2_gennames_b_gpu_multi.py --shards 1,2,3,4,5,6
"""
import argparse, importlib.util, json, sys, time
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('gnb_gpu', H / '13_stage13/stage13_b2_gennames_b_gpu.py'); G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)


def main():
    import torch
    ap = argparse.ArgumentParser(); ap.add_argument('--shards', required=True); ap.add_argument('--minutes', type=float, default=41); a = ap.parse_args()
    t0 = time.monotonic(); todo = [int(x) for x in a.shards.split(',')]; G.check_plan(); root = G.ROOT
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    todo = [k for k in todo if not G.paths(root, k)['npz'].exists()]
    if not todo: G.log('all requested shards done already'); return
    P_, d = G.B.load_papers(); d = G.units(d); pool = G.B.Pool(P_); G.h3(root, d)
    s12 = G.B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t1 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model
    G.log(f'model load {time.perf_counter() - t1:.1f} s'); final_fn, info = G.decide_final(hf, lm, torch, tok, d); G.log('final-state convention', info)
    last = 300.0
    for k in todo:
        el = (time.monotonic() - t0) / 60
        if el + 1.5 * last / 60 + 2 > a.minutes: G.log(f'budget: stop before shard {k} (elapsed {el:.1f} min)'); break
        t2 = time.monotonic(); G.do_shard(root, k, d, hf, tok, torch, final_fn, pool); last = time.monotonic() - t2
    G.log('worker done', json.dumps(dict(peak_GiB=torch.cuda.max_memory_allocated() / 2**30)))


if __name__ == '__main__':
    main()
