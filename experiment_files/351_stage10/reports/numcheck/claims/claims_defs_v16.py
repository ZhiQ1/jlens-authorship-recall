"""claims_defs v16 (2026-11-12 l): v15 (unchanged file) + the numbers of documents round l (C24 for 2-11b; Patchscope 2-7 / 2-9) and the
round k correction note. New ids 'A16-'. Sources: 381_stage13/b2_gennames_b/summary/probe_within.csv (= reports/b2_gennames_b_report.md
primary / secondary tables), b2_gennames_b/summary/robust_posthoc.csv (= reports/b2_gennames_b_robust_posthoc.md), b2_gennames_b_report.md
"Labels" table (control M names); 381_stage13/summary_b2_ps/ps_D.csv (split = test, answer = author; = reports/b2_ps_report.md lines 32–35)
and summary_b2_ps/x4tok_layers.csv (src = title).  Run with:  CLAIMS_DEFS=claims_defs_v16 bash claims_run.sh"""
import pandas as pd
from claims_defs_v15 import *          # noqa: F401,F403
from claims_defs_v15 import C, csv, md, MANUAL
from claims_defs_v5 import A as _A5, py
from claims_lib import JL


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A16-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
CI_ = r' \[' + NUM + ', ' + NUM + r'\]'
PW, RP = '381_stage13/b2_gennames_b/summary/probe_within.csv', '381_stage13/b2_gennames_b/summary/robust_posthoc.csv'
GR = '381_stage13/reports/b2_gennames_b_report.md'
CG = '补充 15（2-11b）预注册主分析，名字 token 平均，团队整群 bootstrap 2,000 次；'


def pw(L, col, pos='name_mean'):
    return csv(PW, col, layer=L, position=pos)


def T(cid, stmt, sels, labs, n, sign=True, comp=CG):
    e, lo, hi = sels
    A(cid, stmt, e, comp, n, 3, [l + '#(?= \\[)' for l in labs], sign=sign)
    A(cid + '-lo', stmt + '（下限）', lo, comp, n, 3, [l + NUM + r' \[#' for l in labs], sign=sign)
    A(cid + '-hi', stmt + '（上限）', hi, comp, n, 3, [l + NUM + r' \[' + NUM + r', #\]' for l in labs], sign=sign)


T('gn-auc48', 'C24：L48 probe AUROC（名字 token 平均）', (pw(48, 'auroc_within'), pw(48, 'lo'), pw(48, 'hi')), [r'L48 AUROC '], '518 篇 / 3,388 对', sign=False)
T('gn-dpos48', 'C24：L48 probe − 排位基线', (pw(48, 'diff_pos'), pw(48, 'diff_pos_lo'), pw(48, 'diff_pos_hi')), [r'probe − 排位 ', r'probe − position '], '518 / 3,388')
T('gn-dstr48', 'C24：L48 probe − 名字特征基线', (pw(48, 'diff_str'), pw(48, 'diff_str_lo'), pw(48, 'diff_str_hi')), [r'probe − 名字特征 ', r'probe − string '], '518 / 3,388')


def _prim(f, col):
    d = pd.read_csv(JL / PW); d = d[d.position == 'name_mean']
    return f(d[col])


A('gn-sh-min', 'C24：打乱标签 AUROC 最小（主分析 7 层）', py(lambda: _prim(min, 'shuffled_within'), 'probe_within.csv name_mean shuffled_within 最小', [PW]), CG, '—', 3, [r'打乱标签 #(?=–)', r'shuffled labels #(?=–)'], sign=False)
A('gn-sh-max', 'C24：打乱标签 AUROC 最大', py(lambda: _prim(max, 'shuffled_within'), '同上最大', [PW]), CG, '—', 3, [r'打乱标签 ' + NUM + '–#', r'shuffled labels ' + NUM + '–#'], sign=False)
A('gn-nlayers', 'C24：主分析 signal 成立的层数', py(lambda: int(_prim(lambda s: s.sum(), 'signal')), 'probe_within.csv name_mean signal = True 的层数', [PW]), '计数', '—', 0,
  [r'在 # 层都成立', r'passes at all # layers'], sign=False)
A('gn-ctrlM', 'C24：control 组真名（M）个数', md(GR, r'^## Labels', col='M', row={'group': 'control'}), 'b2_gennames_b_report.md Labels 表 control 行 M', '—', 0,
  [r'control 组只作描述（# 个真名）', r'descriptive only \(# true names\)'], sign=False)
CR = '事后名气基线（b2_gennames_b_robust_posthoc.md，事后，探索性）；'
T('gn-fame', 'C24：只用名气的 AUROC（事后）', (csv(RP, 'fame', layer=48), csv(RP, 'fame_lo', layer=48), csv(RP, 'fame_hi', layer=48)), [r'只用名气 ', r'fame alone '], '518 / 3,388', sign=False, comp=CR)
T('gn-pmc16', 'C24：probe −（排位 + 名字特征 + 名气）L16', (csv(RP, 'probe_minus_combined', layer=16), csv(RP, 'pmc_lo', layer=16), csv(RP, 'pmc_hi', layer=16)), [r'（L16 ', r'\(L16 '], '518 / 3,388', comp=CR)
T('gn-pmc48', 'C24：probe −（排位 + 名字特征 + 名气）L48', (csv(RP, 'probe_minus_combined', layer=48), csv(RP, 'pmc_lo', layer=48), csv(RP, 'pmc_hi', layer=48)), [r'… L48 '], '518 / 3,388', comp=CR)
# ---- Patchscope 2-7 / 2-9
PD, XT = '381_stage13/summary_b2_ps/ps_D.csv', '381_stage13/summary_b2_ps/x4tok_layers.csv'
CP = '补充 12 第 2-7 项 Patchscope，第一作者，D = 自身 − 配对，测试集，团队整群 95% CI（预注册要求报告、无判定规则）；'


def ps(src, L, col):
    return csv(PD, col, split='test', answer='author', src=src, layer=L)


def pss(src, L):
    return (ps(src, L, 'D'), ps(src, L, 'lo'), ps(src, L, 'hi'))


T('ps-name40', 'Patchscope：名字位置作源 L40', pss('name_all', 40), [r'L40 (?=\+0\.006)', r'L8–L16 约为 0，L40 ', r'at L8–L16, '], '测试集 582 对', comp=CP)
T('ps-name48', 'Patchscope：名字位置作源 L48', pss('name_all', 48), [r'，L48 (?=\+0\.014)', r'at L40, (?=\+0\.014)'], '测试集 582 对', comp=CP)
T('ps-title40', 'Patchscope：标题位置作源 L40', pss('title', 40), [r'（标题位置作源 L40 ', r'\(title source '], '测试集 582 对', comp=CP)
T('ps-colon48', 'Patchscope：“:” 位置作源 L48', pss('colon', 48), [r'到 L40 约为 0，L48 ', r'up to L40, '], '测试集 582 对', comp=CP)
T('ps-x4tok', 'x4tok：标题位置作源、姓的第一个 token L40', (csv(XT, 'mean', src='title', layer=40, role='surname_first'), csv(XT, 'lo', src='title', layer=40, role='surname_first'), csv(XT, 'hi', src='title', layer=40, role='surname_first')),
  [r'在 L40 最高 ', r'peaks at L40 '], '1,178 篇', comp='补充 12 第 2-9 项 x4tok，全部论文；')
# table cells (report / handbook K): rows title, colon, name_all, name_first_author x L8, L16, L40, L48, L56
ROWS = [('title', r'标题最后一个 token '), ('colon', r'“:” '), ('name_all', r'名字位置（全部） '), ('name_first_author', r'名字位置（第一作者的名字） ')]
for src, lab in ROWS:
    for k, L in enumerate([8, 16, 40, 48, 56]):
        pre = r'(?<=[\s>])' + lab + ''.join(NUM + CI_ + ' ' for _ in range(k))
        e, lo, hi = pss(src, L)
        A('pst-%s-L%d' % (src, L), 'Patchscope 表：%s L%d' % (src, L), e, CP, '测试集', 3, [pre + r'#(?= \[)'])
        A('pst-%s-L%d-lo' % (src, L), '同上下限', lo, CP, '测试集', 3, [pre + NUM + r' \[#'])
        A('pst-%s-L%d-hi' % (src, L), '同上上限', hi, CP, '测试集', 3, [pre + NUM + r' \[' + NUM + r', #\]'])
# ---- round j wording of the 3-1 J-lens T − C sentence ("在 L41–L55 为负、L56 约为 0（…）（L41 …") and the round-g |mean5 − false_0| range
LT = '381_stage13/summary_b3_s10_3_1/layer_tc.csv'
C31 = '3-1 补测层（补充 14），团队整群区间；layer_tc.csv；'


def tcj(L, col):
    return csv(LT, col, readout='jlens_public', layer=L, position='all', role='all')


J0 = r'L56 约为 0（'
A('b31j-L56', '3-1：J-lens target − control L56', tcj(56, 'tc_spec'), C31, '—', 3, [J0 + '#', r'about 0 at L56 \(#'])
A('b31j-L56-lo', '同上下限', tcj(56, 'tc_lo'), C31, '—', 3, [J0 + NUM + r' \[#'])
A('b31j-L56-hi', '同上上限', tcj(56, 'tc_hi'), C31, '—', 3, [J0 + NUM + r' \[' + NUM + ', #\]'])
J1 = J0 + NUM + CI_ + r'）（L41 '
A('b31j-L41', '3-1：J-lens target − control L41（round j 写法）', tcj(41, 'tc_spec'), C31, '—', 3, [J1 + '#'])
A('b31j-L41-lo', '同上下限', tcj(41, 'tc_lo'), C31, '—', 3, [J1 + NUM + r' \[#'])
A('b31j-L41-hi', '同上上限', tcj(41, 'tc_hi'), C31, '—', 3, [J1 + NUM + r' \[' + NUM + ', #\]'])
A('b31j-L47', '3-1：J-lens target − control L47（round j 写法）', tcj(47, 'tc_spec'), C31, '—', 3, [J1 + NUM + CI_ + r'，L47 #'])
A('b31j-L49', '3-1：J-lens target − control L49（round j 写法）', tcj(49, 'tc_spec'), C31, '—', 3, [J1 + NUM + CI_ + r'，L47 ' + NUM + r'，L49 #'])
M5 = '391_groups/summary_b1_p12f/p12f_mean5.csv'
HEAD = [('P1', 'all', 48), ('P1', 'all', 52), ('P1', 'names', 52), ('P2', 'attn', 48), ('P2', 'mlp', 52), ('P2', 'mlp', 56)]


def _d(f):
    d = pd.read_csv(JL / M5); d = d[(d.who == 'all_authors') & (d.group == 'all')]
    return f(abs(d[(d.experiment == e) & (d['item'] == i) & (d.layer == L)].mean5_minus_false0.iloc[0]) for e, i, L in HEAD)


A('p12-dmin', 'P1 / P2：六个主结果 |mean5 − false_0| 最小', py(lambda: _d(min), 'p12f_mean5.csv 六个主结果行 |mean5_minus_false0| 最小', [M5]), '—', '—', 3, [r'差的绝对值 #(?=–)'], sign=False)
A('p12-dmax', 'P1 / P2：同上最大', py(lambda: _d(max), '同上最大', [M5]), '—', '—', 3, [r'差的绝对值 ' + NUM + '–#'], sign=False)
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
