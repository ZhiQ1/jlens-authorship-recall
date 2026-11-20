#!/usr/bin/env python3
"""Addendum 20 (LOCKED 2026-11-20) main experiment, step 2 (GPU): fict scoring, fict title position, fict -> false_0 E1 patch.

Frozen scripts are imported by path, never edited: 11_stage11/361_stage11.py (which loads 10_stage10/351_stage10.py via
351_stage10_fix1.py). Scoring = Stage 10 (s10.fast_readout + s10.score: rank = 1 + #logits strictly larger, bf16 model,
float logits), context = encode(PROMPT with the fict title and the true year) + encode(' ' + author)[:-1], every name
token scored at the position before it; the same Stage 10 name-token rows (row ids) as every other condition.

Units per Stage 11 shard k (0..23; only the 1,127 papers of a20_freeze/fict_titles.parquet):
  score     readouts final@63, logit and jlens_public at L24, 32, 40, 48, 56, 62 for every name token (fict prompt)
            -> raw/a20_score/shard_k.npz  (row_id, rank/ties/logprob/top1 per readout@layer)
  titlepos  prompt-only forwards of fict, true, false_0..4: mean log-probability of the title tokens (model output,
            positions title_pos-1, prefix only) for all 7 prompts; residuals (output of block l) at the last title
            token (L16..60 = Stage 11 PROBE_LAYERS) and at ':' (+L63) for fict and true (fp16)
            -> raw/a20_titlepos/shard_k.npz
  patch     E1 with the fict title as donor: in the false_0 run, the aligned post-title tail (tail_prompt + name
            positions) is replaced by the fict run's block-l output, one layer at a time (Stage 11 PATCH_LAYERS, batch of
            15, s11.run_final / s11.record unchanged) -> raw/a20_patch/shard_k.npz (rank_fict, rank_false, rank_patch)
  parity    (shard 0 only) Stage 10 scoring of true and false_0..4 for the shard's papers, compared with the stored
            Stage 10 files -> raw/a20_parity/shard_000.npz + parity.json. WARN only (user rule), never stops.
In-job self-checks (WARN only, values + thresholds in each unit's meta and in raw/a20_checks/<unit>.json):
  patch L63 == fict output; patch rank_false vs stored Stage 11 E1 rank_false; patch rank_fict vs score final@63.
Commands: work --shards SPEC [--parity] [--max-minutes M] | tiny --root DIR | remaining
"""
import argparse, hashlib, importlib.util, json, os, sys, time, traceback
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens')
_sp = importlib.util.spec_from_file_location('s11', H / '11_stage11/361_stage11.py'); s11 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s11)
s10 = s11.s10; R10 = s11.R10; R11 = B / '361_stage11'
FREEZE = B / '391_groups/raw/a20v2_freeze'   # v2: v1 (a20_*) fict == true title by a freeze bug; INVALID
OUT = Path(os.environ.get('A20_OUT', B / '391_groups/raw'))
LAYERS = [24, 32, 40, 48, 56, 62]
PLAN = [('final', 63)] + [('logit', l) for l in LAYERS] + [('jlens_public', l) for l in LAYERS]
PATCH_LAYERS = s11.PATCH_LAYERS
PROBE_LAYERS = s11.PROBE_LAYERS
CONDS = ['true'] + [f'false_{k}' for k in range(5)]
NL = lambda r: -np.log10(np.asarray(r, float))
FROZEN_SHA = {'351_stage10.py': None, '361_stage11.py': None}


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def key(r, l): return f'{r}@{l}'


def out_path(unit, k): return OUT / f'a20v2_{unit}' / f'shard_{k:03d}.npz'


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **d); os.replace(tmp, f)


def check_freeze():
    fz = json.loads((FREEZE / 'h2_main_freeze.json').read_text())
    for f, h in fz['outputs'].items():
        if s10.sha_file(FREEZE / f) != h: raise RuntimeError(f'a20 freeze output changed: {f}')
    return fz


# ------------------------------------------------------------------ context
class Ctx:
    def __init__(self, tiny_model=None):
        import torch, pandas as pd
        self.torch = torch
        self.fz = check_freeze()
        self.m, self.lenses = s10.verify(R10)
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
        self.F = pd.read_parquet(FREEZE / 'fict_titles.parquet')
        self.prompts = {c: s10.condition_prompts(R10, self.papers, c)[0] for c in CONDS}
        if tiny_model is None:
            self.model, self.tok = s10.load_model()
            self.L = s10.open_lenses(self.lenses, PLAN, self.model)
        else:
            self.model, self.tok, self.L = tiny_model
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] or ['cpu'],
                        script_sha256=s10.sha_file(__file__), s10_sha256=s10.sha_file(s10.__file__), s11_sha256=s10.sha_file(s11.__file__),
                        job=os.environ.get('SLURM_JOB_ID'), host=os.uname().nodename, tiny=tiny_model is not None)

    def shard_rows(self, k):
        return self.F[self.F.shard == k]


# ------------------------------------------------------------------ units
def score_condition(C, rows, cond):
    """Stage 10 scoring of every name token of the given papers under `cond` (fict or a Stage 10 condition)."""
    torch = C.torch; ids_all, buf = [], {key(r, l): {x: [] for x in ('rank', 'ties', 'logprob', 'top1')} for r, l in PLAN}
    for r in rows.itertuples():
        if cond == 'fict':
            prompt, pids = r.prompt, json.loads(r.prompt_ids)
        else:
            prompt, pids = C.prompts[cond][r.paper_id]
        if C.model.encode(prompt, max_length=s10.MAX_CONTEXT).reshape(-1).tolist() != pids:
            raise RuntimeError(f'prompt encoding differs from frozen ids: {r.paper_id} {cond}')
        for ai, rids, name in C.ctx[r.paper_id]:
            ids = pids + name[:-1]; pos = [len(pids) - 1 + j for j in range(len(name))]
            res = s10.fast_readout(C.model, C.L, ids, pos, PLAN, torch)
            gold = torch.tensor(name, device=C.model.input_device)
            for rl, lg in res.items():
                rk, ti, lp, t1 = s10.score(lg, gold, torch); b = buf[key(*rl)]
                b['rank'].append(rk); b['ties'].append(ti); b['logprob'].append(lp); b['top1'].append(t1)
            ids_all += rids
    d = dict(row_id=np.array(ids_all, np.int64))
    for kk, b in buf.items():
        for x, v in b.items(): d[f'{x}@{kk}'] = np.concatenate(v) if v else np.zeros(0)
    return d


def do_score(C, k):
    return score_condition(C, C.shard_rows(k), 'fict'), {}


def title_logprob(C, h63, ids, tp):
    torch = C.torch
    pos = [p - 1 for p in tp]
    lg = C.model.unembed(h63[pos].float()).float()
    lp = torch.log_softmax(lg, -1).gather(1, torch.tensor([ids[p] for p in tp], device=lg.device)[:, None])[:, 0]
    return lp.cpu().numpy()


def do_titlepos(C, k):
    rows = C.shard_rows(k); layers = sorted(set(PROBE_LAYERS) | {63})
    out = {f'tlp_mean_{c}': [] for c in ['fict'] + CONDS}; out |= {f'tlp_n_{c}': [] for c in ['fict'] + CONDS}
    rt = {'fict': [], 'true': []}; rc = {'fict': [], 'true': []}; pids_out = []
    for r in rows.itertuples():
        for c in ['fict'] + CONDS:
            if c == 'fict': ids = json.loads(r.prompt_ids); tp = json.loads(r.title_pos)
            else: ids = C.prompts[c][r.paper_id][1]; tp = json.loads(getattr(r, f'title_pos_{c}'))
            acts = s11.record(C, ids, layers if c in ('fict', 'true') else [63])
            lp = title_logprob(C, acts[63], ids, tp)
            out[f'tlp_mean_{c}'].append(float(lp.mean())); out[f'tlp_n_{c}'].append(len(lp))
            if c in ('fict', 'true'):
                it, ic = tp[-1], len(ids) - 1
                rt[c].append(np.stack([acts[l][it].float().cpu().numpy() for l in PROBE_LAYERS]).astype(np.float16))
                rc[c].append(np.stack([acts[l][ic].float().cpu().numpy() for l in PROBE_LAYERS + [63]]).astype(np.float16))
        pids_out.append(r.paper_id)
    d = dict(paper_id=np.array(pids_out), probe_layers=np.array(PROBE_LAYERS), **{kk: np.array(v) for kk, v in out.items()})
    for c in ('fict', 'true'): d[f'resid_title_{c}'] = np.stack(rt[c]); d[f'resid_colon_{c}'] = np.stack(rc[c])
    # self-check: true title residual vs stored Stage 11 titlepos (true, fp16)
    chk = {}
    try:
        P = C.papers.set_index('paper_id'); diffs = []
        for sh in sorted({int(P.loc[p].shard) for p in pids_out}):
            z = np.load(R11 / f'raw/titlepos/true/shard_{sh:03d}.npz'); idx = {p: i for i, p in enumerate(z['resid_paper_id'])}
            for i, p in enumerate(pids_out):
                if p in idx and int(P.loc[p].shard) == sh:
                    a = d['resid_title_true'][i].astype(np.float32); b = z['resid_title'][idx[p]].astype(np.float32)
                    diffs.append(float(np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-9)))
        chk['true_resid_title_rel_l2_vs_stage11_max'] = max(diffs) if diffs else None
        chk['true_resid_title_rel_l2_vs_stage11_median'] = float(np.median(diffs)) if diffs else None
        chk['threshold_rel_l2'] = 0.05
        chk['status'] = 'PASS' if diffs and max(diffs) <= 0.05 else 'WARN'
    except Exception as e: chk = dict(status='WARN', error=repr(e))
    return d, chk


def do_patch(C, k):
    torch = C.torch; rows_, rf, rx, rp = [], [], [], []
    for r in C.shard_rows(k).itertuples():
        X0 = json.loads(r.prompt_ids); F0 = C.prompts[s11.FALSE_FOR_PATCH][r.paper_id][1]
        for ai, rids, name in C.ctx[r.paper_id]:
            X = X0 + name[:-1]; F = F0 + name[:-1]; tail = int(r.tail_prompt) + len(name) - 1
            posX = [len(X0) - 1 + j for j in range(len(name))]; posF = [len(F0) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            acts = s11.record(C, X, PATCH_LAYERS)
            lx = s11.run_final(C, X, posX)[0]; lf = s11.run_final(C, F, posF)[0]
            patch = {}
            for i, l in enumerate(PATCH_LAYERS): patch.setdefault(l, []).append((i, tail, acts[l][-tail:]))
            lp = s11.run_final(C, F, posF, patch=patch, batch=len(PATCH_LAYERS))
            rows_ += rids; rx.append(s11.ranks(lx, gold, torch)); rf.append(s11.ranks(lf, gold, torch))
            rp.append(np.stack([s11.ranks(lp[i], gold, torch) for i in range(len(PATCH_LAYERS))], 1))
    d = dict(row_id=np.array(rows_, np.int64), rank_fict=np.concatenate(rx), rank_false=np.concatenate(rf),
             rank_patch=np.concatenate(rp), layers=np.array(PATCH_LAYERS))
    chk = {}
    i63 = PATCH_LAYERS.index(63)
    chk['L63_equals_fict_share'] = float((d['rank_patch'][:, i63] == d['rank_fict']).mean()); chk['L63_threshold'] = 0.99
    try:
        z = np.load(R11 / f'raw/patch/shard_{k:03d}.npz'); ref = dict(zip(z['row_id'], z['rank_false']))
        m = np.array([r in ref for r in d['row_id']]); rr = np.array([ref[r] for r in d['row_id'][m]])
        chk['false_vs_stage11_rank_equal_share'] = float((d['rank_false'][m] == rr).mean())
        chk['false_vs_stage11_mean_abs_dlog10rank'] = float(np.abs(NL(d['rank_false'][m]) - NL(rr)).mean())
        chk['false_vs_stage11_n'] = int(m.sum()); chk['false_thresholds'] = dict(equal_share=0.75, mean_abs_dlog10rank=0.05)
    except Exception as e: chk['false_vs_stage11_error'] = repr(e)
    sf = out_path('score', k)
    if sf.exists():
        z = np.load(sf); ref = dict(zip(z['row_id'], z['rank@final@63'])); rr = np.array([ref[r] for r in d['row_id']])
        chk['fict_vs_score_final_equal_share'] = float((d['rank_fict'] == rr).mean())
        chk['fict_vs_score_mean_abs_dlog10rank'] = float(np.abs(NL(d['rank_fict']) - NL(rr)).mean())
    ok = chk['L63_equals_fict_share'] >= .99 and chk.get('false_vs_stage11_rank_equal_share', 0) >= .75 and chk.get('false_vs_stage11_mean_abs_dlog10rank', 1) <= .05
    chk['status'] = 'PASS' if ok else 'WARN'
    return d, chk


def stage10_ref(C, cond, pids, readout, layer):
    P = C.papers.set_index('paper_id'); rk, lp = {}, {}
    for sh in sorted({int(P.loc[p].shard) for p in pids}):
        z = np.load(s10.out_file(R10, readout, layer, sh, cond))
        rk.update(zip(z['row_id'].tolist(), z['rank'].tolist())); lp.update(zip(z['row_id'].tolist(), z['logprob'].tolist()))
    return rk, lp


def do_parity(C, k):
    import pandas as pd
    rows = C.shard_rows(k); d = {}; rep = {}
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    for c in CONDS:
        s = score_condition(C, rows, c)
        for kk, v in s.items(): d[f'{c}|{kk}'] = v
        pid_of = toks.set_index('row_id').paper_id.reindex(s['row_id']).to_numpy()
        for r, l in PLAN:
            rk, lp = stage10_ref(C, c, rows.paper_id.tolist(), r, l)
            ref_r = np.array([rk[i] for i in s['row_id']]); ref_l = np.array([lp[i] for i in s['row_id']])
            got = s[f'rank@{key(r, l)}']; gl = s[f'logprob@{key(r, l)}']
            pm = pd.DataFrame(dict(p=pid_of, a=NL(got), b=NL(ref_r))).groupby('p').mean()
            rep[f'{c}|{key(r, l)}'] = dict(n_tokens=int(len(got)), rank_equal_share=float((got == ref_r).mean()),
                                           mean_abs_dlog10rank=float(np.abs(NL(got) - NL(ref_r)).mean()),
                                           max_abs_dlogprob=float(np.abs(gl - ref_l).max()),
                                           paper_mean_nlr_max_abs_diff=float((pm.a - pm.b).abs().max()),
                                           paper_mean_nlr_mean_diff=float((pm.a - pm.b).mean()))
    # tolerance: >= 4 bf16 units at |logit| 32-64 (spacing 0.25) -> logprob 1.0; ranks: Stage 11 smoke thresholds
    thr = dict(rank_equal_share=0.75, mean_abs_dlog10rank=0.05, max_abs_dlogprob=1.0)
    warn = [kk for kk, v in rep.items() if v['rank_equal_share'] < thr['rank_equal_share'] or v['mean_abs_dlog10rank'] > thr['mean_abs_dlog10rank']
            or v['max_abs_dlogprob'] > thr['max_abs_dlogprob']]
    chk = dict(status='WARN' if warn else 'PASS', thresholds=thr, warn_pairs=warn, pairs=rep, n_papers=int(len(rows)), gpu=C.env['gpu'])
    return d, chk


FUN = {'score': do_score, 'titlepos': do_titlepos, 'patch': do_patch, 'parity': do_parity}


def run_unit(C, unit, k, t_start, budget, last):
    f = out_path(unit, k)
    if f.exists(): log(f'skip (exists) {unit} shard {k:03d}'); return last, False
    if budget and (time.monotonic() - t_start) / 60 + 1.5 * last.get(unit, 0) / 60 > budget:
        log(f'time budget reached before {unit} shard {k:03d}'); return last, True
    t0 = time.monotonic(); d, chk = FUN[unit](C, k); el = time.monotonic() - t0
    meta = dict(unit=unit, shard=k, created=time.strftime('%Y-%m-%dT%H:%M:%S'), seconds=el, checks=chk,
                n_papers=int(len(C.shard_rows(k))), freeze_sha=C.fz['outputs'], **C.env)
    save(f, d, meta)
    cf = OUT / 'a20v2_checks' / f'{unit}_{k:03d}.json'; cf.parent.mkdir(parents=True, exist_ok=True); cf.write_text(json.dumps(meta, indent=1, default=str))
    st = chk.get('status', '-') if chk else '-'
    log(f'{unit} shard {k:03d} papers={meta["n_papers"]} rows={len(d["row_id"]) if "row_id" in d else len(d.get("paper_id", d.get("true|row_id", [])))} {el:.0f}s check={st} total={(time.monotonic() - t_start) / 60:.1f}min')
    if st == 'WARN': log(f'WARN {unit} shard {k:03d}: self-check missed its threshold; continuing (user rule). {json.dumps(chk, default=str)[:1500]}')
    last[unit] = el
    return last, False


def parse_shards(s):
    out = []
    for part in s.split('+'):
        a_, _, b_ = part.partition('-'); out += list(range(int(a_), int(b_ or a_) + 1))
    return out


def work(a, C=None):
    t_start = time.monotonic(); shards = parse_shards(a.shards)
    todo = [(u, k) for k in shards for u in ('score', 'titlepos', 'patch')] + ([('parity', shards[0])] if a.parity else [])
    if a.parity: todo = [todo[0], todo[-1]] + todo[1:-1]           # shard's score first, then parity, then the rest
    left = [(u, k) for u, k in todo if not out_path(u, k).exists()]
    if not left: log('nothing to do'); return
    C = C or Ctx(); log(f'model loaded in {(time.monotonic() - t_start) / 60:.1f} min; {len(left)} units: {left}')
    last = {}
    for u, k in todo:
        last, stop = run_unit(C, u, k, t_start, a.max_minutes, last)
        if stop: break
    log(f'job done, {(time.monotonic() - t_start) / 60:.1f} min')


def remaining(a=None):
    import pandas as pd
    sh = sorted(pd.read_parquet(FREEZE / 'fict_titles.parquet').shard.unique())
    miss = [(u, k) for u in ('score', 'titlepos', 'patch') for k in sh if not out_path(u, k).exists()]
    print(len(miss), 'missing', miss[:30], '| parity', out_path('parity', 0).exists())


# ------------------------------------------------------------------ tiny full-pipeline test (CPU, random 64-layer model)
class IdLens:
    def transport(self, h, l): return h


def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global OUT
    OUT = Path(a.root); OUT.mkdir(parents=True, exist_ok=True)
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = Ctx(tiny_model=(model, tok, {'public': IdLens()}))
    keep = C.F[C.F.shard == 0].head(2).paper_id.tolist() + C.F[C.F.shard == 1].head(1).paper_id.tolist()
    C.F = C.F[C.F.paper_id.isin(keep)]
    work(argparse.Namespace(shards='0-1', parity=True, max_minutes=None), C)
    work(argparse.Namespace(shards='0-1', parity=True, max_minutes=None), C)        # must only log 'skip (exists)'
    ok = {}
    z = np.load(out_path('patch', 0)); ok['patch L63 == fict'] = bool((z['rank_patch'][:, -1] == z['rank_fict']).all())
    s = np.load(out_path('score', 0)); ok['score rows == patch rows'] = bool(np.array_equal(np.sort(s['row_id']), np.sort(z['row_id'])))
    ref = dict(zip(s['row_id'], s['rank@final@63'])); ok['patch fict ~ score final'] = float(np.mean([ref[r] == x for r, x in zip(z['row_id'], z['rank_fict'])])) > .9
    t = np.load(out_path('titlepos', 0)); ok['titlepos shapes'] = t['resid_title_fict'].shape[1:] == (len(PROBE_LAYERS), 64) and len(t['tlp_mean_fict']) == 2
    p = np.load(out_path('parity', 0)); ok['parity keys'] = all(f'{c}|rank@final@63' in p.files for c in CONDS)
    ok['all units written'] = all(out_path(u, k).exists() for u in ('score', 'titlepos', 'patch') for k in (0, 1))
    print('TINY CHECKS', json.dumps(ok), flush=True)
    return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'tiny', 'remaining'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--parity', action='store_true')
    ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'work': work, 'remaining': remaining}[a.cmd](a)


if __name__ == '__main__':
    main()
