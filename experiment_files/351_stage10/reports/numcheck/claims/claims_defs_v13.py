"""claims_defs v13 (2026-11-09 g): v12 (unchanged file) + the batch-2 numbers of documents round g (sync_20261108c_manifest.md "round g").
New ids 'A13-'. Sources (381_stage13/summary_b2B/ csv files beside the reports b2_e1noise.md, b2_e1t5.md, b2_e1t5_numden.md, b2_x3role.md,
b2_m3tok.md): e1noise_recovery.csv (group-level |b15 − b1| E1 recovery difference), e1noise_token.csv (token p99 |Δ log10(1/rank)|),
e1t5_mean5.csv (five-title E1t recovery, team CI, false_0), e1t5_numden_tc.csv (num / den T − C, team CI), e1t5_tc.csv (recovery T − C),
x3role_recovery.csv (X3 behaviour by token role, test split, primary set, lexical_neighbour_D), b2_m3tok.md table "Target - control within
citation bin" (team CI) via mdcell.  Run with:  CLAIMS_DEFS=claims_defs_v13 bash claims_run.sh"""
import pandas as pd
from claims_defs_v12 import *          # noqa: F401,F403
from claims_defs_v12 import C, csv, md, MANUAL
from claims_defs_v5 import A as _A5, py
from claims_lib import JL


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A13-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
B = '381_stage13/summary_b2B/'
# ---- 2-4 E1 batch rounding noise
NR, NT = B + 'e1noise_recovery.csv', B + 'e1noise_token.csv'
A('noise-max', '2-4：组级 E1 恢复比例 |batch 15 − batch 1| 最大', py(lambda: pd.read_csv(JL / NR).diff_b15_minus_b1.abs().max(), 'e1noise_recovery.csv |diff_b15_minus_b1| 最大', [NR]), '只给分布、无 CI', '2 个分片 × 50 篇', 4,
  [r'差最大 #(?=（L40）)', r'组级最大 #', r'(?:largest|max(?:imum)?) (?:group-level )?#(?= \(L40\))'], sign=False)
A('noise-L52', '2-4：L52 的组级差（最大）', py(lambda: (lambda d: d[d.layer == 52].diff_b15_minus_b1.abs().max())(pd.read_csv(JL / NR)), 'e1noise_recovery.csv L52 |diff| 最大', [NR]), '只给分布', '—', 3,
  [r'L52 约 #', r'L52 about (?P<v>0\.0\d+)', r'L52 ≈ ?(?P<v>0\.0\d+)'], sign=False)
A('noise-p99', '2-4：单 token log10(1/名次) 差 p99 最高', py(lambda: pd.read_csv(JL / NT).p99_abs_dnlr.max(), 'e1noise_token.csv p99_abs_dnlr 最大', [NT]), '—', '—', 2,
  [r'p99 最高 #', r'p99 (?:up to|at most) #'], sign=False)
# ---- 2-8 E1t five titles
E5 = B + 'e1t5_mean5.csv'
for L in (24, 40, 48, 52):
    W = dict(group='all', layer=L)
    pre = r'全部论文 L24 ' if L == 24 else r'(?:全部论文 L24 ' + NUM + r' \[' + NUM + ', ' + NUM + r'\]（false_0 版 ' + NUM + r'）|（' + NUM + r'）)[^；]{0,40}?、L%d ' % L
    A('e1t5-L%d' % L, 'E1t 五个假标题平均（全部论文）L%d' % L, csv(E5, 'recovery_mean5', **W), 'e1t5_mean5.csv recovery_mean5', '1,186 篇', 3, [pre + '#'], sign=False)
    A('e1t5-L%d-f0' % L, 'E1t false_0 版 L%d' % L, csv(E5, 'recovery_false0', **W), 'e1t5_mean5.csv recovery_false0', '1,186 篇', 3,
      [pre + NUM + r'(?: \[' + NUM + ', ' + NUM + r'\])?（(?:false_0 版 )?#'], sign=False)
A('e1t5-L24-lo', 'E1t 五个假标题 L24 下限（团队）', csv(E5, 'lo_team', group='all', layer=24), 'e1t5_mean5.csv lo_team', '1,186 篇', 3, [r'全部论文 L24 ' + NUM + r' \[#'], sign=False)
A('e1t5-L24-hi', 'E1t 五个假标题 L24 上限（团队）', csv(E5, 'hi_team', group='all', layer=24), 'e1t5_mean5.csv hi_team', '1,186 篇', 3, [r'全部论文 L24 ' + NUM + r' \[' + NUM + ', #\]'], sign=False)
ND = B + 'e1t5_numden_tc.csv'


def nd(q, L, col):
    return csv(ND, col, quantity=q, version='mean5', layer=L)


for col, suf, pat in [('tc', '', r'分母 T − C #'), ('lo_team', '-lo', r'分母 T − C ' + NUM + r' \[#'), ('hi_team', '-hi', r'分母 T − C ' + NUM + r' \[' + NUM + ', #\]'),
                      ('target', '-T', r'（target #(?=、control)'), ('control', '-C', r'（target ' + NUM + '、control #')]:
    A('e1t5-den' + suf, 'E1t 分母 T − C（mean5）' + suf, nd('den', 24, col), 'e1t5_numden_tc.csv den mean5（各层相同）', 'target 593 / control 593', 3, [pat], sign=(suf in ('', '-lo', '-hi')))
for L, lab in [(24, r'分子 T − C L24 '), (40, r'分子 T − C L24 ' + NUM + r' \[' + NUM + ', ' + NUM + r'\]、L40 '), (52, r'分子 T − C L24 [^；]*?、L52 ')]:
    A('e1t5-num-L%d' % L, 'E1t 分子 T − C L%d（mean5）' % L, nd('num', L, 'tc'), 'e1t5_numden_tc.csv num mean5 tc', '593 / 593', 4, [lab + '#'])
    A('e1t5-num-L%d-lo' % L, '同上下限（团队）', nd('num', L, 'lo_team'), 'lo_team', '593 / 593', 4, [lab + NUM + r' \[#'])
    A('e1t5-num-L%d-hi' % L, '同上上限（团队）', nd('num', L, 'hi_team'), 'hi_team', '593 / 593', 4, [lab + NUM + r' \[' + NUM + ', #\]'])
TC = B + 'e1t5_tc.csv'
for col, suf, pat in [('tc_mean5', '', r'比例 T − C L24 #'), ('lo_team', '-lo', r'比例 T − C L24 ' + NUM + r' \[#'), ('hi_team', '-hi', r'比例 T − C L24 ' + NUM + r' \[' + NUM + ', #\]')]:
    A('e1t5-ratio' + suf, 'E1t 恢复比例 T − C L24（mean5）' + suf, csv(TC, col, layer=24), 'e1t5_tc.csv', '593 / 593', 3, [pat])
# ---- 2-3 X3 by token role
XR = B + 'x3role_recovery.csv'
XW = dict(stratum='all', set='primary', subset='all', split='test', false='lexical_neighbour_D', group='all')


def xr(role, col):
    return csv(XR, col, role=role, **XW)


A('x3r-all', 'X3 行为（全部 token）恢复比', xr('ALL', 'ratio'), 'x3role_recovery.csv role = ALL', '测试集 552 篇', 3, [r'全部 token 的结果（#'], sign=False)
A('x3r-all-lo', '同上下限', xr('ALL', 'lo'), 'lo', '552 篇', 3, [r'全部 token 的结果（' + NUM + r' \[#'], sign=False)
A('x3r-all-hi', '同上上限', xr('ALL', 'hi'), 'hi', '552 篇', 3, [r'全部 token 的结果（' + NUM + r' \[' + NUM + ', #\]'], sign=False)
ROLES = ['initial', 'given_first', 'given_cont', 'surname_first', 'surname_cont']


def _roles(f):
    d = pd.read_csv(JL / XR)
    for k, v in XW.items():
        d = d[d[k] == v]
    return f(d[d.role.isin(ROLES)].ratio)


A('x3r-min', 'X3 按角色恢复比最小', py(lambda: _roles(min), 'x3role_recovery.csv 5 个角色 ratio 最小', [XR]), '—', '测试集', 3, [r'恢复比在 #–', r'all roles #–', r'roles #–'], sign=False)
A('x3r-max', 'X3 按角色恢复比最大', py(lambda: _roles(max), '同上最大', [XR]), '—', '测试集', 3, [r'恢复比在 ' + NUM + '–#', r'all roles ' + NUM + '–#', r'roles ' + NUM + '–#'], sign=False)
for role, lab in [('initial', r'首字母 '), ('surname_first', r'姓的第一个 token ')]:
    A('x3r-%s' % role, 'X3 角色 %s' % role, xr(role, 'ratio'), 'ratio', '测试集', 3, [r'(?<=（)' + lab + r'#(?= \[)', r'[，、]' + lab + r'#(?= \[)'], sign=False)
    A('x3r-%s-lo' % role, '同上下限', xr(role, 'lo'), 'lo', '测试集', 3, [r'(?:（|，)' + lab + NUM + r' \[#'], sign=False)
    A('x3r-%s-hi' % role, '同上上限', xr(role, 'hi'), 'hi', '测试集', 3, [r'(?:（|，)' + lab + NUM + r' \[' + NUM + ', #\]'], sign=False)
# ---- 2-10 M3 all-token
M3 = '381_stage13/reports/b2_m3tok.md'
H = r'Target - control within citation bin'


def m3(score, papers, col, part='est'):
    return md(M3, H, col=col, part=part, row={'score': score, 'papers': papers})


CO = 'all cohort target/control'
A('m3-all', 'M3 全部 token 行为分数 target − control', m3('m3_alltok', CO, 'estimate'), 'b2_m3tok.md 引用档内，团队区间', '10 档', 3, [r'target − control 为 #(?= \[\+0\.215)', r'M3 all-token (?:score )?#'])
A('m3-all-lo', '同上下限（团队）', m3('m3_alltok', CO, 'team CI', 'est'), 'team CI', '10 档', 3, [r'target − control 为 ' + NUM + r' \[#(?=, \+0\.25)'])
A('m3-all-hi', '同上上限（团队）', m3('m3_alltok', CO, 'team CI', 'lo'), 'team CI', '10 档', 3, [r'target − control 为 ' + NUM + r' \[' + NUM + r', #\]（团队区间'])
A('m3-sur', 'M3 姓的第一个 token', m3('m3_role_surname_first', CO, 'estimate'), 'b2_m3tok.md', '10 档', 3, [r'10 档），姓的第一个 token #'])
A('m3-ini', 'M3 首字母', m3('m3_role_initial', CO, 'estimate'), 'b2_m3tok.md', '10 档', 3, [r'姓的第一个 token \+0\.\d+，首字母 #'])
A('m3-first', 'M3 第一作者首 token（已发表）', m3('m3_first_exact', CO, 'estimate'), 'b2_m3tok.md', '10 档', 3, [r'已发表值为 #'])
A('m3-first-lo', '同上下限（团队）', m3('m3_first_exact', CO, 'team CI', 'est'), 'team CI', '10 档', 3, [r'已发表值为 ' + NUM + r' \[#'])
A('m3-first-hi', '同上上限（团队）', m3('m3_first_exact', CO, 'team CI', 'lo'), 'team CI', '10 档', 3, [r'已发表值为 ' + NUM + r' \[' + NUM + ', #\]'])
for half, lab in [('tune', r'两半都为正（'), ('test', r'两半都为正（' + NUM + r' \[' + NUM + ', ' + NUM + r'\]、')]:
    P = 'pairs.parquet ' + half
    A('m3-%s' % half, 'M3 全部 token：%s 半' % half, m3('m3_alltok', P, 'estimate'), 'b2_m3tok.md', '—', 3, [lab + '#'])
    A('m3-%s-lo' % half, '同上下限', m3('m3_alltok', P, 'team CI', 'est'), 'team CI', '—', 3, [lab + NUM + r' \[#'])
    A('m3-%s-hi' % half, '同上上限', m3('m3_alltok', P, 'team CI', 'lo'), 'team CI', '—', 3, [lab + NUM + r' \[' + NUM + ', #\]'])
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
