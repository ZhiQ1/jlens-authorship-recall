"""After build_v68.py + postfix_v68.py: re-render grey LaTeX lines that still contained internal codes
(RQ1/RQ2/RQ3, JMRR, M1) inside pre-rendered SVG (C3 cannot read SVG glyphs). user 2026-11-23 plain names."""
import re, sys
sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/normalise_sample_20261122b'); sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/hc_pass_20261123')
from addonly_lib import tex
from texu import ntex
W = '/home/zhang.zhiqi2/jlens_work/27_v67/deck_v68.html'
t = open(W, encoding='utf-8').read()
# slide -> {svg index inside its single fxu block: new TeX}
FIX = {
  63: {0: r'$\mathrm{title\ test}=\mathrm{win}(\mathrm{true\ title})-\mathrm{win}(\mathrm{wrong\ title})$'},
  64: {0: r'$\mathrm{title\ test}=\mathrm{win}(\mathrm{true\ title})-\mathrm{win}(\mathrm{wrong\ title}),\ L56$',
       1: ntex('n = 200 papers · 100 A/B pairs (A−B test) · 25 + 25 pairs (low−high test)')},
  112: {0: r'$\mathrm{mean\ reciprocal\ rank}=\mathrm{mean}_a\,\mathrm{mean}_t\,1/r$'},
  113: {0: r'$A-B=\overline{1/r}_A-\overline{1/r}_B\ \mathrm{by\ token\ position}$'},
  37: {3: ntex('n = 566 (H2) · 4,654 (H3) · 9,108 (top lens word) papers')},
}
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
out, last = [], 0
for i, m in enumerate(ms, 1):
    s = m.group(0)
    if i in FIX:
        b = re.search(r'<div class="fxu".*?<div class="fxkey">', s, re.S)
        blk = b.group(0); svgs = list(re.finditer(r'<svg class="tx".*?</svg>', blk, re.S))
        new = blk
        for idx, tx in sorted(FIX[i].items(), reverse=True):
            sv = svgs[idx]; new = new[:sv.start()] + tex(tx) + new[sv.end():]
        s = s.replace(blk, new, 1)
        # the 37 extra (M1b) in the measured-word box
    if i == 37: s = s.replace(' (M1b)', '')
    out.append(t[last:m.start()]); out.append(s); last = m.end()
out.append(t[last:]); open(W, 'w', encoding='utf-8').write(''.join(out))
print('fixed', sorted(FIX))
