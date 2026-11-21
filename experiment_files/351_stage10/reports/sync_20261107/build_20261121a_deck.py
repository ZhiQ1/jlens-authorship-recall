"""2026-11-21a: narrative line + editable hypothesis table in the merged HTML deck (v46 -> v47). User decisions 2026-11-21 (coordinator relay).
Source = merged_deck/stage1_11_deck.html.before_20261121a (= published v46, live-compared 2026-11-21) -> merged_deck/stage1_11_deck.html.
  A. 'Now asking: ...' small subtitle under the title of each section's first page; 'So: ...' line + status chip at the bottom of each section's
     last page (no new pages). Stage 12-13 split into 4 sub-blocks (65-70 / 71-76 / 77-81 / 82-89); contents menu shows them.
     Wording from ~/jlens_work/narrative_draft_20261120.md; numbers checked against source (asserts below); a few clauses made more precise
     (H3 test only at L40 and L48; 'steepest rise' as on slide 51; route chips per step; 'mostly filled by L50').
     On the two picture slides 65 and 71 the drawing below the title is moved down 26 px to make room for the line.
  B. Slide 68: the old v30 table image replaced by an HTML table (same rows / columns), current H1-H3 results.
Writes build_20261121a_deck.json."""
import re, json, csv, copy
from pathlib import Path
from lxml import etree

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
SRC = D / 'stage1_11_deck.html.before_20261121a'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 97
SL = [m.group(0) for m in ms]
lab = lambda i: re.search(r'aria-label="([^"]*)"', SL[i - 1]).group(1)

# ---------------------------------------------------------------- source checks for every number used
A20 = (Path('/scratch/zhang.zhiqi2/jlens/391_groups/summary_a20/a20_report.md')).read_text()
assert '**+0.751 [+0.723, +0.778]**' in A20 and '**+0.106 [+0.094, +0.118]**' in A20
H3 = {(r['layer'], r['lens']): r for r in csv.DictReader(open('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_h3_samescale_20261114/h3_samescale_paired.csv'))}
r40, r48 = H3[('40', 'jlens_public_b16')], H3[('48', 'jlens_public_b16')]
f3 = lambda x: round(float(x), 3)
assert (f3(r40['tc_diff']), f3(r40['tc_diff_lo']), f3(r40['tc_diff_hi'])) == (0.021, 0.008, 0.034)
assert (f3(r48['tc_diff']), f3(r48['tc_diff_lo']), f3(r48['tc_diff_hi'])) == (0.062, 0.041, 0.081) and r48['n_tc'] == '4654'
TH = list(csv.DictReader(open('/scratch/zhang.zhiqi2/jlens/391_groups/summary_exposure_prereg19/thresholds_ratio.csv')))
assert any('276' in json.dumps(r) for r in TH)
CV = open('/home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md', encoding='utf-8').read()
assert 'L45 0.529 [0.512, 0.547]' in CV and 'L48 0.821 [0.806, 0.835]' in CV  # half by L45 (C02)
# deck-internal anchors the So lines quote (already sourced on those slides)
assert '+0.21</span> [0.20, 0.22]' in SL[32]                       # slide 33, L63 target - control
assert 'steepest rise L57–L61' in SL[50]                           # slide 51
assert 'L45 0.529' in SL[75] or 'L48 0.821' in SL[75]              # slide 76 plotted numbers (E1 mean of 5)
assert 'L50 0.929' in SL[75] and 'L52 0.995' in SL[75]
assert 'φ' in SL[79] or 'phi' in SL[79].lower()

# ---------------------------------------------------------------- texts
ST = {'method': ('c4', 'method'), 'confirmed': ('c1', 'confirmed'), 'fairly solid': ('c2', 'fairly solid'), 'settled': ('c1', 'settled'),
      'summary': ('c4', 'summary'), 'descriptive': ('c4', 'descriptive'), 'exploratory': ('c3', 'exploratory'), 'limits': ('c4', 'limits'),
      'locked': ('c1', 'locked')}
chip = lambda k: '<span class="st %s">%s</span>' % ST[k]
COL = {'ov': '#22304A', 'A': '#D9772B', 'B': '#3C78B4', 'C': '#3E8E4E', 'D': '#C84A3E', 'syn': '#7A5BB8', 's12': '#3C78B4', 'grp': '#3C78B4', 'chk': '#3C78B4'}
ASK = {  # slide: (colour, text, mode)
    1: ('ov', 'can we measure, per paper, whether Qwen3-32B holds its authors, and trust the numbers?', 'title'),
    12: ('A', 'is the author signal about <i>this</i> paper, or just easy names?', 'h1'),
    34: ('B', 'which readout can see the author signal, and how early?', 'h1'),
    44: ('C', 'when does the paper information arrive, and when is it used?', 'h1'),
    52: ('D', 'which part of the name, and which cue in the prompt, carries it?', 'h1'),
    62: ('syn', 'what do the four lines add up to?', 'h2'),
    65: ('s12', 'if the middle layers do not hold the name, what do they hold?', 'svg'),
    71: ('s12', 'where does the information travel, and who writes the name?', 'svg'),
    77: ('s12', 'is it the title’s meaning, or the identity of this paper?', 'h2'),
    82: ('s12', 'are author names hidden in the middle layers, and are made-up names near-misses?', 'h2'),
    90: ('grp', 'does recognising a paper change how strong the signal is, or when it arrives?', 'h2'),
    95: ('chk', 'what could still be wrong?', 'h2'),
}
SO = {  # slide: (html, (left, top, width))
    11: ('one prompt, one score (rank of the true name among all tokens) and true vs 5 false titles give a per-paper measure, compared within citation bins with team-cluster CIs. ' + chip('method'), (70, 608, 1140)),
    33: ('the signal is paper-specific: the true title beats false titles for every group, recognised papers lead only at the output (+0.21), and writing needs about 276× the exposure that recognising does. ' + chip('confirmed'), (70, 648, 1140)),
    43: ('lenses read names only late; a probe at the title reads a little paper-specific signal early, and at the name positions a probe beats the J-lens on the same scale at L40 and L48. ' + chip('fairly solid'), (70, 648, 1140)),
    51: ('it arrives early (mainly L40–L50, half by L45) and is said late (steepest rise L57–L61, written by the MLPs). ' + chip('settled'), (70, 648, 1140)),
    61: ('the surname and full given names carry it, initials little; a given first initial helps; a true co-author helps through the co-author network, not this paper. ' + chip('confirmed'), (70, 648, 1140)),
    64: ('read early, said late: the shelf is mostly filled by L50, and the name comes out only at the end. ' + chip('summary'), (70, 566, 1140)),
    70: ('the middle layers hold the question and the paper’s facts, but nothing beyond what the title text gives at L4 ' + chip('descriptive') + '; before L48 only faint, scattered author traces ' + chip('exploratory'), (70, 556, 770)),
    76: ('title → name positions through the name ← title attention edge (L44–L55, small) ' + chip('fairly solid') + ' → the L52–L56 MLPs carry the paper ' + chip('descriptive') + ' → the L57–L61 MLPs write the name ' + chip('settled'), (70, 598, 1140)),
    81: ('a same-meaning made-up title recovers 75% of the gap; the real title adds +0.11, so H2 is partly supported and meaning explains most of the signal. ' + chip('confirmed'), (70, 620, 1140)),
    89: ('on the same scale a probe reads more of the author than the J-lens at L40 and L48 (H3 supported) ' + chip('fairly solid') + '; made-up names are not confused neighbours ' + chip('exploratory'), (70, 664, 1140)),
    94: ('recognition changes the size, hardly the timing; the higher recovery in B is a small-denominator effect. ' + chip('confirmed'), (70, 478, 1140)),
    97: ('one model, subsamples for interventions and a few post-hoc locks; none of the checks reverses a conclusion. ' + chip('limits'), (70, 530, 1140)),
}
REC = {'ask': {}, 'so': {}, 'changed': []}

def ask_html(k, cls='askl'):
    c, t, m = ASK[k]
    return f'<p class="{cls}" style="color:{COL[c]}"><b>Now asking:</b> {t}</p>'

SHIFT = 30
def shift_svg(sec, title_y):
    """move every top-level svg child below the title (except background rects, defs, desc, the section tag and footer text at y >= 680) down by SHIFT px"""
    i = sec.index('<svg'); j = sec.index('</svg>') + 6
    root = etree.fromstring(sec[i:j].encode('utf-8'))
    ns = '{http://www.w3.org/2000/svg}'
    kids = list(root); tpos = None
    for n, ch in enumerate(kids):
        if ch.tag == ns + 'text' and float(ch.get('y', 0)) == title_y: tpos = n; break
    assert tpos is not None
    g = etree.SubElement(root, ns + 'g'); g.set('transform', f'translate(0,{SHIFT})'); g.set('data-name', 'below title (moved for the ask line)')
    moved = 0
    for ch in kids[tpos + 1:]:
        if ch.get('data-name') == 'section tag': continue
        if ch.tag == ns + 'text' and float(ch.get('y', 0)) >= 680: continue
        root.remove(ch); g.append(ch); moved += 1
    # keep paint order: put g right after the title
    root.remove(g); root.insert(tpos + 1, g)
    out = etree.tostring(root, encoding='unicode')
    return sec[:i] + out + sec[j:], moved

for k in ASK:
    sec = SL[k - 1]; c, t, m = ASK[k]
    if m == 'title':
        add = ask_html(k, 'askl abs').replace('style="', 'style="left:260px;top:128px;width:760px;text-align:center;')
        sec = sec[:-len('</section>')] + add + '</section>'
    elif m == 'h1':
        assert sec.count('</h1>') == 1; sec = sec.replace('</h1>', '</h1>' + ask_html(k), 1)
    elif m == 'h2':
        sec = sec.replace('</h2>', '</h2>' + ask_html(k), 1)
        if k == 62:   # dense picture page: keep the content where it was (ask line takes the old gap above the grey subtitle)
            assert sec.count('<p class="sub">') == 1
            sec = sec.replace('<p class="askl" ', '<p class="askl" data-tight="1" ', 1).replace('<p class="sub">', '<p class="sub" style="margin-bottom:4px">', 1)
    elif m == 'svg':
        ty = {65: 100.0, 71: 84.0}[k]
        sec, nm = shift_svg(sec, ty)
        top = {65: 114, 71: 98}[k]
        add = ask_html(k, 'askl abs').replace('style="', f'style="left:72px;top:{top}px;width:1000px;')
        sec = sec[:-len('</section>')] + add + '</section>'
        REC.setdefault('svg_moved', {})[k] = nm
    SL[k - 1] = sec; REC['ask'][k] = re.sub('<[^>]+>', '', t)

for k, (h, (x, y, w)) in SO.items():
    sec = SL[k - 1]
    add = f'<div class="soln" style="left:{x}px;top:{y}px;width:{w}px"><b>So:</b> {h}</div>'
    SL[k - 1] = sec[:-len('</section>')] + add + '</section>'; REC['so'][k] = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', re.sub(r'<span class="st [^"]+">([^<]+)</span>', r'[\1]', h))).strip()

# ---------------------------------------------------------------- B. slide 68 table
assert lab(68) == 'Stage 12-13 hypotheses'
sec = SL[67]
XS = open('/scratch/zhang.zhiqi2/jlens/381_stage13/reports/x1_similarity.md', encoding='utf-8').read()
assert '| L4 | 0.8974 (0.8922) | 0.9958 | 0.443 | 0.094 | 4.737 |' in XS and '| 3.046 |' in XS and '| 2.185 |' in XS   # ":" question / paper ratio (C23)
CORE = lambda t: f'<span class="core">{t}</span>'
H1C = ('<b>Supported at “:” and the name positions</b> ' + chip('fairly solid') +
       CORE('“:” moves 4.7× (L4), 3.0× (L40), 2.2× (L48) more for a new question than for a new paper') +
       'the state at “:” is organised by the question; the ratio falls to 1.3–1.5× at L56–L63 → slide 77')
H2C = ('<b>Partly supported — meaning explains most</b> ' + chip('confirmed') +
       CORE('φ = 0.75 [0.723, 0.778], R̄ = +0.106 [0.094, 0.118] (add. 20, locked)') +
       'a same-meaning made-up title recovers three quarters of the true − false gap; only the real title gives the rest → slide 80'
       '<span class="was">Earlier, unchanged: M3 and X5 not above the L4 text level; X3 cannot separate meaning from paper identity; X4 decodes the first author (L8) before the year (L40), opposite to H2; X2 does not support H2 → slides 77, 82</span>')
H3C = ('<b>Supported on the same scale</b> (add. 17) ' + chip('fairly solid') +
       CORE('probe − lens L40 +0.021 [0.008, 0.034], L48 +0.062 [0.041, 0.081]') +
       'J-lens, target − control on the same 9,137 name tokens (surname first token, 4,654 papers, locked) → slide 84'
       '<span class="was">Earlier: addendum 11 alone gave ‘partly supported’ because the two scales differed; X4 alone and X2 alone insufficient (text baseline not weaker than Qwen; author subspace R² ≤ 0.009) → slides 82–83</span>')
ROWS = [
    ('<b>H1 task / format:</b> the middle layers represent “output an author list”', 'mostly “author”, punctuation, common name starts; unrelated to the title',
     'paper attributes not readable or very weak', 'the same title under different questions separates early in the middle layers', H1C),
    ('<b>H2 paper identity:</b> the middle layers represent “which paper this is”', 'title-related words (copied from the title); change with a false title',
     'field, year (inferred from the title), citations and recognition all readable, and earlier than the names',
     'the same paper under different questions is close in the middle layers and separates by task only late<br><b>Result:</b> not above the L4 text level, not supported', H2C),
    ('<b>H3 author information already there, just not in vocabulary directions</b>', 'not necessarily', 'the authors’ first token readable by the probe, not by the lens',
     'an author-trained probe transfers across tasks; an author-specific lens (M4) reads names in the middle layers', H3C),
]
th = ['Hypothesis', 'M1: top word of the lens in middle layers', 'M2: probe reads non-name attributes', 'M3: change-of-task control', 'Current result (2026-11-21)']
tb = '<table class="hx"><colgroup><col style="width:150px"><col style="width:118px"><col style="width:136px"><col style="width:156px"><col></colgroup><thead><tr>' + ''.join(f'<th>{x}</th>' for x in th) + '</tr></thead><tbody>'
TINT = {(0, 4): 'sup', (1, 4): 'part', (2, 4): 'sup', (1, 3): 'weak'}
tb += ''.join('<tr>' + ''.join(f'<td class="{TINT.get((ri, ci), "")}">{c}</td>' if (ri, ci) in TINT else f'<td>{c}</td>' for ci, c in enumerate(r)) + '</tr>' for ri, r in enumerate(ROWS)) + '</tbody></table>'
tb += ('<p class="hxleg"><span class="sup">supports</span><span class="part">partly supports</span><span class="weak">weakens</span>'
       '<span class="neu">cannot separate / neutral</span> cell colour = what the result does to the hypothesis; small bold line = core number</p>')
new_sub = '<p class="sub" style="margin-bottom:10px;font-size:19px">Hypotheses H1–H3 × readouts M1–M3, with the current result of each · paper facts are readable at the title early (M2)</p>'
i0 = sec.index('<p class="sub"'); i1 = sec.index('</figure></div>', i0) + len('</figure></div>')
old_block = sec[i0:i1]; assert '<img alt="Hypotheses H1–H3 against readouts M1–M3' in old_block
fig = f'<div style="width:990px;margin:0 auto"><figure class="card hxcard" aria-label="Hypotheses H1–H3 × readouts M1–M3 and current results">{tb}</figure></div>'
sec = sec[:i0] + new_sub + fig + sec[i1:]
oh = re.search(r'<div class="howr".*?</div>', sec, re.S).group(0)
nh = ('<div class="howr" style="left:8px;top:262px;width:128px"><b>How computed: </b>H2: φ<sub>T</sub> = made-up-title share of the true − false gap, '
      'R̄<sub>T</sub> = mean(S<sub>true</sub> − S<sub>made-up</sub>) (566 target papers, final layer); H3: probe − J-lens, target − control within bin, same 9,137 name tokens '
      '(4,654 papers, team cluster); H1 question share · source: a20_report.md, h3_samescale_paired.csv, x1_similarity.md</div>')
assert 'H3 name-position probe spec' in oh
sec = sec.replace(oh, nh)
SL[67] = sec; REC['p68'] = {'rows': 3, 'removed_image_bytes': len(old_block)}

# ---------------------------------------------------------------- CSS + menu
CSS = '''<style>
/* narrative line + hypothesis table (2026-11-21a) */
.askl{font-family:var(--hand);font-size:19px;line-height:1.2;margin:2px 0 8px;opacity:.95}
.askl.abs{position:absolute;z-index:4;margin:0;font-size:18px}
.slide>.askl.abs[style*="text-align:center"]{background:var(--pp);border-radius:12px;padding:2px 10px}
.askl b{font-weight:700}
.askl[data-tight]{margin:-2px 0 0}
.soln{position:absolute;z-index:4;font-family:var(--hand);font-size:15.5px;line-height:1.25;color:#22304A;background:#FFF6DC;border-left:4px solid #D9772B;border-radius:4px;padding:3px 10px;box-shadow:1px 2px 5px rgba(0,0,0,.12)}
.soln b{color:#B54708}
.soln .st,.hx .st{font-family:"Noto Sans SC",system-ui,sans-serif;font-size:11px;padding:0 5px;border-radius:5px;border:1px solid currentColor;white-space:nowrap;vertical-align:1px}
.soln .c1,.hx .c1{color:#2E7D46}.soln .c2,.hx .c2{color:#3C78B4}.soln .c3,.hx .c3{color:#B54708}.soln .c4,.hx .c4{color:#6A7385}
.hxcard{padding:6px 10px 8px}.hxcard::before{display:none}
table.hx{border-collapse:collapse;width:100%;table-layout:fixed;font-family:"Source Sans 3","Noto Sans SC",system-ui,sans-serif;font-size:12.5px;line-height:1.32;color:#1a1a1a}
.hx th{font-weight:700;text-align:left;vertical-align:bottom;padding:4px 7px 5px 0;border-bottom:2px solid #22304A}
.hx td{text-align:left;vertical-align:top;padding:6px 7px 6px 0;border-bottom:1px solid #D5DAE2}
.hx td:last-child{padding-left:7px}
.hx td.sup,.hxleg .sup{background:#e7f1fb}.hx td.weak,.hxleg .weak{background:#fbebeb}.hx td.part,.hxleg .part{background:#f9eeda}.hx td.neu,.hxleg .neu{background:#f0efec}
.hx td.weak{padding-left:6px}
.hx .core{display:block;margin:2px 0 3px;font-weight:700;font-size:12px;color:#22304A}
.hxleg{margin:5px 0 0;font-family:\"Source Sans 3\",\"Noto Sans SC\",system-ui,sans-serif;font-size:11px;color:#5B6372}.hxleg span{display:inline-block;padding:0 6px;margin-right:6px;border-radius:3px;color:#22304A}
.hx .was{display:block;margin-top:4px;color:#5B6372;font-size:11.5px}
</style>'''
head_end = s.index('</head>')
body = s[:ms[0].start()]; tail = s[ms[-1].end():]
assert body.count('</head>') == 1
body = body.replace('</head>', CSS + '</head>', 1)
nav0 = tail.index('<nav class="toc-list"'); nav1 = tail.index('</nav>', nav0)
nav = tail[nav0:nav1]
g6 = re.search(r'<section class="toc-g" aria-labelledby="toc-h6">.*?</section>', nav, re.S).group(0)
assert '>Stage 12–13<span class="toc-r">65–89</span>' in g6
items = re.findall(r'<li>.*?</li>', g6, re.S); assert len(items) == 25
SUB = [('What the middle layers hold', 65, 70), ('The route', 71, 76), ('Meaning or this paper?', 77, 81), ('Names in the middle layers', 82, 89)]
newg = ''
for n, (t, a, b) in enumerate(SUB):
    hid = f'toc-h6{"abcd"[n]}'
    newg += (f'<section class="toc-g" aria-labelledby="{hid}"><h3 class="toc-h" id="{hid}">Stage 12–13 · {t}<span class="toc-r">{a}–{b}</span></h3><ul>'
             + ''.join(items[a - 65:b - 64]) + '</ul></section>')
nav2 = nav.replace(g6, newg)
assert nav2.count('class="toc-i"') == 97
tail = tail[:nav0] + nav2 + tail[nav1:]
out = body + ''.join(SL[i] + (s[ms[i].end():ms[i + 1].start()] if i + 1 < len(ms) else '') for i in range(97)) + tail
OUT.write_text(out, encoding='utf-8')
REC['changed'] = sorted(set(ASK) | set(SO) | {68})
json.dump(REC, open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/sync_20261107/build_20261121a_deck.json', 'w'), indent=1, ensure_ascii=False)
print('wrote', OUT, len(out), 'changed slides', REC['changed'], 'svg moved', REC.get('svg_moved'))
