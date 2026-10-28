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
PUR = RGBColor(0x8A, 0x4F, 0xA3)
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
note(s, 8.9, 5.0, 3.6, 1.45, [[B('Stages 10-11 · jlens')], [T('Qwen3-32B · 2026-10-27')]], rot=2, size=20)

# 2 question -----------------------------------------------------------------
s = new_slide('Earlier labels: for about half of the papers the model cannot write the author list when asked openly (R0: no true author, or R1: a few right but HR2 above 0.5), but picks the true author list in a 4-option multiple choice. We call these target papers. Control papers: cannot write, cannot pick. If recognition is already computed in middle layers, a lens should read the right names better for target than control there.')
title(s, 'The question')
box(s, 0.9, 1.9, 5.3, 2.2, [[B('target  (4,621 papers)', TGT)], [T("can't write the list (R0/R1)")], [T('but picks the true list 4/4 times')]], color=TGT, rot=-1)
box(s, 0.9, 4.45, 5.3, 2.0, [[B('control  (2,220 papers)', CTL)], [T("can't write the list (R0/R1)")], [T("and can't pick the true list")]], color=CTL, rot=1)
text(s, 6.9, 2.0, 5.8, 3.5, [[T('If the model already '), B('knows'), T(' target authors in its middle layers and only fails to say them, a lens on those layers should read the right name '), B('better for target than control', TGT), T('.')],
                             [T('If the knowledge is only assembled at the end, the gap should appear only near the output.')]], size=23, space=18)
note(s, 7.4, 5.25, 4.6, 1.2, [[B('So: at which layer does target pull ahead of control?')]], rot=-2, size=20)

# 3 data -----------------------------------------------------------------
s = new_slide('Data: the evaluation set of the Dreaming Up Authors study, reused as is. It started from 9,999,863 random OAG v2 records, enriched with Semantic Scholar (citations, canonical names, fields, September 2025) and filtered: journal and conference papers, 1 to 19 authors, English (FastText at least 0.8), clean person names, title and first-author surname agreeing between OAG and Semantic Scholar. 1.92 million papers remained. 8 fields chosen by frequency (77 percent of the data), 13 exponential citation bins, up to 100 papers per field and bin: 9,108 papers. Each author is scored alone: 33,811 author contexts, 149,999 name tokens.')
title(s, 'The data')
stats = [('9,108', 'papers, 8 fields'), ('33,811', 'author names'), ('149,999', 'name tokens scored'), ('13', 'citation bins (0 to 63,901)')]
for i, (n, lab) in enumerate(stats):
    x = 0.9 + i * 3.1
    text(s, x, 1.75, 2.9, 1.0, n, size=54, font=TITLE_F, bold=True, color=[TGT, CTL, GRN, INK][i])
    text(s, x, 2.75, 2.8, 0.6, lab, size=19, color=MUTE)
text(s, 0.9, 3.55, 11.6, 0.8, [[B('Source: '), T('the '), B('Dreaming Up Authors'), T(' evaluation set. 9,999,863 random OAG v2 records + Semantic Scholar metadata (Sep 2025) -> quality filters -> 1.92 M papers -> up to 100 per field x citation bin')]], size=18, color=INK)
text(s, 0.9, 4.45, 6.6, 2.4, [[B('Groups'), T(' (group lead\'s labelling run, same model)')],
                            [B('target', TGT), T('  4,621   ·   '), B('control', CTL), T('  2,220')],
                            [T('guard (writes the authors)  214   ·   excluded  2,053')],
                            [T('Medicine, biology, CS, psychology, chemistry, maths, physics, materials science: ~1,100 papers each')]], size=20, space=12)
note(s, 8.2, 4.55, 4.3, 2.1, [[B('Name formats')], [T('73% start with an initial  ("S. Bree")')], [T('26% start with a full given name  ("Yan Zhao")')]], rot=1.5)

# 3b labels, distractors, false titles, statistics ---------------------------------------
s = new_slide('The rules behind every number. Open answer: greedy decoding inside the chat template; a deterministic fuzzy name match counts matched, hallucinated and unretrieved authors; HR2 = (H+U)/(M+H+U); R2 if HR2 is at most 0.5, otherwise R0 if nothing matched and R1 if something did. No human or model judge. Multiple choice: the true list against the real teams of 3 other papers from the same field, with similar team size, the same citation bin and a similar year; 4 orders; the letter probabilities come from the next-token distribution, A and space-A summed, not renormalised (mass is 1.00 on average). Target: 4 of 4 orders right and mean true-letter probability at least 0.5; control: at most 1 of 4. False titles: 5 per paper from the same field, year kept, minimum-cost matching on year, author count, title length and citation bin, no shared surname, word Jaccard at most 0.6; 79 percent strict tier. Statistics: target versus control only within citation bins with at least 30 papers per group, weighted n_t n_c over n_t plus n_c; bootstrap over papers 2,000 times; sensitivity without bins 0-4.')
title(s, 'How groups and contrasts are built', 'labels: group lead\'s pipeline on the same Qwen3-32B · we use them unchanged')
cards = [('open answer -> R0 / R1 / R2', ['greedy, chat template', 'fuzzy name match: M, H, U', 'HR2 = (H+U) / (M+H+U)', 'R2: HR2 <= 0.5 · R0: M = 0 · R1: M > 0', 'a fixed rule, no human or model judge'], INK, -0.6),
         ('multiple choice -> target / control', ['true list + 3 real teams of other papers', '(same field, team size, citation bin, ~year)', '4 orders · p(letter) from next token', 'target: 4/4 and mean p(true) >= 0.5', 'control: <= 1/4'], TGT, 0.6),
         ('5 false titles per paper', ['same field, own year kept', 'min-cost on |dyear|/5 + |dauthors|', '+ |dtitle tokens| + 1.5 |dcitation bin|', 'no shared surname, Jaccard <= 0.6', '79% strict tier'], CTL, 0.5),
         ('statistics', ['target vs control only within citation bin', '10 bins with >= 30 per group', 'weight n_t n_c / (n_t + n_c)', '95% bootstrap over papers, 2,000', 'sensitivity: drop bins 0-4'], GRN, -0.5)]
for i, (h, lines, col, rot) in enumerate(cards):
    box(s, 0.75 + (i % 2) * 6.15, 1.65 + (i // 2) * 2.7, 5.85, 2.5, [[B(h, col)]] + [[T(l)] for l in lines], color=col, size=16, rot=rot)

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
cap(s, 'Lenses (model weights never change; Jacobians to L63 averaged over prompts): public = 557 WikiText-103 prompts (Neuronpedia) · self100 = 100 frozen WikiText-103 prompts · fitA = 100 other WikiText-103 prompts (Stage 9: one skipped prompt replaced -> 100 valid)', y=6.7)

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
s = new_slide('Key slide. Target minus control within citation bins. Left: true title only - middle layers are even slightly negative for the Jacobian lens. Right: title-specific part - about zero until L56, then +0.21 to +0.23 at L62 and the output. Robustness: 11 percent of target papers are R1 (a few authors right) against 1.5 percent of controls; keeping R0 papers only in both groups, the output difference is +0.199 instead of +0.207 and every layer looks the same, and the Stage 11 curves do not change either. The target advantage is late and almost entirely title-specific.')
title(s, 'Target pulls ahead only in the last layers', 'target - control, within citation bin, 95% CI')
chart(s, 'c3_tc_by_layer', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 4.3, [[T('Middle layers: '), B('no head start')], [T('L62 / output:')], [B('+0.21 to +0.23', TGT)], [T('almost all title-specific')], [B('R0 only'), T(' (no author written): output +0.199 vs +0.207')]], rot=1.5, size=18)

# 8b fine layers -----------------------------------------------------------------
s = new_slide('Fine layers L50 to L61 were added afterwards for the logit lens and the public lens. The target advantage does not switch on at L62: for the logit lens the title-specific target minus control difference is +0.007 at L50, +0.03 at L54, +0.07 at L56, +0.11 at L58, +0.18 at L60 and +0.23 at L62. The public lens is negative up to L54 and turns positive at L57. The steepest rise is L57 to L61. Both groups peak at L61.')
title(s, 'It builds up over the last dozen layers', 'fine layers L40-L62 · title-specific signal · 95% CI')
chart(s, 'c11_fine_layers', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.4, [[T('Logit lens: target - control')], [B('+0.007 at L50', CTL)], [B('+0.23 at L62', TGT)], [T('steepest rise '), B('L57-L61')]], rot=-1.5, size=19)

# S11a method -----------------------------------------------------------------
s = new_slide('Stage 11 turns the readout question into interventions. 593 target and 593 control papers, matched within citation bins. Patching: run the paper with its true title and with a matched false title, and copy the true run hidden state into the false run at one layer. Knockout: forbid attention to the title tokens from layer l to the end. Probe: train a linear map from the last title token to the output state. Chain: score every author after the previous ones.')
title(s, 'Stage 11: intervene, do not just read', '593 + 593 papers: min(60, n_t, n_c) per citation bin, seed 11 · patch uses false_0 · knockout masks all heads · all 9,108 for probe and chain')
items = [('patch', 'copy the true-title hidden state into the false-title run at one layer', TGT, -1),
         ('knock out', 'block attention to the title tokens (all heads) from layer l to the last layer', CTL, 1),
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
s = new_slide('Is the author readable at the title itself? With the lenses, barely: about 0.01 to 0.03 title-specific signal at the last title token. A linear probe trained across papers gets more: re-checked with author-team folds and with papers whose prompt title the probe saw in training removed, about 0.05 at L24 rising to 0.08 at L56, and 0.04 to 0.08 more for target papers. The controls (appendix) show this probe signal is specific to the paper, not a topic-to-name association. This is not in conflict with the lens result: the title is read early, at the title token, but names only become readable at the name positions in L57 to L61. Read early, spoken late.')
title(s, 'Read early: a probe finds it at the title', 'title-specific signal at the last title token · lenses: all 9,108 papers · probe: re-checked, title reuse removed: 1,863 papers (896 target, 499 control)')
chart(s, 'c13_title_position', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 4.2, [[T('lenses: '), B('~0.01-0.03')], [T('probe: '), B('0.05 -> 0.08', GRN)], [T('target > control by '), B('+0.04-0.08', TGT)], [T('re-checked: team folds, title reuse removed')], [B('read early', GRN), T(' (title, L16-24), '), B('spoken late', TGT), T(' (names, L57-61)')]], rot=-1.5, size=18)

# S11d chain -----------------------------------------------------------------
s = new_slide('Author chain. When the earlier authors are in the context, later authors become easier: plus 0.17 to 0.23 for target, 0.12 to 0.18 for control. But the title matters less: the title-specific signal drops from 0.45 to 0.26 for later target authors, because the co-authors already identify the paper. Target still beats control within bins, plus 0.11 to 0.15.')
title(s, 'Co-authors help, and partly replace the title', 'model output · all 9,108 papers · 95% CI')
chart(s, 'c14_author_chain', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.6, [[T('later authors '), B('+0.17 to +0.23', TGT)], [T('title-specific part '), B('shrinks')], [T('target > control still')]], rot=1.5, size=18)

# S12a name prior -----------------------------------------------------------------
s = new_slide('How much is just the name prior? We score the same names with no title at all. Without a title the correct name already sits around rank 12 on average: punctuation and the rest of a surname are easy once the prefix is given. The true title improves the surname first token the most: for target papers from about rank 146 to rank 24. Split the target minus control gap within citation bins: about 0.09 is already there without a title (target names are a bit easier to guess), false titles take back 0.05, and 0.21 is paper-specific. On the surname first token the prior part is about zero and 0.42 is paper-specific. The prior barely tracks multiple-choice recognition (Spearman 0.09 vs 0.33 for the paper-specific part).')
title(s, 'How much is just the name prior?', 'model output · no title vs false title vs true title · all 9,108 papers')
chart(s, 'c15_name_prior', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 3.9, [[T('no title: rank '), B('~12')], [T('target - control: '), B('+0.09', MUTE), T(' prior, '), B('+0.21', TGT), T(' paper')], [T('surname 1st: prior ~0, paper '), B('+0.42', TGT)], [T('prior vs recognition rho '), B('0.09')]], rot=1.5, size=17)

# S12b probe controls -----------------------------------------------------------------
s = new_slide('Is the probe at the title token reading real paper knowledge, or just topic to name associations? If we score its output against the authors of another paper, or of another paper in the same field, the signal drops to zero. If we train it only on false-title pairs it gives a similar signal (the earlier even-stronger result came from a leak: the same donor title in training and test). So the last title token carries linearly decodable, paper-specific author information already at L24, more for target papers, even though the lenses cannot read it.')
title(s, 'The probe signal is paper-specific', 'last title token · 5-fold ridge probe · re-checked: author-team folds, title reuse removed')
chart(s, 'c16_probe_controls', 0.6, 1.6, 8.0)
note(s, 9.0, 1.9, 3.7, 3.6, [[T('another paper\'s authors: '), B('0')], [T('same-field paper: '), B('0')], [T('so it is '), B('this paper', TGT), T(', already at L24')], [T('lenses cannot read it')]], rot=-1.5, size=18)

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
s = new_slide('Wrap up. One line: read early, spoken late. The title is taken in during L24 to L50 (patching, knockout, probe at the title token), but the author names only become readable at the name positions in L57 to L61. The lens result (no middle-layer lead for target) and the probe result (a small target lead at the title token) are about different positions and do not conflict.')
title(s, 'What we learned: read early, spoken late')
pts = [('Read early', 'Causally the title is read in L24-L50 and moved into the tokens after it; after L52 it is no longer needed. A probe at the title token reads a little of it from L16-L24.'),
       ('Spoken late', 'At the name positions, paper-specific author knowledge becomes lens-readable only from ~L50, fastest over L57-L61.'),
       ('No lens lead', 'Read with a lens at the names, target is not ahead of control in middle layers; the +0.21 gap is at the end (probe at the title: +0.02-0.04).'),
       ('Real knowledge', 'Name prior is ~1/3 of the gap overall but ~0 on surnames; the rest is paper-specific and grows with citations.'),
       ('Lenses agree', 'Jacobian lenses read more in middle layers, but nothing target-specific.'),
       ('Name format', 'Initials carry little; full given names carry as much as surnames and help predict them.')]
for i, (h, b) in enumerate(pts):
    y = 1.45 + i * 0.92
    text(s, 0.9, y, 3.1, 0.85, h, size=28, font=TITLE_F, bold=True, color=[TGT, GRN, CTL, GRN, INK, TGT][i])
    text(s, 4.0, y + 0.1, 8.6, 0.85, b, size=20)

# 16 caveats & next -----------------------------------------------------------------
s = new_slide('Limits and next steps. Patching and knockout fix when the title is read (L24-L50) but not what happens inside those layers. Stage 12 is running: single-position patching, attention versus MLP patching, a lens fitted on author prompts, and two name-prior baselines. A second model is out of scope: the groups come from the group lead labelling run of Qwen3-32B.')
title(s, 'Caveats and next steps')
text(s, 0.9, 1.6, 6.0, 4.8, [[B('Caveats')], [T('- Readout is correlational; patching/knockout fix the timing, not the mechanism inside L24-L50')], [T('- Parity tolerance raised 0.25 -> 0.5 after the fact')],
                            [T('- Groups are model-specific; low-citation "recognition" is near chance')], [T('- Few control papers above 1,000 citations')], [T('- Label run settings (max length, thinking mode) not in the package')]], size=21, space=10)
note(s, 7.4, 1.7, 5.1, 3.9, [[B('Stage 12 (running)')], [T('1. Patch single positions (quote, year, "Authors:") - done, analysing')], [T('2. Attention vs MLP patching in L8-L56')], [T('3. A lens fitted on author prompts, read at L24-L62')], [T('4. Name-prior baselines: distractor lists without a title; a prompt with no paper')]], rot=1.5, size=19)

# R0/R1 a: three views -----------------------------------------------------------------
s = new_slide('Is the target advantage just the R1 papers? Target pools R0 papers, where the open answer named no true author, and R1 papers, where it named a few; 11 percent of target papers are R1 but only 1.5 percent of controls. Left: three views of target minus control within citation bins. R0 only (groups A versus B, the Stage 1 to 9 comparison) gives +0.199 at the output against +0.207 pooled, and the curve has the same shape. R1 target papers against R0 controls give +0.37: they know their papers better, but they also only pull ahead after L52. Control R1 has only 34 papers, so it is described, not tested. Right: Stage 11 patching by recall level; R1 targets (36 papers) recover a little later but are complete by L52. The title-position probe gives the same picture: R0 view +0.02 to +0.04. Conclusion unchanged.')
title(s, 'Is it just the R1 papers? No.', 'R0 = no true author written · R1 = a few written · A/B/C/D = target/control x R0/R1')
chart(s, 'c17_r0_r1', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 4.4, [[B('R0 only (A - B):', TGT)], [T('output +0.199 vs +0.207, same shape')], [B('R1 (C - B):', PUR), T(' +0.37, also late')], [T('C - A within target: +0.11, from L56')], [B('patching:'), T(' R1 a bit later, done by L52')]], rot=1.5, size=17)

# R0/R1 b: written vs missed authors (appendix) -----------------------------------------------------------------
s = new_slide('Inside R1 papers the open answer got some authors right and missed others. The label package only counts matches, so we rebuilt which authors matched; the rebuilt count equals the package count for 99.3 percent of R1 papers. In 495 papers with both kinds, the authors the model wrote correctly carry more title-specific signal at the output, +0.20, and the same holds without first authors. But the difference is zero up to L52 and grows from L54: even for authors the model actually produces, the paper-specific signal appears only in the last layers. They are also somewhat easier to guess without a title, +0.10.')
title(s, 'Authors it wrote vs authors it missed', 'inside 495 R1 papers · paired within paper · 95% CI')
chart(s, 'c18_r1_authors', 0.5, 1.6, 9.2)
note(s, 9.95, 1.9, 2.9, 4.0, [[T('written - missed, output: '), B('+0.20', TGT)], [T('~0 up to L52, grows from '), B('L54')], [T('no title (prior): +0.10')], [T('same without first authors')]], rot=-1.5, size=18)

# stage labels (top right), by build index; none on the title, conclusions and appendix divider
TAGS = ['', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10',
        'Stage 11', 'Stage 11', 'Stage 11', 'Stage 11', 'Stage 11', 'Stage 12', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10', 'Stage 10',
        '', 'Stage 12 plan', 'Stage 10-11', 'Stage 10-11']
TAG_COL = {'Stage 10-11': PUR, 'Stage 10': CTL, 'Stage 11': TGT, 'Stage 12': GRN, 'Stage 12 plan': GRN}
for sl, tg in zip(prs.slides, TAGS):
    if not tg: continue
    sh = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.2), Inches(0.2), Inches(1.85), Inches(0.42)); sh.adjustments[0] = 0.3
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF); sh.line.color.rgb = TAG_COL[tg]; sh.line.width = Pt(1.75); sh.shadow.inherit = False
    tf = sh.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para = tf.paragraphs[0]; para.alignment = PP_ALIGN.CENTER; r = para.add_run(); r.text = tg
    r.font.name = BODY_F; r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = TAG_COL[tg]
assert len(TAGS) == len(prs.slides._sldIdLst), (len(TAGS), len(prs.slides._sldIdLst))
# 2026-10-28 review: probe results under review (team folds, title-reuse exclusion); marker only, slide text unchanged
REVIEW = {}   # 2026-10-28 17:40: both probe slides re-checked and updated; stamps removed
RED = RGBColor(0xB4, 0x23, 0x18)
for i, sl in enumerate(prs.slides):
    if i not in REVIEW: continue
    sh = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.55), Inches(6.5), Inches(0.42)); sh.adjustments[0] = 0.3
    sh.fill.solid(); sh.fill.fore_color.rgb = RED; sh.line.color.rgb = RED; sh.shadow.inherit = False; sh.rotation = -1.5
    tf = sh.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para = tf.paragraphs[0]; para.alignment = PP_ALIGN.CENTER; r = para.add_run(); r.text = REVIEW[i]
    r.font.name = BODY_F; r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# appendix divider -----------------------------------------------------------------
s = new_slide('Appendix: backup slides for questions - checks, readout levels, the author chain, probe controls, lens comparisons, citations and name formats.')
text(s, 0.9, 2.6, 11.5, 1.2, 'Appendix', size=72, font=TITLE_F, bold=True)
text(s, 0.95, 3.9, 11, 0.8, 'checks · readout levels · author chain · probe controls · lenses · citations · name formats', size=24, color=MUTE)

# order: main line (15 slides), then the appendix. Indices are build order.
ORDER = [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 24, 22, 23,   26,   5, 6, 13, 25, 15, 16, 17, 18, 19, 20, 21]
lst = prs.slides._sldIdLst; ids = list(lst); assert sorted(ORDER) == list(range(len(ids))), (len(ids), ORDER)
for e in ids: lst.remove(e)
for i in ORDER: lst.append(ids[i])
out = HERE / 'Stage10_author_readout_talk.pptx'; prs.save(out); print('saved', out, len(ids), 'slides')
