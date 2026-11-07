"""Summarise the all-token permutation controls (stage13_alltok_controls.py): all-paper (target + control, title reuse dropped)
mean with team-cluster 95% CI (2,000 draws, archived team ids, as stage13_alltok_report.py), per run x layer x control.
Parity: the 'spec' column must equal stage13_alltok_probe.py's perpaper spec (WARN only).
Writes summary_alltok/alltok_controls.csv and appends section 7 to reports/e4b_alltok.md (once)."""
import importlib.util
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; R10 = Path('/scratch/zhang.zhiqi2/jlens/351_stage10'); R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
NB = 2000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight'])
_, TEAMS = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, TEAMS)); GT = papers.set_index('paper_id').group_tight


def mean_cluster(pids, x, seed=2):
    x = np.asarray(x, float); ok = ~np.isnan(x); pids, x = np.asarray(pids)[ok], x[ok]
    t = pd.Series([TEAM[p] for p in pids]); codes, uniq = pd.factorize(t); n = len(uniq)
    W = np.random.default_rng(seed).multinomial(n, np.full(n, 1 / n), size=NB).astype(np.float32)[:, codes]
    return x.mean(), *np.percentile((W @ x) / np.maximum(W.sum(1), 1e-9), [2.5, 97.5]), len(x)


rows, par = [], []
for f in sorted((R13 / 'summary_alltok/controls').glob('perpaper_*.parquet')):
    run, l = f.stem[len('perpaper_'):].rsplit('_L', 1); l = int(l)
    d = pd.read_parquet(f); d = d[(~d.dropped) & d.paper_id.map(GT).isin(['target', 'control']).to_numpy()]
    for col, name in (('spec', 'probe (real gold)'), ('spec_any', 'gold = random other paper'), ('spec_field', 'gold = random paper of the same field')):
        m, lo, hi, n = mean_cluster(d.paper_id.to_numpy(), d[col].to_numpy())
        rows.append(dict(run=run, layer=l, control=name, est=m, lo=lo, hi=hi, n=n))
    pf = R13 / f'summary_alltok/probe/perpaper_{run}_L{l}.parquet'
    if pf.exists():
        q = pd.read_parquet(pf).set_index('paper_id').spec; dd = pd.read_parquet(f).set_index('paper_id').spec
        par.append(dict(run=run, layer=l, max_abs_diff=float((dd - q.loc[dd.index]).abs().max())))
T = pd.DataFrame(rows); T.to_csv(R13 / 'summary_alltok/alltok_controls.csv', index=False)
PAR = pd.DataFrame(par)
fm = lambda r: f'{r.est:+.3f} [{r.lo:+.3f}, {r.hi:+.3f}]' + ('*' if r.lo > 0 or r.hi < 0 else '')
L = ['', '## 7. Permutation controls (added 2026-11-05 on user request; same definitions as the confirmatory E4b controls, stage12_cpu.probe_controls, rng 3712)', '',
     'spec_ctrl = probe(true title) - probe(false_0 title), scored against the gold tokens of another paper; target + control papers, title reuse dropped; team CI. * = CI excludes 0.', '']
for ctrl in ['gold = random other paper', 'gold = random paper of the same field', 'probe (real gold)']:
    s = T[T.control == ctrl]; lays = sorted(s.layer.unique())
    L += [f'### {ctrl}', '', '| run | ' + ' | '.join(f'L{x}' for x in lays) + ' |', '|---|' + '---|' * len(lays)]
    for run in ['e4b_parity', 'first_alltok', 'initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']:
        r = s[s.run == run].set_index('layer')
        if len(r): L.append(f'| {run} | ' + ' | '.join(fm(r.loc[x]) if x in r.index else '' for x in lays) + ' |')
    L.append('')
if len(PAR): L += [f'Parity of the real-gold column with stage13_alltok_probe.py: max per-paper |diff| = {PAR.max_abs_diff.max():.2e} ' +
                   ('(OK)' if PAR.max_abs_diff.max() < 1e-6 else '(WARN)'), '']
rep = R13 / 'reports/e4b_alltok.md'; txt = rep.read_text()
if '## 7. Permutation controls' in txt: txt = txt[:txt.index('\n## 7. Permutation controls')]
rep.write_text(txt.rstrip('\n') + '\n' + '\n'.join(L) + '\n'); print('\n'.join(L))
