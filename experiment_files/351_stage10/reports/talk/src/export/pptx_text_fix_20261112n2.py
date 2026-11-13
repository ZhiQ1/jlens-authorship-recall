"""2026-11-12 n (2): v21 pptx: X1 all-author R as main (slide 69) as deck HTML (sync_20261107/apply_20261112n2.py); notes = notes_zh.json (changed vs .before_20261112n2). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(69, 'R ≈ 0.99 (L24), 0.92 (L40), 0.42 (L48) whichever question the state came from', 'R ≈ 0.996 (L24), 0.933 (L40), 0.455 (L48) for all authors, whichever question the state came from (old first-author version: 0.99 / 0.92 / 0.42)')]
EQ = set()
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
hits = [0] * len(RULES)
for i, (sn, a, b) in enumerate(RULES):
    for p in paras(prs.slides[sn - 1].shapes):
        done = False
        for r in p.runs:
            if (i in EQ and r.text == a) or (i not in EQ and a in r.text): r.text = b if i in EQ else r.text.replace(a, b); hits[i] += 1; done = True
old = json.loads((E / 'notes_zh.json.before_20261112n2').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('rule hits', hits, '; notes replaced', nh, '; NOT replaced', nm)
