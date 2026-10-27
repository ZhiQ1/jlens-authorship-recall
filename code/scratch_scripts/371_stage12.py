"""Stage 12 - follow-ups to Stage 11 + name-prior measurements (2026-10-27; user: run everything except a second model).

Reuses the frozen Stage 10 cohort and the Stage 11 sample/code read-only; outputs in /scratch/$USER/jlens/371_stage12/.

P1 patch_pos    Like Stage 11 E1 (true -> false_0, model output), but ONE post-title position at a time: each of the
                aligned prompt-tail tokens (closing quote / year / ')?\\n' / 'Authors' / ':'), 'names' (all name inputs
                after ':'), 'all' (= Stage 11 E1) and 'none' (unpatched false run in the SAME batch = baseline), at
                PP_LAYERS. Which token carries the paper information?
P2 patch_comp   Component patching on the whole aligned tail: replace only the attention output or only the MLP
                output of ONE layer with the true run's, at PC_LAYERS (+ 'none'). Is the title moved by attention or
                computed by MLPs inside L24-L50?
N1 prior_mc     Name prior of the multiple-choice options: every one of the 4 author lists shown in the Stage 1
                multiple choice (option 0 = true list, 1-3 = real teams of other papers) scored as a chain
                ("Authors: A1, A2, ...") with NO title (delete prompt) and with the TRUE title; model output.
N2 prior_pure   Pure name prior: each author alone after a prompt with no paper at all (PURE_PROMPT); model output and
                logit / public J-lens at PURE_LAYERS. Rows keep Stage 10 row ids (paired with Stage 10 true/delete).
F1 alens_fit    A Jacobian lens fitted on AUTHOR prompts (FIT_N papers outside the Stage 11 sample: prompt + true
                author list), layers FIT_LAYERS, resumable checkpoint (jlens.fit), one prompt-batch per job.
F2 alens_read   With that lens: Stage-10-style readout of the Stage 11 sample (each author alone, name tokens) for true
                + 5 false titles and at the last title token; available once F1 is complete.
Check policy (user rule 2026-10-27): agreement checks are recorded as WARN and never stop GPU work; only a crash holds
the queue. Commands: freeze | work | remaining | analyze
"""
import argparse, importlib.util, json, os, subprocess, sys, time
from pathlib import Path
import numpy as np

DIR = Path(__file__).resolve().parent
S11 = Path.home() / 'jlens_work/11_stage11'
sys.path.insert(0, str(S11))
_sp = importlib.util.spec_from_file_location('s11', S11 / '361_stage11.py'); s11 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s11)
s10 = s11.s10; R10 = s11.R10
ROOT = Path('/scratch') / os.environ.get('USER', '') / 'jlens/371_stage12'
LABELS = Path(s10.LABELS).parent
PP_LAYERS = [32, 40, 44, 48, 50, 52, 56]
PC_LAYERS = [8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56]
PURE_PROMPT = 'The following is the name of a researcher.\nName:'
PURE_PLAN = [('final', 63)] + [(r, l) for r in ('logit', 'jlens_public') for l in (48, 56, 62)]
FIT_N, FIT_LAYERS, FIT_SEED = 40, [24, 32, 40, 44, 48, 52, 56, 62], 12
TC = [c for c in s10.condition_names() if c != 'delete']
log, now, dump, load = s11.log, s11.now, s11.dump, s11.load


def stop(reason):
    s11.stop_queue(reason)      # holds pending s11w / s10p_ / s12* jobs (see the prefix tuple there)


# ------------------------------------------------------------------ freeze
def freeze(a):
    import pandas as pd
    smp = pd.read_parquet(s11.ROOT / 'config/sample.parquet'); papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
    pool = papers[~papers.paper_id.isin(smp.paper_id) & papers.group_tight.isin(['target', 'control'])]
    rng = np.random.default_rng(FIT_SEED)
    fit = pool.iloc[rng.choice(len(pool), FIT_N, replace=False)][['paper_id', 'title', 'year', 'authors', 'group_tight']]
    fit['text'] = [s10.PROMPT.format(title=r.title, year=r.year) + ' ' + ', '.join(a.strip() for a in str(r.authors).split(';')) for r in fit.itertuples()]
    ROOT.mkdir(parents=True, exist_ok=True); (ROOT / 'config').mkdir(exist_ok=True)
    fit.to_parquet(ROOT / 'config/fit_prompts.parquet', index=False)
    dump(ROOT / 'config/protocol.json', dict(version='stage12_v1', created=now(), doc=__doc__, pp_layers=PP_LAYERS, pc_layers=PC_LAYERS,
         pure_prompt=PURE_PROMPT, pure_plan=PURE_PLAN, fit=dict(n=FIT_N, layers=FIT_LAYERS, seed=FIT_SEED, dim_batch=1, max_seq_len=128,
         skip_first=16, sha256=s11.sha_file(ROOT / 'config/fit_prompts.parquet')),
         stage11_sample_sha256=s11.sha_file(s11.ROOT / 'config/sample.parquet'), script_sha256=s11.sha_file(__file__)))
    print('frozen', len(fit), 'fit prompts; median chars', int(fit.text.str.len().median()))


# ------------------------------------------------------------------ units
def fit_done(): return (ROOT / 'alens/lens.pt').exists()


def units():
    m, _ = s10.verify(R10); n11 = 24
    U = [('patch_pos', None, k) for k in range(n11)] + [('patch_comp', None, k) for k in range(n11)] + \
        [('prior_mc', c, k) for c in ('delete', 'true') for k in range(m['n_shards'])] + [('prior_pure', None, k) for k in range(m['n_shards'])]
    if fit_done(): U += [('alens_read', c, k) for c in TC for k in range(n11)]
    return U


def all_units():
    return units() + ([] if fit_done() else [('alens_read', c, k) for c in TC for k in range(24)])


def out_path(u, root=None):
    e, c, k = u; root = root or ROOT
    return root / 'raw' / e / (f'{c}/' if c else '') / f'shard_{k:03d}.npz'


def remaining(a):
    left = [u for u in all_units() if not out_path(u).exists()]; by = {}
    for e, c, k in left: by[e] = by.get(e, 0) + 1
    print(f'{len(left)} of {len(all_units())} units missing', by, '| author lens fit', 'DONE' if fit_done() else f'{fit_progress()}/{FIT_N} prompts')


def fit_progress():
    p = ROOT / 'alens/progress.json'
    return load(p)['done'] if p.exists() else 0


# ------------------------------------------------------------------ GPU: positions / components
def tail_layout(C, r):
    pt = json.loads(C.P.loc[r.paper_id].prompt_ids); pfi = C.prompts[s11.FALSE_FOR_PATCH][r.paper_id][1]
    return pt, pfi, int(r.tail_prompt)


def do_patch_pos(C, shard):
    torch = C.torch; out = dict(row_id=[], rank_true=[], rank_patch=[], tail_tokens=[])
    items_all = None
    for r in C.smp[C.smp.shard == shard].itertuples():
        pt, pfi, S = tail_layout(C, r)
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; nn = len(name) - 1; tail = S + nn
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = s11.record(C, T, PP_LAYERS)
            # items: ('none'), each prompt-tail offset (from the end of the prompt), 'names', 'all'
            items = [('none', [])] + [(f'p{S - i}', [len(pt) - S + i]) for i in range(S)] + [('names', list(range(len(pt), len(T))))] + [('all', list(range(len(T) - tail, len(T))))]
            names = [n for n, _ in items]
            if items_all is None: items_all = names
            elems, patch = [], {}
            for li, l in enumerate(PP_LAYERS):
                for nm, posl in items:
                    e = len(elems); elems.append((nm, l))
                    for pT in posl:
                        pF = pT - len(pt) + len(pfi)
                        patch.setdefault(l, []).append((e, ('at', pF), acts[l][pT]))
            lt = s11.run_final(C, T, posT)[0]
            res = []
            for s0 in range(0, len(elems), 48):          # chunk the batch
                sub = {l: [(e - s0, n, t) for e, n, t in v if s0 <= e < s0 + 48] for l, v in patch.items()}
                lp = s11.run_final(C, F, posF, patch=sub, batch=min(48, len(elems) - s0))
                res += [s11.ranks(lp[i], gold, torch) for i in range(lp.shape[0])]
            rk = np.stack(res, 1).reshape(len(name), len(PP_LAYERS), len(items))
            out['row_id'] += rids; out['rank_true'].append(s11.ranks(lt, gold, torch)); out['rank_patch'].append(rk)
            out['tail_tokens'].append(json.dumps(C.tok.convert_ids_to_tokens(pt[-S:])))
    return dict(row_id=np.array(out['row_id']), rank_true=np.concatenate(out['rank_true']), rank_patch=np.concatenate(out['rank_patch']),
                layers=np.array(PP_LAYERS), items=np.array(items_all), tail_tokens=np.array(out['tail_tokens']))


def do_patch_comp(C, shard):
    torch = C.torch; model = C.model; out = dict(row_id=[], rank_true=[], rank_patch=[])
    comps = ['none'] + [f'{c}{l}' for l in PC_LAYERS for c in ('attn', 'mlp')]
    for r in C.smp[C.smp.shard == shard].itertuples():
        pt, pfi, S = tail_layout(C, r)
        for ai, rids, name in C.ctx[r.paper_id]:
            T = pt + name[:-1]; F = pfi + name[:-1]; tail = S + len(name) - 1
            posT = [len(pt) - 1 + j for j in range(len(name))]; posF = [len(pfi) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=model.input_device)
            rec, hs = {}, []
            try:                                          # record the true run's attention / MLP outputs on the tail
                for l in PC_LAYERS:
                    hs.append(model.layers[l].self_attn.register_forward_hook(lambda m_, i_, o, l=l: rec.__setitem__(('attn', l), o[0][0, -tail:].detach().clone())))
                    hs.append(model.layers[l].mlp.register_forward_hook(lambda m_, i_, o, l=l: rec.__setitem__(('mlp', l), o[0, -tail:].detach().clone())))
                lt = s11.run_final(C, T, posT)[0]
            finally:
                for h in hs: h.remove()
            B = len(comps); hs = []
            try:
                for e, c in enumerate(comps):
                    if c == 'none': continue
                    kind = c.rstrip('0123456789'); l = int(c[len(kind):])
                    mod = model.layers[l].self_attn if kind == 'attn' else model.layers[l].mlp
                    val = rec[(kind, l)]
                    def hook(m_, i_, o, e=e, val=val, kind=kind):
                        t = o[0] if kind == 'attn' else o
                        t[e, -val.shape[0]:] = val.to(t.device, t.dtype); return o
                    hs.append(mod.register_forward_hook(hook))
                lp = s11.run_final(C, F, posF, batch=B)
            finally:
                for h in hs: h.remove()
            out['row_id'] += rids; out['rank_true'].append(s11.ranks(lt, gold, torch))
            out['rank_patch'].append(np.stack([s11.ranks(lp[i], gold, torch) for i in range(B)], 1))
    return dict(row_id=np.array(out['row_id']), rank_true=np.concatenate(out['rank_true']), rank_patch=np.concatenate(out['rank_patch']),
                comps=np.array(comps), layers=np.array(PC_LAYERS))


# ------------------------------------------------------------------ GPU: name priors
_MC = {}
def mc_options():
    if not _MC:
        for line in open(LABELS / 'mc_team.jsonl'):
            o = json.loads(line); _MC[o['paper_id']] = o['options']
    return _MC


def do_prior_mc(C, cond, shard):
    torch = C.torch; mc = mc_options(); rows = []
    dprompts = C.prompts['delete'] if cond == 'delete' else C.prompts['true']
    for pid in C.papers[C.papers.shard == shard].paper_id:
        if pid not in mc: continue
        pids = dprompts[pid][1]
        for oi, names in enumerate(mc[pid]):
            ids, pos, gold, aidx = list(pids), [], [], []
            for n, nm in enumerate(names):
                if n: ids += C.comma
                for t in C.tok.encode(' ' + nm.strip(), add_special_tokens=False):
                    pos.append(len(ids) - 1); ids.append(t); gold.append(t); aidx.append(n)
            if len(ids) > 1000: continue
            res = s10.fast_readout(C.model, C.L, ids[:-1], pos, [('final', 63)], torch)
            rk = s11.ranks(res[('final', 63)], torch.tensor(gold, device=C.model.input_device), torch)
            nlr = -np.log10(rk.astype(float)); aidx = np.array(aidx)
            rows.append((pid, oi, len(names), float(nlr.mean()), float(nlr[aidx == 0].mean()), float(nlr[0]), len(gold)))
    a = np.array(rows, dtype=object)
    return dict(row_id=np.arange(len(rows)), paper_id=np.array([x[0] for x in rows]), option=np.array([x[1] for x in rows]), n_authors=np.array([x[2] for x in rows]),
                mean_nlr=np.array([x[3] for x in rows]), first_author_nlr=np.array([x[4] for x in rows]), first_token_nlr=np.array([x[5] for x in rows]),
                n_tokens=np.array([x[6] for x in rows]))


def do_prior_pure(C, shard):
    torch = C.torch; pp = C.tok(PURE_PROMPT).input_ids; out = {f'{r}@{l}': [] for r, l in PURE_PLAN}; rows = []
    for pid in C.papers[C.papers.shard == shard].paper_id:
        for ai, rids, name in C.ctx.get(pid, []):
            ids = pp + name[:-1]; pos = [len(pp) - 1 + j for j in range(len(name))]
            res = s10.fast_readout(C.model, C.L, ids, pos, PURE_PLAN, torch); g = torch.tensor(name, device=C.model.input_device)
            for k, lg in res.items(): out[f'{k[0]}@{k[1]}'].append(s11.ranks(lg, g, torch))
            rows += rids
    return dict(row_id=np.array(rows), **{k: np.concatenate(v) for k, v in out.items()})


# ------------------------------------------------------------------ GPU: author-prompt lens
def fit_step(C, budget_min):
    """continue the resumable author-lens fit by as many prompts as fit in the budget (~6 min each)."""
    import pandas as pd, jlens
    fp = pd.read_parquet(ROOT / 'config/fit_prompts.parquet'); prompts = fp.text.tolist()
    (ROOT / 'alens').mkdir(parents=True, exist_ok=True); cp = ROOT / 'alens/checkpoint.pt'
    done = fit_progress(); n = max(1, int((budget_min - 6) / 7)); target = min(FIT_N, done + n)
    log(f'author-lens fit: {done} -> {target} of {FIT_N}')
    t0 = time.monotonic()
    lens = jlens.fit(C.model, prompts[:target], source_layers=FIT_LAYERS, target_layer=63, dim_batch=1, max_seq_len=128, skip_first=16,
                     checkpoint_path=str(cp), checkpoint_every=1, resume=cp.exists())
    dump(ROOT / 'alens/progress.json', dict(done=lens.n_prompts, updated=now(), seconds=round(time.monotonic() - t0), per_prompt=round((time.monotonic() - t0) / max(1, lens.n_prompts - done))))
    if lens.n_prompts >= FIT_N:
        tmp = ROOT / 'alens/lens.tmp.pt'; lens.save(str(tmp)); os.replace(tmp, ROOT / 'alens/lens.pt'); log('author lens COMPLETE')
    return lens.n_prompts


_AL = {}
def author_lens(C):
    if 'l' not in _AL:
        import jlens
        L = jlens.JacobianLens.load(str(ROOT / 'alens/lens.pt'))
        for k in list(L.jacobians): L.jacobians[k] = L.jacobians[k].to(s10.layer_device(C.model, k))
        _AL['l'] = L
    return _AL['l']


def do_alens_read(C, cond, shard):
    torch = C.torch; L = author_lens(C); prompts = C.prompts[cond]
    out = {f'alens@{l}@{p}': [] for l in FIT_LAYERS for p in ('name', 'title')}; rows = []
    from jlens.hooks import ActivationRecorder
    for r in C.smp[C.smp.shard == shard].itertuples():
        ptx, pids = prompts[r.paper_id]; it = s11.title_positions(C.tok, ptx, pids)[-1]
        for ai, rids, name in C.ctx[r.paper_id]:
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]; g = torch.tensor(name, device=C.model.input_device)
            with torch.inference_mode(), ActivationRecorder(C.model.layers, at=FIT_LAYERS) as rec:
                C.model.forward(torch.tensor([ids], device=C.model.input_device))
                for l in FIT_LAYERS:
                    h = rec.activations[l][0]
                    lg = C.model.unembed(L.transport(h[pos].float(), l)).float(); out[f'alens@{l}@name'].append(s11.ranks(lg, g, torch))
                    lt = C.model.unembed(L.transport(h[it:it + 1].float(), l)).float().expand(len(name), -1); out[f'alens@{l}@title'].append(s11.ranks(lt, g, torch))
            rows += rids
    return dict(row_id=np.array(rows), **{k: np.concatenate(v) for k, v in out.items()})


def compute(C, u):
    e, c, k = u
    return {'patch_pos': lambda: do_patch_pos(C, k), 'patch_comp': lambda: do_patch_comp(C, k), 'prior_mc': lambda: do_prior_mc(C, c, k),
            'prior_pure': lambda: do_prior_pure(C, k), 'alens_read': lambda: do_alens_read(C, c, k)}[e]()


def save(u, d, env, root=None):
    f = out_path(u, root); f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, meta=np.array(json.dumps(dict(unit=list(u), created=now(), **env))), **d); os.replace(tmp, f)


# ------------------------------------------------------------------ work loop (claims as in Stage 11; fit jobs are separate)
def work(a):
    budget = a.max_minutes; t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}')
    left = s11.slurm_minutes_left()
    if left is not None and (budget is None or left - 8 < budget): budget = left - 8
    CL = ROOT / 'logs/claims'; CL.mkdir(parents=True, exist_ok=True)
    C, last = None, 0.0
    if a.fit:                                            # fit job: one at a time, resumable
        if fit_done(): log('author lens already complete; doing ordinary units instead')
        elif s11.claim(CL / 'alens_fit', me):
            C = s11.Ctx()
            try: fit_step(C, budget - (time.monotonic() - t0) / 60)
            except Exception as e:
                import traceback; log('FIT ERROR (recorded, not stopping the queue):', repr(e)); dump(ROOT / f'logs/fit_error_{me}.json', dict(error=repr(e), tb=traceback.format_exc()))
            finally: os.rename(CL / 'alens_fit', CL / f'alens_fit.done_{me}_{int(time.time())}')
            if not fit_done() and (ROOT / f'logs/fit_error_{me}.json').exists(): return   # after a fit error, do not reuse this CUDA context
        else: log('another job is fitting; doing ordinary units')
    log(f'stage12 work: job {me}, budget {budget:.0f} min')
    while True:
        U = units(); u = None
        for v in U:
            if out_path(v).exists(): continue
            if s11.claim(CL / '_'.join(str(x) for x in v if x is not None), me): u = v; break
        if u is None: log('stage12: nothing left to claim'); return
        if C is not None and (time.monotonic() - t0) / 60 + 1.5 * last / 60 > budget:
            d = CL / '_'.join(str(x) for x in u if x is not None); os.rename(d, d.with_name(d.name + f'.released_{me}')); log('time budget reached; released', u); return
        if C is None: C = s11.Ctx()
        t1 = time.monotonic()
        try: d = compute(C, u)
        except Exception as e:
            stop(f'stage12 {u} crashed: {e!r}'); raise
        save(u, d, C.env); last = time.monotonic() - t1
        log(f'stage12 {u[0]} {u[1] or ""} shard {u[2]:03d} rows={len(d["row_id"])} {last:.0f}s total={(time.monotonic() - t0) / 60:.1f}min')


def analyze(a):
    sys.path.insert(0, str(DIR)); import stage12_analyze; stage12_analyze.main(ROOT, R10, s10, s11)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['freeze', 'work', 'remaining', 'analyze'])
    p.add_argument('--max-minutes', type=float, default=80); p.add_argument('--fit', action='store_true')
    a = p.parse_args()
    {'freeze': freeze, 'work': work, 'remaining': remaining, 'analyze': analyze}[a.command](a)


if __name__ == '__main__':
    main()
