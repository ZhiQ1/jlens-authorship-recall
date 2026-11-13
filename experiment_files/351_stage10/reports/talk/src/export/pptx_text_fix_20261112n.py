"""2026-11-12 n: v21 pptx: all-token / all-author numbers as main (slide 24 diagram + labels + footnote + warning line, slide 70 X3, slide 80 M3) as deck HTML (sync_20261107/apply_20261112n.py); notes = notes_zh.json (changed vs .before_20261112n). usage: IN OUT"""
import sys, json, shutil
from pathlib import Path
from pptx import Presentation
E = Path(__file__).parent; shutil.copy2(sys.argv[1], sys.argv[2]); prs = Presentation(sys.argv[2])
RULES = [(24, 'first author', 'all authors'), (24, 'first author, L40', 'surname 1st token, L40'), (24, '+0.061', '+0.071'),
         (24, 'probe score = log10(1/rank) of the true first-author token', 'probe score = log10(1/rank) of the true name tokens (every author, by role)'),
         (24, '+0.061: Stage 13 E4b re-check, probe scores ONLY THE FIRST NAME TOKEN, target + control (1,395), team folds, title reuse dropped; e4b_trainstd_compare.md',
              '+0.071: addendum 9, all authors, all tokens, surname first token, V0, 1,395 papers (old first-token: +0.061); e4b_alltok.md'),
         (24, '⚠ E4b scores only the first name token (mostly an initial) · all tokens by role: see the addendum-9 slide (surname first token L40 +0.071; 1,395 papers)',
              '⚠ Main number = all authors, all name tokens by role (addendum 9, pre-registered V0; surname first token L40 +0.071, 1,395 papers); old first-token version (E4b) +0.061'),
         (70, '; behaviour keeps ≈ 90% of the first-author preference', '; behaviour keeps ≈ 90% of the author preference'),
         (70, ' (same, 0.90 [0.86, 0.94])', ' (all authors, all tokens 0.897 [0.868, 0.926]; old first-author version 0.90 [0.86, 0.94])'),
         (80, 'first-author first token +0.147 [0.096, 0.191]', 'all authors, all name tokens +0.234 [0.215, 0.252] (2-10; old first-author first-token version +0.147 [0.096, 0.191])')]
EQ = {0, 1, 2, 3, 4, 5, 6, 7}
def paras(shapes):
    for sh in shapes:
        if sh.shape_type == 6: yield from paras(sh.shapes)
        if sh.has_text_frame: yield from sh.text_frame.paragraphs
hits = [0] * len(RULES)
for i, (sn, a, b) in enumerate(RULES):
    for p in paras(prs.slides[sn - 1].shapes):
        done = False
        for r in p.runs:
            if (i in EQ and r.text == a) or (i not in EQ and a in r.text): r.text = b if i in EQ else r.text.replace(a, b); hits[i] += 1; done = True
old = json.loads((E / 'notes_zh.json.before_20261112n').read_text(encoding='utf-8')); new = json.loads((E / 'notes_zh.json').read_text(encoding='utf-8'))
nh, nm = [], []
for k in new:
    if new[k]['text'] == old[k]['text']: continue
    ps = [p for p in prs.slides[int(k) - 1].notes_slide.notes_text_frame.paragraphs if p.text == old[k]['text']]
    if len(ps) == 1: ps[0].runs[0].text = new[k]['text']; [setattr(r, 'text', '') for r in ps[0].runs[1:]]; nh.append(k)
    else: nm.append(k)
prs.save(sys.argv[2]); print('rule hits', hits, '; notes replaced', nh, '; NOT replaced', nm)
