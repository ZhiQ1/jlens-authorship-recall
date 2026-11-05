"""python shot.py file.html outprefix sel1 [sel2 ...]  -> screenshot of element (css selector or text= ) """
import sys, asyncio
from playwright.sync_api import sync_playwright
f, pre, sels = sys.argv[1], sys.argv[2], sys.argv[3:]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1000, 'height': 1200})
    pg.goto('file://' + f, wait_until='load', timeout=120000); pg.wait_for_timeout(1500)
    for i, sel in enumerate(sels):
        el = pg.locator(sel).first
        el.screenshot(path=f'{pre}_{i}.png'); print(sel, el.bounding_box()['height'])
    b.close()
