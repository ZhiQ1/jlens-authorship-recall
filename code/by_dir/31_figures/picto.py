# Line-art pictograms for the story figures (hand-drawn style: round caps, ink + one accent). v2, 2026-11-24.
INK = '#2B3445'; ACC = '#E8954A'; PALE = '#F3E3D3'; HAND = "Patrick Hand, Caveat, sans-serif"
SW = 2.2

def _t(x, y, s, size=14, col=INK, anchor='middle'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-family="{HAND}">{s}</text>'

def card(x, y, w=44, h=56, label=None, fill='#fff', lines=3, hi=None):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{INK}" stroke-width="{SW}"/>']
    for k in range(lines):
        yy = y + 14 + k*12; ww = w - 16 - (k % 2)*8
        col = ACC if hi and k in hi else INK
        o.append(f'<line x1="{x+8}" y1="{yy}" x2="{x+8+ww}" y2="{yy}" stroke="{col}" stroke-width="{SW}" stroke-linecap="round"/>')
    if label: o.append(_t(x + w/2, y + h + 15, label, 14))
    return ''.join(o)

def strip(x, y, n=5, w=18, gap=4, black=(), swap=(), col=INK):
    o = []
    for k in range(n):
        xx = x + k*(w+gap)
        if k in black:
            o.append(f'<rect x="{xx}" y="{y}" width="{w}" height="12" rx="2" fill="{INK}"/>')
        elif k in swap:
            o.append(f'<path d="M{xx} {y+6} q4 -7 9 0 t9 0" fill="none" stroke="{ACC}" stroke-width="{SW}" stroke-linecap="round"/>')
        else:
            o.append(f'<rect x="{xx}" y="{y}" width="{w}" height="12" rx="2" fill="#fff" stroke="{col}" stroke-width="1.6"/>')
    return ''.join(o)

def bars(x, y, hs, labels, w=16, gap=12, base=None, cols=None):
    base = base or y
    o = [f'<line x1="{x-4}" y1="{base}" x2="{x + len(hs)*(w+gap)}" y2="{base}" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>']
    for k, (h, lab) in enumerate(zip(hs, labels)):
        xx = x + k*(w+gap); c = (cols or [ACC]*len(hs))[k]
        o.append(f'<rect x="{xx}" y="{base-h}" width="{w}" height="{h}" rx="2" fill="{c}" stroke="{INK}" stroke-width="1.6"/>')
        o.append(_t(xx + w/2, base + 15, lab, 14))
    return ''.join(o)

# ---- operation pictograms (each returns svg; (x, y) = top-left) ----
def words_carry(x, y):            # swap a word class: random tokens vs synonyms
    return (strip(x, y+6, swap=(1, 3)) + _t(x+118, y+17, 'random', 14, INK, 'start') +
            strip(x, y+30) +
            f'<path d="M{x+26} {y+30} l9 0 M{x+70} {y+30} l9 0" stroke="{ACC}" stroke-width="{SW}" stroke-linecap="round"/>' +
            _t(x+118, y+41, 'synonym', 14, INK, 'start') +
            bars(x+20, y+60, [48, 12], ['random', 'synonym'], w=20, gap=44, base=y+112))

def paraphrase(x, y):             # same meaning, new words; closeness above L4, peak mid-layers
    o = card(x, y+4, 46, 50, 'title') + card(x+86, y+4, 46, 50, 'reworded', hi=(0, 1, 2))
    o += f'<path d="M{x+52} {y+30} h28" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round" marker-end="url(#pa)"/>' + _t(x+66, y+22, '≈', 16)
    o += (f'<line x1="{x}" y1="{y+118}" x2="{x+140}" y2="{y+118}" stroke="{INK}" stroke-width="1.4"/>'
          f'<path d="M{x+4} {y+114} C {x+40} {y+112}, {x+60} {y+82}, {x+80} {y+84} S {x+120} {y+108}, {x+138} {y+110}" fill="none" stroke="{ACC}" stroke-width="{SW}" stroke-linecap="round"/>'
          + _t(x+80, y+79, 'peak', 14))
    return o

def madeup(x, y):                 # three titles, scores on one number line, 75% segment
    o = card(x, y, 52, 60, 'true') + card(x+80, y, 52, 60, 'made-up', hi=(0, 2)) + card(x+160, y, 52, 60, 'other paper', fill='#F1F2F4')
    ly = y + 112; F, A, T = x+10, x+170, x+222
    o += f'<line x1="{x}" y1="{ly}" x2="{x+240}" y2="{ly}" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round"/>'
    o += f'<line x1="{F}" y1="{ly}" x2="{A}" y2="{ly}" stroke="{ACC}" stroke-width="9" stroke-linecap="round" opacity=".85"/>'
    for xx, lab in ((F, 'other'), (A, 'made-up'), (T, 'true')):
        o += f'<circle cx="{xx}" cy="{ly}" r="5.5" fill="#fff" stroke="{INK}" stroke-width="{SW}"/>' + _t(xx, ly+22, lab, 14)
    o += _t((F+A)/2, ly-10, 'brings back ~75%', 14, INK)
    o += f'<path d="M{A+6} {ly-10} q20 -12 40 0" fill="none" stroke="{INK}" stroke-width="1.6"/>' + _t(A+26, ly-18, 'extra', 14)
    return o

def rare_common(x, y):            # same title twice: rare words blacked out vs common words blacked out
    return (_t(x, y+11, 'rare out', 14, INK, 'start') + strip(x+84, y, n=5, w=14, gap=3, black=(1, 3)) +
            _t(x, y+35, 'common out', 14, INK, 'start') + strip(x+84, y+24, n=5, w=14, gap=3, black=(0, 4)) +
            bars(x+40, y+50, [44, 8], ['rare', 'common'], w=22, gap=36, base=y+100))

def recog_citation(x, y):         # two piles of papers, two equal bars, "="
    o = ''
    for k, lab in ((0, 'recognised'), (1, 'not')):
        px = x + 6 + k*104
        for j in range(3):
            o += f'<rect x="{px+j*4}" y="{y+6-j*5}" width="38" height="28" rx="3" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
        o += _t(px+22, y+50, lab, 14)
    o += bars(x+22, y+60, [30, 30], ['extra', 'extra'], w=20, gap=66, base=y+100)
    o += _t(x+74, y+86, '=', 22)
    return o

def variance_pie(x, y, r=42):     # words + meaning fill the pie, identity is a hairline
    import math
    cx, cy = x + 60, y + 50
    def pt(a): return cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a))
    o = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="{SW}"/>'
    x1, y1 = pt(-90); x2, y2 = pt(130)
    o += f'<path d="M{cx} {cy} L{x1} {y1} A{r} {r} 0 1 1 {x2} {y2} Z" fill="{PALE}" stroke="{INK}" stroke-width="1.6"/>'
    x3, y3 = pt(-92)
    o += f'<line x1="{cx}" y1="{cy}" x2="{x3}" y2="{y3}" stroke="#C0392B" stroke-width="2.4"/>'
    o += _t(cx+12, cy+12, 'words', 14) + _t(cx-22, cy-2, 'meaning', 14)
    o += f'<path d="M{x3-2} {y3-2} q-14 -16 -34 -10" fill="none" stroke="#C0392B" stroke-width="1.4"/>' + _t(x3-58, y3-12, 'identity', 14, '#C0392B')
    return o

def subspace(x, y):               # move only a thin slice of the state: almost nothing moves
    o = (f'<rect x="{x}" y="{y+6}" width="120" height="16" rx="3" fill="#fff" stroke="{INK}" stroke-width="{SW}"/>'
         f'<rect x="{x+44}" y="{y+6}" width="12" height="16" fill="{ACC}" stroke="{INK}" stroke-width="1.4"/>'
         f'<path d="M{x+50} {y+24} q0 16 18 20" fill="none" stroke="{INK}" stroke-width="1.8" marker-end="url(#pa)"/>'
         f'<rect x="{x}" y="{y+46}" width="120" height="16" rx="3" fill="#F1F2F4" stroke="{INK}" stroke-width="{SW}"/>'
         f'<rect x="{x+68}" y="{y+46}" width="12" height="16" fill="{ACC}" stroke="{INK}" stroke-width="1.4"/>' + _t(x+150, y+18, 'true', 14) + _t(x+150, y+58, 'false', 14))
    o += bars(x+20, y+68, [3, 34], ['slice', 'whole'], w=20, gap=40, base=y+104)
    return o

def ceiling(x, y):                # two identical state bars under two questions at L4
    return (f'<rect x="{x}" y="{y}" width="90" height="14" rx="3" fill="{PALE}" stroke="{INK}" stroke-width="1.8"/>'
            f'<rect x="{x}" y="{y+24}" width="90" height="14" rx="3" fill="{PALE}" stroke="{INK}" stroke-width="1.8"/>'
            + _t(x+104, y+26, '=', 20) + _t(x+45, y+56, 'two questions, L4', 14))

def pipe_dep(x, y):               # book -> pipe -> name slots
    o = (f'<path d="M{x} {y+8} q12 -8 24 0 q12 -8 24 0 v28 q-12 -8 -24 0 q-12 -8 -24 0 z" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
         f'<line x1="{x+24}" y1="{y+8}" x2="{x+24}" y2="{y+36}" stroke="{INK}" stroke-width="1.4"/>')
    for k in range(3):
        o += f'<line x1="{x+52}" y1="{y+14+k*8}" x2="{x+100}" y2="{y+14+k*8}" stroke="#1F6F8B" stroke-width="2" stroke-linecap="round"/>'
    for k in range(3):
        o += f'<rect x="{x+104+k*14}" y="{y+12}" width="11" height="20" rx="2" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
    return o

def name_tag(x, y):               # title state at L8 -> a small surname tag
    return (f'<rect x="{x}" y="{y+8}" width="60" height="14" rx="3" fill="{PALE}" stroke="{INK}" stroke-width="1.8"/>'
            f'<path d="M{x+64} {y+15} h20" stroke="{INK}" stroke-width="1.8" marker-end="url(#pa)"/>'
            f'<path d="M{x+90} {y+4} h44 l8 11 l-8 11 h-44 z" fill="#fff" stroke="{INK}" stroke-width="1.8"/>' + _t(x+114, y+20, 'Co…', 14))

def crossed(x, y, w=26):          # a crossed-out mark
    return f'<path d="M{x} {y} l{w} {w} M{x+w} {y} l-{w} {w}" stroke="#C0392B" stroke-width="2.6" stroke-linecap="round"/>'

DEFS = f'<marker id="pa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
