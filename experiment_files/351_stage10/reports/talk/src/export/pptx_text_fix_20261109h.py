"""2026-11-09 h: v21 pptx: H3 'partly supported' (slides 65, 70, 81 as deck HTML, apply_20261109h.py), slide-65 table image = Stage13_hypotheses_table_v30_en_tableonly.png (regenerated),
batch-2 status (slide 81), notes = notes_zh.json (changed vs .before_20261109h2). usage: IN OUT"""
import sys, json, shutil, io
from pathlib import Path
from pptx import Presentation
from PIL import Image
E = Path(__file__).parent; D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads'); shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(65, 'H3 (hidden author knowledge): insufficient evidence · X2 (2026-11-05): H2 not supported; H3 passes by rule but the author subspace can hardly decode authors (held-out R² ≤ 0.009) → still insufficient',
          'H3 (hidden author knowledge): partly supported (name-position probe, addendum 11: criterion met for the surname at L40/L48, but lens intervals also exclude 0) · X2 alone: H2 not supported; author subspace can hardly decode authors (R² ≤ 0.009)'),
         (70, 'H3: insufficient evidence (text baseline not weaker than Qwen).', 'H3: partly supported by the name-position probe (addendum 11); X4 alone cannot exclude the title text.'),
         (81, 'subspace R² ≤ 0.009, H3 still insufficient)', 'subspace R² ≤ 0.009, X2 alone leaves H3 insufficient)'),
         (81, 'shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis running;',
          'shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis running;')]
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
hits = [0] * len(RULES)
for i, (sn, a, b) in enumerate(RULES):
    for p in paras(prs.slides[sn - 1].shapes):
        for r in p.runs:
            if a in r.text: r.text = r.text.replace(a, b); hits[i] += 1
        if not hits[i] and a in p.text and p.runs:        # string split over runs: put it into the first run
            t = p.text.replace(a, b); p.runs[0].text = t; [setattr(r, 'text', '') for r in p.runs[1:]]; hits[i] += 1
img = (D / 'Stage13_hypotheses_table_v30_en_tableonly.png').read_bytes(); n65 = 0
for sh in prs.slides[64].shapes:
    if sh.shape_type == 13 and sh.name.startswith('chart image'):
        prs.slides[64].part.related_part(sh._element.blipFill.blip.rEmbed)._blob = img; w, h = Image.open(io.BytesIO(img)).size; sh.height = int(sh.width * h / w); n65 += 1
old = json.loads((E / 'notes_zh.json.before_20261109h2').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('rule hits', hits, '; slide 65 image', n65, '; notes replaced', nh, '; NOT replaced', nm)
