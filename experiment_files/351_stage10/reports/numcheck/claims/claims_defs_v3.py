"""claims_defs v3 (2026-11-07 ~02:50): v2 (unchanged) + claims for the numbers written by sync_20261107/apply_20261107c.py
(user decisions D, B, F). Run with:  CLAIMS_DEFS=claims_defs_v3 bash claims_run.sh"""
from claims_defs_v2 import *          # noqa: F401,F403
from claims_defs_v2 import C, add, csv
JL13 = '381_stage13/'
PD = JL13 + 'summary_b1_e4b5/perdonor_by_run_layer.csv'
XV = JL13 + 'summary_b1_xall/x2_verdict_new__all.csv'
FS = JL13 + 'summary_b1_xall/fit_authall_sanity.csv'
STAGE11 = '361_stage11/summary/E1_recovery.csv'
COMP_B = '真标题 − 供体不在训练折的假标题平均（Vpd，逐个假标题排除）；引用档内 target − control；团队聚类 bootstrap 2,000 次 95% CI'
# B: surname / initial target - control at L40, given-name first token at L16
for k, col in [('', 'tc'), ('-lo', 'tc_lo'), ('-hi', 'tc_hi')]:
    add('B-sur-L40' + k, '姓的第一个 token，target − control，L40（5 个假标题，逐个排除）' + k, csv(PD, col, run='surname_first', layer=40, version='Vpd'), COMP_B, '目标 + 对照 4,654 篇', 3,
        {'': [r'(?:姓 |surname )?L40 #(?= \[0\.013, 0\.048\])'], '-lo': [r'L40 \+0\.030 \[#(?=, 0\.048\])'], '-hi': [r'L40 \+0\.030 \[0\.013, #\]']}[k], sign=(k == ''))
    add('B-ini-L40' + k, '首字母，target − control，L40（5 个假标题，逐个排除）' + k, csv(PD, col, run='initial', layer=40, version='Vpd'), COMP_B, '4,812 篇', 3,
        {'': [r'(?:首字母不显著（|initial (?:is )?not significant \()L40 #'], '-lo': [r'L40 \+0\.014 \[#'], '-hi': [r'L40 \+0\.014 \[−0\.002, #\]']}[k])
add('B-giv-L16', '名的第一个 token，target − control，L16（从 L16 起为正的第一层）', csv(PD, 'tc', run='given_first', layer=16, version='Vpd'), COMP_B, '3,046 篇', 3,
    [r'given_first L16 #(?= \[)'])
# F3: all-author X2 refit
add('F3-X2all', 'X2 全部作者重拟合的作者子空间搬动量（测试集，L48，R_auth）', csv(XV, 'auth_R_S'), '测试集 582 对，均值比 R_S', '582 对', 3,
    [r'搬动 #(?=，约为完整替换的 7%)', r'moves #(?=, about 7% of full patching)'], sign=False)
add('F3-X2full', 'X2 完整替换 R_full（L48，测试集）', csv(XV, 'auth_R_full'), '同上', '582 对', 3, [r'(?:完整替换 R_full|；R_full) #'], sign=False)
add('F2-R2max', '全部作者 S_auth 留出 R² 最大值（L16–L48）', csv(FS, 'authall_r2', 'max'), '5 折团队留出 R²，5,041 篇训练论文', '5,041 篇', 3,
    [r'held-out R² ≤ #(?=[;)])', r'留出 R² ≤ #(?=；用全部作者)'], sign=False)
# D: 99.6% from L52 (E1 recovery, as a percentage)
add('D-E1-L52-pct', 'E1 L52 恢复比例（百分数写法）', csv(STAGE11, 'recovery', group='all', layer=52), 'Stage 11 E1 替换，最终输出恢复比例', '593 + 593 篇', 1,
    [r'#(?=% from L52)'], scale=100, sign=False)
for c in C:
    c.setdefault('excl', None); c.setdefault('alt', [])
