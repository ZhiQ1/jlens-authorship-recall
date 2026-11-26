#!/usr/bin/env python3
"""Addendum 29 (TODO #11): Stage 10 readouts at the never-measured layers L25, L26, L28, L30, L34, L36, L38.
Pre-registration: 391_groups/config/prereg_addendum29.md (sha256 checked). Wrapper around the frozen batch-3 Stage 10 wrapper
13_stage13/stage13_b3_s10_gpu.py (imported by path, NOT edited) with a new item 'a29':
  layers  ITEM_LAYERS['a29'] = [25, 26, 28, 30, 34, 36, 38] (+ the hard-check layers L24, L48 recomputed in the same forward)
  papers  the within-bin analysis set only: citation bins with >= 30 target and >= 30 control papers (5,916 papers)
  conds   true, false_0..4 ('delete' is not needed for the title-specific signal and is skipped)
Outputs raw/b3_s10_a29/<cond>/shard_XXX.npz under 381_stage13 (same layout as 3-1 / 3-2); gate json in summary_b3_s10_a29/.
Commands: run --shards 0 (gate mode, hard check) | run --all | tiny (CPU) | analyze -> 391_groups/summary_a29/
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; J = Path('/scratch/zhang.zhiqi2/jlens'); G = J / '391_groups'
PREREG = G / 'config/prereg_addendum29.md'; SUMM = G / 'summary_a29'
NEW_LAYERS = [25, 26, 28, 30, 34, 36, 38]; NB, SEED, MIN_BIN = 2000, 29, 30


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sys.modules[name] = m; sp.loader.exec_module(m); return m


g = load(H / '13_stage13/stage13_b3_s10_gpu.py', 'b3s10_frozen_for_a29')
g.K.ITEM_LAYERS['a29'] = NEW_LAYERS
g.K.CONDS = [c for c in g.K.CONDS if c != 'delete']
_orig_setup = g.setup


def within_bin_set(papers):
    tc = papers[papers.group_tight.isin(['target', 'control'])]
    ct = tc.groupby(['citation_bin', 'group_tight']).size().unstack(fill_value=0)
    bins = ct.index[(ct.get('target', 0) >= MIN_BIN) & (ct.get('control', 0) >= MIN_BIN)]
    return set(tc.paper_id[tc.citation_bin.isin(bins)])


def setup(item, tiny):
    root, m, lenses, plan, papers, ctx, toks = _orig_setup(item, tiny)
    if not tiny:
        keep = within_bin_set(papers)
        ctx = ctx[ctx.paper_id.isin(keep)]; toks = toks[toks.paper_id.isin(keep)]
    return root, m, lenses, plan, papers, ctx, toks


g.setup = setup


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lock_sha():
    lj = G / 'config/addendum29_lock.json'
    if not lj.exists(): raise SystemExit('addendum 29 not locked')
    want = json.loads(lj.read_text())['sha256']
    if sha(PREREG) != want: raise SystemExit('ADDENDUM 29 CHANGED since lock')
    return want


ACCEPT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_b3_s10_a29/gate_accepted_warn.json')


def run(a):
    if not a.tiny: lock_sha()
    if a.all and not a.tiny:
        # 2026-11-22: the frozen wrapper's gate compares per-shard MEANS of the paper spec between the stored Stage 10 (all target +
        # control papers of shard 0) and the new units (within-bin subset only), so it fails by construction on this subset
        # (ranks at L24/L48 exact 36,720/36,720; per-paper |diff| 0). Per the user's standing rule (tolerance misses are WARN, never
        # stop GPU work) the --all run uses an accepted-as-WARN gate record instead of gate.json.
        if not ACCEPT.exists(): raise SystemExit(f'missing {ACCEPT}')
        _roots = g.K.s10_roots
        def roots(item, tiny=False):
            r = _roots(item, tiny)
            if item == 'a29' and not tiny: r = dict(r, gate=ACCEPT)
            return r
        g.K.s10_roots = roots
    ns = argparse.Namespace(item='a29', shards=a.shards, all=a.all, max_minutes=a.max_minutes, tiny=a.tiny)
    g.run(ns)


def analyze(a):
    want = lock_sha()
    R = g.K.s10_roots('a29', False); root = g.K.R10
    m, _ = g.s10.verify(root)
    papers = pd.read_parquet(root / 'cohort/papers.parquet'); keep = within_bin_set(papers)
    toks = pd.read_parquet(root / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
    units = [(c, k) for c in g.K.CONDS for k in range(m['n_shards'])]
    U = g.load_units(R, units, need_all=not a.allow_missing)
    pids = sorted(keep & set(toks.paper_id))
    sys.path.insert(0, str(H / '13_stage13')); import stage13_cpu as c13
    _, team = c13.group_folds(papers.paper_id.to_numpy()); tm = dict(zip(papers.paper_id, team))
    P = papers.set_index('paper_id').loc[pids]
    codes, uniq = pd.factorize(pd.Series([tm[p] for p in pids]))
    W = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]
    rows = []
    for r in g.K.READOUTS:
        for l in g.K.item_layers('a29'):
            spec = g.paper_spec_new(U, toks, pids, r, l)
            est = 0.0; ws = 0.0; bs = np.zeros(NB)
            for cb, sub in P.groupby('citation_bin'):
                it = np.array([i for i, p in enumerate(pids) if p in sub.index and P.loc[p, 'group_tight'] == 'target'])
                ic = np.array([i for i, p in enumerate(pids) if p in sub.index and P.loc[p, 'group_tight'] == 'control'])
                if len(it) < MIN_BIN or len(ic) < MIN_BIN: continue
                xt, xc = spec[it], spec[ic]; okt, okc = np.isfinite(xt), np.isfinite(xc)
                w = len(it) * len(ic) / (len(it) + len(ic))
                est += w * (xt[okt].mean() - xc[okc].mean())
                bs += w * ((W[:, it[okt]] @ xt[okt]) / W[:, it[okt]].sum(1) - (W[:, ic[okc]] @ xc[okc]) / W[:, ic[okc]].sum(1)); ws += w
            lo, hi = np.percentile(bs / ws, [2.5, 97.5])
            rows.append(dict(readout=r, layer=l, new_layer=l in NEW_LAYERS, est=est / ws, lo=lo, hi=hi, n_papers=len(pids)))
    T = pd.DataFrame(rows).sort_values(['readout', 'layer'])
    out = Path(a.out) if a.out else SUMM; out.mkdir(parents=True, exist_ok=True); T.to_csv(out / 'tc_within_bin.csv', index=False)
    new = T[T.new_layer]
    onset = new[(new.lo > 0) & (new.est > 0.01)]
    rev = new[(new.hi < 0) & (new.est < -0.01)]
    verdict = ('an earlier onset (some filled layer CI > 0 and estimate > 0.01): ' + ', '.join(f'{x.readout} L{x.layer}' for x in onset.itertuples())) if len(onset) \
        else '"≈ 0 before L50" holds at the filled layers (every CI includes 0 or |estimate| ≤ 0.01)'
    res = dict(label='addendum 29 (LOCKED)', addendum_sha256=want, n_papers=len(pids), verdict=verdict,
               reversed_cells=[f'{x.readout} L{x.layer} {x.est:+.4f} [{x.lo:+.4f}, {x.hi:+.4f}]' for x in rev.itertuples()])
    (out / 'a29_results.json').write_text(json.dumps(res, indent=1, default=float))
    (out / 'report.md').write_text('# Addendum 29 — Stage 10 filled layers\n\n' + json.dumps(res, indent=1, default=float) + '\n\n' + T.to_string(index=False, float_format=lambda v: f'{v:.4f}') + '\n')
    print(json.dumps(res, default=float), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['run', 'analyze'])
    ap.add_argument('--shards', default='0'); ap.add_argument('--all', action='store_true'); ap.add_argument('--max-minutes', type=float, default=38)
    ap.add_argument('--tiny', action='store_true'); ap.add_argument('--out'); ap.add_argument('--allow-missing', action='store_true')
    a = ap.parse_args(); {'run': run, 'analyze': analyze}[a.cmd](a)
