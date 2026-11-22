"""v50 verify vs published v49 (.before_20261121e): one new slide (76); other slides change only by slide-number remaps."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261121e').read_text(); b = (D / 'stage1_11_deck.html').read_text()
F = lambda t: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', t, re.S)]
A, B = F(a), F(b); assert len(A) == 100 and len(B) == 101
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121e_deck.json'))
remapped = set(rec['refs_remapped_on_slides'])
num = lambda t: re.sub(r'(\bslides? )\d{1,3}(?:[–-]\d{1,3})?', r'\1N', t)
for nb in range(1, 102):
    if nb == 76: continue
    na = nb if nb <= 75 else nb - 1
    x, y = A[na - 1], B[nb - 1]
    if nb in remapped: assert num(y) == num(x), nb
    else: assert x == y, nb
print('VERIFY PASS e: new 76; remaps on', sorted(remapped))
