"""Deck v17 helpers. sections(h) -> (head, [section strings], tail); apply(h, entries) with entries [{slide,old,new}];
shot(html_path, slides, outprefix) renders 1280x720 PNGs of the given 1-based slides."""
import re, json, sys
CSS_SRC = ('.src{font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;font-size:12.5px;line-height:1.25;font-weight:400;'
           'color:#8a8f98;opacity:1;letter-spacing:0;font-style:normal;white-space:normal}\n.dk .src{color:#9aa3b2}\n')
def sections(h):
    head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
    body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
    return head, [x for x in re.split(r'(?=<section class="slide)', body) if x], tail
def apply(h, entries):
    head, secs, tail = sections(h)
    for e in entries:
        k = e['slide'] - 1; c = secs[k].count(e['old']); assert c == 1, (e['slide'], c, e['old'][:60])
        secs[k] = secs[k].replace(e['old'], e['new'])
    if '.src{' not in head: head = head.replace('</style>', CSS_SRC + '</style>', 1)
    return head + ''.join(secs) + tail
def shot(path, slides, pre):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 772})
        pg.goto('file://' + path, wait_until='networkidle', timeout=180000)
        pg.add_style_tag(content='.nav{display:none!important}'); pg.evaluate("document.getElementById('stage').style.setProperty('--s', 1)")
        for k in slides:
            pg.evaluate(f"document.querySelectorAll('.slide').forEach((el,j)=>el.classList.toggle('on',j==={k-1}))"); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
            pg.locator('#stage').screenshot(path=f'{pre}_{k:02d}.png')
        b.close()
if __name__ == '__main__':
    # python deck_tools.py entries.json out.html [slide numbers to shoot ...]
    import os
    D = os.path.dirname(os.path.abspath(__file__))
    h = open(D + '/deck_v17_readonly.html', encoding='utf-8').read()
    out = apply(h, json.load(open(sys.argv[1], encoding='utf-8'))); open(sys.argv[2], 'w', encoding='utf-8').write(out)
    if len(sys.argv) > 3: shot(os.path.abspath(sys.argv[2]), [int(x) for x in sys.argv[3:]], sys.argv[2].rsplit('.', 1)[0])
    print('ok')
