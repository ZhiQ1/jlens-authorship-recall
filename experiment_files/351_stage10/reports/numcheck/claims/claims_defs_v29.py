"""claims_defs v29 (2026-11-20): v28 + addendum 20 (H2 fictitious titles, locked confirmatory):
phi_T, Rbar_T, phi_C, Rbar_C with CIs (391_groups/summary_a20/primary_secondary_sensitivity.csv).
New ids 'A29-'.  Run with:  CLAIMS_DEFS=claims_defs_v29 bash claims_run.sh"""
from claims_defs_v28 import *          # noqa: F401,F403
from claims_defs_v28 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A29-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'
F = '391_groups/summary_a20/primary_secondary_sensitivity.csv'
CF = '补充 20 虚构标题（锁定），最终输出 L63，团队整群 bootstrap 2,000 次；'
for g, lab, n in [('T', 'PRIMARY target final L63', '566 篇 target'), ('C', 'S1 control final L63', '561 篇 control')]:
    P = [r'φ_' + g + r' ?=? ?#(?= \[)', r'φ_' + g + r' #(?=[，、；）])'] + ([r'(?:recovers|恢复 φ_T =?) ?#(?= \[0\.723)', r'^#(?= \[0\.723, 0\.778\])'] if g == 'T' else [])
    A('phi' + g, '补充 20：φ_' + g, csv(F, 'phi', label=lab), CF, n, 3, [p for p in P if not p.startswith('^')], sign=False)
    A('phi' + g + '-lo', '同上（下限）', csv(F, 'phi_lo', label=lab), CF, n, 3, [r'φ_' + g + r' ?=? ?' + SN + r' \[#(?=, )'], sign=False)
    A('phi' + g + '-hi', '同上（上限）', csv(F, 'phi_hi', label=lab), CF, n, 3, [r'φ_' + g + r' ?=? ?' + SN + r' \[' + SN + r', #\]'], sign=False)
    A('R' + g, '补充 20：R̄_' + g, csv(F, 'Rbar', label=lab), CF, n, 3, [r'R̄_' + g + r' ?=? ?#(?= \[)', r'R̄_' + g + r' #(?=[，、；）])'])
    A('R' + g + '-lo', '同上（下限）', csv(F, 'R_lo', label=lab), CF, n, 3, [r'R̄_' + g + r' ?=? ?' + SN + r' \[#(?=, )'], sign=False)
    A('R' + g + '-hi', '同上（上限）', csv(F, 'R_hi', label=lab), CF, n, 3, [r'R̄_' + g + r' ?=? ?' + SN + r' \[' + SN + r', #\]'], sign=False)
