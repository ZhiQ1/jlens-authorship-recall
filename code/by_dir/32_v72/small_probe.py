"""List every visible HTML text element (outside svg) with computed font-size < 14px on given slides. usage: small_probe.py DECK OUT.json n1,n2,..."""
import sys, json
from playwright.sync_api import sync_playwright
deck, outp, ns = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
JS = r"""
(n) => { const s = document.querySelector('.slide.on'); const R = s.getBoundingClientRect(); const sc = R.width/1280; const out = [];
 const all = [...s.querySelectorAll('*')];
 all.forEach((e, ei) => { if (e.closest('svg') || e.closest('.pg')) return;
   const own = [...e.childNodes].filter(c => c.nodeType === 3 && c.textContent.trim()).map(c => c.textContent).join(' ').trim();
   if (!own) return; const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return;
   const fs = parseFloat(cs.fontSize); if (fs >= 14) return; const q = e.getBoundingClientRect();
   out.push({slide: n, ei, tag: e.tagName, cls: e.className, fs, inline: e.getAttribute('style') || '', x: (q.left-R.left)/sc, y: (q.top-R.top)/sc, w: q.width/sc, h: q.height/sc, text: own.slice(0, 90)}); });
 return out; }
"""
out = []
with sync_playwright() as p:
    br = p.chromium.launch(args=['--disable-dev-shm-usage', '--disable-gpu'])
    pg = br.new_page(viewport={'width': 1280, 'height': 772})
    for n in ns:
        pg.goto('about:blank'); pg.goto('file://' + deck + f'#s{n}'); pg.wait_for_timeout(900)
        out += pg.evaluate(JS, n)
    br.close()
json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
for r in out: print(r['slide'], r['tag'], r['cls'], r['fs'], round(r['x']), round(r['y']), round(r['w']), r['text'][:70])
