"""2026-11-19b: checks of stage1_11_deck.html against the v40 backup stage1_11_deck.html.before_20261119b:
every v40 slide present in the recorded order; slides not listed as changed byte-identical; the two new slides at 72-73;
no visible CJK, no process labels, a figure on every slide from 43, formula + grey n on the new slides, no stale "slide N"
reference (every "slide N" on an old slide maps to the same slide title it pointed to in v40), new-slide lower third <= 2 lines each."""
import re, json, html
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
rec = json.loads((Path(__file__).parent / 'build_20261119b_deck.json').read_text())
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
A = sec((D / 'stage1_11_deck.html.before_20261119b').read_text(encoding='utf-8'))
full = (D / 'stage1_11_deck.html').read_text(encoding='utf-8'); B = sec(full)
print('v40', len(A), 'new', len(B)); bad = []
n2o = {int(k): v for k, v in rec['order_new_to_v40'].items()}
o2n = {v: k for k, v in n2o.items() if isinstance(v, int)}
if len(B) != 94 or sorted(o2n) != list(range(1, 93)): bad.append('slide set')
if n2o[72] != 'N3' or n2o[73] != 'N2': bad.append('new slides not at 72-73')
changed = {int(k) for k in rec['changed_v40']}
ident = [k for k in range(1, 93) if B[o2n[k] - 1] == A[k - 1]]
for k in range(1, 93):
    if k not in changed and k not in ident: bad.append(f'v40 S{k} changed but not recorded')
    if k in changed and k in ident: bad.append(f'v40 S{k} recorded as changed but identical')
print('byte-identical v40 slides:', len(ident), '; changed:', sorted(changed))
CJK = re.compile('[　-〿一-鿿＀-￯]')
BAN = re.compile(r'(?i)after the defen[cs]e|post-defen[cs]e|\bpost[- ]hoc\b|CPU leftovers|redo programme|since 11-1\d|update 11-1\d|added 2026-|\bleftover')
vis_ = lambda t: html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<desc>.*?</desc>|<!--.*?-->', '', re.sub(r'data:[^"]+', '', t), flags=re.S)))
for i, t in enumerate(B, 1):
    v = vis_(t); attrs = ' '.join(re.findall(r'(?:aria-label|alt)="([^"]*)"', re.sub(r'data:[^"]+', '', t)))
    if CJK.search(v + attrs): bad.append(f'S{i}: CJK')
    if BAN.search(v + attrs): bad.append(f'S{i}: process label {BAN.findall(v + attrs)}')
    if i >= 43 and not ('<img' in t or '<svg' in t): bad.append(f'S{i}: no figure')
# stale references: each "slide N" in a v40 slide should point to the same slide (by aria-label) after the move
aria = lambda t: re.search(r'aria-label="([^"]*)"', t).group(1)
for k in range(1, 93):
    ra = re.findall(r'\bslides? (\d{1,3})', re.sub(r'data:[^"]+', '', A[k - 1]))
    rb = re.findall(r'\bslides? (\d{1,3})', re.sub(r'data:[^"]+', '', B[o2n[k] - 1]))
    for x in ra:
        n_old = int(x)
        if not (1 <= n_old <= 92): continue
        tgt = aria(A[n_old - 1]); n_new = o2n[n_old]
        if str(n_new) not in rb: bad.append(f'v40 S{k}: reference to slide {n_old} ({tgt[:30]}) not remapped to {n_new}')
for i in (72, 73):
    t = B[i - 1]
    if 'data-name="formula"' not in t or 'n = 600 papers' not in t: bad.append(f'S{i}: formula / n missing')
    if '<div class="lead">' not in t: bad.append(f'S{i}: lead missing')
    if 'y="693" class="src"' not in t: bad.append(f'S{i}: footer strip missing')
# new references point to the intended slides
for i, n, word in [(72, 73, 'item 2'), (73, 74, 'item 6'), (71, 72, 'item 3')]:
    if word.split()[-1] not in aria(B[n - 1]): bad.append(f'S{i}: pointer to slide {n} is not {word}')
print('PASS' if not bad else 'FAIL'); print('\n'.join(bad))
