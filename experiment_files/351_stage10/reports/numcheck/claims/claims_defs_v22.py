"""claims_defs v22 (2026-11-15 e1d): v21 (unchanged file) + (1) the E1 + X6 extra-layer numbers (addendum 18 item 3, locked confirmatory)
and (2) the D name-chain numbers (addendum 16, locked, final) written into report / handbook / advisor / Stage 13 script / talk pages /
process report / deck (user-approved 2026-11-15).
Sources: 381_stage13/summary_e1x6_extra_20261114/e1x6_recovery.csv (group=all, false_title=average; = report.md "all" table, 5-title mean)
and arrival_decision.json (steepest step); 391_groups/summary_a16_20261115_tinytest/d_contrasts.csv, d_gen.csv, holm.csv.
New ids 'A22-'.  Run with:  CLAIMS_DEFS=claims_defs_v22 bash claims_run.sh"""
from claims_defs_v21 import *          # noqa: F401,F403
from claims_defs_v21 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, jsn


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A22-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
# ------------------------------------------------------------------ (1) E1 + X6 extra layers
RC = '381_stage13/summary_e1x6_extra_20261114/e1x6_recovery.csv'
AD = '381_stage13/summary_e1x6_extra_20261114/arrival_decision.json'
CE = '补充 18 第 3 项：E1 + X6 标题之后全部位置替换，5 个假标题平均 R，全部论文，团队整群 bootstrap 2,000 次（default_rng(13)）；'
SEL = dict(group='all', false_title='average')
HEAD = r'(?:恢复比例 R：|recovery R: |全部 1,186 篇）：)'
PREV = r'(?:L\d\d \d\.\d+(?: \[' + NUM + ', ' + NUM + r'\])?(?:、|, ))*'
for L in range(40, 53):
    labs = [HEAD + PREV + 'L%d ' % L]
    A('e1x6-R%d' % L, 'E1 + X6 补层：5 个假标题平均 R(L%d)' % L, csv(RC, 'R', layer=L, **SEL), CE, '1,186 篇', 3,
      [l + '#' for l in labs], sign=False)
    if L in (40, 45, 48, 50, 52):
        A('e1x6-R%d-lo' % L, 'E1 + X6 补层：R(L%d)（下限）' % L, csv(RC, 'lo', layer=L, **SEL), CE, '1,186 篇', 3,
          [l + NUM + r' \[#' for l in labs], sign=False)
        A('e1x6-R%d-hi' % L, 'E1 + X6 补层：R(L%d)（上限）' % L, csv(RC, 'hi', layer=L, **SEL), CE, '1,186 篇', 3,
          [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=False)
ST = r'L47→L48(?:，|, | )'
A('e1x6-step', 'E1 + X6 补层：最大的一步 R(L48) − R(L47)', jsn(AD, ['steepest', 'd']), CE + '同一组抽样的逐层差', '1,186 篇', 3,
  [ST + r'#(?= \[)'], sign=True)
A('e1x6-step-lo', 'E1 + X6 补层：最大的一步（下限）', jsn(AD, ['steepest', 'lo']), CE, '1,186 篇', 3,
  [ST + NUM + r' \[#'], sign=False)
A('e1x6-step-hi', 'E1 + X6 补层：最大的一步（上限）', jsn(AD, ['steepest', 'hi']), CE, '1,186 篇', 3,
  [ST + NUM + r' \[' + NUM + r', #\]'], sign=False)

# ------------------------------------------------------------------ (2) D name chain
DC = '391_groups/summary_a16_20261115_tinytest/d_contrasts.csv'
DG = '391_groups/summary_a16_20261115_tinytest/d_gen.csv'
HO = '391_groups/summary_a16_20261115_tinytest/holm.csv'
CD = '补充 16 D：名字链条，全部 token，团队整群 bootstrap 2,000 次（seed 391）；'


def T3(cid, stmt, sel, labs, sign=True):
    A(cid, stmt, csv(DC, 'est', **sel), CD, 'A 600 / B 600 篇', 3, [l + '#(?= \\[)' for l in labs], sign=sign)
    A(cid + '-lo', stmt + '（下限）', csv(DC, 'lo', **sel), CD, '同上', 3, [l + NUM + r' \[#' for l in labs], sign=sign)
    A(cid + '-hi', stmt + '（上限）', csv(DC, 'hi', **sel), CD, '同上', 3, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=sign)


G1 = dict(fa_type='all', contrast='G1', score='all_tokens')
T3('d-GA1', 'D：G_A(1)（真合作者名字对其余真作者分数的提高，A 组）', dict(group='A', version='true', **G1), [r'G_A\(1\) '])
T3('d-spec', 'D：G_A(1) 真标题 − 假标题（spec）', dict(group='A', version='spec', **G1),
   [r'真标题 − 假标题 ', r'true − false titles '])
T3('d-AB', 'D：G(1) A − B', dict(group='A-B', version='true', **G1), [r'A − B '])
A('d-holm-p', 'D：G_A(1) Holm 校正后 p', csv(HO, 'p_holm', test='D_GA1'),
  CD + 'Holm 校正（5 个检验）', '—', 4, [r'Holm 校正后 p = #', r'Holm-adjusted p = #'], sign=False)
A('d-gen-other', 'D 生成检查：A 组给出对照第一作者时至少再写对一位作者的比例', csv(DG, 'est', group='A', measure='any_rest_full', cond='G_other1'),
  CD + '贪心生成，作者 2..n', 'A 600 篇', 1, [r'从 #(?=%（给出对照第一作者）)', r'from #(?=% \(control first author given\))'], sign=False, scale=100)
A('d-gen-true', 'D 生成检查：A 组给出真第一作者时至少再写对一位作者的比例', csv(DG, 'est', group='A', measure='any_rest_full', cond='G_true1'),
  CD + '贪心生成，作者 2..n', 'A 600 篇', 1, [r'升到 #(?=%（给出真第一作者）)', r'to #(?=% \(true first author given\))'], sign=False, scale=100)
