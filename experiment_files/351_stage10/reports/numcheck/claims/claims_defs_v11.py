"""claims_defs v11 (2026-11-08 e): v10 (unchanged file) + the numbers of documents round e (sync_20261108c_manifest.md "round e").
New ids 'A11-'. Sources: 381_stage13/e4b_standardisation_check/v5x0_leak_share.json (V5x0 leak share: false_1..4 titles that the
per-title rule would have excluded; surname set 1,395 papers, given name, initial); 361_stage11/summary_r0r1/stage11_curves_by_recall.csv
(pre-completion C target R1 n = 36, A target R0 n = 557); C / D completion numbers = v9 sources (cd_counts / cd_contrasts).
Run with:  CLAIMS_DEFS=claims_defs_v11 bash claims_run.sh"""
from claims_defs_v10 import *          # noqa: F401,F403
from claims_defs_v10 import C, csv, MANUAL
from claims_defs_v9 import ct, cnt
from claims_defs_v5 import A as _A5, jsn


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A11-' + cid; MANUAL[-1] = c['id']


LS = '381_stage13/e4b_standardisation_check/v5x0_leak_share.json'
COMP = 'v5x0_leak_share.json：false_1..4 中按逐个假标题规则本应剔除的比例'
A('leak-sur', 'V5x0 泄漏比例：姓（1,395 篇）', jsn(LS, ['surname_first', 'share']), COMP, '1,395 篇', 0,
  [r'约 #% 本应剔除', r'about #% of false_1\.\.4'], sign=False, scale=100)
A('leak-sur-2', 'V5x0 泄漏比例：姓（两位小数）', jsn(LS, ['surname_first', 'share']), COMP, '1,395 篇', 2, [r'= #%(?= \(target| （target)'], sign=False, scale=100)
A('leak-sur-num', 'V5x0 泄漏：姓 分子', jsn(LS, ['surname_first', 'numerator']), COMP, '—', 0, [r'1,395 篇：# / 5,580', r'1,395 papers: # / 5,580', r'姓 # / 5,580'], sign=False)
A('leak-sur-den', 'V5x0 泄漏：姓 分母', jsn(LS, ['surname_first', 'denominator']), COMP, '—', 0, [r'4,402 / #'], sign=False)
A('leak-sur-n', 'V5x0 泄漏：姓 论文数', jsn(LS, ['surname_first', 'v5x0_papers']), COMP, '—', 0, [r'姓的 # 篇：4,402', r'surname set, # papers: 4,402'], sign=False)
A('leak-sur-t', 'V5x0 泄漏：姓 target', jsn(LS, ['surname_first', 'by_group', 'target', 'share']), COMP, '—', 2, [r'target #%'], sign=False, scale=100)
A('leak-sur-c', 'V5x0 泄漏：姓 control', jsn(LS, ['surname_first', 'by_group', 'control', 'share']), COMP, '—', 2, [r'control #%'], sign=False, scale=100)
A('leak-giv', 'V5x0 泄漏比例：名', jsn(LS, ['given_first', 'share']), COMP, '1,706 篇', 0, [r'名 #%、首字母', r'given name #%, initial'], sign=False, scale=100)
A('leak-giv-1', 'V5x0 泄漏比例：名（一位小数）', jsn(LS, ['given_first', 'share']), COMP, '1,706 篇', 1, [r'名 #%(?= ?[（(]2,894)', r'given names? #%(?= \(2,894)'], sign=False, scale=100)
A('leak-giv-num', 'V5x0 泄漏：名 分子 / 分母', jsn(LS, ['given_first', 'numerator']), COMP, '—', 0, [r'# / 6,824'], sign=False)
A('leak-giv-den', 'V5x0 泄漏：名 分母', jsn(LS, ['given_first', 'denominator']), COMP, '—', 0, [r'2,894 / #'], sign=False)
A('leak-ini', 'V5x0 泄漏比例：首字母', jsn(LS, ['initial', 'share']), COMP, '1,590 篇', 0, [r'首字母 #%(?![\d.])', r'initial #%'], sign=False, scale=100)
A('leak-ini-1', 'V5x0 泄漏比例：首字母（一位小数）', jsn(LS, ['initial', 'share']), COMP, '1,590 篇', 1, [r'首字母 #%(?= ?[（(]4,567)', r'initials? #%(?= \(4,567)'], sign=False, scale=100)
A('leak-ini-num', 'V5x0 泄漏：首字母 分子', jsn(LS, ['initial', 'numerator']), COMP, '—', 0, [r'# / 6,360'], sign=False)
A('leak-ini-den', 'V5x0 泄漏：首字母 分母', jsn(LS, ['initial', 'denominator']), COMP, '—', 0, [r'4,567 / #'], sign=False)
# rewritten C sentence (report e1 / e3)
CR = '361_stage11/summary_r0r1/stage11_curves_by_recall.csv'
A('C-pre-n', '补全前 C 组篇数（Stage 11 样本 target R1）', csv(CR, 'n', exp='E1', layer=48, view='C target R1'), 'stage11_curves_by_recall.csv n', '—', 0,
  [r'补全前（C 组 # 篇）', r'before completion \(C, # papers\)'], sign=False)
A('C-pre-nA', '补全前比较的 A 组篇数（target R0）', csv(CR, 'n', exp='E1', layer=48, view='A target R0'), 'stage11_curves_by_recall.csv n', '—', 0,
  [r'C 组 36 篇[^。]{0,20}A(?: 组)? # 篇', r'对 A # 篇'], sign=False)
A('C-post-n', '补全后 C 篇数（新句）', cnt('C', 'papers_unwritten'), 'cd_counts.csv', '—', 0, [r'补全到 # 篇后（档内可比'], sign=False)
A('C-post-wb', '补全后档内可比 C 篇数（新句）', ct(48, 'n_a'), 'cd_contrasts.csv n_a', '—', 0, [r'（档内可比 # 篇）'], sign=False)
from claims_defs_v9 import T as _T9, cts
import claims_defs_v9 as _v9
_n0 = len(C)
_T9('\x00', 'x', cts(48, ('den_diff', 'den_lo', 'den_hi')), 'x', 'x', 3, [r'分母 C − A '])
for _c, _suf in zip(C[_n0:], ('', '-lo', '-hi')):
    _c['id'] = 'A11-C-post-den' + _suf; _c['stmt'] = '新句：补全后 分母 C − A（同档）' + {'': '', '-lo': '（下限）', '-hi': '（上限）'}[_suf]
    _c['comp'] = 'cd_contrasts.csv within-bin den_diff / den_lo / den_hi（= b2_cd_report.md Contrasts 表）'; _c['n'] = 'C 258 / A 323 篇'
MANUAL[-3:] = [c['id'] for c in C[-3:]]
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
