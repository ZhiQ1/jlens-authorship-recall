"""2026-11-05 deck v17 = v16 + 13 method pages (inline SVG, very light pink grid), each right before its experiment's results.
Reads the backups *.before_20261105.* (made first if missing) and writes the deck HTML, slides.json, notes_zh.json."""
import json, re, shutil, sys
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import method_pages_v17 as MP
from method_lib import svg_of

DECK = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
BK = {DECK: DECK.with_name('stage1_11_deck.before_20261105.html'),
      HERE / 'slides.json': HERE / 'slides.before_20261105.json', HERE / 'notes_zh.json': HERE / 'notes_zh.before_20261105.json'}
for src, bk in BK.items():
    if not bk.exists(): shutil.copy2(src, bk)

h = BK[DECK].read_text()
head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 54
css = ('.mf{padding:0;background:#FFFBFB}\n.mf>svg{position:absolute;left:0;top:0;width:1280px;height:720px;display:block}\n'
       '.mf .pg{color:#22304A}\n')
assert '</style>' in head and '.mf{' not in head
head = head.replace('</style>', css + '</style>', 1)

def method_section(key):
    tag = MP.TAGS[key]
    svg = svg_of(MP.ITEMS[key], tag, uid='m' + key[:4])
    return (f'<section class="slide mf" aria-label="method: {tag}"><span class="tag" style="display:none">Method · {tag}</span>'
            f'{svg}<span class="pg"></span></section>\n')

order = MP.new_order(54)
out = []
for kind, v in order:
    out.append(secs[v - 1] if kind == 'old' else method_section(v))
DECK.write_text(head + ''.join(out) + tail)

meta = json.loads(BK[HERE / 'slides.json'].read_text()); notes = json.loads(BK[HERE / 'notes_zh.json'].read_text())
assert len(meta) == len(notes) == 54
nm, nn = [], {}
for k, (kind, v) in enumerate(order, 1):
    if kind == 'old':
        e = dict(meta[v - 1]); e['i'] = k; nm.append(e); nn[str(k)] = notes[str(v)]
    else:
        nm.append({'i': k, 'kind': 'html', 'text': f'Method · {MP.TAGS[v]} ' + MP.slide_text(v), 'figs': [], 'added': '2026-11-05', 'method': v})
        nn[str(k)] = {'new': True, 'text': MP.NOTES[v]}
(HERE / 'slides.json').write_text(json.dumps(nm, ensure_ascii=False, indent=1))
(HERE / 'notes_zh.json').write_text(json.dumps(nn, ensure_ascii=False, indent=1))
print('deck slides', len(out), '| method pages at', [k for k, (kind, v) in enumerate(order, 1) if kind == 'new'])
for k, (kind, v) in enumerate(order, 1):
    if kind == 'new': print(f'  {k:2d} {v}')
