# Stage expansion L24-L40, v2: three columns, main line centred top-to-bottom, colour = argument type, pictograms.
# Content unchanged from v1 (from 27_v67/experiment_tree.md). 2026-11-24.
import base64, html
import picto as P
W, H = 1900, 1690
INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
LC = (24, 384); CC = (420, 1480); RC = (1516, 1876)          # column x ranges
MID = (CC[0] + CC[1]) / 2
o = []; a = o.append
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def txt(x, y, s, size=15, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def lines(x, y, rows, dy=20):
    """rows: list of (text, size, colour, weight[, italic])"""
    for k, r in enumerate(rows):
        s, size, col, w = r[:4]; it = r[4] if len(r) > 4 else False
        txt(x, y + k*dy, s, size, col, weight=w, italic=it)
def strike(x, y, s, size=15):
    w = 0.6*size*len(s); txt(x, y, s, size, '#9AA3AE', italic=True)
    a(f'<line x1="{x-2}" x2="{x+w}" y1="{y-size*0.33}" y2="{y-size*0.33}" stroke="#9AA3AE" stroke-width="1.8"/>')
def box(x, y, w, h, stroke='#C9CED6', fill='#fff', sw=1.8, rx=12):
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def down(y1, y2, x=MID, sw=3.2):
    a(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2-4}" stroke="{INK}" stroke-width="{sw}" marker-end="url(#am)"/>')
def side(x1, x2, y, col):
    a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="2" marker-end="url(#as{col[1:]})"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs>' + P.DEFS + f'<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
  + ''.join(f'<marker id="as{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for c in (GREYC, BLUE, RED, GREEN, PALE_T)) + '</defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
# title + locator
txt(250, 52, 'Stage ③ · L24–L40: what is read is meaning and specific words, not paper identity', 32, INK, fam=HAND)
txt(250, 82, 'Read top to bottom along the main line; side columns hold what was rewritten or ruled out (left) and exceptions and dependencies (right).', 15, DET)
lx, ly = 24, 20; gx0, gy0, gw, gh = lx+12, ly+28, 186, 92
box(lx, ly, 210, 130, rx=8)
txt(lx+12, ly+20, 'where on the main map', 14, PALE_T)
a(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="#F4F5F7" stroke="#D5D9DF"/>')
cw, lh = gw/48, gh/64
for c0, c1, col in ((0, 8, '#EEF1F5'), (9, 19, '#FFF1DE'), (20, 28, '#E8F0FA'), (29, 47, '#FBE3E1')):
    a(f'<rect x="{gx0+c0*cw}" y="{gy0}" width="{(c1-c0+1)*cw}" height="{gh}" fill="{col}"/>')
a(f'<rect x="{gx0+9*cw}" y="{gy0+(63-40)*lh}" width="{11*cw}" height="{17*lh}" fill="#FFC98A" stroke="#D9772B" stroke-width="2"/>')
txt(gx0+20*cw+4, gy0+(63-33)*lh, '← L24–L40', 14, '#B8601A')

# column dividers + headings
TOP, BOT = 200, 1540
for xx in (LC[1]+18, RC[0]-18):
    a(f'<line x1="{xx}" y1="{TOP-26}" x2="{xx}" y2="{BOT}" stroke="#D5D9DF" stroke-width="1.4"/>')
txt((LC[0]+LC[1])/2, TOP-8, 'Rewritten & ruled out', 15, PALE_T, 'middle', 'bold')
txt(MID, TOP-8, 'Main line', 16, INK, 'middle', 'bold')
txt((RC[0]+RC[1])/2, TOP-8, 'Exceptions & dependencies', 15, PALE_T, 'middle', 'bold')

# ---------- Row A: two equal boxes (lead-in, paraphrase) ----------
AY, AH = TOP+12, 210; BWA = (CC[1]-CC[0]-30)/2
for k, (pic, title, det, concl) in enumerate((
        (P.words_carry, 'Which title words carry the signal?',
         ['swap one word class for random tokens', 'or for WordNet synonyms'],
         [('content words carry it by meaning', 16, BLUE, 'bold'), ('random −0.37 vs synonym −0.09 of 0.33', 14, DET, 'normal'), ('descriptive', 14, BLUE, 'normal', True)]),
        (P.paraphrase, 'Paraphrased title',
         ['reword the title, keep the meaning;', 'is the state still closer to the original?'],
         [('meaning is encoded beyond the words', 16, BLUE, 'bold'), ('closeness above L4 peaks at L36, +0.16', 14, DET, 'normal'), ('pre-registered', 14, BLUE, 'normal', True)]))):
    bx = CC[0] + k*(BWA+30)
    box(bx, AY, BWA, AH)
    a(pic(bx+16, AY+40))
    tx = bx + 190
    txt(tx, AY+32, title, 17, INK, weight='bold')
    lines(tx, AY+58, [(s, 14, DET, 'normal') for s in det])
    lines(tx, AY+122, concl, 21)
a(f'<path d="M{CC[0]+BWA/2} {AY+AH} V {AY+AH+22} H {MID} M{CC[0]+BWA+30+BWA/2} {AY+AH} V {AY+AH+22} H {MID}" fill="none" stroke="{INK}" stroke-width="3.2"/>')
txt(MID+12, AY+AH+44, 'it is meaning — but is it also this exact paper?', 15, DET, italic=True)

# ---------- Row B: made-up title ----------
BY, BH = AY+AH+60, 228
down(AY+AH+22, BY)
box(CC[0], BY, CC[1]-CC[0], BH, stroke=INK, sw=2.4)
a(P.madeup(CC[0]+24, BY+28))
tx = CC[0] + 330
txt(tx, BY+36, 'Made-up title with the same meaning', 19, INK, weight='bold')
lines(tx, BY+64, [('score the true authors under the true title, a same-meaning made-up title', 14, DET, 'normal'),
                  ('and five other papers’ titles; how much of “true − other” does the made-up title bring back?', 14, DET, 'normal')])
lines(tx, BY+128, [('a same-meaning made-up title brings back ~75% (0.75 [0.72, 0.78])', 17, BLUE, 'bold'),
                   ('the real title adds a small extra, +0.11', 15, BLUE, 'normal'),
                   ('locked test', 14, BLUE, 'normal', True)], 24)

# ---------- question node ----------
QY = BY+BH+40
down(BY+BH, QY)
a(f'<rect x="{MID-260}" y="{QY}" width="520" height="52" rx="26" fill="#FFF6E5" stroke="#D9772B" stroke-width="2.4"/>')
txt(MID, QY+33, 'What is the small extra part?', 18, INK, 'middle', 'bold')

# ---------- Row C: four parallel equal boxes ----------
CY, CH = QY+100, 300; gap = 20; BWC = (CC[1]-CC[0]-3*gap)/4
a(f'<line x1="{MID}" y1="{QY+52}" x2="{MID}" y2="{QY+72}" stroke="{INK}" stroke-width="3.2"/>')
a(f'<line x1="{CC[0]+BWC/2}" y1="{QY+72}" x2="{CC[1]-BWC/2}" y2="{QY+72}" stroke="{INK}" stroke-width="3.2"/>')
branches = [
    (P.rare_common, 'Rare vs common words', ['black out only rare (or only', 'common) words of the true title'],
     [('sits on specific words', 15, BLUE, 'bold'), ('rare −0.16 · common −0.03', 14, DET, 'normal'), ('locked test', 14, BLUE, 'normal', True)]),
    (P.recog_citation, 'Recognised / citation check', ['is the extra larger for recognised', 'or much-cited papers?'],
     [('not larger if recognised;', 15, BLUE, 'bold'), ('smaller if much-cited', 15, BLUE, 'bold'), ('locked test', 14, BLUE, 'normal', True)]),
    (P.variance_pie, 'Variance split', ['what explains the title state:', 'words, meaning or identity?'],
     [('identity adds ≈ 0', 15, BLUE, 'bold'), ('meaning adds 0.17–0.27', 14, DET, 'normal'), ('locked test', 14, BLUE, 'normal', True)]),
    (P.subspace, 'Paper-facts subspace', ['swap only the slice of the', 'state that predicts facts'],
     [('no author info there', 15, BLUE, 'bold'), ('slice 0.004 vs whole 0.93', 14, DET, 'normal'), ('pre-registered', 14, BLUE, 'normal', True)]),
]
for k, (pic, title, det, concl) in enumerate(branches):
    bx = CC[0] + k*(BWC+gap)
    a(f'<line x1="{bx+BWC/2}" y1="{QY+72}" x2="{bx+BWC/2}" y2="{CY-4}" stroke="{INK}" stroke-width="2.6" marker-end="url(#am)"/>')
    box(bx, CY, BWC, CH)
    a(pic(bx + (BWC-170)/2 + 14, CY+14))
    txt(bx+14, CY+148, title, 15, INK, weight='bold')
    lines(bx+14, CY+172, [(s, 14, DET, 'normal') for s in det], 18)
    lines(bx+14, CY+226, concl, 20)
    a(f'<path d="M{bx+BWC/2} {CY+CH} V {CY+CH+26} H {MID}" fill="none" stroke="{GREEN}" stroke-width="3.2"/>')

# ---------- Row D: joint conclusion ----------
DY = CY+CH+56
down(CY+CH+26, DY)
box(CC[0]+120, DY, CC[1]-CC[0]-240, 76, stroke=GREEN, fill='#EAF6EC', sw=2.6)
txt(MID, DY+32, 'The real title’s small extra comes from specific words,', 18, GREEN, 'middle', 'bold')
txt(MID, DY+58, 'not from recognising the paper   (only all four together)', 16, GREEN, 'middle')

# ---------- Row E: overturned ----------
EY = DY+76+40
down(DY+76, EY)
box(CC[0]+60, EY, CC[1]-CC[0]-120, 84, stroke='#E3B5AF', fill='#FDF3F1', sw=2)
strike(CC[0]+84, EY+32, 'middle layers store “which paper this is” (partly supported)', 16)
txt(CC[0]+84, EY+64, '→ not a general paper identity, with one small locked exception', 18, RED, weight='bold')

# ---------- Row F: stage conclusion ----------
FY = EY+84+40
down(EY+84, FY)
box(CC[0]+40, FY, CC[1]-CC[0]-80, 78, stroke=GREEN, fill='#FFF1DE', sw=3)
txt(MID, FY+34, 'Stage conclusion: what is read in L24–L40 is meaning and', 19, GREEN, 'middle', 'bold')
txt(MID, FY+60, 'specific words, not paper identity', 19, GREEN, 'middle', 'bold')

# ---------- LEFT column ----------
# L1 at row B: ceiling audit rewrote the early tests
l1y = BY + 10
box(LC[0], l1y, LC[1]-LC[0], 222, stroke='#D5D9DF', fill='#FBFBFC')
a(P.ceiling(LC[0]+16, l1y+18))
txt(LC[0]+16, l1y+96, 'Ceiling audit', 15, INK, weight='bold')
lines(LC[0]+16, l1y+118, [('early tests (change the question,', 14, PALE_T, 'normal'), ('copy the state, find the paper again)', 14, PALE_T, 'normal')], 18)
strike(LC[0]+16, l1y+164, '“supports identity”', 14)
txt(LC[0]+16, l1y+188, '→ cannot separate:', 14, GREYC, weight='bold')
txt(LC[0]+16, l1y+206, 'same words, same state', 14, GREYC, weight='bold')
side(LC[1], CC[0]-4, BY+BH/2, GREYC)
# L2 at row E: ruled-out alternatives (for the exception)
l2y = EY - 18
box(LC[0], l2y, LC[1]-LC[0], 124, stroke='#D5D9DF', fill='#FBFBFC')
for k, (alt, why) in enumerate((('surname simply in the title', 'source check'), ('only the field’s common surnames', 'topic-matched test'))):
    yy = l2y + 18 + k*52
    a(P.crossed(LC[0]+14, yy, 18))
    txt(LC[0]+44, yy+12, alt, 14, '#7A3A33')
    txt(LC[0]+44, yy+31, f'ruled out by the {why}', 14, PALE_T)
side(LC[1], CC[0]+56, EY+42, RED)

# ---------- RIGHT column ----------
r1y = BY + 10
box(RC[0], r1y, RC[1]-RC[0], 150, stroke='#D5D9DF', fill='#FBFBFC')
a(P.pipe_dep(RC[0]+16, r1y+16))
txt(RC[0]+16, r1y+82, 'From stage ④ (route)', 15, INK, weight='bold')
lines(RC[0]+16, r1y+104, [('the title is read and delivered', 14, PALE_T, 'normal'), ('by L52 (put back 0.995)', 14, PALE_T, 'normal')], 18)
a(f'<line x1="{RC[0]}" y1="{BY+BH/2}" x2="{CC[1]+4}" y2="{BY+BH/2}" stroke="{PALE_T}" stroke-width="2" marker-end="url(#as{PALE_T[1:]})"/>')
r2y = EY - 30
box(RC[0], r2y, RC[1]-RC[0], 150, stroke='#C9D6E8', fill='#F5F8FC')
a(P.name_tag(RC[0]+16, r2y+12))
txt(RC[0]+16, r2y+66, 'Small locked exception', 15, INK, weight='bold')
txt(RC[0]+16, r2y+88, 'L8 surname signal beyond topic, +0.05', 14, BLUE, weight='bold')
lines(RC[0]+16, r2y+110, [('two of three tests marginal;', 14, PALE_T, 'normal'), ('about half of the raw signal is topic', 14, PALE_T, 'normal')], 18)
a(f'<line x1="{RC[0]}" y1="{EY+42}" x2="{CC[1]-56}" y2="{EY+42}" stroke="{BLUE}" stroke-width="2" marker-end="url(#as{BLUE[1:]})"/>')

# caveats from the tree (H2 ⑥ s. 73, H2 ⑨a s. 80), added 2026-11-25: dashed = cannot be decided
def caveat(y, rows, ay):
    hh = 26 + 20*len(rows)
    a(f'<rect x="{RC[0]}" y="{y}" width="{RC[1]-RC[0]}" height="{hh}" rx="12" fill="#F7F8FA" stroke="{GREYC}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    for j, (s, w) in enumerate(rows): txt(RC[0]+16, y+26+20*j, s, 16, INK if w == 'bold' else GREYC, weight=w)
    a(f'<line x1="{RC[0]}" y1="{ay}" x2="{CC[1]+4}" y2="{ay}" stroke="{GREYC}" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#as{PALE_T[1:]})"/>')
caveat(BY+172, [('Caveat: made-up title', 'bold'), ('made-up titles are more likely', 'normal'), ('to the model (log-prob +0.12);', 'normal'),
                ('closer meaning brings back more', 'normal'), ('→ part of the extra may be', 'normal'), ('closeness it missed', 'normal')], BY+BH-30)
caveat(CY+10, [('Caveat: rare vs common words', 'bold'), ('unequal counts (3.4 vs 2.1 words);', 'normal'), ('common words frequency-matched,', 'normal'),
               ('not synonyms; equal counts: the', 'normal'), ('gap remains, +0.07 (exploratory)', 'normal')], CY+60)

# ---------- legend + grey lines ----------
LY = BOT + 28
txt(24, LY, 'Colour of a conclusion:', 15, INK, weight='bold')
xx = 236
for lab, col in (('proven by one experiment', BLUE), ('joint (only with several together)', GREEN), ('cannot be decided', GREYC), ('refuted / overturned (old claim struck in grey)', RED)):
    a(f'<rect x="{xx}" y="{LY-13}" width="16" height="16" rx="3" fill="{col}"/>'); txt(xx+24, LY, lab, 14.5, col, weight='bold')
    xx += 40 + 9.2*len(lab)
a(f'<image x="24" y="{LY+16}" width="650" height="35" xlink:href="{b64("tex_stage_f.png")}"/>')
a(f'<image x="700" y="{LY+20}" width="788" height="27" xlink:href="{b64("tex_stage_n.png")}"/>')
txt(24, LY+76, 'φ ≈ 1: meaning alone is enough; R > 0: the real title adds something', 14, PALE_T)
a('</svg>')
open('stage_L24_L40_v2.svg', 'w').write('\n'.join(o))
print('ok')
