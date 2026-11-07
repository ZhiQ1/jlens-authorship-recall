"""Batch 2, addendum 11 part B: groups C (R1 x strong) and D (R1 x fail) completed for Stage 11 E1 / E2.

Plan (frozen): /scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg_addendum11.json, part "B groups C and D completed for
E1 / E2" (sha256 checked at start; a mismatch is a WARN printed in every log and report).
Papers: all R1 x strong (C, 511) and R1 x fail (D, 34) papers of the Stage 10 cohort; the 36 C and 5 D papers already in
the Stage 11 sample are re-used (stored 361_stage11/raw), not re-run -> 475 + 29 new papers.
GPU: the addendum-8 driver 14_groups/rerun_gpu.py is loaded by path (unchanged; it loads the frozen 371_stage12.py and its
s11). Its unit functions FUN['patch'] (= s11.do_patch, E1) and FUN['knockout'] (= s11.do_knockout, E2) are called
unchanged with C.smp = the new paper list; prompts, false_0 title, layers, batch sizes, rank scoring = the originals.
Paper lists (freeze, CPU): 391_groups/config/b2_cd_{C,D}.parquet (+ .sha256), columns as Stage 11 config/sample.parquet,
title_pos / tail_prompt by the Stage 11 freeze rule (rerun_gpu.add_positions), sorted by (citation_bin, paper_id), 50 papers
per shard (as Stage 11 / addendum 8): C 475 -> 10 shards, D 29 -> 1 shard.
Units (skip-if-exists, claims under 391_groups/b2_cd/claims, atomic save):
  check:<e>:K  re-run of original Stage 11 shard K (default 0) through the driver -> 391_groups/b2_cd/check/<e>/  (HARD CHECK)
  <e>:<g>:k    e in patch / knockout, g in C / D -> 391_groups/b2_cd/raw/<e>/<g>/shard_XXX.npz
HARD CHECK (addendum 11 B, "as addendum 8"): the re-run of one original Stage 11 shard reproduces the stored E1 / E2 values:
rows identical and the shard-level estimand (E1 recovery per layer, E2 loss per layer) within |diff| <= 0.005 of the stored
shard (the batch-1 tolerance of addendum 10 / b1_p12f). Rank equality share is reported (WARN below 1.0). On FAIL the job
exits 3 before any new unit and the chain stops.
Analysis (CPU; rerun_analyze.py functions loaded by path): groups A, B, C, D on UNWRITTEN authors (addendum 7 circularity rule;
author position split unwritten_first / unwritten_other as addendum 8; written = reference only). Estimands as Stage 11: E1
R(l) = mean(patched_l - false) / mean(true - false); E2 loss(l) = mean(k64 - k_l) / mean(true - false_0); numerator,
denominator and ratio each with a 95% team-cluster bootstrap (groups_core.Engine, 2,000 draws, seed 391, one shared draw ->
paired contrasts). Contrasts: C - A and D - B within citation bin (bin-standardised: sum_b w_b mean_b(num) / sum_b w_b
mean_b(den), w_b = n_a n_b / (n_a + n_b); C - A bins with >= 10 papers in C and >= 10 in A (addendum 7 P2); D - B bins with
>= 1 D paper and >= 10 B papers - D < 30 papers in total, descriptive only); C - D plain difference and within-bin
(>= 1 / >= 1), descriptive. Plain (unstandardised) differences are given beside every within-bin value. n < 30: descriptive.
Commands: freeze | tiny --root DIR | work (--gate | --all) [--check-shard K] [--max-minutes M] | check | remaining |
          analyze | unittest
Outputs: 391_groups/b2_cd/{raw,check,claims,logs}, 391_groups/b2_cd/summary/*.csv, 391_groups/reports/b2_cd_report.md
"""
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
G = BASE / '391_groups'; CFG = G / 'config'; ROOT = G / 'b2_cd'; REP = G / 'reports/b2_cd_report.md'
PLAN = BASE / '381_stage13/config/prereg_addendum11.json'; PLAN_SHA = open(str(PLAN) + '.sha256').read().split()[0] if Path(str(PLAN) + '.sha256').exists() else ''
LISTS = {'C': 'b2_cd_C.parquet', 'D': 'b2_cd_D.parquet'}; EXPS = ['patch', 'knockout']; PER_SHARD = 50; TOL = 0.005
sys.path.insert(0, str(H / '14_groups'))


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nlr(r): return -np.log10(np.asarray(r, float))


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


COLS = load(H / '13_stage13/b2_groupB_cols.py', 'b2cols')
_M = {}
def rg():
    if 'rg' not in _M: _M['rg'] = load(H / '14_groups/rerun_gpu.py', 'rerun_gpu_b2cd')
    return _M['rg']


def plan_ok():
    ok = PLAN.exists() and sha(PLAN) == PLAN_SHA and PLAN_SHA != ''
    if not ok: log('WARN addendum 11 sha256 differs from its .sha256 file')
    return ok


# ------------------------------------------------------------------ freeze (CPU)
def freeze(a=None, cfg=None):
    import pandas as pd
    cfg = Path(cfg or CFG); m = rg(); s11 = m.s11
    for f in LISTS.values():
        if (cfg / f).exists(): raise SystemExit(f'{cfg / f} exists; refusing to overwrite')
    papers, toks = s11.cohort(); has = set(toks.paper_id); smp11 = pd.read_parquet(R11 / 'config/sample.parquet')
    rec = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), script_sha256=sha(__file__), rerun_gpu_sha256=sha(H / '14_groups/rerun_gpu.py'),
               addendum11_sha256=sha(PLAN), frozen_sha256={k: sha(v) for k, v in m.FROZEN.items()})
    for g, (rl, oc) in {'C': ('R1', 'strong'), 'D': ('R1', 'fail')}.items():
        allg = papers[(papers.recall_level == rl) & (papers.mc_team_outcome_tight == oc)]
        new = allg[allg.paper_id.isin(has) & ~allg.paper_id.isin(smp11.paper_id)][['paper_id', 'citation_bin']].assign(group=g)
        df = new.sort_values(['citation_bin', 'paper_id']).reset_index(drop=True); df['shard'] = np.arange(len(df)) // PER_SHARD
        df = m.add_positions(df, papers)[['paper_id', 'group', 'citation_bin', 'shard', 'title_pos', 'tail_prompt']]
        f = cfg / LISTS[g]; cfg.mkdir(parents=True, exist_ok=True); df.to_parquet(f, index=False); h = sha(f); Path(str(f) + '.sha256').write_text(f'{h}  {f.name}\n')
        rec[g] = dict(cohort=int(len(allg)), with_contexts=int(allg.paper_id.isin(has).sum()), in_stage11_sample=int(allg.paper_id.isin(smp11.paper_id).sum()),
                      new=int(len(df)), shards=int(df.shard.max()) + 1, sha256=h, bins={str(k): int(v) for k, v in df.citation_bin.value_counts().items()},
                      tail_prompt_counts={int(k): int(v) for k, v in df.tail_prompt.value_counts().items()})
        log(g, json.dumps(rec[g])); os.chmod(f, 0o444)
    (cfg / 'b2_cd_freeze.json').write_text(json.dumps(rec, indent=1)); log('wrote', cfg / 'b2_cd_freeze.json'); return rec


def paper_list(g, cfg=None):
    import pandas as pd
    f = Path(cfg or CFG) / LISTS[g]; h = Path(str(f) + '.sha256').read_text().split()[0]
    if sha(f) != h: raise RuntimeError(f'{f} changed since freeze')
    return pd.read_parquet(f)


# ------------------------------------------------------------------ GPU units
def n_shards(g, cfg=None): return int(paper_list(g, cfg).shard.max()) + 1


def all_units(check_shard=0, cfg=None):
    return [('check', e, check_shard) for e in EXPS] + [(e, g, k) for g in LISTS for k in range(n_shards(g, cfg)) for e in EXPS]


def gate_units(check_shard=0):
    return [('check', e, check_shard) for e in EXPS] + [(e, 'C', 0) for e in EXPS]


def out_path(u, root=None):
    root = Path(root or ROOT)
    return root / 'check' / u[1] / f'shard_{u[2]:03d}.npz' if u[0] == 'check' else root / 'raw' / u[0] / u[1] / f'shard_{u[2]:03d}.npz'


def compute(C, u, cfg=None):
    import pandas as pd
    m = rg()
    if u[0] == 'check': C.smp = pd.read_parquet(R11 / 'config/sample.parquet'); return m.FUN[u[1]](C, u[2])
    C.smp = paper_list(u[1], cfg); return m.FUN[u[0]](C, u[2])


def shard_estimand(e, d, pz, smp_pids=None):
    """E1: recovery per layer; E2: loss per layer (denominator from the paired E1 shard pz), all papers of the shard."""
    import pandas as pd
    tk = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id'); pid = tk.loc[d['row_id']].paper_id.to_numpy()
    if e == 'patch':
        df = pd.DataFrame({'p': pid, 't': nlr(d['rank_true']), 'f': nlr(d['rank_false'])})
        for i, l in enumerate(d['layers']): df[f'x{int(l)}'] = nlr(d['rank_patch'][:, i])
        pp = df.groupby('p').mean(); return {int(l): float((pp[f'x{int(l)}'] - pp.f).mean() / (pp.t - pp.f).mean()) for l in d['layers']}
    den = pd.DataFrame({'p': tk.loc[pz['row_id']].paper_id.to_numpy(), 'g': nlr(pz['rank_true']) - nlr(pz['rank_false'])}).groupby('p').g.mean().mean()
    df = pd.DataFrame({'p': pid}); L = [int(l) for l in d['layers']]
    for i, l in enumerate(L): df[f'k{l}'] = nlr(d['rank_ko'][:, i])
    pp = df.groupby('p').mean(); return {l: float((pp.k64 - pp[f'k{l}']).mean() / den) for l in L if l != 64}


def compare(e, new, old, pz):
    """hard-check comparison of one re-run shard (new) with the stored shard (old). Returns a record with status."""
    r = dict(experiment=e, rows_match=len(new['row_id']) == len(old['row_id']) and bool((new['row_id'] == old['row_id']).all()))
    if r['rows_match']:
        ks = ['rank_true', 'rank_false', 'rank_patch'] if e == 'patch' else ['rank_ko']
        r['rank_equal_share'] = float(np.mean([(new[k] == old[k]).mean() for k in ks]))
        r['max_abs_dnlr'] = float(max(np.abs(nlr(new[k]) - nlr(old[k])).max() for k in ks))
        a, b = shard_estimand(e, new, pz), shard_estimand(e, old, pz); r['estimand_max_abs_diff'] = float(max(abs(a[l] - b[l]) for l in b))
        r['estimand_new'] = a; r['estimand_stored'] = b
    r['threshold'] = TOL
    r['status'] = 'PASS' if r['rows_match'] and r.get('estimand_max_abs_diff', 1.0) <= TOL else 'FAIL'
    r['warn'] = (f'rank equality {r["rank_equal_share"]:.4f} < 1 (threshold 1.0, WARN only)' if r['rows_match'] and r['rank_equal_share'] < 1 else '')
    return r


def check(a=None, root=None, k=None, stored=None):
    """HARD CHECK on the check units. Returns rep; status PASS / FAIL / INCOMPLETE."""
    root = Path(root or ROOT); k = getattr(a, 'check_shard', 0) if k is None else k; stored = Path(stored or R11 / 'raw')
    rep = dict(item='addendum 11 B', shard=k, tolerance=TOL)
    fs = {e: out_path(('check', e, k), root) for e in EXPS}
    if not all(f.exists() for f in fs.values()):
        rep['status'] = 'INCOMPLETE'; return rep
    pz = np.load(stored / 'patch' / f'shard_{k:03d}.npz')
    for e in EXPS:
        rep[e] = compare(e, dict(np.load(fs[e])), dict(np.load(stored / e / f'shard_{k:03d}.npz')), pz)
    rep['status'] = 'PASS' if all(rep[e]['status'] == 'PASS' for e in EXPS) else 'FAIL'
    try:
        (root / 'summary').mkdir(parents=True, exist_ok=True); (root / 'summary/hardcheck_rerun.json').write_text(json.dumps(rep, indent=1))
        log('HARDCHECK', rep['status'], json.dumps({e: {x: rep[e].get(x) for x in ('rows_match', 'rank_equal_share', 'estimand_max_abs_diff', 'status', 'warn')} for e in EXPS}))
    except Exception as ex: print('WARN logging failed', repr(ex), flush=True)
    return rep


def save(f, d, meta):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.npz')
    np.savez(tmp, meta=np.array(json.dumps(meta, default=str)), **{k: v for k, v in d.items() if k != 'meta'}); os.replace(tmp, f)


def work(a):
    t0 = time.monotonic(); me = os.environ.get('SLURM_JOB_ID', f'local{os.getpid()}'); s11 = rg().s11
    budget = a.max_minutes or 38; left = s11.slurm_minutes_left()
    if left is not None and left - 6 < budget: budget = left - 6
    plan_ok(); k = a.check_shard
    us = gate_units(k) if a.gate else all_units(k)
    CL = ROOT / 'claims'; CL.mkdir(parents=True, exist_ok=True); C = None; last = {}; env = {}
    log(f'b2_cd work: job {me}, {"gate" if a.gate else "all"}, {sum(not out_path(u).exists() for u in us)} of {len(us)} units to do, budget {budget:.0f} min')
    for u in us:
        f = out_path(u)
        if f.exists(): continue
        if u[0] != 'check' and check(k=k)['status'] == 'FAIL': log('HARD CHECK FAILED - no new unit is run'); sys.exit(3)
        est = 1.5 * last.get(u[0], 120) / 60
        if C is not None and (time.monotonic() - t0) / 60 + est > budget: log('time budget reached before', u); break
        if not s11.claim(CL / '_'.join(map(str, u)), me): log('claimed by another job, skip', u); continue
        if f.exists(): continue
        if C is None:
            C = rg().GCtx(); env = dict(C.env, b2_cd_sha256=sha(__file__), addendum11_sha256=sha(PLAN))
        t1 = time.monotonic(); d = compute(C, u)            # a crash here is a code crash: job fails, chain stops
        try: chk = rg().unit_check(u[1] if u[0] == 'check' else u[0], d)
        except Exception as ex: chk = dict(status='WARN', note=repr(ex))
        save(f, d, dict(unit=list(u), created=time.strftime('%Y-%m-%dT%H:%M:%S'), check=chk, job=me, **env)); last[u[0]] = time.monotonic() - t1
        try: log(f'b2_cd {u[0]} {u[1]} shard {u[2]:03d} rows={len(d["row_id"])} {last[u[0]]:.0f}s total={(time.monotonic() - t0) / 60:.1f}min check', json.dumps(chk))
        except Exception as ex: print('WARN log failed', repr(ex), flush=True)
        if u[0] == 'check':
            rep = check(k=k)
            if rep['status'] == 'FAIL': log('HARD CHECK FAILED - stop'); sys.exit(3)
    rep = check(k=k)
    if rep['status'] == 'FAIL': sys.exit(3)
    remaining()


def remaining(a=None, root=None, cfg=None):
    miss = [u for u in all_units(cfg=cfg) if not out_path(u, root).exists()]
    print(f'REMAINING {len(miss)} of {len(all_units(cfg=cfg))}', json.dumps(['_'.join(map(str, u)) for u in miss]), flush=True); return miss


# ------------------------------------------------------------------ analysis (CPU)
def within_bin3(E, P, ppa, ppb, num, den, min_a, min_b):
    """bin-standardised numerator, denominator, ratio for a and b, and a - b; point and bootstrap."""
    xa = ppa[ppa[num].notna() & ppa[den].notna()]; xb = ppb[ppb[num].notna() & ppb[den].notna()]
    ba = P.citation_bin.reindex(xa.index).to_numpy(); bb = P.citation_bin.reindex(xb.index).to_numpy()
    bins = [b for b in sorted(set(ba) & set(bb)) if (ba == b).sum() >= min_a and (bb == b).sum() >= min_b]
    if not bins: return None
    w = np.array([(ba == b).sum() * (bb == b).sum() / ((ba == b).sum() + (bb == b).sum()) for b in bins]); w = w / w.sum()
    def std(x, bx):
        nu = de = 0.0; bn = bd = 0.0
        for wi, b in zip(w, bins):
            s = x[bx == b]; W = E.W(s.index.to_numpy()); c = W.sum(1)
            nu += wi * s[num].mean(); de += wi * s[den].mean()
            with np.errstate(invalid='ignore', divide='ignore'): bn = bn + wi * (W @ s[num].to_numpy()) / c; bd = bd + wi * (W @ s[den].to_numpy()) / c
        return nu, de, bn, bd
    na_, da_, bna, bda = std(xa, ba); nb_, db_, bnb, bdb = std(xb, bb)
    with np.errstate(invalid='ignore', divide='ignore'): rb = bna / bda - bnb / bdb
    return dict(num=(na_ - nb_, bna - bnb), den=(da_ - db_, bda - bdb), ratio=(na_ / da_ - nb_ / db_, rb), n_bins=len(bins),
                n_a=int(sum((ba == b).sum() for b in bins)), n_b=int(sum((bb == b).sum() for b in bins)))


def analyze(a=None, src=None, lists=None, out=None, rep_path=None):
    """src: {'stage11': {'patch': dir, 'knockout': dir}, 'new': {'patch': {g: dir}, 'knockout': {g: dir}}}"""
    import pandas as pd
    os.environ.setdefault('RERUN_OUT', str(G)); ra = load(H / '14_groups/rerun_analyze.py', 'rerun_analyze_b2cd')
    t0 = time.time(); out = Path(out or ROOT / 'summary'); out.mkdir(parents=True, exist_ok=True); rep_path = Path(rep_path or REP)
    src = src or {'stage11': {e: R11 / 'raw' / e for e in EXPS}, 'new': {e: {g: ROOT / 'raw' / e / g for g in LISTS} for e in EXPS}}
    lists = lists or {g: paper_list(g) for g in LISTS}
    P, tk, au, E = ra.setup(); X = ra.Est(P, E); plan = plan_ok(); warn = [] if plan else ['addendum 11 sha256 differs from its .sha256 file']
    smp11 = pd.read_parquet(R11 / 'config/sample.parquet')
    gs11 = {g: set(smp11.paper_id[P.grp.reindex(smp11.paper_id).to_numpy() == g]) for g in 'ABCD'}
    # data: Stage 11 originals (A, B, C36, D5) + new (C, D)
    d1 = ra.load_dir(src['stage11']['patch']); k1 = ra.load_dir(src['stage11']['knockout'])
    e1o, PL = ra.e1_tokens(d1, tk, au, P); e2o, KL = ra.e2_tokens(k1, e1o, tk, au, P)
    e1n, e2n = [], []
    for g in LISTS:
        dn = ra.load_dir(src['new']['patch'][g]); kn = ra.load_dir(src['new']['knockout'][g])
        if dn is None or kn is None: warn.append(f'no new raw data for group {g}'); continue
        b1_, _ = ra.e1_tokens(dn, tk, au, P); e1n.append(b1_); e2n.append(ra.e2_tokens(kn, b1_, tk, au, P)[0])
        miss = set(lists[g].paper_id) - set(b1_.paper_id)
        if miss: warn.append(f'{g}: {len(miss)} listed papers have no E1 rows (incomplete shards?)')
    e1n = pd.concat(e1n) if e1n else e1o.iloc[:0]; e2n = pd.concat(e2n) if e2n else e2o.iloc[:0]
    design = {'A': gs11['A'], 'B': gs11['B'], 'C': gs11['C'] | set(lists['C'].paper_id), 'D': gs11['D'] | set(lists['D'].paper_id),
              'C_stage11': gs11['C'], 'D_stage11': gs11['D']}
    overlap = {g: len(set(lists[g].paper_id) & gs11[g]) for g in LISTS}
    if any(overlap.values()): warn.append(f'new lists overlap the Stage 11 sample: {overlap}')
    tabs, rows, counts, boots = {}, [], [], {}
    for exp, base_o, base_n, LL in (('E1', e1o, e1n, PL), ('E2', e2o, e2n, KL)):
        base_all = pd.concat([base_o, base_n], ignore_index=True)
        for who in ra.WHO:
            for g, ids in design.items():
                b = base_all[base_all.paper_id.isin(ids)]
                cols = ['true', 'false'] + ([f'p{l}' for l in LL] if exp == 'E1' else [f'k{l}' for l in LL])
                pp = ra.paper_means(b, cols, who); pp['gap'] = pp['true'] - pp['false']
                lays = LL if exp == 'E1' else [l for l in LL if l != 64]
                for l in lays: pp[f'num{l}'] = pp[f'p{l}'] - pp['false'] if exp == 'E1' else pp['k64'] - pp[f'k{l}']
                tabs[(exp, who, g)] = pp
                src_lab = 'stage11' if g in ('A', 'B') or g.endswith('_stage11') else 'stage11+b2_new'
                for l in lays:
                    x = pp.dropna(subset=[f'num{l}', 'gap'])
                    if not len(x): continue
                    r_ = X.ratio(x, f'num{l}', 'gap'); n_ = X.mean(x, f'num{l}'); d_ = X.mean(x, 'gap')
                    boots[(exp, who, g, l)] = (n_[4], d_[4], r_[4])
                    rows.append(dict(experiment=exp, who=who, layer=l, item='recovery' if exp == 'E1' else 'loss', group=g, source=src_lab, n_papers=len(x),
                                     estimate=r_[0], lo=r_[1], hi=r_[2], numerator=n_[0], num_lo=n_[1], num_hi=n_[2], denominator=d_[0], den_lo=d_[1], den_hi=d_[2],
                                     descriptive_only=len(x) < 30))
                if who == 'unwritten':
                    counts.append(dict(experiment=exp, group=g, source=src_lab, design_papers=len(ids), papers_with_rows=b.paper_id.nunique(),
                                       papers_unwritten=int(pp.gap.notna().sum()), authors_unwritten=int(b[ra.WHO['unwritten'](b)].groupby(['paper_id', 'author_index']).ngroups),
                                       authors_written=int(b[ra.WHO['written'](b)].groupby(['paper_id', 'author_index']).ngroups),
                                       inconsistent_papers=int(b[b.consistent == False].paper_id.nunique())))   # noqa: E712
    GV = pd.DataFrame(rows); CN = pd.DataFrame(counts)
    # contrasts
    CON = [('C', 'A', 10, 10, 'within-bin (C >= 10, A >= 10 per bin)'), ('D', 'B', 1, 10, 'within-bin (D >= 1, B >= 10 per bin; descriptive)'),
           ('C', 'D', 1, 1, 'within-bin (>= 1 / >= 1; descriptive)')]
    crow = []
    for exp, LL in (('E1', PL), ('E2', [l for l in KL if l != 64])):
        for who in ('unwritten', 'unwritten_first', 'unwritten_other'):
            for ga, gb, mina, minb, lab in CON:
                pa, pb = tabs[(exp, who, ga)], tabs[(exp, who, gb)]
                for l in LL:
                    if (exp, who, ga, l) not in boots or (exp, who, gb, l) not in boots: continue
                    ra_ = GV[(GV.experiment == exp) & (GV.who == who) & (GV.layer == l) & (GV.group == ga)].iloc[0]
                    rb_ = GV[(GV.experiment == exp) & (GV.who == who) & (GV.layer == l) & (GV.group == gb)].iloc[0]
                    (an, ad, ar), (bn, bd, br) = boots[(exp, who, ga, l)], boots[(exp, who, gb, l)]
                    pl = dict(experiment=exp, who=who, layer=l, contrast=f'{ga} - {gb}', kind='plain difference', n_a=int(ra_.n_papers), n_b=int(rb_.n_papers),
                              n_bins=np.nan, min_a=np.nan, min_b=np.nan, ratio_diff=ra_.estimate - rb_.estimate, num_diff=ra_.numerator - rb_.numerator,
                              den_diff=ra_.denominator - rb_.denominator, p=E.pval(ar - br), descriptive_only=min(ra_.n_papers, rb_.n_papers) < 30 or ga == 'C' and gb == 'D')
                    pl['ratio_lo'], pl['ratio_hi'] = E.ci(ar - br); pl['num_lo'], pl['num_hi'] = E.ci(an - bn); pl['den_lo'], pl['den_hi'] = E.ci(ad - bd)
                    crow.append(pl)
                    wb = within_bin3(E, P, pa, pb, f'num{l}', 'gap', mina, minb)
                    if wb is None: continue
                    r = dict(experiment=exp, who=who, layer=l, contrast=f'{ga} - {gb}', kind=lab, n_a=wb['n_a'], n_b=wb['n_b'], n_bins=wb['n_bins'], min_a=mina, min_b=minb,
                             ratio_diff=wb['ratio'][0], num_diff=wb['num'][0], den_diff=wb['den'][0], p=E.pval(wb['ratio'][1]),
                             descriptive_only=min(wb['n_a'], wb['n_b']) < 30 or (ga, gb) != ('C', 'A'))
                    r['ratio_lo'], r['ratio_hi'] = E.ci(wb['ratio'][1]); r['num_lo'], r['num_hi'] = E.ci(wb['num'][1]); r['den_lo'], r['den_hi'] = E.ci(wb['den'][1])
                    crow.append(r)
    CC = pd.DataFrame(crow)
    COLS.write_csv(GV, COLS.CD_GROUP_VALUES, out / 'cd_group_values.csv'); COLS.write_csv(CC, COLS.CD_CONTRASTS, out / 'cd_contrasts.csv'); COLS.write_csv(CN, COLS.CD_COUNTS, out / 'cd_counts.csv')
    # consistency (WARN only): Stage 11-only groups reproduce the addendum-8 rerun_group_values.csv (same estimator, same draw)
    cons = 'not run'
    try:
        old = pd.read_csv(G / 'summary_rerun/rerun_group_values.csv'); old = old[old.group.isin(list('ABCD')) & old.experiment.isin(['E1', 'E2']) & (old.layer >= 0)]
        new = GV[(GV.group.isin(['A', 'B', 'C_stage11', 'D_stage11']))].assign(group=lambda x: x.group.str.replace('_stage11', ''))
        m = new.merge(old, on=['experiment', 'who', 'layer', 'group'], suffixes=('', '_old'))
        md = float(np.nanmax(np.abs(np.r_[m.estimate - m.estimate_old, m.lo - m.lo_old, m.hi - m.hi_old]))) if len(m) else np.nan
        cons = f'{len(m)} cells (A, B, C36, D5 x E1/E2 x author sets x layers) vs summary_rerun/rerun_group_values.csv: max |diff| (estimate, lo, hi) {md:.1e}'
        if not (md < 1e-9): warn.append(f'Stage 11-only groups differ from rerun_group_values.csv by {md:.2e} (threshold 1e-9; WARN)')
    except Exception as ex: warn.append(f'consistency check vs rerun_group_values.csv failed: {ex!r}')
    hc = None
    hf = ROOT / 'summary/hardcheck_rerun.json'
    if hf.exists() and src is not None: hc = json.loads(hf.read_text())
    report(GV, CC, CN, PL, KL, hc, cons, warn, rep_path, overlap)
    log(f'B2_CD ANALYZED in {time.time() - t0:.0f}s; warn={warn}'); return GV, CC, CN


def report(GV, CC, CN, PL, KL, hc, cons, warn, path, overlap):
    f = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' if np.isfinite(lo) else f'{e:+.3f}'
    L = ['# Addendum 11 B: groups C and D completed for Stage 11 E1 / E2', '',
         f'Written {time.strftime("%Y-%m-%d %H:%M")} by `14_groups/b2_cd.py analyze`. Plan: `381_stage13/config/prereg_addendum11.json` part B (sha256 {"OK" if plan_ok() else "MISMATCH - WARN"}). '
         'C = R1 x strong, D = R1 x fail (Stage 10 cohort, all papers); the Stage 11 sample papers of C (36) and D (5) are the stored Stage 11 runs, the others (475 / 29) are new runs '
         'through the addendum-8 driver (frozen s11.do_patch / do_knockout, unchanged). A, B = Stage 11 sample papers (stored runs). '
         'All values on UNWRITTEN authors (addendum 7); written authors = reference only. 95% team-cluster bootstrap (2,000, seed 391, one shared draw). n < 30 papers: descriptive only.', '']
    if hc:
        L += ['Hard check (re-run of Stage 11 shard {} through the driver vs stored): '.format(hc.get('shard')) +
              '; '.join(f'{e}: rows {hc[e]["rows_match"]}, rank equality {hc[e].get("rank_equal_share", float("nan")):.4f}, estimand max |diff| {hc[e].get("estimand_max_abs_diff", float("nan")):.1e}' for e in EXPS if e in hc) +
              f' (threshold {TOL}) -> **{hc["status"]}**.', '']
    L += [f'Consistency (WARN only): {cons}.', f'Overlap of the new lists with the Stage 11 sample: {overlap} (expected 0).', '']
    L += ['## Counts (unwritten authors)', '', '| exp | group | source | design papers | papers with rows | papers unwritten | authors unwritten | authors written | inconsistent papers |', '|---|---|---|---|---|---|---|---|---|']
    for r in CN.itertuples():
        L.append(f'| {r.experiment} | {r.group} | {r.source} | {r.design_papers} | {r.papers_with_rows} | {r.papers_unwritten} | {r.authors_unwritten} | {r.authors_written} | {r.inconsistent_papers} |')
    gs = ['A', 'B', 'C', 'D', 'C_stage11', 'D_stage11']
    def cell(exp, who, l, g, k='estimate'):
        r = GV[(GV.experiment == exp) & (GV.who == who) & (GV.layer == l) & (GV.group == g)]
        if not len(r): return 'n/a'
        r = r.iloc[0]; lo, hi = {'estimate': ('lo', 'hi'), 'numerator': ('num_lo', 'num_hi'), 'denominator': ('den_lo', 'den_hi')}[k]
        return f(r[k], r[lo], r[hi]) + (' (n<30)' if r.descriptive_only else '')
    for who in ('unwritten', 'unwritten_first', 'unwritten_other', 'written'):
        for exp, LL in (('E1', PL), ('E2', [l for l in KL if l != 64])):
            L += ['', f'## {exp} {"recovery R(l)" if exp == "E1" else "loss(l)"} - {who} authors{" (reference only)" if who == "written" else ""}', '',
                  '| layer | ' + ' | '.join(gs) + ' |', '|---|' + '---|' * len(gs)]
            for l in LL: L.append(f'| L{l} | ' + ' | '.join(cell(exp, who, l, g) for g in gs) + ' |')
    L += ['', '## Numerator / denominator (unwritten authors; selected layers)', '', '| exp | layer | group | n | numerator [CI] | denominator [CI] | ratio [CI] |', '|---|---|---|---|---|---|---|']
    for exp, LL in (('E1', [40, 48, 52, 56]), ('E2', [32, 40, 48, 52])):
        for l in LL:
            for g in ('A', 'B', 'C', 'D'):
                r = GV[(GV.experiment == exp) & (GV.who == 'unwritten') & (GV.layer == l) & (GV.group == g)]
                if len(r):
                    r = r.iloc[0]
                    L.append(f'| {exp} | L{l} | {g} | {r.n_papers}{" (n<30)" if r.descriptive_only else ""} | {f(r.numerator, r.num_lo, r.num_hi)} | {f(r.denominator, r.den_lo, r.den_hi)} | {f(r.estimate, r.lo, r.hi)} |')
    if len(CC):
        L += ['', '## Contrasts (unwritten authors; C - A primary for this item, D - B and C - D descriptive)', '',
              '| exp | layer | authors | contrast | kind | n_a / n_b (bins) | ratio diff [CI] | numerator diff [CI] | denominator diff [CI] |', '|---|---|---|---|---|---|---|---|---|']
        sel = CC[((CC.experiment == 'E1') & CC.layer.isin([40, 48, 52, 56])) | ((CC.experiment == 'E2') & CC.layer.isin([32, 40, 48, 52]))]
        for r in sel.itertuples():
            nb = '' if not np.isfinite(r.n_bins) else f' ({int(r.n_bins)})'
            L.append(f'| {r.experiment} | L{r.layer} | {r.who} | {r.contrast} | {r.kind} | {r.n_a} / {r.n_b}{nb}{" (descriptive)" if r.descriptive_only else ""} | '
                     f'{f(r.ratio_diff, r.ratio_lo, r.ratio_hi)} | {f(r.num_diff, r.num_lo, r.num_hi)} | {f(r.den_diff, r.den_lo, r.den_hi)} |')
    L += ['', 'Full tables: `391_groups/b2_cd/summary/cd_group_values.csv`, `cd_contrasts.csv`, `cd_counts.csv`.', '']
    L += ['## WARN', ''] + ([f'- {w}' for w in warn] or ['- none']) + ['']
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text('\n'.join(L) + '\n'); print('\n'.join(L[:12])); print('wrote', path)


# ------------------------------------------------------------------ hard-check unit test (CPU, stored data only)
def unittest(a=None):
    """identical -> PASS, perturbed -> FAIL, on stored Stage 11 shard 0 (no GPU)."""
    import tempfile
    res = {}
    with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR', '/tmp')) as td:
        root = Path(td)
        for e in EXPS:
            z = dict(np.load(R11 / 'raw' / e / 'shard_000.npz')); save(out_path(('check', e, 0), root), {k: v for k, v in z.items() if k != 'meta'}, {})
        res['identical -> PASS'] = check(root=root, k=0)['status'] == 'PASS'
        z = dict(np.load(out_path(('check', 'patch', 0), root))); rp = z['rank_patch'].copy(); i = list(z['layers']).index(48)
        rp[:, i] = np.maximum(1, (rp[:, i] * 3)); z['rank_patch'] = rp; save(out_path(('check', 'patch', 0), root), z, {})
        res['perturbed E1 (L48 ranks x3) -> FAIL'] = check(root=root, k=0)['status'] == 'FAIL'
        z['rank_patch'] = dict(np.load(R11 / 'raw/patch/shard_000.npz'))['rank_patch']; save(out_path(('check', 'patch', 0), root), z, {})
        zk = dict(np.load(out_path(('check', 'knockout', 0), root))); zk['row_id'] = zk['row_id'][::-1].copy(); save(out_path(('check', 'knockout', 0), root), zk, {})
        res['perturbed E2 (row order) -> FAIL'] = check(root=root, k=0)['status'] == 'FAIL'
    print('UNITTEST', json.dumps(res), flush=True); return all(res.values())


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU, 64-layer random Qwen3)
def tiny(a):
    import torch, transformers, jlens, pandas as pd
    global ROOT
    root = Path(a.root); root.mkdir(parents=True, exist_ok=True); cfg_t = root / 'config'; m = rg(); s10, s11 = m.s10, m.s11
    for f in list(LISTS.values()) + ['b2_cd_freeze.json']:
        p = cfg_t / f
        if p.exists(): os.chmod(p, 0o644); p.unlink()
    rec = freeze(cfg=cfg_t)                                                   # real freeze logic into the test root
    hfc = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
    hfc.num_hidden_layers = 64; hfc.hidden_size = 64; hfc.intermediate_size = 128; hfc.num_attention_heads = 4; hfc.num_key_value_heads = 2; hfc.head_dim = 16
    if hasattr(hfc, 'layer_types'): hfc.layer_types = hfc.layer_types[:64]
    torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(hfc, dtype=torch.float32).eval()
    C = type('T', (), {})(); C.torch = torch; C.tok = s10.tokenizer(); C.model = jlens.from_hf(hf, C.tok)
    C.papers, toks = s11.cohort(); C.ctx = s11.contexts_of(toks); C.P = C.papers.set_index('paper_id')
    C.prompts = {s11.FALSE_FOR_PATCH: s10.condition_prompts(R10, C.papers, s11.FALSE_FOR_PATCH)[0]}
    ok = {'freeze counts 475 / 29': rec['C']['new'] == 475 and rec['D']['new'] == 29, 'freeze shards 10 / 1': rec['C']['shards'] == 10 and rec['D']['shards'] == 1}
    # new units: 2 C papers of shard 0, 1 C paper of shard 9, 2 D papers (lists restricted in memory, real list files untouched)
    lists = {g: paper_list(g, cfg_t) for g in LISTS}
    small = {'C': pd.concat([lists['C'][lists['C'].shard == 0].head(2), lists['C'][lists['C'].shard == 9].head(1)]), 'D': lists['D'].head(2)}
    for g in LISTS:
        C.smp = small[g]
        for e in EXPS:
            for k in sorted(set(small[g].shard)): save(out_path((e, g, k), root), m.FUN[e](C, k), {'tiny': True})
    # 'stored Stage 11' analogue: 2 A + 2 B + 1 C sample papers of shard 0 via the frozen path, and the driver's check unit
    smp = pd.read_parquet(R11 / 'config/sample.parquet'); P = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'recall_level', 'mc_team_outcome_tight']).set_index('paper_id')
    grp = (P.recall_level + '_' + P.mc_team_outcome_tight).reindex(smp.paper_id).to_numpy()
    pick = pd.concat([smp[grp == 'R0_strong'].head(2), smp[grp == 'R0_fail'].head(2), smp[grp == 'R1_strong'].head(1)]); pick = pick.assign(shard=0)
    C.smp = pick
    for e in EXPS: save(root / 'stored' / e / 'shard_000.npz', m.FUN[e](C, 0), {'tiny': True})
    import shutil
    for e in EXPS: (root / 'check' / e).mkdir(parents=True, exist_ok=True); shutil.copy(root / 'stored' / e / 'shard_000.npz', out_path(('check', e, 0), root))
    C.smp = pick; d = m.FUN['patch'](C, 0)
    ok['driver re-run == stored (fp32 tiny, bit-identical)'] = bool(np.array_equal(d['rank_patch'], np.load(root / 'stored/patch/shard_000.npz')['rank_patch']))
    ok['hard check identical -> PASS'] = check(root=root, k=0, stored=root / 'stored')['status'] == 'PASS'
    z = dict(np.load(out_path(('check', 'patch', 0), root))); z['rank_patch'] = np.maximum(1, z['rank_patch'] * 7 + 3); save(out_path(('check', 'patch', 0), root), z, {})
    ok['hard check perturbed -> FAIL'] = check(root=root, k=0, stored=root / 'stored')['status'] == 'FAIL'
    shutil.copy(root / 'stored/patch/shard_000.npz', out_path(('check', 'patch', 0), root))
    # skip-if-exists + remaining + analysis on the tiny outputs
    mt = out_path(('patch', 'C', 0), root).stat().st_mtime
    ok['skip-if-exists (file untouched)'] = out_path(('patch', 'C', 0), root).stat().st_mtime == mt
    miss = remaining(root=root, cfg=cfg_t); ok['remaining lists the not-run shards'] = ('patch', 'C', 1) in miss and ('patch', 'C', 0) not in miss
    ROOT = root
    GV, CC, CN = analyze(src={'stage11': {e: root / 'stored' / e for e in EXPS}, 'new': {e: {g: root / 'raw' / e / g for g in LISTS} for e in EXPS}},
                         lists=small, out=root / 'summary', rep_path=root / 'reports/b2_cd_report.md')
    ok['analysis wrote group values A-D'] = {'A', 'B', 'C', 'D'} <= set(GV.group)
    r = GV[(GV.experiment == 'E1') & (GV.who == 'unwritten') & (GV.group == 'C')]
    ok['E1 L63 recovery == 1 (C, tiny)'] = bool(np.allclose(r[r.layer == 63].estimate, 1.0)) if len(r[r.layer == 63]) else False
    ok['csv columns from the column module'] = list(pd.read_csv(root / 'summary/cd_group_values.csv').columns) == COLS.CD_GROUP_VALUES
    ok = {k: bool(v) for k, v in ok.items()}; print('TINY CHECKS', json.dumps(ok), flush=True); return all(ok.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['freeze', 'tiny', 'work', 'check', 'remaining', 'analyze', 'unittest'])
    ap.add_argument('--gate', action='store_true'); ap.add_argument('--all', action='store_true'); ap.add_argument('--check-shard', type=int, default=0)
    ap.add_argument('--max-minutes', type=float); ap.add_argument('--root')
    a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'unittest': sys.exit(0 if unittest(a) else 1)
    if a.cmd == 'work' and a.gate == a.all: raise SystemExit('work needs exactly one of --gate / --all')
    r = {'freeze': freeze, 'work': work, 'check': check, 'remaining': remaining, 'analyze': analyze}[a.cmd](a)
    if a.cmd == 'check' and r['status'] != 'PASS': sys.exit(3)


if __name__ == '__main__':
    main()
