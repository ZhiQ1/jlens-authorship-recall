"""2026-11-07 ~21:30 follow-up to apply_20261107g.py: two prose places that still said '减 5 个假标题平均' outside item headings
(report #ov, progress talk doc). Item names / table headings that quote the pre-registered item title are left unchanged. Backups = those of apply_20261107g.py (before_20261107d)."""
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports')
for p, a, b in [(R / 'stage1_11/stage1_11_report.html', 'X1–X4 改为全部作者、E4b 减 5 个假标题平均也已完成，结论不变', 'X1–X4 改为全部作者、E4b 逐个假标题排除版（补充 10 第 4 项）也已完成，结论不变'),
                (R / 'talk_docs/progress_report_for_advisor_zh.html', '减 5 个假标题平均的版本（2026-11-06 完成）', '逐个假标题排除的版本（补充 10 第 4 项，2026-11-06 完成）')]:
    s = p.read_text(encoding='utf-8'); assert s.count(a) == 1, (p.name, a); p.write_text(s.replace(a, b), encoding='utf-8'); print('ok', p.name)
