"""2026-11-07: remove the double full stop after the X4 sentence written by apply_20261107g.py (report #m3x1x4-results). Backup *.before_20261107j.html."""
import shutil
from pathlib import Path
P = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html'); B = P.with_name('stage1_11_report.before_20261107j.html')
if not B.exists(): shutil.copy2(P, B)
s = B.read_text(encoding='utf-8'); a = '没有做调参/测试拆分。。'; assert s.count(a) == 1
P.write_text(s.replace(a, '没有做调参/测试拆分。'), encoding='utf-8'); print('ok')
