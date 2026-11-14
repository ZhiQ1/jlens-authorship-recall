"""2026-11-13 v (user rule 2026-11-13): remaining 'same timing' claims checked with data, then reworded.
A Stage 11 target vs control: L48 −0.063 [−0.104, −0.024] (team CI, 381_stage13/summary_e1_tc_timing_20261113/e1_tc_timing.csv, job 11845797) -> nearly the same.
B Stage 10 R1 vs R0 (paper-level CIs, summary_r0r1/): steepest rise same (L59–61), onset 1–2 layers later -> nearly the same.
C vs A within bin: E1 L48 −0.037 [−0.080, +0.009] includes 0 -> keep 'same timing', add basis. X7: method comparison -> unchanged.
Backups *.before_20261113v."""
import os, shutil, sys, json
R = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
import pandas as pd
e = pd.read_csv('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_e1_tc_timing_20261113/e1_tc_timing.csv')
print(e.columns.tolist()); print(e.head(12).to_string())
AZH = 'target 与 control 时间几乎相同（都在 L52–L54 达到 R ≈ 1；L48 target − control −0.063 [−0.104, −0.024]，团队 95% CI，事后，control 略早）'
AEN = 'Target and control have nearly the same timing (both reach R ≈ 1 by L52–L54; at L48 target − control −0.063, team 95% CI [−0.104, −0.024], post hoc; control slightly earlier)'
BZH = '时间几乎相同：上升最陡处相同（L59–61），起点晚 1–2 层（public J-lens L59 vs L57、logit L51 vs L50；论文 bootstrap，事后）'
EDITS = {
 'stage1_11/stage1_11_report.html': [('写对了部分作者的 R1 论文最强，但时间点相同', '写对了部分作者的 R1 论文最强，' + BZH, 1),
     ('R1 论文让优势更大，但不改变时间点', 'R1 论文让优势约大 1.8 倍，' + BZH, 1),
     ('Target and control share the same timing', AEN, 1),
     ('C 与 A 的时间点相同、信号更大', 'C 与 A 的时间点相同（档内 E1 L48 C − A −0.037 [−0.080, +0.009]，区间含 0）、信号更大', 2)],
 'advisor/index.html': [('写对了部分作者的论文（R1）最强，但时间点相同', '写对了部分作者的论文（R1）最强，' + BZH, 1)],
 'process_report/index.html': [('target 与 control 时间相同', AZH, 1)],
 'talk_docs/experiment_walkthrough_zh.html': [('target 和 control 时间点一样。', AZH + '。', 1)],
 'talk_docs/experiment_walkthrough_methods_zh.html': [('target、control 时间点一样。', AZH + '。', 1)],
 'merged_deck/stage1_11_deck.html': [('but are just as late', 'but nearly as late', 1)],
 'talk/src/export/notes_zh.json': [('但时间点一样晚', '但时间几乎一样晚（上升最陡处相同，起点晚 1–2 层）', 1), ('R1 只增加强度不改变时间', 'R1 主要增加强度，时间几乎相同（上升最陡处相同，起点晚 1–2 层）', 1)],
}
for f, reps in EDITS.items():
    p = R + f; s = open(p).read()
    for a, b, n in reps:
        if s.count(a) != n: sys.exit('COUNT %s %r %d != %d' % (f, a, s.count(a), n))
    if not os.path.exists(p + '.before_20261113v'): shutil.copy(p, p + '.before_20261113v')
    for a, b, n in reps: s = s.replace(a, b)
    if f.endswith('.json'): json.loads(s)
    open(p, 'w').write(s); print('ok', f)
