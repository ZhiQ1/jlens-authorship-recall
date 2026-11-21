"""v46 Chromium checks: menu has 97 items with the new titles, keyboard nav across all slides, no page errors, key notes inside the stage."""
import json, re
from playwright.sync_api import sync_playwright
f = 'file:///scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html'
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261120d_style.json'))
bad = []
def chk(n, ok, v=''):
    print(('PASS ' if ok else 'FAIL ') + n, v)
    if not ok: bad.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f + '#s1'); pg.wait_for_timeout(1500)
    n = pg.locator('#toc .toc-i').count(); chk('97 menu items', n == 97, n)
    titles = pg.evaluate("[...document.querySelectorAll('#toc .toc-t')].map(e=>e.textContent)")
    for v in rec['slides'].values(): chk('menu has: ' + v['new_title'][:40], v['new_title'] in titles)
    mis = 0
    for k in range(2, 98):
        pg.keyboard.press('ArrowRight')
        if pg.inner_text('#count') != f'{k} / 97': mis += 1
    chk('keyboard nav 1→97', mis == 0, mis)
    for lab in rec['slides']:
        k = pg.evaluate(f"[...document.querySelectorAll('.slide')].findIndex(s=>s.getAttribute('aria-label')==={json.dumps(lab)})") + 1
        pg.goto('about:blank'); pg.goto(f + f'#s{k}'); pg.wait_for_timeout(700)
        bb = pg.evaluate("(()=>{const s=document.querySelector('.slide.on'); const n=s.querySelector('.keyn'); const r=n.getBoundingClientRect(), q=document.getElementById('stage').getBoundingClientRect(); return [r.left-q.left, r.top-q.top, r.right-q.left, r.bottom-q.top, q.width]})()")
        sc = bb[4] / 1280
        chk(f'note inside stage s{k}', bb[0] >= 0 and bb[2] / sc <= 1272 and bb[3] / sc <= 712, [round(x / sc) for x in bb[:4]])
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.goto('about:blank'); pg.goto(f + '#s59'); pg.wait_for_timeout(800)
    chk('phone: no horizontal scroll', pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
    chk('no page errors', not errs, errs[:3])
    b.close()
print('CHECKS', 'FAIL' if bad else 'PASS', bad)
