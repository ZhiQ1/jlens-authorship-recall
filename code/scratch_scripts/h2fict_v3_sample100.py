#!/usr/bin/env python3
"""v3: plan's manual review sample: 100 selected titles, 5 per Stage 11 citation bin x group (10 x 2 x 5),
fixed seed 20261119. Writes sample100_auto.md (automatic checks) and sample100_selected.csv; the manual judgement is
added by hand into sample100.md. Excluded papers are not eligible (excluded.csv, exclusions_by_bin_group.csv)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v3')
SEED = 20261119
sel = pd.read_csv(OUT / 'selected.csv')
rng = np.random.default_rng(SEED)
pick = pd.concat([g.iloc[rng.choice(len(g), size=min(5, len(g)), replace=False)] for _, g in sel.groupby(['s11_bin', 'group'], sort=True)])
order = sorted(pick.s11_bin.unique(), key=lambda b: int(b.split('-')[0]))
pick = pick.assign(_b=pick.s11_bin.map(order.index)).sort_values(['_b', 'group', 'paper_id']).drop(columns='_b').reset_index(drop=True)
pick.to_csv(OUT / 'sample100_selected.csv', index=False)
esc = lambda s: str(s).replace('|', '\\|')
L = ['| # | bin / grp | field, year | true title | fictitious (selected) | tok f/t | j2 | cos (para) | NLI f/b | Crossref best (j2; top) | r |',
     '|---|---|---|---|---|---|---|---|---|---|---|']
for i, r in pick.iterrows():
    L.append(f'| {i + 1} | {r.s11_bin} / {r.group[0].upper()} | {r.field}, {r.year} | {esc(r.title)} | {esc(r.cand)} | {r.ntok}/{r.ntok_true} | {r.j2_true:.2f} | '
             f'{r.cos_true:.2f} ({r.cos_para:.2f}) | {r.nli_fwd:.2f}/{r.nli_bwd:.2f} | {esc(r.ext_title)[:70]} ({r.ext_j2:.2f}; {int(r.ext_rows)}) | {r["round"]} |')
(OUT / 'sample100_auto.md').write_text('\n'.join(L) + '\n')
print(len(pick)); print('\n'.join(L[:5]))
