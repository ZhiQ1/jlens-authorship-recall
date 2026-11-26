# "From experiments to the story" (2 parts) + contribution overview grid, 16:9, text >= 16 px. 2026-11-25.
# Data: contrib_data.py (from the final tree). Visual system: four colours, line-art pictograms (picto / picto2), no badges.
import html, re, subprocess, collections
import picto as P, picto2 as Q
import contrib_data as D

W, H = 1920, 1080
INK, DET, PALE = '#22304A', '#5A6372', '#A9AEB6'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
SYMCOL = {'Y': BLUE, 'X': RED, 'E': RED, 'U': GREYC, 'O': PALE}
SENTCOL = {'S1': GREEN, 'S2': GREYC, 'S3': BLUE, 'S4': GREEN, 'S5': GREEN, 'S6': GREEN, 'S7': GREEN}
TREECOL = {'Overview': '#EEF1F5', 'Phenomenon': '#EDE7F6', 'H1': '#E8F0FA', 'H2': '#FFF1DE', 'Route': '#E3F2EE',
           'H3': '#E8EEF8', 'Writing': '#FBE3E1', 'Audits': '#F1F1F1'}
OUT = 'deck16x9/'

def esc(s): return html.escape(s)
def tw(s, size): return 0.6 * size * len(s)

class Svg:
    def __init__(s): s.o = []; s.back = []
    def a(s, x): s.o.append(x)
    def txt(s, x, y, t, size=16, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
        st = ' font-style="italic"' if italic else ''
        s.a(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(t)}</text>')
    def box(s, x, y, w, h, stroke='#C9CED6', fill='#fff', sw=1.6, rx=10, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        s.a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
    def line(s, x1, y1, x2, y2, col=INK, w=2, op=1, arrow=False):
        m = f' marker-end="url(#ar{col[1:]})"' if arrow else ''
        s.back.append(f'<path d="M{x1:.1f} {y1:.1f} C{(x1+x2)/2:.1f} {y1:.1f} {(x1+x2)/2:.1f} {y2:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-opacity="{op}"{m}/>')
    def head(s):
        cols = (INK, BLUE, GREEN, GREYC, RED, PALE)
        mk = ''.join(f'<marker id="ar{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in cols)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">'
                f'<defs>{P.DEFS}{mk}</defs><rect width="{W}" height="{H}" fill="#FBFAF5"/>')
    def save(s, name):
        svg = s.head() + ''.join(s.back) + ''.join(s.o) + '</svg>'
        open(OUT + name + '.svg', 'w').write(svg)
        subprocess.run(['rsvg-convert', '-z', '2', '-b', '#FBFAF5', OUT + name + '.svg', '-o', OUT + name + '.png'], check=True)

def picto(name, x, y, w, h):
    """pictogram drawing only (internal labels stripped so no text falls below 16 px)"""
    f = getattr(P, name, None) or getattr(Q, name, None)
    if not f: return ''
    body = re.sub(r'<text\b.*?</text>', '', f(0, 0), flags=re.S)
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" viewBox="-6 -6 196 120" preserveAspectRatio="xMidYMid meet">{body}</svg>'

def symbol(s, x, y, k, size=20):
    """the contribution symbol as a coloured glyph"""
    s.txt(x, y, D.SYM[k], size, SYMCOL[k], 'middle', 'bold')

def legend(s, y):
    x = 40
    s.txt(x, y, 'Symbol:', 16, INK, weight='bold'); x += 82
    for k in 'YXEUO':
        symbol(s, x + 10, y + 1, k, 20); s.txt(x + 26, y, D.SYMNAME[k], 16, SYMCOL[k] if k != 'O' else GREYC); x += 46 + tw(D.SYMNAME[k], 16)
    s.txt(x + 10, y, '★ main line (thick line)', 16, INK, weight='bold')
    x2 = 40; y2 = y + 28
    s.txt(x2, y2, 'Sentence colour:', 16, INK, weight='bold'); x2 += 172
    for lab, c in (('proven by one experiment', BLUE), ('joint (several together)', GREEN), ('cannot be decided', GREYC), ('refuted / overturned', RED)):
        s.a(f'<rect x="{x2}" y="{y2-13}" width="14" height="14" rx="3" fill="{c}"/>'); s.txt(x2 + 20, y2, lab, 16, c, weight='bold'); x2 += 44 + tw(lab, 16)

def short(t, n):
    return t if len(t) <= n else t[:n-1] + '…'

# ---------------- figure a: experiments -> story (two parts) ----------------
def story_part(sids, name, title, part):
    s = Svg()
    s.txt(40, 52, title, 34, INK, fam=HAND)
    s.txt(40, 82, f'Part {part} of 2 · each band: the experiments (left) that build one sentence of the story (right) · thick = main line ★, thin = supporting', 17, DET)
    top, bot = 104, H - 96
    bh = (bot - top) / len(sids)
    SX, SW = 1440, 440                          # sentence card x / width
    for k, sid in enumerate(sids):
        sid_, short_, long_ = next(x for x in D.SENTENCES if x[0] == sid)
        y0 = top + k * bh
        if k: s.a(f'<line x1="40" y1="{y0:.1f}" x2="{W-40}" y2="{y0:.1f}" stroke="#E2E5EA" stroke-width="1.2"/>')
        sc = SENTCOL[sid]
        cy = y0 + bh / 2
        # sentence card
        ch = min(bh - 20, 190)
        s.box(SX, cy - ch/2, SW, ch, stroke=sc, fill='#fff', sw=3, rx=14)
        s.txt(SX + 18, cy - ch/2 + 34, sid, 18, sc, weight='bold')
        lines_ = wrapw(short_, SW - 70, 20)
        for j, ln in enumerate(lines_):
            s.txt(SX + 60, cy - ch/2 + 34 + j*25, ln, 20, sc, weight='bold')
        yy = cy - ch/2 + 34 + len(lines_)*25 + 6
        for ln in wrapw(long_, SW - 36, 16)[: max(1, int((cy + ch/2 - yy - 6) // 20))]:
            s.txt(SX + 18, yy, ln, 16, DET); yy += 20
        rows = [r for r in D.ROWS if r[5] == sid]
        stars = [r for r in rows if r[4]]
        sup = [r for r in rows if not r[4]]
        # star cards
        cw_, chh = min(300, (SX - 110 - 40 - 14 * (len(stars) - 1)) / max(1, len(stars))), min(bh * 0.50, 124)
        pw = 92 if cw_ >= 280 else 70
        cx = 40; busx = []; busy = 0
        for r in stars:
            yC = y0 + 12
            s.box(cx, yC, cw_, chh, stroke=SYMCOL[r[3]], fill=TREECOL[r[2]], sw=2.4, rx=10)
            if r[7]: s.a(picto(r[7], cx + 8, yC + 8, pw, chh - 16))
            tx = cx + (pw + 16 if r[7] else 14)
            symbol(s, tx + 8, yC + 26, r[3], 22); s.txt(tx + 24, yC + 26, '★ ' + r[2], 16, INK, weight='bold')
            for j, ln in enumerate(wrapw(r[1], cw_ - (tx - cx) - 10, 16)[:max(1, int((chh - 50) // 20) - 1)]):
                s.txt(tx, yC + 50 + j*20, ln, 16, INK)
            s.txt(tx, yC + chh - 10, 's. ' + r[0], 16, DET)
            s.back.append(f'<line x1="{cx+cw_/2:.1f}" y1="{yC+chh:.1f}" x2="{cx+cw_/2:.1f}" y2="{yC+chh+12:.1f}" stroke="{sc}" stroke-width="4.5"/>')
            busx.append(cx + cw_/2); busy = yC + chh + 12
            cx += cw_ + 14
        if busx:
            s.back.append(f'<line x1="{min(busx):.1f}" y1="{busy:.1f}" x2="{max(busx)+cw_/2+10:.1f}" y2="{busy:.1f}" stroke="{sc}" stroke-width="4.5"/>')
            s.line(max(busx) + cw_/2 + 10, busy, SX - 6, cy, col=sc, w=4.5, arrow=True)
        # supporting chips (by symbol, tree tag)
        chx, chy = 40, y0 + 12 + chh + 46
        for r in sorted(sup, key=lambda r: 'YEXU'.index(r[3]) if r[3] in 'YEXU' else 9):
            lab = short(r[1], 30)
            wch = tw(lab, 16) + 52
            if chx + wch > SX - 60:
                chx = 40; chy += 34
            if chy > y0 + bh - 8: break
            dash = '5 4' if r[3] == 'E' else None
            s.box(chx, chy - 22, wch, 30, stroke=SYMCOL[r[3]], fill=TREECOL[r[2]], sw=1.4, rx=8, dash=dash)
            symbol(s, chx + 16, chy - 1, r[3], 18)
            s.txt(chx + 30, chy, lab, 16, INK if r[3] != 'U' else GREYC)
            chx += wch + 10
        if sup:
            s.line(SX - 140, chy - 7, SX - 6, cy + 30, col=PALE, w=1.6, op=0.9, arrow=True)
            s.back.append(f'<line x1="40" y1="{chy-7:.1f}" x2="{SX-140:.1f}" y2="{chy-7:.1f}" stroke="{PALE}" stroke-width="1.6"/>')
        gap = D.GAPS.get(sid)
        if gap:
            gy = cy + ch/2 + 18
            for j, ln in enumerate(wrapw('? ' + gap, SW, 16)[:2]):
                if gy + j*19 < y0 + bh - 2: s.txt(SX, gy + j*19, ln, 16, GREYC, italic=True)
    legend(s, H - 58)
    if part == 2:
        nO = sum(1 for r in D.ROWS if r[3] == 'O'); nR = sum(1 for r in D.ROWS if not r[5] and r[3] != 'O')
        s.box(1500, H - 92, 380, 78, stroke='#DADDE2', fill='#F4F4F4', sw=1.2, rx=8)
        s.txt(1514, H - 66, f'○ {nO} minor / no contribution', 16, GREYC, weight='bold')
        s.txt(1514, H - 44, 'early small samples, method checks,', 16, '#9AA0A8')
        s.txt(1514, H - 22, f'infeasible designs · + {nR} robustness checks', 16, '#9AA0A8')
    s.save(name)

def wrapw(t, width, size):
    n = max(8, int(width / (0.6 * size))); out, cur = [], ''
    for w in t.split(' '):
        if len(cur) + len(w) + (1 if cur else 0) > n and cur: out.append(cur); cur = w
        else: cur = (cur + ' ' + w) if cur else w
    if cur: out.append(cur)
    return out

story_part(['S1', 'S2', 'S3', 'S4'], 'exp2story_a', 'From experiments to the story (1): recognised but not said → what is read', 1)

def part_b():
    story_part(['S5', 'S6', 'S7'], 'exp2story_b', 'From experiments to the story (2): delivered → held → written, stuck at writing', 2)
part_b()

# corner group for figure b (○ and robustness) is drawn on the overview grid below.

# ---------------- figure b: contribution overview grid ----------------
def overview():
    s = Svg()
    c = collections.Counter(r[3] for r in D.ROWS)
    s.txt(40, 52, 'What each experiment contributed: all 100, by tree', 34, INK, fam=HAND)
    # counts strip
    x = 40; y = 92
    for k in 'YXEUO':
        lab = f'{D.SYM[k]} {c[k]}  {D.SYMNAME[k]}'
        s.box(x, y - 26, tw(lab, 18) + 30, 36, stroke=SYMCOL[k], fill='#fff', sw=2, rx=8)
        s.txt(x + 14, y, lab, 18, SYMCOL[k] if k != 'O' else GREYC, weight='bold')
        x += tw(lab, 18) + 44
    s.txt(x + 4, y, f'★ main line: {sum(r[4] for r in D.ROWS)}', 18, INK, weight='bold')
    trees = D.TREES
    cols = len(trees); gx0, gw = 40, (W - 80) / cols
    rowh = 31; y0 = 140
    for i, t in enumerate(trees):
        x0 = gx0 + i * gw
        rs = [r for r in D.ROWS if r[2] == t]
        s.box(x0 + 3, y0, gw - 6, 36, stroke=TREECOL[t], fill=TREECOL[t], rx=8)
        ct = collections.Counter(r[3] for r in rs)
        s.txt(x0 + gw/2, y0 + 25, f'{t} ({len(rs)})', 17, INK, 'middle', 'bold')
        for j, r in enumerate(rs):
            yy = y0 + 46 + j * rowh
            fill = '#fff' if r[3] != 'O' else '#F4F4F4'
            s.box(x0 + 3, yy, gw - 6, rowh - 4, stroke=SYMCOL[r[3]] if r[3] != 'O' else '#DADDE2', fill=fill, sw=2.2 if r[4] else 1.1, rx=6,
                  dash='4 3' if r[3] == 'E' else None)
            symbol(s, x0 + 18, yy + 21, r[3], 18)
            px = x0 + 32
            if r[7]:
                s.a(picto(r[7], px, yy + 2, 40, rowh - 8)); px += 44
            lab = ('★ ' if r[4] else '') + r[1]
            room = int((x0 + gw - 10 - px) / (0.6 * 16))
            s.txt(px, yy + 20, short(lab, room), 16, INK if r[3] != 'O' else '#9AA0A8', weight='bold' if r[4] else 'normal')
        # per-tree tally
        tally = ' '.join(f'{D.SYM[k]}{ct[k]}' for k in 'YXEUO' if ct[k])
        s.txt(x0 + gw/2, y0 + 46 + len(rs) * rowh + 18, tally, 16, DET, 'middle')
    s.txt(40, H - 20, 'Cell border = symbol colour (bold border = ★ main line; dashed = excluded an alternative; grey cell = minor / no contribution). Symbols follow the tree\'s role labels; no new numbers.', 16, DET)
    s.save('contrib_overview')

overview()
print('ok')
