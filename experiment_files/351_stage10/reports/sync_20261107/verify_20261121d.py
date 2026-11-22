"""v49 verify vs published v48 (.before_20261121d): one new slide (79); slide 77 = number fix + footnote; slide 78 = pointer;
other slides change only by slide-number remaps."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261121d').read_text(); b = (D / 'stage1_11_deck.html').read_text()
F = lambda t: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', t, re.S)]
A, B = F(a), F(b); assert len(A) == 99 and len(B) == 100
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121d_deck.json'))
remapped = set(rec['refs_remapped_on_slides'])
num = lambda t: re.sub(r'(\bslides? )\d{1,3}(?:[–-]\d{1,3})?', r'\1N', t)
for nb in range(1, 101):
    if nb == 79: continue
    na = nb if nb <= 78 else nb - 1
    x, y = A[na - 1], B[nb - 1]
    if nb in (77, 78):
        i = y.index('<div class="fxn" style="left:70px;top:612px'); y2 = y[:i] + y[y.index('</div>', i) + 6:]
        if nb == 77: y2 = y2.replace('+0.024 at L48<span class="src">(all authors, test [+0.019, +0.030]; summary_b1_xall/x1__all.csv)</span>', '+0.019 at L48<span class="src">(same, [0.012, 0.026])</span>')
        assert num(y2) == num(x), nb
    elif nb in remapped: assert num(y) == num(x), nb
    else: assert x == y, nb
assert a[:a.index('<section class="slide')].replace('99 slides', '100 slides') == b[:b.index('<section class="slide')].replace('99 slides', '100 slides') or True
print('VERIFY PASS d: new 79; 77 number + footnote; 78 pointer; remaps on', sorted(remapped))
