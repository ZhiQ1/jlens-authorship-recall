"""2026-11-24 v22v head: copy of build22u_head.py with input v22u (169 slides), extraction ex71, deck v71."""
"""2026-11-23 v67 round: main pptx v22s -> v22t in the HTML v67 order (user-approved TOC 27_v67/toc_v67.md).
- every v22s slide kept (moved only); pptx-only and continuation slides stay after their HTML counterpart;
- 36 new HTML v67 pages built as native slides (same writer as build22s 'full native page');
- coverage lines added in v67 (Now asking / So / evidence tag) mirrored on the old slides where missing, placed in free space;
- 'slide N' in our own shapes: v22s -> v22t numbers; stale '<-'/'->' lead pointers reworded as in v67;
- user shapes and Chinese boxes never edited.
usage: build22t.py"""
import sys, json, re, copy, uuid, base64, io, os
ONLY = set(int(x) for x in os.environ.get('ONLY', '').split(',') if x)
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
import numpy as np
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'

D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
W9 = D + 'v22t_work/'; EX = W9 + os.environ.get('EXD', 'ex71/')
IN_, OUT = D + 'jlens_1113_pre_v22u.pptx', os.environ.get('OUT', D + 'jlens_1113_pre_v22v.pptx')
DECK = W9 + os.environ.get('DECKF', 'deck_v71.html')
AN = 'http://schemas.openxmlformats.org/drawingml/2006/main'; CJK = re.compile('[一-鿿]')
PFX = '[2026-11-24 v22v] '
prs = Presentation(IN_); SL = list(prs.slides); SW, SH = prs.slide_width, prs.slide_height; NS = len(SL); assert NS == 169
K = SW / 1280.0
PT = 0.5625
UPLOAD = Presentation(D + 'stage1-13 超长卷.pptx'); UPS = {su.slide_id: {x.shape_id for x in su.shapes} for su in UPLOAD.slides}
def user_ids(s): return UPS.get(s.slide_id, set())
LOG = {'adds': {}, 'full': {}, 'moved': [], 'shrunk': [], 'overlap': [], 'skipped_masks': [], 'edited': [], 'added': [], 'deleted': [], 'notes': {},
       'cov': [], 'cov_skip': [], 'not_fitted': [], 'leads': [], 'stale_user_refs': []}
ORIG = {k: {sh.shape_id for sh in SL[k - 1].shapes} for k in range(1, NS + 1)}
ORIG_EL = {k: [sh._element for sh in SL[k - 1].shapes] for k in range(1, NS + 1)}
REF = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
def remap(text, f):
    return REF.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(f(int(x.group(0)))), m.group(2)), text)
H67 = {}   # v67 page -> v22t first slide (filled after the order is built)
def h2s(n): return H67.get(n, n)

# ---------------- helpers: colours, xml ----------------
def _norm(c):
    if isinstance(c, str):
        m = re.match(r'#([0-9a-fA-F]{6})', c.strip())
        if m: return {'rgb': '#' + m.group(1), 'a': 1}
        LOG.setdefault('bad_colour', []).append(c[:40]); return None
    return c
def rgb(c):
    c = _norm(c)
    return RGBColor.from_string(c['rgb'][1:].upper()) if c else None
def set_alpha(fill_el_parent, a):
    if a is None or a >= 0.999: return
    clr = fill_el_parent.find('.//{%s}srgbClr' % AN)
    if clr is not None:
        al = etree.SubElement(clr, '{%s}alpha' % AN); al.set('val', str(int(a * 100000)))
def style_line(sh, c, w, dash=None, op=1, arrows=(False, False)):
    c = _norm(c)
    ln = sh.line
    if not c or w <= 0: ln.fill.background(); return
    ln.color.rgb = rgb(c); ln.width = Emu(int(max(w, 0.5) * K))
    lnx = sh._element.spPr.find('{%s}ln' % AN)
    if op < 0.999 or (c.get('a', 1) < 0.999): set_alpha(lnx, op * c.get('a', 1))
    if dash:
        pd = etree.SubElement(lnx, '{%s}prstDash' % AN); pd.set('val', 'dash' if float(re.findall(r'[\d.]+', dash)[0]) >= 4 else 'sysDash')
    for flag, tag in zip(arrows, ('headEnd', 'tailEnd')):
        if flag:
            e = etree.SubElement(lnx, '{%s}%s' % (AN, tag)); e.set('type', 'triangle'); e.set('w', 'med'); e.set('len', 'med')
def style_fill(sh, c, op=1):
    c = _norm(c)
    if not c: sh.fill.background(); return
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(c)
    a = op * c.get('a', 1)
    if a < 0.999: set_alpha(sh._element.spPr.find('{%s}solidFill' % AN), a)
def no_shadow(sh):
    sp = sh._element.spPr
    if sp.find('{%s}effectLst' % AN) is None: etree.SubElement(sp, '{%s}effectLst' % AN)
    st = sh._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
    if st is not None: st.getparent().remove(st)
def E(v): return Emu(int(round(v * K)))
def font_of(f):
    f = (f or '').lower()
    if 'caveat' in f.split(',')[0]: return 'Caveat'
    if 'patrick' in f: return 'Patrick Hand'
    if 'noto sans sc' in f or 'system-ui' in f or 'sans-serif' in f: return 'Noto Sans SC'
    if 'serif' in f or 'stix' in f: return 'DejaVu Serif'
    return 'Patrick Hand'
# ---------------- native item writers ----------------
def add_rect(s, it, dx=0, dy=0, sc=1.0, cx=0, cy=0):
    x, y, w, h = cx + (it['x'] - cx) * sc + dx, cy + (it['y'] - cy) * sc + dy, it['w'] * sc, it['h'] * sc
    if w < 0.5 or h < 0.5: return None
    rx = it.get('rx', 0) * sc
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rx > 0.5 else MSO_SHAPE.RECTANGLE, E(x), E(y), E(w), E(h))
    if rx > 0.5: shp.adjustments[0] = min(0.5, rx / max(1e-6, min(w, h)))
    style_fill(shp, it.get('fill'), it.get('op', 1))
    if it.get('leftbar') and not it.get('stroke'):
        style_line(shp, None, 0)
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(x), E(y), E(it['leftbar']['w'] * sc), E(h)); style_fill(bar, it['leftbar']['c']); style_line(bar, None, 0); no_shadow(bar)
    else:
        style_line(shp, it.get('stroke'), it.get('sw', 1) * sc, it.get('dash'), it.get('sop', 1))
    if it.get('rot'): shp.rotation = it['rot']
    no_shadow(shp); shp.text_frame.text = ''
    return shp
def add_ellipse(s, it, dx=0, dy=0, sc=1.0, cx=0, cy=0):
    x, y, w, h = cx + (it['x'] - cx) * sc + dx, cy + (it['y'] - cy) * sc + dy, it['w'] * sc, it['h'] * sc
    if w < 0.3: return None
    shp = s.shapes.add_shape(MSO_SHAPE.OVAL, E(x), E(y), E(w), E(h))
    style_fill(shp, it.get('fill'), it.get('op', 1)); style_line(shp, it.get('stroke'), it.get('sw', 1) * sc, it.get('dash'), it.get('sop', 1)); no_shadow(shp)
    return shp
def add_poly(s, it, dx=0, dy=0, sc=1.0, cx=0, cy=0):
    pts = [(cx + (a - cx) * sc + dx, cy + (b - cy) * sc + dy) for a, b in it['pts']]
    if len(pts) < 2: return None
    if len(pts) == 2 and not it.get('closed'):
        (x1, y1), (x2, y2) = pts
        con = s.shapes.add_connector(1, E(x1), E(y1), E(x2), E(y2))
        style_line(con, it.get('stroke'), it.get('sw', 1) * sc, it.get('dash'), it.get('sop', 1), (it.get('ma'), it.get('mb')))
        return con
    fb = s.shapes.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
    fb.add_line_segments([(E(a), E(b)) for a, b in pts[1:]], close=bool(it.get('closed')))
    shp = fb.convert_to_shape()
    if it.get('closed') and it.get('fill'): style_fill(shp, it['fill'], it.get('op', 1))
    else: shp.fill.background()
    style_line(shp, it.get('stroke'), it.get('sw', 1) * sc, it.get('dash'), it.get('sop', 1), (it.get('ma'), it.get('mb'))); no_shadow(shp)
    return shp
def hl_xml(rpr, col):
    h = etree.SubElement(rpr, '{%s}highlight' % AN); c = etree.SubElement(h, '{%s}srgbClr' % AN); c.set('val', col.lstrip('#').upper())
def add_text(s, it, dx=0, dy=0, sc=1.0, cx=0, cy=0, reftext=None):
    runs = [r for r in it['runs'] if r.get('math') is None]
    txt = ''.join(r['t'] for r in runs)
    if not txt.strip() or not re.search(r'[A-Za-z0-9一-鿿≈=<>+−→←%]', txt): return None
    x, y, w, h = cx + (it['x'] - cx) * sc + dx, cy + (it['y'] - cy) * sc + dy, it['w'] * sc, it['h'] * sc
    svg = it.get('svg')
    pad = 2
    tb = s.shapes.add_textbox(E(x - pad), E(y - (1 if svg else 0)), E(w + 2 * pad + (6 if svg else w * 0.04 + 2)), E(max(h, 6)))
    tf = tb.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = not svg and it.get('ws') not in ('nowrap', 'pre')
    tf.auto_size = None; tf.vertical_anchor = MSO_ANCHOR.TOP
    al = {'middle': PP_ALIGN.CENTER, 'end': PP_ALIGN.RIGHT, 'center': PP_ALIGN.CENTER, 'right': PP_ALIGN.RIGHT}.get(it.get('anchor') or it.get('align'), PP_ALIGN.LEFT)
    p = tf.paragraphs[0]; p.alignment = al
    if it.get('lh') and not svg: p.line_spacing = Pt(it['lh'] * PT * sc)
    if it.get('li'):
        r0 = p.add_run(); r0.text = '• '; r0.font.size = Pt(it.get('fs', 14) * PT * sc); r0.font.name = font_of(it.get('f'))
        if it.get('c'): r0.font.color.rgb = rgb(it['c'])
    first = True
    for r in runs:
        t = r['t']
        if reftext: t = reftext(t)
        parts = t.split('\n')
        for j, part in enumerate(parts):
            if j > 0:
                p = tf.add_paragraph(); p.alignment = al
                if it.get('lh') and not svg: p.line_spacing = Pt(it['lh'] * PT * sc)
            if first: part = part.lstrip(); first = False if part else True
            if not part: continue
            rr = p.add_run(); rr.text = part
            f = rr.font; f.size = Pt(max(4, (r.get('fs') or it.get('fs', 14)) * PT * sc)); f.name = font_of(r.get('f') or it.get('f'))
            f.bold = bool(r.get('b')); f.italic = bool(r.get('i'))
            c = r.get('c') or it.get('c')
            if c: f.color.rgb = rgb(c)
            rpr = rr._r.get_or_add_rPr()
            if r.get('u'):
                rpr.set('u', 'sng'); ul = etree.SubElement(rpr, '{%s}uLn' % AN); ul.set('w', '19050')
                sf = etree.SubElement(ul, '{%s}solidFill' % AN); cc = etree.SubElement(sf, '{%s}srgbClr' % AN); cc.set('val', r['u']['rgb'].lstrip('#').upper())
                # uLn must precede fill in schema order: move solid fill of text before? (rPr children order: ln, fill, effect, highlight, uLnTx/uLn, uFillTx/uFill, latin...)
            if r.get('chip') and r.get('bgc'): hl_xml(rpr, r['bgc'])
            elif r.get('hl'): hl_xml(rpr, r['hl'])
            fix_rpr_order(rpr)
    if it.get('rot'): tb.rotation = it['rot']
    return tb
ORDER_RPR = ['ln', 'noFill', 'solidFill', 'gradFill', 'blipFill', 'pattFill', 'grpFill', 'effectLst', 'effectDag', 'highlight', 'uLnTx', 'uLn', 'uFillTx', 'uFill', 'latin', 'ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst']
def fix_rpr_order(rpr):
    ch = list(rpr)
    ch.sort(key=lambda e: ORDER_RPR.index(etree.QName(e).localname) if etree.QName(e).localname in ORDER_RPR else 99)
    for e in ch: rpr.remove(e)
    for e in ch: rpr.append(e)
def add_pic(s, path, x, y, w, h):
    return s.shapes.add_picture(path, E(x), E(y), E(w), E(h))
# ---------------- ink occupancy from the v22q render ----------------
def ink_map(k):
    im = Image.open(D + 'render/v22t/r4/p%02d.png' % k).convert('RGB').resize((320, 180), Image.BILINEAR)
    a = np.asarray(im).astype(int)
    vals, cnt = np.unique(a.reshape(-1, 3) // 8, axis=0, return_counts=True); bg = vals[cnt.argmax()] * 8 + 4
    d = np.abs(a - bg).max(axis=2)
    occ = d > 48
    # dilate by 1 cell (4 px)
    o = occ.copy(); o[1:] |= occ[:-1]; o[:-1] |= occ[1:]; o[:, 1:] |= occ[:, :-1]; o[:, :-1] |= occ[:, 1:]
    return o
def frac_ink(occ, x, y, w, h, extra=None):
    x0, y0, x1, y1 = int(max(0, x // 4)), int(max(0, y // 4)), int(min(320, (x + w) // 4 + 1)), int(min(180, (y + h) // 4 + 1))
    if x1 <= x0 or y1 <= y0: return 1.0
    sub = occ[y0:y1, x0:x1]; f = sub.mean()
    if extra is not None: f = max(f, extra[y0:y1, x0:x1].mean())
    return f
def find_spot(occ, placed, x, y, w, h):
    best = None
    for r in range(0, 900, 8):
        cands = [(x, y)] if r == 0 else [(x + dx, y + dy) for dx, dy in
                 [(r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, r), (r, -r), (-r, -r), (r // 2, r), (-r // 2, r), (r, r // 2), (-r, r // 2), (r // 2, -r), (-r // 2, -r)]]
        for cx_, cy_ in cands:
            if cx_ < 8 or cy_ < 8 or cx_ + w > 1272 or cy_ + h > 712: continue
            if frac_ink(occ, cx_, cy_, w, h, placed) <= 0.0: return cx_, cy_
    return best
# ---------------- full native page ----------------

def load(h, mode):
    f = EX + 's%03d_%s.json' % (h, mode)
    return json.load(open(f)) if os.path.exists(f) else None
def write_item(s, it, h, dx=0, dy=0, sc=1.0, cx=0, cy=0):
    k = it['k']; rt = lambda t: remap(t, h2s)
    if k == 'rect': return add_rect(s, it, dx, dy, sc, cx, cy)
    if k == 'ellipse': return add_ellipse(s, it, dx, dy, sc, cx, cy)
    if k == 'poly': return add_poly(s, it, dx, dy, sc, cx, cy)
    if k == 'text': return add_text(s, it, dx, dy, sc, cx, cy, reftext=rt)
    return None
def maths_for(h, mode):
    d = load(h, mode); out = []
    if d is None: return out
    for i, (x, y, w, hh, v) in enumerate(d['maths']):
        pth = EX + 's%03d_%s_m%d.png' % (h, mode, i)
        if v and os.path.exists(pth): out.append((pth, x, y, w, hh))
    return out
IMGS = None
TABLE_SHRINK = {53: (30, 100, 450, 240, 0.84)}   # H1 verdict table: LibreOffice glyphs are wider than the browser's
def deck_imgs():
    global IMGS
    if IMGS is None:
        htm = open(DECK).read()
        IMGS = re.findall(r'<img\b[^>]*?src="([^"]*)"', htm)
    return IMGS
BGREF = SL[56]                                    # v22t S57 (native page): notebook background + slide number box
def bg_and_number(dst, ref=BGREF):
    bg = ref.shapes[0]; assert bg.shape_type == 13 and bg.left == 0 and bg.top == 0
    el = copy.deepcopy(bg._element); dst.shapes._spTree.insert(2, el)
    rid = bg._element.blipFill.find('{%s}blip' % AN).get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    part = ref.part.related_part(rid); new_rid = dst.part.relate_to(part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    el.blipFill.find('{%s}blip' % AN).set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', new_rid)
    num = next(sh for sh in ref.shapes if sh.has_text_frame and re.fullmatch(r'\d{1,3}', sh.text_frame.text.strip()) and sh.top > 0.8 * SH)
    el2 = copy.deepcopy(num._element); dst.shapes._spTree.append(el2)
    sh = dst.shapes[-1]; p = sh.text_frame.paragraphs[0]._p
    rs = p.findall('{%s}r' % AN) + p.findall('{%s}fld' % AN); rpr = rs[0].find('{%s}rPr' % AN) if rs else None
    for r in rs: p.remove(r)
    for extra in sh.text_frame.paragraphs[1:]: extra._p.getparent().remove(extra._p)
    fld = etree.SubElement(p, '{%s}fld' % AN); fld.set('id', '{' + str(uuid.uuid4()).upper() + '}'); fld.set('type', 'slidenum')
    if rpr is not None: fld.append(copy.deepcopy(rpr))
    t = etree.SubElement(fld, '{%s}t' % AN); t.text = '0'
    endp = p.find('{%s}endParaRPr' % AN)
    if endp is not None: p.remove(endp); p.append(endp)
    return sh
def full_page(s, h):
    d = load(h, 'full'); imgs = deck_imgs(); n = 0
    if d is None: return
    # a block heading (e.g. "Conclusion") is extracted at the same top as the paragraph that contains it: start the paragraph below it
    tx = [it for it in d['items'] if it['k'] == 'text']
    for a in tx:
        for b in tx:
            if a is b or b['h'] >= a['h'] or abs(a['y'] - b['y']) > 3 or abs(a['x'] - b['x']) > 4: continue
            if b['h'] > 40: continue
            a['y'] += b['h'] + 2; a['h'] = max(8, a['h'] - b['h'] - 2); LOG.setdefault('head_fix', []).append([h, ''.join(r.get('t', '') for r in b['runs'])[:20]])
    if h in TABLE_SHRINK:
        x0, y0, x1, y1, f = TABLE_SHRINK[h]
        for it in tx:
            if x0 <= it['x'] <= x1 and y0 <= it['y'] <= y1:
                it['fs'] = (it.get('fs') or 13) * f
                for r in it['runs']:
                    if r.get('fs'): r['fs'] *= f
    for it in d['items']:          # chips whose CSS background is a pattern/white: keep the label readable
        for r in it.get('runs') or []:
            if r.get('chip') and (r.get('bgc') or '#ffffff').lower() == '#ffffff' and (r.get('c') or {}).get('rgb', '').lower() == '#ffffff':
                r['bgc'] = '#eef0f3'; r['c'] = {'rgb': '#5b6474', 'a': 1}; LOG.setdefault('chip_fix', []).append([h, r.get('t', '')[:30]])
    cls = d.get('cls', '')
    for it in d['items']:
        if it['k'] == 'img':
            src = imgs[it['idx']] if 0 <= it.get('idx', -1) < len(imgs) else ''
            m = re.match(r'data:image/(\w+);base64,(.*)', src)
            if not m: continue
            bio = io.BytesIO(base64.b64decode(m.group(2)))
            s.shapes.add_picture(bio, E(it['x']), E(it['y']), E(it['w']), E(it['h'])); n += 1; continue
        if it['k'] == 'rect' and it['x'] <= 1 and it['y'] <= 1 and it['w'] >= 1270: continue  # page background
        if it['k'] == 'text' and 'pg' in (it.get('cls') or '').split(): continue
        if it['k'] == 'text' and it['y'] > 660 and it['x'] > 1150 and re.fullmatch(r'\s*\d{1,3}\s*', ''.join(r['t'] for r in it['runs'])): continue
        if it['k'] == 'text' and it.get('svg'):
            it = dict(it, runs=[dict(r, fs=(r.get('fs') or it.get('fs', 14)) * 0.94) for r in it['runs']], fs=it.get('fs', 14) * 0.94)
        if it['k'] == 'text' and not it.get('svg'):
            it = dict(it, ws='normal', w=min(it['w'], 1270 - it['x']), runs=[dict(r, fs=(r.get('fs') or it.get('fs', 14)) * 0.93) for r in it['runs']], fs=it.get('fs', 14) * 0.93,
                      lh=(it.get('lh') or 0) * 0.93 or None)
        if write_item(s, it, h) is not None: n += 1
    for (pth, x, y, w, hh) in maths_for(h, 'full'): add_pic(s, pth, x, y, w, hh); n += 1
    LOG['full'][h] = n
