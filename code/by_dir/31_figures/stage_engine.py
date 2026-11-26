# Stage-expansion figures on the L24–L40 v2 template: three columns (rewritten & ruled out | main line | exceptions &
# dependencies), main line top-down, side items joined by short arrows, a pictogram per experiment box, four colours,
# a locator map, three grey lines. 2026-11-25.
import base64, html
from PIL import Image
import picto as P0

INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
COL = dict(b='#1F3A6B', g='#2E7D46', x='#6A7385', r='#C0392B', d='#5A6372', p='#8A8F98')
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
W = 1900
LC = (24, 384); CC = (420, 1480); RC = (1516, 1876)
MID = (CC[0] + CC[1]) / 2
CHW = 0.57                                           # char width / font size (DejaVu Sans estimate)

def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def wrap(s, width, size):
    n = max(8, int(width / (CHW*size))); out, cur = [], ''
    for w in s.split(' '):
        if len(cur) + len(w) + (1 if cur else 0) > n and cur: out.append(cur); cur = w
        else: cur = (cur + ' ' + w) if cur else w
    if cur: out.append(cur)
    return out

class Fig:
    def __init__(s): s.o = []
    def a(s, x): s.o.append(x)
    def txt(s, x, y, t, size=15, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
        st = ' font-style="italic"' if italic else ''
        s.a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(t)}</text>')
    def strike(s, x, y, t, size=15, anchor='start'):
        w = 0.53*size*len(t); x0 = x - (w/2 if anchor == 'middle' else 0)
        s.txt(x, y, t, size, '#9AA3AE', anchor, italic=True)
        s.a(f'<line x1="{x0-2}" x2="{x0+w+2}" y1="{y-size*0.33}" y2="{y-size*0.33}" stroke="#9AA3AE" stroke-width="1.8"/>')
    def box(s, x, y, w, h, stroke='#C9CED6', fill='#fff', sw=1.8, rx=12, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def down(s, y1, y2, x=MID, sw=3.2):
        s.a(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2-4}" stroke="{INK}" stroke-width="{sw}" marker-end="url(#am)"/>')
    def harrow(s, x1, x2, y, col, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="2.2"{d} marker-end="url(#as{col[1:]})"/>')

    # rows of text: items are (text, kind[, flags]) with kind in COL; flags: 'B' bold, 'I' italic, 'S' struck
    def rows(s, x, y, items, width, size=14, dy=None):
        dy = dy or size + 5
        for it in items:
            t, k = it[0], it[1]; fl = it[2] if len(it) > 2 else ''
            sz = size + (1 if 'B' in fl and k in 'bgxr' else 0)
            for line in wrap(t, width, sz):
                if 'S' in fl: s.strike(x, y, line, sz)
                else: s.txt(x, y, line, sz, COL[k], weight=('bold' if 'B' in fl else 'normal'), italic=('I' in fl))
                y += dy
        return y
    def rows_h(s, items, width, size=14, dy=None):
        dy = dy or size + 5; h = 0
        for it in items:
            fl = it[2] if len(it) > 2 else ''
            sz = size + (1 if 'B' in fl and it[1] in 'bgxr' else 0)
            h += dy*len(wrap(it[0], width, sz))
        return h

def exp_box(F, x, y, w, b, measure=False):
    """b = dict(pic, title, det=[str], concl=[items])  -> height"""
    wide = w > 420
    if wide:
        tx, tw_ = x + 210, w - 230
    else:
        tx, tw_ = x + 16, w - 32
    det = [(t, 'd') for t in b.get('det', [])]
    th = F.rows_h([(b['title'], 'b', 'B')], tw_, 16) + 6 + F.rows_h(det, tw_, 14) + 10 + F.rows_h(b['concl'], tw_, 14, 20)
    top = 22 if wide else 150
    h = max(top + th + 14, 170 if wide else 0)
    if measure: return h
    F.box(x, y, w, h, stroke=b.get('stroke', '#C9CED6'), sw=b.get('sw', 1.8), fill=b.get('fill', '#fff'))
    if wide: F.a(b['pic'](x+18, y+30))
    else: F.a(b['pic'](x + (w-180)/2, y+16))
    yy = y + (top + 12 if wide else top + 4)
    for line in wrap(b['title'], tw_, 16):
        F.txt(tx, yy, line, 16, INK, weight='bold'); yy += 21
    yy = F.rows(tx, yy+2, det, tw_, 14)
    F.rows(tx, yy+10, b['concl'], tw_, 14, 20)
    return h

def side_item(F, x0, x1, y, it, measure=False):
    w = x1 - x0; tw_ = w - 32
    ph = it.get('pich', 110) if it.get('pic') else 0
    body = [(it['title'], 'b', 'B')] + it['rows']
    h = 16 + ph + F.rows_h(body, tw_, 14) + 12
    if measure: return h
    F.box(x0, y, w, h, stroke=it.get('stroke', '#D5D9DF'), fill=it.get('fill', '#FBFBFC'), dash=it.get('dash'))
    if it.get('pic'): F.a(it['pic'](x0+16, y+12))
    yy = F.rows(x0+16, y+16+ph+14, [(it['title'], 'b', 'B')][:0] or [], tw_)
    yy = y + 16 + ph + 14
    for line in wrap(it['title'], tw_, 15):
        F.txt(x0+16, yy, line, 15, INK, weight='bold'); yy += 20
    F.rows(x0+16, yy, it['rows'], tw_, 14)
    return h

def render(spec, out):
    F = Fig(); a = F.a
    TOP = 200
    # ---------- main line layout (measure first) ----------
    rows = spec['rows']; y = TOP + 14; placed = []
    for k, r in enumerate(rows):
        kind = r['kind']
        if kind == 'boxes':
            n = len(r['boxes']); gap = 20 if n > 2 else 30
            bw = (CC[1]-CC[0]-(n-1)*gap)/n
            h = max(exp_box(F, 0, 0, bw, b, True) for b in r['boxes'])
        elif kind == 'pill': h = 52
        elif kind in ('joint', 'concl'): h = 40 + 26*len(r['lines'])
        elif kind == 'over': h = 44 + 30*len(r['new']) + 28*len(r['old']) - 28
        placed.append((y, h)); r['_y'], r['_h'] = y, h
        nxt = rows[k+1]['kind'] if k+1 < len(rows) else None
        lead = r.get('lead')
        sp = 52 if (kind == 'boxes' and nxt == 'boxes') else 48
        if nxt == 'boxes' and len(rows[k+1]['boxes']) > 1 and kind != 'boxes': sp = 72
        if kind == 'boxes' and len(r['boxes']) > 1: sp = max(sp, 64)
        if lead: sp += 22
        y += h + sp + r.get('pad', 0)
    # side items: place top-aligned with their row, pushed down if needed; grow the row gap if they spill
    for col in ('L', 'R'):
        last = TOP + 4
        for it in [i for i in spec.get('side', []) if i['side'] == col]:
            r = rows[it['row']]
            x0, x1 = (LC if col == 'L' else RC)
            h = side_item(F, x0, x1, 0, it, True)
            yy = max(r['_y'] + it.get('dy', 0), last + 16)
            it['_y'], it['_h'] = yy, h; last = yy + h
    BOT = max(y, max([i['_y']+i['_h'] for i in spec.get('side', [])] + [0]) + 30)
    H = int(BOT + 165)
    a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
    a('<defs>' + P0.DEFS + f'<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
      + ''.join(f'<marker id="as{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in set(COL.values())) + f'<marker id="xg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{COL["g"]}"/></marker></defs>')
    a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
    # title + locator
    F.txt(250, 52, spec['title'], 32, INK, fam=HAND)
    F.txt(250, 82, 'Read top to bottom along the main line; side columns hold what was rewritten or ruled out (left) and exceptions and dependencies (right).', 15, DET)
    lx, ly = 24, 20; gx0, gy0, gw, gh = lx+12, ly+28, 186, 92
    F.box(lx, ly, 210, 150, rx=8)
    F.txt(lx+12, ly+20, 'where on the main map', 14, PALE_T)
    a(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="#F4F5F7" stroke="#D5D9DF"/>')
    cw, lh = gw/48, gh/64
    for c0, c1, col in ((0, 8, '#EEF1F5'), (9, 19, '#FFF1DE'), (20, 28, '#E8F0FA'), (29, 47, '#FBE3E1')):
        a(f'<rect x="{gx0+c0*cw}" y="{gy0}" width="{(c1-c0+1)*cw}" height="{gh}" fill="{col}"/>')
    c0, c1, l0, l1, fill, stroke = spec['loc']
    a(f'<rect x="{gx0+c0*cw}" y="{gy0+(63-l1)*lh}" width="{(c1-c0+1)*cw}" height="{(l1-l0+1)*lh}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    F.txt(gx0, gy0+gh+18, '▲ ' + spec['band'] + ' (outlined)', 14, stroke)
    # column dividers + headings
    for xx in (LC[1]+18, RC[0]-18):
        a(f'<line x1="{xx}" y1="{TOP-26}" x2="{xx}" y2="{BOT}" stroke="#D5D9DF" stroke-width="1.4"/>')
    F.txt((LC[0]+LC[1])/2, TOP-8, 'Rewritten & ruled out', 15, PALE_T, 'middle', 'bold')
    F.txt(MID, TOP-8, 'Main line', 16, INK, 'middle', 'bold')
    F.txt((RC[0]+RC[1])/2, TOP-8, 'Exceptions & dependencies', 15, PALE_T, 'middle', 'bold')
    # ---------- draw main rows ----------
    for k, r in enumerate(rows):
        y, h, kind = r['_y'], r['_h'], r['kind']
        nxt = rows[k+1] if k+1 < len(rows) else None
        if kind == 'boxes':
            n = len(r['boxes']); gap = 20 if n > 2 else 30; bw = (CC[1]-CC[0]-(n-1)*gap)/n
            r['_cx'] = []
            for j, b in enumerate(r['boxes']):
                bx = CC[0] + j*(bw+gap); bh = exp_box(F, bx, y, bw, b, True)
                b2 = dict(b); exp_box(F, bx, y, bw, b2)
                r['_cx'].append((bx + bw/2, y + bh))
                if r.get('xcheck') and j == 0:   # double arrow between two boxes: opposite directions, same answer
                    yy = y + 40
                    gx1, gx2, gc = bx+bw+3, bx+bw+gap-3, COL['g']
                    a(f'<line x1="{gx1+8}" y1="{yy}" x2="{gx2-8}" y2="{yy}" stroke="{gc}" stroke-width="2.6"/>'
                      f'<path d="M{gx1} {yy} l9 -6 v12 z M{gx2} {yy} l-9 -6 v12 z" fill="{gc}"/>')
        elif kind == 'pill':
            a(f'<rect x="{MID-300}" y="{y}" width="600" height="52" rx="26" fill="#FFF6E5" stroke="#D9772B" stroke-width="2.4"/>')
            F.txt(MID, y+33, r['text'], 18, INK, 'middle', 'bold')
        elif kind == 'joint':
            F.box(CC[0]+100, y, CC[1]-CC[0]-200, h, stroke=COL['g'], fill='#EAF6EC', sw=2.6)
            for j, (t, bold) in enumerate(r['lines']):
                F.txt(MID, y+32+j*26, t, 18 if bold else 16, COL['g'], 'middle', 'bold' if bold else 'normal')
        elif kind == 'concl':
            F.box(CC[0]+40, y, CC[1]-CC[0]-80, h, stroke=COL['g'], fill=spec.get('tint', '#FFF1DE'), sw=3)
            for j, (t, bold) in enumerate(r['lines']):
                F.txt(MID, y+32+j*26, t, 19 if bold else 16, COL['g'], 'middle', 'bold' if bold else 'normal')
        elif kind == 'over':
            F.box(CC[0]+60, y, CC[1]-CC[0]-120, h, stroke='#E3B5AF', fill='#FDF3F1', sw=2)
            yy = y + 32
            for t in r['old']: F.strike(CC[0]+84, yy, t, 16); yy += 28
            yy += 4
            for t in r['new']: F.txt(CC[0]+84, yy, t, 18, COL['r'], weight='bold'); yy += 30
        # connector to next row
        if nxt is None: continue
        ny = nxt['_y']; y2 = y + h
        if kind == 'boxes' and len(r['boxes']) > 1:
            merge_col = COL['g'] if nxt['kind'] == 'joint' else INK
            for cx, by in r['_cx']:
                a(f'<path d="M{cx} {by} V {y2+26} H {MID}" fill="none" stroke="{merge_col}" stroke-width="3.2"/>')
            y2 += 26
        if nxt['kind'] == 'boxes' and len(nxt['boxes']) > 1:
            n = len(nxt['boxes']); gap = 20 if n > 2 else 30; bw = (CC[1]-CC[0]-(n-1)*gap)/n
            yb = ny - 22
            a(f'<line x1="{MID}" y1="{y2}" x2="{MID}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
            a(f'<line x1="{CC[0]+bw/2}" y1="{yb}" x2="{CC[1]-bw/2}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
            for j in range(n):
                cx = CC[0] + j*(bw+gap) + bw/2
                a(f'<line x1="{cx}" y1="{yb}" x2="{cx}" y2="{ny-4}" stroke="{INK}" stroke-width="2.6" marker-end="url(#am)"/>')
            if r.get('lead'): F.txt(MID+14, y2+22, r['lead'], 15, DET, italic=True)
        else:
            F.down(y2, ny)
            if r.get('lead'): F.txt(MID+14, (y2+ny)/2+5, r['lead'], 15, DET, italic=True)
    # ---------- side items ----------
    for it in spec.get('side', []):
        r = rows[it['row']]; col = it['side']
        x0, x1 = (LC if col == 'L' else RC)
        side_item(F, x0, x1, it['_y'], it)
        ay = max(it['_y'] + 30, min(it['_y'] + it['_h'] - 20, r['_y'] + min(r['_h'], 140)/2))
        ay = min(ay, r['_y'] + r['_h'] - 10); ay = max(ay, r['_y'] + 10)
        ac = COL[it.get('arrow', 'p')]
        # main-line edge at this row
        if r['kind'] == 'boxes':
            ex0, ex1 = CC[0], CC[1]
        elif r['kind'] == 'pill': ex0, ex1 = MID-300, MID+300
        elif r['kind'] == 'joint': ex0, ex1 = CC[0]+100, CC[1]-100
        elif r['kind'] == 'concl': ex0, ex1 = CC[0]+40, CC[1]-40
        else: ex0, ex1 = CC[0]+60, CC[1]-60
        sy = min(max(ay, it['_y'] + 20), it['_y'] + it['_h'] - 14)
        if col == 'L':
            if abs(sy - ay) > 2: a(f'<path d="M{x1} {sy} H {x1+18} V {ay}" fill="none" stroke="{ac}" stroke-width="2.2"/>'); F.harrow(x1+18, ex0-4, ay, ac, it.get('dash'))
            else: F.harrow(x1, ex0-4, ay, ac, it.get('dash'))
        else:
            if abs(sy - ay) > 2: a(f'<path d="M{x0} {sy} H {x0-18} V {ay}" fill="none" stroke="{ac}" stroke-width="2.2"/>'); F.harrow(x0-18, ex1+4, ay, ac, it.get('dash'))
            else: F.harrow(x0, ex1+4, ay, ac, it.get('dash'))
    # ---------- legend + grey lines ----------
    LY = BOT + 28
    F.txt(24, LY, 'Colour of a conclusion:', 15, INK, weight='bold')
    xx = 236
    for lab, k in (('proven by one experiment', 'b'), ('joint (only with several together)', 'g'), ('cannot be decided', 'x'), ('refuted / overturned (old claim struck in grey)', 'r')):
        a(f'<rect x="{xx}" y="{LY-13}" width="16" height="16" rx="3" fill="{COL[k]}"/>'); F.txt(xx+24, LY, lab, 14.5, COL[k], weight='bold')
        xx += 40 + 9.2*len(lab)
    yy = LY + 14
    for key in ('tex_f', 'tex_n'):
        im = Image.open(spec[key]); w, h = im.size[0]/2, im.size[1]/2
        a(f'<image x="24" y="{yy}" width="{w}" height="{h}" xlink:href="{b64(spec[key])}"/>'); yy += h + 6
    F.txt(24, yy+16, spec['reading'], 14, PALE_T)
    a('</svg>')
    open(out, 'w').write('\n'.join(F.o))
    return W, H
