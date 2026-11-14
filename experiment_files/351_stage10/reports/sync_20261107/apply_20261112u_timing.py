"""2026-11-12 u (user-approved wording): 'recognition changes the size, not the timing' -> 'timing nearly the same' everywhere.
Backups *.before_20261112u. Asserts every replacement count. Numbers from 391_groups/summary_rerun_plot_20261112/ (curves.csv, trend.csv)."""
import json, shutil, os, sys
R = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
import pandas as pd
D = '/scratch/zhang.zhiqi2/jlens/391_groups/summary_rerun_plot_20261112/'
cu = pd.read_csv(D + 'curves.csv'); tr = pd.read_csv(D + 'trend.csv')
s48 = tr[tr.quantity.str.startswith('slope R(L48) per')].iloc[0]
assert (round(s48.estimate, 3), round(s48.lo, 3), round(s48.hi, 3)) == (-0.019, -0.032, -0.007)
g = lambda grp, L: cu[(cu.group == grp) & (cu.layer == L)].iloc[0]
L52 = {k: g(k, 52) for k in ['A', 'U0', 'B', 'C']}
fmt = lambda r: '%.3f [%.3f, %.3f]' % (r.R, r.R_lo, r.R_hi)
assert fmt(L52['A']) == '0.988 [0.980, 0.996]' and fmt(L52['U0']) == '1.000 [0.988, 1.012]' and fmt(L52['B']) == '1.016 [1.002, 1.031]' and fmt(L52['C']) == '0.985 [0.977, 0.994]'
assert '%.3f' % g('C', 48).R == '0.731' and '%.3f' % g('A', 48).R == '0.811'
R52ZH = 'R(L52)：A 0.988 [0.980, 0.996]、U0 1.000 [0.988, 1.012]、B 1.016 [1.002, 1.031]、C 0.985 [0.977, 0.994]'
R52EN = 'R(L52): A 0.988 [0.980, 0.996], U0 1.000 [0.988, 1.012], B 1.016 [1.002, 1.031], C 0.985 [0.977, 0.994]'
NEWZH = ('识别程度改变信号的大小；时间几乎相同——各组到 L52 都达到 R ≈ 1（%s，“L52 之前完成”不受影响），而在 L48 识别程度高的论文恢复得略少'
         '（R(L48) 每多答对一次 −0.019 [−0.032, −0.007]，事后分析；答对次数与组 B → U0 → A 重合，所以这是组间比较，不是组内剂量反应；391_groups/summary_rerun_plot_20261112/trend.csv）。') % R52ZH
SHORTZH = '识别程度改变信号大小，时间几乎相同（各组到 L52 都达到 R ≈ 1；L48 识别程度高的论文略低，事后分析，组间比较）'
C_EN = 'reaches R ≈ 1 by L52 like A (R(L52) 0.985 vs 0.988; at L48 0.731 vs 0.811)'
EDITS = {
 'stage1_11/stage1_11_report.html': [('识别程度改变信号的大小，不改变时间。', NEWZH, 1), ('而 E1 R(L48) 基本持平，从 0.90 到 0.81', 'E1 R(L48) 从 0.90 略降到 0.81', 1),
                                     ('识别程度改变信号大小、不改变时间', SHORTZH, 1)],
 'methods/methods_handbook.html': [('识别程度改变信号的大小，不改变时间。', NEWZH, 1), ('而 E1 R(L48) 基本持平，从 0.90 到 0.81', 'E1 R(L48) 从 0.90 略降到 0.81', 1)],
 'merged_deck/stage1_11_deck.html': [('Recognition changes the size, not the timing', 'Recognition changes the size; timing nearly the same', 2),
                                     ('while E1 R(L48) stays flat, 0.90 → 0.81', 'while E1 R(L48) falls slightly, 0.90 → 0.81', 1),
                                     ('U0 timing as A and B', 'U0 reaches R ≈ 1 by L52 like A and B', 1),
                                     ('same timing as A, larger gap', 'reaching R ≈ 1 by L52 like A, larger gap', 1),
                                     ('vs A: same timing', 'vs A: R ≈ 1 by L52', 1)],
 'talk_docs/stage13_script_zh_en.html': [('same timing as A', C_EN, 1)],
 'github/README_draft_20261106b.md': [('same timing as A', C_EN, 3)],
 '/home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md': [('识别程度改变信号大小、不改变时间', '识别程度改变信号大小，时间几乎相同（L52 前都完成；L48 识别程度高的略低，事后，组间比较）', 1)],
}
NOTES = R + 'talk/src/export/notes_zh.json'
NEDIT = [('识别程度改变信号的大小，不改变时间。', NEWZH, 1), ('但 L48 的恢复比例基本不变（0.90 → 0.81）', 'L48 的恢复比例略降（0.90 → 0.81，每多答对一次 −0.019 [−0.032, −0.007]，事后；答对次数与组 B → U0 → A 重合，是组间比较）', 1)]
done = []
for f, reps in EDITS.items():
    p = f if f.startswith('/') else R + f
    s = open(p).read()
    for a, b, n in reps:
        c = s.count(a)
        if c != n: sys.exit('COUNT %s: %r found %d, expected %d' % (f, a, c, n))
    if not os.path.exists(p + '.before_20261112u'): shutil.copy(p, p + '.before_20261112u')
    for a, b, n in reps: s = s.replace(a, b)
    open(p, 'w').write(s); done.append(f)
s = open(NOTES).read()
for a, b, n in NEDIT:
    if s.count(a) != n: sys.exit('COUNT notes %r %d' % (a, s.count(a)))
if not os.path.exists(NOTES + '.before_20261112u'): shutil.copy(NOTES, NOTES + '.before_20261112u')
for a, b, n in NEDIT: s = s.replace(a, b)
json.loads(s); open(NOTES, 'w').write(s); done.append('notes_zh.json')
print('done', done)
