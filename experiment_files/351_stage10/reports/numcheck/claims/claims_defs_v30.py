"""claims_defs v30 (2026-11-20): v29 + exploratory citation median split (381_stage13/summary_explore_citesplit_20261120/).
New ids 'A30-'.  Run with:  CLAIMS_DEFS=claims_defs_v30 bash claims_run.sh"""
from claims_defs_v29 import *          # noqa: F401,F403
from claims_defs_v29 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A30-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'
R = '381_stage13/summary_explore_citesplit_20261120/recovery_by_half.csv'
L = '381_stage13/summary_explore_citesplit_20261120/lens_tc_by_half.csv'
CF = '按引用数分半（探索性，事后），Stage 11 样本 1,186 篇，中位数 31，团队整群 bootstrap 2,000 次；'
HL = [r'高 − 低 ', r'high − low ']
def tri(cid, stmt, f, col_lo_hi, w, pats, n, estrx):
    # lo / hi patterns are pinned to the written estimate (estrx) so that other numbers after the same prefix are not picked up
    est, lo, hi = col_lo_hi
    A(cid, stmt, csv(f, est, **w), CF, n, 3, [p + '#(?= \\[)' for p in pats])
    A(cid + '-lo', stmt + '（下限）', csv(f, lo, **w), CF, n, 3, [p + estrx + r' \[#(?=, )' for p in pats], sign=False)
    A(cid + '-hi', stmt + '（上限）', csv(f, hi, **w), CF, n, 3, [p + estrx + r' \[' + SN + r', #\]' for p in pats], sign=False)
RC = ('R', 'lo', 'hi')
tri('R48d', '分半：R(L48) 高 − 低（全部）', R, RC, dict(half='high - low', group='all', title='average', layer=48), [r'L48 低半 0\.865 \[0\.843, 0\.886\]、高半 0\.789 \[0\.770, 0\.808\]，高 − 低 ', r'high − low '], '1,186 篇', r'−0\.076')
tri('R52d', '分半：R(L52) 高 − 低（全部）', R, RC, dict(half='high - low', group='all', title='average', layer=52), [r'L52 高 − 低 ', r'L52 '], '1,186 篇', r'−0\.018')
tri('R48tc', '分半：R(L48) target − control 的高 − 低', R, RC, dict(half='high - low', group='target - control', title='average', layer=48), [r'L48 高 − 低 ', r'\(L48 '], '1,186 篇', r'−0\.006')
tri('R48lo', '分半：R(L48) 低半（全部）', R, RC, dict(half='low', group='all', title='average', layer=48), [r'L48 低半 ', r'L48 low '], '594 篇', r'0\.865')
tri('R48hi', '分半：R(L48) 高半（全部）', R, RC, dict(half='high', group='all', title='average', layer=48), [r'高半 ', r'high '], '592 篇', r'0\.789')
tri('J53', '分半：J-lens L53 target − control 的高 − 低', L, ('tc', 'lo', 'hi'), dict(sample='stage11_1186', readout='jlens_public', layer=53, measure='spec_mean_nlr', half='high - low'), [r'L53 '], '1,186 篇', r'−0\.073')
tri('J48full', '分半全队列补充：J-lens L48 高 − 低（中位数 66）', L, ('tc', 'lo', 'hi'), dict(sample='supplement_full_cohort', readout='jlens_public', layer=48, measure='spec_mean_nlr', half='high - low'), [r'L48 '], '6,841 篇', r'−0\.065')
