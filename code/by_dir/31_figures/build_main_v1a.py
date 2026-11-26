# Story figure, MAIN view: prompt tokens (x) x layers L0-L63 (y). Design draft v1, 2026-11-24.
# Content only from 27_v67/experiment_tree.md (full story / story map). No new numbers.
import base64, html

TOKS = ['Who', ' are', ' the', ' authors', ' of', ' the', ' paper', ' titled', ' "', 'A', 'ffect', ' dynamics', ',', ' bere', 'av',
        'ement', ' and', ' resilience', ' to', ' loss', '"', ' (', '2', '0', '0', '7', ')?↵', 'Authors', ':', ' Kar', 'in', ' G', '.',
        ' Co', 'if', 'man', ',', ' George', ' A', '.', ' Bon', 'anno', ',', ' E', 'sh', 'kol', ' Rafael', 'i']
GRP = [0]*9 + [1]*11 + [2]*9 + [3]*19          # question words / title / after the title / author names
GNAME = ['question words', 'title (11 tokens)', 'after the title', 'author names (every token scored)']
GCOL = ['#EEF1F5', '#FFF1DE', '#E8F0FA', '#FBE3E1']
N = len(TOKS)
CW, X0, Y0, LH = 26, 92, 196, 9.0
GR = X0 + CW*N                                   # right edge of the grid
PX = GR + 34                                     # right panel x
W, H = PX + 560, 1010
INK, GREY = '#22304A', '#8a8f98'
S = dict(settled='#2E7D46', locked='#3C78B4', prereg='#6B4FA0', desc='#B54708', expl='#6A7385')
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"

def X(i): return X0 + i*CW
def Y(l): return Y0 + (63 - l)*LH                # top edge of layer l's row
def band(c0, c1, l0, l1):                        # columns c0..c1 inclusive, layers l0..l1 inclusive
    return X(c0), Y(l1), (c1 - c0 + 1)*CW, (l1 - l0 + 1)*LH
def esc(s): return html.escape(s)
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

o = []; a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs>'
  '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#1F6F8B"/></marker>'
  '<marker id="ark" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#9aa3ae"/></marker>'
  '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#3C78B4" stroke-width="2.2" opacity=".35"/></pattern>'
  '</defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
a(f'<text x="24" y="46" font-family="{HAND}" font-size="36" fill="{INK}">Read early, said late: the whole story on one map</text>')
a(f'<text x="24" y="76" font-size="15" fill="{GREY}">x: the prompt as real Qwen3 tokens · y: layers L0–L63 · ①–⑥ = the six stages (right) · '
  f'▲ intervention (replace / block / inject) · ◉ readout (lens / probe)</text>')

# token header
for g in range(4):
    c0 = GRP.index(g); c1 = len(GRP) - 1 - GRP[::-1].index(g)
    a(f'<text x="{(X(c0)+X(c1)+CW)/2}" y="{Y0-80}" font-size="14" text-anchor="middle" fill="{GREY}">{GNAME[g]}</text>')
    a(f'<line x1="{X(c0)+3}" x2="{X(c1)+CW-3}" y1="{Y0-73}" y2="{Y0-73}" stroke="#c9ced6" stroke-width="1.5"/>')
for i, (t, g) in enumerate(zip(TOKS, GRP)):
    a(f'<rect x="{X(i)+1}" y="{Y0-66}" width="{CW-2}" height="58" rx="4" fill="{GCOL[g]}" stroke="#c9ced6"/>')
    cx, cy = X(i) + CW/2 + 4, Y0 - 14
    a(f'<text x="{cx}" y="{cy}" font-size="13" fill="{INK}" transform="rotate(-62 {cx} {cy})">{esc(t.replace(" ", "·"))}</text>')

# layer grid
for l in range(0, 64, 4):
    a(f'<line x1="{X0}" x2="{GR}" y1="{Y(l)+LH}" y2="{Y(l)+LH}" stroke="#e6e9ee" stroke-width="1"/>')
for l in (0, 8, 16, 24, 32, 40, 48, 56, 63):
    a(f'<text x="{X0-8}" y="{Y(l)+LH-1}" font-size="13" text-anchor="end" fill="{GREY}">L{l}</text>')
a(f'<rect x="{X0}" y="{Y(63)}" width="{GR-X0}" height="{64*LH}" fill="none" stroke="#c9ced6"/>')

def rect(c0, c1, l0, l1, fill, op=1, stroke='none', dash=None, sw=1.6, rx=3):
    x, y, w, h = band(c0, c1, l0, l1); d = f' stroke-dasharray="{dash}"' if dash else ''
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
def txt(x, y, s, size=13, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
def struck(x, y, s, size=13):                    # overturned claim: grey, struck through
    w = 0.56*size*len(s)
    txt(x, y, s, size, '#9aa3ae', italic=True)
    a(f'<line x1="{x-2}" x2="{x+w+2}" y1="{y-size*0.32}" y2="{y-size*0.32}" stroke="#9aa3ae" stroke-width="1.6"/>')
def step(n, x, y, col=INK, r=11):
    a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/><text x="{x}" y="{y+5}" font-size="14" font-weight="700" text-anchor="middle" fill="#fff">{n}</text>')

# ① L0-L4: the words decide everything
rect(0, N-1, 0, 4, '#DDE2E8', .75)
txt(X(0)+8, Y(2)+8, 'identical words → identical states: same title under two questions, cos ≈ 1.00 at L4 (the ceiling)', 13, INK)
step('①', X(0)-48, Y(2)+3, '#6A7385')
# ② L4-L24 early read-in (title) ; ":" follows the question
rect(9, 19, 4, 23, '#FFE9CC', .9)
txt(X(9)+6, Y(20)+4, 'early read-in', 13, '#8a5a12')
a(f'<polygon points="{X(19)+CW/2},{Y(8)-6} {X(19)+CW/2+5},{Y(8)+3} {X(19)+CW/2-5},{Y(8)+3}" fill="{S["locked"]}"/>')
txt(X(20)+4, Y(8)+6, 'L8: small surname signal beyond topic (+0.05)', 12.5, S['locked'])
rect(28, 28, 4, 56, 'none', 1, S['locked'], '5 3', 2)
txt(X(20)+4, Y(15)+6, '":" follows the question', 12.5, S['locked'])
txt(X(20)+4, Y(15)+21, '(4.7× more for a new question, L4)', 12, S['locked'])
step('②', X(0)-48, Y(14)+3, '#B54708')
# ③ L24-L52 title read: meaning + specific words
rect(9, 19, 24, 52, '#FFC98A', .85)
txt(X(9)+6, Y(46)+2, 'title read L24 → L52', 13.5, INK, weight='bold')
txt(X(9)+6, Y(43)+4, 'what is read: meaning', 13, INK)
txt(X(9)+6, Y(41)+5, '+ specific (rare) words', 13, INK)
txt(X(9)+6, Y(37)+3, 'same-meaning made-up', 12.5, INK)
txt(X(9)+6, Y(35)+4, 'title gets ~75%', 12.5, INK, weight='bold')
struck(X(9)+6, Y(30)+4, 'stores which paper', 12.5)
struck(X(9)+6, Y(28)+5, 'this is', 12.5)
step('③', X(0)-48, Y(32)+3, '#D9772B')
# ④ L40-L52 delivered to the names via name <- title, many layers in parallel
for l in (44, 46, 48, 50, 52, 54):
    a(f'<line x1="{X(19)+CW-2}" y1="{Y(l)+LH/2}" x2="{X(29)+4}" y2="{Y(l)+LH/2}" stroke="#1F6F8B" stroke-width="1.6" opacity=".9" marker-end="url(#ar)"/>')
txt(X(20)+4, Y(41)+3, 'name ← title, L44–L55,', 12.5, '#1F6F8B')
txt(X(20)+4, Y(41)+18, 'many layers in parallel;', 12.5, '#1F6F8B')
txt(X(20)+4, Y(41)+33, 'cut any one: ≤ 1.25% lost', 12.5, '#1F6F8B')
txt(X(9)+6, Y(55)+2, 'put back: 0.995 by L52', 12.5, S['settled'], weight='bold')
step('④', X(0)-48, Y(48)+3, '#1F6F8B')
# ⑤ L48-L56 held at the names, not as words
rect(29, N-1, 48, 56, 'url(#hatch)', 1)
rect(29, N-1, 48, 56, '#E8F0FA', .45)
txt(X(30), Y(55)+4, 'held at the names, not as words:', 13, INK, weight='bold')
txt(X(30), Y(53)+5, '◉ probe reads it, lens does not (probe − lens +0.06, L48)', 12.5, S['locked'])
txt(X(30), Y(51)+6, '▲ L52–L56 MLPs carry paper info, not name directions', 12.5, S['desc'])
txt(X(30), Y(49)+7, '▲ injected author direction: mostly a write channel', 12.5, S['locked'])
struck(X(20)+4, Y(57)+5, 'format fixed here (L56)', 12.5)
a(f'<line x1="{X(20)+4+0.56*12.5*23+8}" y1="{Y(57)+1}" x2="{X(28)}" y2="{Y(56)+LH/2}" stroke="#9aa3ae" stroke-width="1.2" marker-end="url(#ark)"/>')
step('⑤', X(0)-48, Y(52)+3, '#3C78B4')
# ⑥ L56-L63 the late MLPs write the name; stuck at the first token
rect(29, N-1, 57, 63, '#F6B8B0', .8)
rect(29, N-1, 57, 61, 'none', 1, '#C0392B', None, 1.8)
txt(X(31), Y(61)+6, '▲ L57–L61 MLPs write the name (MLP − attention ≈ +0.04)', 12.5, INK, weight='bold')
txt(X(31), Y(59)+7, '◉ recognised − not grows here → +0.21 at the output', 12.5, INK)
txt(X(31), Y(57)+8, '~1 in 8 papers: name rises after L56, then falls', 12.5, INK)
cx, cy = X(29)+CW/2, Y(63)+LH/2
a(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="#C0392B" stroke-width="2.4"/>'
  f'<path d="M{cx-6} {cy-6}L{cx+6} {cy+6}M{cx+6} {cy-6}L{cx-6} {cy+6}" stroke="#C0392B" stroke-width="2.6"/>')
txt(X(20)+4, Y(62)+2, 'stuck here: the first name token', 13, '#C0392B', weight='bold')
txt(X(20)+4, Y(62)+17, '(given the initial: 4% → 15%)', 12, '#C0392B')
a(f'<line x1="{X(20)+4+238}" y1="{Y(62)-2}" x2="{cx-12}" y2="{cy}" stroke="#C0392B" stroke-width="1.4"/>')
step('⑥', X(0)-48, Y(60)+3, '#C0392B')
# gap ①: where "who wrote it" enters
gx, gy, gw, gh = band(29, N-1, 52, 61)
a(f'<rect x="{gx-4}" y="{gy-4}" width="{gw+8}" height="{gh+8}" rx="6" fill="none" stroke="#6A7385" stroke-width="2" stroke-dasharray="7 5"/>')
a(f'<rect x="{X(36)}" y="{Y(63)-32}" width="{12*CW-4}" height="24" rx="5" fill="#fff" stroke="#6A7385" stroke-width="1.6" stroke-dasharray="7 5"/>')
txt(X(36)+8, Y(63)-15, 'Gap ①: at which step does "who wrote this paper" enter?', 12.5, '#4a5160', weight='bold')

# right panel: the six stages
PANEL = [
    ('⑥', '#C0392B', 'L56–L63 · the late MLPs write the name',
     ['MLP − attention ≈ +0.04 at each of L57–L61', 'gap grows to +0.21 at the output', 'pushing the arrived signal harder: 2.5% → 2.8%'],
     [('settled ▲', 'settled'), ('locked ▲', 'locked')]),
    ('⑤', '#3C78B4', 'L48–L56 · held at the names, not as words',
     ['probe reads +0.06 more than the lens (L48)', 'author direction: 2.5% → 9.7%, mostly write channel', 'MLPs carry paper info, not name directions'],
     [('locked ◉', 'locked'), ('locked ▲', 'locked'), ('descriptive ▲', 'desc')]),
    ('④', '#1F6F8B', 'L40–L52 · delivered over many layers',
     ['name ← title edge, L44–L55', 'cut any single layer: ≤ 1.25% lost', 'put back restores ~100% by L52'],
     [('locked ▲', 'locked'), ('settled ▲', 'settled')]),
    ('③', '#D9772B', 'L24–L40 · meaning + specific words',
     ['made-up title with the same meaning: ~75%', 'the rest sits on rare words, not on recognition', 'identity adds ≈ 0 beyond the text'],
     [('locked ▲', 'locked'), ('locked ◉', 'locked')]),
    ('②', '#B54708', 'L4–L24 · early read-in',
     ['":" follows the question (4.7×, L4)', 'L8 surname signal beyond topic, +0.05', '(two of three tests marginal; ~half topic)'],
     [('descriptive ◉', 'desc'), ('locked ◉', 'locked')]),
    ('①', '#6A7385', 'L0–L4 · the words decide (ceiling)',
     ['same title, same state: cos ≈ 1.00 at L4', 'question-only tests cannot separate', 'meaning from identity'],
     [('exploratory ◉', 'expl')]),
]
slots = [Y(63)+6, Y(54)+14, Y(45)+16, Y(34)+10, Y(20)+18, Y(7)+4]
for (n, col, title, lines, badges), y in zip(PANEL, slots):
    step(n, PX+12, y, col, 12)
    txt(PX+32, y+5, title, 14.5, INK, weight='bold')
    for k, s in enumerate(lines):
        txt(PX+32, y+26+k*18, s, 13, '#3d4656')
    bx = PX + 32
    for lab, key in badges:
        w = 12 + 7.6*len(lab)
        a(f'<rect x="{bx}" y="{y+26+len(lines)*18-12}" width="{w}" height="20" rx="10" fill="#fff" stroke="{S[key]}" stroke-width="1.6"/>')
        txt(bx+w/2, y+26+len(lines)*18+3, lab, 12, S[key], 'middle')
        bx += w + 8
# leader lines from grid to panel
for (n, *_), y, l in zip(PANEL, slots, (60, 52, 47, 32, 14, 2)):
    a(f'<line x1="{GR+2}" y1="{Y(l)+LH/2}" x2="{PX-2}" y2="{y}" stroke="#c9ced6" stroke-width="1.2"/>')

# bottom: gap ②, legend, three grey lines
by = Y(0) + LH + 26
a(f'<rect x="{X0}" y="{by-18}" width="760" height="28" rx="6" fill="#fff" stroke="#6A7385" stroke-width="1.6" stroke-dasharray="7 5"/>')
txt(X0+10, by+1, 'Gap ②: "recognised" comes from the multiple-choice prompt, which was never measured inside', 12.5, '#4a5160', weight='bold')
lx = X0 + 780
leg = [('settled', 'settled'), ('locked', 'locked'), ('pre-registered', 'prereg'), ('descriptive', 'desc'), ('exploratory', 'expl')]
for lab, key in leg:
    w = 12 + 7.6*len(lab)
    a(f'<rect x="{lx}" y="{by-13}" width="{w}" height="20" rx="10" fill="#fff" stroke="{S[key]}" stroke-width="1.6"/>')
    txt(lx+w/2, by+2, lab, 12, S[key], 'middle'); lx += w + 8
struck(lx+8, by+2, 'overturned claim', 12.5)
a(f'<image x="{X0}" y="{by+22}" width="497" height="50" xlink:href="{b64("tex_main_f.png")}"/>')
a(f'<image x="{X0}" y="{by+72}" width="906" height="28" xlink:href="{b64("tex_main_n.png")}"/>')
txt(X0, by+120, 'spec > 0: the true title helps the true author; R ≈ 1: the copied state restores all of the true-title advantage', 14, GREY)
a('</svg>')
open('main_v1.svg', 'w').write('\n'.join(o))
print('ok', W, H)
