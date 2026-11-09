"""claims_defs v5 (2026-11-07): v4 (unchanged) + every result number of
  (1) the merged advisor progress report  351_stage10/reports/advisor/index.html  and
  (2) the merged-deck v20 slides that page relies on (body + speaker notes notes_zh.json):
      14, 16, 17, 24, 26, 30, 55, 59, 61, 67, 68, 69, 70, 71, 72, 81  (see SCOPE_SLIDES below for why).
New claim ids start with 'A5-' (no anchor-word filter; patterns are anchored on literal neighbouring text instead).
Every value is read by code from the named result file (csv / json / md table / md regex / small documented computation);
the numbers inside the regexes are only neighbouring text used to locate the occurrence, never the compared value.
Bound statements ("<= 0.05", "within +-0.02", ">= 0.96") are not equalities: they are listed in BOUNDS and checked by
claims_v5_post.py (pass / fail), not counted as claims.
Run with:  CLAIMS_DEFS=claims_defs_v5 bash claims_run.sh ;  then  python claims_v5_post.py <out_dir>"""
import json
import pandas as pd
from claims_defs_v4 import *          # noqa: F401,F403
from claims_defs_v4 import C, add, csv, md
from claims_lib import JL

J13 = '381_stage13/'
XA = J13 + 'summary_b1_xall/'
PDL = J13 + 'summary_b1_e4b5/perdonor_by_run_layer.csv'
PDN = J13 + 'summary_b1_e4b5/perdonor_n_used_L40.csv'
C3B = J13 + 'summary_c13/c3b/c3b_primary_L40.csv'
X7F = J13 + 'summary_b1_x7f/x7f_knockout.csv'
X7FJ = J13 + 'summary_b1_x7f/x7f_verdict.json'
X7K = J13 + 'summary_x7/x7_knockout.csv'
X6R = J13 + 'summary_x6/x6_recovery.csv'
X6RO = J13 + 'summary_x6/x6_roles.csv'
X1O = J13 + 'summary_x1x4/x1_recovery.csv'
X4O = J13 + 'summary_x1x4/x4_decodability.csv'
X4RS = J13 + 'summary_x1x4/x4_rolesplit.csv'
X3G = J13 + 'summary_x3/x3_gap.csv'
X3R = J13 + 'summary_x3/x3_recovery.csv'
X2V = J13 + 'summary_x2/x2_verdict.csv'
X2F = J13 + 'summary_x2/fit_sanity.csv'
M3R = J13 + 'reports/m3_report.md'
M2P = J13 + 'summary_cpu_group/M2_probes.csv'
V42 = J13 + 'summary_v42/x4_recognition_split.csv'
TSR = J13 + 'reports/e4b_trainstd_compare.md'
S12 = '371_stage12/summary/'
PRI = '371_stage12/summary_cpu/A_prior_decomposition.csv'
B = '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'
BR0 = '351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv'
CA = '351_stage10/summary_r0/target_R1_minus_R0_within_bin.csv'
X3M = '351_stage10/summary_extra/X3_means.csv'
SP = '351_stage10/summary_extra/X2_spearman.csv'
X1CR = '351_stage10/summary_extra/X1_cond_by_first_role.csv'
X1C = '351_stage10/summary_extra/X1_cond.csv'
AG = '351_stage10/summary_title/A_group_bin_layer.csv'
E1 = '361_stage11/summary/E1_recovery.csv'
S73N = '351_stage7_3/summary/paper_null_distribution.csv'
S73R = '351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv'
S73L = '351_stage7_3/recompute_2026-10-30/stage7_l56_loo.csv'
S73I = '351_stage7_3/summary/integrated_ab_bootstrap.csv'
S8 = '351_stage8/stage8D/summary/primary_questions.csv'
S8E = '351_stage8/recompute_2026-10-30/s8_endpoints.csv'
S8V = '351_stage8/stage8D/summary/jlens_minus_vanilla.csv'
S8B = '351_stage8/stage8D/summary/layer_and_band_summary.csv'

SCOPE_SLIDES = {
    14: 'Stage 7.3 Pilot50：导师页“+9.3 pp（Pilot50）”',
    16: 'Stage 8 方法页备注：导师页“Stage 8 冻结主终点复现 +2.33”、Stage 8 分析计划时间',
    17: 'Stage 8D：导师页“+5.18 pp [+2.93, +7.48]”“+2.41”',
    24: 'probe 方法页：导师页 E4b probe L24/L40/L56、M2 年份 R²、73%、补充 9 +0.071',
    26: '引用数页（备注）：导师页“ρ = 0.451”',
    30: 'A 线小结：导师页“主要发现”第 1–2 条（0.44、1/3、+0.21、ρ、R0 +0.199）',
    55: '名字格式页（备注）：导师页“名字内部”条',
    59: 'Keys and shelves 总览：导师页“一句话结论 / 主要发现”第 3–4 条（E1 0.82、P1、P2）',
    61: '小样本 vs 全量对照表：导师页“主要发现”与“各阶段完成情况”',
    67: 'Stage 12：导师页 P1 0.85 / 0.17、P2 0.23 / 0.18 / 0.22、F2 L62',
    68: 'Stage 13 X6/X7：导师页 0.82 / 0.995 / 0.029 / 0.051 与 X7 五个假标题',
    69: 'Stage 13 M3/X1：导师页“中间层……在 “:” 位置表示任务”、X1 批次 1',
    70: 'Stage 13 X4/X3：导师页 X4 +0.046、X3 L36 +0.16、约 90%',
    71: 'Stage 13 X2：导师页 X2 / H3 及批次 1 0.016 → 0.032',
    72: '补充 9 + E4b 五个假标题：导师页 +0.071、+0.076、+0.033、C-3b',
    81: '重做计划：导师页页首更新框（批次 1–3）',
}

MANUAL = []          # claims added below (ids), for the post-processing script


def A(cid, stmt, sel, comp, n, dec, occ, sign=True, scale=1, note='', alt=None):
    add('A5-' + cid, stmt, sel, comp, n, dec, occ, scale=scale, sign=sign, note=note)
    C[-1]['excl'] = None
    C[-1]['alt'] = alt or []
    MANUAL.append('A5-' + cid)


def tri(cid, stmt, sels, comp, n, dec, pats, sign=True, scale=1, note=''):
    """sels / pats: dicts with keys '', '-lo', '-hi'."""
    for k in ('', '-lo', '-hi'):
        if k in pats and pats[k]:
            A(cid + k, stmt + {'': '', '-lo': '（95% CI 下限）', '-hi': '（95% CI 上限）'}[k], sels[k], comp, n, dec, pats[k], sign=sign, scale=scale, note=note)


def py(fn, desc, files):
    return {'t': 'py', 'fn': fn, 'desc': desc, 'files': files}


def mdre(f, rx, nth=0):
    return {'t': 'mdre', 'f': f, 're': rx, 'nth': nth}


def jsn(f, path):
    return {'t': 'json', 'f': f, 'path': path}


def op(o, a, b):
    return {'t': 'op', 'op': o, 'a': a, 'b': b}


def CI3(f, est, lo, hi, **w):
    return {'': csv(f, est, **w), '-lo': csv(f, lo, **w), '-hi': csv(f, hi, **w)}


# ===================================================================================== advisor page update box (batch 1)
COMP_XA = '补充 10 第 1 项（全部作者、全部名字 token），测试集，团队聚类 bootstrap 2,000 次 95% CI'
tri('X1all-L48', 'X1 全部作者：L48 作者 − 年份（测试集）', CI3(XA + 'x1__all.csv', 'a_minus_year', 'a_minus_year_lo', 'a_minus_year_hi', split='test', layer=48),
    COMP_XA, '测试集 582 对', 3,
    {'': [r'作者 − 年份 #(?= \[0\.019)', r'author − year #'], '-lo': [r'作者 − 年份 \+0\.024 \[#'], '-hi': [r'作者 − 年份 \+0\.024 \[0\.019, #\]']})
XAR = dict(set='primary', subset='all', split='test', false='lexical_neighbour_D', group='all')
tri('X3all-ratio', 'X3 全部作者：改写标题行为恢复比 (para − D)/(orig − D)（测试集）', CI3(XA + 'x3_recovery__all.csv', 'ratio', 'lo', 'hi', **XAR), COMP_XA, '测试集 552 篇', 3,
    {'': [r'恢复比 #(?= \[)'], '-lo': [r'恢复比 0\.897 \[#'], '-hi': [r'恢复比 0\.897 \[0\.868, #\]']}, sign=False)
A('X3all-pct', 'X3 全部作者：保留的作者偏好（百分数）', csv(XA + 'x3_recovery__all.csv', 'ratio', **XAR), COMP_XA, '测试集 552 篇', 0,
  [r'保留约 #(?=% 的作者偏好)', r'X3 keeps ≈ #(?=%)'], sign=False, scale=100)
A('X3all-n', 'X3 全部作者：测试集篇数', csv(XA + 'x3_recovery__all.csv', 'n', **XAR), '计数', '—', 0, [r'测试集 #(?= 篇，恢复比)'], sign=False)
tri('X4all-L8', 'X4 全部作者：L8 作者答案 D = self − partner（测试集）', CI3(XA + 'x4_D__all.csv', 'D', 'lo', 'hi', split='test', answer='author', pos='title', layer=8),
    COMP_XA, '测试集 582 对', 3,
    {'': [r'全部作者 #(?= \[0\.039)'], '-lo': [r'全部作者 \+0\.048 \[#'], '-hi': [r'全部作者 \+0\.048 \[0\.039, #\]']})
XVO, XVN = XA + 'x2_verdict_old__all.csv', XA + 'x2_verdict_new__all.csv'
A('X2all-old', 'X2 全部作者打分、旧作者子空间：L48 搬动量 R_auth（测试集）', csv(XVO, 'auth_R_S'), '测试集 582 对，均值比 R_S', '582 对', 3, [r'搬动量从 #(?= 升到)'], sign=False)
A('X2all-new', 'X2 全部作者打分、新作者子空间：L48 搬动量 R_auth（测试集）', csv(XVN, 'auth_R_S'), '同上', '582 对', 3, [r'升到 #(?=（完整替换)', r'X2 moves #'], sign=False)
A('X2all-pct', 'X2 新作者子空间搬动量占完整替换的比例', op('div', csv(XVN, 'auth_R_S'), csv(XVN, 'auth_R_full')), 'auth_R_S ÷ auth_R_full（L48，测试集）', '582 对', 0,
  [r'完整替换的约 #(?=%）)'], sign=False, scale=100)
A('X2all-r2', 'X2 新作者子空间（全部作者）留出 R² 最大值（L16–L48）', csv(XA + 'fit_authall_sanity.csv', 'authall_r2', 'max'), '5 折团队留出 R²，5,041 篇训练论文，L16–L48 取最大', '5,041 篇', 3,
  [r'留出 R² ≤ #(?=）)', r'authall_r2 ≤ #', r'subspace R² ≤ #'], sign=False)

# ---- E4b five false titles, per-donor exclusion (Vpd)
DEF_VPD = ('Vpd = 真标题 − 供体不在训练折的假标题的平均（至少 1 个可用）；保留的论文平均只用 1.50 个假标题（0 个可用的 2,187 篇被剔除），'
           '不是 5 个假标题的平均；目标 + 对照，团队聚类 bootstrap 2,000 次 95% CI')
A('E4b5-kept', 'E4b 五个假标题（Vpd）：L40 保留的目标 + 对照篇数', csv(PDN, 'kept', run='surname_first'), '计数（至少 1 个可用假标题）', '—', 0,
  [r'保留 #(?= 篇，平均)', r'Per-donor exclusion, #(?= papers)'], sign=False)
A('E4b5-mean', 'E4b 五个假标题（Vpd）：保留论文平均用到的假标题个数', csv(PDN, 'mean_used', run='surname_first'), 'perdonor_n_used_L40.csv 列 mean_used（只在保留论文上平均）', '4,654 篇', 1,
  [r'平均 #(?= 个假标题）)'], sign=False)
tri('E4b5-sur', 'E4b Vpd：L40 姓的第一个 token 标题特异信号', CI3(PDL, 'spec', 'lo', 'hi', run='surname_first', layer=40, version='Vpd'), DEF_VPD, '4,654 篇', 3,
    {'': [r'L40 姓首 token #', r'减 5 个假标题平均 #', r'surname L40 #'], '-lo': [r'姓首 token \+0\.076 \[#', r'surname L40 \+0\.076 \[#'],
     '-hi': [r'姓首 token \+0\.076 \[0\.068, #\]', r'surname L40 \+0\.076 \[0\.068, #\]']},
    note='口径：Vpd 平均约 1.5 个假标题，不是 5 个假标题的平均（V5 规则保留 0 篇）')
tri('E4b5-smi', 'E4b Vpd：L40 姓 − 首字母（联合团队抽样）', CI3(C3B, 'est', 'lo', 'hi', version='Vpd', quantity='surname_minus_initial'), DEF_VPD, '9,466 个论文×角色', 3,
    {'': [r'姓 − 首字母 #(?= \[0\.023)', r'surname − initial #(?![.\d])'], '-lo': [r'姓 − 首字母 \+0\.033 \[#'], '-hi': [r'姓 − 首字母 \+0\.033 \[0\.023, #\]']})
A('E4b5-e4b', 'E4b Vpd：L40 原 E4b 第一个 token（e4b_parity 运行）', csv(PDL, 'spec', run='e4b_parity', layer=40, version='Vpd'), DEF_VPD, '4,654 篇', 3, [r'原 E4b 第一个 token #'],
  note='“原 E4b 第一个 token +0.066”是 Vpd 版本；已发表 E4b（V0，false_0）L40 为 +0.061')
A('E4b5-perm', 'E4b Vpd：L40 首字母置换对照（随机另一篇论文的作者）', csv(PDL, 'ctrl_any', run='initial', layer=40, version='Vpd'), DEF_VPD, '4,812 篇', 3, [r'置换对照首字母仍 #'])
A('E4b5-hc', 'E4b 硬检查：V0 e4b_parity L40（复现已发表 +0.061）', csv(PDL, 'spec', run='e4b_parity', layer=40, version='V0'), '真标题 − false_0，false_0 剔除规则', '1,395 篇', 4, [r'硬检查 E4b L40 #'])
tri('E4b5-givL16', 'E4b Vpd：名的第一个 token L16 引用档内 target − control', CI3(PDL, 'tc', 'tc_lo', 'tc_hi', run='given_first', layer=16, version='Vpd'), DEF_VPD, '3,046 篇', 3,
    {'-lo': [r'given_first L16 \+0\.029 \[#'], '-hi': [r'given_first L16 \+0\.029 \[\+0\.005, #\]']})
tri('E4b5-surL24', 'E4b Vpd：姓的第一个 token L24 引用档内 target − control', CI3(PDL, 'tc', 'tc_lo', 'tc_hi', run='surname_first', layer=24, version='Vpd'), DEF_VPD, '4,654 篇', 3,
    {'': [r'surname_first L24 #'], '-lo': [r'surname_first L24 \+0\.019 \[#'], '-hi': [r'surname_first L24 \+0\.019 \[\+0\.001, #\]']})
A('E4b5-V0n', 'V0（false_0）版本 / 补充 9：姓的第一个 token L40 目标 + 对照篇数', csv(PDL, 'n', run='surname_first', layer=40, version='V0'), '计数', '—', 0,
  [r'V0，#(?= 篇）)', r'#(?= papers; e4b_alltok\.md)', r'目标 \+ 对照 #(?= 篇，(?:团队|剔除))'], sign=False)
# ---- X7 five false titles
for g, gl in [('target', 't'), ('control', 'c'), ('all', 'a')]:
    pats = {'t': {'': [r'S\(L52\) 分别为 #', r'target #(?=, control \+0\.042)'], '-lo': [r'95% CI \[#(?=, 0\.029\] /)'], '-hi': [r'95% CI \[0\.015, #(?=\] /)']},
            'c': {'': [r'分别为 \+0\.022、#', r'control #(?=, all \+0\.028)', r'control #(?=，已满足判据)'], '-lo': [r'\] / \[#(?=, 0\.055\])'], '-hi': [r'\[0\.028, #(?=\] / \[0\.022)']},
            'a': {'': [r'\+0\.042、#(?=，均)', r'all #(?= — all)'], '-lo': [r'0\.055\] / \[#'], '-hi': [r'\] / \[0\.022, #\]']}}[gl]
    tri('X7f-' + gl, 'X7 五个假标题平均：%s S(L52)' % g, {'': jsn(X7FJ, ['verdict', 'mean5', g, 'S_L52']), '-lo': jsn(X7FJ, ['verdict', 'mean5', g, 'S_L52_lo']),
                                                    '-hi': jsn(X7FJ, ['verdict', 'mean5', g, 'S_L52_hi'])},
        '补充 10 第 2 项：S = T − F，逐个假标题各用自己的分母，5 个平均；团队聚类 95% CI', '593 / 593 / 1,186 篇', 3, pats)
for k in range(5):
    pat = [r'逐个假标题 #(?= / 0\.035)', r'逐个假标题 0\.051 / #', r'0\.035 / #(?= / 0\.033)', r'0\.048 / #(?= / 0\.041)', r'0\.033 / #(?=；同一报告)'][k]
    A('X7f-c-f%d' % k, 'X7 control S(L52)，false_%d' % k, csv(X7F, 'S', group='control', start_layer=52, title='false_%d' % k), '同上，单个假标题', '593 篇', 3, [pat], sign=False)
A('X7f-n-t', 'X7 五个假标题：target 篇数', csv(X7F, 'n_papers', group='target', start_layer=52, title='false_0'), '计数', '—', 0, [r'target #(?= / control 593 / 全部)'], sign=False)
A('X7f-n-a', 'X7 五个假标题：全部篇数', csv(X7F, 'n_papers', group='all', start_layer=52, title='false_0'), '计数', '—', 0, [r'/ 全部 #(?= 篇)'], sign=False)
X7KW = lambda g, col='S', L=52: csv(X7K, col, group=g, start_layer=L)
A('X7-c0', 'X7（只用 false_0）对照组 S(L52)', X7KW('control'), 'Stage 13 X7，S = T − F，false_0；团队聚类 95% CI', 'control 593 篇', 3,
  [r'只用 false_0 时为 #', r'control 组 #(?=，略高于)', r'control just misses \(#', r'control’s #', r'不成立（#'], sign=False)
tri('X7-c0ci', 'X7（只用 false_0）对照组 S(L52)', {'': X7KW('control'), '-lo': X7KW('control', 'S_lo'), '-hi': X7KW('control', 'S_hi')}, '同上', '593 篇', 3,
    {'-lo': [r'0\.051〔X7，control 593 篇，\[#'], '-hi': [r'0\.051〔X7，control 593 篇，\[0\.033, #\]']}, sign=False)
tri('X7-a', 'X7（只用 false_0）全部论文 S(L52)', {'': X7KW('all'), '-lo': X7KW('all', 'S_lo'), '-hi': X7KW('all', 'S_hi')}, '同上', '1,186 篇', 3,
    {'': [r'损失只剩 #', r'S\(L52\) = #'], '-lo': [r'S\(L52\) = 0\.029 \[#', r'全部论文，团队 CI \[#'], '-hi': [r'S\(L52\) = 0\.029 \[0\.021, #\]', r'全部论文，团队 CI \[0\.021, #\]']}, sign=False)
tri('X7-t', 'X7（只用 false_0）target S(L52)', {'': X7KW('target'), '-lo': X7KW('target', 'S_lo'), '-hi': X7KW('target', 'S_hi')}, '同上', '593 篇', 3,
    {'': [r'target \(S\(L52\) #', r'target 成立（#'], '-lo': [r'0\.018〔X7，target 593 篇，\[#'], '-hi': [r'0\.018〔X7，target 593 篇，\[0\.010, #\]']}, sign=False)
A('X7-L0', 'X7（只用 false_0）全部论文 S(L0)', X7KW('all', 'S', 0), '同上', '1,186 篇', 3, [r'all: #(?=; x7_report)', r'全部 #(?=；381_stage13/reports/x7_report)'], sign=False)
A('X7-L0-2', 'X7 全部论文 S(L0)（两位小数写法）', X7KW('all', 'S', 0), '同上', '1,186 篇', 2, [r'S\(L0\) ≈ (?P<v>1\.00)(?!\d)'], sign=False)
# ---- C-3b
C3 = dict(version='V5x0_noexcl')
for q, ql, pe, plo, phi in [('surname_first', 'sur', r'PASS[；，]L40 姓的第一个 token #', r'PASS[；，]L40 姓的第一个 token \+0\.077 \[#', r'PASS[；，]L40 姓的第一个 token \+0\.077 \[0\.071, #\]'),
                            ('initial', 'ini', r'首字母 #(?= \[0\.029)', r'首字母 \+0\.034 \[#', r'首字母 \+0\.034 \[0\.029, #\]'),
                            ('surname_minus_initial', 'smi', r'姓 − 首字母 #(?= \[0\.035)', r'姓 − 首字母 \+0\.043 \[#', r'\+0\.043 \[0\.035, #\]')]:
    tri('C3b-' + ql, 'C-3b（不剔除标题复用，含泄漏，敏感性）L40 %s' % q, CI3(C3B, 'est', 'lo', 'hi', quantity=q, **C3),
        '补充 13 C-3b：真标题 − 5 个假标题平均，不剔除任何论文 / 假标题；团队聚类 95% CI', '6,841 篇', 3, {'': [pe], '-lo': [plo], '-hi': [phi]})
A('C3b-n', 'C-3b 篇数', csv(C3B, 'n', quantity='surname_first', **C3), '计数', '—', 0, [r'0\.051\]（#(?= 篇)', r'〔#(?= 篇；381_stage13/reports/c13_C3b)'], sign=False)

# ===================================================================================== advisor page main text
AUD = '351_all/351_audit.json'
A('N-T', 'target 篇数 = A + C', op('add', jsn(AUD, ['group_counts', 'A']), jsn(AUD, ['group_counts', 'C'])), 'A + C', '—', 0,
  [r'（target，#', r'目标 #(?=、对照 2,220)', r'目标 #(?= / 对照 2,220)', r'目标 #(?= 篇 0\.328)'], sign=False)
A('N-Ctl', 'control 篇数 = B + D', op('add', jsn(AUD, ['group_counts', 'B']), jsn(AUD, ['group_counts', 'D'])), 'B + D', '—', 0,
  [r'（control，#', r'目标 4,621、对照 #', r'目标 4,621 / 对照 #', r'对照 #(?= 篇 0\.187)'], sign=False)
X3P = csv(X3M, 'mean', layer=62, metric='spec', readout='jlens_public')
A('X3L62-2', 'L62 public J-lens 标题特异信号（两位小数写法“约 0.44”）', X3P, '真标题 − 5 个假标题平均，全部 9,108 篇均值', '9,108 篇', 2,
  [r'L62 约 #(?=；名字先验)', r'≈#(?= at L62)', r'≈#(?= title-specific at L62)', r'L62 约 #(?=〔Stage 10)', r'L62 标题特异约 #'], sign=False)
A('PR-recip', '名字先验占比的倒数（文中写作“约 1/3”的分母）', op('div', csv(PRI, 'true', readout='final', layer=63, role='all_tokens', group='tc_true'),
                                                         csv(PRI, 'prior', readout='final', layer=63, role='all_tokens', group='tc_prior')),
  '真标题差 ÷ 先验（= 1 ÷ 先验占比 0.35）；“1/3”按整数分母比较', '4,621 / 2,220', 0, [r'差的约 1/#', r'only ~1/#'], sign=False,
  note='先验占比源值 0.35（0.087 ÷ 0.247）；“约 1/3”= 0.33，按分母取整一致，但同一页备注写 0.35')
F63 = dict(readout='final', layer=63)
A('S10-out2', '输出处目标−对照（两位小数写法 +0.21）', csv(B, 'spec_mean_nlr_diff', **F63), '引用档内 目标−对照，最终输出 L63', '3,734 / 2,182', 2,
  [r'输出处 #(?=。写对)', r'#(?= at output(?![\u200b ]?\(§6\.13))', r'（输出处 #(?=）)', r'输出处 #(?=〔)'])
tri('S10-out2b', '输出处目标−对照及 CI（两位小数写法）', CI3(B, 'spec_mean_nlr_diff', 'spec_mean_nlr_lo', 'spec_mean_nlr_hi', **F63), '同上', '3,734 / 2,182', 2,
    {'': [r'#(?= \[0\.20, 0\.22\] at the output)'], '-lo': [r'\+0\.21 \[#(?=, 0\.22\])'], '-hi': [r'\+0\.21 \[0\.20, #\]']})
tri('S10-out3mix', '输出处目标−对照（三位估计、两位区间的混写）', CI3(B, 'spec_mean_nlr_diff', 'spec_mean_nlr_lo', 'spec_mean_nlr_hi', **F63), '同上', '3,734 / 2,182', 3,
    {'': [r'输出处 #(?= \[0\.20, 0\.22\])'], '-lo': [r'输出处 \+0\.207 \[#'], '-hi': [r'输出处 \+0\.207 \[0\.20, #\]']})
tri('S10-R0-2', '只用 R0：A − B 输出处（两位小数写法）', CI3(BR0, 'spec_mean_nlr_diff', 'spec_mean_nlr_lo', 'spec_mean_nlr_hi', **F63), '引用档内，A 对 B（都只保留 R0）', 'A 3,423 / B 2,151', 2,
    {'': [r'#(?= \[0\.19, 0\.21\])', r'#(?= at output.?\(§6\.13)', r'输出 #(?=〔Stage 10 只用 R0)'], '-lo': [r'\+0\.20 \[#(?=, 0\.21\])'], '-hi': [r'\+0\.20 \[0\.19, #\]']})
A('S10-CA-2', 'C − A 输出处（两位小数写法）', csv(CA, 'spec_mean_nlr_diff', **F63), '目标组内 R1 − R0，引用档内', 'C 485 / A 3,204', 2, [r'\(#(?= over A\))', r'比 A 多 #'])
BJ = dict(readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=48)
A('S10-L48-2max', 'L48 三种 J-lens 目标−对照（离 0 最近，两位写法）', csv(B, 'spec_mean_nlr_diff', 'max', **BJ), '三种 J-lens 取最大', '3,734 / 2,182', 2, [r'at L48 \(#(?= to −0\.05\))'])
A('S10-L48-2min', 'L48 三种 J-lens 目标−对照（最负，两位写法）', csv(B, 'spec_mean_nlr_diff', 'min', **BJ), '三种 J-lens 取最小', '3,734 / 2,182', 2, [r'at L48 \(−0\.04 to #\)'])
X6A = lambda L, col='R': csv(X6R, col, group='all', false_title='average', layer=L)
A('X6-L48-2', 'X6 五个假标题平均 R(L48)（两位写法）', X6A(48), 'Stage 13 X6，均值比，团队聚类 95% CI', '1,186 篇', 2, [r'L48 恢复 #(?=，L52 恢复 0\.995)'], sign=False)
tri('X6-L48', 'X6 五个假标题平均 R(L48)', {'': X6A(48), '-lo': X6A(48, 'lo'), '-hi': X6A(48, 'hi')}, 'Stage 13 X6，均值比，团队聚类 95% CI', '1,186 篇', 3,
    {'': [r'#(?= at L48 and 0\.995)', r'L48 为 #(?=、L52 为 0\.995)'], '-lo': [r'CI L48 \[#'], '-hi': [r'CI L48 \[0\.806, #\]']}, sign=False)
tri('X6-L52', 'X6 五个假标题平均 R(L52)', {'': X6A(52), '-lo': X6A(52, 'lo'), '-hi': X6A(52, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'L52 恢复 #(?=（5 个假标题平均)', r'0\.821 at L48 and #', r'L52 为 #(?=〔Stage 13 X6)'], '-lo': [r'、L52 \[#(?=, 1\.001\])'], '-hi': [r'、L52 \[0\.990, #\]']}, sign=False)


def _x6_spread(groups=('target', 'control', 'all')):
    d = pd.read_csv(JL / X6R)
    d = d[d.group.isin(groups) & d.layer.isin([48, 52]) & d.false_title.str.contains(' - false_0')]
    return d.R.abs().max()


A('X6-spread', 'X6：各假标题与 false_0 的最大差（L48、L52，target / control / all）', py(_x6_spread, 'x6_recovery.csv 行 false_title="false_k - false_0"、layer∈{48,52}、group∈{target,control,all} 列 R 取 |·| 最大', [X6R]),
  '最大绝对差', '1,186 篇', 3, [r'对照组最大 #(?=〕)'], sign=False)
X6RL = lambda role, L, col='R': csv(X6RO, col, role=role, group='all', false_title='average', layer=L)
tri('X6r-sur', 'X6 角色：姓的第一个 token R(L48)', {'': X6RL('surname_first', 48), '-lo': X6RL('surname_first', 48, 'lo'), '-hi': X6RL('surname_first', 48, 'hi')},
    'X6 按名字 token 角色，5 个假标题平均，全部论文；团队 CI', '1,186 篇', 3,
    {'': [r'surname first token #(?= at L48)', r'姓的第一个 token L48 为 #'], '-lo': [r'团队 CI \[#(?=, 0\.757\])'], '-hi': [r'团队 CI \[0\.711, #\]']}, sign=False)
tri('X6r-cont', 'X6 角色：姓的后续 token R(L48)', {'': X6RL('surname_cont', 48), '-lo': X6RL('surname_cont', 48, 'lo'), '-hi': X6RL('surname_cont', 48, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'surname continuation #', r'姓的后续 token #'], '-lo': [r'0\.757\] / \[#'], '-hi': [r'\] / \[0\.880, #\]']}, sign=False)
# ---- Stage 12 P1 / P2 / N1 / N2 / F2
P1 = lambda item, L, col='recovery': csv(S12 + 'P1_patch_pos.csv', col, layer=L, item=item, group='all')
A('P1-names2', 'P1 只换名字位置 L52（两位写法）', P1('names', 52), 'Stage 12 P1，真标题→false_0，最终输出恢复比例；论文 bootstrap', '1,186 篇', 2,
  [r'只替换名字位置在 L52 恢复 #', r'全部名字位置一起 #', r'all name positions together #', r'0\.61 → #', r'从 0\.61 升到 #'], sign=False)
tri('P1-names3', 'P1 只换名字位置 L52', {'': P1('names', 52), '-lo': P1('names', 52, 'lo'), '-hi': P1('names', 52, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'L52 #(?= \[0\.830)', r'L52 #(?=，单个位置最大)'], '-lo': [r'CI \[#(?=, 0\.864\])'], '-hi': [r'\[0\.830, #\]']}, sign=False)
A('P1-names48', 'P1 只换名字位置 L48', P1('names', 48), '同上', '1,186 篇', 2, [r'name positions alone #(?= →)', r'从 #(?= 升到 0\.85)', r'L48 #(?=、L52 0\.847)'], sign=False)
A('P1-colon2', 'P1 单个位置最大（“:” L52，两位写法）', csv(S12 + 'P1_patch_pos.csv', 'recovery', 'max', layer=52, group='all', item=['p%d' % i for i in range(1, 10)]),
  'Stage 12 P1，9 个单位置取最大', '1,186 篇', 2, [r'只替换 “:” 最多 #', r'“:” 最多恢复 #', r'the colon carries at most #', r'‘:’ alone ≤ #', r'只换“:”最多 #'], sign=False)
tri('P1-colon3', 'P1 “:”（p 位置）L52 恢复', {'': csv(S12 + 'P1_patch_pos.csv', 'recovery', 'max', layer=52, group='all', item=['p%d' % i for i in range(1, 10)]),
                                          '-lo': {'t': 'mdre', 'f': '371_stage12/summary/P1_patch_pos.csv', 're': r'^52,p\d,all,0\.17\d+,([\d.]+),', 'nth': 0},
                                          '-hi': {'t': 'mdre', 'f': '371_stage12/summary/P1_patch_pos.csv', 're': r'^52,p\d,all,0\.17\d+,[\d.]+,([\d.]+)', 'nth': 0}},
    '同上（行 layer=52, group=all, recovery 0.17x 的单位置行）', '1,186 篇', 3,
    {'': [r'“:” L52 #'], '-lo': [r'95% CI \[#(?=, 0\.187\])', r'0\.172 \[#'], '-hi': [r'\[0\.156, #\]']}, sign=False)
A('P1-all2', 'P1 替换整个提示 L52（两位写法）', P1('all', 52), '同上', '1,186 篇', 2, [r'the whole prompt #', r'整个提示 #'], sign=False)
A('P1-all3', 'P1 替换整个提示 L52', P1('all', 52), '同上', '1,186 篇', 3, [r'\(same, #\)', r'E1，L52 #'], sign=False)
P2 = lambda comp, L, col='recovery': csv(S12 + 'P2_patch_comp.csv', col, comp=comp, layer=L, group='all')
tri('P2-att2', 'P2 L48 attention 恢复（两位写法）', {'': P2('attn', 48), '-lo': P2('attn', 48, 'lo'), '-hi': P2('attn', 48, 'hi')}, 'Stage 12 P2，只替换单层组件；最终输出恢复比例', '1,186 篇', 2,
    {'': [r'把标题带进来（#', r'at L48 \(#(?=\); MLP)', r'恢复 #(?=）〔Stage 12 P2)', r'attention at L48 #(?= \[0\.22)', r'L48 注意力 #(?=〔)'],
     '-lo': [r'L48 \+0\.23 \[#'], '-hi': [r'\+0\.23 \[0\.22, #\]']}, sign=False)
tri('P2-att3', 'P2 L48 attention 恢复', {'': P2('attn', 48), '-lo': P2('attn', 48, 'lo'), '-hi': P2('attn', 48, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'attention L48 #(?=（MLP)', r'L48 注意力 #(?= \[0\.221)'], '-lo': [r'注意力 0\.231 \[#'], '-hi': [r'0\.231 \[0\.221, #\]']}, sign=False)
A('P2-mlp48', 'P2 L48 MLP 恢复', P2('mlp', 48), '同上', '1,186 篇', 2, [r'（MLP #(?=）)'], sign=False)
A('P2-mlp52-2', 'P2 L52 MLP（两位写法）', P2('mlp', 52), '同上', '1,186 篇', 2, [r'接手（#(?=、)', r'\(#(?=, 0\.22\))', r'MLP at L52–L56 #', r'MLP #(?= 到 \+0\.22)'], sign=False)
A('P2-mlp56-2', 'P2 L56 MLP（两位写法）', P2('mlp', 56), '同上', '1,186 篇', 2, [r'接手（0\.18、#', r'\(0\.18, #\)', r'\+0\.18 to #', r'\+0\.18 到 #'], sign=False)
tri('P2-mlp52', 'P2 L52 MLP', {'': P2('mlp', 52), '-lo': P2('mlp', 52, 'lo'), '-hi': P2('mlp', 52, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'MLP L52 #'], '-lo': [r'MLP L52 0\.178 \[#'], '-hi': [r'0\.178 \[0\.168, #\]']}, sign=False)
tri('P2-mlp56', 'P2 L56 MLP', {'': P2('mlp', 56), '-lo': P2('mlp', 56, 'lo'), '-hi': P2('mlp', 56, 'hi')}, '同上', '1,186 篇', 3,
    {'': [r'L56 #(?= \[0\.208)', r'L56 #(?=；报告 Stage 12 节 P2)'], '-lo': [r'L56 0\.224 \[#'], '-hi': [r'0\.224 \[0\.208, #\]']}, sign=False)
N1 = lambda p, col: csv(S12 + 'N1_prior_mc.csv', col, prompt=p, group='all')
tri('N1-del', 'N1 删去标题：真作者列表“最像真的”比例', {'': N1('delete', 'true_list_most_plausible'), '-lo': N1('delete', 'best_lo'), '-hi': N1('delete', 'best_hi')},
    'Stage 12 N1，4 个选项中真列表打分最高的比例；R0/R1 论文', '8,894 篇', 3,
    {'': [r'most real" in #', r'“most real” in #', r'比例 #(?=〔Stage 12 N1)'], '-lo': [r'CI \[#(?=, 0\.264\])'], '-hi': [r'\[0\.246, #\]']}, sign=False)
tri('N1-true', 'N1 真标题：真作者列表“最像真的”比例', {'': N1('true', 'true_list_most_plausible'), '-lo': N1('true', 'best_lo'), '-hi': N1('true', 'best_hi')}, '同上', '8,894 篇', 3,
    {'': [r'with the true title #', r'给真标题后 #'], '-lo': [r'CI \[#(?=, 0\.635\])'], '-hi': [r'\[0\.615, #\]']}, sign=False)
A('N1-n', 'N1 论文数', N1('delete', 'n'), '计数', '—', 0, [r'#(?= R0/R1 papers)', r'R0/R1 论文 #'], sign=False)
N2 = lambda g, col: csv(S12 + 'N2_prior_pure.csv', col, group=g)
tri('N2-pure', 'N2 纯名字提示 target − control', {'': N2('tc_pure', 'pure'), '-lo': N2('tc_pure', 'lo'), '-hi': N2('tc_pure', 'hi')}, 'Stage 12 N2，最终输出 L63，引用档内；论文 bootstrap', '4,621 / 2,220', 3,
    {'': [r'target − control #(?= \[0\.031)', r'只有 #(?=〔Stage 12 N2)'], '-lo': [r'\+0\.047 \[#', r'论文 bootstrap 95% CI \[#(?=, 0\.062\])'], '-hi': [r'\[0\.031, #\]']})
tri('N2-true', 'N2 真标题 target − control', {'': N2('tc_true', 'true'), '-lo': N2('tc_true', 'lo'), '-hi': N2('tc_true', 'hi')}, '同上', '4,621 / 2,220', 3,
    {'': [r'vs #(?= with the true title)', r'真标题下 #'], '-lo': [r'真标题，\[#'], '-hi': [r'真标题，\[0\.229, #\]']})
A('N2-share', 'N2 先验占比（纯名字 ÷ 真标题）', op('div', N2('tc_pure', 'pure'), N2('tc_true', 'true')), '0.047 ÷ 0.247', '—', 0, [r'prior ≈ #(?=% of the gap)', r'先验约占 #(?=%)'],
  sign=False, scale=100, note='与 A 部分“名字先验约 1/3”（A_prior_decomposition 0.35）定义不同：这里是纯名字提示 N2')
F2L = lambda col: csv(S12 + 'F2_author_lens.csv', col, layer=62, position='name')
tri('F2-L62', 'F2 作者提示 lens：名字位置 L62 target − control', {'': F2L('tc'), '-lo': F2L('tc_lo'), '-hi': F2L('tc_hi')}, 'Stage 12 F2，真 − 5 个假标题平均，Stage 11 样本', '1,186 篇', 3,
    {'': [r'#(?= only at L62)', r'只有 L62 为 #'], '-lo': [r'Stage 11 样本，\[#'], '-hi': [r'\[0\.210, #\]']})
# ---- E4b (single probe) CI, M2, X3, X4, X1, M3, X2 (original first-author versions)
tri('E4b-tsL40ci', 'E4b 训练折标准化 L40（全部论文）', {'': md(TSR, r'all papers', col='new', row={'layer': 'L40'}),
                                                  '-lo': md(TSR, r'all papers', col='new CI', part='est', row={'layer': 'L40'}),
                                                  '-hi': md(TSR, r'all papers', col='new CI', part='lo', row={'layer': 'L40'})},
    'Stage 13 E4b 复核：团队分折 + 剔除标题复用 + 训练折内标准化；论文 bootstrap', '1,863 篇', 3,
    {'-lo': [r'L40 (?:为 )?\+0\.061 \[#'], '-hi': [r'L40 (?:为 )?\+0\.061 \[0\.047, #\]']})
A('E4b-tsmax', 'E4b 训练折标准化：全部论文信号新旧最大变化', mdre(TSR, r'E4b all-paper signal (0\.\d+)'), 'e4b_trainstd_compare.md “Max |new - orig|”行', '1,863 篇', 4, [r'最大变化 #'], sign=False)
M2 = lambda tg, agg=None, **w: csv(M2P, 'value', agg, condition='true', position='title', target=tg, **w)
A('M2-yr16', 'M2 年份 R² L16（两位写法）', M2('year', layer=16), 'Stage 13 M2，团队分折 probe，标题最后一个 token', '9,108 篇', 2, [r'R² 从 #(?=（L16）)', r'L16 的 #(?= 升到)'], sign=False,
  alt=[('381_stage13/summary_cpu/M2_probes.csv（按论文分折的旧版，L16 0.385）', csv(J13 + 'summary_cpu/M2_probes.csv', 'value', condition='true', position='title', target='year', layer=16), '写法不统一')])
A('M2-yr16-3', 'M2 年份 R² L16', M2('year', layer=16), '同上', '9,108 篇', 3, [r'L16 #(?= → L52 0\.561)'], sign=False)
A('M2-yrmax', 'M2 年份 R² 最高（L52，两位写法）', M2('year', 'max'), '同上，L16–L60 取最大', '9,108 篇', 2, [r'（L16）升到 #', r'L52 的 #(?=〔)'], sign=False)
A('M2-yrmax-3', 'M2 年份 R² 最高（L52）', M2('year', 'max'), '同上', '9,108 篇', 3, [r'→ L52 #(?=，团队整群)'], sign=False)
A('M2-citmax', 'M2 引用数 R² 最高', M2('log citations', 'max'), '同上，L16–L60 取最大', '9,108 篇', 2, [r'引用数到 #'], sign=False)
A('M2-field', 'M2 领域准确率（“约 0.70”）', M2('field', 'min'), '同上，L16–L60 取最小（= L16）', '9,108 篇', 2, [r'领域准确率约 #(?=，“是否认得出”)'], sign=False,
  note='L16–L60 为 0.698–0.722；“约 0.70”只对应 L16（最低层），最高层为 0.72')
A('M2-aucmin', 'M2 “是否认得出” AUROC 最低', M2('recognised (target vs control)', 'min'), '同上，L16–L60 取最小', '9,108 篇', 2, [r'AUROC #(?=–0\.67)'], sign=False)
A('M2-aucmax', 'M2 “是否认得出” AUROC 最高', M2('recognised (target vs control)', 'max'), '同上，L16–L60 取最大', '9,108 篇', 2, [r'AUROC 0\.62–#'], sign=False)
X3GW = dict(set='primary', subset='all', split='test', comparison='lex', pos='title_last', layer=36)
tri('X3-L36', 'X3 改写标题 G′ − G′(L4) 最高（L36，测试集）', CI3(X3G, 'gap_minus_L4', 'dL4_lo', 'dL4_hi', **X3GW), 'Stage 13 X3 主分析，测试集；团队 CI', '552 篇', 2,
    {'': [r'peak L36 (?P<v>\+?0\.\d\d)(?!\d)', r'最高 L36 (?P<v>\+?0\.\d\d)(?!\d)']})
A('X3-L36-3', 'X3 L36（三位写法）', csv(X3G, 'gap_minus_L4', **X3GW), '同上', '552 篇', 3, [r'最高 L36 (?P<v>\+0\.\d\d\d)(?!\d)'])
tri('X3-L36ci', 'X3 L36 CI（三位）', CI3(X3G, 'gap_minus_L4', 'dL4_lo', 'dL4_hi', **X3GW), '同上', '552 篇', 3,
    {'-lo': [r'team CI \[#(?=, 0\.171\])', r'团队 CI \[#(?=, 0\.171\])'], '-hi': [r'\[0\.146, #\]']})
A('X3-n', 'X3 测试集篇数', csv(X3G, 'n', **X3GW), '计数', '—', 0, [r'test #(?= papers, G′)', r'测试集 #(?= 篇，G′)'], sign=False)
X3RW = dict(set='primary', subset='all', split='test', false='lexical_neighbour_D', group='all')
tri('X3-beh', 'X3 行为恢复比（测试集，D 近邻）', CI3(X3R, 'ratio', 'lo', 'hi', **X3RW), 'Stage 13 X3 主分析，(para − D)/(orig − D)；团队 CI', '552 篇', 2,
    {'': [r'same, #(?= \[0\.87)', r'#(?= \[0\.87, 0\.94\])'], '-lo': [r'(?:same, |教师强制打分，|偏好（|全部 |行为恢复比例 |−1\.175 )0\.90 \[#'], '-hi': [r'0\.90 \[0\.8[67], #\]']}, sign=False)
A('X3-pct', 'X3 行为保留的第一作者偏好（百分数）', csv(X3R, 'ratio', **X3RW), '同上', '552 篇', 0,
  [r'keeps ≈ #(?=% of the first-author)', r'保留约 #(?=% 的第一作者)', r'行为恢复（约 #(?=%）)'], sign=False, scale=100)
X4W = lambda ans, L: dict(split='test', answer=ans, pos='title', layer=L)
tri('X4-L8', 'X4 第一作者 D（L8，测试集）', CI3(X4O, 'D', 'lo', 'hi', **X4W('author', 8)), 'Stage 13 X4，D = self − partner；团队 CI', '测试集 582 对', 3,
    {'': [r'D = #(?= \[0\.035)', r'D = #(?=〔Stage 13 X4)', r'第一作者 L8 起可解码（#'], '-lo': [r'(?:D = |可解码（)\+0\.046 \[#', r'95% CI \[#(?=, 0\.059\])'], '-hi': [r'(?:D = |可解码（)\+0\.046 \[0\.035, #\]', r'CI \[0\.035, #\]']})
tri('X4-yr40', 'X4 年份 D（L40，测试集）', CI3(X4O, 'D', 'lo', 'hi', **X4W('year', 40)), '同上', '测试集 582 对', 3,
    {'': [r'year only from L40, #', r'年份要到 L40，#'], '-lo': [r'\+0\.013 \[#', r'同上，\[#(?=, 0\.018\])'], '-hi': [r'\+0\.013 \[0\.008, #\]', r'\[0\.008, #\]']})
RS = dict(measure='qwen', layer=8.0, role='surname_first')
tri('X4-rs', 'X4 L8 姓的第一个 token 上的 D', CI3(X4RS, 'mean', 'lo', 'hi', **RS), 'X4 按 token 角色', '1,178 篇', 3,
    {'': [r'surname \(#(?=\))', r'token 上（#'], '-lo': [r'\[#(?=, 0\.088\])'], '-hi': [r'\[0\.045, #\]']})
A('X4-rs-n', 'X4 角色拆分篇数', csv(X4RS, 'n', **RS), '计数', '—', 0, [r'role split, #(?= papers)', r'按 token 角色，#'], sign=False)
X1T = lambda L, col='R_authors': csv(X1O, col, split='test', layer=L)
A('X1-R24', 'X1 R(L24)（测试集）', X1T(24), 'Stage 13 X1，作者问法来源；均值比', '测试集 582 对', 2, [r'R ≈ #(?= \(L24\))', r'L24 约 #'], sign=False)
A('X1-R40', 'X1 R(L40)', X1T(40), '同上', '582 对', 2, [r'#(?= \(L40\), 0\.42)', r'L40 #(?=、L48 0\.42)'], sign=False)
A('X1-R48', 'X1 R(L48)', X1T(48), '同上', '582 对', 2, [r'#(?= \(L48\) whichever)', r'L48 #(?=〔Stage 13 X1)'], sign=False)
tri('X1-amy48', 'X1 作者 − 年份 L48（测试集）', {'': X1T(48, 'a_minus_year'), '-lo': X1T(48, 'a_minus_year_lo'), '-hi': X1T(48, 'a_minus_year_hi')}, '同上；团队 CI', '582 对', 3,
    {'': [r'except a small #', r'只有 L48 有 #'], '-lo': [r'same, \[#(?=, 0\.026\])', r'同上，\[#(?=, 0\.026\])'], '-hi': [r'\[0\.012, #\]']})
A('X1-n', 'X1 / X2 测试集对数', X1T(48, 'n'), '计数（X2 用同一测试集）', '—', 0, [r'test #(?= pairs)', r'测试集 #(?= 对)'], sign=False)
M3T = lambda col, agg: md(M3R, r'^### title_last', cols=[col], row={'layer': ['L16', 'L24', 'L28', 'L32', 'L36', 'L40']}, agg=agg)
A('M3-Tmin', 'M3 标题位置迁移比 T 在 L16–L40 的最小值（年份 / 引用数 / 领域）', md(M3R, r'^### title_last', cols=['year', 'log citations', 'field'],
                                                                   row={'layer': ['L16', 'L24', 'L28', 'L32', 'L36', 'L40']}, agg='min'),
  'Stage 13 M3，6 个有序问法对平均；团队聚类 95% CI；取最小', '9,108 篇', 2, [r'T ≥ #(?= at L16–L40)', r'都 ≥ #(?=〔Stage 13 M3)'], sign=False)
A('M3-dyr-max', 'M3 年份 T − T(L4)，L16–L40（离 0 最近）', M3T('year: T - T(L4)', 'max'), '同上', '9,108 篇', 2, [r'year T − T\(L4\) (?P<v>−0\.\d\d)(?!\d)(?= to)', r'T − T\(L4\) 为 (?P<v>−0\.\d\d)(?!\d)(?= 到)'])
A('M3-dyr-min', 'M3 年份 T − T(L4)，L16–L40（最负）', M3T('year: T - T(L4)', 'min'), '同上', '9,108 篇', 2, [r'T − T\(L4\) −0\.03 to (?P<v>−0\.\d\d)(?!\d)', r'为 −0\.03 到 (?P<v>−0\.\d\d)(?!\d)'])
XV = lambda col: csv(X2V, col)
A('X2-idRS', 'X2 S_id L40 搬动量', XV('id_R_S'), 'Stage 13 X2，测试集 582 对，R_S 均值比', '582 对', 3, [r'S_id at L40 moves #', r'在 L40 只搬动 #'])
A('X2-idrand', 'X2 S_id 随机子空间', XV('id_R_rand'), '同上', '582 对', 3, [r'\(random #(?=, full replacement)', r'随机子空间 #(?=，完整替换 \+0\.920)'])
A('X2-idfull', 'X2 L40 完整替换', XV('id_R_full'), '同上', '582 对', 3, [r'full replacement #', r'完整替换 #(?=；381)'])
A('X2-authRS', 'X2 S_auth L48 搬动量', XV('auth_R_S'), '同上', '582 对', 3, [r'S_auth at L48 moves #', r'在 L48 搬动 #', r'〔#(?= ÷ 0\.428)'])
A('X2-authrand', 'X2 S_auth 随机子空间', XV('auth_R_rand'), '同上', '582 对', 3, [r'\(random #(?=, full \+0\.428)', r'随机 #(?=，完整替换 \+0\.428)'])
A('X2-authfull', 'X2 L48 完整替换', XV('auth_R_full'), '同上', '582 对', 3, [r'(?<!R_)full #(?=\))', r'完整替换 #(?=〕)', r'0\.018 ÷ #'])
A('X2-half', 'X2 判据 0.5 × R_full（L40）', op('div', XV('id_R_full'), {'t': 'py', 'fn': lambda: 2.0, 'desc': '常数 2（判据 0.5 ×）', 'files': []}),
  '0.5 × id_R_full', '582 对', 3, [r'0\.5 × R_full #'], sign=False)
A('X2-idR', 'X2 R_id（L40，判据写法）', XV('id_R_S'), '同上', '582 对', 3, [r'R_id #(?= <)'], sign=False)
tri('X2-amid', 'X2 R_auth − R_id（L48 / L40）', CI3(X2V, 'auth_minus_id', 'auth_minus_id_lo', 'auth_minus_id_hi'), '同上；团队聚类 95% CI', '582 对', 3,
    {'': [r'R_auth − R_id #'], '-lo': [r'R_auth − R_id \+0\.014 \[#'], '-hi': [r'R_auth − R_id \+0\.014 \[\+0\.008, #\]']})
A('X2-r2max', 'X2 原作者子空间留出 R² 最大', csv(X2F, 'auth_r2', 'max'), '5 折团队留出 R²，L16–L48 取最大', '5,041 篇', 3, [r'held-out R² ≤ #(?=; first-author)', r'留出 R² ≤ #(?=〔S_auth)'], sign=False)
A('X2-r2min4', 'X2 原作者子空间留出 R² 最小（4 位）', csv(X2F, 'auth_r2', 'min'), '同上取最小', '5,041 篇', 4, [r'R² #(?=–0\.0033)'], sign=False)
A('X2-r2max4', 'X2 原作者子空间留出 R² 最大（4 位）', csv(X2F, 'auth_r2', 'max'), '同上取最大', '5,041 篇', 4, [r'R² 0\.0009–#'], sign=False)
A('X2-top1min', 'X2 第一作者 token 猜中率最小', csv(X2F, 'auth_top1', 'min'), 'fit_sanity.csv auth_top1，L16–L48', '5,041 篇', 3, [r'hit rate #(?=–)', r'猜中率 #(?=–)'], sign=False)
A('X2-top1max', 'X2 第一作者 token 猜中率最大', csv(X2F, 'auth_top1', 'max'), '同上', '5,041 篇', 3, [r'hit rate 0\.078–#', r'猜中率 0\.078–#'], sign=False)
A('X2-major', 'X2 常数基线（多数类）', csv(X2F, 'auth_top1_majority', 'max'), 'fit_sanity.csv auth_top1_majority', '5,041 篇', 3, [r'constant baseline #', r'常数基线 #'], sign=False)
A('X2-pct', 'X2 S_auth 搬动量占完整替换', op('div', XV('auth_R_S'), XV('auth_R_full')), 'auth_R_S ÷ auth_R_full', '582 对', 0, [r'about #(?=% of the full)', r'约 #(?=%〔0\.018)'], sign=False, scale=100)
A('X2-ntrain', 'X2 子空间训练论文数', csv(X2F, 'n_train', 'max'), '计数', '—', 0, [r'#(?= training papers)', r'#(?= 篇训练论文)'], sign=False)
A('X2-remove', 'X2 移除臂 L_S − L_rand（两种子空间中较大者）', XV('auth_remove_diff'), 'auth_remove_diff（测试集）', '582 对', 3,
  [r'random subspace \(#\)'], note='S_id 为 +0.0007、S_auth 为 +0.0009，均写作 +0.001')
# ---- name format 73 %, X1 cond (slide 55)
A('fmt-share', '以首字母开头的作者比例', op('div', csv(X1CR, 'n_contexts', **F63, first_role='initial_first'), csv(X1C, 'n_contexts', unit='token', group='all', **F63)),
  '24,739 ÷ 33,780 作者上下文（X1_cond_by_first_role.csv / X1_cond.csv，readout=final）', '33,780 位作者', 0,
  [r'#(?=% 的作者名以首字母开头)', r'（#(?=% 的名字以首字母开头)'], sign=False, scale=100)
GV = lambda col: csv(X1CR, col, **F63, first_role='given_first')
tri('X1c-giv', '完整名进前 10 时姓（后续 token）的差', {'': GV('diff'), '-lo': GV('lo'), '-hi': GV('hi')}, 'Stage 10 §6.7，进前 10 − 未进；论文聚类 bootstrap', '8,876 位作者', 3,
    {'': [r'最终输出 L63 #(?= \[0\.165)'], '-lo': [r'L63 \+0\.222 \[#'], '-hi': [r'\+0\.222 \[0\.165, #\]']})
A('X1c-giv2', '同上（两位写法）', GV('diff'), '同上', '8,876 位作者', 2, [r'姓在输出处高 #'])
LG = lambda col: csv(X1CR, col, readout='logit', layer=62, first_role='given_first')
tri('X1c-givlog', '完整名进前 10 时姓的差（logit L62）', {'': LG('diff'), '-lo': LG('lo'), '-hi': LG('hi')}, '同上，logit lens L62', '8,876 位作者', 3,
    {'': [r'logit lens L62 #(?= \[0\.253)'], '-lo': [r'L62 \+0\.322 \[#'], '-hi': [r'\+0\.322 \[0\.253, #\]']})
A('X1c-givlog2', '同上（两位写法）', LG('diff'), '同上', '8,876 位作者', 2, [r'logit lens 在 L62 高 #'])
A('X1c-n', '完整名开头作者数', GV('n_contexts'), '计数', '—', 0, [r'完整名开头的 #(?= 位作者)'], sign=False)
A('X1c-ntop', '完整名进前 10 的作者数', GV('n_top10'), '计数', '—', 0, [r'名进前 10：#(?= 位)'], sign=False)
# ---- citation (slide 26)
SPW = lambda g, m, col='spearman_rho': csv(SP, col, readout='final', layer=63, group=g, metric=m)
A('rho-all2', 'Spearman ρ 全部（两位写法）', SPW('all', 'spec'), 'Stage 10 X2', '9,108 篇', 2, [r'Spearman 相关：全部 #'], sign=False)
A('rho-t', 'Spearman ρ 目标组内', SPW('target', 'spec'), '同上', '4,621 篇', 3, [r'目标 4,621 篇 #(?=，对照 2,220 篇 0\.187)'], sign=False)
A('rho-t2', 'Spearman ρ 目标组内（两位）', SPW('target', 'spec'), '同上', '4,621 篇', 2, [r'目标组内 #'], sign=False)
A('rho-c', 'Spearman ρ 对照组内', SPW('control', 'spec'), '同上', '2,220 篇', 3, [r'对照 2,220 篇 #(?=；读出水平)'], sign=False)
A('rho-c2', 'Spearman ρ 对照组内（两位）', SPW('control', 'spec'), '同上', '2,220 篇', 2, [r'对照组内 #'], sign=False)
A('rho-lt', 'Spearman ρ 读出水平（目标）', SPW('target', 'level'), '同上，metric=level', '4,621 篇', 3, [r'读出水平只有 #'], sign=False)
A('rho-lc', 'Spearman ρ 读出水平（对照）', SPW('control', 'level'), '同上', '2,220 篇', 3, [r'读出水平只有 0\.181 / #'], sign=False)
A('bin-low2', '目标组 0-2 档（两位）', csv(AG, 'spec_mean_nlr_mean', group_tight='target', citation_bin='0-2', readout='final', layer=63), 'Stage 10 目标组引用档均值', '200 篇', 2,
  [r'从 0–2 档的 (?P<v>\+0\.\d\d)(?!\d)'], sign=False)
A('bin-high2', '目标组 4097+ 档（两位）', csv(AG, 'spec_mean_nlr_mean', group_tight='target', citation_bin='4097+', readout='final', layer=63), '同上', '84 篇', 2, [r'4097\+ 档的 (?P<v>\+0\.\d\d)(?!\d)'], sign=False)
A('bin-lown', '目标组 0-2 档篇数', csv(AG, 'n_papers', group_tight='target', citation_bin='0-2', readout='final', layer=63), '计数', '—', 0, [r'\+0\.347（#(?= 篇)'], sign=False)
A('bin-highn', '目标组 4097+ 档篇数', csv(AG, 'n_papers', group_tight='target', citation_bin='4097+', readout='final', layer=63), '计数', '—', 0, [r'0\.701\]（#(?= 篇)'], sign=False)

# ===================================================================================== Stage 7.3 / Stage 8 (slides 14, 16, 17, 30, 61)


def _s73m(col, mode='jlens_L56'):
    d = pd.read_csv(JL / S73N)
    d = d[(d.pool == 'combined') & (d['mode'] == mode)]
    assert len(d) == 50, len(d)
    return d[col].mean()


S73DESC = 'paper_null_distribution.csv 行 pool=combined, mode=%s（50 行）列 %s 取均值'
A('S73-true', 'Pilot50 L56 真标题胜率', py(lambda: _s73m('true_win'), S73DESC % ('jlens_L56', 'true_win'), [S73N]), '50 篇均值', '50 篇', 3, [r'Pooled L56: #', r'真标题 #(?= 对错误标题)'], sign=False)
A('S73-null', 'Pilot50 L56 20 个错误标题平均胜率', py(lambda: _s73m('null_mean'), S73DESC % ('jlens_L56', 'null_mean'), [S73N]), '50 篇均值', '50 篇', 3, [r'0\.616 vs #', r'对错误标题平均 #'], sign=False)
A('S73-true4', '同上真标题（4 位）', py(lambda: _s73m('true_win'), S73DESC % ('jlens_L56', 'true_win'), [S73N]), '50 篇均值', '50 篇', 4, [r'真标题 #(?=、20 个错误)'], sign=False)
A('S73-null4', '同上错误标题（4 位）', py(lambda: _s73m('null_mean'), S73DESC % ('jlens_L56', 'null_mean'), [S73N]), '50 篇均值', '50 篇', 4, [r'错误标题平均 #(?=；351)'], sign=False)
S73CI = lambda col: csv(S73R, col, item='7.3 L56 J-Lens title advantage pool=combined (B=20,000)')
tri('S73ci', 'Pilot50 L56 标题优势 95% CI（2026-10-30 重算，B = 20,000，pp）', {'': S73CI('recomputed_mean'), '-lo': S73CI('recomputed_ci_low'), '-hi': S73CI('recomputed_ci_high')},
    '论文 bootstrap，B = 20,000，种子 20261046', '50 篇', 1,
    {'-lo': [r'9\.3 (?:pp|个百分点) \[(?P<v>\+?\d+\.\d)(?![\d])'], '-hi': [r'9\.3 (?:pp|个百分点) \[\+?\d+\.\d, (?P<v>\+?\d+\.\d)(?![\d])']}, scale=100, sign=False)
tri('S73ci2', '同上（两位写法，pp）', {'': S73CI('recomputed_mean'), '-lo': S73CI('recomputed_ci_low'), '-hi': S73CI('recomputed_ci_high')}, '同上', '50 篇', 2,
    {'-lo': [r'9\.3 (?:pp|个百分点) \[(?P<v>\+?\d+\.\d\d)(?![\d])'], '-hi': [r'9\.3 (?:pp|个百分点) \[\+?\d+\.\d\d, (?P<v>\+?\d+\.\d\d)(?![\d])']}, scale=100)
tri('S73ci3', '同上（比例写法，3 位）', {'': S73CI('recomputed_mean'), '-lo': S73CI('recomputed_ci_low'), '-hi': S73CI('recomputed_ci_high')}, '同上', '50 篇', 3,
    {'-lo': [r'\+0\.0934 \[#'], '-hi': [r'\+0\.0934 \[0\.047, #\]']}, sign=False)
A('S73-4', 'Pilot50 L56 标题优势（4 位）', S73CI('recomputed_mean'), '同上', '50 篇', 4, [r'50 篇均值 #(?= \[0\.047)'])
A('S73-pos2', 'Pilot50 为正篇数', {'t': 'py', 'fn': lambda: (pd.read_csv(JL / S73N).query("pool=='combined' and mode=='jlens_L56'").title_advantage > 0).sum(),
                                  'desc': 'paper_null_distribution.csv 同上 title_advantage > 0 的行数', 'files': [S73N]}, '计数', '50 篇', 0,
  [r'#(?=/50 papers positive)', r'50 篇里 #(?= 篇为正)', r'#(?=/50 篇为正)'], sign=False)
LOO = lambda agg: csv(S73L, 'mean_without', agg)
A('S73-loo-min', 'Pilot50 逐篇留出后最小（pp，1 位）', LOO('min'), 'stage7_l56_loo.csv 列 mean_without 取最小', '50 次', 1, [r'Leave-one-out: #', r'在 #(?= 到 \+10\.0)'], scale=100)
A('S73-loo-max', 'Pilot50 逐篇留出后最大（pp，1 位）', LOO('max'), '同上取最大', '50 次', 1, [r'\+8\.6 to #', r'\+8\.6 到 #'], scale=100)
A('S73-loo-min2', '同上最小（2 位）', LOO('min'), '同上', '50 次', 2, [r'范围 #(?= 到 \+9\.99)'], scale=100)
A('S73-loo-max2', '同上最大（2 位）', LOO('max'), '同上', '50 次', 2, [r'\+8\.64 到 #'], scale=100)
VAN = py(lambda: _s73m('title_advantage', 'vanilla_L56'), S73DESC % ('vanilla_L56', 'title_advantage'), [S73N])
FIN = py(lambda: _s73m('title_advantage', 'final_L63'), S73DESC % ('final_L63', 'title_advantage'), [S73N])
A('S73-van', 'Pilot50 Vanilla L56 标题优势（pp）', VAN, '50 篇均值', '50 篇', 1, [r'Vanilla L56 #', r'Vanilla 在 L56 为 #'], scale=100)
A('S73-fin', 'Pilot50 最终输出标题优势（pp）', FIN, '50 篇均值', '50 篇', 1, [r'final output #', r'最终输出 #(?=〔Stage 7\.3)'], scale=100)
A('S73-van4', '同上 Vanilla（4 位）', VAN, '50 篇均值', '50 篇', 4, [r'50 篇均值 #(?= / \+0\.0716)'])
A('S73-fin4', '同上最终输出（4 位）', FIN, '50 篇均值', '50 篇', 4, [r'\+0\.1063 / #'])
IAB = lambda col: csv(S73I, col, lens='jlens', pool='combined')
tri('S73ab', 'Pilot50 匹配 A − B（7 层积分，合并池）', {'': IAB('mean_A_minus_B'), '-lo': IAB('ci_lower'), '-hi': IAB('ci_upper')}, '20 对；配对 bootstrap', '20 对', 3,
    {'': [r'integrated: #(?= \[)', r'积分只有 #'], '-lo': [r'integrated: \+0\.018 \[#', r'积分只有 \+0\.018 \[#'], '-hi': [r'(?:integrated: |积分只有 )\+0\.018 \[−0\.021, #\]']})
tri('S73ab4', '同上（4 位）', {'': IAB('mean_A_minus_B'), '-lo': IAB('ci_lower'), '-hi': IAB('ci_upper')}, '同上', '20 对', 4,
    {'': [r'20 对，#(?= \[−0\.0211)'], '-lo': [r'\+0\.0177 \[#'], '-hi': [r'\+0\.0177 \[−0\.0211, #\]']})
EP = lambda which, col: csv(S8E, col, endpoint=which)
R1E, R2E = 'RQ1 jlens 7-layer integrated title advantage', 'RQ2 jlens 7-layer integrated matched A-B'
tri('S8-e1', 'Stage 8 冻结主终点 RQ1（7 层积分，pp）', {'': EP(R1E, 'mean_pp'), '-lo': EP(R1E, 'ci_low_pp'), '-hi': EP(R1E, 'ci_high_pp')}, 's8_endpoints.csv（2026-10-30 重算，B = 10,000）', '200 篇', 2,
    {'': [r'复现 #(?= / \+2\.41)', r'主终点（7 层平均）是 #', r'200 篇，#(?= pp \[1\.50)'], '-lo': [r'\+2\.33 (?:pp )?\[#'], '-hi': [r'\+2\.33 (?:pp )?\[1\.50, #\]']})
tri('S8-e2', 'Stage 8 冻结主终点 RQ2 A − B（7 层积分，pp）', {'': EP(R2E, 'mean_pp'), '-lo': EP(R2E, 'ci_low_pp'), '-hi': EP(R2E, 'ci_high_pp')}, '同上', '100 对', 2,
    {'': [r'\+2\.33 / #(?= pp)', r'#(?= pp \[\+0\.91)'], '-lo': [r'\+2\.41 pp \[#'], '-hi': [r'\+2\.41 pp \[\+0\.91, #\]']})
PQ = lambda q, col: csv(S8, col, question=q)
tri('S8-RQ3', 'Stage 8D RQ3 低 − 高引用（pp）', {'': PQ('RQ3_low_minus_high', 'mean'), '-lo': PQ('RQ3_low_minus_high', 'ci_low'), '-hi': PQ('RQ3_low_minus_high', 'ci_high')}, '配对平衡；bootstrap', '25 + 25 对', 2,
    {'': [r'#(?= pp \[−3\.69)', r'低引用减高引用为 #'], '-lo': [r'\+2\.45 pp \[#'], '-hi': [r'\+2\.45 pp \[−3\.69, #\]']}, scale=100)
JV = lambda col: csv(S8V, col, mode='L56_JLens_minus_Vanilla')
tri('S8-JVci', 'Stage 8D J-Lens − Vanilla（pp）', {'': JV('mean'), '-lo': JV('ci_low'), '-hi': JV('ci_high')}, '论文 bootstrap', '200 篇', 2,
    {'': [r'Vanilla 为 #'], '-lo': [r'−1\.38 pp \[#'], '-hi': [r'−1\.38 pp \[−3\.48, #\]']}, scale=100)
BAND = lambda b, col: csv(S8B, col, scope='citation_band', mode='jlens_L56', band=b)
for b, pe, plo, phi, p2 in [('low', r'low #(?= \[)', r'low \+6\.8 \[#', r'low \+6\.8 \[2\.6, #\]', r'#(?= / \+4\.75)'),
                            ('mid', r'mid #', None, None, r'\+6\.83 / #'),
                            ('high', r'high #(?= \[)', r'high \+4\.4 \[#', r'high \+4\.4 \[−1\.1, #\]', r'\+4\.75 / #')]:
    tri('S8-band-' + b, 'Stage 8D 引用带 %s（pp，1 位）' % b, {'': BAND(b, 'mean'), '-lo': BAND(b, 'ci_low'), '-hi': BAND(b, 'ci_high')}, 'layer_and_band_summary.csv', '50 / 100 / 50 篇', 1,
        {'': [pe, r'%s档 #' % {'low': '低', 'mid': '中', 'high': '高'}[b]], '-lo': [plo] if plo else [], '-hi': [phi] if phi else []}, scale=100)
    A('S8-band2-' + b, 'Stage 8D 引用带 %s（pp，2 位）' % b, BAND(b, 'mean'), '同上', '50 / 100 / 50 篇', 2, [p2], scale=100)
A('S8-RQ1-1d', 'Stage 8D RQ1（1 位写法）', PQ('RQ1_L56_replication', 'mean'), '同 S8-RQ1', '200 篇', 1, [r'200 new papers #', r'#(?= pp new 200)', r'200 篇新论文上 #(?=〔)'], scale=100)
A('S8-RQ2-1d', 'Stage 8D RQ2（1 位写法）', PQ('RQ2_matched_A_minus_B', 'mean'), '同 S8-RQ2', '100 对', 1, [r'#(?= pp on 200 papers)', r'在 200 篇上是 #'], scale=100)
A('S8-drop10b', '去掉最大 10 对后 A − B（备注写法）', {'t': 'py', 'fn': lambda: __import__('claims_defs')._s8_drop10(), 'desc': '同 S8-drop10', 'files': ['351_stage8/stage8D/summary/matched_pair_differences.csv']},
  '事后诊断', '90 对', 2, [r'其余 90 对均值 #'], scale=100)
A('S73-pilot', 'Pilot50 L56 标题优势（备注“Pilot +9.3”）', S73CI('recomputed_mean'), '同 S73', '50 篇', 1, [r'Pilot #(?=〔)'], scale=100)
# ---- Stage 11 E1 in the keys-and-shelves slide (two-decimal / one-decimal forms)
A('E1-L48-2', 'E1 L48 恢复（两位写法）', csv(E1, 'recovery', group='all', layer=48), 'Stage 11 E1，均值比', '593 + 593 篇', 2, [r'Whole prompt: #(?= at L48)', r'整段提示替换在 L48 恢复 #'], sign=False)
A('E1-L52-1', 'E1 L52 恢复（一位写法）', csv(E1, 'recovery', group='all', layer=52), '同上', '593 + 593 篇', 1, [r'≈#(?= from L52)', r'L52 起约 #(?=〔Stage 11 E1)'], sign=False)
A('n1186', 'Stage 11 / 12 / 13 样本篇数（593 + 593）', csv(X6R, 'n_papers', group='all', false_title='false_0', layer=48), '计数', '—', 0,
  [r'(?P<v>1,186)(?= (?:papers|篇))'], sign=False)
A('n593', 'Stage 11 样本每组篇数', csv(X6R, 'n_papers', group='target', false_title='false_0', layer=48), '计数', '—', 0,
  [r'target (?P<v>593)(?![\d,])', r'control (?P<v>593)(?![\d,])', r'目标 (?P<v>593)(?![\d,])', r'对照 (?P<v>593)(?![\d,])'], sign=False)
# ---- addendum 9 (alltok; V0 = published rule) on slide 72 / 24
AP = lambda q, col: csv(J13 + 'summary_alltok/primary_L40.csv', col, quantity=q)
tri('AT-smi', '补充 9：L40 姓 − 首字母', {'': AP('surname_minus_initial', 'est'), '-lo': AP('surname_minus_initial', 'lo'), '-hi': AP('surname_minus_initial', 'hi')},
    '补充 9，真标题 − false_0，两项均值之差；团队 CI', '2,985 个论文×角色', 3,
    {'': [r'difference #(?= \[0\.011)', r'差为 #(?= \[0\.011)'], '-lo': [r'\+0\.028 \[#'], '-hi': [r'\+0\.028 \[0\.011, #\]']})
ATR = J13 + 'summary_alltok/alltok_role_layer.csv'
ATC = J13 + 'summary_alltok/alltok_controls.csv'
AR = lambda run, L, col='spec': csv(ATR, col, run=run, layer=L)
tri('AT-giv40', '补充 9：名的第一个 token L40', {'': AR('given_first', 40), '-lo': AR('given_first', 40, 'spec_lo'), '-hi': AR('given_first', 40, 'spec_hi')},
    '补充 9，真标题 − false_0，目标 + 对照，剔除标题复用；团队 CI', '1,706 篇', 3,
    {'': [r'L40 #(?=, L56 \+0\.163)', r'L40 #(?=〔1,706)'], '-lo': [r'1,706 篇，\[#'], '-hi': [r'1,706 篇，\[0\.108, #\]']})
tri('AT-giv56', '补充 9：名的第一个 token L56', {'': AR('given_first', 56), '-lo': AR('given_first', 56, 'spec_lo'), '-hi': AR('given_first', 56, 'spec_hi')}, '同上', '1,706 篇', 3,
    {'': [r'L56 #(?=〔\[0\.145)', r'L56 #(?=\u200b?\(1,706)'], '-lo': [r'〔\[#(?=, 0\.181\])'], '-hi': [r'\[0\.145, #\]']})
A('AT-givn', '补充 9：名的第一个 token 篇数', AR('given_first', 40, 'n_tc'), '计数', '—', 0, [r'\(#(?= papers; same\))', r'〔#(?= 篇，\[0\.108)'], sign=False)
A('AT-perm-ini', '补充 9：首字母置换对照（随机另一篇论文，L40）', csv(ATC, 'est', run='initial', layer=40, control='gold = random other paper'), '补充 9 第 7 节', '1,590 篇', 2,
  [r'≈ #(?= on initials)', r'在首字母上约为 #'])
A('AT-nmin', '补充 9：L40 目标 + 对照篇数（最少）', csv(ATR, 'n_tc', 'min', layer=40, run=['surname_first', 'initial', 'given_first', 'given_cont', 'surname_cont']), '计数', '—', 0,
  [r'#(?=–1,754 target)'], sign=False)
A('AT-nmax', '补充 9：L40 目标 + 对照篇数（最多）', csv(ATR, 'n_tc', 'max', layer=40, run=['surname_first', 'initial', 'given_first', 'given_cont', 'surname_cont']), '计数', '—', 0,
  [r'1,395–#(?= target)'], sign=False)
A('AT-sur-body', '补充 9：L40 姓的第一个 token（无区间写法）', AR('surname_first', 40), '补充 9', '1,395 篇', 3,
  [r'surname first token L40 #', r'L40 姓的第一个 token #(?=；减 5 个)'])


PRS = lambda col: csv(PRI, col, readout='final', layer=63, role='surname_first', group='tc_spec')
tri('PR-sur-spec', '姓的第一个 token：论文特有部分的目标−对照', {'': PRS('spec'), '-lo': PRS('spec_lo'), '-hi': PRS('spec_hi')}, 'Stage 12 名字先验拆解（CPU），最终输出 L63', '4,621 / 2,220', 3,
    {'': [r'论文特有 #(?= \[0\.393)'], '-lo': [r'论文特有 \+0\.423 \[#'], '-hi': [r'\+0\.423 \[0\.393, #\]']})
A('CA-na', 'C − A 的 C 篇数', csv(CA, 'n_a', **F63), '计数', '—', 0, [r'C #(?= \+ A 3,2)'], sign=False)
A('CA-nb', 'C − A 的 A 篇数', csv(CA, 'n_b', **F63), '计数', '—', 0, [r'C 4\d\d \+ A #'], sign=False)

# ===================================================================================== X4 recognition (all 1,178 pairs vs test-confirmed)
REC = lambda st: XA + 'x4_recognition__%s.csv' % st
RW = lambda L: dict(answer='author', pos='title', layer=L)
A('X4rec-first-min', 'X4 识别（target − control，第一作者，全部 1,178 对）L8–L40 最小', csv(REC('first'), 'target_minus_control', 'min', answer='author', pos='title', layer=[8, 16, 24, 32, 40]),
  '引用档内 target − control 的 D；全部 1,178 对（tune + test 合并，未在测试集确认）；团队 CI', '1,178 对', 2, [r'L8–L40 高 #(?= 到 \+0\.06)'],
  note='口径：全部 1,178 对；按预注册（tune 选层、test 确认），v42 测试集 L8 为 +0.023 [−0.001, +0.048]，未确认')
A('X4rec-first-max', '同上最大', csv(REC('first'), 'target_minus_control', 'max', answer='author', pos='title', layer=[8, 16, 24, 32, 40]), '同上', '1,178 对', 2,
  [r'L8–L40 高 \+0\.04 到 #'], note='同上')
tri('X4rec-all-L8', 'X4 识别（全部作者，全部 1,178 对）L8', CI3(REC('all'), 'target_minus_control', 'lo', 'hi', **RW(8)), '同上（全部作者层）', '1,178 对', 3,
    {'': [r'全部作者 L8 #'], '-lo': [r'L8 \+0\.031 \[#'], '-hi': [r'L8 \+0\.031 \[0\.017, #\]']}, note='同上')
tri('X4rec-all-L40', 'X4 识别（全部作者，全部 1,178 对）L40', CI3(REC('all'), 'target_minus_control', 'lo', 'hi', **RW(40)), '同上', '1,178 对', 3,
    {'': [r'到 L40 #'], '-lo': [r'L40 \+0\.052 \[#'], '-hi': [r'L40 \+0\.052 \[0\.038, #\]']}, note='同上')
VW = dict(split='test', answer='author', pos='title', layer=8)
tri('X4rec-v42', 'X4 识别：tune 选层（L8）后测试集确认值（第一作者）', CI3(V42, 'target_minus_control', 'lo_team', 'hi_team', **VW), 'Stage 13 V42：测试集，团队 CI', '测试集', 3,
    {'': [r'#(?= \[−0\.001, \+?0\.048\])'], '-lo': [r'\+0\.023 \[#(?=, \+?0\.048\])'], '-hi': [r'\+0\.023 \[−0\.001, #\]']})

# ===================================================================================== bounds (checked by claims_v5_post.py)


def _bmax(f, col, **w):
    return csv(f, col, 'max', **w)


BOUNDS = [
    # (id, where it is written (regex on the doc text), selector, operator, threshold, description)
    ('B-X7f-all<=0.05', r'均 ≤ 0\.05|all ≤ 0\.05', {'t': 'py', 'fn': lambda: max(json.loads((JL / X7FJ).read_text())['verdict']['mean5'][g]['S_L52'] for g in ('target', 'control', 'all')),
                                                   'desc': 'x7f_verdict.json mean5 target/control/all S_L52 取最大', 'files': [X7FJ]}, '<=', 0.05, 'X7 五个假标题平均 S(L52) 三组都 ≤ 0.05'),
    ('B-X6-spread<=0.02', r'相差不超过 0\.02|within 0\.02 of false_0', {'t': 'py', 'fn': _x6_spread, 'desc': 'x6_recovery.csv |false_k − false_0| 最大（L48、L52，三组）', 'files': [X6R]},
     '<=', 0.02, 'X6 各假标题与 false_0 相差不超过 0.02'),
    ('B-X6roles52>=0.96', r'all roles ≥ 0\.96|各角色都 ≥ 0\.96', csv(X6RO, 'R', 'min', group='all', false_title='average', layer=52, reportable=True), '>=', 0.955,
     'X6 L52 各可报告角色都 ≥ 0.96（按两位四舍五入比较）'),
    ('B-F2<=0', r'≤ 0 at L24–L56|L24–L56 的 target − control 都 ≤ 0', csv(S12 + 'F2_author_lens.csv', 'tc', 'max', position='name', layer=[24, 32, 40, 44, 48, 52, 56]), '<=', 0.0005,
     'F2 名字位置 L24–L56 target − control 都 ≤ 0（按三位四舍五入）'),
    ('B-X1amy<=0.02', r'within ±0\.02|在 ±0\.02 以内', csv(X1O, 'a_minus_year', 'max', split='test', layer=[4, 8, 16, 24, 32, 40]), '<=', 0.02,
     'X1 作者 − 年份 L4–L40 在 ±0.02 以内（最大值）'),
    ('B-X1amy>=-0.02', r'within ±0\.02|在 ±0\.02 以内', csv(X1O, 'a_minus_year', 'min', split='test', layer=[4, 8, 16, 24, 32, 40]), '>=', -0.02, '同上（最小值）'),
    ('B-M3colon<0.5', r'T < 0\.5', md(M3R, r'^### colon', cols=['year', 'log citations', 'field'], row={'layer': ['L16', 'L24', 'L28', 'L32', 'L36', 'L40']}, agg='max'), '<', 0.5,
     'M3 “:” 位置 T < 0.5（L16–L40 三个目标取最大）'),
    ('B-X2remove<=rand', r'costs no more than a random subspace', csv(X2V, 'auth_remove_diff'), '<=', 0.0015,
     'X2 移除臂不比随机子空间多（L_S − L_rand ≈ +0.001）'),
    ('B-X4rec-test', r'认得出的论文在 L8–L40 更高|L8–L40 高 \+0\.04 到 \+0\.06，区间都不含 0', csv(V42, 'lo_team', split='test', answer='author', pos='title', layer=8), '>', 0.0,
     'X4 识别在测试集确认（tune 选 L8；预注册规则）：测试集团队 CI 下限 > 0'),
]

# patterns that would otherwise double-count: E1 2-dec claim must not take the v4 'recovers 0.82' script text
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
