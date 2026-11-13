"""Round n (3), 2026-11-12, LOCAL only: handbook part F X1 result table — all-author table from 381_stage13/reports/b1_xall_report.md "X1: R (test, confirmatory) by stratum"
(lines 56–64, stratum = all) inserted above the first-author table, which is kept and labelled 旧版只看第一作者. Backups *.before_20261112n3; handbook rebuilt. Log "round n (3)"."""
import re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; F = R / 'methods/parts/F_stage13.html'; HB = R / 'methods/methods_handbook.html'
for p in (F, HB): assert not Path(str(p) + '.before_20261112n3').exists(), p
xa = (J / '381_stage13/reports/b1_xall_report.md').read_text(encoding='utf-8').splitlines()
assert xa[53].startswith('## X1: R (test, confirmatory) by stratum')
rows = []
for l in xa[57:64]:
    c = [x.strip() for x in l.split('|')]; L = c[1]; a = [v.strip() for v in c[2].split('/')]
    rows.append(f'<tr><td>{L}</td>' + ''.join(f'<td>{v.replace("-", "−")}</td>' for v in a[:4]) + f'<td>{a[4]}</td></tr>')
assert rows[3].startswith('<tr><td>L24</td><td>+0.996</td>') and rows[5].startswith('<tr><td>L40</td><td>+0.933</td>') and rows[6].startswith('<tr><td>L48</td><td>+0.455</td>'), rows[3][:40]
TAB = ('<p><b>全部作者（主结果；补充 10 第 1 项，381_stage13/reports/b1_xall_report.md “X1: R (test, confirmatory) by stratum” 表，stratum = all，第 56–64 行）：</b></p>'
       '<table class="t"><tr><th>层</th><th>R authors</th><th>R year</th><th>R field</th><th>R random C</th><th>判定</th></tr>' + ''.join(rows) + '</table>\n<p><b>旧版只看第一作者（原 X1）：</b></p>\n')
s = F.read_text(encoding='utf-8'); a = '<h4>7 结果（test，确认性；clean − corrupt = 0.347）</h4>\n<table class="t">\n<tr><th>层</th><th>R authors</th>'
assert s.count(a) == 1
s = s.replace(a, a.replace('<table class="t">', TAB + '<table class="t">', 1))
shutil.copy2(F, Path(str(F) + '.before_20261112n3')); shutil.copy2(HB, Path(str(HB) + '.before_20261112n3')); F.write_text(s, encoding='utf-8')
subprocess.run([sys.executable, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh:
    fh.write('\n## round n (3)\n\nScript `sync_20261107/apply_20261112n3.py` (backups `*.before_20261112n3`).\n\n| # | file | before | after | count |\n|---|---|---|---|---|\n'
             '| n3-1 | methods/parts/F_stage13.html | X1 result table (first author only) | all-author table (b1_xall_report.md lines 56–64) inserted above; old table labelled 旧版只看第一作者 | 1 |\n')
print('ok')
