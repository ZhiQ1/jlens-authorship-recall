"""HTML v72 from live v71 (user 2026-11-25, HANDOFF items 44-45):
25 story-figure slides (31_figures/deck16x9, ORDER.txt) inserted at the very start of Part 7, before v71 slide 133;
nothing replaced; every "slide N" reference renumbered; jump menu rebuilt.
Writes deck_v72.html (images referenced as story16x9/<file>.png), renumber_map_v72.json, toc_v72.md."""
import re, json, html
W = '/home/zhang.zhiqi2/jlens_work/32_v72/'
FIG = '/home/zhang.zhiqi2/jlens_work/31_figures/deck16x9/'
t = open(W + 'base_v71.html', encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
NOLD = len(ms); assert NOLD == 155, NOLD
SEC = {i + 1: m.group(0) for i, m in enumerate(ms)}
head, tail = t[:ms[0].start()], t[ms[-1].end():]
j = t.find('<nav class="toc-list"'); k = t.find('</nav>', j)
OLDT = {int(a): html.unescape(re.sub(r'<[^>]+>', '', b)) for a, b in re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', t[j:k])}
OLDG = {}
for g in re.findall(r'<section class="toc-g".*?</section>', t[j:k], flags=re.S):
    name = html.unescape(re.sub(r'<span class="toc-r">.*', '', re.search(r'<h3[^>]*>(.*?)</h3>', g).group(1)))
    for n in re.findall(r'<span class="toc-n">(\d+)</span>', g): OLDG[int(n)] = name
assert len(OLDT) == NOLD, len(OLDT)
INS = 133                                   # first v71 slide of Part 7 ("What we learned: read early, spoken late")
assert 'Part 7' in OLDG[INS] and 'What we learned' in OLDT[INS], (OLDG[INS], OLDT[INS])

files = [l.split()[1] for l in open(FIG + 'ORDER.txt') if l.strip()]
assert len(files) == 25, len(files)

STEP = {1: ('L0–L4', 'the input words decide almost everything', 'desc', 'cannot separate meaning from identity here'),
        2: ('L4–L24', 'early read-in; the first traces of the title and of the first author', 'solid', 'joint'),
        3: ('L24–L40', 'the main title-reading phase; what is read is meaning and specific words, not paper identity', 'lnot', 'overturns the general form of H2'),
        4: ('L40–L52', 'the information reaches the name positions, over several layers in parallel; the title is read by L52', 'solid', 'joint'),
        5: ('L48–L56', 'the probe reads it, the lens does not; what arrives is paper information, not ready-made names', 'lsup', 'one experiment each: same-scale test, MLP swap'),
        6: ('L56–L63', 'the late MLPs write the name; the gap grows here, and it gets stuck at writing', 'solid', 'joint')}
BAND2STEP = {v[0].replace('–', '_'): kk for kk, v in STEP.items()}
CIRC = '①②③④⑤⑥'
STAGE_T = {1: 'the input words decide almost everything', 2: 'early read-in; first traces of the title and of the first author',
           3: 'what is read is meaning and specific words, not paper identity', 4: 'the title reaches the names over several layers in parallel; read by L52',
           5: 'the probe reads it, the lens does not; paper information, not ready-made names', 6: 'the late MLPs write the name; it gets stuck at writing'}

def slide(fname, title, ask, so, tagc, tagt, alt, sok='So (this slide)'):
    return (f'<section class="slide lt" aria-label="{html.escape(title)}" data-slot="story_{fname[:-4]}"><span class="tag">Summary · story figures</span>'
            f'<h2 style="font-size:24px;margin:0;max-width:1110px;line-height:1.15">{html.escape(title)}</h2>'
            f'<p class="askl" style="margin:3px 0 0;font-size:15px"><b>Now asking:</b> {html.escape(ask)}</p>'
            f'<img src="story16x9/{fname}" alt="{html.escape(alt)}" style="position:absolute;left:116px;top:100px;width:1048px;height:589.5px">'
            f'<div class="soln" style="left:70px;top:695px;width:1140px;font-size:14px;line-height:1.2"><b>{sok}:</b> {html.escape(so)} <span class="tg {tagc}">{html.escape(tagt)}</span></div>'
            '<span class="pg"></span></section>')

NEW = []
for f in files:
    if f.startswith('step0'):
        NEW.append((f, 'The whole story on one map (all six stages lit)', 'putting every result together, where does recall of a paper’s authors break?',
                    'read early, said late: the title is read and delivered by about L52; the name is written only at L57–L61, and recall stalls there.',
                    'desc', 'summary of the six stages; details on the stage slides',
                    'Token × layer map of the whole story: the title is read L24–L52, delivered to the name positions through parallel pipes, and the name is written at L57–L61, where it gets stuck at the first token.',
                    'So (section)'))
    elif f.startswith('step'):
        s = int(f[4]); band, concl, tc, tt = STEP[s]
        NEW.append((f, f'Step {CIRC[s-1]} of 6 · {band}: {concl}', f'what happens in {band}, position by position?', f'{band}: {concl}.', tc, tt,
                    f'The same map with only stage {s} ({band}) lit; the rest faded.'))
    elif f.startswith('stage_'):
        m = re.match(r'stage_(L\d+_L\d+)_16x9_([abc])\.png', f); band = m.group(1); part = m.group(2)
        s = BAND2STEP[band]; nparts = sum(1 for x in files if x.startswith(f'stage_{band}_'))
        b2, concl, tc, tt = STEP[s]
        NEW.append((f, f'Stage {CIRC[s-1]} · {b2} in detail: {STAGE_T[s]} (part {"abc".index(part)+1} of {nparts})',
                    f'how was the {b2} conclusion reached, experiment by experiment?', f'{b2}: {concl}.', tc, tt,
                    f'Reasoning chain for stage {s} ({b2}): experiments top to bottom, rewritten and ruled-out items on the left, exceptions and dependencies on the right.'))
    elif f.startswith('flow_'):
        part = f[-5]; nparts = sum(1 for x in files if x.startswith('flow_'))
        NEW.append((f, f'How the pieces fit: the story map, step by step (part {"abcd".index(part)+1} of {nparts})',
                    'how does each step of the story depend on the one before, and which experiments carry it?',
                    'each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt.',
                    'desc', 'summary; two known gaps',
                    'Flowchart of the seven story steps with their experiments and the two known gaps as broken links.'))
assert len(NEW) == 25

order = [('old', n) for n in range(1, INS)] + [('new', i) for i in range(25)] + [('old', n) for n in range(INS, NOLD + 1)]
REN = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'old'}
NEWP = {NEW[o[1]][0]: i + 1 for i, o in enumerate(order) if o[0] == 'new'}
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
        if any(x < 1 or x > NOLD for x in nums): return m.group(0)
        new = [REN[x] for x in nums]
        w = m.group(1)
        if len(set(new)) > 1 and not w.endswith('s'): w += 's'
        out = w + m.group(2) + fmt(new)
        if out != m.group(0): REFLOG.append((m.group(0), out))
        return out
    return REF.sub(rep, txt)

for n in SEC: SEC[n] = on_text(SEC[n], renum_text)
out = []
for i, o in enumerate(order):
    s = SEC[o[1]] if o[0] == 'old' else slide(*NEW[o[1]])
    if i > 0: s = re.sub(r'^(<section class="slide[^"]*?) on"', r'\1"', s)
    out.append(s)

groups = []
for i, o in enumerate(order):
    if o[0] == 'old': g = OLDG[o[1]]; title = html.escape(renum_text(OLDT[o[1]]))
    else: g = OLDG[INS]; title = html.escape(NEW[o[1]][1])
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
open(W + 'deck_v72_stage1.html', 'w', encoding='utf-8').write(head + '\n'.join(out) + tail2)
json.dump({'v71_to_v72': REN, 'new': NEWP}, open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v72.json', 'w'), indent=1)
json.dump(REFLOG, open(W + 'refs_v72.json', 'w'), indent=0, ensure_ascii=False)
json.dump([(NEWP[x[0]],) + tuple(x) for x in NEW], open(W + 'new_slides_v72.json', 'w'), indent=1, ensure_ascii=False)
inv = {v: kk for kk, v in REN.items()}
md = ['# v72 table of contents (★ = new in v72; v71 page in brackets)', '']
for g, items in groups:
    md.append(f'## {html.unescape(g)} ({items[0][0]}–{items[-1][0]})')
    md += [f'{n}. {"★ " if n in NEWP.values() else ""}{html.unescape(ti)}' + (f'  (v71 p{inv[n]})' if n in inv else '') for n, ti in items]
    md.append('')
open('/home/zhang.zhiqi2/jlens_work/27_v67/toc_v72.md', 'w').write('\n'.join(md))
print('pages', N, 'refs changed', len(REFLOG), 'new block', min(NEWP.values()), '–', max(NEWP.values()))
