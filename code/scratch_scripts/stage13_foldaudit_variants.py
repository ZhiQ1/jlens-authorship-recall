"""Fold audit 2026-10-30: compute stage13_cpu.group_folds() for every paper set used by a caller, on the current node,
and save (pid, fold, team) per set to foldaudit_2026-10-30/variants/<host>.npz. Reads the ORIGINAL (unpatched) function
from stage13_cpu.before_foldsfreeze_2026-10-30.py if present, else stage13_cpu.py with FOLDS_ARCHIVE disabled."""
import importlib.util, os, socket, sys
from pathlib import Path
import numpy as np, pandas as pd
os.environ['JLENS_FOLDS_ARCHIVE'] = 'off'
H = Path.home() / 'jlens_work/13_stage13'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; ROOT = B / '381_stage13'
src = H / 'stage13_cpu.before_foldsfreeze_2026-10-30.py'
src = src if src.exists() else H / 'stage13_cpu.py'
sp = importlib.util.spec_from_file_location('c13', src); c13 = importlib.util.module_from_spec(sp); sp.loader.exec_module(c13)
np.show_runtime() if hasattr(np, 'show_runtime') else None
ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); donor = ft[ft.k == 0].set_index('paper_id').donor_paper_id
tp = lambda c: np.concatenate([np.load(f)['resid_paper_id'] for f in sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))])
pt, pf = tp('true'), tp('false_0')
sets = {'titlepos_true': (pt, pt, {}), 'titlepos_false0_donor': (pf, np.array([donor[p] for p in pf]), {}),
        'm3_task': (np.load(ROOT / 'summary_m3/resid_cache_pids.npy'),) * 2 + ({},),
        'all9108': (pd.read_parquet(R10 / 'cohort/papers.parquet').paper_id.to_numpy(),) * 2 + ({},),
        'pairs_k2': (pd.read_parquet(ROOT / 'config/pairs.parquet').paper_id.to_numpy(),) * 2 + ({'k': 2, 'seed': 1314},)}
out = {}
for name, (pid, lab, kw) in sets.items():
    f, g = c13.group_folds(lab, **kw); out[name + '_pid'] = np.asarray(pid).astype(str); out[name + '_fold'] = f; out[name + '_team'] = g
    print(name, len(pid), 'teams', len(np.unique(g)), 'fold sizes', np.bincount(f), flush=True)
host = socket.gethostname(); p = ROOT / f'foldaudit_2026-10-30/variants/{host}.npz'; np.savez(p, **out); print('saved', p, 'from', src)
