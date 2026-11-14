"""claims_defs v19 (2026-11-14): v18 + exclusions for the new exploratory section 'pd-sayable' (team-CI pooled 0.207 [0.196, 0.220];
per-bin R values), which are not the published claims S10-L63-lo / X6-min. Run with: CLAIMS_DEFS=claims_defs_v19 bash claims_run.sh"""
from claims_defs_v18 import *          # noqa: F401,F403
from claims_defs_v18 import C
EX = {'S10-L63-lo': r'10 档合并', 'X6-min': r'各档 R\(L48\)'}
for c in C:
    if c['id'] in EX:
        c['excl'] = EX[c['id']] if not c.get('excl') else c['excl'] + '|' + EX[c['id']]
