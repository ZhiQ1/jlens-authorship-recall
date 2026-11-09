"""2026-11-08 c (v30): hypotheses-table PNGs v30 (zh + en), deck slide-65 image, report v30 PDF, handbook 2026-11-08 c PDF, page / talk-doc PDFs (20261108c / 2026-11-08c),
screenshots of changed spots (sync_20261107/shots_g). Deck PDFs: talk/src/export/export_v21_full.sbatch; pptx v21: pptx_text_fix_20261108c.py (both in export_20261108c.sbatch)."""
import subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); D = R / 'downloads'; O = R / 'sync_20261107/shots_g'; O.mkdir(exist_ok=True); PY = sys.executable
MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
if MODE in ('png', 'all'):
    subprocess.run([PY, str(R / 'stage1_11/src/hyp_table_png_v30.py')], check=True)
    subprocess.run([PY, str(R / 'stage1_11/src/hyp_table_png_v30_en.py')], check=True)
    subprocess.run([PY, str(R / 'sync_20261107/deck_slide65_img_20261108c.py')], check=True)
if MODE == 'png': sys.exit(0)
subprocess.run([PY, str(R / 'talk/src/export/export_report_v27.py'), str(D / 'Stage1-13_report_v30_A4.pdf'), '第 30 版（2026-11-08）', '2026-11-08'], check=True)
s = (R / 'methods/export_pdf_20261108b.py').read_text().replace('2026-11-08 b</span>', '2026-11-08 c</span>')
(R / 'methods/export_pdf_20261108c.py').write_text(s)
subprocess.run([PY, str(R / 'methods/export_pdf_20261108c.py'), str(D / 'Stage1-13_methods_handbook_A4.v20261108c.pdf')], check=True)
JOBS = [(R / f'talk_docs/{k}.html', f'talkdoc_{k}_20261108c_A4.pdf') for k in ['experiment_walkthrough_methods_zh', 'experiment_walkthrough_zh', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh', 'stage13_script_zh_en']]
JOBS += [(R / 'advisor/index.html', 'jlens_progress_report_2026-11-08c_A4.pdf'), (R / 'process_report/index.html', 'jlens_process_report_2026-11-08c_A4.pdf'),
         (Path('/scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html'), 'scoring_audit_2026-11-08c_A4.pdf'), (R / 'pages_20261106b/methods_addendum/index.html', 'methods_addendum_2026-11-08c_A4.pdf')]
RP = R / 'stage1_11/stage1_11_report.html'; HB = R / 'methods/methods_handbook.html'; DK = R / 'merged_deck/stage1_11_deck.html'
SHOTS = [(RP, '#pd-b1-p12f', 'report_pd_p12f.png'), (RP, '#pd-b2-cd', 'report_pd_b2cd.png'), (RP, 'div.bx:has-text("Stage 8 的 CPU 代理")', 'report_s8_box.png'),
         (RP, 'div.bx.warn:has-text("偏离 D13-1（补充 13 C-2 的规则触发）")', 'report_d13_box.png'), (RP, '#pd-limits', 'report_limits.png'),
         (RP, 'h3:has-text("三种假设及其预测") + div.tw table', 'report_hyp_table.png'), (HB, '#k-b2-cd', 'hb_k_b2cd.png'), (HB, '#s19-s8d + div.fix', 'hb_s8d.png'),
         (R / 'advisor/index.html', 'li:has-text("C / D 组补全 E1 / E2")', 'advisor_cd.png'),
         (DK, 'section[aria-label="Stage 8 re-scored on CPU: three premises"]', 'deck_s19.png'), (DK, 'section[aria-label="Re-runs: numerator and denominator"]', 'deck_s77.png'),
         (DK, 'section[aria-label="Redo programme (addenda 10–14)"]', 'deck_s81.png'), (DK, 'section[aria-label="Limits that cannot be redone"]', 'deck_s82.png'),
         (DK, 'section[aria-label="Patchscope and paraphrases"]', 'deck_s70.png')]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1400})
    for src, name in JOBS:
        pg.goto(src.as_uri(), wait_until='networkidle', timeout=180000); pg.wait_for_timeout(600); pg.emulate_media(media='print')
        pg.pdf(path=str(D / name), format='A4', print_background=True, margin=dict(top='14mm', bottom='14mm', left='12mm', right='12mm')); print('pdf', name); pg.emulate_media(media='screen')
    for src, sel, png in SHOTS:
        try:
            W = 1320 if src == DK else 1100
            pg.set_viewport_size({'width': W, 'height': 1400}); pg.goto(src.as_uri(), wait_until='load', timeout=300000); pg.wait_for_timeout(800)
            el = pg.locator(sel).first; el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            h = int(min(r[3] + 16, 2400)); pg.set_viewport_size({'width': W, 'height': max(h, 100)}); el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
            r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
            pg.screenshot(path=str(O / png), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=max(r[1] - 8, 0), width=r[2] + 16, height=h)); print('shot', png)
        except Exception as e:
            print('WARN shot', png, str(e)[:160])
    b.close()
