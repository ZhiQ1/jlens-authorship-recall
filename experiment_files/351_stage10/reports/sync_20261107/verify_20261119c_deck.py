"""2026-11-19c: stage1_11_deck.html vs backup .before_20261119c: 94 slides, only the recorded slides changed, no visible CJK, no process
labels, a figure on every slide from 43, no 'robustness open / rerun pending / not established' left, item 2 slide has formula + n + footer."""
import re, json, html
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
rec = json.loads((Path(__file__).parent / 'build_20261119c_deck.json').read_text())
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
A = sec((D / 'stage1_11_deck.html.before_20261119c').read_text(encoding='utf-8')); B = sec((D / 'stage1_11_deck.html').read_text(encoding='utf-8'))
bad = []; ch = {int(k) for k in rec['changed']}
if len(A) != 94 or len(B) != 94: bad.append('count')
for k in range(1, 95):
    if (A[k - 1] != B[k - 1]) != (k in ch): bad.append(f'S{k} change status')
CJK = re.compile('[　-〿一-鿿＀-￯]')
BAN = re.compile(r'(?i)after the defen[cs]e|post-defen[cs]e|\bpost[- ]hoc\b|CPU leftovers|redo programme|since 11-1\d|update 11-1\d|added 2026-|\bleftover|robustness open|rerun pending|robustness not established')
for i, t in enumerate(B, 1):
    t2 = re.sub(r'data:[^"]+', '', t); v = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<desc>.*?</desc>|<!--.*?-->', '', t2, flags=re.S)))
    if CJK.search(v): bad.append(f'S{i} CJK')
    if BAN.search(v): bad.append(f'S{i} label {BAN.findall(v)}')
    if i >= 43 and not ('<img' in t or '<svg' in t): bad.append(f'S{i} no figure')
t = B[72]
if not ('data-name="formula"' in t and 'n = 600 papers' in t and 'y="693" class="src"' in t and 'Fixed step-2 check' in t): bad.append('S73 content')
print('changed:', sorted(ch)); print('PASS' if not bad else 'FAIL'); print('\n'.join(bad))
