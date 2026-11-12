"""2026-11-12 l: v21 pptx: slide 81 status (2-11b verdict passes → C24; Patchscope descriptive), notes 75 / 81 = notes_zh.json (changed vs .before_20261112l). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(81, 'done, conclusion pending;', 'done: pre-registered verdict passes at all 7 layers (C24);'), (81, 'Patchscope (2-7, 2-9) done, results to be written (descriptive);', 'Patchscope (2-7, 2-9) done (descriptive only);')]
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
hits = [0] * len(RULES)
for i, (sn, a, b) in enumerate(RULES):
    for p in paras(prs.slides[sn - 1].shapes):
        done = False
        for r in p.runs:
            if a in r.text: r.text = r.text.replace(a, b); hits[i] += 1; done = True
        if not done and a in p.text and p.runs: p.runs[0].text = p.text.replace(a, b); [setattr(r, 'text', '') for r in p.runs[1:]]; hits[i] += 1
old = json.loads((E / 'notes_zh.json.before_20261112l').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('rule hits', hits, '; notes replaced', nh, '; NOT replaced', nm)
