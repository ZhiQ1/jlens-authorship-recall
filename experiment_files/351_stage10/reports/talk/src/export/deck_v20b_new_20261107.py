"""2026-11-07 ~02:20: deck_v20b_new + slide 72 target − control bullet = user decision B (numbers from sync_20261107/apply_20261107c.py,
which recomputed them from 381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv). deck_v20b_new.py is not edited."""
from deck_v20b_new import *          # noqa: F401,F403
import deck_v20b_new as _M
a = _M.BY['alltok']
i = next(k for k, b in enumerate(a['left']) if b[0] == B('Target − control: '))
a['left'][i] = [B('Target − control (five false titles, per-donor exclusion): '),
                T('given-name first token positive from L16, surname from L24 (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 [−0.002, +0.030]); with false_0 only the surname is not significant before L56 — earlier statement superseded'),
                S('(within bin; b1_e4b5_report.md, per-donor)')]
