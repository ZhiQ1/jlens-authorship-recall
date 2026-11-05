"""Stage 13 X3 per-token re-run (handbook V51; user-approved 2026-11-05). GPU, forward only, no residuals.

para_run (381_stage13.do_para_run) stored only the per-name MEAN first-author score for the four title versions
(original / paraphrase / partner B / lexical neighbour D). Addendum 4/5 ask for X3 results by token role, so this
script re-scores the SAME rows (paper_id, partner, lexical_neighbour read from raw/para_run/shard_k.npz; paraphrase
text from raw/para_gen) with the SAME prompt (381_stage13.build(tok, title, 'authors', [])) and the SAME teacher-forced
batch-1 scoring as 381_stage13.score_tf, but keeps the rank of every first-author name token with its Stage 10 row_id.
Self-check (WARN only, never stops): the per-token mean of log10(1/rank) reproduces the stored para_run scores.
Output: 381_stage13/raw/para_tok/shard_kkk.npz  (row_id, paper_id, token_index, rank_<version>), skip-if-exists.
Usage: stage13_x3_tok_gpu.py work [--shards 0,1] [--root DIR]   |   stage13_x3_tok_gpu.py tiny --root DIR (CPU, tiny model)"""
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('s13', H / '13_stage13/381_stage13.py'); s13 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s13)
s11, s10 = s13.s11, s13.s10
R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
VERS = ['original', 'paraphrase', 'partner', 'lexical']
TOL = 0.05     # |mean per-token nlr - stored score|; bf16, batch 1 both times -> expect ~0, WARN otherwise


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def paraphrases():
    para = {}
    for f in sorted((R13 / 'raw/para_gen').glob('shard_*.npz')):
        z = np.load(f); para |= dict(zip(z['paper_id'], z['paraphrase']))
    return para


def tok_ranks(C, ids_prompt, answer):
    """381_stage13.score_tf, but returns the per-token ranks (batch 1)."""
    torch = C.torch; ids = list(ids_prompt) + list(answer[:-1]); pos = [len(ids_prompt) - 1 + j for j in range(len(answer))]
    lg = s13.run_final(C, ids, pos, batch=1)[0]; g = torch.tensor(answer, device=lg.device)
    return ((lg > lg.gather(1, g[:, None])).sum(1) + 1).cpu().numpy().astype(np.int64)


def do_shard(C, k, para, nmax=None):
    z = np.load(R13 / f'raw/para_run/shard_{k:03d}.npz'); P = C.papers.set_index('paper_id')
    out = {'row_id': [], 'paper_id': [], 'token_index': []} | {f'rank_{v}': [] for v in VERS}; chk = []
    n = len(z['paper_id']) if nmax is None else min(nmax, len(z['paper_id']))
    for i in range(n):
        pid = z['paper_id'][i]; ai, rids, name = C.ctx[pid][0]
        titles = [P.loc[pid].title, para[pid], P.loc[z['partner'][i]].title, P.loc[z['lexical_neighbour'][i]].title]
        rr = {}
        for v, t in zip(VERS, titles):
            ids, _, _ = s13.build(C.tok, t, 'authors', []); rr[v] = tok_ranks(C, ids, name)
        out['row_id'] += list(rids); out['paper_id'] += [pid] * len(name); out['token_index'] += list(range(len(name)))
        for v in VERS: out[f'rank_{v}'] += list(rr[v])
        stored = [z['score_original'][i], z['score_paraphrase'][i], z['score_partner'][i], z['score_lexical'][i]]
        chk.append([float(np.mean(-np.log10(rr[v].astype(float)))) - float(s) for v, s in zip(VERS, stored)])
    chk = np.array(chk)
    d = {k_: np.array(v) for k_, v in out.items()}; d['versions'] = np.array(VERS)
    rep = dict(shard=k, n_papers=n, n_tokens=len(d['row_id']), max_abs=float(np.abs(chk).max()) if n else None,
               mean_abs=float(np.abs(chk).mean()) if n else None, share_exact=float((np.abs(chk) < 1e-9).mean()) if n else None,
               per_version_max=dict(zip(VERS, np.abs(chk).max(0).tolist())) if n else None)
    rep['status'] = 'PASS' if n and rep['max_abs'] <= TOL else 'WARN'
    return d, rep


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def run(C, shards, root, nmax=None):
    para = paraphrases(); reps = []
    for k in shards:
        f = root / f'raw/para_tok/shard_{k:03d}.npz'
        if f.exists(): log('skip (exists)', f); continue
        t0 = time.monotonic(); d, rep = do_shard(C, k, para, nmax)
        # the check is recorded, never fatal (user rule 2026-10-27)
        save(f, d, dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=rep, script_sha256=s10.sha_file(__file__), **getattr(C, 'env', {})))
        try:
            with open(root / 'logs/para_tok_check.jsonl', 'a') as fh: fh.write(json.dumps(rep) + '\n')
            log(f'para_tok shard {k:03d} rows={rep["n_tokens"]} papers={rep["n_papers"]} check {rep["status"]} max|d|={rep["max_abs"]:.4g} '
                f'mean|d|={rep["mean_abs"]:.4g} exact={rep["share_exact"]:.3f} {time.monotonic() - t0:.0f}s')
        except Exception as e: print('log warning', repr(e), flush=True)
        reps.append(rep)
    return reps


def tiny_ctx():
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 2; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:2]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.env = {'tiny': True}
    return C


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['work', 'tiny']); ap.add_argument('--shards', default='all')
    ap.add_argument('--root'); ap.add_argument('--nmax', type=int); a = ap.parse_args()
    root = Path(a.root) if a.root else R13; (root / 'logs').mkdir(parents=True, exist_ok=True)
    shards = list(range(24)) if a.shards == 'all' else [int(x) for x in a.shards.split(',')]
    if a.cmd == 'tiny':
        assert a.root, 'tiny needs --root (never writes into 381_stage13)'
        C = tiny_ctx(); reps = run(C, shards[:2], root, nmax=a.nmax or 3)
        z = np.load(root / f'raw/para_tok/shard_{shards[0]:03d}.npz')
        ok = len(z['row_id']) == len(z['rank_original']) and (z['rank_original'] >= 1).all() and len(set(z['paper_id'])) == (a.nmax or 3)
        print('TINY', 'PASS' if ok else 'FAIL', {k: z[k].shape for k in z.files}, reps); sys.exit(0 if ok else 1)
    C = s13.Ctx(); reps = run(C, shards, root)
    w = [r for r in reps if r['status'] != 'PASS']
    log(f'done {len(reps)} shards; check WARN in {len(w)}')


if __name__ == '__main__':
    main()
