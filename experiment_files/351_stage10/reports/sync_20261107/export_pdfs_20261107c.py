"""2026-11-07 c: re-export the PDFs changed by apply_20261107e.py (H1 cell, U0 n, colon-ratio qualifiers) under new names (previous files kept) + screenshots.
Deck PDFs: talk/src/export/export_v20d_full.sbatch (three parts, lossless)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots_c'; O.mkdir(exist_ok=True); PY = sys.executable
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v29e_A4.pdf'), '第 29 版（2026-11-07 e）', '2026-11-07'], check=True)
s = (R / 'methods/export_pdf_20261107.py').read_text().replace('2026-11-07</span>', '2026-11-07 c</span>')
(R / 'methods/export_pdf_20261107c.py').write_text(s)
subprocess.run([PY, str(R / 'methods/export_pdf_20261107c.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261107c.pdf')], check=True)
JOBS = [(R / f'talk_docs/{k}.html', f'talkdoc_{k}_20261107c_A4.pdf') for k in ['experiment_walkthrough_methods_zh', 'experiment_walkthrough_zh', 'keys_and_shelves_script_zh_en', 'progress_report_for_advisor_zh', 'stage13_script_zh_en']]
SHOTS = [(R / 'stage1_11/stage1_11_report.html', 'h3:has-text("三种假设及其预测") + div.tw', 'report_hyp_table.png'),
         (R / 'stage1_11/stage1_11_report.html', 'td:has-text("n = 2,001 (7298")', 'report_u0.png'),
         (R / 'talk_docs/keys_and_shelves_script_zh_en.html', 'p:has-text("3 到 5 倍（L4–L40")', 'ks_colon.png'),
         (R / 'talk_docs/stage13_script_zh_en.html', 'p:has-text("3 到 5 倍（L4–L40")', 's13_colon.png')]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    for src, name in JOBS:
        pg.goto(src.as_uri(), wait_until='networkidle', timeout=180000); pg.wait_for_timeout(600); pg.emulate_media(media='print')
        pg.pdf(path=str(D / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name); pg.emulate_media(media='screen')
    for src, sel, png in SHOTS:
        pg.set_viewport_size({'width': 1100, 'height': 1400}); pg.goto(src.as_uri(), wait_until='load', timeout=300000); pg.wait_for_timeout(800)
        el = pg.locator(sel).first; el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
        r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
        h = int(min(r[3] + 16, 1800)); pg.set_viewport_size({'width': 1100, 'height': max(h, 100)}); el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
        r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
        pg.screenshot(path=str(O / png), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=max(r[1] - 8, 0), width=r[2] + 16, height=h)); print('shot', png)
    b.close()
