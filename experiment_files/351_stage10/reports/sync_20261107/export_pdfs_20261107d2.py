"""2026-11-07 d2 (after apply_20261107i.py, D13-1 rewording): only report, handbook and the D13-1 / V59 screenshots. Earlier: 2026-11-07 d: re-export the PDFs changed by apply_20261107g.py / h.py (new names, previous kept) + screenshots of changed spots.
Deck PDFs: talk/src/export/export_v20f_full.sbatch (three parts, lossless)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots_d'; O.mkdir(exist_ok=True); PY = sys.executable
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v29f_A4.pdf'), '第 29 版（2026-11-07 f）', '2026-11-07'], check=True)
s = (R / 'methods/export_pdf_20261107.py').read_text().replace('2026-11-07</span>', '2026-11-07 d</span>')
(R / 'methods/export_pdf_20261107d.py').write_text(s)
subprocess.run([PY, str(R / 'methods/export_pdf_20261107d.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261107d.pdf')], check=True)
JOBS0 = [(R / f'talk_docs/{k}.html', f'talkdoc_{k}_20261107d_A4.pdf') for k in ['experiment_walkthrough_methods_zh', 'experiment_walkthrough_zh', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh', 'stage13_script_zh_en']]
JOBS0 += [(R / 'advisor/index.html', 'jlens_progress_report_2026-11-07d_A4.pdf'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-07d_A4.pdf'),
         (Path('/scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html'), 'scoring_audit_2026-11-07d_A4.pdf'), (R / 'pages_20261106b/methods_addendum/index.html', 'methods_addendum_2026-11-07d_A4.pdf')]
RP = R / 'stage1_11/stage1_11_report.html'
SHOTS = [(RP, 'div.bx.warn:has-text("偏离 D13-1")', 'report_D13.png'), (R / 'methods/methods_handbook.html', 'tr:has-text("V59")', 'hb_V59.png')]
SHOTS0 = [ (RP, '#pd-running', 'report_pd_running.png'), (RP, '#pd-limits', 'report_limits.png'),
         (RP, 'p:has-text("同一引用档内，target 论文在标题位置读出第一作者的 D")', 'report_x4.png'), (RP, 'div.pair:has-text("两种标准化差别最大 0.0007")', 'report_611.png'),
         (R / 'methods/methods_handbook.html', 'tr:has-text("V59")', 'hb_V59.png'), (R / 'advisor/index.html', 'section:has-text("局限")', 'advisor_limits.png')]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    for src, name in []:
        pg.goto(src.as_uri(), wait_until='networkidle', timeout=180000); pg.wait_for_timeout(600); pg.emulate_media(media='print')
        pg.pdf(path=str(D / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name); pg.emulate_media(media='screen')
    for src, sel, png in SHOTS:
        try:
            pg.set_viewport_size({'width': 1100, 'height': 1400}); pg.goto(src.as_uri(), wait_until='load', timeout=300000); pg.wait_for_timeout(800)
            el = pg.locator(sel).last if png == 'advisor_limits.png' else pg.locator(sel).first; el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            h = int(min(r[3] + 16, 2000)); pg.set_viewport_size({'width': 1100, 'height': max(h, 100)}); el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            pg.screenshot(path=str(O / png), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=max(r[1] - 8, 0), width=r[2] + 16, height=h)); print('shot', png)
        except Exception as e:
            print('WARN shot', png, str(e)[:120])
    b.close()
