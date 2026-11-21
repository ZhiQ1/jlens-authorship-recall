"""v47 byte verify: only the 25 listed slides changed; head differs only by the added <style> block; after the slides only the contents menu (Stage 12-13 split into 4 groups)."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
a = (D / 'stage1_11_deck.html.before_20261121a').read_text(); b = (D / 'stage1_11_deck.html').read_text()
rec = json.load(open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121a_deck.json'))
MA = list(re.finditer(r'<section class="slide.*?</section>', a, re.S)); MB = list(re.finditer(r'<section class="slide.*?</section>', b, re.S))
A = [m.group(0) for m in MA]; B = [m.group(0) for m in MB]
assert len(A) == len(B) == 97
ch = [i + 1 for i in range(97) if A[i] != B[i]]; assert ch == rec['changed'], ch
assert [A[i][:A[i].index('>')] for i in range(97)] == [B[i][:B[i].index('>')] for i in range(97)]
ha, hb = a[:MA[0].start()], b[:MB[0].start()]
i = hb.index('/* narrative line + hypothesis table (2026-11-21a) */'); j0 = hb.rfind('<style>', 0, i); j1 = hb.index('</style>', i) + 8
assert hb[:j0] + hb[j1:] == ha
gaps_a = [a[MA[k].end():MA[k + 1].start()] for k in range(96)]; gaps_b = [b[MB[k].end():MB[k + 1].start()] for k in range(96)]; assert gaps_a == gaps_b
ta, tb = a[MA[-1].end():], b[MB[-1].end():]
strip = lambda t: re.sub(r'<nav class="toc-list".*?</nav>', '', t, flags=re.S)
assert strip(ta) == strip(tb)
na = re.findall(r'<li>.*?</li>', re.search(r'<nav class="toc-list".*?</nav>', ta, re.S).group(0), re.S)
nb = re.findall(r'<li>.*?</li>', re.search(r'<nav class="toc-list".*?</nav>', tb, re.S).group(0), re.S)
assert na == nb and len(nb) == 97
heads = re.findall(r'<h3 class="toc-h"[^>]*>(.*?)<span class="toc-r">(.*?)</span>', tb)
print(heads)
assert len(heads) == 12
for k in rec['ask']: assert 'Now asking:' in B[int(k) - 1]
for k in rec['so']: assert '<b>So:</b>' in B[int(k) - 1]
assert '<img alt="Hypotheses H1–H3 against readouts' not in B[67] and '<table class="hx">' in B[67]
print('VERIFY PASS: 72 slides byte-identical; changed', ch, '; head = +1 style block; menu 12 groups / 97 items unchanged')
