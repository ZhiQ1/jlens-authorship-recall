#!/usr/bin/env python3
"""Pick 20 of the 60 checked papers (stratified: 10 bins x target/control x 1, fixed seed) and write
sample20_auto.md (table with automatic checks; manual judgement column filled in by hand in sample20.md)
plus sample20.csv (all candidates of those 20 papers, for review)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious')
SEED = 20261117 + 20
sel = pd.read_csv(OUT / 'selected.csv'); allc = pd.read_csv(OUT / 'candidates_checked.csv')
rng = np.random.default_rng(SEED)
pick = pd.concat([g.iloc[[rng.integers(len(g))]] for _, g in sel.groupby(['s11_bin', 'group'], sort=True)])
order = sorted(pick.s11_bin.unique(), key=lambda b: int(b.split('-')[0]))
pick = pick.assign(_b=pick.s11_bin.map(order.index)).sort_values(['_b', 'group']).drop(columns='_b').reset_index(drop=True)
pick.to_csv(OUT / 'sample20_selected.csv', index=False)
allc[allc.paper_id.isin(pick.paper_id)].to_csv(OUT / 'sample20_all_candidates.csv', index=False)
esc = lambda s: str(s).replace('|', '\\|')
L = ['| # | bin / group | field | true title | fictitious (selected) | tok f/t | j2 true | cos true (para / false_0) | NLI f/b | nearest cohort title (j2; cos) | rank of T | Crossref best (j2) | auto |',
     '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for i, r in pick.iterrows():
    L.append(f'| {i + 1} | {r.s11_bin} / {r.group} | {r.field} | {esc(r.title)} | {esc(r.cand)} | {r.ntok}/{r.ntok_true} | {r.j2_true:.2f} | '
             f'{r.cos_true:.2f} ({r.cos_para:.2f} / {r.cos_false0:.2f}) | {r.nli_fwd:.2f}/{r.nli_bwd:.2f} | '
             f'{esc(r.nn_j2_title)[:90]} ({r.nn_j2:.2f}; nn-cos {r.nn_cos:.2f}) | {r.rank_true} | {esc(r.get("ext_title", ""))[:90]} ({r.get("ext_j2", float("nan")):.2f}) | '
             f'{"ok" if r.auto_ok else "FAIL: " + str(r.fails)} ({r.n_cand_ok}/4 ok) |')
(OUT / 'sample20_auto.md').write_text('\n'.join(L) + '\n')
print('\n'.join(L))
