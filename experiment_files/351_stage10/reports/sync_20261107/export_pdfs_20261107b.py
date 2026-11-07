"""2026-11-07 b: re-export the PDFs changed by apply_20261107c.py (D, B, F) under new names (previous files kept) + screenshots.
Deck PDFs: talk/src/export/export_v20d_full.sbatch (three parts, lossless)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots_b'; O.mkdir(exist_ok=True); PY = sys.executable
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v29d_A4.pdf'), '第 29 版（2026-11-07 d）', '2026-11-07'], check=True)
s = (R / 'methods/export_pdf_20261107.py').read_text().replace('2026-11-07</span>', '2026-11-07 b</span>')
(R / 'methods/export_pdf_20261107b.py').write_text(s)
subprocess.run([PY, str(R / 'methods/export_pdf_20261107b.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261107b.pdf')], check=True)
JOBS = [(R / 'talk_docs/keys_and_shelves_script_zh_en.html', 'talkdoc_keys_and_shelves_script_zh_en_20261107b_A4.pdf'),
        (R / 'talk_docs/stage13_script_zh_en.html', 'talkdoc_stage13_script_zh_en_20261107b_A4.pdf'),
        (R / 'talk_docs/progress_report_for_advisor_zh.html', 'talkdoc_progress_report_for_advisor_zh_20261107b_A4.pdf'),
        (R / 'advisor/index.html', 'jlens_progress_report_2026-11-07b_A4.pdf'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-07b_A4.pdf'),
        (Path('/scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html'), 'scoring_audit_2026-11-07b_A4.pdf'),
        (R / 'pages_20261106b/methods_addendum/index.html', 'methods_addendum_2026-11-07b_A4.pdf')]
SHOTS = [(R / 'stage1_11/stage1_11_report.html', 'p:has-text("目标 − 对照（用户确认的措辞）")', 'report_alltok_tc.png'),
         (R / 'stage1_11/stage1_11_report.html', 'h3:has-text("三种假设及其预测") + div.tw', 'report_hyp_table.png'),
         (R / 'methods/methods_handbook.html', '#s13-alltok ~ p:has-text("首字母不显著")', 'hb_alltok.png'),
         (R / 'talk_docs/keys_and_shelves_script_zh_en.html', 'p:has-text("L48 恢复 0.82")', 'ks_082.png')]
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
