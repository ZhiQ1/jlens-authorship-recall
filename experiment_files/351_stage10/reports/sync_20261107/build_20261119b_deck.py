"""2026-11-19b: the last two addendum 18b results (items 3 and 2) woven into the merged HTML deck by topic, between the route slide
(v40 S71 "Stage 12: where the paper information travels") and item 6 (v40 S72), as in the main pptx v22 and integration_map_v20.md.
Source = merged_deck/stage1_11_deck.html.before_20261119b (= published v40) -> merged_deck/stage1_11_deck.html. Idempotent.
  NEW S72  item 3, per-cell patching: recovery by position group x layer (five-title mean, CI bands) + target − control panel
  NEW S73  item 2, windowed attention blocking: loss by window x edge (bars, CIs, locked-rule verdict) + per-window rule-check forest.
           The step-2 sensitivity run is INVALID (a18b_item2.py win_of assigns a layer to the FIRST window containing it, so overlapping
           windows except L40-43 blocked only their last two layers) -> not shown; wording "robustness not established, rerun pending".
  All numbers read from 381_stage13/summary_a18b_item3/, summary_a18b_item2/, summary_a18b_item2_step2/ (asserted).
  "slide N" references with N >= 72 on all old slides -> N + 2.
  Synthesis edits: S44 Line C opener box, S51 Line C summary (one bullet), S68 hypothesis box (Route line), S69 layer-order box,
  S71 lead line (new), S72->74 item 6 lead, S84->86 "What we learned, continued" (new row), S85->87 limits box.
v40 rules kept: no process labels, figure on every slide from 43, no visible Chinese, lower third <= 2 lines each for how / verdict /
caveat, footer one line at y 693 clear of nav. Writes build_20261119b_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, GR, RD, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
SRC = D / 'stage1_11_deck.html.before_20261119b'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 92, len(ms)
head, tail = s[:ms[0].start()], s[ms[-1].end():]
gaps = [s[ms[i].end():ms[i + 1].start()] for i in range(len(ms) - 1)]
S = {k + 1: m.group(0) for k, m in enumerate(ms)}
ORIG = dict(S)
assert 'Stage 12: where the paper information travels' in S[71] and 'item 6: MLP memory lookup' in S[72]
assert 'What we learned, continued' in S[84] and 'Limits (Stage 12–13)' in S[85]
GREY = '#8a8f98'; PU = '#8E6CC8'; GY = '#9AA3B2'; GREYT = '#4B5363'
CJK = re.compile('[　-〿一-鿿＀-￯]')
CHANGED = {}


def note(k, msg): CHANGED.setdefault(k, []).append(msg)


def rep(k, a, b, msg, count=1):
    assert S[k].count(a) == count, (k, S[k].count(a), a[:90])
    S[k] = S[k].replace(a, b); note(k, msg)


def esc(x): return html.escape(str(x), quote=False)


def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')


def rows(p): return list(csv.DictReader(open(p, encoding='utf-8')))


# ======================================================================= data
m3 = rows(R13 / 'summary_a18b_item3/item3_mean5.csv')
hc3 = json.load(open(R13 / 'summary_a18b_item3/item3_hardchecks.json'))
R3 = {(r['group'], int(r['layer'])): {k: (float(v) if k not in ('group',) else v) for k, v in r.items()} for r in m3}
for (g, l), v in {('names', 40): 0.176, ('names', 47): 0.314, ('names', 48): 0.605, ('names', 52): 0.835, ('names', 56): 0.876, ('colon', 48): 0.073,
                  ('colon', 52): 0.177, ('p5', 46): 0.081, ('whole_tail', 40): 0.292, ('whole_tail', 48): 0.804, ('whole_tail', 52): 0.988}.items():
    assert abs(R3[(g, l)]['recovery'] - v) < 0.0006, (g, l)
assert {R3[k]['n_papers'] for k in R3 if k[0] == 'p9'} == {363.0} and {R3[k]['n_papers'] for k in R3 if k[0] != 'p9'} == {600.0}
assert hc3['hardcheck_a']['status'] == 'WARN' and hc3['hardcheck_b']['48']['status'] == 'WARN'
t2 = rows(R13 / 'summary_a18b_item2/item2_table.csv'); k2 = {r['window']: r for r in rows(R13 / 'summary_a18b_item2/item2_criterion.csv')}
t2s = rows(R13 / 'summary_a18b_item2_step2/item2_table.csv'); k2s = {r['window']: r for r in rows(R13 / 'summary_a18b_item2_step2/item2_criterion.csv')}
WIN = ['L40-43', 'L44-47', 'L48-51', 'L52-55', 'L56-59', 'L60-63']
EDG = ['name<-title', 'name<-tail', 'tail<-title', 'colon<-title', 'name<-colon']
EDL = {'name<-title': 'name ← title', 'name<-tail': 'name ← tail', 'tail<-title': 'tail ← title', 'colon<-title': '“:” ← title', 'name<-colon': 'name ← “:”'}
COLE = {'name<-title': OR, 'name<-tail': BL, 'tail<-title': GR, 'colon<-title': PU, 'name<-colon': GY}
MET = [w for w in WIN if k2[w]['verdict'].startswith('information')]
MET_S = [w for w in k2s if k2s[w]['verdict'].startswith('information')]
assert MET == ['L44-47', 'L48-51', 'L52-55'] and all(k2[w]['top_edge'] == 'name<-title' for w in MET)
assert MET_S == ['L42-45', 'L52-55'] and len(k2s) == 11
assert abs(max(float(r['share_of_S']) for r in t2) - 0.034) < 0.0006
T2 = {(r['window'], r['edge']): {k: float(v) for k, v in r.items() if k not in ('window', 'edge')} for r in t2}
T2S = {(r['window'], r['edge']): {k: float(v) for k, v in r.items() if k not in ('window', 'edge')} for r in t2s}
WS = list(k2s)
EFF = {w: ('L40–43' if w == 'L40-43' else 'L%d–%d' % (int(w[1:3]) + 2, int(w[1:3]) + 3)) for w in WS}
lc = lambda w: '%s [%s, %s]' % (fmt(float(k2[w]['top_loss']), 4), fmt(float(k2[w]['top_lo']), 4), fmt(float(k2[w]['top_hi']), 4))
assert lc('L48-51') == '+0.0112 [+0.0084, +0.0138]'


# ======================================================================= lower third (<= 2 lines each) + footer (declutter rules)
def lower(how, verdict, caveat, foot):
    o, y = '', 500.0
    t, h = para(70, y, how, 10.5, 1140, GREYT, lh=13.4); assert h <= 2 * 13.4 + 0.1, how; o += t; y += h + 6 + 13
    t, h = para(70, y, verdict, 13, 1140, INK, lh=16.6); assert h <= 2 * 16.6 + 0.1, verdict; o += t.replace('<text ', '<text font-weight="700" ', 1); y += h + 6
    t, h = para(70, y, caveat, 12, 1140, GREYT, lh=15.4); assert h <= 2 * 15.4 + 0.1, caveat; o += t
    assert L.width(foot, 11) < 1140 * 1.0
    o += f'<text x="70" y="693" class="src" font-size="11" fill="{GREY}" text-anchor="start">{esc(foot)}</text>'
    return o


def ntext(x, y, s_, fs=12): return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="start" font-family="{SANS}">{esc(s_)}</text>'


def new_section(aria, body, lead):
    sec = L.section(aria, aria[:4].lower().replace(' ', ''), body)
    return sec[:-len('</section>')] + f'<div class="lead">{lead}</div></section>'


# ======================================================================= NEW item 3 slide
LAY = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 56, 60]
XP = {l: (l - 40 if l <= 52 else (13.8 if l == 56 else 15.0)) for l in LAY}
G3 = [('names', 'names', BL, None, 3), ('whole_tail', 'whole tail (all)', INK, '6 4', 2.2), ('colon', '“:”', OR, None, 2.6),
      ('p5', 'year tens digit', GR, None, 2), ('p9', 'closing quote (363)', PU, None, 1.8), ('other_tail', 'other tail', GY, None, 1.8)]
pid = 'r18b3'
b = L.frame(pid, 'Name positions carry the title, layer by layer',
            'Addendum 18b item 3 (design locked 2026-11-17, no decision rule → descriptive) · copy one position group true → false at one layer · 5 false titles · 600 papers',
            'Stage 13 · 18b item 3', title_fs=40)
bd, _ = L.badge(70, 124, 'Descriptive (no locked criterion)'); b += bd
fo, _ = L.formula(620, 120, 'R(g, l) = mean_p[ nlr_patch(g, l) − nlr_false ] / mean_p[ nlr_true − nlr_false ]',
                  'g = one position group copied alone at layer l; mean over 5 false titles', fs=16, w=590); b += fo
ax = Ax(120, 210, 500, 186, -0.3, 15.3, -0.04, 1.0)
o = ax.frame([], [0, 0.25, 0.5, 0.75, 1.0], title='Recovery R by position group and layer', ytitle='R')
for l in (40, 44, 48, 52, 56, 60):
    X = ax.X(XP[l]); o += f'<line x1="{X:.1f}" y1="396.0" x2="{X:.1f}" y2="401.0" stroke="{INK}" stroke-width="1.6"/>' + T(X, 415, f'L{l}', 14, PEN, 'middle')
o += f'<rect x="{ax.X(12.35):.1f}" y="392" width="{ax.X(13.45) - ax.X(12.35):.1f}" height="8" fill="#FFFBFB"/>' + T(ax.X(12.9), 404, '//', 12, PEN, 'middle')
desc = []
for g, lab, col, dash, w in G3:
    xs = [XP[l] for l in LAY]; ys = [R3[(g, l)]['recovery'] for l in LAY]
    o += ax.band(xs, [R3[(g, l)]['lo'] for l in LAY], [R3[(g, l)]['hi'] for l in LAY], col, 0.15) + ax.line(xs, ys, col, w=w, dash=dash, r=2.4)
    desc.append(lab + ': ' + '; '.join('L%d %.3f [%.3f, %.3f]' % (l, R3[(g, l)]['recovery'], R3[(g, l)]['lo'], R3[(g, l)]['hi']) for l in LAY))
for l, g, col, dx, dy in [(48, 'names', BL, 20, 16), (52, 'names', BL, 0, 22), (52, 'colon', OR, 0, -9), (46, 'p5', GR, 0, -8), (40, 'names', BL, 14, -8)]:
    o += T(ax.X(XP[l]) + dx, ax.Y(R3[(g, l)]['recovery']) + dy, '%.3f' % R3[(g, l)]['recovery'], 12, col, 'middle', weight=700)
o += L.legend(120, 440, [(G3[0][1], BL, 'line'), (G3[1][1], INK, 'dash'), (G3[2][1], OR, 'line')], fs=12)
o += L.legend(120, 456, [(G3[3][1], GR, 'line'), (G3[4][1], PU, 'line'), (G3[5][1], GY, 'line')], fs=12)
o += ntext(120, 476, 'n = 600 papers (300 target + 300 control) · closing quote 363 · five-title mean · shaded = team 95% CI')
b += o
ax2 = Ax(760, 222, 330, 130, -0.3, 15.3, -0.16, 0.10)
o = T(690, 199, 'Target − control of R', 17, INK, weight=700)
o += ax2.frame([], [-0.15, -0.1, -0.05, 0, 0.05, 0.1], ylab=lambda v: ('%+.2f' % v).replace('-', '−') if v else '0')
for l in (40, 48, 52, 60):
    X = ax2.X(XP[l]); o += T(X, 368, f'L{l}', 13, PEN, 'middle')
o += ax2.hline(0, INK, '0', 1.4)
for g, lab, col, dash, w in G3[:3]:
    xs = [XP[l] for l in LAY]
    o += ax2.band(xs, [R3[(g, l)]['tc_lo'] for l in LAY], [R3[(g, l)]['tc_hi'] for l in LAY], col, 0.15)
    o += ax2.line(xs, [R3[(g, l)]['t_minus_c'] for l in LAY], col, w=2, dash=dash, r=2)
    desc.append(lab + ' T − C: ' + '; '.join('L%d %s' % (l, fmt(R3[(g, l)]['t_minus_c'])) for l in LAY))
o += ntext(690, 392, 'n = 300 target + 300 control papers')
o += T(690, 418, 'whole tail: T − C −0.076 to −0.093 at L40–L50 (L52 −0.024)', 13.5, INK)
o += T(690, 436, 'names: T − C > 0 only from L56 (+0.051)', 13.5, INK)
o += T(690, 454, 'whole tail 0.804 (L48), 0.988 (L52): stored 0.821 / 0.995 kept', 13.5, INK)
b += o
b += lower('How computed: R = mean_p[nlr(patched) − nlr(false)] / mean_p[nlr(true) − nlr(false)] for one position group g copied true → false at layer l (Stage 12 P1 '
           'estimand, paper means first), mean of the 5 false titles’ ratios; 6 groups × 15 layers. 600 papers, paired team bootstrap ×2,000.',
           'Descriptive: names carry most, 0.176 (L40) → 0.314 (L47) → 0.605 (L48) → 0.835 (L52); “:” joins late, 0.073 (L48) → 0.177 (L52); the year tens digit '
           'peaks at 0.081 (L46–L47) and fades to ≈ 0 by L56; quote and other tail ≤ 0.026.',
           'Caveats: no decision rule; hard checks WARN, continued by rule: row-wise rank match with the stored rows 0.72–0.81 (required 1.0, bf16 batch shapes); '
           '1,186-paper mean 0.821137 vs 0.821056 (tolerance 1e-6).',
           '381_stage13/summary_a18b_item3/ (item3_mean5.csv, item3_hardchecks.json) · config/prereg_addendum18b.md')
b = b.replace('<rect width="1280" height="720" fill="url(#%sg)"/>' % pid, '<rect width="1280" height="720" fill="url(#%sg)"/><desc>Plotted — %s</desc>' % (pid, esc(' | '.join(desc))), 1)
NEW3 = new_section('Addendum 18b item 3: per-cell patching', b,
                   '← slide 71: patching positions or one layer part. <b>Here:</b> which position group carries it? → which attention edge? slide 73')

# ======================================================================= NEW item 2 slide
pid = 'r18b2'
b = L.frame(pid, 'One attention edge at a time: name ← title, but small',
            'Addendum 18b item 2 (locked 2026-11-17) · cut one edge (all heads) inside one 4-layer window · S = true − mean of 5 false titles · 600 papers',
            'Stage 13 · 18b item 2', title_fs=40)
bd, _ = L.badge(70, 124, 'Locked rule met in 3 windows · robustness open'); b += bd
fo, _ = L.formula(620, 120, 'loss(e, w) = S(none) − S(edge e cut in window w)',
                  'S = mean_p nlr(true) − mean of 5 false titles; rule: top edge CI > 0 and paired CI > 0 vs every other edge', fs=16, w=590); b += fo
ax = Ax(120, 210, 500, 186, -0.5, 5.5, -0.003, 0.016)
o = ax.frame([], [0, 0.004, 0.008, 0.012, 0.016], ylab=lambda v: ('%.3f' % v) if v else '0', title='Loss of S by window and edge', ytitle='loss (nlr)')
desc = []
for i, w in enumerate(WIN):
    X = ax.X(i); o += f'<line x1="{X:.1f}" y1="396.0" x2="{X:.1f}" y2="401.0" stroke="{INK}" stroke-width="1.6"/>' + T(X, 415, w.replace('-', '–'), 14, PEN, 'middle')
o += ax.hline(0, INK, '0', 1.4)
bw = 13.5
for j, e in enumerate(EDG):
    for i, w in enumerate(WIN):
        r = T2[(w, e)]; X = ax.X(i) + (j - 2) * (bw + 1.5)
        y0, y1 = ax.Y(0), ax.Y(r['loss'])
        o += f'<rect x="{X - bw / 2:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{max(abs(y0 - y1), 0.6):.1f}" fill="{COLE[e]}" fill-opacity="0.85" stroke="{INK}" stroke-width="0.6"/>'
        o += f'<line x1="{X:.1f}" y1="{ax.Y(r["lo"]):.1f}" x2="{X:.1f}" y2="{ax.Y(r["hi"]):.1f}" stroke="{INK}" stroke-width="1"/>'
    desc.append(EDL[e] + ': ' + '; '.join('%s %s [%s, %s]' % (w, fmt(T2[(w, e)]['loss'], 4), fmt(T2[(w, e)]['lo'], 4), fmt(T2[(w, e)]['hi'], 4)) for w in WIN))
for i, w in enumerate(WIN):
    if w in MET: o += T(ax.X(i), ax.Y(float(k2[w]['top_hi'])) - 8, 'rule met', 13, OR, 'middle', weight=700)
    else: o += T(ax.X(i), ax.Y(0.0045 if i == 0 else 0.0028), 'not met', 12, PEN, 'middle')
o += T(ax.X(5.4), ax.Y(0.0152), 'S(none) = 0.328', 12, PEN, 'end')
o += L.legend(120, 440, [(EDL[e], COLE[e], 'box') for e in EDG[:3]], fs=12)
o += L.legend(120, 456, [(EDL[e], COLE[e], 'box') for e in EDG[3:]], fs=12)
o += ntext(120, 476, 'n = 600 papers (300 target + 300 control) · bars = loss, whiskers = paired team 95% CI')
b += o
o = T(690, 199, 'Rule check: top edge per window', 17, INK, weight=700)
fr = []
for w in WIN:
    r = k2[w]; met = w in MET
    fr.append((w.replace('-', '–'), float(r['top_loss']), float(r['top_lo']), float(r['top_hi']), OR if met else GY, 1.0 if met else 0.6,
               EDL[r['top_edge']] + (' · met' if met else ' · not met')))
fo_, fh_ = L.forest(690, 222, 520, fr, -0.002, 0.015, [0, 0.01], rowh=22, labw=80, fs=13)
o += fo_.replace('>+0.01<', '>+0.010<')
o += ntext(690, 392, 'n = 600 papers · top-edge loss, team 95% CI (“met” also needs paired CIs > 0)')
o += T(690, 418, 'one edge in one window: at most 3.4% of S(none) = 0.328', 13.5, INK)
o += T(690, 436, 'robustness not established: the step-2 sensitivity run had a', 13.5, INK)
o += T(690, 454, 'window-assignment error (not shown); rerun pending', 13.5, INK)
b += o
b += lower('How computed: loss = S(none) − S(config), S = paper-mean nlr(true title) − mean of 5 false titles at the output; one edge (all heads) masked inside one '
           '4-layer window; rule: the top edge’s CI > 0 and its paired difference to every other edge CI > 0. 600 papers, paired team bootstrap ×2,000.',
           'Locked rule met in L44–47, L48–51, L52–55, each time name ← title: %s, %s, %s; not met in L40–43, L56–59, L60–63. One edge costs ≤ 3.4%% of S.'
           % (lc('L44-47'), lc('L48-51'), lc('L52-55')),
           'Caveats: robustness not established (the step-2 sensitivity run had a window-assignment error; rerun pending); unblocked ranks match the stored rows in '
           '0.63 / 0.51 of rows (WARN, explicit mask, bf16), continued by rule.',
           '381_stage13/summary_a18b_item2/ (item2_table.csv, item2_criterion.csv) · config/prereg_addendum18b.md')
b = b.replace('<rect width="1280" height="720" fill="url(#%sg)"/>' % pid, '<rect width="1280" height="720" fill="url(#%sg)"/><desc>Plotted — %s</desc>' % (pid, esc(' | '.join(desc))), 1)
NEW2 = new_section('Addendum 18b item 2: windowed attention blocking', b,
                   '← slide 72: names carry it from L48. <b>Here:</b> which attention edge brings it? → the L52–L56 MLP step, slide 74')

# ======================================================================= remap "slide N" (N >= 72 -> N + 2) on all old slides
def remap(t):
    def one(m):
        a = int(m.group(2)); b_ = m.group(4)
        a2 = a + 2 if a >= 72 else a
        if b_ is None: return f'{m.group(1)}{a2}'
        b2 = int(b_) + 2 if int(b_) >= 72 else int(b_)
        return f'{m.group(1)}{a2}{m.group(3)}{b2}'
    parts = re.split(r'(data:[^"]+)', t)
    return ''.join(p if p.startswith('data:') else re.sub(r'(\bslides? )(\d{1,3})(–)?(\d{1,3})?', lambda m: one(m) if (m.group(3) is None) == (m.group(4) is None) else m.group(0), p) for p in parts)


for k in S:
    new = remap(S[k])
    if new != S[k]: S[k] = new; note(k, 'slide numbers remapped (+2 from 72)')

# ======================================================================= synthesis edits (old numbers; texts already remapped)
rep(44, ' → slide 74<br>Stage 4', ' → slide 74 · which positions and which attention edge carry it (items 3, 2) <span class="st c4">descriptive</span> / rule met, robustness open → slides 72–73<br>Stage 4',
    'opener box: items 3, 2 added')
rep(51, 'hardly along author-name directions (item 6, descriptive) → slide 74</li></ul>',
    'hardly along author-name directions (item 6, descriptive) → slide 74</li><li class="new">Names carry the title from L48 (<span class="b">0.84</span> by L52; item 3, descriptive); '
    'one attention edge costs ≤ 3.4% of S (item 2, locked rule met in L44–L55, robustness open) → slides 72–73</li></ul>', 'Line C summary: items 3, 2 bullet')
rep(68, '<b style="color:#3C78B4">Route:</b> L57–L61 written by MLPs (item 4) <span class="st c1">confirmed</span> → slide 75.',
    '<b style="color:#3C78B4">Route:</b> names carry the title from L48, “:” late (item 3) <span class="st c4">descriptive</span> → slide 72; name ← title is the largest single '
    'attention edge in L44–L55 but costs ≤ 3.4% of S (item 2) <span class="st c2">rule met</span>, robustness open → slide 73; L57–L61 written by MLPs (item 4) '
    '<span class="st c1">confirmed</span> → slide 75.', 'hypothesis box: Route line with items 3, 2')
rep(69, '<div class="addb" style="left:972px;top:548px;width:252px;font-size:14px"><b>Refined:</b> positions × layers before the name (item 1) <span class="st c3">exploratory</span> → slide 70; L57–L61',
    '<div class="addb" style="left:972px;top:566px;width:262px;font-size:13px;line-height:1.22"><b>Refined:</b> positions × layers before the name (item 1) <span class="st c3">exploratory</span> → slide 70; '
    'position groups × layers (item 3) <span class="st c4">descriptive</span> → slide 72; attention edges by window (item 2) → slide 73; L57–L61', 'layer-order box: items 3, 2')
rep(71, '<span class="pg"></span>', '<span class="pg"></span><div class="lead">→ finer: which position group (slide 72) and which attention edge (slide 73) carry it, layer by layer</div>',
    'lead line to the new slides')
rep(72, '← slide 71: attention at L48, then MLPs at L52–L56.', '← slides 71–73: the title is on the names by L48.', 'lead: links items 3, 2')
rep(84, 'row-gap:9px', 'row-gap:5px', 'rows tighter for the new row')
rep(84, '→ slide 74.</div>\n<div style="font-size:28px" class="k g">Exposure gap</div>',
    '→ slide 74.</div>\n<div style="font-size:28px" class="k b">Carried by the names</div><div class="v" style="font-size:16px">The title reaches the name positions mostly in the '
    'L47 → L48 step (recovery 0.31 → <span class="a">0.61</span>; 0.84 by L52); “:” joins late <span class="st c4">descriptive</span> (hard checks WARN) → slide 72. One attention edge '
    'cut in a 4-layer window costs ≤ 3.4% of S; name ← title is the largest in L44–L55 <span class="st c2">rule met</span> (robustness open: the sensitivity run had a code error, rerun pending) → slide 73.</div>\n'
    '<div style="font-size:28px" class="k g">Exposure gap</div>', 'new row: carried by the names (items 3, 2)')
rep(85, 'Addendum 16: teacher-forced preferences, greedy decoding only. C: not pre-registered.</div>',
    'Addendum 16: teacher-forced preferences, greedy decoding only. C: not pre-registered. Items 2, 3: 600-paper subsample, hard checks WARN; item 3 has no decision rule; '
    'item 2: robustness not established (the step-2 sensitivity run had a window-assignment error; rerun pending).</div>', 'limits box: items 2, 3')

# user decisions 2026-11-19 (via coordinator): (1) made-up names sentence verbatim; (2) slide 42 probe count = 1,395 (896 + 499);
# 1,863 = all papers kept after the title-reuse exclusion (X1-control pipeline), of which E4b uses 1,395 (E4b_4configs.csv, team split,
# title-reuse removed: target 788 + 108 = 896, control 491 + 8 = 499). The 1,863 sits inside the slide picture -> two small patches.
US = 'about half are not in the data, the same as the shuffled baseline (50.4% vs 50.5%); co-authors are only 4.0% (chance 1.3%)'
rep(82, '>Fabricated names: mostly people not in the data</text>', '>Fabricated names: about half are not in the data</text>', 'title: user sentence')
rep(82, 'Not supported (exploratory, not pre-registered): half of the fabricated names are people not in the data (50.4% [49.0, 51.7], shuffled 50.5%);</tspan>',
    'Not supported (exploratory, not pre-registered): about half are not in the data, the same as the shuffled baseline (50.4% vs 50.5%);</tspan>', 'verdict: user sentence')
rep(82, 'co-authors 4.0% (shuffled 1.3%), but T − C ≈ 0 with full-name matching.</tspan>', 'co-authors are only 4.0% (chance 1.3%); with full-name matching T − C ≈ 0.</tspan>', 'verdict: user sentence')
rep(84, 'Half are people not in the data (50.4%; shuffled baseline 50.5%): plausible names', 'A' + US[1:] + ': plausible names', 'made-up names row: user sentence')
PATCH = ('<div aria-hidden="true" style="position:absolute;left:1057px;top:109px;width:52px;height:22px;background:#FCFDF8;z-index:2;'
         'font-family:var(--hand);font-size:21px;line-height:22px;color:#6A7385;text-align:center">1,395</div>'
         '<div aria-hidden="true" style="position:absolute;left:971px;top:285px;width:32px;height:15px;background:#FFEEA0;z-index:2;'
         'font-family:var(--hand);font-size:14.5px;line-height:15px;color:#858D9C;text-align:center">1,395</div>')
rep(42, '<div class="fxn" style="left:70px;top:672px;width:1100px">', PATCH + '<div class="fxn" style="left:70px;top:672px;width:1100px">',
    'probe count in the picture corrected 1,863 -> 1,395 (896 + 499), matching the n line')
# ======================================================================= assemble
order = list(range(1, 72)) + ['N3', 'N2'] + list(range(72, 93))
S['N3'], S['N2'] = NEW3, NEW2
P = {o: i + 1 for i, o in enumerate(order)}
for k in ('N3', 'N2'):
    vis = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<desc>.*?</desc>', '', S[k], flags=re.S)))
    assert not CJK.search(vis), k
gl = gaps + [gaps[-1]] * 2
outp = head + ''.join(S[o] + (gl[i] if i < len(order) - 1 else '') for i, o in enumerate(order)) + tail
OUT.write_text(outp, encoding='utf-8')
json.dump({'source': str(SRC), 'order_new_to_v40': {P[o]: o for o in order}, 'changed_v40': {str(k): v for k, v in CHANGED.items()},
           'new': {'72': 'item 3 (per-cell patching)', '73': 'item 2 (windowed attention blocking)'}},
          open(Path(__file__).with_suffix('.json'), 'w'), indent=1)
print('slides', len(order)); print('changed (v40 numbers):', {k: v for k, v in CHANGED.items()})
