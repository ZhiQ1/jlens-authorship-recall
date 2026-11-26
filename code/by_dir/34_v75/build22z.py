"""2026-11-25 coordinator: main pptx v22y -> v22z (= HTML v75 changes on slides 124/125 -> S131/S132).
S131: two added curves on chart 2 (new shapes only; the user's chart shapes are not touched): ③ (i) later names only, within-paper
      (dashed blue, open circles) and ④ (i) 1st name only, pooled AUROC (dotted purple, squares) + direct labels;
      our cats lines: Result clause, Caveat extended (fit/eval + prompt); new ③④ caveat line.
S132: sticky note (rect #2101 + text #2102, #2103) deleted (user-approved 2026-11-25); our Caveat #2117 extended (misspellings ≤ 0.6%)."""
import json, copy
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
IN_, OUT = D + 'jlens_1113_pre_v22y.pptx', D + 'jlens_1113_pre_v22z.pptx'
PFX = '[2026-11-25 v22z] '
prs = Presentation(IN_); SL = list(prs.slides); assert len(SL) == 192
U = Presentation(D + 'stage1-13 超长卷.pptx')
def ups(s): return {x.shape_id for su in U.slides if su.slide_id == s.slide_id for x in su.shapes}
def sh(s, sid): return next(x for x in s.shapes if x.shape_id == sid)
added, edited, deleted = [], [], []

XS = [414, 457, 500, 543, 586, 630, 673]
def Y(v): return 281 - (v - 0.4) * 327.5
LATER = [0.545, 0.542, 0.556, 0.510, 0.542, 0.598, 0.586]
FIRST = [0.659, 0.696, 0.695, 0.707, 0.784, 0.771, 0.736]
BLUE, PURP, INK = RGBColor(0x3C, 0x78, 0xB4), RGBColor(0x7A, 0x5F, 0xA8), RGBColor(0x22, 0x30, 0x4A)

s = SL[130]; U131 = ups(s)
def curve(vals, col, dash):
    fb = s.shapes.build_freeform(Pt(XS[0]), Pt(Y(vals[0])), scale=1.0)
    fb.add_line_segments([(Pt(x), Pt(Y(v))) for x, v in zip(XS[1:], vals[1:])], close=False)
    f = fb.convert_to_shape(); f.fill.background(); f.line.color.rgb = col; f.line.width = Pt(1.3); f.line.dash_style = dash
    added.append(f.shape_id); return f
def marker(x, v, col, kind):
    if kind == 'o':
        m = s.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x - 2.2), Pt(Y(v) - 2.2), Pt(4.4), Pt(4.4))
        m.fill.solid(); m.fill.fore_color.rgb = RGBColor(255, 255, 255); m.line.color.rgb = col; m.line.width = Pt(1)
    else:
        m = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x - 2), Pt(Y(v) - 2), Pt(4), Pt(4))
        m.fill.solid(); m.fill.fore_color.rgb = col; m.line.fill.background()
    added.append(m.shape_id)
def text(x, y, w, h, parts, size):
    tb = s.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h)); tf = tb.text_frame; tf.word_wrap = True
    for a in ('margin_left', 'margin_right', 'margin_top', 'margin_bottom'): setattr(tf, a, 0)
    p = tf.paragraphs[0]
    for t, col, bold, ul in parts:
        r = p.add_run(); r.text = t; r.font.size = Pt(size); r.font.name = 'Patrick Hand'; r.font.color.rgb = col; r.font.bold = bold; r.font.underline = ul
    added.append(tb.shape_id); return tb

curve(LATER, BLUE, MSO_LINE.DASH)
for x, v in zip(XS, LATER): marker(x, v, BLUE, 'o')
curve(FIRST, PURP, MSO_LINE.ROUND_DOT)
for x, v in zip(XS, FIRST): marker(x, v, PURP, 's')
text(500, 252, 140, 9, [('③ (i) later names only, within-paper: 0.51–0.60', BLUE, True, False)], 6.5)
text(430, 134, 230, 9, [('④ (i) 1st name only · pooled AUROC (not comparable)', PURP, True, False)], 6.5)

# our cats lines
def append_run(shape, after_text, new_text, ul=False):
    assert shape.shape_id not in U131
    for p in shape.text_frame.paragraphs:
        rs = p.runs
        for i, r in enumerate(rs):
            if after_text in r.text:
                r.text = r.text.replace(after_text, after_text + new_text, 1); edited.append(shape.shape_id); return
    raise SystemExit(f'anchor not found in {shape.shape_id}: {after_text}')
if 11308 not in edited:   # anchor split across runs: append after the run that closes the highlighted clause
    r0 = [r for p in sh(s, 11308).text_frame.paragraphs for r in p.runs]
    tail = r0[-1]; assert tail.text.strip().endswith('.'), tail.text
    tail.text = tail.text.rstrip()[:-1] + ' (same on later-name pairs only: +0.066 to +0.070).'; edited.append(11308)
append_run(sh(s, 11310), 'the confidence check and the H3 link were not pre-registered',
           '; fit on target + control, tested on target only (not pre-registered); own prompt: not comparable across pages')
text(420, 262.5, 268, 16, [('③④ post hoc, not pre-registered: ', INK, True, False),
                         ('curve (i) mixed two pre-name tokens (a line break before the 1st name, “;” before later names)', INK, False, True),
                         ('; ③ above 0.5 only at L52–L56; ④ pooled AUROC, ', INK, False, False), ('not comparable', INK, False, True), ('.', INK, False, False)], 5.3)
s.notes_slide.notes_text_frame.add_paragraph().add_run().text = PFX + '(i) split by pre-name token (post hoc): curves ③/④ added on chart 2 (new shapes; user chart untouched); caveat lines; coordinator 2026-11-25.'

# S132
s2 = SL[131]; U132 = ups(s2)
for sid in (2101, 2102, 2103):
    x = sh(s2, sid); assert sid not in U132
    if sid == 2102: assert x.text_frame.text.strip() == '50.4%'
    if sid == 2103: assert 'vs 50.5% for the shuffled baseline' in x.text_frame.text
    x._element.getparent().remove(x._element); deleted.append(sid)
c = sh(s2, 2117); assert c.shape_id not in U132
runs = [r for p in c.text_frame.paragraphs for r in p.runs]
last = runs[-1]; assert last.text.strip().endswith('.'), last.text
nr = copy.deepcopy(last._r); last._r.addnext(nr)
last.text = last.text.rstrip()[:-1] + '; '
from pptx.text.text import _Run
r2 = _Run(nr, last._parent); r2.text = 'a small share (≤ 0.6%) look like misspellings of a true author.'; r2.font.underline = True
edited.append(2117)
s2.notes_slide.notes_text_frame.add_paragraph().add_run().text = PFX + 'sticky note "50.4% … vs 50.5%" deleted (user-approved: shuffled value equal by construction); Caveat + misspellings ≤ 0.6%.'
prs.save(OUT)
json.dump({'edited': [[131, e] for e in edited if e in (11308, 11310)] + [[132, 2117]], 'added': [[131, a] for a in added], 'deleted': [[132, d] for d in deleted],
           'notes': [131, 132], 'notes_prefix': PFX, 'new_slides': [], 'deleted_slides': [],
           'user_authorised': [[132, d, 'user 2026-11-25: delete the 50.4% vs 50.5% sticky note'] for d in deleted], 'order': list(range(1, 193))},
          open(OUT + '.allow.json', 'w'), ensure_ascii=False)
print('ok', 'added', len(added), 'edited', edited, 'deleted', deleted)
