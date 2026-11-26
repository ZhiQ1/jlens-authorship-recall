# Deck versions of main v4 on a 16:9 base (1920x1080, all text >= 16 px): step 0 = everything lit,
# steps 1-6 = one stage lit, the rest faded (outlines kept). Content unchanged from main v4. 2026-11-25.
import base64, html, os, sys
from PIL import Image

TOKS = ['Who', ' are', ' the', ' authors', ' of', ' the', ' paper', ' titled', ' "', 'A', 'ffect', ' dynamics', ',', ' bere', 'av',
        'ement', ' and', ' resilience', ' to', ' loss', '"', ' (', '2', '0', '0', '7', ')?↵', 'Authors', ':', ' Kar', 'in', ' G', '.',
        ' Co', 'if', 'man', ',', ' George', ' A', '.', ' Bon', 'anno', ',', ' E', 'sh', 'kol', ' Rafael', 'i']
GRP = [0]*9 + [1]*11 + [2]*9 + [3]*19
GNAME = ['the question', 'the title (11 tokens)', 'after the title', 'the author names (every token scored)']
GCOL = ['#EEF1F5', '#FFF1DE', '#E8F0FA', '#FBE3E1']
N = len(TOKS)
W, H = 1920, 1080
CW, X0, Y0, LH = 22, 96, 200, 10.5
GR = X0 + CW*N                                   # 1122
RX = GR + 92                                     # right column x
RW = W - RX - 16
INK, DET, GREY = '#22304A', '#5A6372', '#8a8f98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
PIPE = '#1F6F8B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
FS = 16
def X(i): return X0 + i*CW
def Y(l): return Y0 + (63 - l)*LH
def YM(l): return Y(l) + LH/2
PB = Y(0) + LH
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def tw(s, size=FS): return 0.6*size*len(s)
def wrap(s, width, size=FS):
    n = max(8, int(width/(0.585*size))); out, cur = [], ''
    for w in s.split(' '):
        if len(cur)+len(w)+(1 if cur else 0) > n and cur: out.append(cur); cur = w
        else: cur = (cur+' '+w) if cur else w
    if cur: out.append(cur)
    return out

# ---------- element list with keys ----------
EL = []; KEY = ['base']
def a(s): EL.append((KEY[0], s))
class K:
    def __init__(s, k): s.k = k
    def __enter__(s): s.old = KEY[0]; KEY[0] = s.k
    def __exit__(s, *x): KEY[0] = s.old

def rect(c0, c1, l0, l1, fill, op=1, stroke='none', dash=None, sw=1.6, rx=3):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(c0)}" y="{Y(l1)}" width="{X(c1+1)-X(c0)}" height="{(l1-l0+1)*LH}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x, y, s, size=FS, col=INK, anchor='start', weight='normal', italic=False, fam=SANS, halo=False):
    st = ' font-style="italic"' if italic else ''
    if halo:
        a(f'<text x="{x}" y="{y}" font-size="{size}" fill="#FBFAF5" stroke="#FBFAF5" stroke-width="5" stroke-linejoin="round" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def struck(x, y, s, size=FS, anchor='start'):
    w = tw(s, size)*0.93; x0 = x - (w if anchor == 'end' else 0)
    txt(x, y, s, size, '#9AA3AE', anchor, italic=True)
    a(f'<line x1="{x0-2}" x2="{x0+w+2}" y1="{y-size*0.32}" y2="{y-size*0.32}" stroke="#9AA3AE" stroke-width="1.8"/>')
def lines(x, y, rows, dy=19, size=FS, anchor='start'):
    for k, (s, col, *w) in enumerate(rows):
        if col is None: struck(x, y+k*dy, s, size, anchor)
        else: txt(x, y+k*dy, s, size, col, anchor, weight=(w[0] if w else 'normal'), halo=True)
def step(n, x, y, col, r=14):
    a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/><text x="{x}" y="{y+6}" font-size="16" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')
def pipe(x1, y1, x2, y2, w=7, col=PIPE, inner='#DCEFF5', head=False):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
      f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{inner}" stroke-width="{w-4}" stroke-linecap="round"/>')
    if head: a(f'<path d="M{x2+1} {y2-6} L{x2+10} {y2} L{x2+1} {y2+6} Z" fill="{col}"/>')
def broken_h(x1, x2, y):
    mid = (x1+x2)/2
    pipe(x1, y, mid-14, y, 7, GREYC, '#EEF0F3'); pipe(mid+14, y, x2, y, 7, GREYC, '#EEF0F3')
    a(f'<path d="M{mid-12} {y-8} l4 5 l-4 5 l4 5 M{mid+12} {y-8} l-4 5 l4 5 l-4 5" fill="none" stroke="{GREYC}" stroke-width="2"/>')
    txt(mid, y-12, '?', 20, GREYC, 'middle', 'bold')
def broken_v(x, y1, y2):
    mid = (y1+y2)/2
    pipe(x, y1, x, mid-8, 7, GREYC, '#EEF0F3'); pipe(x, mid+8, x, y2, 7, GREYC, '#EEF0F3')
    a(f'<path d="M{x-8} {mid-6} l5 3 l5 -3 l5 3 M{x-8} {mid+6} l5 -3 l5 3 l5 -3" fill="none" stroke="{GREYC}" stroke-width="2"/>')
    txt(x+14, mid+7, '?', 20, GREYC, 'start', 'bold')
def leader(x1, y1, x2, y2, col='#B8BEC8'):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.4"/><circle cx="{x1}" cy="{y1}" r="3" fill="{col}"/>')
def padlock(cx, cy, col=RED):
    a(f'<path d="M{cx-6} {cy-2} v-5 a6 6 0 0 1 12 0 v5" fill="none" stroke="{col}" stroke-width="2.4"/>'
      f'<rect x="{cx-9}" y="{cy-3}" width="18" height="14" rx="3" fill="#fff" stroke="{col}" stroke-width="2.4"/><circle cx="{cx}" cy="{cy+4}" r="2" fill="{col}"/>')
def marker(x, y, sym, k, col):
    a(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{col}" stroke-width="2"/>')
    txt(x, y+6, k, 16, col, 'middle', 'bold'); txt(x+14, y+6, sym, 16, col)

# ================= drawing =================
txt(24, 40, 'Read early, said late: the whole story on one map', 32, INK, fam=HAND)
txt(24, 66, 'x: the prompt as real Qwen3 tokens · y: layers L0 (bottom) to L63 (top) · follow the blue pipes to nodes 1 → 2 → 3 and the padlock', 16, DET)
# token header
for g in range(4):
    c0 = GRP.index(g); c1 = len(GRP) - 1 - GRP[::-1].index(g)
    txt((X(c0)+X(c1+1))/2, 90, GNAME[g], 16, DET, 'middle')
    a(f'<line x1="{X(c0)+3}" x2="{X(c1+1)-3}" y1="{96}" y2="{96}" stroke="#c9ced6" stroke-width="1.5"/>')
for i, (t, g) in enumerate(zip(TOKS, GRP)):
    if g == 3: a(f'<rect x="{X(i)+1.5}" y="{Y0-100}" width="{CW-3}" height="96" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    else: a(f'<rect x="{X(i)+1}" y="{Y0-100}" width="{CW-2}" height="96" rx="4" fill="{GCOL[g]}" stroke="#c9ced6"/>')
    cx, cy = X(i) + CW/2 + 6, Y0 - 10
    wt = 'bold' if (g == 3 or t == ':') else 'normal'
    a(f'<text x="{cx}" y="{cy}" font-size="16" font-weight="{wt}" fill="{INK}" transform="rotate(-90 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')
# small book over the title heading
bx0, bx1, by = X(9)+70, X(20)-70, 70
# grid
for l in range(0, 64, 4):
    a(f'<line x1="{X0}" x2="{GR}" y1="{Y(l)+LH}" y2="{Y(l)+LH}" stroke="#e6e9ee" stroke-width="1"/>')
for l in (0, 8, 16, 24, 32, 40, 48, 56, 63):
    txt(X0-6, Y(l)+LH-1, f'L{l}', 16, GREY, 'end')
a(f'<rect x="{X0}" y="{Y(63)}" width="{GR-X0}" height="{64*LH}" fill="none" stroke="#c9ced6"/>')
# outlines of every stage block (always kept, so the map stays visible when faded)
for c0, c1, l0, l1 in ((0, N-1, 0, 4), (9, 19, 5, 23), (9, 19, 24, 40), (9, 28, 41, 52), (29, N-1, 48, 56), (29, N-1, 57, 63)):
    rect(c0, c1, l0, l1, 'none', 1, '#C3C9D2', None, 1.2)

with K(1):
    rect(0, N-1, 0, 4, '#DDE2E8', .85)
    txt(X(0)+8, Y(3)+6, 'identical words → identical states: same title under two questions, cos ≈ 1.00 at L4 —', 16, BLUE, halo=True)
    txt(X(0)+8, Y(3)+25, 'the ceiling every later test is measured above', 16, BLUE, halo=True)
    step('①', 30, YM(2), '#6A7385')
with K(2):
    rect(9, 19, 5, 23, '#FFF3DF', 1, '#D9A15A', '6 4', 1.8)
    lines(X(9)+6, Y(23)+16, [('read-in only', '#8a5a12', 'bold'), ('(not yet the title being', '#8a5a12'), ('read): from L8 the words', '#8a5a12'),
                            ('are encoded beyond', BLUE), ('their form', BLUE)])
    a(f'<polygon points="{X(19)+CW/2},{Y(8)-3} {X(19)+CW/2+6},{Y(8)+8} {X(19)+CW/2-6},{Y(8)+8}" fill="{BLUE}"/>')
    lines(X(20)+4, Y(13)+4, [('★ L8: small surname', BLUE, 'bold'), ('signal beyond topic', BLUE), ('(+0.05; 2 of 3 tests', GREYC), ('marginal)', GREYC)])
    rect(28, 28, 4, 56, 'none', 1, BLUE, '5 3', 2)
    lines(X(20)+4, Y(22)+6, [('":" follows the', BLUE), ('question (4.7× at L4)', BLUE)])
    step('②', 30, YM(14), '#B54708')
with K(3):
    rect(9, 19, 24, 40, '#FFC98A', .9)
    lines(X(9)+6, Y(40)+18, [('title read, L24 →', INK, 'bold'), ('meaning + specific words', GREEN, 'bold'), ('(four tests together)', GREEN),
                            ('made-up title, same', BLUE), ('meaning:', BLUE), ('brings back ~75%', BLUE, 'bold'),
                            ('stores which paper this is', None), ('→ not paper identity', RED, 'bold')], dy=19.3)
    step('③', 30, YM(32), '#D9772B')
with K('div'):
    a(f'<line x1="{X(9)-4}" y1="{Y(40)}" x2="{X(29)}" y2="{Y(40)}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    txt(X(9)-8, Y(40)+6, 'L40', 16, INK, 'end', 'bold')
with K(4):
    rect(9, 28, 41, 52, '#FBEAA0', .8)
    lines(X(9)+6, Y(52)+16, [('put back: ≈ 100% by L52', GREEN, 'bold'), ('take away from L52: ≤ 0.05', GREEN), ('(opposite directions agree)', GREEN)])
    step('④', 30, YM(47), PIPE)
with K(5):
    rect(29, N-1, 48, 56, '#DCE7F5', .9)
    txt(X(31)+2, Y(56)+15, 'held at the names, not as words', 16, INK, weight='bold', halo=True)
    step('⑤', 30, YM(52), '#3C78B4')
with K(6):
    rect(29, N-1, 57, 63, '#F6B8B0', .85)
    step('⑥', 30, YM(60), RED)

TX = X(29) + CW/2
with K('arr'):
    a(f'<rect x="{X(29)+2}" y="{Y(54)+2}" width="{X(36)-X(29)-4}" height="{11*LH-4}" rx="5" fill="{PIPE}" fill-opacity=".16" stroke="{PIPE}" stroke-width="2.4"/>')
    for c in range(30, 36):
        a(f'<line x1="{X(c)}" y1="{Y(54)+4}" x2="{X(c)}" y2="{Y(44)+LH-4}" stroke="{PIPE}" stroke-width="1" opacity=".45"/>')
with K('colon'):
    a(f'<rect x="{X(28)+3}" y="{Y(55)}" width="{CW-6}" height="{12*LH}" rx="5" fill="none" stroke="{INK}" stroke-width="1.5"/>')
with K('pipelab'):
    lines(X(20)+4, Y(43)+14, [('name ← title,', GREEN, 'bold'), ('L44–L55: several', GREEN), ('layers in parallel', GREEN), ('one route, one layer', None)], dy=18.5)
# thread segments (bottom → top)
for k, (l0, l1) in (('t40', (40, 48)), ('t48', (48, 52)), ('t52', (52, 56)), ('t56', (56, 61))):
    with K(k): a(f'<line x1="{TX}" y1="{YM(l0)}" x2="{TX}" y2="{YM(l1) if l1 != 61 else Y(61)}" stroke="{PIPE}" stroke-width="4" stroke-linecap="round"/>')
END = X(33) + 4
for l in (44, 46, 48, 50, 52, 54):
    with K(f'p{l}'): pipe(X(20)-2, YM(l), END, YM(l), 7, PIPE, '#DCEFF5', head=True)
def node(l, k):
    a(f'<circle cx="{TX}" cy="{YM(l)}" r="12" fill="{PIPE}" stroke="#fff" stroke-width="2.5"/>'); txt(TX, YM(l)+6, k, 16, '#fff', 'middle', 'bold')
with K('n1'):
    node(40, '1'); txt(TX+20, YM(40)+6, 'L40: starts to arrive (names alone 0.18)', 16, BLUE, weight='bold', halo=True)
with K('arrlab'):
    lines(X(36)+6, YM(47)+6, [('◂ arrival mark on the slots:', BLUE, 'bold'), ('cut any one layer: ≤ 1.25% lost', BLUE)], dy=19)
with K('n2'):
    node(52, '2'); txt(X(36)+6, YM(51.6)+6, 'read by L52 (names alone 0.84)', 16, BLUE, weight='bold', halo=True)
with K('n3'):
    a(f'<rect x="{TX-12}" y="{Y(61)}" width="24" height="{5*LH}" rx="12" fill="{PIPE}" stroke="#fff" stroke-width="2.5"/>')
    txt(TX, YM(59)+6, '3', 16, '#fff', 'middle', 'bold')
    lines(TX+20, Y(62)+10, [('L57–L61: written out —', BLUE, 'bold'), ('the late MLPs write the name', BLUE, 'bold'), ('(MLP − attention ≈ +0.04 at each layer)', BLUE)], dy=19.5)
with K('lock'):
    padlock(TX, Y(63)+8)
    lines(TX-18, Y(63)+14, [('stuck here: the first', RED, 'bold'), ('name token (given the', RED, 'bold'), ('initial: 4% → 15%)', BLUE)], dy=18, anchor='end')
with K('mk'):
    for k, (cx, l, sym, col) in enumerate(((X(37)+6, 53.4, '◉', GREEN), (X(40)+4, 53.4, '◉', GREEN), (X(43)+2, 53.4, '▲', BLUE), (X(46), 53.4, '▲', GREYC))):
        marker(cx, YM(l), sym, 'abcd'[k], col)
with K('fmt'):
    struck(X(9)+4, Y(56)+13, 'format fixed here (L56)', 16)
    txt(X(9)+4, Y(54)+11, '→ layer not pinned down', 16, RED, weight='bold', halo=True)
    a(f'<line x1="{X(9)+4+tw("format fixed here (L56)")*0.93+6}" y1="{Y(56)+8}" x2="{X(28)+3}" y2="{YM(56)}" stroke="#9AA3AE" stroke-width="1.4"/>')
gy = YM(55.4)
with K('gap1'):
    broken_h(X(46), GR+44, gy)
    a(f'<circle cx="{GR+54}" cy="{gy}" r="10" fill="#fff" stroke="{GREYC}" stroke-width="2"/><path d="M{GR+45} {gy+20} q9 -11 18 0" fill="none" stroke="{GREYC}" stroke-width="2"/>')

# ---------- right column ----------
with K('base'):
    a(f'<line x1="{RX-14}" y1="{84}" x2="{RX-14}" y2="{PB}" stroke="#D5D9DF" stroke-width="1.4"/>')
    txt(RX, 92, 'Not on the plot: details and side results', 16, GREY, weight='bold')
def entry(key, y, head, rows, hcol=INK):
    with K(key):
        txt(RX, y, head, 17, hcol, weight='bold'); yy = y
        for s, col, *w in rows:
            for ln in wrap(s, RW-14):
                yy += 19.5
                if col is None: struck(RX+10, yy, ln)
                else: txt(RX+10, yy, ln, 16, col, weight=(w[0] if w else 'normal'))
    return yy
yy = entry('r6', 122, '⑥ L56–L63, also', [('recognised − not grows → +0.21 at the output', BLUE), ('"the signal is too weak"', None),
                                            ('→ pushing it harder: 2.5% → 2.8%; the harm comes from direction, not amount', RED, 'bold'),
                                            ('~1 in 8 papers: name rises after L56, then falls (just past the bound)', BLUE)])
g0 = yy + 30
yy = entry('rg', g0, 'Gap ① (broken pipe, ?)', [('at which step does "who wrote this paper" enter? No direct test; only indirect evidence (late MLP patching, mean ablation)', GREYC)], GREYC)
with K('rg'): leader(GR+66, gy, RX-6, g0-6)
yy = entry('r5', yy+30, '⑤ markers on the plot', [('a  probe reads it, lens does not: +0.06 on the same scale (L48)', GREEN, 'bold'),
                                                    ('b  spread out: author slice ~7%, no single direction, no earlier shelf', GREEN, 'bold'),
                                                    ('c  L52–L56 MLPs carry paper information, not ready-made name directions', BLUE, 'bold'),
                                                    ('d  injected author direction: 2.5% → 9.7%, mostly a write channel (cannot decide whether it uses its own knowledge)', GREYC, 'bold'),
                                                    ('at L48 lens negative, probe positive: unexplained', GREYC)])
yy = entry('r4', yy+30, '④ L40–L52, ruled out', [('"recognised papers are read earlier"', None), ('→ recognition changes size, not timing', RED, 'bold'),
                                                   ('a lucky false title: same timing for all five', RED)])
yy = entry('r3', max(yy+30, Y(38)), '③ L24–L40, also', [('surname simply in the title (source check)', RED), ('only the field’s common surnames (topic test)', RED),
                                                       ('the rest of the extra sits on rare words, not on recognising the paper', GREEN)])
yy = entry('r2', max(yy+30, Y(20)), '② L4–L24, also', [('L8 surname exception: text baseline weak, locked test only at L8; ≈ 0 again by L56', GREYC)])
yy = entry('r1', max(yy+30, Y(5)), '① L0–L4, rewritten', [('"same state across questions = identity"', None), ('→ cannot separate meaning from identity', RED, 'bold')])
RC_BOTTOM = yy

# ---------- multiple-choice card + gap ② ----------
cx0, cy0, cwid, chei = X(0)-30, PB + 24, 500, 136
with K('mc'):
    a(f'<rect x="{cx0}" y="{cy0}" width="{cwid}" height="{chei}" rx="10" fill="#fff" stroke="{INK}" stroke-width="2.2"/>')
    txt(cx0+14, cy0+24, 'Which author list wrote this paper?', 17, INK, weight='bold')
    for k, s in enumerate(['A  Karin G. Coifman, George A. Bonanno, … (true)', 'B  another team’s author list', 'C  another team’s author list', 'D  another team’s author list']):
        yv = cy0 + 45 + k*20
        a(f'<circle cx="{cx0+22}" cy="{yv-5}" r="6" fill="{INK if k == 0 else "#fff"}" stroke="{INK}" stroke-width="1.6"/>')
        txt(cx0+36, yv, s, 16, INK, weight=('bold' if k == 0 else 'normal'))
    txt(cx0+14, cy0+chei-10, 'four option orders · all four right = "recognised"', 16, DET, weight='bold')
    pcx = cx0 + cwid - 60
    broken_v(pcx, PB+2, cy0)
    lines(cx0+cwid+18, cy0+20, [('Gap ②: "recognised" comes only from', GREYC, 'bold'), ('this card; never measured inside this', GREYC),
                                ('prompt — every reading above uses', GREYC), ('the open question', GREYC)], dy=19)
    leader(pcx+30, (PB+cy0)/2, cx0+cwid+14, cy0+14)

# ---------- legend + three grey lines ----------
LX = 1000
with K('base'):
    ly = PB + 24
    txt(LX, ly, 'Colour of a sentence:', 16, INK, weight='bold')
    xx = LX + 214
    for lab, col in (('one experiment', BLUE), ('joint', GREEN), ('cannot decide', GREYC), ('refuted', RED)):
        a(f'<rect x="{xx}" y="{ly-13}" width="14" height="14" rx="3" fill="{col}"/>'); txt(xx+20, ly, lab, 16, col, weight='bold'); xx += 36 + 9.6*len(lab)
    struck(xx, ly, 'old claim')
    txt(LX, ly+22, '◉ readout  ▲ intervention  ━ pipe = delivery  ✂? = known gap  ┆ = read-in only', 16, GREY)
    s = 0.40
    f1, f2 = Image.open('tex_main_f.png').size, Image.open('tex_main_n.png').size
    a(f'<image x="{LX}" y="{ly+32}" width="{f1[0]*s}" height="{f1[1]*s}" xlink:href="{b64("tex_main_f.png")}"/>')
    a(f'<image x="{LX}" y="{ly+32+f1[1]*s+2}" width="{f2[0]*s}" height="{f2[1]*s}" xlink:href="{b64("tex_main_n.png")}"/>')
    GL3 = ly + 32 + f1[1]*s + f2[1]*s + 20
    txt(LX, GL3, 'spec > 0: the true title helps the true author;', 16, GREY)
    txt(LX, GL3+19, 'R ≈ 1: the copied state restores all of the true-title advantage', 16, GREY)

# ================= assemble per step =================
STEPS = {
    0: ('step0_all', None, None),
    1: ('step1_L0_L4', {1, 'r1'}, ('L0–L4: the input words decide almost everything', 'x', 'cannot separate meaning from identity here')),
    2: ('step2_L4_L24', {2, 'r2'}, ('L4–L24: early read-in; the first traces of the title and of the first author', 'g', 'joint')),
    3: ('step3_L24_L40', {3, 'r3', 'div'}, ('L24–L40: the main title-reading phase; what is read is meaning and specific words, not paper identity', 'r', 'overturns H2')),
    4: ('step4_L40_L52', {4, 'r4', 'div', 'arr', 'colon', 'pipelab', 't40', 't48', 'p44', 'p46', 'p48', 'p50', 'p52', 'n1', 'arrlab', 'n2'},
        ('L40–L52: the information reaches the name positions, over several layers in parallel; the title is read by L52', 'g', 'joint')),
    5: ('step5_L48_L56', {5, 'r5', 'rg', 'gap1', 'mk', 'fmt', 't48', 't52', 'p48', 'p50', 'p52', 'p54', 'n2', 'colon'},
        ('L48–L56: the probe reads it, the lens does not; what arrives is paper information, not ready-made names', 'b', 'one experiment each: same-scale test, MLP swap')),
    6: ('step6_L56_L63', {6, 'r6', 'rg', 'gap1', 't56', 'n3', 'lock'},
        ('L56–L63: the late MLPs write the name; the gap grows here, and it gets stuck at writing', 'g', 'joint')),
}
DEFS = ('<defs>'
        '<filter id="fade" filterUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/>'
        '<feComponentTransfer><feFuncR type="linear" slope="0.05" intercept="0.915"/><feFuncG type="linear" slope="0.05" intercept="0.915"/><feFuncB type="linear" slope="0.05" intercept="0.92"/></feComponentTransfer></filter>'
        '<filter id="lit" filterUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="1.25"/>'
        '<feComponentTransfer><feFuncR type="linear" slope="1.04"/><feFuncG type="linear" slope="1.04"/><feFuncB type="linear" slope="1.04"/></feComponentTransfer></filter>'
        '</defs>')
os.makedirs('deck16x9', exist_ok=True)
ONLY = [int(v) for v in sys.argv[1:]] or list(STEPS)
def phenomenon_panel(out):                       # step 0 only: compact phenomenon panel (bottom strip)
    py = H - 42
    out.append(f'<rect x="24" y="{py}" width="{W-48}" height="36" rx="8" fill="#F3F7F4" stroke="{GREEN}" stroke-width="2"/>')
    segs = [('Phenomenon, recognised but not said:', GREEN, 'bold'), ('recognised at ~40 citations vs written at ~11,000', BLUE, 'bold'),
            ('(ρ ~276×; only ρ > 1 confirmed)', GREYC, 'normal'), ('·', GREY, 'normal'), ('name prior only ~19% of the gap', BLUE, 'bold'),
            ('·', GREY, 'normal'), ('R0 alone +0.20 vs pooled +0.21', BLUE, 'bold')]
    xx = 40
    for s, col, wgt in segs:
        out.append(f'<text x="{xx}" y="{py+24}" font-size="16" fill="{col}" font-weight="{wgt}" font-family="{SANS}">{esc(s)}</text>')
        xx += (0.63 if wgt == 'bold' else 0.58)*16*len(s) + 12
    return xx
for n, (name, lit, concl) in STEPS.items():
    if n not in ONLY: continue
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">',
           DEFS, f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>']
    runs = []                                    # group consecutive elements with the same treatment (fewer filter passes)
    for k, s in EL:
        mode = 'n' if (n == 0 or k == 'base') else ('lit' if k in lit else 'fade')
        if runs and runs[-1][0] == mode: runs[-1][1].append(s)
        else: runs.append((mode, [s]))
    for mode, ss in runs:
        body = '\n'.join(ss)
        out.append(body if mode == 'n' else f'<g filter="url(#{mode})">{body}</g>')
    if n == 0: print('panel end x', phenomenon_panel(out))
    if n:
        out.append(f'<text x="{W-24}" y="40" font-size="22" fill="{INK}" text-anchor="end" font-family="{HAND}">Step {"①②③④⑤⑥"[n-1]} of 6</text>')
        cs, ck, ctype = concl
        cc = {'b': '#1E40AF', 'g': '#15803D', 'x': '#4B5563', 'r': '#B91C1C'}[ck]
        out.append(f'<rect x="24" y="{H-42}" width="{W-48}" height="36" rx="8" fill="{cc}"/>')
        out.append(f'<text x="40" y="{H-17}" font-size="19" fill="#fff" font-weight="bold" font-family="{SANS}">{esc(cs)}</text>')
        out.append(f'<text x="{W-40}" y="{H-17}" font-size="17" fill="#fff" text-anchor="end" font-style="italic" font-family="{SANS}">{esc(ctype)}</text>')
    out.append('</svg>')
    open(f'deck16x9/{name}.svg', 'w').write('\n'.join(out))
print('ok', 'right column bottom', RC_BOTTOM, 'plot bottom', PB, 'grey line 3', GL3+19)
