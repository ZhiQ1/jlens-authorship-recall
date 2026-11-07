"""2026-11-07 ~02:50: in the F16 provenance tag written by apply_20261107.py, write the U0 paper count in the canonical form (2,001) -
the summary-table cell itself ('n = 2001 (7298 authors)', mirrored from 391_groups/summary_table.md, all rows without thousands separator) is left unchanged.
Backup stage1_11_report.before_20261107d.html."""
import shutil
from pathlib import Path
P = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html'); B = P.with_name('stage1_11_report.before_20261107d.html')
if not B.exists(): shutil.copy2(P, B)
s = B.read_text(encoding='utf-8')
a = 'U0（R0 × 识别不确定）+0.287 [+0.277, +0.297]; n = 2001 (7298 authors)'
assert s.count(a) == 1
s = s.replace(a, 'U0（R0 × 识别不确定）+0.287 [+0.277, +0.297]，n = 2,001 篇（7,298 位作者）')
P.write_text(s, encoding='utf-8'); print('ok')
