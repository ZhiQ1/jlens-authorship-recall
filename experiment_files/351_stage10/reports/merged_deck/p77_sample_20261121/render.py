import sys
from playwright.sync_api import sync_playwright
d, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772}); errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    for k, name in ((1, 'before'), (2, 'after')):
        pg.goto('about:blank'); pg.goto('file://' + d + f'#s{k}'); pg.wait_for_timeout(1500)
        print(k, pg.inner_text('#count'))
        pg.locator('#stage').screenshot(path=f'{out}/{name}.png')
        # overflow check on the shown slide
        ov = pg.evaluate("""() => { const s=document.querySelector('section.slide.on'); const r=s.getBoundingClientRect(); const bad=[];
          s.querySelectorAll('*').forEach(e=>{const q=e.getBoundingClientRect(); if(q.width&&(q.right>r.right+1||q.bottom>r.bottom+1)) bad.push(e.tagName+':'+(e.textContent||'').slice(0,40))}); return bad.slice(0,10)}""")
        print(name, 'overflow', ov)
    print('console errors', errs); b.close()
