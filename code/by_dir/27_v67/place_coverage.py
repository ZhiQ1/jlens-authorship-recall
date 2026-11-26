"""Place the missing Now asking / So / evidence-tag boxes on v67 pages into free space found on the base render.
usage: place_coverage.py  (reads render/base/sNNN.png, deck_v67.html, coverage_lines.py) -> deck_v67.html, coverage_boxes.json"""
import re, json, sys, html
import numpy as np
from PIL import Image
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
sys.path.insert(0, W); sys.path.insert(0, '/home/zhang.zhiqi2/jlens_work/tools')
from coverage_lines_v66 import C66
ORDER = json.load(open(W + 'order_v67.json'))
C = {i + 1: C66[o[1]] for i, o in enumerate(ORDER) if o[0] == 'old' and o[1] in C66}
OLD = json.load(open(W + 'order_v67_phase1a.json'))
POS1A = {(o[0], o[1]): i + 1 for i, o in enumerate(OLD)}
from prepublish_check import page_features
TAGLAB = {}
D = W + 'deck_v67.html'
t = open(D, encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))

def busy(n):
    n1a = POS1A[tuple(ORDER[n - 1][:2])]
    a = np.asarray(Image.open(W + f'render/base/s{n1a:03d}.png').convert('RGB')).astype(int)
    a = a[:720, :1280]
    flat = a.reshape(-1, 3)
    vals, cnt = np.unique(flat[::7], axis=0, return_counts=True)
    bg = vals[cnt.argmax()]
    m = np.abs(a - bg).sum(2) > 75
    # dilate 7 px
    from scipy.ndimage import binary_dilation
    m = binary_dilation(m, iterations=7)
    m[690:, 1150:] = True   # page number
    return m, bg

def est(text, fs, w):
    cw = 0.50 * fs
    lines = max(1, -(-int(len(text) * cw) // (w - 20)))
    return int(lines * fs * 1.25 + 10)

def find(m, w, h, ys, prefer):
    cs = np.cumsum(np.cumsum(m, 0), 1)
    def free(x, y):
        x2, y2 = x + w - 1, y + h - 1
        s = cs[y2, x2] - (cs[y - 1, x2] if y else 0) - (cs[y2, x - 1] if x else 0) + (cs[y - 1, x - 1] if x and y else 0)
        return s == 0
    yr = list(range(ys[0], ys[1] - h + 1, 4))
    if prefer == 'bottom': yr = yr[::-1]
    for y in yr:
        for x in range(40, 1280 - w - 30, 8):
            if free(x, y): return x, y
    return None

def place(m, text, kind):
    region = (34, 250) if kind == 'now' else (430, 712)
    pref = 'top' if kind == 'now' else 'bottom'
    for reg in (region, (34, 712)):
        for fs in (15, 13.5, 12, 11):
            for w in (900, 760, 640, 540, 440, 360, 300, 240):
                h = est(text, fs, w)
                r = find(m, w, h, reg, pref)
                if r:
                    x, y = r; m[y:y + h, x:x + w] = True
                    return dict(x=x, y=y, w=w, h=h, fs=fs)
    return None

boxes, fail = {}, []
new = []
last = 0
for i, mm in enumerate(ms, 1):
    s = mm.group(0)
    new.append(t[last:mm.start()]); last = mm.end()
    if i not in C:
        new.append(s); continue
    f = page_features(s); spec = C[i]
    m, bg = busy(i)
    dark = bg.mean() < 110
    add = []
    if not f['now'] and spec.get('now'):
        b = place(m, 'Now asking: ' + spec['now'], 'now')
        if not b: fail.append((i, 'now'))
        else:
            add.append(f'<p class="covna" style="position:absolute;z-index:7;left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;margin:0;'
                       f'font-family:var(--hand);font-size:{b["fs"]}px;line-height:1.25;color:#22304A;background:rgba(255,255,255,.9);'
                       f'border-radius:6px;padding:3px 9px;box-sizing:border-box"><b>Now asking:</b> {html.escape(spec["now"])}</p>')
            boxes.setdefault(i, []).append(('now', b))
    need_so = not f['so'] and spec.get('so'); need_tag = not f['tag'] and spec.get('tag')
    if need_so:
        tg = f' <span class="tg {spec["tag"][0]}">{html.escape(spec["tag"][1])}</span>' if need_tag else ''
        lab = 'So (section):' if spec.get('sec') else 'So (this slide):'
        txt = f'{lab} {spec["so"]}' + (' ' + spec['tag'][1] if need_tag else '')
        b = place(m, txt + '  ', 'so')
        if not b: fail.append((i, 'so'))
        else:
            add.append(f'<div class="soln covso" style="left:{b["x"]}px;top:{b["y"]}px;width:{b["w"]}px;font-size:{b["fs"]}px;box-sizing:border-box;z-index:7">'
                       f'<b>{lab}</b> {html.escape(spec["so"])}{tg}</div>')
            boxes.setdefault(i, []).append(('so', b))
    elif need_tag:
        txt = 'Evidence: ' + spec['tag'][1]
        b = place(m, txt + '      ', 'so')
        if not b: fail.append((i, 'tag'))
        else:
            add.append(f'<div class="note-h covtg" style="left:{b["x"]}px;top:{b["y"]}px;z-index:7">Evidence: <span class="tg {spec["tag"][0]}">{html.escape(spec["tag"][1])}</span></div>')
            boxes.setdefault(i, []).append(('tag', b))
    if add:
        s = s[:-len('</section>')] + ''.join(add) + '</section>'
    new.append(s)
new.append(t[last:])
open(D, 'w', encoding='utf-8').write(''.join(new))
json.dump({str(k): v for k, v in boxes.items()}, open(W + 'coverage_boxes.json', 'w'), indent=0)
print('pages with boxes', len(boxes), 'failed', fail)
