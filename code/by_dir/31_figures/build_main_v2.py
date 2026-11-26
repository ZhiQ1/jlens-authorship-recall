# MAIN figure v2: token x layer map with pictorial elements; plot keeps shapes + one short label per block;
# details only in the right column; colour = argument type (blue single / green joint / grey undecidable / red overturned).
# Content unchanged from v1 (27_v67/experiment_tree.md). 2026-11-24.
import base64, html
TOKS = ['Who', ' are', ' the', ' authors', ' of', ' the', ' paper', ' titled', ' "', 'A', 'ffect', ' dynamics', ',', ' bere', 'av',
        'ement', ' and', ' resilience', ' to', ' loss', '"', ' (', '2', '0', '0', '7', ')?↵', 'Authors', ':', ' Kar', 'in', ' G', '.',
        ' Co', 'if', 'man', ',', ' George', ' A', '.', ' Bon', 'anno', ',', ' E', 'sh', 'kol', ' Rafael', 'i']
GRP = [0]*9 + [1]*11 + [2]*9 + [3]*19
N = len(TOKS)
CW, X0, Y0, LH = 24, 96, 300, 11.0
GR = X0 + CW*N; RX = GR + 70; W, H = RX + 620, 1260
INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
def X(i): return X0 + i*CW
def Y(l): return Y0 + (63 - l)*LH
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
o = []; a = o.append
def txt(x, y, s, size=15, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def strike(x, y, s, size=15, anchor='start'):
    w = 0.6*size*len(s); x0 = x - (w/2 if anchor == 'middle' else 0)
    txt(x, y, s, size, '#9AA3AE', anchor, italic=True)
    a(f'<line x1="{x0-2}" x2="{x0+w}" y1="{y-size*0.33}" y2="{y-size*0.33}" stroke="#9AA3AE" stroke-width="1.8"/>')
def block(c0, c1, l0, l1, fill, op=1, stroke='none', sw=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(c0)}" y="{Y(l1)}" width="{(c1-c0+1)*CW}" height="{(l1-l0+1)*LH}" rx="4" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def label(x, y, s, col, size=16, anchor='start'):     # one short label per block, with a light halo
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="bold" fill="#FBFAF5" stroke="#FBFAF5" stroke-width="5" text-anchor="{anchor}" font-family="{SANS}">{esc(s)}</text>')
    txt(x, y, s, size, col, anchor, 'bold')
def leader(x1, y1, x2, y2, col=PALE_T):
    a(f'<path d="M{x1} {y1} H {GR+18} L {x2-10} {y2} H {x2-2}" fill="none" stroke="{col}" stroke-width="1.4"/>'
      f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="{col}"/>')
def mark(x, y, num, col, r=11):
    a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="#fff" stroke-width="2"/>')
    txt(x, y+5, num, 13, '#fff', 'middle', 'bold')
def pipe(x1, y1, x2, y2, w=7, col='#1F6F8B', inner='#DCEFF5'):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
      f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{inner}" stroke-width="{w-4}" stroke-linecap="round"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#3C78B4" stroke-width="2.2" opacity=".28"/></pattern>'
  '<marker id="pk" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#1F6F8B"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
txt(24, 48, 'Read early, said late: the whole story on one map', 36, INK, fam=HAND)
txt(24, 78, 'x: the prompt as real Qwen3 tokens · y: layers L0 (bottom) to L63 (top) · read the plot bottom-up; details for each stage are on the right.', 15, DET)

# ---- header: book over the title, slots for the names ----
bx0, bx1, by = X(9), X(20), Y0-150
mx = (bx0 + bx1)/2
a(f'<path d="M{bx0+6} {by+10} Q {(bx0+mx)/2} {by-6} {mx} {by+8} Q {(mx+bx1)/2} {by-6} {bx1-6} {by+10} V {by+36} Q {(mx+bx1)/2} {by+22} {mx} {by+34} Q {(bx0+mx)/2} {by+22} {bx0+6} {by+36} Z" '
  f'fill="#FFF1DE" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/><line x1="{mx}" y1="{by+8}" x2="{mx}" y2="{by+34}" stroke="{INK}" stroke-width="1.8"/>')
txt(mx, by-12, 'the title (a book the model reads)', 15, INK, 'middle', fam=HAND)
txt((X(29)+X(N))/2, by-12, 'the author names: empty slots the model must fill', 15, INK, 'middle', fam=HAND)
txt((X(0)+X(9))/2, by+30, 'the question', 15, INK, 'middle', fam=HAND)
txt((X(20)+X(29))/2, by+30, 'after the title', 15, INK, 'middle', fam=HAND)
for i, (t, g) in enumerate(zip(TOKS, GRP)):
    if g == 3:
        a(f'<rect x="{X(i)+2}" y="{Y0-100}" width="{CW-4}" height="92" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    else:
        col = ['#EEF1F5', '#FFF1DE', '#E8F0FA'][g]
        a(f'<rect x="{X(i)+1}" y="{Y0-100}" width="{CW-2}" height="92" rx="4" fill="{col}" stroke="#C9CED6"/>')
    cx, cy = X(i) + CW/2 + 5, Y0 - 14
    a(f'<text x="{cx}" y="{cy}" font-size="14" fill="{PALE_T if g == 3 else INK}" transform="rotate(-90 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')

# ---- grid ----
for l in range(0, 64, 4):
    a(f'<line x1="{X0}" x2="{GR}" y1="{Y(l)+LH}" y2="{Y(l)+LH}" stroke="#E8EBEF"/>')
for l in (0, 8, 16, 24, 32, 40, 48, 56, 63):
    txt(X0-8, Y(l)+LH-1, f'L{l}', 14, PALE_T, 'end')
a(f'<rect x="{X0}" y="{Y(63)}" width="{GR-X0}" height="{64*LH}" fill="none" stroke="#C9CED6"/>')

# ① L0-L4 ceiling band (grey: cannot decide)
block(0, N-1, 0, 4, '#DDE2E8', .8)
label(X(1), Y(1)+6, 'same words → same state', GREYC)
# ② L4-L24 early read-in on the title
block(9, 19, 4, 23, '#FFE9CC', .9)
label(X(9)+6, Y(14)+6, 'early read-in', BLUE)
# ':' rail L4-L56
pipe(X(28)+CW/2, Y(4)+LH, X(28)+CW/2, Y(56), 8, '#3C78B4', '#E3EDF8')
label(X(20)+2, Y(20)+6, '":" follows the question', BLUE, 15)
# L8 surname marker
mx8, my8 = X(19)+CW/2, Y(8)+LH/2
a(f'<path d="M{mx8} {my8-8} l3 6 l7 1 l-5 5 l1 7 l-6 -3 l-6 3 l1 -7 l-5 -5 l7 -1 z" fill="{BLUE}"/>')
# ③ L24-L40 meaning + specific words (title)
block(9, 19, 24, 40, '#FFC98A', .9)
label(X(9)+6, Y(36)+4, 'meaning +', GREEN)
label(X(9)+6, Y(34)+6, 'specific words', GREEN)
strike(X(9)+6, Y(28)+6, 'which paper', 15)
# ④ L41-L52 title still read; delivered by parallel pipes (name <- title)
block(9, 19, 41, 52, '#FFDDB0', .9)
label(X(9)+6, Y(47)+6, 'read by L52', BLUE)
for l in (44, 46, 48, 50, 52, 54):
    pipe(X(19)+CW-2, Y(l)+LH/2, X(29)-6, Y(l)+LH/2, 6)
label(X(20)+2, Y(42)+4, 'many parallel', GREEN, 15)
label(X(20)+2, Y(40)+6, 'pipes', GREEN, 15)
# ⑤ L48-L56 held at the names (hatched)
block(29, N-1, 48, 56, 'url(#hatch)')
block(29, N-1, 48, 56, '#E8F0FA', .45)
label(X(30), Y(52)+6, 'held at the names, not as words', BLUE)
strike(X(20)+2, Y(57)+6, 'format fixed here', 14)
# ⑥ L57-L63 MLPs write the name
block(29, N-1, 57, 63, '#F6B8B0', .85)
label(X(31), Y(60)+8, 'MLPs write the name', BLUE)
# padlock at the first name token
px, py = X(29)+CW/2, Y(63)+LH/2+2
a(f'<path d="M{px-5} {py-3} v-4 a5 5 0 0 1 10 0 v4" fill="none" stroke="{RED}" stroke-width="2"/>'
  f'<rect x="{px-8}" y="{py-3}" width="16" height="12" rx="2" fill="{RED}"/>')
# gap ①: broken pipe between "held" and "write", at the right of the names
gx = X(44)+CW/2
pipe(gx, Y(52), gx, Y(55)+2, 7, GREYC, '#EEF0F3'); pipe(gx, Y(59), gx, Y(61), 7, GREYC, '#EEF0F3')
a(f'<path d="M{gx-8} {Y(55)+8} l5 -4 l5 4 l5 -4 M{gx-8} {Y(58)+4} l5 -4 l5 4 l5 -4" fill="none" stroke="{GREYC}" stroke-width="2"/>')

# gap ②: multiple-choice card below the grid with a broken pipe into it
cx2, cy2 = X(3), Y(0) + LH + 34
a(f'<rect x="{cx2-22}" y="{cy2}" width="44" height="34" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
for k, s in enumerate('ABCD'):
    a(f'<circle cx="{cx2-12+k*8}" cy="{cy2+12}" r="2.6" fill="{INK if k == 0 else "none"}" stroke="{INK}" stroke-width="1.2"/>')
txt(cx2, cy2+29, 'A B C D', 9.5, PALE_T, 'middle')
pipe(cx2, cy2, cx2, cy2-10, 7, GREYC, '#EEF0F3'); pipe(cx2, Y(0)+LH+6, cx2, Y(0)+LH, 7, GREYC, '#EEF0F3')
a(f'<path d="M{cx2-8} {cy2-14} l5 -4 l5 4 l5 -4" fill="none" stroke="{GREYC}" stroke-width="2"/>')
txt(cx2+40, cy2+22, 'the multiple-choice test (defines "recognised")', 14, GREYC)

# ---- numbered markers on the plot (same numbers as the right column) ----
mark(X(N-1)+2, Y(62)+LH/2, '⑥', '#C0392B')
mark(gx+22, Y(53), '?', GREYC)
mark(X(N-1)+2, Y(50)+LH/2, '⑤', '#3C78B4')
mark(X(27)-4, Y(43)+4, '④', '#1F6F8B')
mark(X(19)+2, Y(25)+LH/2, '③', '#D9772B')
mark(X(27)-4, Y(23)+4, '②', '#B54708')
mark(X(N-1)+2, Y(2)+LH/2, '①', '#6A7385')
mark(cx2+30, cy2+2, '?', GREYC)
# ---- right column ----
txt(RX, Y(63)-16, 'Details by stage (colour = how it is supported)', 15, PALE_T, weight='bold')
ENT = []   # (marker xy, list of (text, colour, weight[, italic]))
def entry(y, num, numcol, rows, mark=None):
    a(f'<circle cx="{RX+12}" cy="{y-5}" r="12" fill="{numcol}"/>'); txt(RX+12, y, num, 13, '#fff', 'middle', 'bold')
    for k, r in enumerate(rows):
        s, col, w = r[:3]; it = r[3] if len(r) > 3 else False
        if col == 'strike': strike(RX+34, y + k*20, s, 14)
        else: txt(RX+34, y + k*20, s, 14.5 if w == 'bold' else 14, col, weight=w, italic=it)
    if mark and mark[0] >= X(N-2):
        a(f'<path d="M{GR} {mark[1]} L {RX-16} {y-5}" fill="none" stroke="{PALE_T}" stroke-width="1.4"/>')
yy = Y(63) + 12
entry(yy, '⑥', '#C0392B', [('MLP − attention ≈ +0.04 at each of L57–L61', BLUE, 'bold'),
                            ('recognised − not grows to +0.21 at the output', BLUE, 'normal'),
                            ('first name token hardest; giving the initial: 4% → 15%', GREEN, 'bold'),
                            ('"the signal is too weak": pushing it harder, 2.5% → 2.8%', RED, 'normal')], (X(N-1), Y(61)))
yy += 96
entry(yy, '?', GREYC, [('Gap ①: at which step does "who wrote this paper" enter?', GREYC, 'bold'),
                        ('only indirect evidence so far', GREYC, 'normal')], (gx+3, Y(57)))
yy += 54
entry(yy, '⑤', '#3C78B4', [('probe reads +0.06 more than the lens at L48; lens even < 0', BLUE, 'bold'),
                            ('injected author direction: 2.5% → 9.7%, mostly a write channel', BLUE, 'normal'),
                            ('L52–L56 MLPs carry paper info, not name directions', BLUE, 'normal'),
                            ('format fixed at L56', 'strike', 'normal'), ('→ the format layer is not pinned down (sink artefact)', RED, 'bold')], (X(N-1), Y(50)))
yy += 118
entry(yy, '④', '#1F6F8B', [('name ← title, L44–L55; cutting any one layer costs ≤ 1.25%', GREEN, 'bold'),
                            ('put back restores ~100% by L52; take-away agrees', GREEN, 'normal')], (X(25), Y(44)))
yy += 60
entry(yy, '③', '#D9772B', [('made-up title ~75%; the rest sits on rare words; identity ≈ 0', GREEN, 'bold'),
                            ('stores "which paper this is"', 'strike', 'normal'),
                            ('→ not a general paper identity, one small locked exception', RED, 'bold')], (X(19), Y(32)))
yy += 80
entry(yy, '②', '#B54708', [('":" moves 4.7× more for a new question than a new paper (L4)', BLUE, 'bold')], (X(28)+CW/2, Y(18)))
yy += 40
entry(yy, '★', BLUE, [('small locked exception: L8 surname signal beyond topic, +0.05', BLUE, 'bold'),
                       ('two of three tests marginal; about half of the raw signal is topic', PALE_T, 'normal')], (mx8, my8))
yy += 60
entry(yy, '①', '#6A7385', [('same title under two questions: cos ≈ 1.00 at L4', GREYC, 'bold'),
                            ('→ question-only tests cannot separate meaning from identity', GREYC, 'normal')], (X(N-1), Y(2)))
yy += 60
entry(yy, '?', GREYC, [('Gap ②: "recognised" comes from the multiple-choice prompt,', GREYC, 'bold'),
                        ('which was never measured inside', GREYC, 'normal')], (cx2+22, cy2+17))

# ---- legend + three grey lines ----
LY = cy2 + 70
txt(X0, LY, 'Colour:', 15, INK, weight='bold'); xx = X0 + 76
for lab, col in (('proven by one experiment', BLUE), ('joint (several together)', GREEN), ('cannot be decided', GREYC), ('refuted / overturned', RED)):
    a(f'<rect x="{xx}" y="{LY-13}" width="16" height="16" rx="3" fill="{col}"/>'); txt(xx+24, LY, lab, 14.5, col, weight='bold'); xx += 44 + 9.0*len(lab)
strike(xx+10, LY, 'old claim', 14)
a(f'<image x="{X0}" y="{LY+16}" width="497" height="50" xlink:href="{b64("tex_main_f.png")}"/>')
a(f'<image x="{X0}" y="{LY+68}" width="906" height="28" xlink:href="{b64("tex_main_n.png")}"/>')
txt(X0, LY+118, 'spec > 0: the true title helps the true author; R ≈ 1: the copied state restores all of the true-title advantage', 14, PALE_T)
a('</svg>')
open('main_v2.svg', 'w').write('\n'.join(o))
print('ok', W, H, LY+130)
