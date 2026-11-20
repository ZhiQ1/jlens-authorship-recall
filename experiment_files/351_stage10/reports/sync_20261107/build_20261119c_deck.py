"""2026-11-19c: addendum 18b item 2, FIXED step-2 sensitivity result in the merged HTML deck. Source = current deck backed up as
merged_deck/stage1_11_deck.html.before_20261119c -> merged_deck/stage1_11_deck.html (94 slides, nothing moved). Idempotent.
  S73 (item 2) rebuilt: same main chart; the right panel is now a forest of the 11 fixed step-2 windows (rule met for name <- title in 7 of 11,
  L42-L57; no other edge wins); badge "robust"; lower third without "rerun pending".
  Every "robustness open / not established / rerun pending" elsewhere (S44, S51, S68, S86, S87) ->
  "robust to window placement (fixed step-2 check: 7 of 11 overlapping windows L42-L57, same edge); effects small (<= 3.5% of S)".
Numbers from 381_stage13/summary_a18b_item2/ and summary_a18b_item2_step2_fix/ (asserted). Writes build_20261119c_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, GR, RD, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
R13 = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
SRC = D / 'stage1_11_deck.html.before_20261119c'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 94, len(ms)
S = {k + 1: m.group(0) for k, m in enumerate(ms)}
assert 'Addendum 18b item 2: windowed attention blocking' in S[73]
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


t2 = rows(R13 / 'summary_a18b_item2/item2_table.csv'); k2 = {r['window']: r for r in rows(R13 / 'summary_a18b_item2/item2_criterion.csv')}
kf = {r['window']: r for r in rows(R13 / 'summary_a18b_item2_step2_fix/item2_criterion.csv')}
tfx = rows(R13 / 'summary_a18b_item2_step2_fix/item2_table.csv')
WIN = ['L40-43', 'L44-47', 'L48-51', 'L52-55', 'L56-59', 'L60-63']
EDG = ['name<-title', 'name<-tail', 'tail<-title', 'colon<-title', 'name<-colon']
EDL = {'name<-title': 'name ← title', 'name<-tail': 'name ← tail', 'tail<-title': 'tail ← title', 'colon<-title': '“:” ← title', 'name<-colon': 'name ← “:”'}
COLE = {'name<-title': OR, 'name<-tail': BL, 'tail<-title': GR, 'colon<-title': PU, 'name<-colon': GY}
MET = [w for w in WIN if k2[w]['verdict'].startswith('information')]
WSF = list(kf); METF = [w for w in WSF if kf[w]['verdict'].startswith('information')]
assert MET == ['L44-47', 'L48-51', 'L52-55'] and all(k2[w]['top_edge'] == 'name<-title' for w in MET)
assert METF == ['L42-45', 'L44-47', 'L46-49', 'L48-51', 'L50-53', 'L52-55', 'L54-57'] and all(kf[w]['top_edge'] == 'name<-title' for w in METF) and len(WSF) == 11
assert abs(float(kf['L48-51']['top_loss']) - 0.0115) < 6e-5 and abs(max(float(r['share_of_S']) for r in tfx) - 0.035) < 0.0006
T2 = {(r['window'], r['edge']): {k: float(v) for k, v in r.items() if k not in ('window', 'edge')} for r in t2}
lc = lambda w: '%s [%s, %s]' % (fmt(float(k2[w]['top_loss']), 4), fmt(float(k2[w]['top_lo']), 4), fmt(float(k2[w]['top_hi']), 4))


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


pid = 'r18b2'
b = L.frame(pid, 'One attention edge at a time: name ← title, but small',
            'Addendum 18b item 2 (locked 2026-11-17) · cut one edge (all heads) inside one 4-layer window · S = true − mean of 5 false titles · 600 papers',
            'Stage 13 · 18b item 2', title_fs=40)
bd, _ = L.badge(70, 124, 'Locked rule met in 3 windows · robust'); b += bd
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
o = T(690, 199, 'Fixed step-2 check: 11 overlapping windows', 17, INK, weight=700)
fr = []
for w in WSF:
    r = kf[w]; met = w in METF
    fr.append((w.replace('-', '–'), float(r['top_loss']), float(r['top_lo']), float(r['top_hi']), OR if met else GY, 1.0 if met else 0.6,
               EDL[r['top_edge']] + (' · met' if met else ' · not met')))
desc.append('fixed step-2 top edge: ' + '; '.join('%s %s %s [%s, %s]%s' % (w, EDL[kf[w]['top_edge']], fmt(float(kf[w]['top_loss']), 4), fmt(float(kf[w]['top_lo']), 4),
            fmt(float(kf[w]['top_hi']), 4), ' met' if w in METF else '') for w in WSF))
fo_, fh_ = L.forest(690, 214, 520, fr, -0.002, 0.015, [0, 0.01], rowh=14.5, labw=80, fs=11.5)
o += fo_.replace('>+0.01<', '>+0.010<')
o += ntext(690, 406, 'n = 600 papers · top-edge loss, team 95% CI (“met” also needs paired CIs > 0)')
o += T(690, 428, 'robust to window placement: rule met for name ← title in', 13.5, INK)
o += T(690, 445, '7 of 11 windows (L42–L57), incl. all 3 above; no other edge wins', 13.5, INK)
o += T(690, 462, 'largest loss +0.0115 (L48–51) = 3.5% of S(none)', 13.5, INK)
b += o
b += lower('How computed: loss = S(none) − S(config), S = paper-mean nlr(true title) − mean of 5 false titles at the output; one edge (all heads) masked inside one '
           '4-layer window; rule: the top edge’s CI > 0 and its paired difference to every other edge CI > 0. 600 papers, paired team bootstrap ×2,000.',
           'Locked rule met in L44–47, L48–51, L52–55, each time name ← title: %s, %s, %s; not met in L40–43, L56–59, L60–63. Robust to window placement.'
           % (lc('L44-47'), lc('L48-51'), lc('L52-55')),
           'Caveats: effects small (≤ 3.5% of S per edge and window); fixed step-2 check: 7 of 11 overlapping windows L42–L57, same edge (the first step-2 run was '
           'invalid and is superseded); unblocked ranks match the stored rows in 0.63 / 0.51 of rows (WARN, bf16), continued by rule.',
           '381_stage13/summary_a18b_item2/, summary_a18b_item2_step2_fix/ (item2_table.csv, item2_criterion.csv) · config/prereg_addendum18b.md')
b = b.replace('<rect width="1280" height="720" fill="url(#%sg)"/>' % pid, '<rect width="1280" height="720" fill="url(#%sg)"/><desc>Plotted — %s</desc>' % (pid, esc(' | '.join(desc))), 1)
NEW2 = new_section('Addendum 18b item 2: windowed attention blocking', b,
                   '← slide 72: names carry it from L48. <b>Here:</b> which attention edge brings it? → the L52–L56 MLP step, slide 74')

S[73] = NEW2; note(73, 'item 2 rebuilt: fixed step-2 forest, robust')
ROB = 'robust to window placement (fixed step-2 check: 7 of 11 overlapping windows L42–L57, same edge); effects small (≤ 3.5% of S)'
rep(44, '/ rule met, robustness open → slides 72–73', '/ rule met, robust to window placement → slides 72–73', 'robust')
rep(51, 'one attention edge costs ≤ 3.4% of S (item 2, locked rule met in L44–L55, robustness open)',
    'one attention edge costs ≤ 3.5% of S (item 2, locked rule met in L44–L55, robust to window placement)', 'robust')
rep(68, 'but costs ≤ 3.4% of S (item 2) <span class="st c2">rule met</span>, robustness open → slide 73;',
    'but costs ≤ 3.5% of S (item 2) <span class="st c2">rule met</span>, robust → slide 73;', 'robust')
rep(86, 'costs ≤ 3.4% of S; name ← title is the largest in L44–L55 <span class="st c2">rule met</span> (robustness open: the sensitivity run had a code error, rerun pending) → slide 73.',
    'costs ≤ 3.5% of S; name ← title is the largest in L44–L55 <span class="st c2">rule met</span>, robust to window placement (fixed step-2 check: 7 of 11 overlapping windows L42–L57, same edge) → slide 73.', 'robust')
rep(87, 'item 2: robustness not established (the step-2 sensitivity run had a window-assignment error; rerun pending).', 'item 2: ' + ROB + '.', 'robust')
vis = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<desc>.*?</desc>|data:[^"]+', '', ''.join(S.values()), flags=re.S)))
assert not re.search(r'robustness open|rerun pending|robustness not established', vis)
assert not CJK.search(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<desc>.*?</desc>', '', S[73], flags=re.S))))
out = s
for k in sorted(CHANGED, reverse=True):
    m = ms[k - 1]; out = out[:m.start()] + S[k] + out[m.end():]
OUT.write_text(out, encoding='utf-8')
json.dump({'source': str(SRC), 'changed': {str(k): v for k, v in CHANGED.items()}}, open(Path(__file__).with_suffix('.json'), 'w'), indent=1)
print('changed:', CHANGED)
