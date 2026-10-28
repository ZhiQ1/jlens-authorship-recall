"""Review item 3 (2026-10-28): confidence intervals with the author TEAM as the resampling unit.

Papers sharing a full author name are not independent. Every interval below is recomputed by resampling whole teams
(stage13_cpu.group_folds groups, the same groups as the probe folds) with replacement; each paper is weighted by how
often its team was drawn. Point estimates are unchanged (same estimators, same within-bin weights); only the interval
changes. Original per-paper intervals are shown next to them, and rows where "interval excludes 0" flips are listed.
  Stage 10: 6.2 true-title target - control within bin; 6.4 title-specific target - control within bin; 6.3 group
            means of the title-specific signal; R0 view (A - B) and C - A.
  Stage 11: E1 / E1t patching recovery and E2 / E2n knockout loss per group, and target - control of the recovery.
Outputs: 381_stage13/summary_cpu_group/cluster_ci_*.csv, reports/cluster_ci.md
"""
import importlib.util, os
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'
ROOT = B / '381_stage13'; OUT = ROOT / 'summary_cpu_group'; OUT.mkdir(parents=True, exist_ok=True)
NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


c13 = load(H / '13_stage13/stage13_cpu.py', 'c13'); s10 = load(H / '10_stage10/351_stage10.py', 's10')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet')
_, TEAM = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAM))


def team_weights(pids, seed):
    """[NB, len(pids)] weights: each team drawn with replacement (multinomial), a paper gets its team's count."""
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    cnt = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)
    return cnt[:, codes]


def strat_cluster(df, col, gcol, a, b, strata, min_n=30, seed=1):
    """same estimator as s10.stratified_diff (bins with >= min_n per group, weights n_a n_b / (n_a + n_b)), team bootstrap."""
    df = df[df[gcol].isin([a, b])].dropna(subset=[col]).reset_index(drop=True)
    cells = []
    for s, ss in df.groupby(strata):
        ia, ib = ss.index[ss[gcol] == a].to_numpy(), ss.index[ss[gcol] == b].to_numpy()
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    if not cells: return np.nan, np.nan, np.nan
    w = np.array([len(x) * len(y) / (len(x) + len(y)) for x, y in cells]); w /= w.sum()
    x = df[col].to_numpy(float); W = team_weights(df.paper_id.to_numpy(), seed)
    est = sum(wi * (x[ia].mean() - x[ib].mean()) for wi, (ia, ib) in zip(w, cells))
    bt = np.zeros(NB)
    for wi, (ia, ib) in zip(w, cells):
        ma = (W[:, ia] @ x[ia]) / np.maximum(W[:, ia].sum(1), 1e-9); mb = (W[:, ib] @ x[ib]) / np.maximum(W[:, ib].sum(1), 1e-9)
        bt += wi * (ma - mb)
    return est, *np.percentile(bt, [2.5, 97.5])


def mean_cluster(pids, x, seed=2):
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]; W = team_weights(pids, seed)
    return x.mean(), *np.percentile((W @ x) / W.sum(1), [2.5, 97.5])


def ratio_cluster(pids, num, den, seed=3):
    W = team_weights(np.asarray(pids), seed); num, den = np.asarray(num, float), np.asarray(den, float)
    return num.mean() / den.mean(), *np.percentile((W @ num) / (W @ den), [2.5, 97.5])


def flips(d, lo0, hi0, lo1, hi1):
    ex0 = (d[lo0] > 0) | (d[hi0] < 0); ex1 = (d[lo1] > 0) | (d[hi1] < 0); return ex0 != ex1


rows = []
# ---------------- Stage 10
ds = pd.read_parquet(R10 / 'summary_title/paper_title_contrasts.parquet')
ps = pd.read_parquet(R10 / 'summary/paper_scores.parquet', columns=['paper_id', 'readout', 'layer', 'mean_nlr', 'group_tight', 'citation_bin'])
tabs = [('6.4 title-specific target-control', ds, 'spec_mean_nlr', pd.read_csv(R10 / 'summary_title/B_spec_target_vs_control_within_bin.csv'), 'group_tight', 'target', 'control', None),
        ('6.2 true-title target-control', ps, 'mean_nlr', pd.read_csv(R10 / 'summary/B_target_vs_control_within_bin.csv'), 'group_tight', 'target', 'control', None),
        ('R0 view A-B', ds[ds.recall_level == 'R0'], 'spec_mean_nlr', pd.read_csv(R10 / 'summary_r0r1/tc_R0.csv'), 'group_tight', 'target', 'control', None)]
dsx = ds.assign(bg=ds.group_tight.map({'target': 'T', 'control': 'C'}).fillna('') + ds.recall_level.map({'R0': '0', 'R1': '1'}).fillna(''))
tabs.append(('C-A within target', dsx[dsx.bg.isin(['T1', 'T0'])], 'spec_mean_nlr', pd.read_csv(R10 / 'summary_r0r1/C_minus_A.csv'), 'bg', 'T1', 'T0', 10))
for name, data, col, orig, gcol, a, b, mn in tabs:
    for (r, l), sub in data.groupby(['readout', 'layer']):
        o = orig[(orig.readout == r) & (orig.layer == l)]
        if not len(o): continue
        e, lo, hi = strat_cluster(sub, col, gcol, a, b, 'citation_bin', min_n=mn or 30)
        rows.append(dict(table=name, readout=r, layer=int(l), est=e, lo_paper=o[col + '_lo'].iloc[0], hi_paper=o[col + '_hi'].iloc[0], lo_team=lo, hi_team=hi))
    print('done', name, flush=True)
# 6.3 group means
ag = pd.read_csv(R10 / 'summary_title/A_group_layer.csv')
for (r, l), sub in ds[ds.group_tight.isin(['target', 'control'])].groupby(['readout', 'layer']):
    for g in ('target', 'control'):
        s = sub[sub.group_tight == g]; o = ag[(ag.readout == r) & (ag.layer == l) & (ag.group_tight == g)]
        if not len(o): continue
        e, lo, hi = mean_cluster(s.paper_id, s.spec_mean_nlr)
        rows.append(dict(table=f'6.3 title-specific mean, {g}', readout=r, layer=int(l), est=e, lo_paper=o.spec_mean_nlr_lo.iloc[0], hi_paper=o.spec_mean_nlr_hi.iloc[0], lo_team=lo, hi_team=hi))
print('done 6.3', flush=True)
# ---------------- Stage 11
sys_path = str(H / '11_stage11'); import sys; sys.path.insert(0, sys_path); import stage11_analyze as a11
toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id'])
smp = pd.read_parquet(R11 / 'config/sample.parquet')[['paper_id', 'group', 'citation_bin']]
d, layers = a11.load_unit_dir(R11 / 'raw/patch')
def paper_means(dd, cols):
    t = toks.set_index('row_id').loc[dd['row_id']].reset_index(); df = pd.DataFrame({'paper_id': t.paper_id, 'true': a11.nlr(dd['rank_true']), 'false': a11.nlr(dd['rank_false'])})
    for c, v in cols.items(): df[c] = v
    return df.groupby('paper_id').mean().reset_index().merge(smp, on='paper_id')
for nm, sub in (('E1', 'patch'), ('E1t', 'patch_title')):
    dd, ly = (d, layers) if sub == 'patch' else a11.load_unit_dir(R11 / 'raw' / sub)
    pp = paper_means(dd, {f'p{l}': a11.nlr(dd['rank_patch'][:, i]) for i, l in enumerate(ly)})
    if nm == 'E1t' and 63 in list(ly): pp['false'] = pp['p63']
    orig = pd.read_csv(R11 / f'summary/{nm}_recovery.csv')
    for g in ('target', 'control'):
        s = pp[pp.group == g]
        for l in ly:
            if l == 63: continue
            e, lo, hi = ratio_cluster(s.paper_id, s[f'p{l}'] - s['false'], s['true'] - s['false'])
            o = orig[(orig.group == g) & (orig.layer == l)].iloc[0]
            rows.append(dict(table=f'{nm} recovery, {g}', readout='final', layer=int(l), est=e, lo_paper=o.rec_lo, hi_paper=o.rec_hi, lo_team=lo, hi_team=hi))
for nm, sub in (('E2', 'knockout'), ('E2n', 'knockout_name')):
    k, kl = a11.load_unit_dir(R11 / 'raw' / sub); t = toks.set_index('row_id').loc[k['row_id']].reset_index()
    kd = pd.DataFrame({'row_id': k['row_id'], 'paper_id': t.paper_id})
    for i, l in enumerate(kl): kd[f'k{l}'] = a11.nlr(k['rank_ko'][:, i])
    kd = kd.merge(pd.DataFrame({'row_id': d['row_id'], 'true': a11.nlr(d['rank_true']), 'false': a11.nlr(d['rank_false'])}), on='row_id')
    kp = kd.drop(columns='row_id').groupby('paper_id').mean().reset_index().merge(smp, on='paper_id'); orig = pd.read_csv(R11 / f'summary/{nm}_knockout.csv')
    for g in ('target', 'control'):
        s = kp[kp.group == g]
        for l in kl:
            if l == 64: continue
            e, lo, hi = ratio_cluster(s.paper_id, s['k64'] - s[f'k{l}'], s['true'] - s['false'])
            o = orig[(orig.group == g) & (orig.start_layer == l)].iloc[0]
            rows.append(dict(table=f'{nm} loss, {g}', readout='final', layer=int(l), est=e, lo_paper=o.lo, hi_paper=o.hi, lo_team=lo, hi_team=hi))
print('done Stage 11', flush=True)
D = pd.DataFrame(rows); D['width_ratio'] = (D.hi_team - D.lo_team) / (D.hi_paper - D.lo_paper)
D['flip'] = flips(D, 'lo_paper', 'hi_paper', 'lo_team', 'hi_team'); D.to_csv(OUT / 'cluster_ci_all.csv', index=False)
L = ['# Team-cluster bootstrap vs per-paper bootstrap (point estimates unchanged)', '',
     f'Teams: {len(set(TEAM.values()))} groups over {len(TEAM)} papers (papers sharing any full author name).', '',
     '## Interval width ratio (team / paper), by table', '', D.groupby('table').width_ratio.describe()[['count', 'mean', 'min', 'max']].round(2).to_string(), '',
     f'## Rows where "interval excludes 0" changes: {int(D.flip.sum())} of {len(D)}', '']
if D.flip.any(): L += [D[D.flip][['table', 'readout', 'layer', 'est', 'lo_paper', 'hi_paper', 'lo_team', 'hi_team']].round(3).to_string(index=False), '']
(ROOT / 'reports/cluster_ci.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
