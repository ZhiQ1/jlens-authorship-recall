"""Screenshot merged-deck slides through the deck's own hash navigation: shot_deck.py DECK OUTDIR 38,40,..."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
deck, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(exist_ok=True, parents=True)
which = [int(x) for x in sys.argv[3].split(',')]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772})
    for i in which:
        pg.goto(deck.as_uri() + f'#s{i}', wait_until='load', timeout=180000); pg.reload(wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        print(i, pg.evaluate("document.getElementById('count').textContent")); pg.screenshot(path=str(out / f's{i:02d}.png'))
    b.close()
