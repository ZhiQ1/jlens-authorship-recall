"""2026-11-07 copy of patch_editable_v20b.py: slide 64 uses the English hypothesis table (Stage13_hypotheses_table_v28_en_tableonly.png); notes from the 2026-11-07 notes_zh.json. Then pptx_text_fix_20261107.py applies the slide-text fixes of sync_20261107/apply_20261107.py."""
"""2026-11-06 b copy of patch_editable_v20.py: only change = import deck_v20b_new (batch-1 results on slides 72, 75, 81; notes from the updated notes_zh.json)."""
"""v20 copy of patch_editable_v19.py (2026-11-06): deck_v20_new, v20_order.json, talk_v20.pptx pages, slide 23 caveat pointer, slide 52 C-1 line."""
"""v19 copy of patch_editable_v18.py (2026-11-05 evening): deck_v19_new slides, v19_order.json, slide 26 re-rendered with real numbers, slide 64 hypotheses table v28 + X2 line. Original docstring follows."""
"""2026-11-05 editable pptx v18 from the v17 editable pptx (as re-exported with the schematic group-comparison method page).
- image-type pages (slides.json kind 'deck'): content replaced by the v18 talk build pages (native shapes, with grey source runs + probe caveat)
- HTML pages: each html_tags entry becomes a small grey run inserted after the matching text (paragraph search on the plain text);
  method SVG pages: their footnote line becomes a small grey text box at the bottom
- probe method page: caveat text box; cover: pointer line
- new slides (deck_v18_new.py) as native text boxes / pictures / table on a copy of the v17 page-64 background and title style
- order = v18_order.json; page-number boxes renumbered; speaker notes from notes_zh.json (67 + new)
usage: patch_editable_v18.py V17_PPTX TALK_V18_PPTX OUT_PPTX"""
import copy, io, json, re, sys, html as H
from pathlib import Path
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import deck_v20b_new as N
src, talkp, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
prs = Presentation(src); talk = Presentation(talkp)
order = [tuple(x) for x in json.loads((HERE / 'v20_order.json').read_text())]
notes = json.loads((HERE / 'notes_zh.json').read_text()); meta = json.loads((HERE / 'slides.json').read_text())
meta17 = json.loads((HERE / 'slides.before_20261105b.json').read_text())
tags = json.loads((HERE / 'v18_inputs' / 'html_tags.json').read_text(encoding='utf-8'))
assert len(prs.slides) == 67 and len(talk.slides) == 27 and len(order) == len(notes) == len(meta)
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'; R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
E = lambda px: Emu(int(round(px * 9525)))
GREY = RGBColor(0x8A, 0x8F, 0x98); INK = RGBColor(0x22, 0x30, 0x4A); BLUE = RGBColor(0x3C, 0x78, 0xB4)
old = list(prs.slides)

def relink(el, src_part, dst_slide):
    for blip in el.iter(f'{A}blip'):
        rid = blip.get(f'{R}embed'); blob = src_part.related_part(rid).blob
        _, nrid = dst_slide.part.get_or_add_image_part(io.BytesIO(blob)); blip.set(f'{R}embed', nrid)

def append(dst, el):
    tree = dst.shapes._spTree; ext = tree.find('{http://schemas.openxmlformats.org/presentationml/2006/main}extLst')
    (ext.addprevious(el) if ext is not None else tree.append(el))

def replace_content(dst, srcs):
    tree = dst.shapes._spTree
    for el in list(tree)[2:]:
        if not el.tag.endswith('extLst'): tree.remove(el)
    for rid in [r for r, rel in list(dst.part.rels.items()) if rel.reltype.endswith('/image')]: dst.part.drop_rel(rid)
    for el in list(srcs.shapes._spTree)[2:]:
        if el.tag.endswith('extLst'): continue
        n = copy.deepcopy(el); relink(n, srcs.part, dst); append(dst, n)

# 1. image-type pages
nrep = 0
for i, m in enumerate(meta17):
    if m['kind'] == 'deck': replace_content(old[i], talk.slides[m['deck'] - 1]); nrep += 1

# 2. tags on HTML pages
def plain(x):
    x = re.sub(r'<span class="src">.*?</span>', '', x, flags=re.S); x = re.sub(r'<[^>]+>', '', x); return H.unescape(x).replace('​', '')
def norm(x): return re.sub(r'\s+', ' ', x.replace('​', '')).strip()
def add_tag_run(para, after_char, text, size=9):
    """split runs of para so that a grey run with text sits after plain-char offset after_char"""
    pos = 0
    for r in list(para.runs):
        L = len(r.text)
        if pos + L >= after_char:
            cut = after_char - pos; rest = r.text[cut:]; r.text = r.text[:cut]
            new = copy.deepcopy(r._r); r._r.addnext(new)
            from pptx.text.text import _Run
            nr = _Run(new, para); nr.text = ' ' + text; nr.font.size = Pt(size); nr.font.bold = False; nr.font.italic = False
            nr.font.color.rgb = GREY
            if rest:
                rr = copy.deepcopy(r._r); new.addnext(rr); _Run(rr, para).text = rest
            return True
        pos += L
    return False
miss, hit, foot = [], 0, 0
heads = {}
grown = set()
# number fixes made by the html helper (text changed on the web page too)
for sl_no, o, n in [(42, '+0.228]', '+0.229]')]:
    c = 0
    for sh in old[sl_no - 1].shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if o in r.text: r.text = r.text.replace(o, n); c += 1
    assert c == 1, (sl_no, o, c)
for e in tags:
    sl = old[e['slide'] - 1]
    if '<text' in e['new']:   # method SVG footnote
        lines = [H.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<text[^>]*>.*?</text>', e['new'], flags=re.S)]
        lines = [x for x in lines if x]
        tb = sl.shapes.add_textbox(E(70), E(704 - 15 * len(lines)), E(1120), E(15 * len(lines) + 6)); tf = tb.text_frame; tf.word_wrap = True
        for li, t in enumerate(lines):
            p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
            r = p.add_run(); r.text = t; r.font.size = Pt(8.5); r.font.color.rgb = GREY; r.font.name = 'Noto Sans SC'
        foot += 1
        continue
    for m in re.finditer(r'<span class="src">(.*?)</span>', e['new'], flags=re.S):
        tagtxt = H.unescape(re.sub(r'<[^>]+>', '', m.group(1))).replace('​', '')
        before = norm(plain(e['new'][:m.start()]))
        key = before[-18:] if len(before) >= 18 else before
        if not key:   # tag in an empty header cell
            for sh in sl.shapes:
                if getattr(sh, 'has_table', False) and sh.has_table:
                    c0 = sh.table.cell(0, 0)
                    if not c0.text_frame.text.strip():
                        r = c0.text_frame.paragraphs[0].add_run(); r.text = tagtxt; r.font.size = Pt(8); r.font.color.rgb = GREY; hit += 1; break
            else:
                miss.append((e['slide'], key, tagtxt[:50]))
            continue
        done = False
        for sh in sl.shapes:
            frames = []
            if sh.has_text_frame: frames.append((sh.text_frame, 'shape'))
            if getattr(sh, 'has_table', False) and sh.has_table:
                frames += [(c.text_frame, 'head' if ri == 0 else 'cell') for ri, row in enumerate(sh.table.rows) for c in row.cells]
            for tf, where in frames:
                for p in tf.paragraphs:
                    full = ''.join(r.text for r in p.runs); nf = norm(full)
                    if key and key in nf:
                        # map normalised offset back to raw offset (collapse whitespace consistently)
                        idx = nf.index(key) + len(key); raw = 0; k = 0
                        s2 = re.sub(r'\s+', ' ', full).lstrip()
                        lead = len(full) - len(full.lstrip())
                        # walk raw string counting normalised chars
                        cnt = 0; j = 0; prev_space = False; rawstr = full
                        for j, ch in enumerate(rawstr):
                            if j < lead: continue
                            if ch.isspace():
                                if prev_space: continue
                                prev_space = True
                            else: prev_space = False
                            cnt += 1
                            if cnt == idx: break
                        if where == 'head':      # header cells: tag goes to a slide footnote instead (keeps the table height)
                            heads.setdefault(e['slide'], []).append(nf.split()[-1] + ' ' + tagtxt); done = True; break
                        done = add_tag_run(p, j + 1, tagtxt)
                        if done and where == 'shape': grown.add((e['slide'], sh.shape_id))
                        break
                if done: break
            if done: break
        if done: hit += 1
        else: miss.append((e['slide'], key, tagtxt[:50]))
# boxes that got longer: if the text no longer fits up to the boundary, wrap it and push the shapes below it down
def est_px(p):
    w = 0
    for r in p.runs:
        sz = (r.font.size.pt if r.font.size else 16) * 96 / 72
        w += len(r.text) * sz * (0.47 if (r.font.size and r.font.size.pt <= 9.5) else 0.43)
    return w
nfoot = 0; fn = {}
for sl_no, sid in sorted(grown):
    sl = old[sl_no - 1]; sh = next(x for x in sl.shapes if x.shape_id == sid); tf = sh.text_frame
    split = any(x.has_text_frame and x.text_frame.text.strip().startswith('What scale showed') for x in sl.shapes)
    bound = 620 if (split and sh.left < E(600)) else 1240
    x0 = sh.left / 9525
    lim = (sh.width / 9525) if tf.word_wrap else (bound - x0)
    for p in tf.paragraphs:
        if est_px(p) + 16 <= lim * (3 if tf.word_wrap else 1): continue
        for r in p.runs:     # tag runs of this line -> numbered footnote markers
            if r.font.size and r.font.size.pt <= 9.5 and r.text.strip().startswith('('):
                lst = fn.setdefault(sl_no, []); lst.append(r.text.strip()); r.text = f' [{len(lst)}]'; nfoot += 1
for sl_no, items in heads.items():
    fn.setdefault(sl_no, []).append('TABLE ' + ' · '.join(items))
for sl_no, items in fn.items():
    sl = old[sl_no - 1]; n = len(items)
    tb = sl.shapes.add_textbox(E(70), E(700 - 13 * n), E(1100), E(13 * n + 4)); tf = tb.text_frame; tf.word_wrap = True
    for i, t in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = ('Table columns: ' + t[6:]) if t.startswith('TABLE ') else f'[{i + 1}] {t}'; r.font.size = Pt(8); r.font.color.rgb = GREY; r.font.name = 'Noto Sans SC'
print('long-line tags moved to slide footnotes', nfoot, 'on slides', sorted(fn))
print('pptx tags: inserted', hit, 'svg footnotes', foot, 'not placed', len(miss))
for x in miss: print('  MISS', x)

# 2b. corrections from the live published deck (same as edit_deck_v18.py 1b)
def run_sub(sl, o, n):
    c = 0
    for sh in sl.shapes:
        frames = [sh.text_frame] if sh.has_text_frame else []
        if getattr(sh, 'has_table', False) and sh.has_table: frames += [c_.text_frame for row in sh.table.rows for c_ in row.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    if r.text == o or (o in r.text and len(o) > 12): r.text = r.text.replace(o, n); c += 1
    assert c == 1, (o, c)
run_sub(old[13], ' [4.7, 13.9], 35/50 papers positive', ' [4.8, 14.0], 35/50 papers positive')
run_sub(old[16], 'Stage 8D frozen estimates, 95% CI (pp)', 'Stage 8D L56 estimates (PROTOCOL.md), 95% CI (pp)')
run_sub(old[16], 'RQ1 title', 'RQ1 title, L56'); run_sub(old[16], 'RQ2 A−B', 'RQ2 A−B, L56')
run_sub(old[17], 'Scripts not yet archived: ', 'Original scripts missing; recomputed from raw logits (30 Oct), same estimates: ')
run_sub(old[17], 'not a completed experiment', 'post-hoc only')
sh18 = next(sh for sh in old[17].shapes if sh.has_text_frame and 'Original scripts missing' in sh.text_frame.text)
sh18.text_frame.word_wrap = True; sh18.width = E(1235) - sh18.left; sh18.height = sh18.height * 2
# user wording decisions (2026-11-05 afternoon)
def run_sub_any(sl, o, n):
    c = 0
    for sh in sl.shapes:
        frames = [sh.text_frame] if sh.has_text_frame else []
        if getattr(sh, 'has_table', False) and sh.has_table: frames += [c_.text_frame for row in sh.table.rows for c_ in row.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    if o in r.text: r.text = r.text.replace(o, n); c += 1
    assert c == 1, (o, c)
run_sub_any(old[57], '0.83 at L48', '0.82 at L48')
n29 = next(sh for sh in old[28].shapes if sh.has_text_frame and sh.text_frame.text.startswith('Line A: from')); n29.top = n29.top - E(40)
run_sub_any(old[28], '≈0 in middle layers', '≈0 at L24–L40, slightly negative at L48 (−0.04 to −0.05)')
run_sub_any(old[57], '≈ 0 in middle layers', '≈ 0 at L24–L40, slightly negative at L48 (−0.04 to −0.05)')
run_sub_any(old[59], '≈0 middle; R1', '≈0 at L24–L40, slightly negative at L48; R1')
run_sub_any(old[59], ', ≈0 middle', ', ≈0 at L24–L40, slightly negative at L48 (−0.04 to −0.05)')
tbl = next(sh for sh in old[16].shapes if getattr(sh, 'has_table', False) and sh.has_table)
tr = tbl.table._tbl.tr_lst[2]; ntr = copy.deepcopy(tr); tr.addnext(ntr)
from pptx.table import _Row
row = _Row(ntr, tbl.table)
for j, txt in enumerate(['RQ2 A−B, 7-layer (frozen primary)', '+2.41 pp', '[+0.91, +4.00]']):
    tf = row.cells[j].text_frame; ps = tf.paragraphs
    runs = ps[0].runs
    runs[0].text = txt
    for r in runs[1:]: r.text = ' (100 pairs; s8_endpoints.csv)' if j == 0 else ''
tbl.height = tbl.height + row.height
cb = next(sh for sh in old[16].shapes if sh.has_text_frame and sh.text_frame.text.startswith('Citation bands'))
cb.top = E(486)

# keep wrapped text boxes inside the slide (tags made some lines longer)
nfit = 0
for sl in old:
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.word_wrap and sh.left + sh.width > E(1235):
            sh.width = E(1235) - sh.left; nfit += 1
print('boxes fitted to slide width', nfit)

n3 = next(sh for sh in old[2].shapes if sh.has_text_frame and sh.text_frame.text.startswith('What changed in the design'))
n3.top = n3.top - E(26); n3.height = n3.height + E(26)
# 3. probe caveat (v17 slide 23) and cover pointer
def textbox(sl, x, y, w, h, text, size, color=INK, font='Patrick Hand', align=None, bold=False):
    tb = sl.shapes.add_textbox(E(x), E(y), E(w), E(h)); tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    if align: p.alignment = align
    r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.color.rgb = color; r.font.name = font; r.font.bold = bold
    return tb
textbox(old[22], 560, 96, 650, 26, '⚠ E4b scores only the first name token (mostly an initial) · all tokens by role: see the addendum-9 slide (surname first token L40 +0.071; 1,395 papers)', 11,
        RGBColor(0xB5, 0x47, 0x08), align=PP_ALIGN.RIGHT)
hitc = 0
for sh in old[0].shapes:
    if sh.has_text_frame:
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.text.strip() == 'Stages 10–11': r.text = r.text.replace('Stages 10–11', 'Stages 10–13 · post-defence additions (2026-11-05) at the end'); hitc += 1
print('cover label replaced', hitc)

textbox(old[51], 700, 455, 520, 90, 'With a title contrast (addendum 13 C-1): holds at the output (+0.244) and at L62 (+0.278 logit, +0.317 public J-lens); the public J-lens 6-layer mean is not significant (+0.077 [−0.021, +0.180]) (20 pairs, rest of the name; c13_C1.md)', 12, RGBColor(0x9A, 0xDB, 0x8F))
# 3b. slide 26 (method "Group comparisons") re-rendered with real numbers; slide 64 picture + subtitle
sys.path.insert(0, '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/method_figs')
import method_slides as MS, build_method_figs as BMF
from method_lib import pptx_render
assert MS.COMPARE_REAL_NUMBERS
s26 = old[25]
tree = s26.shapes._spTree; pgbox = None
for sh in list(s26.shapes):
    if sh.has_text_frame and sh.text_frame.text.strip() == '26' and sh.top == 6467475: pgbox = sh; continue
    tree.remove(sh._element)
pptx_render(s26, next(it for k, t, it in BMF.slides() if k == 'compare'), prs.slide_width)
if pgbox is not None: tree.remove(pgbox._element); tree.append(pgbox._element)
textbox(s26, 70, 694, 1120, 20, 'P1 +0.200 [0.188, 0.213]: A − B, 3,417 / 2,148 papers; P2 co-authors +0.061, first author +0.031: C − A; dose 0.17 → 0.46: R0 by orders right; 391_groups/primary.csv, stage10_curves.csv', 8.5, GREY, 'Noto Sans SC')
s64 = old[63]
pic = next(sh for sh in s64.shapes if sh.name == 'chart image')
from PIL import Image as _I
HYP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/Stage13_hypotheses_table_v28_en_tableonly.png'
iw, ih = _I.open(HYP).size; w = pic.width; h = int(w * ih / iw)
newpic = s64.shapes.add_picture(HYP, pic.left, pic.top, w, min(h, pic.height)); newpic.name = 'chart image v28 en'
pic._element.getparent().remove(pic._element)
run_sub_any(s64, 'H3 (hidden author knowledge): insufficient evidence', 'H3 (hidden author knowledge): insufficient evidence · X2 (2026-11-05): H2 not supported; H3 passes by rule but the author subspace decodes nothing → still insufficient')
sub64 = next(sh for sh in s64.shapes if sh.has_text_frame and sh.text_frame.text.startswith('Paper facts')); sub64.text_frame.word_wrap = True; sub64.width = E(1140); sub64.height = sub64.height * 2
run_sub_any(s64, 'Hypotheses H1–H3 × readouts M1–M3 and current results (report, 2026-11-01)', 'Hypotheses H1–H3 × readouts M1–M3 and current results (report v28, 2026-11-05)')

# 4. new slides
T64 = old[63]
def find(sl, pred):
    for sh in sl.shapes:
        if pred(sh): return sh
    raise KeyError
TPL = {'bg': find(T64, lambda s: s.name == 'background'), 'tag': find(T64, lambda s: s.name.startswith('Rounded Rectangle')),
       'h2': find(T64, lambda s: s.has_text_frame and s.text_frame.text.startswith('Stage 12–13: what')),
       'sub': find(T64, lambda s: s.has_text_frame and s.text_frame.text.startswith('Paper facts')),
       'pg': find(T64, lambda s: s.has_text_frame and s.text_frame.text.strip() == '64')}
def clone(sl, key, text=None, x=None, y=None, w=None, h=None, part=None):
    el = copy.deepcopy(TPL[key]._element); relink(el, T64.part, sl); append(sl, el); sh = sl.shapes[-1]
    if x is not None: sh.left, sh.top, sh.width, sh.height = E(x), E(y), E(w), E(h)
    if text is not None:
        tf = sh.text_frame; ps = tf.paragraphs
        for p in ps[1:]: p._p.getparent().remove(p._p)
        runs = ps[0].runs
        for r in runs[1:]: r._r.getparent().remove(r._r)
        runs[0].text = text
    return sh
def bullets(sl, x, y, w, h, items, size=16, bullet=True):
    tb = sl.shapes.add_textbox(E(x), E(y), E(w), E(h)); tf = tb.text_frame; tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    for i, segs in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.space_after = Pt(7)
        if bullet:
            r = p.add_run(); r.text = '•  '; r.font.size = Pt(size); r.font.name = 'Patrick Hand'; r.font.color.rgb = INK
        for k, t in segs:
            r = p.add_run(); r.text = (' ' + t) if k == 's' else t
            r.font.name = 'Noto Sans SC' if k == 's' else 'Patrick Hand'
            r.font.size = Pt(9) if k == 's' else Pt(size); r.font.bold = (k == 'b'); r.font.color.rgb = GREY if k == 's' else INK
    return tb
def picture(sl, path, x, y, w):
    from PIL import Image
    iw, ih = Image.open(path).size; h = w * ih / iw
    sl.shapes.add_picture(str(path), E(x), E(y), E(w), E(h)); return h
new_slides = {}
for sp in N.SLIDES:
    sl = prs.slides.add_slide(T64.slide_layout)
    for ph in list(sl.placeholders): ph._element.getparent().remove(ph._element)
    clone(sl, 'bg')
    t = clone(sl, 'tag', sp['tag']); t.width = E(max(110, 9.5 * len(sp['tag']) + 24)); t.left = E(1254 - max(110, 9.5 * len(sp['tag']) + 24))
    if sp.get('kind') == 'divider':
        clone(sl, 'h2', sp['title'], 70, 160, 1140, 90); clone(sl, 'sub', sp['sub'], 70, 260, 1140, 40)
        bullets(sl, 70, 330, 1140, 300, sp['left'], 18, bullet=False)
    else:
        clone(sl, 'h2', sp['title'], 70, 40, 1060, 70); clone(sl, 'sub', sp['sub'], 70, 108, 1140, 50)
        y0 = 168
        if sp.get('left'):
            wl = 1140 - (sp['img_w'] + 22 if sp.get('img') else (322 if sp.get('note') else 0))
            bullets(sl, 70, y0, wl, 500, sp['left'])
            if sp.get('img'):
                hh = picture(sl, sp['img'], 70 + wl + 22, y0, sp['img_w'])
                textbox(sl, 70 + wl + 22, y0 + hh + 4, sp['img_w'], 40, sp['cap'], 9, GREY, 'Noto Sans SC')
            elif sp.get('note'):
                nb = sl.shapes.add_shape(1, E(70 + wl + 22), E(y0 + 20), E(300), E(230)); nb.fill.solid(); nb.fill.fore_color.rgb = RGBColor(0xF2, 0xE3, 0xA6)
                nb.line.fill.background(); nb.rotation = 1.2; tf = nb.text_frame; tf.word_wrap = True
                p = tf.paragraphs[0]; r = p.add_run(); r.text = sp['note'][0]; r.font.bold = True; r.font.size = Pt(15); r.font.name = 'Patrick Hand'; r.font.color.rgb = RGBColor(0x2B, 0x2A, 0x26)
                p2 = tf.add_paragraph(); r = p2.add_run(); r.text = sp['note'][1]; r.font.size = Pt(13.5); r.font.name = 'Patrick Hand'; r.font.color.rgb = RGBColor(0x2B, 0x2A, 0x26)
        elif sp.get('img'):
            hh = picture(sl, sp['img'], (1280 - sp['img_w']) / 2, y0, sp['img_w'])
            textbox(sl, (1280 - sp['img_w']) / 2, y0 + hh + 4, sp['img_w'], 30, sp['cap'], 9, GREY, 'Noto Sans SC'); y0 += hh + 30
        elif sp.get('table'):
            hd, rows = sp['table']
            gt = sl.shapes.add_table(len(rows) + 1, len(hd), E(70), E(y0), E(1140), E(34 * (len(rows) + 1))).table
            for j, c in enumerate(hd): gt.cell(0, j).text = c
            for i, r_ in enumerate(rows, 1):
                for j, c in enumerate(r_): gt.cell(i, j).text = c
            for row in gt.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs:
                        for r in p.runs: r.font.size = Pt(11); r.font.name = 'Patrick Hand'
            y0 += 34 * (len(rows) + 1) + 10
        if sp.get('bottom'):
            bullets(sl, 70, max(y0, 560) if not sp.get('table') else y0, 1140, 120, sp['bottom'], 13.5, bullet=False)
    clone(sl, 'pg', '0'); new_slides[sp['key']] = sl

# 5. reorder, page numbers, notes
lst = prs.slides._sldIdLst; ids = list(lst); n_old = 67
id_old = {i + 1: ids[i] for i in range(n_old)}
id_new = {sp['key']: ids[n_old + j] for j, sp in enumerate(N.SLIDES)}
for e in ids: lst.remove(e)
for kind, v in order: lst.append(id_old[v] if kind == 'old' else id_new[v])
slides = list(prs.slides); assert len(slides) == len(order)
PG_TOP = 6467475
def set_pg(sh, k):
    r = sh.text_frame.paragraphs[0].runs; r[0].text = str(k)
    for x in r[1:]: x._r.getparent().remove(x._r)
    w = int(len(str(k)) * 7.6 * 9525); sh.width = Emu(w); sh.left = Emu(int(1250 * 9525) - w)
ren = 0
for k, (kind, v) in enumerate(order, 1):
    sl = slides[k - 1]
    want = str(v) if kind == 'old' else '0'
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == want and sh.top == PG_TOP: set_pg(sh, k); ren += 1; break
for k, sl in enumerate(slides, 1):
    nt = notes[str(k)]; m = meta[k - 1]
    if m.get('new18'): s_txt = 'v18 新增页（原生形状，2026-11-05）'
    elif m.get('method'): s_txt = '方法页（原生形状）'
    else: s_txt = f"deck 第 {m['deck']} 页（按 v18 源文件重建）" if m['kind'] == 'deck' else '合并 PPT 自身页面（按网页元素重建）'
    sl.notes_slide.notes_text_frame.text = f"第 {k} / {len(slides)} 页 · {s_txt} · " + ('【新写讲稿】' if nt['new'] else '按 deck 讲稿备注翻译（已按复核结果更新）') + '\n〔…〕内为数字出处。\n\n' + nt['text']
prs.save(out)
print('saved', out, len(slides), 'slides; image pages replaced', nrep, '; page boxes renumbered', ren)
