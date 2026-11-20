"""2026-11-18b: weave the 2026-11-18 slides of the merged HTML deck into its argument (user feedback: new content was
"just tacked on"). Mirrors gslides_20261112/integration_map_v20.md (pptx v20), mapped by content onto this deck's own order.
Source = merged_deck/stage1_11_deck.html.before_20261118b (backup taken before any change) -> merged_deck/stage1_11_deck.html.
  1. REORDER (whole slides, nothing deleted; old numbers = before_20261118b):
     88 (add. 19)  -> after 26 "More citations, more paper knowledge" (Line A)
     86 (add. 16 B + D) -> after 57 "Co-authors help, and partly replace the title" (Line D, before the Line D summary)
     75 (18b item 1) -> after 66 "Layer order (X5)"
     77, 78 (18b items 6, 4) -> after 67 "Stage 12: where the paper information travels" (route)
     76 (18b item 5) -> after 70 "Patchscope and paraphrases"
     87 (C, fabricated names) -> after 74 "Names the model writes itself (C24)"
     planned, not inserted: 18b item 3 then item 2 between the route (67) and item 6 (77).
  2. NEW slide "What we learned, continued" after 79 "What we learned".
  3. Lead line ("<- slide X ... Here: ... -> slide Y") + new tag on every moved slide.
  4. Add-beside boxes / extra bullets on synthesis slides (2, 12, 30, 31, 40, 41, 50, 51, 58, 59, 65, 66, 80, 81).
  5. Formula + grey "n = ... papers" line on every chart/number slide that had none.
Writes build_20261118b_deck.json (order, changed slides). Idempotent: always rebuilds from the backup."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
SRC = D / 'stage1_11_deck.html.before_20261118b'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 91, len(ms)
head, tail = s[:ms[0].start()], s[ms[-1].end():]
S = {k + 1: m.group(0) for k, m in enumerate(ms)}
ORIG = dict(S)

# ---------------------------------------------------------------- order
order = list(range(1, 13)) + [42, 13, 43] + list(range(14, 27)) + [88] + list(range(27, 42)) + [44, 45, 48, 46, 47] + list(range(49, 58)) + [86] + list(range(58, 67)) + [75, 67, 77, 78, 68, 69, 70, 76, 71, 72, 73, 74, 87, 79, 'WL', 80] + list(range(81, 86)) + [89, 90, 91]
assert sorted(x for x in order if x != 'WL') == list(range(1, 92)), 'order must keep every slide once'
P = {o: k + 1 for k, o in enumerate(order)}

# ---------------------------------------------------------------- css
CSS = '''<style>
.fxn{position:absolute;z-index:3;font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;font-size:12px;line-height:1.5;color:#8a8f98}
.fxn .fx{display:inline-block;font-family:"STIX Two Math","Cambria Math","Latin Modern Math","DejaVu Serif","Times New Roman",serif;font-style:italic;font-size:13px;line-height:1.35;color:#22304A;background:#FFF6DC;border:1.2px solid #D9772B;border-radius:8px;padding:1px 8px;margin-right:9px}
.fxn .nn{color:#8a8f98;white-space:normal}
.dk .fxn .nn,.fxn.d .nn{color:#AAB4C5}
.dk .fxn .fx,.fxn.d .fx{background:#262c38;color:#F2E3A6;border-color:#F6A65A}
.addb{position:absolute;z-index:3;background:#FFF6DC;color:#22304A;border:1.6px dashed #D9772B;border-radius:10px;padding:6px 11px;font-family:var(--hand);font-size:16px;line-height:1.3}
.addb b{color:#B54708;font-weight:700}
.addb .st{font-family:"Noto Sans SC",system-ui,sans-serif;font-size:11px;padding:0 5px;border-radius:5px;border:1px solid currentColor;white-space:nowrap}
.addb .c1{color:#2E7D46}.addb .c2{color:#3C78B4}.addb .c3{color:#B54708}.addb .c4{color:#6A7385}
.lead{position:absolute;left:70px;top:38px;max-width:830px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;z-index:3;font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;font-size:12.5px;line-height:1.35;color:#4B5363}
.lead b{color:#3C78B4}
.dk .lead{color:#AAB4C5}.dk .lead b{color:#7DC4F5}
li.new{font-size:17px;line-height:1.28}
.wl{display:grid;grid-template-columns:250px 1fr;column-gap:24px;row-gap:12px;margin-top:20px;align-items:baseline}
.wl .k{font-family:var(--title);font-size:34px;line-height:1}
.wl .v{font-size:19.5px;line-height:1.33}
.wl .st{font-family:"Noto Sans SC",system-ui,sans-serif;font-size:12px;padding:0 5px;border-radius:5px;border:1px solid currentColor;white-space:nowrap}
</style>'''
assert head.count('</head>') == 1
head = head.replace('</head>', CSS + '</head>')

CHANGED = {}


def ins(old, html, note):
    """insert html just before the closing </section> of old slide"""
    t = S[old]
    assert t.endswith('</section>')
    S[old] = t[:-len('</section>')] + html + '</section>'
    CHANGED.setdefault(old, []).append(note)


def rep(old, a, b, note):
    assert S[old].count(a) == 1, (old, S[old].count(a), a[:60])
    S[old] = S[old].replace(a, b)
    CHANGED.setdefault(old, []).append(note)


def fxn(old, left, top, width, formula, n, dark=False):
    f = f'<span class="fx">{formula}</span>' if formula else ''
    nn = f'<span class="nn">{n}</span>' if n else ''
    ins(old, f'<div class="fxn{" d" if dark else ""}" style="left:{left}px;top:{top}px;width:{width}px">{f}{nn}</div>',
        'formula + n' if formula else 'n line (formula already on the slide)')


def addb(old, left, top, width, html, note, extra=''):
    ins(old, f'<div class="addb" style="left:{left}px;top:{top}px;width:{width}px;{extra}">{html}</div>', note)


ST = {'confirmed': 'c1', 'supported': 'c2', 'exploratory': 'c3', 'descriptive': 'c4'}


def st(label, key=None):
    return f'<span class="st {ST[key or label.split()[0].strip(",;")]}">{label}</span>'


# ---------------------------------------------------------------- 3. moved slides: lead + tag
LEADS = {
    88: (f'← slide {P[26]}: more citations, more knowledge.', 'how much exposure do recognising and writing need?', f'→ slide {P[27]}'),
    86: (f'← slide {P[57]}: co-authors help, partly replace the title.', 'this paper, or who works with whom? does the format matter?', f'→ slide {P[58]}'),
    75: (f'← slide {P[66]}: when each fact first appears.', 'is the author on an earlier shelf at some prompt position?', f'→ route, slide {P[67]}'),
    77: (f'← slide {P[67]}: attention at L48, then MLPs at L52–L56.', 'is that MLP step a memory lookup?', f'→ who writes L57–L61? slide {P[78]}'),
    78: (f'← slides {P[50]}, {P[77]}: steepest rise at L57–L61.', 'who writes the last layers?', f'→ 5-false-title timing, slide {P[68]}'),
    76: (f'← slide {P[70]}: a paraphrase keeps ≈ 90% of the preference.', 'which title words carry it?', f'→ subspace swap, slide {P[71]}'),
    87: (f'← slide {P[74]}: the probe tells true from made-up names.', 'are made-up names confused neighbours?', f'→ slide {P[79]}'),
    42: (f'← slide {P[12]}: is it about this paper?', 'is any author signal there at all?', f'→ crossed control, slide {P[13]}'),
    43: (f'← slide {P[13]}: the title changes which name wins.', 'does gold beat 100 real names more for A than B?', f'→ shuffled titles, slide {P[14]}'),
    48: (f'← slides {P[44]}–{P[45]}: readable only in the last layers.', 'intervene, do not just read', f'→ method pictures, slides {P[46]}–{P[47]}'),
}
for old, (a, b, c) in LEADS.items():
    top = ' style="top:26px"' if old == 48 else ''   # picture slide: its title starts higher
    ins(old, f'<div class="lead"{top}>{a} <b>Here:</b> {b} {c}</div>', 'lead line')
rep(88, '>Added after the defence · groups<', '>Line A · addendum 19<', 'tag')
rep(86, '>Added after the defence · groups<', '>Line D · addendum 16<', 'tag')
rep(87, '>Added after the defence · groups<', '>Stage 13 · exploratory<', 'tag')

# ---------------------------------------------------------------- 4. synthesis slides
rep(2, '<span style="color:#9B7BD8;border:1.5px solid #9B7BD8">purple tag = comparison</span>',
    '<span style="color:#9B7BD8;border:1.5px solid #9B7BD8">purple tag = comparison</span><span style="color:#B54708;border:1.5px dashed #D9772B;background:#FFF6DC;font-size:15px">new results sit inside their lines: A exposure (add. 19) · D format, chain (add. 16) · 12–13 route, title words, made-up names (add. 18b, C)</span>',
    'pill: where the new results sit')
addb(12, 70, 470, 1140, f'<b>+ addendum 19</b> {st("confirmed")} <span style="font-size:13px">(lock made after the data had been seen)</span>: writing an author needs far more exposure than recognising the paper → slide {P[88]}<br><b>Order:</b> the small samples now run Stage 4 → 5 → 7.2 → 7.3 (slides {P[42]}–{P[14]}): each slide’s own conclusion leads to the next', 'box: add. 19, new order')
addb(31, 70, 470, 1140, f'<b>+ addendum 18b item 1</b> {st("exploratory")}: the readout map over prompt positions × layers, before the name → slide {P[75]}', 'box: item 1')
addb(41, 70, 560, 1140, f'<b>+ addendum 18b:</b> who writes the L57–L61 rise? the MLPs (item 4) {st("confirmed")} → slide {P[78]} · the L52–L56 MLPs carry paper information, not name directions (item 6) {st("descriptive")} → slide {P[77]}<br><b>Moved:</b> the Stage 4 and 7.2 small-sample slides now sit in Line A (slides {P[42]}, {P[43]}); the summary (slide {P[50]}) still quotes them · Stage 11 design (slide {P[48]}) now comes before its method pictures', 'box: items 4, 6, moves')
addb(51, 70, 560, 1140, f'<b>+ addendum 16:</b> answer format (only F4, a given first initial, helps) {st("supported")} and co-author chain (a network association, not memory of this paper) → slide {P[86]}', 'box: add. 16')
# Line A summary: right column full -> card in the left half
addb(30, 70, 326, 540, f'<b>Since 11-14 · full cohort</b><br>Exposure gap {st("confirmed")} (add. 19; lock made after the data had been seen): recognising ≈ 40 citations, writing ≈ 11,000, ρ = 276 [203, 390] → slide {P[88]}<br>Co-author chain (add. 16): a real effect (+0.167), but a co-author network association, not memory of this paper → slide {P[86]}', 'card: add. 19, add. 16', 'font-size:15px;transform:rotate(-.6deg)')
fxn(30, 70, 452, 540, 'T − C = Σ<sub>b</sub> w<sub>b</sub> (spec<sub>T,b</sub> − spec<sub>C,b</sub>)', 'n = 50 / 200 papers, 100 pairs (Stages 1–9) · 9,108 (Stages 10–11, add. 19) · 1,428 (add. 16 D)', True)
rep(40, 'paper-specific</li></ul></div><span class="pg"></span></div>',
    f'paper-specific</li><li class="new">Readout map (add. 18b item 1, <span class="a">exploratory</span>): faint early traces at year / \':\' / first title token, +0.008 to +0.049; uncorrected → slide {P[75]}</li></ul></div><span class="pg"></span></div>', 'bullet: item 1')
fxn(40, 70, 430, 540, 'Δ = spec<sub>lens</sub> − spec<sub>logit lens</sub>', 'n = 50 / 200 papers (Stages 1–9) · 9,108 (10–11) · 1,395 (probe) · 600 (add. 18b)', True)
rep(50, 'costs nothing</li></ul></div><span class="pg"></span></div>',
    f'costs nothing</li><li class="new">L57–L61 written by the MLPs: MLP − attention loss <span class="b">+0.040</span> [0.036, 0.045] (item 4, <span class="g">confirmed</span>) → slide {P[78]}</li><li class="new">L52–L56 MLPs carry paper information, hardly along author-name directions (item 6, descriptive) → slide {P[77]}</li></ul></div><span class="pg"></span></div>', 'bullets: items 4, 6')
fxn(50, 70, 430, 540, 'R(l) = mean(patched − false) / mean(true − false)', 'n = 20–200 (Stages 1–9) · 9,108 (10) · 1,186 (11) · 600 (add. 18b)', True)
rep(58, 'title matters less</li></ul></div><span class="pg"></span></div>',
    f'title matters less</li><li class="new">Answer format (add. 16): a given first initial (F4) helps recognised papers more, A − B <span class="b">+0.085</span> [0.047, 0.124] (supported via F4 only)</li><li class="new">Co-author chain (add. 16): +0.167, not title-specific, A ≈ B → network association → slide {P[86]}</li></ul></div><span class="pg"></span></div>', 'bullets: add. 16')
fxn(58, 70, 430, 540, 'spec = nlr<sub>true</sub> − mean<sub>5</sub> nlr<sub>false</sub>', 'n = 20 pairs (1–9) · 9,108 (10–11) · 1,186 (P1) · 1,200 / 1,428 (add. 16 B / D)', True)
addb(59, 292, 470, 300, f'<b>Since 11-17 (add. 18b):</b> ④ goes on: L52–L56 MLPs carry paper information, not name directions {st("descriptive")} → slide {P[77]}; L57–L61 are written by MLPs {st("confirmed")} → slide {P[78]}. ③ early traces before the name stay faint {st("exploratory")} → slide {P[75]}.', 'box: items 1, 4, 6', 'font-size:13px;padding:4px 8px')
addb(65, 1137, 250, 136, f'<b>Update 11-17/18</b><br><b style="color:#3C78B4">H2:</b> title meaning matters more than wording (item 5) {st("descriptive")} → slide {P[76]}; still not separable from paper identity.<br><b style="color:#3C78B4">H3:</b> faint early traces (item 1) {st("exploratory")} → slide {P[75]}; L52–L56 MLP content mostly outside the author-name directions (item 6) {st("descriptive")} → slide {P[77]}.<br><b style="color:#3C78B4">Route:</b> L57–L61 written by MLPs (item 4) {st("confirmed")} → slide {P[78]}.<br><span style="color:#8a8f98;font-size:11px">n = 600 papers (add. 18b)</span>',
     'box: hypothesis update', 'font-size:12px;line-height:1.25;padding:5px 6px')
addb(66, 972, 548, 252, f'<b>Refined since 11-17:</b> positions × layers before the name (item 1) {st("exploratory")} → slide {P[75]}; L57–L61 written by MLPs (item 4) {st("confirmed")} → slide {P[78]}', 'box: items 1, 4', 'font-size:14px')
fxn(66, 70, 668, 880, '≤L<sub>x</sub> = earliest measured layer at which the source’s own rule passes', 'n = 9,108 (Stage 10, X5) · 1,186 (patching, knockout) · 552–582 test (Stage 13)')
addb(80, 88, 596, 1124, f'<b>Update and new limits since 11-14:</b> H3 is now supported on the same scale (addendum 17 item 2, locked test), so "insufficient evidence" above is outdated (slide {P[65]}). '
     f'Add. 19: lock made after the data had been seen; recall c50 near the top of the citation range (16 of 9,108 papers above 11,038). Item 1: 672 cells tested, no multiple-comparison correction. '
     f'Item 5: crude WordNet synonyms. Items 4 / 6: one layer and component at a time, 600-paper subsample, parity WARN (bf16 batch shapes). Add. 16: teacher-forced preferences, greedy decoding only. C: post hoc, not pre-registered.',
     'box: new limits', 'font-size:14.5px')
rep(65, '<div class="howr" style="left:70px;top:201px;width:1140px">', '<div class="howr" style="left:8px;top:262px;width:128px">', 'howr moved off the subtitle (text unchanged)')
rep(81, '<li>1. Group comparisons A / B / C / D: three findings, intervention re-runs (E1 and P1 / P2 numerator / denominator), recognition; why recall fails: output format and name chain (addendum 16), fabricated names, exposure threshold (addendum 19)</li>',
    f'<li>1. Group comparisons A / B / C / D: three findings, intervention re-runs (E1 and P1 / P2 numerator / denominator), recognition. Moved into the lines on 2026-11-18: exposure threshold (addendum 19) → slide {P[88]} (Line A); output format and name chain (addendum 16) → slide {P[86]} (Line D); fabricated names → slide {P[87]} (Stage 13)</li>',
    'item 1 text: moved results')

# ---------------------------------------------------------------- 2. new slide: What we learned, continued
WL = f'''<section class="slide lt" aria-label="What we learned, continued"><span class="tag">Stage 12–13 · 2026-11-15/18</span>
<div class="lead">← slide {P[79]}: what we learned up to 11-14. <b>Here:</b> the results of 11-15 to 11-18, each with its status → limits, slide {P[80]}</div>
<h2 style="font-size:54px;margin-top:6px">What we learned, continued: who writes it, what it needs</h2>
<div class="wl">
<div class="k a">Written late by MLPs</div><div class="v">L57–L61: ablating an MLP layer costs more than ablating attention at every layer, <span class="a">+0.040</span> [0.036, 0.045] {st("confirmed")} (locked criterion) → slide {P[78]}. L52–L56 MLPs carry paper information, mostly outside the author-name directions {st("descriptive")} → slide {P[77]}.</div>
<div class="k g">Exposure gap</div><div class="v">Recognising a paper needs ≈ 40 citations, writing an author ≈ 11,000: ρ = <span class="a">276</span> [203, 390] {st("confirmed")} (lock made after the data had been seen; recall threshold near the top of the range) → slide {P[88]}.</div>
<div class="k b">Meaning, not wording</div><div class="v">Random content words erase the title signal (loss <span class="a">0.374</span> of S = 0.328); WordNet synonyms cost only <span class="a">0.087</span> {st("descriptive")} (crude synonyms) → slide {P[76]}.</div>
<div class="k g">Early traces</div><div class="v">Before the name, year / ':' / the first title token hold faint author traces, +0.008 to +0.049; 59 cells meet the locked rule, 60 of 672 tested cells have CI &gt; 0, no multiple-comparison correction {st("exploratory")} → slide {P[75]}.</div>
<div class="k b">Format and chain</div><div class="v">A given first initial (F4) helps recognised papers more, A − B <span class="a">+0.085</span> [0.047, 0.124] {st("supported")} (F4 only). A true co-author helps (+0.167 [0.147, 0.185]) but not title-specifically (+0.012 [−0.001, 0.025]): a co-author network association → slide {P[86]}.</div>
<div class="k a">Made-up names</div><div class="v">Half are people not in the data (50.4%; shuffled baseline 50.5%): plausible names, not confused neighbours {st("exploratory")} (not supported) → slide {P[87]}. The probe beats output confidence only at L40–L52 (C24) {st("exploratory")} (undecided) → slide {P[74]}.</div>
</div>
<div class="fxn" style="left:70px;top:668px;width:1120px"><span class="fx">loss(c) = S(none) − S(c),&nbsp; ρ = c<sub>50</sub><sup>recall</sup> / c<sub>50</sub><sup>recog</sup></span><span class="nn">n = 600 papers (add. 18b) · 9,108 (add. 19) · 1,200 / 1,428 (add. 16 B / D) · 40,219 names in 8,872 papers (C) · 518 (C24)</span></div>
<span class="pg"></span></section>'''
S['WL'] = WL

# ---------------------------------------------------------------- 5. formula + n where missing
F_SPEC = r'spec = nlr<sub>true</sub> − mean<sub>5</sub> nlr<sub>false</sub>'
F_TC = r'T − C = Σ<sub>b</sub> w<sub>b</sub> (spec<sub>T,b</sub> − spec<sub>C,b</sub>)'
F_R = 'R(l) = mean(patched − false) / mean(true − false)'
FX = [
    # old, left, top, width, formula, n, dark
    (3, 70, 418, 560, 'score = log<sub>10</sub>(1/rank),&nbsp; target = A + C, control = B + D', 'n = 50 / 200 papers (Pilot50 / Stage 8) · 9,108 papers (full cohort)', True),
    (4, 70, 668, 1100, 'target = A + C,&nbsp; control = B + D', 'n = 6,841 papers (frozen cohort: 4,621 target + 2,220 control)', False),
    (7, 70, 560, 700, 'pass: 4/4 orders right ∧ mean p(true) ≥ 0.5', 'n = 9,108 papers (labels) · 6,841 (cohort) · 50 (Pilot50)', False),
    (8, 70, 440, 560, 'r = 1 + #{tokens with a larger logit},&nbsp; nlr = log<sub>10</sub>(1/r)', 'n = settings for every sample: 20 papers (Stage 4) → 9,108 papers (Stage 10)', False),
    (9, 70, 690, 450, 'w<sub>b</sub> = n<sub>t,b</sub> n<sub>c,b</sub> / (n<sub>t,b</sub> + n<sub>c,b</sub>),&nbsp; HR2 = (H+U)/(M+H+U)', None, False),
    (9, 770, 692, 440, None, 'n = 9,108 papers · 45,540 false-title pairs (35,898 strict)', False),
    (10, 70, 570, 560, 'title-specific = nlr<sub>true</sub> − mean<sub>5</sub> nlr<sub>false</sub>', 'n = 9,108 papers · lenses fitted on 557 / 100 / 100 WikiText-103 prompts', False),
    (11, 70, 662, 1100, 'Δ<sub>max</sub> = max |z<sub>fast</sub> − z<sub>slow</sub>|', 'n = 12 contexts (parity) · 972 tokens (Stage 6 cross-check) · 9,108 papers (negative control)', False),
    (13, 700, 600, 510, 'T = M(P title) − M(Q title),&nbsp; M = logit(G) − logit(F)', 'n = 50 papers · 20 matched A/B pairs', False),
    (14, 760, 560, 450, 'adv = win(true title) − mean<sub>20</sub> win(wrong title)', 'n = 50 papers · 1,000 contexts (20 wrong titles each) · 20 A/B pairs', False),
    (15, 70, 668, 1100, 'adv = win(true title) − mean<sub>20</sub> win(wrong title)', 'n = 50 papers · 1,000 wrong titles · 6 low-citation papers · 20 A/B pairs', False),
    (17, 760, 600, 450, 'RQ1 = win(true title) − win(wrong title), L56', 'n = 200 papers · 100 A/B pairs (RQ2) · 25 + 25 pairs (RQ3)', False),
    (18, 70, 420, 560, 'A − B after removing the top k = mean of the remaining pair differences', 'n = 100 A/B pairs (200 papers)', False),
    (19, 70, 430, 800, F_SPEC + ', 6-layer mean', 'n = 200 papers · 100 A/B pairs', False),
    (21, 70, 628, 760, None, 'n = 9,108 papers · 7,247 author teams · 2,000 draws', False),
    (22, 70, 668, 1100, 'title-specific = nlr<sub>true</sub> − mean<sub>5</sub> nlr<sub>false</sub>', 'n = 4,621 target + 2,220 control papers (Stage 10; all 9,108 scored)', False),
    (25, 70, 676, 1100, 'probe signal = probe(true title) − probe(false_0)', 'n = 1,863 papers (X1-control pipeline, title reuse removed)', False),
    (26, 70, 668, 1100, F_SPEC + ', per citation bin', 'n = 9,108 papers (bins with < 10 papers omitted)', False),
    (28, 70, 668, 1100, F_TC + ';&nbsp; ' + F_R, 'n = A 3,423 / B 2,151 (R0) · C 391 vs B 885 (R1) · patching 551 + 36 + 588 papers', False),
    (29, 70, 668, 1100, 'written − missed = spec(written author) − spec(missed author), same paper', 'n = 495 R1 papers (paired within paper)', False),
    (32, 760, 600, 450, 'KL(final ‖ readout) per layer', 'n = 20 generic + 20 paper prompts · author pilot 20 papers', False),
    (33, 820, 600, 390, 'Δ = adv(J-Lens) − adv(Vanilla)', 'n = 50 papers · 20 A/B pairs · 20,000 bootstrap draws', False),
    (34, 780, 610, 430, 'J<sub>l</sub> = E<sub>x</sub>[∂h<sub>63</sub> / ∂h<sub>l</sub>]', 'n = 100 + 100 WikiText prompts planned (Fit A 4, Fit B 0 done)', False),
    (36, 70, 668, 1100, 'nlr = log<sub>10</sub>(1/rank of the true name token)', 'n = 9,108 papers (true title)', False),
    (37, 70, 668, 1100, 'nlr = log<sub>10</sub>(1/rank);&nbsp; top-10 share = P(rank ≤ 10)', 'n = 9,108 papers (true title)', False),
    (38, 70, 668, 1100, 'extra = spec<sub>lens</sub> − spec<sub>logit lens</sub>;&nbsp; T − C of the extra', 'n = 9,108 papers (4,621 target + 2,220 control)', False),
    (39, 70, 672, 1100, 'spec = nlr<sub>true</sub> − nlr<sub>false_0</sub>;&nbsp; T − C within bin', 'n = 9,108 papers (lenses) · 1,395 papers (probe: 896 target + 499 control)', False),
    (42, 70, 676, 1100, 'RR = mean over papers of 1/rank (first-listed author, first token)', 'n = 20 papers, 93 authors', False),
    (43, 70, 600, 600, 'win = P(logit gold > logit false);&nbsp; matched A − B', 'n = 50 papers · 100 false names each (75,000 pairs) · 20 A/B pairs', False),
    (48, 70, 645, 1100, 'share = (intervened − false) / (true − false)', 'n = 593 + 593 papers (patch, knockout) · 9,108 (probe, chain)', False),
    (52, 70, 600, 620, 'JMRR = mean<sub>a</sub> mean<sub>t</sub> 1/r (teacher forcing)', 'n = 50 papers · 227 authors · 972 name tokens · 20 A/B pairs', False),
    (53, 740, 600, 470, 'A − B = JMRR<sub>A</sub> − JMRR<sub>B</sub> by token position', 'n = 20 A/B pairs (40 papers) · 10,000 pair-bootstrap draws', False),
    (54, 70, 668, 1100, F_SPEC + ', by name format', 'n = 9,108 papers (T − C: 4,621 + 2,220)', False),
    (55, 70, 668, 1100, 'Δ = nlr(later words | first word in top 10) − nlr(… not in top 10)', 'n = 8,876 authors (Stage 10)', False),
    (56, 300, 145, 900, 'spec by token role;&nbsp; ρ = Spearman(spec, orders right)', 'n = 9,108 papers (left) · 8,894 R0/R1 papers (right)', False),
    (57, 70, 668, 1100, 'chain = spec(after co-authors) − spec(author alone)', 'n = 9,108 papers (4,621 target, 2,220 control)', False),
    (60, 120, 600, 1000, 'share = x<sub>(1)</sub> / Σ<sub>i</sub> x<sub>i</sub>', 'n = 20 papers (Stage 4) · 100 pairs (8D) · 5,000 false names (7.2) · 796 papers (0–2 bin)', False),
    (61, 70, 630, 1100, F_SPEC + ';&nbsp; T − C within bin', 'n = 20–200 papers (Stages 1–9) · 9,108 (Stages 10–11)', False),
    (69, 70, 560, 1100, 'T = probe transfer across questions;&nbsp; ' + F_R, 'n = 9,108 papers (M3, team folds) · 582 test pairs (X1)', False),
    (70, 70, 560, 1100, 'D = decode(own title state) − decode(partner);&nbsp; G′ − G(L4)', 'n = 552 test papers (X3) · 1,178 papers (X4 role split) · test split, team CI', False),
    (71, 70, 520, 1100, 'moved share = (patched − false) / (true − false)', 'n = 582 test pairs · subspace fit on 5,041 training papers', False),
    (79, 70, 688, 450, F_R, None, False),
    (79, 770, 690, 440, None, 'n = 9,108 (readouts) · 1,186 (interventions) · 1,395 (probe)', False),
    (82, 70, 640, 1100, 'contrast = Σ<sub>b</sub> w<sub>b</sub> (spec<sub>A,b</sub> − spec<sub>B,b</sub>), Holm over 4', 'n = 3,417 / 2,148 (P1) · 8,288 (P3) · 390 / 2,826 (P2-other) · 292 / 3,199 (P2-first) · 200 (R2)', False),
    (83, 70, 560, 1100, 'R = mean(patched − false) / mean(true − false)', 'n = A 557 · B 586 · U0 599 · C 462 · R2 200 papers', False),
    (85, 70, 540, 1100, 'ratio B − A = R<sub>B</sub> − R<sub>A</sub>;&nbsp; numerator = mean(patched − false)', 'n = A 557 / B 586 papers (unwritten authors) · 694–711 papers per false title', False),
    (89, 70, 500, 1100, 'retrieval = P(top-1 = same paper);&nbsp; T − C within bin', 'n = 9,108 papers (X5, M3) · 4,621 / 2,220 (M3 T − C) · 1,155 interval rows', False),
    (90, 70, 692, 450, F_R, None, False),
    (90, 770, 694, 440, None, 'n = 4,654 (E4b) · 694–711 / false title (P1/P2) · 462 (C) · 582 test pairs', False),
]
for old, l, t, w, f, n, dk in FX:
    fxn(old, l, t, w, f, n, dk)

# ---------------------------------------------------------------- assemble
body = '\n'.join(S[o] for o in order)
OUT.write_text(head + body + tail, encoding='utf-8')
untouched = [o for o in range(1, 92) if S[o] == ORIG[o]]
assert all(o not in CHANGED for o in untouched)
rec = {'order_new_to_old': {P[o]: o for o in order}, 'P_old_to_new': {str(k): v for k, v in P.items()},
       'changed_old': {str(k): v for k, v in sorted(CHANGED.items())}, 'untouched_old': untouched}
(Path(__file__).parent / 'build_20261118b_deck.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding='utf-8')
print('slides', len(order), '| changed', len(CHANGED), '| untouched', len(untouched))
print('moves:', {o: P[o] for o in (88, 86, 75, 77, 78, 76, 87, 'WL')})
