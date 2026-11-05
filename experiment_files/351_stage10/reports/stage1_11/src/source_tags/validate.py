"""Usage: python validate.py SEG file.json  -> checks every old occurs exactly once in the segment, no overlaps, new minus src spans == old (unless entry has "fix": true)."""
import sys, json, re
sys.path.insert(0, __file__.rsplit('/',1)[0]); from segs import bounds, strip_src
s = open(__file__.rsplit('/',1)[0] + '/report_v26_readonly.html', encoding='utf-8').read()
seg, fn = sys.argv[1], sys.argv[2]
a, b = bounds(s)[seg]; t = s[a:b]
L = json.load(open(fn, encoding='utf-8')); bad = 0; spans = []; ntag = 0
for i, e in enumerate(L):
    o, n = e['old'], e['new']
    c = t.count(o)
    if c != 1: print('COUNT', c, i, repr(o[:80])); bad += 1; continue
    p = t.index(o); spans.append((p, p + len(o), i))
    if not e.get('fix') and strip_src(n) != o: print('CHANGED-TEXT', i, repr(o[:80])); bad += 1
    if 'class="src"' not in n and not e.get('fix'): print('NO-TAG', i); bad += 1
    if re.search('minyan', n, re.I): print('FORBIDDEN', i); bad += 1
    ntag += n.count('class="src"')
spans.sort()
for x, y in zip(spans, spans[1:]):
    if y[0] < x[1]: print('OVERLAP', x[2], y[2]); bad += 1
print(f'{seg}: {len(L)} entries, {ntag} tags, {bad} problems')
