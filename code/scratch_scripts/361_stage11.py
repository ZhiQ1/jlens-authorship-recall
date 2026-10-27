"""Stage 11 - causal and context follow-ups to Stage 10 (2026-10-26; user: "ok do all of it").

Reads the frozen Stage 10 cohort, prompts and conditions read-only (/scratch/$USER/jlens/351_stage10); never writes there.
Outputs: /scratch/$USER/jlens/361_stage11/.

E1 patch     Activation patching. Each author context is run with the true title and with the best-matched false title
             (false_0). In the false run, the residual (output of decoder block l) at the aligned tail - the prompt tokens
             after the title, shared by both prompts (closing quote, year, "Authors:"), plus all name positions - is
             replaced by the true run's, one layer l at a time. Score: rank of the gold name token at the model output.
             recovery(l) = mean(patched - false) / mean(true - false), log10(1/rank) per token, paper means.
             l = 63 replaces the output itself and must recover exactly (sanity check).
E2 knockout  Attention knockout, true title. From decoder layer l on (l, l+1, ..., 63), every position after the title is
             blocked from attending to the title tokens. l = 64 blocks nothing but uses the same explicit mask (baseline).
             loss(l) = mean(baseline - knocked) / mean(true - false_0).
E3 chain     Author chain. All authors of a paper in one sequence, "Authors: A1, A2, ..." (each name tokenised exactly
             as in Stage 10, joined by the "," token), for all 7 Stage 10 conditions; every name token scored at the
             model output and with the logit lens / public Jacobian lens at L40-L62. Rows keep Stage 10 row ids, so
             chain and isolated scores are paired token by token.

E1/E2 sample: citation bins with >= 30 target and >= 30 control papers (as Stage 10 B); per bin min(60, n_t, n_c) papers
of each group, seed 11; 50 papers per shard. E3: all 9,108 papers, Stage 10 shards (128 papers) x 7 conditions.

Commands: freeze | preflight (CPU) | smoke (GPU, gate for work) | work (GPU, claims units) | remaining | analyze (CPU)
"""
import argparse, hashlib, importlib.util, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np

DIR = Path(__file__).resolve().parent
S10DIR = Path.home() / 'jlens_work/10_stage10'
_spec = importlib.util.spec_from_file_location('s10fix1', S10DIR / '351_stage10_fix1.py')
_fix1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_fix1)
s10 = _fix1.s10                                   # frozen Stage 10 module with the fix-1 load_model (and weight prefetch)
R10 = s10.ROOT
ROOT = Path('/scratch') / os.environ.get('USER', '') / 'jlens/361_stage11'
CONDS = s10.condition_names()
PATCH_LAYERS = [24, 32, 40, 48, 50, 52, 54, 56, 57, 58, 59, 60, 61, 62, 63]
KO_LAYERS = [0, 24, 32, 40, 48, 50, 52, 54, 56, 58, 60, 62, 64]     # 64 = nothing blocked (explicit-mask baseline)
CHAIN_LAYERS = [40, 48, 52, 56, 58, 60, 62]
CHAIN_PLAN = [('final', 63)] + [(r, l) for r in ('logit', 'jlens_public') for l in CHAIN_LAYERS]
PER_BIN, MIN_BIN, PAPERS_PER_SHARD, SEED = 60, 30, 50, 11
FALSE_FOR_PATCH = 'false_0'


def now(): return time.strftime('%Y-%m-%dT%H:%M:%S')
def log(*x): print(now(), *x, flush=True)
def sha_file(p): return s10.sha_file(p)
def dump(p, o): Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(json.dumps(o, indent=1, sort_keys=True, default=str))
def load(p): return json.loads(Path(p).read_text())


# ------------------------------------------------------------------ data
def cohort():
    import pandas as pd
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'author_index', 'token_index', 'token_id'])
    return papers, toks


def contexts_of(toks):
    """{paper_id: [(author_index, [row_ids], [token_ids]), ...] sorted by author_index}"""
    out = {}
    for (pid, ai), g in toks.sort_values(['paper_id', 'author_index', 'token_index']).groupby(['paper_id', 'author_index'], sort=False):
        out.setdefault(pid, []).append((int(ai), g.row_id.tolist(), g.token_id.tolist()))
    for v in out.values(): v.sort()
    return out


def title_positions(tok, prompt, pids):
    """token positions overlapping the title characters (between 'titled "' and the closing '" (')."""
    e = tok(prompt, return_offsets_mapping=True)
    if e.input_ids != pids: raise RuntimeError('prompt ids differ from frozen ids')
    a = prompt.index('titled "') + len('titled "'); b = prompt.rindex('" (')
    return [i for i, (x, y) in enumerate(e.offset_mapping) if x < b and y > a]


def common_suffix(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]: n += 1
    return n


# ------------------------------------------------------------------ freeze
def freeze(a):
    import pandas as pd
    m, lenses = s10.verify(R10); cm = s10.verify_conditions(R10)
    papers, toks = cohort()
    rng = np.random.default_rng(SEED); rows = []
    for b, g in papers.groupby('citation_bin'):
        t = g[g.group_tight == 'target']; c = g[g.group_tight == 'control']
        if len(t) < MIN_BIN or len(c) < MIN_BIN: continue
        k = min(PER_BIN, len(t), len(c))
        for grp, sub in (('target', t), ('control', c)):
            pick = sub.iloc[rng.choice(len(sub), k, replace=False)]
            rows += [dict(paper_id=p, group=grp, citation_bin=b) for p in pick.paper_id]
    smp = pd.DataFrame(rows).sort_values(['citation_bin', 'group', 'paper_id']).reset_index(drop=True)
    smp['shard'] = np.arange(len(smp)) // PAPERS_PER_SHARD
    tok = s10.tokenizer(); pf, _ = s10.condition_prompts(R10, papers, FALSE_FOR_PATCH); pt_, _ = s10.condition_prompts(R10, papers, 'true')
    tpos, suf = [], []
    for pid in smp.paper_id:
        (ptx, pids), (pfx, fids) = pt_[pid], pf[pid]
        tp = title_positions(tok, ptx, pids); tf = title_positions(tok, pfx, fids); tpos.append(json.dumps(tp))
        # aligned tail: shared suffix, cut so it starts after the last title token in both prompts
        s = min(common_suffix(pids, fids), len(pids) - 1 - max(tp), len(fids) - 1 - max(tf)); suf.append(s)
        if s < 3: raise RuntimeError(f'{pid}: aligned tail {s} too short')
    smp['title_pos'] = tpos; smp['tail_prompt'] = suf
    ROOT.mkdir(parents=True, exist_ok=True); (ROOT / 'config').mkdir(exist_ok=True)
    smp.to_parquet(ROOT / 'config/sample.parquet', index=False)
    proto = dict(version='stage11_v1', created=now(), doc=__doc__, model=s10.MODEL, revision=s10.REV,
                 patch_layers=PATCH_LAYERS, ko_layers=KO_LAYERS, chain_plan=CHAIN_PLAN, false_for_patch=FALSE_FOR_PATCH,
                 sample=dict(per_bin=PER_BIN, min_bin=MIN_BIN, seed=SEED, papers_per_shard=PAPERS_PER_SHARD, n=len(smp),
                             n_target=int((smp.group == 'target').sum()), n_control=int((smp.group == 'control').sum()),
                             bins=sorted(smp.citation_bin.unique().tolist()), sha256=sha_file(ROOT / 'config/sample.parquet')),
                 stage10=dict(protocol_sha256=m['protocol_sha256'], lens_public_sha256=lenses['public']['sha256'],
                              inputs={f: sha_file(R10 / f) for f in ['cohort/papers.parquet', 'cohort/name_tokens.parquet', 'cohort/conditions/prompts.parquet']}),
                 script_sha256=sha_file(__file__))
    dump(ROOT / 'config/protocol.json', proto)
    print(json.dumps({k: proto['sample'][k] for k in ('n', 'n_target', 'n_control', 'bins')}, indent=1))


def verify():
    pr = load(ROOT / 'config/protocol.json')
    if sha_file(ROOT / 'config/sample.parquet') != pr['sample']['sha256']: raise RuntimeError('sample.parquet changed')
    for f, h in pr['stage10']['inputs'].items():
        if sha_file(R10 / f) != h: raise RuntimeError(f'Stage 10 input changed: {f}')
    return pr


# ------------------------------------------------------------------ units
def units():
    import pandas as pd
    smp = pd.read_parquet(ROOT / 'config/sample.parquet'); m, _ = s10.verify(R10)
    n12 = int(smp.shard.max()) + 1
    return [('patch', None, k) for k in range(n12)] + [('knockout', None, k) for k in range(n12)] + \
           [('chain', c, k) for c in CONDS for k in range(m['n_shards'])]


def out_path(u, root=None):
    e, c, k = u; root = root or ROOT
    return root / 'raw' / e / (f'{c}/' if c else '') / f'shard_{k:03d}.npz'


def remaining(a):
    left = [u for u in units() if not out_path(u).exists()]
    by = {}
    for e, c, k in left: by[e] = by.get(e, 0) + 1
    print(f'{len(left)} of {len(units())} units missing', by)


# ------------------------------------------------------------------ GPU helpers
class Ctx:
    """model, tokenizer, lenses, data; loaded once per job."""
    def __init__(self):
        import torch, pandas as pd
        self.torch = torch
        self.m, self.lenses = s10.verify(R10)
        self.papers, toks = cohort(); self.ctx = contexts_of(toks)
        self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in CONDS}
        self.smp = pd.read_parquet(ROOT / 'config/sample.parquet')
        self.model, self.tok = s10.load_model()
        self.L = s10.open_lenses(self.lenses, CHAIN_PLAN, self.model)
        self.comma = self.tok.encode(',', add_special_tokens=False)
        assert self.comma == [11]
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], script_sha256=sha_file(__file__))


def ranks(logits, gold, torch):
    r, _, _, _ = s10.score(logits.float(), gold, torch); return r


def run_final(C, ids, positions, patch=None, mask_fn=None, batch=1):
    """forward of `batch` copies of ids; returns final-output logits [batch, len(positions), V].
    patch: {layer: [(element, tail_len, tensor[tail_len, d])]} replaces block outputs; mask_fn(layer) -> 4D mask or None."""
    torch = C.torch; model = C.model; handles = []
    x = torch.tensor([ids] * batch, device=model.input_device)
    try:
        for l, items in (patch or {}).items():
            def hook(mod, inp, out, items=items):
                h = out if torch.is_tensor(out) else out[0]
                for e, n, t in items: h[e, -n:] = t.to(h.device, h.dtype)
                return out
            handles.append(model.layers[l].register_forward_hook(hook))
        if mask_fn is not None:
            for l in range(len(model.layers)):
                def pre(mod, args, kwargs, l=l):
                    mk = mask_fn(l)
                    if mk is not None: kwargs['attention_mask'] = mk.to(next(mod.parameters()).device)
                    return args, kwargs
                handles.append(model.layers[l].register_forward_pre_hook(pre, with_kwargs=True))
        from jlens.hooks import ActivationRecorder
        with torch.inference_mode(), ActivationRecorder(model.layers, at=[63]) as rec:
            model.forward(x)
            h = rec.activations[63][:, positions]
            return torch.stack([model.unembed(h[i].float()).float() for i in range(batch)])
    finally:
        for hd in handles: hd.remove()


def record(C, ids, layers):
    torch = C.torch
    from jlens.hooks import ActivationRecorder
    with torch.inference_mode(), ActivationRecorder(C.model.layers, at=layers) as rec:
        C.model.forward(torch.tensor([ids], device=C.model.input_device))
        return {l: rec.activations[l][0].detach().clone() for l in layers}


def do_patch(C, shard):
    torch = C.torch; rows, out_t, out_f, out_p = [], [], [], []
    pf = C.prompts[FALSE_FOR_PATCH]
    for r in C.smp[C.smp.shard == shard].itertuples():
        pt = json.loads(C.P.loc[r.paper_id].prompt_ids); pfi = pf[r.paper_id][1]
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; tail = r.tail_prompt + len(name) - 1
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = record(C, T, PATCH_LAYERS)
            lt = run_final(C, T, posT)[0]; lf = run_final(C, F, posF)[0]
            patch = {}
            for i, l in enumerate(PATCH_LAYERS): patch.setdefault(l, []).append((i, tail, acts[l][-tail:]))
            lp = run_final(C, F, posF, patch=patch, batch=len(PATCH_LAYERS))
            rows += rids; out_t.append(ranks(lt, gold, torch)); out_f.append(ranks(lf, gold, torch))
            out_p.append(np.stack([ranks(lp[i], gold, torch) for i in range(len(PATCH_LAYERS))], 1))
    return dict(row_id=np.array(rows), rank_true=np.concatenate(out_t), rank_false=np.concatenate(out_f),
                rank_patch=np.concatenate(out_p), layers=np.array(PATCH_LAYERS))


def ko_mask(C, T_len, title_pos, ko_layers, dtype):
    """returns mask_fn(layer) -> additive mask [B,1,T,T] (0 allowed, min blocked)."""
    torch = C.torch; B = len(ko_layers)
    causal = torch.ones(T_len, T_len, dtype=torch.bool).tril()
    blk = torch.zeros(T_len, T_len, dtype=torch.bool)
    tp = torch.tensor(title_pos); after = torch.arange(max(title_pos) + 1, T_len)
    blk[after[:, None], tp[None, :]] = True
    neg = torch.finfo(dtype).min; cache = {}
    def fn(layer):
        key = tuple(layer >= k for k in ko_layers)
        if key not in cache:
            allow = causal[None].repeat(B, 1, 1)
            for i, on in enumerate(key):
                if on: allow[i] &= ~blk
            mk = torch.zeros(B, 1, T_len, T_len, dtype=dtype); mk.masked_fill_(~allow[:, None], neg); cache[key] = mk
        return cache[key]
    return fn


def do_knockout(C, shard):
    torch = C.torch; rows, out_k = [], []
    dtype = next(C.model.layers[0].parameters()).dtype
    for r in C.smp[C.smp.shard == shard].itertuples():
        pt = json.loads(C.P.loc[r.paper_id].prompt_ids); tpos = json.loads(r.title_pos)
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; pos = [len(pt) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            lk = run_final(C, T, pos, mask_fn=ko_mask(C, len(T), tpos, KO_LAYERS, dtype), batch=len(KO_LAYERS))
            rows += rids; out_k.append(np.stack([ranks(lk[i], gold, torch) for i in range(len(KO_LAYERS))], 1))
    return dict(row_id=np.array(rows), rank_ko=np.concatenate(out_k), layers=np.array(KO_LAYERS))


def chain_ids(C, pids, ctxs):
    ids, pos, rows, gold, aidx = list(pids), [], [], [], []
    for n, (ai, rids, name) in enumerate(ctxs):
        if n: ids += C.comma
        for j, t in enumerate(name):
            pos.append(len(ids) - 1); ids.append(t); rows.append(rids[j]); gold.append(t); aidx.append(n)
    return ids[:-1], pos, rows, gold, aidx


def do_chain(C, cond, shard):
    torch = C.torch; prompts = C.prompts[cond]
    out = {f'{r}@{l}': [] for r, l in CHAIN_PLAN}; rows, chain_pos = [], []
    for pid in C.papers[C.papers.shard == shard].paper_id:
        if pid not in C.ctx: continue
        ids, pos, rr, gold, aidx = chain_ids(C, prompts[pid][1], C.ctx[pid])
        res = s10.fast_readout(C.model, C.L, ids, pos, CHAIN_PLAN, torch)
        g = torch.tensor(gold, device=C.model.input_device)
        for (r, l), lg in res.items(): out[f'{r}@{l}'].append(ranks(lg, g, torch))
        rows += rr; chain_pos += aidx
    return dict(row_id=np.array(rows), chain_index=np.array(chain_pos), **{k: np.concatenate(v) for k, v in out.items()})


def compute(C, u):
    e, c, k = u
    return do_patch(C, k) if e == 'patch' else do_knockout(C, k) if e == 'knockout' else do_chain(C, c, k)


def save(u, d, env, root=None):
    f = out_path(u, root); f.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(unit=list(u), created=now(), protocol_sha256=sha_file(ROOT / 'config/protocol.json'), **env)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


# ------------------------------------------------------------------ smoke (GPU gate)
def smoke(a):
    verify(); rep = smoke_run(Ctx())
    if rep['status'] != 'PASS': sys.exit(2)


def smoke_run(C):
    """4 sample papers + 2 chain papers into a temp root, then checks; writes reports/smoke.json (PASS needed by work)."""
    orig = (C.smp, C.papers)
    try: return _smoke(C)
    finally: C.smp, C.papers = orig


def _smoke(C):
    torch = C.torch; tmp = ROOT / 'smoke'; checks = {}
    smp = C.smp.groupby('group').head(2)
    C.smp = smp.assign(shard=0)
    p = compute(C, ('patch', None, 0)); save(('patch', None, 0), p, C.env, tmp)
    k = compute(C, ('knockout', None, 0)); save(('knockout', None, 0), k, C.env, tmp)
    # Stage 10 final ranks for the same rows
    s10r = {}
    for cond in ('true', FALSE_FOR_PATCH):
        z = [np.load(s10.out_file(R10, 'final', 63, sh, cond)) for sh in sorted(set(C.papers[C.papers.paper_id.isin(smp.paper_id)].shard))]
        s10r[cond] = dict(zip(np.concatenate([q['row_id'] for q in z]), np.concatenate([q['rank'] for q in z])))
    ref_t = np.array([s10r['true'][r] for r in p['row_id']]); ref_f = np.array([s10r[FALSE_FOR_PATCH][r] for r in p['row_id']])
    i63 = PATCH_LAYERS.index(63)
    checks['patch_true_matches_stage10'] = float((p['rank_true'] == ref_t).mean())
    checks['patch_false_matches_stage10'] = float((p['rank_false'] == ref_f).mean())
    checks['patch_L63_equals_true'] = float((p['rank_patch'][:, i63] == p['rank_true']).mean())
    nl = lambda r: -np.log10(r.astype(float))
    checks['patch_recovery_L63'] = float((nl(p['rank_patch'][:, i63]) - nl(p['rank_false'])).mean() / max(1e-9, (nl(p['rank_true']) - nl(p['rank_false'])).mean()))
    kt = np.array([s10r['true'][r] for r in k['row_id']]); i64 = KO_LAYERS.index(64)
    checks['ko_baseline_matches_stage10'] = float((k['rank_ko'][:, i64] == kt).mean())
    checks['ko_baseline_mean_abs_dlog10rank'] = float(np.abs(nl(k['rank_ko'][:, i64]) - nl(kt)).mean())   # explicit mask -> other SDPA kernel (bf16)
    checks['ko_L0_lowers_score'] = float(nl(k['rank_ko'][:, i64]).mean() - nl(k['rank_ko'][:, KO_LAYERS.index(0)]).mean())
    pid2 = C.papers.paper_id.iloc[:2].tolist(); C.papers = C.papers[C.papers.paper_id.isin(pid2)]
    ch = compute(C, ('chain', 'true', int(C.papers.shard.iloc[0]))); save(('chain', 'true', 0), ch, C.env, tmp)
    z = np.load(s10.out_file(R10, 'final', 63, int(C.papers.shard.iloc[0]), 'true')); ref = dict(zip(z['row_id'], z['rank']))
    first = ch['chain_index'] == 0
    checks['chain_first_author_matches_stage10'] = float((ch['final@63'][first] == np.array([ref[r] for r in ch['row_id'][first]])).mean())
    refc = np.array([ref[r] for r in ch['row_id'][first]])
    checks['chain_first_author_mean_abs_dlog10rank'] = float(np.abs(nl(ch['final@63'][first]) - nl(refc)).mean())
    checks['chain_n_rows'] = int(len(ch['row_id']))
    ok = (checks['patch_true_matches_stage10'] >= .9 and checks['patch_false_matches_stage10'] >= .9 and checks['patch_L63_equals_true'] >= .99
          and abs(checks['patch_recovery_L63'] - 1) < .02 and checks['ko_L0_lowers_score'] > 0
          # same computation through a different kernel or sequence length: bf16 noise only (Stage 10 parity: max 0.37 logit)
          and checks['ko_baseline_matches_stage10'] >= .75 and checks['ko_baseline_mean_abs_dlog10rank'] <= .05
          and checks['chain_first_author_matches_stage10'] >= .75 and checks['chain_first_author_mean_abs_dlog10rank'] <= .05)
    rep = dict(status='PASS' if ok else 'FAIL', created=now(), checks=checks, gpu=C.env['gpu'], script_sha256=C.env['script_sha256'])
    dump(ROOT / 'reports/smoke.json', rep); print(json.dumps(rep, indent=1), flush=True)
    if not ok: stop_queue('Stage 11 smoke test FAIL')
    return rep


def stop_queue(reason):
    """on a failed gate: hold every pending Stage 11 worker and Stage 10 pool job (scontrol hold: reversible, nothing is
    cancelled) and pause the Stage 10 dispatcher, so no further GPU allocation is spent on a known failure."""
    if os.environ.get('SLURM_JOB_PARTITION') not in ('gpu', 'gpu-short', 'gpu-interactive'):
        log('stop_queue skipped (not a GPU job):', reason); return
    try:
        (R10 / 'logs/pool/PAUSED').write_text(json.dumps(dict(created=now(), reason=reason, by=os.environ.get('SLURM_JOB_ID'))))
        q = subprocess.run(['squeue', '-u', os.environ['USER'], '-h', '-t', 'PENDING', '-o', '%i|%j'], capture_output=True, text=True, timeout=90).stdout
        ids = [l.split('|')[0] for l in q.split() if l.split('|')[1].startswith(('s11w', 's10p_'))]
        if ids: subprocess.run(['scontrol', 'hold', ','.join(ids)], timeout=90)
        log('STOP:', reason, '- held', len(ids), 'pending jobs; release with: scontrol release <ids>')
    except Exception as e: log('stop_queue failed:', e)


# ------------------------------------------------------------------ work (claims units, as Stage 10 steal mode)
def running_jobs():
    try: r = subprocess.run(['squeue', '-u', os.environ['USER'], '-h', '-t', 'RUNNING', '-o', '%i'], capture_output=True, text=True, timeout=90)
    except Exception: return None
    return set(r.stdout.split()) if r.returncode == 0 else None


def claim(d, me):
    try: d.mkdir(parents=True); (d / 'owner').write_text(me); return True
    except FileExistsError: pass
    try: owner = (d / 'owner').read_text().strip()
    except FileNotFoundError: return False
    if owner == me: return True
    run = running_jobs()
    if run is None or owner in run: return False
    moved = d.with_name(f'{d.name}.stale_{owner}_{me}')
    try: os.rename(d, moved)
    except OSError: return False
    if (moved / 'owner').read_text().strip() != owner: os.rename(moved, d); return False
    return claim(d, me)


def work(a, budget=None, t_start=None):
    budget = budget if budget is not None else a.max_minutes; t_start = t_start or time.monotonic()
    me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    verify(); CL = ROOT / 'logs/claims'; CL.mkdir(parents=True, exist_ok=True)
    C, last, U = None, 0.0, units()
    sm = ROOT / 'reports/smoke.json'
    if not sm.exists():                       # gate: the first job to get here runs the GPU smoke test, the others wait for it
        C = Ctx()
        for _ in range(90):                    # the smoke lock is a claim: a dead owner's lock is taken over
            if sm.exists(): break
            if claim(ROOT / 'logs/smoke.lock', me): log('running smoke test'); smoke_run(C); break
            log('waiting for the smoke test of another job'); time.sleep(20)
    if not sm.exists() or load(sm)['status'] != 'PASS':
        stop_queue(f'smoke test not PASS ({sm})'); raise RuntimeError(f'smoke test not PASS: {sm}')
    log(f'stage11 work: job {me}, budget {budget} min, {len(U)} units')
    while True:
        u = None
        for v in U:
            if out_path(v).exists(): continue
            if claim(CL / '_'.join(str(x) for x in v if x is not None), me): u = v; break
        if u is None: log('stage11: nothing left to claim'); return
        if budget and C is not None and (time.monotonic() - t_start) / 60 + 1.5 * last / 60 > budget:
            d = CL / '_'.join(str(x) for x in u if x is not None); os.rename(d, d.with_name(d.name + f'.released_{me}'))
            log('time budget reached; released', u); return
        if C is None: C = Ctx()
        t0 = time.monotonic(); d = compute(C, u); save(u, d, C.env); last = time.monotonic() - t0
        log(f'stage11 {u[0]} {u[1] or ""} shard {u[2]:03d} rows={len(d["row_id"])} {last:.0f}s total={(time.monotonic() - t_start) / 60:.1f}min')


# ------------------------------------------------------------------ preflight (CPU)
def preflight(a):
    import pandas as pd
    res = []
    def check(n, ok, det=''): res.append(ok); print(('PASS' if ok else 'FAIL'), n, det, flush=True)
    pr = verify(); check('protocol + Stage 10 inputs unchanged', True)
    papers, toks = cohort(); ctx = contexts_of(toks); smp = pd.read_parquet(ROOT / 'config/sample.parquet')
    check('sample size', len(smp) == pr['sample']['n'], f"{pr['sample']['n_target']} target / {pr['sample']['n_control']} control, {smp.shard.nunique()} shards")
    check('sample balanced per bin', bool((smp.groupby(['citation_bin', 'group']).size().unstack().diff(axis=1).iloc[:, -1] == 0).all()))
    tok = s10.tokenizer(); P = papers.set_index('paper_id'); pf = s10.condition_prompts(R10, papers, FALSE_FOR_PATCH)[0]
    bad = 0
    for r in smp.itertuples():
        pt = json.loads(P.loc[r.paper_id].prompt_ids); tp = json.loads(r.title_pos); fids = pf[r.paper_id][1]
        txt = tok.decode([pt[i] for i in tp]); title = P.loc[r.paper_id].title
        tail_ok = pt[-r.tail_prompt:] == fids[-r.tail_prompt:] and len(pt) - r.tail_prompt > max(tp)
        if title.strip()[:8] not in txt or not tail_ok: bad += 1
    check('title positions decode to the title; tail lengths reproduce', bad == 0, f'{bad} bad')
    class Fake: comma = [11]
    lens = []
    for c in CONDS:
        pr_c = s10.condition_prompts(R10, papers, c)[0]
        for pid in papers.paper_id.iloc[::97]:
            if pid not in ctx: continue
            ids, pos, rows, gold, aidx = chain_ids(Fake, pr_c[pid][1], ctx[pid])
            full = ids + [gold[-1]]
            assert all(full[p + 1] == g for p, g in zip(pos, gold)); lens.append(len(ids))
    check('chain ids: every scored position predicts its gold token', True, f'max length {max(lens)}')
    check('chain max length <= 1024', max(lens) <= 1024)
    tot = sum(len(v) for v in ctx.values()); check('all Stage 10 authors present for chain', tot == 33811, f'{tot} author contexts')
    check('lens public has chain layers', all(l in s10.verify(R10)[1]['public']['source_layers'] for l in CHAIN_LAYERS))
    print(f'PREFLIGHT {"PASS" if all(res) else "FAIL"}: {sum(res)}/{len(res)}'); sys.exit(0 if all(res) else 1)


# ------------------------------------------------------------------ analyze (CPU)
def analyze(a):
    import stage11_analyze; stage11_analyze.main(ROOT, R10, s10)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['freeze', 'preflight', 'smoke', 'work', 'remaining', 'analyze'])
    p.add_argument('--max-minutes', type=float, default=None)
    a = p.parse_args()
    sys.path.insert(0, str(DIR))
    {'freeze': freeze, 'preflight': preflight, 'smoke': smoke, 'work': work, 'remaining': remaining, 'analyze': analyze}[a.command](a)


if __name__ == '__main__':
    main()
