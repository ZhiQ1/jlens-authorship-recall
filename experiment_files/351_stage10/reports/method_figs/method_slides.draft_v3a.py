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
    b.append(Group([Text(1055, 628, '(patched − false) ÷', 17, C['pen']), Text(1055, 650, '(true − false)', 17, C['pen']),
                    Text(1055, 680, 'mean of 5 false titles,', 14, C['pen']), Text(1055, 698, '1,186 papers', 14, C['pen'])], 'formula'))
    return b


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
    b = title('Scoring: rank → log → spec', 'Coifman, Bonanno, Rafaeli (2007) · model output (L63)')
    y0, dy, th = 214, 50, 30
    xs_rank, cw = 556, 44
    b.append(step_label(1, 176, 186, '7 prompts, same name'))
    b.append(step_label(2, xs_rank + 13, 186, 'rank of each name token'))
    b.append(step_label(3, 912, 186, 'mean log10(1/rank)'))
    for k, (cond, ranks, m) in enumerate(SCORE_ROWS):
        y = y0 + k * dy
        kind = 'true' if cond == 'true' else ('false' if cond.startswith('false') else None)
        g = [Text(150, y + 22, cond, 19, C['ink'], 'end', bold=(cond == 'true'))]
        x = 164
        g.append(tok(x, y, 40, th, 'white')); x += 44
        nt = 7 if kind == 'true' else (9 if kind == 'false' else 0)
        for i in range(nt):
            g.append(tok(x, y, 13, th, kind)); x += 16
        if nt == 0:
            g.append(Text(x + 4, y + 21, '(no title)', 15, C['pen'])); x += 76
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
        g.append(Text(900, y + 22, f'{m:+.4f}'.replace('-', '−'), 20, C['true'] if cond == 'true' else C['ink'], bold=(cond == 'true')))
        b.append(Group(g, f'row {cond}'))
    # bracket for the 5 false rows
    yt, yb = y0 + dy + 4, y0 + 5 * dy + th - 4
    b.append(Group([Poly([(990, yt), (1002, yt), (1002, yb), (990, yb)], C['ink'], 2),
                    Line(1002, (yt + yb) / 2, 1022, (yt + yb) / 2, C['ink'], 2),
                    Text(1030, (yt + yb) / 2 - 4, 'mean false', 18, C['pen']),
                    Text(1030, (yt + yb) / 2 + 20, '−1.1126', 20, bold=True)], 'false mean'))
    b.append(Text(xs_rank, y0 + 7 * dy + 8, 'first author shown · mean over all 16 tokens', 15, C['pen']))
    # step 4: contrasts
    yb4 = 640
    b.append(step(4, 84, yb4))
    b.append(Group([Rect(108, yb4 - 26, 330, 52, '#FFFFFF', C['true'], 2.5, 10),
                    Text(124, yb4 + 8, 'spec = true − mean false = +0.3935', 19, C['ink'], bold=True)], 'spec box'))
    b.append(Text(462, yb4 + 8, 'total = true − delete = +0.1618', 19, C['ink']))
    b.append(Text(760, yb4 + 8, 'topic = mean false − delete = −0.2318', 19, C['ink']))
    SOURCES['scoring'] = ['ranks, mean_nlr per condition, false mean −1.1126, spec +0.3935, total +0.1618, topic −0.2318: '
                          'methods/parts/A_global1.html G5.5 (raw final/L63/shard_011.npz rows 25025–25040; '
                          'summary_title/paper_title_contrasts.parquet readout=final layer=63)']
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


# ================================================================== groups & samples (Sankey)
CELLS = {'R0': [('A', 'strong', 4110), ('U0', 'uncertain', 2002), ('B', 'fail', 2186)],
         'R1': [('C', 'strong', 511), ('', 'uncertain', 51), ('D', 'fail', 34)],
         'R2': [('', 'strong', 204), ('', 'uncertain', 9), ('', 'fail', 1)]}
RTOT = {'R0': 8298, 'R1': 596, 'R2': 214}

def groups():
    b = title('Groups and samples', '9,108 papers, two behavioural tests')
    sc = 400 / 9108; top = 210; gap1, gap2 = 22, 7
    x1, x2, x3, bw = 80, 330, 560, 22
    fillc = {'A': C['true'], 'C': C['true'], 'B': C['blue'], 'D': C['blue'], 'U0': C['false'], '': C['false']}
    b.append(Group([Rect(x1, top, bw, 9108 * sc, C['ink'], None), Text(x1 - 6, top + 9108 * sc / 2 - 8, '9,108', 20, C['ink'], 'end', bold=True),
                    Text(x1 - 6, top + 9108 * sc / 2 + 14, 'papers', 17, C['pen'], 'end')], 'all papers'))
    y_src, y2 = top, top
    # column 2 (recall) and column 3 (cells)
    y3 = top
    for R in ('R0', 'R1', 'R2'):
        hR = RTOT[R] * sc
        b.append(Poly(band(x1 + bw, y_src, y_src + hR, x2, y2, y2 + hR), None, fill=C['pen'], closed=True, fill_op=.18, name=f'band all→{R}'))
        b.append(Group([Rect(x2, y2, bw, max(hR, 3), C['ink']), Text(x2 + bw / 2, y2 - 6, R, 18, C['ink'], 'middle', bold=True)], f'node {R}'))
        ys = y2
        for lab, rec, n in CELLS[R]:
            h = max(n * sc, 2.5)
            hb = n * sc
            b.append(Poly(band(x2 + bw, ys, ys + hb, x3, y3, y3 + hb), None, fill=fillc[lab], closed=True, fill_op=.35, name=f'band {R}→{rec}'))
            b.append(Rect(x3, y3, bw, h, fillc[lab], C['ink'], 1))
            if R == 'R0':
                b.append(Text(x3 + bw + 10, y3 + h / 2 + 6, f'{lab} {n:,}' + ('' if lab != 'U0' else ''), 19, C['ink']))
                b.append(Text(x3 + bw + 110, y3 + h / 2 + 6, rec, 16, C['pen']))
            ys += hb; y3 += h + gap2
        y_src += hR; y2 += max(hR, 3) + gap1; y3 += gap1 - gap2
    # small cells: labels in one line each
    yR1 = top + RTOT['R0'] * sc + gap1 + 3 * gap2
    b.append(Text(x3 + bw + 10, yR1 + 8, 'C 511 · 51 · D 34', 19))
    b.append(Text(x3 + bw + 10, yR1 + 52, 'R2: 204 · 9 · 1', 19, C['pen']))
    b.append(step_label(1, x2 - 8, 182, 'open recall'))
    b.append(step_label(2, x3 - 8, 182, 'recognition'))
    # legend chips
    lx = 80; ly = 668
    for col, lab in ((C['true'], 'target = A + C'), (C['blue'], 'control = B + D'), (C['false'], 'not used in contrasts')):
        b.append(Group([Rect(lx, ly - 15, 22, 18, col, C['ink'], 1, 3), Text(lx + 30, ly, lab, 17)], f'legend {lab}'))
        lx += 52 + text_w(lab, 17) + 20
    # right: who samples which cells
    rx = 880
    b.append(step_label(3, rx + 12, 182, 'who uses which cells'))
    rows = [('Stage 10 · M2 · M3', 'all 9,108 papers', [C['true'], C['blue'], C['false']]),
            ('Stages 11–13 · X-series', '593 target + 593 control', [C['true'], C['blue']]),
            ('', '1,178 matched pairs (X)', []),
            ('Stages 1–9', 'Pilot50 · Stage 8: 200 (A, B)', [C['true'], C['blue']])]
    yy = 236
    for head, txt, cols in rows:
        g = []
        if head:
            g.append(Text(rx, yy, head, 21, C['ink'], bold=True)); yy += 30
        cx = rx
        for c in cols:
            g.append(Rect(cx, yy - 15, 16, 16, c, C['ink'], 1, 3)); cx += 20
        g.append(Text(cx + (6 if cols else 0), yy, txt, 18, C['ink'])); yy += 46 if head or not cols else 46
        b.append(Group(g, f'sample {txt}'))
    SOURCES['groups'] = ['9,108; R0/R1/R2 8,298/596/214; cells 4,110/2,002/2,186, 511/51/34, 204/9/1: 351_stage10/cohort/papers.parquet recall_level × mc_team_outcome_tight',
                         'target 4,621 = A + C, control 2,220 = B + D: papers.parquet group_tight',
                         '593 + 593 = 1,186: 361_stage11/config/sample.parquet (361_stage11.py:56, 109–115); 1,178 pairs: 381_stage13/config/pairs.parquet',
                         'Pilot50 / Stage 8 200 papers from A and B: 351_stage8/config/analysis_plan.json groups; deck slide 5 (Stage 1)']
    return b


# ================================================================== statistical conventions
BINS = [('0-2', 200, 352), ('3-4', 207, 355), ('5-8', 237, 332), ('9-16', 288, 275), ('17-32', 327, 234), ('33-64', 401, 185),
        ('65-128', 441, 165), ('129-256', 497, 126), ('257-512', 533, 105), ('513-1024', 603, 53), ('1025-2048', 539, 29),
        ('2049-4096', 264, 9), ('4097+', 84, 0)]

def stats():
    b = title('Statistical conventions', 'compare within citation bins · resample whole teams')
    x0, yb, bw, gp, sc = 80, 470, 46, 8, 0.33
    b.append(step_label(1, 92, 188, 'citation bins'))
    for i, (lab, nt, nc) in enumerate(BINS):
        x = x0 + i * (bw + gp); used = nt >= 30 and nc >= 30
        g = [Rect(x, yb - 210, bw, 210, '#FFFFFF' if used else C['faint'], C['ink'] if used else C['cell'], 1.4, 6, dash=not used)]
        g.append(Rect(x + 6, yb - nt * sc, 15, nt * sc, C['true'], None))
        g.append(Rect(x + 25, yb - nc * sc, 15, max(nc * sc, 0.5), C['blue'], None))
        g.append(Text(x + bw / 2, yb + 18, lab, 13, C['ink'] if used else C['pen'], 'middle'))
        if lab == '65-128':
            g.append(Text(x + bw / 2, yb - 222, 'example', 13, C['true'], 'middle'))
            g.append(Rect(x - 3, yb - 213, bw + 6, 216, None, C['true'], 2.5, 8))
        b.append(Group(g, f'bin {lab}'))
    xd = x0 + 10 * (bw + gp) - 4
    b.append(Text(xd + 1.5 * (bw + gp), yb + 40, 'fewer than 30: dropped', 14, C['pen'], 'middle'))
    b.append(Group([Rect(x0, yb + 32, 14, 12, C['true']), Text(x0 + 20, yb + 43, 'target', 15),
                    Rect(x0 + 78, yb + 32, 14, 12, C['blue']), Text(x0 + 98, yb + 43, 'control', 15)], 'bin legend'))
    b.append(step_label(2, 92, yb + 86, 'target − control in each bin'))
    b.append(step_label(3, 92, yb + 136, 'merge bins, weight', fs=20))
    b.append(Text(310, yb + 143, 'w ∝ nₜ·n꜀ / (nₜ + n꜀)', 22, C['ink'], bold=True))
    # teams
    rx = 860
    b.append(step_label(4, rx + 12, 188, 'teams'))
    papers = [(890, 250, 0), (950, 236, 0), (925, 300, 0), (1040, 246, 1), (1100, 290, 1), (1180, 240, 2), (1215, 300, 2), (1160, 330, 2), (1010, 340, 3)]
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
    b.append(Text(rx, 400, 'shared author name → one team', 18, C['pen']))
    b.append(Text(rx, 430, '7,247 teams · 9,108 papers', 20, C['ink'], bold=True))
    b.append(step_label(5, rx + 12, 486, 'resample whole teams'))
    # fold strip: 5 folds, squares coloured by team
    fx, fy = rx, 520
    folds = [[0, 0, 0, 3], [1, 1, 2], [2, 2, 3], [0, 1], [3, 2]]
    folds = [[0, 0, 0], [1, 1], [2, 2, 2], [3], []]
    g = []
    for f in range(5):
        x = fx + f * 76
        g.append(Rect(x, fy, 70, 44, '#FFFFFF', C['ink'], 1.6, 6))
        for k, t in enumerate(folds[f]):
            g.append(Rect(x + 8 + k * 19, fy + 14, 15, 15, tcol[t], C['ink'], 1, 2))
        g.append(Text(x + 35, fy + 64, f'fold {f + 1}', 14, C['pen'], 'middle'))
    b.append(Group(g, 'fold strip'))
    b.append(Text(rx, fy + 100, 'one team = one fold', 18, C['pen']))
    SOURCES['stats'] = ['bin counts target/control (group_tight × citation_bin): 351_stage10/cohort/papers.parquet; ≥ 30 per group rule MIN_STRATUM: 351_stage10.py:642',
                        'w_b = n_t·n_c/(n_t+n_c): 351_stage10.py stratified_diff :670–680 (also stage11_analyze.py:33–38, stage13_cluster_ci.py:45, 14_groups/groups_core.py:112)',
                        '7,247 teams over 9,108 papers: 381_stage13/reports/cluster_ci.md line 3; team rule stage13_cpu.py group_folds :109–123']
    return b


# ================================================================== Stage 8 independent replication
def replication():
    b = title('Independent replication (Stage 8)', 'plan first, data second')
    y = 330
    b.append(Line(90, y, 1190, y, C['ink'], 3, arrow=True, name='time axis'))
    pts = [(170, 1, 'lock the plan', '10-18 14:29'), (450, 2, '200 new papers', '100 A/B pairs'),
           (730, 3, 'score', '10-18 21:47 → 10-20'), (1010, 4, 'check vs plan', '')]
    for x, n, lab, sub in pts:
        g = [Circle(x, y, 9, C['ink']), step(n, x, y - 120), Text(x, y - 80, lab, 22, C['ink'], 'middle', bold=True)]
        if sub: g.append(Text(x, y + 34, sub, 18, C['pen'], 'middle'))
        b.append(Group(g, f'event {lab}'))
    b.append(padlock(160, y - 52, 1.0))
    b.append(Group([Rect(115, y + 54, 110, 30, '#FFFFFF', C['ink'], 1.4, 4), Text(170, y + 75, 'analysis_plan', 15, C['ink'], 'middle')], 'plan file'))
    # 200 papers as small squares
    g = []
    for i in range(50):
        g.append(Rect(390 + (i % 10) * 12, y + 54 + (i // 10) * 12, 9, 9, C['true'] if i % 2 == 0 else C['blue'], None))
    b.append(Group(g, 'papers'))
    b.append(Text(450, y + 132, '¼ shown', 14, C['pen'], 'middle'))
    b.append(Text(588, y - 40, 'L56 primary: 10-18 21:14', 15, C['pen'], 'middle'))
    # results
    def ci_row(yy, lab, est, lo, hi, col):
        X = lambda v: 760 + v * 52
        return Group([Text(740, yy + 6, lab, 18, C['ink'], 'end'),
                      Line(X(lo), yy, X(hi), yy, col, 4, round=True), Circle(X(est), yy, 8, col),
                      Text(X(hi) + 12, yy + 6, f'+{est:.2f} pp [{lo:.2f}, {hi:.2f}]', 18, C['ink'])], f'result {lab}')
    b.append(Group([Line(760, 470, 760, 600, C['pen'], 1.5, dash=True), Text(760, 622, '0', 15, C['pen'], 'middle')], 'zero line'))
    b.append(ci_row(505, 'L56 win rate (RQ1)', 5.18, 2.93, 7.48, C['true']))
    b.append(ci_row(565, 'frozen endpoint (7 layers)', 2.33, 1.50, 3.19, C['ink']))
    SOURCES['replication'] = ['plan locked 2026-10-18 14:29 (FROZEN_BEFORE_STAGE8_SCORING): 351_stage8/config/analysis_plan.json mtime; L56 primary 21:14: 08_stage8/351_stage8_PROTOCOL.md (handbook C_stage1_9 s19-s8-protocol)',
                              '200 new papers = 100 A/B pairs: handbook s19-s8a; scoring 10-18 21:47 → 10-20 09:05: s19-s8c',
                              'RQ1 L56 +5.18 pp [2.93, 7.48]: s19-s8d, 351_stage8/stage8D/summary/primary_questions.csv; frozen endpoint +2.33 pp [1.50, 3.19]: s19-s8dsupp, 351_stage8/recompute_2026-10-30/s8_endpoints.csv']
    return b


# ================================================================== layer-by-layer readout (real ranks)
CO_RANK = [(24, 37675), (40, 3979), (48, 44676), (56, 120750), (60, 23169), (61, 9811), (62, 120), (63, 61)]
LAYERS_R = [24, 32, 40, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]
MEAN_T = [-4.2483, -4.2929, -3.9605, -4.4742, -4.3159, -4.3900, -4.1552, -4.0890, -4.0522, -4.1588, -4.0651, -3.9333, -3.9181, -3.4255, -3.3573, -2.6339, -1.1108, -0.7719]
MEAN_F = [-4.2501, -4.1322, -3.6768, -4.3793, -4.2211, -4.3558, -4.1422, -4.0584, -3.9732, -4.2638, -4.1228, -3.9704, -3.9457, -3.6793, -3.6491, -3.3500, -2.1774, -1.1939]

def readout():
    b = title('Layer-by-layer readout', 'Coifman, Bonanno, Rafaeli (2007) · logit lens')
    # prompt row at the bottom
    spec = ([('white', '…titled')] + [('true', w) for w in TRUE_T.split()[:2]] + [('true', '…')] +
            [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')] + [('name', t) for t in NAME])
    row, cols = tok_row(spec, 80, 636, fs=15, name='true prompt')
    b.append(row)
    co = [c for c in cols if c[3] == 'Co'][0]; cx = co[0] + co[1] / 2
    b.append(step_label(1, 92, 610, 'true-title prompt'))
    # layer column above " Co"
    ytop, ybot = 196, 590
    Y = lambda L: ybot - (L - 20) / (63 - 20) * (ybot - ytop)
    g = [Line(cx, ybot, cx, ytop - 10, C['pen'], 6, round=True, op=.35)]
    for L, r in CO_RANK:
        y = Y(L)
        g.append(Circle(cx, y, 6, C['ink']))
        g.append(Text(cx - 34, y + 6, f'L{L}' if L < 63 else 'out', 16, C['pen'], 'end'))
        g.append(Group([Rect(cx + 50, y - 13, 86, 26, C['name'] if r <= 100 else '#FFFFFF', C['ink'], 1.2, 4),
                        Text(cx + 93, y + 6, f'{r:,}', 16, C['ink'], 'middle')], f'rank L{L}'))
    b.append(Group(g, 'Co layers'))
    b.append(magnifier(cx + 22, Y(62) - 4, 9))
    b.append(step_label(2, cx - 120, 184, 'lens at each layer'))
    b.append(step_label(3, cx + 64, 160, 'rank of “Co”'))
    # chart: mean log10(1/rank) of the 7 first-author tokens
    b.append(step_label(4, 820, 184, 'all 7 name tokens'))
    b.append(chart(840, 240, 340, 300, LAYERS_R, [(MEAN_F, C['pen'], 'false_0'), (MEAN_T, C['true'], 'true')], -5, 0,
                   xlab='layer', ylab='mean log10(1/rank)', yticks=(-4, -2, 0),
                   xticks=[(24, 'L24'), (40, 'L40'), (48, 'L48'), (56, 'L56'), (63, 'out')], name='mean chart'))
    SOURCES['readout'] = ['ranks of " Co" (row 25029) and of the 7 first-author tokens, logit lens L24–L62 + final L63, true and false_0: '
                          '351_stage10/raw/logit/L*/shard_011.npz, raw/final/L63/shard_011.npz, raw/cond_false_0/... (rows 25025–25031 by row_id; layout 351_stage10.py:548–577)',
                          'means are the mean of log10(1/rank) over these 7 tokens (computed for the slide)']
    return b


# ================================================================== knockout (block) + X7
X7_S = [(0, 1.004), (24, 0.873), (32, 0.558), (40, 0.293), (48, 0.143), (52, 0.029)]

def knockout():
    b = title('Knockout (block attention)', 'Coifman, Bonanno, Rafaeli (2007)')
    spec = ([('white', '…titled')] + [('true', w) for w in TRUE_T.split()] +
            [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')] + [('name', t) for t in NAME[:3]] + [('name', '…')])
    row, cols = tok_row(spec, 80, 560, fs=15, name='true prompt')
    tcols = [c for c in cols if c[2] == 'true']; tail = cols[len(tcols) + 1:]
    # layer band above the prompt: blocked from l upward
    yl = 330
    b.append(Group([Rect(80, 196, cols[-1][0] + cols[-1][1] - 80, yl - 196, C['red'], None, fill_op=.08),
                    Line(80, yl, cols[-1][0] + cols[-1][1] + 10, yl, C['red'], 1.8, dash=True),
                    Text(cols[-1][0] + cols[-1][1] + 16, yl + 6, 'layer l', 18, C['red']),
                    Text(cols[-1][0] + cols[-1][1] + 16, 220, 'blocked', 17, C['red'])], 'blocked band'))
    # attention arcs from the tail to title words
    g = []
    for k, (x, w, kk, lab) in enumerate(tail[::3]):
        sx = x + w / 2
        for (tx, tw, _, _) in tcols[1::3]:
            ex = tx + tw / 2
            g.append(Poly(qcurve((sx, 552), ((sx + ex) / 2, 420 - (sx - ex) * 0.12), (ex, 552)), C['pen'], 1.8, dash=True))
    b.append(Group(g, 'attention to title'))
    b.append(cross((tcols[-1][0] + tail[0][0]) / 2 + 30, 440, 13))
    b.append(row)
    b.append(step_label(1, 92, 640, 'block tail → title from l up: T'))
    b.append(step_label(2, 500, 640, 'same on false title: F'))
    b.append(step_label(3, 860, 186, 'S = T − F'))
    # bar chart of S
    x0, y0, h = 880, 560, 300
    g = [Line(x0 - 10, y0, x0 + 6 * 56, y0, C['ink'], 2), Line(x0 - 10, y0, x0 - 10, y0 - h - 10, C['ink'], 2),
         Text(x0 - 16, y0 - h + 5, '1', 15, C['pen'], 'end'), Text(x0 - 16, y0 + 5, '0', 15, C['pen'], 'end'),
         Line(x0 - 16, y0 - h, x0 - 10, y0 - h, C['ink'], 1.6)]
    for i, (L, s) in enumerate(X7_S):
        x = x0 + i * 56
        g.append(Rect(x, y0 - s * h, 38, s * h, C['red'], C['ink'], 1.2, 2, fill_op=.75))
        g.append(Text(x + 19, y0 - s * h - 8, f'{s:.2f}', 15, C['ink'], 'middle'))
        g.append(Text(x + 19, y0 + 20, f'L{L}', 15, C['pen'], 'middle'))
    g.append(Text(x0 + 160, y0 + 46, 'block from layer', 15, C['pen'], 'middle'))
    b.append(Group(g, 'S chart'))
    b.append(Text(880, 650, 'L52: target 0.018 · control 0.051', 17, C['ink']))
    SOURCES['knockout'] = ['S = T − F (fraction of the true − false gap) L0 1.004, L24 0.873, L32 0.558, L40 0.293, L48 0.143, L52 0.029 (target 0.018, control 0.051): 381_stage13/reports/x7_report.md lines 20/37/48–54',
                           'blocked = every position after the title cannot attend to the title tokens from layer l up: 381_stage13/config/prereg_addendum3.json X7; 361_stage11/reports/stage11_report.md E2']
    return b


# ================================================================== probe
def probe():
    b = title('Probe', 'read a property straight from the state')
    spec = [('white', '…titled')] + [('true', w) for w in TRUE_T.split()] + [('white', '(2007)?')]
    row, cols = tok_row(spec, 80, 300, fs=15, name='true prompt')
    b.append(row)
    lt = [c for c in cols if c[2] == 'true'][-1]; cx = lt[0] + lt[1] / 2
    b.append(Group([Line(cx, 292, cx, 196, C['pen'], 6, round=True, op=.35), Circle(cx, 236, 8, C['ink']),
                    Text(cx + 14, 241, 'L40', 16, C['pen'])], 'title state'))
    b.append(step_label(1, 92, 362, 'state at the last title token'))
    # many papers' dots into funnel
    g = [Circle(700 + (i % 6) * 22, 210 + (i // 6) * 22 + (i % 2) * 6, 6, C['ink']) for i in range(18)]
    b.append(Group(g, 'states of all papers'))
    b.append(Poly(qcurve((cx + 10, 236), (500, 190), (690, 226)), C['pen'], 2, arrow=True, dash=True))
    b.append(funnel(714, 300, 110, 80))
    b.append(step_label(2, 860, 312, 'ridge probe, 5 folds'))
    b.append(Line(769, 386, 769, 430, C['ink'], 2.5, arrow=True))
    # answers
    b.append(Group([tok(650, 440, 110, 34, 'name', 'first author', 16), tok(780, 440, 70, 34, 'white', 'year', 16)], 'answers'))
    b.append(step_label(3, 880, 457, 'score the answer'))
    b.append(Group([Text(650, 512, 'author, true − false title, L40:', 18, C['pen']), Text(1010, 512, '+0.061', 20, C['ink'], bold=True),
                    Text(650, 542, 'year R², L16 → L52:', 18, C['pen']), Text(1010, 542, '0.38 → 0.56', 20, C['ink'], bold=True)], 'probe numbers'))
    # fold strip
    tcol = [C['true'], C['blue'], C['green'], C['purple'], C['red']]
    g = []
    fy = 600
    for f in range(5):
        x = 80 + f * 104
        g.append(Rect(x, fy, 96, 40, '#FFFFFF', C['ink'], 1.6, 6))
        for k in range(4):
            g.append(Rect(x + 8 + k * 21, fy + 12, 16, 16, tcol[(f + (k // 2) * 2) % 5] if k < 3 else tcol[f], C['ink'], 1, 2))
    b.append(Group(g, 'fold strip'))
    b.append(Text(80, fy + 66, 'colour = author team; a team never spans two folds', 16, C['pen']))
    SOURCES['probe'] = ['E4b title-specific probe score L40 +0.061 [0.047, 0.076] (team folds, train-fold standardised, all papers): 381_stage13/reports/e4b_trainstd_compare.md "Confirmatory configuration", row L40 "new"',
                        'M2 year R² at the last title token L16 0.383 → L52 0.561: 381_stage13/reports/m2_teamci.md lines 46/86',
                        '5 folds by author team (7,247 teams): m3_report.md line 3, fold_audit.md line 45, cluster_ci.md line 3']
    return b


# ================================================================== changing the question (M3 / X1)
X1 = [('L24', 0.991, 0.985, 0.992), ('L40', 0.921, 0.917, 0.915), ('L48', 0.424, 0.405, 0.417)]

def question():
    b = title('Changing the question', 'same title, three questions')
    qs = [('Who are the authors of the paper titled', 'Authors:'), ('In what year was the research paper titled', 'published? Year:'),
          ('In what research field is the paper titled', 'Field:')]
    tx = 560; ys = [214, 284, 354]
    dots = []
    for (pre, post), y in zip(qs, ys):
        g = [Text(tx - 10, y + 22, pre, 17, C['pen'], 'end')]
        x = tx
        for w in TRUE_T.split()[:3] + ['…', 'loss']:
            ww = tok_w(w, 15); g.append(tok(x, y, ww, 32, 'true', w, 15)); x += ww + 4
        g.append(Text(x + 6, y + 22, post, 17, C['pen']))
        dots.append((x - tok_w('loss', 15) / 2 - 4, y))
        b.append(Group(g, f'prompt {post}'))
    b.append(step_label(1, 92, 186, 'three questions'))
    # dots and M3 comparison bracket
    dx = 1060
    g = []
    for (x, y), col in zip(dots, (C['ink'], C['blue'], C['green'])):
        g.append(Line(x, y + 2, x, y - 12, C['pen'], 1.5)); g.append(Circle(dx, y + 16, 9, col))
        g.append(Line(x + 20, y + 16, dx - 14, y + 16, C['pen'], 1.4, dash=True))
    g.append(Poly([(dx + 22, 226), (dx + 34, 226), (dx + 34, 374), (dx + 22, 374)], C['ink'], 2))
    b.append(Group(g, 'title states'))
    b.append(step_label(2, dx + 64, 290, 'compare', fs=19))
    b.append(Text(dx - 20, 412, 'M3: no closer than at L4', 17, C['ink']))
    # X1: copy year-question title state into authors run with another title
    y5 = 480
    b.append(step_label(3, 92, y5 - 20, 'X1: copy title states into a run with another title'))
    g = [Text(tx - 10, y5 + 52, "authors question, partner's title", 17, C['pen'], 'end')]
    x = tx
    for w in ['Scholars', 'and', 'foreign', 'policy', '…']:
        ww = tok_w(w, 15); g.append(tok(x, y5 + 30, ww, 32, 'false', w, 15)); x += ww + 4
    g.append(Text(x + 6, y5 + 52, 'Authors:', 17, C['pen']))
    b.append(Group(g, 'corrupt prompt'))
    b.append(Poly(qcurve((dx, ys[1] + 28), (dx + 120, 440), (x - 30, y5 + 24)), C['blue'], 3.5, arrow=True, name='copy arrow'))
    b.append(Text(dx + 76, 470, 'any question', 16, C['blue']))
    # recovery table
    g = [Text(640, 610, 'R', 18, C['ink'], bold=True)]
    for j, h in enumerate(('from authors', 'year', 'field')):
        g.append(Text(760 + j * 120, 610, h, 16, C['pen'], 'middle'))
    for i, (L, a, yv, f) in enumerate(X1):
        yy = 640 + i * 26
        g.append(Text(640, yy, L, 17, C['pen']))
        for j, v in enumerate((a, yv, f)):
            g.append(Text(760 + j * 120, yy, f'{v:.2f}', 18, C['ink'], 'middle'))
    b.append(Group(g, 'X1 table'))
    b.append(step_label(4, 92, 640, "score A's first author", fs=19))
    SOURCES['question'] = ['prompts: ~/jlens_work/13_stage13/381_stage13.py TASKS lines 48–50',
                           'X1 R (test, n 582) from authors/year/field: L24 0.991/0.985/0.992, L40 0.921/0.917/0.915, L48 0.424/0.405/0.417: 381_stage13/reports/x1_report.md lines 15–18',
                           'partner title "Scholars and foreign policy: varieties of research experience." (1966): 381_stage13/config/pairs.parquet partner; 351_all/351_all_papers.csv',
                           'M3 transfer/identity never above L4: 381_stage13/reports/m3_report.md lines 12–19, 96–105']
    return b


# ================================================================== paraphrased title (X3)
def paraphrase():
    b = title('Paraphrased title (X3)', 'same paper in other words vs other paper, same words')
    rows = [('original', 'Affect dynamics, bereavement and resilience to loss', 'true'),
            ('paraphrase', 'Affect fluctuations, grief and adaptability in the face of loss', 'true'),
            ('neighbour D', 'Affect and Resistance to Temptation.', 'false')]
    ys = [200, 270, 340]; ends = []
    for (lab, t, kind), y in zip(rows, ys):
        g = [Text(196, y + 22, lab, 19, C['ink'], 'end', bold=(lab == 'original'))]
        x = 210
        for w in t.split():
            ww = tok_w(w, 15); g.append(tok(x, y, ww, 32, kind if lab != 'paraphrase' else 'true', w, 15)); x += ww + 4
        ends.append((x - 4, y + 16))
        b.append(Group(g, f'title {lab}'))
    b.append(step_label(1, 92, 175, 'three titles, same question'))
    # dots and distances
    px = 860
    pos = {'original': (px, 260), 'paraphrase': (px + 60, 300), 'neighbour D': (px + 150, 210)}
    g = []
    for (lab, _, kind), (ex, ey) in zip(rows, ends):
        cx, cy = pos[lab]
        g.append(Line(ex + 6, ey, cx - 12, cy, C['pen'], 1.2, dash=True))
    g.append(Line(*pos['original'], *pos['paraphrase'], C['true'], 3.5))
    g.append(Line(*pos['original'], *pos['neighbour D'], C['pen'], 3.5))
    for lab, (cx, cy) in pos.items():
        g.append(Circle(cx, cy, 9, C['true'] if lab != 'neighbour D' else C['false'], C['ink'], 1.5))
    b.append(Group(g, 'states'))
    b.append(step_label(2, 1050, 300, 'distances', fs=19))
    b.append(Text(860, 360, "closer to its paraphrase: +0.32 (L8)", 17, C['ink']))
    # Venn of words
    vy = 520
    b.append(step_label(3, 92, 440, 'word overlap'))
    def venn(x, a_words, b_words, shared, lab_b, j2):
        g = [Circle(x, vy, 70, C['true'], C['ink'], 1.6, fill_op=.15), Circle(x + 90, vy, 70, C['true'] if lab_b == 'paraphrase' else C['false'], C['ink'], 1.6, fill_op=.25)]
        for k, w in enumerate(a_words): g.append(Text(x - 30, vy - 28 + k * 20, w, 14, C['ink'], 'middle'))
        for k, w in enumerate(shared): g.append(Text(x + 45, vy - 10 + k * 22, w, 15, C['ink'], 'middle', bold=True))
        for k, w in enumerate(b_words): g.append(Text(x + 122, vy - 38 + k * 20, w, 14, C['ink'], 'middle'))
        g.append(Text(x + 45, vy + 96, f'{lab_b}: {j2:.2f}', 17, C['ink'], 'middle'))
        return Group(g, f'venn {lab_b}')
    b.append(venn(200, ['dynamic', 'bereave', 'resilien'], ['fluctua', 'grief', 'adapt', 'face'], ['affect', 'loss'], 'paraphrase', 0.222))
    b.append(venn(560, ['dynamic', 'bereave', 'resilien', 'loss'], ['resist', 'temptat'], ['affect'], 'neighbour D', 0.143))
    b.append(Group([Text(860, 480, 'median overlap, 1,115 papers', 17, C['pen']), Text(860, 512, 'paraphrase 0.61 · D 0.15', 20, C['ink'], bold=True),
                    Text(860, 580, 'first-author score,', 17, C['pen']), Text(860, 608, 'paraphrase − D: +0.239', 20, C['ink'], bold=True)], 'X3 numbers'))
    SOURCES['paraphrase'] = ['paraphrase "Affect fluctuations, grief and adaptability in the face of loss" (jaccard2 0.222): 381_stage13/summary_x3/para_nli.csv + config/x3_lexical_neighbour_j2.csv (paper 28578a60…)',
                             'neighbour D "Affect and Resistance to Temptation." (1975, jaccard2 0.143): config/x3_lexical_neighbour_j2.csv; titles 351_all/351_all_papers.csv',
                             'medians 0.615 / 0.15 over the primary set n = 1,115: x3_lexical_neighbour_j2.csv para_jaccard2 / lexical_jaccard2',
                             "G' = cos(orig, para) − cos(orig, D) at the last title token +0.316 at L8; first-author score paraphrase − D +0.239 [0.212, 0.266]: 381_stage13/reports/x3_report.md Verdict",
                             'Venn words = jaccard2 tokens (stop words removed, light stemming; prereg_addendum5.json word_overlap); stems shortened on the slide']
    return b


# ================================================================== patchscope (X4)
def patchscope():
    b = title('Patchscope (X4)', 'move one state into an empty slot, let the model talk')
    spec = [('white', 'Who…titled')] + [('true', w) for w in TRUE_T.split()] + [('white', '(2007)?'), ('white', 'Authors'), ('white', ':')]
    row, cols = tok_row(spec, 80, 300, fs=15, name='source prompt')
    b.append(row)
    lt = [c for c in cols if c[2] == 'true'][-1]; sx = lt[0] + lt[1] / 2
    b.append(Group([Line(sx, 292, sx, 196, C['pen'], 6, round=True, op=.35), Circle(sx, 236, 9, C['ink']), Text(sx + 14, 241, 'layer l', 16, C['blue'])], 'source state'))
    b.append(step_label(1, 92, 362, 'state at the last title token'))
    # target prompts
    ty = 470
    spec2 = [('white', 'Paper:'), ('white', 'X'), ('white', 'The'), ('white', 'first'), ('white', 'author'), ('white', 'of'), ('white', 'the'), ('white', 'paper'), ('white', 'is')]
    row2, cols2 = tok_row(spec2, 300, ty, fs=16, h=34, name='target prompt')
    b.append(row2)
    xc = cols2[1]; xx = xc[0] + xc[1] / 2
    b.append(Rect(xc[0] - 3, ty - 3, xc[1] + 6, 40, None, C['blue'], 2.5, 6))
    b.append(Poly(qcurve((sx + 10, 240), (xx + 120, 300), (xx, ty - 8)), C['blue'], 4, arrow=True, name='inject arrow'))
    b.append(step_label(2, 92, ty + 17, 'inject at X, same layer'))
    ex = cols2[-1][0] + cols2[-1][1] + 14
    b.append(Line(ex, ty + 17, ex + 40, ty + 17, C['ink'], 2.5, arrow=True))
    b.append(Group([tok(ex + 48, ty, 50, 34, 'name', 'Co', 16), tok(ex + 102, ty, 40, 34, 'name', 'if', 16), tok(ex + 146, ty, 50, 34, 'name', 'man', 16)], 'answer prompt'))
    b.append(step_label(3, ex + 64, ty - 36, 'score', fs=19))
    b.append(Text(300, ty + 70, 'also: "…published in the year" · "Research field:"', 16, C['pen']))
    # numbers
    b.append(step_label(4, 92, 620, 'self − partner title'))
    b.append(Group([Text(380, 628, 'first author from L8: +0.046', 20, C['ink'], bold=True), Text(720, 628, 'year from L40: +0.013', 20, C['ink'], bold=True)], 'X4 numbers'))
    SOURCES['patchscope'] = ['target prompts "Paper: X\\nThe first author of the paper is" / "…published in the year" / "Research field:": 381_stage13.py line 123 PS_TARGETS',
                             'first author earliest L8 +0.046 [0.035, 0.059]; year earliest L40 +0.013 [0.008, 0.018] (D = self − partner): 381_stage13/reports/x4_report.md lines 9, 11']
    return b


# ================================================================== group comparisons
DOSE = [0.170, 0.219, 0.256, 0.316, 0.463]

def compare():
    b = title('Group comparisons', 'which cells are compared')
    gx, gy, cw, chh = 210, 220, 130, 74
    cols = ['strong', 'uncertain', 'fail']
    for j, c in enumerate(cols):
        b.append(Text(gx + j * cw + cw / 2, gy - 14, c, 18, C['pen'], 'middle'))
    for i, R in enumerate(('R0', 'R1', 'R2')):
        b.append(Text(gx - 16, gy + i * chh + chh / 2 + 7, R, 20, C['ink'], 'end', bold=True))
        for j, (lab, rec, n) in enumerate(CELLS[R]):
            fill = {'A': C['true'], 'C': C['true'], 'B': C['blue'], 'D': C['blue']}.get(lab, '#FFFFFF')
            op = .85 if lab in ('A', 'B', 'C') else (.35 if lab == 'D' else 1)
            g = [Rect(gx + j * cw, gy + i * chh, cw - 6, chh - 6, fill, C['ink'], 1.4, 6, fill_op=op)]
            g.append(Text(gx + j * cw + (cw - 6) / 2, gy + i * chh + chh / 2 + 2, (lab + ' ' if lab else '') + f'{n:,}', 19,
                          '#FFFFFF' if lab in ('A', 'B', 'C') else C['ink'], 'middle', bold=bool(lab)))
            b.append(Group(g, f'cell {R} {rec}'))
    # P1 arc A–B, P2 arc C–A
    ax, ay = gx + (cw - 6) / 2, gy
    bx = gx + 2 * cw + (cw - 6) / 2
    b.append(Poly(qcurve((ax, ay - 30), ((ax + bx) / 2, ay - 80), (bx, ay - 30)), C['ink'], 2.5, name='P1 arc'))
    b.append(Text((ax + bx) / 2, ay - 64, 'P1', 20, C['ink'], 'middle', bold=True))
    cy_ = gy + chh + (chh - 6) / 2
    b.append(Poly(qcurve((gx - 50, gy + (chh - 6) / 2), (gx - 110, gy + chh * 0.8), (gx - 50, cy_)), C['ink'], 2.5, name='P2 arc'))
    b.append(Text(gx - 116, gy + chh * 0.8 + 6, 'P2', 20, C['ink'], 'end', bold=True))
    b.append(step_label(1, 92, 470, 'P1: A − B'))
    b.append(Text(260, 477, '+0.200 [0.188, 0.213]', 20, C['ink'], bold=True))
    b.append(step_label(2, 92, 520, 'P2: C − A, unwritten'))
    b.append(Text(130, 556, 'co-authors +0.061 [0.034, 0.090]', 18, C['ink']))
    b.append(Text(130, 584, 'first author +0.031 [−0.006, 0.069]', 18, C['pen']))
    b.append(Text(92, 650, 'title-specific signal at the output', 16, C['pen']))
    # dose curve
    b.append(step_label(3, 770, 186, 'dose: MC orders right (R0)'))
    b.append(chart(800, 250, 380, 300, [0, 1, 2, 3, 4], [(DOSE, C['true'], '')], 0, 0.5, xlab='orders right (of 4)',
                   yticks=(0, 0.25, 0.5), xticks=[(k, str(k)) for k in range(5)], name='dose chart'))
    b.append(Text(808, 250 + 300 - DOSE[0] / 0.5 * 300 - 14, '0.17', 17, C['ink']))
    b.append(Text(1180 - 6, 250 + 300 - DOSE[4] / 0.5 * 300 - 14, '0.46', 17, C['ink'], 'end'))
    SOURCES['compare'] = ['cell counts: 351_stage10/cohort/papers.parquet (recall_level × mc_team_outcome_tight)',
                          'P1 A − B +0.200 [0.188, 0.213]; P2 co-authors +0.061 [0.034, 0.090], first author +0.031 [−0.006, 0.069]: 391_groups/primary.csv rows 0, 9, 5 (final L63, unwritten authors, team bootstrap)',
                          'dose 0.170 / 0.219 / 0.256 / 0.316 / 0.463 by mc_team_a 0–4 (R0, unwritten, final L63): 391_groups/stage10_curves.csv']
    return b
