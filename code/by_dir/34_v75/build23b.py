"""2026-11-25 coordinator: main pptx v23a -> v23b (user): restore the not-in-data chance markers removed in v23a — S132 #2066 (triangle)
+ #2067 (line), S133 #73 (tick) — copied back from v22z at their original z-order. Text changes of v23a stay."""
import copy, json
from pptx import Presentation
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
old = Presentation(D + 'jlens_1113_pre_v22z.pptx'); new = Presentation(D + 'jlens_1113_pre_v23a.pptx')
restored = []
for si, sids in ((131, [2066, 2067]), (132, [73])):
    so, sn = old.slides[si], new.slides[si]
    otree = so.shapes._spTree; ntree = sn.shapes._spTree
    oids = [x.shape_id for x in so.shapes]
    for sid in sids:
        el = next(x for x in so.shapes if x.shape_id == sid)._element
        assert all(x.shape_id != sid for x in sn.shapes)
        # insert after the nearest preceding shape (in v22z order) that still exists in v23a
        prev = [p for p in oids[:oids.index(sid)] if any(x.shape_id == p for x in sn.shapes)][-1]
        pel = next(x for x in sn.shapes if x.shape_id == prev)._element
        pel.addnext(copy.deepcopy(el)); restored.append([si + 1, sid, 'after', prev])
    sn.notes_slide.notes_text_frame.add_paragraph().add_run().text = '[2026-11-25 v23b] chance marker of the not-in-data bar restored (user): it is the reading baseline of the chart.'
new.save(D + 'jlens_1113_pre_v23b.pptx')
json.dump({'edited': [], 'added': [[r[0], r[1]] for r in restored], 'deleted': [], 'notes': [132, 133], 'notes_prefix': '[2026-11-25 v23b] ', 'new_slides': [], 'deleted_slides': [], 'user_authorised': [], 'order': list(range(1, 193))},
          open(D + 'jlens_1113_pre_v23b.pptx.allow.json', 'w'))
print('ok', restored)
