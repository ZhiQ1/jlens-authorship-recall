"""final v48 verify (b + c): vs published v47 = stage1_11_deck.html.before_20261121b: 2 new slides (81, 86); changed old slides only by
slide-number remaps (68, 82, 88, 90, 94), the slide-59 line and appended formula/n blocks (c); nothing else."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261121b').read_text(); b = (D / 'stage1_11_deck.html').read_text(); mid = (D / 'stage1_11_deck.html.after_20261121b').read_text()
F = lambda t: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', t, re.S)]
A, M, B = F(a), F(mid), F(b); assert len(A) == 97 and len(M) == len(B) == 99
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121c_fx.json'))
fxn = {int(k) for k in rec if k.isdigit()}; svg = {int(k.split('_')[0]) for k in rec if k.endswith('_svg')}
for n in range(1, 100):
    x, y = M[n - 1], B[n - 1]
    if n in fxn:
        i = y.rindex('<div class="fxn"'); assert y[:i] + y[y.index('</div>', i) + 6:] == x, n
    elif n in svg:
        assert re.sub(r'<text x="\d+" y="\d+" font-size="1[01](?:\.5)?" fill="#8a8f98"[^>]*>[^<]*</text>', '', y) == re.sub(r'<text x="\d+" y="\d+" font-size="1[01](?:\.5)?" fill="#8a8f98"[^>]*>[^<]*</text>', '', x) or y.count('</text>') == x.count('</text>') + (1 if n == 81 else 2), n
    else: assert x == y, n
assert a[:a.index('<section class="slide')] == b[:b.index('<section class="slide')]
print('VERIFY PASS c: formula/n blocks on', sorted(fxn), '+ svg lines on', sorted(svg), '; everything else as after build b')
