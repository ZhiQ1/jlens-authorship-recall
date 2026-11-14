"""Exploratory (探索性), post hoc: diagnostics for fabricated_names_20261114.py (cohort coauthor connectivity, homonym drive)."""
import sys, pandas as pd
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/14_groups')
import fabricated_names_20261114 as f
O = '/scratch/zhang.zhiqi2/jlens/391_groups/summary_fabricated_20261114/'
F = pd.read_parquet(O + 'fabricated_names.parquet'); U = F[~F.dup_in_paper]
L = ['# diagnostics (exploratory, post hoc)', '', 'cls_si x cls_si_rare:', pd.crosstab(U.cls_si, U.cls_si_rare).to_string(), '']
P = pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet', columns=['paper_id', 'authors', 'field'])
for name, ak, mf in (('si', f.akey_si, None), ('si_rare', f.akey_si, 3), ('full', f.akey_full, None)):
    K, CO, FK, AK, field, Kown, common = f.build(P, ak, mf)
    s = pd.Series([len(CO[p]) for p in K])
    L.append(f'{name}: papers with >=1 cohort neighbour (shared key) {int((s > 0).sum())} of {len(s)}; median coauthor-key set {s.median()}; mean {s.mean():.1f}; common keys {len(common)}')
c = U[U.cls_si == 'coauthor']
L += ['', f'si coauthor names: {len(c)} in {c.paper_id.nunique()} papers; top surnames:', c.norm.str.split().str[-1].value_counts().head(15).to_string()]
open(O + 'diagnostics.txt', 'w').write('\n'.join(L)); print('\n'.join(L))
