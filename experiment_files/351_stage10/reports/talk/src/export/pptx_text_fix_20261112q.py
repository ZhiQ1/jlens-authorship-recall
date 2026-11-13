"""2026-11-12 q: v21 pptx as deck HTML (sync_20261107/apply_20261112q.py): slide 62 X1 step 4 + R table (all authors) + footnote, slide 63 X3 label + footnote,
slide 64 footnote (first author by design), slide 81 2-1 status (D12-5); notes = notes_zh.json (changed vs .before_20261112q). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
EQ = [(62, 'score first author', 'score all authors'), (62, 'R: Stage 13 X1, test set 582 papers; 381_stage13/reports/x1_report.md', 'R: Stage 13 X1, all authors (batch 1 item 1), test 582 papers; b1_xall_report.md (old first-author: 0.99 / 0.92 / 0.42)'),
      (63, 'first-author score, paraphrase − D: +0.239', 'all-author score, paraphrase − D: +0.229'),
      (63, '+0.239: Stage 13 X3 behaviour, test, 552 papers; x3_textbase_recovery.md', '+0.229: Stage 13 X3 behaviour, all authors (batch 1 item 1), test, 552 papers; b1_xall_report.md (old first-author: +0.239)'),
      (64, 'D: Stage 13 X4, test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; 381_stage13/reports/x4_report.md', 'D: Stage 13 X4 (prompt asks for the first author by design), test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; x4_report.md')]
SUB = [(81, '2-1 stopped (D12-1, user to decide);', '2-1: deviation D12-5 (gate reference computed in the wrong precision, f64 vs the fp32 log; not a relaxed criterion); gate fixed to fp32 vs fp32 and resumed, gate v4 queued;')]
hits = {}
for sn, a, b in EQ:
    for p in paras(prs.slides[sn - 1].shapes):
        for r in p.runs:
            if r.text == a: r.text = b; hits[a[:30]] = hits.get(a[:30], 0) + 1
for sn, a, b in SUB:
    for p in paras(prs.slides[sn - 1].shapes):
        for r in p.runs:
            if a in r.text: r.text = r.text.replace(a, b); hits[a[:30]] = hits.get(a[:30], 0) + 1
OLD = ['0.99', '0.98', '0.99', '0.92', '0.92', '0.92', '0.42', '0.41', '0.42']; NEW = ['0.996', '0.990', '0.992', '0.933', '0.928', '0.929', '0.455', '0.431', '0.444']
runs = [r for p in paras(prs.slides[61].shapes) for r in p.runs]
start = [i for i, r in enumerate(runs) if r.text == 'R from']; k = 0
for r in runs[start[0]:] if start else []:
    if k < 9 and r.text == OLD[k]: r.text = NEW[k]; k += 1
old = json.loads((E / 'notes_zh.json.before_20261112q').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for kk in new:
    if new[kk]['text'] == old[kk]['text']: continue
    ps = [p for p in prs.slides[int(kk) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[kk]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[kk]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(kk)
    else: nm.append(kk)
prs.save(sys.argv[2]); print('hits', hits, '; R cells', k, '/ 9 ; notes replaced', nh, '; NOT replaced', nm)
