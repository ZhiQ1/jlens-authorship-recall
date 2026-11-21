"""Render chosen slides (by aria-label) of a deck HTML to PNG. usage: render_labels_20261120d.py deck.html outdir prefix"""
import os, re, sys, json
from playwright.sync_api import sync_playwright
deck, out, pre = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
LABELS = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/style_labels_20261120d.json'))
t = open(deck).read()
secs = re.findall(r'<section class="slide[^"]*"[^>]*>', t)
labs = [re.search(r'aria-label="([^"]*)"', s).group(1) if 'aria-label' in s else '' for s in secs]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    for key, lab in LABELS.items():
        if lab not in labs: print('MISSING', key, lab); continue
        k = labs.index(lab) + 1
        pg.goto('about:blank'); pg.goto('file://' + deck + f'#s{k}'); pg.wait_for_timeout(1200)
        assert pg.inner_text('#count').startswith(f'{k} /'), pg.inner_text('#count')
        pg.locator('#stage').screenshot(path=f'{out}/{pre}_{key}.png'); print('ok', key, 'slide', k)
    b.close()
