"""2026-11-12 r (priority build for the talk): v21 pptx as deck HTML (sync_20261107/apply_20261112r.py).
IN = pptx before round r, OUT = new pptx. Needs the export shots (talk/src/export/shots/sNN.png, 84-slide deck).
- 67, 68, 72 -> full-slide pictures of the new chart slides; new slides 73 (name-position probe), 74 (C24) inserted after 72 as pictures.
- 59: P1/P2 numbers (five-title mean, false_0 in parentheses); 82 (-> 84): C24 exception + chart picture (crop of the rendered slide);
  21: CI-method text; 65: header date patch over the table image + caption; every priority slide: one-line 怎么算 text box.
- notes of all changed / new slides = notes_zh.json (new numbering). usage: IN OUT"""
import sys, json, copy, shutil
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from PIL import Image
E = Path(__file__).parent; SH = E / 'shots'; FR = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/r_frag')
shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
PX = 12191695 / 1280
notes = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
ONE = json.load(open(FR / 'how_all.json', encoding='utf-8'))['one']
hits = []

def walk(shs):
    for sh in shs:
        yield sh
        if sh.shape_type == 6: yield from walk(sh.shapes)

def tb(slide, x, y, w, h, text, size=8, color=(0x4B, 0x53, 0x63), bold_prefix='怎么算：', fill=None):
    s = slide.shapes.add_textbox(Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    tf = s.text_frame; tf.word_wrap = True
    for m in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, m, 0)
    p = tf.paragraphs[0]
    if bold_prefix:
        r = p.add_run(); r.text = bold_prefix; r.font.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(0xB0, 0x56, 0x6F)
    r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.color.rgb = RGBColor(*color)
    if fill: s.fill.solid(); s.fill.fore_color.rgb = RGBColor(*fill)
    return s

def picture_slide(idx0, png):
    """replace content of slide idx0 (0-based) by a full-slide picture; keep the slide (and its notes part)"""
    sl = prs.slides[idx0]
    for sh in list(sl.shapes): sh._element.getparent().remove(sh._element)
    sl.shapes.add_picture(str(png), 0, 0, prs.slide_width, prs.slide_height)
    return sl

def set_notes(sl, text):
    tf = sl.notes_slide.notes_text_frame; tf.text = text

def sub_run(sl, a, b):
    n = 0
    for sh in walk(sl.shapes):
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if a in r.text: r.text = r.text.replace(a, b); n += 1
    return n

# ---- edits on existing slides (old numbering; before insertion)
S = lambda n: prs.slides[n - 1]
for a, b in [('name positions alone 0.61 → 0.85; ‘:’ alone ≤ 0.17', 'name positions alone 0.613 → 0.841 (false_0 0.61 → 0.85); ‘:’ ≤ 0.181 (0.17)'),
             ('(E1, P1; 1,186 papers)', '(E1, P1 5-title mean; 1,186 papers)'),
             ('at L48 (0.23); MLP takes over at L52–56 (0.18, 0.22)', 'at L48 (0.237; false_0 0.231); MLP takes over at L52–56 (0.181, 0.226; false_0 0.178, 0.224)'),
             ('(P2, 1,186 papers)', '(P2 5-title mean, p12f_mean5.csv)')]:
    k = sub_run(S(59), a, b); hits.append(('59', a[:25], k))
k = sub_run(S(82), '— a preference, not generation', '— a preference, not generation (C24 使用模型自生成文本，非 teacher forcing)'); hits.append(('82', 'C24', k))
k = sub_run(S(65), '(report v30, 2026-11-08)', '(report v41, 2026-11-12)'); hits.append(('65 caption', '', k))
pic = [sh for sh in S(65).shapes if sh.shape_type == 13 and sh.name.startswith('chart image')][0]
fx = lambda px: pic.left + px / 2760 * pic.width; fy = lambda py: pic.top + py / 2052 * pic.height
r = S(65).shapes.add_shape(1, Emu(int(fx(1890))), Emu(int(fy(12))), Emu(int(fx(2750) - fx(1890))), Emu(int(fy(78) - fy(12))))
r.fill.solid(); r.fill.fore_color.rgb = RGBColor(255, 255, 255); r.line.fill.background()
tf = r.text_frame; tf.text = 'Current result (report v41, 2026-11-12)'; run = tf.paragraphs[0].runs[0]; run.font.size = Pt(10); run.font.bold = True; run.font.color.rgb = RGBColor(0, 0, 0)
tb(S(21), 860, 588, 380, 100, 'CIs: Stage 10–12 published tables = paper-level bootstrap (papers resampled within bin × group); from Stage 13 on the team-cluster bootstrap (resample author teams) is the main method · 团队级补算进行中', 11, (0x22, 0x30, 0x4A), bold_prefix='')
POS = {59: (70, 640, 520), 6: (70, 642, 480), 20: (880, 575, 350), 21: (70, 672, 690), 35: (412, 234, 400), 46: (70, 683, 950),
       23: (70, 664, 1140), 44: (70, 664, 1140), 45: (70, 664, 1140), 49: (70, 664, 1140), 65: (70, 201, 1140), 78: (70, 655, 1140)}
for n, (x, y, w) in POS.items(): tb(S(n), x, y, w, 30, ONE[str(n)], 8)
# 82: chart picture crop from the rendered slide 84
im = Image.open(SH / 's84.png'); sc = im.size[0] / 1280
crop = im.crop((int(130 * sc), int(560 * sc), int(1042 * sc), int(712 * sc))); cp = E / 'shots/r_s84_chart.png'; crop.save(cp)
S(82).shapes.add_picture(str(cp), Emu(int(130 * PX)), Emu(int(560 * PX)), Emu(int(912 * PX)), Emu(int(152 * PX)))
# chart slides as pictures
for n in (67, 68, 72): picture_slide(n - 1, SH / f's{n:02d}.png')
# insert two new slides after 72
lay = prs.slides[66].slide_layout
new = []
for k in (73, 74):
    sl = prs.slides.add_slide(lay)
    for sh in list(sl.shapes): sh._element.getparent().remove(sh._element)
    sl.shapes.add_picture(str(SH / f's{k}.png'), 0, 0, prs.slide_width, prs.slide_height); new.append(sl)
lst = prs.slides._sldIdLst; ids = list(lst)
for el in ids[-2:]: lst.remove(el)
for j, el in enumerate(ids[-2:]): lst.insert(72 + j, el)
assert len(prs.slides) == 84
# static page-number text boxes on slides after the insertion: old n -> n + 2
pn = []
for k in range(75, 85):
    for sh in prs.slides[k - 1].shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == str(k - 2):
            for r in sh.text_frame.paragraphs[0].runs: r.text = ''
            sh.text_frame.paragraphs[0].runs[0].text = str(k); pn.append(k); break
hits.append(('page numbers', pn, len(pn)))
# notes for changed + new slides (new numbering)
old = json.loads((E / 'notes_zh.json.before_20261112r').read_text(encoding='utf-8')); nn = []
for k in range(1, 85):
    ok = None if k in (73, 74) else (k - 2 if k > 74 else k)
    if ok is None or notes[str(k)]['text'] != old[str(ok)]['text']:
        set_notes(prs.slides[k - 1], notes[str(k)]['text']); nn.append(k)
prs.save(sys.argv[2]); print('hits', hits, '; notes set', nn, '; slides', len(prs.slides))
