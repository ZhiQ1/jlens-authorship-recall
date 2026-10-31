"""Fold audit 2026-10-30: which fold variant did each ORIGINAL run use? Fingerprints from saved outputs:
E4b group runs: per-paper 'dropped' (title-reuse flag, a function of the folds) for the probe trained on true titles;
team partitions: pairs.parquet team, x4_textbase*_perpaper team (compared as partitions).
Usage: python stage13_foldaudit_fingerprint.py variants/*.npz"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
B = Path('/scratch/zhang.zhiqi2/jlens'); ROOT = B / '381_stage13'
ft = pd.read_parquet(B / '351_stage10/cohort/conditions/false_titles.parquet'); DONOR = ft[ft.k == 0].set_index('paper_id').donor_paper_id
def same_partition(a, b):
    a, b = pd.factorize(pd.Series(a))[0], pd.factorize(pd.Series(b))[0]; return bool((a == b).all())
saved = {}
for d in ('summary_cpu_group', 'summary_cpu_trainstd'):
    pp = pd.read_parquet(ROOT / d / 'perpaper_probe_spec.parquet')
    s = pp[(pp.split == 'group') & (pp.excl == 'none') & (pp.control == 'probe (as in Stage 11)')].drop_duplicates('paper_id').set_index('paper_id').dropped
    saved[d] = s
fz = np.load(ROOT / 'summary_cpu_teamci/folds_group.npz')
pairs = pd.read_parquet(ROOT / 'config/pairs.parquet')
tb = {f: pd.read_csv(ROOT / 'summary_x1x4' / f).set_index('paper_id').team for f in ('x4_textbase_perpaper.csv', 'x4_textbase2_perpaper.csv')}
for f in sys.argv[1:]:
    z = np.load(f, allow_pickle=True); print('==', Path(f).stem)
    for s in ('titlepos_true', 'titlepos_false0_donor', 'm3_task', 'all9108', 'pairs_k2'):
        print(f'  {s}: fold sizes {np.bincount(z[s + "_fold"])}')
    print('  vs folds_group.npz: true fold identical', bool((fz['true_pid'] == z['titlepos_true_pid']).all() and (fz['true_fold'] == z['titlepos_true_fold']).all()),
          '| false_0 fold identical', bool((fz['false_0_pid'] == z['titlepos_false0_donor_pid']).all() and (fz['false_0_fold'] == z['titlepos_false0_donor_fold']).all()),
          '| teams identical', bool((fz['true_team'] == z['titlepos_true_team']).all() and (fz['false_0_team'] == z['titlepos_false0_donor_team']).all()))
    pid, fo = z['titlepos_true_pid'], z['titlepos_true_fold']; F = dict(zip(pid, fo))
    for d, s in saved.items():
        mine = pd.Series({p: (DONOR.get(p) in F and F[DONOR.get(p)] != F[p]) for p in s.index})
        print(f'  E4b {d}: dropped flag mismatches {int((mine != s).sum())} of {len(s)}')
    for a, b in (('titlepos_true', 'm3_task'), ('titlepos_true', 'all9108')):
        same_ids = (z[a + '_pid'] == z[b + '_pid']).all()
        print(f'  {b} same pid order as {a}: {bool(same_ids)}; folds identical: {bool(same_ids and (z[a + "_fold"] == z[b + "_fold"]).all())}')
    t = dict(zip(z['pairs_k2_pid'], z['pairs_k2_team']))
    print('  pairs.parquet team partition identical:', same_partition(pairs.team, [t[p] for p in pairs.paper_id]))
    ta = dict(zip(z['all9108_pid'], z['all9108_team']))
    for k, v in tb.items(): print(f'  {k} team partition identical (vs pairs-k2 teams):', same_partition(v, [t[p] for p in v.index]))
