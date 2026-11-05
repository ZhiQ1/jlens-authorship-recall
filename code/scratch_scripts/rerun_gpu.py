"""Addendum 8 GPU re-runs (R2 x strong; R0 x uncertain 600): Stage 11 E1/E2 and Stage 12 P1/P2 on new paper lists.

Spec (frozen): /scratch/zhang.zhiqi2/jlens/391_groups/config/prereg_addendum8_groups.json ("GPU re-runs") + addendum 7.
The frozen scripts 11_stage11/361_stage11.py and 12_stage12/371_stage12.py are imported by path and NOT edited. Their unit
functions (do_patch = E1, do_knockout = E2, do_patch_pos = P1, do_patch_comp = P2) are called unchanged; only the paper
list (C.smp) differs. Prompts, false_0 title, layers, batch sizes, rank scoring = the originals.
(Only one s11 module instance is used: the one loaded inside 371_stage12, so both stages share it.)

Paper lists (freeze, CPU), columns as Stage 11 config/sample.parquet (paper_id, group, citation_bin, shard, title_pos,
tail_prompt), title_pos / tail_prompt computed by the Stage 11 freeze rule:
  rerun_R2.parquet      all R2 x strong (mc_team_outcome_tight) papers with scored author contexts.
  rerun_U0_600.parquet  600 R0 x uncertain papers; per citation bin n_b = 600 * share of the bin in the Stage 11 sample
                        (largest remainder; ties broken by ascending citation); within bin numpy default_rng(1105) choice
                        without replacement, bins visited in the Stage 11 freeze order (pandas groupby on citation_bin),
                        candidates in papers.parquet order. A bin with fewer papers than n_b: all of them, the shortfall
                        re-allocated proportionally over the other bins (not needed if every bin is large enough; logged).
  Sorted by (citation_bin, paper_id), 50 papers per shard (as Stage 11). sha256 written beside each file.

Units: (experiment, group, shard) with experiment in patch (E1), knockout (E2), patch_pos (P1), patch_comp (P2);
P1/P2 for R2 only. Output: 391_groups/raw/<experiment>/<group>/shard_XXX.npz (skip if exists; atomic save).
Check: 'check' recomputes ONE original Stage 11 shard (E1 + E2) through this driver -> 391_groups/check/ and compares
with 361_stage11/raw/{patch,knockout}/shard_XXX.npz (WARN only).

Commands: freeze | tiny --root DIR | work --units SPEC [--max-minutes M] | check --shard K | remaining
SPEC: comma list of exp:group:shards, e.g. patch:R2:0,knockout:R2:0  or  patch:U0:all
"""
import argparse, hashlib, importlib.util, inspect, json, os, sys, textwrap, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('s12', H / '12_stage12/371_stage12.py'); s12 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(s12)
s11 = s12.s11; s10 = s11.s10; R10 = s11.R10
R11 = Path('/scratch/zhang.zhiqi2/jlens/361_stage11')
OUT = Path(os.environ.get('RERUN_OUT', '/scratch/zhang.zhiqi2/jlens/391_groups'))
CFG = Path('/scratch/zhang.zhiqi2/jlens/391_groups/config')
LISTS = {'R2': 'rerun_R2.parquet', 'U0': 'rerun_U0_600.parquet'}
EXPS = {'R2': ['patch', 'knockout', 'patch_pos', 'patch_comp'], 'U0': ['patch', 'knockout']}
U0_N, U0_SEED, PER_SHARD = 600, 1105, 50
FROZEN = {'361_stage11.py': H / '11_stage11/361_stage11.py', '371_stage12.py': H / '12_stage12/371_stage12.py'}


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cite_lo(b): return int(str(b).split('-')[0].rstrip('+'))


# ------------------------------------------------------------------ freeze (CPU)
def add_positions(smp, papers):
    """Stage 11 freeze rule for title positions and the aligned tail (361_stage11.freeze, unchanged logic)."""
    tok = s10.tokenizer(); pf, _ = s10.condition_prompts(R10, papers, s11.FALSE_FOR_PATCH); pt_, _ = s10.condition_prompts(R10, papers, 'true')
    tpos, suf = [], []
    for pid in smp.paper_id:
        (ptx, pids), (pfx, fids) = pt_[pid], pf[pid]
        tp = s11.title_positions(tok, ptx, pids); tf = s11.title_positions(tok, pfx, fids); tpos.append(json.dumps(tp))
        s = min(s11.common_suffix(pids, fids), len(pids) - 1 - max(tp), len(fids) - 1 - max(tf)); suf.append(s)
        if s < 3: raise RuntimeError(f'{pid}: aligned tail {s} too short')
    smp['title_pos'] = tpos; smp['tail_prompt'] = suf
    return smp


def allocate(share, avail, n):
    """largest-remainder allocation of n over bins proportional to share, capped by avail (shortfall re-allocated)."""
    bins = sorted(share, key=cite_lo); alloc = {b: 0 for b in bins}; active = [b for b in bins]; left = n; notes = []
    while left > 0 and active:
        tot = sum(share[b] for b in active); q = {b: left * share[b] / tot for b in active}
        fl = {b: int(np.floor(q[b])) for b in active}; rem = left - sum(fl.values())
        order = sorted(active, key=lambda b: (-(q[b] - fl[b]), cite_lo(b)))
        for b in order[:rem]: fl[b] += 1
        capped = [b for b in active if alloc[b] + fl[b] > avail[b]]
        if not capped:
            for b in active: alloc[b] += fl[b]
            left = 0
        else:
            for b in capped: notes.append(f'bin {b}: only {avail[b]} papers, take all'); left -= avail[b] - alloc[b]; alloc[b] = avail[b]; active.remove(b)
    return alloc, notes


def freeze(a):
    import pandas as pd
    for f in LISTS.values():
        if (CFG / f).exists(): raise SystemExit(f'{CFG / f} exists; refusing to overwrite')
    papers, toks = s11.cohort(); has = set(toks.paper_id)
    smp11 = pd.read_parquet(R11 / 'config/sample.parquet')
    out = {}
    r2 = papers[(papers.recall_level == 'R2') & (papers.mc_team_outcome_tight == 'strong')]
    log('R2 x strong', len(r2), 'with contexts', r2.paper_id.isin(has).sum())
    r2 = r2[r2.paper_id.isin(has)][['paper_id', 'citation_bin']].assign(group='R2')
    out['R2'] = r2
    u0 = papers[(papers.recall_level == 'R0') & (papers.mc_team_outcome_tight == 'uncertain') & papers.paper_id.isin(has)]
    share = smp11.citation_bin.value_counts().to_dict(); avail = u0.citation_bin.value_counts().to_dict()
    avail = {b: int(avail.get(b, 0)) for b in share}
    alloc, notes = allocate(share, avail, U0_N); log('U0 allocation', alloc, notes)
    assert sum(alloc.values()) == U0_N
    rng = np.random.default_rng(U0_SEED); rows = []
    for b, g in u0.groupby('citation_bin'):                     # Stage 11 freeze order
        if b not in alloc: continue
        k = alloc[b]; pick = g.iloc[rng.choice(len(g), k, replace=False)] if k < len(g) else g
        rows += [dict(paper_id=p, citation_bin=b, group='U0') for p in pick.paper_id]
    out['U0'] = pd.DataFrame(rows)
    rec = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), script_sha256=sha(__file__), frozen_sha256={k: sha(v) for k, v in FROZEN.items()},
               addendum8_sha256=sha(CFG / 'prereg_addendum8_groups.json'), u0_allocation=alloc, u0_notes=notes, u0_seed=U0_SEED,
               stage11_sample_bins=share, u0_available=avail)
    for g, df in out.items():
        df = df.sort_values(['citation_bin', 'paper_id']).reset_index(drop=True)
        df['shard'] = np.arange(len(df)) // PER_SHARD
        df = add_positions(df, papers)[['paper_id', 'group', 'citation_bin', 'shard', 'title_pos', 'tail_prompt']]
        f = CFG / LISTS[g]; df.to_parquet(f, index=False); h = sha(f); Path(str(f) + '.sha256').write_text(f'{h}  {f.name}\n')
        rec[g] = dict(n=len(df), shards=int(df.shard.max()) + 1, sha256=h, tail_prompt_counts={int(k): int(v) for k, v in df.tail_prompt.value_counts().items()},
                      bins={str(k): int(v) for k, v in df.citation_bin.value_counts().items()})
        log(g, json.dumps(rec[g]))
        os.chmod(f, 0o444)
    p = CFG / 'rerun_freeze.json'; p.write_text(json.dumps(rec, indent=1)); log('wrote', p)


# ------------------------------------------------------------------ GPU context
class GCtx:
    """model + data (no lenses: E1/E2/P1/P2 use none)."""
    def __init__(self):
        import torch
        self.torch = torch; self.papers, toks = s11.cohort(); self.ctx = s11.contexts_of(toks); self.P = self.papers.set_index('paper_id')
        self.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(R10, self.papers, s11.FALSE_FOR_PATCH)[0]}
        self.model, self.tok = s10.load_model()
        self.env = dict(torch=torch.__version__, gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                        driver_sha256=sha(__file__), frozen_sha256={k: sha(v) for k, v in FROZEN.items()})


def paper_list(group):
    import pandas as pd
    f = CFG / LISTS[group]; h = Path(str(f) + '.sha256').read_text().split()[0]
    if sha(f) != h: raise RuntimeError(f'{f} changed')
    return pd.read_parquet(f)


FUN = {'patch': lambda C, k: s11.do_patch(C, k), 'knockout': lambda C, k: s11.do_knockout(C, k),
       'patch_pos': lambda C, k: s12.do_patch_pos(C, k), 'patch_comp': lambda C, k: s12.do_patch_comp(C, k)}


def out_path(e, g, k, root=None): return (root or OUT) / 'raw' / e / g / f'shard_{k:03d}.npz'


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta)), **d); os.replace(tmp, f)


def parse_units(spec):
    us = []
    for part in spec.replace(';', ',').replace(' ', ',').split(','):
        if not part: continue
        e, g, ks = part.split(':')
        n = int(paper_list(g).shard.max()) + 1
        for k in (range(n) if ks == 'all' else [int(x) for x in ks.split('+')]): us.append((e, g, k))
    return us


def unit_check(e, d):
    """in-job self-checks (WARN only)."""
    nl = lambda r: -np.log10(np.asarray(r, float)); rep = dict(rows=int(len(d['row_id'])))
    if e == 'patch':
        L = list(d['layers']); i63 = L.index(63) if 63 in L else len(L) - 1; rep['L63_equals_true'] = float((d['rank_patch'][:, i63] == d['rank_true']).mean())
        rep['true_minus_false'] = float((nl(d['rank_true']) - nl(d['rank_false'])).mean())
    if e == 'knockout':
        l = list(d['layers']); rep['ko_L0_lowers'] = float(nl(d['rank_ko'][:, l.index(max(l))]).mean() - nl(d['rank_ko'][:, l.index(0)]).mean())
    if e == 'patch_pos':
        it = list(d['items']); rep['all_L56_rec'] = float(((nl(d['rank_patch'][:, -1, it.index('all')]) - nl(d['rank_patch'][:, -1, it.index('none')])).mean())
                                                         / max(1e-9, (nl(d['rank_true']) - nl(d['rank_patch'][:, -1, it.index('none')])).mean()))
    if e == 'patch_comp':
        rep['n_comps'] = int(d['rank_patch'].shape[1])
    return rep


def work(a):
    t0 = time.monotonic(); budget = a.max_minutes
    left = s11.slurm_minutes_left()
    if left is not None and (budget is None or left - 5 < budget): budget = left - 5
    us = parse_units(a.units) if a.units else []; C = None; lists = {}; last = {}
    log('units', len(us), 'budget', budget)
    if getattr(a, 'check', None) is not None:
        C = GCtx()
        try: check(argparse.Namespace(shard=a.check), C)
        except Exception as ex:
            import traceback; log('CHECK CRASHED (non-fatal, work continues):', repr(ex)); traceback.print_exc()
    for e, g, k in us:
        f = out_path(e, g, k)
        if f.exists(): log('skip (exists)', f); continue
        el = (time.monotonic() - t0) / 60
        if budget and C is not None and el + 1.5 * last.get(e, 0) / 60 > budget: log('time budget reached before', e, g, k); break
        if C is None: C = GCtx()
        if g not in lists: lists[g] = paper_list(g)
        C.smp = lists[g]
        t1 = time.monotonic()
        try: d = FUN[e](C, k)
        except Exception as ex:
            import traceback; log('UNIT CRASH', e, g, k, repr(ex)); traceback.print_exc(); raise
        try: chk = unit_check(e, d)
        except Exception as ex: chk = dict(status='WARN', note=repr(ex))
        save(f, d, dict(unit=[e, g, k], created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=chk, papers=C.smp[C.smp.shard == k].paper_id.tolist(), **C.env))
        last[e] = time.monotonic() - t1
        log(f'{e} {g} shard {k:03d} rows={len(d["row_id"])} {last[e]:.0f}s total={(time.monotonic() - t0) / 60:.1f}min check', json.dumps(chk))


def remaining(a):
    for g, es in EXPS.items():
        n = int(paper_list(g).shard.max()) + 1
        for e in es:
            miss = [k for k in range(n) if not out_path(e, g, k).exists()]
            print(e, g, f'{n - len(miss)}/{n} done', 'missing', miss)


# ------------------------------------------------------------------ check: one original Stage 11 shard through this driver
def check(a, C=None):
    import pandas as pd
    k = a.shard; C = C or GCtx(); C.smp = pd.read_parquet(R11 / 'config/sample.parquet'); nl = lambda r: -np.log10(np.asarray(r, float))
    rep = dict(shard=k)
    for e in ('patch', 'knockout'):
        f = OUT / 'check' / e / f'shard_{k:03d}.npz'
        if f.exists(): d = dict(np.load(f))
        else:
            t1 = time.monotonic(); d = FUN[e](C, k); save(f, d, dict(unit=[e, 'stage11', k], **C.env)); log(e, 'check shard', k, f'{time.monotonic() - t1:.0f}s')
        z = np.load(R11 / 'raw' / e / f'shard_{k:03d}.npz'); same = len(z['row_id']) == len(d['row_id']) and bool((z['row_id'] == d['row_id']).all())
        r = dict(rows_match=same, gpu_stored=json.loads(str(z['meta'])).get('gpu'))
        if same:
            for c in ([x for x in ('rank_true', 'rank_false', 'rank_patch') if x in z.files] + (['rank_ko'] if 'rank_ko' in z.files else [])):
                r[c + '_equal'] = float((z[c] == d[c]).mean()); r[c + '_mean_abs_dnlr'] = float(np.abs(nl(z[c]) - nl(d[c])).mean())
                r[c + '_max_abs_dnlr'] = float(np.abs(nl(z[c]) - nl(d[c])).max())
            # paper-level recovery / loss per layer, stored vs new (the estimand itself)
            smp = C.smp.set_index('paper_id'); tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
            pid = tk.loc[d['row_id']].paper_id.to_numpy()
            if e == 'patch':
                for lab, src in (('stored', z), ('new', d)):
                    df = pd.DataFrame({'p': pid, 't': nl(src['rank_true']), 'f': nl(src['rank_false'])})
                    for i, l in enumerate(src['layers']): df[f'x{l}'] = nl(src['rank_patch'][:, i])
                    pp = df.groupby('p').mean(); r[f'recovery_{lab}'] = {int(l): float((pp[f'x{l}'] - pp.f).mean() / (pp.t - pp.f).mean()) for l in src['layers']}
            else:
                pz = np.load(R11 / 'raw/patch' / f'shard_{k:03d}.npz'); den = pd.DataFrame({'p': pid, 'g': nl(pz['rank_true']) - nl(pz['rank_false'])}).groupby('p').g.mean().mean()
                for lab, src in (('stored', z), ('new', d)):
                    df = pd.DataFrame({'p': pid}); L = list(src['layers'])
                    for i, l in enumerate(L): df[f'k{l}'] = nl(src['rank_ko'][:, i])
                    pp = df.groupby('p').mean(); r[f'loss_{lab}'] = {int(l): float((pp.k64 - pp[f'k{l}']).mean() / den) for l in L if l != 64}
            key = 'recovery' if e == 'patch' else 'loss'
            r[f'{key}_max_abs_diff'] = max(abs(r[f'{key}_new'][l] - r[f'{key}_stored'][l]) for l in r[f'{key}_new'])
        r['status'] = 'PASS' if same and r.get(f'{"recovery" if e == "patch" else "loss"}_max_abs_diff', 1) <= 0.02 else 'WARN'
        rep[e] = r
    rep['status'] = 'PASS' if all(rep[e]['status'] == 'PASS' for e in ('patch', 'knockout')) else 'WARN'
    p = OUT / 'check' / f'check_stage11_shard{k:03d}.json'; p.write_text(json.dumps(rep, indent=1)); log('CHECK', rep['status'], json.dumps(rep))


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU, 2-layer random Qwen3)
def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global OUT, CFG
    root = Path(a.root); OUT = root; CFG = root / 'config'; CFG.mkdir(parents=True, exist_ok=True)
    real = Path('/scratch/zhang.zhiqi2/jlens/391_groups/config')
    for f in ('prereg_addendum8_groups.json',): (CFG / f).write_bytes((real / f).read_bytes())
    for f in LISTS.values():
        if (CFG / f).exists(): os.chmod(CFG / f, 0o644); (CFG / f).unlink()
    freeze(a)                                        # real freeze logic into the test root
    cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    cfg.num_hidden_layers = 64; cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
    if hasattr(cfg, 'layer_types'): cfg.layer_types = cfg.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.float32).eval()
    # 64 tiny layers: every layer list, batch size and hook of the frozen code is used unchanged (no monkeypatching)
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(R10, C.papers, s11.FALSE_FOR_PATCH)[0]}; C.env = {'tiny': True}
    res = {}
    for g in LISTS:
        full = paper_list(g); C.smp = pd.concat([full[full.shard == 0].head(2), full[full.shard == 1].head(1)])
        for e in EXPS[g]:
            for k in (0, 1):
                f = out_path(e, g, k); d = FUN[e](C, k); save(f, d, dict(unit=[e, g, k], check=unit_check(e, d), tiny=True))
            # skip-if-exists: rerun of an existing unit through work() must not recompute
            res[(e, g)] = np.load(out_path(e, g, 0))
    ok = {}
    z = res[('patch', 'R2')]; ok['E1 last layer == true'] = bool((z['rank_patch'][:, -1] == z['rank_true']).all())
    z = res[('knockout', 'U0')]; ok['E2 shape'] = z['rank_ko'].shape[1] == len(s11.KO_LAYERS)
    z = res[('patch_pos', 'R2')]; it = list(z['items']); ok['P1 items'] = it[0] == 'none' and it[-1] == 'all' and z['rank_patch'].shape[1:] == (len(s12.PP_LAYERS), len(it))
    z = res[('patch_comp', 'R2')]; ok['P2 comps'] = len(z['comps']) == 1 + 2 * len(s12.PC_LAYERS)
    # P2: patching attn AND mlp of every layer == true run; spot check: none equals the E1 false run on the same rows
    e1 = res[('patch', 'R2')]
    # batched vs batch-1 fp32 rounding can move a rank by 1 (tiny run 11638140: 95.7% equal, mean |d log10 rank| 1.4e-7): tolerance, not equality
    nl = lambda r: -np.log10(np.asarray(r, float))
    ok['P2 none ~ E1 false'] = bool(np.abs(nl(z['rank_patch'][:, 0]) - nl(e1['rank_false'])).mean() < 1e-3) and bool((z['row_id'] == e1['row_id']).all())
    ok['P1 none ~ E1 false'] = bool(np.abs(nl(res[('patch_pos', 'R2')]['rank_patch'][:, 0, 0]) - nl(e1['rank_false'])).mean() < 1e-3)
    work(argparse.Namespace(units='patch:R2:0+1,knockout:U0:0+1', max_minutes=None))      # must only log 'skip (exists)'
    print('TINY CHECKS', json.dumps(ok), flush=True)
    return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['freeze', 'tiny', 'work', 'check', 'remaining'])
    ap.add_argument('--units'); ap.add_argument('--max-minutes', type=float); ap.add_argument('--shard', type=int, default=0); ap.add_argument('--root'); ap.add_argument('--check', type=int)
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    {'freeze': freeze, 'work': work, 'check': check, 'remaining': remaining}[a.cmd](a)


if __name__ == '__main__':
    main()
