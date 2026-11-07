"""v16 -> v20 page map (copy of page_map_v16_v19.py) (2026-11-05): writes reports/talk/v16_to_v20_page_map.{md,csv}."""
import json, re, sys, csv
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import method_pages_v17 as MP, deck_v20_new as N
from pptx import Presentation
o17 = MP.new_order(54)                                   # v17 pos -> ('old', v16) | ('new', method key)
o18 = [tuple(x) for x in json.loads((HERE / 'v20_order.json').read_text())]
meta = json.loads((HERE / 'slides.json').read_text())
talk = Presentation(HERE / 'v18_inputs' / 'talk_v18.pptx')
def talk_title(n):
    for sh in talk.slides[n - 1].shapes:
        if sh.has_text_frame and sh.name == 'TextBox 2': return sh.text_frame.text.split('\n')[0]
    return ''
_h = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html').read_text(encoding='utf-8')
_secs = [x for x in re.split(r'(?=<section class="slide)', _h.split('\n</div>\n<nav', 1)[0]) if x.startswith('<section class="slide')]
assert len(_secs) == len(meta), (len(_secs), len(meta))
def html_title(k):
    s = _secs[k - 1]
    m = re.search(r'<h2[^>]*>(.*?)</h2>', s, re.S) or re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    if m: t = m.group(1)
    else:
        m = re.search(r'aria-label="([^"]*)"', s); t = m.group(1) if m else ''
    t = re.sub(r'<span class="src">.*?</span>', '', t, flags=re.S); t = re.sub(r'<br\s*/?>', ' ', t); t = re.sub(r'<[^>]+>', '', t)
    tag = re.search(r'<span class="tag[^"]*"[^>]*>(.*?)</span>', s, re.S)
    tag = re.sub(r'<[^>]+>', '', tag.group(1)) if tag else ''
    return (tag + ' — ' if tag else '') + re.sub(r'\s+', ' ', t).strip()
def title(k):
    m = meta[k - 1]
    if m['kind'] == 'deck': return talk_title(m['deck'])
    if m.get('new18'): return next(s['title'] for s in N.SLIDES if s['key'] == m['new18'])
    return html_title(k)
v17_of_v16 = {v: i for i, (kind, v) in enumerate(o17, 1) if kind == 'old'}
v18_of_v17 = {v: i for i, (kind, v) in enumerate(o18, 1) if kind == 'old'}
rows = []
for a in range(1, 55):
    b = v18_of_v17.get(v17_of_v16[a]); rows.append((a, b if b else 'removed', title(b) if b else ''))
new = []
for k, (kind, v) in enumerate(o18, 1):
    if kind == 'new': new.append((k, {'alltok': 'new in v20', 'st8cpu': 'new in v20', 'pdlim': 'new in v20', 'pd5': 'new in v18, rewritten in v20 (redo programme)', 'x2': 'new in v19', 'pd1': 'new in v19 (replaces v18 "plan and status")', 'pd2': 'new in v19', 'pd3': 'new in v19', 'pd3b': 'new in v19', 'pd0': 'new in v18, text updated in v19', 'x6x7_': ''}.get(v, 'new in v18'), title(k)))
    else:
        k17 = o17[v - 1]
        if k17[0] == 'new': new.append((k, f'new in v17 (method page {k17[1]})', title(k)))
OUT = HERE.parent.parent
with open(OUT / 'v16_to_v20_page_map.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['v16', 'v20', 'title (v20)'])
    w.writerows(rows); w.writerow([]); w.writerow(['v20', 'status', 'title'])
    w.writerows(new)
md = ['# Deck v16 → v20 page map (2026-11-05)', '', 'v20 = 82 slides. No v16 slide was removed. Titles are the v20 slide titles (first line).', '',
      '| v16 | v20 | title (v20) |', '|---|---|---|'] + [f'| {a} | {b} | {t} |' for a, b, t in rows] + \
     ['', '## Slides new since v16 (v17 method pages + v18–v20 additions)', '', '| v20 | status | title |', '|---|---|---|'] + [f'| {k} | {s} | {t} |' for k, s, t in new]
(OUT / 'v16_to_v20_page_map.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
print('\n'.join(md))
