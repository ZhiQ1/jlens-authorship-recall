"""2026-11-07: re-export the PDFs of the documents changed by apply_20261107.py (new names with 20261107 / v29c; previous files kept),
and screenshot a few changed places. Deck PDFs: talk/src/export/export_v20c_full.sbatch (lossless, two parts)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots'; O.mkdir(exist_ok=True)
PY = sys.executable
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v29c_A4.pdf'), '第 29 版（2026-11-07 c）', '2026-11-07'], check=True)
s = (R / 'methods/export_pdf_20261106b.py').read_text().replace('2026-11-06 b</span>', '2026-11-07</span>')
(R / 'methods/export_pdf_20261107.py').write_text(s.replace('(2026-11-06 b header)', '(2026-11-07 header)'))
subprocess.run([PY, str(R / 'methods/export_pdf_20261107.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261107.pdf')], check=True)
JOBS = [(R / 'talk_docs/experiment_walkthrough_methods_zh.html', 'talkdoc_experiment_walkthrough_methods_zh_20261107_A4.pdf'),
        (R / 'talk_docs/experiment_walkthrough_zh.html', 'talkdoc_experiment_walkthrough_zh_20261107_A4.pdf'),
        (R / 'talk_docs/methods_handbook_guide_plain_zh.html', 'talkdoc_methods_handbook_guide_plain_zh_20261107_A4.pdf'),
        (R / 'talk_docs/progress_report_for_advisor_zh.html', 'talkdoc_progress_report_for_advisor_zh_20261107_A4.pdf'),
        (R / 'advisor/index.html', 'jlens_progress_report_2026-11-07_A4.pdf'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-07_A4.pdf')]
SHOTS = [(R / 'stage1_11/stage1_11_report.html', '#ov ol', 'report_ov.png'), (R / 'stage1_11/stage1_11_report.html', 'div.bx.warn:has-text("协议变更")', 'report_s8.png'),
         (R / 'stage1_11/stage1_11_report.html', 'div.finding:has-text("中间层（L24–L48）各种 lens")', 'report_p27_f14.png'),
         (R / 'stage1_11/stage1_11_report.html', 'p:has-text("而且主要是标题特异的")', 'report_p21.png'),
         (R / 'advisor/index.html', 'li:has-text("Stage 8：分析计划")', 'advisor_s8.png'), (R / 'talk_docs/methods_handbook_guide_plain_zh.html', 'td:has-text("分析计划在 10-18 14:29")', 'guide_s8.png')]
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
