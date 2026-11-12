"""2026-11-12 i: v21 pptx: slide 81 status (2-2, 2-7/2-9, 2-11b done; 2-1 stopped; 3-1 done, 3-2 194/504), slide 82 (L41–L47, L49 filled by 3-1),
notes = notes_zh.json (changed vs .before_20261112i). As deck HTML (sync_20261107/apply_20261112i.py). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(81, 'shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis running; 2-1 gate re-run (job killed by the cluster epilog, watchdog added); other items in progress;',
          'done, conclusion pending; 2-2, 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9) done, results to be written (descriptive); 2-1 stopped (D12-1, user to decide);'),
         (81, '3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: queued, start after batch 2', '3-1 Stage 10 L41–L47, L49: done · 3-2 L0–L23: running (194/504)'),
         (82, '(no L25–L31, L33–L39; no plan to fill)', '(no L25–L31, L33–L39; no plan to fill; L41–L47, L49 filled by 3-1)')]
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
old = json.loads((E / 'notes_zh.json.before_20261112i').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('rule hits', hits, '; notes replaced', nh, '; NOT replaced', nm)
