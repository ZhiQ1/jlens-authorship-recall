"""Batch 3 items 3-1 / 3-2 (addendum 14): Stage 10 readouts at new layers for target + control (6,841 papers), GPU wrapper.

Stage 10 fast path, unchanged: model from 351_stage10_fix1.load_model (hf_device_map fix + prefetch), readouts from the frozen
351_stage10.py functions (open_lenses, fast_readout, score, condition_prompts, verify, readout_plan); neither file is edited.
One forward per author context (prompt + name[:-1]), every name token scored at the position before it, rank = 1 + number of
vocabulary logits strictly greater (bf16 logits), conditions true, false_0..4, delete; readouts logit + jlens_public.
  --item 3-1 : L41-L47, L49 + L24, L48 (hard-check layers, recomputed in the same forward)
  --item 3-2 : L0-L23     + L24, L48
Unit = (condition, Stage 10 shard of 128 papers), restricted to target + control contexts; one npz per unit with all pairs:
  raw/b3_s10_<item>/<cond>/shard_XXX.npz  (keys: stage13_b3_cols.RAW_S10). At L24/L48 the stored Stage 10 rank of every
  token is compared in the job (chk_*), and for every rank mismatch the bf16 distance to the stored rank is computed from the
  new logits (stage13_b3_checks.ulps_to_rank_torch).
Commands
  run   [--shards 0 | --all] [--max-minutes M] [--tiny]   compute missing units (claims + skip-if-exists + atomic save)
        --shards = gate mode: afterwards runs gate-check on those shards; exit 3 if the hard check fails.
  gate-check --shards 0        CPU: hard check on saved units of those shards -> summary_b3_s10_<item>/gate.json
  remaining                    print number of missing units
  chain --sbatch FILE          after an --all job: resubmit itself (round+1, <= MAX_ROUNDS) or submit the analysis (once)
  tiny-root                    CPU: build the tiny Stage-10 root (copied cohort/config + random tiny lens) for the tiny test
  tiny-ref --shards 0          CPU: the FROZEN 351_stage10.run on the tiny model writes the tiny 'stored Stage 10' L24/L48
                               reference into the tiny root (so the tiny hard check compares the wrapper with the frozen path)
"""
import argparse, importlib.util, json, os, subprocess, sys, time, shutil
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b3_cols.py', 'b3_cols'); CK = load(H / '13_stage13/stage13_b3_checks.py', 'b3_checks')
fix1 = load(H / '10_stage10/351_stage10_fix1.py', 's10fix1'); s10 = fix1.s10
ME = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
TINY_S10 = K.R13 / 'b3_tiny/s10root'                 # tiny copy of the Stage 10 root (cohort + config + tiny lens)
ULPS_CAP = 4000                                        # per unit: more rank mismatches than this -> ulps NaN (gross error)


def log(*x):
    try: print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
    except Exception: pass


def wjson(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); tmp = p.with_name(p.name + f'.tmp{os.getpid()}')
    tmp.write_text(json.dumps(obj, indent=1, default=str) + '\n'); os.replace(tmp, p)


def s10root(tiny): return TINY_S10 if tiny else K.R10


def unit_path(R, cond, k): return R['raw'] / cond / f'shard_{k:03d}.npz'


def ref_rank_file(tiny, cond, r, l, k): return s10.out_file(s10root(tiny), r, l, k, cond)


# ---------------------------------------------------------------- tiny model / tiny root
def tiny_model():
    """random 64-layer Qwen3 (as stage13_b2_np_gpu.tiny_model: same config, seed, dtype); real tokenizer."""
    import torch, transformers, jlens
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
    tok = s10.tokenizer(); return jlens.from_hf(hf, tok), tok


def tiny_root(a):
    """copy the frozen Stage 10 cohort + config (verify() passes on the copy) and register a random 64x64 'public' lens."""
    import torch, jlens
    T = TINY_S10
    if (T / 'config/lenses.json').exists(): log('tiny root exists', T); s10.verify(T); return
    for rel in ['config/manifest.json', 'config/protocol.json', 'config/conditions_manifest.json', 'cohort/papers.parquet',
                'cohort/contexts.parquet', 'cohort/name_tokens.parquet', 'cohort/excluded_authors.csv',
                'cohort/conditions/false_titles.parquet', 'cohort/conditions/prompts.parquet']:
        (T / rel).parent.mkdir(parents=True, exist_ok=True); shutil.copy2(K.R10 / rel, T / rel)
    g = torch.Generator().manual_seed(14)
    lens = jlens.JacobianLens({l: torch.eye(64) + 0.3 * torch.randn(64, 64, generator=g) for l in range(63)}, n_prompts=1, d_model=64)
    lp = T / 'tiny_public_lens.pt'; lens.save(str(lp))
    s10.dump(T / 'config/lenses.json', {'public': dict(path=str(lp), sha256=s10.sha_file(lp), source_layers=list(range(63)), n_prompts=1, registered=s10.now())})
    (T / 'reports').mkdir(exist_ok=True)
    s10.verify(T); log('tiny root built', T)


def tiny_ref(a):
    s10.load_model = tiny_model                                              # frozen run(), only the model is the tiny one
    ns = argparse.Namespace(root=str(TINY_S10), readouts=','.join(K.READOUTS), layers=','.join(map(str, K.CHECK_LAYERS)), shards=a.shards,
                            condition=','.join(K.CONDS), max_minutes=None, skip_parity_gate=True)
    s10.run(ns); log('tiny reference written by the frozen 351_stage10.run', TINY_S10 / 'raw')


# ---------------------------------------------------------------- claims
def claim(R, cond, k):
    R['claims'].mkdir(parents=True, exist_ok=True); d = R['claims'] / f'{cond}_{k:03d}'
    try: d.mkdir(); (d / 'owner').write_text(f'{ME} {time.strftime("%Y-%m-%dT%H:%M:%S")}\n'); return True
    except FileExistsError:
        try: o = (d / 'owner').read_text().split()[0]
        except Exception: o = ''
        if o == ME: return True
        if o.isdigit():                                                        # reclaim if the owner job is gone
            try: st = subprocess.run(['squeue', '-h', '-j', o, '-o', '%T'], capture_output=True, text=True, timeout=60).stdout.strip()
            except Exception: st = 'UNKNOWN'
            if st == '':
                (d / 'owner').write_text(f'{ME} {time.strftime("%Y-%m-%dT%H:%M:%S")} (reclaimed from {o})\n'); return True
        return False


# ---------------------------------------------------------------- data
def setup(item, tiny):
    root = s10root(tiny); m, lenses = s10.verify(root)
    layers = K.item_layers(item); plan = s10.readout_plan(lenses, K.READOUTS, layers)
    if plan != K.item_pairs(item): raise RuntimeError('plan order differs from stage13_b3_cols.item_pairs')
    papers = pd.read_parquet(root / 'cohort/papers.parquet')
    tc = set(papers.paper_id[papers.group_tight.isin(K.GROUPS)])
    if not tiny and len(tc) != K.N_PAPERS_TC: raise RuntimeError(f'target+control papers {len(tc)} != {K.N_PAPERS_TC}')
    ctx = pd.read_parquet(root / 'cohort/contexts.parquet'); ctx = ctx[ctx.paper_id.isin(tc)]
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'context_id', 'paper_id', 'token_index', 'token_id'])
    toks = toks[toks.paper_id.isin(tc)]
    return root, m, lenses, plan, papers, ctx, toks


def units_for(m, shards): return [(c, k) for c in K.CONDS for k in shards]


def parse_shards(a, m):
    return list(range(m['n_shards'])) if a.all else s10.parse_shards(a.shards, m['n_shards'])


# ---------------------------------------------------------------- run
def run(a):
    import torch
    R = K.s10_roots(a.item, a.tiny); root, m, lenses, plan, papers, ctx, toks = setup(a.item, a.tiny)
    if a.all and not a.tiny:
        g = json.loads(R['gate'].read_text()) if R['gate'].exists() else None
        if g is None or g.get('status') != 'PASS': log('REFUSE --all: gate.json missing or not PASS', R['gate']); sys.exit(3)
    if R['fail'].exists(): log('REFUSE: HARD_CHECK_FAILED marker exists', R['fail']); sys.exit(3)
    shards = parse_shards(a, m)
    todo = [(c, k) for c, k in units_for(m, shards) if not unit_path(R, c, k).exists()]
    log(f'b3_s10 {a.item} job {ME}: {len(todo)} of {len(shards) * len(K.CONDS)} units to do; pairs {len(plan)}; budget {a.max_minutes} min', 'TINY' if a.tiny else '')
    t_start = time.monotonic()
    if todo:
        model, tok = tiny_model() if a.tiny else fix1.load_model()
        L = s10.open_lenses(lenses, plan, model)
        env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else ['cpu'],
                   s10_script_sha256=s10.sha_file(s10.__file__), fix1_sha256=s10.sha_file(fix1.__file__), wrapper_sha256=s10.sha_file(__file__),
                   plan_sha256=K.PLAN_SHA, protocol_sha256=m['protocol_sha256'], lens_sha256=lenses['public']['sha256'], job=ME, tiny=a.tiny, item=a.item)
        log('model + lenses ready', f'{(time.monotonic() - t_start) / 60:.1f} min', env['gpu'])
        prompts_by = {}; last = 0.0
        for cond, k in todo:
            el = (time.monotonic() - t_start) / 60
            if a.max_minutes and el + 1.5 * max(last, 20 if a.tiny else 40) / 60 > a.max_minutes:
                log('time budget reached; remaining units left for the next job'); break
            if unit_path(R, cond, k).exists(): continue
            if not claim(R, cond, k): log('claimed by another job, skip', cond, k); continue
            if cond not in prompts_by: prompts_by[cond] = s10.condition_prompts(root, papers, cond)
            t0 = time.monotonic()
            d = compute_unit(model, L, plan, ctx, toks, cond, k, prompts_by[cond], a.tiny, torch)
            meta = dict(env, cond=cond, shard=k, pairs=[K.pair_name(r, l) for r, l in plan], check_pairs=[K.pair_name(r, l) for r, l in K.check_pairs()],
                        condition_prompts_sha256=prompts_by[cond][1], n_rows=int(len(d['row_id'])), created=s10.now(), seconds=time.monotonic() - t0)
            f = unit_path(R, cond, k); f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
            np.savez(tmp, meta=np.array(json.dumps(meta, sort_keys=True)), **d); os.replace(tmp, f)
            last = time.monotonic() - t0
            try:
                ex = (d['chk_ref_rank'] == d['rank'][[plan.index(p) for p in K.check_pairs()]]).mean()
                log(f'[{cond}] shard {k:03d} tokens={len(d["row_id"])} {last:.0f}s total={(time.monotonic() - t_start) / 60:.1f}min '
                    f'L24/L48 exact={ex:.4f} max_ulps={np.nanmax(d["chk_ulps"]) if d["chk_ulps"].size else 0:.2f}')
            except Exception as e: log('WARNING log line failed:', e)
    if not a.all:                                                              # gate mode
        res = gate_check(a.item, shards, a.tiny)
        if res['status'] != 'PASS': log('GATE HARD CHECK FAILED -> exit 3'); sys.exit(3)


def compute_unit(model, L, plan, ctx, toks, cond, k, prompts, tiny, torch):
    prompts, _ = prompts
    cs = ctx[ctx.shard == k].sort_values('context_id')
    tk = toks[toks.context_id.isin(set(cs.context_id))].sort_values('row_id')
    rows = tk.row_id.to_numpy(); n = len(rows); pos_of = pd.Series(np.arange(n), index=rows)
    P = len(plan); cp = K.check_pairs(); ci = [plan.index(p) for p in cp]
    out = dict(row_id=rows, rank=np.zeros((P, n), np.int32), ties=np.zeros((P, n), np.int32), logprob=np.zeros((P, n), np.float32),
               top1=np.zeros((P, n), np.int32), chk_ref_rank=np.zeros((len(cp), n), np.int32), chk_ulps=np.zeros((len(cp), n), np.float32),
               chk_dlogprob=np.zeros((len(cp), n), np.float32))
    ref = {}
    for j, (r, l) in enumerate(cp):                                            # stored Stage 10 ranks (all rows of the shard)
        z = np.load(ref_rank_file(tiny, cond, r, l, k)); s = pd.Series(np.arange(len(z['row_id'])), index=z['row_id'])
        ix = s.reindex(rows).to_numpy()
        if np.isnan(ix.astype(float)).any(): raise RuntimeError(f'stored Stage 10 rows missing {cond} {r} L{l} shard {k}')
        ix = ix.astype(int); ref[(r, l)] = (z['rank'][ix], z['logprob'][ix]); out['chk_ref_rank'][j] = z['rank'][ix]
    tok_by_ctx = {c: g for c, g in tk.groupby('context_id', sort=False)}
    enc_checked = set(); n_mis = 0
    for _, c in cs.iterrows():
        prompt, pids = prompts[c.paper_id]
        if c.paper_id not in enc_checked:
            if model.encode(prompt, max_length=s10.MAX_CONTEXT).reshape(-1).tolist() != pids: raise RuntimeError(f'prompt encoding differs: {c.paper_id}')
            enc_checked.add(c.paper_id)
        t = tok_by_ctx[c.context_id].sort_values('token_index')
        name = t.token_id.tolist(); idx = pos_of[t.row_id.to_numpy()].to_numpy()
        ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]
        res = s10.fast_readout(model, L, ids, pos, plan, torch)
        gold = torch.tensor(name, device=model.input_device)
        for pi, rl in enumerate(plan):
            logits = res[rl]
            rk, ti, lp, t1 = s10.score(logits, gold, torch)
            out['rank'][pi, idx] = rk; out['ties'][pi, idx] = ti; out['logprob'][pi, idx] = lp; out['top1'][pi, idx] = t1
            if rl in ref:
                j = cp.index(rl); rr, rl_lp = ref[rl]; rr = rr[idx]
                out['chk_dlogprob'][j, idx] = lp - rl_lp[idx]
                mis = np.nonzero(rk != rr)[0]
                if len(mis):
                    n_mis += len(mis)
                    if n_mis > ULPS_CAP: out['chk_ulps'][j, idx[mis]] = np.nan; continue
                    mt = torch.tensor(mis, device=logits.device)
                    out['chk_ulps'][j, idx[mis]] = CK.ulps_to_rank_torch(logits[mt], gold.to(logits.device)[mt], torch.tensor(rr[mis]), torch)
    for key in ('rank',):
        if n and (out[key] < 1).any(): raise RuntimeError(f'unfilled rows {cond} shard {k}')
    return out


# ---------------------------------------------------------------- checks
def load_units(R, units, need_all=True):
    out = {}
    for c, k in units:
        f = unit_path(R, c, k)
        if not f.exists():
            if need_all: raise FileNotFoundError(f)
            continue
        z = np.load(f); out[(c, k)] = {x: z[x] for x in z.files}; out[(c, k)]['meta'] = json.loads(str(z['meta']))
    return out


def rank_rows(item, U, scope):
    rows = []; allp = []
    for (r, l) in K.check_pairs():
        per = []
        for c in K.CONDS:
            us = [u for (cc, _), u in U.items() if cc == c]
            if not us: continue
            j = [K.pair_name(*p) for p in K.check_pairs()].index(K.pair_name(r, l)); pi = us[0]['meta']['pairs'].index(K.pair_name(r, l))
            new = np.concatenate([u['rank'][pi] for u in us]); ref = np.concatenate([u['chk_ref_rank'][j] for u in us])
            ul = np.concatenate([u['chk_ulps'][j] for u in us]); dl = np.concatenate([u['chk_dlogprob'][j] for u in us])
            per.append((new, ref, ul, dl))
            x = CK.rank_match(new, ref, ul, dl, K.ULPS_MAX, K.RANK_EXACT_MIN)
            rows.append(dict(item=item, scope=scope, readout=r, layer=l, cond=c, **{k_: x[k_] for k_ in K.RANK_MATCH if k_ in x}))
        if per:
            cat = [np.concatenate([p[i] for p in per]) for i in range(4)]; allp.append(cat)
            x = CK.rank_match(*cat, K.ULPS_MAX, K.RANK_EXACT_MIN)
            rows.append(dict(item=item, scope=scope, readout=r, layer=l, cond='ALL', **{k_: x[k_] for k_ in K.RANK_MATCH if k_ in x}))
    cat = [np.concatenate([p[i] for p in allp]) for i in range(4)]
    pooled = CK.rank_match(*cat, K.ULPS_MAX, K.RANK_EXACT_MIN)
    return pd.DataFrame(rows)[K.RANK_MATCH], pooled


def paper_spec_new(U, toks, pids, readout, layer):
    """per-paper spec_mean_nlr (token mean, true - mean false_k) from new units, for papers pids."""
    pidx = {p: i for i, p in enumerate(pids)}; lev = {}
    for c in ['true'] + K.FALSE:
        us = [u for (cc, _), u in U.items() if cc == c]
        pi = us[0]['meta']['pairs'].index(K.pair_name(readout, layer))
        rid = np.concatenate([u['row_id'] for u in us]); rk = np.concatenate([u['rank'][pi] for u in us])
        pp = toks.set_index('row_id').paper_id.reindex(rid).to_numpy()
        keep = np.array([p in pidx for p in pp]); codes = np.array([pidx[p] for p in pp[keep]])
        lev[c] = CK.paper_means(codes, len(pids), CK.nlr(rk[keep]))
    return CK.spec_total_topic(lev)['spec']


def paper_spec_ref_tiny(toks, pids, readout, layer, shards):
    """tiny mode: the 'published' per-paper value computed from the tiny frozen-path reference raw with the same function."""
    pidx = {p: i for i, p in enumerate(pids)}; lev = {}
    for c in ['true'] + K.FALSE:
        rid, rk = [], []
        for k in shards:
            z = np.load(ref_rank_file(True, c, readout, layer, k)); rid.append(z['row_id']); rk.append(z['rank'])
        rid = np.concatenate(rid); rk = np.concatenate(rk)
        pp = toks.set_index('row_id').paper_id.reindex(rid).to_numpy()
        keep = np.array([p in pidx for p in pp]); codes = np.array([pidx[p] for p in pp[keep]])
        lev[c] = CK.paper_means(codes, len(pids), CK.nlr(rk[keep]))
    return CK.spec_total_topic(lev)['spec']


def gate_check(item, shards, tiny):
    R = K.s10_roots(item, tiny); root = s10root(tiny)
    papers = pd.read_parquet(root / 'cohort/papers.parquet', columns=['paper_id', 'shard', 'group_tight'])
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    U = load_units(R, units_for(None, shards))
    rows, pooled = rank_rows(item, U, f'gate shards {shards}')
    checks = [dict(item=item, check='rank_exact_L24_L48', scope='gate pooled', value=pooled['share_exact'], threshold=K.RANK_EXACT_MIN,
                   status='PASS' if pooled['share_exact'] >= K.RANK_EXACT_MIN else 'FAIL', kind='HARD', note=f"{pooled['n_exact']}/{pooled['n_tokens']} exact"),
              dict(item=item, check='mismatch_within_4_bf16', scope='gate pooled', value=pooled['max_ulps'], threshold=K.ULPS_MAX,
                   status='PASS' if pooled['n_mismatch_le_ulps'] == pooled['n_mismatch'] else 'FAIL', kind='HARD',
                   note=f"{pooled['n_mismatch_le_ulps']}/{pooled['n_mismatch']} mismatches within {K.ULPS_MAX} units")]
    sub = papers[papers.shard.isin(shards) & papers.group_tight.isin(K.GROUPS)]
    pids = sub.paper_id.to_numpy(); grp = sub.group_tight.to_numpy()
    pt = None if tiny else pd.read_parquet(K.R10 / 'summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'readout', 'layer', 'spec_mean_nlr'])
    for r in K.READOUTS:
        new = paper_spec_new(U, toks, pids, r, 48)
        if tiny: ref = paper_spec_ref_tiny(toks, pids, r, 48, shards)
        else: ref = pt[(pt.readout == r) & (pt.layer == 48)].set_index('paper_id').spec_mean_nlr.reindex(pids).to_numpy()
        for g in K.GROUPS:
            mk = grp == g
            if mk.sum(): checks.append(dict(item=item, **CK.scalar_check(f'paper_spec_L48_{r}_{g}_mean', float(np.nanmean(new[mk])), float(np.nanmean(ref[mk])), K.PAPER_SPEC_TOL, 'HARD', 'gate papers')))
        d = np.abs(new - ref); sh = float(np.mean(d <= K.PAPER_SPEC_TOL))
        checks.append(dict(item=item, check=f'paper_spec_L48_{r}_share_within', scope='gate papers', value=sh, threshold=K.PAPER_SHARE_WARN,
                           status='PASS' if sh >= K.PAPER_SHARE_WARN else 'WARN', kind='WARN', note=f'max per-paper |diff| {np.nanmax(d):.5f}'))
    status = 'FAIL' if any(c['status'] == 'FAIL' for c in checks) else 'PASS'
    res = dict(item=item, status=status, shards=shards, tiny=tiny, created=s10.now(), checks=checks, rank_rows=rows.to_dict('records'),
               unit_seconds={f'{c}_{k}': u['meta']['seconds'] for (c, k), u in U.items()},
               gpu=sorted({str(u['meta']['gpu']) for u in U.values()}))
    wjson(R['gate'], res)
    try:
        for c in checks: log('GATE', c['status'], c['check'], f"value={c['value']:.6g} thr={c['threshold']}", c.get('note', ''))
        log('GATE STATUS', status, '->', R['gate'])
    except Exception as e: log('WARNING gate log failed:', e)
    return res


# ---------------------------------------------------------------- remaining / chain
def remaining(a, quiet=False):
    R = K.s10_roots(a.item, a.tiny); m, _ = s10.verify(s10root(a.tiny))
    n = sum(not unit_path(R, c, k).exists() for c, k in units_for(m, range(m['n_shards'])))
    if not quiet: print(n)
    return n


def chain(a):
    """after an --all job (only when it exited 0): resubmit (round + 1) while units remain; else submit the analysis once."""
    R = K.s10_roots(a.item, a.tiny); R['chain'].mkdir(parents=True, exist_ok=True)
    n = remaining(a, quiet=True); rnd = int(os.environ.get('ROUND', '1')); mx = int(os.environ.get('MAX_ROUNDS', '16'))
    def submit(marker, cmd):
        if a.dry: log('dry run: would create marker', marker, 'and run', ' '.join(cmd)); return
        try: fd = os.open(R['chain'] / marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, f'{ME} {time.ctime()}\n'.encode()); os.close(fd)
        except FileExistsError: log('chain marker exists (another job already submitted):', marker); return
        log('SUBMIT', ' '.join(cmd))
        if a.dry: log('dry run: not submitted'); return
        for i in range(3):
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=120); log('sbatch:', p.stdout.strip(), p.stderr.strip())
                if p.returncode == 0: return
            except Exception as e: log('sbatch error', e)
            q = subprocess.run(['squeue', '-u', os.environ.get('USER', 'zhang.zhiqi2'), '-h', '-o', '%j'], capture_output=True, text=True).stdout
            log('after sbatch error, squeue job names:', ' '.join(sorted(set(q.split())))); time.sleep(30)
    if n > 0:
        if rnd >= mx: log(f'{n} units remain but MAX_ROUNDS={mx} reached: stop (resubmit by hand)'); return
        submit(f'round_{rnd + 1}', ['sbatch', f'--export=ALL,ITEM={a.item},MODE=all,AUTO=1,ROUND={rnd + 1},MAX_ROUNDS={mx}', a.sbatch])
    else:
        submit('analyze', ['sbatch', f'--export=ALL,ITEM={a.item}', a.analyze_sbatch])


def main():
    K.check_plan()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=['run', 'gate-check', 'remaining', 'chain', 'tiny-root', 'tiny-ref'])
    ap.add_argument('--item', choices=['3-1', '3-2'], default='3-1'); ap.add_argument('--shards', default='0'); ap.add_argument('--all', action='store_true')
    ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--tiny', action='store_true')
    ap.add_argument('--sbatch', default=str(H / '13_stage13/stage13_b3_s10_gpu.sbatch'))
    ap.add_argument('--analyze-sbatch', default=str(H / '13_stage13/stage13_b3_s10_analyze.sbatch')); ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    if a.command == 'tiny-root': return tiny_root(a)
    if a.command == 'tiny-ref': return tiny_ref(a)
    if a.command == 'gate-check':
        m, _ = s10.verify(s10root(a.tiny)); r = gate_check(a.item, s10.parse_shards(a.shards, m['n_shards']), a.tiny)
        sys.exit(0 if r['status'] == 'PASS' else 3)
    {'run': run, 'remaining': remaining, 'chain': chain}[a.command](a)


if __name__ == '__main__':
    main()
