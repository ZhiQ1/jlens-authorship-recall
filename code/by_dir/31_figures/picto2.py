# More line-art pictograms for the stage figures (same style as picto.py). 2026-11-25.
# Each function takes the top-left (x, y) and draws in about 180 x 120 px.
import math
from picto import INK, ACC, PALE, HAND, SW, _t, card, strip, bars, crossed
TEAL = '#1F6F8B'; RED = '#C0392B'; GREYP = '#9AA3AE'

def L(x1, y1, x2, y2, col=INK, w=SW, arrow=False, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    m = ' marker-end="url(#pa)"' if arrow else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}{m}/>'
def R(x, y, w, h, fill='#fff', col=INK, sw=1.8, rx=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>'
def C(cx, cy, r, fill='#fff', col=INK, sw=1.8):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>'
def P(d, col=INK, w=SW, fill='none'):
    return f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
def axes(x, y, w=150, h=80):
    return L(x, y+h, x+w, y+h, INK, 1.4) + L(x, y, x, y+h, INK, 1.4)
def toks(x, y, n=6, w=16, gap=3, fills=None, labels=None):
    o = ''
    for k in range(n):
        f = (fills or {}).get(k, '#fff')
        o += R(x+k*(w+gap), y, w, 18, f, INK, 1.5, 2)
        if labels and k in labels: o += _t(x+k*(w+gap)+w/2, y+14, labels[k], 14)
    return o
def scissors(cx, cy, col=RED):
    return (C(cx-6, cy+7, 4, '#fff', col, 1.8) + C(cx+6, cy+7, 4, '#fff', col, 1.8) +
            L(cx-4, cy+4, cx+5, cy-9, col, 2) + L(cx+4, cy+4, cx-5, cy-9, col, 2))
def lens(cx, cy, r=13, col=INK):
    return C(cx, cy, r, '#fff', col, 2.2) + L(cx+r*0.7, cy+r*0.7, cx+r*1.5, cy+r*1.5, col, 3)
def probe(cx, cy, col=INK):        # a needle probe
    return P(f'M{cx} {cy} l18 -18', col, 2.6) + C(cx+21, cy-21, 5, ACC, col, 1.8)

# ---------------- L0–L4 ----------------
def colon_move(x, y):              # ":" state: new question moves it far, new paper a little
    o = _t(x+14, y+30, ':', 30)
    o += C(x+40, y+60, 6, ACC) + L(x+46, y+60, x+150, y+40, INK, SW, True) + _t(x+110, y+34, 'new question', 14)
    o += L(x+46, y+62, x+80, y+76, INK, SW, True) + _t(x+110, y+92, 'new paper', 14)
    return o
def layer0_same(x, y):             # three question prompts, identical last token at layer 0
    o = ''
    for k, q in enumerate(('authors', 'year', 'field')):
        yy = y + 6 + k*28
        o += _t(x, yy+14, q, 14, INK, 'start') + toks(x+60, yy, 3, 16) + R(x+117, yy, 18, 18, ACC, INK, 1.8, 2)
    o += P(f'M{x+146} {y+12} q14 36 0 74', INK, 1.8) + _t(x+168, y+56, '=', 22)
    return o
def embed_only(x, y):              # one token embedding, no layers run
    o = R(x, y+70, 30, 22, ACC) + _t(x+15, y+108, 'token', 14)
    for k in range(3):
        o += R(x+56, y+66-k*26, 70, 18, '#F1F2F4', GREYP, 1.4)
    o += crossed(x+78, y+18, 26) + _t(x+90, y+108, 'no layers run', 14)
    return o
def bert_find(x, y):               # another model (knows no papers) finds the same title
    o = R(x, y+10, 60, 70, '#F1F2F4') + _t(x+30, y+52, 'BERT', 15)
    o += L(x+64, y+45, x+96, y+45, INK, SW, True) + card(x+102, y+16, 40, 52) + lens(x+150, y+70, 14)
    return o

# ---------------- L4–L24 ----------------
def probe_transfer(x, y):          # probe trained under one question, tested under another
    o = _t(x, y+16, 'train: field', 14, INK, 'start') + R(x, y+24, 110, 16, PALE) + probe(x+80, y+40)
    o += _t(x, y+74, 'test: authors', 14, INK, 'start') + R(x, y+82, 110, 16, '#fff') + probe(x+80, y+98, GREYP)
    o += bars(x+120, y+60, [44, 14], ['same', 'other'], w=14, gap=26, base=y+104)
    return o
def sink(x, y):                    # ":" attends mostly to position 0
    o = toks(x, y+70, 7, 18, 4, {0: PALE, 6: ACC}, {0: '0', 6: ':'})
    o += P(f'M{x+141} {y+68} C {x+120} {y+10}, {x+20} {y+10}, {x+9} {y+68}', INK, 3.2)
    o += P(f'M{x+141} {y+68} q-24 -26 -48 0', GREYP, 1.4)
    o += _t(x+75, y+20, 'mostly to position 0', 14)
    return o
def timeline(x, y, marks=(('L8–16', 0.12), ('L48–52', 0.56), ('L53–62', 0.98))):
    o = L(x, y+60, x+180, y+60, INK, 2)
    for lab, f in marks:
        xx = x + f*180
        o += L(xx, y+52, xx, y+68, INK, 2) + _t(xx, y+88, lab, 14)
    o += _t(x+90, y+30, 'first appears', 14) + C(x+0.12*180, y+60, 6, ACC)
    return o
def probe_attr(x, y):              # probe at the title reads the year, but the words give it away
    o = card(x, y+8, 50, 60, 'title') + probe(x+40, y+68)
    o += L(x+70, y+38, x+104, y+38, INK, SW, True) + R(x+110, y+24, 56, 28, '#fff') + _t(x+138, y+44, 'year', 14)
    o += _t(x+138, y+86, 'from the words?', 14, RED)
    return o
def surname_l8(x, y):              # L8 title state moved into a fixed prompt; minus a topic partner
    o = R(x, y+10, 60, 16, PALE) + _t(x+30, y+46, 'L8 state', 14)
    o += L(x+64, y+18, x+86, y+18, INK, 1.8, True)
    o += R(x+92, y+4, 92, 28, '#fff') + _t(x+138, y+23, 'first author is…', 14)
    o += R(x, y+64, 60, 16, '#F1F2F4') + _t(x+30, y+100, 'topic partner', 14)
    o += _t(x+110, y+80, 'own − partner', 14)
    return o
def probe_groups(x, y):            # probe at the title: recognised vs not
    o = card(x, y+4, 46, 56) + probe(x+36, y+60)
    o += bars(x+90, y+60, [40, 26], ['recog.', 'not'], w=20, gap=26, base=y+100)
    return o
def source_check(x, y):            # is the surname literally in the title?
    o = card(x, y, 50, 60, 'title') + _t(x+90, y+36, '∌', 26) + R(x+118, y+18, 54, 26, '#fff') + _t(x+145, y+36, 'Co…', 14)
    return o
def topic_pair(x, y):              # same-topic partner paper with other authors
    return card(x, y, 44, 56, 'paper') + _t(x+70, y+34, '≈ topic', 14) + card(x+100, y, 44, 56, 'partner', '#F1F2F4')

# ---------------- L40–L52 ----------------
def putback(x, y):                 # copy true-run states of the after-title positions into the false run
    o = _t(x, y+14, 'true', 14, INK, 'start') + toks(x+44, y, 6, 16, 3, {3: ACC, 4: ACC, 5: ACC})
    o += _t(x, y+64, 'false', 14, INK, 'start') + toks(x+44, y+50, 6, 16, 3, {0: '#F1F2F4', 1: '#F1F2F4', 2: '#F1F2F4'})
    for k in (3, 4, 5):
        xx = x + 44 + k*19 + 8
        o += L(xx, y+20, xx, y+46, INK, 1.8, True)
    o += _t(x+100, y+96, 'copy at one layer', 14)
    return o
def takeaway(x, y):                # block the after-title positions from reading the title
    o = toks(x, y+60, 7, 16, 3, {0: PALE, 1: PALE, 2: PALE, 5: ACC, 6: ACC})
    o += P(f'M{x+111} {y+58} q-40 -46 -84 0', INK, 2)
    o += scissors(x+72, y+30)
    o += _t(x+66, y+100, 'from L52 to the end', 14)
    return o
def five_titles(x, y):
    o = ''
    for k in range(5):
        o += card(x+k*30, y+10, 26, 36, None, '#F1F2F4', 2)
    o += _t(x+72, y+66, 'false_0 … false_4', 14) + _t(x+72, y+96, 'same timing', 14, TEAL)
    return o
def position_copy(x, y):           # copy one position group at a time
    o = toks(x, y+20, 8, 16, 3, {5: ACC, 6: ACC, 7: ACC}, {4: ':'})
    o += P(f'M{x+100} {y+46} v12 h52 v-12', INK, 1.8) + _t(x+126, y+76, 'names only', 14)
    o += bars(x+10, y+92, [6, 18], ['L40', 'L52'], w=14, gap=18, base=y+112) if False else ''
    return o
def edge_block(x, y):              # cut one attention edge (name <- title) in a 4-layer window
    o = toks(x, y+70, 7, 16, 3, {0: PALE, 1: PALE, 2: PALE, 5: '#FBE3E1', 6: '#FBE3E1'})
    o += P(f'M{x+111} {y+68} C {x+100} {y+20}, {x+40} {y+20}, {x+27} {y+68}', TEAL, 2.6)
    o += scissors(x+68, y+32)
    o += _t(x+30, y+108, 'title', 14) + _t(x+110, y+108, 'names', 14)
    return o
def layer_sweep(x, y):             # cut one layer at a time; each costs little
    o = ''
    for k in range(6):
        yy = y + 8 + k*16
        o += R(x, yy, 90, 12, PALE if k != 2 else '#fff', INK, 1.4)
    o += scissors(x+106, y+46) + L(x, y+46, x+90, y+46, RED, 2, dash='4 3')
    o += _t(x+160, y+44, '≤ 1.25%', 14) + _t(x+150, y+70, 'each', 14)
    return o
def groups_timing(x, y):           # recognised vs not: curves rise at the same time, different height
    o = axes(x, y+10, 150, 76)
    o += P(f'M{x} {y+84} C {x+60} {y+82}, {x+80} {y+20}, {x+150} {y+18}', ACC, 2.4)
    o += P(f'M{x} {y+84} C {x+60} {y+84}, {x+80} {y+44}, {x+150} {y+42}', INK, 2.0)
    o += _t(x+110, y+108, 'same timing', 14)
    return o

# ---------------- L48–L56 ----------------
def lens_cannot(x, y):             # lens reads vocabulary directions: nothing
    o = R(x, y+30, 80, 18, PALE) + lens(x+108, y+38, 14) + crossed(x+140, y+20, 22) + _t(x+60, y+86, 'vocabulary directions', 14)
    return o
def probe_can(x, y):
    o = R(x, y+30, 80, 18, PALE) + probe(x+70, y+48) + _t(x+122, y+30, '✓', 26, '#2E7D46') + _t(x+60, y+86, 'trained readout', 14)
    return o
def same_scale(x, y):              # probe and lens on one ruler
    o = L(x, y+60, x+170, y+60, INK, 2)
    for k in range(8):
        o += L(x+k*24, y+54, x+k*24, y+66, INK, 1.4)
    o += lens(x+40, y+30, 10) + probe(x+110, y+44)
    o += _t(x+85, y+92, 'same tokens, one scale', 14)
    return o
def spread(x, y):                  # difference spread over many directions
    cx, cy = x + 70, y + 56
    o = ''
    for k in range(12):
        a = math.radians(k*30 + 8)
        o += L(cx, cy, cx + 44*math.cos(a), cy + 44*math.sin(a), INK if k % 3 else ACC, 1.8)
    o += _t(cx+70, cy-10, 'no axis', 14, INK, 'start') + _t(cx+70, cy+12, '> 7%', 14, INK, 'start')
    return o
def readout_map(x, y):             # grid of cells with a few faint dots
    o = ''
    for i in range(8):
        for j in range(5):
            o += R(x+i*16, y+8+j*16, 14, 14, '#fff', '#C9CED6', 1)
    for i, j in ((2, 1), (5, 3), (6, 0), (1, 4)):
        o += C(x+i*16+7, y+8+j*16+7, 4, ACC, ACC, 1)
    o += _t(x+66, y+108, 'no earlier shelf', 14)
    return o
def mlp_swap(x, y):                # swap the MLP output vs only 512 name directions
    o = R(x, y+20, 56, 36, PALE) + _t(x+28, y+44, 'MLP', 14)
    o += L(x+60, y+38, x+86, y+38, INK, 1.8, True) + R(x+92, y+20, 56, 36, '#fff') + _t(x+120, y+44, 'false', 14)
    o += bars(x+20, y+70, [38, 6], ['whole', 'names'], w=20, gap=40, base=y+108)
    return o
def inject(x, y):                  # add an author direction to the state
    o = R(x, y+40, 90, 18, PALE) + L(x+20, y+20, x+70, y+38, ACC, 3, True) + _t(x+44, y+14, '+ author direction', 14)
    o += L(x+96, y+49, x+124, y+49, INK, 1.8, True) + R(x+130, y+36, 50, 26, '#fff') + _t(x+155, y+54, 'name?', 14)
    o += _t(x+90, y+92, 'another author works too', 14, RED)
    return o
def colon_swap(x, y):              # swap the ":" state for the year prompt's
    o = _t(x, y+40, 'authors', 14, INK, 'start') + R(x+64, y+24, 24, 24, ACC) + _t(x+76, y+42, ':', 18)
    o += _t(x, y+90, 'year', 14, INK, 'start') + R(x+64, y+74, 24, 24, '#F1F2F4') + _t(x+76, y+92, ':', 18)
    o += P(f'M{x+96} {y+86} q30 -10 0 -46', INK, 1.8) + L(x+96, y+40, x+90, y+40, INK, 1.8, True) + _t(x+150, y+66, 'at L56', 14)
    return o

# ---------------- L56–L63 ----------------
def mean_ablate(x, y):             # replace one layer's MLP (or attention) with its average
    o = R(x, y+10, 66, 30, PALE) + _t(x+33, y+30, 'MLP', 14) + R(x, y+54, 66, 30, '#fff') + _t(x+33, y+74, 'attn', 14)
    o += L(x+72, y+25, x+100, y+25, INK, 1.8, True) + R(x+106, y+10, 66, 30, '#F1F2F4') + _t(x+139, y+30, 'average', 14)
    o += _t(x+90, y+108, 'one layer, L57–L61', 14)
    return o
def gap_grows(x, y):
    o = axes(x, y+6, 160, 80)
    o += P(f'M{x} {y+80} H {x+100} C {x+130} {y+78}, {x+140} {y+20}, {x+160} {y+14}', RED, 2.6)
    o += P(f'M{x} {y+82} H {x+160}', INK, 1.6)
    o += _t(x+80, y+106, 'last dozen layers', 14)
    return o
def rank_late(x, y):               # rank of the true name: far away until L62
    o = L(x+20, y+4, x+20, y+96, INK, 1.6) + _t(x+40, y+16, 'rank 10', 14, INK, 'start') + _t(x+40, y+92, 'rank 10,000', 14, INK, 'start')
    o += C(x+20, y+88, 6, ACC) + P(f'M{x+28} {y+84} q70 0 82 -62', INK, 1.8) + C(x+112, y+18, 6, ACC) + _t(x+130, y+50, 'L62', 14)
    return o
def token_parts(x, y):             # initial vs surname tokens
    return bars(x+14, y+10, [10, 54, 46], ['initial', 'surname 1st', 'rest'], w=20, gap=50, base=y+90)
def initial_given(x, y):           # supply the first initial
    o = R(x, y+20, 104, 28, '#fff') + _t(x+52, y+40, 'Authors: K.', 14) + L(x+110, y+34, x+136, y+34, INK, 1.8, True)
    o += bars(x+20, y+60, [8, 30], ['default', 'given K.'], w=22, gap=44, base=y+104)
    return o
def amplify(x, y):                 # push the arrived signal harder
    o = R(x, y+30, 90, 18, PALE) + L(x+10, y+60, x+120, y+60, ACC, 4, True) + _t(x+60, y+86, '× stronger', 14)
    o += _t(x+150, y+44, '2.5 → 2.8%', 14)
    return o
def dir_len(x, y):                 # direction-only vs length-only pushes
    o = L(x+20, y+80, x+80, y+40, INK, 2.2, True) + L(x+20, y+80, x+100, y+80, ACC, 2.2, True)
    o += L(x+20, y+80, x+50, y+20, RED, 2.2, True)
    o += _t(x+130, y+30, 'direction', 14, RED) + _t(x+130, y+86, 'length', 14, ACC)
    return o
def rise_fall(x, y):
    o = axes(x, y+6, 160, 80) + P(f'M{x} {y+80} C {x+70} {y+80}, {x+100} {y+10}, {x+120} {y+20} S {x+150} {y+70}, {x+160} {y+70}', RED, 2.6)
    o += L(x+100, y+6, x+100, y+86, GREYP, 1.4, dash='4 3') + _t(x+100, y+106, 'L56', 14)
    return o
def reversal(x, y):                # authors -> title vs title -> authors
    o = card(x, y+10, 44, 56, 'title') + R(x+130, y+24, 50, 28, '#fff') + _t(x+155, y+43, 'authors', 14)
    o += L(x+50, y+30, x+124, y+30, INK, 2, True) + L(x+124, y+52, x+50, y+52, GREYP, 2, True)
    return o
def name_chain(x, y):              # give the first author; does the next one follow?
    o = R(x, y+30, 56, 26, PALE) + _t(x+28, y+48, '1st', 14) + L(x+60, y+43, x+86, y+43, INK, 1.8, True)
    o += R(x+92, y+30, 56, 26, '#fff') + _t(x+120, y+48, '2nd?', 14) + _t(x+80, y+90, 'via co-author network', 14)
    return o
def fabricated(x, y):              # where fabricated names come from: half not in the data
    cx, cy, r = x + 50, y + 50, 40
    o = C(cx, cy, r, '#fff') + P(f'M{cx} {cy-r} A{r} {r} 0 0 1 {cx} {cy+r} Z', INK, 1.6, PALE)
    o += _t(cx+92, cy-6, 'half: not', 14) + _t(cx+92, cy+14, 'in the data', 14)
    return o
def gap_icon(x, y):                # broken pipe
    o = (L(x, y+40, x+60, y+40, '#6A7385', 8) + L(x, y+40, x+60, y+40, '#EEF0F3', 4) +
         L(x+90, y+40, x+150, y+40, '#6A7385', 8) + L(x+90, y+40, x+150, y+40, '#EEF0F3', 4) + _t(x+75, y+48, '?', 26, '#6A7385'))
    return o
def realfake(x, y):
    return bars(x+20, y+10, [52, 46], ['states', 'confidence'], w=24, gap=50, base=y+90) + _t(x+92, y+24, '+0.05', 14)
def first_rest(x, y):              # initial-format names: first token weak, later tokens strong
    return toks(x+10, y, 4, 30, 6, {0: '#F1F2F4', 1: ACC, 2: ACC, 3: ACC}, {0: 'K.'}) + bars(x+30, y+40, [8, 40], ['first', 'later'], w=24, gap=50, base=y+96)
def given_helps(x, y):             # full given name in the top 10 -> surname easier
    o = R(x, y+20, 70, 26, PALE) + _t(x+35, y+38, 'Karin', 14) + L(x+76, y+33, x+100, y+33, INK, 1.8, True)
    o += R(x+106, y+20, 70, 26, '#fff') + _t(x+141, y+38, 'Coifman', 14)
    o += _t(x+90, y+80, 'vs only "K." → ≈ 0', 14)
    return o
