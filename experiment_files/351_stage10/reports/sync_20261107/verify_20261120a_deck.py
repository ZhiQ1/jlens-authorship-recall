"""2026-11-20a: stage1_11_deck.html vs backup .before_20261120a: all 94 slides byte-identical except slide 27, whose only change is the n-line text;
everything outside the slides identical."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
A = (D / 'stage1_11_deck.html.before_20261120a').read_text(encoding='utf-8'); B = (D / 'stage1_11_deck.html').read_text(encoding='utf-8')
rec = json.loads((Path(__file__).parent / 'build_20261120a_deck.json').read_text())
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
SA, SB = sec(A), sec(B); bad = []
if len(SA) != 94 or len(SB) != 94: bad.append('count')
diff = [k + 1 for k in range(min(len(SA), len(SB))) if SA[k] != SB[k]]
if diff != [27]: bad.append(f'slides changed {diff}')
if SB[26].replace(rec['new'], rec['old']) != SA[26]: bad.append('S27 changed beyond the n line')
if '1,568' not in SB[26] or B.count('1,568 (stricter reuse rule)') != 1: bad.append('S27 new text')
_it = iter(SA); b = re.sub(r'<section class="slide.*?</section>', lambda m: next(_it), B, flags=re.S)
if b != A: bad.append('outside-slide changes')
print('slides identical:', 94 - len(diff), '/ 94; changed:', diff)
print('PASS' if not bad else 'FAIL'); print('\n'.join(bad))
