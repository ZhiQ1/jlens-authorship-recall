import sys, json
from playwright.sync_api import sync_playwright
deck, outp = sys.argv[1], sys.argv[2]; out = []
with sync_playwright() as p:
    br = p.chromium.launch(args=['--disable-dev-shm-usage', '--disable-gpu']); pg = br.new_page(viewport={'width': 1280, 'height': 772})
    for n in [3, 9, 20, 52, 65, 97, 106, 170]:
        pg.goto('about:blank'); pg.goto('file://' + deck + f'#s{n}'); pg.wait_for_timeout(900)
        out += pg.evaluate("""(n) => { const s = document.querySelector('.slide.on'); const R = s.getBoundingClientRect(); const sc = R.width/1280;
          return [...s.querySelectorAll('[data-fs14]')].map(b => { const q = b.getBoundingClientRect(); return {slide: n, cls: b.className, x: (q.left-R.left)/sc, y: (q.top-R.top)/sc, w: q.width/sc, h: q.height/sc, text: b.textContent.trim().slice(0, 60)}; }); }""", n)
    br.close()
json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False); print(len(out))
