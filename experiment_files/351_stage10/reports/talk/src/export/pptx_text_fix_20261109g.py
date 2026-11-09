"""2026-11-09 g: v21 pptx: slide 81 batch-2 status (as deck HTML, apply_20261109g.py) + notes = notes_zh.json (changed vs .before_20261109g). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
OLD = '2-11b (addendum 15), shard 0 only, queued; other items in progress;'
NEW = ('2-11b (addendum 15): shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis running; '
       '2-1 gate re-run (job killed by the cluster epilog, watchdog added); other items in progress;')
hit = 0
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
for p in paras(prs.slides[80].shapes):
    for r in p.runs:
        if OLD in r.text: r.text = r.text.replace(OLD, NEW); hit += 1
old = json.loads((E / 'notes_zh.json.before_20261109g').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('slide 81 hit', hit, '; notes replaced', nh, '; NOT replaced', nm)
