"""v72 small-text fix (user item: 8 small-text boxes >= 14 px). For the given slides: every absolutely positioned text box
(.cats/.addb/.covso/.covna/.lead) holding text < 14 px gets 14 px (chips .tg/.st, numerals .q, reading lines .fxkey keep
their deck-wide size); then a position/width is searched where the box overlaps no other text/image/svg.
usage: relayout2.py DECK OUT.json n1,n2,..."""
import sys, json
from playwright.sync_api import sync_playwright
deck, outp, ns = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
CSS = "[data-fs14]:not(.tg):not(.q):not(.st):not(.fxkey), [data-fs14] *:not(.tg):not(.q):not(.st):not(.fxkey):not(svg):not(svg *){font-size:14px !important} [data-fs14].lead{white-space:normal;max-width:none}"
JS = r"""
([n, CSS]) => { const s = document.querySelector('.slide.on'); const R = s.getBoundingClientRect(); const sc = R.width/1280; const res = [];
 if (!document.getElementById('fs14css')) { const st = document.createElement('style'); st.id = 'fs14css'; st.textContent = CSS; document.head.appendChild(st); }
 const skip = e => e.closest('.tg,.q,.st,.fxkey,svg,.pg,[hidden]');
 const boxes = [...s.querySelectorAll('.cats,.addb,.covso,.covna,.lead')].filter(b => getComputedStyle(b).position === 'absolute' && !b.closest('[hidden]'));
 const targets = boxes.filter(b => [b, ...b.querySelectorAll('*')].some(e => !skip(e) && [...e.childNodes].some(c => c.nodeType===3 && c.textContent.trim()) && parseFloat(getComputedStyle(e).fontSize) < 14));
 targets.forEach(b => {
   const big = [b, ...b.querySelectorAll('*')].filter(e => !skip(e) && parseFloat(getComputedStyle(e).fontSize) > 14.01).map(e => e.className + ':' + getComputedStyle(e).fontSize);
   const obst = []; const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
   while (w.nextNode()) { const t = w.currentNode; if (!t.textContent.trim()) continue; const el = t.parentElement;
     if (b.contains(el) || el.closest('.pg') || el.closest('[hidden]')) continue; const cs = getComputedStyle(el); if (cs.visibility==='hidden'||cs.display==='none') continue;
     const rg = document.createRange(); rg.selectNodeContents(t); for (const q of rg.getClientRects()) if (q.width > 1 && q.height > 1) obst.push(q); }
   s.querySelectorAll('img, svg, canvas, table').forEach(e => { if (b.contains(e)) return; if (e.tagName.toLowerCase()==='svg' && e.parentElement.closest('svg')) return;
     if (e.closest('[hidden]')) return; const q = e.getBoundingClientRect(); if (q.width > 2 && q.height > 2 && q.width < R.width*0.98) obst.push(q); });
   const O = obst.map(q => [(q.left-R.left)/sc, (q.top-R.top)/sc, (q.right-R.left)/sc, (q.bottom-R.top)/sc]);
   const q0 = b.getBoundingClientRect(); const orig = {left: (q0.left-R.left)/sc, top: (q0.top-R.top)/sc, width: q0.width/sc, height: q0.height/sc};
   const st0 = b.getAttribute('style'); b.setAttribute('data-fs14', '');
   const hit = (x0,y0,x1,y1) => O.some(o => !(x1 <= o[0]-3 || x0 >= o[2]+3 || y1 <= o[1]-3 || y0 >= o[3]+3));
   const cw = b.style.width ? parseFloat(b.style.width) : null; let best = null;
   const c0 = cw || orig.width; const widths = [c0, c0+40, c0+80, c0+120, c0+160, c0+200, 560, 700, 900, 940, 1140].filter((v,i,a)=>a.indexOf(v)===i);
   for (const wd of widths) {
     b.style.width = wd + 'px'; b.style.left = orig.left + 'px'; b.style.top = orig.top + 'px';
     const q = b.getBoundingClientRect(); const W = q.width/sc, H = q.height/sc;
     const tryAt = (x, y) => { if (x < 30 || x + W > 1250 || y < 4 || y + H > 716) return false; return !hit(x, y, x+W, y+H); };
     if (tryAt(orig.left, orig.top)) { const d0 = (wd-c0)*0.3; if (!best || d0 < best.d) best = {left: orig.left, top: orig.top, width: wd, W, H, d: d0}; if (wd === c0) break; continue; }
     for (let y = 4; y + H <= 716; y += 4) for (let x = 30; x + W <= 1250; x += 6) {
       if (!tryAt(x, y)) continue; const d = Math.hypot(x-orig.left, y-orig.top) + (wd-(cw||orig.width))*0.3;
       if (!best || d < best.d) best = {left: x, top: y, width: wd, W, H, d}; }
   }
   b.removeAttribute('data-fs14'); if (st0 === null) b.removeAttribute('style'); else b.setAttribute('style', st0);
   res.push({slide: n, cls: b.className, style: st0, orig, best, big, text: b.textContent.trim().slice(0, 70)});
 });
 return res; }
"""
out = []
with sync_playwright() as p:
    br = p.chromium.launch(args=['--disable-dev-shm-usage', '--disable-gpu'])
    pg = br.new_page(viewport={'width': 1280, 'height': 772})
    for n in ns:
        pg.goto('about:blank'); pg.goto('file://' + deck + f'#s{n}'); pg.wait_for_timeout(900)
        r = pg.evaluate(JS, [n, CSS]); out += r
        for x in r: print(n, x['cls'], {k: round(v) for k, v in x['orig'].items()}, x['best'] and {k: round(v) for k, v in x['best'].items()}, x['big'], x['text'][:50], flush=True)
    br.close()
json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
