"""Addendum 16, items B (format lock) and D (name chain): pre-registered analysis (CPU, read-only on the raw data).

Plan (LOCKED): 391_groups/config/prereg_addendum16.md, sha256 c78daad0...; recorded deviations prereg_addendum16_deviations.md
(D16-1 .. D16-6, D16-4 timing correction, F4 control note, R0 correction; sha256 a1512fda...). Both checked at start.
Inputs (never modified): raw/a16_{B,D}/parsed/shard_KKK.parquet (frozen D16-4 parse rule, prereg16_a16.py reparse, script sha256
db7c7386...), raw/a16_{B,D}/tf/shard_KKK.parquet (teacher forcing), config/prereg16_sample_{B,D}.parquet (sha256-checked).

Interval method (plan section 1): archived author-team cluster bootstrap, 2,000 draws = groups_core.Engine (folds_own9108_k5s13
team ids, one multinomial draw over teams, seed 391, shared by every estimate of B AND D, so every difference is paired).
95% percentile intervals; two-sided percentile p = min(1, 2 min(share <= 0, share >= 0)), floor 1/2000.

Estimands
B (generation, paper level, true title): per condition c and outcome o: true match rate, chance match rate (same output vs the
  fixed control paper's authors), chance-corrected = mean over papers of (true - chance).
  Comparable outcomes (plan section 2): F1 ~ F0: >= 1 author (full matcher, any_full);
                                        F2 ~ F0: >= 1 surname (surname matcher, any_sur);
                                        F3, F4 ~ F0: first author's surname matched anywhere in the list (first_sur; D16-6;
                                        first-position version first_sur_pos1 beside it).
  Delta_g(c) = corrected_g(c) - corrected_g(F0) on that outcome (same papers); DiD(c) = Delta_A(c) - Delta_B(c).
  Decision: supported if for >= 1 c both Delta_A(c) > 0 and DiD(c) > 0 with Holm-adjusted 95% CIs excluding 0.
  Fabrication (beside every condition): share of papers with >= 1 generated item that matches no true author (full matcher
  for F0/F1, surname matcher for F2/F3/F4 and for the F0 comparison of F2-F4); if Delta fabrication_A(c) > Delta_A(c) the
  condition is flagged "not interpretable".
  Teacher forcing (descriptive): author score = mean log10(1/rank) of the author's tokens; paper score = mean over scored
  authors (F0/F1/F2 all authors, F3/F4 first author; group C: unwritten authors only); spec = true - mean(false_0..4);
  deleted-title version; first-author first-token log10(1/rank) and median rank.
D (teacher forcing): scored set authors k+1..n (group C: unwritten only); paper score as above.
  G_g(1) = score(P_true1) - score(P_other1), true title. Main: G_A(1), two-sided, Holm (one of the 5 tests).
  Secondary (descriptive): G_A(1) - G_B(1); G(2); title-specific (spec of P_true1 - spec of P_other1); deleted-title version;
  P_reverse vs forward; decomposition vs P_none; order checks (P_shuffle2, P_shuffle2x vs P_true2); generation check.
Multiplicity: Holm over 5 tests (B F1..F4, D). Each B condition is one test: intersection-union p_c = max(p(Delta_A), p(DiD))
  (both must be > 0). Holm step j (0-based, ascending p) uses level alpha/(5 - j); the "Holm-adjusted CI" of a test is the
  percentile interval at that level (step-down: a test after a non-rejection is not rejected). Bonferroni (alpha/5) CIs given
  beside.
Exploratory R0 check (not confirmatory): F0, R0 groups A and B, >= 1 correct author written, first author vs co-author only,
  chance control, team CI.
Outputs: 391_groups/summary_a16_20261115/*.csv + report.md (+ meta.json).
Usage: prereg16_analyze_20261115.py [--shards-B 0,1] [--shards-D 0,1] [--out DIR] [--allow-missing]
"""
import argparse, glob, hashlib, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens'); G = BASE / '391_groups'; CFG = G / 'config'
R10 = BASE / '351_stage10'
PREREG_SHA = 'c78daad08f77080e7dd49c84c2501f9ca31b1195ab9e38364e3c3bab9243e66a'
DEV_SHA = 'a1512fdae33b4a841afc99b8424cb3c28169b9bd81f3992db7ba6c6b6eb5049b'
SCRIPT16_SHA = 'db7c7386359522500cd128aeb1fe0e6b3a70d06bbb25b76d5916069963208449'
ALPHA, M_TESTS = 0.05, 5
TITLES = ['true'] + [f'false_{k}' for k in range(5)] + ['delete']
FMTS = ['F0', 'F1', 'F2', 'F3', 'F4']
DCONDS = ['P_true1', 'P_true2', 'P_other1', 'P_other2', 'P_none', 'P_shuffle2', 'P_shuffle2x', 'P_reverse']
sys.path.insert(0, str(H / '14_groups'))
WARN = []


def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def warn(m): WARN.append(m); log('WARN', m)


# ------------------------------------------------------------------ bootstrap
class Boot:
    def __init__(self):
        import groups_core as gc
        P = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id']).set_index('paper_id')
        self.E = gc.Engine(P); self.NB = gc.NB; self.pval = gc.Engine.pval

    def mean(self, pids, v):
        """paper-level mean with nan skipped -> (est, boot[NB], n)."""
        v = np.asarray(v, float); m = ~np.isnan(v); v0 = np.where(m, v, 0.0); W = self.E.W(list(pids))
        with np.errstate(invalid='ignore', divide='ignore'):
            return (v0.sum() / m.sum() if m.sum() else np.nan), (W @ v0) / (W @ m), int(m.sum())

    @staticmethod
    def ci(b, level=0.95):
        b = b[np.isfinite(b)]
        if len(b) < 0.5 * 2000: return (np.nan, np.nan)
        a = (1 - level) / 2 * 100; return tuple(np.percentile(b, [a, 100 - a]))


def row(B, est, boot, n, **kw):
    lo, hi = B.ci(boot); return dict(**kw, est=est, lo=lo, hi=hi, p=B.pval(boot), n=n, descriptive_only=bool(n < 30))


# ------------------------------------------------------------------ loading + checks
def load_item(item, shards, allow_missing):
    s = pd.read_parquet(CFG / f'prereg16_sample_{item}.parquet')
    ref = Path(str(CFG / f'prereg16_sample_{item}.parquet') + '.sha256').read_text().split()[0]
    if sha(CFG / f'prereg16_sample_{item}.parquet') != ref: raise SystemExit(f'SAMPLE CHANGED {item}')
    want = sorted(s.shard.unique()) if shards is None else shards
    have = [k for k in want if (G / f'raw/a16_{item}/parsed/shard_{k:03d}.parquet').exists() and (G / f'raw/a16_{item}/tf/shard_{k:03d}.parquet').exists()]
    miss = sorted(set(want) - set(have))
    if miss:
        if not allow_missing: raise SystemExit(f'{item}: missing parsed/tf shards {miss}')
        warn(f'{item}: missing shards {miss} (allowed; partial run)')
    par = pd.concat([pd.read_parquet(G / f'raw/a16_{item}/parsed/shard_{k:03d}.parquet') for k in have], ignore_index=True)
    tf = pd.concat([pd.read_parquet(G / f'raw/a16_{item}/tf/shard_{k:03d}.parquet') for k in have], ignore_index=True)
    # consistency: parsed (frozen reparse) vs the scoring stored at generation time (same script for shards run with db7c...)
    chk = []
    for k in have:
        m = json.loads((G / f'raw/a16_{item}/meta_v2/shard_{k:03d}.json').read_text())
        g = pd.read_parquet(G / f'raw/a16_{item}/gen_v2/shard_{k:03d}.parquet')
        p = pd.read_parquet(G / f'raw/a16_{item}/parsed/shard_{k:03d}.parquet')
        cols = [c for c in p.columns if c in g.columns and c not in ('paper_id', 'grp', 'cond')]
        j = p.merge(g[['paper_id', 'cond'] + cols], on=['paper_id', 'cond'], suffixes=('', '_g'))
        diff = int(sum((j[c].astype(str) != j[c + '_g'].astype(str)).sum() for c in cols))
        chk.append(dict(item=item, shard=k, gen_script=m['script_sha256'][:12], rows=len(p), cells_differing_parsed_vs_gen=diff,
                        parity=';'.join(f"{c}:{v.get('status', '')[:4]}" for c, v in m.get('parity_vs_stage10', {}).items()),
                        batch_vs_single=m.get('gen_batch_vs_single_identical')))
        if m['script_sha256'] == SCRIPT16_SHA and diff: warn(f'{item} shard {k}: parsed differs from gen_v2 in {diff} cells although same script')
    s = s[s.shard.isin(have)].reset_index(drop=True)
    return s, par, tf, pd.DataFrame(chk)


def paper_tf(tf, keys, c_unwritten, grp_of):
    """token -> author score (mean nlr) -> paper score (mean over scored authors); group C: unwritten authors only."""
    t = tf.copy(); t['nlr'] = -np.log10(t['rank'].astype(float))
    if c_unwritten: t = t[~(t.paper_id.map(grp_of).eq('C') & t.written)]
    a = t.groupby(keys + ['author_index'], sort=False).nlr.mean().reset_index()
    p = a.groupby(keys, sort=False).nlr.mean()
    return p


# ------------------------------------------------------------------ B
B_OUT = {  # outcome name -> (true column, chance column)
    'any_full': ('any_full', 'c_any_full'), 'first_full': ('first_full', 'c_first_full'),
    'any_sur': ('any_sur', 'c_any_sur'), 'first_sur': ('first_sur', 'c_first_sur'), 'first_sur_pos1': ('first_sur_pos1', 'c_first_sur_pos1')}
MAIN_OUT = {'F1': 'any_full', 'F2': 'any_sur', 'F3': 'first_sur', 'F4': 'first_sur'}
FAB_MATCH = {'F1': 'full', 'F2': 'sur', 'F3': 'sur', 'F4': 'sur'}


def b_analysis(B, s, par, tf):
    S = s.set_index('paper_id'); par = par.copy()
    par['fab_any_full'] = (par.n_fab_full > 0).astype(float); par['fab_any_sur'] = (par.n_fab_sur > 0).astype(float)
    par['fab_share_full'] = np.where(par.n_items > 0, par.n_fab_full / par.n_items.clip(lower=1), np.nan)
    par['fab_share_sur'] = np.where(par.n_items > 0, par.n_fab_sur / par.n_items.clip(lower=1), np.nan)
    par['empty'] = (par.n_items == 0).astype(float)
    if par.duplicated(['paper_id', 'cond']).any(): raise SystemExit('duplicate paper x cond in B parsed')
    wide = {c: par[par.cond == c].set_index('paper_id').reindex(s.paper_id) for c in FMTS}
    for c in FMTS:
        if wide[c].n_items.isna().any(): warn(f'B {c}: {int(wide[c].n_items.isna().sum())} papers without output')
    rates, main, fab, split = [], [], [], []
    groups = [('A', s.grp == 'A'), ('B', s.grp == 'B'), ('C', s.grp == 'C'), ('all', s.grp.notna())]
    fat = [('all', s.fa_type.notna()), ('initial_first', s.fa_type == 'initial_first'), ('given_first', s.fa_type == 'given_first')]
    # rates per group x fa_type x condition x outcome
    for gname, gm in groups:
        for fname, fm in fat:
            sel = (gm & fm).to_numpy(); pids = s.paper_id[sel]
            for c in FMTS:
                w = wide[c][sel]
                for o, (tc, cc) in B_OUT.items():
                    t = w[tc].astype(float).to_numpy(); ch = w[cc].astype(float).to_numpy()
                    e1, b1, n = B.mean(pids, t); e2, b2, _ = B.mean(pids, ch); e3, b3, _ = B.mean(pids, t - ch)
                    r = dict(group=gname, fa_type=fname, cond=c, outcome=o, n=n, descriptive_only=bool(n < 30), true=e1, chance=e2, corrected=e3)
                    r['true_lo'], r['true_hi'] = B.ci(b1); r['chance_lo'], r['chance_hi'] = B.ci(b2); r['corr_lo'], r['corr_hi'] = B.ci(b3)
                    rates.append(r)
                for fc in ['fab_any_full', 'fab_any_sur', 'fab_share_full', 'fab_share_sur', 'empty', 'n_items']:
                    e, b, n = B.mean(pids, w[fc].astype(float).to_numpy()); lo, hi = B.ci(b)
                    fab.append(dict(group=gname, fa_type=fname, cond=c, measure=fc, est=e, lo=lo, hi=hi, n=n, descriptive_only=bool(n < 30)))
    # main comparisons (Delta, DiD) + the same within fa_type (descriptive)
    boots = {}
    for fname, fm in fat:
        for c, o in list(MAIN_OUT.items()) + [('F3', 'first_sur_pos1'), ('F4', 'first_sur_pos1'), ('F1', 'first_full'), ('F2', 'first_sur')]:
            tc, cc = B_OUT[o]
            dd = {}
            for gname, gm in groups[:3]:
                sel = (gm & fm).to_numpy(); pids = s.paper_id[sel]
                v = (wide[c][tc].astype(float) - wide[c][cc].astype(float) - (wide['F0'][tc].astype(float) - wide['F0'][cc].astype(float))).to_numpy()[sel]
                e, b, n = B.mean(pids, v); dd[gname] = (e, b, n)
                fmatch = FAB_MATCH[c]; fv = (wide[c][f'fab_any_{fmatch}'] - wide['F0'][f'fab_any_{fmatch}']).to_numpy()[sel]
                ef, bf, _ = B.mean(pids, fv)
                r = row(B, e, b, n, fa_type=fname, cond=c, outcome=o, contrast=f'Delta_{gname}', primary=(fname == 'all' and MAIN_OUT[c] == o))
                r['fab_delta'] = ef; r['fab_delta_lo'], r['fab_delta_hi'] = B.ci(bf); main.append(r)
                if fname == 'all' and MAIN_OUT[c] == o: boots[(c, gname)] = b; boots[(c, gname, 'fab')] = bf
            e = dd['A'][0] - dd['B'][0]; b = dd['A'][1] - dd['B'][1]
            main.append(row(B, e, b, min(dd['A'][2], dd['B'][2]), fa_type=fname, cond=c, outcome=o, contrast='DiD_A-B', primary=(fname == 'all' and MAIN_OUT[c] == o)))
            if fname == 'all' and MAIN_OUT[c] == o: boots[(c, 'DiD')] = b
    # teacher forcing
    grp_of = S.grp.to_dict()
    ps = paper_tf(tf, ['paper_id', 'cond', 'title_cond'], True, grp_of).unstack('title_cond')
    t0 = tf[(tf.author_index == 0) & (tf.token_index == 0)].copy(); t0['nlr'] = -np.log10(t0['rank'].astype(float))
    ft = t0.set_index(['paper_id', 'cond', 'title_cond']).nlr.unstack('title_cond')
    fr = t0.set_index(['paper_id', 'cond', 'title_cond'])['rank'].unstack('title_cond')
    tfr = []
    for gname, gm in groups:
        for fname, fm in fat:
            sel = (gm & fm).to_numpy(); pids_all = s.paper_id[sel]
            for c in FMTS:
                for lab, X in (('all_tokens', ps), ('first_author_first_token', ft)):
                    x = X.xs(c, level='cond').reindex(pids_all)
                    meas = {'true': x['true'], 'false_mean': x[[f'false_{k}' for k in range(5)]].mean(1), 'delete': x['delete']}
                    meas['spec'] = meas['true'] - meas['false_mean']; meas['true_minus_delete'] = meas['true'] - meas['delete']
                    for mname, v in meas.items():
                        e, b, n = B.mean(pids_all, v.to_numpy()); lo, hi = B.ci(b)
                        tfr.append(dict(group=gname, fa_type=fname, cond=c, score=lab, measure=mname, est=e, lo=lo, hi=hi, n=n, descriptive_only=bool(n < 30)))
                r = fr.xs(c, level='cond').reindex(pids_all)['true']
                tfr.append(dict(group=gname, fa_type=fname, cond=c, score='first_author_first_token', measure='median_rank_true', est=float(np.nanmedian(r)) if r.notna().any() else np.nan,
                                lo=np.nan, hi=np.nan, n=int(r.notna().sum()), descriptive_only=bool(r.notna().sum() < 30)))
                tfr.append(dict(group=gname, fa_type=fname, cond=c, score='first_author_first_token', measure='share_rank_le5_true', est=float((r <= 5).mean()) if r.notna().any() else np.nan,
                                lo=np.nan, hi=np.nan, n=int(r.notna().sum()), descriptive_only=bool(r.notna().sum() < 30)))
    return pd.DataFrame(rates), pd.DataFrame(main), pd.DataFrame(fab), pd.DataFrame(tfr), boots


# ------------------------------------------------------------------ D
def d_analysis(B, s, par, tf):
    S = s.set_index('paper_id'); grp_of = S.grp.to_dict()
    ps = paper_tf(tf, ['paper_id', 'cond', 'title_cond'], True, grp_of).unstack('title_cond')
    fm = [f'false_{k}' for k in range(5)]
    def score(cond, version, pids, scored_from=None):
        x = ps.xs(cond, level='cond').reindex(pids)
        if version == 'true': return x['true'].to_numpy()
        if version == 'delete': return x['delete'].to_numpy()
        if version == 'false_mean': return x[fm].mean(1).to_numpy()
        if version == 'spec': return (x['true'] - x[fm].mean(1)).to_numpy()
        if version == 'true_minus_delete': return (x['true'] - x['delete']).to_numpy()
    # P_none restricted to the scored sets (2..n for k = 1, 3..n for k = 2) for the decomposition
    t = tf[tf.cond == 'P_none']
    none_k = {}
    for k in (1, 2):
        tt = t[t.author_index >= k].assign(cond=f'P_none_from{k + 1}')
        none_k[k] = paper_tf(tt, ['paper_id', 'cond', 'title_cond'], True, grp_of).unstack('title_cond')
    tt = t[t.author_index == 0].assign(cond='P_none_first'); none_first = paper_tf(tt, ['paper_id', 'cond', 'title_cond'], True, grp_of).unstack('title_cond')
    ps = pd.concat([ps, none_k[1], none_k[2], none_first])
    # first scored author's first token (author index k) version
    t1 = tf[tf.token_index == 0].copy(); t1['nlr'] = -np.log10(t1['rank'].astype(float))
    firsttok = {}
    for cond, k in (('P_true1', 1), ('P_other1', 1), ('P_true2', 2), ('P_other2', 2), ('P_none', 1)):
        firsttok[cond] = t1[(t1.cond == cond) & (t1.author_index == k)].set_index(['paper_id', 'title_cond']).nlr.unstack()
    groups = [('A', s.grp == 'A'), ('B', s.grp == 'B'), ('C', s.grp == 'C'), ('all', s.grp.notna())]
    fat = [('all', s.fa_type.notna()), ('initial_first', s.fa_type == 'initial_first'), ('given_first', s.fa_type == 'given_first')]
    CONTR = [  # name, cond_a, cond_b
        ('G1', 'P_true1', 'P_other1'), ('G2', 'P_true2', 'P_other2'),
        ('true1_minus_none', 'P_true1', 'P_none_from2'), ('other1_minus_none', 'P_other1', 'P_none_from2'),
        ('true2_minus_none', 'P_true2', 'P_none_from3'), ('other2_minus_none', 'P_other2', 'P_none_from3'),
        ('shuffle2_minus_true2', 'P_shuffle2', 'P_true2'), ('shuffle2x_minus_true2', 'P_shuffle2x', 'P_true2'),
        ('reverse_minus_none_first', 'P_reverse', 'P_none_first')]
    rows, levels, boots = [], [], {}
    for fname, fmk in fat:
        gb = {}
        for gname, gm in groups:
            sel = (gm & fmk).to_numpy(); pids = s.paper_id[sel]
            for version in ['true', 'spec', 'delete', 'true_minus_delete', 'false_mean']:
                for cname, ca, cb in CONTR:
                    v = score(ca, version, pids) - score(cb, version, pids)
                    e, b, n = B.mean(pids, v); r = row(B, e, b, n, group=gname, fa_type=fname, version=version, contrast=cname, score='all_tokens')
                    r['primary'] = (gname == 'A' and fname == 'all' and version == 'true' and cname == 'G1'); r['low_power_C'] = gname == 'C'
                    rows.append(r); gb[(gname, version, cname)] = (e, b, n)
                if fname == 'all':
                    for cond in DCONDS + ['P_none_from2', 'P_none_from3', 'P_none_first']:
                        e, b, n = B.mean(pids, score(cond, version, pids)); lo, hi = B.ci(b)
                        levels.append(dict(group=gname, version=version, cond=cond, est=e, lo=lo, hi=hi, n=n))
            for cname, ca, cb in (('G1', 'P_true1', 'P_other1'), ('G2', 'P_true2', 'P_other2'), ('true1_minus_none', 'P_true1', 'P_none')):
                for version in ['true', 'spec']:
                    xa = firsttok[ca].reindex(pids); xb = firsttok[cb].reindex(pids)
                    f = (lambda x: x['true']) if version == 'true' else (lambda x: x['true'] - x[fm].mean(1))
                    e, b, n = B.mean(pids, (f(xa) - f(xb)).to_numpy())
                    rows.append(row(B, e, b, n, group=gname, fa_type=fname, version=version, contrast=cname, score='first_scored_author_first_token', primary=False, low_power_C=gname == 'C'))
        for version in ['true', 'spec', 'delete', 'true_minus_delete']:
            for cname in ['G1', 'G2', 'reverse_minus_none_first', 'true1_minus_none']:
                for ga, gbn in (('A', 'B'), ('C', 'A')):
                    a, b_ = gb[(ga, version, cname)], gb[(gbn, version, cname)]
                    rows.append(row(B, a[0] - b_[0], a[1] - b_[1], min(a[2], b_[2]), group=f'{ga}-{gbn}', fa_type=fname, version=version, contrast=cname, score='all_tokens',
                                    primary=False, low_power_C=ga == 'C'))
        if fname == 'all': boots['G_A1'] = gb[('A', 'true', 'G1')][1]
    # reverse vs forward (A): reverse gain (author 1 | authors 2..n vs none) - forward gain (authors 2..n | author 1 vs none)
    return pd.DataFrame(rows), pd.DataFrame(levels), boots


def d_gen(B, s, par):
    par = par.copy(); par['recall_rest'] = par.n_rest_full / par.n_rest; par['any_rest_sur'] = (par.n_rest_sur > 0).astype(float)
    par['recall_rest_sur'] = par.n_rest_sur / par.n_rest; par['fab_any'] = (par.n_fab_full > 0).astype(float); par['any_rest_full'] = par.any_rest_full.astype(float)
    w = {c: par[par.cond == c].set_index('paper_id').reindex(s.paper_id) for c in ['G_true1', 'G_other1']}
    out = []
    for gname, gm in [('A', s.grp == 'A'), ('B', s.grp == 'B'), ('C', s.grp == 'C'), ('all', s.grp.notna())]:
        sel = gm.to_numpy(); pids = s.paper_id[sel]
        for m in ['any_rest_full', 'recall_rest', 'any_rest_sur', 'recall_rest_sur', 'fab_any', 'n_items']:
            a = w['G_true1'][m].astype(float).to_numpy()[sel]; b = w['G_other1'][m].astype(float).to_numpy()[sel]
            for lab, v in (('G_true1', a), ('G_other1', b), ('true1_minus_other1', a - b)):
                e, bb, n = B.mean(pids, v); out.append(row(B, e, bb, n, group=gname, measure=m, cond=lab, low_power_C=gname == 'C'))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ D16-5 control exclusion share
def d16_5(sB, sD):
    import importlib.util
    sp = importlib.util.spec_from_file_location('a16', H / '14_groups/prereg16_a16.py'); a16 = importlib.util.module_from_spec(sp); sp.loader.exec_module(a16)
    if sha(H / '14_groups/prereg16_a16.py') != SCRIPT16_SHA: warn('prereg16_a16.py sha differs from D16-4 record')
    p = pd.read_parquet(R10 / 'cohort/papers.parquet')
    p['alist'] = p.authors.map(a16.authors_of); p['surnames'] = p.alist.map(lambda L: {a16.words(a)[-1] for a in L if a16.words(a)})
    p['fa_init'] = p.alist.map(lambda L: a16.init_norm(L[0]) if L else '')
    P = p.set_index('paper_id', drop=False); byf = {f: g for f, g in p.groupby('field')}
    out = []
    for item, s, rules in (('B', sB, ['ctrl', 'ctrl_f4']), ('D', sD, ['ctrl'])):
        for r in s.itertuples():
            row_ = P.loc[r.paper_id]; c = byf[row_.field]; c = c[c.paper_id != r.paper_id]
            share = c.surnames.map(lambda x: bool(x & row_.surnames))
            for rule in rules:
                pool = (c.n_authors_listed - row_.n_authors_listed).abs() <= 1 if rule == 'ctrl' else (c.fa_init == row_.fa_init)
                cid = r.ctrl_paper_id if rule == 'ctrl' else r.ctrl_f4_paper_id
                out.append(dict(item=item, rule=rule, paper_id=r.paper_id, grp=r.grp, n_pool=int(pool.sum()), n_excluded=int((pool & share).sum()),
                                chosen_shares_surname=bool(P.loc[cid, 'surnames'] & row_.surnames)))
    d = pd.DataFrame(out); d['share_excluded'] = d.n_excluded / d.n_pool.clip(lower=1)
    summ = d.groupby(['item', 'rule', 'grp']).agg(papers=('paper_id', 'size'), mean_share_excluded=('share_excluded', 'mean'),
                                                  pooled_share_excluded=('n_excluded', 'sum'), pool=('n_pool', 'sum'),
                                                  papers_with_any_excluded=('n_excluded', lambda x: float((x > 0).mean())),
                                                  chosen_control_shares_surname=('chosen_shares_surname', 'sum')).reset_index()
    summ['pooled_share_excluded'] = summ.pooled_share_excluded / summ.pool
    tot = d.groupby(['item', 'rule']).agg(papers=('paper_id', 'size'), mean_share_excluded=('share_excluded', 'mean'),
                                          pooled_share_excluded=('n_excluded', 'sum'), pool=('n_pool', 'sum'),
                                          papers_with_any_excluded=('n_excluded', lambda x: float((x > 0).mean())),
                                          chosen_control_shares_surname=('chosen_shares_surname', 'sum')).reset_index().assign(grp='all')
    tot['pooled_share_excluded'] = tot.pooled_share_excluded / tot.pool
    return pd.concat([summ, tot], ignore_index=True)


# ------------------------------------------------------------------ R0 (exploratory)
def r0(B, s, par):
    d = par[par.cond == 'F0'].set_index('paper_id').reindex(s.paper_id)
    d['any_fs'] = d.any_full | d.any_sur; d['first_fs'] = d.first_full | d.first_sur; d['co_only_fs'] = d.any_fs & ~d.first_fs
    d['co_only_full'] = d.any_full & ~d.first_full; d['c_any_fs'] = d.c_any_full | d.c_any_sur
    d['corr_any_full'] = d.any_full.astype(float) - d.c_any_full.astype(float); d['corr_any_fs'] = d.any_fs.astype(float) - d.c_any_fs.astype(float)
    out = []
    for gname, gm in [('A', s.grp == 'A'), ('B', s.grp == 'B'), ('A+B (R0)', s.grp.isin(['A', 'B'])), ('C (R1, reference)', s.grp == 'C')]:
        for fname, fm in [('all', s.fa_type.notna()), ('initial_first', s.fa_type == 'initial_first'), ('given_first', s.fa_type == 'given_first')]:
            sel = (gm & fm).to_numpy(); pids = s.paper_id[sel]
            for m in ['any_full', 'first_full', 'co_only_full', 'c_any_full', 'corr_any_full', 'any_fs', 'first_fs', 'co_only_fs', 'c_any_fs', 'corr_any_fs']:
                e, b, n = B.mean(pids, d[m].astype(float).to_numpy()[sel])
                out.append(row(B, e, b, n, group=gname, fa_type=fname, measure=m))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ Holm
def holm(B, bootsB, mainB, bootsD):
    tests = []
    for c in ['F1', 'F2', 'F3', 'F4']:
        pa, pd_ = B.pval(bootsB[(c, 'A')]), B.pval(bootsB[(c, 'DiD')])
        tests.append(dict(test=f'B_{c}', p_DeltaA=pa, p_DiD=pd_, p=max(pa, pd_)))
    tests.append(dict(test='D_GA1', p=B.pval(bootsD['G_A1'])))
    t = pd.DataFrame(tests).sort_values('p', kind='stable').reset_index(drop=True)
    t['holm_step'] = np.arange(len(t)); t['level'] = ALPHA / (M_TESTS - t.holm_step)
    t['p_holm'] = np.minimum(1, np.maximum.accumulate((M_TESTS - t.holm_step) * t.p))
    cont = True; rej = []
    for r in t.itertuples():
        ok = cont and r.p <= r.level
        rej.append(ok); cont = ok
    t['rejected_holm'] = rej
    out = []
    for r in t.itertuples():
        lvl = 1 - r.level
        if r.test.startswith('B_'):
            c = r.test[2:]
            items = [('Delta_A', bootsB[(c, 'A')], mainB.query("primary and contrast=='Delta_A' and cond==@c").est.iloc[0]),
                     ('DiD_A-B', bootsB[(c, 'DiD')], mainB.query("primary and contrast=='DiD_A-B' and cond==@c").est.iloc[0])]
        else:
            items = [('G_A(1)', bootsD['G_A1'], np.nanmean(bootsD['G_A1']) * np.nan)]
        for nm, b, e in items:
            lo, hi = B.ci(b, lvl); blo, bhi = B.ci(b, 1 - ALPHA / M_TESTS); ulo, uhi = B.ci(b)
            out.append(dict(test=r.test, quantity=nm, est=e, ci95_lo=ulo, ci95_hi=uhi, holm_level=r.level, holm_ci_lo=lo, holm_ci_hi=hi,
                            bonf_ci_lo=blo, bonf_ci_hi=bhi, p_raw=B.pval(b), p_test=r.p, p_holm=r.p_holm, holm_step=r.holm_step, rejected_holm=r.rejected_holm))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ report
def f3(x): return 'nan' if pd.isna(x) else f'{x:+.3f}'


def report(out, res, meta):
    L = []; P = L.append
    hl, mB, rB, fB, tB, dC, dL, dG, ex, r0d = (res[k] for k in ['holm', 'b_main', 'b_rates', 'b_fab', 'b_tf', 'd_contrasts', 'd_levels', 'd_gen', 'd16_5', 'r0'])
    P('# Addendum 16, items B (output format) and D (name chain): pre-registered analysis')
    P(''); P(f"Run {meta['created']} (job {meta.get('job')}); plan sha256 {PREREG_SHA[:8]}... (verified), deviations sha256 {DEV_SHA[:8]}... (verified). "
             f"B: {meta['B_papers']} papers / shards {meta['B_shards']}; D: {meta['D_papers']} papers / shards {meta['D_shards']}. "
             'Intervals: archived author-team cluster bootstrap, 2,000 draws, one shared draw for B and D (groups_core.Engine, seed 391). NOT PUBLISHED.')
    if WARN: P(''); P('WARN: ' + ' | '.join(WARN))
    P(''); P('## 1. Confirmatory tests (Holm over 5)')
    P(''); P('| test | quantity | estimate | 95% CI | Holm level | Holm-adj. CI | Bonferroni (0.01) CI | p (test) | p Holm | rejected |'); P('|---|---|---|---|---|---|---|---|---|---|')
    for r in hl.itertuples():
        P(f'| {r.test} | {r.quantity} | {f3(r.est)} | [{f3(r.ci95_lo)}, {f3(r.ci95_hi)}] | {r.holm_level:.4f} | [{f3(r.holm_ci_lo)}, {f3(r.holm_ci_hi)}] | '
          f'[{f3(r.bonf_ci_lo)}, {f3(r.bonf_ci_hi)}] | {r.p_test:.4f} | {r.p_holm:.4f} | {r.rejected_holm} |')
    P(''); P('Verdicts:')
    for line in meta['verdicts']: P(f'- {line}')
    P(''); P('## 2. B: rates per condition (true, chance, true - chance), all papers of each group')
    for o in ['any_full', 'any_sur', 'first_sur', 'first_sur_pos1', 'first_full']:
        P(''); P(f'### outcome {o}'); P(''); P('| group | cond | n | true | chance | true - chance [95% CI] |'); P('|---|---|---|---|---|---|')
        for r in rB[(rB.fa_type == 'all') & (rB.outcome == o) & (rB.group != 'all')].itertuples():
            P(f'| {r.group} | {r.cond} | {r.n} | {r.true:.3f} | {r.chance:.3f} | {f3(r.corrected)} [{f3(r.corr_lo)}, {f3(r.corr_hi)}] |')
    P(''); P('## 3. B: Delta (condition - F0, chance-corrected) and DiD A - B, with fabrication change (interpretability rule)')
    P(''); P('| fa_type | cond | outcome | contrast | estimate [95% CI] | n | fabrication change [95% CI] | flag |'); P('|---|---|---|---|---|---|---|---|')
    for r in mB.itertuples():
        flag = ''
        if r.contrast.startswith('Delta') and not pd.isna(r.fab_delta) and r.fab_delta > 0 and r.fab_delta > r.est: flag = 'fabrication rises more than recall -> not interpretable'
        if r.descriptive_only: flag += ' n<30 descriptive'
        fd = '' if pd.isna(r.fab_delta) else f'{f3(r.fab_delta)} [{f3(r.fab_delta_lo)}, {f3(r.fab_delta_hi)}]'
        P(f"| {r.fa_type} | {r.cond} | {r.outcome}{' (primary)' if r.primary else ''} | {r.contrast} | {f3(r.est)} [{f3(r.lo)}, {f3(r.hi)}] | {r.n} | {fd} | {flag} |")
    P(''); P('## 4. B: fabrication beside every condition (share of papers with >= 1 unmatched item; empty-answer share)')
    P(''); P('| group | cond | fab_any_full | fab_any_sur | empty | mean items |'); P('|---|---|---|---|---|---|')
    for g in ['A', 'B', 'C']:
        for c in FMTS:
            x = fB[(fB.group == g) & (fB.fa_type == 'all') & (fB.cond == c)].set_index('measure').est
            P(f'| {g} | {c} | {x["fab_any_full"]:.3f} | {x["fab_any_sur"]:.3f} | {x["empty"]:.3f} | {x["n_items"]:.2f} |')
    P(''); P('## 5. B: first-token-type split (descriptive; chance-corrected rate on the comparable outcome)')
    P(''); P('| group | fa_type | n | F0 any_full | F1 any_full | F0 any_sur | F2 any_sur | F0 first_sur | F3 first_sur | F4 first_sur |'); P('|---|---|---|---|---|---|---|---|---|---|')
    for g in ['A', 'B', 'C']:
        for ft in ['initial_first', 'given_first']:
            x = rB[(rB.group == g) & (rB.fa_type == ft)].set_index(['cond', 'outcome']).corrected; n = rB[(rB.group == g) & (rB.fa_type == ft)].n.iloc[0]
            P(f"| {g} | {ft} | {n}{' (n<30)' if n < 30 else ''} | {f3(x['F0', 'any_full'])} | {f3(x['F1', 'any_full'])} | {f3(x['F0', 'any_sur'])} | {f3(x['F2', 'any_sur'])} | "
              f"{f3(x['F0', 'first_sur'])} | {f3(x['F3', 'first_sur'])} | {f3(x['F4', 'first_sur'])} |")
    P(''); P('## 6. B: teacher forcing (descriptive): all-token paper score, spec = true - mean of 5 false titles')
    P(''); P('| group | cond | true | spec [95% CI] | true - delete | first-author first token spec | median rank first token (true) | share rank<=5 |'); P('|---|---|---|---|---|---|---|---|')
    for g in ['A', 'B', 'C']:
        for c in FMTS:
            x = tB[(tB.group == g) & (tB.fa_type == 'all') & (tB.cond == c)]
            a = x[x.score == 'all_tokens'].set_index('measure'); f = x[x.score == 'first_author_first_token'].set_index('measure')
            P(f"| {g} | {c} | {a.est['true']:.3f} | {f3(a.est['spec'])} [{f3(a.lo['spec'])}, {f3(a.hi['spec'])}] | {f3(a.est['true_minus_delete'])} | {f3(f.est['spec'])} | "
              f"{f.est['median_rank_true']:.0f} | {f.est['share_rank_le5_true']:.3f} |")
    P(''); P('## 7. D: contrasts (all tokens of the scored set; group C low power, 228 papers)')
    P(''); P('| group | version | contrast | estimate [95% CI] | p | n |'); P('|---|---|---|---|---|---|')
    sel = dC[(dC.fa_type == 'all') & (dC.score == 'all_tokens') & (dC.version.isin(['true', 'spec', 'delete', 'true_minus_delete']))]
    for r in sel.itertuples():
        P(f"| {r.group}{' (low power)' if r.low_power_C else ''} | {r.version} | {r.contrast}{' (PRIMARY)' if r.primary else ''} | {f3(r.est)} [{f3(r.lo)}, {f3(r.hi)}] | {r.p:.4f} | {r.n} |")
    P(''); P('### D first scored author, first token (beside the main score)'); P(''); P('| group | version | contrast | estimate [95% CI] | n |'); P('|---|---|---|---|---|')
    for r in dC[(dC.fa_type == 'all') & (dC.score != 'all_tokens')].itertuples():
        P(f'| {r.group} | {r.version} | {r.contrast} | {f3(r.est)} [{f3(r.lo)}, {f3(r.hi)}] | {r.n} |')
    P(''); P('### D first-token-type split of G(1) and G(2), true title'); P(''); P('| group | fa_type | contrast | estimate [95% CI] | n |'); P('|---|---|---|---|---|')
    for r in dC[(dC.fa_type != 'all') & (dC.score == 'all_tokens') & (dC.version == 'true') & dC.contrast.isin(['G1', 'G2']) & dC.group.isin(['A', 'B', 'C', 'A-B'])].itertuples():
        P(f"| {r.group} | {r.fa_type} | {r.contrast} | {f3(r.est)} [{f3(r.lo)}, {f3(r.hi)}] | {r.n}{' (n<30)' if r.descriptive_only else ''} |")
    P(''); P('### D levels (paper score, true title)'); P(''); P('| group | ' + ' | '.join(DCONDS + ['P_none_from2', 'P_none_from3', 'P_none_first']) + ' |'); P('|---' * 12 + '|')
    for g in ['A', 'B', 'C']:
        x = dL[(dL.group == g) & (dL.version == 'true')].set_index('cond').est
        P(f'| {g} | ' + ' | '.join(f'{x[c]:.3f}' for c in DCONDS + ['P_none_from2', 'P_none_from3', 'P_none_first']) + ' |')
    P(''); P('## 8. D generation check (secondary): true vs control first author given, greedy rest, authors 2..n')
    P(''); P('| group | measure | G_true1 | G_other1 | difference [95% CI] |'); P('|---|---|---|---|---|')
    for g in ['A', 'B', 'C']:
        for m in ['any_rest_full', 'recall_rest', 'any_rest_sur', 'fab_any']:
            x = dG[(dG.group == g) & (dG.measure == m)].set_index('cond')
            P(f"| {g} | {m} | {x.est['G_true1']:.3f} | {x.est['G_other1']:.3f} | {f3(x.est['true1_minus_other1'])} [{f3(x.lo['true1_minus_other1'])}, {f3(x.hi['true1_minus_other1'])}] |")
    P(''); P('## 9. D16-5 control exclusion (share of the eligible control pool removed because it shares an author surname)')
    P(''); P('| item | rule | group | papers | mean share excluded | pooled share | papers with >=1 excluded | chosen controls sharing a surname |'); P('|---|---|---|---|---|---|---|---|')
    for r in ex.itertuples():
        P(f'| {r.item} | {r.rule} | {r.grp} | {r.papers} | {r.mean_share_excluded:.4f} | {r.pooled_share_excluded:.4f} | {r.papers_with_any_excluded:.3f} | {r.chosen_control_shares_surname} |')
    P(''); P('## 10. Exploratory R0 check (F0, all B shards; not confirmatory)')
    P(''); P('| group | measure | estimate [95% CI] | n |'); P('|---|---|---|---|')
    for r in r0d[r0d.fa_type == 'all'].itertuples(): P(f'| {r.group} | {r.measure} | {r.est:.3f} [{r.lo:.3f}, {r.hi:.3f}] | {r.n} |')
    P(''); P('full = full-name matcher (surname + first initial); fs = full-name OR surname-only match (old r0_prompt.py "any"); co_only = >= 1 co-author but not the first author; c_ = same output vs the fixed control paper; corr = true - chance.')
    P(''); P('## 11. Open choices (not specified by the plan; most literal reading used)')
    for line in meta['open_choices']: P(f'- {line}')
    P(''); P('## 12. Parse / shard checks'); P(''); P('```'); P(res['checks'].to_string(index=False)); P('```')
    (out / 'report.md').write_text('\n'.join(L) + '\n')


OPEN = [
    'Holm-adjusted CI: percentile interval at level alpha/(5 - j) for the test at Holm step j (ascending p, step-down); each B condition is one test with intersection-union p = max(p Delta_A, p DiD). Bonferroni (0.01) CIs and plain 95% CIs reported beside.',
    'Percentile p-value (two-sided) = groups_core.Engine.pval, floor 1/2000; bootstrap = the archived Engine draw (seed 391), shared by B and D.',
    'Fabrication for the interpretability rule: share of papers with >= 1 generated item matching no true author, matcher comparable to the outcome (full for F1, surname for F2/F3/F4, same matcher for F0); rule applied as Delta fabrication_A(c) > 0 and > Delta_A(c) (point estimates; \'raises fabrication\' read as a positive change). Item shares and empty-answer shares reported beside.',
    'F0 comparison outcomes: F2 vs F0 any_sur (surname-only matcher on the F0 list); F3/F4 vs F0 first_sur (first author surname anywhere in the F0 list, D16-6); chance column of the same rule (F4 uses the same-initial control, F0 the +-1-author control).',
    'Group C: TF scores use unwritten authors only (plan section 1); C generation outcomes use all authors (generation is not split by written status). C in B/D is reported, not part of any decision.',
    'D "first-author first-token version": the first SCORED author (author 2 for k = 1, author 3 for k = 2), first token, since prefix authors are never scored.',
    'D "P_reverse vs forward": reverse_minus_none_first = score(author 1 | prefix authors 2..n) - score(author 1 | no prefix); forward comparator = true1_minus_none = score(authors 2..n | author 1) - score(authors 2..n | no prefix) (both relative to P_none; the plan names no baseline).',
    'D title-specific version = (true - mean of 5 false titles) of P_true1 minus the same of P_other1; deleted-title version = G on the deleted-title prompts; true_minus_delete reported as well.',
    'fa_type "other" (B 10, D 7 papers) is included in the pooled analysis and omitted from the split.',
    'Paper with a nan cell (e.g. F4 TF when the first author has no given name) is dropped from that cell only.',
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--shards-B'); ap.add_argument('--shards-D'); ap.add_argument('--out', default=str(G / 'summary_a16_20261115'))
    ap.add_argument('--allow-missing', action='store_true'); a = ap.parse_args()
    if sha(CFG / 'prereg_addendum16.md') != PREREG_SHA: raise SystemExit('PREREG CHANGED')
    if sha(CFG / 'prereg_addendum16_deviations.md') != DEV_SHA: warn('deviations file sha differs from a1512fda...')
    if sha(H / '14_groups/prereg16_a16.py') != SCRIPT16_SHA: warn('prereg16_a16.py sha differs from the D16-4 record')
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    pars = lambda x: None if x is None else [int(k) for k in x.split(',')]
    sB, parB, tfB, chB = load_item('B', pars(a.shards_B), a.allow_missing)
    sD, parD, tfD, chD = load_item('D', pars(a.shards_D), a.allow_missing)
    log('loaded', len(sB), len(parB), len(tfB), len(sD), len(parD), len(tfD))
    import os
    B = Boot()
    # team check: sample team column and the Engine team partition agree
    for s in (sB, sD):
        t = B.E.team.loc[s.paper_id].to_numpy()
        if pd.crosstab(t, s.team.to_numpy()).astype(bool).sum(1).max() != 1: warn('sample team ids and Engine teams disagree')
    res = {}
    res['b_rates'], res['b_main'], res['b_fab'], res['b_tf'], bootsB = b_analysis(B, sB, parB, tfB); log('B done')
    res['d_contrasts'], res['d_levels'], bootsD = d_analysis(B, sD, parD, tfD); log('D tf done')
    res['d_gen'] = d_gen(B, sD, parD)
    res['r0'] = r0(B, sB, parB)
    res['d16_5'] = d16_5(sB, sD); log('D16-5 done')
    h = holm(B, bootsB, res['b_main'], bootsD)
    gA1 = res['d_contrasts'].query('primary').est.iloc[0]; h.loc[h.test == 'D_GA1', 'est'] = gA1
    res['holm'] = h; res['checks'] = pd.concat([chB, chD], ignore_index=True)
    for k, v in res.items(): v.to_csv(out / f'{k}.csv', index=False)
    # verdicts
    V = []; mB = res['b_main']
    supp = []
    for c in ['F1', 'F2', 'F3', 'F4']:
        x = h[h.test == f'B_{c}']; dA = x[x.quantity == 'Delta_A'].iloc[0]; dd = x[x.quantity == 'DiD_A-B'].iloc[0]
        ok = bool(dA.rejected_holm and dA.holm_ci_lo > 0 and dd.holm_ci_lo > 0)
        fabd = mB.query("primary and contrast=='Delta_A' and cond==@c").fab_delta.iloc[0]
        interp = not (fabd > 0 and fabd > dA.est)
        if ok and interp: supp.append(c)
        V.append(f'B {c} ({MAIN_OUT[c]}): Delta_A = {f3(dA.est)} [Holm CI {f3(dA.holm_ci_lo)}, {f3(dA.holm_ci_hi)}], DiD = {f3(dd.est)} [Holm CI {f3(dd.holm_ci_lo)}, {f3(dd.holm_ci_hi)}]; '
                 f'p_test {dA.p_test:.4f}, Holm p {dA.p_holm:.4f}; fabrication change A {f3(fabd)} -> {"interpretable" if interp else "NOT interpretable"}; '
                 f'{"criterion met" if ok else "criterion not met"}.')
    V.append(f"B overall: {'SUPPORTED via ' + ','.join(supp) if supp else 'NOT SUPPORTED'} (rule: >= 1 c with Delta_A > 0 and DiD > 0, Holm-adjusted CIs excluding 0).")
    x = h[h.test == 'D_GA1'].iloc[0]
    dsup = bool(x.rejected_holm)
    V.append(f"D G_A(1) = {f3(gA1)} [95% {f3(x.ci95_lo)}, {f3(x.ci95_hi)}; Holm CI {f3(x.holm_ci_lo)}, {f3(x.holm_ci_hi)}], p {x.p_test:.4f}, Holm p {x.p_holm:.4f}: "
             f"{'chain effect SUPPORTED, direction ' + ('helps' if gA1 > 0 else 'hinders') if dsup else 'chain effect NOT supported'} (rule: Holm-adjusted 95% CI of G_A(1) excludes 0; two-sided).")
    meta = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), job=os.environ.get('SLURM_JOB_ID'), script_sha256=sha(__file__), prereg_sha256=PREREG_SHA,
                deviations_sha256=sha(CFG / 'prereg_addendum16_deviations.md'), B_papers=len(sB), D_papers=len(sD),
                B_shards=f'{int(sB.shard.min())}-{int(sB.shard.max())} ({sB.shard.nunique()})', D_shards=f'{int(sD.shard.min())}-{int(sD.shard.max())} ({sD.shard.nunique()})',
                verdicts=V, open_choices=OPEN, warnings=WARN)
    (out / 'meta.json').write_text(json.dumps(meta, indent=1, default=str))
    report(out, res, meta)
    for v in V: print('VERDICT', v)
    print(h.to_string())
    log('wrote', out)


if __name__ == '__main__':
    main()
