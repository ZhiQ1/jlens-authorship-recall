"""claims_defs v28 (2026-11-19 evening): v27 (unchanged file) + addendum 18b item 2 FIXED step-2 sensitivity
(381_stage13/summary_a18b_item2_step2_fix/item2_table.csv): largest loss (L48-51 name <- title) with CI, its share of S (3.5%).
v26 'A26-i2-share' (main run, 3.4%) loses its '≤ x% of S' pattern, which now carries the fixed-run 3.5%.
New ids 'A28-'.  Run with:  CLAIMS_DEFS=claims_defs_v28 bash claims_run.sh"""
from claims_defs_v27 import *          # noqa: F401,F403
from claims_defs_v27 import C, csv, MANUAL
from claims_defs_v5 import A as _A5

for c in C:
    if c['id'] == 'A26-i2-share':
        c['occ'] = [p for p in c['occ'] if not p.startswith('≤ #')]


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A28-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'
F = '381_stage13/summary_a18b_item2_step2_fix/item2_table.csv'
CF = '补充 18b 第 2 项步长 2 敏感性（修正窗口分配后），11 个重叠 4 层窗口，单边断开 S 损失，团队整群 bootstrap 2,000 次；'
W = dict(window='L48-51', edge='name<-title')
L = [r'最大损失 ', r'largest loss ', r'最大 ']
A('i2f-max', '18b-2 修正步长 2：最大损失（L48–51 名字←标题）', csv(F, 'loss', **W), CF, '600 篇子样本', 4, [l + '#(?= \\[)' for l in L])
A('i2f-max-lo', '同上（下限）', csv(F, 'lo', **W), CF, '600 篇子样本', 4, [l + SN + r' \[#(?=, )' for l in L], sign=False)
A('i2f-max-hi', '同上（上限）', csv(F, 'hi', **W), CF, '600 篇子样本', 4, [l + SN + r' \[' + SN + r', #\]' for l in L], sign=False)
A('i2f-share', '18b-2 修正步长 2：单边损失占 S（最大）', csv(F, 'share_of_S', 'max'), CF, '600 篇子样本', 1,
  [r'≤ S 的 #(?=%)', r'≤ #(?=% of S)', r'约为 S 的 #(?=%)', r'≈ #(?=% of S)'], sign=False, scale=100)
# guard: an older deck version wrote the main-run "≤ 3.4% of S" next to "robustness open" (main-run value); such text is not this claim
C[-1]['excl'] = r'robustness open'
