# Stage expansion figure, L24-L40 ("reasoning chain"). Design draft v1, 2026-11-24.
# Content only from 27_v67/experiment_tree.md (tree 3 H2, story map, full story). No new numbers.
import base64, html
W, H = 1900, 1330
INK, GREY = '#22304A', '#8a8f98'
S = dict(settled='#2E7D46', locked='#3C78B4', prereg='#6B4FA0', desc='#B54708', expl='#6A7385')
REL = dict(joint='#2E7D46', cross='#1F6F8B', rescue='#B54708', lead='#6A7385', excl='#C0392B', dep='#6B4FA0')
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
o = []; a = o.append
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def txt(x, y, s, size=14, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def strike(x, y, s, size=14, col='#9aa3ae'):
    w = 0.6*size*len(s); txt(x, y, s, size, col, italic=True)
    a(f'<line x1="{x-2}" x2="{x+w}" y1="{y-size*0.33}" y2="{y-size*0.33}" stroke="{col}" stroke-width="1.8"/>')
def badge(x, y, lab, key):
    w = 12 + 7.8*len(lab)
    a(f'<rect x="{x}" y="{y-14}" width="{w}" height="21" rx="10.5" fill="#fff" stroke="{S[key]}" stroke-width="1.7"/>')
    txt(x+w/2, y+2, lab, 12.5, S[key], 'middle'); return w
def box(x, y, w, title, lines, tags, fill='#fff', stroke='#c9ced6', h=None, dash=None):
    h = h or (40 + 20*len(lines) + 30)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.8"{d}/>')
    txt(x+14, y+26, title, 15, INK, weight='bold')
    for k, s in enumerate(lines):
        txt(x+14, y+50+20*k, s, 13.5, '#3d4656')
    bx = x + 14
    for lab, key in tags:
        bx += badge(bx, y+h-14, lab, key) + 8
    return (x, y, w, h)
def arrow(x1, y1, x2, y2, col, dash=None, sw=2.2, curve=None, marker='a'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    if curve:
        cx, cy = curve; path = f'M{x1} {y1} Q {cx} {cy} {x2} {y2}'
    else:
        path = f'M{x1} {y1} L{x2} {y2}'
    a(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{sw}"{d} marker-end="url(#{marker}{col[1:]})"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs>' + ''.join(f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>'
                      for c in set(REL.values()) | {INK, GREY}) + '</defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
txt(260, 50, 'Stage ③ · L24–L40: what is read is meaning and specific words, not paper identity', 32, INK, fam=HAND)
txt(260, 80, 'How the conclusion was reached: experiments top to bottom in the order they were run; line styles = how they relate (legend at the bottom)', 15, GREY)

# locator (mini main figure)
lx, ly = 24, 18
a(f'<rect x="{lx}" y="{ly}" width="210" height="150" rx="8" fill="#fff" stroke="#c9ced6"/>')
gx0, gy0, gw, gh = lx+14, ly+30, 182, 100
a(f'<rect x="{gx0}" y="{gy0}" width="{gw}" height="{gh}" fill="#F4F5F7" stroke="#d5d9df"/>')
cw = gw/48; lh = gh/64
def mx(c): return gx0 + c*cw
def my(l): return gy0 + (63-l)*lh
for c0, c1, col in ((0, 8, '#EEF1F5'), (9, 19, '#FFF1DE'), (20, 28, '#E8F0FA'), (29, 47, '#FBE3E1')):
    a(f'<rect x="{mx(c0)}" y="{gy0}" width="{(c1-c0+1)*cw}" height="{gh}" fill="{col}" opacity=".8"/>')
a(f'<rect x="{mx(9)}" y="{my(40)}" width="{11*cw}" height="{17*lh}" fill="#FFC98A" stroke="#D9772B" stroke-width="2"/>')
txt(lx+12, ly+20, 'where on the main map', 12.5, GREY)
txt(mx(9)+2, my(40)-4, 'L24–L40 · title', 11.5, '#D9772B', weight='bold')

# --- column positions
LX, CX, RX = 30, 520, 1500          # left column, centre chain, right column
# Row 1: lead-in (which title words carry it)
b1 = box(CX, 110, 560, '① Which title words carry the signal?  ▲',
         ['swap one word class for random tokens vs WordNet synonyms', 'content words: random −0.37 vs synonym −0.09 of 0.33',
          '→ content words carry it by meaning'], [('descriptive', 'desc')], h=150)
# Row 2: made-up title
b2 = box(CX, 330, 560, '② Made-up title with the same meaning  ▲',
         ['score the true authors under true / made-up / 5 false titles', 'made-up title brings back 0.75 [0.72, 0.78] of the gap',
          'the real title adds +0.11 on top'], [('locked', 'locked')], h=150)
arrow(CX+280, 260, CX+280, 328, REL['lead'], '6 5')
txt(CX+292, 300, 'lead-in: is it the meaning or this exact paper?', 13.5, REL['lead'], italic=True)
# cross-stage dependency from Route
arrow(CX-100, 352, CX-2, 405, REL['dep'], None, 2.4, curve=(CX-60, 352))
txt(CX-172, 284, 'from stage ④:', 13.5, REL['dep'], weight='bold')
txt(CX-172, 302, 'title read and', 13.5, REL['dep'], weight='bold')
txt(CX-172, 320, 'delivered by L52', 13.5, REL['dep'], weight='bold')
txt(CX-172, 338, '(put back 0.995)', 13, REL['dep'])
# Row 3: question node
qx, qy = CX+280, 560
a(f'<ellipse cx="{qx}" cy="{qy}" rx="270" ry="44" fill="#FFF6E5" stroke="#D9772B" stroke-width="2.2"/>')
txt(qx, qy-4, '~75% is meaning — what is the small part left?', 16, INK, 'middle', 'bold')
txt(qx, qy+20, 'four tests, run in parallel', 13.5, GREY, 'middle', italic=True)
arrow(CX+280, 480, qx, qy-46, INK)
# Row 4: four branches
BY = 660; BW = 360; BX = [350, 730, 1110, 1490]
branches = [
    ('③a Rare vs common words  ▲', ['swap only rare / only common title words', 'rare: −0.16 · common: −0.03', '→ the extra sits on specific words'], [('locked', 'locked')]),
    ('③b Recognised / citation check  ▲', ['is the extra larger for recognised or', 'much-cited papers?  → not larger;', 'smaller for much-cited ones'], [('locked', 'locked')]),
    ('③c Variance split  ◉', ['what explains the title state?', 'meaning adds 0.17–0.27 · identity ≈ 0', '→ no room for identity'], [('locked', 'locked')]),
    ('③d Paper-facts subspace swap  ▲', ['swap only the subspace that predicts', 'paper facts: 0.004 vs whole state 0.93', '→ no author information there'], [('pre-registered', 'prereg')]),
]
bb = []
for x, (t, l, tg) in zip(BX, branches):
    bb.append(box(x, BY, BW, t, l, tg, h=150))
    arrow(qx, qy+44, x+BW/2, BY-2, INK, sw=1.8)
# Row 5: joint conclusion
JY = 900
a(f'<rect x="{CX-40}" y="{JY}" width="640" height="78" rx="12" fill="#EAF6EC" stroke="{REL["joint"]}" stroke-width="2.4"/>')
txt(CX+280, JY+32, 'JOINT: the real title\'s small extra comes from', 15.5, INK, 'middle', 'bold')
txt(CX+280, JY+56, 'specific words, not from recognising the paper', 15.5, INK, 'middle', 'bold')
for x in BX:
    a(f'<path d="M{x+BW/2} {BY+150} Q {x+BW/2} {JY-30} {CX+280} {JY-2}" fill="none" stroke="{REL["joint"]}" stroke-width="2.6" marker-end="url(#a{REL["joint"][1:]})"/>')
txt(CX+620, JY+36, 'joint: each covers one part;', 13, REL['joint'], italic=True)
txt(CX+620, JY+54, 'drop one and the conclusion is open', 13, REL['joint'], italic=True)
# Row 6: overturned + now
OY = 1010
a(f'<rect x="{CX-150}" y="{OY-10}" width="860" height="76" rx="10" fill="#F1F2F4" stroke="#9aa3ae" stroke-width="1.6"/>')
strike(CX-130, OY+18, 'overturned: middle layers store "which paper this is" (partly supported)', 14.5)
txt(CX-130, OY+48, '→ now: not a general paper identity, with one small locked exception', 15, INK, weight='bold')
arrow(CX+280, JY+78, CX+280, OY-12, INK)
# Row 7: final conclusion (full-story wording)
FY = 1100
a(f'<rect x="{CX-150}" y="{FY}" width="860" height="70" rx="12" fill="#FFF1DE" stroke="#D9772B" stroke-width="2.6"/>')
txt(CX+280, FY+30, 'The main title-reading phase: what is read is meaning and', 16.5, INK, 'middle', 'bold')
txt(CX+280, FY+54, 'specific words, not paper identity', 16.5, INK, 'middle', 'bold')
arrow(CX+280, OY+66, CX+280, FY-2, INK)

# left column: early tests + rescue + paraphrase
e1 = box(LX, 430, 300, '0 Early tests (same title,', ['other question; copy state;', 'find the paper again)', '', ''], [('exploratory', 'expl')], h=172)
strike(LX+14, 430+100, '"supports identity"', 14)
txt(LX+14, 430+122, '→ cannot separate', 14, INK, weight='bold')
a1 = box(LX, 1010, 300, 'Ceiling audit  ◉', ['same title, 2 questions:', 'cos ≈ 1.00 already at L4'], [('exploratory', 'expl')], h=120)
arrow(LX+150, 1008, LX+150, 606, REL['rescue'], None, 2.8, curve=(LX+60, 800))
txt(LX+120, 760, 'rescue: the', 13.5, REL['rescue'], weight='bold')
txt(LX+120, 778, 'audit rewrote', 13.5, REL['rescue'])
txt(LX+120, 796, 'the early', 13.5, REL['rescue'])
txt(LX+120, 814, 'conclusion', 13.5, REL['rescue'])
p1 = box(LX, 190, 300, 'Paraphrased title  ▲', ['meaning beyond the words:', 'gap peaks at L36, +0.16'], [('pre-registered', 'prereg')], h=120)
arrow(LX+300, 230, CX-2, 200, REL['joint'], None, 1.8)
txt(LX+312, 208, 'supports "meaning"', 12.5, REL['joint'], italic=True)

# right column: small exception + exclusions
x1 = box(RX, 300, 380, 'Small locked exception  ◉', ['L8 surname signal beyond topic +0.05', 'two of three tests marginal;', 'about half of the raw signal is topic'], [('locked', 'locked')], fill='#EEF4FB', stroke=S['locked'], h=150)
arrow(RX-2, 375, CX+562, 400, S['locked'], '4 3', 1.8)
txt(CX+860, 368, 'kept as a small exception', 13, S['locked'], 'middle', italic=True)
for k, (alt, why) in enumerate((('surname simply in the title', 'source check'), ('common surnames of the field', 'topic-matched test'))):
    y = 110 + k*82
    a(f'<rect x="{RX+120}" y="{y}" width="260" height="58" rx="8" fill="#fff" stroke="{REL["excl"]}" stroke-width="1.6" stroke-dasharray="3 3"/>')
    txt(RX+132, y+24, alt, 13.5, '#7a3a33')
    txt(RX+132, y+44, f'ruled out by the {why}', 12.5, GREY)
    a(f'<path d="M{RX+360} {y+10} L{RX+376} {y+48} M{RX+376} {y+10} L{RX+360} {y+48}" stroke="{REL["excl"]}" stroke-width="2.4"/>')
    arrow(RX+40, 300, RX+118, y+29, REL['excl'], None, 1.8, curve=(RX+40, y+29))

# legend
LY = 1210
txt(30, LY, 'Relations:', 14, INK, weight='bold')
items = [('joint (lines merge into one conclusion)', 'joint', None), ('cross-check ↔ opposite directions, same conclusion (not in this stage)', 'cross', None),
         ('rescue (curved back to the test it rewrote)', 'rescue', None), ('lead-in (dashed: the question it raised)', 'lead', '6 5'),
         ('exclusion (into a crossed-out alternative)', 'excl', None), ('cross-stage dependency (from another stage)', 'dep', None)]
x = 130
for k, (lab, key, dash) in enumerate(items):
    yy = LY - 5 + (k // 3)*24; xx = 130 + (k % 3)*590
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<line x1="{xx}" y1="{yy}" x2="{xx+40}" y2="{yy}" stroke="{REL[key]}" stroke-width="2.6"{d} marker-end="url(#a{REL[key][1:]})"/>')
    txt(xx+50, yy+5, lab, 13, '#3d4656')
txt(30, LY+56, '▲ intervention (replace / swap / patch)   ◉ readout (probe / regression / cosine)   grey struck text = overturned claim', 13, GREY)
a(f'<image x="30" y="{LY+66}" width="650" height="35" xlink:href="{b64("tex_stage_f.png")}"/>')
a(f'<image x="700" y="{LY+70}" width="788" height="27" xlink:href="{b64("tex_stage_n.png")}"/>')
txt(1500, LY+90, 'φ ≈ 1: meaning alone is enough', 13.5, GREY)
a('</svg>')
open('stage_L24_L40_v1.svg', 'w').write('\n'.join(o))
print('ok')
