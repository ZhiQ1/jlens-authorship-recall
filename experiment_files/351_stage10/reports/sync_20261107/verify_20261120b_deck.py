"""2026-11-20b verify: every slide not listed as changed is byte-identical to the source; head/tail differ only in the menu."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261120b').read_text(); b = (D / 'stage1_11_deck.html').read_text()
A = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', a, re.S)]
B = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', b, re.S)]
assert len(A) == 94 and len(B) == 96, (len(A), len(B))
rec = json.load(open(Path(__file__).parent / 'build_20261120b_deck.json'))
changed = {int(k) for k in rec['changed']} | {k for k, _, _ in rec['remapped_refs']}
mapn = lambda k: k if k < 80 else k + 2
bad = [k for k in range(1, 95) if k not in changed and A[k - 1] != B[mapn(k) - 1]]
print('unchanged slides identical:', 94 - len(changed), 'mismatches', bad); assert not bad
for k in sorted(changed): print('changed', k, '->', mapn(k), len(A[k - 1]), '->', len(B[mapn(k) - 1]))
ha, hb = a[:a.index('<section class="slide')], b[:b.index('<section class="slide')]
assert ha == hb, 'head changed'
ea = list(re.finditer(r'<section class="slide.*?</section>', a, re.S))[-1].end(); eb = list(re.finditer(r'<section class="slide.*?</section>', b, re.S))[-1].end()
ta, tb = a[ea:], b[eb:]
strip = lambda t: re.sub(r'<nav class="toc-list".*?</nav>', '', t, flags=re.S).replace('96 slides', '94 slides')
assert strip(ta) == strip(tb), 'tail differs outside the menu'
print('items in menu:', tb.count('class="toc-i"'))
assert tb.count('class="toc-i"') == 96
print('VERIFY PASS')
