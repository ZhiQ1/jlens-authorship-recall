"""Round r, fragment b (reduced scope per coordinator): slide 65 only. Keeps the original table image and overlays a white patch
on the image's header cell "Current result (report v30, 2026-11-08)" -> "Current result (report v41, 2026-11-12)";
figcaption date updated the same way. Header box located in the 2760x2052 image: x 1890..2740, y 15..75 px."""
import re, json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); OUT = R / 'sync_20261107/r_frag'
h = (R / 'merged_deck/stage1_11_deck.html').read_text(encoding='utf-8')
st = [m.start() for m in re.finditer(r'<section[^>]*class="[^"]*slide', h)]
s = h[st[64]:st[65]]; assert 'aria-label="Stage 12-13 hypotheses"' in s
W, H = 2760, 2052; x0, y0, x1, y1 = 1890, 12, 2750, 78
img_open = s.index('<img alt="Hypotheses'); img_end = s.index('>', img_open) + 1
patch = (f'<div style="position:absolute;left:{x0 / W * 100:.2f}%;top:{y0 / H * 100:.2f}%;width:{(x1 - x0) / W * 100:.2f}%;height:{(y1 - y0) / H * 100:.2f}%;'
         'background:#fff;display:flex;align-items:center;font-family:\'Source Sans 3\',\'Noto Sans SC\',system-ui,sans-serif;font-weight:700;font-size:12px;color:#1a1a1a;padding-left:2px;white-space:nowrap">'
         'Current result (report v41, 2026-11-12)</div>')
new = s[:img_open] + '<div style="position:relative">' + s[img_open:img_end] + patch + '</div>' + s[img_end:]
a, b = 'current results (report v30, 2026-11-08)', 'current results (report v41, 2026-11-12)'
assert new.count(a) == 1; new = new.replace(a, b)
(OUT / 'slide65.html').write_text(new, encoding='utf-8')
(OUT / 'slide65.json').write_text(json.dumps({'aria': 'Stage 12-13 hypotheses', 'note_append': '',
    'manifest': [['slide 65 image header "Current result (report v30, 2026-11-08)"', 'overlay "Current result (report v41, 2026-11-12)" (image kept)'], ['slide 65 figcaption ' + a, b]],
    'sources': ['header text only; no numbers changed']}, ensure_ascii=False, indent=1), encoding='utf-8')
print('ok', len(new))
