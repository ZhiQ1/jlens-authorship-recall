"""2026-11-12, POST HOC, DESCRIPTIVE (not in the pre-registered main comparison).
Title-position probe on all name tokens (addendum 9 / addendum 10 item 4 / deviation D1): an "all name tokens combined" row,
pooled from the stored per-paper role scores (summary_b1_e4b5/probe/perpaper_<role>_L<l>.parquet), no new fit, no GPU.

Pooling (token-weighted = mean over ALL of the paper's name tokens of the five addendum-9 roles: initial, given_first,
given_cont, surname_first, surname_cont; each token scored by its own role probe). A role's tokens enter the paper's
pooled score for false title k only when that ROLE probe's title-reuse flag for k is False (the same exclusion as the role
rows, applied per role probe):
  V0    spec  = sum_r w_r0 spec_k0_r / sum_r w_r0,  w_rk = n_tok_r * (not dropped_k_r); paper kept if sum w_r0 > 0
  V5x0  spec  = sum_r w_r0 spec5_r  / sum_r w_r0   (five-title mean, false_0-only exclusion; contains leakage)
  Vpd   s_k   = sum_r w_rk spec_k_r / sum_r w_rk;  spec_pd = mean over k with sum_r w_rk > 0; kept if >= 1 such k
Controls (random other paper / same field) pooled identically from the ctrl_*_k columns.
Estimators: the EXACT functions of stage13_b1_e4b5_perdonor.py (team_weights, mean_cluster, strat_cluster, perdonor),
extracted by ast and exec'd (that script runs at import, so it is not imported); same seeds (spec 2, tc 1), 2,000 draws,
archived author-team clusters, citation bins with >= 30 papers in both groups, weights n_t n_c / (n_t + n_c).
Parity (WARN only): every existing L40 row of perdonor_by_run_layer.csv is recomputed with the extracted functions.
Output: 381_stage13/summary_tc_extra_roles_20261112/{pooled_by_layer.csv, parity_L40.csv, report.md}.
"""
import ast
from pathlib import Path
import numpy as np, pandas as pd, importlib.util

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'
PR = R13 / 'summary_b1_e4b5/probe'; REF = R13 / 'summary_b1_e4b5/perdonor_by_run_layer.csv'
OUT = R13 / 'summary_tc_extra_roles_20261112'; OUT.mkdir(parents=True, exist_ok=True)
SRC = H / '13_stage13/stage13_b1_e4b5_perdonor.py'
ROLES = ['initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']; KS = [0, 1, 2, 3, 4]
LABEL = 'post hoc, descriptive (not in the pre-registered main comparison)'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# ---- exact estimator code from the per-donor script
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); META = papers.set_index('paper_id')
NS = dict(np=np, pd=pd, NB=2000, KS=KS, TEAM=TEAM)
tree = ast.parse(SRC.read_text())
fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('team_weights', 'mean_cluster', 'strat_cluster', 'perdonor', 'f3')]
assert {f.name for f in fns} == {'team_weights', 'mean_cluster', 'strat_cluster', 'perdonor', 'f3'}
exec(compile(ast.Module(body=fns, type_ignores=[]), str(SRC), 'exec'), NS)
mean_cluster, strat_cluster, perdonor, f3 = NS['mean_cluster'], NS['strat_cluster'], NS['perdonor'], NS['f3']
warns = []


def estimate(sub, col, ca, cf):
    m, lo, hi, n = mean_cluster(sub.paper_id.to_numpy(), sub[col].to_numpy())
    t, tlo, thi, nb = strat_cluster(sub.reset_index(drop=True), col, 'group_tight', 'target', 'control', 'citation_bin')
    ma = mean_cluster(sub.paper_id.to_numpy(), sub[ca].to_numpy()); mf = mean_cluster(sub.paper_id.to_numpy(), sub[cf].to_numpy())
    return dict(spec=m, lo=lo, hi=hi, n=n, tc=t, tc_lo=tlo, tc_hi=thi, tc_bins=nb, ctrl_any=ma[0], ctrl_any_lo=ma[1], ctrl_any_hi=ma[2],
                ctrl_field=mf[0], ctrl_field_lo=mf[1], ctrl_field_hi=mf[2])


def tc_n(sub, col):
    """papers inside the used bins (target, control)"""
    s = sub.dropna(subset=[col]); nt = nc = 0
    for _, ss in s.groupby('citation_bin'):
        a, b = (ss.group_tight == 'target').sum(), (ss.group_tight == 'control').sum()
        if a >= 30 and b >= 30: nt += a; nc += b
    return int(nt), int(nc)


# ---- parity: all existing L40 rows (per-role runs) recomputed
ref = pd.read_csv(REF); par = []
for run in ['e4b_parity', 'first_alltok'] + ROLES:
    d = perdonor(pd.read_parquet(PR / f'perpaper_{run}_L40.parquet').join(META, on='paper_id')); tc = d.group_tight.isin(['target', 'control'])
    for v, sub, col, ca, cf in (('Vpd', d[tc & (d.n_used >= 1)], 'spec_pd', 'ctrl_any_pd', 'ctrl_field_pd'),
                                ('V5x0', d[tc & ~d.drop0], 'spec5', 'ctrl_any5', 'ctrl_field5'), ('V0', d[tc & ~d.drop0], 'spec0', 'ctrl_any0', 'ctrl_field0')):
        e = estimate(sub, col, ca, cf); r = ref[(ref.run == run) & (ref.layer == 40) & (ref.version == v)].iloc[0]
        dmax = max(abs(e[k] - r[k]) for k in ('spec', 'lo', 'hi', 'tc', 'tc_lo', 'tc_hi', 'ctrl_any', 'ctrl_field'))
        nt, nc = tc_n(sub, col)
        par.append(dict(run=run, version=v, tc=e['tc'], tc_lo=e['tc_lo'], tc_hi=e['tc_hi'], ref_tc=r.tc, ref_tc_lo=r.tc_lo, ref_tc_hi=r.tc_hi,
                        n=e['n'], ref_n=int(r.n), n_target_in_bins=nt, n_control_in_bins=nc, max_abs_diff=dmax, ok=bool(dmax <= 1e-9 and e['n'] == r.n)))
P = pd.DataFrame(par); P.to_csv(OUT / 'parity_L40.csv', index=False); print(P.to_string(), flush=True)
if not P.ok.all(): warns.append(f'WARN parity: {int((~P.ok).sum())} of {len(P)} L40 rows differ (max |diff| {P.max_abs_diff.max():.2e}); continued')

# ---- pooled all-roles rows
layers = sorted({int(f.stem.rsplit('_L', 1)[1]) for f in PR.glob('perpaper_initial_L*.parquet')}); rows = []; pooled40 = None
for l in layers:
    parts = []
    for r in ROLES:
        d = pd.read_parquet(PR / f'perpaper_{r}_L{l}.parquet')
        if not (d.drop0 == d.dropped_0).all(): warns.append(f'WARN {r} L{l}: drop0 != dropped_0 for some papers')
        cols = ['paper_id', 'n_tok', 'spec5', 'ctrl_any5', 'ctrl_field5'] + [f'{c}_k{k}' for c in ('spec', 'ctrl_any', 'ctrl_field') for k in KS] + [f'dropped_{k}' for k in KS]
        parts.append(d[cols].assign(role=r))
    A = pd.concat(parts, ignore_index=True)
    n = A.n_tok.to_numpy(float)
    def pool(val, wk):
        w = np.where(np.isnan(A[val].to_numpy(float)), 0, n * (~A[wk].to_numpy(bool)))
        g = pd.DataFrame({'paper_id': A.paper_id, 'w': w, 'wx': w * np.nan_to_num(A[val].to_numpy(float))}).groupby('paper_id')[['w', 'wx']].sum()
        return (g.wx / g.w.where(g.w > 0)).rename(val)
    D = pd.DataFrame(index=pd.Index(sorted(A.paper_id.unique()), name='paper_id'))
    D['n_tok_all'] = A.groupby('paper_id').n_tok.sum()
    D['n_tok_used0'] = pd.DataFrame({'p': A.paper_id, 'w': n * (~A.dropped_0.to_numpy(bool))}).groupby('p').w.sum()
    for c in ('spec', 'ctrl_any', 'ctrl_field'):
        D[f'{c}0'] = pool(f'{c}_k0', 'dropped_0'); D[f'{c}5'] = pool(f'{c}5' if c == 'spec' else f'{c}5', 'dropped_0')
        K = np.stack([pool(f'{c}_k{k}', f'dropped_{k}').reindex(D.index).to_numpy() for k in KS], 1)
        D[f'{c}_pd'] = np.nanmean(np.where(np.isnan(K), np.nan, K), 1) if c != 'spec' else np.nanmean(K, 1)
    D['n_used'] = np.stack([pool(f'spec_k{k}', f'dropped_{k}').reindex(D.index).notna().to_numpy() for k in KS], 1).sum(1)
    D = D.reset_index().join(META, on='paper_id'); tc = D.group_tight.isin(['target', 'control'])
    if l == 40: pooled40 = D; D.to_parquet(OUT / 'perpaper_all_roles_pooled_L40.parquet')
    for v, sub, col, ca, cf in (('Vpd', D[tc & (D.n_used >= 1)], 'spec_pd', 'ctrl_any_pd', 'ctrl_field_pd'),
                                ('V5x0', D[tc & D.spec0.notna()], 'spec5', 'ctrl_any5', 'ctrl_field5'), ('V0', D[tc & D.spec0.notna()], 'spec0', 'ctrl_any0', 'ctrl_field0')):
        e = estimate(sub, col, ca, cf); nt, nc = tc_n(sub, col)
        rows.append(dict(run='all_roles_pooled', layer=l, version=v, **e, n_target_in_bins=nt, n_control_in_bins=nc, label=LABEL))
    print('layer', l, 'done', flush=True)
T = pd.DataFrame(rows); T.to_csv(OUT / 'pooled_by_layer.csv', index=False)

# ---- report
ref40 = ref[ref.layer == 40]
L = [f'# Target - control at L40: extra roles and all name tokens pooled ({LABEL})', '',
     'Written 2026-11-12 by `~/jlens_work/13_stage13/stage13_tc_extra_roles_20261112.py` (CPU only, stored per-paper scores of summary_b1_e4b5/probe, no new fit).',
     'Estimators are the exact functions of stage13_b1_e4b5_perdonor.py (team-cluster bootstrap, 2,000 draws, archived author teams; citation bins with >= 30 papers in both groups, weights n_t n_c / (n_t + n_c)).', '',
     '## Parity (all existing L40 rows of perdonor_by_run_layer.csv recomputed)', '',
     f'{int(P.ok.sum())} / {len(P)} rows identical (max |diff| {P.max_abs_diff.max():.1e}). given_first V0: {f3(*P[(P.run == "given_first") & (P.version == "V0")][["tc", "tc_lo", "tc_hi"]].iloc[0])}.', '',
     '## L40, target - control within citation bin [team CI] (n = target + control papers after exclusion)', '',
     '| role | V0 (pre-registered rule) | Vpd (per-donor) | V5x0 (contains leakage) |', '|---|---|---|---|']
for run in ROLES:
    g = ref40[ref40.run == run].set_index('version')
    L.append(f'| {run} | ' + ' | '.join(f'{f3(g.loc[v, "tc"], g.loc[v, "tc_lo"], g.loc[v, "tc_hi"])} (n {int(g.loc[v, "n"]):,})' for v in ('V0', 'Vpd', 'V5x0')) + ' |')
g = T[T.layer == 40].set_index('version')
L.append('| **all name tokens pooled (post hoc)** | ' + ' | '.join(f'{f3(g.loc[v, "tc"], g.loc[v, "tc_lo"], g.loc[v, "tc_hi"])} (n {int(g.loc[v, "n"]):,})' for v in ('V0', 'Vpd', 'V5x0')) + ' |')
L += ['', 'Role rows: copied from summary_b1_e4b5/perdonor_by_run_layer.csv (already computed). Pooled row: new, this script.', '',
      '## All name tokens pooled, L40: title-specific signal and permutation controls (all target + control papers)', '',
      '| version | spec [team CI] | gold = random other paper | gold = random paper, same field | n |', '|---|---|---|---|---|']
for v in ('V0', 'Vpd', 'V5x0'):
    r = g.loc[v]; L.append(f'| {v} | {f3(r.spec, r.lo, r.hi)} | {f3(r.ctrl_any, r.ctrl_any_lo, r.ctrl_any_hi)} | {f3(r.ctrl_field, r.ctrl_field_lo, r.ctrl_field_hi)} | {int(r.n):,} |')
L += ['', '## All name tokens pooled, target - control by layer', '', '| version | ' + ' | '.join(f'L{x}' for x in layers) + ' |', '|---' * (len(layers) + 1) + '|']
for v in ('V0', 'Vpd', 'V5x0'):
    s = T[T.version == v].set_index('layer'); L.append(f'| {v} | ' + ' | '.join(f3(s.loc[x, 'tc'], s.loc[x, 'tc_lo'], s.loc[x, 'tc_hi']) for x in layers) + ' |')
L += ['', '## Definition and caveats', '',
      '- Pooled paper score = mean over all of the paper\'s tokens of the five addendum-9 roles (punctuation / particles excluded, as in addendum 9), each token scored by its own ROLE probe (five separate ridge maps), not by one probe fitted on all tokens. A role\'s tokens are left out of the pooled score for false title k when that role probe flags title reuse for k (V0 / V5x0: false_0 flag; Vpd: flag of each k).',
      '- Papers are therefore kept if at least one role is usable; the paper set is larger than any single role\'s, and roles are mixed in different proportions across papers (73% of names start with an initial).',
      '- The five role rows share papers and team clusters, so the pooled row is not independent of them.',
      '- V5x0 contains title-reuse leakage (false_1..4 donors not excluded); sensitivity only.', '- Teacher-forced preference, not generation.']
if warns: L += ['', '## Warnings', ''] + [f'- {w}' for w in warns]
(OUT / 'report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
