"""Screenshots of the sections changed by edit_v29b.py (fixed rule 6). usage: shot_v29b.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11'); O = D / 'chk_20261106b'; O.mkdir(exist_ok=True)
SEL = {'ov': '#ov .bx', 'pd_running': '#pd-running', 'alltok_tc': '#alltok-results p:has-text("目标 − 对照（用户确认的措辞）")',
       'alltok_boxes': '#alltok-results .bx.ok', 'alltok_c3b': '#alltok-results .bx:has-text("C-3b")',
       'x1x4_box': '#m3x1x4-results .bx.ok', 'x3_ptr': '#x3-results p.note:has-text("全部作者版本")', 'x2_ptr': '#x2-results p.note:has-text("全部作者版本")'}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1200, 'height': 1000})
    pg.goto((D / 'stage1_11_report.html').as_uri(), wait_until='load', timeout=300000); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(800)
    for k, sel in SEL.items():
        el = pg.locator(sel).last if k == 'alltok_boxes' else pg.locator(sel).first
        el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(500)
        r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y + window.scrollY, r.width, r.height]}')
        h = int(min(r[3] + 16, 2400)); pg.set_viewport_size({'width': 1200, 'height': h}); pg.evaluate(f'window.scrollTo(0, {r[1] - 8})'); pg.wait_for_timeout(400)
        pg.screenshot(path=str(O / f'{k}.png'), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=0, width=r[2] + 16, height=h)); print(k, 'ok', r)
    b.close()
