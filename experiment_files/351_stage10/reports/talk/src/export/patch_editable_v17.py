"""2026-11-05: editable pptx v17 = v16 editable + 13 method pages drawn as NATIVE shapes (method_figs/method_lib.py primitives:
autoshapes, connectors with tailEnd arrows, freeform polylines, text boxes in Caveat / Patrick Hand; very light pink background fill
+ a locked group of grid lines at the back), each inserted right before its experiment's results (method_pages_v17.INSERT).
Page-number boxes of the old slides are renumbered; all speaker notes rewritten from notes_zh.json / slides.json (67).
usage: patch_editable_v17.py V16_PPTX OUT_PPTX"""
import copy, json, re, sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import method_pages_v17 as MP
from method_lib import pptx_render

src, out = Path(sys.argv[1]), Path(sys.argv[2])
prs = Presentation(src)
notes = json.loads((HERE / 'notes_zh.json').read_text()); meta = json.loads((HERE / 'slides.json').read_text())
assert len(prs.slides) == 54 and len(notes) == len(meta) == 67
old = list(prs.slides)
PX = prs.slide_width / 1280
PG_TOP = 6467475

def pg_boxes(sl, num):
    return [sh for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip() == str(num) and sh.top == PG_TOP]

tmpl = pg_boxes(old[3], 4); assert len(tmpl) == 1; tmpl = tmpl[0]

def set_pg(sh, k):
    r = sh.text_frame.paragraphs[0].runs; r[0].text = str(k)
    for x in r[1:]: x._r.getparent().remove(x._r)
    w = int(len(str(k)) * 7.6 * PX); sh.width = Emu(w); sh.left = Emu(int(1250 * PX) - w)

order = MP.new_order(54)
new_ids, stats = {}, {}
for kind, v in order:
    if kind != 'new': continue
    sl = prs.slides.add_slide(old[3].slide_layout)
    for ph in list(sl.placeholders): ph._element.getparent().remove(ph._element)
    stats[v] = pptx_render(sl, MP.ITEMS[v], prs.slide_width)
    el = copy.deepcopy(tmpl._element); sl.shapes._spTree.append(el)
    new_ids[v] = sl
# reorder
lst = prs.slides._sldIdLst; ids = list(lst)
id_of_old = {i + 1: ids[i] for i in range(54)}
id_of_new = {v: ids[54 + j] for j, v in enumerate([v for kind, v in order if kind == 'new'])}
for e in ids: lst.remove(e)
for kind, v in order: lst.append(id_of_old[v] if kind == 'old' else id_of_new[v])
slides = list(prs.slides); assert len(slides) == 67
# page numbers
renum = 0
for k, (kind, v) in enumerate(order, 1):
    sl = slides[k - 1]
    if kind == 'new':
        set_pg(pg_boxes(sl, 4)[0], k)
    else:
        for sh in pg_boxes(sl, v):
            set_pg(sh, k); renum += 1
# notes
for k, sl in enumerate(slides, 1):
    nt = notes[str(k)]; m = meta[k - 1]
    if m.get('method'): src_txt = '方法页（原生形状，2026-11-05 新增）'
    else: src_txt = f"deck 第 {m['deck']} 页（按源文件重建）" if m['kind'] == 'deck' else '合并 PPT 自身页面（按网页元素重建）'
    sl.notes_slide.notes_text_frame.text = f"第 {k} / {len(meta)} 页 · {src_txt} · " + ('【新写讲稿】' if nt['new'] else '按 deck 讲稿备注翻译（已按复核结果更新）') + '\n\n' + nt['text']
prs.save(out)
print('saved', out, len(slides), 'slides; renumbered page boxes', renum)
for k, (kind, v) in enumerate(order, 1):
    if kind == 'new': print(f'  slide {k:2d} {v:12s} leaf shapes {stats[v]["leaf"]}, groups {stats[v]["group"]}, grid lines {stats[v]["grid"]}')
