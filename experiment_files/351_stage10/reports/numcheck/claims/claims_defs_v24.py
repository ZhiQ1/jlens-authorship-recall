"""claims_defs v24 (2026-11-17): v23 (unchanged file) + the numbers of the user-decided wording (2026-11-17):
(1) D interpretation "co-author network association, not paper-specific memory": title-deleted G_A(1) +0.223;
(2) B: Holm-adjusted p of F1 / F2 / F3 DiD written next to the Holm CIs;
(3) bottleneck C (fabricated names, exploratory) and bottleneck F (exposure thresholds, exploratory) in report #pd-sayable.
Sources: 391_groups/summary_a16_20261115/d_contrasts.csv, holm.csv; 391_groups/summary_fabricated_20261114/class_shares_by_group.csv,
chance_baselines.csv, target_minus_control.csv; 391_groups/summary_exposure_20261114/logistic_thresholds.csv, exposure_by_bin.csv.
New ids 'A24-'.  Run with:  CLAIMS_DEFS=claims_defs_v24 bash claims_run.sh"""
from claims_defs_v23 import *          # noqa: F401,F403
from claims_defs_v23 import C, csv, MANUAL
from claims_defs_v5 import A as _A5, op


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A24-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.]+'
# ------------------------------------------------------------------ (1) D: title deleted
DC = '391_groups/summary_a16_20261115/d_contrasts.csv'
CD = '补充 16 D：名字链条，全部 token，团队整群 bootstrap 2,000 次（seed 391）；删去标题版本；'
DEL = dict(group='A', fa_type='all', version='delete', contrast='G1', score='all_tokens')
L = [r'删去标题时效应反而更大（', r'with the title deleted it is larger \(', r'with the title deleted ']
A('d-del', 'D：删去标题时的 G_A(1)', csv(DC, 'est', **DEL), CD, 'A 600 篇', 3, [l + '#(?= \\[)' for l in L], sign=True)
A('d-del-lo', 'D：删去标题时的 G_A(1)（下限）', csv(DC, 'lo', **DEL), CD, 'A 600 篇', 3, [l + SN + r' \[#' for l in L], sign=False)
A('d-del-hi', 'D：删去标题时的 G_A(1)（上限）', csv(DC, 'hi', **DEL), CD, 'A 600 篇', 3, [l + SN + r' \[' + SN + r', #\]' for l in L], sign=False)

# ------------------------------------------------------------------ (2) B: Holm p for F1 / F2 / F3
HO = '391_groups/summary_a16_20261115/holm.csv'
CB = '补充 16 B：输出格式，团队整群 bootstrap 2,000 次（seed 391），Holm 校正（5 个检验）；'
for t, zh, en in [('B_F2', r'F2（只写姓）DiD ', r'F2 \(surnames only\) DiD '),
                  ('B_F1', r'F1（姓在前的列表）', r'F1 \(surname-first list\) '),
                  ('B_F3', r'F3（只写第一作者的姓）', r"F3 \(first author's surname only\) ")]:
    A('b-' + t[2:].lower() + '-p', 'B %s：DiD 的 Holm 校正后 p' % t[2:], csv(HO, 'p_holm', test=t, quantity='DiD_A-B'), CB, '—', 3,
      [zh + r'[^；]*?Holm 校正后 p #', en + r'[^;]*?Holm p #'], sign=False)

# ------------------------------------------------------------------ (3a) bottleneck C: fabricated names (exploratory)
FB = '391_groups/summary_fabricated_20261114/'
CC = '编造名分类（探索性，事后），姓 + 首字母键，全部 8,872 篇 / 40,219 个名字，团队整群 bootstrap 2,000 次；'
SH = dict(keys='si', group='all')
NID = [r'25\.4% / #(?=% \[)', r'（#(?=% \[[\d.]+, [\d.]+\] 不在数据中)']
A('c-nid', '瓶颈 C：不在数据中的编造名比例', csv(FB + 'class_shares_by_group.csv', 'share', cls='not_in_data', **SH), CC, '8,872 篇', 1, NID, sign=False, scale=100)
A('c-nid-lo', '瓶颈 C：不在数据中（下限）', csv(FB + 'class_shares_by_group.csv', 'lo', cls='not_in_data', **SH), CC, '8,872 篇', 1,
  [r'25\.4% / [\d.]+% \[#', r'（[\d.]+% \[#(?=, [\d.]+\] 不在数据中)'], sign=False, scale=100)
A('c-nid-hi', '瓶颈 C：不在数据中（上限）', csv(FB + 'class_shares_by_group.csv', 'hi', cls='not_in_data', **SH), CC, '8,872 篇', 1,
  [r'25\.4% / [\d.]+% \[[\d.]+, #(?=\])', r'（[\d.]+% \[[\d.]+, #(?=\] 不在数据中)'], sign=False, scale=100)
CO = r'(?=% \[[\d.]+, [\d.]+\] / [\d.]+% / )'
A('c-co', '瓶颈 C：合作者类编造名比例', csv(FB + 'class_shares_by_group.csv', 'share', cls='coauthor', **SH), CC, '8,872 篇', 1,
  [r'(?<=：)#' + CO, r'合作者比例 #(?=% 虽高于)', r'合作者比例 #(?=% \[[\d.]+, [\d.]+\] 高于)'], sign=False, scale=100)
A('c-co-lo', '瓶颈 C：合作者类（下限）', csv(FB + 'class_shares_by_group.csv', 'lo', cls='coauthor', **SH), CC, '8,872 篇', 1,
  [r'(?<=：)[\d.]+% \[#(?=, [\d.]+\] / [\d.]+% / )'], sign=False, scale=100)
A('c-co-hi', '瓶颈 C：合作者类（上限）', csv(FB + 'class_shares_by_group.csv', 'hi', cls='coauthor', **SH), CC, '8,872 篇', 1,
  [r'(?<=：)[\d.]+% \[[\d.]+, #(?=\] / [\d.]+% / )'], sign=False, scale=100)
A('c-shuf', '瓶颈 C：同领域打乱基线的合作者比例', csv(FB + 'chance_baselines.csv', 'share', keys='si', baseline='perm_fab_field', group='all', cls='coauthor'),
  CC + '同领域内打乱编造名，20 次平均', '—', 1, [r'同领域内打乱的随机基线为 #(?=% /)', r'同领域打乱基线 #(?=%)'], sign=False, scale=100)
TC = FB + 'target_minus_control.csv'
CT = CC + 'target − control（pooled ratio，配对团队 bootstrap），单位：百分点；'
for k, lab in [('full', '全名键'), ('si_rare', '罕见名键')]:
    s = dict(keys=k, cls='coauthor')
    pre = lab + r' #(?=(?: 个百分点)? \[)'
    A('c-tc-' + k, '瓶颈 C：%s下合作者类 target − control' % lab, csv(TC, 'target_minus_control', **s), CT, '—', 2, [pre], sign=False, scale=100)
    A('c-tc-' + k + '-lo', '瓶颈 C：%s下合作者类 target − control（下限）' % lab, csv(TC, 'lo', **s), CT, '—', 2,
      [lab + ' ' + SN + r'(?: 个百分点)? \[#'], sign=False, scale=100)
    A('c-tc-' + k + '-hi', '瓶颈 C：%s下合作者类 target − control（上限）' % lab, csv(TC, 'hi', **s), CT, '—', 2,
      [lab + ' ' + SN + r'(?: 个百分点)? \[' + SN + r', #\]'], sign=False, scale=100)

# ------------------------------------------------------------------ (3b) bottleneck F: exposure thresholds (exploratory)
LT = '391_groups/summary_exposure_20261114/logistic_thresholds.csv'
CF = '逻辑回归 结果 ~ log10(1+引用数) + 年份（中心化），50% 门槛取平均年份处，9,108 篇，团队整群 bootstrap 2,000 次（探索性，事后）；'
RC = r'(?:认出|约) '
A('f-rec50', '瓶颈 F：认出的 50% 门槛（引用数）', csv(LT, 'cit50', outcome='recognition'), CF, '9,108 篇', 0, [RC + r'#(?= 次引用 \[)'], sign=False)
A('f-rec50-lo', '瓶颈 F：认出门槛（下限）', csv(LT, 'cit50_lo', outcome='recognition'), CF, '9,108 篇', 0, [RC + r'\d+ 次引用 \[#'], sign=False)
A('f-rec50-hi', '瓶颈 F：认出门槛（上限）', csv(LT, 'cit50_hi', outcome='recognition'), CF, '9,108 篇', 0, [RC + r'\d+ 次引用 \[\d+, #\]'], sign=False)
WC = [(r'门槛为 ', r' 次引用'), (r'写出 ', r' 次')]
A('f-rcl50', '瓶颈 F：写出的 50% 门槛（引用数）', csv(LT, 'cit50', outcome='recall'), CF, '9,108 篇', 0, [a + '#(?=' + b + r' \[)' for a, b in WC], sign=False)
A('f-rcl50-lo', '瓶颈 F：写出门槛（下限）', csv(LT, 'cit50_lo', outcome='recall'), CF, '9,108 篇', 0, [a + r'[\d,]+' + b + r' \[#' for a, b in WC], sign=False)
A('f-rcl50-hi', '瓶颈 F：写出门槛（上限）', csv(LT, 'cit50_hi', outcome='recall'), CF, '9,108 篇', 0,
  [a + r'[\d,]+' + b + r' \[[\d,]+, #\]' for a, b in WC], sign=False)
A('f-ratio', '瓶颈 F：写出门槛 / 认出门槛（点估计）', op('div', csv(LT, 'cit50', outcome='recall'), csv(LT, 'cit50', outcome='recognition')),
  CF + '两个门槛点估计之比（区间尚未计算）', '9,108 篇', 0, [r'11,038 / 40 ≈ #', r'ratio ≈ #'], sign=False)
EB = '391_groups/summary_exposure_20261114/exposure_by_bin.csv'
PB = dict(citation_bin='pooled within-bin (bins with >=30 per group)')
CP = '同一引用档内 target − control（两组都 ≥ 30 篇的 10 档，权重 n_t n_c/(n_t+n_c)），最终输出，全部作者全部 token（探索性）；'
A('f-pool', '瓶颈 F：档内合并 target − control', csv(EB, 'spec_all_diff', **PB), CP, '3,734 / 2,182 篇', 3, [r'10 档合并 #(?= \[)'], sign=True)
A('f-pool-lo', '瓶颈 F：档内合并（下限）', csv(EB, 'spec_all_diff_lo', **PB), CP, '同上', 3, [r'10 档合并 ' + SN + r' \[#'], sign=False)
A('f-pool-hi', '瓶颈 F：档内合并（上限）', csv(EB, 'spec_all_diff_hi', **PB), CP, '同上', 3, [r'10 档合并 ' + SN + r' \[' + SN + r', #\]'], sign=False)
