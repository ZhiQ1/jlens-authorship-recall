"""Stage 13 (2026-10-28, review): re-run the Stage 11 title-token probe E4b and its controls (report 6.12, Stage 12 X1)
with author-team group folds, next to the original per-paper folds, without touching any other line of their code:
the original functions are loaded from their source files and only the fold line is replaced.
  E4b      : stage10_extra_r0r1.probe   (same as stage11_analyze.probe_section; alpha chosen on fold 0; all probe layers)
  controls : stage12_cpu.probe_controls (gold permutations, false-title training; L24/40/56)
SPLIT=paper must reproduce the published numbers exactly (sanity check); SPLIT=group uses stage13_cpu.group_folds.
Outputs: 381_stage13/summary_cpu_group/E4b_{paper,group}.csv, X1controls_{paper,group}.csv, reports/e4b_split_compare.md
"""
import importlib.util, os, sys, types
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); OUT = ROOT / 'summary_cpu_group'; OUT.mkdir(parents=True, exist_ok=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
ORIG = 'fold = np.random.default_rng(11).integers(0, folds, len(pid))'

def patched(module, fname, split):
    import inspect, textwrap
    src = textwrap.dedent(inspect.getsource(getattr(module, fname))); assert src.count(ORIG) == 1, fname
    new = src.replace(ORIG, 'fold = _FOLD(pid, folds)')
    ns = dict(vars(module)); ns['_FOLD'] = (lambda pid, k: np.random.default_rng(11).integers(0, k, len(pid))) if split == 'paper' else (lambda pid, k: c13.group_folds(pid, k=k)[0])
    exec(compile(new, f'<{fname}:{split}>', 'exec'), ns); return ns[fname]

r0 = load(H / '10_stage10/stage10_extra_r0r1.py', 'r0'); s12c = load(H / '12_stage12/stage12_cpu.py', 's12c')
papers = pd.read_parquet(Path('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet'))
ds = pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/summary_title/paper_title_contrasts.parquet', columns=['paper_id', 'group_tight', 'recall_level', 'citation_bin']).drop_duplicates('paper_id')
L = ['# E4b and its controls: per-paper folds vs author-team group folds', '']
for split in ('paper', 'group'):
    r0.rng = np.random.default_rng(3513); r0.a11.rng = np.random.default_rng(3611)
    S = OUT / f'tmp_{split}'; S.mkdir(exist_ok=True); lines = []
    patched(r0, 'probe', split)(lines, S, ds)
    pd.read_csv(S / 'E4b_probe_by_recall.csv').assign(split=split).to_csv(OUT / f'E4b_{split}.csv', index=False)
    s12c.rng = np.random.default_rng(3712); s12c.S = S
    patched(s12c, 'probe_controls', split)(papers)
    pd.read_csv(S / 'X1_probe_controls.csv').assign(split=split).to_csv(OUT / f'X1controls_{split}.csv', index=False)
    print('done', split, flush=True)
E = pd.concat([pd.read_csv(OUT / f'E4b_{s}.csv') for s in ('paper', 'group')]); X = pd.concat([pd.read_csv(OUT / f'X1controls_{s}.csv') for s in ('paper', 'group')])
f = lambda v, lo, hi: f'{v:+.3f} [{lo:+.3f}, {hi:+.3f}]'
L += ['## E4b title-token probe: target - control within bin (pooled) and target / control means', '', '| layer | split | target - control | target (A+C mean) | control |', '|---|---|---|---|---|']
for _, r in E.sort_values(['layer', 'split'], ascending=[True, False]).iterrows():
    L.append(f"| L{int(r.layer)} | {r.split} | {f(r.tc_pooled, r.tc_pooled_lo, r.tc_pooled_hi)} | {(r.T0 * r.T0_n + r.T1 * r.T1_n) / (r.T0_n + r.T1_n):+.3f} | {(r.C0 * r.C0_n + r.C1 * r.C1_n) / (r.C0_n + r.C1_n):+.3f} |")
L += ['', '## Controls (report 6.12): title-specific probe signal, all papers, and target - control', '', '| layer | control | split | spec, all papers | target - control |', '|---|---|---|---|---|']
for _, r in X.sort_values(['layer', 'control', 'split'], ascending=[True, True, False]).iterrows():
    L.append(f"| L{int(r.layer)} | {r.control} | {r.split} | {f(r.spec_all, r.spec_all_lo, r.spec_all_hi)} | {f(r.tc, r.tc_lo, r.tc_hi)} |")
pub = pd.read_csv('/scratch/zhang.zhiqi2/jlens/371_stage12/summary_cpu/X1_probe_controls.csv'); xp = X[X.split == 'paper'].merge(pub, on=['layer', 'control'], suffixes=('', '_pub'))
L += ['', f"Sanity check: paper-split controls vs the published 6.12 numbers, max |difference| of spec_all = {np.abs(xp.spec_all - xp.spec_all_pub).max():.4f}"]
pe = pd.read_csv('/scratch/zhang.zhiqi2/jlens/361_stage11/summary_r0r1/E4b_probe_by_recall.csv'); ep = E[E.split == 'paper'].merge(pe, on='layer', suffixes=('', '_pub'))
L += [f"Sanity check: paper-split E4b vs the published R0/R1 E4b, max |difference| of the pooled target - control = {np.abs(ep.tc_pooled - ep.tc_pooled_pub).max():.4f}"]
(ROOT / 'reports/e4b_split_compare.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))
