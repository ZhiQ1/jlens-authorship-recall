"""Update the Stage 1-11 merged deck: refresh the Stage 10-11 image slides from the current deck renders,
insert the R0/R1 slides into Line A, and edit the Line A comparison / overview pages."""
import base64, re, sys
from pathlib import Path
src, pages, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
s = src.read_text()
old2new = lambda n: n if n <= 12 else (n + 1 if n <= 18 else n + 2)      # v7 (25 pages) -> v8 (27 pages)
img = lambda n: 'data:image/jpeg;base64,' + base64.b64encode((pages / f'p{n:02d}.jpg').read_bytes()).decode()
def repl(m):
    n = old2new(int(m.group(1)))
    return f'<section class="slide im" aria-label="{m.group(2)}"><img alt="Stage 10-11 slide {n}" src="{img(n)}"></section>'
s, k = re.subn(r'<section class="slide im" aria-label="([^"]*)"><img alt="Stage 10-11 slide (\d+)" src="data:image/jpeg;base64,[A-Za-z0-9+/=]+"></section>',
               lambda m: repl(type('M', (), {'group': lambda self, i: {1: m.group(2), 2: m.group(1)}[i]})()), s)
print('image slides refreshed:', k)
# insert the two R0/R1 slides after the last Line A image slide (old deck slide 22 -> new 24), before the Line A comparison page
anchor = re.search(r'<section class="slide im" aria-label="[^"]*"><img alt="Stage 10-11 slide 24"[^>]*></section>', s)
assert anchor
new = ''.join(f'<section class="slide im" aria-label="R0/R1"><img alt="Stage 10-11 slide {n}" src="{img(n)}"></section>' for n in (13, 20))
s = s[:anchor.end()] + new + s[anchor.end():]
def sub(old, newtxt):
    global s
    assert s.count(old) == 1, old[:60]; s = s.replace(old, newtxt)
# Line A comparison page
sub('<li>Signal rises steadily with citations (ρ = 0.45)</li></ul>',
    '<li>Signal rises steadily with citations (ρ = 0.45)</li><li>Same groups as the pilot (R0 only, A − B): <span class="b">+0.20</span> [0.19, 0.21], same late shape</li><li>R1 papers (C) know more (+0.11 over A) but are just as late</li></ul>')
sub('so the 7-layer average and the L56 endpoint both diluted it.</div>',
    'so the 7-layer average and the L56 endpoint both diluted it. Restricting the full cohort to the pilot’s A/B groups (R0 only) changes nothing: the R1 papers do not drive the result.</div>')
# design page note
sub('<b>Note:</b> target/control include R1 papers; an R0-only check keeps it comparable to A/B.',
    '<b>Note:</b> target/control include R1 papers; with R0 only (A vs B, as in the pilot) the output gap is +0.199 vs +0.207 and every layer looks the same.')
# overview tables
sub('<td>10 title-specific signal, 11 name prior, probe controls</td>', '<td>10 title-specific signal, 11 name prior, probe controls, R0/R1 split</td>')
sub('<tr><td>Key layer</td><td>L56</td>',
    '<tr><td>Same groups (A vs B, R0 only)</td><td>A − B as above</td><td>+0.20 at output, ≈0 middle; R1 adds strength, not timing</td><td class="g">comparable, unchanged</td></tr>\n<tr><td>Key layer</td><td>L56</td>')
out.write_text(s); print('wrote', out, len(s) // 1024, 'KB')
