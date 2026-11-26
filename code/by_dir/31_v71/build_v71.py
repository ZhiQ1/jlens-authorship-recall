"""HTML v71 from live v70 (user decisions 2026-11-24, HANDOFF items 32/33/35):
- new explanation slides after 73 ("How the 75% is computed") and after 102 ("The locked rule of this slide"),
- B12 (v70 151) moved right after 45, B22 (v70 150) right after 51, content unchanged,
- B13–B21 (v70 152–160, "How computed") deleted after migration: repeated statistics notes -> new continuation
  slide 15b "Statistical conventions (continued)"; everything else -> script 备查 (script_stage1_13_v65.md),
- B23 kept; every "slide N" reference renumbered (deck, fragments, jump menu).
Writes deck_v71.html, renumber_map_v71.json, toc_v71.md."""
import re, json, html, sys
W = '/home/zhang.zhiqi2/jlens_work/31_v71/'
F = '/home/zhang.zhiqi2/jlens_work/27_v67/fragments/'
t = open(W + 'base_v70.html', encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
assert len(ms) == 161, len(ms)
SEC = {i + 1: m.group(0) for i, m in enumerate(ms)}
head, tail = t[:ms[0].start()], t[ms[-1].end():]
j = t.find('<nav class="toc-list"'); k = t.find('</nav>', j)
OLDT = {int(a): html.unescape(re.sub(r'<[^>]+>', '', b)) for a, b in re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', t[j:k])}
OLDG = {}
for g in re.findall(r'<section class="toc-g".*?</section>', t[j:k], flags=re.S):
    name = html.unescape(re.sub(r'<span class="toc-r">.*', '', re.search(r'<h3[^>]*>(.*?)</h3>', g).group(1)))
    for n in re.findall(r'<span class="toc-n">(\d+)</span>', g): OLDG[int(n)] = name
if 161 not in OLDT:
    OLDT[161] = html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h2[^>]*>(.*?)</h2>', SEC[161], flags=re.S).group(1)))
    OLDG[161] = OLDG[160]
assert len(OLDT) == 161

R = lambda a, b: list(range(a, b + 1))
order = ([('old', n) for n in R(1, 15)] + [('new', 'stats15b')] + [('old', n) for n in R(16, 45)] + [('old', 151)]
         + [('old', n) for n in R(46, 51)] + [('old', 150)] + [('old', n) for n in R(52, 73)] + [('new', 'explain75')]
         + [('old', n) for n in R(74, 102)] + [('new', 'locked')] + [('old', n) for n in R(103, 149)] + [('old', 161)])
DELETED = R(152, 160)
olds = [o[1] for o in order if o[0] == 'old']
assert sorted(olds + DELETED) == R(1, 161)
REN = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'old'}
NEWP = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'new'}
N = len(order)

def on_text(sec, fn):
    hid = []
    def keep(m): hid.append(m.group(0)); return f'\x00{len(hid)-1}\x00'
    s = re.sub(r'<svg class="tx".*?</svg>', keep, sec, flags=re.S)
    parts = re.split(r'(<[^>]+>)', s)
    s = ''.join(p if p.startswith('<') else fn(p) for p in parts)
    return re.sub(r'\x00(\d+)\x00', lambda m: hid[int(m.group(1))], s)

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
REFLOG = []
def renum_text(txt):
    def rep(m):
        nums = expand(m.group(3))
        if any(x < 1 or x > 161 for x in nums): return m.group(0)
        if any(x in DELETED for x in nums):
            REFLOG.append(('DELETED-REF', m.group(0))); return m.group(0)
        new = [REN[x] for x in nums]
        w = m.group(1)
        if len(set(new)) > 1 and not w.endswith('s'): w += 's'
        out = w + m.group(2) + fmt(new)
        if out != m.group(0): REFLOG.append((m.group(0), out))
        return out
    return REF.sub(rep, txt)

# ---- new pages
def frag(name):
    s = open(F + name, encoding='utf-8').read()
    m = re.search(r'<section class="slide[^"]*"[^>]*>.*?</section>', s, flags=re.S)
    return m.group(0)
newhtml = {'explain75': frag('v71_explain_75.html'), 'locked': frag('v71_locked_rule.html')}
L = newhtml['locked']
def sub1(s, a, b):
    assert a in s, a[:70]; return s.replace(a, b, 1)
L = sub1(L, 'Grid for one readout: 9 prompt positions × 20 layers; each cell = within-bin target − control of spec',
         'Grid for one readout: 9 positions × 20 measured layers (rule at L8–L48); cell = within-bin T − C')
L = sub1(L, 'slide-102 rule', 'slide 102 rule')
L = sub1(L, 'layers →  (schematic: 20 tested layers)', 'layers →  (schematic: 20 measured layers, L8–L60)')
assert L.count('>after title<') == 1; L = L.replace('>after title<', '>&quot;)?\\n&quot;<')
L = sub1(L, '672 cells tested', '672 estimable cells tested (9 positions × 14 layers up to L48 × 3 readouts × 2 name tokens; the quote position is not estimable)')
newhtml['locked'] = L
CI_TEAM = [19, 24, 31, 33, 36, 45, 72, 74, 75, 94, 95, 96, 98, 99, 102, 119, 120, 147]
CI_PAPER = [41, 42, 44, 68]
td = 'padding:5px 12px 5px 0;border-bottom:1px dashed rgba(170,180,197,.45);vertical-align:top'
rows = [
    ('Team-cluster bootstrap, 2,000 draws', 'author teams are resampled, so co-authored papers are not counted as independent; where two conditions are compared on the same papers the draws are paired (slides {{p:95}}, {{p:96}}); both citation halves share one set of draws on slide {{p:31}}',
     'slides ' + ', '.join('{{p:%d}}' % n for n in CI_TEAM)),
    ('Paper-level bootstrap', 'papers are resampled one by one (used where the stored analysis was done per paper)',
     'slides ' + ', '.join('{{p:%d}}' % n for n in CI_PAPER)),
    ('Holm correction', 'the format test corrects over its 5 answer-format tests', 'slide {{p:33}}'),
]
trs = ''.join(f'<tr><td style="{td};white-space:nowrap"><b>{a}</b></td><td style="{td}">{b}</td><td style="{td};color:#6A7385">{c}</td></tr>' for a, b, c in rows)
newhtml['stats15b'] = ('<section class="slide lt" aria-label="Statistical conventions (continued)" data-slot="stats15b"><span class="tag">Method · Statistical conventions</span>'
    '<h2 style="font-size:44px">Statistical conventions (continued): which interval each slide uses</h2>'
    '<p class="sub" style="font-size:16px;margin-bottom:8px">Every 95% interval in the deck comes from one of these resampling schemes; this page replaces the per-slide notes on the earlier backup pages</p>'
    f'<table style="border-collapse:collapse;font-size:16px;line-height:1.35;width:1140px"><tbody>{trs}</tbody></table>'
    '<div class="soln" style="left:70px;top:640px;width:1140px"><b>So (this slide):</b> unless a slide says otherwise, intervals are team-cluster bootstrap with 2,000 draws; the paper-level and Holm exceptions are listed here. <span class="tg desc">descriptive</span></div>'
    '<span class="pg"></span></section>')

# ---- renumber old pages and new pages (new pages carry v70 numbers and {{p:N}} placeholders)
for n in SEC:
    if n in DELETED: continue
    SEC[n] = on_text(SEC[n], renum_text)
for kx in newhtml:
    newhtml[kx] = on_text(newhtml[kx], renum_text)
    newhtml[kx] = re.sub(r'\{\{p:(\d+)\}\}', lambda m: str(REN[int(m.group(1))]), newhtml[kx])

out = []
for i, o in enumerate(order):
    s = SEC[o[1]] if o[0] == 'old' else newhtml[o[1]]
    if i > 0: s = re.sub(r'^(<section class="slide[^"]*?) on"', r'\1"', s)
    out.append(s)

groups = []
for i, o in enumerate(order):
    if o[0] == 'old':
        prev = order[i - 1] if i else None
        g = OLDG[o[1]] if o[1] not in (150, 151) else groups[-1][0]
        title = html.escape(renum_text(OLDT[o[1]]))
    else:
        g = groups[-1][0]
        title = html.escape(re.search(r'aria-label="([^"]*)"', newhtml[o[1]]).group(1))
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
open(W + 'deck_v71.html', 'w', encoding='utf-8').write(head + '\n'.join(out) + tail2)
json.dump({'v70_to_v71': REN, 'new': NEWP, 'deleted_v70': DELETED}, open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v71.json', 'w'), indent=1)
inv = {v: kk for kk, v in REN.items()}
md = ['# v71 table of contents (★ = new in v71; v70 page in brackets)', '', 'Deleted from v70 (user-approved 2026-11-24, after migration): slides 152–160 (backups B13–B21, "How computed").', '']
for g, items in groups:
    md.append(f'## {html.unescape(g)} ({items[0][0]}–{items[-1][0]})')
    md += [f'{n}. {"★ " if n in NEWP.values() else ""}{html.unescape(ti)}' + (f'  (v70 p{inv[n]})' if n in inv else '') for n, ti in items]
    md.append('')
open('/home/zhang.zhiqi2/jlens_work/27_v67/toc_v71.md', 'w').write('\n'.join(md))
json.dump(REFLOG, open(W + 'refs_v71.json', 'w'), indent=0, ensure_ascii=False)
print('pages', N, 'refs changed', sum(1 for r in REFLOG if r[0] != 'DELETED-REF'), 'deleted-refs', [r for r in REFLOG if r[0] == 'DELETED-REF'], 'new', NEWP)
