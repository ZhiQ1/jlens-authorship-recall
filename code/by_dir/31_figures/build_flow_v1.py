# Story-map relation flowchart (design draft v1, 2026-11-25): the seven steps of the story map as a flow,
# upstream dependencies as arrows, each step's experiments hanging below it; colour = relation type
# (blue one experiment, green joint, grey cannot decide, red refuted / rewritten / ruled out); position:
# rescue / rule-out left, exceptions / caveats / dependencies right; the two known gaps as broken links.
# Content from 27_v67/experiment_tree.md "Story map"; no new numbers.
import html
INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
C = dict(b='#1F3A6B', g='#2E7D46', x='#6A7385', r='#C0392B')
FILL = dict(b='#EEF2F8', g='#EAF6EC', x='#F3F4F6', r='#FDF3F1')
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
W = 2000
LC = (30, 500); CC = (560, 1300); LANE = 1328; RC = (1440, 1940)
CHW = 0.58
def esc(s): return html.escape(s)
def wrap(s, width, size):
    n = max(8, int(width/(CHW*size))); out, cur = [], ''
    for w in s.split(' '):
        if len(cur)+len(w)+(1 if cur else 0) > n and cur: out.append(cur); cur = w
        else: cur = (cur+' '+w) if cur else w
    if cur: out.append(cur)
    return out

STEPS = [
 dict(n='①', t='Phenomenon: recognised but not said', tint='#EEF1F5',
      c=[('g', 'multiple-choice recognition test: defines the groups (A: 4,110)'), ('g', 'name prior: ~19% of the gap'),
         ('g', 'group comparison: +0.207 at the output'), ('g', 'R0-only recount: +0.20, same shape'), ('g', 'exposure: recognise ~40 vs write ~11,000 citations (ρ ~276)')],
      cj='joint: the gap is real, late, and an exposure gap',
      L=[('r', 'Rescue: small samples (pilot 50 → 200 papers; true title +9 / +5 pp) rested on a few pairs → full cohort + pre-registration'),
         ('r', 'Ruled out: recognised papers read earlier'), ('r', 'Ruled out: statistical artefacts')],
      R=[('x', '"recognised" is 25.5% in the lowest citation bin'), ('x', 'ρ rule locked after the data: only ρ > 1 confirmed'),
         ('gap2', 'Gap ②: "recognised" is defined only on the multiple-choice prompt, never measured inside it')]),
 dict(n='②', t='Read early: when the title and the question are read', tint='#FFF6E8',
      c=[('g', 'put back ⇄ take away (opposite directions, both: read by L52)'), ('g', '":" distance ratio'), ('g', 'probe transfer at ":"')],
      cj='joint / cross-check: read by L52; ":" follows the question',
      L=[('r', 'Ruled out: a lucky false title (all five agree)'), ('r', 'Rescue: format supplement — "fixed only at L56" was a sink-cutting artefact')],
      R=[('x', 'format layer not pinned down; year / field cannot be tested')]),
 dict(n='③', t='Delivered: meaning and specific words, not paper identity', tint='#FFE2BF',
      c=[('b', 'lead-in: which title words carry the signal'), ('g', 'made-up title: brings back 0.751'), ('g', 'where the extra appears'),
         ('g', 'rare vs common words'), ('g', 'recognised / citation check'), ('g', 'variance split'), ('g', 'attribute-subspace swap')],
      cj='joint (none can be dropped): meaning + specific words, not identity',
      L=[('r', 'Rescue: ceiling audit withdrew "change-the-question supports identity"'), ('r', 'Ruled out: literal overlap (source check)'),
         ('r', 'Ruled out: topic prior (topic-matched + confirmatory)')],
      R=[('b', 'Exception: L8 surname signal, small locked (T1 robust, T2 and T3 marginal)'), ('gap1', 'Gap ①: then where does "who wrote this paper" enter?')]),
 dict(n='④', t='Where it goes and by which route', tint='#FBF3CF',
      c=[('g', 'position and component patching'), ('g', 'windowed attention-edge blocking'), ('g', 'single-layer sweep: any one ≤ 1.25%'), ('g', 'layer order')],
      cj='joint: name ← title, several layers in parallel',
      L=[('r', 'Overturned: "one route, one layer"')],
      R=[('x', 'a single-layer cut is only a lower bound; 600-paper sub-sample')]),
 dict(n='⑤', t='In what form it is held', tint='#E8F0FA',
      c=[('x', 'lead-in: early lens comparisons inconclusive'), ('g', 'author-prompt lens cannot read it'), ('g', 'probe can (title, names)'),
         ('g', 'author subspace ~7%'), ('g', 'spread over many directions'), ('g', 'no earlier shelf'), ('b', 'L52–L56 MLPs: paper information, not names')],
      cj='joint: linearly readable, spread out; small effect, correlational',
      L=[('r', 'Rescue: same-scale test — probe beats lens by +0.062 at L48')],
      R=[('x', 'injecting the author direction: mainly a write channel'), ('x', 'at L48 lens negative, probe positive: unexplained')]),
 dict(n='⑥', t='Who writes the name', tint='#FBE3E1',
      c=[('b', 'L57–L61 mean ablation: MLP − attention +0.040'), ('g', 'first token vs the rest'), ('g', 'given name helps the surname'),
         ('g', 'which tokens carry the signal'), ('g', 'co-authors help')],
      cj='the late MLPs write it; signal on surnames and full given names',
      L=[('r', 'Ruled out: fabricated names are mixed-up neighbours')],
      R=[('gap1', 'Gap ①: no direct test; MLP patching and mean ablation are indirect only')]),
 dict(n='⑦', t='Where it gets stuck', tint='#F6C9C3',
      c=[('g', 'giving the first initial: 4.0% → 15.2%'), ('g', 'name chain: via the co-author network'), ('g', 'strengthening: 2.5% → 2.8%'),
         ('g', 'why pushing hurts: direction'), ('g', 'late suppression: ~1 in 8')],
      cj='joint: the bottleneck is the late writing step, not signal strength',
      L=[('r', 'Ruled out: the reversal curse'), ('r', 'Overturned: "the signal is too weak"')],
      R=[('x', 'late suppression just past the bound'), ('gap1', 'Gap ①: do the late MLPs hold this paper’s author knowledge? no experiment yet')]),
]
DEPS = [(0, 1, 'groups + scoring'), (1, 2, 'reaches the names by L52'), (1, 3, 'read by L52'), (3, 4, 'delivered to the names'),
        (3, 5, 'delivered'), (4, 5, 'not ready-made names'), (5, 6, 'MLPs write it'), (3, 6, 'delivered before L52')]
AUDIT_T = 'Robustness across all steps: audits and replications'
AUDIT = [('g', 'four pre-registered replication batches (false titles, all-token probes, position and component patching, completed groups): no conclusion changed'),
         ('b', 'name prior by layer: changes no conclusion'), ('b', 'paper vs team intervals: width ratio ~1; "excludes 0" changes in 2 of 1,155 rows')]

o = []; a = o.append
def txt(x, y, s, size=14, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
    st = ' font-style="italic"' if italic else ''
    a(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')

# ---- layout ----
def chip_rows(items, width):
    rows, cur, cw = [], [], 0
    for k, s in items:
        w = (0.66 if k == 'b' else 0.6)*14*len(s) + 28
        if cur and cw + w + 10 > width: rows.append(cur); cur, cw = [], 0
        cur.append((k, s, w)); cw += w + 10
    if cur: rows.append(cur)
    return rows
def side_h(items, width):
    return sum(14 + 19*len(wrap(s, width-28 - (40 if k.startswith('gap') else 0), 14)) + 10 for k, s in items)

y = 170; geo = []
for st in STEPS:
    cr = chip_rows(st['c'], CC[1]-CC[0]-24)
    ch = 64 + 16 + len(cr)*42 + 36
    h = max(ch, side_h(st['L'], LC[1]-LC[0]) , side_h(st['R'], RC[1]-RC[0]))
    geo.append((y, h, cr)); y += h + 70
AUD_Y = y; H = int(y + 90 + 150)

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
a('<defs>' + ''.join(f'<marker id="m{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for k, c in list(C.items()) + [('i', INK)]) + '</defs>')
a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
txt(30, 52, 'Story map: how the seven steps depend on each other', 36, INK, fam=HAND)
txt(30, 84, 'Steps run top to bottom; thick arrows = upstream dependency (label = what is handed down). Under each step hang its experiments; rescues and rule-outs on the left, exceptions, caveats and gaps on the right.', 15, DET)
for xx, lab in ((LC, 'Rescued, rewritten & ruled out'), (CC, 'Step and its experiments'), (RC, 'Exceptions, caveats & known gaps')):
    txt((xx[0]+xx[1])/2, 140, lab, 15, PALE_T if xx != CC else INK, 'middle', 'bold')
for xx in (LC[1]+30, RC[0]-30):
    a(f'<line x1="{xx}" y1="{120}" x2="{xx}" y2="{H-80}" stroke="#D5D9DF" stroke-width="1.4"/>')

def broken(x1, y1, x2, y2):
    mx, my = (x1+x2)/2, (y1+y2)/2
    a(f'<line x1="{x1}" y1="{y1}" x2="{mx-(x2-x1)*0.08}" y2="{my-(y2-y1)*0.08}" stroke="{C["x"]}" stroke-width="2.4" stroke-dasharray="7 5"/>'
      f'<line x1="{mx+(x2-x1)*0.08}" y1="{my+(y2-y1)*0.08}" x2="{x2}" y2="{y2}" stroke="{C["x"]}" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#mx)"/>')
    txt(mx-8, my+6, '?', 20, C['x'], 'end', 'bold')
def pipe_icon(x, y):
    a(f'<line x1="{x}" y1="{y}" x2="{x+12}" y2="{y}" stroke="{C["x"]}" stroke-width="7" stroke-linecap="round"/><line x1="{x+20}" y1="{y}" x2="{x+32}" y2="{y}" stroke="{C["x"]}" stroke-width="7" stroke-linecap="round"/>')

anch = {}; gap1_pts = []
for i, (st, (y0, h, cr)) in enumerate(zip(STEPS, geo)):
    # step box
    a(f'<rect x="{CC[0]}" y="{y0}" width="{CC[1]-CC[0]}" height="64" rx="14" fill="{st["tint"]}" stroke="{INK}" stroke-width="2.4"/>')
    a(f'<circle cx="{CC[0]+36}" cy="{y0+32}" r="20" fill="{INK}"/>'); txt(CC[0]+36, y0+39, st['n'], 20, '#fff', 'middle', 'bold')
    fs = min(19, (CC[1]-CC[0]-90)/(0.63*len(st['t'])))
    txt(CC[0]+68, y0+40, st['t'], round(fs, 1), INK, weight='bold')
    anch[i] = (y0, y0+64)
    # hanging experiments
    yy = y0 + 64 + 16
    a(f'<line x1="{(CC[0]+CC[1])/2}" y1="{y0+64}" x2="{(CC[0]+CC[1])/2}" y2="{yy}" stroke="{INK}" stroke-width="1.6"/>')
    for row in cr:
        xx = CC[0] + 12
        for k, s, w in row:
            a(f'<rect x="{xx}" y="{yy}" width="{w}" height="32" rx="16" fill="{FILL[k]}" stroke="{C[k]}" stroke-width="1.8"/>')
            txt(xx+14, yy+21, s, 14, C[k], weight=('bold' if k == 'b' else 'normal'))
            xx += w + 10
        yy += 42
    txt(CC[0]+16, yy+16, st['cj'], 15, C['g'], weight='bold')
    # side items
    for side, items in (('L', st['L']), ('R', st['R'])):
        x0, x1 = LC if side == 'L' else RC
        sy = y0
        for k, s in items:
            isgap = k.startswith('gap'); kk = 'x' if isgap else k
            lines = wrap(s, x1-x0-28-(40 if isgap else 0), 14)
            hh = 14 + 19*len(lines)
            dash = ' stroke-dasharray="7 5"' if isgap else ''
            a(f'<rect x="{x0}" y="{sy}" width="{x1-x0}" height="{hh}" rx="10" fill="{FILL[kk]}" stroke="{C[kk]}" stroke-width="1.8"{dash}/>')
            tx = x0 + 14
            if isgap: pipe_icon(x0+12, sy+hh/2); tx += 40
            for j, l in enumerate(lines): txt(tx, sy+22+19*j, l, 14, C[kk], weight=('bold' if j == 0 and k in 'rb' else 'normal'))
            ay = sy + min(hh/2, 26)
            if side == 'L':
                a(f'<line x1="{x1}" y1="{ay}" x2="{CC[0]-4}" y2="{min(ay, y0+40)}" stroke="{C[kk]}" stroke-width="1.8" marker-end="url(#m{kk})"/>')
            else:
                if isgap:
                    if k == 'gap1': gap1_pts.append((x1, sy+hh/2))
                    else: gap2 = (x0, sy+hh/2, i)
                else:
                    a(f'<line x1="{x0}" y1="{ay}" x2="{CC[1]+4}" y2="{min(ay, y0+40)}" stroke="{C[kk]}" stroke-width="1.8" marker-end="url(#m{kk})"/>')
            sy += hh + 10

# dependency arrows: adjacent steps straight down the centre, skips along the lane
for s, t, lab in DEPS:
    ys, ye = geo[s][0] + geo[s][1], geo[t][0]
    if t == s + 1:
        cx = (CC[0]+CC[1])/2
        a(f'<line x1="{cx}" y1="{ys+4}" x2="{cx}" y2="{ye-4}" stroke="{INK}" stroke-width="3.4" marker-end="url(#mi)"/>')
        txt(cx+14, (ys+ye)/2+5, lab, 14, DET, italic=True)
    else:
        ln = {(1, 3): 0, (3, 5): 1, (3, 6): 2}[(s, t)]
        lx = LANE + ln*24
        y1, y2 = anch[s][0]+14+ln*12, anch[t][0]+30+ln*10
        a(f'<path d="M{CC[1]} {y1} H {lx} V {y2} H {CC[1]+6}" fill="none" stroke="{INK}" stroke-width="2.6" marker-end="url(#mi)"/>')
        my = (y1+y2)/2 + 60*ln
        a(f'<text x="{lx+16}" y="{my}" font-size="14" fill="{DET}" font-style="italic" text-anchor="middle" transform="rotate(-90 {lx+16} {my})" font-family="{SANS}">{esc(lab)}</text>')
# gap ① broken links: the three gap boxes joined along the right margin
gx = RC[1] + 18
for (x, yv) in gap1_pts:
    a(f'<line x1="{x}" y1="{yv}" x2="{gx}" y2="{yv}" stroke="{C["x"]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
for (x1, y1), (x2, y2) in zip(gap1_pts, gap1_pts[1:]):
    broken(gx, y1, gx, y2)
# gap ② broken link: from the multiple-choice definition (step ①) to where internal reading starts (step ②)
x0g, ygap, ig = gap2
broken(x0g, ygap, CC[1]+6, anch[1][0]+50)

# robustness strip (audits and replications, all steps)
a(f'<rect x="{LC[0]}" y="{AUD_Y}" width="{RC[1]-LC[0]}" height="128" rx="14" fill="#F7FAF7" stroke="{C["g"]}" stroke-width="2" stroke-dasharray="3 0"/>')
txt(LC[0]+18, AUD_Y+30, AUDIT_T, 18, C['g'], weight='bold')
for j, (k, s) in enumerate(AUDIT):
    txt(LC[0]+32, AUD_Y+58+j*24, ('• ' + s), 16, C[k], weight=('bold' if j == 0 else 'normal'))
# legend
ly = H - 46
txt(30, ly, 'Colour = relation type:', 15, INK, weight='bold')
xx = 230
for lab, k in (('proven by one experiment', 'b'), ('joint (several together)', 'g'), ('cannot be decided', 'x'), ('refuted / rewritten / ruled out', 'r')):
    a(f'<rect x="{xx}" y="{ly-13}" width="16" height="16" rx="3" fill="{C[k]}"/>'); txt(xx+24, ly, lab, 14.5, C[k], weight='bold'); xx += 46 + 8.8*len(lab)
pipe_icon(xx, ly-5); txt(xx+42, ly, '- - ? - -  broken link = known gap', 14.5, C['x'], weight='bold')
a('</svg>')
open('flow_v1.svg', 'w').write('\n'.join(o))
print('ok', W, H)
