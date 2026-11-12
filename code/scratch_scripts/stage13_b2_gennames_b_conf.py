"""2-11b POST-HOC generation-confidence baseline (事后，探索性; user approval 2026-11-12). Does NOT change the addendum-15 verdict.
New file; the locked runner / analysis are only imported by path.

GPU step (this file): teacher-forced replay of the STORED generated tokens of every paper (papers/shard_KKK.csv gen_ids) after the
same chat prompt (v1 chat_prompt, Qwen3 template, enable_thinking=False), Qwen3-32B bf16, one forward per paper (use_cache=False).
Per M/H name (names/shard_KKK.parquet, absolute token positions tok_first..tok_last):
  (a) lp_first = log p(first name token) at the pre-name position tok_first-1, ent_pre = entropy of the next-token
      distribution there;
  (b) lp_mean = mean log p over all name tokens (each token from the position before it); also lp_sum, n_tok.
Replay check: share of generated positions (P-1 .. end-1) where the teacher-forced argmax == the stored generated next token;
also the share of stored H2 positions where it == the stored final-layer argmax (h2/shard_KKK.csv). If a shard is < 0.99 on the
first measure: conf/REPLAY_STOP is written and the job exits 3 (nothing further runs; chain stops and mails).
Outputs per shard (atomic, skip if done): conf/shard_KKK.parquet, conf/replay_KKK.json.
Commands: gpu --shards 0 | gpu --shards 1,2,... [--minutes 41] | tiny --out DIR
"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); ROOT = R13 / 'b2_gennames_b'
_sp = importlib.util.spec_from_file_location('gnb_gpu', H / '13_stage13/stage13_b2_gennames_b_gpu.py'); G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
B = G.B; MIN_AGREE = 0.99


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def atomic(path, write):
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_name(path.stem + f'.tmp{os.getpid()}' + path.suffix); write(tmp); os.replace(tmp, path)


def out_paths(out, k): return out / f'conf/shard_{k:03d}.parquet', out / f'conf/replay_{k:03d}.json'


def replay_shard(src, out, k, d, hf, tok, torch):
    """src: root with names/papers/h2 of shard k; out: root receiving conf/. d: paper table (title, year) indexed by paper_id."""
    import pandas as pd
    fp, fj = out_paths(out, k)
    if fp.exists() and fj.exists(): log(f'conf shard {k:03d} done already: skip'); return json.loads(fj.read_text())
    N = pd.read_parquet(src / f'names/shard_{k:03d}.parquet'); PP = pd.read_csv(src / f'papers/shard_{k:03d}.csv')
    try: H2 = pd.read_csv(src / f'h2/shard_{k:03d}.csv')
    except Exception: H2 = pd.DataFrame(columns=['paper_id', 'pos', 'final_argmax'])
    K = N[N.status.isin(['M', 'H'])]; g = K.groupby('paper_id'); h2g = H2.groupby('paper_id') if len(H2) else None
    rows = []; agree = n_pos = h2a = h2n = 0; plen_bad = 0; t0 = time.perf_counter()
    for r in PP.itertuples():
        pr = B.V1.chat_prompt(tok, d.loc[r.paper_id, 'title'], d.loc[r.paper_id, 'year']); pids = tok(pr, add_special_tokens=False).input_ids
        if len(pids) != int(r.n_prompt): plen_bad += 1
        gen = json.loads(r.gen_ids); seq = pids + gen; P = len(pids)
        if len(gen) < 2: continue
        with torch.inference_mode():
            lg = hf(input_ids=torch.tensor([seq[:-1]], device=hf.device), use_cache=False).logits[0]      # [L-1, V]; row p predicts seq[p+1]
            am = lg[P - 1:].argmax(-1).cpu().numpy(); tgt = np.array(seq[P:])
            agree += int((am == tgt).sum()); n_pos += len(tgt)
            if h2g is not None and r.paper_id in h2g.groups:
                hh = H2.loc[h2g.groups[r.paper_id]]; tfa = lg[torch.tensor(hh.pos.to_numpy(), device=lg.device)].argmax(-1).cpu().numpy()
                h2a += int((tfa == hh.final_argmax.to_numpy()).sum()); h2n += len(hh)
            if r.paper_id in g.groups:
                s = K.loc[g.groups[r.paper_id]]
                for x in s.itertuples():
                    f, l = int(x.tok_first), int(x.tok_last); pos = torch.arange(f - 1, l, device=lg.device)
                    lp = torch.log_softmax(lg[pos].float(), -1); toks = torch.tensor(seq[f:l + 1], device=lg.device)
                    tl = lp.gather(1, toks[:, None])[:, 0].cpu().numpy(); ent = float(-(lp[0].exp() * lp[0]).sum())
                    rows.append(dict(paper_id=x.paper_id, item_index=int(x.item_index), status=x.status, lp_first=float(tl[0]), ent_pre=ent,
                                     lp_mean=float(tl.mean()), lp_sum=float(tl.sum()), n_tok=len(tl), tf_argmax_first_eq=bool(int(lp[0].argmax()) == seq[f])))
    C = pd.DataFrame(rows, columns=['paper_id', 'item_index', 'status', 'lp_first', 'ent_pre', 'lp_mean', 'lp_sum', 'n_tok', 'tf_argmax_first_eq'])
    rep = dict(shard=k, papers=len(PP), names=len(C), positions=n_pos, agree=agree, agreement=agree / max(1, n_pos),
               h2_positions=h2n, h2_agree=h2a, agreement_vs_stored_final_argmax=(h2a / h2n) if h2n else None,
               prompt_length_mismatch=plen_bad, wall_s=time.perf_counter() - t0, job=os.environ.get('SLURM_JOB_ID'))
    atomic(fp, lambda p: C.to_parquet(p, index=False)); atomic(fj, lambda p: p.write_text(json.dumps(rep, indent=1)))
    log(f'conf shard {k:03d}', rep); return rep


def gate(out, rep):
    if rep['agreement'] < MIN_AGREE:
        (out / 'conf').mkdir(parents=True, exist_ok=True); (out / 'conf/REPLAY_STOP').write_text(json.dumps(rep, indent=1))
        log(f'REPLAY CHECK FAILED: {rep["agreement"]:.4f} < {MIN_AGREE} (shard {rep["shard"]}): stop'); sys.exit(3)


def paper_table():
    _, d = B.load_papers(); return d.set_index('paper_id')


def gpu(a):
    import torch
    t0 = time.monotonic(); G.check_plan(); out = ROOT
    if (out / 'conf/REPLAY_STOP').exists(): raise SystemExit('REPLAY_STOP present: stop')
    todo = [int(x) for x in a.shards.split(',')]; todo = [k for k in todo if not all(p.exists() for p in out_paths(out, k))]
    if not todo: log('all requested conf shards done already'); return
    d = paper_table()
    s12 = B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t1 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model
    log(f'model load {time.perf_counter() - t1:.1f} s'); last = 60.0
    for k in todo:
        el = (time.monotonic() - t0) / 60
        if el + 1.5 * last / 60 + 2 > a.minutes: log(f'budget: stop before shard {k} (elapsed {el:.1f} min)'); break
        t2 = time.monotonic(); rep = replay_shard(ROOT, out, k, d, hf, tok, torch); last = time.monotonic() - t2; gate(out, rep)
    log('conf worker done', json.dumps(dict(peak_GiB=torch.cuda.max_memory_allocated() / 2**30)))


def tiny(a):
    """CPU, random 4-layer Qwen3-shaped model (same seed/config as the runner tiny tests):
    (1) replay of the hash-runner tiny shard 5 (generated by this same tiny model) -> agreement should be ~1.0;
    (2) replay of 6 papers of the REAL shard 0 (Qwen3-32B text; random model) -> metrics for real M/H names, agreement low ->
        the gate must write REPLAY_STOP in the test root and exit 3 (caught here)."""
    import torch, transformers, pandas as pd
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True); d = paper_table()
    s10 = B.load_mod(H / '12_stage12/371_stage12.py', 's12').s10; tok = s10.tokenizer()
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    r1 = replay_shard(R13 / 'b2_gennames_b_tiny/hash_test_11764219', out / 'own', 5, d, hf, tok, torch)
    sub = out / 'real0'; (sub / 'names').mkdir(parents=True, exist_ok=True); (sub / 'papers').mkdir(exist_ok=True); (sub / 'h2').mkdir(exist_ok=True)
    PP = pd.read_csv(ROOT / 'papers/shard_000.csv'); N = pd.read_parquet(ROOT / 'names/shard_000.parquet'); H2 = pd.read_csv(ROOT / 'h2/shard_000.csv')
    keep = PP[PP.n_M + PP.n_H > 0].paper_id.head(6)
    PP[PP.paper_id.isin(keep)].to_csv(sub / 'papers/shard_000.csv', index=False); N[N.paper_id.isin(keep)].to_parquet(sub / 'names/shard_000.parquet', index=False)
    H2[H2.paper_id.isin(keep)].to_csv(sub / 'h2/shard_000.csv', index=False)
    r2 = replay_shard(sub, sub, 0, d, hf, tok, torch); C = pd.read_parquet(out_paths(sub, 0)[0])
    stopped = False
    try: gate(sub, r2)
    except SystemExit as e: stopped = e.code == 3
    again = replay_shard(sub, sub, 0, d, hf, tok, torch)
    checks = {'own-model replay agreement >= 0.99': r1['agreement'] >= 0.99, 'prompt lengths match stored n_prompt': r1['prompt_length_mismatch'] == 0 and r2['prompt_length_mismatch'] == 0,
              'metrics for every M/H name of the 6 real papers': len(C) == int((N.paper_id.isin(keep) & N.status.isin(['M', 'H'])).sum()) and len(C) > 0,
              'metrics finite, lp <= 0, entropy >= 0': bool(np.isfinite(C[['lp_first', 'ent_pre', 'lp_mean']].to_numpy()).all() and (C.lp_first <= 0).all() and (C.ent_pre >= 0).all()),
              'gate stops on low agreement (REPLAY_STOP written)': stopped and (sub / 'conf/REPLAY_STOP').exists(),
              'skip-if-done': again == r2}
    for k_, v in checks.items(): print('CONF TINY CHECK', 'PASS' if v else 'FAIL', k_, flush=True)
    print('own', r1, '\nreal0', r2, flush=True); ok = all(checks.values()); print('CONF TINY', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['gpu', 'tiny']); ap.add_argument('--shards'); ap.add_argument('--minutes', type=float, default=41)
    ap.add_argument('--out'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    gpu(a)


if __name__ == '__main__':
    main()
