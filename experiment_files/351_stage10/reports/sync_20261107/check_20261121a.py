"""v47 Chromium checks: 97 slides, menu 12 groups / 97 items with the 4 Stage 12-13 sub-blocks, keyboard nav, no page errors,
every ask / So line and the slide-68 table inside the stage and clear of the nav buttons, phone no horizontal scroll."""
import json, sys
from playwright.sync_api import sync_playwright
f = 'file:///scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html'
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121a_deck.json'))
bad = []
def chk(n, ok, v=''):
    print(('PASS ' if ok else 'FAIL ') + n, v)
    if not ok: bad.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-dev-shm-usage']); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f + '#s1'); pg.wait_for_timeout(1500)
    chk('97 menu items', pg.locator('#toc .toc-i').count() == 97)
    hs = pg.evaluate("[...document.querySelectorAll('#toc .toc-h')].map(e=>e.textContent)")
    chk('12 menu groups', len(hs) == 12, hs)
    chk('4 Stage 12-13 sub-blocks', sum(h.startswith('Stage 12–13 · ') for h in hs) == 4)
    mis = 0
    for k in range(2, 98):
        pg.keyboard.press('ArrowRight')
        if pg.inner_text('#count') != f'{k} / 97': mis += 1
    chk('keyboard nav 1->97', mis == 0, mis)
    pg.click('#tocbtn'); pg.wait_for_timeout(200); pg.locator('#toc a[href="#s77"]').click(); pg.wait_for_timeout(300)
    chk('menu jump 77', pg.inner_text('#count') == '77 / 97')
    JS = """(sel)=>{const s=document.querySelector('.slide.on'); const q=document.getElementById('stage').getBoundingClientRect(); const sc=q.width/1280;
      const nav=[...document.querySelectorAll('.nav button,.nav .count')].map(e=>e.getBoundingClientRect());
      return [...s.querySelectorAll(sel)].map(e=>{const r=e.getBoundingClientRect(); const hitnav=nav.some(n=>!(r.right<=n.left||r.left>=n.right||r.bottom<=n.top||r.top>=n.bottom));
        return [(r.left-q.left)/sc,(r.top-q.top)/sc,(r.right-q.left)/sc,(r.bottom-q.top)/sc,hitnav]})}"""
    for k in sorted(set(map(int, rec['ask'])) | set(map(int, rec['so'])) | {68}):
        pg.goto('about:blank'); pg.goto(f + f'#s{k}'); pg.wait_for_timeout(600)
        for sel in ('.askl', '.soln', 'table.hx'):
            for r in pg.evaluate(JS, sel):
                chk(f's{k} {sel} inside stage, clear of nav', r[0] >= 0 and r[2] <= 1280.5 and r[1] >= 0 and r[3] <= 704 and not r[4], [round(x) for x in r[:4]])
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.goto('about:blank'); pg.goto(f + '#s68'); pg.wait_for_timeout(800)
    chk('phone: no horizontal scroll', pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
    chk('no page errors', not errs, errs[:3])
    b.close()
print('CHECKS', 'FAIL' if bad else 'PASS', bad)
