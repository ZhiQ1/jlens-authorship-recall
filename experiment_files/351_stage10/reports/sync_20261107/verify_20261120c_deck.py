import re
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261120c').read_text(); b = (D / 'stage1_11_deck.html').read_text()
A = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', a, re.S)]; B = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', b, re.S)]
assert len(A) == 96 and len(B) == 97 and B[:91] == A[:91] and B[92:] == A[91:]
assert a[:a.index('<section class="slide')] == b[:b.index('<section class="slide')]
ea = list(re.finditer(r'<section class="slide.*?</section>', a, re.S))[-1].end(); eb = list(re.finditer(r'<section class="slide.*?</section>', b, re.S))[-1].end()
strip = lambda t: re.sub(r'<nav class="toc-list".*?</nav>', '', t, flags=re.S).replace('97 slides', '96 slides')
assert strip(a[ea:]) == strip(b[eb:]) and b[eb:].count('class="toc-i"') == 97
print('VERIFY PASS: 96 old slides byte-identical, new slide 92, menu 97')
