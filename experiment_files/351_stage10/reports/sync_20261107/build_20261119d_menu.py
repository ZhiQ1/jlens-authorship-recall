"""2026-11-19d: add a jump menu (table of contents) to the merged HTML deck. Nothing else changes: all <section class="slide">
blocks except the two content fixes (slide 75 pointer; 18b item 4 'settled' on 44, 51, 62, 68, 69, 75, 86) stay byte-identical; only the nav bar (a 'contents' button), one extra <style> block, the panel markup after the nav and the
deck script (show() also syncs the menu; menu code added before the initial show) change.
Source = merged_deck/stage1_11_deck.html.before_20261119d -> merged_deck/stage1_11_deck.html. Idempotent (always rebuilds from the backup).
Titles: h1/h2 of the slide; else the largest SVG <text> (method / figure slides); else a fixed map for the Stage 10-11 picture slides
(keyed by their img alt, read off the images 2026-11-19); slide 1 uses the document <title>. Duplicate titles get the tag's suffix.
Sections are found from the deck's own markers (asserted), not hard-coded slide numbers. Writes build_20261119d_menu.json."""
import re, json, html
from pathlib import Path

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
SRC = D / 'stage1_11_deck.html.before_20261119d'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
assert 'id="toc"' not in s
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 94, len(ms)
SL = [m.group(0) for m in ms]
CJK = re.compile('[　-〿一-鿿＀-￯]')

# ---------------------------------------------------------------- two content fixes (coordinator 2026-11-19, same build)
# (1) slide 75 lead pointer: the L52-L56 MLP slide is 74 (72 is item 3). Other pointers on 70-76 checked: correct.
# (2) 18b item 4 (C29, L57-L61 written by the MLPs) is settled per the user: its status wording -> "settled (locked criterion met)".
#     Other items' statuses untouched.
CHANGED = {}
def rep(k, a, b, msg):
    assert SL[k - 1].count(a) == 1, (k, SL[k - 1].count(a), a[:80])
    SL[k - 1] = SL[k - 1].replace(a, b); CHANGED.setdefault(k, []).append(msg)
ST = 'settled (locked criterion met)'
rep(75, '<div class="lead">← slides 51, 72: steepest rise', '<div class="lead">← slides 51, 74: steepest rise', 'lead pointer 72 -> 74')
rep(44, 'the MLPs (item 4) <span class="st c1">confirmed</span>', f'the MLPs (item 4) <span class="st c1">{ST}</span>', 'item 4 status')
rep(51, '[0.036, 0.045] (item 4, <span class="g">confirmed</span>) → slide 75', f'[0.036, 0.045] · item 4 <span class="g">{ST}</span> → slide 75', 'item 4 status')
rep(62, 'L57–L61 are written by MLPs <span class="st c1">confirmed</span>', f'L57–L61 are written by MLPs <span class="st c1">{ST}</span>', 'item 4 status')
rep(68, 'L57–L61 written by MLPs (item 4) <span class="st c1">confirmed</span>', f'L57–L61 written by MLPs (item 4) <span class="st c1" style="white-space:normal">{ST}</span>', 'item 4 status')  # narrow box: let the pill wrap
rep(69, 'L57–L61 written by MLPs (item 4) <span class="st c1">confirmed</span>', f'L57–L61 written by MLPs (item 4) <span class="st c1">{ST}</span>', 'item 4 status')
rep(86, '<span class="st c1">confirmed</span> (locked criterion) → slide 75', f'<span class="st c1">{ST}</span> → slide 75', 'item 4 status')
OLDB, NEWB = 'Locked criterion: met (5 / 5 layers)', 'Settled: locked criterion met (5 / 5 layers)'
wb = lambda x: sum(16 * 0.58 for _ in x) + 26  # same width rule as the badge builder (apply_20261112r_lib.width + padding)
assert abs(wb(OLDB) - 360.1) < 0.2
rep(75, f'<rect x="70.0" y="124.0" width="360.1" height="28"', f'<rect x="70.0" y="124.0" width="{wb(NEWB):.1f}" height="28"', 'badge width')
rep(75, f'>{OLDB}</text>', f'>{NEWB}</text>', 'item 4 badge')
rep(75, '<tspan x="70.0" dy="0.0">Locked criterion met at all 5 layers: MLP − attention loss +0.037 to +0.046, mean +0.040 [+0.036, +0.045]; attention ≈ 0 (≤ 0.0012); each MLP layer</tspan><tspan x="70.0" dy="16.6">removes 11–14% of S.</tspan>',
    '<tspan x="70.0" dy="0.0">Settled (locked criterion met at all 5 layers): MLP − attention loss +0.037 to +0.046, mean +0.040 [+0.036, +0.045]; attention ≈ 0 (≤ 0.0012);</tspan><tspan x="70.0" dy="16.6">each MLP layer removes 11–14% of S.</tspan>',
    'item 4 verdict line')
for k, t in enumerate(SL): assert 'confirmed</span> (locked criterion)' not in t
_parts, _last = [], 0
for m, t in zip(ms, SL): _parts += [s[_last:m.start()], t]; _last = m.end()
s = ''.join(_parts) + s[_last:]

IMG = {  # Stage 10-11 picture slides: alt -> title as printed on the picture
    4: 'How groups and contrasts are built', 5: 'How we read the model', 17: 'Can we trust the numbers?',
    6: 'Knowing the paper shows up only at the end', 12: 'How much is just the name prior?', 21: 'The probe signal is paper-specific',
    24: 'More citations, more paper knowledge', 13: 'Is it just the R1 papers? No.', 20: 'Authors it wrote vs authors it missed',
    18: 'Names become readable late', 22: 'Which lens reads best?', 23: 'Do lenses reveal hidden paper knowledge?',
    11: 'Read early: a probe finds it at the title', 7: 'Target pulls ahead only in the last layers', 8: 'It builds up over the last dozen layers',
    9: 'Stage 11: intervene, do not just read', 10: 'The title is read in L24–L50, early', 25: 'First token or the rest of the name?',
    26: 'Knowing the given name helps with the surname', 27: 'Where the signal sits, and a dose-response', 19: 'Co-authors help, and partly replace the title'}


def txt(x):
    x = re.sub(r'<br\s*/?>', ' ', x)
    x = html.unescape(re.sub(r'<[^>]+>', '', x))
    return re.sub(r'\s+', ' ', x).strip()


def tag_of(t):
    m = re.search(r'class="tag[^"]*"[^>]*>(.*?)</', t, re.S)
    if m: return txt(m.group(1))
    m = re.search(r'<text[^>]*data-name="tag"[^>]*>(.*?)</text>', t, re.S)
    return txt(m.group(1)) if m else ''


doc_title = txt(re.search(r'<title>(.*?)</title>', s).group(1))
titles, tags, how = [], [], []
for k, t in enumerate(SL, 1):
    t2 = re.sub(r'data:[^"]+', '', t)
    tags.append(tag_of(t2))
    if k == 1:
        titles.append(doc_title); how.append('doc title'); continue
    h = re.search(r'<h[12][^>]*>(.*?)</h[12]>', t2, re.S)
    if h:
        titles.append(txt(h.group(1))); how.append('h'); continue
    best = None
    for m in re.finditer(r'<text([^>]*)>(.*?)</text>', t2, re.S):
        fs = re.search(r'font-size="([\d.]+)"', m.group(1))
        if fs and float(fs.group(1)) >= 36 and (best is None or float(fs.group(1)) > best[0]): best = (float(fs.group(1)), txt(m.group(2)))
    if best:
        titles.append(best[1]); how.append('svg'); continue
    a = re.search(r'<img alt="Stage 10-11 slide (\d+)"', t2)
    if a:
        titles.append(IMG[int(a.group(1))]); how.append('img'); continue
    titles.append(re.search(r'aria-label="([^"]*)"', t2).group(1)); how.append('aria')
# duplicate titles ("What we saw") -> add the tag's last part
dups = {t for t in titles if titles.count(t) > 1}
for k, ti in enumerate(titles):
    if ti in dups:
        suf = tags[k].split('·')[-1].strip()
        assert suf, (k + 1, ti)
        titles[k] = f'{ti}: {suf}'
assert len(set(titles)) == 94, [t for t in titles if titles.count(t) > 1]
assert all(t and not CJK.search(t) and len(t) < 110 for t in titles), titles
assert 'aria' not in how, how


# sections from the deck's own markers
def first(pred, start=0):
    for k in range(start, 94):
        if pred(k): return k
    raise AssertionError('marker not found')


secs = [(0, 'Overview and setup')]
for L in 'ABCD':
    k = first(lambda k: tags[k] == f'Overview · Line {L}')
    secs.append((k, f'Line {L} · {titles[k]}'))
secs.append((first(lambda k: tags[k] == 'Overview · Lines A–D'), 'Synthesis'))
secs.append((first(lambda k: tags[k].startswith('Method · Changing the question')), 'Stage 12–13'))
secs.append((first(lambda k: tags[k].startswith('Groups')), 'Group comparisons'))
secs.append((first(lambda k: tags[k] == 'Stage 13 · checks'), 'Checks and limits'))
starts = [a for a, _ in secs]
assert starts == sorted(starts) and len(set(starts)) == len(starts), secs
assert starts == [0, 11, 33, 43, 51, 61, 64, 87, 91], starts  # as of v41; change deliberately if the deck is restructured

# ---------------------------------------------------------------- markup
e = lambda x: html.escape(x, quote=True)
groups = []
for j, (a, name) in enumerate(secs):
    b = secs[j + 1][0] if j + 1 < len(secs) else 94
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span>'
                    f'<span class="toc-t">{e(titles[k])}</span></a></li>' for k in range(a, b))
    rng = f'{a + 1}–{b}' if b - a > 1 else f'{a + 1}'
    groups.append(f'<section class="toc-g" aria-labelledby="toc-h{j}"><h3 class="toc-h" id="toc-h{j}">{e(name)}'
                  f'<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
ICON = ('<svg class="toc-ic" viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" focusable="false">'
        '<path d="M2 3.5h12M2 8h12M2 12.5h12" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>')
BTN = (f'<button id="tocbtn" type="button" aria-haspopup="dialog" aria-expanded="false" aria-controls="toc" '
       f'title="Contents (C)">{ICON}<span class="toc-bl">contents</span></button>')
PANEL = ('<div class="toc-scrim" id="tocscrim" hidden></div>'
         '<div class="toc" id="toc" role="dialog" aria-modal="false" aria-labelledby="toc-title" hidden>'
         '<div class="toc-top"><span class="toc-title" id="toc-title">Contents</span><span class="toc-cnt">94 slides</span>'
         '<button class="toc-x" id="tocx" type="button" aria-label="Close contents">×</button></div>'
         '<nav class="toc-list" aria-label="All slides">' + ''.join(groups) + '</nav></div>')

CSS = r'''<style>
/* jump menu (2026-11-19d) */
#tocbtn{display:inline-flex; align-items:center; gap:6px}
.toc-ic{display:block; flex:none}
.toc-scrim{position:fixed; inset:0; z-index:20; background:rgba(16,20,28,.22)}
.toc{position:fixed; z-index:21; left:50%; bottom:calc(54px + env(safe-area-inset-bottom,0px)); transform:translateX(-50%);
  width:min(460px, calc(100vw - 32px)); max-height:calc(100vh - 54px - 24px - env(safe-area-inset-bottom,0px) - env(safe-area-inset-top,0px));
  display:flex; flex-direction:column; font-family:var(--hand); color:var(--chrome-ink); background:var(--chrome);
  border:2px solid var(--chrome-ink); border-radius:18px 6px 16px 6px/6px 16px 6px 18px; box-shadow:0 8px 28px rgba(0,0,0,.28); overflow:hidden}
.toc[hidden],.toc-scrim[hidden]{display:none}
.toc-top{display:flex; align-items:baseline; gap:10px; padding:10px 10px 8px 18px; border-bottom:1.5px dashed var(--chrome-pen)}
.toc-title{font-family:var(--title); font-weight:700; font-size:30px; line-height:1}
.toc-cnt{font-size:15px; color:var(--chrome-pen); flex:1}
.toc-x{font:inherit; font-size:24px; line-height:1; width:40px; height:40px; color:var(--chrome-ink); background:transparent;
  border:2px solid transparent; border-radius:12px 5px 11px 5px/5px 11px 5px 12px; cursor:pointer; align-self:center}
.toc-x:hover{border-color:var(--chrome-pen)}
.toc-list{overflow-y:auto; overscroll-behavior:contain; -webkit-overflow-scrolling:touch; padding:4px 0 10px}
.toc-g ul{list-style:none; margin:0; padding:0}
.toc-h{display:flex; align-items:baseline; gap:8px; margin:0; padding:12px 18px 3px; font-family:var(--hand); font-weight:400;
  font-size:14px; letter-spacing:.04em; text-transform:uppercase; color:var(--chrome-pen)}
.toc-r{margin-left:auto; letter-spacing:0; font-size:13px; opacity:.8}
.toc-i{display:flex; align-items:flex-start; gap:12px; min-height:34px; padding:6px 18px; color:var(--chrome-ink); text-decoration:none;
  font-size:17px; line-height:1.25; border-left:4px solid transparent}
.toc-i:hover{background:rgba(125,140,165,.14)}
.toc-n{flex:none; width:2.1em; text-align:right; color:var(--chrome-pen); font-variant-numeric:tabular-nums}
.toc-t{flex:1; min-width:0; overflow-wrap:anywhere}
.toc-i[aria-current="true"]{background:rgba(246,166,90,.22); border-left-color:#F6A65A; font-weight:700}
.toc-i[aria-current="true"] .toc-n{color:inherit}
.toc-i:focus-visible,.toc-x:focus-visible{outline:3px solid #F6A65A; outline-offset:-3px}
@media (max-width:600px){
  .nav{gap:8px; padding-left:8px; padding-right:8px}
  .toc{left:0; right:0; bottom:0; transform:none; width:auto; max-height:min(82vh, calc(100vh - 24px - env(safe-area-inset-top,0px)));
    border-width:2px 0 0; border-radius:18px 18px 0 0; padding-bottom:env(safe-area-inset-bottom,0px);
    padding-left:env(safe-area-inset-left,0px); padding-right:env(safe-area-inset-right,0px)}
  .toc-i{min-height:44px; align-items:center; padding:8px 16px; font-size:18px}
  .toc-h{padding:14px 16px 4px}
  .toc-x{width:44px; height:44px}
}
@media (max-width:380px){ .toc-bl{display:none} #tocbtn{padding-left:11px; padding-right:11px} }
</style>'''

JS = r'''  /* jump menu (2026-11-19d) */
  function syncToc(){var a=document.querySelectorAll('#toc .toc-i');for(var k=0;k<a.length;k++){if(k===i)a[k].setAttribute('aria-current','true');else a[k].removeAttribute('aria-current');}}
  var toc=document.getElementById('toc'), tocbtn=document.getElementById('tocbtn'), scrim=document.getElementById('tocscrim');
  var items=[].slice.call(toc.querySelectorAll('.toc-i'));
  function tocOpen(){return !toc.hidden}
  function openToc(){toc.hidden=false; scrim.hidden=false; tocbtn.setAttribute('aria-expanded','true'); syncToc();
    var c=items[i]; if(c){c.scrollIntoView({block:'center'}); try{c.focus({preventScroll:true})}catch(e){c.focus()}}}
  function closeToc(back){if(!tocOpen())return; toc.hidden=true; scrim.hidden=true; tocbtn.setAttribute('aria-expanded','false'); if(back)tocbtn.focus();}
  tocbtn.addEventListener('click',function(e){e.stopPropagation(); if(tocOpen())closeToc(true); else openToc();});
  document.getElementById('tocx').addEventListener('click',function(){closeToc(true)});
  scrim.addEventListener('click',function(){closeToc(false)});
  document.addEventListener('click',function(e){if(tocOpen()&&!toc.contains(e.target)&&!tocbtn.contains(e.target))closeToc(false);});
  items.forEach(function(a,k){a.addEventListener('click',function(e){e.preventDefault(); show(k); closeToc(true);});});
  toc.addEventListener('keydown',function(e){
    var k=items.indexOf(document.activeElement);
    if(e.key==='Escape'){e.preventDefault(); closeToc(true);}
    else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault(); var n=k<0?i:Math.max(0,Math.min(items.length-1,k+(e.key==='ArrowDown'?1:-1))); items[n].focus(); items[n].scrollIntoView({block:'nearest'});}
    else if(e.key==='Home'||e.key==='End'){e.preventDefault(); var h=e.key==='Home'?0:items.length-1; items[h].focus(); items[h].scrollIntoView({block:'nearest'});}
    else if(e.key===' '&&k>=0){e.preventDefault(); items[k].click();}
    e.stopPropagation();});
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&tocOpen()){e.preventDefault(); closeToc(true);}
    else if((e.key==='c'||e.key==='C')&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&!tocOpen()){e.preventDefault(); openToc();}});
  ['touchstart','touchend'].forEach(function(t){toc.addEventListener(t,function(e){e.stopPropagation()},{passive:true});});
'''

NAV0 = '<nav class="nav" aria-label="Slide navigation"><button id="prev" type="button">'
SHOW0 = "try{history.replaceState(null,'','#s'+(i+1))}catch(e){}}"
INIT0 = "  var m=/^#s(\\d+)$/.exec(location.hash||''); show(m?parseInt(m[1],10)-1:0);"
for a in (NAV0, '</nav>', '</head>', SHOW0, INIT0):
    assert s.count(a) == 1, a
o = s.replace('</head>', CSS + '</head>', 1)
o = o.replace(NAV0, NAV0.replace('<button id="prev"', BTN + '<button id="prev"'), 1)
o = o.replace('</nav>', '</nav>' + PANEL, 1)
o = o.replace(SHOW0, SHOW0[:-1] + ' syncToc();}', 1)
o = o.replace(INIT0, JS + INIT0, 1)
assert [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', o, re.S)] == SL
vis = txt(re.sub(r'<script.*?</script>|<style.*?</style>', '', BTN + PANEL, flags=re.S))
assert not CJK.search(vis + CSS + JS)
OUT.write_text(o, encoding='utf-8')
rec = {'source': str(SRC), 'out': str(OUT), 'titles': {k + 1: t for k, t in enumerate(titles)}, 'title_source': {k + 1: h for k, h in enumerate(how)},
       'sections': [{'start': a + 1, 'name': n} for a, n in secs], 'content_changed': CHANGED, 'bytes_in': len(s.encode()), 'bytes_out': len(o.encode())}
(Path(__file__).parent / 'build_20261119d_menu.json').write_text(json.dumps(rec, indent=1, ensure_ascii=False))
print('ok', len(s), '->', len(o)); print(json.dumps(rec['sections']))
for k, t in enumerate(titles, 1): print(k, how[k - 1], t)
