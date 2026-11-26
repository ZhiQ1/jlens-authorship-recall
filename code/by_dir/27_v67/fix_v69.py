"""v69 from deck_v68.html (user 2026-11-23): relabelled chart images (64, 112), slide 86 layout, v67-number cells on 53/82/136,
135 ref, 35 marker, 23 verb. Add-only: nothing deleted except the on-screen '⚠ subtitle to confirm' marker the user asked to remove."""
import re, json, base64
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
t = open(W + 'deck_v68.html', encoding='utf-8').read()
M = {int(k): v for k, v in json.load(open(W + 'renumber_map_v68.json'))['v67_to_v68'].items()}
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
S = {i: m.group(0) for i, m in enumerate(ms, 1)}
LOG = []
def rep(n, a, b, cnt=1):
    s = S[n]; k = s.count(a); assert k >= cnt, (n, a[:60], k)
    S[n] = s.replace(a, b) ; LOG.append((n, a[:70], b[:70]))
# 1 chart images
for n, fn in ((64, 's64_plain.png'), (112, 's112_plain.png')):
    m = re.search(r'(<img[^>]*src="data:image/png;base64,)([^"]+)(")', S[n]); assert m
    new = base64.b64encode(open(W + 'regen_v69/' + fn, 'rb').read()).decode()
    S[n] = S[n][:m.start(2)] + new + S[n][m.end(2):]; LOG.append((n, 'chart image', fn))
# 2 bare v67 numbers in 'Slides' cells of the H1/H2 verdict cards and the evidence ledger
for n in (53, 82, 136):
    def cell(mm):
        nums = re.findall(r'\d+', mm.group(1))
        if not all(5 <= int(x) <= 160 for x in nums): return mm.group(0)
        new = re.sub(r'\d+', lambda q: str(M[int(q.group(0))]), mm.group(1))
        LOG.append((n, mm.group(1), new)); return mm.group(0).replace(mm.group(1), new)
    S[n] = re.sub(r'<td(?: style="[^"]*")?>(\d{1,3}(?:,\s*\d{1,3})*)</td>(?=</tr>)', cell, S[n])
# 3 S6: direction-driven damage is slide 106 (why pushing hurts), not 125 (direction asymmetry)
rep(135, '→ slides 123, 125', '→ slides 123, 106')
# 4 slide 35: on-screen confirmation marker removed (subtitle kept as approved earlier)
rep(35, '<span class="pmn">⚠ subtitle to confirm (the three checks are predictions, not readouts of results)</span>', '')
# 5 slide 23: overstrong verb
rep(23, 'the own state names its own first author better', "the paper's own state carries information about its first author", 2)
rep(23, 'can the title state name its own first author when read out by another prompt?', "does the paper's own title state carry information about its first author when read out by another prompt?")
# 6 slide 86: re-lay out so nothing is covered (row block ends well above the readout-map box at y 470)
rep(86, '<p class="m" style="font-size:24px;margin-top:60px">Opening question</p>', '<p class="m" style="font-size:22px;margin-top:30px">Opening question</p>')
rep(86, '<h1 class="b" style="font-size:84px;max-width:820px">', '<h1 class="b" style="font-size:70px;max-width:900px">')
rep(86, '<div class="row" style="margin-top:44px;gap:30px">', '<div class="row" style="margin-top:38px;gap:30px;max-height:150px">')
rep(86, '<p class="t">Is J-Lens better', '<p class="t" style="font-size:19px;line-height:1.3">Is J-Lens better')
rep(86, '<p class="t">Lenses read name shape', '<p class="t" style="font-size:19px;line-height:1.3">Lenses read name shape')
rep(86, '<text x="4" y="98" font-size="16" fill="var(--lG)" style="font-family:var(--hand)">probe</text>', '<text x="-9" y="102" font-size="16" fill="var(--lG)" style="font-family:var(--hand)">probe</text>')
out, last = [], 0
for i, m in enumerate(ms, 1):
    out.append(t[last:m.start()]); out.append(S[i]); last = m.end()
out.append(t[last:]); open(W + 'deck_v69.html', 'w', encoding='utf-8').write(''.join(out))
for l in LOG: print(*l, sep=' | ')
