"""2026-11-08 round e: slide-text fixes of sync_20261107/apply_20261108a.py for the editable pptx (run level; misses are printed).
Slide 72 bullet (wording B v3, compact), slide 19 RQ1 lower bound, slide-24 caveat V0 label. usage: pptx_text_fix_20261108a.py PPTX"""
import sys
from pptx import Presentation
p = sys.argv[1]; prs = Presentation(p)
RULES = [('Target − control (five false titles, per-donor exclusion): ', 'Target − control, three versions: '),
         ('given-name first token positive from L16, surname from L24 (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 [−0.002, +0.030]); with false_0 only the surname is not significant before L56 — earlier statement superseded',
          'pre-registered (false_0; 1,706 / 1,395 papers): given name + at L24–L48, surname n.s. (L40 +0.012 [−0.026, +0.048]); per-donor (post hoc, D1; 4,654 papers): surname + from L24 (L40 +0.030 [0.013, 0.048]); 5-title mean (leaky, sensitivity only): surname L40 +0.024 [−0.006, +0.052] → given name consistent, surname evidence weak (post hoc only)'),
         ('(within bin; b1_e4b5_report.md, per-donor)', '(within bin; perdonor_by_run_layer.csv V0 / Vpd / V5x0)'),
         ('+0.130 [0.109, 0.153]', '+0.130 [0.108, 0.153]'),
         ('(1,395 papers; e4b_alltok.md)', '(pre-registered V0: false_0 only, 1,395 papers; e4b_alltok.md)')]
def runs(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from runs(sh.shapes)
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs: yield from para.runs
        if getattr(sh, 'has_table', False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for para in c.text_frame.paragraphs: yield from para.runs
hits = {a: [] for a, _ in RULES}
for i, s in enumerate(prs.slides, 1):
    for r in runs(s.shapes):
        for a, b in RULES:
            if a in r.text: r.text = r.text.replace(a, b); hits[a].append(i)
prs.save(p)
for a, _ in RULES: print(('OK   ' if hits[a] else 'MISS ') + a[:70], hits[a])
