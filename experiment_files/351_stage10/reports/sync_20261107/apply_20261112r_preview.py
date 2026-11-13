"""Round r preview: render <section> fragments with the deck's own <head> (CSS + fonts) to PNG.
usage: apply_20261112r_preview.py OUTDIR frag1.html [frag2.html ...]  (run with PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw)
Adds a Noto Sans SC subset (only the CJK characters present) like the final deck."""
import sys, re, urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
DECK = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')

def cjk_link(text):
    chars = ''.join(sorted(set(re.findall(r'[⺀-鿿　-〿＀-￯]', text))))
    return f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&text={urllib.parse.quote(chars)}&display=swap">' if chars else ''

if __name__ == '__main__':
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    h = DECK.read_text(encoding='utf-8'); head = h[:h.index('</head>')]
    frags = [Path(f).read_text(encoding='utf-8') for f in sys.argv[2:]]
    for f, fr in zip(sys.argv[2:], frags):
        fr = fr.replace('class="slide ', 'class="slide on ', 1)
        doc = head + cjk_link(fr) + '<style>.nav{display:none}</style></head><body><div class="viewport"><div class="stage" id="stage" style="--s:1">' + fr + '</div></div></body></html>'
        p = out / (Path(f).stem + '_preview.html'); p.write_text(doc, encoding='utf-8')
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=1.5)
        for f in sys.argv[2:]:
            p = out / (Path(f).stem + '_preview.html'); pg.goto(p.as_uri(), wait_until='networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
            pg.locator('#stage').screenshot(path=str(out / (Path(f).stem + '.png'))); print('wrote', out / (Path(f).stem + '.png'))
        b.close()
