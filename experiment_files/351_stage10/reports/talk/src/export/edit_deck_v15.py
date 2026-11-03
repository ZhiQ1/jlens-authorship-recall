"""2026-11-03 deck v15 (user-approved wording): slides 38/54 images from build.py, 40/48/50/51 text."""
import re, base64, io, sys
from pathlib import Path
from PIL import Image
BUILD = Path(sys.argv[1])  # folder with p10.png, p15.png rendered from the current build.py
SRC = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.before_20261103.html')
DST = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
h = SRC.read_text()
head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 54
def jpg(p):
    b = io.BytesIO(); Image.open(p).convert('RGB').save(b, 'JPEG', quality=90); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
for k, alt, png in [(38, 'Stage 10-11 slide 10', 'p10.png'), (54, 'Stage 10-11 slide 15', 'p15.png')]:
    assert f'alt="{alt}"' in secs[k - 1]; secs[k - 1] = re.sub(r'src="data:image/jpeg;base64,[^"]+"', 'src="' + jpg(BUILD / png) + '"', secs[k - 1])
def rep(k, a, b):
    assert secs[k - 1].count(a) == 1, (k, a); secs[k - 1] = secs[k - 1].replace(a, b)
rep(40, 'Depends on name format; routed through the tokens right after the title; co-authors partly replace the title',
        'Depends on name format; the information enters the name positions at L44–52, partly via the tokens right after the title; co-authors partly replace the title')
rep(48, 'Middle layers may hold the task or the paper’s identity, which rank-based lenses cannot score.',
        'Stage 13: \':\' and name positions hold the task; the title position holds paper attributes and meaning beyond the words, not shown to be paper identity.')
rep(50, '<td class="r">still to verify</td>', '<td class="r">only one piece of evidence (Stage 9 Fit A); Fit B not completed</td>')
rep(51, 'Paper facts are readable at the title early (M2), but neither paper identity (H2) nor hidden author knowledge (H3) is established',
        'Paper facts are readable at the title early (M2) · H2 (paper identity) partly supported but not established; H3 (hidden author knowledge): insufficient evidence')
rep(51, '<p class="sub" style="margin-bottom:20px">', '<p class="sub" style="margin-bottom:16px">')
rep(51, '<div style="width:1030px;margin:0 auto">', '<div style="width:990px;margin:0 auto">')
out = head + ''.join(secs) + tail; DST.write_text(out); print('wrote', DST, out.count('<section class="slide'))
