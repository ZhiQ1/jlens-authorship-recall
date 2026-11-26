"""2026-11-25 coordinator: main pptx v22x -> v22y: S166 (= HTML v73/v74 158) So line in our own shape reworded to known gap ① (same as the image)."""
import json, re
from pptx import Presentation
D='/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
IN_, OUT = D+'jlens_1113_pre_v22x.pptx', D+'jlens_1113_pre_v22y.pptx'
PFX='[2026-11-25 v22y] '
OLD='each step hands one question to the next; two links are still broken: where “who wrote this paper” enters, and recognition measured inside the multiple-choice prompt.'
NEW='Gap ①: where “who wrote this paper” enters — do the late MLPs hold this paper’s author knowledge? Not tested yet.'
prs=Presentation(IN_); SL=list(prs.slides); assert len(SL)==192
U=Presentation(D+'stage1-13 超长卷.pptx'); ups={x.shape_id for su in U.slides if su.slide_id==SL[165].slide_id for x in su.shapes}
s=SL[165]; hit=[]
for sh in s.shapes:
    if sh.has_text_frame and OLD in sh.text_frame.text:
        assert sh.shape_id not in ups
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if OLD.strip() in r.text: r.text=r.text.replace(OLD.strip(),NEW); hit.append(sh.shape_id)
assert len(hit)==1, hit
s.notes_slide.notes_text_frame.add_paragraph().add_run().text=PFX+'So line reworded to known gap ① (same as the image), coordinator 2026-11-25.'
prs.save(OUT)
json.dump({'edited':[[166,hit[0]]],'added':[],'deleted':[],'notes':[166],'notes_prefix':PFX,'new_slides':[],'deleted_slides':[],'user_authorised':[],'order':list(range(1,193))},open(OUT+'.allow.json','w'))
print('ok',hit)
