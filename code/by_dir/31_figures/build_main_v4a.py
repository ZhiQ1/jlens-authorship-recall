# Story figure, MAIN view v4 (2026-11-25): back to the v1 approach (labels drawn on the plot, annotated map),
# plus the information flow (pipes title -> ":" -> names, three nodes, padlock, broken-pipe gaps).
# Built on build_main.py (v1). Content only from 27_v67/experiment_tree.md; no new numbers.
import base64, html

TOKS = ['Who', ' are', ' the', ' authors', ' of', ' the', ' paper', ' titled', ' "', 'A', 'ffect', ' dynamics', ',', ' bere', 'av',
        'ement', ' and', ' resilience', ' to', ' loss', '"', ' (', '2', '0', '0', '7', ')?↵', 'Authors', ':', ' Kar', 'in', ' G', '.',
        ' Co', 'if', 'man', ',', ' George', ' A', '.', ' Bon', 'anno', ',', ' E', 'sh', 'kol', ' Rafael', 'i']
GRP = [0]*9 + [1]*11 + [2]*9 + [3]*19
GNAME = ['the question', 'the title (11 tokens)', 'after the title', 'the author names (every token scored)']
GCOL = ['#EEF1F5', '#FFF1DE', '#E8F0FA', '#FBE3E1']
N = len(TOKS)
CW, X0, Y0, LH = 30, 112, 300, 14.0
GR = X0 + CW*N                                   # right edge of the grid (1552)
RX = GR + 110                                     # right column x
W = RX + 560
INK, DET, GREY = '#22304A', '#5A6372', '#8a8f98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
PIPE = '#1F6F8B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"

def X(i): return X0 + i*CW
def Y(l): return Y0 + (63 - l)*LH                # top edge of layer l's row
def YM(l): return Y(l) + LH/2
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
PB = Y(0) + LH                                   # plot bottom
H = int(PB + 400)

o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
  '<line x1="0" y1="0" x2="0" y2="8" stroke="#3C78B4" stroke-width="2.2" opacity=".30"/></pattern></defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')

def rect(c0, c1, l0, l1, fill, op=1, stroke='none', dash=None, sw=1.6, rx=3):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(c0)}" y="{Y(l1)}" width="{X(c1+1)-X(c0)}" height="{(l1-l0+1)*LH}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x, y, s, size=14, col=INK, anchor='start', weight='normal', italic=False, fam=SANS, halo=False):
    st = ' font-style="italic"' if italic else ''
    if halo:
        a(f'<text x="{x}" y="{y}" font-size="{size}" fill="#FBFAF5" stroke="#FBFAF5" stroke-width="5" stroke-linejoin="round" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def tw(s, size): return 0.6*size*len(s)
def struck(x, y, s, size=14, anchor='start'):
    w = tw(s, size)*0.95; x0 = x - (w/2 if anchor == 'middle' else 0)
    txt(x, y, s, size, '#9AA3AE', anchor, italic=True)
    a(f'<line x1="{x0-2}" x2="{x0+w+2}" y1="{y-size*0.32}" y2="{y-size*0.32}" stroke="#9AA3AE" stroke-width="1.8"/>')
def step(n, x, y, col, r=13):
    a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/><text x="{x}" y="{y+5}" font-size="15" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')
def pipe(x1, y1, x2, y2, w=8, col=PIPE, inner='#DCEFF5', head=False):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
      f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{inner}" stroke-width="{w-4}" stroke-linecap="round"/>')
    if head:
        a(f'<path d="M{x2+1} {y2-7} L{x2+11} {y2} L{x2+1} {y2+7} Z" fill="{col}"/>')
def broken_h(x1, x2, y, label='?'):              # horizontal broken pipe (known gap)
    mid = (x1 + x2)/2
    pipe(x1, y, mid-16, y, 8, GREYC, '#EEF0F3'); pipe(mid+16, y, x2, y, 8, GREYC, '#EEF0F3')
    a(f'<path d="M{mid-14} {y-9} l4 6 l-4 6 l4 6 M{mid+14} {y-9} l-4 6 l4 6 l-4 6" fill="none" stroke="{GREYC}" stroke-width="2"/>')
    txt(mid, y-14, label, 22, GREYC, 'middle', 'bold')
def broken_v(x, y1, y2, label='?'):              # vertical broken pipe (y1 < y2)
    mid = (y1 + y2)/2
    pipe(x, y1, x, mid-14, 8, GREYC, '#EEF0F3'); pipe(x, mid+14, x, y2, 8, GREYC, '#EEF0F3')
    a(f'<path d="M{x-9} {mid-12} l6 4 l6 -4 l6 4 M{x-9} {mid+12} l6 -4 l6 4 l6 -4" fill="none" stroke="{GREYC}" stroke-width="2"/>')
    txt(x+16, mid+8, label, 22, GREYC, 'start', 'bold')
def leader(x1, y1, x2, y2, col='#B8BEC8'):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.4"/><circle cx="{x1}" cy="{y1}" r="3" fill="{col}"/>')
def padlock(cx, cy, col=RED):
    a(f'<path d="M{cx-7} {cy-2} v-6 a7 7 0 0 1 14 0 v6" fill="none" stroke="{col}" stroke-width="2.6"/>'
      f'<rect x="{cx-11}" y="{cy-3}" width="22" height="17" rx="3" fill="#fff" stroke="{col}" stroke-width="2.6"/>'
      f'<circle cx="{cx}" cy="{cy+5}" r="2.4" fill="{col}"/>')
def marker(x, y, sym, k, col):                   # small numbered marker on the plot (◉ readout / ▲ intervention)
    a(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{col}" stroke-width="2"/>')
    txt(x, y+5, k, 14, col, 'middle', 'bold')
    txt(x+15, y+5, sym, 14, col)

# ---------- title ----------
txt(24, 48, 'Read early, said late: the whole story on one map', 36, INK, fam=HAND)
txt(24, 78, 'x: the prompt as real Qwen3 tokens · y: layers L0 (bottom) to L63 (top) · follow the blue pipes from the title to the numbered nodes 1 → 2 → 3 and the padlock.', 15, DET)

# ---------- token header (v1 style) + book over the title ----------
for g in range(4):
    c0 = GRP.index(g); c1 = len(GRP) - 1 - GRP[::-1].index(g)
    txt((X(c0)+X(c1+1))/2, Y0-126, GNAME[g], 15, DET, 'middle')
    a(f'<line x1="{X(c0)+3}" x2="{X(c1+1)-3}" y1="{Y0-118}" y2="{Y0-118}" stroke="#c9ced6" stroke-width="1.5"/>')
bx0, bx1, by = X(9)+40, X(20)-40, Y0-188
mx = (bx0 + bx1)/2
a(f'<path d="M{bx0} {by+10} Q {(bx0+mx)/2} {by-6} {mx} {by+8} Q {(mx+bx1)/2} {by-6} {bx1} {by+10} V {by+36} Q {(mx+bx1)/2} {by+22} {mx} {by+34} Q {(bx0+mx)/2} {by+22} {bx0} {by+36} Z" '
  f'fill="#FFF1DE" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/><line x1="{mx}" y1="{by+8}" x2="{mx}" y2="{by+34}" stroke="{INK}" stroke-width="1.8"/>')
txt(bx1+14, by+28, 'the paper the model has to recognise', 15, INK, fam=HAND)
for i, (t, g) in enumerate(zip(TOKS, GRP)):
    if g == 3:
        a(f'<rect x="{X(i)+2}" y="{Y0-108}" width="{CW-4}" height="100" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    else:
        a(f'<rect x="{X(i)+1}" y="{Y0-108}" width="{CW-2}" height="100" rx="4" fill="{GCOL[g]}" stroke="#c9ced6"/>')
    cx, cy = X(i) + CW/2 + 5, Y0 - 16
    wt = 'bold' if (g == 3 or t == ':') else 'normal'
    a(f'<text x="{cx}" y="{cy}" font-size="14" font-weight="{wt}" fill="{INK}" transform="rotate(-90 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')

# ---------- layer grid ----------
for l in range(0, 64, 4):
    a(f'<line x1="{X0}" x2="{GR}" y1="{Y(l)+LH}" y2="{Y(l)+LH}" stroke="#e6e9ee" stroke-width="1"/>')
for l in (0, 4, 8, 16, 24, 32, 40, 48, 52, 56, 63):
    txt(X0-8, Y(l)+LH-2, f'L{l}', 14, GREY, 'end')
a(f'<rect x="{X0}" y="{Y(63)}" width="{GR-X0}" height="{64*LH}" fill="none" stroke="#c9ced6"/>')

# ---------- stage blocks, aligned to their layer bands ----------
# ① L0–L4, every position: the words decide
rect(0, N-1, 0, 4, '#DDE2E8', .8)
txt(X(0)+10, Y(2)+10, 'identical words → identical states: same title under two questions, cos ≈ 1.00 at L4 — the ceiling every later test is measured above', 14, BLUE)
step('①', X0-60, YM(2), '#6A7385')
# ② L5–L23, title: read-in only (lighter, dashed outline)
rect(9, 19, 5, 23, '#FFF6E8', 1, '#D9A15A', '6 4', 1.8)
txt(X(9)+8, Y(22)+12, 'read-in only (not yet the title', 14, '#8a5a12', weight='bold')
txt(X(9)+8, Y(22)+30, 'being read): from L8 the words', 14, '#8a5a12')
txt(X(9)+8, Y(22)+48, 'are encoded beyond their form', 14, BLUE)
a(f'<polygon points="{X(19)+CW/2},{Y(8)-4} {X(19)+CW/2+7},{Y(8)+9} {X(19)+CW/2-7},{Y(8)+9}" fill="{BLUE}"/>')
txt(X(20)+6, Y(9)+2, '★ L8: small surname', 14, BLUE, weight='bold')
txt(X(20)+6, Y(9)+20, 'signal beyond topic', 14, BLUE)
txt(X(20)+6, Y(9)+38, '(+0.05; 2 of 3 tests', 14, GREYC)
txt(X(20)+6, Y(9)+56, 'marginal)', 14, GREYC)
step('②', X0-60, YM(14), '#B54708')
# ":" column: follows the question
rect(28, 28, 4, 56, 'none', 1, BLUE, '5 3', 2)
txt(X(20)+6, Y(20)+4, '":" follows the', 14, BLUE)
txt(X(20)+6, Y(20)+22, 'question (4.7× at L4)', 14, BLUE)
# ③ L24–L40, title: meaning + specific words
rect(9, 19, 24, 40, '#FFC98A', .9)
txt(X(9)+8, Y(39)+8, 'title read, L24 →', 15, INK, weight='bold')
txt(X(9)+8, Y(37)+8, 'meaning + specific words', 14, GREEN, weight='bold')
txt(X(9)+8, Y(35)+8, '(four tests together)', 14, GREEN)
txt(X(9)+8, Y(32)+8, 'made-up title, same meaning:', 14, BLUE)
txt(X(9)+8, Y(30)+8, 'brings back ~75%', 14, BLUE, weight='bold')
struck(X(9)+8, Y(27)+8, 'stores which paper this is', 14)
txt(X(9)+8, Y(25)+8, '→ not paper identity', 14, RED, weight='bold')
step('③', X0-60, YM(32), '#D9772B')
# divider at L40/L41
a(f'<line x1="{X(9)-6}" y1="{Y(40)}" x2="{X(29)}" y2="{Y(40)}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 4"/>')
txt(X(9)-10, Y(40)+5, 'L40', 14, INK, 'end', 'bold')
# ④ L41–L52, title + after-title positions: delivered
rect(9, 28, 41, 52, '#FBEAA0', .75)
txt(X(9)+8, Y(52)+14, 'put back: ≈ 100% by L52', 14, GREEN, weight='bold')
txt(X(9)+8, Y(52)+32, 'take away from L52: ≤ 0.05', 14, GREEN)
txt(X(9)+8, Y(52)+50, '(opposite directions agree)', 14, GREEN)
step('④', X0-60, YM(47), PIPE)
# ⑤ L48–L56, names: held, not as words (markers only; text in the right column)
rect(29, N-1, 48, 56, 'url(#hatch)', 1)
rect(29, N-1, 48, 56, '#E8F0FA', .45)
txt(X(31)+4, Y(56)+13, 'held at the names, not as words', 14, INK, weight='bold', halo=True)
step('⑤', X0-60, YM(52), '#3C78B4')
# ⑥ L57–L63, names: the late MLPs write
rect(29, N-1, 57, 63, '#F6B8B0', .8)
step('⑥', X0-60, YM(60), RED)

# ---------- the information flow ----------
TX = X(29) + CW/2                                 # the "arrival" column = first name token
# parallel pipes title -> through ":" -> name slots
for l in (44, 46, 48, 50, 52, 54):
    pipe(X(20)-2, YM(l), TX-14, YM(l), 8, PIPE, '#DCEFF5', head=True)
# ":" pass-through ring
a(f'<rect x="{X(28)+3}" y="{Y(55)}" width="{CW-6}" height="{12*LH}" rx="6" fill="none" stroke="{INK}" stroke-width="1.6"/>')
txt(X(28)+CW/2, Y(55)-6, ':', 18, INK, 'middle', 'bold')
txt(X(20)+6, Y(43)+14, 'name ← title, L44–L55:', 14, GREEN, weight='bold', halo=True)
txt(X(20)+6, Y(43)+32, 'several layers in parallel', 14, GREEN, halo=True)
struck(X(20)+6, Y(43)+50, 'one route, one layer', 14)
# arrival mark on the slots: bracket on the name column
a(f'<path d="M{TX-8} {YM(54)-8} h-5 V {YM(44)+8} h5" fill="none" stroke="{PIPE}" stroke-width="3"/>')
# the thread up the arrival column: L40 -> L52 -> L57–L61 -> padlock
a(f'<line x1="{TX}" y1="{YM(40)}" x2="{TX}" y2="{Y(61)}" stroke="{PIPE}" stroke-width="4" stroke-linecap="round"/>')
def node(l, k):
    a(f'<circle cx="{TX}" cy="{YM(l)}" r="13" fill="{PIPE}" stroke="#fff" stroke-width="2.5"/>')
    txt(TX, YM(l)+5, k, 14, '#fff', 'middle', 'bold')
node(40, '1'); txt(TX+22, YM(40)+5, 'L40: starts to arrive (names alone 0.18)', 14, BLUE, weight='bold', halo=True)
txt(TX+22, YM(46)+5, '◂ arrival mark · cut any one layer: ≤ 1.25% lost', 14, BLUE, halo=True)
node(52, '2'); txt(TX+22, YM(52)+5, 'read by L52 (names alone 0.84)', 14, BLUE, weight='bold', halo=True)
a(f'<rect x="{TX-14}" y="{Y(61)}" width="28" height="{5*LH}" rx="14" fill="{PIPE}" stroke="#fff" stroke-width="2.5"/>')
txt(TX, YM(59)+5, '3', 14, '#fff', 'middle', 'bold')
txt(TX+22, YM(60)+5, 'L57–L61: written out — the late MLPs write the name', 14, BLUE, weight='bold', halo=True)
txt(TX+22, YM(58)+5, '   (MLP − attention ≈ +0.04 at each layer)', 14, BLUE, halo=True)
padlock(TX, Y(63)+12)
txt(TX+22, Y(63)+20, 'stuck here: the first name token (given the initial: 4% → 15%)', 14, RED, weight='bold', halo=True)

# ⑤ markers (text in the right column)
for k, (cx, l, sym, col) in enumerate(((X(37), 53.6, '◉', GREEN), (X(43), 53.6, '◉', GREEN), (X(37), 50, '▲', BLUE), (X(43), 50, '▲', GREYC))):
    marker(cx, YM(l), sym, 'abcd'[k], col)
# format overturn at ":" L56
struck(X(20)+6, Y(56)+13, 'format fixed here (L56)', 14)
a(f'<line x1="{X(20)+6+tw("format fixed here (L56)", 14)*0.95+6}" y1="{Y(56)+8}" x2="{X(28)+2}" y2="{YM(56)}" stroke="#9AA3AE" stroke-width="1.4"/>')
txt(X(20)+6, Y(57)+13, '→ layer not pinned down', 14, RED, weight='bold', halo=True)

# gap ①: a broken pipe from "who wrote this paper" into the late MLPs (L56)
gy = YM(55)
broken_h(X(44), GR+52, gy)
a(f'<circle cx="{GR+62}" cy="{gy}" r="11" fill="#fff" stroke="{GREYC}" stroke-width="2"/><path d="M{GR+52} {gy+22} q10 -12 20 0" fill="none" stroke="{GREYC}" stroke-width="2"/>')

# ---------- right column: only what is not already on the plot ----------
a(f'<line x1="{RX-14}" y1="{Y(63)-30}" x2="{RX-14}" y2="{PB}" stroke="#D5D9DF" stroke-width="1.4"/>')
txt(RX, Y(63)-40, 'Not on the plot: details and side results', 15, GREY, weight='bold')
def entry(y, head, rows, hcol=INK):
    txt(RX, y, head, 15, hcol, weight='bold')
    yy = y
    for r in rows:
        yy += 20
        s, col = r[0], r[1]
        if len(r) > 2 and r[2] == 'strike': struck(RX+10, yy, s, 14)
        else: txt(RX+10, yy, s, 14, col, weight=(r[2] if len(r) > 2 else 'normal'))
    return yy
# gap ① label, leader to the broken pipe
y0 = Y(63) - 6
yy = entry(y0, 'Gap ① (broken pipe, ?)', [('at which step does "who wrote this paper"', GREYC),
                                          ('enter? No direct test; only indirect evidence', GREYC),
                                          ('(late MLP patching, mean ablation)', GREYC)], GREYC)
leader(GR+76, gy, RX-6, y0-5)
yy = entry(yy+34, '⑥ L56–L63, also', [('recognised − not grows → +0.21 at the output', BLUE),
                                      ('"the signal is too weak"', None, 'strike'),
                                      ('→ pushing it harder: 2.5% → 2.8%; the harm', RED, 'bold'),
                                      ('   comes from direction, not amount', RED),
                                      ('~1 in 8 papers: name rises after L56, then falls', BLUE),
                                      ('   (just past the bound)', GREYC)])
yy = entry(max(yy+34, Y(56)), '⑤ markers on the plot', [('a  probe reads it, lens does not:', GREEN, 'bold'),
                                                       ('   +0.06 on the same scale (L48)', GREEN),
                                                       ('b  spread out: author slice ~7%,', GREEN, 'bold'),
                                                       ('   no single direction, no earlier shelf', GREEN),
                                                       ('c  L52–L56 MLPs carry paper information,', BLUE, 'bold'),
                                                       ('   not ready-made name directions', BLUE),
                                                       ('d  injected author direction: 2.5% → 9.7%,', GREYC, 'bold'),
                                                       ('   mostly a write channel (cannot decide', GREYC),
                                                       ('   whether it uses its own knowledge)', GREYC),
                                                       ('at L48 lens negative, probe positive: unexplained', GREYC)])
yy = entry(yy+34, '④ L40–L52, ruled out', [('"recognised papers are read earlier":', None, 'strike'),
                                           ('→ recognition changes size, not timing', RED, 'bold'),
                                           ('a lucky false title: same timing for all five', RED)])
yy = entry(max(yy+34, Y(38)), '③ L24–L40, also', [('surname simply in the title (source check)', RED),
                                                     ('only the field’s common surnames (topic test)', RED),
                                                     ('the rest of the extra sits on rare words,', GREEN),
                                                     ('not on recognising the paper', GREEN)])
yy = entry(max(yy+34, Y(20)), '② L4–L24, also', [('L8 surname exception: text baseline weak,', GREYC),
                                               ('locked test only at L8; ≈ 0 again by L56', GREYC)])
yy = entry(max(yy+34, Y(6)), '① L0–L4, rewritten', [('"same state across questions = identity"', None, 'strike'),
                                                   ('→ cannot separate meaning from identity', RED, 'bold')])

# ---------- multiple-choice card (defines "recognised") + gap ② ----------
cx0, cy0, cwid, chei = X(29), PB + 86, 520, 176
a(f'<rect x="{cx0}" y="{cy0}" width="{cwid}" height="{chei}" rx="12" fill="#fff" stroke="{INK}" stroke-width="2.4"/>')
txt(cx0+18, cy0+30, 'Which author list wrote this paper?', 17, INK, weight='bold')
opts = ['A   Karin G. Coifman, George A. Bonanno, …  (true)', 'B   another team’s author list', 'C   another team’s author list', 'D   another team’s author list']
for k, s in enumerate(opts):
    yy = cy0 + 60 + k*24
    a(f'<circle cx="{cx0+26}" cy="{yy-5}" r="7" fill="{INK if k == 0 else "#fff"}" stroke="{INK}" stroke-width="1.8"/>')
    txt(cx0+42, yy, s, 15, INK, weight=('bold' if k == 0 else 'normal'))
txt(cx0+18, cy0+chei-14, 'shown in four option orders · all four orders right = "recognised"', 14, DET, weight='bold')
pcx = cx0 + cwid/2
broken_v(pcx, PB+2, cy0)
gl = (PB + cy0)/2
leader(pcx+44, gl, cx0+cwid+36, gl)
txt(cx0+cwid+44, gl-14, 'Gap ②: "recognised" comes only from this card;', 14, GREYC, weight='bold')
txt(cx0+cwid+44, gl+4, 'it was never measured inside this prompt —', 14, GREYC)
txt(cx0+cwid+44, gl+22, 'every reading above uses the open question', 14, GREYC)
txt(cx0-14, cy0+30, 'the recognition test →', 15, INK, 'end', fam=HAND)

# ---------- legend + three grey lines ----------
ly = PB + 40
txt(24, ly, 'Colour of a sentence:', 14, INK, weight='bold')
xx = 214
for lab, col in (('proven by one experiment', BLUE), ('joint (several together)', GREEN), ('cannot be decided', GREYC), ('refuted / overturned', RED)):
    a(f'<rect x="{xx}" y="{ly-12}" width="14" height="14" rx="3" fill="{col}"/>'); txt(xx+20, ly, lab, 14, col, weight='bold')
    xx += 44 + 8.6*len(lab)
struck(xx, ly, 'old claim', 14); xx += 100
ly2 = ly + 30
txt(24, ly2, '◉ readout (lens / probe)   ▲ intervention   ━ pipe = delivery   ✂ broken pipe ? = known gap   ┆ dashed outline = read-in only', 14, GREY)
gx0 = 24; gy0 = cy0 + chei + 34
a(f'<image x="{gx0}" y="{gy0}" width="497" height="50" xlink:href="{b64("tex_main_f.png")}"/>')
a(f'<image x="{gx0}" y="{gy0+50}" width="906" height="28" xlink:href="{b64("tex_main_n.png")}"/>')
txt(gx0, gy0+100, 'spec > 0: the true title helps the true author; R ≈ 1: the copied state restores all of the true-title advantage', 14, GREY)
a('</svg>')
H2 = int(gy0 + 120)
s = '\n'.join(o).replace(f'height="{H}" viewBox="0 0 {W} {H}"', f'height="{H2}" viewBox="0 0 {W} {H2}"', 1).replace(f'<rect width="{W}" height="{H}"', f'<rect width="{W}" height="{H2}"', 1)
open('main_v4.svg', 'w').write(s)
print('ok', W, H2)
