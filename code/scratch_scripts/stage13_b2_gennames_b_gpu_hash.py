"""2-11b runner with a generation hash / run id in EVERY per-shard file (addendum 15, locked; logic unchanged).
Why: stage13_b2_gennames_b_gpu.py do_shard (lines 91-94) writes four files per shard separately (names parquet, papers csv,
h2 csv, then npz), each atomic on its own; two jobs running the same shard at the same time could leave files of one shard
from different runs, and the label files carry no run id. This module replaces do_shard (imported module, file not edited):
  run_id  = '<SLURM_JOB_ID>-<pid>-<unix time>' of this shard run, written into names (column), papers (column), h2 (column),
            npz meta and npz array 'run_id';
  gen_sha = sha256 of the paper's generated token ids (json), written into names and papers (per paper), and into the npz as
            array 'gen_sha' aligned with 'key' (per M/H name); npz 'key' is now a plain str array (no pickle needed).
Generation, parsing, labels, residuals, H2 rule and skip-if-done are those of the original do_shard.
Commands: multi --shards 1,2,3 [--minutes 41] | tiny --root DIR
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('gnb_gpu', H / '13_stage13/stage13_b2_gennames_b_gpu.py'); G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
B = G.B


def gsha(gen_ids_json): return hashlib.sha256(gen_ids_json.encode()).hexdigest()


def do_shard_hash(root, k, d, hf, tok, torch, final_fn, pool, layers=None):
    import pandas as pd
    layers = layers or G.LAYERS; P = G.paths(root, k)
    if P['npz'].exists(): G.log(f'shard {k:03d} done already: skip'); return None
    run_id = f'{os.environ.get("SLURM_JOB_ID", "local")}-{os.getpid()}-{int(time.time())}'
    sub = d[d.shard == k]; names, prows, h2, vec = [], [], [], {f'{p}@{l}': [] for p in B.POS for l in layers}; t0 = time.perf_counter()
    for r in sub.itertuples():
        rows, v, prow, hh, _ = B.process_paper(r, tok, torch, hf, final_fn, layers, pool)
        sha = gsha(prow['gen_ids']); prow['gen_sha'] = sha; prow['run_id'] = run_id
        for x in rows: x['gen_sha'] = sha; x['run_id'] = run_id
        for x in hh: x['run_id'] = run_id
        names += rows; prows.append(prow); h2 += hh
        for key in vec: vec[key] += v[key]
    wall = time.perf_counter() - t0; st, agr = B.h2_status(h2)
    N = pd.DataFrame(names); K = N[N.status.isin(['M', 'H'])] if len(N) else N
    keys = (K.paper_id + '|' + K.item_index.astype(str)).to_numpy(dtype=str) if len(K) else np.array([], dtype=str)
    ksha = K.gen_sha.to_numpy(dtype=str) if len(K) else np.array([], dtype=str)
    X = {key: (np.stack(v).astype(np.float16) if v else np.zeros((0, 1), np.float16)) for key, v in vec.items()}
    H2 = pd.DataFrame(h2, columns=['paper_id', 'pos', 'next_tok', 'final_argmax', 'step_logit_argmax', 'run_id'])
    G.atomic(P['names'], lambda p: N.to_parquet(p, index=False)); G.atomic(P['papers'], lambda p: pd.DataFrame(prows).to_csv(p, index=False))
    G.atomic(P['h2'], lambda p: H2.to_csv(p, index=False))
    meta = dict(shard=k, papers=len(sub), wall_s=wall, H2=st, H2_agreement=agr, H2_positions=len(h2), job=os.environ.get('SLURM_JOB_ID'), run_id=run_id)
    G.atomic(P['npz'], lambda p: np.savez(p, key=keys, gen_sha=ksha, run_id=np.array(run_id), meta=np.array(json.dumps(meta)), **X))
    G.log(f'shard {k:03d}', meta)
    if st == 'FAIL': (root / 'HARD_CHECK_FAILED').write_text(json.dumps(meta)); G.log('H2 HARD FAIL: stop'); sys.exit(2)
    if st == 'NO_POSITIONS': G.log('WARN H2: no analysed positions in this shard')
    return dict(meta=meta, prows=prows, names=N)


G.do_shard = do_shard_hash


def multi(a):
    import torch
    t0 = time.monotonic(); todo = [int(x) for x in a.shards.split(',')]; G.check_plan(); root = G.ROOT
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    todo = [k for k in todo if not G.paths(root, k)['npz'].exists()]
    if not todo: G.log('all requested shards done already'); return
    P_, d = B.load_papers(); d = G.units(d); pool = B.Pool(P_); G.h3(root, d)
    s12 = B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t1 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model
    G.log(f'model load {time.perf_counter() - t1:.1f} s'); final_fn, info = G.decide_final(hf, lm, torch, tok, d); G.log('final-state convention', info)
    last = 300.0
    for k in todo:
        el = (time.monotonic() - t0) / 60
        if el + 1.5 * last / 60 + 2 > a.minutes: G.log(f'budget: stop before shard {k} (elapsed {el:.1f} min)'); break
        t2 = time.monotonic(); do_shard_hash(root, k, d, hf, tok, torch, final_fn, pool); last = time.monotonic() - t2
    G.log('worker done', json.dumps(dict(peak_GiB=torch.cuda.max_memory_allocated() / 2**30)))


def tiny(root):
    """random 4-layer model on CPU, 4 papers of shard 5, written with run id + gen hash into a temp root."""
    import torch, transformers, jlens
    root.mkdir(parents=True, exist_ok=True); G.check_plan()
    P_, d = B.load_papers(); d = G.units(d); pool = B.Pool(P_)
    s10 = B.load_mod(H / '12_stage12/371_stage12.py', 's12').s10; tok = s10.tokenizer()
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); lm = jlens.from_hf(hf, tok)
    final_fn, _ = G.decide_final(hf, lm, torch, tok, d); small = d[d.shard == 5].head(4)
    sh = do_shard_hash(root, 5, small, hf, tok, torch, final_fn, pool, layers=[0, 1, 2]); again = do_shard_hash(root, 5, small, hf, tok, torch, final_fn, pool, layers=[0, 1, 2])
    print('TINY hash runner', 'PASS' if sh and again is None else 'FAIL', sh['meta'] if sh else None, flush=True); return bool(sh) and again is None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['multi', 'tiny']); ap.add_argument('--shards'); ap.add_argument('--minutes', type=float, default=41)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(Path(a.root)) else 1)
    multi(a)


if __name__ == '__main__':
    main()
