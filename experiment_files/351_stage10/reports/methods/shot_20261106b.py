"""Screenshots of the handbook places changed by edit_20261106b.py -> shots_20261106b/"""
from pathlib import Path
from playwright.sync_api import sync_playwright
D = Path(__file__).parent; O = D / 'shots_20261106b'; O.mkdir(exist_ok=True)
SEL = {'xall': '#s13-xall', 'alltok_tc': 'p:has-text("7 结果") , #s13-alltok ~ p:has-text("按逐个假标题排除")', 'alltok_e4b5': 'p:has-text("2026-11-06 补做（补充 10 第 4 项）")',
       'k_running': '#k-b1-xall', 'k_e4b5': '#k-b1-e4b5', 'g_v61': 'tr:has-text("V61")'}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1100, 'height': 1000})
    pg.goto((D / 'methods_handbook.html').as_uri(), wait_until='load', timeout=300000); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(800)
    for k, sel in SEL.items():
        el = pg.locator(sel).last if k == 'alltok_tc' else pg.locator(sel).first
        el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
        r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
        h = int(min(r[3] + 16, 2000)); pg.set_viewport_size({'width': 1100, 'height': max(h, 200)}); el.evaluate('e => e.scrollIntoView()'); pg.wait_for_timeout(300)
        r = el.evaluate('e => {const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]}')
        pg.screenshot(path=str(O / f'{k}.png'), timeout=120000, clip=dict(x=max(r[0] - 8, 0), y=max(r[1] - 8, 0), width=r[2] + 16, height=h)); print(k, 'ok')
    b.close()
