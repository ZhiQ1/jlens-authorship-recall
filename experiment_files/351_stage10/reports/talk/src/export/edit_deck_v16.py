"""2026-11-04 deck v16 (user-approved): slide 54 title 'Limits' (image from build.py p15), slide 50 lens-stability row."""
import re, base64, io, sys
from pathlib import Path
from PIL import Image
BUILD = Path(sys.argv[1])
SRC = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.before_20261104.html')
DST = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
h = SRC.read_text()
head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 54
b = io.BytesIO(); Image.open(BUILD / 'p15.png').convert('RGB').save(b, 'JPEG', quality=90)
assert 'alt="Stage 10-11 slide 15"' in secs[53]
secs[53] = re.sub(r'src="data:image/jpeg;base64,[^"]+"', 'src="data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode() + '"', secs[53])
a = '<td>three Jacobian lenses agree</td>'; assert secs[49].count(a) == 1
secs[49] = secs[49].replace(a, '<td>three Jacobian lenses fitted on different text agree; fit stability rests on Stage 9 Fit A only</td>')
out = head + ''.join(secs) + tail; DST.write_text(out); print('wrote', DST, out.count('<section class="slide'))
