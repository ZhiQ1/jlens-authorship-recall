"""2026-11-07 b: + slide 50 '100% from L52' -> '99.6% from L52'."""
"""2026-11-07: apply to the editable pptx the slide-text changes made in the deck HTML by sync_20261107/apply_20261107.py
(X2 rho 0.45 -> 0.451 on slides 30 and 61; slide 60 'Protocol drift' wording). Edits run text in place; asserts each change. usage: pptx_text_fix_20261107.py PPTX"""
import re, sys
from pptx import Presentation
p = sys.argv[1]; prs = Presentation(p); sl = list(prs.slides)
RULES = [(30, r'ρ = 0\.45(?!\d)', 'ρ = 0.451'), (61, r'ρ = 0\.45(?!\d)', 'ρ = 0.451'),
         (50, r'100% from L52', '99.6% from L52'),
         (None, r'primary endpoint changed between README and run', 'plan locked 10-18 14:29 (7-layer integral primary); the 21:14 PROTOCOL switched to L56, both before 8C scoring; who and why open (U28)')]
def runs(s):
    for sh in s.shapes:
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                for r in para.runs: yield r
        if getattr(sh, 'has_table', False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for para in c.text_frame.paragraphs:
                        for r in para.runs: yield r
done = []
for k, pat, new in RULES:
    targets = [(k, sl[k - 1])] if k else list(enumerate(sl, 1))
    n = 0
    for i, s in targets:
        for r in runs(s):
            if re.search(pat, r.text): r.text = re.sub(pat, new, r.text); n += 1; done.append((i, pat))
    print(pat, 'slide', k, 'runs changed', n)
    assert n >= 1, pat
prs.save(p); print('saved', p, done)
