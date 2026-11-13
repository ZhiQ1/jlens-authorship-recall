"""Round n (2), 2026-11-12, LOCAL only. (3) X1 replacement R: main = all authors (381_stage13/reports/b1_xall_report.md "X1: R (test, confirmatory) by stratum", lines 61, 63, 64:
L24 0.996, L40 0.933, L48 0.455), old first-author values (0.99 / 0.92 / 0.42) in parentheses — deck slide 69 + notes, README (the report has no X1 R sentence).
(4) Handbook F X3 behaviour table: all-author table from b1_xall_report.md "X3 behaviour" (lines 136–148) inserted above, first-author table kept and labelled 旧版只看第一作者.
Backups *.before_20261112n2; handbook rebuilt. Log appended to the manifest under "round n (2)"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable
DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'; READ = R / 'github/README_draft_20261106b.md'; F = R / 'methods/parts/F_stage13.html'; HB = R / 'methods/methods_handbook.html'
EDIT = [DECK, NOTES, READ, F]
for p in EDIT + [HB]: assert not Path(str(p) + '.before_20261112n2').exists(), p
xa = (J / '381_stage13/reports/b1_xall_report.md').read_text(encoding='utf-8').splitlines()
assert xa[60].startswith('| L24 | +0.996 /') and xa[62].startswith('| L40 | +0.933 /') and xa[63].startswith('| L48 | +0.455 /'), (xa[60][:20], xa[62][:20], xa[63][:20])
x3 = {tuple(c.strip() for c in l.split('|')[1:4]): [c.strip() for c in l.split('|')[4:7]] for l in xa[138:147]}
assert x3[('all', 'test', 'all')][1] == '+0.897 [+0.868, +0.926]' and x3[('all', 'test', 'target_minus_control')][1] == '-0.007 [-0.075, +0.059]'
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; NJ = json.loads(S[NOTES]); LOG = []
def R_(old, new, files, n=None):
    tot = 0
    for p in files:
        if isinstance(p, tuple): t = NJ[p[1]]['text']
        else: t = S[p]
        c = t.count(old)
        if not c: continue
        t = t.replace(old, new); tot += c
        if isinstance(p, tuple): NJ[p[1]]['text'] = t
        else: S[p] = t
        LOG.append((('notes_zh.json #' + p[1]) if isinstance(p, tuple) else str(p).replace(str(R) + '/', ''), old, new, c))
    assert tot >= 1 and (n is None or tot == n), (old[:70], tot, n)
NK = [('N', k) for k in NJ]
R_('R ≈ 0.99 (L24), 0.92 (L40), 0.42 (L48) whichever question the state came from', 'R ≈ 0.996 (L24), 0.933 (L40), 0.455 (L48) for all authors, whichever question the state came from (old first-author version: 0.99 / 0.92 / 0.42)', [DECK], 1)
R_('L24 约 0.99，L40 约 0.92，L48 约 0.42〔', '全部作者 L24 约 0.996，L40 约 0.933，L48 约 0.455〔补充 10 第 1 项；381_stage13/reports/b1_xall_report.md “X1: R (test, confirmatory) by stratum” 表〕（旧版只看第一作者：L24 约 0.99，L40 约 0.92，L48 约 0.42）〔', NK, 1)
R_('恢复 R 在 L24 约 0.99、L40 0.92、L48 0.42〔', '恢复 R 在 L24 约 0.996、L40 0.933、L48 0.455（全部作者，b1_xall_report.md；旧版只看第一作者：0.99 / 0.92 / 0.42）〔', NK, 1)
R_('(R 0.99 at L24, 0.92 at L40)', '(all authors R 0.996 at L24, 0.933 at L40; old first-author version: 0.99, 0.92)', [READ], 1)
lab = {'all': '全部', 'target': 'target', 'control': 'control', 'target_minus_control': 'target − control'}
rows = ''.join(f'<tr><td>{sp} {lab[g]}</td><td>{x3[("all", sp, g)][0]}</td><td><b>{x3[("all", sp, g)][1].replace("-", "−")}</b></td><td>{x3[("all", sp, g)][2].replace("-", "−")}</td></tr>' for sp in ('test', 'all') for g in ('all', 'target', 'control', 'target_minus_control'))
TAB = ('<p><b>全部作者、全部名字 token（主结果；补充 10 第 1 项，381_stage13/reports/b1_xall_report.md “X3 behaviour” 表，主分析集，all subset）：</b></p>'
       '<table class="t"><tr><th>集合 · 组</th><th>n</th><th>恢复比例 [区间]</th><th>改写 − D [区间]</th></tr>' + rows + '</table>\n<p><b>旧版只看第一作者（原 X3）：</b></p>\n')
m = re.search(r'<table class="t">\s*<tr><th>[^<]*</th>(?:(?!</table>).)*?<tr><td>test 全部</td><td>552</td>', S[F], flags=re.S); assert m
S[F] = S[F][:m.start()] + TAB + S[F][m.start():]; LOG.append(('methods/parts/F_stage13.html', '(X3 behaviour table, first author)', 'all-author table inserted above; old table labelled 旧版只看第一作者', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB]: shutil.copy2(p, Path(str(p) + '.before_20261112n2'))
for p in EDIT: p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round n (2)', '', 'Script `sync_20261107/apply_20261112n2.py` (backups `*.before_20261112n2`). X1 all-author R from b1_xall_report.md lines 61/63/64; the report has no X1 R sentence (nothing changed there). Handbook F X3 table: all-author table added, first-author table kept as 旧版.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| n2-{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round n2:', len(LOG))
