"""2026-11-02: editable pptx v14 from v11 (the DOM extractor edit/specs.json is not on the cluster, so build_editable.py cannot rerun).
- slides 30, 51(->53), 52(->54): replaced by the current deck/build.py pages 11, 14, 15 (native shapes, rebuilt by run_build into DECK_PPTX)
- slide 47: v12 bullet text + P1-done note
- new slides 51, 52 (Stage 12-13 table, X5 layer order): native text boxes, card, note; background picture; geometry from the web deck DOM
- speaker notes: notes_zh.json (54)
usage: patch_editable_v14.py V11_PPTX DECK_PPTX DOM_DIR OUT_PPTX"""
import copy, io, json, sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
HERE = Path(__file__).parent
v11, deckp, dom, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
prs = Presentation(v11); deck = Presentation(deckp)
notes = json.loads((HERE / 'notes_zh.json').read_text()); meta = json.loads((HERE / 'slides.json').read_text())
boxes = json.loads((dom / 'dom_boxes.json').read_text())
assert len(prs.slides) == 52 and len(deck.slides) == 27 and len(notes) == 54 == len(meta)
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'; R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
E = lambda v: Emu(int(round(v * 9525)))

def relink(el, src_part, dst_slide):
    for blip in el.iter(f'{A}blip'):
        rid = blip.get(f'{R}embed'); blob = src_part.related_part(rid).blob
        _, nrid = dst_slide.part.get_or_add_image_part(io.BytesIO(blob)); blip.set(f'{R}embed', nrid)

def append(dst_slide, el):
    tree = dst_slide.shapes._spTree; ext = tree.find('{http://schemas.openxmlformats.org/presentationml/2006/main}extLst')
    (ext.addprevious(el) if ext is not None else tree.append(el))

def replace_content(dst, src):
    tree = dst.shapes._spTree
    for el in list(tree)[2:]:
        if not el.tag.endswith('extLst'): tree.remove(el)
    for rid in [r for r, rel in list(dst.part.rels.items()) if rel.reltype.endswith('/image')]: dst.part.drop_rel(rid)
    for el in list(src.shapes._spTree)[2:]:
        if el.tag.endswith('extLst'): continue
        n = copy.deepcopy(el); relink(n, src.part, dst); append(dst, n)

slides = list(prs.slides)
replace_content(slides[29], deck.slides[10]); replace_content(slides[50], deck.slides[13]); replace_content(slides[51], deck.slides[14])

def find(sl, pred):
    for sh in sl.shapes:
        if pred(sh): return sh
    raise KeyError
# slide 47 text
def sub_text(sl, old, new):
    hit = 0
    for sh in sl.shapes:
        if not sh.has_text_frame: continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if old in r.text: r.text = r.text.replace(old, new); hit += 1
    assert hit == 1, (old, hit)
sub_text(slides[46], 'Information travels title → tail tokens → name', 'Information travels title → name positions (L44–52), partly via tail tokens')
# the longer bullet wraps to 2 lines (as on the web page): grow its box, move the last bullet down; grow the note upward
s47 = slides[46]
bl = find(s47, lambda s: s.has_text_frame and s.text_frame.text.startswith('•  Information travels'))
bl.text_frame.word_wrap = True; bl.height = E(65)
last = find(s47, lambda s: s.has_text_frame and s.text_frame.text.startswith('•  Earlier co-authors')); last.top = last.top + E(32)
nt = find(s47, lambda s: s.has_text_frame and s.text_frame.text.startswith('Line D:')); nt.top = nt.top - E(30); nt.height = nt.height + E(30)
sub_text(slides[46], 'Stage 12 P1 now patches single tail positions.', 'Stage 12 P1 (done) patched single positions: the name positions carry the signal (+0.85 at L52), the colon alone little (+0.17).')

# templates: lt slide 49 (tag, h2, note, page number), dk slide 11 (card, caption), lt slide 48 (sub)
t49 = slides[48]; t11 = slides[10]; t48 = slides[47]
T = {'tag': find(t49, lambda s: s.name.startswith('Rounded Rectangle')), 'h2': find(t49, lambda s: s.has_text_frame and s.text_frame.text.startswith('What the small')),
     'note': find(t49, lambda s: s.has_text_frame and s.text_frame.text.startswith('Stage 10 answered')),
     'pg': find(t49, lambda s: s.has_text_frame and s.text_frame.text.strip() == '49'),
     'sub': find(t48, lambda s: s.has_text_frame and s.text_frame.text.startswith('Is the book on the shelf')),
     'card': find(t11, lambda s: s.name == 'Rectangle 8'), 'cap': find(t11, lambda s: s.has_text_frame and s.text_frame.text.startswith('Left: all 50'))}

def clone(sl, key, b, text=None, rot=0.0):
    el = copy.deepcopy(T[key]._element); append(sl, el); sh = sl.shapes[-1]
    sh.left, sh.top, sh.width, sh.height = E(b['x']), E(b['y']), E(b['w']), E(b['h']); sh.rotation = rot
    if text is not None:
        tf = sh.text_frame; ps = tf.paragraphs
        for p in ps[1:]: p._p.getparent().remove(p._p)
        runs = ps[0].runs
        for r in runs[1:]: r._r.getparent().remove(r._r)
        runs[0].text = text
    return sh

def rot_of(tf):
    import math, re
    if tf == 'none': return 0.0
    a, b = [float(x) for x in re.findall(r'[-\d.e]+', tf)[:2]]; return math.degrees(math.atan2(b, a)) % 360

BLUE = RGBColor(0x3C, 0x78, 0xB4)
def new_slide(k, bg_png, tag, h2, sub, img_path, cap=None, note=None):
    b = boxes[str(k)]; sl = prs.slides.add_slide(slides[48].slide_layout)
    for ph in list(sl.placeholders): ph._element.getparent().remove(ph._element)
    pic = sl.shapes.add_picture(str(bg_png), 0, 0, prs.slide_width, prs.slide_height); pic.name = 'background'
    t = clone(sl, 'tag', b['tag'], tag); t.line.color.rgb = BLUE; t.text_frame.paragraphs[0].runs[0].font.color.rgb = BLUE
    clone(sl, 'h2', b['h2'], h2); s = clone(sl, 'sub', b['sub'], sub)
    c = b['card']; r = rot_of(c['tf'])
    clone(sl, 'card', c, rot=r)
    ih = (c['w'] - 20) * img_h_w(img_path)
    p = sl.shapes.add_picture(str(img_path), E(c['x'] + 10), E(c['y'] + 10), E(c['w'] - 20), E(ih)); p.rotation = r; p.name = 'chart image'
    if cap: cb = dict(b['cap']); cb['y'] = c['y'] + 10 + ih + 3; cb['x'] = c['x'] + 12; clone(sl, 'cap', cb, cap, rot=r)
    if note:
        nb = b['note']; n = clone(sl, 'note', nb, rot=rot_of(nb['tf'])); tf = n.text_frame
        for pp in tf.paragraphs[1:]: pp._p.getparent().remove(pp._p)
        p0 = tf.paragraphs[0]
        for rr in list(p0.runs): rr._r.getparent().remove(rr._r)
        for i, para in enumerate(note):
            pp = p0 if i == 0 else tf.add_paragraph(); pp.space_after = Pt(9)
            for txt, bold, size in para:
                rr = pp.add_run(); rr.text = txt; f = rr.font; f.name = 'Patrick Hand'; f.size = Pt(size * 0.75); f.bold = bold
                f.color.rgb = RGBColor(0x8A, 0x4A, 0x10) if (bold and i > 0) else RGBColor(0x2B, 0x2A, 0x26)
        tf.auto_size = MSO_AUTO_SIZE.NONE
    clone(sl, 'pg', b['pg'], str(k))
    return sl

def img_h_w(path):
    from PIL import Image
    w, h = Image.open(path).size; return h / w

def flat(path):  # RGBA -> RGB on white (as in the web deck)
    from PIL import Image
    im = Image.open(path); o = dom / (Path(path).stem + '_rgb.png')
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); bg.save(o); return o
    return Path(path)

a = new_slide(51, dom / 'bg_51.png', 'Stage 12–13', 'Stage 12–13: what the middle layers hold',
              'Paper facts are readable at the title early (M2), but neither paper identity (H2) nor hidden author knowledge (H3) is established',
              flat(meta[50]['figs'][0]), cap='Hypotheses H1–H3 × readouts M1–M3 and current results (report, 2026-11-01)')
b = new_slide(52, dom / 'bg_52.png', 'Stage 13 · X5', 'Layer order (X5)',
              'Earliest layer at which each kind of information appears · existing results only, each source keeps its own rule',
              flat(meta[51]['figs'][0]),
              note=[[('Read early, carried, spoken late', True, 20)], [('≤L8–L16', True, 18), (': title facts and the first-author token', False, 18)],
                    [('L48–L52', True, 18), (': the paper signal reaches the post-title tail (patching R ≥ 0.5 at L48, ≥ 0.95 at L52; knockout costs nothing from L52)', False, 18)],
                    [('L53–L62', True, 18), (': names readable by lens', False, 18)]])
# order: new slides after slide 50
lst = prs.slides._sldIdLst; ids = list(lst); new = ids[-2:]
for e in new: lst.remove(e)
for j, e in enumerate(new): lst.insert(50 + j, e)
assert len(prs.slides) == 54
for k, sl in enumerate(prs.slides, 1):
    nt = notes[str(k)]; m = meta[k - 1]
    src_txt = f"deck 第 {m['deck']} 页（按源文件重建）" if m['kind'] == 'deck' else '合并 PPT 自身页面（按网页元素重建）'
    sl.notes_slide.notes_text_frame.text = f"第 {k} / {len(meta)} 页 · {src_txt} · " + ('【新写讲稿】' if nt['new'] else '按 deck 讲稿备注翻译（已按复核结果更新）') + '\n\n' + nt['text']
prs.save(out); print('saved', out, len(prs.slides), 'slides')
