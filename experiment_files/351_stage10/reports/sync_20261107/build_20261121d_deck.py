"""2026-11-21d: HTML deck v48 -> v49.
Source = merged_deck/stage1_11_deck.html.before_20261121d (= published v48) -> merged_deck/stage1_11_deck.html.
  * slide 77 'Same title, different question': X1 authors − year at L48 +0.019 [0.012, 0.026] (first-author value) ->
    +0.024 [0.019, 0.030] (all-author test value, 381_stage13/summary_b1_xall/x1__all.csv); ceiling footnote added (limitation).
    Layout/style of slide 77 unchanged (the chart redesign awaits the user).
  * slide 78 'Patchscope and paraphrases': one exploratory pointer line to the new slide 79.
  * new slide after 78 (= new 79): exploratory checks of the title-position tests — L4 ceiling (summary_explore_l4audit_20261121),
    X4 source (summary_explore_x4_source_20261121), X3 checks (summary_explore_x3_checks_20261121), meaning twins
    (summary_explore_twins_20261121). All numbers read from those files and asserted.
  * old 79..99 -> 80..100; textual slide references remapped; contents menu rebuilt (100 slides). Writes build_20261121d_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, SANS

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
J = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
SRC = D / 'stage1_11_deck.html.before_20261121d'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 99
SL = [m.group(0) for m in ms]
aria = lambda x: re.search(r'aria-label="([^"]*)"', x).group(1)
assert aria(SL[76]) == 'Same title, different question' and aria(SL[77]) == 'Patchscope and paraphrases'
GREY = '#8a8f98'; CTRL = '#9AA3B2'; OR2 = '#B54708'
CJK = re.compile('[　-〿一-鿿＀-￯]')
def esc(x): return html.escape(str(x), quote=False)
def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')
def cif(lo, hi, d=3, sign=True): return f'[{fmt(lo, d, sign)}, {fmt(hi, d, sign)}]'
def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'
REC = {'values': {}}
# ------------------------------------------------------------------ data
X1 = [r for r in csv.DictReader(open(J / 'summary_b1_xall/x1__all.csv')) if r['split'] == 'test' and r['layer'] == '48' and r['stratum'] == 'all']
assert len(X1) == 1; amy = tuple(float(X1[0][k]) for k in ('a_minus_year', 'a_minus_year_lo', 'a_minus_year_hi'))
assert abs(amy[0] - 0.024) < 0.0006 and abs(amy[1] - 0.019) < 0.0006 and abs(amy[2] - 0.030) < 0.0006
L4 = {r['rep']: r for r in csv.DictReader(open(J / 'summary_explore_l4audit_20261121/l4audit.csv'))}
def l4(rep, k): return float(L4[rep][k])
assert abs(l4('bert_last_L1', 'ret_test') - 1.0) < 1e-9 and abs(l4('qwen_L0', 'ret_test') - 0.680) < 0.001
TW = list(csv.DictReader(open(J / 'summary_explore_twins_20261121/layer_similarity.csv')))
def tw(layer, set_): r = [x for x in TW if int(x['layer']) == layer and x['set'] == set_]; assert len(r) == 1; return r[0]
CNT = json.load(open(J / 'summary_explore_twins_20261121/counts.json'))
assert CNT['mutual_nn_both_models'] == 106 and CNT['bert>=0.9&mpnet>=0.8']['n'] == 7
X4R = (J / 'summary_explore_x4_source_20261121/report.md').read_text()
for frag in ('| author_surname_first@8 | text bert surname_first | +0.180 | +0.076 | +0.104 [+0.029, +0.180] |',
             '| year_informative@40 | text bert year | +0.158 | +0.163 | -0.005 [-0.082, +0.072] |',
             'Counts: (a) 0, (b) 8, (c) 99, any 104 of 1178.',
             '| author_surname_first@8 | +0.0663 [+0.0454, +0.0884] | +0.0663 [+0.0454, +0.0884] | +0.0667 [+0.0456, +0.0890] | +0.0640 [+0.0420, +0.0871] |',
             '| author_surname_first@8 | bert | +0.0348 | +0.0761 | +0.0881 | +0.0086 [-0.0022, +0.0202] |',
             '| Qwen author_surname_first | +0.0834 [+0.0417, +0.1252] |'):
    assert frag in X4R, frag
X3R = (J / 'summary_explore_x3_checks_20261121/report.md').read_text()
for frag in ('| all-mpnet-base-v2 · mean (L12) | +0.30 | +0.60 [+0.54, +0.67] (Qwen best L36, +0.49) | L32 +0.10 [+0.06, +0.15]; L36 +0.20 [+0.15, +0.24]; L40 +0.07 [+0.03, +0.12] |',
             '| all-mpnet-base-v2 · mean (L12) | +1.52 | +0.92 [+0.50, +1.47] (Qwen best L36, +1.65) | none |',
             '| citations: low / high half (median 29) | gL48 | 556.0 / 554.0 | -0.008 [-0.024, +0.008] | +0.025 [+0.010, +0.040] | +0.033 [+0.011, +0.056] |'):
    assert frag in X3R, frag
X3B = list(csv.DictReader(open(J / 'summary_explore_x3_checks_20261121/B_familiarity_regroup.csv')))
REC['x3_B_columns'] = list(X3B[0].keys()) if X3B else []

# ------------------------------------------------------------------ slide 77: number fix + ceiling footnote
s77 = SL[76]
old = 'authors − year within ±0.02, except a small +0.019 at L48<span class="src">(same, [0.012, 0.026])</span>'
assert s77.count(old) == 1
s77 = s77.replace(old, f'authors − year within ±0.02, except a small {fmt(amy[0])} at L48<span class="src">(all authors, test {cif(amy[1], amy[2])}; summary_b1_xall/x1__all.csv)</span>')
foot = ('<div class="fxn" style="left:70px;top:612px;width:820px"><span class="nn"><b style="color:#B54708">Exploratory · ceiling:</b> '
        'this test is ceiling-limited at the title position: the title text is identical under the three questions, so the title states are nearly the same '
        '(same paper: cosine 0.998 at L4, 0.983 at L24; two papers ≈ 0.45), retrieval is already 1.000 at L4 and a text-only BERT reaches 1.000 from its layer 1. '
        'M3 and retrieval cannot separate paper identity on their own; X1’s task independence follows from the near-identical states and is not a finding about identity. '
        '· summary_explore_l4audit_20261121</span></div>')
s77 = s77.replace('<span class="pg"></span>', '<span class="pg"></span>' + foot, 1)
REC['values']['s77'] = f'authors − year L48 {amy}'
# ------------------------------------------------------------------ slide 78 pointer
s78 = SL[77]
ptr = ('<div class="fxn" style="left:70px;top:612px;width:820px"><span class="nn"><b style="color:#B54708">Exploratory checks → slide 79:</b> '
       'X4 surname at L8 survives removing literal overlap and a text-only baseline; the year at L40 does not beat a text model; '
       'X3 matches a text model for most layers and tracks citations, not recognition.</span></div>')
s78 = s78.replace('<span class="pg"></span>', '<span class="pg"></span>' + ptr, 1)

# ------------------------------------------------------------------ new slide (79)
def slide_n():
    pid = 'xtp'; vals = []
    bo = L.frame(pid, 'What the title-position tests can and cannot separate',
                 'Four checks on existing data: the L4 ceiling, Patchscope (X4), paraphrases (X3), meaning twins', 'Meaning or this paper?', title_fs=42)
    bd, bw = L.badge(70, 124, 'Exploratory (post hoc, not pre-registered)', col=OR2, fs=16); bo += bd
    # panel 1: ceiling — retrieval by layer, Qwen vs BERT
    x0 = 70; bo += T(x0, 186, '1 · The ceiling: same paper, three questions', 16, INK, weight=700)
    ax = Ax(x0 + 46, 204, 260, 150, 0, 12, 0.6, 1.02)
    bo += ax.frame([0, 2, 4, 6, 8, 12], [0.6, 0.8, 1.0], xlab=lambda v: f'L{v}', ylab=lambda v: f'{v:.1f}', title=None, ytitle='retrieval')
    bl = [(k, l4(f'bert_last_L{k}', 'ret_test')) for k in range(0, 13) if f'bert_last_L{k}' in L4]
    bo += ax.line([k for k, _ in bl], [v for _, v in bl], CTRL, 2.2, r=2.6)
    X5 = (J / 'reports/x5_retrieval.md').read_text()
    assert '| L4 | test | 582 | +1.000 [+1.000, +1.000]' in X5 and '| L8 | test | 582 | +1.000 [+1.000, +1.000]' in X5
    qw = [(0, l4('qwen_L0', 'ret_test')), (4, 1.0), (8, 1.0)]
    bo += ax.line([k for k, _ in qw], [v for _, v in qw], BL, 2.8, r=3.4)
    bo += ax.hline(1.0, OR, '4 4', 1.4)
    bo += L.legend(x0 + 46, 378, [('Qwen', BL, 'line'), ('BERT (text only)', CTRL, 'line'), ('ceiling', OR, 'dash')], fs=12, gap=10)
    vals.append('ret Qwen ' + ', '.join(f'L{k} {v:.3f}' for k, v in qw) + ' | BERT ' + ', '.join(f'L{k} {v:.3f}' for k, v in bl))
    bo += ntext(x0, 404, 'Qwen L4: T 0.98–1.00, retrieval 1.000 → no room above L4')
    bo += ntext(x0, 418, 'L4 pre-registered for M3 before data (add. 2); X5 by analogy')
    bo += f'<text x="{x0}" y="436" font-size="12.5" fill="{INK}" font-style="italic" font-family="\'STIX Two Math\',\'Cambria Math\',\'DejaVu Serif\',serif">retrieval = top-1 same paper across questions</text>'
    bo += ntext(x0, 450, 'n = 9,108 papers (test 582) · bert-base-uncased')
    # panel 2: meaning twins similarity by layer
    x1 = 430; bo += T(x1, 186, '4 · Meaning twins: real papers, same meaning', 16, INK, weight=700)
    ax2 = Ax(x1 + 46, 204, 270, 150, 4, 63, 0, 0.9)
    bo += ax2.frame([4, 16, 32, 48, 63], [0, 0.4, 0.8], ylab=lambda v: f'{v:.1f}', title=None, ytitle='centred cosine')
    LYS = sorted({int(x['layer']) for x in TW})
    for set_, col, w in (('same paper paraphrase (X3)', BL, 2.8), ('twins (all mutual NN)', OR, 2.8), ('lexical neighbour D (X3)', CTRL, 2.2), ('random pairs', '#C3C9D2', 1.6)):
        ys = [float(tw(l, set_)['mean_cos']) for l in LYS]
        bo += ax2.line(LYS, ys, col, w, r=2.6)
        vals.append(f'{set_}: ' + ', '.join(f'L{l} {v:.3f}' for l, v in zip(LYS, ys)))
    bo += L.legend(x1 + 46, 378, [('paraphrase', BL, 'line'), ('twins', OR, 'line'), ('word-matched D', CTRL, 'line')], fs=12, gap=10)
    t4, t63 = float(tw(4, 'twins (all mutual NN)')['mean_cos']), float(tw(63, 'twins (all mutual NN)')['mean_cos'])
    bo += ntext(x1, 404, f'twins {t4:.2f} (L4) → {t63:.2f} (L63): flat, no identity layer')
    bo += ntext(x1, 418, '106 candidate pairs, 7 strict → feasibility weak')
    bo += f'<text x="{x1}" y="436" font-size="12.5" fill="{INK}" font-style="italic" font-family="\'STIX Two Math\',\'Cambria Math\',\'DejaVu Serif\',serif">cos(h_A − μ, h_B − μ), last title token</text>'
    bo += ntext(x1, 450, 'n = 106 twin pairs · 1,137 paraphrase / D pairs')
    # panels 3-4: X4 and X3 numbers
    x2 = 800; bo += T(x2, 186, '2 · X4: where the L8 surname signal comes from', 16, INK, weight=700)
    lines2 = [('literal overlap ≈ 0: ', 'D +0.064 without the 104 flagged titles vs +0.066 with them'),
              ('beyond a text model: ', 'surname L8 Qwen − BERT +0.104 [0.029, 0.180]'),
              ('recognised papers: ', 'target − control +0.083 [0.042, 0.125]'),
              ('year L40: ', 'Qwen − BERT −0.005 [−0.082, +0.072] → not beyond text'),
              ('topic prior: ', 'not measured directly (proxy slope +0.009 [−0.002, +0.020])')]
    y = 206
    for a_, b_ in lines2:
        t, h_ = para(x2, y, a_ + b_, 12.5, 410, INK, lh=15); bo += t; y += h_ + 2
    bo += f'<text x="{x2}" y="{y + 12:.0f}" font-size="12.5" fill="{INK}" font-style="italic" font-family="\'STIX Two Math\',\'Cambria Math\',\'DejaVu Serif\',serif">D = decode(own title state) − decode(partner)</text>'
    bo += ntext(x2, y + 26, 'n = 1,178 papers · effect = mean / sd · team CI')
    y3 = y + 52; bo += T(x2, y3, '3 · X3: paraphrase advantage vs a text model', 16, INK, weight=700)
    lines3 = [('all-mpnet reaches 60% [54, 67] of Qwen; ', 'Qwen above it only at L32–L40'),
              ('matched-D subset: ', '92% [50, 147], no layer significant (all-mpnet trained on scholarly pairs)'),
              ('target = control: ', 'G′ difference 0.000 [−0.017, 0.018]; retention 0.898 vs 0.898'),
              ('citations, high − low: ', '+0.015 to +0.033 at L24–L48 → exposure, not the recognition label')]
    y = y3 + 20
    for a_, b_ in lines3:
        t, h_ = para(x2, y, a_ + b_, 12.5, 410, INK, lh=15); bo += t; y += h_ + 2
    bo += f'<text x="{x2}" y="{y + 12:.0f}" font-size="12.5" fill="{INK}" font-style="italic" font-family="\'STIX Two Math\',\'Cambria Math\',\'DejaVu Serif\',serif">G′ = (para − D) / (orig − D) of the state similarity</text>'
    bo += ntext(x2, y + 26, 'n = 1,110 papers (matched D 66) · team CI')
    REC['right_bottom'] = y + 26
    bold = ('Exploratory: the title-position tests are ceiling-limited (M3, retrieval, X1) or match a text-only model (X3, X4 year); '
            'what goes beyond text is the X4 surname signal for recognised papers. Separating meaning from identity needs inputs that differ (addendum 20: made-up titles).')
    t, h_ = para(70, 500, bold, 13, 690, INK, lh=16.6); bo += t.replace('<text ', '<text font-weight="700" ', 1)
    bo += L.footer('381_stage13/summary_explore_{l4audit,x4_source,x3_checks,twins}_20261121/', y=694)
    sec = L.section('Exploratory: what the title-position tests can and cannot separate', pid, bo)
    lead = '<div class="lead">← slide 78: Patchscope and paraphrases. <b>Here:</b> what do these tests separate? → title words, slide 80</div>'
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['values']['n'] = vals
    return sec

N = slide_n()
order = SL[:76] + [s77, s78, N] + SL[78:]
assert len(order) == 100
def newnum(n): return n if n <= 78 else n + 1
def remap(t):
    def r(m):
        a = int(m.group(2)); out = m.group(1) + str(newnum(a))
        if m.group(4): out += m.group(3) + str(newnum(int(m.group(4))))
        return out
    return re.sub(r'(\bslides? )(\d{1,3})(?:([–-])(\d{1,3}))?', r, t)
fixed = []
for k, sec in enumerate(order):
    if sec is N: continue
    new = remap(sec)
    if new != sec: fixed.append(k + 1)
    order[k] = new
REC['refs_remapped_on_slides'] = fixed
head, tail = s[:ms[0].start()], s[ms[-1].end():]
between = [s[ms[i].end():ms[i + 1].start()] for i in range(98)]
assert all(x in ('', '\n') for x in between)
o = head + '\n'.join(order) + tail
m = re.search(r'<nav class="toc-list" aria-label="All slides">(.*?)</nav></div>', o, re.S)
groups = re.findall(r'<section class="toc-g" aria-labelledby="toc-h(\w+)"><h3 class="toc-h" id="toc-h\w+">(.*?)<span class="toc-r">(.*?)</span></h3><ul>(.*?)</ul></section>', m.group(1), re.S)
titles, gstart = [], []
for gid, name, rng, ul in groups:
    its = re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', ul); gstart.append((gid, len(titles), name))
    for n_, t_ in its: assert int(n_) == len(titles) + 1; titles.append(t_)
assert len(titles) == 99
titles = titles[:78] + [esc('What the title-position tests can and cannot separate')] + titles[78:]
gstart = [(gid, (a + 1 if a + 1 <= 78 else a + 2) - 1, name) for gid, a, name in gstart]
grp = []
for j, (gid, a, name) in enumerate(gstart):
    b_ = gstart[j + 1][1] if j + 1 < len(gstart) else 100
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span><span class="toc-t">{titles[k]}</span></a></li>' for k in range(a, b_))
    rng = f'{a + 1}–{b_}' if b_ - a > 1 else f'{a + 1}'
    grp.append(f'<section class="toc-g" aria-labelledby="toc-h{gid}"><h3 class="toc-h" id="toc-h{gid}">{name}<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
o = o[:m.start(1)] + ''.join(grp) + o[m.end(1):]
assert o.count('<span class="toc-cnt">99 slides</span>') == 1
o = o.replace('<span class="toc-cnt">99 slides</span>', '<span class="toc-cnt">100 slides</span>')
vis = re.sub(r'<script.*?</script>|<style.*?</style>|data:[^"]+', '', N, flags=re.S)
assert not CJK.search(re.sub(r'<[^>]+>', ' ', vis))
OUT.write_text(o, encoding='utf-8')
REC['toc'] = [{'id': g, 'start': a + 1, 'name': n} for g, a, n in gstart]
(Path(__file__).parent / 'build_20261121d_deck.json').write_text(json.dumps(REC, indent=1, ensure_ascii=False))
print('ok', REC['right_bottom'], REC['toc'], 'remapped on', fixed)
