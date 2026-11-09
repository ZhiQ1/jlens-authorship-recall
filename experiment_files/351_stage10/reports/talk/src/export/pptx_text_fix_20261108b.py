"""2026-11-08 b: copy of v20g pptx -> v20h with today's decisions: 187/194 clause deleted, D13-1 sentence removed from notes (held to next batch), D14-1 locked path.
usage: pptx_text_fix_20261108b.py IN OUT"""
import sys, re, shutil
from pptx import Presentation
shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(' — 187 / 194 units done, result pending; result after approval', ' — result after approval'),
         ('187 / 194 units done, result pending', ''),
         ('194 个单元已完成 187 个，结果尚未出来，', ''),
         ('381_stage13/b3_33_v2/prereg_addendum14_deviations_DRAFT.json', '381_stage13/config/prereg_addendum14_deviations.json')]
RX = [re.compile(r'Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1〔[^〕]*〕）。')]
def runs(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from runs(sh.shapes)
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs: yield from para.runs
        if getattr(sh, 'has_table', False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for para in c.text_frame.paragraphs: yield from para.runs
hits = {}
for i, s in enumerate(prs.slides, 1):
    rs = list(runs(s.shapes))
    if s.has_notes_slide: rs += list(runs(s.notes_slide.shapes))
    for r in rs:
        for a, b in RULES:
            if a in r.text: r.text = r.text.replace(a, b); hits.setdefault(a, []).append(i)
        for rx in RX:
            if rx.search(r.text): r.text = rx.sub('', r.text); hits.setdefault(rx.pattern, []).append(i)
prs.save(sys.argv[2])
left = []
for i, s in enumerate(prs.slides, 1):
    txt = ' '.join(r.text for r in runs(s.shapes)) + (' '.join(r.text for r in runs(s.notes_slide.shapes)) if s.has_notes_slide else '')
    for k in ['187 /', '187 个', 'D13-1', 'DRAFT.json', 'pending confirmation', '待确认）']:
        if k in txt: left.append((i, k))
print('hits', hits); print('LEFT', left)
