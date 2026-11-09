"""claims_defs v7 (2026-11-07 late): v6 (unchanged file) + after document round d (sync_20261107d_manifest.md):
 (1) the result numbers in the advisor scope (advisor page + deck slides 14,16,17,24,26,30,55,59,61,67-72,81 incl. notes) that v6 left
     unregistered (many are registered numbers in their edited wording); design constants are classified in NONRESULT, not registered;
 (2) the numbers behind the round-d rounding / definition fixes, the D14-1 (3-3 stop) statement, the Stage 7.1B progress share,
     the D13-1 proxy numbers (c2_followup_proxy.csv, aa_all) and the Vpd exclusion split 2,187 = 1,491 + 696;
 (3) DEF_STATUS: code rules that mark each static definition-issue row resolved / unresolved / held against the current text.
New ids start with 'A7-'. Values are read by code; numbers inside regexes are neighbouring text only.
Run with:  CLAIMS_DEFS=claims_defs_v7 bash claims_run.sh ; CLAIMS_DEFS=claims_defs_v7 python claims_v5_post.py <out> ; python claims_v7_post.py <out>"""
import json
import numpy as np
import pandas as pd
from claims_defs_v6 import *          # noqa: F401,F403
from claims_defs_v6 import C, csv, md, JL, py, MANUAL, FAR_IS_MISMATCH
from claims_defs_v5 import A as _A5, op, jsn

def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A7-' + cid; MANUAL[-1] = c['id']


def T(cid, stmt, sels, comp, n, dec, pats, **k):
    for part in ('', '-lo', '-hi'):
        if pats.get(part):
            A(cid + part, stmt + {'': '', '-lo': '（下限）', '-hi': '（上限）'}[part], sels[part], comp, n, dec, pats[part], **k)


def CI(f, est, lo, hi, **w):
    return {'': csv(f, est, **w), '-lo': csv(f, lo, **w), '-hi': csv(f, hi, **w)}


F63 = dict(readout='final', layer=63)
S73R = '351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv'
S73I = dict(item='7.3 L56 J-Lens title advantage pool=combined (B=20,000)')
S8 = '351_stage8/stage8D/summary/primary_questions.csv'
PRI = '371_stage12/summary_cpu/A_prior_decomposition.csv'
E1 = '361_stage11/summary/E1_recovery.csv'
E2 = '361_stage11/summary/E2_knockout.csv'
B = '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'
PDL = '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv'
PDN = '381_stage13/summary_b1_e4b5/perdonor_n_used_L40.csv'
ATR = '381_stage13/summary_alltok/alltok_role_layer.csv'
M2P = '381_stage13/summary_cpu_group/M2_probes.csv'
X3R = '381_stage13/summary_x3/x3_recovery.csv'
N2 = '371_stage12/summary/N2_prior_pure.csv'
P1 = '371_stage12/summary/P1_patch_pos.csv'

# ---------------------------------------------------------------- (1) registered quantities in their round-d wording
A('S73-4', 'Pilot50 L56 标题优势（4 位，B = 20,000 重算）', csv(S73R, 'recomputed_mean', **S73I), '论文 bootstrap B = 20,000', '50 篇', 4, [r'50 篇均值 #(?= \[0\.048)'])
A('S73-hi3', '同上 95% CI 上限（3 位）', csv(S73R, 'recomputed_ci_high', **S73I), '同上', '50 篇', 3, [r'\+0\.0934 \[0\.048, #\]'], sign=False)
T('S8RQ1ci', 'Stage 8D RQ1 95% CI（个百分点写法）', {'': csv(S8, 'mean', question='RQ1_L56_replication'), '-lo': csv(S8, 'ci_low', question='RQ1_L56_replication'),
                                                  '-hi': csv(S8, 'ci_high', question='RQ1_L56_replication')}, '论文 bootstrap', '200 篇', 2,
  {'-lo': [r'5\.18 个百分点 \[\+?#'], '-hi': [r'5\.18 个百分点 \[\+?2\.93, \+?#\]']}, scale=100, sign=False)
A('S8RQ2-b', 'Stage 8D RQ2（备注写法）', csv(S8, 'mean', question='RQ2_matched_A_minus_B'), '100 对配对差均值', '100 对', 2, [r'A−B 为 #(?= \[\+0\.32)', r'均值 #(?= pp，按 A−B)'], scale=100)
A('S8band-hi', 'Stage 8D 低引用带 95% CI 上限（pp）', csv('351_stage8/stage8D/summary/layer_and_band_summary.csv', 'ci_high', scope='citation_band', mode='jlens_L56', band='low'),
  'layer_and_band_summary.csv', '50 篇', 1, [r'low \+6\.8 \[2\.5, #\]'], scale=100, sign=False)
A('E4b-L40wei', 'E4b 训练折标准化 L40（“L40 为”写法）', md('381_stage13/reports/e4b_trainstd_compare.md', r'all papers', col='new', row={'layer': 'L40'}),
  '团队分折 + 剔除标题复用 + 训练折内标准化', '1,395 篇', 3, [r'L40 为 #(?= \[0\.047)'])
XB = dict(readout='final', layer=63, group='target', citation_bin='4097+')
T('bin4097', '目标组 4097+ 档标题特异信号', CI('351_stage10/summary_extra/X2_by_bin.csv', 'spec', 'spec_lo', 'spec_hi', **XB), 'Stage 10 X2_by_bin，最终输出 L63；论文 bootstrap', '84 篇', 3,
  {'-lo': [r'\+0\.644 \[#'], '-hi': [r'\+0\.644 \[0\.591, #\]']}, sign=False)
A('rho-full', 'Spearman ρ 全部（“全部 9,108 篇”写法）', csv('351_stage10/summary_extra/X2_spearman.csv', 'spearman_rho', group='all', metric='spec', **F63), 'Stage 10 X2', '9,108 篇', 3,
  [r'9,108 篇 #(?= \[0\.433)'], sign=False)
PRS = lambda col, role='all_tokens', g='tc_prior': csv(PRI, col, readout='final', layer=63, role=role, group=g)
A('PR-share2', '名字先验占比（删标题条件，两位写法）', op('div', PRS('prior'), PRS('true', g='tc_true')), '先验 ÷ 真标题差', '4,621 / 2,220', 2,
  [r'only ~#(?= of the gap)', r'差的约 #(?=（约三分之一）)', r'先验 #(?= 定义不同)', r'prior of §6\.12: #'], sign=False)
T('PR-prior', '名字先验的目标−对照（全部名字 token）', {'': PRS('prior'), '-lo': PRS('prior_lo'), '-hi': PRS('prior_hi')}, 'Stage 12 CPU 拆解，最终输出 L63', '4,621 / 2,220', 3,
  {'': [r'先验 #(?= \[0\.070)'], '-lo': [r'先验 \+0\.087 \[#'], '-hi': [r'\+0\.087 \[0\.070, #\]']})
T('PR-sur', '姓的第一个 token 上名字先验的目标−对照', {'': PRS('prior', 'surname_first'), '-lo': PRS('prior_lo', 'surname_first'), '-hi': PRS('prior_hi', 'surname_first')},
  '同上', '4,621 / 2,220', 3, {'-lo': [r'先验 目标−对照 \+0\.022 \[#'], '-hi': [r'\+0\.022 \[−0\.019, #\]']})
BJ = dict(readout=['jlens_public', 'jlens_self100', 'jlens_fitA'], layer=48)
A('L48-jmax', 'L48 三种 J-lens 目标−对照（离 0 最近）', csv(B, 'spec_mean_nlr_diff', 'max', **BJ), '三种 J-lens 取最大', '3,734 / 2,182', 3, [r'Jacobian lens L48 #(?= 到 −0\.05)'])
A('L48-jmin', 'L48 三种 J-lens 目标−对照（最负）', csv(B, 'spec_mean_nlr_diff', 'min', **BJ), '三种 J-lens 取最小', '3,734 / 2,182', 3, [r'Jacobian lens L48 −0\.037 到 #'])
T('E1-L52', 'E1 L52 恢复比例（全部）', CI(E1, 'recovery', 'rec_lo', 'rec_hi', group='all', layer=52), 'Stage 11 E1，均值比', '593 + 593 篇', 3,
  {'': [r'L52 #(?= \[0\.989)'], '-lo': [r'L52 0\.996 \[#'], '-hi': [r'0\.996 \[0\.989, #\]']}, sign=False)
A('E2-L52', 'E2 从 L52 起阻断的损失比例', csv(E2, 'loss_fraction', group='all', start_layer=52), 'Stage 11 E2', '1,186 篇', 3, [r'1,186 篇，L52 #(?= \[0\.001)'])
A('P1n-lo', 'P1 只换名字位置 L52 下限', csv(P1, 'lo', layer=52, item='names', group='all'), 'Stage 12 P1', '1,186 篇', 3, [r'0\.847 \[#'], sign=False)
A('N2-pure-b', 'N2 纯名字 target − control（备注算式）', csv(N2, 'pure', group='tc_pure'), 'Stage 12 N2', '4,621 / 2,220', 3, [r'〔#(?= ÷ 0\.247)'], sign=False)
A('N2-true-b', 'N2 真标题 target − control（备注算式）', csv(N2, 'true', group='tc_true'), 'Stage 12 N2', '4,621 / 2,220', 3, [r'0\.047 ÷ #'], sign=False)
X3W = dict(set='primary', subset='all', split='test', false='lexical_neighbour_D', group='all')
A('X3-beh', 'X3 行为恢复比（测试集）', csv(X3R, 'ratio', **X3W), 'Stage 13 X3', '552 篇', 2, [r'same, #(?= \[0\.86)', r'教师强制打分，#(?= \[0\.86)', r'#(?= \[0\.86, 0\.94\])'], sign=False)
A('X3-beh-lo', 'X3 行为恢复比下限（修正后 0.86）', csv(X3R, 'lo', **X3W), '同上', '552 篇', 2, [r'(?:same, |教师强制打分，|偏好（|全部 |行为恢复比例 |−1\.175 )0\.90 \[#'], sign=False)
T('AT-ini', '补充 9：首字母 L40', CI(ATR, 'spec', 'spec_lo', 'spec_hi', run='initial', layer=40), '补充 9，真标题 − false_0；团队 CI', '1,590 篇', 3,
  {'-lo': [r'\+0\.044 \[#'], '-hi': [r'\+0\.044 \[0\.030, #\]']})
A('B-ini', 'Vpd 首字母 L40 target − control', csv(PDL, 'tc', run='initial', layer=40, version='Vpd'), '逐个假标题排除（Vpd）', '4,812 篇', 3, [r'initial L40 #(?= \[−0\.002)'])
A('AT-sur', '补充 9（V0）：L40 姓的第一个 token', csv(ATR, 'spec', run='surname_first', layer=40), '补充 9，真标题 − false_0', '1,395 篇', 3,
  [r'姓首 token 为 #', r'L40 姓的第一个 token #(?=；逐个)'])
A('Vpd-first', 'Vpd：L40 第一个 token（e4b_parity）', csv(PDL, 'spec', run='e4b_parity', layer=40, version='Vpd'), 'Vpd，4,654 篇', '4,654 篇', 3, [r'第一个 token #(?=；原 E4b)'])
A('V0-first', '原 E4b（V0，1,395 篇）L40', csv(PDL, 'spec', run='e4b_parity', layer=40, version='V0'), 'V0：真标题 − false_0', '1,395 篇', 3, [r'原 E4b（1,395 篇）#'])
A('Vpd-mean', 'Vpd：保留论文平均可用假标题数', csv(PDN, 'mean_used', run='surname_first'), 'perdonor_n_used_L40.csv mean_used', '4,654 篇', 1,
  [r'~#(?= false titles each)', r'约 #(?= 个可用假标题)'], sign=False)
A('Vpd-sur', 'Vpd：L40 姓首 token（新写法）', csv(PDL, 'spec', run='surname_first', layer=40, version='Vpd'), 'Vpd，4,654 篇', '4,654 篇', 3, [r'可用假标题）#'])
M2F = lambda agg: csv(M2P, 'value', agg, condition='true', position='title', target='field')
A('M2-fmin', 'M2 领域准确率 L16–L60 最小', M2F('min'), 'Stage 13 M2，团队分折', '9,108 篇', 2, [r'领域准确率约 #(?=–)'], sign=False)
A('M2-fmax', 'M2 领域准确率 L16–L60 最大', M2F('max'), '同上', '9,108 篇', 2, [r'领域准确率约 0\.70–#'], sign=False)

# ---------------------------------------------------------------- (2a) D14-1: 3-3 stopped (b3_33_v2 / b3_33_option2 / summary_b3_71b)
C1S = '381_stage13/b3_33_v2/v2_C1_summary.json'
MAIN = lambda k: jsn(C1S, ['main_final63', 0, k])
A('D14-chg', '3-3：输出层 target−control（eff_all_rr）快路径 − 旧逐前缀', MAIN('change'), 'v2_C1_summary.json main_final63[0]（final L63, eff_all_rr）', '7 篇', 4, [r'差值之差 #'])
A('D14-wlo', '同上 Welch 95% CI 下限', MAIN('change_welch_lo'), '按论文 Welch', '7 篇', 4, [r'Welch 95% CI \[(?P<v>−0\.\d{4})(?!\d)'])
A('D14-whi', '同上 Welch 95% CI 上限', MAIN('change_welch_hi'), '按论文 Welch', '7 篇', 4, [r'Welch 95% CI \[−0\.0207, #\]'])
A('D14-wlo3', '同上 Welch 下限（3 位）', MAIN('change_welch_lo'), '按论文 Welch', '7 篇', 3, [r'Welch 95% CI \[(?P<v>−0\.\d{3})(?!\d)'])
A('D14-whi3', '同上 Welch 上限（3 位）', MAIN('change_welch_hi'), '按论文 Welch', '7 篇', 3, [r'Welch 95% CI \[−0\.\d{3}, #\]'])
A('D14-blo', '同上论文 bootstrap 下限', MAIN('change_boot_lo'), '论文级 bootstrap', '7 篇', 4, [r'bootstrap \[#(?=, \+0\.0181)'])
A('D14-bhi', '同上论文 bootstrap 上限', MAIN('change_boot_hi'), '论文级 bootstrap', '7 篇', 4, [r'bootstrap \[−0\.0005, #\]'])
CCS = '381_stage13/b3_33_option2/G_cross_class_share.csv'
A('D14-xt', '3-3：长度跨档比例 target', csv(CCS, 'cross_share', tight='target'), 'G_cross_class_share.csv', '4 篇', 0, [r'target #(?=%、control)'], sign=False, scale=100)
A('D14-xc', '3-3：长度跨档比例 control', csv(CCS, 'cross_share', tight='control'), '同上', '3 篇', 0, [r'control #(?=%。Stage 10)'], sign=False, scale=100)
A('D14-tol', '3-3：0.25 容差一致性通过率（全部 23,280 个分数）', csv('381_stage13/b3_33_option2/T_tolerance_pass_rates.csv', 'pre_025_lp', scope='ALL'), 'T_tolerance_pass_rates.csv scope=ALL 列 pre_025_lp', '23,280 个分数', 2,
  [r'919 行）通过率 #(?=%)'], sign=False, scale=100)
GATE = '381_stage13/summary_b3_71b/gate.json'
A('D14-rank', '3-3：原判据名次完全一致比例', jsn(GATE, ['checks', 0, 'value']), 'gate.json checks[0]（1,166 个旧上下文，23,280 个分数）', '23,280 个分数', 1, [r'未通过（#(?=%)'], sign=False, scale=100)
A('D14-np', '3-3：同时有新旧结果的论文数', py(lambda: len(json.loads((JL / GATE).read_text())['papers']), 'gate.json papers 列表长度', [GATE]), '计数', '—', 0,
  [r'只有 #(?= 篇论文同时有)'], sign=False)
# ---- Stage 7.1B progress
T71 = '351_stage7_1B_terminal/'
N71 = py(lambda: len(list((JL / T71 / 'raw').glob('*.json'))), '351_stage7_1B_terminal/raw/*.json 个数（已完成的上下文）', [T71 + 'raw'])
TOT = jsn(T71 + 'plan.json', ['n_tasks'])
A('71B-done', 'Stage 7.1B 已完成上下文数', N71, '计数', '—', 0, [r'只完成 #(?= / 15,519)', r'停在 #(?= / 15,519)'], sign=False)
A('71B-tot', 'Stage 7.1B 计划上下文数', TOT, 'plan.json n_tasks', '—', 0, [r'1,166 / #'], sign=False)
A('71B-pct', 'Stage 7.1B 完成比例', op('div', N71, TOT), '已完成 ÷ n_tasks', '—', 1, [r'个上下文（#(?=%)'], sign=False, scale=100)
# ---------------------------------------------------------------- (2b) D13-1 proxy (c2_followup_proxy.csv, aa_all)
PX = '381_stage13/c13_C2_followup/c2_followup_proxy.csv'
PXW = lambda ep: dict(version='aa_all', endpoint=ep)
COMPX = '补充 13 C-2 跟进：全部作者 CPU 代理（public J-lens 名次，Stage 10 的 5 个假标题），RQ1 团队 bootstrap，RQ2 配对 bootstrap'
T('D13-L56-RQ2', 'D13-1 代理 L56 RQ2', CI(PX, 'rq2', 'rq2_lo', 'rq2_hi', **PXW('L56')), COMPX, '100 对', 3,
  {'': [r'RQ2 #(?= \[−0\.032)', r'（#(?= \[−0\.032, \+0\.163\]，区间含 0)'], '-lo': [r'\+0\.064 \[#'], '-hi': [r'\+0\.064 \[−0\.032, #\]']})
T('D13-z-RQ2', 'D13-1 代理 7 层积分（L16 = 0）RQ2', CI(PX, 'rq2', 'rq2_lo', 'rq2_hi', **PXW('int7_L16zero')), COMPX, '100 对', 3,
  {'': [r'RQ2 (?:为 )?#(?= \[\+0\.007)'], '-lo': [r'\+0\.046 \[#'], '-hi': [r'\+0\.046 \[\+0\.007, #\]']})
T('D13-e-RQ2', 'D13-1 代理 7 层积分（L16 = L24）RQ2', CI(PX, 'rq2', 'rq2_lo', 'rq2_hi', **PXW('int7_L16eqL24')), COMPX, '100 对', 3,
  {'': [r'(?:或|/) #(?= \[\+0\.005)'], '-lo': [r'\+0\.049 \[#(?=, \+0\.094)'], '-hi': [r'\+0\.049 \[\+0\.005, #\]']},
  note='下限源值 0.005497，三位四舍五入为 +0.005（for_user 文本写 +0.006）')
T('D13-z-RQ1', 'D13-1 代理 7 层积分（L16 = 0）RQ1', CI(PX, 'rq1', 'rq1_team_lo', 'rq1_team_hi', **PXW('int7_L16zero')), COMPX, '200 篇', 3,
  {'': [r'RQ1 (?:为 )?#(?= \[\+0\.093)'], '-lo': [r'\+0\.111 \[#'], '-hi': [r'\+0\.111 \[\+0\.093, #\]']})
T('D13-e-RQ1', 'D13-1 代理 7 层积分（L16 = L24）RQ1', CI(PX, 'rq1', 'rq1_team_lo', 'rq1_team_hi', **PXW('int7_L16eqL24')), COMPX, '200 篇', 3,
  {'': [r'(?:或|/) #(?= \[\+0\.095)'], '-lo': [r'\+0\.117 \[#'], '-hi': [r'\+0\.117 \[\+0\.095, #\]']})
T('D13-6-RQ2', 'D13-1 代理 6 层 int6 RQ2', CI(PX, 'rq2', 'rq2_lo', 'rq2_hi', **PXW('int6')), COMPX, '100 对', 3,
  {'': [r'RQ2 (?:为 )?#(?= \[\+?0\.008)'], '-lo': [r'RQ2 (?:为 )?\+0\.054 \[\+?#'], '-hi': [r'RQ2 (?:为 )?\+0\.054 \[\+?0\.008, \+?#\]']})
T('D13-6-RQ1', 'D13-1 代理 6 层 int6 RQ1', CI(PX, 'rq1', 'rq1_team_lo', 'rq1_team_hi', **PXW('int6')), COMPX, '200 篇', 3,
  {'': [r'RQ1 #(?= \[0\.109)'], '-lo': [r'RQ1 \+0\.130 \[#'], '-hi': [r'RQ1 \+0\.130 \[0\.109, #\]']})
# ---------------------------------------------------------------- (2c) Vpd exclusion split 2,187 = 1,491 + 696
META = '351_stage10/cohort/papers.parquet'
PP40 = '381_stage13/summary_b1_e4b5/probe/perpaper_surname_first_L40.parquet'


def _nzero(groups):
    d = pd.read_parquet(JL / PP40)
    g = pd.read_parquet(JL / META, columns=['paper_id', 'group_tight']).set_index('paper_id').group_tight
    d['g'] = d.paper_id.map(g)
    use = np.stack([~d['dropped_%d' % k].to_numpy(bool) for k in range(5)], 1).sum(1)
    return int(((use == 0) & d.g.isin(groups)).sum())


DZ = '同 stage13_b1_e4b5_perdonor.py perdonor()：可用假标题数 = 5 − dropped_k 之和，取 0 的论文；group_tight 来自 cohort/papers.parquet'
A('Vpd-z-all', 'Vpd：一个可用假标题都没有的目标 + 对照论文', py(lambda: _nzero(['target', 'control']), DZ, [PP40, META]), '计数', '6,841 篇中', 0,
  [r'另 #(?= 篇一个可用)', r'(?P<v>2,187)(?= (?:篇|papers))'], sign=False)
A('Vpd-z-t', '同上 target', py(lambda: _nzero(['target']), DZ, [PP40, META]), '计数', '4,621 篇中', 0, [r'target #(?= / 4,621)', r'(?P<v>1,491)(?![\d,])'], sign=False)
A('Vpd-z-c', '同上 control', py(lambda: _nzero(['control']), DZ, [PP40, META]), '计数', '2,220 篇中', 0, [r'control #(?= / 2,220)', r'(?<![\d,])(?P<v>696)(?= ?(?:/|篇|papers))'], sign=False)

# ---------------------------------------------------------------- design constants in scope (classified, not registered)
NONRESULT = [   # (regex on the number, regex on its +-40-char context, label)
    (r'^95%$', r'CI|bootstrap|置信|聚类|团队', 'CI 置信水平（设计常数）'),
    (r'^0\.05$', r'≤|界线|判据|threshold', 'X7 预注册阈值 0.05（设计常数；BOUNDS 检查 S(L52) ≤ 0.05）'),
    (r'^0\.5$', r'<|×|判据', '判据阈值 0.5（设计常数）'),
    (r'^0\.02$', r'±|不超过|within|最多差|相差', '等效 / 差异界 0.02（设计常数；BOUNDS 检查）'),
    (r'^0\.96$', r'≥', '下界 0.96（BOUNDS 检查）'),
    (r'^0\.25$', r'随机|chance', '随机水平 1/4（4 个选项，设计常数）'),
    (r'^7\.[1-4]$', r'Stage|、|\(|；|阶段', 'Stage 编号'),
    (r'^80%$', r'≈80% at L48', '引用旧说法“≈80% at L48”（引号内的旧写法；源 X6 0.821）'),
]
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
