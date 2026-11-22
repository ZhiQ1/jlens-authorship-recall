"""2026-11-21e: HTML deck v49 -> v50.
Source = merged_deck/stage1_11_deck.html.before_20261121e (= published v49) -> merged_deck/stage1_11_deck.html.
  * new slide after 75 ('L57–L61 mean ablation') = new 76: addendum 21 injection / sufficiency test (locked confirmatory, C37).
    Left: group A correct-writing rate by condition (own / mismatched / random at L48, L52 x beta 1, 2, 4; baseline line).
    Right: teacher-forced output rank change vs beta (own and mismatched, L48 and L52). Numbers read from 391_groups/summary_a21/.
  * old 76..100 -> 77..101; textual slide references remapped; contents menu rebuilt (101 slides). Writes build_20261121e_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, SANS

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
G = Path('/scratch/zhang.zhiqi2/jlens/391_groups/summary_a21')
SRC = D / 'stage1_11_deck.html.before_20261121e'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 100
SL = [m.group(0) for m in ms]
aria = lambda x: re.search(r'aria-label="([^"]*)"', x).group(1)
assert aria(SL[74]) == 'Addendum 18b item 4: L57–L61 mean ablation' and aria(SL[75]) == 'The Stage 11 timing holds for all 5 false titles'
GREY = '#8a8f98'; CTRL = '#9AA3B2'; LIGHT = '#C9CED6'; OR2 = '#B54708'
CJK = re.compile('[　-〿一-鿿＀-￯]')
def esc(x): return html.escape(str(x), quote=False)
def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')
def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'
MATH = "'STIX Two Math','Cambria Math','DejaVu Serif',serif"
def mtext(x, y, s_, fs=12.5): return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{INK}" font-style="italic" font-family="{MATH}">{esc(s_)}</text>'
REC = {'values': {}}
# ------------------------------------------------------------------ data
RT = {(r['grp'], r['cond']): r for r in csv.DictReader(open(G / 'rates.csv'))}
def rate(cond): return float(RT[('A', cond)]['any_full'])
PR = list(csv.DictReader(open(G / 'primary.csv')))
def prim(l, b, con):
    r = [x for x in PR if x['grp'] == 'A' and x['outcome'] == 'any_full' and int(x['layer']) == l and int(x['beta']) == b and x['contrast'] == con]
    assert len(r) == 1; return r[0]
TF = list(csv.DictReader(open(G / 'tf.csv')))
def tf(l, b, con):
    r = [x for x in TF if x['grp'] == 'A' and int(x['layer']) == l and int(x['beta']) == b and x['contrast'] == con]
    assert len(r) == 1; return tuple(float(r[0][k]) for k in ('est', 'lo', 'hi'))
RES = json.load(open(G / 'a21_results.json'))
assert RES['n_papers'] == 1200 and RES['by_grp'] == {'A': 600, 'B': 600} and RES['verdict'] == 'Not supported'
base = rate('base'); assert abs(base - 0.038333) < 1e-4
Gs = [float(prim(l, b, 'own - base')['est']) for l in (48, 52) for b in (1, 2, 4)]
Ss = [float(prim(l, b, 'own - mis')['est']) for l in (48, 52) for b in (1, 2, 4)]
assert abs(min(Gs) + 0.010) < 5e-4 and abs(max(Gs) - 0.005) < 5e-4 and abs(min(Ss) + 0.0017) < 5e-4 and abs(max(Ss) - 0.020) < 5e-4
s522 = prim(52, 2, 'own - mis'); assert abs(float(s522['lo']) - 0.003) < 5e-4 and abs(float(s522['hi']) - 0.037) < 5e-4 and abs(float(s522['p_holm']) - 0.15) < 1e-6
assert all(float(prim(l, b, 'own - base')['holm_lo']) < 0 < float(prim(l, b, 'own - base')['holm_hi']) for l in (48, 52) for b in (1, 2, 4))
t524 = tf(52, 4, 'own - base'); assert abs(t524[0] + 0.102) < 5e-4
own_max = max(rate(f'own_L{l}_b{b}') for l in (48, 52) for b in (1, 2, 4)); assert abs(own_max - 0.0433) < 5e-4

# ------------------------------------------------------------------ new slide
def slide_n():
    pid = 'inj'; vals = []
    bo = L.frame(pid, 'Strengthening the arrived information does not make the model write the author',
                 'Injection test: add β·Δ (the paper’s own title signal) at L48 or L52, before the late MLPs', 'Why it cannot say', title_fs=36)
    bd, bw = L.badge(70, 124, 'Locked confirmatory (addendum 21) · not supported', col='#2E7D46', fs=16); bo += bd
    # left: grouped bars of group A correct-writing rate
    x0 = 70; bo += T(x0, 186, 'Recognised papers (A) writing ≥ 1 true author', 16, INK, weight=700)
    ax = Ax(x0 + 52, 204, 520, 190, 0, 6, 0, 0.06)
    bo += ax.frame([], [0, 0.02, 0.04, 0.06], ylab=lambda v: f'{v * 100:.0f}%', title=None, ytitle='share of papers')
    cells = [(l, b) for l in (48, 52) for b in (1, 2, 4)]
    bw_ = 22
    for k, (l, b) in enumerate(cells):
        cx = ax.X(k + 0.5)
        for j, (src_, col) in enumerate((('own', BL), ('mis', CTRL), ('rand', LIGHT))):
            v = rate(f'{src_}_L{l}_b{b}'); x = cx + (j - 1.5) * bw_ + 1; y = ax.Y(v)
            bo += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw_ - 2}" height="{ax.Y(0) - y:.1f}" fill="{col}" rx="2"/>'
            vals.append(f'L{l} b{b} {src_} {v:.4f}')
        bo += T(cx, ax.Y(0) + 18, f'L{l} · β{b}', 12.5, PEN, anchor='middle', font=SANS)
    bo += ax.hline(base, OR, '6 4', 1.8)
    bo += T(ax.X(6) - 4, ax.Y(base) - 6, f'no injection {base * 100:.1f}%', 12.5, OR2, anchor='end', font=SANS)
    bo += L.legend(x0 + 52, 438, [('own Δ', BL, 'box'), ('another paper’s Δ', CTRL, 'box'), ('random', LIGHT, 'box'), ('no injection', OR, 'dash')], fs=12.5, gap=12)
    bo += mtext(x0, 470, 'G = rate(own) − rate(no injection),  S = rate(own) − rate(another paper)')
    bo += ntext(x0, 486, f'G {fmt(min(Gs))} to {fmt(max(Gs))}, all Holm intervals include 0; largest S {fmt(float(s522["est"]))} [{fmt(float(s522["lo"]))}, {fmt(float(s522["hi"]))}] (L52 β2), Holm p 0.15')
    bo += ntext(x0, 500, 'n = 1,200 papers (600 A, 600 B) · equal-norm controls · team bootstrap 2,000, Holm over 6 cells')
    # right: teacher-forced rank change vs beta
    x1 = 690; bo += T(x1, 186, 'Pushing harder only lowers the true name’s rank', 16, INK, weight=700)
    ax2 = Ax(x1 + 52, 204, 440, 190, 0, 4, -0.12, 0.01)
    bo += ax2.frame([0, 1, 2, 4], [-0.12, -0.08, -0.04, 0], xlab=lambda v: f'β={v}', ylab=lambda v: f'{v:+.2f}'.replace('-', '−').replace('+0.00', '0'), title=None, ytitle='Δ log₁₀(1/rank)')
    for l, dash in ((52, None), (48, '5 4')):
        own = [(0, 0.0, 0.0, 0.0)] + [(b, *tf(l, b, 'own - base')) for b in (1, 2, 4)]
        mis = [(0, 0.0)] + [(b, tf(l, b, 'own - base')[0] - tf(l, b, 'own - mis')[0]) for b in (1, 2, 4)]
        bo += ax2.line([x[0] for x in own], [x[1] for x in own], BL, 2.8, dash=dash, r=3.2)
        bo += ax2.line([x[0] for x in mis], [x[1] for x in mis], CTRL, 2.4, dash=dash, r=2.8)
        for b_, e, lo, hi in own[1:]: bo += ax2.whisk(b_, lo, hi, BL)
        vals.append(f'TF L{l} own ' + ', '.join(f'b{x[0]} {x[1]:+.3f}' for x in own) + ' | mis ' + ', '.join(f'b{x[0]} {x[1]:+.3f}' for x in mis))
    bo += ax2.hline(0, PEN, '3 3', 1.0)
    bo += L.legend(x1 + 52, 438, [('own Δ', BL, 'line'), ('another paper’s Δ', CTRL, 'line'), ('solid L52 · dashed L48', PEN, 'dash')], fs=12.5, gap=12)
    bo += mtext(x1, 470, 'Δ = mean log₁₀(1/rank_true) with injection − without (teacher-forced, L63)')
    bo += ntext(x1, 486, f'own L52 β4 {fmt(t524[0])} [{fmt(t524[1])}, {fmt(t524[2])}]; another paper’s Δ hurts about as much → generic damage')
    bo += ntext(x1, 500, 'n = 600 recognised papers (A); same pattern in B')
    bold = ('So: the information that has arrived by L48–L52 is not just too weak — making it stronger does not unlock the name; '
            'the bottleneck is the late conversion into a name (L57–L61, written by the MLPs).')
    t, h_ = para(70, 540, bold, 14, 1130, INK, lh=18); bo += t.replace('<text ', '<text font-weight="700" ', 1)
    bo += L.footer('391_groups/summary_a21/ (rates.csv, primary.csv, tf.csv) · prereg_addendum21.md sha256 bdbf80bd…', y=694)
    sec = L.section('Addendum 21: injection test (strengthening the arrived information)', pid, bo)
    lead = '<div class="lead">← slide 75: the MLPs write the name in L57–L61. <b>Here:</b> is the arrived information simply too weak? → slide 77</div>'
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['values']['n'] = vals
    return sec

N = slide_n()
order = SL[:75] + [N] + SL[75:]
assert len(order) == 101
def newnum(n): return n if n <= 75 else n + 1
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
between = [s[ms[i].end():ms[i + 1].start()] for i in range(99)]
assert all(x in ('', '\n') for x in between)
o = head + '\n'.join(order) + tail
m = re.search(r'<nav class="toc-list" aria-label="All slides">(.*?)</nav></div>', o, re.S)
groups = re.findall(r'<section class="toc-g" aria-labelledby="toc-h(\w+)"><h3 class="toc-h" id="toc-h\w+">(.*?)<span class="toc-r">(.*?)</span></h3><ul>(.*?)</ul></section>', m.group(1), re.S)
titles, gstart = [], []
for gid, name, rng, ul in groups:
    its = re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', ul); gstart.append((gid, len(titles), name))
    for n_, t_ in its: assert int(n_) == len(titles) + 1; titles.append(t_)
assert len(titles) == 100
titles = titles[:75] + [esc('Strengthening the arrived information does not make the model write the author')] + titles[75:]
gstart = [(gid, (a if a <= 75 else a + 1), name) for gid, a, name in gstart]
grp = []
for j, (gid, a, name) in enumerate(gstart):
    b_ = gstart[j + 1][1] if j + 1 < len(gstart) else 101
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span><span class="toc-t">{titles[k]}</span></a></li>' for k in range(a, b_))
    rng = f'{a + 1}–{b_}' if b_ - a > 1 else f'{a + 1}'
    grp.append(f'<section class="toc-g" aria-labelledby="toc-h{gid}"><h3 class="toc-h" id="toc-h{gid}">{name}<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
o = o[:m.start(1)] + ''.join(grp) + o[m.end(1):]
assert o.count('<span class="toc-cnt">100 slides</span>') == 1
o = o.replace('<span class="toc-cnt">100 slides</span>', '<span class="toc-cnt">101 slides</span>')
vis = re.sub(r'<script.*?</script>|<style.*?</style>|data:[^"]+', '', N, flags=re.S)
assert not CJK.search(re.sub(r'<[^>]+>', ' ', vis))
OUT.write_text(o, encoding='utf-8')
REC['toc'] = [{'id': g, 'start': a + 1, 'name': n} for g, a, n in gstart]
(Path(__file__).parent / 'build_20261121e_deck.json').write_text(json.dumps(REC, indent=1, ensure_ascii=False))
print('ok', REC['toc'], 'remapped on', fixed)
