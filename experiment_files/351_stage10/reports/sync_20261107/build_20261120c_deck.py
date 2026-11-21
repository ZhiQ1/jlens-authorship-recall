"""2026-11-20c: exploratory citation median split of the Stage 11 sample woven into the merged HTML deck (v44 -> v45).
Source = merged_deck/stage1_11_deck.html.before_20261120c (= published v44) -> merged_deck/stage1_11_deck.html.
  * one new data slide after slide 91 ("Recovery by group: numerator and denominator", E1 recovery) = new 92; old 92..96 -> 93..97.
  * contents menu: one item inserted, ranges / '97 slides' updated. No slide references >= 92 exist in v44 (checked).
Numbers read from 381_stage13/summary_explore_citesplit_20261120/ (recovery_by_half.csv, lens_tc_by_half.csv, info.json).
Writes build_20261120c_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, GR, RD, PINK, LIGHT, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
C = Path('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_explore_citesplit_20261120')
SRC = D / 'stage1_11_deck.html.before_20261120c'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 96
SL = [m.group(0) for m in ms]
assert 'aria-label="Recovery by group: numerator and denominator"' in SL[90]
GREY = '#8a8f98'; SERIF = "'STIX Two Math','Cambria Math','DejaVu Serif','Times New Roman',serif"
CJK = re.compile('[　-〿一-鿿＀-￯]')
def esc(x): return html.escape(str(x), quote=False)
def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')
def cif(lo, hi, d=3, sign=True): return f'[{fmt(lo, d, sign)}, {fmt(hi, d, sign)}]'
def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'
INFO = json.load(open(C / 'info.json'))
assert INFO['median_citations'] == 31.0 and INFO['n'] == {'high/control': 296, 'high/target': 296, 'low/control': 297, 'low/target': 297} and INFO['NB'] == 2000
assert INFO['full_cohort_median'] == 66.0 and sum(INFO['full_n'].values()) == 6841
RR = list(csv.DictReader(open(C / 'recovery_by_half.csv')))
R = {(r['half'], r['group'], int(r['layer'])): r for r in RR if r['title'] == 'average'}
g = lambda h, gr, l, k='R': float(R[(h, gr, l)][k])
LT = list(csv.DictReader(open(C / 'lens_tc_by_half.csv')))
LZ = {(r['sample'], r['readout'], int(r['layer']), r['half']): r for r in LT if r['measure'] == 'spec_mean_nlr'}
lz = lambda smp, ro, l, h, k='tc': float(LZ[(smp, ro, l, h)][k])
EXP = [(('low', 'all', 48), 0.865), (('high', 'all', 48), 0.789), (('high - low', 'all', 48), -0.076), (('high - low', 'target', 48), -0.079),
       (('high - low', 'control', 48), -0.073), (('low', 'all', 52), 1.006), (('high', 'all', 52), 0.988), (('high - low', 'all', 52), -0.018),
       (('high - low', 'target - control', 48), -0.006), (('both', 'all', 48), 0.821)]
for k, v in EXP: assert abs(g(*k) - v) < 0.0006, (k, g(*k))
assert abs(lz('stage11_1186', 'jlens_public', 53, 'high - low') + 0.073) < 0.0006 and abs(lz('stage11_1186', 'jlens_public', 54, 'high - low') + 0.076) < 0.0006
assert abs(lz('supplement_full_cohort', 'jlens_public', 48, 'high - low') + 0.065) < 0.0006
LOGL = [40, 48, 50, 51, 52, 53, 54, 55, 56]
assert all(lz('stage11_1186', 'logit', l, 'high - low', 'lo') < 0 < lz('stage11_1186', 'logit', l, 'high - low', 'hi') for l in LOGL)
REC = {}

def slide():
    pid = 'cite1'
    b = L.frame(pid, 'More-cited papers: the title arrives a little later', 'Citation median split of the 1,186 Stage 11 papers (median 31; ties to the low half) · E1 tail patching, 5 false titles · lens readouts at the name positions',
                'Groups · citations', title_fs=46)
    bd, bw = L.badge(70, 124, 'Exploratory (post hoc, not pre-registered)', col='#B54708', fs=16); b += bd
    fm, fw = L.formula(1210 - 470, 118, 'R(l) = mean(patched − false) / mean(true − false)', 'state of the post-title tail copied true → false at layer l; mean of 5 false titles', fs=17, w=470); b += fm
    vals = []
    # left: R by layer, low vs high (all papers)
    LY = [40, 48, 50, 52, 56]
    ax = Ax(120, 222, 440, 200, 38, 58, 0.2, 1.05)
    b += ax.frame(LY, [0.25, 0.5, 0.75, 1.0], ylab=lambda v: f'{v:g}', title='Share of the gap recovered, by citation half', ytitle='R(l)')
    for h, col, lab in (('low', BL, 'low half (≤ 31 citations)'), ('high', OR, 'high half (≥ 32)')):
        ys = [g(h, 'all', l) for l in LY]
        b += ax.band(LY, [g(h, 'all', l, 'lo') for l in LY], [g(h, 'all', l, 'hi') for l in LY], col, 0.16) + ax.line(LY, ys, col, 2.6, r=3.5)
        vals.append(f'{h} R: ' + ', '.join(f'L{l} {v:.3f}' for l, v in zip(LY, ys)))
    for h, col, dx, dy, anc in (('low', BL, -8, -8, 'end'), ('high', OR, 8, 18, 'start')):
        v = g(h, 'all', 48); b += T(ax.X(48) + dx, ax.Y(v) + dy, f'{v:.3f}', 13, col, anc, weight=700)
    b += L.legend(120, 462, [('low half (≤ 31 citations)', BL, 'line'), ('high half (≥ 32)', OR, 'line')], fs=13, gap=14)
    b += ntext(120, 480, 'band = 95% CI · all 1,186 papers (target + control), R(l) as published for E1 (0.821 at L48)')
    # middle: high - low at L48 / L52 by group
    rows = [('all papers', 'all'), ('target', 'target'), ('control', 'control'), ('target − control', 'target - control')]
    fx0 = 620; b += T(fx0, 208, 'High − low half, R at L48 (L52 grey)', 16, INK, weight=700)
    ax2 = Ax(fx0 + 130, 228, 270, 4 * 34, -0.16, 0.08, 0, 1)
    for v in (-0.15, -0.1, -0.05, 0, 0.05):
        X = ax2.X(v); b += f'<line x1="{X:.1f}" y1="228" x2="{X:.1f}" y2="{228 + 136}" stroke="{INK if v == 0 else "#E7DADA"}" stroke-width="{1.6 if v == 0 else 1}" stroke-dasharray="{"" if v == 0 else "3 4"}"/>' + T(X, 380, f'{v:+.2f}'.replace('-', '−') if v else '0', 12, PEN, 'middle')
    for i, (lab, gr) in enumerate(rows):
        y = 228 + 34 * (i + 0.5)
        e, lo, hi = g('high - low', gr, 48), g('high - low', gr, 48, 'lo'), g('high - low', gr, 48, 'hi')
        e2 = g('high - low', gr, 52)
        b += T(fx0 + 122, y + 5, lab, 13.5, INK, 'end')
        b += f'<line x1="{ax2.X(lo):.1f}" y1="{y:.1f}" x2="{ax2.X(hi):.1f}" y2="{y:.1f}" stroke="{OR}" stroke-width="2.4"/><circle cx="{ax2.X(e):.1f}" cy="{y:.1f}" r="4.5" fill="{OR}"/>'
        b += f'<circle cx="{ax2.X(e2):.1f}" cy="{y + 9:.1f}" r="3" fill="{LIGHT}" stroke="{PEN}" stroke-width="0.8"/>'
        b += T(fx0 + 410, y + 5, f'{fmt(e)} {cif(lo, hi)}', 12.5, INK, font=SANS)
        vals.append(f'high−low {gr} L48 {e:.3f} [{lo:.3f}, {hi:.3f}]; L52 {e2:.3f}')
    # bottom right: J-lens T-C by half
    ax3 = Ax(fx0 + 60, 430, 360, 90, 47, 57, -0.15, 0.08)
    b += T(fx0, 418, 'J-lens target − control (within bins): blue low, orange high half', 15, INK, weight=700)
    b += ax3.frame([48, 50, 52, 54, 56], [-0.1, 0, 0.05], ylab=lambda v: f'{v:+.2f}'.replace('-', '−') if v else '0')
    b += ax3.hline(0, PEN, '3 4', 1)
    JL = [48, 50, 51, 52, 53, 54, 55, 56]
    for h, col in (('low', BL), ('high', OR)):
        ys = [lz('stage11_1186', 'jlens_public', l, h) for l in JL]
        b += ax3.line(JL, ys, col, 2.2, r=2.6)
        vals.append(f'J-lens T−C {h}: ' + ', '.join(f'L{l} {v:+.3f}' for l, v in zip(JL, ys)))
    # bottom text
    y = 562
    how = ('How computed: halves by the median citation count of the 1,186 Stage 11 papers (31; low = 0–31, high = 32–1,010); R(l) as in E1 (mean over 5 false titles, paper means of log10(1/rank)); '
           'lens target − control within citation bins; team-cluster bootstrap, 2,000 draws (one draw set); published R(L48) 0.821 / R(L52) 0.995 reproduced exactly · '
           '381_stage13/summary_explore_citesplit_20261120/ (recovery_by_half.csv, lens_tc_by_half.csv)')
    t, h_ = para(70, y, how, 10.5, 1140, '#4B5363', lh=13.4); b += t; y += h_ + 5
    j53, j54 = (lz('stage11_1186', 'jlens_public', l, 'high - low') for l in (53, 54))
    j53c = cif(lz('stage11_1186', 'jlens_public', 53, 'high - low', 'lo'), lz('stage11_1186', 'jlens_public', 53, 'high - low', 'hi'))
    fc = lz('supplement_full_cohort', 'jlens_public', 48, 'high - low'); fcc = cif(lz('supplement_full_cohort', 'jlens_public', 48, 'high - low', 'lo'), lz('supplement_full_cohort', 'jlens_public', 48, 'high - low', 'hi'))
    bold = (f'Exploratory: in more-cited papers the post-title information arrives slightly later (R at L48 {g("high", "all", 48):.3f} vs {g("low", "all", 48):.3f}, high − low {fmt(g("high - low", "all", 48))}, both groups); '
            f'the target − control difference in timing does not depend on citations ({fmt(g("high - low", "target - control", 48))} {cif(g("high - low", "target - control", 48, "lo"), g("high - low", "target - control", 48, "hi"))}).')
    t, h_ = para(70, y, bold, 13, 1140, INK, lh=16.6); b += t.replace('<text ', '<text font-weight="700" ', 1); y += h_ + 3
    side = ("Logit lens target − control L40–L56: no half difference (all CIs include 0). J-lens: the high half's own target − control is below 0 at L48–L55, but the high − low difference excludes 0 only at L53–L55 (L53 −0.073 [−0.138, −0.010], L54 −0.076 [−0.141, −0.012], L55 −0.073 [−0.145, −0.006]); full cohort (median 66): high − low below 0 at every layer L40–L56 (L48 −0.065 [−0.093, −0.038]) — fits the vocabulary-crowding reading (exploratory).")
    t, h_ = para(70, y, side, 12, 1140, PEN, lh=15.2); b += t; y += h_
    REC['bottom'] = y
    b += ntext(70, 700, 'n = 1,186 papers (low ≤ 31 citations: 297 target + 297 control; high ≥ 32: 296 + 296) · full-cohort supplement 6,841 papers · team-cluster bootstrap, 2,000 draws', 11.5)
    b += L.footer('381_stage13/summary_explore_citesplit_20261120/report.md · info.json', y=714)
    sec = L.section('Citation split: arrival by citation half (exploratory)', pid, b)
    lead = '<div class="lead">← slide 91: recovery by group. <b>Here:</b> does citation count change when the title arrives? → recognition and timing, slide 93</div>'
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['values'] = vals
    return sec

NEW = slide()
parts, last = [], 0
for i, m in enumerate(ms):
    parts.append(s[last:m.start()]); parts.append(SL[i] + ('\n' + NEW if i == 90 else '')); last = m.end()
o = ''.join(parts) + s[last:]
newsecs = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', o, re.S)]
assert len(newsecs) == 97 and newsecs[:91] == SL[:91] and newsecs[92:] == SL[91:]
# contents menu
m = re.search(r'<nav class="toc-list" aria-label="All slides">(.*?)</nav></div>', o, re.S)
groups = re.findall(r'<section class="toc-g" aria-labelledby="toc-h(\d+)"><h3 class="toc-h" id="toc-h\d+">(.*?)<span class="toc-r">.*?</span></h3><ul>(.*?)</ul></section>', m.group(1), re.S)
titles, gstart = [], []
for j, name, ul in groups:
    its = re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', ul); gstart.append((len(titles), name))
    for n_, t_ in its: assert int(n_) == len(titles) + 1; titles.append(t_)
assert len(titles) == 96
titles = titles[:91] + [esc('More-cited papers: the title arrives a little later')] + titles[91:]
gstart = [(a if a <= 91 else a + 1, n) for a, n in gstart]
grp = []
for j, (a, name) in enumerate(gstart):
    b_ = gstart[j + 1][0] if j + 1 < len(gstart) else 97
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span><span class="toc-t">{titles[k]}</span></a></li>' for k in range(a, b_))
    rng = f'{a + 1}–{b_}' if b_ - a > 1 else f'{a + 1}'
    grp.append(f'<section class="toc-g" aria-labelledby="toc-h{j}"><h3 class="toc-h" id="toc-h{j}">{name}<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
o = o[:m.start(1)] + ''.join(grp) + o[m.end(1):]
assert o.count('<span class="toc-cnt">96 slides</span>') == 1
o = o.replace('<span class="toc-cnt">96 slides</span>', '<span class="toc-cnt">97 slides</span>')
vis = re.sub(r'<script.*?</script>|<style.*?</style>|data:[^"]+', '', NEW, flags=re.S)
assert not CJK.search(re.sub(r'<[^>]+>', ' ', vis))
OUT.write_text(o, encoding='utf-8')
REC.update({'toc': [{'start': a + 1, 'name': n} for a, n in gstart], 'new_slide': 92})
(Path(__file__).parent / 'build_20261120c_deck.json').write_text(json.dumps(REC, indent=1, ensure_ascii=False))
print('ok bottom', REC['bottom'], REC['toc'])
