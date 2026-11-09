"""2026-11-07 d: slide-text fixes of sync_20261107/apply_20261107g.py applied to the editable pptx (run level). Rules that are not found in a single run are printed, not forced.
usage: pptx_text_fix_20261107d.py PPTX"""
import sys
from pptx import Presentation
p = sys.argv[1]; prs = Presentation(p)
RULES = [('116 / 194 units done, 78 left in three parallel chains', '187 / 194 units done, result pending'),
         ('3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23 · 3-3 Stage 7.1B fast path: code in progress', '3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: code ready, after batch 2 · 3-3 Stage 7.1B fast path: stopped (deviation D14-1; equivalence with the old per-prefix results not confirmed)'),
         ('E4b minus five false titles: surname L40 +0.076', 'E4b, per-donor exclusion (4,654 papers, ~1.5 false titles each): surname L40 +0.076'),
         ('Five false titles (batch 1)', 'Per-donor exclusion (batch 1)'),
         ('all papers (1,863), team folds', 'target + control (1,395), team folds'),
         ('[2.6, 11.6]', '[2.5, 11.6]'), ('[0.87, 0.94]', '[0.86, 0.94]'),
         ('Name prior is only ~1/3 of the gap', 'Name prior (delete-title condition) is only ~0.35 of the gap'),
         ('prior ≈ 19% of the gap', 'pure name prior ≈ 19% of the gap (delete-title prior of §6.12: 0.35)'),
         ('100% from L52', '99.6% from L52')]
def runs(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from runs(sh.shapes)
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                yield from para.runs
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
for a, _ in RULES: print(('OK   ' if hits[a] else 'MISS ') + a[:60], hits[a])
