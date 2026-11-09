"""2026-11-07 ~22:20 REPAIR: apply_20261107g.py started the report from stage1_11_report.before_20261107d.html, a backup name that
apply_20261107d.py had already used at ~02:50 (state BEFORE apply_20261107d/e). So the report lost the 03:00 edits of apply_20261107d.py
(U0 tag 2,001) and apply_20261107e.py (H1 cell of the hypothesis table, X1 colon sentence late layers, U0 table cell 2,001).
This script re-applies exactly those replacements on the current report (all later edits kept). Backup *.before_20261107k.html."""
import json, shutil
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); P = R / 'stage1_11/stage1_11_report.html'
B = P.with_name('stage1_11_report.before_20261107k.html')
if not B.exists(): shutil.copy2(P, B)
s = B.read_text(encoding='utf-8')
NUM = json.load(open(R / 'sync_20261107/H1_numbers_20261107.json'))
SRC = f'<span class="src">（Stage 13 X1 相似度检查，“:” 位置，同篇换问法与换论文的相对距离之比，9,108 篇、3 个问法对平均：L4–L40 为 {NUM["lo"]}–{NUM["hi"]}，L48 {NUM["l48"]}，L56–L63 {NUM["late_lo"]}–{NUM["late_hi"]}；381_stage13/reports/x1_similarity.md colon 表；summary_m3/x1_similarity.csv question_share）</span>'
REPS = [('U0（R0 × 识别不确定）+0.287 [+0.277, +0.297]; n = 2001 (7298 authors)', 'U0（R0 × 识别不确定）+0.287 [+0.277, +0.297]，n = 2,001 篇（7,298 位作者）'),
        ('<td>见上文 M3、X1 结果</td>', f'<td>在 “:” 和名字位置成立；在 L4–L40，“:” 位置换问法时的移动是换论文时的 3–5 倍（L48 为 {NUM["l48"]} 倍，L56–L63 为 {NUM["late_lo"]}–{NUM["late_hi"]} 倍）' + SRC + '</td>'),
        ('换问法的移动距离在 L4–L40 是换论文的 3–5 倍（L48 约 2.2 倍）', f'换问法的移动距离在 L4–L40 是换论文的 3–5 倍（L48 约 {NUM["l48"]} 倍，L56–L63 为 {NUM["late_lo"]}–{NUM["late_hi"]} 倍）'),
        ('n = 2001 (7298 authors)', 'n = 2,001 (7298 authors)')]
for a, b in REPS:
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
assert '<th>目前结果（第 29 版，2026-11-07）</th>' in s and '偏离 D13-1' in s and '首字母不显著（L40 +0.014' in s
P.write_text(s, encoding='utf-8'); print('ok')
