"""2026-11-25 main pptx v22v -> v22w (mirrors HTML v72; user HANDOFF items 44-45):
- 25 story-figure slides inserted before v22v S141 (= HTML v71 133, start of Part 7 "What we learned"), as native slides:
  tag + title + Now asking line (text) + the full figure as one picture + So line with evidence tag (text); nothing replaced;
- the 8 small-text slides of HTML v72 (3, 9, 20, 52, 65, 97, 106, 170 = v22v S3, S9, S21, S56, S69, S101, S113, S153):
  the same boxes (our own shapes only) raised to >= 14 px equivalent (7.875 pt) and moved to the HTML v72 geometry;
- every "slide N" in our own shapes renumbered v22v -> v22w (N >= 141 -> N + 25);
- user shapes (stage1-13 超长卷.pptx) and Chinese boxes never edited.
usage: build22w.py [DRY]"""
import sys, json, re, copy, uuid, os
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
DRY = len(sys.argv) > 1
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
W = '/home/zhang.zhiqi2/jlens_work/32_v72/'
IN_, OUT = D + 'jlens_1113_pre_v22v.pptx', D + 'jlens_1113_pre_v22w.pptx'
AN = 'http://schemas.openxmlformats.org/drawingml/2006/main'; CJK = re.compile('[一-鿿]')
PFX = '[2026-11-25 v22w] '
prs = Presentation(IN_); SL = list(prs.slides); SW, SH = prs.slide_width, prs.slide_height; NS = len(SL); assert NS == 163
K = SW / 1280.0; PT = 0.5625
def E(v): return Emu(int(round(v * K)))
UPLOAD = Presentation(D + 'stage1-13 超长卷.pptx'); UPS = {su.slide_id: {x.shape_id for x in su.shapes} for su in UPLOAD.slides}
def user_ids(s): return UPS.get(s.slide_id, set())
LOG = {'edited': [], 'notes': {}, 'renum': [], 'box': [], 'box_miss': [], 'stale_user_refs': []}
INS = 141
PM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22v_v71.json'))
assert PM['v71_to_v22v_first']['133'] == INS
RM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v72.json'))
NEWS = json.load(open(W + 'new_slides_v72.json'))            # [v72 page, file, title, ask, so, tagcls, tagtext, alt, (sok)]
assert len(NEWS) == 25 and [x[0] for x in NEWS] == list(range(133, 158))
REF = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
def remap(text, f): return REF.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(f(int(x.group(0)))), m.group(2)), text)
def old2new(n): return n + 25 if INS <= n <= NS else n
def norm(t): return re.sub(r'[\s·①②③④⑤⑥]+', '', t)

# ---------------- 1) small-text boxes (HTML v72 geometry, px) ----------------
G = json.load(open(W + 'geom_v72.json'))
H2P = {3: 3, 9: 9, 20: 21, 52: 56, 65: 69, 97: 101, 106: 113, 170: 153}
for v71, k in [(3, 3), (9, 9), (20, 21), (52, 56), (65, 69), (97, 101), (106, 113), (145, 153)]:
    assert k in PM['v71_to_v22v_all'][str(v71)], (v71, k)
MINPT = 14 * PT
def is_chip(r):
    try: col = str(r.font.color.rgb).upper() if r.font.color and r.font.color.type is not None else ''
    except Exception: col = ''
    return col == 'FFFFFF' or (r.font.name == 'Noto Sans SC' and r.font.size is not None and r.font.size.pt < 6.6)
def inside(a, b, tol):   # shape a's top-left inside b's rect (EMU) with tolerance
    return b.left - tol <= a.left <= b.left + b.width and b.top - tol <= a.top <= b.top + b.height
for g in G:
    k = H2P[g['slide']]; s = SL[k - 1]; ups = user_ids(s)
    key = norm(g['text'])[:18]
    cands = [sh for sh in s.shapes if sh.has_text_frame and sh.shape_id not in ups and not CJK.search(sh.text_frame.text)
             and norm(sh.text_frame.text).startswith(key)]
    if len(cands) != 1:
        LOG['box_miss'].append([g['slide'], k, g['text'][:40], [c.shape_id for c in cands]]); continue
    T = cands[0]; tol = int(6 * 12700)
    bgs = [sh for sh in s.shapes if sh.shape_type == 1 and sh.shape_id not in ups and sh is not T and not (sh.has_text_frame and sh.text_frame.text.strip())
           and inside(T, sh, tol) and sh.width >= 0.6 * T.width]
    bars = [b for b in bgs if b.width <= 4 * 12700]; bgs = [b for b in bgs if b.width > 4 * 12700]
    bg = max(bgs, key=lambda b: b.width * b.height) if bgs else None
    # pptx layouts differ from the HTML (user-edited slides): keep the pptx place if the grown box fits there, else search free space on THIS slide
    box = [T] + ([bg] if bg is not None else []) + bars
    bx = bg if bg is not None else T
    dl, dt = (T.left - bx.left, T.top - bx.top) if bg is not None else (0, 0)
    pad_r = (bx.left + bx.width) - (T.left + T.width) if bg is not None else 0
    def est_h(wbox):
        wtxt = (wbox - dl - max(pad_r, 0)) / 12700.0
        tot = 0.0; lines = 0
        for p in T.text_frame.paragraphs:
            wsum = 0.0; lh = 0.0
            for r in p.runs:
                sz = r.font.size.pt if r.font.size is not None else MINPT
                sz = max(sz, 11 * PT) if is_chip(r) else max(sz, MINPT)
                wsum += len(r.text) * sz * 0.47; lh = max(lh, sz)
            n = max(1, -(-wsum // max(wtxt, 10))); lines += n; tot += n * (lh or MINPT) * 1.28
        return int((tot + 2 * dt / 12700.0 + 2) * 12700)
    obst = []
    for sh in s.shapes:
        if sh in box or (sh.width * sh.height >= 0.9 * SW * SH): continue   # full-slide background picture / grid group
        if sh.left >= SW or sh.top >= SH or sh.left + sh.width <= 0: continue
        if sh.has_text_frame and re.fullmatch(r'\s*\d{0,3}\s*', sh.text_frame.text) and sh.top > 0.85 * SH: continue
        obst.append((sh.left, sh.top, sh.left + sh.width, sh.top + sh.height))
    M = int(2 * 12700)
    def free(x, y, w, h):
        if x < int(15 * 12700) or y < 0 or x + w > SW - int(10 * 12700) or y + h > SH - int(4 * 12700): return False
        return not any(not (x + w <= o[0] - M or x >= o[2] + M or y + h <= o[1] - M or y >= o[3] + M) for o in obst)
    best = None
    for wf in (1.0, 1.15, 1.3, 1.5, 1.75, 2.0):
        w = int(bx.width * wf); h = est_h(w)
        if free(bx.left, bx.top, w, h):
            d = (wf - 1) * 100
            if best is None or d < best[4]: best = (bx.left, bx.top, w, h, d)
            break
    if best is None or best[4] > 0:
        step = int(4 * 12700)
        for wf in (1.0, 1.15, 1.3, 1.5, 1.75, 2.0):
            w = int(bx.width * wf); h = est_h(w)
            for y in range(0, SH - h, step):
                for x in range(int(15 * 12700), SW - w, step):
                    if not free(x, y, w, h): continue
                    d = ((x - bx.left) ** 2 + (y - bx.top) ** 2) ** 0.5 / 12700 + (wf - 1) * 100
                    if best is None or d < best[4]: best = (x, y, w, h, d)
    if best is None:
        LOG['box_miss'].append([g['slide'], k, 'no free space', T.shape_id]); best = (bx.left, bx.top, bx.width, est_h(bx.width), -1)
    nx, ny, nw, nh = [int(v) for v in best[:4]]
    MAN = {(9, 2668): (213, 1, 390, 26), (56, 6390): (215, 2, 420, 36), (56, 9397): (518, 62, 169, 36), (21, 8092): (340, 1, 272, 24)}   # pt; checked on the LibreOffice render
    if (k, T.shape_id) in MAN: nx, ny, nw, nh = [int(v * 12700) for v in MAN[(k, T.shape_id)]]; best = (nx, ny, nw, nh, -2)
    moved = []
    if bg is not None:
        bg.left, bg.top, bg.width, bg.height = nx, ny, nw, nh
        for b in bars: b.left, b.top, b.height = nx, ny, nh
        T.left, T.top = nx + dl, ny + dt; T.width = max(nw - dl - max(pad_r, 0), int(40 * 12700)); T.height = max(nh - 2 * dt, int(8 * 12700))
        moved = [bg.shape_id] + [b.shape_id for b in bars]
    else:
        T.left, T.top, T.width, T.height = nx, ny, nw, nh
    LOG.setdefault('geom', []).append([k, T.shape_id, round(best[4], 1), [round(v / 12700) for v in (nx, ny, nw, nh)]])
    tf = T.text_frame; tf.word_wrap = True; tf.auto_size = None
    nfix = 0
    for p in tf.paragraphs:
        for r in p.runs:
            sz = r.font.size.pt if r.font.size is not None else None
            if sz is None: continue
            if is_chip(r):
                if sz < 11 * PT: r.font.size = Pt(11 * PT); nfix += 1
            elif sz < MINPT - 1e-6: r.font.size = Pt(MINPT); nfix += 1
        if p.line_spacing is not None and hasattr(p.line_spacing, 'pt') and p.line_spacing.pt < MINPT * 1.2: p.line_spacing = Pt(MINPT * 1.25)
    for sid in [T.shape_id] + moved: LOG['edited'].append([k, sid])
    LOG['box'].append([g['slide'], k, T.shape_id, moved, nfix, LOG['geom'][-1][2:], g['text'][:30]])
    LOG['notes'].setdefault(k, []).append('Small-text box raised to >= 14 px equivalent and moved to free space (as HTML v72).')

# ---------------- 2) renumber "slide N" in our own shapes ----------------
for k in range(1, NS + 1):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or not sh.has_text_frame or CJK.search(sh.text_frame.text): continue
        ch = False
        for p_ in sh.text_frame.paragraphs:
            for r in p_.runs:
                nt = remap(r.text, old2new)
                if nt != r.text: r.text = nt; ch = True
        if ch:
            LOG['edited'].append([k, sh.shape_id]); LOG['renum'].append([k, sh.shape_id])
            LOG['notes'].setdefault(k, []).append('Slide references renumbered to v22w (HTML v72 order).')
    for sh in s.shapes:
        if sh.shape_id in ups and sh.has_text_frame and REF.search(sh.text_frame.text): LOG['stale_user_refs'].append([k, sh.shape_id, sh.text_frame.text[:60]])

# ---------------- 3) the 25 new native slides ----------------
BGREF = SL[16 - 1]          # v22v S16: native page built from HTML (notebook background, tag box, title, sub line, So line, slide number)
def shp(sid): return next(sh for sh in BGREF.shapes if sh.shape_id == sid)
def bg_and_number(dst, ref=BGREF):
    bg = ref.shapes[0]; assert bg.shape_type == 13 and bg.left == 0 and bg.top == 0
    el = copy.deepcopy(bg._element); dst.shapes._spTree.insert(2, el)
    RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
    rid = bg._element.blipFill.find('{%s}blip' % AN).get(RID)
    part = ref.part.related_part(rid); new_rid = dst.part.relate_to(part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    el.blipFill.find('{%s}blip' % AN).set(RID, new_rid)
    num = next(sh for sh in ref.shapes if sh.has_text_frame and re.fullmatch(r'\d{1,3}', sh.text_frame.text.strip()) and sh.top > 0.8 * SH)
    el2 = copy.deepcopy(num._element); dst.shapes._spTree.append(el2)
    sh = dst.shapes[-1]; p = sh.text_frame.paragraphs[0]._p
    rs = p.findall('{%s}r' % AN) + p.findall('{%s}fld' % AN); rpr = rs[0].find('{%s}rPr' % AN) if rs else None
    for r in rs: p.remove(r)
    if not rs:
        rpr = None
    fld = etree.SubElement(p, '{%s}fld' % AN); fld.set('id', '{' + str(uuid.uuid4()).upper() + '}'); fld.set('type', 'slidenum')
    if rpr is not None: fld.append(copy.deepcopy(rpr))
    t = etree.SubElement(fld, '{%s}t' % AN); t.text = '0'
    endp = p.find('{%s}endParaRPr' % AN)
    if endp is not None: p.remove(endp); p.append(endp)
    return sh
def clone(dst, src):
    el = copy.deepcopy(src._element); dst.shapes._spTree.append(el); return dst.shapes[-1]
def set_runs(sh, parts):
    """parts: list of (text, dict(size, bold, color, font, hl))"""
    tf = sh.text_frame
    for p in tf.paragraphs[1:]: p._p.getparent().remove(p._p)
    p = tf.paragraphs[0]
    proto = p.runs[0]._r if p.runs else None
    for r in list(p._p.findall('{%s}r' % AN)): p._p.remove(r)
    for txt, st in parts:
        if proto is not None:
            r_el = copy.deepcopy(proto); r_el.find('{%s}t' % AN).text = txt; endp = p._p.find('{%s}endParaRPr' % AN)
            if endp is not None: endp.addprevious(r_el)
            else: p._p.append(r_el)
            from pptx.text.text import _Run
            r = _Run(r_el, p)
        else:
            r = p.add_run(); r.text = txt
        f = r.font
        if 'size' in st: f.size = Pt(st['size'])
        if 'bold' in st: f.bold = st['bold']
        if 'font' in st: f.name = st['font']
        if 'color' in st: f.color.rgb = RGBColor.from_string(st['color'])
        rpr = r._r.get_or_add_rPr()
        for h in rpr.findall('{%s}highlight' % AN): rpr.remove(h)
        if st.get('hl'):
            h = etree.Element('{%s}highlight' % AN); c = etree.SubElement(h, '{%s}srgbClr' % AN); c.set('val', st['hl'])
            pos = None
            for i, ch in enumerate(rpr):
                if etree.QName(ch).localname in ('uLnTx', 'uLn', 'uFillTx', 'uFill', 'latin', 'ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst'): pos = i; break
            if pos is None: rpr.append(h)
            else: rpr.insert(pos, h)
TAGC = {'desc': ('FFFFFF', '6A7385'), 'expl': ('FFFFFF', 'B54708'), 'lnot': ('FFFFFF', 'C84A3E'), 'lsup': ('FFFFFF', '3C78B4'),
        'settled': ('FFFFFF', '2E7D46'), 'solid': ('3C78B4', None), 'lim': ('B54708', None)}
NEWSL = []
for pg, fname, title, ask, so, tc, tt, alt, *rest in NEWS:
    sok = rest[0] if rest else 'So (this slide)'
    ns = prs.slides.add_slide(BGREF.slide_layout)
    for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
    nb = bg_and_number(ns)
    clone(ns, shp(5)); tg = clone(ns, shp(6)); set_runs(tg, [('Summary · story figures', {})])
    ti = clone(ns, shp(7)); set_runs(ti, [(title, {'size': 24 * PT, 'bold': True})])
    ti.left, ti.top, ti.width, ti.height = E(70), E(40), E(1110), E(32)
    ak = clone(ns, shp(8)); set_runs(ak, [('Now asking: ', {'size': 15 * PT, 'bold': True, 'color': '22304A'}), (ask, {'size': 15 * PT, 'bold': False, 'color': '22304A'})])
    ak.left, ak.top, ak.width, ak.height = E(70), E(76), E(1140), E(20)
    pic = ns.shapes.add_picture(W + 'story16x9/' + fname, E(116), E(100), E(1048), E(589.5)); pic.name = 'story figure ' + fname[:-4]
    pic._element.nvPicPr.cNvPr.set('descr', alt)
    b1 = clone(ns, shp(21)); b2 = clone(ns, shp(22)); st_ = clone(ns, shp(23))
    for b in (b1, b2): b.top, b.height = E(694), E(22)
    b1.left, b1.width = E(70), E(1140); b2.left = E(70)
    fg, hl = TAGC[tc]
    set_runs(st_, [(sok + ': ', {'size': 14 * PT, 'bold': True, 'color': 'B54708'}), (so + ' ', {'size': 14 * PT, 'bold': False, 'color': '22304A'}),
                   (' ' + tt + ' ', {'size': 11 * PT, 'bold': True, 'color': fg, 'font': 'Noto Sans SC', 'hl': hl})])
    st_.left, st_.top, st_.width, st_.height = E(82), E(697), E(1120), E(18)
    st_.text_frame.word_wrap = True
    el_ = nb._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
    ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v72 page %d (summary chapter, story figure).' % pg
    NEWSL.append(ns)

# ---------------- 4) order ----------------
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
lst = prs.slides._sldIdLst; ids = list(lst)
old_el = {k: ids[k - 1] for k in range(1, NS + 1)}; new_el = ids[NS:]
SEQ = [('old', k) for k in range(1, INS)] + [('new', i) for i in range(25)] + [('old', k) for k in range(INS, NS + 1)]
for e in list(lst): lst.remove(e)
for t, k in SEQ: lst.append(old_el[k] if t == 'old' else new_el[k])
for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
print('boxes', len(LOG['box']), 'missing', LOG['box_miss'])
for b in LOG['box']: print('  box', b)
print('renum shapes', len(LOG['renum']), 'stale user refs', len(LOG['stale_user_refs']))
if DRY: sys.exit(0)
prs.save(OUT)
order = [k if t == 'old' else 0 for t, k in SEQ]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': [], 'deleted': [], 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [i for i, o in enumerate(order, 1) if o == 0], 'deleted_slides': [], 'user_authorised': [], 'order': order},
          open(OUT + '.allow.json', 'w'), indent=0)
# map HTML v72 -> v22w
V71_22V_ALL = {int(a): b for a, b in PM['v71_to_v22v_all'].items()}
REN = {int(a): b for a, b in RM['v71_to_v72'].items()}
all72 = {}
for p71, ks in V71_22V_ALL.items(): all72[REN[p71]] = [old2new(k) for k in ks]
for i, x in enumerate(NEWS): all72[x[0]] = [INS + i]
json.dump({'v72_to_v22w_first': {str(p): all72[p][0] for p in sorted(all72)}, 'v72_to_v22w_all': {str(p): all72[p] for p in sorted(all72)},
           'v22v_to_v22w': {str(k): old2new(k) for k in range(1, NS + 1)},
           'note': 'v22w = HTML v72 order; 25 native story-figure slides (v72 133-157) at S141-S165 before the old Part 7; small-text boxes on S3, S9, S21, S56, S69, S101, S113, S153(v22v) -> S178(v22w) raised to 14 px eq.'},
          open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22w_v72.json', 'w'), indent=0)
json.dump(LOG, open(W + 'build22w_log.json', 'w'), indent=0, ensure_ascii=False)
print('saved', OUT, 'slides', len(prs.slides))
