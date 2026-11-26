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
W9 = D + 'v22t_work/'; EX = W9 + os.environ.get('EXD', 'ex/')
IN_, OUT = D + 'jlens_1113_pre_v22t.pptx', os.environ.get('OUT', D + 'jlens_1113_pre_v22u.pptx')
DECK = W9 + os.environ.get('DECKF', 'deck_v67.html')
AN = 'http://schemas.openxmlformats.org/drawingml/2006/main'; CJK = re.compile('[一-鿿]')
PFX = '[2026-11-24 v22u] '
prs = Presentation(IN_); SL = list(prs.slides); SW, SH = prs.slide_width, prs.slide_height; NS = len(SL); assert NS == 168
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

# ================= v22u: HTML v69/v70 changes mirrored on v22t =================
MAP = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json'))
for p, v in MAP['v68_to_v22t_first'].items(): H67[int(p)] = v
H67[161] = NS + 1                                     # new backup B23 goes last
REBUILD = {36: 37, 37: 38, 53: 57, 54: 58, 82: 86, 83: 87, 108: 115, 127: 135, 135: 143, 136: 144}   # HTML v70 page -> our-only v22t slide
MAPS = {int(a): b for a, b in json.load(open(W9 + 'maps70/maps.json')).items()} if os.path.exists(W9 + 'maps70/maps.json') else {}
_load0 = load
def load(h, mode):
    d = _load0(h, mode)
    if d is None or mode != 'full' or h not in MAPS: return d
    b = MAPS[h]
    def inside(x, y): return b['x'] - 2 <= x <= b['x'] + b['w'] + 2 and b['y'] - 2 <= y <= b['y'] + b['h'] + 2
    def ctr(it):
        if it['k'] == 'poly': xs = [q[0] for q in it['pts']]; ys = [q[1] for q in it['pts']]; return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        return it['x'] + it.get('w', 0) / 2, it['y'] + it.get('h', 0) / 2
    SVGTXT = ('Read early, said late: where each step happens', 'x: the prompt as Qwen3 tokens', 'Step 1:')
    LEG = {'settled', 'locked', 'fairly solid', 'descriptive', 'exploratory', 'pending'}
    def keep(it):
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).lstrip()
        return t0.startswith('Now asking') or t0.startswith('So (') or any(k in (it.get('cls') or '').split() for k in ('askl', 'soln', 'covna', 'covso', 'covtg', 'lead'))
    def clipped(it):
        if it['k'] != 'text' or it['x'] > b['x'] + b['w'] or it['x'] + it['w'] < b['x']: return False
        if not (b['y'] - 70 <= it['y'] <= b['y'] + b['h'] + 40): return False
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).strip()
        return t0.startswith(SVGTXT) or (t0 in LEG and it['h'] <= 14)
    d = dict(d); d['items'] = [it for it in d['items'] if keep(it) or not (inside(*ctr(it)) or clipped(it))]
    d['maths'] = [m if not inside(m[0] + m[2] / 2, m[1] + m[3] / 2) else [m[0], m[1], m[2], m[3], False] for m in d['maths']]
    return d
LOG['rebuilt'] = []
for h, k in REBUILD.items():
    s = SL[k - 1]; ups = user_ids(s); assert not ups, (k, 'has user shapes')
    shapes = list(s.shapes); bg = shapes[0]; assert bg.shape_type == 13 and bg.left == 0 and bg.top == 0
    num = [sh for sh in shapes if sh.has_text_frame and re.fullmatch(r'\d{1,3}', sh.text_frame.text.strip()) and sh.top > 0.8 * SH]
    keep_ = {bg.shape_id} | {x.shape_id for x in num[-1:]}
    for sh in shapes:
        if sh.shape_id in keep_: continue
        LOG['deleted'].append([k, sh.shape_id, 'rebuilt from HTML v70 page %d' % h]); sh._element.getparent().remove(sh._element)
    full_page(s, h)
    if h in MAPS:
        b = MAPS[h]; add_pic(s, W9 + 'maps70/map_%03d.png' % h, b['x'], b['y'], b['w'], b['h'])
    if num:      # keep the slide-number box last
        el_ = num[-1]._element; el_.getparent().remove(el_); s.shapes._spTree.append(el_)
    LOG['rebuilt'].append([h, k]); LOG['notes'].setdefault(k, []).append('Our content rebuilt from HTML deck v70 page %d (canonical matrix / v69–v70 fixes).' % h)

# HTML 23 (v22t S24): verb fix in our own shapes ("names" -> "carries information about")
REPL23 = [(r"the own state names its own first author better", "the paper's own state carries information about its first author"),
          (r"can the title state name its own first author when", "does the paper's own title state carry information about its first author when")]
def frame_sub(tf, pairs):
    ch = False
    for p in tf.paragraphs:
        full = ''.join(r.text for r in p.runs); new = full
        for a, b_ in pairs: new = re.sub(a, b_, new)
        if new == full: continue
        for r in p.runs:
            nr = r.text
            for a, b_ in pairs: nr = re.sub(a, b_, nr)
            if nr != r.text: r.text = nr; ch = True
        if ''.join(r.text for r in p.runs) != new and p.runs:
            p.runs[0].text = new
            for r in p.runs[1:]: r.text = ''
        ch = True
    return ch
for k, pairs in ((24, REPL23),):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or not sh.has_text_frame or CJK.search(sh.text_frame.text): continue
        if frame_sub(sh.text_frame, pairs): LOG['edited'].append([k, sh.shape_id])
    LOG['notes'].setdefault(k, []).append('Wording: "the own state names its first author" -> "carries information about its first author" (HTML v69).')

# HTML 35 (v22t S36, the user's table): our "How to read" line updated; current results noted beside the user's table (table untouched)
s = SL[35]; ups = user_ids(s)
for sh in s.shapes:
    if sh.shape_id in ups or not sh.has_text_frame: continue
    if sh.text_frame.text.startswith('How to read'):
        frame_sub(sh.text_frame, [(r' · ⚠ = known issue, marked for confirmation, not yet changed', ''),
                                  (r'measured top lens word and the evidence matrix see slide 36b', 'measured top lens word and the evidence matrix → slide %d' % H67[37])])
        LOG['edited'].append([36, sh.shape_id])
occ = ink_map(36); placed = np.zeros_like(occ)
lines = ['Current results (2026-11-24, from the canonical matrix):',
         '• Task only (H1): downgraded — “:” follows the question; the format layer is not pinned down (descriptive; locked rule downgraded) → slide %d' % H67[53],
         '• Change-the-question check: cannot separate — ceiling: the same title text gives cosine 0.998 already at L4 → slide %d' % H67[77],
         '• Paper facts are inferable from the title text and readable early (attribute probe) · surname signal from L8']
w, hgt = 600, 64
spot = find_spot(occ, placed, 660, 560, w, hgt) or find_spot(occ, placed, 40, 560, w, hgt)
if spot:
    tb = s.shapes.add_textbox(E(spot[0]), E(spot[1]), E(w), E(hgt)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for j, ln in enumerate(lines):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph(); r = p.add_run(); r.text = ln
        r.font.size = Pt((11 if j else 11.5) * PT); r.font.name = 'Noto Sans SC'; r.font.bold = (j == 0); r.font.color.rgb = RGBColor(0x22, 0x30, 0x4A)
    LOG['notes'].setdefault(36, []).append('Current results from the canonical matrix noted beside your table (table unchanged).')
else:
    LOG['not_fitted'].append([36, 'current results note'])

# new backup B23 (HTML 161), last
ns = prs.slides.add_slide(BGREF.slide_layout)
for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
nb_ = bg_and_number(ns); full_page(ns, 161)
el_ = nb_._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v70 page 161 (B23).'
FINAL = list(prs.slides)
for f in ns._element.iter('{%s}fld' % AN):
    if f.get('type') == 'slidenum':
        t = f.find('{%s}t' % AN)
        if t is not None: t.text = str(len(FINAL))
for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
for k in range(1, NS + 1):
    nid = max(ORIG[k]) + 4000
    for x in SL[k - 1].shapes:
        if any(x._element is b for b in ORIG_EL[k]): continue
        x._element.xpath('./*[1]/p:cNvPr')[0].set('id', str(nid)); nid += 1
prs.save(OUT)
ADDED = [[k, sid] for k in range(1, NS + 1) for sid in [x.shape_id for x in SL[k - 1].shapes] if sid not in ORIG[k]]
DELS = [[k, sid] for k, sid, _ in LOG['deleted']]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': ADDED, 'deleted': DELS, 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [NS + 1], 'user_authorised': [], 'order': list(range(1, NS + 1)) + [0]}, open(OUT + '.allow.json', 'w'), indent=0)
M = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json'))
out = {'v70_to_v22u_first': dict(M['v68_to_v22t_first'], **{'161': NS + 1}), 'v70_to_v22u_all': dict(M['v68_to_v22t_all'], **{'161': [NS + 1]}),
       'note': 'v22u = v22t slide order unchanged (1-168) + B23 at 169; HTML v69/v70 kept v68 page numbers 1-160, added 161.'}
json.dump(out, open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22u_v70.json', 'w'), indent=0)
json.dump({'log': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in LOG.items()}}, open(W9 + 'build22u_log.json', 'w'), indent=0)
print('slides', len(FINAL), 'rebuilt', LOG['rebuilt'], 'edited', len(LOG['edited']), 'not fitted', LOG['not_fitted'])
