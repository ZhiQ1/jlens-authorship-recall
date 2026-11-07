"""Batch 2 group B GPU units (addendum 12 items 2-4, 2-8, 2-3, 2-10). New file; frozen code loaded by path, never edited.

Plan (frozen): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum12.json (sha256 checked; mismatch = WARN).
Frozen code used unchanged: 11_stage11/361_stage11.py (record, run_final, ranks, do_patch_title) through the addendum-8
driver 14_groups/rerun_gpu.py (one shared s11 instance); 13_stage13/381_stage13.py (build, run_final) and
13_stage13/stage13_x3_tok_gpu.py (tok_ranks = 381_stage13.score_tf keeping per-token ranks; paraphrases()).

Unit types (one npz per unit; skip-if-exists; claims in 381_stage13/logs/claims_b2B; atomic save):
  e1noise  2-4  Stage 11 E1 on two original shards (rule: the lowest-index shard with the highest target share = 6 and the
               lowest-index shard with the highest control share = 0), per name token:
               ORIGINAL arms (= 361_stage11.do_patch, unchanged order of calls): true and false_0 at batch 1, patched at all
               15 PATCH_LAYERS in one batch of 15 (rank_patch_b15);
               NEW arms: patched at L40 / L48 / L52 each alone at batch 1 (rank_patch_b1); unpatched true and false_0 as
               15 identical copies in one batch (rank_true_b15 / rank_false_b15 = element 0; whether all 15 copies agree is
               stored). Deviation stated: the original unpatched runs were batch 1, so their "original batch size" arm is
               the batch-1 run itself; the batch-of-15 copy measures the rounding of a 15-batch for the unpatched runs.
  e1t5     2-8  E1t (361_stage11.do_patch_title, unchanged) with donor false_k (k = 1..4) on the 24 Stage 11 shards:
               s11.FALSE_FOR_PATCH = false_k and C.prompts[false_k] (title position of false_k by the frozen rule), as X6 /
               batch 1 item 3 did for E1 / P1 / P2. Unit ('e1t5', 'false_0_check', 0) re-runs false_0 shard 0 (gate check).
  x3tok    2-3  X3 behaviour scoring per name token for ALL authors: rows (paper, author, partner B, lexical neighbour D)
               = the batch-1 all-author rows raw/b1_xall/para/shard_k.npz (stage13_b1_xall.do_para); prompt
               381_stage13.build(tok, title, 'authors', []) for original / paraphrase / partner / D title; batch-1
               teacher-forced ranks of every name token (stage13_x3_tok_gpu.tok_ranks). Self-check (WARN): per-author mean
               log10(1/rank) == stored b1_xall score.
  m3tok    2-10 M3 authors task ('Who are the authors of the paper titled "{t}"?\\nAuthors:', 381_stage13.build) on the 72
               Stage 10 shards, every name token of every author teacher-forced (one batch-1 forward per author context, as
               score_tf). Plus, per paper, the EXACT published path (do_task: prompt-only batch-1 forward, last-block state at ':' -> unembed)
               for the first author's first token (exact_paper_id / exact_first_rank). Gate guard uses the exact arm; the
               in-sequence first token vs stored raw/task author_first_nlr is a WARN-only number.
Gate (--gate): e1noise:0, e1t5 false_0_check:0, e1t5 false_1:0, x3tok:0, m3tok:0, then gate checks written to
summary_b2B/gate.json: HARD (exit 3, chain stops): e1noise original arms == stored raw/patch shard 0 (rows identical, E1
recovery per layer |diff| <= 0.005); e1t5 false_0 re-run == stored raw/patch_title shard 0 (rows identical, E1t recovery per
layer |diff| <= 0.005, false baseline = the batch's L63 element as stage11_analyze). Gross-mismatch guard (exit 3) for x3tok /
m3tok shard 0: mean |d| > 0.1 vs the stored per-author scores (only a wrong row / prompt can do that); 0.005 < mean |d| <= 0.1
is a WARN, not a stop.
Commands: work (--gate | --all) [--types e1noise,e1t5,x3tok,m3tok] [--max-minutes M] | gatecheck | remaining | tiny --root DIR
"""
import argparse, hashlib, importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
R13 = BASE / '381_stage13'
PLAN = R13 / 'config/prereg_addendum12.json'
TITLES = ['false_0', 'false_1', 'false_2', 'false_3', 'false_4']; TYPES = ['e1noise', 'e1t5', 'x3tok', 'm3tok']
TOL = 0.005; GROSS = 0.1
R = dict(root=R13)                         # test root for tiny (raw / logs / summary are under R['root'])


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load(H / '13_stage13/b2_groupB_cols.py', 'b2cols')
rg = load(H / '14_groups/rerun_gpu.py', 'rerun_gpu_b2B'); s11, s10 = rg.s11, rg.s10
x3t = load(H / '13_stage13/stage13_x3_tok_gpu.py', 'x3tok_b2B'); s13 = x3t.s13


def plan_ok():
    try: ok = sha(PLAN) == Path(str(PLAN) + '.sha256').read_text().split()[0]
    except Exception: ok = False
    if not ok: log('WARN addendum 12 sha256 differs from its .sha256 file')
    return ok


def noise_shards(smp):
    t = smp.groupby('shard').group.apply(lambda g: (g == 'target').mean())
    return sorted({int(t[t == t.max()].index.min()), int(t[t == t.min()].index.min())})


# ------------------------------------------------------------------ context
class B2Ctx:
    def __init__(self, model=None, tok=None, env=None):
        import torch, pandas as pd
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in ['true'] + TITLES}
        if model is None: self.model, self.tok = s10.load_model()
        else: self.model, self.tok = model, tok
        self.smp0 = pd.read_parquet(R11 / 'config/sample.parquet'); self.smp = self.smp0
        self.env = env if env is not None else dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                                                    driver_sha256=sha(__file__), plan_sha256=sha(PLAN),
                                                    frozen_sha256={k: sha(v) for k, v in rg.FROZEN.items()} | {'381_stage13.py': sha(H / '13_stage13/381_stage13.py')})
        self._para = None

    def record(self, ids, layers): return s11.record(self, ids, layers)
    def unembed(self, h): return self.model.unembed(h)

    @property
    def para(self):
        if self._para is None: self._para = x3t.paraphrases() if R['root'] == R13 or (R13 / 'raw/para_gen').exists() else {}
        return self._para


# ------------------------------------------------------------------ 2-4 e1noise
def do_e1noise(C, shard, smp=None):
    """361_stage11.do_patch (unchanged call order for the original arms) + batch-1 patched L40/48/52 + unpatched batch 15."""
    torch = C.torch; PL = s11.PATCH_LAYERS; NL = COLS.NOISE_LAYERS; pf = C.prompts[s11.FALSE_FOR_PATCH]; smp = C.smp0 if smp is None else smp
    out = {k: [] for k in ('row_id', 'paper_id', 'rank_true_b1', 'rank_false_b1', 'rank_true_b15', 'rank_false_b15', 'rank_patch_b15', 'rank_patch_b1', 'idt', 'idf')}
    for r in smp[smp.shard == shard].itertuples():
        pt = json.loads(C.P.loc[r.paper_id].prompt_ids); pfi = pf[r.paper_id][1]
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; tail = r.tail_prompt + len(name) - 1
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = s11.record(C, T, PL)
            lt = s11.run_final(C, T, posT)[0]; lf = s11.run_final(C, F, posF)[0]
            patch = {}
            for i, l in enumerate(PL): patch.setdefault(l, []).append((i, tail, acts[l][-tail:]))
            lp = s11.run_final(C, F, posF, patch=patch, batch=len(PL))
            # new arms
            p1 = [s11.ranks(s11.run_final(C, F, posF, patch={l: [(0, tail, acts[l][-tail:])]}, batch=1)[0], gold, torch) for l in NL]
            ltb = s11.run_final(C, T, posT, batch=len(PL)); lfb = s11.run_final(C, F, posF, batch=len(PL))
            rtb = [s11.ranks(ltb[i], gold, torch) for i in range(len(PL))]; rfb = [s11.ranks(lfb[i], gold, torch) for i in range(len(PL))]
            out['row_id'] += list(rids); out['paper_id'] += [r.paper_id] * len(name)
            out['rank_true_b1'].append(s11.ranks(lt, gold, torch)); out['rank_false_b1'].append(s11.ranks(lf, gold, torch))
            out['rank_patch_b15'].append(np.stack([s11.ranks(lp[i], gold, torch) for i in range(len(PL))], 1)); out['rank_patch_b1'].append(np.stack(p1, 1))
            out['rank_true_b15'].append(rtb[0]); out['rank_false_b15'].append(rfb[0])
            out['idt'].append(np.full(len(name), all(np.array_equal(x, rtb[0]) for x in rtb))); out['idf'].append(np.full(len(name), all(np.array_equal(x, rfb[0]) for x in rfb)))
    cat = lambda k: np.concatenate(out[k])
    return dict(row_id=np.array(out['row_id']), paper_id=np.array(out['paper_id']), rank_true_b1=cat('rank_true_b1'), rank_false_b1=cat('rank_false_b1'),
                rank_true_b15=cat('rank_true_b15'), rank_false_b15=cat('rank_false_b15'), rank_patch_b15=cat('rank_patch_b15'), rank_patch_b1=cat('rank_patch_b1'),
                layers_b15=np.array(PL), layers_b1=np.array(NL), b15_elements_identical_true=cat('idt'), b15_elements_identical_false=cat('idf'))


# ------------------------------------------------------------------ 2-8 e1t5
def do_e1t5(C, cond, shard, smp=None):
    old = s11.FALSE_FOR_PATCH; C.smp = C.smp0 if smp is None else smp; s11.FALSE_FOR_PATCH = cond
    try: d = s11.do_patch_title(C, shard)
    finally: s11.FALSE_FOR_PATCH = old
    return d | dict(false_condition=np.array(cond))


# ------------------------------------------------------------------ 2-3 x3tok
def do_x3tok(C, shard, nmax=None):
    z = np.load(R13 / f'raw/b1_xall/para/shard_{shard:03d}.npz'); P = C.P; para = C.para
    out = {k: [] for k in COLS.RAW_X3TOK}; chk = []; ids_cache = {}
    n = len(z['paper_id']) if nmax is None else min(nmax, len(z['paper_id']))
    for i in range(n):
        pid = str(z['paper_id'][i]); ai = int(z['author_index'][i])
        cx = {a: (rids, name) for a, rids, name in C.ctx[pid]}; rids, name = cx[ai]
        key = (pid, str(z['partner'][i]), str(z['lexical_neighbour'][i]))
        if key not in ids_cache:
            titles = [P.loc[pid].title, para[pid], P.loc[key[1]].title, P.loc[key[2]].title]
            ids_cache = {key: [s13.build(C.tok, t, 'authors', [])[0] for t in titles]}
        rr = [x3t.tok_ranks(C, ids, name) for ids in ids_cache[key]]
        out['row_id'] += list(rids); out['paper_id'] += [pid] * len(name); out['author_index'] += [ai] * len(name); out['n_authors'] += [int(z['n_authors'][i])] * len(name)
        out['token_index'] += list(range(len(name))); out['partner'] += [key[1]] * len(name); out['lexical_neighbour'] += [key[2]] * len(name)
        for v, x in zip(COLS.X3_VERS, rr): out[f'rank_{v}'] += list(x)
        stored = [z['score_original'][i], z['score_paraphrase'][i], z['score_partner'][i], z['score_lexical'][i]]
        chk.append([float(nlr(x).mean()) - float(s) for x, s in zip(rr, stored)])
    d = {k: np.array(v) for k, v in out.items()}; chk = np.abs(np.array(chk)) if chk else np.zeros((0, 4))
    rep = dict(rows=int(n), tokens=int(len(d['row_id'])), mean_abs=float(chk.mean()) if n else None, max_abs=float(chk.max()) if n else None,
               share_exact=float((chk < 1e-9).mean()) if n else None)
    return d, rep


# ------------------------------------------------------------------ 2-10 m3tok
def do_m3tok(C, shard, nmax=None):
    Pp = C.papers[C.papers.shard == shard]
    if nmax: Pp = Pp.head(nmax)
    out = {k: [] for k in COLS.RAW_M3TOK if not k.startswith('exact_')}; first = {}; exact_pid, exact_rank = [], []
    for r in Pp.itertuples():
        cx = C.ctx.get(r.paper_id, [])
        if not cx: continue
        ids, _, _ = s13.build(C.tok, r.title, 'authors', [])
        for j, (ai, rids, name) in enumerate(cx):
            rk = x3t.tok_ranks(C, ids, name)
            out['row_id'] += list(rids); out['paper_id'] += [r.paper_id] * len(name); out['author_index'] += [ai] * len(name)
            out['token_index'] += list(range(len(name))); out['rank'] += list(rk)
            if j == 0:
                first[r.paper_id] = float(nlr(rk[:1])[0])
                # exact published path (381_stage13.do_task): prompt-only batch-1 forward, last-block state at ':' -> unembed
                last = len(C.model.layers) - 1; ic = len(ids) - 1
                h = C.record(ids, [last])[last][ic:ic + 1].float(); lg = C.unembed(h).float(); g = C.torch.tensor(name[:1], device=lg.device)
                rk0 = int(((lg > lg.gather(1, g[:, None])).sum(1) + 1).item())
                exact_pid.append(r.paper_id); exact_rank.append(rk0)
    d = {k: np.array(v) for k, v in out.items()}; d['exact_paper_id'] = np.array(exact_pid); d['exact_first_rank'] = np.array(exact_rank, dtype=np.int64)
    exact = dict(zip(exact_pid, nlr(exact_rank))) if exact_pid else {}
    rep = dict(papers=len(first), tokens=int(len(d['row_id'])))
    f = R13 / f'raw/task/shard_{shard:03d}.npz'
    if f.exists() and first:
        z = np.load(f); st = dict(zip(z['paper_id'], z['author_first_nlr'])); dd = np.array([abs(first[p] - st[p]) for p in first if p in st and np.isfinite(st[p])])
        if len(dd): rep |= dict(first_first_mean_abs=float(dd.mean()), first_first_max_abs=float(dd.max()), first_first_share_exact=float((dd < 1e-12).mean()), n_compared=int(len(dd)))
        de = np.array([abs(exact[p] - st[p]) for p in exact if p in st and np.isfinite(st[p])])
        if len(de): rep |= dict(exact_mean_abs=float(de.mean()), exact_max_abs=float(de.max()), exact_share_exact=float((de < 1e-12).mean()))
    return d, rep


# ------------------------------------------------------------------ units, IO
def all_units(types=TYPES):
    import pandas as pd
    U = []
    if 'e1noise' in types: U += [('e1noise', None, k) for k in noise_shards(pd.read_parquet(R11 / 'config/sample.parquet'))]
    if 'e1t5' in types: U += [('e1t5', 'false_0_check', 0)] + [('e1t5', t, k) for t in TITLES[1:] for k in range(24)]
    if 'x3tok' in types: U += [('x3tok', None, k) for k in range(24)]
    if 'm3tok' in types: U += [('m3tok', None, k) for k in range(72)]
    return U


GATE_UNITS = [('e1noise', None, 0), ('e1t5', 'false_0_check', 0), ('e1t5', 'false_1', 0), ('x3tok', None, 0), ('m3tok', None, 0)]


def out_path(u, root=None):
    root = Path(root or R['root']) / 'raw'
    sub = {'e1noise': 'b2_e1noise', 'e1t5': 'b2_e1t5', 'x3tok': 'b2_x3tok', 'm3tok': 'b2_m3tok'}[u[0]]
    return root / sub / (u[1] or '') / f'shard_{u[2]:03d}.npz'


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **{k: v for k, v in d.items() if k != 'meta'}); os.replace(tmp, f)


def compute(C, u):
    t, c, k = u
    if t == 'e1noise': return do_e1noise(C, k), {}
    if t == 'e1t5': return do_e1t5(C, 'false_0' if c == 'false_0_check' else c, k), {}
    if t == 'x3tok': return do_x3tok(C, k)
    return do_m3tok(C, k)


# ------------------------------------------------------------------ gate checks
def _pid(rows):
    import pandas as pd
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id'); return tk.loc[rows].paper_id.to_numpy()


def e1_recovery(rt, rf, rp, layers, pid, false_from_l63=False):
    import pandas as pd
    df = pd.DataFrame({'p': pid, 't': nlr(rt), 'f': nlr(rf)})
    for i, l in enumerate(layers): df[f'x{int(l)}'] = nlr(rp[:, i])
    if false_from_l63: df['f'] = df['x63']
    pp = df.groupby('p').mean(); return {int(l): float((pp[f'x{int(l)}'] - pp.f).mean() / (pp.t - pp.f).mean()) for l in layers}


def cmp_e1(new, old, kind):
    """kind 'e1noise' (new = e1noise unit vs stored raw/patch) or 'e1t5' (new = do_patch_title rerun vs stored raw/patch_title)."""
    r = dict(rows_match=len(new['row_id']) == len(old['row_id']) and bool((np.asarray(new['row_id']) == old['row_id']).all()))
    if r['rows_match']:
        if kind == 'e1noise': a = (new['rank_true_b1'], new['rank_false_b1'], new['rank_patch_b15'], new['layers_b15'])
        else: a = (new['rank_true'], new['rank_false'], new['rank_patch'], new['layers'])
        b = (old['rank_true'], old['rank_false'], old['rank_patch'], old['layers'])
        r['rank_equal_share'] = float(np.mean([(x == y).mean() for x, y in zip(a[:3], b[:3])]))
        pid = _pid(old['row_id']); ra_ = e1_recovery(*a, pid, kind == 'e1t5'); rb_ = e1_recovery(*b, pid, kind == 'e1t5')
        r['recovery_max_abs_diff'] = float(max(abs(ra_[l] - rb_[l]) for l in rb_))
    r['threshold'] = TOL; r['status'] = 'PASS' if r['rows_match'] and r.get('recovery_max_abs_diff', 1) <= TOL else 'FAIL'
    if r['rows_match'] and r['rank_equal_share'] < 1: r['warn'] = f'rank equality {r["rank_equal_share"]:.4f} < 1.0 (WARN only)'
    return r


def gatecheck(a=None, root=None, stored=None):
    root = Path(root or R['root']); stored = Path(stored or R11 / 'raw'); rep = dict(tolerance=TOL, gross=GROSS)
    f = out_path(('e1noise', None, 0), root)
    rep['e1noise_orig_arms'] = cmp_e1(dict(np.load(f)), dict(np.load(stored / 'patch/shard_000.npz')), 'e1noise') if f.exists() else dict(status='MISSING')
    f = out_path(('e1t5', 'false_0_check', 0), root)
    rep['e1t5_false0_rerun'] = cmp_e1(dict(np.load(f)), dict(np.load(stored / 'patch_title/shard_000.npz')), 'e1t5') if f.exists() else dict(status='MISSING')
    for t, key in (('x3tok', 'mean_abs'), ('m3tok', 'exact_mean_abs')):
        f = out_path((t, None, 0), root)
        if not f.exists(): rep[t] = dict(status='MISSING'); continue
        chk = json.loads(str(np.load(f)['meta'])).get('check', {}); v = chk.get(key)
        rep[t] = dict(value=v, pass_threshold=TOL, gross_threshold=GROSS,
                      status='MISSING' if v is None else ('PASS' if v <= TOL else ('WARN' if v <= GROSS else 'FAIL')))
    st = [rep[k]['status'] for k in ('e1noise_orig_arms', 'e1t5_false0_rerun', 'x3tok', 'm3tok')]
    rep['status'] = 'FAIL' if 'FAIL' in st else ('INCOMPLETE' if 'MISSING' in st else 'PASS')
    try:
        (root / 'summary_b2B').mkdir(parents=True, exist_ok=True); (root / 'summary_b2B/gate.json').write_text(json.dumps(rep, indent=1, default=str))
        log('GATE', rep['status'], json.dumps(rep, default=str))
    except Exception as ex: print('WARN gate log failed', repr(ex), flush=True)
    return rep


# ------------------------------------------------------------------ work loop
def work(a):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); plan_ok()
    budget = a.max_minutes or 38; left = s11.slurm_minutes_left()
    if left is not None and left - 6 < budget: budget = left - 6
    types = a.types.split(',') if a.types else TYPES
    if not a.gate:
        g = gatecheck()
        if g['status'] == 'FAIL': log('GATE FAILED earlier - --all refuses to run'); sys.exit(3)
    us = [u for u in (GATE_UNITS if a.gate else all_units(types)) if u[0] in types]
    CL = R13 / 'logs/claims_b2B'; CL.mkdir(parents=True, exist_ok=True); C = None; last = {}; broken = set(); dflt = dict(e1noise=400, e1t5=90, x3tok=60, m3tok=60)
    log(f'b2B work: job {me}, {"gate" if a.gate else "all"}, {sum(not out_path(u).exists() for u in us)} of {len(us)} units to do, budget {budget:.0f} min')
    for u in us:
        f = out_path(u)
        if f.exists() or u[0] in broken: continue
        if C is not None and (time.monotonic() - t0) / 60 + 1.5 * last.get(u[0], dflt[u[0]]) / 60 > budget: log('time budget reached before', u); break
        name = '_'.join(str(x) for x in u if x is not None)
        if not s11.claim(CL / name, me): log('claimed by another job, skip', u); continue
        if f.exists(): continue
        if C is None: C = B2Ctx()
        t1 = time.monotonic()
        try: d, chk = compute(C, u)
        except Exception as ex:
            broken.add(u[0]); (R13 / 'logs').mkdir(exist_ok=True)
            (R13 / f'logs/b2B_error_{name}_{me}.txt').write_text(traceback.format_exc())
            try: os.rename(CL / name, CL / f'{name}.crashed_{me}')
            except OSError: pass
            log('UNIT CRASH (type skipped for this job; job will exit 2):', u, repr(ex)); continue
        save(f, d, dict(unit=[x for x in u], created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=chk, job=me, **C.env)); last[u[0]] = time.monotonic() - t1
        try: log(f'b2B {name} rows={len(d["row_id"])} {last[u[0]]:.0f}s total={(time.monotonic() - t0) / 60:.1f}min check', json.dumps(chk))
        except Exception as ex: print('WARN log failed', repr(ex), flush=True)
    if a.gate or any(out_path(u).exists() for u in GATE_UNITS):
        g = gatecheck()
        if g['status'] == 'FAIL': log('GATE FAILED'); sys.exit(3)
    remaining()
    if broken: sys.exit(2)


def remaining(a=None):
    miss = [u for u in all_units() if not out_path(u).exists()]
    by = {}
    for u in miss: by[u[0]] = by.get(u[0], 0) + 1
    print(f'REMAINING {len(miss)} of {len(all_units())}', json.dumps(by), flush=True); return miss


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU, 64-layer random Qwen3)
def tiny(a):
    import torch, transformers, jlens, pandas as pd, shutil
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True); R['root'] = root
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); C = B2Ctx(model=jlens.from_hf(hf, tok), tok=tok, env={'tiny': True})
    smp = C.smp0; pick = pd.concat([smp[(smp.shard == 0)].head(2), smp[(smp.shard == 6)].head(2)])
    C.smp0 = pick; ok = {}
    ok['noise shards by rule == [0, 6]'] = noise_shards(smp) == [0, 6]
    # e1noise on 2 papers of shards 0 and 6; 'stored' analogue = frozen s11.do_patch on the same papers
    for k in (0, 6):
        save(out_path(('e1noise', None, k)), do_e1noise(C, k), {'tiny': True})
        C.smp = pick; save(root / 'stored/patch' / f'shard_{k:03d}.npz', s11.do_patch(C, k), {'tiny': True})
        save(root / 'stored/patch_title' / f'shard_{k:03d}.npz', s11.do_patch_title(C, k), {'tiny': True})
    z = np.load(out_path(('e1noise', None, 0)))
    ok['e1noise keys == column module'] = all(k in z.files for k in COLS.RAW_NOISE)
    ok['e1noise L63 of the 15-batch == true (b1)'] = bool((z['rank_patch_b15'][:, -1] == z['rank_true_b1']).all())
    # e1t5: false_0 check + false_1..4 on shard 0
    for c in ['false_0_check'] + TITLES[1:]: save(out_path(('e1t5', c, 0)), do_e1t5(C, 'false_0' if c == 'false_0_check' else c, 0, smp=pick), {'tiny': True})
    ok['FALSE_FOR_PATCH restored'] = s11.FALSE_FOR_PATCH == 'false_0'
    z0 = np.load(out_path(('e1t5', 'false_0_check', 0))); z1 = np.load(out_path(('e1t5', 'false_1', 0))); zs = np.load(root / 'stored/patch_title/shard_000.npz')
    ok['e1t5 false_0 via driver == frozen path'] = bool(np.array_equal(z0['rank_patch'], zs['rank_patch']))
    ok['e1t5 false_1 differs from false_0'] = not np.array_equal(z1['rank_false'], z0['rank_false'])
    # x3tok / m3tok on 3 rows / 3 papers (self-check vs stored real-model scores is meaningless on the tiny model: WARN expected)
    for k in (0,):
        d, rep = do_x3tok(C, k, nmax=3); save(out_path(('x3tok', None, k)), d, {'tiny': True, 'check': rep})
        d, rep = do_m3tok(C, k, nmax=3); save(out_path(('m3tok', None, k)), d, {'tiny': True, 'check': rep})
    zx = np.load(out_path(('x3tok', None, 0))); zm = np.load(out_path(('m3tok', None, 0)))
    ok['x3tok keys == column module'] = all(k in zx.files for k in COLS.RAW_X3TOK)
    ok['m3tok keys == column module'] = all(k in zm.files for k in COLS.RAW_M3TOK)
    # x3tok per-token mean == score_tf (frozen 381_stage13) on the same tiny model
    pid = str(zx['paper_id'][0]); ai = int(zx['author_index'][0]); name = {a_: n for a_, _, n in C.ctx[pid]}[ai]
    ids = s13.build(C.tok, C.P.loc[pid].title, 'authors', [])[0]
    ok['x3tok mean == frozen score_tf (tiny)'] = abs(float(nlr(zx['rank_original'][(zx['paper_id'] == pid) & (zx['author_index'] == ai)]).mean()) - float(s13.score_tf(C, ids, name)[0])) < 1e-9
    ids0 = s13.build(C.tok, C.P.loc[str(zm['exact_paper_id'][0])].title, 'authors', [])[0]; ix = list(zm['paper_id']).index(zm['exact_paper_id'][0])
    ok['m3tok exact prompt-only first token == in-sequence first token (fp32 tiny, causal)'] = int(zm['exact_first_rank'][0]) == int(zm['rank'][ix])
    ok['m3tok exact arm per paper'] = len(zm['exact_paper_id']) == len(set(zm['paper_id']))
    ok['m3tok every author of the paper'] = len(set(zm['author_index'][zm['paper_id'] == zm['paper_id'][0]])) == len(C.ctx[str(zm['paper_id'][0])])
    # gate check on tiny: identical -> PASS for the HARD parts (x3/m3 self-checks are vs real-model scores -> may say FAIL/WARN)
    g = gatecheck(root=root, stored=root / 'stored')
    ok['gate e1noise identical -> PASS'] = g['e1noise_orig_arms']['status'] == 'PASS'
    ok['gate e1t5 identical -> PASS'] = g['e1t5_false0_rerun']['status'] == 'PASS'
    zz = dict(np.load(out_path(('e1noise', None, 0)))); zz['rank_patch_b15'] = zz['rank_patch_b15'] * 5 + 2; save(root / 'pert/raw/b2_e1noise/shard_000.npz', zz, {})
    shutil.copytree(root / 'raw/b2_e1t5', root / 'pert/raw/b2_e1t5', dirs_exist_ok=True)
    zt = dict(np.load(out_path(('e1t5', 'false_0_check', 0)))); zt['rank_patch'] = zt['rank_patch'] * 5 + 2; save(root / 'pert/raw/b2_e1t5/false_0_check/shard_000.npz', zt, {})
    gp = gatecheck(root=root / 'pert', stored=root / 'stored')
    ok['gate e1noise perturbed -> FAIL'] = gp['e1noise_orig_arms']['status'] == 'FAIL'
    ok['gate e1t5 perturbed -> FAIL'] = gp['e1t5_false0_rerun']['status'] == 'FAIL'
    ok = {k: bool(v) for k, v in ok.items()}; print('TINY GPU-PART CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'gatecheck', 'remaining', 'tiny'])
    ap.add_argument('--gate', action='store_true'); ap.add_argument('--all', action='store_true'); ap.add_argument('--types')
    ap.add_argument('--max-minutes', type=float); ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'work' and a.gate == a.all: raise SystemExit('work needs exactly one of --gate / --all')
    r = {'work': work, 'gatecheck': gatecheck, 'remaining': remaining}[a.cmd](a)
    if a.cmd == 'gatecheck' and r['status'] == 'FAIL': sys.exit(3)


if __name__ == '__main__':
    main()
