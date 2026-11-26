# MAIN figure v3 (from v2): pipes run into the name slots; wider name region (first author's tokens + "…");
# right column ordered ① bottom → ⑥ top, level with each band; stage ③ / ④ clearly separated at L40;
# larger multiple-choice card. Content unchanged (27_v67/experiment_tree.md). 2026-11-25.
import base64, html
QT = ['Who', ' are', ' the', ' authors', ' of', ' the', ' paper', ' titled', ' "']
TT = ['A', 'ffect', ' dynamics', ',', ' bere', 'av', 'ement', ' and', ' resilience', ' to', ' loss']
AT = ['"', ' (', '2', '0', '0', '7', ')?↵', 'Authors', ':']
NT = [' Kar', 'in', ' G', '.', ' Co', 'if', 'man', ', …']                    # first author's tokens, then the rest
TOKS = QT + TT + AT + NT
GRP = [0]*9 + [1]*11 + [2]*9 + [3]*len(NT)
N = len(TOKS); NAME0 = 29
WID = [23]*29 + [46]*len(NT)
X0, Y0, LH = 96, 300, 15.0
XS = [X0]
for w in WID: XS.append(XS[-1] + w)
GR = XS[-1]; RX = GR + 64; W, H = RX + 630, 1660
INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
def X(i): return XS[i]
def CWi(i): return WID[i]
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
def block(c0, c1, l0, l1, fill, op=1, stroke='none', sw=1.6, dash=None, inset=0):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{X(c0)}" y="{Y(l1)+inset}" width="{X(c1+1)-X(c0)}" height="{(l1-l0+1)*LH-2*inset}" rx="4" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def label(x, y, s, col, size=16, anchor='start'):
    a(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="bold" fill="#FBFAF5" stroke="#FBFAF5" stroke-width="5" text-anchor="{anchor}" font-family="{SANS}">{esc(s)}</text>')
    txt(x, y, s, size, col, anchor, 'bold')
def mark(x, y, num, col, r=11):
    a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="#fff" stroke-width="2"/>')
    txt(x, y+5, num, 13, '#fff', 'middle', 'bold')
def pipe(x1, y1, x2, y2, w=7, col='#1F6F8B', inner='#DCEFF5', head=False):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
      f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{inner}" stroke-width="{w-4}" stroke-linecap="round"/>')
    if head:
        a(f'<path d="M{x2+2} {y2-7} L{x2+12} {y2} L{x2+2} {y2+7} Z" fill="{col}"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#3C78B4" stroke-width="2.2" opacity=".28"/></pattern></defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
txt(24, 48, 'Read early, said late: the whole story on one map', 36, INK, fam=HAND)
txt(24, 78, 'x: the prompt as real Qwen3 tokens · y: layers L0 (bottom) to L63 (top) · read the plot bottom-up; details for each stage sit level with it on the right.', 15, DET)

# ---- header ----
bx0, bx1, by = X(9), X(20), Y0-150
mx = (bx0 + bx1)/2
a(f'<path d="M{bx0+6} {by+10} Q {(bx0+mx)/2} {by-6} {mx} {by+8} Q {(mx+bx1)/2} {by-6} {bx1-6} {by+10} V {by+36} Q {(mx+bx1)/2} {by+22} {mx} {by+34} Q {(bx0+mx)/2} {by+22} {bx0+6} {by+36} Z" '
  f'fill="#FFF1DE" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/><line x1="{mx}" y1="{by+8}" x2="{mx}" y2="{by+34}" stroke="{INK}" stroke-width="1.8"/>')
txt(mx, by-12, 'the title (a book the model reads)', 15, INK, 'middle', fam=HAND)
txt((X(NAME0)+GR)/2, by-12, 'the author names: empty slots to fill', 15, INK, 'middle', fam=HAND)
txt((X(NAME0)+GR)/2, by+8, "(first author's tokens shown; the other names follow, every token scored)", 14, PALE_T, 'middle')
txt((X(0)+X(9))/2, by+30, 'the question', 15, INK, 'middle', fam=HAND)
txt((X(20)+X(29))/2, by+30, 'after the title', 15, INK, 'middle', fam=HAND)
for i, (t, g) in enumerate(zip(TOKS, GRP)):
    w = CWi(i)
    if g == 3:
        a(f'<rect x="{X(i)+3}" y="{Y0-100}" width="{w-6}" height="92" rx="5" fill="#fff" stroke="{INK}" stroke-width="1.8" stroke-dasharray="5 3"/>')
        cx, cy = X(i) + w/2 + 6, Y0 - 16
        a(f'<text x="{cx}" y="{cy}" font-size="16" fill="{INK}" font-weight="bold" transform="rotate(-90 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')
    else:
        col = ['#EEF1F5', '#FFF1DE', '#E8F0FA'][g]
        a(f'<rect x="{X(i)+1}" y="{Y0-100}" width="{w-2}" height="92" rx="4" fill="{col}" stroke="#C9CED6"/>')
        cx, cy = X(i) + w/2 + 5, Y0 - 14
        a(f'<text x="{cx}" y="{cy}" font-size="14" fill="{INK}" transform="rotate(-90 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')

# ---- grid ----
for l in range(0, 64, 4):
    a(f'<line x1="{X0}" x2="{GR}" y1="{Y(l)+LH}" y2="{Y(l)+LH}" stroke="#E8EBEF"/>')
for l in (0, 8, 16, 24, 32, 40, 48, 56, 63):
    txt(X0-8, Y(l)+LH-2, f'L{l}', 14, PALE_T, 'end')
a(f'<rect x="{X0}" y="{Y(63)}" width="{GR-X0}" height="{64*LH}" fill="none" stroke="#C9CED6"/>')
a(f'<line x1="{X(NAME0)}" y1="{Y(63)}" x2="{X(NAME0)}" y2="{Y(0)+LH}" stroke="#C9CED6" stroke-width="1.4" stroke-dasharray="3 4"/>')

# ① L0-L4
block(0, N-1, 0, 4, '#DDE2E8', .8)
label(X(1), Y(2)+8, 'same words → same state', GREYC)
# ② L4-L23
block(9, 19, 4, 23, '#FFEFD9', 1)
label(X(9)+6, Y(15)+6, 'early read-in', BLUE)
mx8, my8 = X(19)+CWi(19)/2, Y(8)+LH/2
a(f'<path d="M{mx8} {my8-8} l3 6 l7 1 l-5 5 l1 7 l-6 -3 l-6 3 l1 -7 l-5 -5 l7 -1 z" fill="{BLUE}"/>')
# ③ L24-L40 (orange) and ④ L41-L52 (yellow), separated by a divider at L40/L41
block(9, 19, 24, 40, '#FFC98A', .95, inset=1)
label(X(9)+6, Y(35)+4, 'meaning +', GREEN)
label(X(9)+6, Y(33)+6, 'specific words', GREEN)
strike(X(9)+6, Y(28)+6, 'which paper', 15)
block(9, 19, 41, 52, '#FBEAA0', .95, inset=2)
a(f'<line x1="{X(9)-6}" y1="{Y(40)}" x2="{X(20)+6}" y2="{Y(40)}" stroke="{INK}" stroke-width="2.4" stroke-dasharray="7 4"/>')
txt(X(9)-10, Y(40)+5, 'L40', 14, INK, 'end', 'bold')
label(X(9)+6, Y(47)+6, 'read by L52', BLUE)
# ':' rail L4-L56 (drawn before the pipes so the pipes pass over it)
cxr = X(28) + CWi(28)/2
pipe(cxr, Y(4)+LH, cxr, Y(56), 8, '#3C78B4', '#E3EDF8')
label(X(20)+2, Y(21)+6, '":" follows', BLUE, 15)
label(X(20)+2, Y(19)+8, 'the question', BLUE, 15)
# ⑤ L48-L56 held at the names
block(NAME0, N-1, 48, 56, 'url(#hatch)')
block(NAME0, N-1, 48, 56, '#E8F0FA', .45)
label(X(NAME0)+52, Y(51)+3, 'held at the names, not as words', BLUE, 15)
# ④ pipes: title → through ':' → into the name slots
for l in (44, 46, 48, 50, 52, 54):
    pipe(X(20)-2, Y(l)+LH/2, X(NAME0)+18, Y(l)+LH/2, 7, head=True)
label(X(20)+2, Y(42)+6, 'many parallel', GREEN, 15)
label(X(20)+2, Y(40)+8, 'pipes', GREEN, 15)
strike(X(20)+2, Y(58)+6, 'format fixed here', 14)
# ⑥ L57-L63
block(NAME0, N-1, 57, 63, '#F6B8B0', .85)
label(X(NAME0)+44, Y(60)+8, 'MLPs write the name', BLUE)
px, py = X(NAME0)+CWi(NAME0)/2, Y(62)+2
a(f'<path d="M{px-6} {py-3} v-5 a6 6 0 0 1 12 0 v5" fill="none" stroke="{RED}" stroke-width="2.4"/>'
  f'<rect x="{px-9}" y="{py-3}" width="18" height="14" rx="2" fill="{RED}"/>')
# gap ①: broken pipe between ⑤ and ⑥, right side of the names
gx = X(N-1) + CWi(N-1)/2
pipe(gx, Y(52), gx, Y(55)+4, 7, GREYC, '#EEF0F3'); pipe(gx, Y(59)+4, gx, Y(61), 7, GREYC, '#EEF0F3')
a(f'<path d="M{gx-9} {Y(56)+6} l5 -4 l5 4 l5 -4 M{gx-9} {Y(58)+6} l5 -4 l5 4 l5 -4" fill="none" stroke="{GREYC}" stroke-width="2"/>')

# multiple-choice card (defines "recognised") + gap ② broken pipe into the grid
cx0, cy0 = X(0)+10, Y(0) + LH + 50
a(f'<rect x="{cx0}" y="{cy0}" width="380" height="132" rx="10" fill="#fff" stroke="{INK}" stroke-width="2.2"/>')
txt(cx0+16, cy0+26, 'Which author list wrote this paper?', 15, INK, weight='bold')
opts = ['A  true author list', 'B  another team', 'C  another team', 'D  another team']
for k, s in enumerate(opts):
    yy = cy0 + 50 + k*21
    a(f'<circle cx="{cx0+24}" cy="{yy-5}" r="6" fill="{INK if k == 0 else "#fff"}" stroke="{INK}" stroke-width="1.6"/>')
    txt(cx0+38, yy, s, 14, INK)
txt(cx0+200, cy0+71, 'all four orders right', 14, DET)
txt(cx0+200, cy0+92, '= "recognised"', 14, DET, weight='bold')
pc = cx0 + 190
pipe(pc, cy0, pc, cy0-14, 7, GREYC, '#EEF0F3'); pipe(pc, Y(0)+LH+14, pc, Y(0)+LH, 7, GREYC, '#EEF0F3')
a(f'<path d="M{pc-9} {cy0-20} l5 -4 l5 4 l5 -4" fill="none" stroke="{GREYC}" stroke-width="2"/>')

# ---- numbered markers ----
mark(X(N-2)+10, Y(61)+LH/2, '⑥', '#C0392B')
mark(gx-26, Y(58)+LH/2, '?', GREYC)
mark(X(N-1)+CWi(N-1)-12, Y(49)+LH/2, '⑤', '#3C78B4')
mark(X(27), Y(45)+LH/2, '④', '#1F6F8B')
mark(X(19)+6, Y(25)+LH/2, '③', '#D9772B')
mark(X(27), Y(23)+LH/2, '②', '#B54708')
mark(X(N-1)+CWi(N-1)-12, Y(2)+LH/2, '①', '#6A7385')
mark(pc+22, cy0-8, '?', GREYC)

# ---- right column: ① bottom → ⑥ top, level with the bands ----
ENTRIES = [  # (anchor y on the plot, num, colour, rows); listed top → bottom
    (Y(61), '⑥', '#C0392B', [('MLP − attention ≈ +0.04 at each of L57–L61', BLUE, 'bold'),
                             ('recognised − not grows to +0.21 at the output', BLUE, 'normal'),
                             ('first name token hardest; giving the initial: 4% → 15%', GREEN, 'bold'),
                             ('"the signal is too weak": pushing it harder, 2.5% → 2.8%', RED, 'normal')]),
    (Y(57), '?', GREYC, [('Gap ①: at which step does "who wrote this paper" enter?', GREYC, 'bold'),
                         ('only indirect evidence so far', GREYC, 'normal')]),
    (Y(52), '⑤', '#3C78B4', [('probe reads +0.06 more than the lens at L48; lens even < 0', BLUE, 'bold'),
                             ('injected author direction: 2.5% → 9.7%, mostly a write channel', BLUE, 'normal'),
                             ('L52–L56 MLPs carry paper info, not name directions', BLUE, 'normal'),
                             ('format fixed at L56', 'strike', 'normal'),
                             ('→ the format layer is not pinned down (sink artefact)', RED, 'bold')]),
    (Y(46), '④', '#1F6F8B', [('name ← title, L44–L55; cutting any one layer costs ≤ 1.25%', GREEN, 'bold'),
                             ('put back restores ~100% by L52; take-away agrees', GREEN, 'normal')]),
    (Y(32), '③', '#D9772B', [('made-up title ~75%; the rest sits on rare words; identity ≈ 0', GREEN, 'bold'),
                             ('stores "which paper this is"', 'strike', 'normal'),
                             ('→ not a general paper identity, one small locked exception', RED, 'bold')]),
    (Y(16), '②', '#B54708', [('":" moves 4.7× more for a new question than a new paper (L4)', BLUE, 'bold')]),
    (Y(9), '★', BLUE, [('small locked exception: L8 surname signal beyond topic, +0.05', BLUE, 'bold'),
                       ('two of three tests marginal; about half of the raw signal is topic', PALE_T, 'normal')]),
    (Y(2), '①', '#6A7385', [('same title under two questions: cos ≈ 1.00 at L4', GREYC, 'bold'),
                            ('→ question-only tests cannot separate meaning from identity', GREYC, 'normal')]),
    (cy0+20, '?', GREYC, [('Gap ②: "recognised" comes from the multiple-choice prompt,', GREYC, 'bold'),
                          ('which was never measured inside', GREYC, 'normal')]),
]
# centre each entry on its anchor, then push down to avoid overlap (order preserved)
LINE = 21; tops = []; prev_bot = Y(63) - 6
for anchor, num, col, rows in ENTRIES:
    h = LINE*len(rows); top = max(anchor - h/2, prev_bot + 12)
    tops.append(top); prev_bot = top + h
txt(RX, Y(63) - 22, 'Details by stage, level with the plot (colour = how it is supported)', 15, PALE_T, weight='bold')
for (anchor, num, col, rows), top in zip(ENTRIES, tops):
    y = top + 15
    a(f'<circle cx="{RX+12}" cy="{y-5}" r="12" fill="{col}"/>'); txt(RX+12, y, num, 13, '#fff', 'middle', 'bold')
    for k, r in enumerate(rows):
        s, c, w = r
        if c == 'strike': strike(RX+34, y + k*LINE, s, 14)
        else: txt(RX+34, y + k*LINE, s, 14.5 if w == 'bold' else 14, c, weight=w)
    a(f'<path d="M{GR+4} {anchor} L {RX-16} {y-5}" fill="none" stroke="#D5D9DF" stroke-width="1.2"/>')

# ---- legend + three grey lines ----
LY = cy0 + 170
txt(X0, LY, 'Colour:', 15, INK, weight='bold'); xx = X0 + 76
for lab, col in (('proven by one experiment', BLUE), ('joint (several together)', GREEN), ('cannot be decided', GREYC), ('refuted / overturned', RED)):
    a(f'<rect x="{xx}" y="{LY-13}" width="16" height="16" rx="3" fill="{col}"/>'); txt(xx+24, LY, lab, 14.5, col, weight='bold'); xx += 44 + 9.0*len(lab)
strike(xx+10, LY, 'old claim', 14)
a(f'<image x="{X0}" y="{LY+16}" width="497" height="50" xlink:href="{b64("tex_main_f.png")}"/>')
a(f'<image x="{X0}" y="{LY+68}" width="906" height="28" xlink:href="{b64("tex_main_n.png")}"/>')
txt(X0, LY+118, 'spec > 0: the true title helps the true author; R ≈ 1: the copied state restores all of the true-title advantage', 14, PALE_T)
a('</svg>')
open('main_v3.svg', 'w').write('\n'.join(o).replace(f'height="{H}" viewBox="0 0 {W} {H}"', f'height="{LY+140}" viewBox="0 0 {W} {LY+140}"'))
print('ok', W, LY+140)
