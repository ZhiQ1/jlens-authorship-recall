"""HTML v73 from live v72 (= local 32_v72/deck_v72.html, verified identical):
figure block (v72 133-157) gets 4 new slides at their ORDER.txt positions (step0b after step0; exp2story_a, exp2story_b,
contrib_overview after flow_16x9_d). Updated images are swapped by file (story16x9/ copies from 31_figures/deck16x9);
existing sections unchanged apart from renumbered "slide N" references. Jump menu rebuilt."""
import re, json, html
W = '/home/zhang.zhiqi2/jlens_work/33_v73/'
FIG = '/home/zhang.zhiqi2/jlens_work/31_figures/deck16x9/'
t = open(W + 'base_v72.html', encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
NOLD = len(ms); assert NOLD == 180, NOLD
SEC = {i + 1: m.group(0) for i, m in enumerate(ms)}
head, tail = t[:ms[0].start()], t[ms[-1].end():]
j = t.find('<nav class="toc-list"'); k = t.find('</nav>', j)
OLDT = {int(a): html.unescape(re.sub(r'<[^>]+>', '', b)) for a, b in re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', t[j:k])}
OLDG = {}
for g in re.findall(r'<section class="toc-g".*?</section>', t[j:k], flags=re.S):
    name = html.unescape(re.sub(r'<span class="toc-r">.*', '', re.search(r'<h3[^>]*>(.*?)</h3>', g).group(1)))
    for n in re.findall(r'<span class="toc-n">(\d+)</span>', g): OLDG[int(n)] = name
assert len(OLDT) == NOLD
# figure block check
blk = [n for n in SEC if 'data-slot="story_' in SEC[n]]
assert blk == list(range(133, 158)), (blk[0], blk[-1], len(blk))
files = [l.split()[1] for l in open(FIG + 'ORDER.txt') if l.strip()]
assert len(files) == 29
slot = {n: re.search(r'data-slot="story_([^"]+)"', SEC[n]).group(1) + '.png' for n in blk}
old_files = [slot[n] for n in blk]
assert [f for f in files if f in old_files] == old_files, 'order mismatch'

def slide(fname, title, ask, so, tagc, tagt, alt, sok='So (this slide)'):
    return (f'<section class="slide lt" aria-label="{html.escape(title)}" data-slot="story_{fname[:-4]}"><span class="tag">Summary · story figures</span>'
            f'<h2 style="font-size:24px;margin:0;max-width:1110px;line-height:1.15">{html.escape(title)}</h2>'
            f'<p class="askl" style="margin:3px 0 0;font-size:15px"><b>Now asking:</b> {html.escape(ask)}</p>'
            f'<img src="story16x9/{fname}" alt="{html.escape(alt)}" style="position:absolute;left:116px;top:100px;width:1048px;height:589.5px">'
            f'<div class="soln" style="left:70px;top:695px;width:1140px;font-size:14px;line-height:1.2"><b>{sok}:</b> {html.escape(so)} <span class="tg {tagc}">{html.escape(tagt)}</span></div>'
            '<span class="pg"></span></section>')
NEWD = {
 'step0b_phenomenon.png': ('Before the map: recognised but not said — a large exposure gap, not just guessable names',
   'how large is the gap between recognising and writing, and is it more than guessable names?',
   'recognising needs about 40 citations, writing about 11,000 (ρ ≈ 276; only ρ > 1 is confirmed); guessable names are only about 19% of the gap, and papers with no author written give the same picture.',
   'solid', 'joint',
   'Two panels: recognition and writing rise with citations at about 40 and about 11,000; the name prior is about 19% of the recognised-minus-not gap, and R0 papers alone give +0.20 vs +0.21 pooled.'),
 'exp2story_a.png': ('From experiments to the story (1 of 2): which experiments build sentences 1–4',
   'which experiments carry each sentence of the story, and how do they combine?',
   'S1 rests on four main-line experiments together, S2 on one audit (it cannot decide), S3 on two, S4 on five together.',
   'desc', 'summary; 24 of 100 experiments are main line',
   'Experiment cards with contribution symbols on the left, linked by thick main-line and thin supporting lines to story sentences 1 to 4 on the right.'),
 'exp2story_b.png': ('From experiments to the story (2 of 2): which experiments build sentences 5–7',
   'which experiments carry the last three sentences, and what is still missing?',
   'S5 rests on a cross-check (put back and take away agree); S6 and S7 each combine positive results with an overturned claim; gap ① is still open.',
   'desc', 'summary; one known gap',
   'Experiment cards with contribution symbols linked to story sentences 5 to 7; the open gap is marked.'),
 'contrib_overview.png': ('What each experiment contributed: all 100 at a glance',
   'how many experiments advanced the story, overturned a claim, ruled out an alternative, could not decide, or added little?',
   '48 advanced the story, 5 overturned an earlier claim, 12 ruled out an alternative, 11 could not decide, 24 added little; 24 are main line.',
   'desc', 'summary of the experiment tree',
   'Grid of all 100 experiments by tree, each cell with its contribution symbol, with counts per symbol.'),
}
exec(open(W + 'helpers.py').read())
order = []
bi = {f: n for n, f in slot.items()}
for n in range(1, 133): order.append(('old', n))
for f in files:
    order.append(('old', bi[f]) if f in bi else ('new', f))
for n in range(158, NOLD + 1): order.append(('old', n))
REN = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'old'}
NEWP = {o[1]: i + 1 for i, o in enumerate(order) if o[0] == 'new'}
N = len(order); assert N == 184
for n in SEC: SEC[n] = on_text(SEC[n], renum_text)
out = []
for i, o in enumerate(order):
    s = SEC[o[1]] if o[0] == 'old' else slide(o[1], *NEWD[o[1]])
    if i > 0: s = re.sub(r'^(<section class="slide[^"]*?) on"', r'\1"', s)
    out.append(s)
groups = []
for i, o in enumerate(order):
    if o[0] == 'old': g = OLDG[o[1]]; title = html.escape(renum_text(OLDT[o[1]]))
    else: g = OLDG[133]; title = html.escape(NEWD[o[1]][0])
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
open(W + 'deck_v73.html', 'w', encoding='utf-8').write(head + '\n'.join(out) + tail2)
json.dump({'v72_to_v73': REN, 'new': NEWP}, open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v73.json', 'w'), indent=1)
json.dump(REFLOG, open(W + 'refs_v73.json', 'w'), indent=0, ensure_ascii=False)
inv = {v: kk for kk, v in REN.items()}
md = ['# v73 table of contents (★ = new in v73; v72 page in brackets)', '']
for g, items in groups:
    md.append(f'## {html.unescape(g)} ({items[0][0]}–{items[-1][0]})')
    md += [f'{n}. {"★ " if n in NEWP.values() else ""}{html.unescape(ti)}' + (f'  (v72 p{inv[n]})' if n in inv else '') for n, ti in items]
    md.append('')
open('/home/zhang.zhiqi2/jlens_work/27_v67/toc_v73.md', 'w').write('\n'.join(md))
print('pages', N, 'refs changed', len(REFLOG), 'new', NEWP, 'block', REN[133], '-', REN[157] if 157 in REN else None)
json.dump([[NEWP[f], f, *NEWD[f]] for f in sorted(NEWP, key=NEWP.get)], open(W + 'new_slides_v73.json', 'w'), indent=0, ensure_ascii=False)
