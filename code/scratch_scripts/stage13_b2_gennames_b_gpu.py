"""Item 2-11b real runner (addendum 15, LOCKED: 381_stage13/config/prereg_addendum15.json, sha256 checked at start).
Matcher v3b (stage13_b2_gennames_b_v3b.py -> v3 -> rev2 pipeline; all imported by path, not edited).

Units: the 6,841 target + control papers (cohort order), shard k = papers with index % 48 == k (~143 papers).
Per paper: Qwen3-32B chat prompt -> HF generate (greedy, 96 new tokens, batch 1, KV cache, output_hidden_states, output_logits)
-> parse -> label (M / H / P / U) -> residuals at L16..L56 for M and H names taken from the generate hidden states
(name_mean = primary, pred_first = secondary, last = descriptive), float16.
Checks:
  H1 (WARN only)   50 papers (rng 1211) generated twice in one job: number with identical tokens. Done once (summary/h1.json).
  H2 (HARD)        per shard: argmax of lm_head(stored final state) == generated next token at every analysed position;
                   < 0.99 -> HARD_CHECK_FAILED file, exit 2. Zero positions -> WARN.
  H3 (crash-only)  Stage 10 matcher on stored texts reproduces the package counts (expected 6,828/6,841); mismatch = WARN.
Saves per shard (skip if done): raw/shard_KKK.npz, names/shard_KKK.parquet, papers/shard_KKK.csv, h2/shard_KKK.csv.
Shard 0 run writes b2_gennames_b/shard0_cost.md (s/paper, peak memory, load time, H1/H2/H3, projected A100-h).
Commands: gpu --shard K [--cost] | gpu --all | tiny --root DIR
"""
import argparse, hashlib, importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
PLAN = R13 / 'config/prereg_addendum15.json'; ROOT = R13 / 'b2_gennames_b'
_sp = importlib.util.spec_from_file_location('gnb_v3b', H / '13_stage13/stage13_b2_gennames_b_v3b.py'); V3B = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V3B)
V3 = V3B.V3; B = V3.B; V3.patch()
N_SHARDS, N_H1, H2_MIN = 48, 50, 0.99
LAYERS = B.LAYERS


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def check_plan():
    sha = hashlib.sha256(PLAN.read_bytes()).hexdigest(); ref = (PLAN.parent / 'prereg_addendum15.json.sha256').read_text().split()[0]
    if sha != ref: raise SystemExit(f'PLAN CHANGED (addendum 15): {sha} != {ref}')
    return sha


def units(d):
    d = d.reset_index(drop=True).copy(); d['shard'] = np.arange(len(d)) % N_SHARDS; return d


def paths(root, k):
    return dict(npz=root / f'raw/shard_{k:03d}.npz', names=root / f'names/shard_{k:03d}.parquet', papers=root / f'papers/shard_{k:03d}.csv', h2=root / f'h2/shard_{k:03d}.csv')


def atomic(path, write):
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_name(path.stem + f'.tmp{os.getpid()}' + path.suffix); write(tmp); os.replace(tmp, path)


def h3(root, d):
    f = root / 'summary/h3.json'; f.parent.mkdir(parents=True, exist_ok=True)
    if f.exists(): return json.loads(f.read_text())
    try:
        res = B.parity(root / 'summary', d); res['status'] = 'OK' if res['H3_counts_equal'] == 6828 else 'WARN'
    except Exception:
        traceback.print_exc(); raise SystemExit('H3 comparison code crashed: stop')
    atomic(f, lambda p: p.write_text(json.dumps(res, indent=1))); log('H3', res['H3_counts_equal'], res['status']); return res


def decide_final(hf, lm, torch, tok, d):
    """hidden_states[-1]: already final-normed (lm_head only) or not; decided on one paper, recorded."""
    r = next(d.itertuples()); pr = B.V1.chat_prompt(tok, r.title, r.year); pids = tok(pr, add_special_tokens=False).input_ids
    g = B.gen_one(hf, tok, torch, pids, LAYERS, None, max_new=2); st = g['state'](-1, g['P'] - 1)[None, None]; ref = g['logits'][0][0].float()
    a = float((hf.lm_head(st)[0, 0].float() - ref).abs().max()); b = float((lm.unembed(st)[0, 0].float() - ref).abs().max())
    return (lambda h: hf.lm_head(h)) if a <= b else (lambda h: lm.unembed(h)), dict(lm_head_only=a, norm_then_lm_head=b, adopted='lm_head only' if a <= b else 'norm + lm_head')


def h1(root, hf, tok, torch, d, final_fn, pool, n=N_H1):
    f = root / 'summary/h1.json'
    if f.exists(): return json.loads(f.read_text())
    idx = np.random.default_rng(1211).choice(len(d), min(n, len(d)), replace=False); sub = d.iloc[np.sort(idx)]
    runs = [[B.process_paper(r, tok, torch, hf, final_fn, LAYERS, pool)[2]['gen_ids'] for r in sub.itertuples()] for _ in (0, 1)]
    same = sum(a == b for a, b in zip(*runs)); res = dict(n=len(sub), identical=int(same), status='OK' if same == len(sub) else 'WARN', at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    atomic(f, lambda p: p.write_text(json.dumps(res, indent=1))); log('H1 (WARN only)', res); return res


def do_shard(root, k, d, hf, tok, torch, final_fn, pool, layers=LAYERS):
    import pandas as pd
    P = paths(root, k)
    if P['npz'].exists(): log(f'shard {k:03d} done already: skip'); return None
    sub = d[d.shard == k]; names, prows, h2, vec = [], [], [], {f'{p}@{l}': [] for p in B.POS for l in layers}; t0 = time.perf_counter()
    for r in sub.itertuples():
        rows, v, prow, hh, _ = B.process_paper(r, tok, torch, hf, final_fn, layers, pool)
        names += rows; prows.append(prow); h2 += hh
        for key in vec: vec[key] += v[key]
    wall = time.perf_counter() - t0
    st, agr = B.h2_status(h2)
    N = pd.DataFrame(names); K = N[N.status.isin(['M', 'H'])]
    keys = (K.paper_id + '|' + K.item_index.astype(str)).to_numpy()
    X = {key: (np.stack(v).astype(np.float16) if v else np.zeros((0, 1), np.float16)) for key, v in vec.items()}
    atomic(P['names'], lambda p: N.to_parquet(p, index=False)); atomic(P['papers'], lambda p: pd.DataFrame(prows).to_csv(p, index=False))
    atomic(P['h2'], lambda p: pd.DataFrame(h2).to_csv(p, index=False))
    meta = dict(shard=k, papers=len(sub), wall_s=wall, H2=st, H2_agreement=agr, H2_positions=len(h2), job=os.environ.get('SLURM_JOB_ID'))
    atomic(P['npz'], lambda p: np.savez(p, key=keys, meta=np.array(json.dumps(meta)), **X))
    log(f'shard {k:03d}', meta)
    if st == 'FAIL':
        (root / 'HARD_CHECK_FAILED').write_text(json.dumps(meta)); log('H2 HARD FAIL: stop'); sys.exit(2)
    if st == 'NO_POSITIONS': log('WARN H2: no analysed positions in this shard')
    return dict(meta=meta, prows=prows, names=N)


def cost_report(root, out, load_s, fin_info, h1r, h2m, h3r, sh, peak, d, tiny=False):
    import pandas as pd
    pr = pd.DataFrame(sh['prows']); spp = sh['meta']['wall_s'] / max(1, len(pr)); N = sh['names']
    proj_gen = len(d) * spp / 3600; n_jobs = int(np.ceil(proj_gen * 60 / 38)) if spp > 0 else 0
    L = [f'# 2-11b shard 0 cost report{" (TINY CPU TEST - not 32B numbers)" if tiny else ""}', '',
         f'Job {os.environ.get("SLURM_JOB_ID")} on {os.uname().nodename}, {time.strftime("%Y-%m-%dT%H:%M:%S")}. Plan prereg_addendum15.json (locked).', '',
         '## Timing and memory', '',
         f'- model load: {load_s:.1f} s', f'- shard 0: {len(pr)} papers in {sh["meta"]["wall_s"]:.1f} s = **{spp:.2f} s/paper** '
         f'(generate {pr.t_gen.mean():.2f} s, parse/label/slice {pr.t_post.mean():.3f} s); mean generated tokens {pr.n_gen.mean():.1f}, EOS share {pr.eos.mean():.2f}, '
         f'ms per generated token {1000 * pr.t_gen.sum() / max(1, pr.n_gen.sum()):.1f}',
         f'- hidden_states per paper: mean {pr.hs_bytes.mean() / 2**20:.1f} MB, max {pr.hs_bytes.max() / 2**20:.1f} MB',
         f'- peak GPU memory allocated: {peak}', f'- final-state convention: {fin_info}', '',
         '## Checks', '',
         f'- H1 determinism (WARN only): {h1r}', f'- H2 self-consistency (HARD, >= {H2_MIN}): {h2m["H2"]} {h2m["H2_agreement"]:.4f} over {h2m["H2_positions"]} positions',
         f'- H3 matcher reproduction (crash-only): {h3r.get("H3_counts_equal")}/{h3r.get("papers")} ({h3r.get("status")})', '',
         '## Labels in shard 0', '', f'- {N.status.value_counts().to_dict()}', '',
         '## Projection (all 6,841 papers, this s/paper)', '',
         f'- generation: {proj_gen:.2f} A100-80GB h; H1 (100 extra generations, once): {100 * spp / 3600:.2f} h; '
         f'+ one model load per job (~{load_s / 60:.1f} min). About {n_jobs} jobs of ~38 usable minutes.',
         f'- total ≈ **{proj_gen + 100 * spp / 3600 + n_jobs * load_s / 3600:.2f} A100-h**', '']
    out.write_text('\n'.join(L) + '\n'); log('wrote', out)


def run(a):
    import torch, pandas as pd
    check_plan(); root = ROOT
    if (root / 'HARD_CHECK_FAILED').exists(): raise SystemExit('HARD_CHECK_FAILED present: stop')
    P_, d = B.load_papers(); d = units(d); pool = B.Pool(P_); h3r = h3(root, d)
    s12 = B.load_mod(H / '12_stage12/371_stage12.py', 's12'); t0 = time.perf_counter(); lm, tok = s12.s10.load_model(); hf = lm._hf_model; load_s = time.perf_counter() - t0
    torch.cuda.reset_peak_memory_stats(); final_fn, fin_info = decide_final(hf, lm, torch, tok, d); log('final-state convention', fin_info)
    todo = [a.shard] if a.shard is not None else range(N_SHARDS); t_start = time.monotonic()
    h1r = h1(root, hf, tok, torch, d, final_fn, pool) if (a.shard == 0 or a.cost) else (json.loads((root / 'summary/h1.json').read_text()) if (root / 'summary/h1.json').exists() else 'not run yet')
    for k in todo:
        if a.shard is None and (time.monotonic() - t_start) / 60 > a.minutes: log('budget: stop'); break
        sh = do_shard(root, k, d, hf, tok, torch, final_fn, pool)
        if sh and (a.cost or k == 0) and not (root / 'shard0_cost.md').exists():
            peak = f'{torch.cuda.max_memory_allocated() / 2**30:.1f} GiB (reserved {torch.cuda.max_memory_reserved() / 2**30:.1f} GiB)'
            cost_report(root, root / 'shard0_cost.md', load_s, fin_info, h1r, sh['meta'], h3r, sh, peak, d)


def tiny(root):
    """runner test with a random 4-layer Qwen3-shaped model on CPU, 6 papers of shard 0, H1 on 3 papers; uses a temp root."""
    import torch, transformers, jlens
    root.mkdir(parents=True, exist_ok=True); check_plan()
    P_, d = B.load_papers(); d = units(d); pool = B.Pool(P_)
    s12 = B.load_mod(H / '12_stage12/371_stage12.py', 's12'); s10 = s12.s10; tok = s10.tokenizer(); h3r = h3(root, d)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 4; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:4]
    t0 = time.perf_counter(); torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval(); lm = jlens.from_hf(hf, tok); load_s = time.perf_counter() - t0
    global LAYERS
    LAYERS = [0, 1, 2]; final_fn, fin_info = decide_final(hf, lm, torch, tok, d)
    small = d[d.shard == 0].head(6); h1r = h1(root, hf, tok, torch, small, final_fn, pool, n=3)
    sh = do_shard(root, 0, small, hf, tok, torch, final_fn, pool, layers=LAYERS)
    again = do_shard(root, 0, small, hf, tok, torch, final_fn, pool, layers=LAYERS)
    cost_report(root, root / 'shard0_cost.md', load_s, fin_info, h1r, sh['meta'], h3r, sh, 'n/a (CPU)', d, tiny=True)
    z = np.load(paths(root, 0)['npz'])
    checks = {'H3 = 6,828': h3r['H3_counts_equal'] == 6828, 'H1 ran': h1r['n'] == 3, 'H2 not FAIL': sh['meta']['H2'] != 'FAIL',
              'skip-if-done works': again is None, 'npz has all pos@layer': all(f'{p}@{l}' in z.files for p in B.POS for l in LAYERS),
              'cost report written': (root / 'shard0_cost.md').exists()}
    for k, v in checks.items(): print('RUNNER TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    ok = all(checks.values()); print('RUNNER TINY', 'PASS' if ok else 'FAIL', flush=True); return ok


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['gpu', 'tiny']); ap.add_argument('--shard', type=int); ap.add_argument('--all', action='store_true')
    ap.add_argument('--cost', action='store_true'); ap.add_argument('--minutes', type=float, default=36); ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(Path(a.root)) else 1)
    if a.shard is None and not a.all: raise SystemExit('gpu needs --shard K or --all')
    run(a)


if __name__ == '__main__':
    main()
