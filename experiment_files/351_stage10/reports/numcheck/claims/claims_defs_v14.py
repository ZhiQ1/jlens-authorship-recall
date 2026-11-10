"""claims_defs v14 (2026-11-09 h): v13 (unchanged file) + the name-position probe numbers of documents round h
(sync_20261108c_manifest.md "round h"; H3 -> 部分支持). New ids 'A14-'. Sources: 381_stage13/summary_b2_np/*_v2.csv beside
381_stage13/reports/b2_np_report_v2.md: np_role_layer_v2.csv (probe spec / CI, target − control within bin, control rows any / field),
np_lens_compare_v2.csv (logit / J-lens spec at the name position), np_groups_unwritten_v2.csv (behaviour groups, A − B),
np_usable_titles_v2.csv (usable false titles per kept paper).  Run with:  CLAIMS_DEFS=claims_defs_v14 bash claims_run.sh"""
from claims_defs_v13 import *          # noqa: F401,F403
from claims_defs_v13 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A14-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
CI_ = r' \[' + NUM + ', ' + NUM + r'\]'
D = '381_stage13/summary_b2_np/'
RL, LC, GU, UT = D + 'np_role_layer_v2.csv', D + 'np_lens_compare_v2.csv', D + 'np_groups_unwritten_v2.csv', D + 'np_usable_titles_v2.csv'
COMP = '补充 11 A 名字位置 probe（Vpd 主结果，D11-1），团队整群 bootstrap 2,000 次；'


def T(cid, stmt, f, est, lo, hi, w, labs, n, sign=True):
    A(cid, stmt, csv(f, est, **w), COMP + est, n, 3, [l + '#(?= \\[)' for l in labs], sign=sign)
    A(cid + '-lo', stmt + '（下限）', csv(f, lo, **w), COMP + lo, n, 3, [l + NUM + r' \[#' for l in labs], sign=sign)
    A(cid + '-hi', stmt + '（上限）', csv(f, hi, **w), COMP + hi, n, 3, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=sign)


SF = dict(version='Vpd', run='surname_first')
PZ, PE = r'(?:排除版；probe |per-donor exclusion; probe )', r'(?:；|; )target − control '
T('np-L40', '名字位置 probe：姓首 token L40（Vpd）', RL, 'spec', 'lo', 'hi', dict(layer=40, **SF), [PZ + 'L40 '], '4,654 篇')
T('np-L48', '名字位置 probe：姓首 token L48（Vpd）', RL, 'spec', 'lo', 'hi', dict(layer=48, **SF), [PZ + 'L40 ' + NUM + CI_ + '[、,] ?L48 '], '4,654 篇')
T('np-tc40', '名字位置 probe：姓首 token target − control L40（Vpd，同档）', RL, 'tc_diff', 'tc_lo', 'tc_hi', dict(layer=40, **SF), [r'(?:0\.110\]|0\.110\])' + PE + 'L40 '], '4,654 篇')
T('np-tc48', '名字位置 probe：姓首 token target − control L48', RL, 'tc_diff', 'tc_lo', 'tc_hi', dict(layer=48, **SF), [PE + 'L40 ' + NUM + CI_ + '[、,] ?L48 '], '4,654 篇')
T('np-logit40', '名字位置：logit lens 姓首 token L40', LC, 'lens_spec', 'lens_lo', 'lens_hi', dict(layer=40, readout='logit', **SF), [r'logit L40 '], '4,654 篇')
T('np-jl40', '名字位置：public J-lens 姓首 token L40', LC, 'lens_spec', 'lens_lo', 'lens_hi', dict(layer=40, readout='jlens_public', **SF), [r'J-lens L40 '], '4,654 篇')
IN = dict(version='Vpd', run='initial', layer=40)
T('np-ini-ctrl', '名字位置：首字母对照行（任意另一篇论文）L40', RL, 'any_est', 'any_lo', 'any_hi', IN, [r'对照行（', r'control row \('], '4,812 篇')
T('np-ini-sig', '名字位置：首字母信号 L40', RL, 'spec', 'lo', 'hi', IN, [r'约为信号（', r'about half the signal \('], '4,812 篇')
T('np-sur-perm', '名字位置：姓的置换对照（任意另一篇论文）L40', RL, 'any_est', 'any_lo', 'any_hi', dict(layer=40, **SF), [r'置换对照约为 0（L40 ', r'permutation control[^(]{0,20}\(L40 '], '4,654 篇')
T('np-AB', '名字位置：按行为分组 A − B 姓 L40（只作描述）', GU, 'est', 'lo', 'hi', dict(version='Vpd', run='surname_first', layer=40, group='A-B'), [r'A − B 姓 L40 ', r'A − B surname L40 '], 'A 2,774 / B 1,501 篇')
V0 = dict(version='V0', run='surname_first', layer=40)
T('np-V0', '名字位置：V0 姓 L40（敏感性）', RL, 'spec', 'lo', 'hi', V0, [r'V0（1,395 篇，姓 L40 ', r'V0 \(1,395 papers, surname L40 '], '1,395 篇')
T('np-V0tc', '名字位置：V0 姓 target − control L40', RL, 'tc_diff', 'tc_lo', 'tc_hi', V0, [r'V0（1,395 篇，姓 L40 ' + NUM + CI_ + r'，target − control L40 '], '1,395 篇')
T('np-V5x0', '名字位置：V5x0 姓 L40（含泄漏，仅敏感性）', RL, 'spec', 'lo', 'hi', dict(version='V5x0', run='surname_first', layer=40), [r'V5x0（L40 ', r'V5x0 \(L40 '], '1,395 篇')
A('np-V0n', '名字位置：V0 姓篇数', csv(RL, 'n_tc', **V0), '计数', '—', 0, [r'V0（# 篇，姓 L40'], sign=False)
A('np-usable', '名字位置：Vpd 每篇平均可用假标题数（姓，保留论文）', csv(UT, 'mean_used_kept', run='surname_first', group='target+control'), 'np_usable_titles_v2.csv mean_used_kept', '4,654 篇', 1,
  [r'D11-1，每篇平均约 #(?= 个可用假标题)', r'~#(?= usable false titles)'], sign=False)
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
