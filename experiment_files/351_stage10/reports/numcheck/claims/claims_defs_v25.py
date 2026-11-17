"""claims_defs v25 (2026-11-17 d): v24 (unchanged file) + the final 2026-11-17 numbers:
(1) D name chain: group B and group C G(1) (all tokens, true titles) written next to group A;
(2) bottleneck F, addendum 19 (locked 2026-11-17, confirmatory analysis of already-seen data, post hoc lock):
    threshold ratio rho = c50(recall) / c50(recognition) with team-bootstrap CI, log10 rho, sensitivity rho (recognition excl. uncertain),
    within-bin target - control WLS trend slope.
Sources: 391_groups/summary_a16_20261115/d_contrasts.csv; 391_groups/summary_exposure_prereg19/thresholds_ratio.csv, prereg19_results.json.
New ids 'A25-'.  Run with:  CLAIMS_DEFS=claims_defs_v25 bash claims_run.sh"""
from claims_defs_v24 import *          # noqa: F401,F403
from claims_defs_v24 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, jsn


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A25-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'
# ------------------------------------------------------------------ (1) D: groups B and C
DC = '391_groups/summary_a16_20261115/d_contrasts.csv'
CD = '补充 16 D：名字链条，全部 token，真标题，团队整群 bootstrap 2,000 次（seed 391）；'
for g, lz, le, n in [('B', r'B 组 G\(1\) ', r'[Gg]roup B G\(1\) ', 'B 600 篇'), ('C', r'C 组 ', r'group C ', 'C 227 篇')]:
    s = dict(group=g, fa_type='all', version='true', contrast='G1', score='all_tokens')
    if g == 'B':
        L = [lz, le, r'B 组 ']
    else:
        L = [r'(?<=；)C 组 ', r'(?<=; )group C ', r'(?<=、)C 组 ']
    A('d-%s' % g, 'D：%s 组 G(1)' % g, csv(DC, 'est', **s), CD, n, 3, [l + '#(?= \\[|（227)' for l in L], sign=True)
    A('d-%s-lo' % g, 'D：%s 组 G(1)（下限）' % g, csv(DC, 'lo', **s), CD, n, 3, [l + SN + r' \[#(?=, )' for l in L], sign=False)
    A('d-%s-hi' % g, 'D：%s 组 G(1)（上限）' % g, csv(DC, 'hi', **s), CD, n, 3, [l + SN + r' \[' + SN + r', #\]' for l in L], sign=False)

# ------------------------------------------------------------------ (2) bottleneck F, addendum 19
TR = '391_groups/summary_exposure_prereg19/thresholds_ratio.csv'
PJ = '391_groups/summary_exposure_prereg19/prereg19_results.json'
CF = '补充 19（2026-11-17 锁定，已看过数据的确认性分析，事后锁定）：两个逻辑回归在同一组 2,000 次团队抽样上重拟合，9,108 篇，7,247 个团队；'
RH = dict(quantity='rho_recall_over_recognition')
LR = [r'ρ = ', r'比值 ρ = ', r'精确值 ', r'exact ']
A('f19-rho', '瓶颈 F：ρ = c50(写出) / c50(认出)', csv(TR, 'est', **RH), CF, '9,108 篇', 0, [l + '#(?= \\[)' for l in LR], sign=False)
A('f19-rho-lo', '瓶颈 F：ρ（下限）', csv(TR, 'lo', **RH), CF, '9,108 篇', 0, [l + SN + r' \[#(?=, )' for l in LR] + [r'95% CI #(?=–[\d,]+ ?倍)'], sign=False)
A('f19-rho-hi', '瓶颈 F：ρ（上限）', csv(TR, 'hi', **RH), CF, '9,108 篇', 0, [l + SN + r' \[' + SN + r', #\]' for l in LR] + [r'95% CI [\d,]+–#(?= ?倍)'], sign=False)
A('f19-lrho', '瓶颈 F：log10 ρ', csv(TR, 'log10_1p_est', **RH), CF, '9,108 篇', 2, [r'log10 ρ #(?= \[)'], sign=False)
A('f19-lrho-lo', '瓶颈 F：log10 ρ（下限）', csv(TR, 'log10_1p_lo', **RH), CF, '9,108 篇', 2, [r'log10 ρ ' + SN + r' \[#(?=, )'], sign=False)
A('f19-lrho-hi', '瓶颈 F：log10 ρ（上限）', csv(TR, 'log10_1p_hi', **RH), CF, '9,108 篇', 2, [r'log10 ρ ' + SN + r' \[' + SN + r', #\]'], sign=False)
RS = dict(quantity='rho_recall_over_recognition_excl_uncertain')
A('f19-sens', '瓶颈 F：敏感性 ρ（认出去掉不确定）', csv(TR, 'est', **RS), CF + '敏感性，只作描述；', '7,046 篇', 0, [r'(?<!log10 )ρ #(?= \[)'], sign=False)
A('f19-sens-lo', '瓶颈 F：敏感性 ρ（下限）', csv(TR, 'lo', **RS), CF + '敏感性；', '7,046 篇', 0, [r'ρ 1,184 \[#(?=, )'], sign=False)
A('f19-sens-hi', '瓶颈 F：敏感性 ρ（上限）', csv(TR, 'hi', **RS), CF + '敏感性；', '7,046 篇', 0, [r'ρ 1,184 \[[\d,]+, #\]'], sign=False)
CS = '补充 19 次分析：档内 target − control（最终输出 L63，全部名字 token）对 log10(1 + 档中位引用数) 的 WLS 斜率，10 档；'
LT = [r'WLS 斜率 ', r'WLS slope ', r'(?<=随曝光增大（)斜率 ']
A('f19-slope', '瓶颈 F：档内趋势斜率', jsn(PJ, ['trend', 'slope']), CS, '10 档', 3, [l + '#(?= \\[)' for l in LT], sign=True)
A('f19-slope-lo', '瓶颈 F：档内趋势斜率（下限）', jsn(PJ, ['trend', 'lo']), CS, '10 档', 3, [l + SN + r' \[#(?=, )' for l in LT], sign=True)
A('f19-slope-hi', '瓶颈 F：档内趋势斜率（上限）', jsn(PJ, ['trend', 'hi']), CS, '10 档', 3, [l + SN + r' \[' + SN + r', #\]' for l in LT], sign=True)
