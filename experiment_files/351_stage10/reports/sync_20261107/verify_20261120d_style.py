"""2026-11-20d verify: only the 10 restyled slides differ; on them no number is added or lost (text nodes); head differs by the CSS block; menu differs only in the 10 titles."""
import re, sys, json, html
from pathlib import Path
a, b = Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()
rec = json.load(open(Path(__file__).parent / 'build_20261120d_style.json'))
labs = set(rec['slides'])
A = re.findall(r'<section class="slide.*?</section>', a, re.S); B = re.findall(r'<section class="slide.*?</section>', b, re.S)
assert len(A) == len(B), (len(A), len(B))
lab = lambda s: (re.search(r'aria-label="([^"]*)"', s) or [None, ''])[1]
NUM = re.compile(r'[+−-]?\d[\d,]*(?:\.\d+)?')
def nums(s):
    s = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', s, flags=re.S)
    txt = html.unescape(' '.join(re.findall(r'>([^<]+)<', s)))
    return set(n.lstrip('+−-') for n in NUM.findall(txt))
bad = []
for i, (x, y) in enumerate(zip(A, B), 1):
    if lab(x) in labs:
        nx, ny = nums(x), nums(y)
        added, lost = ny - nx, nx - ny
        print(i, lab(x)[:45], '| numbers', len(nx), '-> added', sorted(added), 'lost', sorted(lost))
        if added or lost: bad.append(i)
    elif x != y: print('UNEXPECTED change', i, lab(x)); bad.append(i)
ha, hb = a[:a.index('<section class="slide')], b[:b.index('<section class="slide')]
assert hb.replace(re.search(r'<style>\n/\* key-number note.*?</style>', hb, re.S).group(0), '') == ha, 'head differs beyond CSS'
ea = list(re.finditer(r'<section class="slide.*?</section>', a, re.S))[-1].end(); eb = list(re.finditer(r'<section class="slide.*?</section>', b, re.S))[-1].end()
ta, tb = a[ea:], b[eb:]
for v in rec['slides'].values():
    tb = tb.replace(html.escape(v['new_title'], quote=False), html.escape(v['old_title'], quote=False))
assert ta == tb, 'tail differs beyond the 10 menu titles'
print('VERIFY', 'FAIL' if bad else 'PASS', bad)
