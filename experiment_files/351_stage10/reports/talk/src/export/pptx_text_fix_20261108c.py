"""2026-11-08 c: copy of the v20h pptx -> v21 with the same text changes as the deck HTML (sync_20261107/apply_20261108c.py, _part2.py):
slide 19 (Stage 8: int6 is not the locked endpoint, D13-1, three premises), 65 (caption v30 + image = Stage13_hypotheses_table_v30_en_tableonly.png),
70 (X4 recognition gap not H2 evidence), 75 (agenda status), 77 (C row 462 papers, footer), 79 (colon B/A five titles), 81 (status 2026-11-08),
82 (two limitation bullets added, cloned from the last bullet); speaker notes = notes_zh.json (changed notes replaced as whole paragraphs).
usage: pptx_text_fix_20261108c.py IN OUT"""
import sys, json, shutil, copy
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads')
shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame:
            yield from sh.text_frame.paragraphs
        if getattr(sh, 'has_table', False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells: yield from c.text_frame.paragraphs
# (slide, old, new, mode) mode 'sub' = substring in a run, 'eq' = whole run text equal
RULES = [
 (19, 'Stage 8 frozen endpoint, re-scored on CPU', 'Stage 8 re-scored on CPU: three premises', 'eq'),
 (19, 'Multi-layer endpoint: ', '6-layer mean (int6, no L16): ', 'eq'),
 (19, '→ both hold', '→ both positive, but not the locked 7-layer endpoint', 'sub'),
 (19, 'RQ2 +0.064 [−0.032, +0.163], not significant', 'RQ2 +0.064 [−0.032, +0.163], CI includes 0 → addendum-13 rule triggered the W re-run; not done = deviation D13-1', 'eq'),
 (19, 'a CPU proxy with Stage 10’s 5 false titles and the rank metric; the GPU re-run of the original W was not done (user decision 2026-11-06)',
      'a CPU proxy with Stage 10’s 5 false titles and the rank metric, not W; locked 7-layer endpoint (approx., no L16): RQ2 +0.046 [+0.007, +0.088] / +0.049 [+0.005, +0.094], same direction (c2_followup_proxy.csv)', 'eq'),
 (19, 'Reading', 'Three premises', 'eq'),
 (19, 'The frozen multi-layer conclusion survives an all-author, all-token re-scoring; the single-layer L56 A − B gap does not.',
      'W scores only the first author’s first token (64.5% are initials); D13-1 (rule triggered at L56 only); U28 (L56 made primary at 21:14, by whom and why unknown).', 'eq'),
 (65, '(report v29, 2026-11-07)', '(report v30, 2026-11-08)', 'sub'),
 (70, 'H2 partly supported but not established (rests on M2 and X1); H3', 'H2 partly supported but not established (rests on M2 and X1; X4 recognition gap no longer counted); H3', 'sub'),
 (75, 'done, batch 1 (only P1 / P2 with five false titles still running), batches 2 and 3;', 'done, batch 1 (complete), batches 2 and 3 (in progress);', 'sub'),
 (77, 'C  R1 × recognised (descriptive)', 'C  R1 × recognised (addendum 11 B)', 'eq'),
 (77, '32', '462', 'eq'), (77, '+0.464 [0.388, 0.538]', '+0.559 [0.529, 0.590]', 'eq'), (77, '+0.335', '+0.408', 'eq'),
 (77, '+0.721 [0.650, 0.806]', '+0.731 [0.705, 0.757]', 'eq'), (77, '+0.996 [0.968, 1.026]', '+0.985 [0.977, 0.994]', 'eq'),
 (77, 'C 32 / D 5 / R2-unwritten 28 papers → descriptive', 'C completed to 462 papers: within bin same timing as A, larger gap (C − A +0.075 [+0.024, +0.130]); D 33 / R2-unwritten 28 papers → descriptive', 'eq'),
 (77, ' (rerun_report.md Counts)', ' (rerun_report.md Counts; b2_cd_report.md)', 'eq'),
 (79, '(B/A 0.78–0.99)', '(B/A 0.72–0.87 with five false titles; false_0 0.78–0.99)', 'sub'),
 (81, 'status 2026-11-06 evening', 'status 2026-11-08', 'sub'),
 (81, 'Batch 1, running: ', 'Batch 1, done: ', 'eq'),
 (81, 'P1 / P2 with five false titles — result after approval', 'P1 / P2 with five false titles (five-title mean primary, false_0 beside): every mean5 − false_0 CI includes 0 → conclusions unchanged; colon numerator B/A 0.72–0.87 (b1_p12f_report.md)', 'eq'),
 (81, 'code, tiny tests and hard-check unit tests done; starts automatically after batch 1;', 'running; C / D completion done (C 462 papers: same timing as A); 2-11 stopped by its hard check → 2-11b (addendum 15), shard 0 only, queued; other items in progress;', 'sub'),
 (81, '3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: code ready, after batch 2', '3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: queued, start after batch 2', 'sub'),
 (82, 'Written 2026-11-06', 'Written 2026-11-06; last two items added 2026-11-08 (v30)', 'eq')]
hits = {i: 0 for i in range(len(RULES))}
for si, s in enumerate(prs.slides, 1):
    for p in paras(s.shapes):
        for r in p.runs:
            for i, (sn, a, b, mode) in enumerate(RULES):
                if sn != si: continue
                if (mode == 'eq' and r.text == a) or (mode == 'sub' and a in r.text):
                    r.text = b if mode == 'eq' else r.text.replace(a, b); hits[i] += 1
# slide 82: two bullets cloned from the last bullet ('•  ', label, text, src, text)
s82 = prs.slides[81]; last = [p for p in paras(s82.shapes) if p.text.startswith('•  High-citation bins')]
add82 = 0
if len(last) == 1:
    p0 = last[0]; prev = p0._p
    for label, text in [('Layers and samples: ', 'Stage 10 samples L24–L40 every 8th layer (no L25–L31, L33–L39; no plan to fill); interventions use 1,186 of 9,108 papers; denominator effects (C 0.559 vs A 0.407)'),
                        ('Post hoc and single title: ', 'parity tolerance 0.25 → 0.5 was used (Stage 10 main round, max 0.367); M5 part B and the E4b X1-controls pipeline use false_0 only, no plan')]:
        new = copy.deepcopy(p0._p); prev.addnext(new); prev = new
        from pptx.text.text import _Paragraph
        np_ = _Paragraph(new, p0._parent); rs = np_.runs
        rs[0].text = '•  '; rs[1].text = label; rs[2].text = text
        for r in rs[3:]: r.text = ''
        add82 += 1
# slide 65 image
img = (D / 'Stage13_hypotheses_table_v30_en_tableonly.png').read_bytes(); img65 = 0
for sh in prs.slides[64].shapes:
    if sh.shape_type == 13 and sh.name.startswith('chart image'):   # only the table picture (the background part is shared by many slides)
        part = prs.slides[64].part.related_part(sh._element.blipFill.blip.rEmbed); part._blob = img; img65 += 1
        from PIL import Image; import io
        w, h = Image.open(io.BytesIO(img)).size; sh.height = int(sh.width * h / w)   # keep the aspect ratio of the v30 image
# notes
old = json.loads((E / 'notes_zh.json.before_20261108c').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nhit, nmiss = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    s = prs.slides[int(k) - 1]; ps = [p for p in s.notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1 and len(ps[0].runs) >= 1:
        ps[0].runs[0].text = new[k]['text']
        for r in ps[0].runs[1:]: r.text = ''
        nhit.append(k)
    else: nmiss.append(k)
prs.save(sys.argv[2])
miss = [RULES[i][:2] for i, c in hits.items() if c == 0]
print('rule hits', sum(1 for c in hits.values() if c), '/', len(RULES), '; NOT HIT:', miss)
print('slide 82 bullets added', add82, '; slide 65 images replaced', img65, '; notes replaced', nhit, '; notes NOT replaced', nmiss)
left = []
for i, s in enumerate(prs.slides, 1):
    txt = ' '.join(p.text for p in paras(s.shapes))
    for k in ['both hold', 'result after approval', 'report v29', 'C 32 / D 5', '(B/A 0.78–0.99)', 'still running']:
        if k in txt: left.append((i, k))
print('LEFT', left)
