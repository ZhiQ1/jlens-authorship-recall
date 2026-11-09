"""2026-11-08 round e: re-export the PDFs changed by apply_20261108a.py (new names, previous kept) + screenshots.
Deck PDFs: talk/src/export/export_v20g_full.sbatch (three parts, lossless)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots_e'; O.mkdir(exist_ok=True); PY = sys.executable
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v29g_A4.pdf'), '第 29 版（2026-11-08 g）', '2026-11-08'], check=True)
s = (R / 'methods/export_pdf_20261107.py').read_text().replace('2026-11-07</span>', '2026-11-08 a</span>')
(R / 'methods/export_pdf_20261108a.py').write_text(s)
subprocess.run([PY, str(R / 'methods/export_pdf_20261108a.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261108a.pdf')], check=True)
JOBS = [(R / f'talk_docs/{k}.html', f'talkdoc_{k}_20261108a_A4.pdf') for k in ['experiment_walkthrough_methods_zh', 'experiment_walkthrough_zh', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh', 'stage13_script_zh_en']]
JOBS += [(R / 'advisor/index.html', 'jlens_progress_report_2026-11-08a_A4.pdf'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-08a_A4.pdf'),
         (Path('/scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html'), 'scoring_audit_2026-11-08a_A4.pdf'), (R / 'pages_20261106b/methods_addendum/index.html', 'methods_addendum_2026-11-08a_A4.pdf')]
RP = R / 'stage1_11/stage1_11_report.html'
SHOTS = [(RP, 'p:has-text("目标 − 对照（用户确认的措辞）")', 'report_alltok_B3.png'), (RP, '#pd-b1-e4b5', 'report_pd_e4b5.png'),
         (R / 'methods/methods_handbook.html', '#s13-alltok ~ p:has-text("有三个版本")', 'hb_alltok_B3.png'), (R / 'advisor/index.html', 'li:has-text("有三个版本")', 'advisor_B3.png'),
         (RP, 'div.bx:has-text("Stage 8 的 CPU 代理")', 'report_s8_rq1.png')]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    for src, name in JOBS:
        pg.goto(src.as_uri(), wait_until='networkidle', timeout=180000); pg.wait_for_timeout(600); pg.emulate_media(media='print')
        pg.pdf(path=str(D / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name); pg.emulate_media(media='screen')
    for src, sel, png in SHOTS:
        try:
            pg.set_viewport_size({'width': 1100, 'height': 1400}); pg.goto(src.as_uri(), wait_until='load', timeout=300000); pg.wait_for_timeout(800)
            el = pg.locator(sel).first; el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            h = int(min(r[3] + 16, 2000)); pg.set_viewport_size({'width': 1100, 'height': max(h, 100)}); el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            pg.screenshot(path=str(O / png), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=max(r[1] - 8, 0), width=r[2] + 16, height=h)); print('shot', png)
        except Exception as e:
            print('WARN shot', png, str(e)[:120])
    b.close()
