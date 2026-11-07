"""v20d three-part copy of export_deck_v20b_split.py (2026-11-07): PNG slides (no JPEG), PARTS env e.g. "1-27,28-55,56-82" -> names ..._part1of3_p1-27.pdf. Earlier docstring follows."""
"""v18 copy of export_deck.py (2026-11-05): Stage1-13 file names; NOTES_H env = notes page height; 〔…〕 source tags in notes rendered grey/small."""
"""Export the merged Stage 1-11 deck (merged/stage1_11_deck.html) to two PDFs:
  slides only : one 1280x720 page per slide
  with notes  : slide on top (1280x720), Chinese speaker notes below (notes_zh.json)
Slides are rendered by headless Chromium with the page's own web fonts (checked loaded before every capture)."""
import base64, html, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# usage: export_deck.py OUT [DECK_HTML] [LABEL] [--jpeg Q]
#   old usage (OUT only) is unchanged: DECK = ../merged/stage1_11_deck.html, files named v11, PNG slide images.
#   2026-11-02: optional deck path, version label and JPEG slide images (keeps each PDF under the 15 MB limit).
args = [a for a in sys.argv[1:]]; JPEG_Q = None
if '--jpeg' in args: k = args.index('--jpeg'); JPEG_Q = int(args[k + 1]); del args[k:k + 2]
HERE = Path(__file__).parent; OUT = Path(args[0]); OUT.mkdir(parents=True, exist_ok=True)
DECK = Path(args[1]) if len(args) > 1 else HERE.parent / 'merged/stage1_11_deck.html'
LABEL = args[2] if len(args) > 2 else 'v11'
SHOTS = HERE / 'shots'; SHOTS.mkdir(exist_ok=True)
notes = json.loads((HERE / 'notes_zh.json').read_text()); slides = json.loads((HERE / 'slides.json').read_text())
PENDING = '【待复核】'

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 772}, device_scale_factor=1.5)
    pg.goto(DECK.as_uri(), wait_until='networkidle', timeout=180000)
    pg.add_style_tag(content='.nav{display:none!important} .stage{box-shadow:none!important} body{background:#fff}')
    pg.evaluate('document.fonts.ready')
    fams = pg.evaluate("[...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family)")
    assert {'Caveat', 'Patrick Hand'} <= set(fams), fams
    n = pg.evaluate("document.querySelectorAll('.slide').length"); assert n == len(slides) == len(notes), (n, len(slides), len(notes))
    pg.evaluate("document.getElementById('stage').style.setProperty('--s', 1)")
    labels = []
    for i in range(n):
        pg.evaluate(f"document.querySelectorAll('.slide').forEach((el,k)=>el.classList.toggle('on',k==={i}))")
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
        st = pg.locator('#stage'); bb = st.bounding_box(); assert abs(bb['width'] - 1280) < 1 and abs(bb['height'] - 720) < 1, bb
        st.screenshot(path=str(SHOTS / f's{i + 1:02d}.png'))
        labels.append(pg.evaluate(f"(document.querySelectorAll('.slide')[{i}].querySelector('.tag')||{{}}).textContent||''"))
    print('captured', n, 'slides; fonts', sorted(set(fams)), flush=True)

    def img(k):
        if JPEG_Q is None: return 'data:image/png;base64,' + base64.b64encode((SHOTS / f's{k:02d}.png').read_bytes()).decode()
        import io; from PIL import Image
        buf = io.BytesIO(); Image.open(SHOTS / f's{k:02d}.png').convert('RGB').save(buf, 'JPEG', quality=JPEG_Q, optimize=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    import os
    PARTS = [tuple(int(x) for x in p.split('-')) for p in os.environ.get('PARTS', f'1-{n}').split(',')]
    for PI, (A, B) in enumerate(PARTS, 1):
        font = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap">'
        # ---- slides only
        pages = ''.join(f'<div class="pg"><img src="{img(k)}"></div>' for k in range(A, B + 1))
        doc = f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:1280px 720px;margin:0}}html,body{{margin:0}}.pg{{width:1280px;height:720px;break-after:page;overflow:hidden}}.pg img{{width:1280px;height:720px;display:block}}</style></head><body>{pages}</body></html>'
        (HERE / 'slides_only.html').write_text(doc); q = b.new_page(); q.goto((HERE / 'slides_only.html').as_uri(), wait_until='networkidle')
        q.pdf(path=str(OUT / f'Stage1-13_deck_{LABEL}_slides_part{PI}of{len(PARTS)}_p{A}-{B}.pdf'), width='1280px', height='720px', print_background=True, margin=dict(top='0', bottom='0', left='0', right='0'))
        # ---- with notes
        import os, re as _re
        H = int(os.environ.get('NOTES_H', '1150'))
        blocks = []
        for k in range(A, B + 1):
            nt = notes[str(k)]; s = slides[k - 1]
            src = f"deck 第 {s['deck']} 页" if s['kind'] == 'deck' else '合并 PPT 自身页面'
            tag = '<span class="new">新写讲稿</span>' if nt['new'] else '<span class="old">按 deck 讲稿备注翻译（已按复核结果更新）</span>'
            txt = html.escape(nt['text']).replace(html.escape(PENDING), '<b class="pend">待复核</b>'); txt = _re.sub(r'〔(.*?)〕', r'<span class="src">（\1）</span>', txt)
            blocks.append(f'<div class="pg"><img src="{img(k)}"><div class="nb"><div class="hd">第 {k} / {n} 页 · {(html.escape(labels[k - 1]) + " · ") if labels[k - 1] else ""}{src} {tag}</div><div class="tx">{txt}</div></div></div>')
        doc = f'''<!doctype html><html><head><meta charset="utf-8">{font}<style>
    @page{{size:1280px {H}px;margin:0}} html,body{{margin:0;background:#fff}}
    .pg{{width:1280px;height:{H}px;break-after:page;overflow:hidden;display:flex;flex-direction:column}}
    .pg img{{width:1280px;height:720px;display:block;border-bottom:2px solid #d5dae3}}
    .nb{{flex:1;padding:22px 56px 26px;font-family:"Noto Sans SC","Droid Sans Fallback",sans-serif;color:#1F2937;overflow:hidden}}
    .hd{{font-size:17px;color:#5B6474;margin-bottom:12px}} .tx{{font-size:21px;line-height:1.62}} .src{{font-size:14px;color:#8a8f98;line-height:1.35}}
    .new{{background:#FFF4D6;color:#8A4A10;border:1px solid #E0B85A;border-radius:4px;padding:1px 8px;margin-left:8px;font-weight:700}}
    .old{{color:#2F7D3B;margin-left:8px}} .pend{{background:#B42318;color:#fff;border-radius:4px;padding:0 6px;font-weight:700}}
    </style></head><body>{''.join(blocks)}</body></html>'''
        (HERE / 'with_notes.html').write_text(doc); q = b.new_page(viewport={'width': 1280, 'height': H}); q.goto((HERE / 'with_notes.html').as_uri(), wait_until='networkidle')
        q.evaluate('document.fonts.ready')
        over = q.evaluate("[...document.querySelectorAll('.nb')].map((e,i)=>[i+1, e.scrollHeight, e.clientHeight]).filter(x=>x[1]>x[2]+1)")
        print('notes fonts', q.evaluate("[...document.fonts].filter(f=>f.status=='loaded').map(f=>f.family).filter((v,i,a)=>a.indexOf(v)==i)"), '| overflowing notes:', over, flush=True)
        q.pdf(path=str(OUT / f'Stage1-13_deck_{LABEL}_with_notes_zh_part{PI}of{len(PARTS)}_p{A}-{B}.pdf'), width='1280px', height=f'{H}px', print_background=True, margin=dict(top='0', bottom='0', left='0', right='0'))
    b.close()
print('wrote', OUT)
