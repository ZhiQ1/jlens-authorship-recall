"""claims_defs v9 (2026-11-08 c): v8 (unchanged file) + every new or changed number of documents round c
(sync_20261108c_manifest.md; report v30, deck v21, handbook 2026-11-08 c). New ids start with 'A9-'.
Sources (every value read by code; numbers inside regexes are neighbouring text only):
  R1 (C04) P1 / P2 five false titles : 391_groups/summary_b1_p12f/p12f_mean5.csv, p12f_mean5_B_minus_A.csv, p12f_per_title.csv,
                                       tails_by_title.csv; false_0 colon B/A: 391_groups/summary_rerun/p1_p2_num_den_B_minus_A.csv
  R4 (C08) C / D completion          : 391_groups/b2_cd/summary/cd_group_values.csv, cd_contrasts.csv, cd_counts.csv
                                       (= tables of 391_groups/reports/b2_cd_report.md)
  C07 premises                       : audit_20261105/part_A_stage4_9.md line 10 (129 / 200, 64.5%); D13-1 numbers = v7 A7-D13-*
  X4 not H2 evidence                 : 381_stage13/summary_x1x4/x4_rolesplit.csv (BERT given_first, Qwen L8 given_first)
  limitations L01-L09                : 351_stage10/reports/parity.json (tolerance_amendment); 361_stage11/summary/E1_recovery.csv;
                                       numcheck/claims/out_20261108_140102 (680 / 4,307); ~/jlens_work/for_user_2026-11-07.md (1,024);
                                       ~/jlens_work/conclusions_v30_checks.md (3 h); 381_stage13/b2_gennames_v2/summary/repro_check.json (0.880 / 0.90)
Collisions: four older claims whose loose patterns now also hit the new five-title numbers get an exclusion (EXCL9 below);
the new numbers are checked by the A9 claims instead.
Document list: v8 list + process_report/draft_zh.md (source of the process report page).
Run with:  CLAIMS_DEFS=claims_defs_v9 bash claims_run.sh"""
import json, re
from pathlib import Path
import pandas as pd
from claims_defs_v8 import *          # noqa: F401,F403
from claims_defs_v8 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, py, mdre, jsn, op
from claims_lib import JL
import claims_docs

# ------------------------------------------------------------------ documents: + process report draft (md)
_dl0 = claims_docs.doc_list
def _doc_list():
    d = _dl0()
    p = claims_docs.REP / 'process_report/draft_zh.md'
    if p.exists():
        d.append(('过程报告草稿 draft_zh.md', 'md', p))
    return d
claims_docs.doc_list = _doc_list


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A9-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
CIR = r'\[%s, %s\]' % (NUM, NUM)


def T(cid, stmt, sels, comp, n, dec, labs, f0=None, f0labs=None, **k):
    """estimate / lo / hi (and optionally the false_0 value written after the CI) for each label regex (label ends before the number)."""
    A(cid, stmt, sels[''], comp, n, dec, [l + r'#(?= \[)' for l in labs], **k)
    A(cid + '-lo', stmt + '（下限）', sels['-lo'], comp, n, dec, [l + NUM + r' \[#' for l in labs], **k)
    A(cid + '-hi', stmt + '（上限）', sels['-hi'], comp, n, dec, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], **k)
    if f0 is not None:
        A(cid + '-f0', stmt + '（false_0，已发表）', f0, comp.split('；')[0] + '；false_0 列', n, dec,
          [l + NUM + ' ' + CIR + r'(?:（(?:false_0 )?| \((?:false_0 )?| )#' for l in (f0labs or labs)], **k)


# ================================================================== R1: P1 / P2 with five false titles (C04)
M5 = '391_groups/summary_b1_p12f/p12f_mean5.csv'
M5BA = '391_groups/summary_b1_p12f/p12f_mean5_B_minus_A.csv'
PT = '391_groups/summary_b1_p12f/p12f_per_title.csv'
TAIL = '391_groups/summary_b1_p12f/tails_by_title.csv'
RBA = '391_groups/summary_rerun/p1_p2_num_den_B_minus_A.csv'
COMP_R1 = '补充 10 第 3 项：5 个假标题平均的恢复比例（mean5），Stage 11 样本 1,186 篇，团队整群 bootstrap 2,000 次 95% CI；p12f_mean5.csv 列 ratio / ratio_lo / ratio_hi'


def m5(exp, item, L, col):
    return csv(M5, col, experiment=exp, who='all_authors', group='all', item=item, layer=L)


def m5s(exp, item, L):
    return {'': m5(exp, item, L, 'ratio'), '-lo': m5(exp, item, L, 'ratio_lo'), '-hi': m5(exp, item, L, 'ratio_hi')}


T('R1-P1all-L48', 'P1 / P2 五个假标题：P1 全部位置 L48', m5s('P1', 'all', 48), COMP_R1, '1,186 篇', 3,
  [r'(?:P1 全部位置|P1 all positions) L48 '], f0=m5('P1', 'all', 48, 'ratio_false0'))
T('R1-P1all-L52', 'P1 / P2 五个假标题：P1 全部位置 L52', m5s('P1', 'all', 52), COMP_R1, '1,186 篇', 3,
  [r'(?:P1 全部位置|P1 all positions) L48 ' + NUM + ' ' + CIR + r'[^；;]{0,20}?[、,] ?L52 ', r'P1 全部位置 L52 '],
  f0=m5('P1', 'all', 52, 'ratio_false0'))
T('R1-P1names-L52', 'P1 / P2 五个假标题：P1 只换名字位置 L52', m5s('P1', 'names', 52), COMP_R1, '1,186 篇', 3,
  [r'(?:P1 只换名字位置|name positions only) L52 '], f0=m5('P1', 'names', 52, 'ratio_false0'))
T('R1-P1p9-L44', 'P1 / P2 五个假标题：P1 只换 p9（标题的右引号）L44', m5s('P1', 'p9', 44), COMP_R1, '各假标题 694–711 篇', 3,
  [r'P1 只换 p9（标题的右引号） L44 '], f0=m5('P1', 'p9', 44, 'ratio_false0'))
T('R1-P2attn-L48', 'P1 / P2 五个假标题：P2 注意力 L48', m5s('P2', 'attn', 48), COMP_R1, '1,186 篇', 3,
  [r'(?:P2 注意力|attention) L48 (?=\+0\.\d+ \[0\.229)', r'P2 注意力 L48 '], f0=m5('P2', 'attn', 48, 'ratio_false0'))
T('R1-P2mlp-L52', 'P1 / P2 五个假标题：P2 MLP L52', m5s('P2', 'mlp', 52), COMP_R1, '1,186 篇', 3,
  [r'(?:P2 MLP|MLP) L52 (?=\+)'], f0=m5('P2', 'mlp', 52, 'ratio_false0'))
T('R1-P2mlp-L56', 'P1 / P2 五个假标题：P2 MLP L56', m5s('P2', 'mlp', 56), COMP_R1, '1,186 篇', 3,
  [r'(?:P2 MLP|MLP) L52 ' + NUM + ' ' + CIR + r'[^；;]{0,20}?[、,] ?L56 (?=\+)', r'(?:P2 MLP|MLP) L56 (?=\+)'],
  f0=m5('P2', 'mlp', 56, 'ratio_false0'))
A('R1-n', 'P1 / P2 五个假标题：篇数', m5('P1', 'all', 48, 'n_papers'), '计数（p12f_mean5.csv n_papers）', '—', 0,
  [r'\+0\.\d+ \[0\.\d+, [01]\.\d+\] \+0\.\d+ #(?![\d.])', r'Stage 11 样本 # 篇，团队整群'], sign=False)

# p9 papers per false title (n_papers max over the p9 rows of each title = all-group count)
for k in range(5):
    A('R1-p9-n-f%d' % k, 'p9 位置：false_%d 的篇数' % k, csv(PT, 'n_papers', 'max', item='p9', title='false_%d' % k), 'p12f_per_title.csv item = p9 的 n_papers（取最大 = all 组）',
      '—', 0, [r'false_%d #(?=、| ?篇)' % k], sign=False)


def _p9n(f):
    d = pd.read_csv(JL / PT); s = d[d['item'] == 'p9'].groupby('title').n_papers.max()
    return f(s)


A('R1-p9-min', 'p9 位置：各假标题篇数最小', py(lambda: _p9n(min), 'p12f_per_title.csv item = p9，每个假标题取 n_papers 最大，再取最小', [PT]), '计数', '—', 0,
  [r'各假标题 #(?=–\d)', r'p9: #(?=–\d)'], sign=False)
A('R1-p9-max', 'p9 位置：各假标题篇数最大', py(lambda: _p9n(max), '同上取最大', [PT]), '计数', '—', 0,
  [r'各假标题 \d+–#', r'p9: \d+–#'], sign=False)


def _p9_titles_per_paper():
    t = pd.read_csv(JL / TAIL); c = (t[[x for x in t.columns if x.startswith('tail_false_')]] == 9).sum(axis=1)
    return c.mean()


A('R1-p9-titles', 'p9 位置：平均每篇可用假标题数（尾长 = 9 的假标题个数，对 1,186 篇平均）',
  py(_p9_titles_per_paper, 'tails_by_title.csv：每篇 tail_false_k == 9 的个数，对全部 1,186 篇取平均', [TAIL]), '计数平均', '1,186 篇', 0,
  [r'平均每篇约 #(?= 个可用假标题)'], sign=False, note='口径：对全部 1,186 篇平均（只对有 ≥ 1 个尾长 9 的论文平均会更高）')

# colon (':' = item p1) numerator B/A: five titles and false_0
COMP_BA = 'P1 只替换 “:”（item p1），未写出作者，分子 B/A（B 586 / A 557 篇）'
for L, z in [(44, [r'5 个假标题版 L44 #', r'5 个假标题版 #(?=–0\.\d)', r'B/A #(?=–0\.\d+ with five)', r'colon numerator B/A #(?=–)', r'分子 B/A #(?=–0\.\d+（false_0)']),
             (48, [r'5 个假标题版 L44 0\.\d+、L48 #', r'5 个假标题版 0\.\d+–#', r'B/A 0\.\d+–#(?= with five)', r'colon numerator B/A 0\.\d+–#', r'分子 B/A 0\.\d+–#(?=（false_0)'])]:
    A('R1-BA5-L%d' % L, '“:” 分子 B/A（5 个假标题）L%d' % L, csv(M5BA, 'B_over_A_numerator', experiment='P1', item='p1', layer=L),
      COMP_BA + '；p12f_mean5_B_minus_A.csv B_over_A_numerator', '—', 2, z, sign=False)
for L, z in [(44, [r'false_0 版 L44 #', r'false_0 版 #(?=–)', r'false_0 #(?=–0\.\d+\))', r'0\.\d+–0\.\d+ vs #(?=–)', r'\(false_0 #(?=–)', r'（false_0 #(?=–0\.\d+）)']),
             (48, [r'false_0 版 L44 0\.\d+、L48 #', r'false_0 版 0\.\d+–#', r'\(false_0 0\.\d+–#\)', r'0\.\d+–0\.\d+ vs 0\.\d+–#', r'（false_0 0\.\d+–#）'])]:
    A('R1-BA0-L%d' % L, '“:” 分子 B/A（false_0）L%d' % L, csv(RBA, 'B_over_A_numerator', experiment='P1', item='p1', layer=L),
      COMP_BA + '；summary_rerun/p1_p2_num_den_B_minus_A.csv B_over_A_numerator', '—', 2, z, sign=False)
A('R1-BAden', '“:” 分母 B/A（5 个假标题，L44）', csv(M5BA, 'B_over_A_denominator', experiment='P1', item='p1', layer=44),
  'p12f_mean5_B_minus_A.csv B_over_A_denominator', '—', 2, [r'分母 B/A #'], sign=False)

# ================================================================== R4: C / D completion (C08)
GV = '391_groups/b2_cd/summary/cd_group_values.csv'
CT = '391_groups/b2_cd/summary/cd_contrasts.csv'
CN = '391_groups/b2_cd/summary/cd_counts.csv'
WB = 'within-bin (C >= 10, A >= 10 per bin)'
COMP_CD = '补充 11 B：未写出作者；团队整群 bootstrap 2,000 次 95% CI；b2_cd_report.md'


def gv(exp, grp, L, col):
    return csv(GV, col, experiment=exp, who='unwritten', group=grp, layer=L)


def gvs(exp, grp, L, c=('estimate', 'lo', 'hi')):
    return {'': gv(exp, grp, L, c[0]), '-lo': gv(exp, grp, L, c[1]), '-hi': gv(exp, grp, L, c[2])}


def ct(L, col, exp='E1'):
    return csv(CT, col, experiment=exp, who='unwritten', contrast='C - A', kind=WB, layer=L)


def cts(L, c=('ratio_diff', 'ratio_lo', 'ratio_hi')):
    return {'': ct(L, c[0]), '-lo': ct(L, c[1]), '-hi': ct(L, c[2])}


PRE = r'(?:323 篇）：E1 恢复比例|323 papers\) E1 recovery) '
T('R4-CA-L48', 'C / D 组补全：同一引用档内 C − A，E1 恢复比例 L48', cts(48), COMP_CD + ' Contrasts 表（within-bin，6 档）', 'C 258 / A 323 篇', 3, [PRE + 'L48 '])
T('R4-CA-L52', 'C / D 组补全：同一引用档内 C − A，E1 恢复比例 L52', cts(52), COMP_CD + ' Contrasts 表', 'C 258 / A 323 篇', 3, [PRE + 'L48 ' + NUM + ' ' + CIR + '[，,] ?L52 '])
T('R4-CA-L56', 'C / D 组补全：同一引用档内 C − A，E1 恢复比例 L56', cts(56), COMP_CD + ' Contrasts 表', 'C 258 / A 323 篇', 3,
  [PRE + 'L48 ' + NUM + ' ' + CIR + '[，,] ?L52 ' + NUM + ' ' + CIR + r'(?:；| \()L56 '])
T('R4-CA-den', 'C / D 组补全：同一引用档内 C − A，分母（真假标题差距）之差', cts(48, ('den_diff', 'den_lo', 'den_hi')), COMP_CD + ' Contrasts 表 denominator diff', 'C 258 / A 323 篇', 3,
  [r'同档内 C − A ', r'within bin C − A ', r'larger gap \(C − A '])
A('R4-CA-nC', 'C / D 组补全：同档比较 C 篇数', ct(48, 'n_a'), '计数（cd_contrasts.csv n_a）', '—', 0, [r'C # 篇、A 323', r'C # / A 323 papers', r'只用到 C 462 篇中的 # 篇'], sign=False)
A('R4-CA-nA', 'C / D 组补全：同档比较 A 篇数', ct(48, 'n_b'), '计数（n_b）', '—', 0, [r'C 258 篇、A # 篇', r'C 258 / A # papers'], sign=False)
A('R4-CA-bins', 'C / D 组补全：同档比较的引用档数', ct(48, 'n_bins'), '计数（n_bins）', '—', 0, [r'（# 个引用档，C 258', r'\(# bins, C 258'], sign=False)
# denominators (E1 L48 rows; the denominator is the same at every layer)
T('R4-den-C', 'C / D 组补全：C 的分母（真 − false_0，E1，未写出作者）', gvs('E1', 'C', 48, ('denominator', 'den_lo', 'den_hi')), COMP_CD + ' Numerator / denominator 表', 'C 462 篇', 3,
  [r'分母 C ', r'(?:补充 11 B 补全）|\(addendum 11 B\)) 462 '])
A('R4-den-C-b', 'C 的分母（简写处）', gv('E1', 'C', 48, 'denominator'), COMP_CD, 'C 462 篇', 3,
  [r'denominator C #', r'U0 0\.293、C #', r'C #(?= (?:对|vs) A 0\.\d)'], sign=False)
A('R4-den-C-lo2', 'C 的分母下限（注释处）', gv('E1', 'C', 48, 'den_lo'), COMP_CD, 'C 462 篇', 3, [r'补全后的 462 篇，\[#'], sign=False)
A('R4-den-C-hi2', 'C 的分母上限（注释处）', gv('E1', 'C', 48, 'den_hi'), COMP_CD, 'C 462 篇', 3, [r'补全后的 462 篇，\[' + NUM + ', #\]'], sign=False)
T('R4-den-A', 'C / D 组补全：A 的分母', gvs('E1', 'A', 48, ('denominator', 'den_lo', 'den_hi')), COMP_CD + ' Numerator / denominator 表', 'A 557 篇', 3,
  [r'分母 C ' + NUM + ' ' + CIR + '、A '])
A('R4-den-A-b', 'A 的分母（简写处）', gv('E1', 'A', 48, 'denominator'), COMP_CD, 'A 557 篇', 3,
  [r'denominator C 0\.\d+, A #', r'C 0\.\d+ (?:对|vs) A #'], sign=False)
# table P5.1 / P5.2 / deck slide 77 C and D rows
T('R4-C-E1L48', 'C / D 组补全：C 的 E1 恢复比例 L48', gvs('E1', 'C', 48), COMP_CD + ' E1 表', 'C 462 篇', 3,
  [r'n = 507 \(660 authors\) ', r'(?:补充 11 B 补全）|\(addendum 11 B\)) 462 ' + NUM + ' ' + CIR + r' [+−\-]?\d\.\d+ '])
T('R4-C-E1L52', 'C / D 组补全：C 的 E1 恢复比例 L52', gvs('E1', 'C', 52), COMP_CD + ' E1 表', 'C 462 篇', 3,
  [r'n = 507 \(660 authors\) ' + NUM + ' ' + CIR + r'; n = 462 \(2103 authors\) ',
   r'(?:补充 11 B 补全）|\(addendum 11 B\)) 462 ' + NUM + ' ' + CIR + r' [+−\-]?\d\.\d+ ' + NUM + ' ' + CIR + r' (?:[+−\-]?\d\.\d+ )?'])
T('R4-C-E2L52', 'C / D 组补全：C 的 E2 阻断损失 L52', gvs('E2', 'C', 52), COMP_CD + ' E2 表', 'C 462 篇', 3,
  [r'n = 507 \(660 authors\) ' + NUM + ' ' + CIR + r'; n = 462 \(2103 authors\) ' + NUM + ' ' + CIR + r'; n = 462 \(2103 authors\) '])
A('R4-C-num48', 'C 的 E1 分子 L48', gv('E1', 'C', 48, 'numerator'), COMP_CD, 'C 462 篇', 3, [r'(?:补充 11 B 补全）|\(addendum 11 B\)) 462 ' + NUM + ' ' + CIR + ' #'])
A('R4-C-num52', 'C 的 E1 分子 L52', gv('E1', 'C', 52, 'numerator'), COMP_CD, 'C 462 篇', 3,
  [r'补充 11 B 补全） 462 ' + NUM + ' ' + CIR + ' ' + NUM + ' ' + NUM + ' ' + CIR + ' #'])
DCELL = r'; n = 33 \(141 authors\); descriptive \(addendum 11\) '
for cid, exp, L, k in [('R4-D-E1L48', 'E1', 48, 0), ('R4-D-E1L52', 'E1', 52, 1), ('R4-D-E2L52', 'E2', 52, 2)]:
    s = gvs(exp, 'D', L)
    stmt = 'C / D 组补全：D 的 %s %s L%d（描述）' % (exp, '恢复比例' if exp == 'E1' else '阻断损失', L)
    pats_e = [r'n = 34 \(41 authors\) ' + ''.join(NUM + ' ' + CIR + DCELL for _ in range(k)) + r'#(?= \[)']
    A(cid, stmt, s[''], COMP_CD, 'D 33 篇', 3, pats_e)
    A(cid + '-lo', stmt + '（下限）', s['-lo'], COMP_CD, 'D 33 篇', 3, [p.replace(r'#(?= \[)', NUM + r' \[#') for p in pats_e])
    A(cid + '-hi', stmt + '（上限）', s['-hi'], COMP_CD, 'D 33 篇', 3, [p.replace(r'#(?= \[)', NUM + r' \[' + NUM + r', #\]') for p in pats_e])


def cnt(g, col, exp='E1'):
    return csv(CN, col, experiment=exp, group=g)


A('R4-nC', 'C 组未写出作者的篇数', cnt('C', 'papers_unwritten'), '计数（cd_counts.csv）', '—', 0,
  [r'C 组未写出作者 # 篇', r'C has # papers', r'C completed to # papers', r'C # papers: same timing', r'C \(#\): larger', r'补全到 # 篇', r'只用到 C # 篇中的',
   r'补全后的 # 篇', r'n = #(?= \(2103 authors\))', r'C 为补充 11 B 补全后的 # 篇', r'C # 篇，同一引用档内', r'补全到 # 篇后', r'(?:补充 11 B 补全）|\(addendum 11 B\)) #(?= \+?0\.\d+ \[)'], sign=False)
A('R4-nC-auth', 'C 组未写出作者数', cnt('C', 'authors_unwritten'), '计数', '—', 0, [r'n = 462 \(# authors\)'], sign=False)
A('R4-nD', 'D 组未写出作者的篇数', cnt('D', 'papers_unwritten'), '计数', '—', 0,
  [r'D（# 篇）', r'D \(# papers\)', r'D # 篇按补充 11', r'D # / R2', r'n = #(?= \(141 authors\))', r'D（# 篇，补充 11 B）', r'D 33 篇'.replace('33', '#'), r'D #(?= 篇、R2)', r'D # 篇只作描述'], sign=False)
A('R4-nD-auth', 'D 组未写出作者数', cnt('D', 'authors_unwritten'), '计数', '—', 0, [r'n = 33 \(# authors\)'], sign=False)
# (D design count 34: not stated in the documents; not registered)


def _e2_all_include0():
    d = pd.read_csv(JL / CT)
    x = d[(d.experiment == 'E2') & (d.who == 'unwritten') & (d.contrast == 'C - A') & (d.kind == WB) & d.layer.between(32, 52)]
    return int(((x.ratio_lo <= 0) & (x.ratio_hi >= 0)).sum() == len(x) and len(x) > 0)


E2_INCLUDE0 = _e2_all_include0()       # bound statement "E2 L32–L52 区间都含 0" (reported, not a claim)

# ================================================================== C07 premises (Stage 8 first token = initial)
AUD = 'audit_20261105/part_A_stage4_9.md'
A('S8-init-n', 'Stage 8 金标准第一作者第一个 token 只是首字母的篇数', mdre(AUD, r'for \*\*(\d+)/200 \('), 'part_A_stage4_9.md 第 10 行（正则计数）', '200 篇', 0,
  [r'200 篇里有 # 篇', r'\(# of 200 papers'], sign=False)
A('S8-init-N', 'Stage 8 篇数（首字母计数的分母）', mdre(AUD, r'for \*\*\d+/(\d+) \('), '同上', '—', 0, [r'Stage 8 的 # 篇里有', r'of # papers, 64'], sign=False)
A('S8-init-pct', 'Stage 8 首字母比例', op('div', mdre(AUD, r'for \*\*(\d+)/200 \('), mdre(AUD, r'for \*\*\d+/(\d+) \(')), '129 / 200', '200 篇', 1,
  [r'里有 129 篇（#%）', r'200 papers, #%', r'\(#% are initials\)', r'W 只给第一作者的第一个 token 打分（#%', r'S8 中 #% 是首字母', r'first token \(#% are initials\)'], sign=False, scale=100)

# D13-1 int6 RQ1 estimate / upper bound: the v7 patterns anchor on the old lower bound 0.109 (corrected to 0.108 in v8), so they no
# longer match; same selector as A7-D13-6-RQ1, patterns anchored on the corrected text
PX = '381_stage13/c13_C2_followup/c2_followup_proxy.csv'
A('D13-6-RQ1', 'D13-1 代理 6 层 int6 RQ1（全部作者，public J-lens）', csv(PX, 'rq1', version='aa_all', endpoint='int6'), 'c2_followup_proxy.csv aa_all int6 rq1', '200 篇', 3,
  [r'RQ1 #(?= \[0\.108)', r'CPU proxy:? RQ1 #(?=, RQ2)'])
A('D13-6-RQ1-hi', 'D13-1 代理 6 层 int6 RQ1（上限）', csv(PX, 'rq1_team_hi', version='aa_all', endpoint='int6'), 'c2_followup_proxy.csv aa_all int6 rq1_team_hi', '200 篇', 3,
  [r'RQ1 \+0\.130 \[0\.108, #\]'], sign=False)

# ================================================================== X4 no longer H2 evidence (text baseline)
X4RS = '381_stage13/summary_x1x4/x4_rolesplit.csv'
A('X4-bert-given', 'X4：名的第一个 token 上 BERT 文本基线 D', csv(X4RS, 'mean', measure='text_bert', role='given_first'), 'x4_rolesplit.csv measure = text_bert, role = given_first', '357 篇', 3,
  [r'BERT 基线 #(?= 不弱于)', r'BERT baseline #', r'BERT #(?=，Qwen)', r'BERT 文本基线 #'])
A('X4-qwen-given', 'X4：名的第一个 token 上 Qwen L8 D', csv(X4RS, 'mean', measure='qwen', layer=8.0, role='given_first'), 'x4_rolesplit.csv measure = qwen, layer 8, role = given_first', '357 篇', 3,
  [r'不弱于 Qwen L8 #', r'(?:weaker|stronger) than Qwen L8 #', r'BERT \+0\.\d+，Qwen #', r'大于 Qwen 的 #'])

# ================================================================== limitations L01-L09
PAR = '351_stage10/reports/parity.json'


def _par():
    return json.loads((JL / PAR).read_text())['tolerance_amendment']


A('L02-max', '一致性检查主轮最大差', jsn(PAR, ['tolerance_amendment', 'reassessed_runs', 1, 'max']), 'parity.json tolerance_amendment.reassessed_runs[1].max', '25 个组合', 3,
  [r'组合的?最大差 #', r'主轮（最大差 #', r'max(?:imum)? difference #', r'main round, max #', r'max #(?=[;)])'], sign=False)
A('L02-old', '一致性容差（原）', jsn(PAR, ['tolerance_amendment', 'old_tolerance_max_abs_logit']), 'parity.json', '—', 2,
  [r'从 # 放宽到 0\.5', r'from # to 0\.5', r'tolerance # → 0\.5', r'容差 # → 0\.5', r'# → 0\.5 was used'], sign=False)
A('L02-new', '一致性容差（新）', jsn(PAR, ['tolerance_amendment', 'new_tolerance_max_abs_logit']), 'parity.json', '—', 1,
  [r'从 0\.25 放宽到 #', r'from 0\.25 to #', r'0\.25 → #', r'只有按 # 才通过', r'passes only at #'], sign=False)


def _n_main_pairs():
    d = json.loads((JL / PAR).read_text())
    r = [x for x in d['runs'] if x['created'] == '2026-10-24T23:48:37'][0]
    return len(r['max_abs_logit_diff'])


A('L02-pairs', '一致性检查主轮的（读出 × 层）组合数', py(_n_main_pairs, 'parity.json runs[created = 2026-10-24T23:48:37] max_abs_logit_diff 的键数', [PAR]), '计数', '—', 0,
  [r'主轮 # 个（读出 × 层）', r'\(# readout × layer pairs', r'# readout × layer pairs'], sign=False)
A('L02-rank', '名次完全一致的上限', py(lambda: float(re.search(r'ranks < (\d+) agree', _par()['reason']).group(1)), 'parity.json tolerance_amendment.reason（正则）', [PAR]), '—', '—', 0,
  [r'名次 < #', r'ranks? < #'], sign=False)
A('L02-dlog', '名次不一致对 log10(1/名次) 的最大影响', py(lambda: float(re.search(r'at most (\d+\.\d+)', _par()['reason']).group(1)), 'parity.json tolerance_amendment.reason（正则）', [PAR]), '—', '—', 3,
  [r'最多变 #', r'by at most #'], sign=False)
E1R = '361_stage11/summary/E1_recovery.csv'
A('L03-n', '干预实验篇数', csv(E1R, 'n_papers', group='all', layer=48), 'E1_recovery.csv n_papers（group = all, L48）', '—', 0,
  [r'只用 9,108 篇中的 # 篇', r'use # of 9,108', r'只用 # / 9,108', r'只用了? ?# 篇[（，]', r'只用 # 篇、', r'干预只用 # 篇'], sign=False)
A('L03-t', '干预实验 target 篇数', csv(E1R, 'n_papers', group='target', layer=48), 'E1_recovery.csv n_papers（group = target）', '—', 0, [r'target # \+ control'], sign=False)
A('L03-c', '干预实验 control 篇数', csv(E1R, 'n_papers', group='control', layer=48), 'E1_recovery.csv n_papers（group = control）', '—', 0, [r'target \d+ \+ control #'], sign=False)
OUT0 = '351_stage10/reports/numcheck/claims/out_20261108_140102/'


def _rows(f):
    return len(pd.read_csv(JL / (OUT0 + f)))


A('L09-claims', '数字核对：已登记的结论数字', py(lambda: _rows('claims_registry.csv'), 'out_20261108_140102/claims_registry.csv 行数', [OUT0 + 'claims_registry.csv']), '计数', '—', 0,
  [r'已登记 # 个', r'# registered claims', r'# 个结论数字、4', r'登记 # 个'], sign=False)
A('L09-occ', '数字核对：已登记的出现处', py(lambda: _rows('claims_check.csv'), 'out_20261108_140102/claims_check.csv 行数', [OUT0 + 'claims_check.csv']), '计数', '—', 0,
  [r'680 个结论数字、# 处', r'680 registered claims / # occurrences', r'680 个、# 处', r'680 / # ', r'# occurrences all'], sign=False)


def _all_consistent():
    d = pd.read_csv(JL / (OUT0 + 'claims_check.csv'))
    return int((d.status == '一致').all())


L09_ALL_CONSISTENT = _all_consistent()
FU = '/home/zhang.zhiqi2/jlens_work/for_user_2026-11-07.md'
A('L09-unreg', '数字核对：未登记的像结论数字（2026-11-07 计数）', mdre(FU, r'约 ([\d,]+) 个像结论的数字'), 'for_user_2026-11-07.md 第 56 行', '—', 0,
  [r'约 # 个像结论的数字', r'about # conclusion-like', r'~#(?= )'], sign=False)
CHK = '/home/zhang.zhiqi2/jlens_work/conclusions_v30_checks.md'
A('L05-hours', 'M2 用 5 个假标题重做的 CPU 用时估计', mdre(CHK, r'估计约 (\d+) 小时墙钟'), 'conclusions_v30_checks.md A3', '—', 0,
  [r'残差已在盘上，约 # 小时', r'on disk, about # h'], sign=False)
RC = '381_stage13/b2_gennames_v2/summary/repro_check.json'
A('B2-11-share', '2-11 首名复现率', jsn(RC, ['share']), 'repro_check.json share（50 篇）', '50 篇', 3, [r'首名复现率 # <', r'\(# < 0\.90\)', r'复现率 # <'], sign=False)
A('B2-11-thr', '2-11 首名复现率门槛', jsn(RC, ['threshold']), 'repro_check.json threshold', '—', 2, [r'0\.880 < #'], sign=False)

# ================================================================== collisions with older loose patterns
EXCL9 = {'E1-L48': r'0\.807, 0\.835', 'P1-names': r'0\.827, 0\.856', 'A5-P2-mlp52': r'0\.174, 0\.188',
         'A5-P2-mlp52-lo': r'0\.174, 0\.188', 'A5-P2-mlp52-hi': r'0\.174, 0\.188', 'A7-Vpd-mean': r'共享尾长|p9 位置'}
for c in C:
    if c['id'] in EXCL9:
        c['excl'] = EXCL9[c['id']] if not c.get('excl') else c['excl'] + '|' + EXCL9[c['id']]
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
