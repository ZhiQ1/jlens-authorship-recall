"""After integrate.py: (1) rewrite lead-line pointers that no longer point at the real neighbour; (2) apply the box moves in move_plan.json."""
import re, json
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
D = W + 'deck_v67_full.html'
t = open(D, encoding='utf-8').read()
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
out, last, cnt = [], 0, 0
for i, m in enumerate(ms, 1):
    s = m.group(0)
    def fixlead(L):
        global cnt
        inner = L.group(2)
        def back(a):
            global cnt
            if int(a.group(3)) != i - 1: cnt += 1; return 'see ' + a.group(2) + a.group(3)
            return a.group(0)
        def fwd(a):
            global cnt
            if int(a.group(3)) != i + 1: cnt += 1; return '· see' + a.group(1) + a.group(2) + a.group(3)
            return a.group(0)
        inner = re.sub(r'←(\s*)(slides?\s*)(\d+)', back, inner)
        inner = re.sub(r'→([^←→<]{0,80}?)(slides?\s*)(\d+)', fwd, inner)
        inner = re.sub(r'^see ', 'See ', inner)
        return L.group(1) + inner + L.group(3)
    s = re.sub(r'(<div class="lead"[^>]*>)(.*?)(</div>)', fixlead, s, flags=re.S)
    out.append(t[last:m.start()]); out.append(s); last = m.end()
out.append(t[last:]); t = ''.join(out)
plan = json.load(open(W + 'move_plan.json'))
ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
moved = 0
for key, (r, b, o, sm) in plan.items():
    if not b: continue
    n, kind = key.split('|'); n = int(n); cls = {'now': 'covna', 'so': 'covso', 'tag': 'covtg'}[kind]
    s = ms[n - 1].group(0)
    mm = re.search(r'<(p|div) class="[^"]*%s[^"]*" style="([^"]*)"' % cls, s); st = mm.group(2)
    st2 = re.sub(r'left:\d+px', f'left:{b["x"]}px', st); st2 = re.sub(r'top:\d+px', f'top:{b["y"]}px', st2)
    st2 = re.sub(r'width:\d+px', f'width:{b["w"]}px', st2); st2 = re.sub(r'font-size:[\d.]+px', f'font-size:{b["fs"]}px', st2)
    t = t.replace(s, s.replace(st, st2, 1), 1); moved += 1
    ms = list(re.finditer(r'<section class="slide[^"]*"[^>]*>.*?</section>', t, flags=re.S))
open(D, 'w', encoding='utf-8').write(t)
print('lead pointers rewritten', cnt, 'boxes moved', moved)
