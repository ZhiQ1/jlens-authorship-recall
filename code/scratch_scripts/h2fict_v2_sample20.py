#!/usr/bin/env python3
"""v2: pick 20 of the selected papers (1 per Stage 11 citation bin x group, new fixed seed 20261138) and write
sample20_auto.md (automatic checks; manual judgement is added by hand into sample20.md), sample20_selected.csv,
sample20_all_candidates.csv. Papers excluded under the rule are not eligible (they are listed in excluded.csv)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v2')
SEED = 20261138
sel = pd.read_csv(OUT / 'selected.csv'); allc = pd.read_csv(OUT / 'all_checked.csv')
rng = np.random.default_rng(SEED)
pick = pd.concat([g.iloc[[rng.integers(len(g))]] for _, g in sel.groupby(['s11_bin', 'group'], sort=True)])
order = sorted(pick.s11_bin.unique(), key=lambda b: int(b.split('-')[0]))
pick = pick.assign(_b=pick.s11_bin.map(order.index)).sort_values(['_b', 'group']).drop(columns='_b').reset_index(drop=True)
pick.to_csv(OUT / 'sample20_selected.csv', index=False)
allc[allc.paper_id.isin(pick.paper_id)].to_csv(OUT / 'sample20_all_candidates.csv', index=False)
esc = lambda s: str(s).replace('|', '\\|')
L = ['| # | bin / group | field, year | true title | fictitious (selected) | tok f/t | j2 true | cos true (para / false_0) | NLI f/b | pattern | nearest cohort title (j2) | Crossref best of top 3 (j2) | round; ok/cands |',
     '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for i, r in pick.iterrows():
    L.append(f'| {i + 1} | {r.s11_bin} / {r.group} | {r.field}, {r.year} | {esc(r.title)} | {esc(r.cand)} | {r.ntok}/{r.ntok_true} | {r.j2_true:.2f} | '
             f'{r.cos_true:.2f} ({r.cos_para:.2f} / {r.cos_false0:.2f}) | {r.nli_fwd:.2f}/{r.nli_bwd:.2f} | {r.pattern:.2f} | '
             f'{esc(r.nn_j2_title)[:80]} ({r.nn_j2:.2f}) | {esc(r.ext_title)[:90]} ({r.ext_j2:.2f}) | r{r["round"]}; {r.n_cand_ok}/{r.n_cand} |')
(OUT / 'sample20_auto.md').write_text('\n'.join(L) + '\n')
print('\n'.join(L))
