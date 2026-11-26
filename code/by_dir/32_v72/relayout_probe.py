"""For every slide: find coverage boxes (.covso / .covna) whose inline font-size < 14px, set 14px and find a position
where the box overlaps no other text / image / svg on the slide. Writes relayout.json. usage: relayout_probe.py DECK OUT.json"""
import sys, json
from playwright.sync_api import sync_playwright
deck, outp = sys.argv[1], sys.argv[2]
JS = r"""
(n) => {
 const s = document.querySelector('.slide.on'); const R = s.getBoundingClientRect();
 const sc = R.width / 1280; const res = [];
 const boxes = [...s.querySelectorAll('.covso, .covna')];
 boxes.forEach((b, bi) => {
   const fs = parseFloat(b.style.fontSize || getComputedStyle(b).fontSize);
   if (!(fs < 14)) return;
   const obst = [];
   const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
   while (w.nextNode()) { const t = w.currentNode; if (!t.textContent.trim()) continue; const el = t.parentElement;
     if (b.contains(el) || el.closest('.pg') || el.closest('[hidden]')) continue;
     if (getComputedStyle(el).visibility === 'hidden' || getComputedStyle(el).display === 'none') continue;
     const rg = document.createRange(); rg.selectNodeContents(t); for (const q of rg.getClientRects()) if (q.width > 1 && q.height > 1) obst.push(q); }
   s.querySelectorAll('img, svg, canvas, table').forEach(e => { if (b.contains(e)) return; if (e.tagName.toLowerCase()==='svg' && e.parentElement.closest('svg')) return;
     if (e.closest('[hidden]')) return; const q = e.getBoundingClientRect(); if (q.width > 2 && q.height > 2 && q.width < R.width*0.98) obst.push(q); });
   const O = obst.map(q => [(q.left-R.left)/sc, (q.top-R.top)/sc, (q.right-R.left)/sc, (q.bottom-R.top)/sc]);
   const orig = {left: parseFloat(b.style.left), top: parseFloat(b.style.top), width: parseFloat(b.style.width), fs};
   b.style.fontSize = '14px';
   const hit = (x0,y0,x1,y1) => O.some(o => !(x1 <= o[0]-3 || x0 >= o[2]+3 || y1 <= o[1]-3 || y0 >= o[3]+3));
   let best = null;
   const widths = [orig.width, 440, 560, 700, 900, 1140].filter((v,i,a)=>v && a.indexOf(v)===i);
   for (const wd of widths) {
     b.style.width = wd + 'px'; const h = b.getBoundingClientRect().height / sc;
     if (wd === orig.width && !hit(orig.left, orig.top, orig.left+wd, orig.top+h)) { best = {left: orig.left, top: orig.top, width: wd, h, d: 0}; break; }
     for (let y = 56; y + h <= 712; y += 6) for (let x = 40; x + wd <= 1240; x += 8) {
       if (hit(x, y, x+wd, y+h)) continue;
       const d = Math.hypot(x-orig.left, y-orig.top) + (wd-orig.width)*0.3;
       if (!best || d < best.d) best = {left: x, top: y, width: wd, h, d};
     }
     if (best) break;
   }
   b.style.fontSize = orig.fs + 'px'; b.style.width = orig.width + 'px';
   res.push({slide: n, bi, cls: b.className, orig, best, text: b.textContent.slice(0, 80)});
 });
 return res;
}
"""
out = []
with sync_playwright() as p:
    br = p.chromium.launch(args=['--disable-dev-shm-usage', '--disable-gpu'])
    pg = br.new_page(viewport={'width': 1280, 'height': 772})
    pg.goto('file://' + deck + '#s1'); pg.wait_for_timeout(2500)
    N = pg.evaluate("document.querySelectorAll('section.slide').length")
    for n in range(1, N + 1):
        pg.goto('about:blank'); pg.goto('file://' + deck + f'#s{n}'); pg.wait_for_timeout(700)
        r = pg.evaluate(JS, n)
        if r: print(n, json.dumps(r)[:300], flush=True); out += r
    br.close()
json.dump(out, open(outp, 'w'), indent=1)
print('boxes', len(out), 'nofit', sum(1 for r in out if not r['best']))
