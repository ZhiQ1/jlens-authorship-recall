"""claims_defs v23 (2026-11-15 b): v22 (unchanged file) + (1) the addendum 16 item B numbers (output format, locked confirmatory,
final, all 30 shards, 1,500 papers; user-approved 2026-11-15) and (2) the exploratory R0 check on all 1,200 R0 papers, written into
report / handbook / advisor / Stage 13 script / talk pages / process report.
Sources: 391_groups/summary_a16_20261115/holm.csv (B_F1..B_F4; est, ci95_lo/hi, holm_ci_lo/hi, p_holm) and r0.csv.
New ids 'A23-'.  Run with:  CLAIMS_DEFS=claims_defs_v23 bash claims_run.sh"""
from claims_defs_v22 import *          # noqa: F401,F403
from claims_defs_v22 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A23-' + cid; MANUAL[-1] = c['id']


NUM = r'[+−\-]?\d\.\d+'
HO = '391_groups/summary_a16_20261115/holm.csv'
R0 = '391_groups/summary_a16_20261115/r0.csv'
CB = '补充 16 B：输出格式，chance-corrected，团队整群 bootstrap 2,000 次（seed 391），Holm 校正（5 个检验）；'
NAB = 'A 600 / B 600 篇'

# ---- (1) B, F4: DiD (Holm-adjusted CI) and Delta_A (plain 95% CI)
F4D = dict(test='B_F4', quantity='DiD_A-B')
L = [r'比 B 组多 ', r'surname more often \(']
A('b-F4-did', 'B F4：DiD（A − B 组）', csv(HO, 'est', **F4D), CB, NAB, 3, [l + '#(?= \\[)' for l in L], sign=True)
A('b-F4-did-lo', 'B F4：DiD（Holm 校正区间下限）', csv(HO, 'holm_ci_lo', **F4D), CB, NAB, 3, [l + NUM + r' \[#' for l in L], sign=False)
A('b-F4-did-hi', 'B F4：DiD（Holm 校正区间上限）', csv(HO, 'holm_ci_hi', **F4D), CB, NAB, 3, [l + NUM + r' \[' + NUM + r', #\]' for l in L], sign=False)
A('b-F4-p', 'B F4：Holm 校正后 p', csv(HO, 'p_holm', **F4D), CB, '—', 4,
  [r'比 B 组多 [^）]*?Holm 校正后 p = #', r'over group B, Holm p = #'], sign=False)
F4A = dict(test='B_F4', quantity='Delta_A')
L = [r'F4 的 Δ_A ', r'F4 Δ_A ']
A('b-F4-dA', 'B F4：Δ_A', csv(HO, 'est', **F4A), CB, 'A 600 篇', 3, [l + '#(?= \\[)' for l in L], sign=True)
A('b-F4-dA-lo', 'B F4：Δ_A（95% 下限）', csv(HO, 'ci95_lo', **F4A), CB, 'A 600 篇', 3, [l + NUM + r' \[#' for l in L], sign=False)
A('b-F4-dA-hi', 'B F4：Δ_A（95% 上限）', csv(HO, 'ci95_hi', **F4A), CB, 'A 600 篇', 3, [l + NUM + r' \[' + NUM + r', #\]' for l in L], sign=False)

# ---- F2 / F1 / F3 DiD (Holm-adjusted CI written in parentheses)
for t, zh, en, ci in [('B_F2', r'F2（只写姓）DiD ', r'F2 \(surnames only\) DiD ', True),
                      ('B_F1', r'F1（姓在前的列表）', r'F1 \(surname-first list\) ', True),
                      ('B_F3', r'F3（只写第一作者的姓）', r"F3 \(first author's surname only\) ", False)]:
    sel = dict(test=t, quantity='DiD_A-B')
    cid = 'b-' + t[2:].lower() + '-did'
    A(cid, 'B %s：DiD（A − B 组）' % t[2:], csv(HO, 'est', **sel), CB, NAB, 3, [zh + '#', en + '#'], sign=True)
    if ci:
        lo_l = [zh + NUM + r'（(?:Holm 校正区间 )?#', en + NUM + r' \((?:Holm CI )?#']
        hi_l = [zh + NUM + r'（(?:Holm 校正区间 )?' + NUM + ', #）', en + NUM + r' \((?:Holm CI )?' + NUM + r', #\)']
        A(cid + '-lo', 'B %s：DiD（Holm 校正区间下限）' % t[2:], csv(HO, 'holm_ci_lo', **sel), CB, NAB, 3, lo_l, sign=False)
        A(cid + '-hi', 'B %s：DiD（Holm 校正区间上限）' % t[2:], csv(HO, 'holm_ci_hi', **sel), CB, NAB, 3, hi_l, sign=False)

# ---- (2) exploratory R0 check, all 1,200 R0 papers
CR = '补充 16 B 的 F0（原格式）输出，探索性 R0 检查，A + B 组全部 R0 论文，团队整群 bootstrap 2,000 次；'
AB = dict(group='A+B (R0)', fa_type='all')
A('r0-full', 'R0：至少写对 1 个完整作者名的比例', csv(R0, 'est', measure='any_full', **AB), CR, '1,200 篇', 2,
  [r'完整作者名的占 #(?=% \[)', r'≥ 1 correct full name #(?=% \[)'], sign=False, scale=100)
A('r0-full-lo', 'R0：完整作者名比例（下限）', csv(R0, 'lo', measure='any_full', **AB), CR, '1,200 篇', 1,
  [r'完整作者名的占 [\d.]+% \[#(?=%)', r'≥ 1 correct full name [\d.]+% \[#(?=%)'], sign=False, scale=100)
A('r0-full-hi', 'R0：完整作者名比例（上限）', csv(R0, 'hi', measure='any_full', **AB), CR, '1,200 篇', 1,
  [r'完整作者名的占 [\d.]+% \[[\d.]+%, #(?=%\])', r'≥ 1 correct full name [\d.]+% \[[\d.]+%, #(?=%\])'], sign=False, scale=100)
A('r0-chance', 'R0：同领域对照论文的偶然匹配', csv(R0, 'est', measure='c_any_full', **AB), CR, '1,200 篇', 2,
  [r'偶然匹配为 #(?=%)', r'chance #(?=%\))', r'（偶然 #(?=%）)'], sign=False, scale=100)
A('r0-fs', 'R0：也算只写对姓的比例', csv(R0, 'est', measure='any_fs', **AB), CR, '1,200 篇', 1,
  [r'只写对姓的，占 #(?=%)', r'surname also allowed #(?=%)'], sign=False, scale=100)
A('r0-A', 'R0：A 组完整作者名比例', csv(R0, 'est', measure='any_full', group='A', fa_type='all'), CR, 'A 600 篇', 1,
  [r'（A 组 #(?=%、B 组)', r'\(A #(?=%, B )'], sign=False, scale=100)
A('r0-B', 'R0：B 组完整作者名比例', csv(R0, 'est', measure='any_full', group='B', fa_type='all'), CR, 'B 600 篇', 1,
  [r'（A 组 [\d.]+%、B 组 #(?=%)', r'\(A [\d.]+%, B #(?=%)'], sign=False, scale=100)
