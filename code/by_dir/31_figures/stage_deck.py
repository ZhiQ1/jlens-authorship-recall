# 16:9 deck versions (1920x1080, text >= 16 px) of the stage-expansion figures, same template as stage_engine.py.
# A figure taller than one slide is split at row boundaries into parts (_a, _b, ...), each with the locator,
# the column headings, "(continued)" and the legend + three grey lines. Nothing is dropped. 2026-11-25.
import base64, html
from PIL import Image
import picto as P0, picto2 as P2
from stage_engine import COL, INK, DET, PALE_T, SANS, HAND, wrap, esc, b64

FLOOR = 16
_t0 = P0._t
def _t16(x, y, s, size=14, col=P0.INK, anchor='middle'): return _t0(x, y, s, max(size, FLOOR), col, anchor)
P0._t = _t16; P2._t = _t16                      # pictogram labels at >= 16 px

W, H = 1920, 1080
LC = (20, 370); CC = (400, 1520); RC = (1550, 1900)
MID = (CC[0] + CC[1]) / 2
TOP = 128; LIMIT = H - 128                      # content area per slide

class F16:
    def __init__(s): s.o = []
    def a(s, x): s.o.append(x)
    def txt(s, x, y, t, size=16, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
        size = max(size, FLOOR); st = ' font-style="italic"' if italic else ''
        s.a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(t)}</text>')
    def strike(s, x, y, t, size=16, anchor='start'):
        size = max(size, FLOOR); w = 0.53*size*len(t); x0 = x - (w/2 if anchor == 'middle' else 0)
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
    def _sz(s, it, size):
        fl = it[2] if len(it) > 2 else ''
        return max(size, FLOOR) + (1 if 'B' in fl and it[1] in 'bgxr' else 0), fl
    def rows(s, x, y, items, width, size=16, dy=None):
        for it in items:
            sz, fl = s._sz(it, size); d = dy or sz + 5
            for line in wrap(it[0], width, sz):
                if 'S' in fl: s.strike(x, y, line, sz)
                else: s.txt(x, y, line, sz, COL[it[1]], weight=('bold' if 'B' in fl else 'normal'), italic=('I' in fl))
                y += d
        return y
    def rows_h(s, items, width, size=16, dy=None):
        h = 0
        for it in items:
            sz, fl = s._sz(it, size); d = dy or sz + 5
            h += d*len(wrap(it[0], width, sz))
        return h

def exp_box(F, x, y, w, b, measure=False):
    wide = w > 440
    pw = b.get('picw', 180)
    tx, tw_ = (x + pw + 34, w - pw - 52) if wide else (x + 16, w - 32)
    det = [(t, 'd') for t in b.get('det', [])]
    th = 22*len(wrap(b['title'], tw_, 19.5)) + 4 + F.rows_h(det, tw_, 16) + 8 + F.rows_h(b['concl'], tw_, 16, 21)
    top = 18 if wide else 146
    h = max(top + th + 12, 166 if wide else 0)
    if measure: return h
    F.box(x, y, w, h, stroke=b.get('stroke', '#C9CED6'), sw=b.get('sw', 1.8), fill=b.get('fill', '#fff'))
    F.a(b['pic'](x+18, y+26) if wide else b['pic'](x + (w-180)/2, y+12))
    yy = y + (top + 14 if wide else top + 6)
    for line in wrap(b['title'], tw_, 19.5):
        F.txt(tx, yy, line, 18, INK, weight='bold'); yy += 22
    yy = F.rows(tx, yy+2, det, tw_, 16)
    F.rows(tx, yy+8, b['concl'], tw_, 16, 21)
    return h

def _merge(rows):                               # join consecutive plain rows of one colour into one paragraph
    out = []
    for it in rows:
        fl = it[2] if len(it) > 2 else ''
        pfl = (out[-1][2] if len(out[-1]) > 2 else '') if out else None
        if out and 'N' not in fl and 'N' not in pfl and out[-1][1] == it[1] and pfl == fl:
            out[-1] = (out[-1][0] + ' ' + it[0], it[1]) + ((fl,) if fl else ())
        else: out.append(tuple(it))
    return out
def side_item(F, x0, x1, y, it, measure=False):
    it = dict(it); it['rows'] = _merge(it['rows'])
    w = x1 - x0; tw_ = w - 28
    ph = it.get('pich', 110) if it.get('pic') else 0
    th = 21*len(wrap(it['title'], tw_, 17))
    h = 14 + ph + 6 + th + F.rows_h(it['rows'], tw_, 16) + 10
    if measure: return h
    F.box(x0, y, w, h, stroke=it.get('stroke', '#D5D9DF'), fill=it.get('fill', '#FBFBFC'), dash=it.get('dash'))
    if it.get('pic'): F.a(it['pic'](x0+14, y+10))
    yy = y + 14 + ph + 14
    for line in wrap(it['title'], tw_, 17):
        F.txt(x0+14, yy, line, 17, INK, weight='bold'); yy += 21
    F.rows(x0+14, yy, it['rows'], tw_, 16)
    return h

def _row_h(F, r):
    k = r['kind']
    if k == 'boxes':
        n = len(r['boxes']); gap = 18 if n > 2 else 26; bw = (CC[1]-CC[0]-(n-1)*gap)/n
        return max(exp_box(F, 0, 0, bw, b, True) for b in r['boxes'])
    if k == 'pill': return 50
    if k in ('joint', 'concl'): return 34 + 26*len(r['lines'])
    if k == 'over': return 40 + 30*len(r['new']) + 28*(len(r['old'])-1)
def _gap(rows, k):
    r = rows[k]; nxt = rows[k+1] if k+1 < len(rows) else None
    sp = 40
    if nxt and nxt['kind'] == 'boxes' and len(nxt['boxes']) > 1: sp = 60
    if r['kind'] == 'boxes' and len(r['boxes']) > 1: sp = max(sp, 56)
    if nxt and nxt['kind'] == 'boxes' and len(nxt['boxes']) > 1 and r['kind'] == 'boxes' and len(r['boxes']) > 1: sp = 84
    if r.get('lead'): sp += 20
    return sp

def render_deck(spec, stem):
    F = F16(); rows = spec['rows']; sides = spec.get('side', [])
    for r in rows: r['_h'] = _row_h(F, r)
    for it in sides: it['_h'] = side_item(F, *(LC if it['side'] == 'L' else RC), 0, it, True)
    # ---- partition rows into slides ----
    parts, cur, y = [], [], TOP + 40
    for k, r in enumerate(rows):
        sh = max([it['_h'] for it in sides if it['row'] == k] + [0])
        need = max(r['_h'], sh)
        if cur and y + need > LIMIT - 30:
            parts.append(cur); cur, y = [], TOP + 50
        cur.append(k); y += r['_h'] + _gap(rows, k)
    parts.append(cur)
    outs = []
    for pi, idx in enumerate(parts):
        F = F16(); a = F.a
        cont_in, cont_out = pi > 0, pi < len(parts) - 1
        r0 = rows[idx[0]]
        y = TOP + ((76 if (r0['kind'] == 'boxes' and len(r0['boxes']) > 1) else 50) if cont_in else 22)
        for j, k in enumerate(idx):
            rows[k]['_y'] = y; y += rows[k]['_h'] + _gap(rows, k)
        # side items in this part
        last = {'L': TOP + 4, 'R': TOP + 4}
        for it in [s for s in sides if s['row'] in idx]:
            yy = max(rows[it['row']]['_y'], last[it['side']] + 14); it['_y'] = yy; last[it['side']] = yy + it['_h']
        a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
        a('<defs>' + P0.DEFS + f'<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
          + ''.join(f'<marker id="as{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in set(COL.values())) + '</defs>')
        a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
        title = spec['title'] + (' (continued)' if cont_in else '')
        F.txt(24, 44, title, 30, INK, fam=HAND)
        if len(parts) > 1: F.txt(24, 74, f'part {pi+1} of {len(parts)} · read the main line top to bottom', 16, DET)
        else: F.txt(24, 74, 'read the main line top to bottom', 16, DET)
        # locator (top right)
        bx, by, gw, gh = W-214, 8, 120, 60
        F.box(bx, by, 196, 94, rx=8)
        gx0, gy0 = bx+10, by+8
        a(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="#F4F5F7" stroke="#D5D9DF"/>')
        cw, lh = gw/48, gh/64
        for c0, c1, col in ((0, 8, '#EEF1F5'), (9, 19, '#FFF1DE'), (20, 28, '#E8F0FA'), (29, 47, '#FBE3E1')):
            a(f'<rect x="{gx0+c0*cw}" y="{gy0}" width="{(c1-c0+1)*cw}" height="{gh}" fill="{col}"/>')
        c0, c1, l0, l1, fill, stroke = spec['loc']
        a(f'<rect x="{gx0+c0*cw}" y="{gy0+(63-l1)*lh}" width="{(c1-c0+1)*cw}" height="{(l1-l0+1)*lh}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        F.txt(gx0+gw+8, gy0+22, 'map', 16, PALE_T); F.txt(gx0+gw+8, gy0+42, 'locator', 16, PALE_T)
        F.txt(gx0, by+88, '▲ ' + spec['band'], 16, stroke, weight='bold')
        BOT = max([rows[k]['_y'] + rows[k]['_h'] for k in idx] + [it['_y'] + it['_h'] for it in sides if it['row'] in idx]) + 16
        if cont_out: BOT = max(BOT, rows[idx[-1]]['_y'] + rows[idx[-1]]['_h'] + 70)
        for xx in (LC[1]+15, RC[0]-15):
            a(f'<line x1="{xx}" y1="{TOP-20}" x2="{xx}" y2="{BOT}" stroke="#D5D9DF" stroke-width="1.4"/>')
        F.txt((LC[0]+LC[1])/2, TOP-2, 'Rewritten & ruled out', 16, PALE_T, 'middle', 'bold')
        F.txt(MID, TOP-2, 'Main line', 17, INK, 'middle', 'bold')
        F.txt((RC[0]+RC[1])/2, TOP-2, 'Exceptions & dependencies', 16, PALE_T, 'middle', 'bold')
        # incoming connector
        if cont_in:
            r0 = rows[idx[0]]
            F.txt(MID+14, TOP+30, '↓ from the previous slide', 16, DET, italic=True)
            if r0['kind'] == 'boxes' and len(r0['boxes']) > 1:
                n = len(r0['boxes']); gap = 18 if n > 2 else 26; bw = (CC[1]-CC[0]-(n-1)*gap)/n; yb = r0['_y'] - 20
                a(f'<line x1="{MID}" y1="{TOP+12}" x2="{MID}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
                a(f'<line x1="{CC[0]+bw/2}" y1="{yb}" x2="{CC[1]-bw/2}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
                for j in range(n):
                    cx = CC[0] + j*(bw+gap) + bw/2
                    a(f'<line x1="{cx}" y1="{yb}" x2="{cx}" y2="{r0["_y"]-4}" stroke="{INK}" stroke-width="2.6" marker-end="url(#am)"/>')
            else: F.down(TOP+12, r0['_y'])
        # rows
        for j, k in enumerate(idx):
            r = rows[k]; y, h, kind = r['_y'], r['_h'], r['kind']
            nxt = rows[idx[j+1]] if j+1 < len(idx) else None
            if kind == 'boxes':
                n = len(r['boxes']); gap = 18 if n > 2 else 26; bw = (CC[1]-CC[0]-(n-1)*gap)/n; r['_cx'] = []
                for jj, b in enumerate(r['boxes']):
                    bx_ = CC[0] + jj*(bw+gap); bh = exp_box(F, bx_, y, bw, b)
                    r['_cx'].append((bx_ + bw/2, y + bh))
                    if r.get('xcheck') and jj == 0:
                        yy = y + 40; gx1, gx2, gc = bx_+bw+3, bx_+bw+gap-3, COL['g']
                        a(f'<line x1="{gx1+8}" y1="{yy}" x2="{gx2-8}" y2="{yy}" stroke="{gc}" stroke-width="2.6"/><path d="M{gx1} {yy} l9 -6 v12 z M{gx2} {yy} l-9 -6 v12 z" fill="{gc}"/>')
            elif kind == 'pill':
                a(f'<rect x="{MID-300}" y="{y}" width="600" height="50" rx="25" fill="#FFF6E5" stroke="#D9772B" stroke-width="2.4"/>')
                F.txt(MID, y+32, r['text'], 19, INK, 'middle', 'bold')
            elif kind == 'joint':
                F.box(CC[0]+80, y, CC[1]-CC[0]-160, h, stroke=COL['g'], fill='#EAF6EC', sw=2.6)
                for jj, (t, bold) in enumerate(r['lines']): F.txt(MID, y+30+jj*26, t, 19 if bold else 17, COL['g'], 'middle', 'bold' if bold else 'normal')
            elif kind == 'concl':
                F.box(CC[0]+30, y, CC[1]-CC[0]-60, h, stroke=COL['g'], fill=spec.get('tint', '#FFF1DE'), sw=3)
                for jj, (t, bold) in enumerate(r['lines']): F.txt(MID, y+30+jj*26, t, 20 if bold else 17, COL['g'], 'middle', 'bold' if bold else 'normal')
            elif kind == 'over':
                F.box(CC[0]+50, y, CC[1]-CC[0]-100, h, stroke='#E3B5AF', fill='#FDF3F1', sw=2)
                yy = y + 30
                for t in r['old']: F.strike(CC[0]+72, yy, t, 17); yy += 28
                yy += 2
                for t in r['new']: F.txt(CC[0]+72, yy, t, 19, COL['r'], weight='bold'); yy += 30
            y2 = y + h
            last_row = nxt is None
            if kind == 'boxes' and len(r['boxes']) > 1 and not (last_row and not cont_out):
                nk = (nxt or (rows[k+1] if k+1 < len(rows) else None))
                mc = COL['g'] if (nk and nk['kind'] == 'joint') else INK
                for cx, bb in r['_cx']: a(f'<path d="M{cx} {bb} V {y2+24} H {MID}" fill="none" stroke="{mc}" stroke-width="3.2"/>')
                y2 += 24
            if last_row:
                if cont_out:
                    F.down(y2, y2 + 40)
                    F.txt(MID+14, y2 + 34, 'continues on the next slide ↓', 16, DET, italic=True)
                continue
            ny = nxt['_y']
            if nxt['kind'] == 'boxes' and len(nxt['boxes']) > 1:
                n = len(nxt['boxes']); gap = 18 if n > 2 else 26; bw = (CC[1]-CC[0]-(n-1)*gap)/n; yb = ny - 20
                a(f'<line x1="{MID}" y1="{y2}" x2="{MID}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
                a(f'<line x1="{CC[0]+bw/2}" y1="{yb}" x2="{CC[1]-bw/2}" y2="{yb}" stroke="{INK}" stroke-width="3.2"/>')
                for jj in range(n):
                    cx = CC[0] + jj*(bw+gap) + bw/2
                    a(f'<line x1="{cx}" y1="{yb}" x2="{cx}" y2="{ny-4}" stroke="{INK}" stroke-width="2.6" marker-end="url(#am)"/>')
                if r.get('lead'): F.txt(MID+14, y2+20, r['lead'], 16, DET, italic=True)
            else:
                F.down(y2, ny)
                if r.get('lead'): F.txt(MID+14, (y2+ny)/2+6, r['lead'], 16, DET, italic=True)
        # side items
        for it in [s for s in sides if s['row'] in idx]:
            r = rows[it['row']]; col = it['side']; x0, x1 = (LC if col == 'L' else RC)
            side_item(F, x0, x1, it['_y'], it)
            ay = max(it['_y'] + 28, min(it['_y'] + it['_h'] - 18, r['_y'] + min(r['_h'], 140)/2))
            ay = max(min(ay, r['_y'] + r['_h'] - 10), r['_y'] + 10)
            ac = COL[it.get('arrow', 'p')]
            k_ = r['kind']
            ex0, ex1 = {'boxes': (CC[0], CC[1]), 'pill': (MID-300, MID+300), 'joint': (CC[0]+80, CC[1]-80), 'concl': (CC[0]+30, CC[1]-30)}.get(k_, (CC[0]+50, CC[1]-50))
            sy = min(max(ay, it['_y'] + 18), it['_y'] + it['_h'] - 12)
            if col == 'L':
                if abs(sy-ay) > 2: a(f'<path d="M{x1} {sy} H {x1+14} V {ay}" fill="none" stroke="{ac}" stroke-width="2.2"/>'); F.harrow(x1+14, ex0-4, ay, ac, it.get('dash'))
                else: F.harrow(x1, ex0-4, ay, ac, it.get('dash'))
            else:
                if abs(sy-ay) > 2: a(f'<path d="M{x0} {sy} H {x0-14} V {ay}" fill="none" stroke="{ac}" stroke-width="2.2"/>'); F.harrow(x0-14, ex1+4, ay, ac, it.get('dash'))
                else: F.harrow(x0, ex1+4, ay, ac, it.get('dash'))
        # footer: legend + three grey lines
        LY = H - 96
        F.txt(24, LY, 'Colour of a conclusion:', 16, INK, weight='bold')
        xx = 252
        for lab, k_ in (('proven by one experiment', 'b'), ('joint (only with several together)', 'g'), ('cannot be decided', 'x'), ('refuted / overturned (old claim struck in grey)', 'r')):
            a(f'<rect x="{xx}" y="{LY-13}" width="15" height="15" rx="3" fill="{COL[k_]}"/>'); F.txt(xx+22, LY, lab, 16, COL[k_], weight='bold'); xx += 40 + 9.6*len(lab)
        fx = 24
        for key in ('tex_f', 'tex_n'):
            im = Image.open(spec[key]); w, h = im.size[0]*0.46, im.size[1]*0.46
            a(f'<image x="{fx}" y="{H-80}" width="{w}" height="{h}" xlink:href="{b64(spec[key])}"/>'); fx += w + 30
        F.txt(24, H-16, spec['reading'], 16, PALE_T)
        a('</svg>')
        suf = '' if len(parts) == 1 else '_' + 'abcdef'[pi]
        fn = f'deck16x9/{stem}_16x9{suf}.svg'
        open(fn, 'w').write('\n'.join(F.o)); outs.append((fn, BOT))
    return outs
