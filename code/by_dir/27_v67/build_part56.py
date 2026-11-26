"""v67 agent C (2026-11-23): Part 5 (route + H3) and Part 6 (writing step) slide fragments.
Writes ~/jlens_work/27_v67/fragments/<slot>.html (standalone <section class="slide mf">, deck CSS classes) and
fragments/part56_numbers.md; references are {{p:<v65 page>}} / {{new:<slot>}} placeholders for the integrator.
All plotted / quoted numbers are read here from the locked result files (paths in NUM) or quoted from existing slides.
usage: build_part56.py"""
import csv, json, re, sys, html as H
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/normalise_sample_20261122b'); sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/hc_pass_20261123')
from addonly_lib import tex
from texu import ntex

R = '/scratch/zhang.zhiqi2/jlens/391_groups/'
OUT = '/home/zhang.zhiqi2/jlens_work/27_v67/fragments/'
INK, GREY, ORANGE, BLUE, GREEN, RED, PURPLE, FXG = '#22304A', '#6A7385', '#D9772B', '#3C78B4', '#2E7D46', '#C84A3E', '#7B5EA7', '#8a8f98'
PH = "'Patrick Hand',Caveat,cursive"; CAV = "Caveat,'Patrick Hand',cursive"; SANS = "'Noto Sans SC','PingFang SC','Droid Sans Fallback',system-ui,sans-serif"
NUM = []   # (number as shown, meaning, source)
def num(shown, what, src): NUM.append((shown, what, src)); return shown

def rd(path): return list(csv.DictReader(open(R + path)))
def f3(x, sign=True): x = float(x); s = f'{x:+.3f}' if sign else f'{x:.3f}'; return s.replace('-', '−')
def pct(x, d=1): return f'{100 * float(x):.{d}f}%'
def ci(lo, hi): return f'[{f3(lo)}, {f3(hi)}]'

# ---------------------------------------------------------------- real Qwen3 tokens of the example prompt (verified with the cached tokenizer)
TOK = ['Who', '·are', '·the', '·authors', '·of', '·the', '·paper', '·titled', '·"', 'A', 'ffect', '·dynamics', ',', '·bere', 'av', 'ement', '·and',
       '·resilience', '·to', '·loss', '"', '·(', '2', '0', '0', '7', ')?↵', 'Authors', ':', '·Kar', 'in', '·G', '.', '·Co', 'if', 'man']
GRP = [0] * 9 + [1] * 11 + [2] * 9 + [3] * 7
GCOL = ['#EEF1F5', '#FFF1DE', '#E8F0FA', '#EAF6EC']; GNAME = ['question', 'title (11 tokens)', 'after the title', 'author name (teacher-forced)']
TAIL = list(range(20, 29)); NAME = list(range(29, 36)); TITLE = list(range(9, 20)); COLON = 28

def t(x, y, s, size=14, fill=INK, anchor='start', font=PH, weight=None, extra=''):
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-family="{font}"{w}{extra}>{s}</text>'

def tokrow(x0, y0, cw, hi=None, ring=None, groups=True, lab=9.5):
    """real token boxes; hi: idx -> fill colour (affected positions), ring: idx -> stroke colour."""
    hi = hi or {}; ring = ring or {}; o = []
    for i, (tk, g) in enumerate(zip(TOK, GRP)):
        x = x0 + i * cw
        fill = hi.get(i, GCOL[g]); st = ring.get(i, '#C9CED6'); sw = 2.2 if i in ring else 1
        o.append(f'<rect x="{x + 1:.1f}" y="{y0:.1f}" width="{cw - 2:.1f}" height="15" rx="3" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
        o.append(f'<text x="{x + cw / 2:.1f}" y="{y0 - 3:.1f}" font-size="{lab}" fill="{INK}" text-anchor="start" font-family="{SANS}" '
                 f'transform="rotate(-55 {x + cw / 2:.1f} {y0 - 3:.1f})">{H.escape(tk)}</text>')
    if groups:
        for g, (a, b) in enumerate([(0, 9), (9, 20), (20, 29), (29, 36)]):
            xa, xb = x0 + a * cw + 2, x0 + b * cw - 2
            o.append(f'<path d="M{xa:.1f} {y0 + 19:.1f} V{y0 + 23:.1f} H{xb:.1f} V{y0 + 19:.1f}" fill="none" stroke="{GREY}" stroke-width="1"/>')
            o.append(t((xa + xb) / 2, y0 + 34, GNAME[g], 10.5, GREY, 'middle', SANS))
    return ''.join(o)
def tx(x0, cw, i): return x0 + i * cw + cw / 2

def section(slot, label, title, part, body, overlays, tsize=30):
    pid = slot.replace('-', '')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" role="img" aria-label="{H.escape(label)}"><defs>'
           f'<pattern id="{pid}g" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#FAEEEE" stroke-width="1"/></pattern>'
           f'<marker id="{pid}a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
           f'<marker id="{pid}o" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{ORANGE}"/></marker>'
           f'<pattern id="{pid}h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#9AA3B2" stroke-width="2.2"/></pattern>'
           f'</defs><rect width="1280" height="720" fill="#FFFBFB"/><rect width="1280" height="720" fill="url(#{pid}g)"/>'
           + t(70, 58, title, tsize, INK, font=CAV, weight=700)
           + f'<g data-name="section tag"><rect x="{1254 - 9 * len(part) - 26:.1f}" y="16" width="{9 * len(part) + 26:.1f}" height="28" rx="10" fill="none" stroke="{BLUE}" stroke-width="2"/>'
           + t(1254 - (9 * len(part) + 26) / 2, 36, part, 16, BLUE, 'middle') + '</g>'
           + body.replace('#ARW', f'#{pid}a').replace('#ARO', f'#{pid}o').replace('#HATCH', f'#{pid}h') + '</svg>')
    return (f'<section class="slide mf" aria-label="{H.escape(label)}" data-slot="{slot}"><span class="tag" style="display:none">{H.escape(label)}</span>'
            f'{svg}{overlays}<span class="pg"></span></section>')

def ask(s, top=70): return f'<p class="askl abs" style="left:70px;top:{top}px;width:1120px;color:#D9772B"><b>Now asking:</b> {s}</p>'
def tagrow(inner, top=98, left=70): return f'<div style="position:absolute;z-index:4;left:{left}px;top:{top}px;font-size:12.5px;font-family:{SANS};color:{GREY}">{inner}</div>'
def soln(s, top=650, label='So (this slide)'): return f'<div class="soln" style="left:70px;top:{top}px;width:1140px"><b>{label}:</b> {s}</div>'
def cats(left, top, width, items, size=13):
    out = f'<div class="cats" style="left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;line-height:1.24">'
    for k, v, subs in items:
        out += f'<div class="it"><span class="k">{k}:</span> {v}</div>' + ''.join(f'<div class="sb">– {s}</div>' for s in subs)
    return out + '</div>'
SEP = ' <span style="color:#8a8f98">·</span> '
def fxu(left, top, width, formulas, nline, keys, size=11):
    return (f'<div class="fxu" style="left:{left}px;top:{top}px;width:{width}px"><div>{SEP.join(tex(x, size) for x in formulas)}</div>'
            f'<div>{tex(ntex(nline), size)}</div>' + ''.join(f'<div class="fxkey">{H.escape(k)}</div>' for k in keys) + '</div>')
def q(n): return f'<span class="q">{n}</span>'
def qsvg(x, y, n, col=ORANGE):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{col}"/>' + t(x, y + 4.5, str(n), 12, '#fff', 'middle', SANS, 700)
def ring(x, y, r=8, col=ORANGE): return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{col}" stroke-width="2.6"/>'
def box(x, y, w, h, fill='#fff', st=INK, rx=8, sw=1.6, dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{st}" stroke-width="{sw}"{d}/>'
def arrow(x1, y1, x2, y2, col=INK, w=1.8, head='#ARW', dash=''):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{d} marker-end="url({head})"/>'
def axes(x0, y0, x1, y1, ymin, ymax, ticks, fmt, ylab, grid=True):
    o = []
    def Y(v): return y0 - (v - ymin) / (ymax - ymin) * (y0 - y1)
    for v in ticks:
        yy = Y(v)
        if grid: o.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="#E7DADA" stroke-width="1" stroke-dasharray="3 4"/>')
        o.append(f'<line x1="{x0 - 5}" y1="{yy:.1f}" x2="{x0}" y2="{yy:.1f}" stroke="{INK}" stroke-width="1.4"/>' + t(x0 - 8, yy + 4, fmt(v), 12, GREY, 'end'))
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    o.append(t(x0 + 6, y1 + 2, ylab, 12, GREY))
    return ''.join(o), Y

# ================================================================ data
a32 = rd('summary_a32/a32_table.csv'); a32j = json.load(open(R + 'summary_a32/a32_results.json'))
a25 = {(r['grp'], r['cond']): r for r in rd('summary_a25/a25_rates.csv')}
a21 = {(r['grp'], r['cond']): r for r in rd('summary_a21/rates.csv')}
unl = rd('summary_a25_unlock/unlock_table.csv')
def U(layer, beta, quantity): return next(r for r in unl if r['layer'] == str(layer) and r['beta'] == str(beta) and r['quantity'] == quantity)
a25j = json.load(open(R + 'summary_a25/a25_results.json'))
a27 = rd('summary_a27/contrasts.csv'); a27j = json.load(open(R + 'summary_a27/a27_results.json'))
def C27(fam, layer, beta, grp='A'): return next(r for r in a27 if r['grp'] == grp and r['family'] == fam and r['layer'] == str(layer) and r['beta'] == str(beta))
a31 = rd('summary_a31/a31_dla_by_layer.csv'); a31j = json.load(open(R + 'summary_a31/a31_results.json'))
a31rep = open(R + 'summary_a31/a31_report.md').read()

frag = {}

# ================================================================ Part 5: route (single-layer edge cuts)
def page_route():
    slot = 'route'
    L = [40, 42, 44, 46, 48, 50, 52, 54, 56]
    E = [('name<-title', 'name ← title', ORANGE), ('name<-tail', 'name ← after-title', BLUE), ('tail<-title', 'after-title ← title', GREEN),
         ('colon<-title', '“:” ← title', PURPLE), ('name<-colon', 'name ← “:”', GREY)]
    cell = {(r['window'], r['edge']): r for r in a32}
    carries = {(c['window'], c['edge']) for c in a32j['carries']}
    dom = {d['window'] for d in a32j['dominant_edge_rule'] if d['verdict'].startswith('information in')}
    b = []
    # method schematic: tokens + the 5 edges (attention from receiver to sender), one layer cut at a time
    x0, cw, y0 = 70, 15.6, 172
    b.append(t(70, 240, 'Method: cut all heads of ONE attention edge at ONE layer, then read the score at the output', 14, INK, weight=700))
    b.append(tokrow(x0, y0, cw, ring={i: ORANGE for i in TITLE} | {COLON: PURPLE}, groups=False))
    arcs = [(14.5, 32, ORANGE, -46), (24, 32, BLUE, -30), (14.5, 24, GREEN, -22), (14.5, COLON, PURPLE, -36), (COLON, 32, GREY, -16)]
    for (a_, b_, col, h) in arcs:
        xa, xb = x0 + a_ * cw + cw / 2, x0 + b_ * cw + cw / 2
        b.append(f'<path d="M{xb:.1f} {y0 + 16:.1f} C{xb:.1f} {y0 + 16 - h * 1.0:.1f} {xa:.1f} {y0 + 16 - h * 1.0:.1f} {xa:.1f} {y0 + 16:.1f}" '
                 f'fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="5 3"/>')
    b.append(t(70, 258, '✂ one layer l at a time: L40, L42, …, L56 · edges drawn under the tokens', 12, RED))
    # control schematic: none vs edge cut; S = true − mean of false_0…false_4
    yc = 268
    b.append(box(70, yc, 250, 52, '#fff', GREY)); b.append(t(82, yc + 20, 'nothing cut → S(none)', 13, INK, weight=700))
    b.append(t(82, yc + 40, 'S = nlr(true) − mean nlr(false_0…false_4)', 11.5, GREY, font=SANS))
    b.append(box(350, yc, 250, 52, '#FFF4EC', ORANGE)); b.append(t(362, yc + 20, 'edge e cut at layer l → S(e, l)', 13, INK, weight=700))
    b.append(t(362, yc + 40, 'same papers, same five false titles', 11.5, GREY, font=SANS))
    b.append(t(335, yc + 31, '−', 22, INK, 'middle', weight=700))
    b.append(t(70, yc + 72, 'loss = S(none) − S(e, l): the part of the paper signal that needed that edge at that layer', 12.5, INK))
    # result chart: heatmap edges × layers, share of S
    hx, hy, cwh, ch = 190, 384, 46, 29
    b.append(t(70, hy - 12, 'Result: loss as % of S(none), per edge and single layer', 14, INK, weight=700))
    mx = max(float(r['share_of_S']) for r in a32)
    for j, l in enumerate(L):
        b.append(t(hx + j * cwh + cwh / 2, hy + 5 * ch + 16, f'L{l}', 12, GREY, 'middle'))
    for i, (key, lab, col) in enumerate(E):
        b.append(t(hx - 8, hy + i * ch + ch / 2 + 4, lab, 12.5, col, 'end', weight=700))
        for j, l in enumerate(L):
            w = f'L{l}-{l}'; r = cell[(w, key)]; sh = float(r['share_of_S'])
            a = max(0.0, sh) / mx
            fill = f'rgba(217,119,43,{0.08 + 0.80 * a:.2f})' if sh > 0 else '#F3F4F6'
            b.append(f'<rect x="{hx + j * cwh + 1:.1f}" y="{hy + i * ch + 1:.1f}" width="{cwh - 2}" height="{ch - 2}" rx="3" fill="{fill}" stroke="#E7DADA"/>')
            if (w, key) in carries:
                b.append(f'<rect x="{hx + j * cwh + 1:.1f}" y="{hy + i * ch + 1:.1f}" width="{cwh - 2}" height="{ch - 2}" rx="3" fill="none" stroke="{INK}" stroke-width="2.4"/>')
                b.append(t(hx + j * cwh + cwh / 2, hy + i * ch + ch / 2 + 4.5, num(f'{100 * sh:.2f}', f'single-layer loss share {lab} {w}', 'addendum 32 · summary_a32/a32_table.csv share_of_S'), 11.5, INK, 'middle', SANS, 700))
    # dominance marks (frozen rule) at L48, L52
    for j, l in enumerate(L):
        if f'L{l}-{l}' in dom:
            xx = hx + j * cwh + cwh / 2
            b.append(f'<line x1="{xx:.1f}" y1="{hy - 4}" x2="{xx:.1f}" y2="{hy + 5 * ch + 2}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    j48, j52 = L.index(48), L.index(52)
    b.append(qsvg(hx + j48 * cwh + cwh / 2 - 12, hy - 18, 1)); b.append(qsvg(hx + j52 * cwh + cwh / 2 + 12, hy - 18, 1))
    b.append(t(hx + 9 * cwh + 6, hy + 12, 'L48, L52:', 11.5, RED, weight=700)); b.append(t(hx + 9 * cwh + 6, hy + 26, 'name ← title', 11.5, RED))
    b.append(t(hx + 9 * cwh + 6, hy + 40, 'beats every', 11.5, RED)); b.append(t(hx + 9 * cwh + 6, hy + 54, 'other edge', 11.5, RED))
    b.append(qsvg(hx + 9 * cwh + 14, hy + 5 * ch - 30, 2)); b.append(t(hx + 9 * cwh + 26, hy + 5 * ch - 26, 'max 1.25%', 11.5, INK, weight=700))
    b.append(f'<rect x="{hx}" y="{hy + 5 * ch + 24}" width="14" height="10" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    b.append(t(hx + 20, hy + 5 * ch + 33, 'framed = carries information (loss > 0 after Holm over 45 cells); darker = larger loss', 11, GREY, font=SANS))
    mxs = num(f'{100 * mx:.2f}%', 'largest single-layer loss share (name ← title, L48)', 'addendum 32 · summary_a32/a32_table.csv share_of_S max')
    n6 = [c for c in a32j['carries']]
    num('6 of 45', 'cells that carry information (Holm)', 'addendum 32 · summary_a32/a32_results.json carries')
    num('L48, L52', 'layers where the frozen dominance rule names name ← title', 'addendum 32 · summary_a32/a32_results.json dominant_edge_rule')
    num('0.328', 'S(none)', 'existing slide {{p:75}} / {{p:77}}')
    num('600 (300 + 300)', 'papers in the sub-sample', 'existing slide {{p:75}}; prereg addendum 32 §2')
    ov = ask('which single layers does each attention edge need, or is the route spread over many layers?')
    ov += tagrow('<span class="tg lsup">locked · supported</span> single-layer route located &nbsp;·&nbsp; evidence type: intervention ▲ (edge knockout)')
    ov += fxu(70, 566, 560, [r'$\mathrm{loss}(e,l)=S(\mathrm{none})-S(e\ \mathrm{cut\ at}\ l)$', r'$S=\overline{\mathrm{nlr}}(\mathrm{true})-\overline{\mathrm{nlr}}(\mathrm{false}_{0..4})$'],
              'n = 600 papers (300 target + 300 control) · 5 edges × 9 layers = 45 cells, Holm', ['loss > 0: that edge at that layer carries part of the paper signal'])
    ov += cats(668, 128, 560, [
        ('Method', 'one attention edge (all heads) cut at <b>one</b> layer, L40–L56; same papers and five false titles as the window test (slide {{p:75}}).', []),
        (q(1) + ' Result', f'<span class="mk">name ← title carries information at L44, L48, L52, L54</span>; at <b>L48</b> and <b>L52</b> it beats every other edge.', [
            'also small: “:” ← title at L50 and name ← “:” at L44;', f'<b>6 of 45</b> cells pass Holm; none reversed.']),
        (q(2) + ' Size', f'each single cut removes <b>at most {mxs}</b> of S(none) = 0.328.', []),
        ('Control', 'S already subtracts the five false titles, so names that are easy to guess do not count.', []),
        ('Caveat', '<span class="ul">a single-layer cut is a lower bound: the other layers can carry the same information</span>; 600-paper sub-sample.', []),
        ('Compare', 'the 4-layer windows (slide {{p:75}}) cost up to 3.5% — the information is spread over neighbouring layers.', []),
    ])
    ov += soln('the title reaches the names through many layers in parallel; name ← title at L48 and L52 is the strongest single step, but no single layer is a bottleneck '
               '<span class="st c2">locked · supported</span>')
    frag[slot] = section(slot, 'Single-layer route: no single layer is a bottleneck', 'Cutting one layer at a time: name ← title helps a little at L44–L54, no bottleneck',
                         'Part 5 · route + H3', ''.join(b), ov, 28)

# ================================================================ Part 5: injection (probe author direction vs own title signal)
def page_injection():
    slot = 'injection'
    b = []
    x0, cw, y0 = 70, 15, 176
    b.append(t(70, 124, 'Method: add a push at the after-title positions (prefill) at L48 or L52, before the late MLP writer; then let the model answer', 13.5, INK, weight=700))
    b.append(tokrow(x0, y0, cw, hi={i: '#FFE1C2' for i in TAIL}, ring={i: ORANGE for i in TAIL}, lab=9))
    xt = x0 + 24.5 * cw
    b.append(arrow(xt + 40, y0 + 44, xt + 6, y0 + 18, ORANGE, 2.2, '#ARO')); b.append(t(xt + 44, y0 + 50, '+ v at L48 / L52', 12.5, ORANGE, 'start', weight=700))
    # two kinds of push (side boxes) with their controls
    bx = 640
    b.append(box(bx, 120, 280, 98, '#F6F7F9', GREY)); b.append(t(bx + 10, 140, '① push = the paper’s own title signal', 13, INK, weight=700))
    b.append(t(bx + 10, 158, 'v = β·Δ, Δ = h(true title) − mean h(false)', 11.5, GREY, font=SANS))
    b.append(t(bx + 10, 176, 'controls: another paper’s Δ, random', 11.5, GREY, font=SANS)); b.append(t(bx + 10, 194, '(same norm), no push', 11.5, GREY, font=SANS))
    b.append(t(bx + 10, 211, 'β = 1, 2, 4', 11.5, GREY, font=SANS))
    b.append(box(bx + 296, 120, 284, 98, '#EEF4FB', BLUE)); b.append(t(bx + 306, 140, '② push = the probe’s author direction', 13, INK, weight=700))
    b.append(t(bx + 306, 158, 'v = β·‖Δ‖·u(this paper’s first author)', 11.5, GREY, font=SANS))
    b.append(t(bx + 306, 176, 'controls: another author’s direction,', 11.5, GREY, font=SANS)); b.append(t(bx + 306, 194, 'random (same norm), no push', 11.5, GREY, font=SANS))
    b.append(t(bx + 306, 211, 'β = 1, 2 in range · β = 4 outside', 11.5, GREY, font=SANS))
    # two charts, same y scale: group A (recognised) first-author surname written, L52
    def chart(cx, title, rows, base, colours, labels, note_idx=None, hatch_b4=False):
        o = [t(cx, 262, title, 13.5, INK, weight=700)]
        ax, Y = axes(cx + 40, 446, cx + 560, 286, 0, 0.20, [0, 0.05, 0.10, 0.15, 0.20], lambda v: f'{100 * v:.0f}%', 'first author’s surname written (recognised papers)')
        o.append(ax)
        o.append(f'<line x1="{cx + 40}" y1="446" x2="{cx + 560}" y2="446" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
        gw = 160
        for g, beta in enumerate([1, 2, 4]):
            gx = cx + 70 + g * gw
            for k, (cond, col) in enumerate(zip(rows, colours)):
                v = float(cond[beta])
                xx = gx + k * 34; yy = Y(v)
                o.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="30" height="{446 - yy:.1f}" rx="2" fill="{col}"/>')
                if hatch_b4 and beta == 4:
                    o.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="30" height="{446 - yy:.1f}" rx="2" fill="url(#HATCH)" opacity=".55"/>')
                if k == 0:
                    o.append(t(xx + 15, yy - 5, pct(v), 11.5, INK, 'middle', SANS, 700))
            o.append(t(gx + 50, 463, f'L52 · β{beta}' + (' (outside range)' if hatch_b4 and beta == 4 else ''), 11.5, GREY, 'middle', SANS))
        yb = Y(base)
        o.append(f'<line x1="{cx + 40}" y1="{yb:.1f}" x2="{cx + 560}" y2="{yb:.1f}" stroke="{ORANGE}" stroke-width="1.8" stroke-dasharray="6 4"/>')
        o.append(t(cx + 556, yb - 5, f'no push {pct(base)}', 11.5, '#B54708', 'end', SANS))
        lx = cx + 330
        for k, (lab, col) in enumerate(zip(labels, colours)):
            o.append(f'<rect x="{lx + k * 82}" y="254" width="12" height="10" fill="{col}"/>' + t(lx + k * 82 + 16, 263, lab, 11.5, INK))
        return ''.join(o)
    base_a = float(a25[('A', 'base')]['first_sur'])
    own = {bb: a21[('A', f'own_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}; mis21 = {bb: a21[('A', f'mis_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}
    rnd21 = {bb: a21[('A', f'rand_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}
    gold = {bb: a25[('A', f'gold_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}; mis25 = {bb: a25[('A', f'mis_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}
    rnd25 = {bb: a25[('A', f'rand_L52_b{bb}')]['first_sur'] for bb in (1, 2, 4)}
    base21 = float(a21[('A', 'base')]['first_sur'])
    b.append(chart(70, '① own title signal: no gain', [own, mis21, rnd21], base21, [ORANGE, '#9AA3B2', '#C9CED6'], ['own Δ', 'another Δ', 'random']))
    b.append(chart(660, '② author direction: name gets written', [gold, mis25, rnd25], base_a, [BLUE, '#9AA3B2', '#C9CED6'], ['this author', 'another author', 'random'], hatch_b4=True))
    # markers
    Yf = lambda v: 446 - v / 0.20 * 160
    b.append(ring(660 + 70 + 160 + 15, Yf(float(gold[2])) + 8, 9, ORANGE)); b.append(qsvg(660 + 70 + 160 + 15 - 34, Yf(float(gold[2])) - 8, 2))
    b.append(qsvg(70 + 70 + 160 + 15, Yf(float(own[2])) - 26, 1))
    num(pct(base_a), 'group A first-author surname written, no push (probe-direction run)', 'addendum 25 · summary_a25/a25_rates.csv A,base,first_sur')
    num(pct(gold[2]), 'group A, this author’s direction, L52 β2', 'addendum 25 · summary_a25/a25_rates.csv A,gold_L52_b2')
    for bb in (1, 4): num(pct(gold[bb]), f'group A, this author’s direction, L52 β{bb}', 'addendum 25 · summary_a25/a25_rates.csv')
    for bb in (1, 2, 4): num(pct(own[bb]), f'group A, own Δ, L52 β{bb}', 'addendum 21 · summary_a21/rates.csv first_sur')
    num(pct(base21), 'group A, no push (title-signal run)', 'addendum 21 · summary_a21/rates.csv A,base,first_sur')
    wd = U(52, 2, 'write donor: donor dir - base'); wg = U(52, 2, 'write gold: gold dir - base'); sp = U(52, 1, 'first_sur: gold - base'); sym = U(48, 2, 'symmetry: (gold dir - base)[gold] - (donor dir - base)[donor]')
    wds = num(f3(wd['A']), 'another author’s direction writes THAT author (A, L52 β2)', 'addendum 25 (post hoc, exploratory) · summary_a25_unlock/unlock_table.csv write donor')
    wgs = num(f3(wg['A']), 'this author’s direction writes this author (A, L52 β2)', 'addendum 25 (post hoc, exploratory) · summary_a25_unlock/unlock_table.csv write gold')
    sps = num(f3(sp['A_minus_B']) + ' ' + ci(sp['AmB_lo'], sp['AmB_hi']), 'recognised − not recognised, gold − base, L52 β1', 'addendum 25 (post hoc, exploratory) · summary_a25_unlock/unlock_table.csv')
    syms = num(f3(sym['A_minus_B']) + ' ' + ci(sym['AmB_lo'], sym['AmB_hi']), 'recognised − not recognised, symmetry contrast, L48 β2', 'addendum 25 (post hoc, exploratory) · summary_a25_unlock/unlock_table.csv')
    P564 = num(f3(C27('P', 56, 4)['est']), 'own − another, L56 β4 (why pushing hurts)', 'addendum 27 · summary_a27/contrasts.csv A,P')
    num('599 + 599', 'papers A + B in the probe-direction run', 'addendum 25 · summary_a25/a25_results.json n_A, n_B')
    num('600 + 600', 'papers A + B in the title-signal run', 'addendum 21 · summary_a21/a21_results.json by_grp')
    ov = ask('if we push the information that has already arrived, or the author direction the probe reads, does the model write the author?', 68)
    ov += tagrow('① <span class="tg lnot">locked · not supported</span> &nbsp; ② <span class="tg lsup">locked · supported</span> direction usable &nbsp;+&nbsp; '
                 '<span class="tg expl">exploratory</span> mostly a write channel &nbsp;·&nbsp; evidence type: intervention ▲ (injection)', 96)
    ov += fxu(110, 474, 520, [r'$G=\mathrm{rate}(\mathrm{own}\ \Delta)-\mathrm{rate}(\mathrm{no\ push})$', r'$S=\mathrm{rate}(\mathrm{own})-\mathrm{rate}(\mathrm{another})$'],
              'n = 600 recognised + 600 not recognised papers', ['G ≈ 0: pushing the title signal adds nothing'])
    ov += fxu(700, 474, 520, [r'$G=\mathrm{rate}(\mathrm{author\ dir.})-\mathrm{rate}(\mathrm{no\ push})$', r'$S=\mathrm{rate}(\mathrm{this})-\mathrm{rate}(\mathrm{another\ author})$'],
              'n = 599 recognised + 599 not recognised papers', ['S > 0: this author’s direction writes this paper’s author more'])
    ov += cats(70, 526, 560, [
        (q(1) + ' Result', f'own title signal: <b>{pct(base21)} → {pct(own[2])}</b> (L52 β2), no gain at any layer or β; see slide {{{{p:78}}}}.', []),
        ('Why', f'the damage is <b>direction-driven</b>, and near the writer the paper’s own push hurts more than another paper’s (P {P564} at L56 β4; slide {{{{new:injection-why}}}}).', []),
        ('So', '<span class="mk">more of what already arrived does not help</span>.', []),
    ], 12.5)
    ov += cats(660, 530, 560, [
        (q(2) + ' Result', f'author direction: <b>{pct(base_a)} → {pct(gold[2])}</b> (L52 β2) vs <b>{pct(mis25[2])}</b> for another author’s direction.', []),
        ('Control', f'<span class="ul">another author’s direction also writes <i>that</i> author ({wds} vs {wgs})</span> → mainly a write channel;', [
            f'recognised-specific extra only {sps} (L52 β1), {syms} (L48 β2) — small.']),
    ], 12.5)
    ov += soln('the late layers can write a name when handed the answer’s direction, but not when handed more of the arrived title signal; '
               'the direction works mainly as a write channel, with a small recognised-specific part <span class="st c2">locked</span> <span class="st c3">exploratory</span>', 650)
    frag[slot] = section(slot, 'Injection: author direction vs own title signal', 'Two pushes before the writer: the author direction writes names, more title signal does not',
                         'Part 5 · route + H3', ''.join(b), ov, 27)

# ================================================================ Part 6: late suppression (DLA + rise-then-fall)
def page_suppression():
    slot = 'suppression'
    b = []
    x0, cw, y0 = 70, 15.6, 182
    b.append(t(70, 124, 'Method: at the first author’s first surname token, read the true token’s rank layer by layer (L56 → output)', 13.5, INK, weight=700))
    b.append(tokrow(x0, y0, cw, hi={33: '#FFE1C2'}, ring={33: ORANGE}))
    b.append(t(x0 + 33.5 * cw, y0 + 50, 'scored token “·Co”', 12, ORANGE, 'end', weight=700))
    # rule schematic: rank trajectory with rise then fall
    sx, sy = 640, 132
    b.append(box(sx, sy - 6, 300, 112, '#fff', GREY)); b.append(t(sx + 10, sy + 12, 'Rule (fixed before data): rise then fall', 12.5, INK, weight=700))
    pts = [(56, 0.5), (57, 0.75), (58, 1.0), (59, 1.25), (60, 1.1), (61, 0.8), (62, 0.65), (63, 0.55)]
    px = lambda l: sx + 30 + (l - 56) * 34; py = lambda v: sy + 92 - v * 50
    b.append(f'<polyline points="{" ".join(f"{px(l):.1f},{py(v):.1f}" for l, v in pts)}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    for l, v in pts: b.append(f'<circle cx="{px(l):.1f}" cy="{py(v):.1f}" r="2.6" fill="{BLUE}"/>')
    b.append(arrow(px(56) + 4, py(0.5), px(59) - 6, py(1.25) + 4, RED, 1.4)); b.append(arrow(px(59) + 6, py(1.25) + 4, px(63) - 4, py(0.55), RED, 1.4))
    b.append(t(px(57.2), py(1.25) - 2, '≥ 2× better', 11, RED, 'middle', SANS)); b.append(t(px(61.4), py(1.18), '≥ 2× worse', 11, RED, 'middle', SANS))
    for l in (56, 59, 63): b.append(t(px(l), sy + 104, 'out' if l == 63 else f'L{l}', 10.5, GREY, 'middle', SANS))
    b.append(box(sx + 316, sy - 6, 274, 112, '#F6F7F9', GREY)); b.append(t(sx + 326, sy + 12, 'Also: who pushes the logit, layer by layer', 12.5, INK, weight=700))
    b.append(t(sx + 326, sy + 32, 'direct contribution of each attention', 11.5, GREY, font=SANS)); b.append(t(sx + 326, sy + 48, 'and MLP output to the true token’s', 11.5, GREY, font=SANS))
    b.append(t(sx + 326, sy + 64, 'final logit (L40–L63)', 11.5, GREY, font=SANS))
    b.append(t(sx + 326, sy + 86, 'Control: target vs control papers,', 11.5, INK, font=SANS)); b.append(t(sx + 326, sy + 102, 'compared within citation bins', 11.5, INK, font=SANS))
    # chart 1: DLA MLP + attention per layer, target vs control
    cx = 70
    b.append(t(cx, 268, 'Contribution to the true token’s final logit, by layer', 13.5, INK, weight=700))
    ax, Y = axes(cx + 44, 470, cx + 560, 290, -0.2, 3.2, [0, 1, 2, 3], lambda v: f'{v:.0f}', 'logit units')
    b.append(ax)
    X = lambda l: cx + 44 + (l - 40) / 23 * 500
    b.append(f'<rect x="{X(56.5):.1f}" y="290" width="{X(61.5) - X(56.5):.1f}" height="180" fill="#E8F0FA" opacity=".8"/>')
    b.append(t((X(56.5) + X(61.5)) / 2, 462, 'L57–L61', 11.5, BLUE, 'middle', SANS, 700))
    b.append(f'<line x1="{cx + 44}" y1="{Y(0):.1f}" x2="{cx + 548}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.6"/>')
    for l in (40, 44, 48, 52, 56, 60, 63): b.append(t(X(l), 486, f'L{l}', 11.5, GREY, 'middle'))
    ser = [('target', 'dla_mlp_logit', BLUE, '', 'MLP · target'), ('control', 'dla_mlp_logit', GREY, '', 'MLP · control'),
           ('target', 'dla_attn_logit', BLUE, '5 4', 'attention · target'), ('control', 'dla_attn_logit', GREY, '5 4', 'attention · control')]
    for g, col_, c, dash, lab in ser:
        pts = [(int(r['layer']), float(r[col_])) for r in a31 if r['group'] == g]
        d = f' stroke-dasharray="{dash}"' if dash else ''
        b.append(f'<polyline points="{" ".join(f"{X(l):.1f},{Y(v):.1f}" for l, v in pts)}" fill="none" stroke="{c}" stroke-width="2.2"{d}/>')
    tg62 = next(float(r['dla_mlp_logit']) for r in a31 if r['group'] == 'target' and r['layer'] == '62')
    b.append(t(X(62) - 6, Y(tg62) - 6, 'MLP L62 ' + num(f'{tg62:.2f}', 'target MLP DLA logit at L62', 'addendum 31 · summary_a31/a31_dla_by_layer.csv'), 11, BLUE, 'end', SANS, 700))
    lg = [('MLP · target', BLUE, ''), ('MLP · control', GREY, ''), ('attention · target', BLUE, '5 4'), ('attention · control', GREY, '5 4')]
    for k, (lab, c, dash) in enumerate(lg):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        b.append(f'<line x1="{cx + 60}" y1="{318 + k * 15}" x2="{cx + 84}" y2="{318 + k * 15}" stroke="{c}" stroke-width="2.2"{d}/>' + t(cx + 90, 322 + k * 15, lab, 11.5, INK))
    # chart 2: rise-then-fall share, target vs control (primary) + all name tokens (secondary)
    m = re.search(r'primary: first author surname-first token\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', a31rep)
    n_, st_, tlo, thi, sc_, clo, chi, tc, tclo, tchi = m.groups()
    m2 = re.search(r'secondary: all name tokens\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', a31rep)
    _, st2, t2lo, t2hi, sc2, c2lo, c2hi, tc2, tc2lo, tc2hi = m2.groups()
    b.append(t(660, 268, 'Share of papers with rise-then-fall', 13.5, INK, weight=700))
    ax2, Y2 = axes(704, 470, 1230, 290, 0, 0.18, [0, 0.05, 0.10, 0.15], lambda v: f'{100 * v:.0f}%', 'share of papers')
    b.append(ax2); b.append(f'<line x1="704" y1="470" x2="1230" y2="470" stroke="{INK}" stroke-width="2"/>')
    bars = [('first author, first surname token', [(st_, tlo, thi, BLUE, 'target'), (sc_, clo, chi, '#9AA3B2', 'control')]),
            ('all name tokens', [(st2, t2lo, t2hi, BLUE, 'target'), (sc2, c2lo, c2hi, '#9AA3B2', 'control')])]
    for g, (lab, bs) in enumerate(bars):
        gx = 760 + g * 240
        for k, (v, lo, hi, c, gl) in enumerate(bs):
            v, lo, hi = float(v), float(lo), float(hi); xx = gx + k * 70
            b.append(f'<rect x="{xx}" y="{Y2(v):.1f}" width="56" height="{470 - Y2(v):.1f}" rx="2" fill="{c}"/>')
            b.append(f'<line x1="{xx + 28}" y1="{Y2(lo):.1f}" x2="{xx + 28}" y2="{Y2(hi):.1f}" stroke="{INK}" stroke-width="1.6"/>')
            b.append(t(xx + 28, Y2(hi) - 6, pct(v), 12, INK, 'middle', SANS, 700)); b.append(t(xx + 28, 484, gl, 11, GREY, 'middle', SANS))
        b.append(t(gx + 63, 500, lab, 11.5, INK, 'middle', SANS))
    b.append(ring(760 + 28, Y2(float(st_)) - 2, 11)); b.append(qsvg(760 + 28 - 26, Y2(float(st_)) - 10, 1))
    b.append(qsvg(1000 + 63, Y2(max(float(st2), float(sc2), float(c2hi))) - 34, 2))
    S1 = num(pct(st_), 'target share with rise-then-fall (primary token)', 'addendum 31 · summary_a31/a31_report.md primary share_target')
    S0 = num(pct(sc_), 'control share (primary token)', 'addendum 31 · summary_a31/a31_report.md share_control')
    TC = num(f3(tc) + ' ' + ci(tclo, tchi), 'target − control within citation bins (primary)', 'addendum 31 · summary_a31/a31_report.md tc_within_bin')
    num(f'[{pct(tlo)}, {pct(thi)}]', 'target CI', 'addendum 31 · summary_a31/a31_report.md'); num(f'[{pct(clo)}, {pct(chi)}]', 'control CI', 'addendum 31 · summary_a31/a31_report.md')
    TC2 = num(f3(tc2) + ' ' + ci(tc2lo, tc2hi), 'target − control, all name tokens', 'addendum 31 · summary_a31/a31_report.md secondary')
    num(pct(st2) + ' vs ' + pct(sc2), 'all-name-token shares target vs control', 'addendum 31 · summary_a31/a31_report.md secondary')
    comp = a31j.get('components', {}) if isinstance(a31j, dict) else {}
    num('1,186 (593 + 593)', 'papers', 'addendum 31 · summary_a31/a31_report.md n_papers; prereg addendum 31 §2')
    num('+0.040 [+0.036, +0.045]', 'MLP − attention loss mean L57–L61 (cited)', 'existing slide {{p:77}}')
    ov = ask('the average true-name rank keeps rising to the output; does it hide papers whose name rises after L56 and is then pushed down?', 68)
    ov += tagrow('<span class="tg lsup">locked · supported</span> late-suppression subgroup, more often in recognised papers (just above the bound) &nbsp;·&nbsp; '
                 'evidence type: readout ◉ (logit lens + direct logit attribution)', 96)
    ov += fxu(110, 510, 520, [r'$\mathrm{DLA}_l=r\,\langle c_l,\ g\odot W_U[t]\rangle,\ \ c\in\{\mathrm{attn},\mathrm{MLP}\}$'],
              'n = 1,186 papers (593 target + 593 control)', ['DLA > 0: this layer part pushes the true name up at the output'])
    ov += fxu(700, 510, 530, [r'$\mathrm{RTF}:\ \max_{57..62}y_l-y_{56}\geq0.301\ \wedge\ \max_{57..62}y_l-y_{63}\geq0.301$', r'$y_l=\log_{10}(1/\mathrm{rank}_l)$'],
              'n = 593 target + 593 control papers · team-bootstrap 95% CI', ['share > 0: some papers’ true name rises after L56, then falls by the output'])
    ov += cats(70, 572, 1150, [
        (q(1) + ' Result', f'rise-then-fall in <b>{S1}</b> of target vs <b>{S0}</b> of control papers; <span class="mk">T − C {TC}</span> → subgroup more frequent when the paper is recognised.', []),
        (q(2) + ' Control', f'over all name tokens the share is about the same in both groups (T − C {TC2}); <span class="ul">the T − C lower bound is just above 0</span>.', []),
    ], 12.5)
    ov += soln('the name is written by the late MLPs (slide {{p:77}}), and in about 1 in 8 recognised papers it rises after L56 and is then pushed back down — '
               'one concrete way “recognised but not said” fails at the writing step <span class="st c2">locked</span>', 650)
    frag[slot] = section(slot, 'Late suppression in a subgroup', 'In about 1 in 8 recognised papers the name rises after L56 and then falls',
                         'Part 6 · writing step', ''.join(b), ov, 29)

# ================================================================ Part 6: direction asymmetry (why pushing hurts)
def page_pushdir():
    slot = 'injection-why'
    b = []
    x0, cw, y0 = 70, 15.6, 182
    b.append(t(70, 124, 'Method: same pushes at the after-title positions, at L48, L56 or L57; score = rank of every true name at the output', 13.5, INK, weight=700))
    b.append(tokrow(x0, y0, cw, hi={i: '#FFE1C2' for i in TAIL}, ring={i: ORANGE for i in TAIL}))
    # four kinds of push (same norm)
    kinds = [('own Δ', 'the paper’s own title signal', ORANGE), ('another Δ', 'another paper’s, same norm', '#9AA3B2'),
             ('norm only', 'longer along the state h', GREEN), ('direction only', 'Δ turned ⟂ h, same norm', RED)]
    for k, (a_, b_, c) in enumerate(kinds):
        xx = 640 + (k % 2) * 296; yy = 124 + (k // 2) * 50
        b.append(box(xx, yy, 284, 42, '#fff', c)); b.append(t(xx + 10, yy + 18, a_, 13, c, weight=700)); b.append(t(xx + 10, yy + 35, b_, 11.5, GREY, font=SANS))
    b.append(t(640, 236, 'contrasts fixed before data: N = norm only − none · O = direction only − none', 11.5, INK, font=SANS)); b.append(t(640, 251, 'P = own − another (at L56, L57)', 11.5, INK, font=SANS))
    # chart 1: N and O per cell
    cells = [(48, 1), (48, 2), (48, 4), (56, 1), (56, 2), (56, 4), (57, 1), (57, 2), (57, 4)]
    b.append(t(70, 268, 'Effect on the true names’ rank, by layer and push size β', 13.5, INK, weight=700))
    ax, Y = axes(114, 470, 1230, 290, -0.65, 0.05, [-0.6, -0.4, -0.2, 0], lambda v: f'{v:+.1f}'.replace('-', '−').replace('+0.0', '0'), 'Δ log10(1/rank) vs no push')
    b.append(ax); b.append(f'<line x1="114" y1="{Y(0):.1f}" x2="1230" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.8"/>')
    gw = 122
    for j, (l, bb) in enumerate(cells):
        gx = 140 + j * gw
        for k, fam, c in [(0, 'N', GREEN), (1, 'O', RED), (2, 'P', ORANGE)]:
            if fam == 'P' and l == 48: continue
            r = C27(fam, l, bb); v = float(r['est']); lo, hi = float(r['lo']), float(r['hi'])
            xx = gx + k * 30; y1, y2 = sorted([Y(0), Y(v)])
            b.append(f'<rect x="{xx}" y="{y1:.1f}" width="26" height="{max(1.2, y2 - y1):.1f}" rx="2" fill="{c}"/>')
            b.append(f'<line x1="{xx + 13}" y1="{Y(lo):.1f}" x2="{xx + 13}" y2="{Y(hi):.1f}" stroke="{INK}" stroke-width="1.3"/>')
            if fam == 'O' and bb == 4:
                b.append(t(xx + 13, Y(v) + 14, num(f3(v), f'direction-only effect L{l} β4', 'addendum 27 · summary_a27/contrasts.csv A,O'), 11, RED, 'middle', SANS, 700))
            if fam == 'P' and bb == 4:
                b.append(t(xx + 13, Y(v) + 14, num(f3(v), f'own − another L{l} β4', 'addendum 27 · summary_a27/contrasts.csv A,P'), 11, '#B54708', 'middle', SANS, 700))
        b.append(t(gx + 42, 486, f'L{l} · β{bb}', 11.5, GREY, 'middle', SANS))
    for k, (lab, c) in enumerate([('norm only − none (N)', GREEN), ('direction only − none (O)', RED), ('own − another (P)', ORANGE)]):
        b.append(f'<rect x="{640 + k * 196}" y="258" width="12" height="10" fill="{c}"/>' + t(640 + k * 196 + 16, 267, lab, 11.5, INK))
    b.append(f'<line x1="{140 + 3 * gw - 10}" y1="290" x2="{140 + 3 * gw - 10}" y2="470" stroke="{BLUE}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    b.append(t(140 + 3 * gw - 4, 462, 'L56–L57: right before the writer →', 11.5, BLUE, 'start', SANS, 700))
    r56 = C27('O', 56, 4); b.append(ring(140 + 5 * gw + 30 + 13, Y(float(r56['est'])), 10)); b.append(qsvg(140 + 5 * gw + 30 + 13 + 20, Y(float(r56['est'])) - 14, 1))
    rP = C27('P', 57, 4); b.append(qsvg(140 + 8 * gw + 60 + 13 + 18, Y(float(rP['est'])) - 6, 2))
    # verdict numbers
    nN = sum(1 for (l, bb) in cells if float(C27('N', l, bb)['est']) < 0 and float(C27('N', l, bb)['p_holm']) < 0.05)
    nO = sum(1 for (l, bb) in cells if float(C27('O', l, bb)['est']) < 0 and float(C27('O', l, bb)['p_holm']) < 0.05)
    num(f'{nO} of 9', 'direction-only cells Holm-significantly < 0', 'addendum 27 · summary_a27/contrasts.csv, a27_results.json O_cells_neg')
    num(f'{nN} of 9', 'norm-only cells Holm-significantly < 0 (L56 β4, L57 β4)', 'addendum 27 · summary_a27/a27_results.json N_cells_neg')
    o48 = num(f3(C27('O', 48, 1)['est']), 'direction-only L48 β1', 'addendum 27 · summary_a27/contrasts.csv')
    n57 = num(f3(C27('N', 57, 4)['est']), 'norm-only L57 β4', 'addendum 27 · summary_a27/contrasts.csv')
    p562 = num(f3(C27('P', 56, 2)['est']), 'own − another L56 β2', 'addendum 27 · summary_a27/contrasts.csv')
    num('600', 'recognised papers (group A)', 'addendum 27 · summary_a27/contrasts.csv n')
    ov = ask('more title signal did not help and at β4 even hurt (slide {{new:injection}}); is the damage the extra length of the push, its direction, or this paper’s own signal?', 68)
    ov += tagrow('<span class="tg lsup">locked · supported</span> damage is direction-driven; own hurts more than another near the writer &nbsp;·&nbsp; evidence type: intervention ▲ (injection)', 96)
    ov += fxu(110, 506, 1100, [r'$N=\mathrm{TF}(\mathrm{norm\ only})-\mathrm{TF}(\mathrm{none})$', r'$O=\mathrm{TF}(\mathrm{direction\ only})-\mathrm{TF}(\mathrm{none})$',
                               r'$P=\mathrm{TF}(\mathrm{own})-\mathrm{TF}(\mathrm{another})$', r'$\mathrm{TF}=\overline{\log_{10}(1/\mathrm{rank})}$'],
              'n = 600 recognised papers · team-bootstrap 95% CI, Holm within each family', ['O < 0: a push in a new direction (same length) lowers the true name'])
    ov += cats(70, 560, 1150, [
        (q(1) + ' Result', f'<span class="mk">direction-only pushes hurt in all {nO} cells</span> (from {o48} at L48 β1 to the large drops shown at L56–L57); '
                          f'length-only pushes hurt only at β4 near the writer ({nN} of 9 cells, e.g. {n57}).', []),
        (q(2) + ' Result', f'right before the writer the paper’s <b>own</b> signal hurts <b>more</b> than another paper’s (P {p562} at L56 β2, larger at β4) — the reverse of “own helps”.', []),
        ('Caveat', '<span class="ul">teacher-forced scores only; injection at the after-title positions only; one decomposition (length vs direction)</span>.', []),
    ], 12.5)
    ov += soln('the late writer is sensitive to the direction of its input, not just to how much signal arrives: extra paper signal near L56–L57 disrupts rather than helps '
               '<span class="st c2">locked · supported</span>', 650)
    frag[slot] = section(slot, 'Why pushing hurts: direction, not length', 'Pushing harder hurts through direction, and the paper’s own push hurts most near the writer',
                         'Part 5 · route + H3', ''.join(b), ov, 27)


# ================================================================ Part 6: direction asymmetry (H5, reversal curse) — addendum 30
a30t = {r['test'].split()[0]: r for r in rd('summary_a30/a30_tests.csv')}
a30d = {r['grp']: r for r in rd('summary_a30/a30_descriptive.csv')}
FWD = ['Co', 'if', 'man', ',', '·K', '.', '·G', '.,', '·…', '·(', '2', '0', '0', '7', ').', '·A', 'ffect', '·dynamics', ',', '·bere', 'av', 'ement', '·and', '·resilience', '·to', '·loss']
def toks(x0, y0, cw, tk, cols, lab=9.5):
    o = []
    for i, (w, c) in enumerate(zip(tk, cols)):
        x = x0 + i * cw
        o.append(f'<rect x="{x + 1:.1f}" y="{y0:.1f}" width="{cw - 2:.1f}" height="15" rx="3" fill="{c}" stroke="#C9CED6"/>')
        o.append(f'<text x="{x + cw / 2:.1f}" y="{y0 - 3:.1f}" font-size="{lab}" fill="{INK}" font-family="{SANS}" transform="rotate(-55 {x + cw / 2:.1f} {y0 - 3:.1f})">{H.escape(w)}</text>')
    return ''.join(o)
def page_asymmetry():
    slot = 'asymmetry'
    b = []
    r1, r2, r3 = a30t['R1'], a30t['R2'], a30t['R3']
    b.append(t(70, 124, 'Method: score the same papers in both directions', 13.5, INK, weight=700))
    # forward: citation prefix (authors) -> title scored
    b.append(t(70, 160, 'forward  authors → title', 12.5, ORANGE, weight=700))
    b.append(toks(70, 196, 18, FWD, ['#EAF6EC'] * 15 + ['#FFE1C2'] * 11))
    b.append(t(70 + 7 * 18, 230, 'citation prefix: true authors (Year).', 11, GREY, 'middle', SANS)); b.append(t(70 + 20.5 * 18, 230, 'title scored (true vs false_0…false_4)', 11, ORANGE, 'middle', SANS))
    # reverse: Stage 10 prompt title -> authors scored
    b.append(t(560, 160, 'reverse  title → authors', 12.5, BLUE, weight=700))
    rv = {i: '#FFF1DE' for i in TITLE}; rv.update({i: '#CFE2F5' for i in NAME})
    b.append(tokrow(560, 196, 14.8, hi=rv, groups=False, lab=8.5))
    b.append(t(560 + 14.5 * 14.8, 230, 'title given', 11, GREY, 'middle', SANS)); b.append(t(560 + 32.5 * 14.8, 230, 'authors scored', 11, BLUE, 'middle', SANS))
    # control schematic
    b.append(box(1110, 140, 130, 96, '#F6F7F9', GREY)); b.append(t(1120, 158, 'Control:', 12, INK, weight=700))
    for k, ln in enumerate(['another same-field', 'paper’s authors in', 'the prefix (F_id);', 'A vs B papers']):
        b.append(t(1120, 176 + k * 15, ln, 11, GREY, font=SANS))
    # chart 1: F_id by group (descriptive) + R1
    b.append(t(70, 268, 'Forward title likelihood from the true authors, beyond field', 13.5, INK, weight=700))
    ax, Y = axes(114, 470, 600, 290, 0, 0.8, [0, 0.2, 0.4, 0.6, 0.8], lambda v: f'{v:.1f}', 'F_id (log-prob per title token)')
    b.append(ax); b.append(f'<line x1="114" y1="470" x2="600" y2="470" stroke="{INK}" stroke-width="2"/>')
    for k, (g, lab, c) in enumerate([('A', 'recognised (A)', BLUE), ('B', 'not recognised (B)', '#9AA3B2')]):
        v = float(a30d[g]['F_id']); xx = 200 + k * 180
        b.append(f'<rect x="{xx}" y="{Y(v):.1f}" width="90" height="{470 - Y(v):.1f}" rx="2" fill="{c}"/>')
        b.append(t(xx + 45, Y(v) - 6, num(f'{v:.3f}', f'mean F_id group {g}', 'addendum 30 · summary_a30/a30_descriptive.csv'), 12.5, INK, 'middle', SANS, 700))
        b.append(t(xx + 45, 486, lab, 12, GREY, 'middle', SANS))
    R1 = num(f3(r1['est']) + ' ' + ci(r1['lo'], r1['hi']), 'R1: A − B of F_id within citation bins', 'addendum 30 · summary_a30/a30_tests.csv R1')
    b.append(qsvg(470, 310, 1)); b.append(t(484, 314, 'A − B ' + R1, 12, BLUE, 'start', SANS, 700))
    # chart 2: generation success, forward vs reverse, by group
    b.append(t(660, 268, 'Generation success on the same papers', 13.5, INK, weight=700))
    ax2, Y2 = axes(704, 470, 1230, 290, 0, 0.05, [0, 0.01, 0.02, 0.03, 0.04, 0.05], lambda v: f'{100 * v:.0f}%', 'share of papers')
    b.append(ax2); b.append(f'<line x1="704" y1="470" x2="1230" y2="470" stroke="{INK}" stroke-width="2"/>')
    for g_i, (g, lab) in enumerate([('A', 'recognised (A)'), ('B', 'not recognised (B)')]):
        gx = 760 + g_i * 240
        for k, (col_, c, nm) in enumerate([('fwd_success', ORANGE, 'authors → title'), ('rev_success', BLUE, 'title → authors')]):
            v = float(a30d[g][col_]); xx = gx + k * 74
            b.append(f'<rect x="{xx}" y="{Y2(v):.1f}" width="60" height="{max(1.2, 470 - Y2(v)):.1f}" rx="2" fill="{c}"/>')
            b.append(t(xx + 30, Y2(v) - 6, num(pct(v), f'{nm} success group {g}', 'addendum 30 · summary_a30/a30_descriptive.csv'), 12, INK, 'middle', SANS, 700))
        b.append(t(gx + 67, 486, lab, 12, GREY, 'middle', SANS))
    for k, (lab, c) in enumerate([('authors → title (title F1 ≥ 0.8)', ORANGE), ('title → authors (≥ 1 full true author)', BLUE)]):
        b.append(f'<rect x="{900}" y="{296 + k * 16}" width="12" height="10" fill="{c}"/>' + t(916, 305 + k * 16, lab, 11.5, INK))
    R2 = num(f3(r2['est']) + ' ' + ci(r2['lo'], r2['hi']), 'R2: forward success − reverse success, group A', 'addendum 30 · summary_a30/a30_tests.csv R2')
    b.append(ring(760 + 30, Y2(float(a30d['A']['fwd_success'])) + 6, 9)); b.append(qsvg(760 - 16, Y2(float(a30d['A']['fwd_success'])) - 2, 2))
    R3 = num(f3(r3['est']) + ' ' + ci(r3['lo'], r3['hi']), 'R3 (secondary): F_id predicts recognition probability beyond citations (std slope)', 'addendum 30 · summary_a30/a30_tests.csv R3')
    num('600 + 600', 'papers A + B', 'addendum 30 · a30_report.md')
    ov = ask('is “recognised but not said” a reversal curse: authors stored as authors → title, so recall from the title runs the wrong way?', 68)
    ov += tagrow('<span class="tg lnot">locked · not supported</span> reading “Reversed”: authors → title is slightly harder &nbsp;·&nbsp; '
                 'evidence type: behaviour (generation) + teacher-forced likelihood', 96)
    ov += fxu(110, 506, 500, [r'$F_{\mathrm{id}}=F_{\mathrm{spec}}(\mathrm{true\ authors})-F_{\mathrm{spec}}(\mathrm{other\ authors})$',
                              r'$F_{\mathrm{spec}}=\mathrm{lp}(\mathrm{true})-\overline{\mathrm{lp}}(\mathrm{false}_{0..4})$'],
              'n = 600 recognised + 600 not recognised papers', ['F_id > 0: the true authors make this title more likely than another field’s authors do'])
    ov += fxu(700, 506, 520, [r'$R_2=\mathrm{success}(\mathrm{authors}\to\mathrm{title})-\mathrm{success}(\mathrm{title}\to\mathrm{authors})$'],
              'n = 600 recognised papers, paired · team-bootstrap 95% CI, Holm over two tests', ['R2 > 0: authors → title is easier (what a reversal curse predicts)'])
    ov += cats(70, 562, 1150, [
        (q(1) + ' Result', f'given the true authors, the true title is <span class="mk">far more likely for recognised papers</span> (A − B {R1}) — the association is stored.', []),
        (q(2) + ' Result', f'but <b>generating the title from the authors is slightly harder</b> than recalling the authors from the title (R2 {R2}): locked reading “Reversed”.', []),
        ('Caveat', '<span class="ul">greedy decoding; one citation format; both success rates are low</span>; secondary: forward likelihood also predicts recognition beyond citations (' + R3 + ').', []),
    ], 12.5)
    ov += soln('the reversal-curse explanation is not supported: the authors–title association exists, but writing either side out is hard, '
               'which points back to the writing step <span class="st c2">locked</span>', 650)
    frag[slot] = section(slot, 'Direction asymmetry: not a reversal curse', 'Authors → title is slightly harder than title → authors: no reversal curse',
                         'Part 6 · writing step', ''.join(b), ov, 29)

# ================================================================ text pages: question cards, verdict cards, evidence matrices
def card(x, y, w, h, head, lines, col, size=13):
    o = box(x, y, w, h, '#fff', col, 10, 2) + f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="10" fill="{col}" opacity=".14"/>' + t(x + 12, y + 21, head, 16, col, weight=700)
    yy = y + 50
    for ln in lines:
        o += t(x + 14, yy, ln, size, INK); yy += size + 7
    return o
def htmlblock(left, top, width, head, col, body, size=13):
    return (f'<div style="position:absolute;z-index:4;left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;line-height:1.3;font-family:{PH};color:{INK};'
            f'background:rgba(255,255,255,.85);border:2px solid {col};border-radius:10px;padding:6px 12px">'
            f'<div style="font-size:17px;font-weight:700;color:{col};margin-bottom:3px">{head}</div>{body}</div>')

def page_h3_question():
    slot = 'h3-question'
    b = []
    # emphasis schematic: route flow title → after-title → names, readouts at the names (probe vs lens)
    sx, sy = 70, 140
    b.append(t(sx, sy - 8, 'What this part tests, on the real prompt', 14, INK, weight=700))
    for k, (lab, col, xx) in enumerate([('title', '#FFF1DE', sx), ('after-title (“:”)', '#E8F0FA', sx + 190), ('author name positions', '#EAF6EC', sx + 400)]):
        b.append(box(xx, sy + 10, 170 if k < 2 else 200, 50, col, '#C9CED6')); b.append(t(xx + (85 if k < 2 else 100), sy + 41, lab, 14, INK, 'middle', weight=700))
    b.append(arrow(sx + 172, sy + 35, sx + 188, sy + 35)); b.append(arrow(sx + 362, sy + 35, sx + 398, sy + 35))
    b.append(f'<path d="M{sx + 85} {sy + 60} C{sx + 85} {sy + 110} {sx + 500} {sy + 110} {sx + 500} {sy + 62}" fill="none" stroke="{ORANGE}" stroke-width="2.4" marker-end="url(#ARO)"/>')
    b.append(t(sx + 290, sy + 112, 'route: which edges, which layers?', 13, ORANGE, 'middle', weight=700))
    b.append(box(sx + 420, sy + 130, 80, 34, '#EEF4FB', BLUE)); b.append(t(sx + 460, sy + 152, 'probe', 13, BLUE, 'middle', weight=700))
    b.append(box(sx + 510, sy + 130, 80, 34, '#F6F7F9', GREY)); b.append(t(sx + 550, sy + 152, 'lens', 13, GREY, 'middle', weight=700))
    b.append(arrow(sx + 460, sy + 128, sx + 470, sy + 64, BLUE)); b.append(arrow(sx + 550, sy + 128, sx + 530, sy + 64, GREY))
    b.append(t(sx + 400, sy + 186, 'same tokens, same scale: does the probe see more?', 12, INK, 'middle', SANS))
    ov = ask('after the title is read, how does its information reach the author name positions, and in what form is it held there?')
    ov += htmlblock(700, 120, 520, 'Hypothesis (H3 + route)', BLUE,
                    'The paper’s information travels from the title to the name positions over attention, and the author information is held there '
                    '<span class="mk">in a form the vocabulary readouts (lenses) cannot see</span>.')
    ov += htmlblock(700, 238, 250, 'If it holds, we expect', GREEN,
                    '① a probe on the name tokens beats the lens <b>on the same scale</b>;<br>② cutting the title → name route removes signal;<br>'
                    '③ handing the late layers the probe’s author direction makes them write <i>this</i> author.', 12.5)
    ov += htmlblock(970, 238, 250, 'If it fails, we expect', RED,
                    '① probe ≈ lens on the same tokens;<br>② no edge or layer matters;<br>③ the direction does nothing, or writes any author it points to.', 12.5)
    ov += htmlblock(70, 380, 1150, 'Tests in this part', INK,
                    '<b>Route:</b> where the paper information travels (slide {{p:73}}) → which positions carry it (slide {{p:74}}) → which attention edge, 4-layer windows (slide {{p:75}}) '
                    '→ MLP lookup at L52–L56 (slide {{p:76}}) → single layers (slide {{new:route}}).<br>'
                    '<b>Readouts:</b> lenses over layers (slides {{p:34}}–{{p:42}}) → probe on every name token (slide {{p:89}}) → probe vs lens on the same scale (slide {{p:90}}) '
                    '→ directions of the difference (slide {{p:91}}) → swapping a small subspace (slide {{p:88}}) → readout map (slide {{p:72}}).<br>'
                    '<b>Use:</b> injecting the author direction vs more title signal (slide {{new:injection}}) → why pushing hurts (slide {{new:injection-why}}).', 12.5)
    ov += f'<div style="position:absolute;z-index:4;left:640px;top:280px;font-size:24px;color:{GREY}">→</div>'
    ov += soln('Part 4 showed the title is read for its meaning and specific words; this part follows that information to the name positions and asks how it is held.', 650, 'So (section)')
    frag[slot] = section(slot, 'Question card: route and H3', 'Question: how does the title reach the names, and how is it held there?', 'Part 5 · route + H3', ''.join(b), ov, 30)

def page_w_question():
    slot = 'w-question'
    b = []
    # emphasis schematic: layer timeline L48 → L63 with the writer band and the questions placed on it
    sx, sy, sw = 90, 190, 520
    X = lambda l: sx + (l - 44) / 19 * sw
    b.append(t(70, 140, 'Where the last steps happen (layers at the author name positions)', 14, INK, weight=700))
    b.append(f'<line x1="{sx}" y1="{sy}" x2="{sx + sw}" y2="{sy}" stroke="{INK}" stroke-width="2.4" marker-end="url(#ARW)"/>')
    for l in (44, 48, 52, 56, 60, 63):
        b.append(f'<line x1="{X(l):.1f}" y1="{sy - 6}" x2="{X(l):.1f}" y2="{sy + 6}" stroke="{INK}" stroke-width="1.6"/>' + t(X(l), sy + 24, 'out' if l == 63 else f'L{l}', 12, GREY, 'middle'))
    b.append(f'<rect x="{X(44):.1f}" y="{sy - 46}" width="{X(52) - X(44):.1f}" height="30" rx="6" fill="#EAF6EC" stroke="{GREEN}"/>' + t((X(44) + X(52)) / 2, sy - 26, 'info arrives (L44–L52)', 12, GREEN, 'middle', weight=700))
    b.append(f'<rect x="{X(56.5):.1f}" y="{sy - 46}" width="{X(61.5) - X(56.5):.1f}" height="30" rx="6" fill="#E8F0FA" stroke="{BLUE}"/>' + t((X(56.5) + X(61.5)) / 2, sy - 26, 'MLPs write', 12, BLUE, 'middle', weight=700))
    for k, (l, txt, col) in enumerate([(52, '① more input → more names?', ORANGE), (57, '② pushed down late?', RED), (60, '③ which part of the name?', PURPLE)]):
        b.append(arrow(X(l), sy + 70 + k * 26, X(l), sy + 8, col, 1.4)); b.append(t(X(l) + 6, sy + 74 + k * 26, txt, 12.5, col, weight=700))
    ov = ask('the information is at the name positions by about L50; why does the model still not write the author?')
    ov += htmlblock(700, 120, 520, 'Hypothesis (writing step)', BLUE,
                    'Recall fails at the <span class="mk">late writing step</span> (the L57–L61 MLPs and the first name token), not because too little information arrives.')
    ov += htmlblock(700, 228, 250, 'If it holds, we expect', GREEN,
                    '① removing the late MLPs removes the signal;<br>② a stronger arrived signal does not help;<br>③ some papers’ names rise and then fall late;<br>'
                    '④ the first token is the hardest; a hint of it helps;<br>⑤ writing the title from the authors is no easier.', 12.5)
    ov += htmlblock(970, 228, 250, 'If it fails, we expect', RED,
                    '① attention, not MLPs, writes;<br>② more input → more names;<br>③ no late fall;<br>④ all name tokens equally hard;<br>⑤ authors → title much easier (a reversal curse).', 12.5)
    ov += htmlblock(70, 412, 1150, 'Tests in this part', INK,
                    '<b>Who writes:</b> mean ablation at L57–L61 (slide {{p:77}}) → late suppression in a subgroup (slide {{new:suppression}}).<br>'
                    '<b>Does more input help:</b> strengthening the arrived information (slide {{p:78}}) → why pushing hurts (slide {{new:injection-why}}).<br>'
                    '<b>Is it the direction of storage:</b> authors → title vs title → authors (slide {{new:asymmetry}}).<br>'
                    '<b>Which part of the name:</b> first token vs the rest (slides {{p:52}}–{{p:58}}) → co-author chain (slide {{p:60}}) → names it writes itself, true vs made up (slides {{p:92}}, {{p:93}}).', 12.5)
    ov += soln('Part 5 showed the information arrives and is held at the name positions; this part asks what goes wrong when it has to be written out.', 650, 'So (section)')
    frag[slot] = section(slot, 'Question card: the writing step', 'Question: why is a recognised author still not written?', 'Part 6 · writing step', ''.join(b), ov, 30)

def page_h3_verdict():
    slot = 'h3-verdict'
    b = []
    # contrast schematic: what holds / what does not
    b.append(t(70, 132, 'Verdict at a glance', 14, INK, weight=700))
    rows = [('Probe sees more than the lens at the names', 'locked · supported', BLUE), ('Route: parallel, name ← title strongest at L48/L52', 'locked · supported', BLUE),
            ('No single layer is a bottleneck', 'locked', BLUE), ('Author direction writes names (mostly any author)', 'locked + exploratory', '#B54708'),
            ('More title signal makes it write', 'locked · not supported', RED)]
    for k, (txt, tagt, col) in enumerate(rows):
        yy = 150 + k * 44
        b.append(box(70, yy, 560, 36, '#fff', col, 8, 1.6)); b.append(t(84, yy + 23, txt, 13.5, INK, weight=700)); b.append(t(620, yy + 23, tagt, 11.5, col, 'end', SANS, 700))
    ov = ask('what do the route and readout tests together say about H3?')
    ov += htmlblock(670, 120, 550, 'Conclusion', BLUE,
                    '<b>H3 supported on the same scale</b>: at the name positions a probe separates target from control more than the lens (L40 <b>+0.021</b>, L48 <b>+0.062</b>; slide {{p:69}}). '
                    'The title reaches the names over <span class="mk">parallel routes</span>; name ← title is strongest at L48 and L52 (slides {{p:75}}, {{new:route}}).', 13)
    ov += htmlblock(670, 268, 550, 'Evidence strength', INK,
                    '<span class="tg lsup">locked · supported</span> same-scale probe vs lens; route rule met in the windows and at single layers.<br>'
                    '<span class="tg lsup">locked · supported</span> the author direction is usable; <span class="tg expl">exploratory</span> it works mainly as a write channel (slide {{new:injection}}).<br>'
                    '<span class="tg lsup">locked · supported</span> pushing more title signal hurts through direction (slide {{new:injection-why}}).<br>'
                    '<span class="tg desc">descriptive</span> the name positions carry most of the restored signal by L52 (slide {{p:74}}).', 12.5)
    ov += htmlblock(670, 420, 550, 'Open questions', ORANGE,
                    '<span class="ul">which subspace holds the authors</span> (a small subspace swap moves little, slide {{p:88}}); '
                    'is the direction an unlock or just a write channel; a linear causal test at L48–L56 is not yet run.', 12.5)
    ov += f'<div style="position:absolute;z-index:4;left:640px;top:250px;font-size:24px;color:{GREY}">→</div>'
    ov += soln('the information is there at the name positions in a probe-readable form; whether the late layers can use it is the question of Part 6 '
               '<span class="st c2">locked</span>', 650)
    frag[slot] = section(slot, 'Verdict card: route and H3', 'Verdict: held at the names, readable by a probe, reached over parallel routes', 'Part 5 · route + H3', ''.join(b), ov, 29)

def page_w_verdict():
    slot = 'w-verdict'
    b = []
    b.append(t(70, 132, 'Verdict at a glance', 14, INK, weight=700))
    rows = [('L57–L61 MLPs, not attention, write the name', 'settled', GREEN), ('More arrived signal does not help', 'locked · not supported', RED),
            ('Not a reversal curse: authors → title is slightly harder', 'locked · not supported', RED), ('Late rise-then-fall in ~1 in 8 recognised papers', 'locked (just above bound)', BLUE),
            ('A first-initial hint helps; the rest stays hard', 'locked · supported', BLUE)]
    for k, (txt, tagt, col) in enumerate(rows):
        yy = 150 + k * 44
        b.append(box(70, yy, 560, 36, '#fff', col, 8, 1.6)); b.append(t(84, yy + 23, txt, 13.5, INK, weight=700)); b.append(t(620, yy + 23, tagt, 11.5, col, 'end', SANS, 700))
    ov = ask('what do the writing-step tests together say about why a recognised author is not written?')
    ov += htmlblock(670, 120, 550, 'Conclusion', BLUE,
                    '<b>The bottleneck is the late writing step</b>: the L57–L61 MLPs write the name (MLP − attention <b>+0.040</b> [+0.036, +0.045], slide {{p:77}}); '
                    '<span class="mk">more of the arrived signal does not help</span> (slide {{p:78}}) and near the writer disrupts rather than helps (slide {{new:injection-why}}); '
                    'storage direction is not the cause: writing the title from the authors is slightly harder (slide {{new:asymmetry}}).', 13)
    ov += htmlblock(670, 284, 550, 'Evidence strength', INK,
                    '<span class="tg settled">settled</span> late MLPs write (locked criterion met at all 5 layers).<br>'
                    '<span class="tg lnot">locked · not supported</span> strengthening the arrived information; reversal curse (reading “Reversed”).<br>'
                    '<span class="tg lsup">locked · supported</span> direction-driven damage; late suppression in a subgroup (slide {{new:suppression}}); '
                    'first-initial hint 4.0% → 15.2% in recognised papers (slide {{p:59}}).', 12.5)
    ov += htmlblock(670, 452, 550, 'Open questions', ORANGE,
                    '<span class="ul">which heads or neurons push the name down</span> in the subgroup; a first-token causal test; a second model.', 12.5)
    ov += f'<div style="position:absolute;z-index:4;left:640px;top:250px;font-size:24px;color:{GREY}">→</div>'
    ov += soln('read early, said late: the information reaches the names, and recall fails at the late writing step <span class="st c1">settled</span> <span class="st c2">locked</span>', 650)
    frag[slot] = section(slot, 'Verdict card: the writing step', 'Verdict: the bottleneck is the late writing step, not the arrival', 'Part 6 · writing step', ''.join(b), ov, 29)

# evidence matrix: hypotheses × kinds of evidence, cells coloured by verdict, slide refs
MCOL = {'s': ('#E3F1E7', GREEN), 'l': ('#E6EFF8', BLUE), 'n': ('#F8E4E2', RED), 'd': ('#EEF0F3', GREY), 'x': ('#FCEBDD', '#B54708'), 'p': ('#FFFFFF', '#C9CED6')}
def matrix(slot, after, rows, label, title, part, so, so_label):
    cols = ['Prediction', 'Readout (lens / probe)', 'Replace / knock out', 'Inject / push', 'Rewritten titles · behaviour', 'Result (verdict)']
    th = ''.join(f'<th style="padding:5px 6px;border-bottom:2px solid {INK};text-align:left;font-size:13px">{c}</th>' for c in cols)
    trs = ''
    PRED = {'H1': 'the middle layers fix the answer format', 'H2': 'the title state codes which paper it is', 'H3': 'a probe sees author information the lens cannot',
            'Ro': 'one dominant edge carries the title', 'Wr': 'recall fails at the late writing step', 'St': 'authors → title is easier than title → authors'}
    for name, cells_, hl in rows:
        bg = 'background:rgba(255,228,94,.35);' if hl else ''
        tds = f'<td style="padding:4px 6px;font-size:12px;line-height:1.25;color:{INK};font-style:italic;vertical-align:top;border:1px solid #fff">{PRED[name[:2]]}</td>'
        for kind, txt in cells_:
            f, c = MCOL[kind]
            tds += f'<td style="padding:4px 6px;background:{f};border:1px solid #fff;color:{c};font-size:12px;line-height:1.25;vertical-align:top">{txt}</td>'
        trs += f'<tr><td style="padding:4px 6px;font-weight:700;font-size:13px;{bg}vertical-align:top;width:130px">{name}</td>{tds}</tr>'
    legend = ' '.join(f'<span style="display:inline-block;padding:0 6px;border-radius:4px;background:{MCOL[k][0]};color:{MCOL[k][1]};border:1px solid {MCOL[k][1]};margin-right:4px">{lab}</span>'
                      for k, lab in [('s', 'settled'), ('l', 'locked · supported'), ('n', 'locked · not supported'), ('d', 'descriptive'), ('x', 'exploratory'), ('p', 'later part')])
    ov = ask(f'with {after} done, where does each hypothesis stand?')
    ov += (f'<div style="position:absolute;z-index:4;left:70px;top:112px;width:1150px;font-family:{SANS};color:{INK}"><table style="border-collapse:collapse;width:100%">'
           f'<tr><th style="padding:5px 6px;border-bottom:2px solid {INK};text-align:left;font-size:13px">Hypothesis</th>{th}</tr>{trs}</table>'
           f'<div style="font-size:11.5px;margin-top:6px">{legend} &nbsp; highlighted row = updated by this part</div></div>')
    ov += soln(so, 650, so_label)
    frag[slot] = section(slot, label, title, part, '', ov, 30)

H1ROW = ('H1 · question format', [('d', 'the “:” state tracks the question (slide {{p:81}}, {{p:118}})'), ('x', 'format test distorted by cutting the attention sink (slide {{new:h1-format}})'),
                                  ('p', '—'), ('p', '—'), ('l', 'revised: the format layer is not pinned down')], False)
H2ROW = ('H2 · paper identity', [('l', 'small surname signal at L8 beyond topic (slide {{new:h2-exception}})'), ('d', 'title tokens matter by meaning (slide {{p:84}})'),
                                 ('p', '—'), ('l', 'same-meaning made-up title gets ≈ 75% (slide {{p:85}})'), ('n', 'not a general paper identity; one small locked exception')], False)
def h3row(hl): return ('H3 · held, not in vocabulary', [('l', 'probe beats lens on the same scale (slide {{p:90}})'), ('d', 'names carry most of the restored signal by L52 (slide {{p:74}})'),
                                                         ('x', 'author direction writes names, mostly any author (slide {{new:injection}})'), ('p', '—'), ('l', 'supported on the same scale')], hl)
def routerow(hl): return ('Route', [('p', '—'), ('l', 'name ← title strongest at L48/L52; no single-layer bottleneck (slides {{p:75}}, {{new:route}})'),
                                    ('p', '—'), ('p', '—'), ('l', 'parallel routes')], hl)
DPEND = ('Storage direction (reversal curse)', [('p', '—'), ('p', '—'), ('p', '—'), ('p', 'next part'), ('p', 'tested in Part 6')], False)
def drow(hl): return ('Storage direction (reversal curse)', [('l', 'given the authors, the title is far more likely for recognised papers (slide {{new:asymmetry}})'), ('p', '—'), ('p', '—'),
                                                             ('n', 'authors → title slightly harder than title → authors (slide {{new:asymmetry}})'), ('n', 'not supported (reading “Reversed”)')], hl)
WPEND = ('Writing step', [('p', 'next part'), ('p', 'next part'), ('p', 'next part'), ('p', '—'), ('p', 'tested in Part 6')], False)
def wrow(hl): return ('Writing step', [('l', 'late rise-then-fall in a subgroup (slide {{new:suppression}})'), ('s', 'L57–L61 MLPs write (slide {{p:77}})'),
                                       ('n', 'more arrived signal does not help (slide {{p:78}}); direction hurts (slide {{new:injection-why}})'), ('p', '—'), ('s', 'the bottleneck')], hl)

def page_h3_matrix():
    matrix('h3-matrix', 'Part 5', [H1ROW, H2ROW, h3row(True), routerow(True), WPEND, DPEND], 'Evidence matrix after Part 5', 'Evidence so far: H3 and the route are now filled in',
           'Part 5 · route + H3', 'the information reaches the names over parallel routes and is held there in a probe-readable form; next, Part 6 asks why it is still not written out.', 'So (section)')
def page_w_matrix():
    matrix('w-matrix', 'Part 6', [H1ROW, H2ROW, h3row(False), routerow(False), wrow(True), drow(True)], 'Evidence matrix after Part 6', 'Evidence so far: every hypothesis now has a verdict',
           'Part 6 · writing step', 'read early, said late — the summary (Part 7) walks through the whole route on one map.', 'So (section)')

for fn in [page_h3_question, page_route, page_injection, page_pushdir, page_h3_verdict, page_h3_matrix, page_w_question, page_suppression, page_asymmetry, page_w_verdict, page_w_matrix]:
    fn()

# unique LaTeX glyph ids per fragment (avoid clashes with the deck and other fragments)
for slot, s in frag.items():
    pfx = 'p56' + slot.replace('-', '') + '_'
    s = re.sub(r'id="(t\d+_[^"]+)"', lambda m: f'id="{pfx}{m.group(1)}"', s); s = re.sub(r'href="#(t\d+_[^"]+)"', lambda m: f'href="#{pfx}{m.group(1)}"', s)
    open(OUT + slot + '.html', 'w').write(s + '\n')
with open(OUT + 'part56_numbers.md', 'w') as f:
    f.write('# Part 5–6 fragments: every number shown → source (agent C, 2026-11-23)\n\nPaths are relative to /scratch/zhang.zhiqi2/jlens/391_groups/ unless marked "existing slide" (v65 page).\n\n| shown | meaning | source |\n|---|---|---|\n')
    seen = set()
    for a_, b_, c_ in NUM:
        if (a_, b_) in seen: continue
        seen.add((a_, b_)); f.write(f'| {a_} | {b_} | {c_} |\n')
print('wrote', sorted(frag), len(NUM), 'numbers')
