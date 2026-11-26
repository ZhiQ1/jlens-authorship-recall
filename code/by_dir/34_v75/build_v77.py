"""2026-11-25 coordinator: HTML v76 -> v77 (user): restore the not-in-data bar's chance marker on slide 125 (it is the reading baseline of
the whole chart; only the '50.4% vs 50.5%' text comparison stays removed). Restored byte-identical from v75."""
import re
W = '/home/zhang.zhiqi2/jlens_work/'
t = open(W + '34_v75/deck_v76.html').read()
S = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, re.S)); m = S[124]; s = m.group(0)
mark = '<path d="M519.3 366.2 l6 -7 h-12 z" fill="#8A94A6"/><line x1="519.3" y1="367.2" x2="519.3" y2="394.2" stroke="#8A94A6" stroke-width="2"/>'
assert mark in open(W + '34_v75/deck_v75.html').read() and mark not in s
anchor = '<line x1="511.3" y1="381.2" x2="525.7" y2="381.2" stroke="#22304A" stroke-width="1.6"/>'
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + mark)
t = t[:m.start()] + s + t[m.end():]
open(W + '34_v75/deck_v77.html', 'w').write(t)
v75 = re.findall(r'<section class="slide[^"]*"[^>]*>.*?</section>', open(W + '34_v75/deck_v75.html').read(), re.S)[124]
print('ok; marker order same as v75:', v75.index(anchor) < v75.index(mark))
