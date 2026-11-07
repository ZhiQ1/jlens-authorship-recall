"""2026-11-07 follow-up to apply_20261107.py (report only; backup stage1_11_report.before_20261107b.html):
- §7 J-lens sentence: move the new provenance tag inside the sentence (before '。') so the sentence itself carries the data;
- #ov bullet 4 heading 'Jacobian lens 没有显示额外的论文信息。': short pointer tag to the files of the same bullet."""
import shutil
from pathlib import Path
P = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html'); B = P.with_name('stage1_11_report.before_20261107b.html')
if not B.exists(): shutil.copy2(P, B)
s = B.read_text(encoding='utf-8')
a = 'Jacobian lens 能让中间层读出更多与名字相关的信息，但这部分信息不区分论文；三种 Jacobian lens 的结论一致。<span class="src">（Stage 10 X3，三种 Jacobian lens − logit lens'
assert s.count(a) == 1
i = s.index(a); j = s.index('</span>', i) + 7
tag = s[i + len('Jacobian lens 能让中间层读出更多与名字相关的信息，但这部分信息不区分论文；三种 Jacobian lens 的结论一致。'):j]
s = s[:i] + 'Jacobian lens 能让中间层读出更多与名字相关的信息，但这部分信息不区分论文；三种 Jacobian lens 的结论一致' + tag + '。' + s[j:]
h = '<li><b>Jacobian lens 没有显示额外的论文信息。</b>'
assert s.count(h) == 1
s = s.replace(h, '<li><b>Jacobian lens 没有显示额外的论文信息</b><span class="src">（数据见本条：351_stage7_4/summary/jlens_increment_bootstrap.csv、351_stage8/stage8D/summary/jlens_minus_vanilla.csv、351_stage10/summary_extra/X3_pairwise.csv、X3_tc_spec_vs_logit.csv）</span><b>。</b>')
P.write_text(s, encoding='utf-8'); print('ok')
