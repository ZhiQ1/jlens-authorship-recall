#!/usr/bin/env python3
"""HTML deck v50 -> v51 (2026-11-22, user approved the P77 chart style): text-list experiment pages become
method-figure + result-chart pages. Numbers are read from result files at build time (never copied from old pages).
Pages (by aria-label): "Same title, different question" (M3, X1; from merged_deck/p77_sample_20261121/p77_new_section.html,
So line final), "Patchscope and paraphrases" (X4, X3), "X2: swap only a subspace" (X2), "Retrieval, behaviour and interval
checks" (X5 + remaining checks as text), "Stage 8 re-scored on CPU: three premises" (C-2 proxy forest).
usage: build_20261122a_charts.py <in_deck> <out_deck> <numbers_json>
"""
import json, re, sys
from pathlib import Path
import pandas as pd

R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); MD = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
IN, OUT, NJ = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
INK, PEN, BLUE, GREY, ORANGE, GRID, LBLUE = '#22304A', '#6A7385', '#3C78B4', '#8A93A3', '#D9772B', '#E4EAF2', '#9DBCDD'
HAND = "font-family=\"'Patrick Hand',Caveat,cursive\""
MATH = "font-family=\"'STIX Two Math','Cambria Math','DejaVu Serif','Times New Roman',serif\""
N = {}

def t(x, y, s, size=13, fill=INK, anchor='start', weight=None):
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {HAND}{w}>{s}</text>'
def chip(x, y, w, s, fill='#FFFFFF', stroke=INK, size=11.5, h=22):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'
            + t(x + w / 2, y + h / 2 + 4.5, s, size, INK, 'middle'))
def adefs(i, col=BLUE): return (f'<defs><marker id="bh{i}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
                                f'<path d="M0 0L10 5L0 10z" fill="{col}"/></marker></defs>')
def svg(W, H, label, body): return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{label}" '
                                    f'style="width:{W}px;height:{H}px;display:block;overflow:visible">' + ''.join(body) + '</svg>')
def formula(H, s): return f'<text x="0" y="{H - 2}" font-size="12.5" fill="{PEN}" {MATH} font-style="italic">{s}</text>'
def f3(x): return f'{x:.3f}'
def ci(v, lo, hi, d=3): return f'{v:+.{d}f} [{lo:.{d}f}, {hi:.{d}f}]'

def line_chart(title, series, layers, ymin, ymax, ticks, H=222, W=545, zero=True, hline=None, fx=''):
    x0, x1, y0, y1 = 46, 470, H - 38, 62
    X = lambda l: x0 + (l - layers[0]) / (layers[-1] - layers[0]) * (x1 - x0); Y = lambda v: y0 - (v - ymin) / (ymax - ymin) * (y0 - y1)
    o = [t(0, 14, title, 15, INK, weight=700)]
    for v in ticks:
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{INK if (zero and v == 0) else GRID}" stroke-width="{1.2 if (zero and v == 0) else 1}"/>')
        o.append(t(x0 - 6, Y(v) + 4, f'{v:g}', 12, PEN, 'end'))
    prev = -99
    for l in layers:
        if X(l) - prev >= 22 or l == layers[-1] and X(l) - prev >= 14: o.append(t(X(l), y0 + 16, f'L{l}', 11, PEN, 'middle')); prev = X(l)
    if hline: o.append(f'<line x1="{x0}" y1="{Y(hline[0]):.1f}" x2="{x1}" y2="{Y(hline[0]):.1f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>' + t(x1 + 6, Y(hline[0]) + 4, hline[1], 11.5, INK))
    for name, pts, col, dash in series:   # pts: {layer: (v, lo, hi)}
        ls = sorted(pts); band = [(X(l), Y(min(ymax, pts[l][2]))) for l in ls] + [(X(l), Y(max(ymin, pts[l][1]))) for l in reversed(ls)]
        o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in band)}" fill="{col}" fill-opacity="0.16"/>')
        o.append(f'<polyline points="{" ".join(f"{X(l):.1f},{Y(pts[l][0]):.1f}" for l in ls)}" fill="none" stroke="{col}" stroke-width="2.4"' + (' stroke-dasharray="5 4"' if dash else '') + '/>')
        for l in ls: o.append(f'<circle cx="{X(l):.1f}" cy="{Y(pts[l][0]):.1f}" r="3" fill="{col}"/>')
    ly = 36; lx = x0
    for i, (name, pts, col, dash) in enumerate(series):
        o.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 18}" y2="{ly}" stroke="{col}" stroke-width="2.6"' + (' stroke-dasharray="5 4"' if dash else '') + '/>' + t(lx + 24, ly + 4, name, 12, INK)); lx += 24 + 6.6 * len(name) + 22
    o.append(formula(H, fx))
    return svg(W, H, title, o)

def page(label, tag, title, ask, left, right, so, nline, src, extra=''):
    col = lambda c: f'<div style="width:545px;flex:none">{c[0]}<div style="height:6px"></div>{c[1]}<p style="font-size:14.5px;line-height:1.25;margin-top:4px">{c[2]}</p></div>'
    return (f'<section class="slide lt" aria-label="{label}"><span class="tag">{tag}</span>\n<h2 style="font-size:46px;margin-bottom:2px">{title}</h2>\n'
            + (f'<p class="askl" style="color:#3C78B4;margin-bottom:4px"><b>Now asking:</b> {ask}</p>\n' if ask else '<div style="height:8px"></div>\n') +
            f'<div class="row" style="gap:50px;margin-top:2px">{col(left)}\n{col(right)}</div>\n{extra}'
            f'<div class="soln" style="left:70px;top:600px;width:880px"><b>So:</b> {so}</div>\n'
            f'<div class="fxn" style="left:970px;top:612px;width:250px"><span class="nn">{nline}</span></div>'
            f'<span class="src" style="position:absolute;left:70px;top:668px;width:1100px;font-size:10px">​({src})</span>\n<span class="pg"></span></section>')

# ======================================================================= X4 + X3 (Patchscope and paraphrases)
x4f = pd.read_csv(R13 / 'summary_x1x4/x4_decodability.csv'); x4f = x4f[(x4f.split == 'test') & (x4f.pos == 'title')]
x4a = pd.read_csv(R13 / 'summary_b1_xall/x4_D__all.csv'); x4a = x4a[(x4a.split == 'test') & (x4a.pos == 'title') & (x4a.answer == 'author')]
x4e = pd.read_csv(R13 / 'summary_x1x4/x4_earliest.csv').set_index(['answer', 'pos'])
def ser(df, ans=None):
    d = df if ans is None else df[df.answer == ans]
    return {int(r.layer): (r.D, r.lo, r.hi) for r in d.itertuples()}
X4 = dict(first=ser(x4f, 'author'), all=ser(x4a), year=ser(x4f, 'year'), field=ser(x4f, 'field'))
N['x4'] = {k: {l: list(v) for l, v in s.items()} for k, s in X4.items()}; N['x4_n_test'] = int(x4f.n.iloc[0])
assert x4e.loc[('author', 'title'), 'earliest_tune'] == 8 and x4e.loc[('year', 'title'), 'earliest_tune'] == 40 and pd.isna(x4e.loc[('field', 'title'), 'earliest_tune'])
x3 = pd.read_csv(R13 / 'summary_x3/x3_gap.csv'); x3 = x3[(x3.set == 'primary') & (x3.subset == 'all') & (x3.split == 'test') & (x3.pos == 'title_last')]
X3 = {c: {int(r.layer): (r.gap_minus_L4, r.dL4_lo, r.dL4_hi) for r in x3[x3.comparison == c].itertuples()} for c in ('lex', 'partner')}
x3n = int(x3.n.iloc[0]); N['x3_gap_minus_L4'] = {c: {l: list(v) for l, v in s.items()} for c, s in X3.items()}; N['x3_n_test'] = x3n
x3b = pd.read_csv(R13 / 'summary_b1_xall/x3_recovery__all.csv'); x3b = x3b[(x3b.set == 'primary') & (x3b.subset == 'all') & (x3b.split == 'test') & (x3b['false'] == 'lexical_neighbour_D')].set_index('group')
RET = (x3b.loc['all', 'ratio'], x3b.loc['all', 'lo'], x3b.loc['all', 'hi']); TC = (x3b.loc['target_minus_control', 'ratio'], x3b.loc['target_minus_control', 'lo'], x3b.loc['target_minus_control', 'hi'])
N['x3_behaviour_retention'] = list(map(float, RET)); N['x3_retention_T_minus_C'] = list(map(float, TC))
lexpeak = max(X3['lex'], key=lambda l: X3['lex'][l][0])

def x4_method():
    o = [adefs(1), t(0, 14, 'How X4 works (patchscope)', 15, INK, weight=700), t(0, 40, 'own prompt', 12, PEN)]
    o.append(chip(74, 26, 120, 'Who … titled', '#EEF1F5', GREY))
    for k, w in enumerate(['Affect', 'dynamics', '…', 'loss']): o.append(chip(200 + k * 52, 26, 48, w, '#F7E7A6'))
    o.append(f'<circle cx="{200 + 3 * 52 + 42}" cy="30" r="4" fill="{BLUE}" stroke="#fff"/>')
    o.append(t(0, 110, 'decode prompt', 12, PEN)); o.append(chip(92, 96, 230, 'Paper: X · The first author of the paper is', '#FFFFFF', INK, 11))
    o.append(f'<path d="M398 52 C 398 80, 140 74, 132 94" fill="none" stroke="{BLUE}" stroke-width="2.2" marker-end="url(#bh1)"/>')
    o.append(t(330, 76, 'inject the title state at X (layer l)', 12, BLUE)); o.append(f'<path d="M326 107 L360 107" stroke="{INK}" stroke-width="1.6" marker-end="url(#bh1)"/>')
    o.append(t(366, 111, 'score the true answer', 12, INK))
    o.append(t(0, 140, 'D = score with own state − score with a partner paper’s state', 11.5, PEN)); o.append(t(0, 154, 'answers: first author, all authors, year, field', 11.5, PEN))
    return svg(545, 160, 'X4 method', o)

def x3_method():
    o = [t(0, 14, 'How X3 works (paraphrase vs word-matched paper)', 15, INK, weight=700)]
    rows = [('original', 'Affect dynamics, bereavement and resilience', '#F7E7A6'), ('paraphrase', 'Emotional change, grief and coping', '#F7E7A6'),
            ('word-matched other paper', 'Affect dynamics in teams under deadline', '#FFFFFF')]
    for i, (lab, s, fill) in enumerate(rows):
        y = 26 + i * 32; o.append(t(0, y + 15, lab, 12, PEN)); o.append(chip(170, y, 300, s, fill, INK, 11.5))
        o.append(f'<circle cx="466" cy="{y + 4}" r="4" fill="{BLUE}" stroke="#fff"/>')
    o.append(f'<path d="M490 37 C 520 37, 520 67, 492 67" fill="none" stroke="{BLUE}" stroke-width="2"/>' + t(524, 56, 'cos', 11.5, BLUE))
    o.append(f'<path d="M490 37 C 536 37, 536 99, 492 99" fill="none" stroke="{GREY}" stroke-width="2"/>' + t(524, 92, 'cos', 11.5, GREY))
    o.append(t(0, 140, 'same prompt, state at the last title token, every layer', 11.5, PEN))
    o.append(t(0, 154, 'gap G = cos(original, paraphrase) − cos(original, other)', 11.5, PEN))
    return svg(545, 160, 'X3 method', o)

L4L = [8, 16, 24, 32, 40, 48, 56]
x4_chart = line_chart('X4: first author decodable from L8, year only from L40',
                      [('first author', X4['first'], BLUE, False), ('all authors', X4['all'], LBLUE, False), ('year', X4['year'], ORANGE, False), ('field', X4['field'], GREY, True)],
                      L4L, -0.02, 0.10, [0, 0.05, 0.1], fx='D(l) = mean[ log10(1/rank | own state) − log10(1/rank | partner state) ]')
lx = sorted(X3['lex'])
x3_chart = line_chart('X3: paraphrase stays closer than a word-matched paper, peak L36',
                      [('vs word-matched paper', X3['lex'], BLUE, False), ('vs random partner', X3['partner'], GREY, True)],
                      lx, -0.18, 0.2, [-0.1, 0, 0.1, 0.2], fx='G′(l) − G′(L4), G′ = cos(orig, para) − cos(orig, other), last title token')
fa8, fa40, yr40 = X4['first'][8], X4['first'][40], X4['year'][40]
x4_line = (f'<b>X4:</b> first author from L8 ({ci(*fa8)}), all authors from L8 ({ci(*X4["all"][8])}); year only from L40 ({ci(*yr40)}); '
           f'field passes at no layer (tune → test rule). The L8 surname signal is not explained by literal overlap but the year does not beat a text-only model (exploratory checks →  slide {{EXPL}}).')
x3_line = (f'<b>X3:</b> gap above its L4 level from L8, peak L{lexpeak} {ci(*X3["lex"][lexpeak])}; behaviour keeps {RET[0]:.3f} [{RET[1]:.3f}, {RET[2]:.3f}] of the author preference; '
           f'target − control {TC[0]:+.3f} [{TC[1]:.3f}, {TC[2]:.3f}]. A text-only embedding model shows most of this gap (→ slide {{EXPL}}): meaning, not separable from identity.')
sec_x4x3 = page('Patchscope and paraphrases', 'Stage 13 · X4 X3', 'Patchscope and paraphrases', None,
                (x4_method(), x4_chart, x4_line), (x3_method(), x3_chart, x3_line),
                'the first author is readable from the title state early (L8) and a paraphrase keeps the title’s state better than a word-matched paper — but both look like what a text-only model also sees, so neither separates paper identity from meaning. <span class="st" style="color:#3C78B4">fairly solid · descriptive</span>',
                f'n = {N["x4_n_test"]:,} test papers (X4) · {x3n:,} test papers (X3)',
                'X4: summary_x1x4/x4_decodability.csv (first author, year, field), summary_b1_xall/x4_D__all.csv (all authors), x4_earliest.csv, test split, team CI · X3: summary_x3/x3_gap.csv, summary_b1_xall/x3_recovery__all.csv, test split, team CI')

# ======================================================================= X2
x2 = pd.read_csv(R13 / 'summary_b1_xall/x2_curves_new__all.csv'); x2 = x2[(x2.split == 'test') & (x2.arm == 'carry')]
X2 = {s: {int(r.layer): (r.value, r.lo, r.hi) for r in x2[x2.S == s].itertuples()} for s in ('id', 'auth', 'rand', 'full')}
vd = pd.read_csv(R13 / 'summary_b1_xall/x2_verdict_new__all.csv').iloc[0]
san = pd.read_csv(R13 / 'summary_b1_xall/fit_authall_sanity.csv'); r2max = float(san.authall_r2.max())
N['x2'] = {s: {l: list(v) for l, v in d.items()} for s, d in X2.items()}; N['x2_verdict'] = {k: (float(vd[k]) if not isinstance(vd[k], str) else vd[k]) for k in ('verdict', 'id_layer', 'id_R_S', 'id_R_full', 'auth_layer', 'auth_R_S', 'auth_R_full', 'auth_minus_id', 'auth_minus_id_lo', 'auth_minus_id_hi')}
N['x2_auth_r2_max'] = r2max; x2n = int(x2.n.iloc[0])

def x2_method():
    o = [adefs(3), t(0, 14, 'How X2 works', 15, INK, weight=700), t(0, 40, 'paper A', 12, PEN)]
    for k, w in enumerate(['Affect', 'dynamics', '…', 'loss']): o.append(chip(70 + k * 52, 26, 48, w, '#F7E7A6'))
    o.append(f'<rect x="300" y="22" width="34" height="30" rx="4" fill="{BLUE}" fill-opacity="0.25" stroke="{BLUE}"/>' + t(317, 41, 'S', 12, BLUE, 'middle'))
    o.append(t(342, 36, 'S_id: 9 paper-attribute dims', 11.5, INK)); o.append(t(342, 50, 'S_auth: 10 author dims', 11.5, INK))
    o.append(t(0, 110, 'paper B', 12, PEN)); o.append(chip(70, 96, 200, 'Who are the authors… (B’s title)', '#FFFFFF', INK, 11))
    o.append(chip(276, 96, 58, 'Authors:', '#FFFFFF'))
    o.append(f'<path d="M317 54 L317 92" stroke="{BLUE}" stroke-width="2.4" marker-end="url(#bh3)"/>' + t(326, 80, 'swap only the S-component of A’s state, layer l', 11.5, BLUE))
    o.append(t(0, 140, 'score A’s authors; compare with a random subspace of the same size', 11.5, PEN))
    o.append(t(0, 154, 'and with the full replacement (all dims)', 11.5, PEN))
    return svg(545, 160, 'X2 method', o)

def x2_chart():
    H, W, x0, x1, y0, y1 = 222, 545, 46, 520, 184, 56
    ymax = 0.045; Y = lambda v: y0 - v / ymax * (y0 - y1)
    o = [t(0, 14, 'X2: either subspace moves only a few percent', 15, INK, weight=700)]
    for v in (0, 0.02, 0.04):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{INK if v == 0 else GRID}"/>' + t(x0 - 6, Y(v) + 4, f'{v:g}', 12, PEN, 'end'))
    cols = {'id': GREY, 'auth': BLUE, 'rand': '#D5DAE2'}; ls = [16, 24, 32, 40, 48]; gw = (x1 - x0) / len(ls)
    for gi, l in enumerate(ls):
        gx = x0 + gi * gw + 12
        for qi, s in enumerate(('id', 'auth', 'rand')):
            v, lo, hi = X2[s][l]; bx = gx + qi * 22; top = Y(max(v, 0))
            o.append(f'<rect x="{bx:.1f}" y="{top:.1f}" width="18" height="{abs(Y(0) - Y(v)):.1f}" fill="{cols[s]}" stroke="{INK}" stroke-width="0.7"/>')
            o.append(f'<line x1="{bx + 9:.1f}" y1="{Y(min(hi, ymax)):.1f}" x2="{bx + 9:.1f}" y2="{Y(max(lo, -0.004)):.1f}" stroke="{INK}" stroke-width="1.2"/>')
        o.append(t(gx + 33, y0 + 16, f'L{l}', 11.5, PEN, 'middle')); o.append(t(gx + 33, y1 - 6, f'full {X2["full"][l][0]:.2f}', 11, ORANGE, 'middle'))
    for qi, (s, lab) in enumerate((('id', 'S_id'), ('auth', 'S_auth'), ('rand', 'random'))):
        o.append(f'<rect x="{x0 + 260 + qi * 70}" y="22" width="12" height="12" fill="{cols[s]}" stroke="{INK}" stroke-width="0.7"/>' + t(x0 + 276 + qi * 70, 32, lab, 12, INK))
    o.append(formula(H, 'moved share = mean(patched − corrupt) / mean(clean − corrupt)'))
    return svg(W, H, 'X2 moved share by layer', o)

v = N['x2_verdict']
x2_line_l = f'<b>Method:</b> the subspaces were fitted on 5,041 training papers; S_auth hardly decodes authors (held-out R² ≤ {r2max:.3f}).'
x2_line_r = (f'<b>Result:</b> S_id at L{int(v["id_layer"])} moves {v["id_R_S"]:.3f} (full {v["id_R_full"]:.3f}); S_auth at L{int(v["auth_layer"])} moves {v["auth_R_S"]:.3f} '
             f'(full {v["auth_R_full"]:.3f}); pre-registered rule: H2 not supported, H3 passes (S_auth − S_id {ci(v["auth_minus_id"], v["auth_minus_id_lo"], v["auth_minus_id_hi"])}).')
sec_x2 = page('X2: swap only a subspace', 'Stage 13 · X2', 'X2: swap only a subspace', 'are author names hidden in the middle layers, and are made-up names near-misses?',
              (x2_method(), '', x2_line_l), (x2_chart(), '', x2_line_r),
              'H3 passes by the locked rule, but a subspace that cannot decode authors moves only about 7% of the full replacement — the information carried from the title to the names lies almost entirely outside both subspaces. <span class="st" style="color:#3C78B4">pre-registered · weak evidence</span>',
              f'n = {x2n} test pairs · subspaces fitted on 5,041 papers', 'X2: summary_b1_xall/x2_curves_new__all.csv, x2_verdict_new__all.csv, fit_authall_sanity.csv; all authors, test split, team CI')

# ======================================================================= X5 (+ checks)
x5 = pd.read_csv(R13 / 'summary_x5/x5_retrieval.csv'); x5 = x5[x5.set == 'all']
X5 = {p: {int(r.layer): (r.top1, r.top1_lo_team, r.top1_hi_team) for r in x5[x5.pos == p].itertuples()} for p in ('title_last', 'colon')}
N['x5'] = {p: {l: list(v) for l, v in d.items()} for p, d in X5.items()}

def x5_method():
    o = [adefs(4), t(0, 14, 'How X5 works (retrieval across questions)', 15, INK, weight=700)]
    o.append(t(0, 40, 'question 1', 12, PEN)); o.append(chip(86, 26, 120, 'In what year … titled', '#EEF1F5', GREY))
    for k, w in enumerate(['Affect', '…', 'loss']): o.append(chip(212 + k * 52, 26, 48, w, '#F7E7A6'))
    o.append(f'<circle cx="{212 + 2 * 52 + 42}" cy="30" r="4" fill="{BLUE}" stroke="#fff"/>')
    o.append(t(0, 104, 'question 2,', 12, PEN)); o.append(t(0, 118, 'all papers', 12, PEN))
    for k in range(6): o.append(f'<circle cx="{110 + k * 46}" cy="104" r="7" fill="{BLUE if k == 2 else "#C3C9D2"}" stroke="{INK}" stroke-width="0.8"/>')
    o.append(f'<path d="M354 54 C 354 80, 210 80, 204 94" fill="none" stroke="{BLUE}" stroke-width="2.2" marker-end="url(#bh4)"/>')
    o.append(t(372, 80, 'nearest state = same paper?', 12, BLUE))
    o.append(t(0, 144, 'top-1 retrieval among 9,108 papers, per layer; position: last title token or colon', 11.5, PEN))
    return svg(545, 160, 'X5 method', o)

x5L = sorted(X5['title_last'])
x5_chart = line_chart('X5: the title finds its paper perfectly from L4 to L44', [('last title token', X5['title_last'], BLUE, False), ('colon', X5['colon'], GREY, True)],
                      x5L, 0, 1.05, [0, 0.5, 1.0], zero=False, fx='retrieval(l) = P(nearest state under q₂ is the same paper), 9,108 papers')
ret = X5['title_last']
x5_line = (f'<b>X5:</b> {ret[4][0]:.3f} at L4, {ret[44][0]:.4f} at L44, {ret[48][0]:.3f} at L48, {ret[63][0]:.3f} at the output; never above L4 — a ceiling, since the title text is identical (text-only BERT also 1.000 from its layer 1).')
checks = ('<ul class="t" style="font-size:15.5px;line-height:1.3;margin-top:4px">'
          '<li><b>M3 behaviour scores:</b> year target − control +0.007 [0.003, 0.012]; all authors, all name tokens +0.234 [0.215, 0.252]</li>'
          '<li><b>N2 by layer:</b> pure name prior target − control +0.047 at the output, +0.039 at logit L62; public J-lens L48 −0.133 → only L62 reproduces the output</li>'
          '<li><b>Paper vs team intervals:</b> width ratio 0.97–1.00 (median); “excludes 0” changes in 2 of 1,155 rows</li>'
          '<li><b>M5 true vs false title at the name positions:</b> output 0.919; logit L24 0.516 → L62 0.899; probe at title / colon AUROC 0.50–0.52</li></ul>')
sec_x5 = page('Retrieval, behaviour and interval checks', 'Stage 13 · checks', 'Retrieval, behaviour and interval checks', 'what could still be wrong?',
              (x5_method(), x5_chart, x5_line), ('<p style="font-size:16px;font-weight:700;margin-top:2px">Other checks (existing data, descriptive)</p>', checks, ''),
              'retrieval across questions is at its ceiling from L4, so it cannot show identity; the behaviour, prior and interval checks change no conclusion. <span class="st" style="color:#6A7385">descriptive · X5 pre-registered</span>',
              'n = 9,108 papers (X5, M3) · 4,621 / 2,220 (M3 T − C) · 1,155 interval rows', 'X5: summary_x5/x5_retrieval.csv, team CI · other checks: m3 behaviour (2-10), N2, interval comparison, summary_m5 (as on the previous version of this page)')

# ======================================================================= Stage 8 CPU proxy (C-2)
c2 = pd.read_csv(R13 / 'c13_C2_followup/c2_followup_proxy.csv'); c2 = c2[c2.version == 'aa_all'].set_index('endpoint')
EP = [('int6', '6-layer mean (no L16)'), ('L56', 'L56 alone'), ('int7_L16zero', '7-layer, L16 = 0'), ('int7_L16eqL24', '7-layer, L16 = L24')]
N['c2_aa_all'] = {e: {k: float(c2.loc[e, k]) for k in ('rq1', 'rq1_team_lo', 'rq1_team_hi', 'rq2', 'rq2_lo', 'rq2_hi')} for e, _ in EP}

def c2_method():
    o = [t(0, 14, 'How the CPU proxy works', 15, INK, weight=700)]
    o.append(t(0, 42, 'same 200 Stage 8 papers', 12.5, INK)); o.append(t(0, 60, '100 A / B pairs', 12.5, INK))
    o.append(chip(190, 30, 150, 'true title', '#F7E7A6')); o.append(chip(190, 60, 150, '5 false titles (Stage 10)', '#FFFFFF'))
    o.append(t(352, 46, 'score every author,', 12, PEN)); o.append(t(352, 62, 'every name token', 12, PEN))
    o.append(t(0, 100, 'RQ1 = true − false (all papers) · RQ2 = A − B (paired)', 12.5, BLUE))
    o.append(t(0, 122, 'endpoints: 6-layer mean, L56 alone, two versions of the locked 7-layer endpoint', 11.5, PEN))
    o.append(t(0, 140, 'rank metric (public J-lens), NOT the W statistic of Stage 8', 11.5, PEN))
    return svg(545, 160, 'C-2 method', o)

def c2_chart():
    H, W, x0, x1 = 222, 545, 170, 520; lo_, hi_ = -0.05, 0.25; X = lambda v: x0 + (v - lo_) / (hi_ - lo_) * (x1 - x0)
    o = [t(0, 14, 'RQ1 positive everywhere; RQ2 not at L56 alone', 15, INK, weight=700)]
    for v in (0, 0.1, 0.2):
        o.append(f'<line x1="{X(v):.1f}" y1="34" x2="{X(v):.1f}" y2="{H - 34}" stroke="{INK if v == 0 else GRID}"/>' + t(X(v), H - 20, f'{v:g}', 11.5, PEN, 'middle'))
    for i, (e, lab) in enumerate(EP):
        y = 50 + i * 38; r = c2.loc[e]; o.append(t(0, y + 8, lab, 12, INK))
        for dy, (v, lo, hi), col in ((-6, (r.rq1, r.rq1_team_lo, r.rq1_team_hi), GREY), (8, (r.rq2, r.rq2_lo, r.rq2_hi), BLUE)):
            o.append(f'<line x1="{X(lo):.1f}" y1="{y + dy}" x2="{X(hi):.1f}" y2="{y + dy}" stroke="{col}" stroke-width="2"/><circle cx="{X(v):.1f}" cy="{y + dy}" r="4" fill="{col}"/>')
    o.append(f'<circle cx="{x1 - 120}" cy="26" r="4" fill="{GREY}"/>' + t(x1 - 112, 30, 'RQ1', 12, INK) + f'<circle cx="{x1 - 60}" cy="26" r="4" fill="{BLUE}"/>' + t(x1 - 52, 30, 'RQ2', 12, INK))
    o.append(formula(H, 'spec = nlr_true − mean₅ nlr_false, averaged over the endpoint’s layers; 95% team CI'))
    return svg(W, H, 'C-2 forest', o)

g = N['c2_aa_all']
c2_line_r = (f'<b>Result:</b> 6-layer mean RQ1 {ci(g["int6"]["rq1"], g["int6"]["rq1_team_lo"], g["int6"]["rq1_team_hi"])}, RQ2 {ci(g["int6"]["rq2"], g["int6"]["rq2_lo"], g["int6"]["rq2_hi"])}; '
             f'L56 alone RQ2 {ci(g["L56"]["rq2"], g["L56"]["rq2_lo"], g["L56"]["rq2_hi"])} (CI includes 0 → the addendum-13 rule asked for the W re-run, not done = deviation D13-1).')
c2_line_l = '<b>Premises:</b> W scores only the first author’s first token (64.5% initials); D13-1; U28 (L56 made primary at 21:14, by whom and why unknown).'
sec_c2 = page('Stage 8 re-scored on CPU: three premises', 'Stage 8 · CPU proxy', 'Stage 8 re-scored on CPU: three premises', None,
              (c2_method(), '', c2_line_l), (c2_chart(), '', c2_line_r),
              'with five false titles and every author, Stage 8’s direction holds (RQ1 and RQ2 positive on the 6- and 7-layer endpoints), but L56 alone does not, so the Stage 8 result rests on three premises. <span class="st" style="color:#3C78B4">fairly solid with premises</span>',
              'n = 200 papers · 100 A/B pairs', 'addendum 13 C-2: 381_stage13/c13_C2_followup/c2_followup_proxy.csv (version aa_all: all authors, all name tokens), team CI')

# ======================================================================= M3 / X1 (approved sample) and assembly
p77 = (MD / 'p77_sample_20261121/p77_new_section.html').read_text()
p77 = p77.replace('aria-label="Same title, different question (chart draft)"', 'aria-label="Same title, different question"')
so_old = re.search(r'<div style="position:absolute;left:70px;width:880px;top:614px;border:1.8px dashed[^>]*><b>So:</b>.*?</div>', p77, re.S); assert so_old
p77 = p77.replace(so_old.group(0), '<div class="soln" style="left:70px;top:610px;width:880px"><b>So:</b> at the title these tests are ceiling-limited: the same title text already gives the same state under every question at L4 (a text-only BERT too), so M3 and X1 cannot separate meaning from paper identity; X1’s task independence follows from that. <span class="st" style="color:#B54708">exploratory ceiling check</span></div>')
x1a = pd.read_csv(R13 / 'summary_b1_xall/x1__all.csv'); x1a = x1a[(x1a.split == 'test') & (x1a.layer == 48)].iloc[0]
AY = (float(x1a.a_minus_year), float(x1a.a_minus_year_lo), float(x1a.a_minus_year_hi)); N['x1_authors_minus_year_L48'] = list(AY)
m_ = re.search(r'at L4 R ([\d.]+) \(text-replacement control\)\.', p77); assert m_
p77 = p77.replace(m_.group(0), m_.group(0)[:-1] + f'; authors − year at L48 {AY[0]:+.3f} [{AY[1]:.3f}, {AY[2]:.3f}].')
p77 = p77.replace('class="src" style="position:absolute;left:70px;top:652px;font-size:10.5px"', 'class="src" style="position:absolute;left:70px;top:668px;width:1100px;font-size:10px"')
assert '+0.024 [0.019, 0.030]' in p77

deck = IN.read_text()
secs = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', deck, flags=re.S))
lab = lambda s: re.search(r'aria-label="([^"]*)"', s).group(1)
expl = [i + 1 for i, m in enumerate(secs) if lab(m.group(0)).startswith('Exploratory: what the title-position tests')]; assert len(expl) == 1
sec_x4x3 = sec_x4x3.replace('{EXPL}', str(expl[0]))
REPL = {'Same title, different question': p77, 'Patchscope and paraphrases': sec_x4x3, 'X2: swap only a subspace': sec_x2,
        'Retrieval, behaviour and interval checks': sec_x5, 'Stage 8 re-scored on CPU: three premises': sec_c2}
out, last, done = [], 0, {}
for i, m in enumerate(secs):
    L = lab(m.group(0))
    if L in REPL:
        assert L not in done; old = m.group(0); new = REPL[L]
        if ' on"' in old.split('>')[0]: new = new.replace('class="slide lt"', 'class="slide lt on"', 1)
        out.append(deck[last:m.start()]); out.append(new); last = m.end(); done[L] = i + 1
out.append(deck[last:]); new_deck = ''.join(out)
assert set(done) == set(REPL), done
assert len(re.findall(r'<section class="slide', new_deck)) == len(secs)
OUT.write_text(new_deck); N['pages'] = done; NJ.write_text(json.dumps(N, indent=1, default=float))
print('ok', done, len(deck), '->', len(new_deck))
