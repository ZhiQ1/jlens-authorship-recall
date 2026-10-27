"""Build the hand-written style Stage 10 talk (python-pptx). Charts come from charts.py; fonts: Caveat (titles), Patrick Hand (text)."""
from pathlib import Path
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = Path(__file__).parent; CH = HERE / 'charts'
INK, TGT, CTL, MUTE, NOTE, GRN = RGBColor(0x2B, 0x2D, 0x42), RGBColor(0xE0, 0x7A, 0x2F), RGBColor(0x3A, 0x6E, 0xA5), RGBColor(0x6E, 0x70, 0x80), RGBColor(0xFF, 0xF1, 0xA8), RGBColor(0x3C, 0x8D, 0x5A)
TITLE_F, BODY_F = 'Caveat', 'Patrick Hand'

# grid-paper background
bg = HERE / 'paper.png'
img = Image.new('RGB', (2000, 1125), (253, 253, 250)); d = ImageDraw.Draw(img)
for x in range(0, 2000, 50): d.line([(x, 0), (x, 1125)], fill=(226, 234, 243), width=2)
for y in range(0, 1125, 50): d.line([(0, y), (2000, y)], fill=(226, 234, 243), width=2)
d.line([(150, 0), (150, 1125)], fill=(240, 196, 196), width=3)
img.save(bg)

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide(notes):
    s = prs.slides.add_slide(BLANK)
    s.shapes.add_picture(str(bg), 0, 0, prs.slide_width, prs.slide_height)
    s.notes_slide.notes_text_frame.text = notes
    return s


def text(s, x, y, w, h, paras, size=20, font=BODY_F, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space=8):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
    for i, p in enumerate(paras if isinstance(paras, list) else [paras]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.alignment = align; para.space_after = Pt(space)
        runs = p if isinstance(p, list) else [(p, {})]
        for t, o in runs:
            r = para.add_run(); r.text = t; f = r.font; f.name = o.get('font', font); f.size = Pt(o.get('size', size))
            f.bold = o.get('bold', bold); f.color.rgb = o.get('color', color)
    return tb


def title(s, t, sub=None):
    text(s, 0.75, 0.3, 11.9, 0.9, t, size=46, font=TITLE_F, bold=True)
    if sub: text(s, 0.78, 1.08, 11.9, 0.45, sub, size=19, color=MUTE)


def note(s, x, y, w, h, paras, rot=-1.5, size=19, fill=NOTE):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)); sh.rotation = rot
    sh.fill.solid(); sh.fill.fore_color.rgb = fill; sh.line.color.rgb = RGBColor(0xE2, 0xD3, 0x7A); sh.line.width = Pt(1)
    sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_right = Inches(0.22); tf.margin_top = tf.margin_bottom = Inches(0.18)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.space_after = Pt(9); para.alignment = PP_ALIGN.LEFT
        runs = p if isinstance(p, list) else [(p, {})]
        for t, o in runs:
            r = para.add_run(); r.text = t; r.font.name = o.get('font', BODY_F); r.font.size = Pt(o.get('size', size)); r.font.bold = o.get('bold', False)
            r.font.color.rgb = o.get('color', INK)
    return sh


def box(s, x, y, w, h, paras, color=INK, size=19, rot=0):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)); sh.rotation = rot
    sh.adjustments[0] = 0.08; sh.fill.background(); sh.line.color.rgb = color; sh.line.width = Pt(2.25)
    tf = sh.text_frame; tf.word_wrap = True; tf.margin_left = tf.margin_right = Inches(0.18); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.alignment = PP_ALIGN.CENTER; para.space_after = Pt(4)
        runs = p if isinstance(p, list) else [(p, {})]
        for t, o in runs:
            r = para.add_run(); r.text = t; r.font.name = o.get('font', BODY_F); r.font.size = Pt(o.get('size', size)); r.font.bold = o.get('bold', False); r.font.color.rgb = o.get('color', color)
    return sh


def arrow(s, x1, y1, x2, y2, color=INK):
    c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2)); c.line.color.rgb = color; c.line.width = Pt(2.25)
    ln = c.line._get_or_add_ln(); from lxml import etree
    ln.append(etree.fromstring('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))


def chart(s, name, x, y, w):
    im = Image.open(CH / f'{name}.png'); h = w * im.height / im.width
    s.shapes.add_picture(str(CH / f'{name}.png'), Inches(x), Inches(y), Inches(w), Inches(h)); return h


def cap(s, t, y=6.95): text(s, 0.78, y, 11.8, 0.35, t, size=14, color=MUTE)


B = lambda t, c=INK: (t, {'bold': True, 'color': c})
T = lambda t: (t, {})

# 1 title -----------------------------------------------------------------
s = new_slide('Opening. One question: when Qwen3-32B "knows" who wrote a paper, at which layer does that knowledge show up? 9,108 papers, every author name token, read out layer by layer.')
text(s, 0.9, 1.6, 11.5, 1.2, 'Where does Qwen3-32B', size=66, font=TITLE_F, bold=True)
text(s, 0.9, 2.65, 11.5, 1.2, [[('hold', {'color': TGT, 'bold': True}), (" a paper's authors?", {'bold': True})]], size=66, font=TITLE_F)
text(s, 0.95, 4.05, 10.5, 0.6, 'A layer-by-layer readout of author names for 9,108 papers', size=26, color=MUTE)
note(s, 8.9, 5.0, 3.6, 1.45, [[B('Stage 10 · jlens')], [T('Qwen3-32B · 2026-10-26')]], rot=2, size=20)

# 2 question -----------------------------------------------------------------
s = new_slide('Earlier labels: for about half of the papers the model cannot write the authors when asked openly, but picks the true author list in a 4-option multiple choice. We call these target papers. Control papers: cannot write, cannot pick. If recognition is already computed in middle layers, a lens should read the right names better for target than control there.')
title(s, 'The question')
box(s, 0.9, 1.9, 5.3, 2.2, [[B('target  (4,621 papers)', TGT)], [T("can't write the authors")], [T('but picks the true list 4/4 times')]], color=TGT, rot=-1)
box(s, 0.9, 4.45, 5.3, 2.0, [[B('control  (2,220 papers)', CTL)], [T("can't write the authors")], [T("and can't pick the true list")]], color=CTL, rot=1)
text(s, 6.9, 2.0, 5.8, 3.5, [[T('If the model already '), B('knows'), T(' target authors in its middle layers and only fails to say them, a lens on those layers should read the right name '), B('better for target than control', TGT), T('.')],
                             [T('If the knowledge is only assembled at the end, the gap should appear only near the output.')]], size=23, space=18)
note(s, 7.4, 5.25, 4.6, 1.2, [[B('So: at which layer does target pull ahead of control?')]], rot=-2, size=20)

# 3 data -----------------------------------------------------------------
s = new_slide('Data: 9,108 papers across 8 fields, years 1817-2020, citations 0 to 63,901 in 13 bins. Each author is scored alone: 33,811 author contexts, 149,999 name tokens.')
title(s, 'The data')
stats = [('9,108', 'papers, 8 fields'), ('33,811', 'author names'), ('149,999', 'name tokens scored'), ('13', 'citation bins (0 to 63,901)')]
for i, (n, lab) in enumerate(stats):
    x = 0.9 + i * 3.1
    text(s, x, 1.75, 2.9, 1.0, n, size=54, font=TITLE_F, bold=True, color=[TGT, CTL, GRN, INK][i])
    text(s, x, 2.75, 2.8, 0.6, lab, size=19, color=MUTE)
text(s, 0.9, 3.9, 6.6, 2.8, [[B('Groups'), T(' (from an earlier labelling run of the same model)')],
                            [B('target', TGT), T('  4,621   ·   '), B('control', CTL), T('  2,220')],
                            [T('guard (writes the authors)  214   ·   excluded  2,053')],
                            [T('Medicine, biology, CS, psychology, chemistry, maths, physics, materials science: ~1,100 papers each')]], size=20, space=12)
note(s, 8.2, 4.1, 4.3, 2.3, [[B('Name formats')], [T('73% start with an initial  ("S. Bree")')], [T('26% start with a full given name  ("Yan Zhao")')]], rot=1.5)

# 4 method -----------------------------------------------------------------
s = new_slide('Method. Prompt: Who are the authors of the paper titled "..." (year)? Authors: then one author name. Teacher forcing: at each name token we ask what rank the correct token gets. Readouts: logit lens, three Jacobian lenses (public from Neuronpedia, self100, fitA), and the real model output. Layers 24 to 62. Metric log10(1/rank): 0 = rank 1, -1 = rank 10. Each paper is also run with 5 matched false titles and with no title; title-specific signal = true minus mean of the false titles, so name guessability cancels out.')
title(s, 'How we read the model')
box(s, 0.8, 1.7, 3.6, 1.6, [[T('"Who are the authors of the paper titled ')], [B('"{title}"', TGT), T(' ({year})? Authors: ')], [B('S. Bree', CTL)]], size=18, rot=-1)
arrow(s, 4.5, 2.5, 5.3, 2.5)
box(s, 5.4, 1.7, 3.0, 1.6, [[B('hidden state')], [T('layers 24 · 32 · 40')], [T('48 · 56 · 62')]], size=19)
arrow(s, 8.5, 2.5, 9.3, 2.5)
box(s, 9.4, 1.55, 3.3, 1.9, [[B('readouts')], [T('logit lens')], [T('3 Jacobian lenses')], [T('real output (L63)')]], size=18, rot=1)
text(s, 0.85, 3.85, 5.9, 2.6, [[B('Score'), T(' = rank of the correct next name token,')], [T('as log10(1 / rank):  0 = rank 1,  -1 = rank 10')],
                              [B('7 title conditions'), T(': the true title, 5 matched false titles, no title')]], size=20, space=12)
note(s, 7.3, 4.0, 5.2, 2.3, [[B('title-specific signal')], [T('= true title  -  mean(5 false titles)')], [T('Same name, same tokens: what is left is knowing ')], [B('this paper', TGT)]], rot=-1.5, size=20)
cap(s, 'Target vs control is always compared within a citation bin. 95% bootstrap CIs over papers (2,000 draws).')

# 5 checks -----------------------------------------------------------------
s = new_slide('Checks before trusting numbers: the fast path matches a per-prefix reference up to bf16 rounding; ranks match a previous stage on 972 tokens; punctuation tokens, which cannot depend on the title, show no title-specific signal. The parity tolerance was raised from 0.25 to 0.5 after seeing the results - say this openly.')
title(s, 'Can we trust the numbers?')
for i, (h, b, col) in enumerate([('fast = slow', 'One forward pass vs one per prefix: max gap 0.37 logit (bf16 rounding); ranks 1-41 identical', CTL),
                                 ('matches Stage 6', '972 tokens: same token ids, median log-prob gap ~1e-5', GRN),
                                 ('negative control', 'Punctuation tokens show ~0 title-specific signal at every layer', TGT)]):
    box(s, 0.9 + i * 4.1, 2.0, 3.7, 2.6, [[B(h, col)], [T(b)]], color=col, size=19, rot=[-1, 1, -0.5][i])
note(s, 3.0, 5.15, 7.2, 1.25, [[B('Caveat: '), T('the parity tolerance was raised 0.25 -> 0.5 after seeing these bf16 gaps.')]], rot=-1, size=19)

# 6 level by layer -----------------------------------------------------------------
s = new_slide('All readouts get better with depth. The logit lens reads almost nothing before L48 (ranks in the tens of thousands) and jumps at L62. Jacobian lenses read more from L40, fitA the most. The real output is best of all.')
title(s, 'Names become readable late', 'all 9,108 papers · true title')
chart(s, 'c1_level_by_layer', 0.6, 1.55, 8.0)
note(s, 9.0, 1.9, 3.7, 3.4, [[T('Logit lens: almost nothing until '), B('L48', CTL)], [T('Jacobian lenses read more from '), B('L40', GRN)], [T('Everything jumps at '), B('L62', TGT), T(' (rank ~10)')]], rot=1.5)

# 7 spec by layer -----------------------------------------------------------------
s = new_slide('Now remove name guessability: true title minus false titles. Flat up to L48 for both groups. Starts at L56, big at L62 and the output. Target ends roughly twice as high as control.')
title(s, 'Knowing the paper shows up only at the end', 'title-specific signal · public Jacobian lens (lines) and model output (diamonds)')
chart(s, 'c2_spec_by_layer', 0.6, 1.6, 8.0)
note(s, 9.0, 1.9, 3.7, 3.4, [[B('L24-L48: ~0'), T(' for both groups')], [T('rises at '), B('L56')], [T('L62: '), B('target +0.56', TGT), T(' vs '), B('control +0.24', CTL)]], rot=-1.5)

# 8 target - control -----------------------------------------------------------------
s = new_slide('Key slide. Target minus control within citation bins. Left: true title only - middle layers are even slightly negative for the Jacobian lens. Right: title-specific part - about zero until L56, then +0.21 to +0.23 at L62 and the output. The target advantage is late and almost entirely title-specific.')
title(s, 'Target pulls ahead only in the last layers', 'target - control, within citation bin, 95% CI')
chart(s, 'c3_tc_by_layer', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[T('Middle layers: '), B('no head start')], [T('L62 / output:')], [B('+0.21 to +0.23', TGT)], [T('almost all title-specific')]], rot=1.5, size=19)

# 8b fine layers -----------------------------------------------------------------
s = new_slide('Fine layers L50 to L61 were added afterwards for the logit lens and the public lens. The target advantage does not switch on at L62: for the logit lens the title-specific target minus control difference is +0.007 at L50, +0.03 at L54, +0.07 at L56, +0.11 at L58, +0.18 at L60 and +0.23 at L62. The public lens is negative up to L54 and turns positive at L57. The steepest rise is L57 to L61. Both groups peak at L61.')
title(s, 'It builds up over the last dozen layers', 'fine layers L40-L62 · title-specific signal · 95% CI')
chart(s, 'c11_fine_layers', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[T('Logit lens: target - control')], [B('+0.007 at L50', CTL)], [B('+0.23 at L62', TGT)], [T('steepest rise '), B('L57-L61')]], rot=-1.5, size=19)

# S11a method -----------------------------------------------------------------
s = new_slide('Stage 11 turns the readout question into interventions. 593 target and 593 control papers, matched within citation bins. Patching: run the paper with its true title and with a matched false title, and copy the true run hidden state into the false run at one layer. Knockout: forbid attention to the title tokens from layer l to the end. Probe: train a linear map from the last title token to the output state. Chain: score every author after the previous ones.')
title(s, 'Stage 11: intervene, do not just read', '593 target + 593 control papers (balanced within citation bins) · all 9,108 for probe and chain')
items = [('patch', 'copy the true-title hidden state into the false-title run at one layer', TGT, -1),
         ('knock out', 'block attention to the title tokens from layer l on', CTL, 1),
         ('probe', 'linear map from the last title token to the output state', GRN, -0.5),
         ('chain', '"Authors: A1, A2, ..." instead of each author alone', INK, 0.8)]
for i, (h, d, col, rot) in enumerate(items):
    box(s, 0.9 + (i % 2) * 6.1, 1.9 + (i // 2) * 2.35, 5.6, 2.0, [[B(h, col)], [T(d)]], color=col, size=20, rot=rot)
cap(s, 'Score: rank of the correct name token at the model output; "share of the true-false gap" = (intervened - false) / (true - false).')

# S11b patch + knockout -----------------------------------------------------------------
s = new_slide('Two causal curves. Left: copying the hidden states of the tokens after the title (closing quote, year, Authors:, the name) from the true run into the false run recovers 29 percent at L40, 83 percent at L48 and everything from L52. Copying only the last title token recovers about 12 percent. Right: blocking attention to the title from L0 removes 83 percent of the effect, from L32 37 percent, from L48 6 percent, from L52 nothing. Blocking only the colon and name positions removes at most 15 percent, so the information is routed through the tokens right after the title. Target and control follow the same curves.')
title(s, 'The title is read in L24-L50, early', 'model output · share of the true-false gap · CIs about +/-0.02')
chart(s, 'c12_patch_knockout', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.6, [[B('L52+', TGT), T(': title no longer needed')], [T('info moved to the tokens '), B('right after'), T(' the title')], [T('same timing for target and control')]], rot=1.5, size=18)

# S11c title position -----------------------------------------------------------------
s = new_slide('Is the author readable at the title itself? With the lenses, barely: about 0.01 to 0.03 title-specific signal at the last title token. A linear probe trained across papers gets more, 0.04 at L16 rising to 0.08 at L56, and a little more for target papers. Caution: a probe trained across papers can also pick up topic-to-name associations, not only this paper.')
title(s, 'Not readable at the title token itself', 'title-specific signal at the last title token · all 9,108 papers')
chart(s, 'c13_title_position', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.6, [[T('lenses: '), B('~0.01-0.03')], [T('probe: '), B('0.04 -> 0.08', GRN)], [T('target a bit higher; may include topic -> name associations')]], rot=-1.5, size=18)

# S11d chain -----------------------------------------------------------------
s = new_slide('Author chain. When the earlier authors are in the context, later authors become easier: plus 0.17 to 0.23 for target, 0.12 to 0.18 for control. But the title matters less: the title-specific signal drops from 0.45 to 0.26 for later target authors, because the co-authors already identify the paper. Target still beats control within bins, plus 0.11 to 0.15.')
title(s, 'Co-authors help, and partly replace the title', 'model output · all 9,108 papers · 95% CI')
chart(s, 'c14_author_chain', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.6, [[T('later authors '), B('+0.17 to +0.23', TGT)], [T('title-specific part '), B('shrinks')], [T('target > control still')]], rot=1.5, size=18)

# 9 lens quality -----------------------------------------------------------------
s = new_slide('Comparing lenses. On readout quality fitA is best in most middle layers, self100 at L40; at L48 the Jacobian lenses put the right token in the top 10 for 15-18% of tokens versus 1% for the logit lens. At L62 the plain logit lens is best.')
title(s, 'Which lens reads best?', 'all papers · true title')
chart(s, 'c4_lens_quality', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[B('Middle layers:', GRN)], [T('fitA best; at L48 15-18% top-10 vs 1% for logit')], [B('L62:', CTL), T(' logit lens best (59%)')]], rot=-1.5, size=19)

# 10 lens extra -----------------------------------------------------------------
s = new_slide('Do Jacobian lenses see paper-specific information the logit lens misses? A little: +0.01 to +0.03 more title-specific signal at L24-L48, CIs above zero, but tiny next to 0.44 at L62. And it is not bigger for target: target minus control of that extra is about zero, negative at L48 and L56.')
title(s, 'Do lenses reveal hidden paper knowledge?', 'paired differences, 95% CI')
chart(s, 'c5_lens_extra', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[T('Extra signal: '), B('+0.01 to +0.03')], [T('vs ~0.44 at L62')], [B('Not bigger for target', TGT), T(' (even negative at L48-56)')]], rot=1.5, size=19)

# 11 citation -----------------------------------------------------------------
s = new_slide('Citations. Within both groups the title-specific signal rises steadily with citation bin: target from +0.35 in bin 0-2 to +0.64 in 4097+. Spearman with log citations: 0.45 overall, 0.33 within target, 0.19 within control. The level itself changes much less - names are not easier to guess for famous papers, the model just knows famous papers better.')
title(s, 'More citations, more paper knowledge', 'model output · bins with < 10 papers omitted')
chart(s, 'c6_citation', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[T('Target: '), B('+0.35 -> +0.64', TGT)], [T('Spearman (title-specific)')], [B('0.45'), T(' all · 0.33 target · 0.19 control')], [T('Target > control in every bin')]], rot=-1.5, size=18)

# 12 first token vs first name -----------------------------------------------------------------
s = new_slide('Is the signal decided by the first token? It depends on the name format. Initial-first names: the initial carries little, the signal is on the later tokens that include the surname. Given-name-first names: the given name carries about as much as the rest. Note teacher forcing: later tokens already see the correct prefix in every condition, so their title-specific signal can only come from the title.')
title(s, 'First token or the rest of the name?', 'model output · split by name format')
chart(s, 'c7_format_position', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[B('Initial:', CTL), T(' carries little; signal is on the surname')], [B('Full given name:', TGT), T(' carries about as much as the surname')]], rot=1.5, size=19)

# 13 knowing given name helps -----------------------------------------------------------------
s = new_slide('Does knowing the first word make the rest easier? For a full given name, yes: when it is in the top 10 the surname is +0.22 better at the output, +0.32 for the logit lens at L62. For an initial, no. Mixing both formats would even show a negative effect, because initials are easy and the surnames after them are hard.')
title(s, 'Knowing the given name helps with the surname', 'true title · later words when the first word is / is not in the top 10')
chart(s, 'c8_first_word_helps', 0.6, 1.6, 8.0)
note(s, 9.0, 1.9, 3.7, 3.4, [[B('Given name in top 10', TGT)], [T('surname +0.22 (output)')], [T('+0.32 (logit L62)')], [B('Initial in top 10', CTL), T(': no help')]], rot=-1.5)

# 14 roles + graded -----------------------------------------------------------------
s = new_slide('Left: title-specific signal by token role at the output - surname first token carries most, initials least, punctuation about zero (negative control). Right: across all unrecalled papers, the more multiple-choice orders right, the better the model output (Spearman 0.27).')
title(s, 'Where the signal sits, and a dose-response', 'model output')
chart(s, 'c9_roles', 0.4, 1.6, 7.3)
chart(s, 'c10_graded', 7.9, 1.9, 5.0)
cap(s, 'Right: R0/R1 papers, centred within citation bin; Spearman rho = 0.27, p < 0.001.')

# 15 conclusions -----------------------------------------------------------------
s = new_slide('Wrap up the five findings.')
title(s, 'What we learned')
pts = [('Late', 'Paper-specific author knowledge builds up from about L50, fastest over L57-L61, peaking at L61-L62.'),
       ('Read early', 'Causally, the title is read in L24-L50 and moved into the tokens after it; after L52 it is no longer needed.'),
       ('No head start', 'Target papers are not ahead of control in middle layers; the +0.21 gap is at the end.'),
       ('Real knowledge', 'The gap is title-specific and grows with citations, so it is not name guessing.'),
       ('Lenses agree', 'Jacobian lenses read more in middle layers, but nothing target-specific.'),
       ('Name format', 'Initials carry little; full given names carry as much as surnames and help predict them.')]
for i, (h, b) in enumerate(pts):
    y = 1.45 + i * 0.92
    text(s, 0.9, y, 3.1, 0.85, h, size=28, font=TITLE_F, bold=True, color=[TGT, GRN, CTL, GRN, INK, TGT][i])
    text(s, 4.0, y + 0.1, 8.6, 0.85, b, size=20)

# 16 caveats & next -----------------------------------------------------------------
s = new_slide('Limits and next steps. Patching and knockout now fix when the title is read (L24-L50) but not what happens inside those layers. Next: patch single positions after the title, localise the computation inside L24-L50, and repeat on a second model.')
title(s, 'Caveats and next steps')
text(s, 0.9, 1.6, 6.0, 4.8, [[B('Caveats')], [T('- Readout is correlational; patching/knockout fix the timing, not the mechanism inside L24-L50')], [T('- Parity tolerance raised 0.25 -> 0.5 after the fact')],
                            [T('- Groups are model-specific; low-citation "recognition" is near chance')], [T('- Few control papers above 1,000 citations')]], size=21, space=10)
note(s, 7.4, 1.7, 5.1, 3.6, [[B('Next')], [T('1. Patch single positions (quote, year, "Authors:") to find which token carries the paper')], [T('2. Patch / probe per layer inside L24-L50 to see when it is computed')], [T('3. Repeat on a second model')]], rot=1.5, size=19)

out = HERE / 'Stage10_author_readout_talk.pptx'; prs.save(out); print('saved', out)
