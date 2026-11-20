"""2026-11-18b: render slides of a deck HTML to PNG with headless Chromium + nav/anchor/phone checks.
usage: render_20261118b.py <deck.html> <outdir> <slides: all | 1,2,5-9> [--checks]"""
import sys, json
from playwright.sync_api import sync_playwright
deck, out, sel = sys.argv[1], sys.argv[2], sys.argv[3]
checks = '--checks' in sys.argv
f = 'file://' + deck
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 772})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(f); pg.wait_for_timeout(1500)
    N = pg.evaluate("document.querySelectorAll('.slide').length")
    if sel == 'all': ns = list(range(1, N + 1))
    else:
        ns = []
        for part in sel.split(','):
            if '-' in part: a, c = part.split('-'); ns += list(range(int(a), int(c) + 1))
            else: ns.append(int(part))
    for n in ns:
        pg.goto('about:blank'); pg.goto(f + f'#s{n}'); pg.wait_for_timeout(700)
        pg.screenshot(path=f'{out}/s{n:02d}.png')
        c = pg.inner_text('#count'); pgnum = pg.evaluate("(document.querySelector('.slide.on .pg')||{}).textContent||''")
        if c != f'{n} / {N}': print('COUNT MISMATCH', n, c)
        if pgnum and pgnum != str(n): print('PG MISMATCH', n, pgnum)
    print('rendered', len(ns), 'of', N)
    if checks:
        # keyboard nav through all slides
        pg.goto('about:blank'); pg.goto(f + '#s1'); pg.wait_for_timeout(800)
        bad = 0
        for k in range(2, N + 1):
            pg.keyboard.press('ArrowRight')
            if pg.evaluate('location.hash') != f'#s{k}' or pg.inner_text('#count') != f'{k} / {N}': bad += 1
        pg.keyboard.press('ArrowRight'); print('ArrowRight end ->', pg.inner_text('#count'))
        pg.keyboard.press('Home'); print('Home ->', pg.inner_text('#count'))
        pg.keyboard.press('End'); print('End ->', pg.inner_text('#count'))
        pg.keyboard.press('ArrowLeft'); print('ArrowLeft from end ->', pg.inner_text('#count'))
        print('keyboard nav mismatches', bad)
        ph = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        worst = 0
        for n in range(1, N + 1):
            ph.goto('about:blank'); ph.goto(f + f'#s{n}'); ph.wait_for_timeout(250)
            sw = ph.evaluate('document.documentElement.scrollWidth'); worst = max(worst, sw)
            if sw > 390: print('PHONE HSCROLL', n, sw)
            if n in ns[:0]: pass
        for n in [int(x) for x in sys.argv[sys.argv.index('--phone') + 1].split(',')] if '--phone' in sys.argv else []:
            ph.goto('about:blank'); ph.goto(f + f'#s{n}'); ph.wait_for_timeout(1200); ph.screenshot(path=f'{out}/phone_s{n:02d}.png')
        print('phone max scrollWidth', worst, '(viewport 390)')
    print('page errors', errs)
    b.close()
