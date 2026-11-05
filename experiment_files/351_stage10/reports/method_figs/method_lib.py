"""Primitive library for the method slides (v3, 2026-11-05).
A slide = list of primitives (Rect, Circle, Line, Poly, Text, Group) on a 1280 x 720 px canvas.
Back-ends: svg_of() -> SVG string; pptx_render() -> python-pptx native shapes on a slide (1 px = slide_width/1280 EMU).
Background (method category): very light pink paper + pink 32-px grid.  In pptx: slide background fill + a locked
group of thin grid lines at the back of the z-order."""
from dataclasses import dataclass, field
from pathlib import Path
import math

FONTS = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/talk/src/fonts')
C = dict(paper='#FFFBFB', grid='#FAEEEE', ink='#22304A', pen='#6A7385', true='#D9772B', false='#C3C9D2',
         white='#FFFFFF', name='#F7E7A6', blue='#3C78B4', red='#C84A3E', green='#3E8E4E', cell='#D5DAE2',
         tag='#B0566F', purple='#8A6BC8', faint='#EEF0F4')
FONT = {'title': 'Caveat', 'hand': 'Patrick Hand'}
W, H, GRID = 1280, 720, 32


# ------------------------------------------------------------------ primitives
@dataclass
class Rect:
    x: float; y: float; w: float; h: float
    fill: str = None; stroke: str = None; sw: float = 1.6; rx: float = 0; dash: bool = False; fill_op: float = 1; name: str = ''

@dataclass
class Circle:
    cx: float; cy: float; r: float
    fill: str = None; stroke: str = None; sw: float = 0; fill_op: float = 1; name: str = ''

@dataclass
class Line:
    x1: float; y1: float; x2: float; y2: float
    stroke: str = C['ink']; sw: float = 2; dash: bool = False; arrow: bool = False; round: bool = False; op: float = 1; name: str = ''

@dataclass
class Poly:                       # polyline / polygon; curves are sampled into points
    pts: list
    stroke: str = None; sw: float = 2; fill: str = None; closed: bool = False; dash: bool = False; arrow: bool = False
    round: bool = False; fill_op: float = 1; name: str = ''

@dataclass
class Text:                       # (x, y) = baseline anchor point, as in SVG
    x: float; y: float; s: str
    fs: float = 19; col: str = C['ink']; anchor: str = 'start'; font: str = 'hand'; bold: bool = False; rot: float = 0
    name: str = ''

@dataclass
class Group:
    items: list = field(default_factory=list); name: str = ''


def qcurve(p0, c, p2, n=18):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1]) for t in (i / n for i in range(n + 1))]

def ccurve(p0, c1, c2, p3, n=20):
    out = []
    for i in range(n + 1):
        t = i / n; a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0], a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1]))
    return out

def band(x0, y0a, y0b, x1, y1a, y1b, n=20):
    """Sankey band between vertical segments [y0a,y0b] at x0 and [y1a,y1b] at x1 (closed polygon points)."""
    m = (x0 + x1) / 2
    top = ccurve((x0, y0a), (m, y0a), (m, y1a), (x1, y1a), n)
    bot = ccurve((x1, y1b), (m, y1b), (m, y0b), (x0, y0b), n)
    return top + bot


# ------------------------------------------------------------------ font metrics
from fontTools.ttLib import TTFont
_F = {}
def _font(kind):
    if kind not in _F:
        t = TTFont(FONTS / ('Caveat.ttf' if kind == 'title' else 'PatrickHand-Regular.ttf'))
        _F[kind] = (t.getBestCmap(), t['hmtx'].metrics, t['head'].unitsPerEm, t['OS/2'].usWinAscent, t['OS/2'].usWinDescent)
    return _F[kind]

def text_w(s, fs, kind='hand', bold=False):
    cmap, hm, upm, _, _ = _font(kind)
    w = sum(hm[cmap[ord(ch)]][0] if ord(ch) in cmap else 0.6 * upm for ch in s) / upm * fs
    return w * (1.07 if bold else 1)


# ------------------------------------------------------------------ helpers built from primitives
def tok(x, y, w, h, kind, label='', fs=15, name=''):
    fill = {'true': C['true'], 'false': C['false'], 'white': C['white'], 'name': C['name']}[kind]
    it = [Rect(x, y, w, h, fill, C['ink'], 1.6, 4)]
    if label:
        it.append(Text(x + w / 2, y + h / 2 + fs * 0.33, label, fs, '#FFFFFF' if kind == 'true' else C['ink'], 'middle'))
    return Group(it, name or f'token {label or kind}') if label else it[0]

def tok_w(label, fs=15, pad=12, mn=22):
    return max(mn, text_w(label, fs) + pad)

def tok_row(spec, x, y, h=32, fs=15, gap=4, name='prompt'):
    """spec = [(kind, label)]; returns (Group, [(x, w, kind, label)])"""
    cols = []
    for k, lab in spec:
        w = tok_w(lab, fs); cols.append((x, w, k, lab)); x += w + gap
    return Group([tok(cx, y, w, h, k, lab, fs) for cx, w, k, lab in cols], name), cols

def dot(x, y, r=6, fill=None):
    return Circle(x, y, r, fill or C['ink'])

def magnifier(x, y, r=16):
    return Group([Circle(x, y, r, '#FFFFFF', C['ink'], 3, fill_op=.6),
                  Line(x + r * .7, y + r * .7, x + r * 1.6, y + r * 1.6, C['ink'], 5, round=True)], 'magnifier')

def cross(x, y, s=10):
    return Group([Line(x - s, y - s, x + s, y + s, C['red'], 4, round=True),
                  Line(x + s, y - s, x - s, y + s, C['red'], 4, round=True)], 'red cross')

def step(n, x, y, r=13):
    return Group([Circle(x, y, r, C['ink']), Text(x, y + 6, str(n), 18, '#FFFFFF', 'middle')], f'step {n}')

def step_label(n, x, y, s, col=None, fs=20):
    """numbered circle + short label; (x, y) = circle centre"""
    return Group([step(n, x, y), Text(x + 21, y + 7, s, fs, col or C['ink'])], f'step {n} label')

def title(s, sub=None):
    it = [Text(70, 100, s, 58, font='title', bold=True, name='title')]
    if sub: it.append(Text(72, 136, sub, 21, C['pen'], name='subtitle'))
    return it

def section_tag(s='Methods in pictures'):
    fs = 18; w = text_w(s, fs) + 30; x = W - 26 - w
    return Group([Rect(x, 22, w, 30, None, C['tag'], 2, 10), Text(x + w / 2, 43, s, fs, C['tag'], 'middle')], 'section tag')

def flow_node(n, x, y, label, fs=19, h=40, fill='#FFFFFF', name=None):
    """numbered node of the step flow; returns (Group, (x, y, w, h))"""
    w = text_w(label, fs) + 58
    g = Group([Rect(x, y, w, h, fill, C['ink'], 2, 12), step(n, x + 22, y + h / 2, 12),
               Text(x + 42, y + h / 2 + fs * 0.33, label, fs)], name or f'flow node {n}')
    return g, (x, y, w, h)

def flow_arrow(a, b, side='h', col=None, bend=0):
    """arrow between two node boxes a, b = (x, y, w, h); side 'h' right->left edge, 'v' bottom->top edge"""
    col = col or C['ink']
    if side == 'h':
        p0, p2 = (a[0] + a[2] + 4, a[1] + a[3] / 2), (b[0] - 6, b[1] + b[3] / 2)
    else:
        p0, p2 = (a[0] + a[2] / 2, a[1] + a[3] + 4), (b[0] + b[2] / 2, b[1] - 6)
    if abs(p0[1] - p2[1]) < 1 and side == 'h' or abs(p0[0] - p2[0]) < 1 and side == 'v':
        return Line(p0[0], p0[1], p2[0], p2[1], col, 2.5, arrow=True, name='flow arrow')
    c = ((p0[0] + p2[0]) / 2 + bend, p0[1]) if side == 'h' else (p0[0], (p0[1] + p2[1]) / 2 + bend)
    if side == 'h': c = (p0[0] + (p2[0] - p0[0]) * 0.55, p2[1])
    return Poly(qcurve(p0, c, p2, 16), col, 2.5, arrow=True, name='flow arrow')

def formula_box(x, y, s, fs=27, sub=None, w=None, name='formula'):
    """prominent formula: cream box with an orange border; (x, y) = top-left"""
    tw = max(text_w(s, fs, bold=True), text_w(sub, 16) if sub else 0)
    w = w or tw + 44; h = fs + 30 + (22 if sub else 0)
    it = [Rect(x, y, w, h, '#FFF6DA', C['true'], 3, 14), Text(x + w / 2, y + 12 + fs * 0.92, s, fs, C['ink'], 'middle', bold=True)]
    if sub: it.append(Text(x + w / 2, y + h - 12, sub, 16, C['pen'], 'middle'))
    return Group(it, name)

def funnel(x, y, w=106, h=68, name='funnel'):
    return Poly([(x, y), (x + w, y), (x + w * .62, y + h * .6), (x + w * .62, y + h), (x + w * .38, y + h), (x + w * .38, y + h * .6)],
                C['ink'], 2.5, '#FFFFFF', closed=True, name=name)


# ------------------------------------------------------------------ shared helpers
def walk(items):
    for it in items:
        if isinstance(it, Group): yield from walk(it.items)
        else: yield it

def shorten(p0, p1, d):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    return (p1[0] - dx / L * d, p1[1] - dy / L * d)

def words(items, skip_tokens=False):
    n = 0
    def rec(its, in_tok):
        nonlocal n
        for it in its:
            if isinstance(it, Group):
                if it.name == 'section tag' or it.name.startswith('formula'): continue
                rec(it.items, in_tok or it.name.startswith('token') or it.name.endswith('prompt'))
            elif isinstance(it, Text) and not (skip_tokens and in_tok):
                n += sum(1 for w in it.s.split() if any(ch.isalpha() for ch in w))
    rec(items, False); return n


# ------------------------------------------------------------------ back-end 1: SVG
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def svg_of(items, tag, uid='m', width_attr=''):
    """uid prefixes the pattern/marker ids so several SVGs can live in one HTML page."""
    cols = sorted({it.stroke for it in walk(items) if isinstance(it, (Line, Poly)) and it.arrow})
    marks = ''.join(f'<marker id="{uid}a{c[1:]}" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="5" markerHeight="5" '
                    f'orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in cols)

    def st(stroke, sw, dash=False, rnd=False, op=1):
        if not stroke: return 'stroke="none"'
        s = f'stroke="{stroke}" stroke-width="{sw:g}"'
        if dash: s += f' stroke-dasharray="{4 * sw:g} {3 * sw:g}"'
        if rnd: s += ' stroke-linecap="round"'
        if op != 1: s += f' stroke-opacity="{op:g}"'
        return s

    def fo(op): return f' fill-opacity="{op:g}"' if op != 1 else ''

    def one(it):
        if isinstance(it, Group):
            return f'<g data-name="{esc(it.name)}">' + ''.join(one(i) for i in it.items) + '</g>'
        if isinstance(it, Rect):
            return (f'<rect x="{it.x:.1f}" y="{it.y:.1f}" width="{it.w:.1f}" height="{it.h:.1f}" rx="{it.rx:g}" '
                    f'fill="{it.fill or "none"}"{fo(it.fill_op)} {st(it.stroke, it.sw, it.dash)}/>')
        if isinstance(it, Circle):
            return f'<circle cx="{it.cx:.1f}" cy="{it.cy:.1f}" r="{it.r:g}" fill="{it.fill or "none"}"{fo(it.fill_op)} {st(it.stroke, it.sw)}/>'
        if isinstance(it, Line):
            x2, y2 = (shorten((it.x1, it.y1), (it.x2, it.y2), 4 * it.sw) if it.arrow else (it.x2, it.y2))
            m = f' marker-end="url(#{uid}a{it.stroke[1:]})"' if it.arrow else ''
            return (f'<line x1="{it.x1:.1f}" y1="{it.y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'{st(it.stroke, it.sw, it.dash, it.round, it.op)}{m}/>')
        if isinstance(it, Poly):
            pts = list(it.pts)
            if it.arrow: pts[-1] = shorten(pts[-2], pts[-1], 4 * it.sw)
            m = f' marker-end="url(#{uid}a{it.stroke[1:]})"' if it.arrow else ''
            tagn = 'polygon' if it.closed else 'polyline'
            return (f'<{tagn} points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{it.fill or "none"}"{fo(it.fill_op)} '
                    f'stroke-linejoin="round" {st(it.stroke, it.sw, it.dash, it.round)}{m}/>')
        if isinstance(it, Text):
            rot = f' transform="rotate({it.rot:g} {it.x:.1f} {it.y:.1f})"' if it.rot else ''
            fam = "Caveat,'Patrick Hand',cursive" if it.font == 'title' else "'Patrick Hand',Caveat,cursive"
            bw = ' font-weight="700"' if it.bold else ''
            return (f'<text x="{it.x:.1f}" y="{it.y:.1f}" font-size="{it.fs:g}" fill="{it.col}" text-anchor="{it.anchor}" '
                    f'font-family="{fam}"{bw}{rot}>{esc(it.s)}</text>')
        raise TypeError(it)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"{width_attr} role="img" aria-label="{esc(tag)}">\n<defs>'
            f'<pattern id="{uid}g" width="{GRID}" height="{GRID}" patternUnits="userSpaceOnUse"><path d="M{GRID} 0H0V{GRID}" fill="none" '
            f'stroke="{C["grid"]}" stroke-width="1"/></pattern>{marks}</defs>\n'
            f'<rect width="{W}" height="{H}" fill="{C["paper"]}"/><rect width="{W}" height="{H}" fill="url(#{uid}g)"/>\n'
            + '\n'.join(one(i) for i in items) + '\n</svg>')


# ------------------------------------------------------------------ back-end 2: python-pptx native shapes
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

class _Ctx:
    px = 9525.0
CTX = _Ctx()
def E(v): return Emu(int(round(v * CTX.px)))
def rgb(h): return RGBColor.from_string(h[1:])

def _alpha(parent_xml, op):
    if op == 1: return
    clr = parent_xml.find('.//' + qn('a:srgbClr'))
    etree.SubElement(clr, qn('a:alpha')).set('val', str(int(op * 100000)))

def _line(shape, stroke, sw, dash=False, arrow=False, rnd=False, op=1):
    ln = shape.line
    if not stroke:
        ln.fill.background(); return
    ln.color.rgb = rgb(stroke); ln.width = E(sw)
    lnx = ln._get_or_add_ln()
    _alpha(lnx, op)
    if dash: ln.dash_style = MSO_LINE.DASH
    if rnd: lnx.set('cap', 'rnd')
    if arrow:
        te = etree.SubElement(lnx, qn('a:tailEnd')); te.set('type', 'triangle'); te.set('w', 'lg'); te.set('len', 'lg')

def _fill(shape, fill, op=1):
    if fill:
        shape.fill.solid(); shape.fill.fore_color.rgb = rgb(fill); _alpha(shape._element.spPr, op)
    else:
        shape.fill.background()

def _nostyle(shape):
    """drop the theme style reference (it adds a soft shadow); fill and line are always set explicitly"""
    st = shape._element.find(qn('p:style'))
    if st is not None: shape._element.remove(st)

def pptx_add(shapes, it, counter):
    if isinstance(it, Group):
        g = shapes.add_group_shape(); g.name = it.name or 'group'
        for i in it.items: pptx_add(g.shapes, i, counter)
        counter['group'] += 1; return g
    counter['leaf'] += 1
    if isinstance(it, Rect):
        s = shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if it.rx else MSO_SHAPE.RECTANGLE, E(it.x), E(it.y), E(it.w), E(it.h))
        if it.rx: s.adjustments[0] = min(0.5, it.rx / max(1e-6, min(it.w, it.h)))
        _fill(s, it.fill, it.fill_op); _line(s, it.stroke, it.sw, it.dash)
    elif isinstance(it, Circle):
        s = shapes.add_shape(MSO_SHAPE.OVAL, E(it.cx - it.r), E(it.cy - it.r), E(2 * it.r), E(2 * it.r))
        _fill(s, it.fill, it.fill_op); _line(s, it.stroke, it.sw)
    elif isinstance(it, Line):
        s = shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(it.x1), E(it.y1), E(it.x2), E(it.y2))
        _line(s, it.stroke, it.sw, it.dash, it.arrow, it.round, it.op)
    elif isinstance(it, Poly):
        fb = shapes.build_freeform(E(it.pts[0][0]), E(it.pts[0][1]), scale=1.0)
        fb.add_line_segments([(E(x), E(y)) for x, y in it.pts[1:]], close=it.closed)
        s = fb.convert_to_shape()
        _fill(s, it.fill, it.fill_op); _line(s, it.stroke, it.sw, it.dash, it.arrow and not it.closed, it.round)
    elif isinstance(it, Text):
        _, _, upm, asc, desc = _font(it.font)
        tw = text_w(it.s, it.fs, it.font, it.bold) * 1.12 + 6
        th = (asc + desc) / upm * it.fs * 1.02
        top = it.y - asc / upm * it.fs
        left = {'start': it.x, 'middle': it.x - tw / 2, 'end': it.x - tw}[it.anchor]
        if it.rot:                                 # rotate the box about the text anchor (start anchor only)
            a = math.radians(it.rot); dx, dy = tw / 2, th / 2 - asc / upm * it.fs
            cx, cy = it.x + dx * math.cos(a) - dy * math.sin(a), it.y + dx * math.sin(a) + dy * math.cos(a)
            left, top = cx - tw / 2, cy - th / 2
        s = shapes.add_textbox(E(left), E(top), E(tw), E(th))
        if it.rot: s.rotation = it.rot % 360
        tf = s.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = False; tf.auto_size = MSO_AUTO_SIZE.NONE; tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = {'start': PP_ALIGN.LEFT, 'middle': PP_ALIGN.CENTER, 'end': PP_ALIGN.RIGHT}[it.anchor]
        r = p.add_run(); r.text = it.s
        f = r.font; f.size = Pt(it.fs * 0.75); f.name = FONT[it.font]; f.bold = it.bold; f.color.rgb = rgb(it.col)
        rPr = r._r.get_or_add_rPr()
        for tagn in ('a:ea', 'a:cs'):
            el = etree.SubElement(rPr, qn(tagn)); el.set('typeface', FONT[it.font])
    else:
        raise TypeError(it)
    s.name = it.name or type(it).__name__.lower()
    _nostyle(s)
    return s

def pptx_grid(slide):
    """thin pink grid lines, grouped and locked at the very back"""
    g = slide.shapes.add_group_shape(); g.name = 'background grid (locked)'
    for x in range(0, W + 1, GRID):
        c = g.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x), 0, E(x), E(H)); _line(c, C['grid'], 1); _nostyle(c)
    for y in range(0, H, GRID):
        c = g.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, 0, E(y), E(W), E(y)); _line(c, C['grid'], 1); _nostyle(c)
    locks = etree.SubElement(g._element.nvGrpSpPr.find(qn('p:cNvGrpSpPr')), qn('a:grpSpLocks'))
    for k in ('noGrp', 'noUngrp', 'noSelect', 'noRot', 'noChangeAspect', 'noMove', 'noResize'):
        locks.set(k, '1')
    sp_tree = slide.shapes._spTree; sp_tree.remove(g._element); sp_tree.insert(2, g._element)   # back of z-order
    return len(g.shapes)

def pptx_render(slide, items, slide_width_emu):
    """paper background + locked grid + all primitives as native shapes; returns counts"""
    CTX.px = slide_width_emu / W
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = rgb(C['paper'])
    ng = pptx_grid(slide)
    cnt = {'leaf': 0, 'group': 0}
    for it in items: pptx_add(slide.shapes, it, cnt)
    cnt['grid'] = ng
    return cnt
