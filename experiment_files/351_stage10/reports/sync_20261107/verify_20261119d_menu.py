"""2026-11-19d: stage1_11_deck.html vs backup .before_20261119d: all 94 slides byte-identical except the two recorded content fixes (75 pointer; item 4 settled), text outside the slides differs only by
the menu additions (CSS block, button, panel, syncToc call, menu JS), 94 menu items in slide order, no visible CJK in the menu."""
import re, html, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
A = (D / 'stage1_11_deck.html.before_20261119d').read_text(encoding='utf-8'); B = (D / 'stage1_11_deck.html').read_text(encoding='utf-8')
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
SA, SB = sec(A), sec(B); bad = []
if len(SA) != 94 or len(SB) != 94: bad.append('count')
diff = [k + 1 for k in range(min(len(SA), len(SB))) if SA[k] != SB[k]]
rec = json.loads((Path(__file__).parent / 'build_20261119d_menu.json').read_text())
exp = sorted(int(k) for k in rec['content_changed'])
if diff != exp: bad.append(f'slides changed {diff} != recorded {exp}')
if exp != [44, 51, 62, 68, 69, 75, 86]: bad.append(f'unexpected recorded set {exp}')
if '← slides 51, 74:' not in SB[74] or '← slides 51, 72' in SB[74]: bad.append('S75 pointer')
for k in exp[:-1] + [86]:
    if k != 75 and 'settled (locked criterion met)' not in SB[k - 1]: bad.append(f'S{k} item 4 status')
if 'Settled: locked criterion met (5 / 5 layers)' not in SB[74]: bad.append('S75 badge')
for k in range(94):
    if k + 1 not in exp and SA[k] != SB[k]: bad.append(f'S{k+1} changed')
# outside-slides: B with the menu additions removed must equal A
b = B
b = re.sub(r'<style>\n/\* jump menu \(2026-11-19d\) \*/.*?</style>', '', b, count=1, flags=re.S)
b = re.sub(r'<button id="tocbtn".*?</button>', '', b, count=1, flags=re.S)
b = re.sub(r'<div class="toc-scrim".*?</nav></div>', '', b, count=1, flags=re.S)
b = b.replace(' syncToc();}', '}', 1)
b = re.sub(r'  /\* jump menu \(2026-11-19d\) \*/\n.*?(?=  var m=/\^#s)', '', b, count=1, flags=re.S)
_it = iter(SA); b = re.sub(r'<section class="slide.*?</section>', lambda m: next(_it), b, flags=re.S)  # compare outside-slide text only
if b != A: bad.append('outside-slide changes beyond the menu')
items = re.findall(r'<a class="toc-i" href="#s(\d+)" data-i="(\d+)">', B)
if [int(h) for h, _ in items] != list(range(1, 95)) or [int(i) for _, i in items] != list(range(94)): bad.append('menu items')
panel = re.search(r'<div class="toc-scrim".*?</nav></div>', B, re.S).group(0)
vis = html.unescape(re.sub(r'<[^>]+>', ' ', panel + re.search(r'<button id="tocbtn".*?</button>', B, re.S).group(0)))
if re.search('[　-〿一-鿿＀-￯]', vis): bad.append('CJK in menu')
print('slides identical:', 94 - len(diff), '/ 94; changed:', diff, '; menu items:', len(items))
print('PASS' if not bad else 'FAIL'); print('\n'.join(bad))
