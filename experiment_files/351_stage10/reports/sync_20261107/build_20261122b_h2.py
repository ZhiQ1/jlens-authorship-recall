"""HTML deck v52 -> v53 (2026-11-22): new H2 wording (user order; status stays 'partly supported'). Pure string replacements, each must match once."""
import hashlib, shutil, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck'); F = D / 'stage1_11_deck.html'; B = D / 'stage1_11_deck.html.before_20261122b'
if not B.exists(): shutil.copy2(F, B)
t = B.read_text()
import h2w_texts_20261122 as T
CORE = T.NEW_EN.replace('R̄_T', 'R̄<sub>T</sub>')
CAV = '<span class="src">' + T.CAV_EN + '</span>'
CAVS = '<span class="src">(Addendum 24: 3.4 vs 2.1 words replaced; common words frequency-matched, not synonyms, so meaning changes.)</span>'
R = [
 ('<b>Partly supported — meaning explains most</b> <span class="st c1">confirmed</span><span class="core">φ = 0.75 [0.723, 0.778], R̄ = +0.106 [0.094, 0.118] (add. 20, locked)</span>a same-meaning made-up title recovers three quarters of the true − false gap; only the real title gives the rest → slide 82',
  '<b>Partly supported</b> <span class="st c1">confirmed</span> ' + CORE + ' ' + CAVS + ' → slides 82–84'),
 ('<span class="was">Earlier, unchanged: M3 and X5 not above the L4 text level; X3 cannot separate meaning from paper identity; X4 decodes the first author (L8) before the year (L40), opposite to H2; X2 does not support H2 → slides 78, 82</span>',
  ''),
 ('made-up title recovers 0.75, real title +0.11 (add. 20) <span class="st c1">locked</span> → slide 82.',
  'made-up title recovers 0.75, real title +0.11 (add. 20) <span class="st c1">locked</span>; not larger for recognised papers (add. 22) → slide 82.'),
 ('<tspan x="70.0" dy="16.6">meaning similarity explains most of the signal. Not borderline; unchanged in every sensitivity analysis (φ_T 0.708–0.778).</tspan>',
  '<tspan x="70.0" dy="16.6">meaning similarity explains most. Not borderline (φ_T 0.708–0.778). Later: not larger for recognised papers (add. 22); see slide 84.</tspan>'),
 ('<b>So:</b> a same-meaning made-up title recovers 75% of the gap; the real title adds +0.11, so H2 is partly supported and meaning explains most of the signal.',
  '<b>So:</b> H2 partly supported — a real-title extra over a same-meaning made-up title exists (R̄<sub>T</sub> +0.106), mostly carried by meaning (75%); it is not larger for recognised papers (add. 22). Full wording with the addendum-24 caveats: slide 68.'),
 ('– H2 (paper identity): partly supported, meaning similarity explains most (addendum 20); the real-title extra is +0.11',
  '– H2 (paper identity): partly supported — the real-title extra (+0.106) is mostly meaning (75%) and not larger for recognised papers (add. 22); full wording on slide 68'),
]
for a, b in R:
    n = t.count(a)
    if n != 1: sys.exit(f'count {n}: {a[:80]}')
    t = t.replace(a, b)
F.write_text(t); print('v53 written', len(t), hashlib.sha256(t.encode()).hexdigest()[:12])
