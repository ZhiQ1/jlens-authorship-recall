"""Phase 2: integrate fragments into v67 slots, resolve {{p:N}} (v65=v66 numbers) and {{new:slot}}, add the remaining Part
transitions. Re-runnable: reads deck_v67.html (phase 1 + coverage), writes deck_v67_full.html."""
import re, json, html, os, sys
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
FR = W + 'fragments/'
t = open(W + 'deck_v67.html', encoding='utf-8').read()
M = json.load(open(W + 'renumber_map.json'))
REN = {int(k): v for k, v in M['v66_to_v67'].items()}; SLOT = M['slots']
ALIAS = {'reversal': 'asymmetry'}
miss = []
def resolve(s):
    def rp(m):
        n = int(m.group(1)); return str(REN[n])
    def rn(m):
        k = ALIAS.get(m.group(1), m.group(1))
        if k not in SLOT: miss.append(k); return m.group(0)
        return str(SLOT[k])
    s = re.sub(r'\{\{p:(\d+)\}\}', rp, s)
    return re.sub(r'\{\{new:([\w-]+)\}\}', rn, s)
done = []
for slot in SLOT:
    if slot in ('how-to-read', 'gap-picture'): continue
    f = FR + slot + '.html'
    if not os.path.exists(f): miss.append('file:' + slot); continue
    frag = open(f, encoding='utf-8').read().strip()
    frag = resolve(frag)
    if '<span class="pg"></span>' not in frag:
        frag = frag[:-len('</section>')] + '<span class="pg"></span></section>'
    m = re.search(r'<section class="slide lt" aria-label="[^"]*" data-slot="%s">.*?</section>' % re.escape(slot), t, flags=re.S)
    assert m, slot
    t = t[:m.start()] + frag + t[m.end():]; done.append(slot)

# Part transitions not covered by fragments / A pages: end of Part 1 (v66 p67) and end of Part 8 (v66 p106)
def add_note(v66, text, tagc, tagl, x, y, w, fs=12.5):
    global t
    ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
    m = ms[REN[v66] - 1]; s = m.group(0)
    box = (f'<div class="soln covtr" style="left:{x}px;top:{y}px;width:{w}px;font-size:{fs}px;box-sizing:border-box;z-index:7">'
           f'<b>So (section):</b> {text} <span class="tg {tagc}">{tagl}</span></div>')
    s = s[:-len('</section>')] + box + '</section>'
    t = t[:m.start()] + s + t[m.end():]
TR = json.load(open(W + 'transitions.json')) if os.path.exists(W + 'transitions.json') else {}
for k, v in TR.items():
    add_note(int(k), html.escape(v['text']), v['tagc'], v['tagl'], v['x'], v['y'], v['w'], v.get('fs', 12.5))
# jump-menu titles of new pages = the fragment's own aria-label
for slot, n in SLOT.items():
    m = re.search(r'<section class="slide[^"]*" aria-label="([^"]*)" data-slot="%s"' % re.escape(slot), t)
    if not m: continue
    lab = m.group(1)
    t = re.sub(r'(<span class="toc-n">%d</span><span class="toc-t">)[^<]*(</span>)' % n, lambda mm: mm.group(1) + lab + mm.group(2), t, count=1)
open(W + 'deck_v67_full.html', 'w', encoding='utf-8').write(t)
print('integrated', len(done), 'missing', miss)
