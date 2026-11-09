"""2026-11-08 d (round d after checks): v21 pptx -> v21 with the deck HTML changes of sync_20261107/apply_20261108d.py (slides 77, 81, 82; notes 72, 81, 82).
usage: pptx_text_fix_20261108d.py IN OUT"""
import sys, json, shutil, copy
from pathlib import Path
from pptx import Presentation
from pptx.text.text import _Paragraph
E = Path(__file__).parent
shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
        if getattr(sh, 'has_table', False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells: yield from c.text_frame.paragraphs
RULES = [(77, 'within bin same timing as A, larger gap', 'within bin (258 of 462 C papers, 6 bins) same timing as A, larger gap'),
         (81, 'colon numerator B/A 0.72–0.87 (b1_p12f_report.md)', 'colon numerator B/A 0.72–0.87; p9: 694–711 papers per false title, different sets, unweighted (b1_p12f_report.md)'),
         (81, '(C 462 papers: same timing as A)', '(C 462 papers; within bin 258 of 462 vs A: same timing)'),
         (82, 'last two items added', 'last three items added'),
         (82, 'parity tolerance 0.25 → 0.5 was used (Stage 10 main round, max 0.367);', 'parity tolerance 0.25 → 0.5 was used, a post-hoc change (main round: 10 of 25 pairs above 0.25, max 0.367; size matches bf16 rounding, up to ~0.46);')]
hits = [0] * len(RULES)
for si, s in enumerate(prs.slides, 1):
    for p in paras(s.shapes):
        for r in p.runs:
            for i, (sn, a, b) in enumerate(RULES):
                if sn == si and a in r.text: r.text = r.text.replace(a, b); hits[i] += 1
last = [p for p in paras(prs.slides[81].shapes) if p.text.startswith('•  Post hoc and single title')]
if len(last) == 1:
    new = copy.deepcopy(last[0]._p); last[0]._p.addnext(new); rs = _Paragraph(new, last[0]._parent).runs
    rs[0].text = '•  '; rs[1].text = 'Layer gap, stopped item: '
    rs[2].text = 'X4 year onset somewhere in L33–L40; Jacobian vs logit jump between L32 and L40; X4 first-author peak could be L33–L47 · 2-11 stopped (first-name reproduction 0.880 < 0.90)'
    for r in rs[3:]: r.text = ''
old = json.loads((E / 'notes_zh.json.before_20261108d').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2])
print('rule hits', hits, '; bullet added', len(last), '; notes replaced', nh, '; NOT replaced', nm)
