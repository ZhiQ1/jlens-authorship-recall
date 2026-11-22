#!/usr/bin/env python3
"""Draft (NOT in the live deck): chart version of HTML deck page "Same title, different question" (M3, X1).
Numbers are read from the result files at build time (never copied from the old page):
  M3  381_stage13/summary_m3/m3_transfer.csv  (train == 'avg' rows = mean of 6 ordered question pairs, team CI)
  X1  381_stage13/summary_b1_xall/x1__all.csv (split == 'test', all authors, team CI)
  ceiling: 381_stage13/reports/x1_similarity.md (raw cosine, title_last), 381_stage13/reports/x5_retrieval.md (all 9,108)
Writes <out>/p77_sample.html (head of the deck + P65 + old P77 + new P77 + nav) and <out>/p77_numbers.json.
usage: p77_sample_20261121.py <outdir>
"""
import json, re, sys
from pathlib import Path
import pandas as pd

R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
DECK = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
INK, PEN, BLUE, GREY, ORANGE, GRID = '#22304A', '#6A7385', '#3C78B4', '#8A93A3', '#D9772B', '#E4EAF2'
HAND = "font-family=\"'Patrick Hand',Caveat,cursive\""
MATH = "font-family=\"'STIX Two Math','Cambria Math','DejaVu Serif','Times New Roman',serif\""

# ---------------------------------------------------------------- numbers
m3 = pd.read_csv(R13 / 'summary_m3/m3_transfer.csv'); m3 = m3[m3.train == 'avg']
def m3row(pos, tgt): return m3[(m3.pos == pos) & (m3.target == tgt)].sort_values('layer')
tf, cf, ty = m3row('title_last', 'field'), m3row('colon', 'field'), m3row('title_last', 'year')
x1 = pd.read_csv(R13 / 'summary_b1_xall/x1__all.csv'); x1 = x1[x1.split == 'test'].set_index('layer')
sim = open(R13 / 'reports/x1_similarity.md').read().split('## colon')[0]
cos = {int(m.group(1)): (float(m.group(2)), float(m.group(3))) for m in re.finditer(r'\| L(\d+) \| ([\d.]+) \([\d.]+\) \| ([\d.]+) \|', sim)}
x5 = open(R13 / 'reports/x5_retrieval.md').read().split('## colon')[0]
ret = {int(m.group(1)): float(m.group(2)) for m in re.finditer(r'\| L(\d+) \| all \| 9108 \| \+([\d.]+) ', x5)}
yr = ty[(ty.layer >= 16) & (ty.layer <= 40)].T_minus_L4
N = dict(m3_papers=9108, x1_test=int(x1.loc[24, 'n']),
         field_title={int(r.layer): [r.ratio, r.lo, r.hi] for r in tf.itertuples()},
         field_colon={int(r.layer): [r.ratio, r.lo, r.hi] for r in cf.itertuples()},
         year_title_minus_L4_L16_40=[float(yr.max()), float(yr.min())],
         x1={int(l): {q: [x1.loc[l, f'R_{q}'], x1.loc[l, f'R_{q}_lo'], x1.loc[l, f'R_{q}_hi']] for q in ('authors', 'year', 'field')} for l in (4, 24, 40, 48)},
         cos_same_paper={4: cos[4][0], 24: cos[24][0]}, cos_two_papers_L4=cos[4][1],
         x5_top1={l: ret[l] for l in (4, 44, 48)})
json.dump(N, open(OUT / 'p77_numbers.json', 'w'), indent=1, default=float)
assert ret[4] == 1.0 and ret[44] == 1.0, ret

def f3(x): return f'{x:.3f}'
def t(x, y, s, size=13, fill=INK, anchor='start', weight=None, extra=''):
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {HAND}{w} {extra}>{s}</text>'
def chip(x, y, w, s, fill='#FFFFFF', stroke=INK, size=12.5, h=22, color=INK):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'
            + t(x + w / 2, y + h / 2 + 4.5, s, size, color, 'middle'))
def arrow_defs(i): return (f'<defs><marker id="ah{i}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
                           f'<path d="M0 0L10 5L0 10z" fill="{BLUE}"/></marker></defs>')
def step(x, y, n): return f'<circle cx="{x}" cy="{y}" r="10" fill="{INK}"/>' + t(x, y + 4.5, n, 13, '#FFFFFF', 'middle')

# ---------------------------------------------------------------- method schematics (Methods-in-pictures style)
def m3_method():
    W, H = 545, 150; o = [arrow_defs(1)]
    o.append(t(0, 14, 'How M3 works', 15, INK, weight=700))
    rows = [('authors', 'Who are the authors of the paper titled', 'Authors:'), ('year', 'In what year was the research paper titled', 'Year:'),
            ('field', 'In what research field is the paper titled', 'Field:')]
    for i, (q, pre, col) in enumerate(rows):
        y = 26 + i * 30
        o.append(chip(0, y, 186, pre[:30] + '…', '#EEF1F5', GREY, 11))
        for k, w in enumerate(['Affect', 'dynamics', '…', 'loss']): o.append(chip(192 + k * 52, y, 48, w, '#F7E7A6', INK, 11.5))
        o.append(chip(400, y, 58, col, '#FFFFFF', INK, 11.5))
        o.append(f'<circle cx="{192 + 3 * 52 + 42}" cy="{y + 4}" r="4" fill="{BLUE}" stroke="#fff" stroke-width="1"/><circle cx="{400 + 52}" cy="{y + 4}" r="4" fill="{GREY}" stroke="#fff" stroke-width="1"/>')
    o.append(t(186 + 3, 124, 'question first (9 tokens) · then the identical title', 11.5, PEN))
    o.append(f'<path d="M472 37 C 510 37, 510 67, 474 67" fill="none" stroke="{BLUE}" stroke-width="2" marker-end="url(#ah1)"/>')
    o.append(f'<path d="M472 37 C 528 37, 528 97, 474 97" fill="none" stroke="{BLUE}" stroke-width="2" marker-end="url(#ah1)"/>')
    o.append(t(0, 140, '● state at the last title token (blue) or the colon (grey), every layer L4–L63', 11.5, PEN)); o.append(t(0, 154, '→ probe trained under one question, tested under the other two', 11.5, BLUE))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 160" role="img" aria-label="M3 method" style="width:{W}px;height:160px;display:block;overflow:visible">' + ''.join(o) + '</svg>'

def x1_method():
    W = 545; o = [arrow_defs(2)]
    o.append(t(0, 14, 'How X1 works', 15, INK, weight=700))
    o.append(t(0, 40, 'paper A', 12.5, PEN)); o.append(chip(56, 26, 150, 'year / field / authors question', '#EEF1F5', GREY, 11))
    for k, w in enumerate(['Affect', 'dynamics', '…', 'loss']): o.append(chip(212 + k * 52, 26, 48, w, '#F7E7A6', INK, 11.5))
    o.append(chip(420, 26, 52, '…', '#FFFFFF', INK, 11.5))
    o.append(t(0, 110, 'other paper', 12.5, PEN)); o.append(chip(70, 96, 136, 'Who are the authors…', '#EEF1F5', GREY, 11))
    for k, w in enumerate(['Scholars', 'foreign', '…', 'policy']): o.append(chip(212 + k * 52, 96, 48, w, '#FFFFFF', INK, 11.5))
    o.append(chip(420, 96, 58, 'Authors:', '#FFFFFF', INK, 11.5))
    o.append(f'<rect x="209" y="23" width="210" height="28" rx="6" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5 3"/>')
    o.append(f'<path d="M314 52 L314 92" stroke="{BLUE}" stroke-width="2.4" marker-end="url(#ah2)"/>')
    o.append(t(322, 76, 'copy A’s title states at layer l', 12, BLUE))
    o.append(f'<path d="M482 107 L520 107" stroke="{INK}" stroke-width="1.6" marker-end="url(#ah2)"/>')
    o.append(t(520, 98, 'score', 11.5, INK, 'end')); o.append(t(530, 128, 'A’s authors', 11.5, INK, 'end'))
    o.append(t(0, 145, 'one bar group per source question: does it matter which question A’s state came from?', 11.5, PEN))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 160" role="img" aria-label="X1 method" style="width:{W}px;height:160px;display:block;overflow:visible">' + ''.join(o) + '</svg>'

# ---------------------------------------------------------------- result charts
def m3_chart():
    W, H, x0, x1_, y0, y1 = 545, 222, 42, 470, 184, 50   # plot box
    X = lambda l: x0 + (l - 4) / (63 - 4) * (x1_ - x0); Y = lambda v: y0 - v / 1.05 * (y0 - y1)
    o = [t(0, 14, 'M3: transfer T at the title stays at its L4 level', 15, INK, weight=700)]
    L4 = N['field_title'][4][0]
    o.append(f'<rect x="{x0}" y="{Y(1.0):.1f}" width="{x1_ - x0}" height="{Y(0.95) - Y(1.0):.1f}" fill="#F7E7A6" fill-opacity="0.7"/>')
    o.append(t(x0 + 6, Y(1.0) - 4, f'ceiling: identical title text, cos(same paper, 2 questions) {N["cos_same_paper"][4]:.3f} at L4', 11, PEN))
    for v in (0, 0.5, 1.0):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1_}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>'); o.append(t(x0 - 6, Y(v) + 4, f'{v:g}', 12, PEN, 'end'))
    for l in (4, 16, 24, 40, 48, 56, 63): o.append(t(X(l), y0 + 16, f'L{l}', 11.5, PEN, 'middle'))
    o.append(f'<line x1="{x0}" y1="{Y(L4):.1f}" x2="{x1_}" y2="{Y(L4):.1f}" stroke="{INK}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    for ser, col in ((N['field_title'], BLUE), (N['field_colon'], GREY)):
        ls = sorted(ser); band = [(X(l), Y(ser[l][2])) for l in ls] + [(X(l), Y(ser[l][1])) for l in reversed(ls)]
        o.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in band)}" fill="{col}" fill-opacity="0.18"/>')
        o.append(f'<polyline points="{" ".join(f"{X(l):.1f},{Y(ser[l][0]):.1f}" for l in ls)}" fill="none" stroke="{col}" stroke-width="2.4"/>')
        for l in ls: o.append(f'<circle cx="{X(l):.1f}" cy="{Y(ser[l][0]):.1f}" r="3" fill="{col}"/>')
    o.append(t(x1_ + 6, Y(N['field_title'][63][0]) + 4, 'title', 12.5, BLUE)); o.append(t(x1_ + 6, Y(N['field_colon'][63][0]) + 4, 'colon', 12.5, GREY))
    o.append(t(x1_ + 6, Y(L4) - 10, 'L4 level', 11.5, INK))
    o.append(f'<text x="0" y="{H - 2}" font-size="12.5" fill="{PEN}" {MATH} font-style="italic">T = acc(train q₁ → test q₂) / acc(train q₂ → test q₂), mean of 6 ordered question pairs</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="M3 transfer by layer" style="width:{W}px;height:{H}px;display:block;overflow:visible">' + ''.join(o) + '</svg>'

def x1_chart():
    W, H, x0, x1_, y0, y1 = 545, 222, 42, 520, 184, 62
    Y = lambda v: y0 - v / 1.05 * (y0 - y1)
    o = [t(0, 14, 'X1: same recovery whichever question A’s state came from', 15, INK, weight=700)]
    for v in (0, 0.5, 1.0):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1_}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>'); o.append(t(x0 - 6, Y(v) + 4, f'{v:g}', 12, PEN, 'end'))
    cols = {'authors': BLUE, 'year': '#7FA7CF', 'field': '#B9CDE3'}; gw = (x1_ - x0) / 3
    for gi, l in enumerate((24, 40, 48)):
        gx = x0 + gi * gw + 24
        for qi, q in enumerate(('authors', 'year', 'field')):
            v, lo, hi = N['x1'][l][q]; bx = gx + qi * 34
            o.append(f'<rect x="{bx:.1f}" y="{Y(v):.1f}" width="28" height="{Y(0) - Y(v):.1f}" fill="{cols[q]}" stroke="{INK}" stroke-width="0.8"/>')
            o.append(f'<line x1="{bx + 14:.1f}" y1="{Y(hi):.1f}" x2="{bx + 14:.1f}" y2="{Y(lo):.1f}" stroke="{INK}" stroke-width="1.4"/>')
            o.append(t(bx + 14, Y(hi) - 4, f'{v:.3f}', 10.5, INK, 'middle'))
        o.append(t(gx + 48, y0 + 16, f'L{l}', 12, PEN, 'middle'))
    for qi, q in enumerate(('authors', 'year', 'field')):
        o.append(f'<rect x="{x1_ - 200 + qi * 68}" y="{y1 - 30}" width="12" height="12" fill="{cols[q]}" stroke="{INK}" stroke-width="0.8"/>'); o.append(t(x1_ - 184 + qi * 68, y1 - 20, q, 12, INK))
    o.append(t(x1_ - 350, y1 - 20, 'state came from:', 11.5, PEN))
    o.append(f'<text x="0" y="{H - 2}" font-size="12.5" fill="{PEN}" {MATH} font-style="italic">R(l) = mean(patched − other) / mean(own − other)</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="X1 recovery by source question" style="width:{W}px;height:{H}px;display:block;overflow:visible">' + ''.join(o) + '</svg>'

# ---------------------------------------------------------------- page
ft, cf_ = N['field_title'], N['field_colon']; xa = N['x1']
m3_line = (f'<b>M3:</b> a field probe trained under one question transfers almost perfectly at the title (T {f3(ft[40][0])} at L40) — '
           f'but already {f3(ft[4][0])} at L4, never above it (year T − T(L4) {N["year_title_minus_L4_L16_40"][1]:+.3f} to {N["year_title_minus_L4_L16_40"][0]:+.3f} at L16–L40); '
           f'at the colon T is {min(v[0] for l, v in cf_.items() if l <= 52):.2f}–{max(v[0] for l, v in cf_.items() if l <= 52):.2f} at L4–L52 (question-specific).')
x1_line = (f'<b>X1:</b> R {f3(xa[24]["authors"][0])} / {f3(xa[40]["authors"][0])} / {f3(xa[48]["authors"][0])} (authors) vs '
           f'{f3(xa[24]["year"][0])} / {f3(xa[40]["year"][0])} / {f3(xa[48]["year"][0])} (year) at L24 / L40 / L48; at L4 R {f3(xa[4]["authors"][0])} (text-replacement control).')
ceil = (f'Ceiling: same paper, two questions — title-state cosine {N["cos_same_paper"][4]:.4f} at L4, {N["cos_same_paper"][24]:.4f} at L24 '
        f'(two papers {N["cos_two_papers_L4"]:.2f}); X5 retrieval of the paper across questions {N["x5_top1"][4]:.3f} at L4–L44 ({N["x5_top1"][48]:.3f} at L48).')
SRC = '<span class="src">​(M3: summary_m3/m3_transfer.csv, 9,108 papers, 5 team folds, team CI · X1: summary_b1_xall/x1__all.csv, test 582 papers, team CI · x1_similarity.md, x5_retrieval.md)</span>'
sec = f'''<section class="slide lt" aria-label="Same title, different question (chart draft)"><span class="tag">Stage 13 · M3 X1</span>
<h2 style="font-size:46px;margin-bottom:2px">Same title, different question</h2>
<p class="askl" style="color:#3C78B4;margin-bottom:4px"><b>Now asking:</b> is it the title’s meaning, or the identity of this paper?</p>
<div class="row" style="gap:50px;margin-top:2px"><div style="width:545px;flex:none">{m3_method()}<div style="height:6px"></div>{m3_chart()}
<p style="font-size:14.5px;line-height:1.25;margin-top:4px">{m3_line}</p></div>
<div style="width:545px;flex:none">{x1_method()}<div style="height:6px"></div>{x1_chart()}
<p style="font-size:14.5px;line-height:1.25;margin-top:4px">{x1_line}</p></div></div>
<div style="position:absolute;left:70px;right:70px;top:590px;font-size:13.5px;color:{PEN};font-family:var(--hand)">{ceil}</div>
<div style="position:absolute;left:70px;width:880px;top:614px;border:1.8px dashed {ORANGE};border-radius:10px;padding:5px 12px;font-size:15.5px;color:#B54708;background:#FFF6DC;font-family:var(--hand)"><b>So:</b> conclusion text pending user decision — M3 / X1 are ceiling-limited at the title position.</div>
<div class="fxn" style="left:970px;top:612px;width:250px"><span class="nn">n = 9,108 papers (M3) · 582 test papers (X1)</span></div>{SRC.replace('class="src"', 'class="src" style="position:absolute;left:70px;top:652px;font-size:10.5px"')}
<span class="pg"></span></section>'''
t_ = DECK.read_text(); head = t_[:t_.index('<div class="viewport">')]
secs = re.findall(r'<section class="slide[^"]*"[^>]*>.*?</section>', t_, flags=re.S)
old = [s for s in secs if 'aria-label="Same title, different question"' in s]; assert len(old) == 1
last = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t_, flags=re.S))[-1]
nav = t_[last.end():]
page = head + '<div class="viewport"><div class="stage" id="stage">' + old[0].replace('slide lt"', 'slide lt on"', 1) + sec + nav
(OUT / 'p77_sample.html').write_text(page); (OUT / 'p77_new_section.html').write_text(sec)
print('ok', OUT / 'p77_sample.html'); print(json.dumps({k: v for k, v in N.items() if k in ('cos_same_paper', 'x5_top1', 'year_title_minus_L4_L16_40')}, default=float))
