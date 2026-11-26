"""2026-11-25 coordinator: HTML v75 -> v76 (user: remove the remaining '50.4% vs 50.5%' comparisons on slide 125, same reason as the sticky note:
the shuffled value equals the observed one by construction). Bar label -> '50.4%', that bar's grey chance marker removed, Result ① reworded."""
import re
W = '/home/zhang.zhiqi2/jlens_work/'
t = open(W + '34_v75/deck_v75.html').read()
S = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, re.S)); assert len(S) == 184
m = S[124]; s = m.group(0); assert 'Made-up names are not confused neighbours' in s
pairs = [
 ('>50.4%  (chance 50.5%)</text>', '>50.4%</text>'),
 ('<path d="M519.3 366.2 l6 -7 h-12 z" fill="#8A94A6"/><line x1="519.3" y1="367.2" x2="519.3" y2="394.2" stroke="#8A94A6" stroke-width="2"/>', ''),
 ('about half are not in the data, <span class="mk">the same as the shuffled baseline (50.4% vs 50.5%)</span>;',
  '<span class="mk">about half (50.4%) are not in the data</span> (in none of the cohort’s author lists);'),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]; s = s.replace(a, b)
t = t[:m.start()] + s + t[m.end():]
open(W + '34_v75/deck_v76.html', 'w').write(t); print('ok')
