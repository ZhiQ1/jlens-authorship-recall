"""Check that the coverage boxes did not overlap anything: base vs cov render must be identical outside the box rects."""
import json, numpy as np
from PIL import Image
W = '/home/zhang.zhiqi2/jlens_work/27_v67/'
B = json.load(open(W + 'coverage_boxes.json'))
bad = []
for k, bx in sorted(B.items(), key=lambda x: int(x[0])):
    n = int(k)
    a = np.asarray(Image.open(W + f'render/base/s{n:03d}.png').convert('RGB')).astype(int)[:720, :1280]
    b = np.asarray(Image.open(W + f'render/cov/s{n:03d}.png').convert('RGB')).astype(int)[:720, :1280]
    d = np.abs(a - b).sum(2) > 30
    m = np.zeros_like(d)
    for kind, r in bx:
        m[max(0, r['y'] - 6):r['y'] + r['h'] + 6, max(0, r['x'] - 6):r['x'] + r['w'] + 6] = True
    out = d & ~m
    if out.sum() > 20:
        ys, xs = np.where(out)
        bad.append((n, int(out.sum()), int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
    # content under the box (box drawn over busy pixels)
    under = (np.abs(a - np.median(a.reshape(-1, 3), 0)).sum(2) > 75) & m
print('pages checked', len(B), 'spill outside boxes:', bad)
