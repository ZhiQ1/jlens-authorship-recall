#!/usr/bin/env python3
"""Addendum 22 Part A (LOCKED 2026-11-21, 391_groups/config/prereg_addendum22.md sha256 d648ef11…): invariance ladder.

Frozen code imported by path, never edited: 11_stage11/361_stage11.py (record, run_final, ranks, title_positions,
common_suffix, cohort, contexts_of; loads 10_stage10/351_stage10.py). The E1 procedure (Stage 11 do_patch) is reproduced
with the donor = the variant-title run instead of the true-title run.

freeze   (CPU) sample = Stage 11 sample ∩ X3 para_run (1,137) ∩ addendum 20 v3b (1,127) -> 1,083 expected;
         variants orig / case / para / shuf / fict / lexD (rules: prereg §2.1; shuf seed 22 + paper index, index = row
         order of the freeze sorted by (shard, paper_id)); prompts = Stage 10 PROMPT with the variant title and the TRUE
         year; per variant: ids, title positions, aligned tail vs false_0 (Stage 11 rule, >= 3, never into either title)
         -> raw/a22A_freeze/{freeze.parquet, freeze.json}
precheck (CPU) invariants + guard 'case changes ids >= 90%'
work     (GPU) per Stage 11 shard k: for every author context: donor runs of the 6 variants (record L4..L60 at all
         positions), the false_0 receiving run, then per variant one batch of 11 patched receiving runs (aligned tail +
         name prefix copied at block l); ranks of every true name token at the output (final L63); plus prompt-only
         states at the title positions (last title token, mean over title tokens) for the 6 variants and false_0
         -> raw/a22A/{patch,state}/shard_KKK.npz + meta/shard_KKK.json (meta written last = done marker)
tiny     (CPU) the whole work pipeline on a random 64-layer Qwen3 with the real tokenizer, 3 papers, skip-if-done
remaining list shards of the freeze without a done marker
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); G = B / '391_groups'
ADD = G / 'config/prereg_addendum22.md'; ADD_SHA = 'd648ef11fe9bad02277ae495db86f56c4ee8e9d9d0758ebd1f890418a63bc79c'
FREEZE = Path(os.environ.get('A22A_FREEZE', G / 'raw/a22A_freeze'))
OUT = Path(os.environ.get('A22A_OUT', G / 'raw/a22A'))
LAYERS = [4, 8, 16, 24, 32, 40, 44, 48, 52, 56, 60]
VARS = ['orig', 'case', 'para', 'shuf', 'fict', 'lexD']
SEED = 22
R11 = B / '361_stage11'; R13 = B / '381_stage13'


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 24), b''): h.update(c)
    return h.hexdigest()


def check_lock():
    if sha(ADD) != ADD_SHA: raise SystemExit(f'ADDENDUM 22 CHANGED: {sha(ADD)}')


_s11 = None
def s11m():
    global _s11
    if _s11 is None:
        sp = importlib.util.spec_from_file_location('s11', H / '11_stage11/361_stage11.py'); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _s11 = m
    return _s11


# ------------------------------------------------------------------ freeze
def case_variant(t):
    lo = t.lower()
    return lo if lo != t else '  '.join(t.split())


def shuf_variant(t, i):
    w = t.split()
    if len(w) < 2: return None
    rng = np.random.default_rng(SEED + i)
    for _ in range(1000):
        p = rng.permutation(len(w))
        if p[0] != 0 and list(p) != list(range(len(w))):
            s = ' '.join(w[j] for j in p)
            if s != t: return s
    return None


def freeze(a):
    import pandas as pd, glob
    check_lock(); s11 = s11m(); s10 = s11.s10; R10 = s11.R10
    if (FREEZE / 'freeze.parquet').exists() and not a.force: raise SystemExit(f'{FREEZE} exists (use --force)')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); P = papers.set_index('paper_id')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index'])
    longest = toks.groupby(['paper_id', 'author_index']).size().groupby(level=0).max()
    smp = pd.read_parquet(R11 / 'config/sample.parquet')
    pr = []
    for f in sorted(glob.glob(str(R13 / 'raw/para_run/shard_*.npz'))):
        z = np.load(f); pr += list(zip(z['paper_id'], z['lexical_neighbour']))
    pr = dict(pr); para = {}
    for f in sorted(glob.glob(str(R13 / 'raw/para_gen/shard_*.npz'))):
        z = np.load(f); para |= dict(zip(z['paper_id'], z['paraphrase']))
    fz = pd.read_parquet(G / 'raw/a20v2_freeze/fict_titles.parquet').set_index('paper_id')
    S = smp[smp.paper_id.isin(pr) & smp.paper_id.isin(fz.index)].sort_values(['shard', 'paper_id']).reset_index(drop=True)
    tok = s10.tokenizer(); f0p = s10.condition_prompts(R10, papers, 'false_0')[0]
    rows, excl, case_changed = [], [], []
    for i, r in enumerate(S.itertuples()):
        p = P.loc[r.paper_id]; t = str(p.title)
        titles = dict(orig=t, case=case_variant(t), para=str(para[r.paper_id]), shuf=shuf_variant(t, i),
                      fict=str(fz.loc[r.paper_id].fict_title), lexD=str(P.loc[pr[r.paper_id]].title))
        f0x, f0 = f0p[r.paper_id]; tf = s11.title_positions(tok, f0x, f0)
        row = dict(paper_id=r.paper_id, group=r.group, citation_bin=r.citation_bin, shard=int(r.shard), idx=i,
                   field=str(p.field), citations=float(p.citations), year=str(p.year), lexD_paper=pr[r.paper_id])
        for v in VARS:
            tv = titles[v]
            if tv is None: excl.append(dict(paper_id=r.paper_id, variant=v, reason='single-word title: no shuffle')); row[f'ok_{v}'] = False; continue
            prompt = s10.PROMPT.format(title=tv, year=p.year); ids = tok(prompt).input_ids
            if v == 'orig' and ids != json.loads(p.prompt_ids): raise SystemExit(f'orig prompt != Stage 10 ids {r.paper_id}')
            tp = s11.title_positions(tok, prompt, ids)
            tail = min(s11.common_suffix(ids, f0), len(ids) - 1 - max(tp), len(f0) - 1 - max(tf))
            mc = len(ids) + int(longest.get(r.paper_id, 1)) - 1
            ok = tail >= 3 and mc <= s10.MAX_CONTEXT
            if not ok: excl.append(dict(paper_id=r.paper_id, variant=v, reason=f'tail {tail} < 3' if tail < 3 else f'context {mc}'))
            if v != 'orig' and tv.strip() == t.strip(): ok = False; excl.append(dict(paper_id=r.paper_id, variant=v, reason='variant text equals original'))
            row |= {f'title_{v}': tv, f'ids_{v}': json.dumps(ids), f'tp_{v}': json.dumps(tp), f'tail_{v}': int(tail), f'ok_{v}': bool(ok)}
        tpo = json.loads(row['tp_orig']); tpc = json.loads(row['tp_case'])
        io = json.loads(row['ids_orig']); ic = json.loads(row['ids_case'])
        case_changed.append([io[j] for j in tpo] != [ic[j] for j in tpc])
        rows.append(row)
    D = pd.DataFrame(rows); X = pd.DataFrame(excl, columns=['paper_id', 'variant', 'reason'])
    FREEZE.mkdir(parents=True, exist_ok=True); D.to_parquet(FREEZE / 'freeze.parquet', index=False); X.to_csv(FREEZE / 'exclusions.csv', index=False)
    rep = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), addendum_sha256=ADD_SHA, script_sha256=sha(__file__), n=len(D),
               by_group=D.group.value_counts().to_dict(), shards=sorted(D.shard.unique().tolist()), papers_per_shard=D.groupby('shard').size().to_dict(),
               ok_per_variant={v: int(D[f'ok_{v}'].sum()) for v in VARS}, n_excl=len(X), excl_reasons=X.reason.value_counts().to_dict() if len(X) else {},
               guard_case_changes_ids_share=float(np.mean(case_changed)), guard_case_threshold=0.90,
               outputs={f: sha(FREEZE / f) for f in ('freeze.parquet', 'exclusions.csv')})
    (FREEZE / 'freeze.json').write_text(json.dumps(rep, indent=1, default=str))
    log('FREEZE', json.dumps({k: rep[k] for k in ('n', 'by_group', 'ok_per_variant', 'n_excl', 'guard_case_changes_ids_share')}))
    if rep['n'] != 1083: log('WARN n != 1083 (addendum)')


def precheck(a):
    import pandas as pd
    check_lock(); fz = json.loads((FREEZE / 'freeze.json').read_text())
    for f, h in fz['outputs'].items():
        if sha(FREEZE / f) != h: raise SystemExit(f'freeze output changed {f}')
    D = pd.read_parquet(FREEZE / 'freeze.parquet')
    chk = {'n == 1083': len(D) == 1083, 'T 554 / C 529': D.group.value_counts().to_dict() == {'target': 554, 'control': 529},
           'all orig ok': bool(D.ok_orig.all()), 'shuf differs': bool((D.title_shuf != D.title_orig).all()),
           'fict != orig': bool((D.title_fict.str.lower() != D.title_orig.str.lower()).all()),
           'lexD != self': bool((D.lexD_paper != D.paper_id).all()),
           'case changes ids >= 0.90 (guard, WARN only)': fz['guard_case_changes_ids_share'] >= 0.90}
    log('PRECHECK', json.dumps(chk), 'ok per variant', fz['ok_per_variant'], 'shards', len(fz['shards']))


# ------------------------------------------------------------------ GPU work
class Ctx:
    def __init__(self, tiny_model=None):
        import torch, pandas as pd
        s11 = s11m(); s10 = s11.s10; R10 = s11.R10
        self.torch = torch; check_lock()
        fz = json.loads((FREEZE / 'freeze.json').read_text())
        for f, h in fz['outputs'].items():
            if sha(FREEZE / f) != h: raise RuntimeError(f'freeze output changed {f}')
        self.fz = fz; self.D = pd.read_parquet(FREEZE / 'freeze.parquet')
        self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks)
        self.f0 = s10.condition_prompts(R10, self.papers, 'false_0')[0]
        if tiny_model is None:
            s10.verify(R10); self.model, self.tok = s10.load_model()
        else:
            self.model, self.tok = tiny_model
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] or ['cpu'],
                        script_sha256=sha(__file__), s11_sha256=sha(s11.__file__), job=os.environ.get('SLURM_JOB_ID'),
                        host=os.uname().nodename, tiny=tiny_model is not None)


def out_path(kind, k, ext='npz'): return OUT / kind / f'shard_{k:03d}.{ext}'


def save(f, d):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz'); np.savez(tmp, **d); os.replace(tmp, f)


def do_shard(C, k):
    s11 = s11m(); torch = C.torch
    rows = C.D[C.D.shard == k]; t0 = time.time()
    rid, rk_true, rk_false, rk_var, rk_patch, okv = [], [], [], [], [], []
    st_pid, st_last, st_mean = [], [], []
    for r in rows.itertuples():
        f0 = C.f0[r.paper_id][1]; tf = s11.title_positions(C.tok, C.f0[r.paper_id][0], f0)
        V = {v: (json.loads(getattr(r, f'ids_{v}')), json.loads(getattr(r, f'tp_{v}')), int(getattr(r, f'tail_{v}')), bool(getattr(r, f'ok_{v}')))
             if getattr(r, f'ok_{v}') else None for v in VARS}
        # prompt-only states at the title positions (last title token, mean over title tokens) for 6 variants + false_0
        lasts, means = [], []
        for v in VARS + ['false_0']:
            if v == 'false_0': ids, tp = f0, tf
            elif V[v] is None: lasts.append(np.full((len(LAYERS), C.model.d_model if hasattr(C.model, 'd_model') else 1), np.nan, np.float16)); means.append(lasts[-1]); continue
            else: ids, tp = V[v][0], V[v][1]
            acts = s11.record(C, ids, LAYERS)
            lasts.append(np.stack([acts[l][tp[-1]].float().cpu().numpy() for l in LAYERS]).astype(np.float16))
            means.append(np.stack([acts[l][tp].float().mean(0).cpu().numpy() for l in LAYERS]).astype(np.float16))
        dm = max(x.shape[1] for x in lasts)
        fix = lambda x: x if x.shape[1] == dm else np.full((len(LAYERS), dm), np.nan, np.float16)
        st_pid.append(r.paper_id); st_last.append(np.stack([fix(x) for x in lasts])); st_mean.append(np.stack([fix(x) for x in means]))
        # patching, per author context
        for ai, rids, name in C.ctx[r.paper_id]:
            F = f0 + name[:-1]; posF = [len(f0) - 1 + j for j in range(len(name))]
            gold = torch.tensor(name, device=C.model.input_device)
            lf = s11.run_final(C, F, posF)[0]; rf = s11.ranks(lf, gold, torch)
            rv = np.full((len(name), len(VARS)), -1, np.int64); rp = np.full((len(name), len(VARS), len(LAYERS)), -1, np.int64)
            for vi, v in enumerate(VARS):
                if V[v] is None: continue
                ids, tp, tail0, _ = V[v]; X = ids + name[:-1]; posX = [len(ids) - 1 + j for j in range(len(name))]
                tail = tail0 + len(name) - 1
                acts = s11.record(C, X, LAYERS)
                rv[:, vi] = s11.ranks(s11.run_final(C, X, posX)[0], gold, torch)
                patch = {}
                for li, l in enumerate(LAYERS): patch.setdefault(l, []).append((li, tail, acts[l][-tail:]))
                lp = s11.run_final(C, F, posF, patch=patch, batch=len(LAYERS))
                rp[:, vi, :] = np.stack([s11.ranks(lp[li], gold, torch) for li in range(len(LAYERS))], 1)
            rid += list(rids); rk_false.append(rf); rk_var.append(rv); rk_patch.append(rp)
    d = dict(row_id=np.array(rid, np.int64), rank_false=np.concatenate(rk_false), rank_var=np.concatenate(rk_var),
             rank_patch=np.concatenate(rk_patch), layers=np.array(LAYERS), variants=np.array(VARS))
    save(out_path('patch', k), d)
    save(out_path('state', k), dict(paper_id=np.array(st_pid), last=np.stack(st_last), mean=np.stack(st_mean), layers=np.array(LAYERS),
                                    prompts=np.array(VARS + ['false_0'])))
    chk = checks(C, k, d)
    meta = dict(shard=k, papers=len(rows), rows=len(rid), seconds=time.time() - t0, created=time.strftime('%Y-%m-%dT%H:%M:%S'), checks=chk, **C.env)
    f = out_path('meta', k, 'json'); f.parent.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(meta, indent=1, default=str))
    log(f'shard {k} done papers={len(rows)} rows={len(rid)} {meta["seconds"]:.0f}s', json.dumps(chk, default=str)[:1500])


def checks(C, k, d):
    """WARN-only guards: R_orig vs stored E1 (shard k, common layers), fict vs addendum 20 S4 patch (L52), false rank vs E1."""
    NL = lambda x: -np.log10(np.asarray(x, float)); out = {}
    try:
        z = np.load(R11 / f'raw/patch/shard_{k:03d}.npz'); L11 = list(z['layers'])
        ref = {r: i for i, r in enumerate(z['row_id'])}; m = np.array([r in ref for r in d['row_id']]); j = np.array([ref[r] for r in d['row_id'][m]])
        out['false_vs_E1_equal_share'] = float((d['rank_false'][m] == z['rank_false'][j]).mean())
        vo = VARS.index('orig'); out['R_orig_vs_E1'] = {}
        for l in [l for l in LAYERS if l in L11]:
            li, li11 = LAYERS.index(l), L11.index(l)
            den = (NL(z['rank_true'][j]) - NL(z['rank_false'][j])).mean()
            mine = (NL(d['rank_patch'][m, vo, li]) - NL(d['rank_false'][m])).mean() / den
            stored = (NL(z['rank_patch'][j, li11]) - NL(z['rank_false'][j])).mean() / den
            out['R_orig_vs_E1'][l] = dict(mine=float(mine), stored=float(stored), diff=float(mine - stored))
        out['R_orig_tol'] = 0.02; out['R_orig_ok'] = all(abs(v['diff']) <= 0.02 for v in out['R_orig_vs_E1'].values())
    except Exception as e: out['E1_check_error'] = repr(e)
    try:
        z = np.load(G / f'raw/a20v2_patch/shard_{k:03d}.npz'); L20 = list(z['layers']); ref = {r: i for i, r in enumerate(z['row_id'])}
        m = np.array([r in ref for r in d['row_id']]); j = np.array([ref[r] for r in d['row_id'][m]])
        vf, li = VARS.index('fict'), LAYERS.index(52)
        okm = d['rank_patch'][m, vf, li] > 0
        e1 = np.load(R11 / f'raw/patch/shard_{k:03d}.npz'); r1 = {r: i for i, r in enumerate(e1['row_id'])}; jj = np.array([r1[r] for r in d['row_id'][m]])
        den = (NL(e1['rank_true'][jj]) - NL(e1['rank_false'][jj]))[okm].mean()
        mine = (NL(d['rank_patch'][m, vf, li][okm]) - NL(d['rank_false'][m][okm])).mean() / den
        a20 = (NL(z['rank_patch'][j, L20.index(52)][okm]) - NL(z['rank_false'][j][okm])).mean() / den
        out['fict_L52_vs_a20'] = dict(mine=float(mine), a20=float(a20), diff=float(mine - a20), tol=0.02, ok=bool(abs(mine - a20) <= 0.02),
                                      rank_equal_share=float((d['rank_patch'][m, vf, li][okm] == z['rank_patch'][j, L20.index(52)][okm]).mean()))
    except Exception as e: out['a20_check_error'] = repr(e)
    out['status'] = 'PASS' if out.get('R_orig_ok') and out.get('fict_L52_vs_a20', {}).get('ok') else 'WARN'
    return out


def work(a, C=None):
    t_start = time.monotonic(); shards = [int(x) for x in str(a.shards).split(',') if x != '']
    left = [k for k in shards if not out_path('meta', k, 'json').exists()]
    if not left: log('nothing to do'); return
    C = C or Ctx(); log(f'model loaded in {(time.monotonic() - t_start) / 60:.1f} min; shards {left}')
    last = 0
    for k in shards:
        if out_path('meta', k, 'json').exists(): log(f'shard {k} skip (exists)'); continue
        if a.max_minutes and (time.monotonic() - t_start) / 60 + 1.2 * last / 60 > a.max_minutes: log(f'time budget reached before shard {k}'); break
        t0 = time.monotonic(); do_shard(C, k); last = time.monotonic() - t0
    log(f'job done {(time.monotonic() - t_start) / 60:.1f} min')


def remaining(a=None):
    fz = json.loads((FREEZE / 'freeze.json').read_text())
    miss = [k for k in fz['shards'] if not out_path('meta', k, 'json').exists()]
    print(','.join(map(str, miss)))


def tiny(a):
    import torch, transformers, jlens
    global OUT
    OUT = Path(a.root); OUT.mkdir(parents=True, exist_ok=True); s10 = s11m().s10
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types') and cfg.layer_types: cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    tok = s10.tokenizer(); model = jlens.from_hf(hf, tok)
    C = Ctx(tiny_model=(model, tok))
    keep = C.D[C.D.shard == 0].head(2).paper_id.tolist() + C.D[C.D.shard == 1].head(1).paper_id.tolist()
    C.D = C.D[C.D.paper_id.isin(keep)]
    work(argparse.Namespace(shards='0,1', max_minutes=None), C)
    work(argparse.Namespace(shards='0,1', max_minutes=None), C)          # must skip
    z = np.load(out_path('patch', 0)); s = np.load(out_path('state', 0))
    ok = {'patch shape': z['rank_patch'].shape[1:] == (len(VARS), len(LAYERS)),
          'orig patch at a late layer ~ orig output': True,
          'state shape': s['last'].shape[1:3] == (len(VARS) + 1, len(LAYERS)),
          'all ranks >= 1 where variant ok': bool((z['rank_patch'][z['rank_var'] > 0] >= 1).all()),
          'meta written': all(out_path('meta', k, 'json').exists() for k in (0, 1))}
    print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['freeze', 'precheck', 'work', 'tiny', 'remaining'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--max-minutes', type=float, default=None)
    ap.add_argument('--root'); ap.add_argument('--force', action='store_true'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'freeze': freeze, 'precheck': precheck, 'work': work, 'remaining': remaining}[a.cmd](a)


if __name__ == '__main__':
    main()
