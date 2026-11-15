"""Addendum 18 item 3, decision quantities (new file; analysis code imported by path, unchanged).
Same data, same 2,000 team draws (default_rng(13) over the sorted union of papers) as stage13_e1x6_extra_analyze_20261114.py.
5-title mean R(l), all papers, layers L40..L52: half-arrival = first l with 95% lower bound >= 0.5; full-arrival = first l with lower >= 0.9;
a = first l with lower >= 0.1; steepest single-layer increase R(l) - R(l-1) (consecutive measured layers) with CI on the same draws."""
import importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd
H = Path.home() / 'jlens_work'
sp = importlib.util.spec_from_file_location('ea', H / '13_stage13/stage13_e1x6_extra_analyze_20261114.py'); A = importlib.util.module_from_spec(sp); sp.loader.exec_module(A)
R13 = A.R13; OUT = R13 / 'summary_e1x6_extra_20261114'
c13 = A.load(H / '13_stage13/stage13_cpu.py', 'c13')
papers = pd.read_parquet(A.R10 / 'cohort/papers.parquet'); _, team = c13.group_folds(papers.paper_id.to_numpy()); TEAM = dict(zip(papers.paper_id, team))
toks = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id')
src = {'false_0': A.R11 / 'raw/patch'} | {t: R13 / 'raw/xf_patch' / t for t in A.TITLES[1:]}
pp = {}
for t in A.TITLES:
    tt, ly = A.merge(A.load_dir(src[t]), A.load_dir(R13 / 'raw/e1x6_extra_20261114' / t))
    pp[t] = tt.assign(paper_id=toks.loc[tt.index].paper_id.to_numpy()).groupby('paper_id').mean()
allp = sorted(set().union(*[set(p.index) for p in pp.values()])); codes, uniq = pd.factorize(pd.Series([TEAM[p] for p in allp]))
cnt = np.random.default_rng(13).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=A.NB).astype(np.float64)
Wall = pd.DataFrame(cnt[:, codes].T, index=allp)
L = list(range(40, 53)); est, bt = {}, {}
for l in L:
    es, bs = [], []
    for t in A.TITLES:
        s = pp[t]; W = Wall.loc[s.index].to_numpy(); den = (s['true'] - s['false']).to_numpy(); num = (s[f'p{l}'] - s['false']).to_numpy(); ok = np.isfinite(num)
        es.append(num[ok].mean() / den[ok].mean()); bs.append((num[ok] @ W[ok]) / (den[ok] @ W[ok]))
    est[l] = float(np.mean(es)); bt[l] = np.mean(bs, 0)
lo = {l: float(np.percentile(bt[l], 2.5)) for l in L}; hi = {l: float(np.percentile(bt[l], 97.5)) for l in L}
first = lambda thr: next((l for l in L if lo[l] >= thr), None)
inc = [dict(frm=L[i - 1], to=L[i], d=est[L[i]] - est[L[i - 1]], lo=float(np.percentile(bt[L[i]] - bt[L[i - 1]], 2.5)), hi=float(np.percentile(bt[L[i]] - bt[L[i - 1]], 97.5))) for i in range(1, len(L))]
st = max(inc, key=lambda r: r['d'])
res = dict(curve={l: [est[l], lo[l], hi[l]] for l in L}, a_lower_ge_0p1=first(0.1), half_arrival=first(0.5), full_arrival=first(0.9), steepest=st, increments=inc)
(OUT / 'arrival_decision.json').write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'curve'}, indent=1))
