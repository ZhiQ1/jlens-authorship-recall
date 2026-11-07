"""Handbook 2026-11-07 b (after sync_20261107/apply_20261107c.py): regenerate part K from the report after sync_20261107/apply_20261107.py (same conversion as edit_20261106b.py),
then run build_methods.py. Other parts were edited by apply_20261107.py (backups *.before_20261107.*)."""
import re, shutil, subprocess, sys
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods'); P = D / 'parts'
def bk7(p):
    b = p.with_name(p.stem + '.before_20261107b' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')
# --- K from the report (same conversion as edit_20261106.py)
rep_html = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html').read_text(encoding='utf-8')
assert '首字母不显著（L40 +0.014' in rep_html, 'run sync_20261107/apply_20261107c.py first'
fr = rep_html[rep_html.index('<div class="partbar" id="p5">'):]
fr = re.sub(r'<div class="partbar".*?</div>\s*<div class="p19"><main>', '', fr, count=1, flags=re.S)
fr = fr.replace('</main></div>', '')
for sid, kid in [('pd-groups', 'k-groups'), ('pd-cpu', 'k-cpu'), ('pd-running', 'k-running'), ('pd-limits', 'k-limits')]:
    fr = fr.replace(f'<section id="{sid}"><h2>', f'<h3 id="{kid}">')
fr = re.sub(r'</h2>', '</h3>', fr); fr = fr.replace('</section>', '')
fr = re.sub(r'<h3>(.*?)</h3>', r'<h4>\1</h4>', fr, flags=re.S)
fr = fr.replace('<span class="ln lA">A 这篇论文？</span>', '').replace('<span class="ln lC">C 哪一层</span>', '')
fr = re.sub(r'<span class="st">([^<]*)</span>', r'<span class="st st-done">\1</span>', fr)
fr = fr.replace('<div class="bx">', '<div class="fix">').replace('<table>', '<table class="t">')
fr = fr.replace('#x2-results', '#s13-x2').replace('#alltok-results', '#s13-alltok').replace('见第四部分的说明', '见本手册 M5 节')
fr = fr.replace('id="pd-b1-', 'id="k-b1-').replace('id="pd-p1p2-numden"', 'id="k-p1p2-numden"')
bk7(P / 'K_post_defence.html')
K = ('<section id="k-post"><h2>十一 答辩后新增（2026-11-05 / 06）</h2>\n'
     '<p class="lead">答辩材料 2026-11-02/03 定稿之后的工作。分组对比是答辩后新增的分析，分析计划在看结果前写定（补充 7、8）；其余 CPU 补充分析是事后分析；重做计划（补充 10–14）的规则都在看结果前写定。'
     '与《Stage 1–13 实验报告》第 29 版第五部分内容相同（图号、表号沿用报告）。</p>\n' + fr.strip() + '\n</section>')
assert 'p19' not in re.sub(r'data:[^"]*', '', K)
(P / 'K_post_defence.html').write_text(K, encoding='utf-8')

subprocess.run([sys.executable, str(D / 'build_methods.py')], check=True)
