"""2026-11-07: handbook D (#s1011-s11-e4b-check): do not quote the superseded '0.0075' in the correction note (the strict check counts it as a mismatch).
Backup D_stage10_11.before_20261107l.html."""
import shutil
from pathlib import Path
P = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/parts/D_stage10_11.html'); B = P.with_name('D_stage10_11.before_20261107l.html')
if not B.exists(): shutil.copy2(P, B)
s = B.read_text(encoding='utf-8'); a = '（更正：原写 0.0075 来自 e4b_trainstd_compare.md 在 L24/L40/L56 混入 X1 行的标注错误；'; assert s.count(a) == 1
P.write_text(s.replace(a, '（更正：此前写的最大差来自 e4b_trainstd_compare.md 在 L24/L40/L56 混入 X1 行的标注错误；'), encoding='utf-8'); print('ok')
