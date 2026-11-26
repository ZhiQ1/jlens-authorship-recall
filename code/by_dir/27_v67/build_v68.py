"""v68 from published v67 (deck_v67_full.html), add-only (user 2026-11-23):
Part 3 split into 3a/3b (+2 small question cards, Part 3 card lists both), small-sample blocks behind a divider page in Parts 4/5/6,
reference fixes, page-47 Now asking, internal codes -> plain names (+ Glossary continuation page), matrices "at L8" -> "from L8".
Writes deck_v68.html, renumber_map_v68.json, toc_v68.md, refs_v68.tsv."""
import re, json, html
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
t = open(W + 'deck_v67_full.html', encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
assert len(ms) == 154
SEC = {i + 1: m.group(0) for i, m in enumerate(ms)}
head, tail = t[:ms[0].start()], t[ms[-1].end():]
j = t.find('<nav class="toc-list"'); k = t.find('</nav>', j)
OLDT = {int(a): html.unescape(re.sub(r'<[^>]+>', '', b)) for a, b in re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', t[j:k])}
OLDG = {}
for g in re.findall(r'<section class="toc-g".*?</section>', t[j:k], flags=re.S):
    name = html.unescape(re.sub(r'<span class="toc-r">.*', '', re.search(r'<h3[^>]*>(.*?)</h3>', g).group(1)))
    for n in re.findall(r'<span class="toc-n">(\d+)</span>', g): OLDG[int(n)] = name

# ------------------------------------------------------------------ order
R = lambda a, b: list(range(a, b + 1))
order = [('old', n) for n in R(1, 38)] + [('new', 'p3a')] + [('old', n) for n in R(39, 46)] + [('new', 'p3b')] \
    + [('old', n) for n in R(47, 53)] + [('new', 'div4')] + [('old', n) for n in R(54, 81)] + [('new', 'div5')] \
    + [('old', n) for n in R(86, 93)] + [('old', n) for n in R(82, 85)] + [('old', n) for n in R(94, 105)] + [('new', 'div6')] \
    + [('old', n) for n in R(108, 118)] + [('old', 106), ('old', 107)] + [('old', n) for n in R(119, 143)] + [('new', 'gloss2')] \
    + [('old', n) for n in R(144, 154)]
olds = [o[1] for o in order if o[0] == 'old']
assert sorted(olds) == R(1, 154), sorted(set(R(1, 154)) - set(olds))
REN = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'old'}
NEWP = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'new'}
N = len(order)

# ------------------------------------------------------------------ text-node helpers
def on_text(sec, fn, skip_hidden=True):
    hid = []
    def keep(m): hid.append(m.group(0)); return f'\x00{len(hid)-1}\x00'
    s = re.sub(r'<span[^>]*\shidden[^>]*>.*?</span>', keep, sec, flags=re.S) if skip_hidden else sec
    s = re.sub(r'<svg class="tx".*?</svg>', keep, s, flags=re.S)
    parts = re.split(r'(<[^>]+>)', s)
    s = ''.join(p if p.startswith('<') else fn(p) for p in parts)
    return re.sub(r'\x00(\d+)\x00', lambda m: hid[int(m.group(1))], s)

# internal codes -> plain names (visible text and svg text; hidden source notes keep the codes for the script)
LONG = {'A': '“Is it about this paper?”', 'B': '“What can each readout see?”', 'C': '“When does it appear and when is it used?”', 'D': '“Which token carries it?”'}
SHORT = {'A': 'about this paper', 'B': 'readouts', 'C': 'timing', 'D': 'which token'}
CODE_RULES = [
    (r'^\s*Line ([A-D])\s*$', lambda m: m.group(0).replace(f'Line {m.group(1)}', 'Opening question')),
    (r'Overview · Line ([A-D])', lambda m: f'Overview · {SHORT[m.group(1)]}'),
    (r'(Stage [\d.]+(?:–8E)?D? · )Line ([A-D])', lambda m: m.group(1) + SHORT[m.group(2)]),
    (r'Lines A, B', lambda m: 'about this paper, readouts'),
    (r'\bLine ([A-D])\b', lambda m: LONG[m.group(1)]),
    (r'\bStage 8D–8E\b', lambda m: 'Stage 8 replication and follow-up audit'),
    (r'\b8E external audit', lambda m: 'Stage 8 follow-up audit'),
    (r'\bStage 8D\b', lambda m: 'Stage 8 replication'),
    (r'\b8D\b', lambda m: 'Stage 8 replication'),
    (r'\b8E\b', lambda m: 'Stage 8 follow-up audit'),
    (r'\bRQ1\b', lambda m: 'title test'), (r'\bRQ2\b', lambda m: 'A−B test'), (r'\bRQ3\b', lambda m: 'low−high test'),
    (r'\bJMRR\b', lambda m: 'mean reciprocal rank of the name tokens'),
    (r' \(M4\)', lambda m: ''),
    (r'\bM1 prediction', lambda m: 'lens'), (r'\bM2 prediction', lambda m: 'probe'), (r'\bM3 prediction', lambda m: 'change-the-question test'),
    (r'\bM1 \(measured\)', lambda m: 'lens word (measured)'), (r'\bM2 probes', lambda m: 'probes'), (r'\bM3 / question swap', lambda m: 'question swap'),
    (r'readouts M1–M3', lambda m: 'three checks'),
    (r'\bM1–M3\b', lambda m: 'the three checks'),
    (r'Prediction M([1-3]):', lambda m: 'Prediction:'),
    (r'\bM1\b', lambda m: 'top lens word'), (r'\bM2\b', lambda m: 'attribute probe'), (r'\bM3\b', lambda m: 'change-the-question test'),
    (r'change-of-task control', lambda m: 'change-the-question test'),
    (r'change-of-task probe \(change-the-question test\)', lambda m: 'change-the-question test'),
]
ncode = 0
def plain(txt):
    global ncode
    for pat, f in CODE_RULES:
        txt, n = re.subn(pat, f, txt, flags=re.M); ncode += n
    return txt

# ------------------------------------------------------------------ targeted content edits on v67 pages
FIX = []
def sub1(n, a, b):
    global SEC
    assert SEC[n].count(a) >= 1, (n, a[:60]); SEC[n] = SEC[n].replace(a, b, 1); FIX.append((n, a, b))
# 3. probe-vs-lens references -> name-position probe page (v67 95); B22 -> colon-ratio page (v67 49)
sub1(103, '; slide 36). The title', '; slide 95). The title')
sub1(139, 'locked name-position probe test (slide 35)', 'locked name-position probe test (slide 95)')
sub1(144, 'Backup B22 · for slide 35', 'Backup B22 · for slide 49')
# 3b. full reference audit: content corrections (v67 numbers; renumbered below)
sub1(35, 'and the evidence matrix → slide 35b', 'and the evidence matrix → slide 37')
sub1(35, 'surname test → slides 67, 68', 'surname test → slides 67, 68, 78')
sub1(37, 'more for a new question than for a new paper <span class="tg solid">fairly solid</span> → slide 47', 'more for a new question than for a new paper <span class="tg solid">fairly solid</span> → slide 49')
sub1(129, '→ slides 95, 36', '→ slide 95')
sub1(37, 'an author-trained probe transfers across tasks; an author-specific lens (M4) reads names in the middle layers', 'an author-trained probe transfers across tasks; an author lens reads mid-layer names')
sub1(37, 'Mixed (M1 measured)', 'Mixed (lens word measured)')
sub1(37, 'M3 not above the L4 text level', 'question swap ≤ L4 text level')
# 4. page 47 Now asking
sub1(47, 'Now asking:</b> is it the title’s meaning, or the identity of this paper?', 'Now asking:</b> Does the question change what the model stores at the title?')
# 6. matrices: H2 row "at L8" -> "from L8"
for n in (80, 104, 122):
    SEC[n] = SEC[n].replace('small surname signal at L8 beyond topic', 'small surname signal from L8 beyond topic')
    assert 'signal from L8 beyond topic' in SEC[n], n
# 1. Part 3 card lists both questions
sub1(38, 'Question card · H1: is the answer format set in the middle layers?</h2>',
     'Question card · Part 3: title (3a) and format (H1, 3b)</h2>')
sub1(38, '<div class="cats" style="left:70px;top:470px;width:1140px;font-size:14.5px">',
     '<div class="cats" style="left:70px;top:446px;width:1140px;font-size:14.5px"><div class="it"><span class="k">Two questions:</span> '
     '<span class="mk">3a when is the title read?</span> → slides {{3a}} · <span class="mk">3b H1: when is the answer format fixed?</span> → slides {{3b}}</div>')

# ------------------------------------------------------------------ renumber references (v67 -> v68) + codes
REF = re.compile(r'\b(slides?|Slides?)(\s+)(\d{1,3}(?:\s*(?:–|-|,|and|&amp;|&)\s*\d{1,3})*)')
def expand(spec):
    nums = []
    for p in re.split(r'\s*(?:,|and|&amp;|&)\s*', spec):
        if re.search(r'[–-]', p):
            a, b = [int(x) for x in re.split(r'\s*[–-]\s*', p)]
            nums.extend(range(a, b + 1) if b - a < 15 else [a, b])
        elif p.strip(): nums.append(int(p))
    return nums
def fmt(nums):
    nums = sorted(set(nums)); out = []; a = prev = nums[0]
    for x in nums[1:] + [None]:
        if x is not None and x == prev + 1: prev = x; continue
        out.append(str(a) if a == prev else (f'{a}–{prev}' if prev > a + 1 else f'{a}, {prev}'))
        if x is not None: a = prev = x
    return ', '.join(out)
nref = 0
def renum_text(txt):
    global nref
    def rep(m):
        global nref
        nums = expand(m.group(3))
        if any(x < 1 or x > 154 for x in nums): return m.group(0)
        new = [REN[x] for x in nums]; nref += 1
        w = m.group(1)
        if len(set(new)) > 1 and not w.endswith('s'): w += 's'
        return w + m.group(2) + fmt(new)
    return REF.sub(rep, txt)

S3a = f'{REN[39]}–{REN[46]}'; S3b = f'{REN[47]}–{REN[52]}'
for n in SEC:
    s = on_text(SEC[n], renum_text, skip_hidden=False)
    s = on_text(s, plain)
    SEC[n] = s.replace('{{3a}}', S3a).replace('{{3b}}', S3b)

# ------------------------------------------------------------------ new pages
FONT = "font-family:var(--hand)"
def card(slot, part, title, ask, blocks, svg, so, tagc, tagl):
    return (f'<section class="slide lt" aria-label="{html.escape(title)}" data-slot="{slot}"><span class="tag">{part}</span>\n'
            f'<h2 style="font-size:40px;margin-top:6px;max-width:1080px">{title}</h2>\n'
            f'<p class="askl"><b>Now asking:</b> {ask}</p>\n'
            f'<div class="cats" style="left:70px;top:190px;width:540px;font-size:15px;line-height:1.35">{blocks}</div>\n{svg}\n'
            f'<div class="soln" style="left:70px;top:660px;width:1140px"><b>So (section):</b> {so} <span class="tg {tagc}">{tagl}</span></div>\n'
            f'<span class="pg"></span></section>')
def timeline(marks, x0=660, y0=230, w=560):
    L = lambda l: x0 + 20 + l / 63 * (w - 40)
    s = [f'<svg viewBox="0 0 1280 720" width="1280" height="720" style="position:absolute;left:0;top:0;pointer-events:none" aria-hidden="true">'
         f'<g font-family="\'Patrick Hand\',Caveat,cursive" font-size="14" fill="#22304A">'
         f'<rect x="{x0}" y="{y0}" width="{w}" height="300" rx="10" fill="#FFF6DC" stroke="#D9772B" stroke-dasharray="5 4"/>'
         f'<line x1="{L(0)}" y1="{y0+200}" x2="{L(63)}" y2="{y0+200}" stroke="#22304A" stroke-width="2"/>']
    for l in (0, 16, 32, 48, 63):
        s.append(f'<line x1="{L(l):.0f}" y1="{y0+195}" x2="{L(l):.0f}" y2="{y0+205}" stroke="#22304A"/><text x="{L(l):.0f}" y="{y0+224}" text-anchor="middle" fill="#6A7385">L{l}</text>')
    for k, (a, b, col, lab, row) in enumerate(marks):
        yy = y0 + 40 + row * 50
        s.append(f'<rect x="{L(a):.0f}" y="{yy}" width="{max(6, L(b)-L(a)):.0f}" height="26" rx="6" fill="{col}" opacity=".85"/>'
                 + (f'<text x="{L(b):.0f}" y="{yy-6}" text-anchor="end" fill="{col}" font-size="15">{lab}</text>' if a > 50 else f'<text x="{L(a):.0f}" y="{yy-6}" fill="{col}" font-size="15">{lab}</text>'))
    s.append(f'<text x="{x0+20}" y="{y0+270}" fill="#6A7385" font-size="13">layers of Qwen3-32B (schematic; numbers as on the cited slides)</text></g></svg>')
    return ''.join(s)
def blk(k, v): return f'<div class="it"><span class="k">{k}</span> {v}</div>'
P = REN
newhtml = {}
newhtml['p3a'] = card('p3a', 'Part 3a', 'Part 3a · When is the title read?',
    'at which layers is the title read, and from when is it no longer needed?',
    blk('Question:', 'when does the paper information arrive at the positions after the title?')
    + blk('What we did:', f'read with lenses (slides {P[40]}, {P[41]}), then intervene: put back and take away (slides {P[42]}–{P[45]})')
    + blk('If read early, we expect:', 'put back restores most of the true-title advantage before the late layers; taking the title away late costs nothing')
    + blk('What follows:', f'the timing pages, slides {P[39]}–{P[46]}; then 3b asks about the question format (slide {NEWP["p3b"]})'),
    timeline([(24, 50, '#3C78B4', 'title read (L24–L50)', 0), (45, 52, '#2E7D46', 'half by L45 → full by L52', 1), (57, 61, '#C84A3E', 'name written (L57–L61)', 2)]),
    'first the title: when is it read and delivered?', 'settled', 'settled')
newhtml['p3b'] = card('p3b', 'Part 3b', 'Part 3b · H1: when is the answer format fixed?',
    'does the question settle the answer format in the middle layers?',
    blk('Question:', 'H1 says the middle layers mainly encode the task (“output an author list”)')
    + blk('What we did:', f'compare the same title under different questions (slide {P[47]}), the layer order (slide {P[48]}), the “:” distance ratio (slide {P[49]}), knockout and swap at “:” (slide {P[50]})')
    + blk('If H1 holds, we expect:', 'the format is fixed at a middle layer and cannot be changed after it')
    + blk('Caveat:', '<span class="ul">only the authors question gives a usable format measure</span>'),
    timeline([(4, 48, '#3C78B4', '“:” tracks the question (L4–L48)', 0), (40, 56, '#B54708', 'format layer not pinned down (L40–L56)', 1), (56, 56, '#2E7D46', 'swap at L56 lowers the author signal', 2)]),
    f'then the question format; the verdict card (slide {P[51]}) scores H1.', 'lsup', 'locked · H1 revised')

def divider(slot, part, first, last, decisive, summary, chain):
    rows = ''.join(f'<li><span style="display:inline-block;width:2.2em;color:#AAB4C5">{P[n]}</span>{html.escape(plain(OLDT[n]))}</li>' for n in range(first, last + 1) if n in OLDT)
    svg = ('<svg viewBox="0 0 1280 720" width="1280" height="720" style="position:absolute;left:0;top:0;pointer-events:none" aria-hidden="true">'
           '<g font-family="\'Patrick Hand\',Caveat,cursive" font-size="16" fill="#EEF1F5">'
           + ''.join(f'<circle cx="{720 + i*120}" cy="560" r="{14 + i*7}" fill="#3C78B4" opacity="{.25 + i*.18:.2f}"/><text x="{720 + i*120}" y="{608 + i*4}" text-anchor="middle">{lab}</text>'
                     for i, lab in enumerate(['20', '50', '200', '9,108 papers']))
           + '<path d="M700 520 H1110" stroke="#EEF1F5" stroke-width="2" marker-end="url(#dvA)"/>'
           f'<text x="700" y="508">{chain}</text>'
           '<defs><marker id="dvA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#EEF1F5"/></marker></defs></g></svg>')
    return (f'<section class="slide dk" aria-label="Background: how we got here (small samples) · {part}" data-slot="{slot}"><span class="tag">{part} · background</span>\n'
            f'<h2 style="font-size:46px;margin-top:6px">Background: how we got here (small samples)</h2>\n'
            f'<p class="askl"><b>Now asking:</b> what did the earlier, smaller samples suggest before the decisive tests?</p>\n'
            f'<div class="cats" style="left:70px;top:190px;width:560px;font-size:14.5px;line-height:1.3;color:#EEF1F5"><div class="it"><span class="k" style="color:#F6A65A">In this block:</span> slides {P[first]}–{P[last]}</div>'
            f'<ul style="margin:4px 0 0;padding-left:0;list-style:none;font-size:14.5px;line-height:1.32">{rows}</ul></div>\n'
            f'<div class="cats" style="left:700px;top:190px;width:510px;font-size:15px;line-height:1.35;color:#EEF1F5">'
            f'<div class="it"><span class="k" style="color:#F6A65A">What they suggested:</span> {summary}</div>'
            f'<div class="it"><span class="k" style="color:#F6A65A">Caveat:</span> <span class="ul">small samples; single papers or pairs can drive a result</span></div>'
            f'<div class="it"><span class="k" style="color:#F6A65A">Decisive tests:</span> start at slide {decisive}</div></div>\n{svg}\n'
            f'<div class="soln" style="left:70px;top:660px;width:1140px"><b>So (section):</b> these pages set up the question; the decisive tests of this part start at slide {decisive}. <span class="tg desc">descriptive</span></div>\n'
            f'<span class="pg"></span></section>')
newhtml['div4'] = divider('div4', 'Part 4', 54, 66, P[67], 'the true title helps the true author in late layers; whether recognised papers gain more stayed uncertain', 'about this paper: pilot → replication → full cohort')
newhtml['div5'] = divider('div5', 'Part 5', 86, 93, P[82], 'lenses read names only late and add little; a probe at the title reads a little paper-specific signal early', 'readouts: pilot lenses → full cohort')
newhtml['div6'] = divider('div6', 'Part 6', 108, 118, P[106], 'the recognition gap sits on the rest of the name; full given names and surnames carry the signal, initials little', 'which token: pilot → full cohort')

G2 = [('“Is it about this paper?” (pages of the small-sample line)', 'Line A'), ('“What can each readout see?”', 'Line B'),
      ('“When does it appear and when is it used?”', 'Line C'), ('“Which token carries it?”', 'Line D'),
      ('title test (true title vs wrong titles)', 'RQ1'), ('A−B test (recognised vs not, paired)', 'RQ2'), ('low−high test (citation bands)', 'RQ3'),
      ('Stage 8 replication (200 new papers)', 'Stage 8D'), ('Stage 8 follow-up audit (not pre-registered; unique-token weights, wrong-title length, raw-logit recompute)', 'Stage 8E'),
      ('mean reciprocal rank of the name tokens (teacher-forced)', 'JMRR'),
      ('top lens word (top word of the lens in middle layers)', 'M1'), ('attribute probe (probe reads non-name attributes)', 'M2'),
      ('change-the-question test (same title under another question)', 'M3'), ('author-specific lens (lens fitted on author prompts)', 'M4')]
rows = ''.join(f'<tr><td style="padding:3px 10px 3px 0;border-bottom:1px dashed rgba(170,180,197,.45);color:#6A7385;white-space:nowrap">{b}</td>'
               f'<td style="padding:3px 10px;border-bottom:1px dashed rgba(170,180,197,.45);color:#6A7385">→</td>'
               f'<td style="padding:3px 0;border-bottom:1px dashed rgba(170,180,197,.45)">{html.escape(a)}</td></tr>' for a, b in G2)
newhtml['gloss2'] = (f'<section class="slide lt" aria-label="Glossary (continued)" data-slot="gloss2"><span class="tag">Glossary</span>'
    f'<h2 style="font-size:44px">Glossary (continued): codes in the older reports</h2>'
    f'<p class="sub" style="font-size:15px;margin-bottom:6px">code in the older reports and scripts → plain name on the slides</p>'
    f'<table style="border-collapse:collapse;font-size:15px;line-height:1.3;width:900px"><tbody>{rows}</tbody></table><span class="pg"></span></section>')

# ------------------------------------------------------------------ assemble
out = []
for i, o in enumerate(order):
    s = SEC[o[1]] if o[0] == 'old' else newhtml[o[1]]
    if i > 0: s = re.sub(r'^(<section class="slide[^"]*?) on"', r'\1"', s)
    out.append(s)
GN = {'p3a': 'Part 3 · Read early: the question and the title (H1)', 'p3b': 'Part 3 · Read early: the question and the title (H1)',
      'div4': None, 'div5': None, 'div6': None, 'gloss2': None}
groups = []
for i, o in enumerate(order):
    if o[0] == 'old':
        g = OLDG[o[1]]; title = html.escape(plain(renum_text(OLDT[o[1]])))
    else:
        prev = order[i - 1]; g = OLDG[prev[1]] if prev[0] == 'old' else groups[-1][0]
        title = html.escape(re.search(r'aria-label="([^"]*)"', newhtml[o[1]]).group(1))
    if o == ('old', 47): title = title
    if not groups or groups[-1][0] != g: groups.append([g, []])
    groups[-1][1].append((i + 1, title))
toc = ['<nav class="toc-list" aria-label="All slides">']
for gi, (g, items) in enumerate(groups):
    toc.append(f'<section class="toc-g" aria-labelledby="toc-h{gi}"><h3 class="toc-h" id="toc-h{gi}">{html.escape(g)}<span class="toc-r">{items[0][0]}–{items[-1][0]}</span></h3><ul>')
    toc += [f'<li><a class="toc-i" href="#s{n}" data-i="{n-1}"><span class="toc-n">{n}</span><span class="toc-t">{ti}</span></a></li>' for n, ti in items]
    toc.append('</ul></section>')
toc.append('</nav>')
tj = tail.find('<nav class="toc-list"'); tk = tail.find('</nav>', tj) + 6
tail2 = tail[:tj] + ''.join(toc) + tail[tk:]
tail2 = re.sub(r'<span class="toc-cnt">\d+ slides</span>', f'<span class="toc-cnt">{N} slides</span>', tail2)
open(W + 'deck_v68.html', 'w', encoding='utf-8').write(head + '\n'.join(out) + tail2)
json.dump({'v67_to_v68': REN, 'new': NEWP}, open(W + 'renumber_map_v68.json', 'w'), indent=1)
md = ['# v68 table of contents (★ = new in v68)', '']
for g, items in groups:
    md.append(f'## {html.unescape(g)} ({items[0][0]}–{items[-1][0]})')
    inv = {v: k for k, v in REN.items()}
    md += [f'{n}. {"★ " if n in NEWP.values() else ""}{html.unescape(ti)}' + (f'  (v67 p{inv[n]})' if n in inv else '') for n, ti in items]
    md.append('')
open(W + 'toc_v68.md', 'w').write('\n'.join(md))
json.dump(FIX, open(W + 'fix_v68.json', 'w'), indent=0, ensure_ascii=False)
print('pages', N, 'refs renumbered', nref, 'code replacements', ncode, 'new', NEWP)
