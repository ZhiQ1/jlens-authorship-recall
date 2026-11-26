# 16:9 deck version (1920x1080, text >= 16 px) of the story-map relation flowchart, split at step boundaries.
# Same content as build_flow_v1.py (STEPS, DEPS imported from a copy of its data). 2026-11-25.
import html, re
src = open('build_flow_v1.py').read()
ns = {}
exec(src[src.index('STEPS = ['):src.index('o = []; a = o.append')], ns)   # take only the data (STEPS, DEPS)
STEPS, DEPS, AUDIT, AUDIT_T = ns['STEPS'], ns['DEPS'], ns['AUDIT'], ns['AUDIT_T']
INK, DET, PALE_T = '#22304A', '#5A6372', '#8A8F98'
C = dict(b='#1F3A6B', g='#2E7D46', x='#6A7385', r='#C0392B')
FILL = dict(b='#EEF2F8', g='#EAF6EC', x='#F3F4F6', r='#FDF3F1')
SANS = "DejaVu Sans, sans-serif"; HAND = "Patrick Hand, Caveat, sans-serif"
W, H = 1920, 1080
LC = (20, 440); CC = (490, 1270); LANE = 1296; RC = (1410, 1856)
TOP = 120; LIMIT = H - 70
FS = 16
def esc(s): return html.escape(s)
def wrap(s, width, size=FS):
    n = max(8, int(width/(0.6*size))); out, cur = [], ''
    for w in s.split(' '):
        if len(cur)+len(w)+(1 if cur else 0) > n and cur: out.append(cur); cur = w
        else: cur = (cur+' '+w) if cur else w
    if cur: out.append(cur)
    return out
def chip_rows(items, width):
    rows, cur, cw = [], [], 0
    for k, s in items:
        w = (0.68 if k == 'b' else 0.62)*FS*len(s) + 28
        if cur and cw + w + 10 > width: rows.append(cur); cur, cw = [], 0
        cur.append((k, s, w)); cw += w + 10
    if cur: rows.append(cur)
    return rows
def item_h(k, s, width): return 14 + 21*len(wrap(s, width-28-(40 if k.startswith('gap') else 0)))
def side_h(items, width): return sum(item_h(k, s, width) + 10 for k, s in items)
def step_h(st):
    cr = chip_rows(st['c'], CC[1]-CC[0]-24)
    return max(62 + 14 + len(cr)*44 + 34, side_h(st['L'], LC[1]-LC[0]), side_h(st['R'], RC[1]-RC[0])), cr

# partition steps into slides
geo = [step_h(st) for st in STEPS]
parts, cur, y = [], [], TOP + 30
for i, (h, cr) in enumerate(geo):
    if cur and y + h > LIMIT - 40: parts.append(cur); cur, y = [], TOP + 50
    cur.append(i); y += h + 64
parts.append(cur)
part_of = {i: p for p, idx in enumerate(parts) for i in idx}

for pi, idx in enumerate(parts):
    o = []; a = o.append
    def txt(x, y, s, size=FS, col=INK, anchor='start', weight='normal', italic=False, fam=SANS):
        st = ' font-style="italic"' if italic else ''
        a(f'<text x="{x}" y="{y}" font-size="{max(size, FS)}" fill="{col}" text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}"{st}>{esc(s)}</text>')
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">')
    a('<defs>' + ''.join(f'<marker id="m{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>' for k, c in list(C.items()) + [('i', INK)]) + '</defs>')
    a(f'<rect width="{W}" height="{H}" fill="#FBFAF5"/>')
    txt(24, 44, 'Story map: how the seven steps depend on each other' + (' (continued)' if pi else ''), 30, INK, fam=HAND)
    txt(24, 74, f'part {pi+1} of {len(parts)} · thick arrows = upstream dependency (label = what is handed down); experiments hang under each step', 16, DET)
    for xx, lab in ((LC, 'Rescued, rewritten & ruled out'), (CC, 'Step and its experiments'), (RC, 'Exceptions, caveats & known gaps')):
        txt((xx[0]+xx[1])/2, TOP-14, lab, 16, PALE_T if xx != CC else INK, 'middle', 'bold')
    for xx in (LC[1]+25, RC[0]-25):
        a(f'<line x1="{xx}" y1="{TOP-34}" x2="{xx}" y2="{LIMIT}" stroke="#D5D9DF" stroke-width="1.4"/>')
    def broken(x1, y1, x2, y2, arrow=True):
        mx, my = (x1+x2)/2, (y1+y2)/2
        m = ' marker-end="url(#mx)"' if arrow else ''
        a(f'<line x1="{x1}" y1="{y1}" x2="{mx-(x2-x1)*0.08}" y2="{my-(y2-y1)*0.08}" stroke="{C["x"]}" stroke-width="2.4" stroke-dasharray="7 5"/>'
          f'<line x1="{mx+(x2-x1)*0.08}" y1="{my+(y2-y1)*0.08}" x2="{x2}" y2="{y2}" stroke="{C["x"]}" stroke-width="2.4" stroke-dasharray="7 5"{m}/>')
        txt(mx-8, my+6, '?', 20, C['x'], 'end', 'bold')
    def pipe_icon(x, y):
        a(f'<line x1="{x}" y1="{y}" x2="{x+12}" y2="{y}" stroke="{C["x"]}" stroke-width="7" stroke-linecap="round"/><line x1="{x+20}" y1="{y}" x2="{x+32}" y2="{y}" stroke="{C["x"]}" stroke-width="7" stroke-linecap="round"/>')
    y = TOP + (50 if pi else 30); anch = {}; gap1_pts = []; gap2 = None
    for i in idx:
        st = STEPS[i]; h, cr = geo[i]; y0 = y
        a(f'<rect x="{CC[0]}" y="{y0}" width="{CC[1]-CC[0]}" height="62" rx="14" fill="{st["tint"]}" stroke="{INK}" stroke-width="2.4"/>')
        a(f'<circle cx="{CC[0]+34}" cy="{y0+31}" r="20" fill="{INK}"/>'); txt(CC[0]+34, y0+38, st['n'], 20, '#fff', 'middle', 'bold')
        fs = min(20, (CC[1]-CC[0]-80)/(0.64*len(st['t'])))
        txt(CC[0]+64, y0+39, st['t'], round(max(fs, 17), 1), INK, weight='bold')
        anch[i] = (y0, y0+62, y0+h)
        yy = y0 + 62 + 14
        a(f'<line x1="{(CC[0]+CC[1])/2}" y1="{y0+62}" x2="{(CC[0]+CC[1])/2}" y2="{yy}" stroke="{INK}" stroke-width="1.6"/>')
        for row in cr:
            xx = CC[0] + 12
            for k, s, w in row:
                a(f'<rect x="{xx}" y="{yy}" width="{w}" height="34" rx="17" fill="{FILL[k]}" stroke="{C[k]}" stroke-width="1.8"/>')
                txt(xx+14, yy+23, s, 16, C[k], weight=('bold' if k == 'b' else 'normal')); xx += w + 10
            yy += 44
        txt(CC[0]+14, yy+18, st['cj'], 17, C['g'], weight='bold')
        for side, items in (('L', st['L']), ('R', st['R'])):
            x0, x1 = LC if side == 'L' else RC; sy = y0
            for k, s in items:
                isgap = k.startswith('gap'); kk = 'x' if isgap else k
                lines = wrap(s, x1-x0-28-(40 if isgap else 0)); hh = 14 + 21*len(lines)
                dash = ' stroke-dasharray="7 5"' if isgap else ''
                a(f'<rect x="{x0}" y="{sy}" width="{x1-x0}" height="{hh}" rx="10" fill="{FILL[kk]}" stroke="{C[kk]}" stroke-width="1.8"{dash}/>')
                tx = x0 + 14
                if isgap: pipe_icon(x0+12, sy+hh/2); tx += 40
                for j, l in enumerate(lines): txt(tx, sy+23+21*j, l, 16, C[kk], weight=('bold' if j == 0 and k in 'rb' else 'normal'))
                ay = sy + min(hh/2, 26)
                if side == 'L': a(f'<line x1="{x1}" y1="{ay}" x2="{CC[0]-4}" y2="{min(ay, y0+40)}" stroke="{C[kk]}" stroke-width="1.8" marker-end="url(#m{kk})"/>')
                elif isgap:
                    if k == 'gap1': gap1_pts.append((x1, sy+hh/2))
                    else: gap2 = (x0, sy+hh/2)
                else: a(f'<line x1="{x0}" y1="{ay}" x2="{CC[1]+4}" y2="{min(ay, y0+40)}" stroke="{C[kk]}" stroke-width="1.8" marker-end="url(#m{kk})"/>')
                sy += hh + 10
        y += h + 64
    cx = (CC[0]+CC[1])/2
    # dependencies
    for s, t, lab in DEPS:
        ps, pt = part_of[s], part_of[t]
        if pt == pi or ps == pi:
            if t == s + 1:
                if ps == pt == pi:
                    ys, ye = anch[s][2], anch[t][0]
                    a(f'<line x1="{cx}" y1="{ys+4}" x2="{cx}" y2="{ye-4}" stroke="{INK}" stroke-width="3.4" marker-end="url(#mi)"/>')
                    txt(cx+14, (ys+ye)/2+6, lab, 16, DET, italic=True)
                elif ps == pi:
                    ys = anch[s][2]; a(f'<line x1="{cx}" y1="{ys+4}" x2="{cx}" y2="{LIMIT-4}" stroke="{INK}" stroke-width="3.4" marker-end="url(#mi)"/>')
                    txt(cx+14, LIMIT-12, f'{lab} → step {STEPS[t]["n"]} (next slide)', 16, DET, italic=True)
                else:
                    ye = anch[t][0]; a(f'<line x1="{cx}" y1="{TOP+4}" x2="{cx}" y2="{ye-4}" stroke="{INK}" stroke-width="3.4" marker-end="url(#mi)"/>')
                    txt(cx+14, TOP+24, f'from step {STEPS[s]["n"]} (previous slide): {lab}', 16, DET, italic=True)
            else:
                ln = {(1, 3): 0, (3, 5): 1, (3, 6): 2}[(s, t)]; lx = LANE + ln*26
                if ps == pt == pi:
                    y1, y2 = anch[s][0]+14+ln*12, anch[t][0]+28+ln*10
                    a(f'<path d="M{CC[1]} {y1} H {lx} V {y2} H {CC[1]+6}" fill="none" stroke="{INK}" stroke-width="2.6" marker-end="url(#mi)"/>')
                    my = (y1+y2)/2 + 40*ln
                elif ps == pi:
                    y1 = anch[s][0]+14+ln*12; y2 = LIMIT - 4
                    a(f'<path d="M{CC[1]} {y1} H {lx} V {y2}" fill="none" stroke="{INK}" stroke-width="2.6" marker-end="url(#mi)"/>')
                    lab = f'{lab} → {STEPS[t]["n"]}'; my = (y1+y2)/2 + 40*ln
                else:
                    y1 = TOP - 6; y2 = anch[t][0]+28+ln*10
                    a(f'<path d="M{lx} {y1} V {y2} H {CC[1]+6}" fill="none" stroke="{INK}" stroke-width="2.6" marker-end="url(#mi)"/>')
                    lab = f'from {STEPS[s]["n"]}: {lab}'
                    if (y2 - y1) < 0.6*16*len(lab) + 16: lab = f'from {STEPS[s]["n"]}'
                    my = (y1+y2)/2
                a(f'<text x="{lx+17}" y="{my}" font-size="16" fill="{DET}" font-style="italic" text-anchor="middle" transform="rotate(-90 {lx+17} {my})" font-family="{SANS}">{esc(lab)}</text>')
    # gap ① broken links (joined along the right margin; continued off-slide when other parts hold gap ① boxes too)
    gx = RC[1] + 22
    for (x, yv) in gap1_pts:
        a(f'<line x1="{x}" y1="{yv}" x2="{gx}" y2="{yv}" stroke="{C["x"]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    for (x1, y1), (x2, y2) in zip(gap1_pts, gap1_pts[1:]): broken(gx, y1, gx, y2)
    all_gap1_parts = sorted({part_of[i] for i, st in enumerate(STEPS) for k, _ in st['R'] if k == 'gap1'})
    if gap1_pts:
        if any(p < pi for p in all_gap1_parts): broken(gx, TOP - 10, gx, gap1_pts[0][1], arrow=True)
        if any(p > pi for p in all_gap1_parts): broken(gx, gap1_pts[-1][1], gx, LIMIT - 4, arrow=True)
    if gap2 and 1 in anch: broken(gap2[0], gap2[1], CC[1]+6, anch[1][0]+50)
    if pi == len(parts) - 1:                     # robustness strip (audits and replications) under the last step
        rows = [(k, l) for k, s in AUDIT for l in wrap('• ' + s, RC[1]-LC[0]-60)]
        ah = 52 + 22*len(rows); ay0 = min(y, LIMIT - ah - 8)
        a(f'<rect x="{LC[0]}" y="{ay0}" width="{RC[1]-LC[0]}" height="{ah}" rx="14" fill="#F7FAF7" stroke="{C["g"]}" stroke-width="2"/>')
        txt(LC[0]+18, ay0+30, AUDIT_T, 18, C['g'], weight='bold')
        for j, (k, l) in enumerate(rows): txt(LC[0]+32, ay0+56+22*j, l, 16, C[k], weight=('bold' if k == 'g' else 'normal'))
    # legend
    ly = H - 30
    txt(24, ly, 'Colour = relation type:', 16, INK, weight='bold')
    xx = 236
    for lab, k in (('proven by one experiment', 'b'), ('joint (several together)', 'g'), ('cannot be decided', 'x'), ('refuted / rewritten / ruled out', 'r')):
        a(f'<rect x="{xx}" y="{ly-13}" width="15" height="15" rx="3" fill="{C[k]}"/>'); txt(xx+22, ly, lab, 16, C[k], weight='bold'); xx += 46 + 9.6*len(lab)
    pipe_icon(xx, ly-5); txt(xx+42, ly, '- - ? - -  broken link = known gap', 16, C['x'], weight='bold')
    a('</svg>')
    suf = '' if len(parts) == 1 else '_' + 'abcdef'[pi]
    open(f'deck16x9/flow_16x9{suf}.svg', 'w').write('\n'.join(o))
    print(f'flow_16x9{suf}', idx, int(y))
