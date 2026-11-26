"""v67 skeleton (2026-11-23, agent A): reorder live v66 per toc_proposal (r2 + brief extras), add placeholder slots,
renumber slide references, rebuild the jump-menu TOC. Add-only: every v66 section is kept verbatim except reference numbers.
usage: build_skeleton.py  -> deck_v67.html, renumber_map.json, order_v67.json"""
import re, json, html
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
SRC = W + 'live_v66.html'
TOC = '/home/zhang.zhiqi2/jlens_work/25_restructure/toc_proposal_20261123.md'
t = open(SRC, encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
assert len(ms) == 118, len(ms)
SEC = {i + 1: m.group(0) for i, m in enumerate(ms)}
head, tail = t[:ms[0].start()], t[ms[-1].end():]
between = [t[ms[i].end():ms[i + 1].start()] for i in range(117)]
assert all(not b.strip() for b in between)

# old TOC titles
j = t.find('<nav class="toc-list"'); k = t.find('</nav>', j)
OLDT = {int(a): html.unescape(re.sub(r'<[^>]+>', '', b)) for a, b in
        re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', t[j:k])}

# ---- order from the approved TOC (+ brief extras) ----
NEWMAP = [  # (substring in TOC new line, slot id, title)
    ('How to read this deck', 'how-to-read', 'How to read this deck'),
    ('The gap in one picture', 'gap-picture', 'The gap in one picture'),
    ('Question card · H1', 'h1-question', 'Question card · H1: is the answer format fixed in the middle layers?'),
    ('When is the answer format fixed', 'h1-format', 'When is the answer format fixed? The format layer is not pinned down'),
    ('Verdict card · H1', 'h1-verdict', 'Verdict card · H1'),
    ('Evidence matrix (updated after H1)', 'h1-matrix', 'Evidence matrix after H1'),
    ('Question card · H2', 'h2-question', 'Question card · H2: does the title state hold this paper’s identity?'),
    ('Real title vs made-up title vs rare/common words', 'rare-words', 'Rare words carry the real-title extra'),
    ('The one locked exception', 'h2-exception', 'The one locked exception: a small surname signal at L8'),
    ('Verdict card · H2', 'h2-verdict', 'Verdict card · H2'),
    ('Evidence matrix (updated after H2)', 'h2-matrix', 'Evidence matrix after H2'),
    ('Question card · H3', 'h3-question', 'Question card · H3: is author information there but not in vocabulary directions?'),
    ('Single-layer route', 'route', 'Single-layer route: many small parallel paths'),
    ('Verdict card · H3', 'h3-verdict', 'Verdict card · H3'),
    ('Evidence matrix (updated after H3)', 'h3-matrix', 'Evidence matrix after H3'),
    ('Question card · Bottleneck', 'w-question', 'Question card · Bottleneck: where does writing the name fail?'),
    ('Late suppression in a subgroup', 'suppression', 'Late suppression: in about 1 in 8 papers the name rises, then falls'),
    ('Probe direction: write channel vs unlock', 'asymmetry', 'Direction asymmetry: generating the title is slightly harder than recalling the authors'),
    ('Verdict card · Bottleneck', 'w-verdict', 'Verdict card · Bottleneck'),
    ('Evidence matrix (updated after Bottleneck)', 'w-matrix', 'Evidence matrix after the bottleneck'),
]
EXTRA_BEFORE = {  # brief: extra pages
    'h1-format': [('h1-colon-ratio', 'At “:”, a new question moves the state more than a new paper')],
    'rare-words': [('ceiling', 'Why the change-the-question test cannot see identity: a ceiling'),
                   ('recog-citations', 'Recognised vs not, and by citations: the real-title extra does not grow'),
                   ('variance', 'Variance split: identity adds ≈ 0 beyond text features')],
}
EXTRA_AFTER = {'route': [('injection', 'Injecting the author direction: mostly a write channel'), ('injection-why', 'Why pushing hurts: direction, not length')]}
S_TITLES = ['S1 · Read early, said late', 'S2 · Step ① the question', 'S3 · Steps ② + ③ the title and what is read',
            'S4 · Step ④ delivery to the name positions', 'S5 · Step ⑤ held, but not in vocabulary directions',
            'S6 · Steps ⑥ + ⑦ written late, stuck at writing', 'S7 · Evidence ledger', 'S8 · What we ruled out',
            'S9 · Against the literature', 'S10 · Open questions and next steps']

order = []  # ('old', n) | ('new', slot, title, part)
part = None; sk = 0
for ln in open(TOC, encoding='utf-8'):
    ln = ln.rstrip('\n')
    m = re.match(r'## Part (\S+)', ln)
    if m: part = m.group(1); continue
    m = re.match(r'\s*(\d+)\. (.*)$', ln)
    if not m: continue
    body = m.group(2)
    mo = re.search(r'\(v65 p(\d+)\)', body)
    if mo: order.append(('old', int(mo.group(1)), part)); continue
    if body.startswith('='): order.append(('old', int(m.group(1)), part)); continue
    if 'S1 Answer' in body or re.search(r'★\s+S\d', body):
        sk += 1; order.append(('new', 'part7_S%02d' % sk, S_TITLES[sk - 1], part)); continue
    hit = [x for x in NEWMAP if x[0] in body]
    assert len(hit) == 1, body
    _, slot, title = hit[0]
    for s2, t2 in EXTRA_BEFORE.get(slot, []): order.append(('new', s2, t2, part))
    order.append(('new', slot, title, part))
    for s2, t2 in EXTRA_AFTER.get(slot, []): order.append(('new', s2, t2, part))
olds = [o[1] for o in order if o[0] == 'old']
assert sorted(olds) == list(range(1, 119)), (len(olds), sorted(set(range(1, 119)) - set(olds)))
assert sk == 10
N = len(order)
REN = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'old'}
SLOTNUM = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'new'}

# ---- renumber references in visible text (never inside tags/attributes) ----
def map_list(nums):
    return [REN.get(n, n) for n in nums]
def fmt(nums):
    nums = sorted(set(nums))
    if len(nums) == 1: return str(nums[0])
    # contiguous runs as ranges
    out, a = [], nums[0]; prev = a
    for x in nums[1:] + [None]:
        if x is not None and x == prev + 1: prev = x; continue
        out.append(str(a) if a == prev else (f'{a}–{prev}' if prev > a + 1 else f'{a}, {prev}'))
        if x is not None: a = prev = x
    s = ', '.join(out)
    return s
REF = re.compile(r'\b(slides?|Slides?)(\s+)(\d{1,3}(?:\s*(?:–|-|,|and|&amp;|&)\s*\d{1,3})*)')
def expand(spec):
    nums = []
    for part_ in re.split(r'\s*(?:,|and|&amp;|&)\s*', spec):
        if re.search(r'[–-]', part_):
            a, b = [int(x) for x in re.split(r'\s*[–-]\s*', part_)]
            nums.extend(range(a, b + 1) if b - a < 15 else [a, b])
        elif part_.strip(): nums.append(int(part_))
    return nums
nref = 0
def fix_text(s):
    global nref
    def rep(m):
        global nref
        nums = expand(m.group(3))
        if any(n < 1 or n > 118 for n in nums): return m.group(0)
        new = map_list(nums); nref += 1
        word = m.group(1)
        if len(set(new)) > 1 and not word.endswith('s'): word += 's'
        return word + m.group(2) + fmt(new)
    return REF.sub(rep, s)
def renum(sec):
    parts = re.split(r'(<[^>]+>)', sec)
    return ''.join(p if p.startswith('<') else fix_text(p) for p in parts)

def placeholder(slot, title, n):
    return (f'<section class="slide lt" aria-label="{html.escape(title)}" data-slot="{slot}"><span class="tag">new</span>\n'
            f'<h2 style="font-size:40px;margin-top:6px">{html.escape(title)}</h2>\n'
            f'<p class="sub">[placeholder for slot {slot}; filled in phase 2]</p><span class="pg"></span></section>')

out = []
for i, o in enumerate(order):
    if o[0] == 'old':
        s = renum(SEC[o[1]])
        if i > 0: s = s.replace('<section class="slide on', '<section class="slide', 1).replace(' on"', '"', 1) if re.match(r'<section class="slide[^"]* on"', s) else s
        out.append(s)
    else:
        out.append(placeholder(o[1], o[2], i + 1))
# first slide must carry 'on' as in v66 (v66 p1 stays first)
assert order[0] == ('old', 1, '0')

# ---- jump-menu TOC grouped by Part ----
PARTN = {'0': 'Part 0 · Opening', '1': 'Part 1 · Setup and methods', '2': 'Part 2 · Recognised but not said',
         '3': 'Part 3 · Read early: the question and the title (H1)', '4': 'Part 4 · What is read: meaning, not identity (H2)',
         '5': 'Part 5 · Where it goes and how it is held (route + H3)', '6': 'Part 6 · Said late, stuck at writing',
         '7': 'Part 7 · Summary', '8': 'Part 8 · Checks and limits', 'B': 'Glossary and backups'}
groups = []
for i, o in enumerate(order):
    p = o[-1]
    if not groups or groups[-1][0] != p: groups.append([p, []])
    title = fix_text(html.escape(OLDT[o[1]])) if o[0] == 'old' else html.escape(o[2])
    title = re.sub(r' \((?:M3, )?X[1-5](?:, X[1-5])?\)', '', title).replace('X2: swap only a subspace', 'Swap only a subspace')
    groups[-1][1].append((i + 1, title))
toc = ['<nav class="toc-list" aria-label="All slides">']
for gi, (p, items) in enumerate(groups):
    toc.append(f'<section class="toc-g" aria-labelledby="toc-h{gi}"><h3 class="toc-h" id="toc-h{gi}">{PARTN[p]}'
               f'<span class="toc-r">{items[0][0]}–{items[-1][0]}</span></h3><ul>')
    for n, ti in items:
        toc.append(f'<li><a class="toc-i" href="#s{n}" data-i="{n-1}"><span class="toc-n">{n}</span><span class="toc-t">{ti}</span></a></li>')
    toc.append('</ul></section>')
toc.append('</nav>')
tj = tail.find('<nav class="toc-list"'); tk = tail.find('</nav>', tj) + len('</nav>')
assert tj > 0
tail2 = tail[:tj] + ''.join(toc) + tail[tk:]
tail2 = tail2.replace('<span class="toc-cnt">118 slides</span>', f'<span class="toc-cnt">{N} slides</span>')
deck = head + '\n'.join(out) + tail2
open(W + 'deck_v67.html', 'w', encoding='utf-8').write(deck)
json.dump({'v66_to_v67': REN, 'slots': SLOTNUM}, open(W + 'renumber_map.json', 'w'), indent=1)
json.dump([list(o) for o in order], open(W + 'order_v67.json', 'w'), indent=0)
print('pages', N, 'refs renumbered', nref, 'slots', len(SLOTNUM))
