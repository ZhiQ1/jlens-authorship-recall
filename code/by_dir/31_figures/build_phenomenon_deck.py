# Deck continuation of step 0 (1920x1080, text >= 16 px): the phenomenon "recognised but not said" — exposure gap
# (Phenomenon ⑩⑪, s. 24) and name-prior control (Phenomenon ③④⑧, s. 68 / 94-2 / 26). Numbers only from
# 27_v67/experiment_tree.md; curves are sketches (shape only). 2026-11-25.
import base64, html, math, subprocess, sys
sys.path.insert(0, '.')
from mk_latex import render
from PIL import Image
W, H = 1920, 1080
INK, DET, GREY = '#22304A', '#5A6372', '#8a8f98'
BLUE, GREEN, GREYC, RED = '#1F3A6B', '#2E7D46', '#6A7385', '#C0392B'
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
o = []; a = o.append
def esc(s): return html.escape(s)
def txt(x, y, s, size=16, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{max(size, 16)}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def img(p, x, y, s=0.42):
    w, h = Image.open(p).size
    a(f'<image x="{x}" y="{y}" width="{w*s}" height="{h*s}" xlink:href="data:image/png;base64,{base64.b64encode(open(p, "rb").read()).decode()}"/>')
    return h*s
render(r"$\rho=c_{50}(\mathrm{write})\,/\,c_{50}(\mathrm{recognise})$", 'tex_phen_f1.png')
render(r"$n=9{,}108\ \mathrm{papers}$", 'tex_phen_n1.png')
render(r"$\mathrm{share}=(T-C)_{\mathrm{no\ title}}\,/\,(T-C)_{\mathrm{true\ title}}$", 'tex_phen_f2.png')
render(r"$n=\mathrm{full\ cohort,\ target\ vs\ control\ within\ citation\ bins;\ R0=\mathrm{papers\ with\ no\ author\ written}}$", 'tex_phen_n2.png')

a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#22304A"/></marker></defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
txt(24, 40, 'Before the map: recognised but not said', 32, INK, fam=HAND)
txt(24, 66, 'Now asking: how large is the gap between recognising and writing, and is it more than guessable names?', 16, DET)
txt(W-24, 40, 'Step 0 · continued', 22, INK, 'end', fam=HAND)

# ---------- A: exposure gap ----------
a(f'<rect x="24" y="92" width="920" height="790" rx="14" fill="#fff" stroke="#D5D9DF" stroke-width="1.4"/>')
txt(44, 126, '① Exposure: writing needs far more citations than recognising', 19, GREEN, weight='bold')
X0, X1, YB, YT = 120, 900, 600, 220
def XL(v): return X0 + (X1 - X0) * v / 5.0
def YV(p): return YB - (YB - YT) * p
a(f'<line x1="{X0}" y1="{YB}" x2="{X1}" y2="{YB}" stroke="{INK}" stroke-width="1.6"/><line x1="{X0}" y1="{YB}" x2="{X0}" y2="{YT-20}" stroke="{INK}" stroke-width="1.6"/>')
for v, lab in ((0, '1'), (1, '10'), (2, '100'), (3, '1,000'), (4, '10,000'), (5, '100,000')):
    a(f'<line x1="{XL(v)}" y1="{YB}" x2="{XL(v)}" y2="{YB+8}" stroke="{INK}" stroke-width="1.4"/>'); txt(XL(v), YB+30, lab, 16, DET, 'middle')
txt((X0+X1)/2, YB+58, 'citations of the paper (log scale)', 16, DET, 'middle')
txt(X0-12, YV(1)+6, '1', 16, DET, 'end'); txt(X0-12, YV(0.5)+6, '½', 16, DET, 'end'); txt(X0-12, YB+6, '0', 16, DET, 'end')
a(f'<text x="64" y="{(YB+YT)/2}" font-size="16" fill="{DET}" text-anchor="middle" transform="rotate(-90 64 {(YB+YT)/2})" font-family="{SANS}">share of papers (sketch)</text>')
a(f'<line x1="{X0}" y1="{YV(0.5)}" x2="{X1}" y2="{YV(0.5)}" stroke="#C9CED6" stroke-width="1.2" stroke-dasharray="5 4"/>')
lr, lw = math.log10(40), math.log10(11038)
a(f'<rect x="{XL(lr)}" y="{YT-10}" width="{XL(lw)-XL(lr)}" height="{YB-YT+10}" fill="{GREEN}" fill-opacity=".08"/>')
txt((XL(lr)+XL(lw))/2, YV(0.74), 'recognised but not said', 17, GREEN, 'middle', 'bold')
def curve(c, col, dash):
    pts = ' '.join(f'{XL(v/20):.1f},{YV(1/(1+math.exp(-3.2*(v/20-c)))):.1f}' for v in range(0, 101))
    d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="4"{d}/>')
curve(lr, BLUE, None); curve(lw, BLUE, '10 6')
for lv, lab, anc, dx in ((lr, '~40', 'end', -16), (lw, '~11,000', 'start', 16)):
    a(f'<circle cx="{XL(lv)}" cy="{YV(0.5)}" r="11" fill="#fff" stroke="{INK}" stroke-width="3"/><circle cx="{XL(lv)}" cy="{YV(0.5)}" r="5" fill="{INK}"/>')
    txt(XL(lv)+dx, YV(0.5)+36, lab, 20, INK, anc, 'bold')
txt(XL(lr)-16, YV(0.86), 'recognising', 18, BLUE, 'end', 'bold'); txt(XL(lr)-16, YV(0.86)+21, '(multiple choice)', 16, BLUE, 'end')
txt(XL(lw)+18, YV(0.22), 'writing at least', 18, BLUE, weight='bold'); txt(XL(lw)+18, YV(0.22)+21, 'one true author', 16, BLUE)
a(f'<line x1="{XL(lr)+16}" y1="{YV(0.5)-26}" x2="{XL(lw)-16}" y2="{YV(0.5)-26}" stroke="{INK}" stroke-width="2.4" marker-start="url(#ah)" marker-end="url(#ah)"/>')
txt((XL(lr)+XL(lw))/2, YV(0.5)-36, 'ρ ~276× more exposure', 19, INK, 'middle', 'bold')
y = YB + 92
txt(44, y, 'Result: half-way points (c50) ~40 vs ~11,000 citations.', 16, INK); y += 22
txt(44, y, 'Caveat: rule locked after seeing the estimates → only ρ > 1 is confirmed.', 16, GREYC); y += 22
txt(44, y, 'c50 40 [36, 44] vs 11,038 [8,172, 15,607]; ρ 276 [203, 390]; ~25% guessing floor', 16, GREY); y += 16
y += img('tex_phen_f1.png', 44, y) + 4
y += img('tex_phen_n1.png', 44, y) + 20
txt(44, y, 'ρ > 1: writing needs more exposure than recognising', 16, GREY)

# ---------- B: name-prior control ----------
BX = 976
a(f'<rect x="{BX}" y="92" width="920" height="790" rx="14" fill="#fff" stroke="#D5D9DF" stroke-width="1.4"/>')
txt(BX+20, 126, '② Not just guessable names', 19, BLUE, weight='bold')
SC = 2600; bx0 = BX + 60
txt(bx0, 186, 'recognised − not recognised, true title (+0.25)', 17, INK, weight='bold')
w1, w2 = 0.047*SC, 0.247*SC
a(f'<rect x="{bx0}" y="202" width="{w2}" height="56" rx="6" fill="{GREEN}" fill-opacity=".18" stroke="{GREEN}" stroke-width="2"/>')
a(f'<rect x="{bx0}" y="202" width="{w1}" height="56" rx="6" fill="#DADDE2" stroke="{GREYC}" stroke-width="2"/>')
a(f'<circle cx="{bx0+w1}" cy="230" r="9" fill="{GREYC}"/>')
txt(bx0+w1/2, 290, 'name prior', 16, GREYC, 'middle', 'bold'); txt(bx0+w1/2, 310, '~19%', 18, GREYC, 'middle', 'bold')
txt(bx0+w1+(w2-w1)/2, 238, 'paper-specific part remains', 18, GREEN, 'middle', 'bold')
txt(bx0+w1+(w2-w1)/2, 290, '(no-title score removed)', 16, GREEN, 'middle')
txt(bx0, 372, 'same comparison: all papers vs papers with no author written', 17, INK, weight='bold')
for k, (lab, v, col) in enumerate((('pooled', 0.207, GREEN), ('R0 only', 0.199, BLUE))):
    yy = 392 + k*74
    a(f'<rect x="{bx0+110}" y="{yy}" width="{v*SC}" height="50" rx="6" fill="{col}" fill-opacity=".18" stroke="{col}" stroke-width="2"/>')
    txt(bx0+96, yy+32, lab, 17, col, 'end', 'bold')
    a(f'<circle cx="{bx0+110+v*SC}" cy="{yy+25}" r="11" fill="#fff" stroke="{col}" stroke-width="3"/><circle cx="{bx0+110+v*SC}" cy="{yy+25}" r="5" fill="{col}"/>')
    txt(bx0+110+v*SC+20, yy+32, f'+{v:.2f}'.replace('0.21', '0.21').replace('+0.20', '+0.20'), 20, col, weight='bold')
txt(bx0+110, 560, 'same late shape: the partly written papers do not drive it', 16, BLUE)
y = YB + 92
txt(BX+20, y, 'Result: the name prior is ~19% of the gap; R0 alone gives the same picture.', 16, INK); y += 22
txt(BX+20, y, 'Control: no title → how guessable the names are (true list looks most real 0.26, chance 0.25).', 16, DET); y += 22
txt(BX+20, y, 'name prior +0.047 [0.031, 0.062] vs +0.247; R0 +0.199 vs pooled +0.207', 16, GREY); y += 16
y += img('tex_phen_f2.png', BX+20, y) + 4
y += img('tex_phen_n2.png', BX+20, y) + 20
txt(BX+20, y, 'share ≪ 1: most of the gap is not guessable names', 16, GREY)

a(f'<rect x="24" y="{H-42}" width="{W-48}" height="36" rx="8" fill="#15803D"/>')
txt(40, H-17, 'So: recognised but not said is real, a large exposure gap, and not explained by guessable names', 19, '#fff', weight='bold')
txt(W-40, H-17, 'joint', 17, '#fff', 'end', italic=True)
a('</svg>')
open('deck16x9/step0b_phenomenon.svg', 'w').write('\n'.join(o))
subprocess.run(['rsvg-convert', '-z', '2', '-b', '#FBFAF5', 'deck16x9/step0b_phenomenon.svg', '-o', 'deck16x9/step0b_phenomenon.png'], check=True)
print('ok')
