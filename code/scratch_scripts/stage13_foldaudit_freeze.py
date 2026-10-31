"""Fold audit 2026-10-30: write the archived ORIGINAL-run team folds, one file per paper set, next to folds_group.npz.
Source: foldaudit_2026-10-30/variants/c0622.npz (identical, fold and team, to the variants recomputed on the original
nodes d0139, c0685, c0602, c0613, c0621, c0606, c3155) and summary_cpu_teamci/folds_group.npz (cross-checked).
Each file: ids = the exact input sequence passed to group_folds (paper ids; for false_0 the donor ids, with repeats),
fold, team (as returned), k, seed, plus paper_id (the row paper ids, = ids except for false_0). README.md lists sha256."""
import hashlib
from pathlib import Path
import numpy as np
D = Path('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_cpu_teamci'); V = Path('/scratch/zhang.zhiqi2/jlens/381_stage13/foldaudit_2026-10-30/variants')
z = np.load(V / 'c0622.npz', allow_pickle=True); g = np.load(D / 'folds_group.npz', allow_pickle=True)
assert (g['true_pid'].astype(str) == z['titlepos_true_pid'].astype(str)).all() and (g['true_fold'] == z['titlepos_true_fold']).all() and (g['true_team'] == z['titlepos_true_team']).all()
assert (g['false_0_pid'].astype(str) == z['titlepos_false0_donor_pid'].astype(str)).all() and (g['false_0_fold'] == z['titlepos_false0_donor_fold']).all()
import pandas as pd
ft = pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/conditions/false_titles.parquet'); donor = ft[ft.k == 0].set_index('paper_id').donor_paper_id
fpid = g['false_0_pid'].astype(str); fdon = np.array([donor[p] for p in fpid]).astype(str)
files = {
  'folds_own9108_k5s13.npz': dict(ids=z['titlepos_true_pid'].astype(str), paper_id=z['titlepos_true_pid'].astype(str), fold=z['titlepos_true_fold'], team=z['titlepos_true_team'], k=5, seed=13,
      note='9,108 papers, own ids (Stage 11 titlepos order = cohort papers.parquet order = M3 cache order). Used by M2 true, M2b, M2c, E4b/X1-controls group, E4b trainstd, M3, X4 textbase/textbase2, cluster_ci, X6, X7.'),
  'folds_donor9108_false0_k5s13.npz': dict(ids=fdon, paper_id=fpid, fold=g['false_0_fold'], team=g['false_0_team'], k=5, seed=13,
      note='9,108 false_0 rows (titlepos false_0 order); group_folds input = donor paper ids (with repeats). Used by M2 false_0 (stage13_cpu m2, stage13_m2_teamci).'),
  'folds_pairs1178_k2s1314.npz': dict(ids=z['pairs_k2_pid'].astype(str), paper_id=z['pairs_k2_pid'].astype(str), fold=z['pairs_k2_fold'], team=z['pairs_k2_team'], k=2, seed=1314,
      note='1,178 X1/X3/X4 pairs papers (config/pairs.parquet order). 381_stage13.py freeze uses only the team (for the tune/test split); pairs.parquet already stores team and split.'),
}
L = ['# Archived team folds (fold audit 2026-10-30)', '', 'stage13_cpu.group_folds() returns these when its input id set and (k, seed) match a file here (and donors is None);',
     'otherwise it computes (tie order between equal-size groups can depend on the CPU: AVX-512 numpy sort). Set JLENS_FOLDS_ARCHIVE=off to force computing.',
     'folds_group.npz (2026-10-30, M2 team-CI) is kept unchanged; its true/false_0 folds equal the first two files below.', '', '| file | rows | k | seed | sha256 | note |', '|---|---|---|---|---|---|']
for n, d in files.items():
    p = D / n; assert not p.exists(), f'{p} exists; not overwriting'
    np.savez(p, **{k: np.asarray(v) for k, v in d.items()}); h = hashlib.sha256(p.read_bytes()).hexdigest()
    L.append(f"| {n} | {len(d['ids'])} | {d['k']} | {d['seed']} | `{h}` | {d['note']} |"); print(n, h)
h = hashlib.sha256((D / 'folds_group.npz').read_bytes()).hexdigest(); L.append(f'| folds_group.npz (original M2 team-CI file) | 9108 x 2 | 5 | 13 | `{h}` | true_* and false_0_* |')
(D / 'README.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
