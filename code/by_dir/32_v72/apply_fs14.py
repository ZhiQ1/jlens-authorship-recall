"""Apply the 14-px relayout (relayout2.json + two hand placements checked by render) to deck_v72_stage1.html -> deck_v72.html."""
import re, json, sys
W = '/home/zhang.zhiqi2/jlens_work/32_v72/'
R = json.load(open(W + 'relayout2.json'))
MANUAL = {(3, 'addb'): (238, 476, 360), (170, 'soln covso'): (40, 670, 494), (106, 'cats'): (70, 482, 830)}
t = open(W + 'deck_v72_stage1.html', encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
SEC = [m.group(0) for m in ms]
CSS = ("<style id=\"fs14css\">/* v72: small-text boxes raised to 14 px (chips, circled numerals and reading lines keep their deck-wide size) */"
       "[data-fs14]:not(.tg):not(.q):not(.st):not(.fxkey), [data-fs14] *:not(.tg):not(.q):not(.st):not(.fxkey):not(svg):not(svg *){font-size:14px !important}"
       " [data-fs14].lead{white-space:normal;max-width:none}</style>")
def setp(st, k, v):
    if re.search(r'(^|;)\s*%s\s*:' % k, st): return re.sub(r'((?:^|;)\s*%s\s*:)\s*[^;]*' % k, r'\g<1>%spx' % v, st, count=1)
    return st.rstrip(';') + ';%s:%spx' % (k, v)
log = []
for r in R:
    n, cls = r['slide'], r['cls']
    x, y, w = MANUAL.get((n, cls), (round(r['best']['left']), round(r['best']['top']), round(r['best']['width'])))
    s = SEC[n - 1]
    if r['style'] is None:
        tag = f'<div class="{cls}">'; assert s.count(tag) == 1, (n, cls)
        new = f'<div class="{cls}" data-fs14 style="left:{x}px;top:{y}px;width:{w}px;max-width:none">'
    else:
        tag = f'class="{cls}" style="{r["style"]}"'; assert s.count(tag) == 1, (n, cls, s.count(tag))
        st = setp(setp(setp(r['style'], 'left', x), 'top', y), 'width', w)
        new = f'class="{cls}" data-fs14 style="{st}"'
    SEC[n - 1] = s.replace(tag, new, 1); log.append((n, cls, x, y, w))
out = t[:ms[0].start()]
assert 'id="fs14css"' not in out; out = out.replace('</head>', CSS + '</head>', 1)
pos = ms[0].start(); parts = [out]
for i, m in enumerate(ms):
    parts.append(SEC[i]); parts.append(t[m.end():ms[i + 1].start()] if i + 1 < len(ms) else t[m.end():])
open(W + 'deck_v72.html', 'w', encoding='utf-8').write(''.join(parts))
for l in log: print(l)
