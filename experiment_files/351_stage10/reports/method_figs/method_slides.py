"""Method slides (v3, 2026-11-05): every slide is a list of primitives from method_lib.
Running example (handbook G5.5): "Affect dynamics, bereavement and resilience to loss" (2007), Coifman, Bonanno, Rafaeli.
Sources of every number are listed in SOURCES (also printed by build_method_figs.py)."""
from method_lib import *
import math

TRUE_T = 'Affect dynamics, bereavement and resilience to loss'
FALSE_T = 'The conjunction fallacy and the many meanings of and'
NAME = ['Kar', 'in', 'G', '.', 'Co', 'if', 'man']          # Qwen tokens " Kar" "in" " G" "." " Co" "if" "man"
SOURCES = {}


# ================================================================== legend
def legend():
    b = [Text(70, 100, 'Reading the method figures', 58, font='title', bold=True)]
    b += [step(k + 1, 86 + 32 * k, 142) for k in range(3)] + [Text(170, 149, 'steps, in order', 21, C['pen'])]
    cw, ch, x0, y0, gx, gy = 268, 236, 70, 178, 20, 22

    def card(i, ttl, draw):
        cx, cy = x0 + (i % 4) * (cw + gx), y0 + (i // 4) * (ch + gy)
        b.append(Group([Rect(cx, cy, cw, ch, '#FFFFFF', C['ink'], 2, 12), Text(cx + 16, cy + 36, ttl, 26, bold=True)]
                       + draw(cx, cy), f'card {ttl}'))

    def d_prompt(cx, cy):
        s = []
        for row, (yy, tk) in enumerate([(66, 'true'), (142, 'false')]):
            x, xs = cx + 16, {}
            for k, w in [('white', 26), (tk, 22), (tk, 22), (tk, 22), ('white', 26), ('white', 26), ('white', 12), ('name', 22), ('name', 22)]:
                s.append(tok(x, cy + yy, w, 30, k)); xs.setdefault(k, []).append(x + w / 2); x += w + 4
            mid = lambda k: (xs[k][0] + xs[k][-1]) / 2
            s.append(Text(mid(tk), cy + yy + 52, tk, 17, C['pen'], 'middle'))
            if row == 0:
                s.append(Text(mid('name'), cy + yy + 52, 'name', 17, C['pen'], 'middle'))
        return s
    card(0, 'Prompt tokens', d_prompt)

    def d_layers(cx, cy):
        x = cx + 70
        s = [Line(x, cy + 204, x, cy + 58, C['ink'], 3, arrow=True)]
        for t, yy in [('L0', 196), ('', 160), ('', 124), ('L63', 88)]:
            s.append(Line(x - 8, cy + yy, x + 8, cy + yy, C['ink'], 2))
            if t: s.append(Text(x + 18, cy + yy + 6, t, 19))
        return s
    card(1, 'Layers', d_layers)

    def d_state(cx, cy):
        s = [Rect(cx + 30 + c * 34, cy + 60 + r * 30, 34, 30, None, C['cell'], 1.5) for r in range(4) for c in range(5)]
        s.append(dot(cx + 30 + 3 * 34 + 17, cy + 60 + 30 + 15, 8))
        s.append(Text(cx + 30, cy + 204, 'position →', 17, C['pen']))
        s.append(Text(cx + 222, cy + 180, 'layer →', 17, C['pen'], rot=-90))
        return s
    card(2, 'State = dot', d_state)

    def d_copy(cx, cy):
        return [dot(cx + 50, cy + 84, 9), dot(cx + 50, cy + 176, 9, C['false']),
                Line(cx + 50, cy + 97, cx + 50, cy + 162, C['blue'], 4, arrow=True),
                Text(cx + 76, cy + 90, 'true run', 19), Text(cx + 76, cy + 182, 'false run', 19)]
    card(3, 'Copy a state', d_copy)

    def d_block(cx, cy):
        s = [tok(cx + 24, cy + 170, 24, 28, 'true'), tok(cx + 52, cy + 170, 24, 28, 'true'), tok(cx + 190, cy + 170, 26, 28, 'name')]
        for xx in (36, 64):
            s.append(Poly(qcurve((cx + 203, cy + 168), (cx + 120, cy + 70), (cx + xx, cy + 168)), C['pen'], 2, dash=True))
        s.append(cross(cx + 123, cy + 119, 12))
        return s
    card(4, 'Block', d_block)

    def d_inject(cx, cy):
        return [dot(cx + 50, cy + 84, 9),
                Poly(qcurve((cx + 62, cy + 92), (cx + 140, cy + 96), (cx + 160, cy + 146)), C['blue'], 4, arrow=True),
                tok(cx + 56, cy + 152, 34, 34, 'white'), tok(cx + 96, cy + 152, 34, 34, 'white'),
                tok(cx + 140, cy + 152, 40, 34, 'white', 'X', 20), tok(cx + 186, cy + 152, 30, 34, 'name')]
    card(5, 'Inject', d_inject)

    def d_read(cx, cy):
        s = [magnifier(cx + 50, cy + 104, 24)]
        for k, (w, ok) in enumerate([('1. Coifman', True), ('2. Smith', False), ('3. Zhang', False)]):
            y = cy + 70 + k * 34
            s.append(Group([Rect(cx + 112, y, 136, 28, C['name'] if ok else '#FFFFFF', C['ink'], 1.2, 4),
                            Text(cx + 122, y + 20, w, 18)], f'rank {k + 1}'))
        return s
    card(6, 'Read out', d_read)

    def d_probe(cx, cy):
        s = [dot(cx + 34 + k * 20, cy + 70 + (k % 2) * 10, 6) for k in range(5)]
        s.append(funnel(cx + 26, cy + 100))
        s.append(Line(cx + 140, cy + 154, cx + 178, cy + 154, C['ink'], 2.5, arrow=True))
        s.append(tok(cx + 184, cy + 138, 64, 32, 'white', 'year', 17))
        return s
    card(7, 'Probe', d_probe)
    return b


# ================================================================== replacement (patching)
X6 = [('L24', 0.080), ('L40', 0.302), ('L48', 0.821), ('L52', 0.995)]

def patch():
    fs = 15
    b = title('Replacement (patching)', 'Coifman, Bonanno, Rafaeli (2007)')

    def row_spec(ttl, kind):
        return ([('white', '…titled')] + [(kind, w) for w in ttl.split()] +
                [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')] + [('name', t) for t in NAME])

    def layout(spec, x_end):          # right-aligned so the copied (post-title) positions line up in both runs
        ws = [tok_w(lab, fs) for _, lab in spec]
        x = x_end - sum(ws) - 4 * (len(ws) - 1); cols = []
        for (k, lab), w in zip(spec, ws):
            cols.append((x, w, k, lab)); x += w + 4
        return cols

    x_end = 985
    ct, cf = layout(row_spec(TRUE_T, 'true'), x_end), layout(row_spec(FALSE_T, 'false'), x_end)
    n_suf = 3 + len(NAME)
    x_left = min(ct[0][0], cf[0][0])
    TOK_T, TOK_F, TOP_T, TOP_F, LL_T, LL_F, TH = 318, 600, 172, 454, 226, 508, 32

    def ladder(cl, y_tok, y_top, yl, nm):
        g = []
        for x, w, kind, lab in cl:
            c = x + w / 2
            g.append(Line(c, y_tok - 8, c, y_top, C['pen'], 5, round=True, op=.35))
        g.append(Text(x_left - 12, y_top + 6, 'L63', 15, C['pen'], 'end'))
        g.append(Text(x_left - 12, y_tok - 4, 'L0', 15, C['pen'], 'end'))
        g.append(Line(cl[0][0] + cl[0][1] / 2 - 10, yl, x_end + 20, yl, C['blue'], 1.6, dash=True))
        g.append(Text(x_end + 26, yl + 6, 'layer l', 18, C['blue']))
        return Group(g, f'{nm} run layers')

    b += [ladder(ct, TOK_T, TOP_T, LL_T, 'true'), ladder(cf, TOK_F, TOP_F, LL_F, 'false')]
    b.append(Group([Line(x + w / 2, LL_T + 9, x + w / 2, LL_F - 10, C['blue'], 3.5, arrow=True) for x, w, k, lab in ct[-n_suf:]], 'copy arrows'))
    b.append(Group([tok(x, TOK_T, w, TH, k, lab, fs) for x, w, k, lab in ct], 'true prompt'))
    b.append(Group([tok(x, TOK_F, w, TH, k, lab, fs) for x, w, k, lab in cf], 'false prompt'))
    for cl, yl, nm in ((ct, LL_T, 'true'), (cf, LL_F, 'false')):
        b.append(Group([dot(x + w / 2, yl, 6, C['ink'] if i >= len(cl) - n_suf else C['pen']) for i, (x, w, k, lab) in enumerate(cl)],
                       f'{nm} states at layer l'))
    b.append(step_label(1, ct[1][0] + 13, TOK_T + TH + 30, 'true title'))
    b.append(step_label(2, cf[1][0] + 13, TOK_F + TH + 30, 'false title'))
    sx0 = ct[-n_suf][0]
    b.append(Group([step(3, sx0 - 26 - text_w('copy at layer l', 20) - 21, 412), Text(sx0 - 26, 419, 'copy at layer l', 20, C['blue'], 'end')],
                   'step 3 label'))
    nx = (cf[-len(NAME)][0] + cf[-1][0] + cf[-1][1]) / 2
    b.append(magnifier(nx - 92, TOK_F + TH + 28, 13))
    b.append(step_label(4, nx - 44, TOK_F + TH + 30, 'score the name'))
    sx, y0, y1 = 1130, 590, 230
    g = [Line(sx, y0, sx, y1, C['ink'], 3)]
    for v in (0, 0.5, 1):
        y = y0 + (y1 - y0) * v
        g += [Line(sx - 8, y, sx + 8, y, C['ink'], 2), Text(sx - 16, y + 6, f'{v:g}', 17, C['pen'], 'end')]
    for t, v in X6:
        y = y0 + (y1 - y0) * v
        g += [dot(sx, y, 8, C['blue']), Text(sx + 16, y + 6, f'{t} {v:.3f}', 18)]
    b.append(Group(g, 'recovery scale'))
    b.append(step_label(5, 1068, 186, 'recovery R(l)', fs=21))
    b.append(Group([Text(1055, 640, 'mean of 5 false titles,', 15, C['pen']), Text(1055, 660, '1,186 papers', 15, C['pen'])], 'footnote'))
    b.append(formula_box(600, 64, 'R(l) = (patched − false) ÷ (true − false)', 28))
    return b



# ================================================================== small chart helper
def chart(x0, y0, w, h, xs, series, ymin, ymax, xlab=None, ylab=None, yticks=(), xticks=None, name='chart', fs=15):
    """line chart; series = [(values, colour, label)]; xs = numeric x positions (same for all); returns Group"""
    X = lambda v: x0 + (v - xs[0]) / (xs[-1] - xs[0]) * w
    Y = lambda v: y0 + h - (v - ymin) / (ymax - ymin) * h
    g = [Line(x0, y0 + h, x0 + w + 8, y0 + h, C['ink'], 2), Line(x0, y0 + h, x0, y0 - 6, C['ink'], 2)]
    for t in yticks:
        g += [Line(x0 - 6, Y(t), x0, Y(t), C['ink'], 1.6), Text(x0 - 10, Y(t) + 5, f'{t:g}'.replace('-', '−'), fs, C['pen'], 'end')]
    for v, lab in (xticks or []):
        g += [Line(X(v), y0 + h, X(v), y0 + h + 6, C['ink'], 1.6), Text(X(v), y0 + h + 22, lab, fs, C['pen'], 'middle')]
    for vals, col, lab in series:
        pts = [(X(a), Y(b)) for a, b in zip(xs, vals)]
        g.append(Poly(pts, col, 3, round=True))
        g += [Circle(px, py, 4.5, col) for px, py in pts]
        if lab: g.append(Text(pts[-1][0] + 10, pts[-1][1] + 5, lab, fs + 2, col))
    if xlab: g.append(Text(x0 + w / 2, y0 + h + 44, xlab, fs, C['pen'], 'middle'))
    if ylab: g.append(Text(x0, y0 - 16, ylab, fs, C['pen']))
    return Group(g, name)

def fmt(v, d=3, sign=True):
    s = f'{v:+.{d}f}' if sign else f'{v:.{d}f}'
    return s.replace('-', '−')

def padlock(x, y, s=1.0, col=None):
    col = col or C['ink']
    arc = [(x + 9 * s + 9 * s * math.cos(math.pi + i * math.pi / 12), y - 2 * s + 11 * s * math.sin(math.pi + i * math.pi / 12)) for i in range(13)]
    return Group([Poly(arc, col, 3 * s), Rect(x - 2 * s, y - 2 * s, 22 * s, 18 * s, col, col, 1, 3)], 'padlock')




def flow(nodes, edges, fs=19):
    """nodes = [(id, n, x, y, label)], edges = [(a, b, side)] -> (items, boxes)"""
    items, box = [], {}
    for i, n, x, y, lab in nodes:
        g, bx = flow_node(n, x, y, lab, fs); items.append(g); box[i] = bx
    arrows = [flow_arrow(box[a], box[b], side) for a, b, side in edges]
    return [Group(arrows, 'flow arrows')] + items, box


def prompt_spec(ttl, kind, name=True, n_name=None):
    s = [('white', '…titled')] + [(kind, w) for w in ttl.split()] + [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')]
    if name: s += [('name', t) for t in NAME[:n_name]]
    return s


# ================================================================== scoring & spec (G5.5 real ranks)
SCORE_ROWS = [  # condition, first-author 7 token ranks (final L63), mean_nlr over all 16 tokens
    ('true', [83, 2, 25, 1, 61, 1, 1], -0.7190),
    ('false_0', [300, 1, 20, 1, 330, 115, 1], -1.0234),
    ('false_1', [855, 3, 18, 1, 304, 58, 1], -1.1540),
    ('false_2', [823, 3, 7, 2, 519, 154, 1], -1.2625),
    ('false_3', [278, 1, 19, 1, 170, 230, 1], -1.1334),
    ('false_4', [664, 1, 26, 1, 158, 20, 1], -0.9895),
    ('delete', [185, 2, 17, 1, 113, 5, 1], -0.8808)]

def scoring():
    b = title('Scoring: rank → log → spec', 'Coifman, Bonanno, Rafaeli (2007) · output layer')
    y0, dy, th = 222, 44, 30
    xs_rank, cw = 556, 44
    f, bx = flow([('p', 1, 120, 160, '7 prompts'), ('r', 2, xs_rank, 160, 'rank per name token'),
                  ('m', 3, 878, 160, 'mean log10(1/rank)'), ('c', 4, 80, 572, 'contrast')],
                 [('p', 'r', 'h'), ('r', 'm', 'h')])
    b += f
    for k, (cond, ranks, m) in enumerate(SCORE_ROWS):
        y = y0 + k * dy
        kind = 'true' if cond == 'true' else ('false' if cond.startswith('false') else None)
        g = [Text(150, y + 22, cond, 19, C['ink'], 'end', bold=(cond == 'true'))]
        x = 164
        g.append(tok(x, y, 40, th, 'white')); x += 44
        nt = 7 if kind == 'true' else (9 if kind == 'false' else 0)
        for i in range(nt):
            g.append(tok(x, y, 13, th, kind)); x += 16
        if nt == 0: x += 76
        for i in range(3):
            g.append(tok(x, y, 13, th, 'white')); x += 16
        for i in range(7):
            g.append(tok(x, y, 11, th, 'name')); x += 14
        g.append(Line(x + 6, y + th / 2, xs_rank - 10, y + th / 2, C['pen'], 1.6, arrow=True))
        for i, r in enumerate(ranks):
            cx = xs_rank + i * cw
            g.append(Rect(cx, y, cw - 4, th, C['name'] if r == 1 else '#FFFFFF', C['ink'], 1.2, 4))
            g.append(Text(cx + (cw - 4) / 2, y + 21, str(r), 16, C['ink'], 'middle'))
        xe = xs_rank + 7 * cw
        g.append(Line(xe + 4, y + th / 2, 892, y + th / 2, C['pen'], 1.6, arrow=True))
        g.append(Text(900, y + 22, fmt(m, 4), 20, C['true'] if cond == 'true' else C['ink'], bold=(cond == 'true')))
        b.append(Group(g, f'row {cond}'))
    yt, yb = y0 + dy + 4, y0 + 5 * dy + th - 4
    b.append(Group([Poly([(990, yt), (1002, yt), (1002, yb), (990, yb)], C['ink'], 2),
                    Line(1002, (yt + yb) / 2, 1022, (yt + yb) / 2, C['ink'], 2),
                    Text(1030, (yt + yb) / 2 - 4, 'mean false', 18, C['pen']),
                    Text(1030, (yt + yb) / 2 + 20, '−1.1126', 20, bold=True)], 'false mean'))
    b.append(Text(xs_rank, y0 + 7 * dy + 4, 'author 1 shown · mean over 16 tokens', 15, C['pen']))
    # step 4 branches: spec (formula), total, topic
    c = bx['c']
    fb = formula_box(330, 556, 'spec = mean nlr(true) − mean over 5 false titles', 26, sub='= −0.7190 − (−1.1126) = +0.3935')
    b.append(fb)
    b.append(Group([flow_arrow(c, (330, 556, 10, 80), 'h'),
                    Poly(qcurve((c[0] + c[2] / 2, c[1] + c[3] + 4), (c[0] + c[2] / 2, 676), (322, 676)), C['ink'], 2.5, arrow=True)], 'branch arrows'))
    b.append(Text(330, 682, 'total = true − delete = +0.1618 · topic = mean false − delete = −0.2318', 18, C['ink']))
    SOURCES['scoring'] = ['ranks (first author, 7 tokens), mean_nlr of each condition, false mean −1.1126, spec +0.3935, total +0.1618, topic −0.2318: '
                          '351_stage10/reports/methods/parts/A_global1.html G5.5 (raw final/L63/shard_011.npz rows 25025–25040; summary_title/paper_title_contrasts.parquet readout=final layer=63)']
    return b


# ================================================================== groups & samples (Sankey)
CELLS = {'R0': [('A', 'strong', 4110), ('U0', 'uncertain', 2002), ('B', 'fail', 2186)],
         'R1': [('C', 'strong', 511), ('', 'uncertain', 51), ('D', 'fail', 34)],
         'R2': [('', 'strong', 204), ('', 'uncertain', 9), ('', 'fail', 1)]}
RTOT = {'R0': 8298, 'R1': 596, 'R2': 214}
FILLC = {'A': C['true'], 'C': C['true'], 'B': C['blue'], 'D': C['blue'], 'U0': C['false'], '': C['false']}

def groups():
    b = title('Groups and samples', 'example: cell C')
    f, bx = flow([('a', 1, 70, 160, 'papers'), ('r', 2, 250, 160, 'open recall'), ('m', 3, 470, 160, 'recognition'),
                  ('c', 4, 700, 160, 'cells'), ('s', 5, 900, 160, 'samples')],
                 [('a', 'r', 'h'), ('r', 'm', 'h'), ('m', 'c', 'h'), ('c', 's', 'h')])
    b += f
    sc = 300 / 9108; top = 246; gap1, gap2 = 18, 6
    x1, x2, x3, bw = 110, 300, 520, 22
    b.append(Group([Rect(x1, top, bw, 9108 * sc, C['ink'], None), Text(x1 - 8, top + 9108 * sc / 2 + 7, '9,108', 20, C['ink'], 'end', bold=True)], 'all papers'))
    y_src, y2, y3 = top, top, top
    for R in ('R0', 'R1', 'R2'):
        hR = RTOT[R] * sc
        b.append(Poly(band(x1 + bw, y_src, y_src + hR, x2, y2, y2 + hR), None, fill=C['pen'], closed=True, fill_op=.18, name=f'band all→{R}'))
        b.append(Group([Rect(x2, y2, bw, max(hR, 3), C['ink']), Text(x2 - 8, y2 + max(hR, 3) / 2 + 7, R, 18, C['ink'], 'end', bold=True)], f'node {R}'))
        ys = y2
        for lab, rec, n in CELLS[R]:
            h = max(n * sc, 2.5); hb = n * sc
            b.append(Poly(band(x2 + bw, ys, ys + hb, x3, y3, y3 + hb), None, fill=FILLC[lab], closed=True, fill_op=.35, name=f'band {R}→{rec}'))
            b.append(Rect(x3, y3, bw, h, FILLC[lab], C['ink'], 1))
            if R == 'R0':
                b.append(Group([Text(x3 + bw + 10, y3 + h / 2 + 7, f'{lab} {n:,}', 20, C['ink'], bold=True),
                                Text(x3 + bw + 110, y3 + h / 2 + 7, rec, 16, C['pen'])], f'label {lab}'))
            ys += hb; y3 += h + gap2
        y_src += hR; y2 += max(hR, 3) + gap1; y3 += gap1 - gap2
    yR1 = top + RTOT['R0'] * sc + gap1 + 3 * gap2
    b.append(Text(x3 + bw + 10, yR1 + 10, 'C 511 · 51 · D 34', 19, C['ink'], bold=True))
    b.append(Text(x3 + bw + 10, yR1 + 48, 'R2: 204 · 9 · 1', 18, C['pen']))
    b.append(formula_box(560, 628, 'target = A + C = 4,621   ·   control = B + D = 2,220', 25))
    # right: who samples which cells
    rx = 860
    rows = [('Stage 10 · M2 · M3', 'all papers', [C['true'], C['blue'], C['false']]),
            ('Stages 11–13 · X', '593 target + 593 control', [C['true'], C['blue']]),
            ('', '1,178 matched pairs', []),
            ('Stages 1–9', 'Pilot50 · Stage 8 (A, B)', [C['true'], C['blue']])]
    yy = 262; g = []
    for head, txt, cols in rows:
        if head:
            g.append(Text(rx, yy, head, 20, C['ink'], bold=True)); yy += 28
        cx = rx
        for c in cols:
            g.append(Rect(cx, yy - 15, 16, 16, c, C['ink'], 1, 3)); cx += 20
        g.append(Text(cx + (6 if cols else 0), yy, txt, 18, C['ink'])); yy += 44
    b.append(Group(g, 'samples'))
    b.append(Group([Line(bx['s'][0] + bx['s'][2] / 2, bx['s'][1] + 44, bx['s'][0] + bx['s'][2] / 2, 236, C['ink'], 2, arrow=True)], 'samples arrow'))
    SOURCES['groups'] = ['9,108; R0/R1/R2 8,298/596/214; cells 4,110/2,002/2,186 · 511/51/34 · 204/9/1: 351_stage10/cohort/papers.parquet recall_level × mc_team_outcome_tight (method_figs/cohort_cells.csv)',
                         'target 4,621 = A + C, control 2,220 = B + D: papers.parquet group_tight; example paper = R1, target (cell C)',
                         '593 + 593 = 1,186: 361_stage11/config/sample.parquet (361_stage11.py:56, 109–115); 1,178 pairs: 381_stage13/config/pairs.parquet',
                         'Pilot50 / Stage 8 from A and B: 351_stage8/config/analysis_plan.json "groups"; deck slide "Cohort and behavioural labels"']
    return b


# ================================================================== statistical conventions
BINS = [('0-2', 200, 352), ('3-4', 207, 355), ('5-8', 237, 332), ('9-16', 288, 275), ('17-32', 327, 234), ('33-64', 401, 185),
        ('65-128', 441, 165), ('129-256', 497, 126), ('257-512', 533, 105), ('513-1024', 603, 53), ('1025-2048', 539, 29),
        ('2049-4096', 264, 9), ('4097+', 84, 0)]

def stats():
    b = title('Statistical conventions', 'example paper: bin 65–128')
    f, bx = flow([('b', 1, 70, 160, 'citation bins'), ('d', 2, 290, 160, 'target − control'), ('w', 3, 540, 160, 'weighted mean'),
                  ('t', 4, 860, 160, 'teams'), ('r', 5, 1010, 160, 'resample teams')],
                 [('b', 'd', 'h'), ('d', 'w', 'h'), ('t', 'r', 'h')])
    b += f
    x0, yb, bw, gp, sc = 70, 470, 46, 8, 0.3
    for i, (lab, nt, nc) in enumerate(BINS):
        x = x0 + i * (bw + gp); used = nt >= 30 and nc >= 30
        g = [Rect(x, yb - 200, bw, 200, '#FFFFFF' if used else C['faint'], C['ink'] if used else C['cell'], 1.4, 6, dash=not used)]
        g.append(Rect(x + 6, yb - nt * sc, 15, nt * sc, C['true'], None))
        if nc: g.append(Rect(x + 25, yb - nc * sc, 15, nc * sc, C['blue'], None))
        g.append(Text(x + bw / 2, yb + 18, lab, 12.5, C['ink'] if used else C['pen'], 'middle'))
        if lab == '65-128':
            g.append(Rect(x - 4, yb - 204, bw + 8, 208, None, C['true'], 2.5, 8))
        b.append(Group(g, f'bin {lab}'))
    b.append(Group([Rect(x0, yb + 34, 14, 12, C['true']), Text(x0 + 20, yb + 45, 'target', 15),
                    Rect(x0 + 80, yb + 34, 14, 12, C['blue']), Text(x0 + 100, yb + 45, 'control', 15),
                    Text(x0 + 10 * (bw + gp) + 80, yb + 45, '< 30: dropped', 15, C['pen'], 'middle')], 'bin legend'))
    b.append(formula_box(70, 560, 'Δ = Σ w_b · (mean_t − mean_c),   w_b ∝ n_t·n_c / (n_t + n_c)', 25))
    # teams
    papers = [(890, 270, 0), (950, 256, 0), (925, 320, 0), (1040, 266, 1), (1100, 310, 1), (1180, 260, 2), (1215, 320, 2), (1160, 350, 2), (1010, 360, 3)]
    tcol = [C['true'], C['blue'], C['green'], C['purple']]
    links = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7)]
    g = []
    for t in range(4):
        pts = [(x, y) for x, y, tt in papers if tt == t]
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        r = max(max(math.hypot(x - cx, y - cy) for x, y in pts) + 26, 30)
        g.append(Circle(cx, cy, r, tcol[t], tcol[t], 1.5, fill_op=.12))
    for a, c in links:
        g.append(Line(papers[a][0], papers[a][1], papers[c][0], papers[c][1], C['ink'], 2))
    for x, y, t in papers:
        g.append(Rect(x - 11, y - 13, 22, 26, '#FFFFFF', C['ink'], 1.6, 3))
        g += [Line(x - 6, y - 5 + k * 6, x + 6, y - 5 + k * 6, C['cell'], 1.4) for k in range(3)]
    b.append(Group(g, 'teams illustration'))
    b.append(Text(870, 420, 'shared author name = one team', 17, C['pen']))
    b.append(Text(870, 448, '7,247 teams', 21, C['ink'], bold=True))
    fx, fy = 860, 480
    folds = [[0, 0, 0], [1, 1], [2, 2, 2], [3], []]
    g = []
    for k in range(5):
        x = fx + k * 76
        g.append(Rect(x, fy, 70, 40, '#FFFFFF', C['ink'], 1.6, 6))
        for j, t in enumerate(folds[k]):
            g.append(Rect(x + 8 + j * 19, fy + 12, 15, 15, tcol[t], C['ink'], 1, 2))
    b.append(Group(g, 'fold strip'))
    b.append(Text(860, fy + 66, 'one team, one fold · 2,000 draws', 17, C['pen']))
    SOURCES['stats'] = ['target/control papers per citation bin (group_tight × citation_bin; e.g. 65–128: 441 / 165): 351_stage10/cohort/papers.parquet',
                        '≥ 30 per group (MIN_STRATUM): ~/jlens_work/10_stage10/351_stage10.py:642; w_b = n_t·n_c/(n_t+n_c): stratified_diff :670–680 (same in stage11_analyze.py:38, stage13_cluster_ci.py:45, 14_groups/groups_core.py:112)',
                        '7,247 teams over 9,108 papers: 381_stage13/reports/cluster_ci.md line 3 (team rule stage13_cpu.py group_folds :109–123); 2,000 bootstrap draws: B_BOOT, handbook G5.4 / m2_teamci.md']
    return b


# ================================================================== Stage 8 independent replication
def replication():
    b = title('Independent replication (Stage 8)', 'plan first, data second')
    f, bx = flow([('l', 1, 70, 200, 'lock the plan'), ('p', 2, 330, 200, '200 new papers'), ('s', 3, 600, 200, 'score'),
                  ('c', 4, 820, 200, 'check vs plan'), ('q', 5, 980, 320, 'L56'), ('e', 6, 980, 400, '7 layers')],
                 [('l', 'p', 'h'), ('p', 's', 'h'), ('s', 'c', 'h')])
    b += f
    b.append(Group([flow_arrow(bx['c'], bx['q'], 'v'), Poly(qcurve((bx['c'][0] + 30, bx['c'][1] + 44), (bx['c'][0] + 30, 420), (974, 420)), C['ink'], 2.5, arrow=True)], 'branch arrows'))
    b.append(Group([Text(80, 270, '10-18 14:29', 19, C['pen']), Text(80, 296, '(L56 primary 21:14)', 16, C['pen'])], 'lock time'))
    b.append(padlock(250, 268, 0.9))
    b.append(Text(600, 270, '10-18 21:47 → 10-20', 19, C['pen']))
    g = [Rect(330 + (i % 10) * 13, 256 + (i // 10) * 13, 10, 10, C['true'] if i % 2 == 0 else C['blue'], None) for i in range(50)]
    b.append(Group(g, 'papers (quarter shown)'))
    b.append(Text(330, 338, '100 A/B pairs', 17, C['pen']))
    def ci_row(yy, est, lo, hi, col):
        X = lambda v: 1110 + v * 18
        return Group([Line(X(lo), yy, X(hi), yy, col, 4, round=True), Circle(X(est), yy, 7, col),
                      Text(1110, yy + 30, f'+{est:.2f} pp [{lo:.2f}, {hi:.2f}]', 17, C['ink'])], 'result')
    b.append(Line(1110, 330, 1110, 470, C['pen'], 1.5, dash=True))
    b.append(ci_row(340, 5.18, 2.93, 7.48, C['true']))
    b.append(ci_row(420, 2.33, 1.50, 3.19, C['ink']))
    b.append(formula_box(70, 520, 'RQ1 = win rate(true title) − mean win rate(20 false titles)', 25,
                         sub='first author vs 100 false names · J-Lens · paper bootstrap'))
    SOURCES['replication'] = ['plan locked 2026-10-18 14:29 (status FROZEN_BEFORE_STAGE8_SCORING): 351_stage8/config/analysis_plan.json (mtime); L56 made primary 21:14: 08_stage8/351_stage8_PROTOCOL.md (handbook C_stage1_9 s19-s8-protocol)',
                              '200 new papers = 100 matched A/B pairs: handbook s19-s8a; scoring 2026-10-18 21:47 → 2026-10-20 09:05: s19-s8c',
                              'RQ1 L56 +5.18 pp [2.93, 7.48]: s19-s8d, 351_stage8/stage8D/summary/primary_questions.csv; frozen 7-layer endpoint +2.33 pp [1.50, 3.19]: s19-s8dsupp, 351_stage8/recompute_2026-10-30/s8_endpoints.csv',
                              'definition (true − mean of 20 false titles; 100 false authors): analysis_plan.json primary_endpoint']
    return b


# ================================================================== layer-by-layer readout (real ranks)
CO_RANK = [(24, 37675), (40, 3979), (48, 44676), (56, 120750), (60, 23169), (61, 9811), (62, 120), (63, 61)]
LAYERS_R = [24, 32, 40, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
MEAN_T = [-4.2483, -4.2929, -3.9605, -4.4742, -4.3159, -4.3900, -4.1552, -4.0890, -4.0522, -4.1588, -4.0651, -3.9333, -3.9181, -3.4255, -3.3573, -2.6339, -1.1108, -0.7719]
MEAN_F = [-4.2501, -4.1322, -3.6768, -4.3793, -4.2211, -4.3558, -4.1422, -4.0584, -3.9732, -4.2638, -4.1228, -3.9704, -3.9457, -3.6793, -3.6491, -3.3500, -2.1774, -1.1939]

def readout():
    b = title('Layer-by-layer readout', 'Coifman, Bonanno, Rafaeli (2007) · logit lens')
    f, bx = flow([('p', 1, 70, 160, 'prompt'), ('s', 2, 220, 160, 'state at name'), ('l', 3, 500, 160, 'lens → vocabulary'),
                  ('r', 4, 750, 160, 'rank of true token'), ('m', 5, 1010, 160, 'mean')],
                 [('p', 's', 'h'), ('s', 'l', 'h'), ('l', 'r', 'h'), ('r', 'm', 'h')])
    b += f
    spec = ([('white', '…titled')] + [('true', w) for w in TRUE_T.split()[:2]] + [('true', '…')] +
            [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')] + [('name', t) for t in NAME])
    row, cols = tok_row(spec, 470, 652, fs=15, name='true prompt')
    b.append(row)
    co = [c for c in cols if c[3] == 'Co'][0]; cx = co[0] + co[1] / 2
    ytop, ybot = 250, 620
    _ix = {L: i for i, (L, r) in enumerate(CO_RANK)}
    Y = lambda L: ybot - _ix[L] / (len(CO_RANK) - 1) * (ybot - ytop)
    g = [Line(cx, ybot, cx, ytop - 6, C['pen'], 6, round=True, op=.35)]
    for L, r in CO_RANK:
        y = Y(L)
        g.append(Circle(cx, y, 6, C['ink']))
        g.append(Text(cx - 16, y + 6, f'L{L}' if L < 63 else 'out', 16, C['pen'], 'end'))
        g.append(Group([Rect(cx + 40, y - 13, 86, 26, C['name'] if r <= 100 else '#FFFFFF', C['ink'], 1.2, 4),
                        Text(cx + 83, y + 6, f'{r:,}', 16, C['ink'], 'middle')], f'rank L{L}'))
    b.append(Group(g, 'Co layers'))
    b.append(magnifier(cx - 74, Y(62) + 2, 9))
    b.append(Text(cx + 40, ytop - 22, 'rank of “Co”', 17, C['pen']))
    b.append(formula_box(70, 236, 'nlr = log10(1 / rank)', 27, sub='rank = 1 + #{tokens scored above the true one}'))
    b.append(chart(130, 380, 380, 190, LAYERS_R, [(MEAN_F, C['pen'], 'false_0'), (MEAN_T, C['true'], 'true')], -5, 0,
                   ylab='mean nlr, 7 tokens', yticks=(-4, -2, 0),
                   xticks=[(24, 'L24'), (40, 'L40'), (48, 'L48'), (56, 'L56'), (63, 'out')], name='mean chart'))
    SOURCES['readout'] = ['ranks of " Co" (row 25029) and mean nlr of the 7 first-author tokens (rows 25025–25031), logit lens L24–L62 + final L63, true and false_0: '
                          '351_stage10/raw/logit/L*/shard_011.npz, raw/final/L63/shard_011.npz, raw/cond_false_0/…; tabulated in method_figs/coifman_layer_ranks.csv',
                          'rank definition (strictly greater logits): 351_stage10.py score() :442–449, handbook G5.1']
    return b


# ================================================================== knockout (block) + X7
X7_S = [(0, 1.004), (24, 0.873), (32, 0.558), (40, 0.293), (48, 0.143), (52, 0.029)]

def knockout():
    b = title('Knockout (block attention)', 'Coifman, Bonanno, Rafaeli (2007)')
    f, bx = flow([('k', 1, 70, 160, 'block tail → title from l'), ('t', 2, 420, 140, 'true title: T'), ('f', 3, 420, 192, 'false title: F'),
                  ('s', 4, 680, 166, 'S = T − F')],
                 [('k', 't', 'h'), ('k', 'f', 'h'), ('t', 's', 'h'), ('f', 's', 'h')])
    b += f
    spec = ([('white', '…titled')] + [('true', w) for w in TRUE_T.split()] +
            [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')] + [('name', t) for t in NAME[:3]] + [('name', '…')])
    row, cols = tok_row(spec, 70, 560, fs=15, name='true prompt')
    tcols = [c for c in cols if c[2] == 'true']; tail = cols[len(tcols) + 1:]
    yl = 360; xr = cols[-1][0] + cols[-1][1]
    b.append(Group([Rect(70, 252, xr - 70, yl - 252, C['red'], None, fill_op=.08),
                    Line(70, yl, xr + 10, yl, C['red'], 1.8, dash=True),
                    Text(xr + 16, yl + 6, 'layer l', 18, C['red']), Text(xr + 16, 274, 'blocked', 17, C['red'])], 'blocked band'))
    g = []
    for (x, w, kk, lab) in tail[::3]:
        sx = x + w / 2
        for (tx, tw, _, _) in tcols[1::3]:
            ex = tx + tw / 2
            g.append(Poly(qcurve((sx, 552), ((sx + ex) / 2, 430 - (sx - ex) * 0.12), (ex, 552)), C['pen'], 1.8, dash=True))
    b.append(Group(g, 'attention to title'))
    b.append(cross((tcols[-1][0] + tail[0][0]) / 2 + 30, 450, 13))
    b.append(row)
    x0, y0, h = 900, 560, 250
    g = [Line(x0 - 10, y0, x0 + 6 * 56, y0, C['ink'], 2), Line(x0 - 10, y0, x0 - 10, y0 - h - 10, C['ink'], 2),
         Text(x0 - 16, y0 - h + 5, '1', 15, C['pen'], 'end'), Text(x0 - 16, y0 + 5, '0', 15, C['pen'], 'end'),
         Line(x0 - 16, y0 - h, x0 - 10, y0 - h, C['ink'], 1.6)]
    for i, (L, s) in enumerate(X7_S):
        x = x0 + i * 56
        g.append(Rect(x, y0 - s * h, 38, s * h, C['red'], C['ink'], 1.2, 2, fill_op=.75))
        g.append(Text(x + 19, y0 - s * h - 8, f'{s:.2f}', 15, C['ink'], 'middle'))
        g.append(Text(x + 19, y0 + 20, f'L{L}', 15, C['pen'], 'middle'))
    g.append(Text(x0 + 160, y0 + 44, 'block from layer · S', 15, C['pen'], 'middle'))
    b.append(Group(g, 'S chart'))
    b.append(Text(900, 640, 'L52: target 0.018 · control 0.051', 17, C['ink']))
    b.append(formula_box(70, 626, 'S(l) = T(l) − F(l)', 27, sub='loss as share of (true − false), 1,186 papers'))
    SOURCES['knockout'] = ['S = T − F (share of the true − false gap) L0 1.004, L24 0.873, L32 0.558, L40 0.293, L48 0.143, L52 0.029 (target 0.018, control 0.051): 381_stage13/reports/x7_report.md lines 20, 37, 48–54',
                           'blocked = every position after the title cannot attend to the title tokens from layer l up; F = same knockout on the false_0 run: 381_stage13/config/prereg_addendum3.json "X7"; 361_stage11/reports/stage11_report.md E2']
    return b


# ================================================================== probe
def probe():
    b = title('Probe', 'Coifman, Bonanno, Rafaeli (2007) · state at “loss”')
    f, bx = flow([('s', 1, 70, 160, 'state at last title token'), ('p', 2, 400, 160, 'ridge probe, team folds'),
                  ('a', 3, 760, 140, 'first author'), ('y', 4, 760, 192, 'year')],
                 [('s', 'p', 'h'), ('p', 'a', 'h'), ('p', 'y', 'h')])
    b += f
    spec = [('white', '…titled')] + [('true', w) for w in TRUE_T.split()] + [('white', '(2007)?')]
    row, cols = tok_row(spec, 70, 390, fs=15, name='true prompt')
    b.append(row)
    lt = [c for c in cols if c[2] == 'true'][-1]; cx = lt[0] + lt[1] / 2
    b.append(Group([Line(cx, 382, cx, 262, C['pen'], 6, round=True, op=.35), Circle(cx, 300, 8, C['ink']),
                    Text(cx + 14, 305, 'L40', 16, C['pen'])], 'title state'))
    g = [Circle(640 + (i % 6) * 22, 268 + (i // 6) * 22 + (i % 2) * 6, 6, C['ink']) for i in range(18)]
    b.append(Group(g, 'states of all papers'))
    b.append(Poly(qcurve((cx + 12, 298), (560, 260), (630, 280)), C['pen'], 2, arrow=True, dash=True))
    b.append(funnel(650, 350, 110, 80))
    b.append(Line(705, 436, 705, 470, C['ink'], 2.5, arrow=True))
    b.append(Group([tok(620, 476, 110, 34, 'name', 'first author', 16), tok(740, 476, 70, 34, 'white', 'year', 16)], 'answers'))
    b.append(Group([Text(880, 300, 'first author, L40', 18, C['pen']), Text(880, 330, '+0.061', 24, C['ink'], bold=True),
                    Text(880, 384, 'year R², L16 → L52', 18, C['pen']), Text(880, 414, '0.38 → 0.56', 24, C['ink'], bold=True)], 'probe numbers'))
    tcol = [C['true'], C['blue'], C['green'], C['purple'], C['red']]
    g = []
    fy = 552
    for k in range(5):
        x = 70 + k * 100
        g.append(Rect(x, fy, 92, 38, '#FFFFFF', C['ink'], 1.6, 6))
        for j in range(3):
            g.append(Rect(x + 10 + j * 26, fy + 11, 16, 16, tcol[k], C['ink'], 1, 2))
    b.append(Group(g, 'fold strip'))
    b.append(Text(70, fy + 62, 'colour = author team; one team, one fold', 16, C['pen']))
    b.append(formula_box(600, 560, 'spec = probe(true title) − probe(false title)', 25, sub='probe score = log10(1/rank) of the true first-author token'))
    SOURCES['probe'] = ['E4b title-specific probe score L40 +0.061 [0.047, 0.076] (author-team folds, train-fold standardised, all papers): 381_stage13/reports/e4b_trainstd_compare.md "Confirmatory configuration", row L40, column "new"',
                        'M2 year R² at the last title token L16 0.383 → L52 0.561: 381_stage13/reports/m2_teamci.md lines 46, 86',
                        'probe definition (5-fold ridge to the L63 ":" residual, gold ranked among cohort first tokens): STATUS.md Stage 11 E4b; stage10_extra_r0r1.py ~l.239']
    return b


# ================================================================== changing the question (M3 / X1)
X1 = [('L24', 0.991, 0.985, 0.992), ('L40', 0.921, 0.917, 0.915), ('L48', 0.424, 0.405, 0.417)]

def question():
    b = title('Changing the question', 'Coifman, Bonanno, Rafaeli (2007)')
    f, bx = flow([('q', 1, 70, 160, 'three questions'), ('m', 2, 330, 136, 'M3: compare states'),
                  ('x', 3, 330, 190, 'X1: copy into other title'), ('s', 4, 690, 190, 'score first author')],
                 [('q', 'm', 'h'), ('q', 'x', 'h'), ('x', 's', 'h')])
    b += f
    qs = [('authors', 'Authors:'), ('year', 'Year:'), ('field', 'Field:')]
    tx = 170; ys = [262, 312, 362]; dots = []
    for (lab, post), y in zip(qs, ys):
        g = [Text(tx - 10, y + 22, lab, 18, C['pen'], 'end')]
        x = tx
        for w in TRUE_T.split()[:3] + ['…', 'loss']:
            ww = tok_w(w, 15); g.append(tok(x, y, ww, 32, 'true', w, 15)); x += ww + 4
        g.append(Text(x + 6, y + 22, post, 17, C['pen']))
        dots.append((x - tok_w('loss', 15) / 2 - 4, y))
        b.append(Group(g, f'prompt {lab}'))
    dx = 640; g = []
    for (x, y), col in zip(dots, (C['ink'], C['blue'], C['green'])):
        g.append(Circle(dx, y + 16, 9, col)); g.append(Line(x + 60, y + 16, dx - 14, y + 16, C['pen'], 1.4, dash=True))
    g.append(Poly([(dx + 22, 274), (dx + 34, 274), (dx + 34, 382), (dx + 22, 382)], C['ink'], 2))
    g.append(Text(dx + 46, 334, 'no closer than at L4', 18, C['ink']))
    b.append(Group(g, 'M3 states'))
    y5 = 440
    g = [Text(tx - 10, y5 + 22, 'other', 18, C['pen'], 'end')]
    x = tx
    for w in ['Scholars', 'and', 'foreign', 'policy', '…']:
        ww = tok_w(w, 15); g.append(tok(x, y5, ww, 32, 'false', w, 15)); x += ww + 4
    g.append(Text(x + 6, y5 + 22, 'Authors:', 17, C['pen']))
    b.append(Group(g, 'partner prompt'))
    b.append(Poly(qcurve((dots[1][0] - 40, ys[1] + 34), (dots[1][0] + 40, 410), (x - 60, y5 - 6)), C['blue'], 3.5, arrow=True, name='copy arrow'))
    g = [Text(860, 286, 'R from', 17, C['pen'])]
    for j, h in enumerate(('authors', 'year', 'field')):
        g.append(Text(1000 + j * 90, 286, h, 16, C['pen'], 'middle'))
    for i, (L, a, yv, f_) in enumerate(X1):
        yy = 320 + i * 32
        g.append(Text(860, yy, L, 18, C['pen']))
        for j, v in enumerate((a, yv, f_)):
            g.append(Text(1000 + j * 90, yy, f'{v:.2f}', 20, C['ink'], 'middle', bold=True))
    b.append(Group(g, 'X1 table'))
    b.append(formula_box(70, 540, 'R(l) = (patched − other) ÷ (own − other)', 27, sub='title states copied at layer l; 582 test papers'))
    SOURCES['question'] = ['prompts (authors / year / field): ~/jlens_work/13_stage13/381_stage13.py TASKS lines 48–50',
                           'X1 R (test, n 582), source authors/year/field: L24 0.991/0.985/0.992, L40 0.921/0.917/0.915, L48 0.424/0.405/0.417: 381_stage13/reports/x1_report.md lines 15–18',
                           'other (partner) title "Scholars and foreign policy: varieties of research experience." (1966): 381_stage13/config/pairs.parquet; 351_all/351_all_papers.csv',
                           'M3: transfer and identity never above their L4 values: 381_stage13/reports/m3_report.md lines 12–19, 96–105']
    return b


# ================================================================== paraphrased title (X3)
def paraphrase():
    b = title('Paraphrased title (X3)', 'same paper in other words vs other paper, same words')
    f, bx = flow([('t', 1, 70, 160, 'three titles'), ('s', 2, 290, 160, 'states at last title token'),
                  ('d', 3, 640, 160, 'compare distances'), ('w', 4, 930, 160, 'word overlap')],
                 [('t', 's', 'h'), ('s', 'd', 'h')])
    b += f
    b.append(Poly(qcurve((bx['t'][0] + bx['t'][2] / 2, 204), (bx['t'][0] + 120, 236), (bx['w'][0] - 6, 212)), C['ink'], 2.5, arrow=True, name='branch arrow'))
    rows = [('original', 'Affect dynamics, bereavement and resilience to loss', 'true'),
            ('paraphrase', 'Affect fluctuations, grief and adaptability in the face of loss', 'true'),
            ('neighbour D', 'Affect and Resistance to Temptation.', 'false')]
    ys = [262, 316, 370]; ends = []
    for (lab, t, kind), y in zip(rows, ys):
        g = [Text(186, y + 22, lab, 18, C['ink'], 'end', bold=(lab == 'original'))]
        x = 200
        for w in t.split():
            ww = tok_w(w, 15); g.append(tok(x, y, ww, 32, kind, w, 15)); x += ww + 4
        ends.append((x - 4, y + 16))
        b.append(Group(g, f'title {lab} prompt'))
    pos = {'original': (720, 330), 'paraphrase': (760, 380), 'neighbour D': (850, 280)}
    g = []
    for (lab, _, kind), (ex, ey) in zip(rows, ends):
        cx, cy = pos[lab]
        g.append(Line(ex + 6, ey, cx - 12, cy, C['pen'], 1.2, dash=True))
    g.append(Line(*pos['original'], *pos['paraphrase'], C['true'], 3.5))
    g.append(Line(*pos['original'], *pos['neighbour D'], C['pen'], 3.5))
    for lab, (cx, cy) in pos.items():
        g.append(Circle(cx, cy, 9, C['true'] if lab != 'neighbour D' else C['false'], C['ink'], 1.5))
    b.append(Group(g, 'states'))
    vy = 330
    def venn(x, a_words, b_words, shared, lab_b, j2):
        g = [Circle(x, vy, 52, C['true'], C['ink'], 1.6, fill_op=.12), Circle(x + 64, vy, 52, C['true'] if lab_b == 'para' else C['false'], C['ink'], 1.6, fill_op=.25)]
        for k, w in enumerate(shared): g.append(Text(x + 32, vy - 4 + k * 20, w, 14, C['ink'], 'middle', bold=True))
        g.append(Text(x + 32, vy + 74, f'{lab_b} {j2:.2f}', 16, C['ink'], 'middle'))
        return Group(g, f'venn {lab_b}')
    b.append(venn(950, [], [], ['affect', 'loss'], 'para', 0.222))
    b.append(venn(950, [], [], ['affect'], 'D', 0.143)) if False else None
    b.append(Group([Circle(1110, 470, 40, C['true'], C['ink'], 1.6, fill_op=.12), Circle(1160, 470, 40, C['false'], C['ink'], 1.6, fill_op=.3),
                    Text(1135, 476, 'affect', 14, C['ink'], 'middle', bold=True), Text(1135, 534, 'D 0.14', 16, C['ink'], 'middle')], 'venn D'))
    b.append(Text(930, 590, 'medians: 0.61 vs 0.15', 18, C['pen']))
    b.append(formula_box(70, 470, "G′ = cos(orig, para) − cos(orig, D)", 27, sub='+0.32 at L8 · peak +0.46 at L36 (test set)'))
    b.append(Text(70, 600, 'first-author score, paraphrase − D: +0.239', 19, C['ink']))
    SOURCES['paraphrase'] = ['paraphrase "Affect fluctuations, grief and adaptability in the face of loss" (jaccard2 0.222, NLI both ways 0.998/0.999): 381_stage13/summary_x3/para_nli.csv; config/x3_lexical_neighbour_j2.csv (paper 28578a60…)',
                             'neighbour D "Affect and Resistance to Temptation." (P. Fry 1975; jaccard2 0.143): config/x3_lexical_neighbour_j2.csv; titles 351_all/351_all_papers.csv',
                             'median jaccard2 0.615 (paraphrase) vs 0.15 (D), primary set n = 1,115: x3_lexical_neighbour_j2.csv para_jaccard2 / lexical_jaccard2',
                             "G′ +0.316 at L8, peak +0.463 at L36; first-author score paraphrase − D +0.239 [0.212, 0.266]: 381_stage13/reports/x3_report.md Verdict (primary set, test)"]
    return b


# ================================================================== patchscope (X4)
def patchscope():
    b = title('Patchscope (X4)', 'Coifman, Bonanno, Rafaeli (2007)')
    f, bx = flow([('s', 1, 70, 160, 'state at last title token'), ('i', 2, 400, 160, 'inject at X'), ('o', 3, 600, 160, 'model answers'),
                  ('c', 4, 850, 160, 'self vs partner')],
                 [('s', 'i', 'h'), ('i', 'o', 'h'), ('o', 'c', 'h')])
    b += f
    spec = [('white', 'Who…titled')] + [('true', w) for w in TRUE_T.split()] + [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')]
    row, cols = tok_row(spec, 70, 330, fs=15, name='source prompt')
    b.append(row)
    lt = [c for c in cols if c[2] == 'true'][-1]; sx = lt[0] + lt[1] / 2
    b.append(Group([Line(sx, 322, sx, 236, C['pen'], 6, round=True, op=.35), Circle(sx, 266, 9, C['ink']), Text(sx + 14, 271, 'layer l', 16, C['blue'])], 'source state'))
    ty = 450
    spec2 = [('white', 'Paper:'), ('white', 'X'), ('white', 'The'), ('white', 'first'), ('white', 'author'), ('white', 'of'), ('white', 'the'), ('white', 'paper'), ('white', 'is')]
    row2, cols2 = tok_row(spec2, 300, ty, fs=16, h=34, name='target prompt')
    b.append(row2)
    xc = cols2[1]; xx = xc[0] + xc[1] / 2
    b.append(Rect(xc[0] - 3, ty - 3, xc[1] + 6, 40, None, C['blue'], 2.5, 6))
    b.append(Poly(qcurve((sx + 10, 270), (xx + 140, 330), (xx, ty - 8)), C['blue'], 4, arrow=True, name='inject arrow'))
    ex = cols2[-1][0] + cols2[-1][1] + 14
    b.append(Line(ex, ty + 17, ex + 40, ty + 17, C['ink'], 2.5, arrow=True))
    b.append(Group([tok(ex + 48, ty, 50, 34, 'name', 'Co', 16), tok(ex + 102, ty, 40, 34, 'name', 'if', 16), tok(ex + 146, ty, 50, 34, 'name', 'man', 16)], 'answer prompt'))
    b.append(Text(300, ty + 64, 'also: year · field prompts', 17, C['pen']))
    b.append(formula_box(70, 560, 'D = score(own state) − score(partner state)', 27, sub='score = log10(1/rank) of the true answer tokens'))
    b.append(Group([Text(820, 590, 'first author from L8: +0.046', 20, C['ink'], bold=True),
                    Text(820, 622, 'year from L40: +0.013', 20, C['ink'], bold=True)], 'X4 numbers'))
    SOURCES['patchscope'] = ['target prompts "Paper: X\\nThe first author of the paper is" / "…published in the year" / "Research field:": ~/jlens_work/13_stage13/381_stage13.py line 123 PS_TARGETS',
                             'source = authors-prompt residual at the last title token, injected at the same layer; D = mean score(self) − mean score(partner): 381_stage13.py lines 27–29, x4_report.md line 3',
                             'first author earliest L8 +0.046 [0.035, 0.059]; year earliest L40 +0.013 [0.008, 0.018]: 381_stage13/reports/x4_report.md lines 9, 11']
    return b


# ================================================================== group comparisons
DOSE = [0.170, 0.219, 0.256, 0.316, 0.463]
COMPARE_REAL_NUMBERS = True       # (user 2026-11-05 ~17:20: real numbers on) True puts the 391_groups results (P1, P2, dose curve) back on the page
SCHEMATIC_DOSE = [0.12, 0.17, 0.23, 0.30, 0.42]   # illustrative shape only, not data

def compare():
    b = title('Group comparisons', 'example paper: cell C')
    f, bx = flow([('c', 1, 70, 160, '9 cells'), ('p1', 2, 250, 136, 'P1: A − B'), ('p2', 3, 250, 190, 'P2: C − A'),
                  ('d', 4, 700, 160, 'dose: orders right')],
                 [('c', 'p1', 'h'), ('c', 'p2', 'h')])
    b += f
    gx, gy, cw, chh = 170, 316, 120, 62
    for j, c in enumerate(['strong', 'uncertain', 'fail']):
        b.append(Text(gx + j * cw + cw / 2, gy - 12, c, 17, C['pen'], 'middle'))
    for i, R in enumerate(('R0', 'R1', 'R2')):
        b.append(Text(gx - 14, gy + i * chh + chh / 2 + 4, R, 19, C['ink'], 'end', bold=True))
        for j, (lab, rec, n) in enumerate(CELLS[R]):
            fill = {'A': C['true'], 'C': C['true'], 'B': C['blue'], 'D': C['blue']}.get(lab, '#FFFFFF')
            op = .85 if lab in ('A', 'B', 'C') else (.35 if lab == 'D' else 1)
            g = [Rect(gx + j * cw, gy + i * chh, cw - 6, chh - 6, fill, C['ink'], 1.4, 6, fill_op=op)]
            g.append(Text(gx + j * cw + (cw - 6) / 2, gy + i * chh + chh / 2 + 3, (lab + ' ' if lab else '') + f'{n:,}', 18,
                          '#FFFFFF' if lab in ('A', 'B', 'C') else C['ink'], 'middle', bold=bool(lab)))
            b.append(Group(g, f'cell {R} {rec}'))
    ax = gx + (cw - 6) / 2; bxx = gx + 2 * cw + (cw - 6) / 2
    b.append(Poly(qcurve((ax, gy - 30), ((ax + bxx) / 2, gy - 62), (bxx, gy - 30)), C['ink'], 2.5, name='P1 arc'))
    b.append(Text((ax + bxx) / 2, gy - 50, 'P1', 18, C['ink'], 'middle', bold=True))
    b.append(Poly(qcurve((gx - 44, gy + 26), (gx - 90, gy + chh * 0.8), (gx - 44, gy + chh + 26)), C['ink'], 2.5, name='P2 arc'))
    b.append(Text(gx - 96, gy + chh * 0.8 + 6, 'P2', 18, C['ink'], 'end', bold=True))
    if COMPARE_REAL_NUMBERS:
        b.append(Group([Text(560, 314, 'P1', 19, C['ink'], bold=True), Text(600, 314, '+0.200 [0.188, 0.213]', 19, C['ink']),
                        Text(560, 352, 'P2', 19, C['ink'], bold=True), Text(600, 352, 'co-authors +0.061', 19, C['ink']),
                        Text(600, 380, 'first author +0.031 (ns)', 18, C['pen'])], 'P numbers'))
        b.append(chart(860, 280, 320, 200, [0, 1, 2, 3, 4], [(DOSE, C['true'], '')], 0, 0.5, xlab='orders right (R0)',
                       yticks=(0, 0.25, 0.5), xticks=[(k, str(k)) for k in range(5)], name='dose chart'))
        b.append(Text(866, 480 - DOSE[0] / 0.5 * 200 - 14, '0.17', 17, C['ink']))
        b.append(Text(1174, 480 - DOSE[4] / 0.5 * 200 - 14, '0.46', 17, C['ink'], 'end'))
    else:   # schematic placeholders only (user decision 2026-11-05: no post-defence results on this page)
        b.append(Group([Text(560, 314, 'P1', 19, C['ink'], bold=True), Text(600, 314, 'Δ₁', 22, C['ink'], bold=True),
                        Text(560, 352, 'P2', 19, C['ink'], bold=True), Text(600, 352, 'Δ₂', 22, C['ink'], bold=True),
                        ], 'P placeholders'))
        b.append(chart(860, 280, 320, 200, [0, 1, 2, 3, 4], [(SCHEMATIC_DOSE, C['pen'], '')], 0, 0.5, xlab='orders right (R0)',
                       yticks=(), xticks=[(k, str(k)) for k in range(5)], name='dose chart (schematic)'))
        b.append(Text(860, 540, 'schematic, not results · 示意，不是结果', 16, C['pen'], name='schematic note'))
    b.append(formula_box(70, 570, 'contrast = Σ w_b (mean_cell1 − mean_cell2)', 26, sub='title-specific signal, unwritten authors, output layer; team bootstrap'))
    if not COMPARE_REAL_NUMBERS:
        SOURCES['compare'] = ['cell counts: 351_stage10/cohort/papers.parquet (recall_level × mc_team_outcome_tight); P1/P2/dose shown as schematic placeholders only']
        return b
    SOURCES['compare'] = ['cell counts: 351_stage10/cohort/papers.parquet (recall_level × mc_team_outcome_tight)',
                          'P1 A − B +0.200 [0.188, 0.213]; P2 C − A co-authors +0.061 [0.034, 0.090], first author +0.031 [−0.006, 0.069] (Holm p 0.11): 391_groups/primary.csv (rows 0, 9, 5); within-bin weights groups_core.py:112',
                          'dose by multiple-choice orders right 0–4 (R0, unwritten authors, final L63): 0.170 / 0.219 / 0.256 / 0.316 / 0.463: 391_groups/stage10_curves.csv',
                          'NOTE: post-defence analysis (addenda 7–8), results so far sent to the user only']
    return b
