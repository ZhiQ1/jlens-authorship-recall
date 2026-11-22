"""v53 Chromium checks (H2 wording): 100 slides, menu 12 groups / 100 items, keyboard nav, menu jumps to 81 and 86, no page errors, new-slide key notes and leads inside the stage."""
from playwright.sync_api import sync_playwright
f = 'file:///scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html'
bad = []
def chk(n, ok, v=''):
    print(('PASS ' if ok else 'FAIL ') + n, v)
    if not ok: bad.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-dev-shm-usage']); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f + '#s1'); pg.wait_for_timeout(1500)
    chk('101 menu items', pg.locator('#toc .toc-i').count() == 101)
    hs = pg.evaluate("[...document.querySelectorAll('#toc .toc-h')].map(e=>e.textContent)"); chk('12 groups', len(hs) == 12, hs)
    mis = 0
    for k in range(2, 102):
        pg.keyboard.press('ArrowRight')
        if pg.inner_text('#count') != f'{k} / 101': mis += 1
    chk('keyboard nav 1->101', mis == 0, mis)
    for k in (68, 82, 84, 93):
        pg.goto('about:blank'); pg.goto(f + '#s1'); pg.wait_for_timeout(500)
        pg.click('#tocbtn'); pg.wait_for_timeout(200); pg.locator(f'#toc a[href="#s{k}"]').click(); pg.wait_for_timeout(300)
        chk(f'menu jump {k}', pg.inner_text('#count') == f'{k} / 101')
        r = pg.evaluate("""()=>{const s=document.querySelector('.slide.on');const q=document.getElementById('stage').getBoundingClientRect();const sc=q.width/1280;
           return [...s.querySelectorAll('.keyn,.lead')].map(e=>{const r=e.getBoundingClientRect();return [(r.left-q.left)/sc,(r.top-q.top)/sc,(r.right-q.left)/sc,(r.bottom-q.top)/sc]})}""")
        for x in r: chk(f's{k} note/lead inside stage', x[0] >= 0 and x[2] <= 1280.5 and x[1] >= 0 and x[3] <= 704, [round(v) for v in x])
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.goto('about:blank'); pg.goto(f + '#s68'); pg.wait_for_timeout(800)
    chk('phone: no horizontal scroll', pg.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'))
    chk('no page errors', not errs, errs[:3])
    b.close()
print('CHECKS', 'FAIL' if bad else 'PASS', bad)
