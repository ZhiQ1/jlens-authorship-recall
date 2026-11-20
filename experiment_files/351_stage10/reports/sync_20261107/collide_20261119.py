"""2026-11-19: Chromium collision check for the merged deck. For every slide: visible text boxes that touch the page number or the
prev / count / next buttons, and pairs of text boxes that overlap (> 35% of the smaller box). Also counts lines of small text
(< 12 px) below y = 480 as a 'crowding' indicator. usage: collide_20261119.py <deck.html>"""
import sys, json
from playwright.sync_api import sync_playwright
f = 'file://' + sys.argv[1]
JS = r"""() => {
 const sl = document.querySelector('.slide.on'); const st = document.getElementById('stage').getBoundingClientRect();
 const sc = st.width / 1280;
 const R = r => ({x: (r.left - st.left) / sc, y: (r.top - st.top) / sc, w: r.width / sc, h: r.height / sc});
 const boxes = [];
 const walk = document.createTreeWalker(sl, NodeFilter.SHOW_TEXT);
 let n; while ((n = walk.nextNode())) {
   const t = n.textContent.trim(); if (!t) continue;
   const el = n.parentElement; const cs = getComputedStyle(el);
   if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('desc,title')) continue;
   const rg = document.createRange(); rg.selectNodeContents(n);
   for (const r of rg.getClientRects()) { if (r.width < 2 || r.height < 2) continue;
     const b = R(r); b.t = t.slice(0, 40); b.fs = parseFloat(cs.fontSize) / sc; b.pg = !!el.closest('.pg'); boxes.push(b); }
 }
 const nav = ['prev', 'count', 'next'].map(id => R(document.getElementById(id).getBoundingClientRect()));
 const pg = boxes.filter(b => b.pg);
 const hit = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
 const out = {nav: [], pg: [], ov: [], small: 0};
 const txt = boxes.filter(b => !b.pg);
 for (const b of txt) { for (const z of nav) if (hit(b, z) > 4) out.nav.push(b.t);
   for (const z of pg) if (hit(b, z) > 4) out.pg.push(b.t);
   if (b.fs < 12 && b.y > 480) out.small++; }
 for (let i = 0; i < txt.length; i++) for (let j = i + 1; j < txt.length; j++) {
   const a = txt[i], b = txt[j]; const h = hit(a, b); if (h > 0.35 * Math.min(a.w * a.h, b.w * b.h) && a.t !== b.t) out.ov.push(a.t + ' ⟷ ' + b.t); }
 return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    pg.goto(f); pg.wait_for_timeout(1500)
    N = pg.evaluate("document.querySelectorAll('.slide').length")
    for k in range(1, N + 1):
        pg.goto('about:blank'); pg.goto(f + f'#s{k}'); pg.wait_for_timeout(400)
        o = pg.evaluate(JS)
        if o['nav'] or o['pg'] or o['ov'] or o['small'] > 6:
            print(f"s{k}: nav={sorted(set(o['nav']))[:3]} pg={sorted(set(o['pg']))[:2]} overlaps={len(o['ov'])} {o['ov'][:3]} small_lines_below480={o['small']}")
    b.close()
