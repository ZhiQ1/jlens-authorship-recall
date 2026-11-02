"""2026-11-02 final deck edits: slide 52 (limits) image from build.py, slide 47 note, two new Stage 12-13 slides before the wrap-up."""
import re, base64, io
from pathlib import Path
from PIL import Image
SP = Path('/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad')
SRC = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.before_20261102.html')
DST = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
h = SRC.read_text()
head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
# last section ends before '\n</div>\n<nav'
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 52, len(secs)

def jpg(path, q=90):
    b = io.BytesIO(); Image.open(path).convert('RGB').save(b, 'JPEG', quality=q); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
def png(path):
    im = Image.open(path)
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

# slide 52: limits, rebuilt from build.py (deck page 15)
s52 = secs[51]; assert 'Stage 10-11 slide 15' in s52
secs[51] = re.sub(r'src="data:image/jpeg;base64,[^"]+"', 'src="' + jpg(SP / 'deckbuild/p15.png') + '"', s52)
# slide 47: P1 is done
old = 'Stage 12 P1 now patches single tail positions.'
assert secs[46].count(old) == 1
secs[46] = secs[46].replace(old, 'Stage 12 P1 (done) patched single positions: the name positions carry the signal (+0.85 at L52), the colon alone little (+0.17).')

HYP = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/Stage13_hypotheses_table_v23_tableonly.png'
X5 = '/scratch/zhang.zhiqi2/jlens/381_stage13/reports/x5_layer_order.png'
new_a = f'''<section class="slide lt" aria-label="Stage 12-13 hypotheses"><span class="tag">Stage 12–13</span>
<h2>Stage 12–13: what the middle layers hold</h2>
<p class="sub" style="margin-bottom:20px">Paper facts are readable at the title early (M2), but neither paper identity (H2) nor hidden author knowledge (H3) is established</p>
<div style="width:1030px;margin:0 auto"><figure class="card" style="transform:rotate(-0.4deg)"><img alt="Hypotheses H1–H3 against readouts M1–M3 and the current results" src="{png(HYP)}"><figcaption>Hypotheses H1–H3 × readouts M1–M3 and current results (report, 2026-11-01)</figcaption></figure></div>
<span class="pg"></span></section>'''
new_b = f'''<section class="slide lt" aria-label="Stage 13 X5 layer order"><span class="tag">Stage 13 · X5</span>
<h2>Layer order (X5)</h2>
<p class="sub" style="margin-bottom:12px">Earliest layer at which each kind of information appears · existing results only, each source keeps its own rule</p>
<div class="row" style="gap:22px;align-items:flex-start"><div style="width:880px;flex:none"><figure class="card" style="transform:rotate(0.4deg)"><img alt="Stage 13 X5: earliest layer per readout" src="{png(X5)}"></figure></div>
<div class="note" style="flex:1;font-size:18px;line-height:1.35;padding:14px 16px;margin-top:20px;transform:rotate(1.2deg)"><span class="h" style="font-size:20px">Read early, carried, spoken late</span><b>≤L8–L16</b>: title facts and the first-author token<br><br><b>L48–L52</b>: the paper signal reaches the post-title tail (patching R ≥ 0.5 at L48, ≥ 0.95 at L52; knockout costs nothing from L52)<br><br><b>L53–L62</b>: names readable by lens</div></div>
<span class="pg"></span></section>'''
secs = secs[:50] + [new_a, new_b] + secs[50:]
assert len(secs) == 54
out = head + ''.join(secs) + tail
DST.write_text(out); print('wrote', DST, len(out) // 1024, 'KB', 'sections', out.count('<section class="slide'))
