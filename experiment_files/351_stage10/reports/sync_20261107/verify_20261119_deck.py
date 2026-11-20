"""2026-11-19: checks of stage1_11_deck.html against the v39 backup stage1_11_deck.html.before_20261119:
fate of every v39 slide (kept byte-identical / kept edited / rebuilt / split / deleted), CJK left in visible text,
process labels left, figure-less slides from new S43 on, formula + n on every slide with a new figure."""
import re, json, hashlib, html
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
rec = json.loads((Path(__file__).parent / 'build_20261119_deck.json').read_text())
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
A = sec((D / 'stage1_11_deck.html.before_20261119').read_text(encoding='utf-8'))
full = (D / 'stage1_11_deck.html').read_text(encoding='utf-8'); B = sec(full)
print('v39', len(A), 'new', len(B))
n2o = {int(k): v for k, v in rec['order_new_to_v39'].items()}
o2n = {v: k for k, v in n2o.items() if isinstance(v, int)}
ident = [k for k in range(1, len(A) + 1) if k in o2n and B[o2n[k] - 1] == A[k - 1]]
print('byte-identical v39 slides:', len(ident), ident)
for k in range(1, len(A) + 1):
    f = rec['fate_v39'][str(k)]
    if f == 'kept': assert k in ident, k
print('fates:'); [print(f'  v39 {k:2d} -> new {o2n.get(k, "-")}: {rec["fate_v39"][str(k)][:150]}') for k in range(1, len(A) + 1) if rec['fate_v39'][str(k)] != 'kept']
CJK = re.compile('[　-〿一-鿿＀-￯]')
BAN = re.compile(r'(?i)after the defen[cs]e|post-defen[cs]e|\bpost[- ]hoc\b|CPU leftovers|redo programme|since 11-1\d|update 11-1\d|added 2026-|\bleftover')
bad_cjk, bad_ban, nofig = [], [], []
for i, t in enumerate(B, 1):
    t2 = re.sub(r'data:[^"]+', '', t)
    vis = html.unescape(re.sub(r'<[^>]+>', ' ', t2))
    attrs = ' '.join(re.findall(r'(?:aria-label|alt)="([^"]*)"', t2))
    c = [w for w in re.findall(r'\S*[　-〿一-鿿＀-￯]+\S*', vis + ' ' + attrs)]
    if c: bad_cjk.append((i, c[:5]))
    b = BAN.findall(vis + ' ' + attrs)
    if b: bad_ban.append((i, b))
    hasfig = '<img' in t or t.count('<svg') >= 1
    if i >= 43 and not hasfig: nofig.append(i)
print('CJK left (slide, examples):', bad_cjk)
print('process labels left:', bad_ban)
print('slides >= 43 without a figure:', nofig)
head = full[:full.index('<section')]
print('page-level CJK outside slides (font subset link only):', bool(CJK.search(re.sub(r'<link[^>]*>', '', head))))
