"""Agent A pages for v67: how-to-read (Part 0) and gap-picture (Part 2). Replaces their placeholder sections in deck_v67.html."""
import re, json
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
D = W + 'deck_v67.html'
t = open(D, encoding='utf-8').read()
REN = json.load(open(W + 'renumber_map.json'))['v66_to_v67']
p = lambda n: REN[str(n)]
src = open(W + 'live_v66.html', encoding='utf-8').read()
secs = re.findall(r'<section class="slide[^"]*"[^>]*>.*?</section>', src, flags=re.S)
# grey formula block of the exposure page (same quantity, same n): reuse it verbatim, reading line kept
s29 = secs[28]
i = s29.find('<div class="fxu"'); j = s29.find('<div class="fxkey">', i); k = s29.find('</div>', j) + 6
fxu = s29[i:k] + '</div>'
assert fxu.count('<div') == fxu.count('</div>'), (fxu.count('<div'), fxu.count('</div>'))
fxu = re.sub(r'style="left:\d+px;top:\d+px;width:\d+px"', 'style="left:120px;top:470px;width:780px"', fxu, 1)

TAGS = [('settled', 'settled', 'shown with interventions or the full cohort; not in doubt'),
        ('lsup', 'locked · supported', 'a rule fixed before the run, and the result passed it'),
        ('lnot', 'locked · not supported', 'a rule fixed before the run, and the result failed it'),
        ('desc', 'descriptive', 'measured, but no test decides it'),
        ('expl', 'exploratory', 'a clue only: looked at after the fact'),
        ('solid', 'fairly solid', 'several checks agree, no locked test')]
rows = ''.join(f'<div class="it"><span class="tg {c}">{l}</span> {d}</div>' for c, l, d in TAGS)
how = f'''<section class="slide lt" aria-label="How to read this deck" data-slot="how-to-read"><span class="tag">How to read</span>
<h2 style="font-size:46px;margin-top:6px">How to read this deck</h2>
<p class="askl" style="color:#22304A"><b>Now asking:</b> what do the coloured tags, the grey lines and the cards mean?</p>
<div class="cats" style="left:70px;top:190px;width:540px;font-size:15px;line-height:1.35">
<div class="it"><span class="k">Evidence tags:</span> every result carries one</div>{rows}
<div class="it" style="margin-top:6px"><span class="k">Caveat:</span> <span class="ul">exploratory results are never used for a conclusion</span>; they are marked “clue”.</div></div>
<div class="cats" style="left:660px;top:190px;width:560px;font-size:15px;line-height:1.35">
<div class="it"><span class="k">Three grey lines under every chart:</span></div>
<div class="it"><span class="q">1</span> the formula of the plotted number (LaTeX)</div>
<div class="it"><span class="q">2</span> the sample size n (LaTeX)</div>
<div class="it"><span class="q">3</span> one reading, e.g. <span style="color:#8a8f98">“R ≈ 1: fully restored”</span></div>
<div class="it" style="margin-top:8px"><span class="k">Parts 3–6 follow one pattern:</span></div>
<div class="it">question card → <span class="mk">experiments</span> → verdict card → evidence matrix</div>
<div class="it" style="margin-top:8px"><span class="k">Names:</span> plain test names on the slides; codes and file names are in the Glossary, slide {p(107)}, and in the script.</div>
<div class="it"><span class="k">Method figures:</span> how to read them, slide {p(5)}.</div></div>
<svg viewBox="0 0 1280 720" width="1280" height="720" style="position:absolute;left:0;top:0;pointer-events:none" aria-hidden="true">
<g font-family="'Patrick Hand',Caveat,cursive" font-size="15" fill="#22304A">
<rect x="70" y="560" width="1150" height="92" rx="10" fill="#FFF6DC" stroke="#D9772B" stroke-dasharray="5 4"/>
<g transform="translate(95,606)">
<rect x="0" y="-20" width="190" height="40" rx="8" fill="#fff" stroke="#3C78B4"/><text x="95" y="5" text-anchor="middle">question card</text>
<path d="M200 0 H260" stroke="#22304A" stroke-width="2" marker-end="url(#ahA)"/>
<rect x="270" y="-20" width="300" height="40" rx="8" fill="#fff" stroke="#22304A"/><text x="420" y="5" text-anchor="middle">experiment pages (schematic → chart)</text>
<path d="M580 0 H640" stroke="#22304A" stroke-width="2" marker-end="url(#ahA)"/>
<rect x="650" y="-20" width="190" height="40" rx="8" fill="#fff" stroke="#2E7D46"/><text x="745" y="5" text-anchor="middle">verdict card</text>
<path d="M850 0 H910" stroke="#22304A" stroke-width="2" marker-end="url(#ahA)"/>
<rect x="920" y="-20" width="180" height="40" rx="8" fill="#fff" stroke="#6A7385"/><text x="1010" y="5" text-anchor="middle">evidence matrix</text></g>
<defs><marker id="ahA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#22304A"/></marker></defs></g></svg>
<div class="soln" style="left:70px;top:666px;width:1150px"><b>So (section):</b> the setup is fixed; next, the first finding: the model recognises papers it cannot write the authors of (Part 2). <span class="tg desc">descriptive</span></div>
<span class="pg"></span></section>'''

import math
X = lambda c: 120 + math.log10(1 + c) / 5.0 * 900
ticks = ''.join(f'<line x1="{X(c):.1f}" y1="330" x2="{X(c):.1f}" y2="338" stroke="#22304A" stroke-width="1.6"/><text x="{X(c):.1f}" y="356" text-anchor="middle" fill="#6A7385">{lab}</text>'
                for c, lab in [(0, '0'), (10, '10'), (100, '100'), (1000, '1k'), (10000, '10k'), (100000, '100k')])
xr, xw = X(40), X(11038)
xr_lo, xr_hi, xw_lo, xw_hi = X(36), X(44), X(8172), X(15607)
gap = f'''<section class="slide lt" aria-label="The gap in one picture" data-slot="gap-picture"><span class="tag">Recognised but not said</span>
<h2 style="font-size:42px;margin-top:6px">The gap in one picture: writing needs about 276× the exposure of recognising</h2>
<p class="askl" style="color:#22304A"><b>Now asking:</b> on one citation axis, where does recognising start, and where does writing start?</p>
<svg viewBox="0 0 1280 720" width="1280" height="720" style="position:absolute;left:0;top:0" role="img" aria-label="Recognition and writing thresholds on one citation axis">
<g font-family="'Patrick Hand',Caveat,cursive" font-size="15" fill="#22304A">
<line x1="120" y1="330" x2="1020" y2="330" stroke="#22304A" stroke-width="2"/>{ticks}
<text x="570" y="384" text-anchor="middle" fill="#6A7385">citations of the paper (log scale)</text>
<rect x="{xr_lo:.1f}" y="300" width="{xr_hi-xr_lo:.1f}" height="30" fill="#3C78B4" opacity=".25"/>
<line x1="{xr:.1f}" y1="230" x2="{xr:.1f}" y2="330" stroke="#3C78B4" stroke-width="3"/>
<circle cx="{xr:.1f}" cy="330" r="9" fill="#3C78B4" stroke="#fff" stroke-width="2"/>
<text x="{xr:.1f}" y="200" text-anchor="middle" fill="#3C78B4" font-size="17">① recognising: half the papers</text>
<text x="{xr:.1f}" y="220" text-anchor="middle" fill="#3C78B4" font-size="17">at c50 = 40 [36, 44]</text>
<rect x="{xw_lo:.1f}" y="300" width="{xw_hi-xw_lo:.1f}" height="30" fill="#C84A3E" opacity=".25"/>
<line x1="{xw:.1f}" y1="230" x2="{xw:.1f}" y2="330" stroke="#C84A3E" stroke-width="3"/>
<circle cx="{xw:.1f}" cy="330" r="9" fill="#C84A3E" stroke="#fff" stroke-width="2"/>
<text x="{xw:.1f}" y="200" text-anchor="middle" fill="#C84A3E" font-size="17">② writing ≥ 1 true author: half</text>
<text x="{xw:.1f}" y="220" text-anchor="middle" fill="#C84A3E" font-size="17">at c50 = 11,038 [8,172, 15,607]</text>
<path d="M{xr:.1f} 262 H{xw:.1f}" stroke="#22304A" stroke-width="2" marker-start="url(#ahG)" marker-end="url(#ahG)"/>
<rect x="{(xr+xw)/2-95:.1f}" y="244" width="190" height="34" rx="8" fill="#FFF6DC" stroke="#D9772B"/>
<text x="{(xr+xw)/2:.1f}" y="267" text-anchor="middle" font-size="18"><tspan font-weight="700">③ ρ = 276</tspan> [203, 390]</text>
<text x="{(xr+400)/2:.1f}" y="420" text-anchor="middle" fill="#3C78B4">recognised but not said: papers in this stretch</text>
<path d="M{xr+10:.1f} 400 H{xw-10:.1f}" stroke="#D9772B" stroke-width="10" opacity=".25"/>
<defs><marker id="ahG" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#22304A"/></marker></defs>
</g></svg>
{fxu}
<div class="cats" style="left:930px;top:400px;width:300px;font-size:14.5px;line-height:1.3">
<div class="it"><span class="k">Result:</span> <span class="q">1</span> recognising starts at about <b>40</b> citations; <span class="q">2</span> writing at about <b>11,038</b>.</div>
<div class="it"><span class="k">Result:</span> <span class="q">3</span> the gap is <b>ρ = 276</b> [203, 390].</div>
<div class="it"><span class="k">Caveat:</span> <span class="ul">the exact ratio was locked after seeing the estimates; only ρ &gt; 1 is confirmed</span>.</div>
<div class="it"><span class="k">Source:</span> same fit as slide {p(29)}.</div></div>
<div class="soln" style="left:70px;top:620px;width:1150px"><b>So (section):</b> <span class="mk">recognised but not said</span> is a large exposure gap; next we ask what the model reads early — the question and the title (Part 3). <span class="tg lsup">locked · ρ &gt; 1</span></div>
<span class="pg"></span></section>'''

def put(slot, html_):
    global t
    m = re.search(r'<section class="slide lt" aria-label="[^"]*" data-slot="%s">.*?</section>' % re.escape(slot), t, flags=re.S)
    assert m, slot
    t = t[:m.start()] + html_ + t[m.end():]
put('how-to-read', how); put('gap-picture', gap)
open(D, 'w', encoding='utf-8').write(t)
print('ok')
