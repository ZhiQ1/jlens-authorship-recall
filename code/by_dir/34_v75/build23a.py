"""2026-11-25 coordinator: main pptx v22z -> v23a (= HTML v76): S132 bar label '50.4%  (chance 50.5%)' -> '50.4%', that bar's chance marker
(#2066 triangle, #2067 line) deleted, Result #2115 reworded; S133 (pptx-only) '50.4% (chance 50.5%)' -> '50.4%', its tick #73 deleted.
User-approved 2026-11-25 (same reason as the deleted sticky note)."""
import json
from pptx import Presentation
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
IN_, OUT = D + 'jlens_1113_pre_v22z.pptx', D + 'jlens_1113_pre_v23a.pptx'
PFX = '[2026-11-25 v23a] '
prs = Presentation(IN_); SL = list(prs.slides); assert len(SL) == 192
U = Presentation(D + 'stage1-13 超长卷.pptx')
def ups(s): return {x.shape_id for su in U.slides if su.slide_id == s.slide_id for x in su.shapes}
def sh(s, sid): return next(x for x in s.shapes if x.shape_id == sid)
edited, deleted = [], []
def settext(s, sid, old, new):
    x = sh(s, sid); assert sid not in ups(s)
    rs = [r for p in x.text_frame.paragraphs for r in p.runs]; hit = [r for r in rs if old in r.text]; assert len(hit) == 1, (sid, old)
    hit[0].text = hit[0].text.replace(old, new); edited.append([SL.index(s) + 1, sid])
def delete(s, sid):
    x = sh(s, sid); assert sid not in ups(s); x._element.getparent().remove(x._element); deleted.append([SL.index(s) + 1, sid])
s = SL[131]
settext(s, 2068, '50.4%  (chance 50.5%)', '50.4%')
delete(s, 2066); delete(s, 2067)
x = sh(s, 2115); rs = [r for p in x.text_frame.paragraphs for r in p.runs]
r1 = next(r for r in rs if r.text == ' about half are not in the data, '); r2 = next(r for r in rs if r.text == 'the same as the shuffled baseline (50.4% vs 50.5%)')
r1.text = ' '; r2.text = 'about half (50.4%) are not in the data'
r3 = rs[rs.index(r2) + 1]; assert r3.text == ';'; r3.text = ' (in none of the cohort’s author lists);'
edited.append([132, 2115])
s3 = SL[132]
settext(s3, 74, '50.4% (chance 50.5%)', '50.4%')
delete(s3, 73)
for s_ in (s, s3):
    s_.notes_slide.notes_text_frame.add_paragraph().add_run().text = PFX + 'not-in-data chance comparison (50.4% vs 50.5%) removed: equal by construction (user-approved 2026-11-25).'
prs.save(OUT)
json.dump({'edited': edited, 'added': [], 'deleted': deleted, 'notes': [132, 133], 'notes_prefix': PFX, 'new_slides': [], 'deleted_slides': [],
           'user_authorised': [d + ['user 2026-11-25: remove the 50.4% vs 50.5% comparison'] for d in deleted], 'order': list(range(1, 193))},
          open(OUT + '.allow.json', 'w'), ensure_ascii=False)
print('ok', edited, deleted)
