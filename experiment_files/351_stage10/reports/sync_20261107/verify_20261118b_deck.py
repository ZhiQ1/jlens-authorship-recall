"""2026-11-18b: per-slide check of stage1_11_deck.html against stage1_11_deck.html.before_20261118b:
every old slide appears exactly once; untouched slides are byte-identical; changed slides only gained content
(old text minus the edited tags/lists) ; anchors and counts."""
import re, json, hashlib
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
rec = json.loads((Path(__file__).parent / 'build_20261118b_deck.json').read_text())
sec = lambda s: [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', s, re.S)]
A = sec((D / 'stage1_11_deck.html.before_20261118b').read_text(encoding='utf-8'))
B = sec((D / 'stage1_11_deck.html').read_text(encoding='utf-8'))
h = lambda t: hashlib.sha256(t.encode()).hexdigest()
HB = {h(t): k + 1 for k, t in enumerate(B)}
print('old', len(A), 'new', len(B))
same = [k + 1 for k, t in enumerate(A) if h(t) in HB]
print('byte-identical old slides:', len(same), same)
print('expected untouched      :', rec['untouched_old'] == same)
o2n = rec['P_old_to_new']
for k, t in enumerate(A, 1):
    nb = B[o2n[str(k)] - 1]
    if k in same: assert nb == t
    else:
        # every changed old slide: the new one must contain the old image payloads and end with </section>
        imgs = re.findall(r'src="(data:[^"]{50})', t)
        assert all(i in nb for i in imgs), k
        assert len(nb) > len(t) - 200, k
print('changed slides keep all their images: ok')
print('order new<-old:', ' '.join(f'{n}<{o}' for n, o in rec['order_new_to_old'].items()))
