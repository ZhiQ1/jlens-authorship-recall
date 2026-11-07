"""Master queue / plan document 2026-11-06 b: rows of make_plan_20261106.py with statuses as of 2026-11-06 ~21:00 EST
(batch 1 items 1, 2, 4 done; item 3 running 116/194; C-3b done (sensitivity only); batch 2 'code ready, queued (auto)'; batch 3 (addendum 14) 'code in progress';
3-4 / 3-5 not done). Writes plan_master_queue_20261106b.{md,html} and downloads/plan_master_queue_20261106b_A4.pdf. make_plan_20261106.py is not changed."""
import sys
from pathlib import Path
D = Path(__file__).parent; sys.path.insert(0, str(D))
import make_plan_20261106 as P
R13 = '381_stage13/reports/'
NEW = {
 '1 X1–X4 for all authors (incl. new S_auth)': ('done', R13 + 'b1_xall_report.md (hard check PASS; conclusions unchanged); report Part 4 M3/X1/X4 box + Part 5 #pd-b1-xall'),
 '3 P1 / P2 with five false titles': ('running', '116 / 194 units done, 78 left in three parallel chains (g391_b1p12f 11691019 / 11691020 / 11691021); analysis → 391_groups/reports/b1_p12f_report.md; placeholder #pd-b1-p12f'),
 '4 E4b and all-token probe minus five false titles (per-donor exclusion)': ('done', R13 + 'b1_e4b5_report.md (hard check E4b L40 +0.0609 PASS); report #alltok-results + #pd-b1-e4b5'),
 'C-3b same for the five-false-title version': ('done (sensitivity only)', R13 + 'c13_C3b.md (hard check PASS; includes leakage, not a conclusion)'),
}
rows = []
for g, i, b, s, a, r in P.ROWS:
    if i in NEW: s, r = NEW[i]
    elif g == 'Batch 2': s = 'code ready, queued (auto)'; r = (r + '; ' if r else '') + 'code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1' + ('; deviation D12 (prereg_addendum12_deviations.json)' if i.split()[0] in ('2-1', '2-2', '2-11') else '') + ('; source = year-free X4 prompt (deviation, b2_groupA_handoff.md)' if i.startswith('2-7') else '')
    elif i.startswith('3-4'): s = 'not done'; r = 'user decision 2026-11-06 (b); CPU proxy C-2 reported instead; 3-5 depends on it (not done) — addendum 14'
    elif i.startswith('further batch-3 items'):
        continue
    rows.append((g, i, b, s, a, r))
assert sum(1 for x in rows if x[1] in NEW) == len(NEW)
k = next(n for n, x in enumerate(rows) if x[1].startswith('3-4'))
rows[k:k] = [('Batch 3', '3-1 Stage 10 L41–L47 and L49 (6,841 papers, logit + public J-lens)', 'batch 3', 'code in progress', 'addendum 14', 'starts after batch 2; hard check = L24 / L48 reproduction'),
             ('Batch 3', '3-2 Stage 10 L0–L23', 'batch 3', 'code in progress', 'addendum 14', 'after 3-1'),
             ('Batch 3', '3-3 Stage 7.1B fast path', 'batch 3', 'code in progress', 'addendum 14', '')]
P.ROWS[:] = rows
md = P.md().replace('Status as of 2026-11-06 ~04:10 EST.', 'Status as of 2026-11-06 ~21:00 EST (revision b).')
html = P.page().replace('截至 2026-11-06 约 04:10 EST。', '截至 2026-11-06 约 21:00 EST（b 版）。').replace("'code ready, queued (auto)'", '')
for st, col in [('code ready, queued (auto)', '#1D6FB8'), ('code in progress', '#7C3AED')]:
    html = html.replace(f'background:#555">{st}', f'background:{col}">{st}')
(D / 'plan_master_queue_20261106b.md').write_text(md, encoding='utf-8'); (D / 'plan_master_queue_20261106b.html').write_text(html, encoding='utf-8')
if '--pdf' in sys.argv:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 1600})
        pg.goto((D / 'plan_master_queue_20261106b.html').as_uri(), wait_until='networkidle'); pg.screenshot(path=str(D / 'chk_plan_20261106b.png'), full_page=True)
        pg.emulate_media(media='print')
        out = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/plan_master_queue_20261106b_A4.pdf')
        pg.pdf(path=str(out), format='A4', landscape=True, print_background=True, margin=dict(top='12mm', bottom='12mm', left='10mm', right='10mm')); b.close(); print('pdf', out)
print('ok', len(rows), 'rows')
