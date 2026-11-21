"""v48 byte verify: 97 old slides kept (59, 68, 82, 88, 90, 94 changed only by the listed edits), 2 new slides at 81 and 86, head and gaps unchanged, menu 99."""
import re
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261121b').read_text(); b = (D / 'stage1_11_deck.html').read_text()
MA = list(re.finditer(r'<section class="slide.*?</section>', a, re.S)); MB = list(re.finditer(r'<section class="slide.*?</section>', b, re.S))
A = [m.group(0) for m in MA]; B = [m.group(0) for m in MB]
assert len(A) == 97 and len(B) == 99
old = lambda n: n if n <= 80 else (n - 1 if n <= 85 else n - 2)
ch = [n for n in range(1, 100) if n not in (81, 86) and B[n - 1] != A[old(n) - 1]]
assert ch == [59, 68, 82, 88, 90, 94], ch
for n in (68, 82, 88, 90, 94):  # only slide numbers changed
    x, y = A[old(n) - 1], B[n - 1]
    assert re.sub(r'slides? \d+(?:[–-]\d+)?|← slide 81: the extra is small at the title\.|← slide 80: the made-up title recovers three quarters\.', '#', x) == re.sub(r'slides? \d+(?:[–-]\d+)?|← slide 81: the extra is small at the title\.|← slide 80: the made-up title recovers three quarters\.', '#', y), n
x, y = A[58], B[58]; i = y.index('<text x="70" y="672"'); assert y[:i] + y[y.index('</text>', i) + 7:] == x
assert a[:MA[0].start()] == b[:MB[0].start()]
strip = lambda t: re.sub(r'<nav class="toc-list".*?</nav>', '', t, flags=re.S).replace('99 slides', '97 slides')
assert strip(a[MA[-1].end():]) == strip(b[MB[-1].end():]) and b[MB[-1].end():].count('class="toc-i"') == 99
print('VERIFY PASS: 91 slides byte-identical, 6 changed (59 line; 68/82/88/90/94 slide numbers), new 81 and 86, menu 99')
