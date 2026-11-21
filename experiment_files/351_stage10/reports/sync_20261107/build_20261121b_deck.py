"""2026-11-21b: exploratory results of 2026-11-20/21 woven into the merged HTML deck (v47 -> v48).
Source = merged_deck/stage1_11_deck.html.before_20261121b (= published v47) -> merged_deck/stage1_11_deck.html.
  * new slide before old 81 (= new 81, 'Meaning or this paper?' block): title-position probe true − made-up title by layer
    (391_groups/summary_a20/S5_E4b_probe.csv) + probe citation split (381_stage13/summary_explore_citesplit_probes_20261121/).
  * new slide after old 84 (= new 86, 'Names in the middle layers' block): name-position PCA (summary_explore_pca_np_20261120/)
    + direction overlap (summary_explore_dir_overlap_20261121/).
  * slide 59 (format lock): one exploratory line with the F4 coverage of group A (391_groups/summary_a16_20261115/b_rates.csv).
  * old 81..84 -> 82..85, old 85..97 -> 87..99; textual 'slide N' / 'slides N–M' references remapped; contents menu rebuilt
    (block ranges, 99 slides). All plotted / quoted numbers are read from the files above and asserted.
Writes build_20261121b_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, LIGHT, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
J = Path('/scratch/zhang.zhiqi2/jlens')
SRC = D / 'stage1_11_deck.html.before_20261121b'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 97
SL = [m.group(0) for m in ms]
aria = lambda x: re.search(r'aria-label="([^"]*)"', x).group(1)
assert aria(SL[58]) == 'Answer format (B), addendum 16'
assert aria(SL[79]) == 'Fictitious titles (addendum 20): meaning vs this paper'
assert aria(SL[80]) == 'Fictitious titles (addendum 20): layers and patching'
assert aria(SL[83]) == 'Name-position probe: H3 supported on the same scale'
GREY = '#8a8f98'; CTRL = '#9AA3B2'
CJK = re.compile('[　-〿一-鿿＀-￯]')
def esc(x): return html.escape(str(x), quote=False)
def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')
def cif(lo, hi, d=3, sign=True): return f'[{fmt(lo, d, sign)}, {fmt(hi, d, sign)}]'
def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'
def keynote(num, cap, top=574):
    return f'<div class="keyn" style="top:{top}px"><span class="kn">{esc(num)}</span><span class="kc">{esc(cap)}</span></div>'
REC = {'values': {}}

# ------------------------------------------------------------------ data
S5 = list(csv.DictReader(open(J / '391_groups/summary_a20/S5_E4b_probe.csv')))
p5 = {(int(r['layer']), r['group']): r for r in S5}
f5 = lambda l, g, k: float(p5[(l, g)][k])
assert abs(f5(40, 'target', 'd_true_fict') - 0.016) < 0.0006 and abs(f5(40, 'target', 'd_true_fict_lo') + 0.001) < 0.0006
assert abs(f5(40, 'control', 'd_true_fict') - 0.009) < 0.0006 and abs(f5(40, 'T-C within bin', 'd_true_fict') - 0.008) < 0.0006
assert abs(f5(52, 'target', 'd_true_fict') - 0.039) < 0.0006 and abs(f5(56, 'target', 'd_true_fict') - 0.041) < 0.0006
CP = list(csv.DictReader(open(J / '381_stage13/summary_explore_citesplit_probes_20261121/citesplit_probes.csv')))
cp = {(r['set'], r['half']): r for r in CP}
SETS = [('title probe, L40 (1,395 reuse-free; median 55)', 'title E4b V0 (spec0, reuse-free) L40 · FULL (median 55)'),
        ('title probe, L40 (4,654; median 66)', 'title E4b Vpd L40 · FULL (median 66)'),
        ('name-position probe, L40 (4,654)', 'name-position Vpd L40 · FULL (median 66)'),
        ('name-position probe, L48 (4,654)', 'name-position Vpd L48 · FULL (median 66)')]
c = lambda key, h, k='tc_within': float(cp[(key, h)][k])
for key, v in zip([k for _, k in SETS], (0.003, -0.019, 0.002, 0.001)): assert abs(c(key, 'high - low') - v) < 0.0006, key
PCA = json.load(open(J / '381_stage13/summary_explore_pca_np_20261120/pca_results.json'))['layers']
pc = {l: PCA[l]['Vpd (usable false titles)'] for l in ('40', '48')}
assert (pc['40']['main_n50'], pc['40']['main_n80'], pc['48']['main_n50'], pc['48']['main_n80']) == (31, 234, 25, 151)
assert abs(pc['40']['delta_share_mainPC']['10'] - 0.599) < 0.0006 and abs(pc['48']['delta_share_mainPC']['10'] - 0.808) < 0.0006
assert abs(pc['40']['delta_share_mainPC']['1'] - 0.007) < 0.0006 and abs(pc['48']['delta_share_mainPC']['1'] - 0.500) < 0.0006
assert abs(pc['40']['probeQ_share_mainPC']['10'] - 0.024) < 0.0006 and abs(pc['48']['probeQ_share_mainPC']['10'] - 0.014) < 0.0006
OV = list(csv.DictReader(open(J / '381_stage13/summary_explore_dir_overlap_20261121/dir_overlap.csv')))
ov = {(int(r['layer']), r['direction']): float(r['cos_with_Delta']) for r in OV}
OVJ = json.load(open(J / '381_stage13/summary_explore_dir_overlap_20261121/dir_overlap.json'))['layers']
assert abs(OVJ['40']['Delta_share_all_dirs'] - 0.071) < 0.0006 and abs(OVJ['48']['Delta_share_all_dirs'] - 0.061) < 0.0006
assert abs(ov[(48, 'author_gold (target papers)')] + 0.133) < 0.0006 and abs(ov[(40, 'author_gold (target papers)')] + 0.127) < 0.0006
BR = list(csv.DictReader(open(J / '391_groups/summary_a16_20261115/b_rates.csv')))
br = {(r['group'], r['fa_type'], r['cond'], r['outcome']): r for r in BR}
b = lambda g, cnd, k='true': float(br[(g, 'all', cnd, 'any_full')][k])
assert abs(b('A', 'F0') - 0.040) < 0.0006 and abs(b('A', 'F4') - 0.1517) < 0.0006 and abs(b('B', 'F0') - 0.005) < 0.0006 and abs(b('B', 'F4') - 0.0317) < 0.0006
fixed = (b('A', 'F4') - b('A', 'F0')) / (1 - b('A', 'F0')); assert abs(fixed - 0.116) < 0.001
BADGE = 'Exploratory (post hoc, not pre-registered)'

# ------------------------------------------------------------------ new slide A (new 81)
def slide_a():
    pid = 'xpa'; vals = []
    bo = L.frame(pid, 'Not at the title: the real-title extra and the exposure gap both form later',
                 'Title-position probe with the made-up titles (addendum 20 set) · probe target − control split by citations', 'Meaning or this paper?', title_fs=42)
    bd, bw = L.badge(70, 124, BADGE, col='#B54708', fs=16); bo += bd
    fm, fw = L.formula(1210 - 440, 118, 'Δ = probe(true) − probe(made-up title)', 'title-position probe (first author, first name token), per paper', fs=17, w=440); bo += fm
    # left: true − made-up by layer, target vs control
    LY = [16, 24, 32, 40, 44, 48, 52, 56, 60]
    ax = Ax(130, 222, 430, 200, 14, 62, -0.03, 0.11)
    bo += ax.frame([16, 24, 32, 40, 48, 56], [0, 0.05, 0.1], ylab=lambda v: f'{v:+.2f}'.replace('-', '−') if v else '0',
                   title='At the title: true − made-up, by layer', ytitle='Δ (log10 1/rank)')
    bo += ax.hline(0, PEN, '3 4', 1.2)
    ys0 = [f5(l, 'target', 'd_true_f0') for l in LY]
    bo += ax.line(LY, ys0, BL, 1.6, dash='5 4', pts=False, op=0.6)
    bo += T(ax.X(60) + 4, ax.Y(ys0[-1]) + 4, 'true − false', 12.5, BL)
    for g, col, lab in (('target', BL, 'target'), ('control', CTRL, 'control')):
        ys = [f5(l, g, 'd_true_fict') for l in LY]
        bo += ax.band(LY, [f5(l, g, 'd_true_fict_lo') for l in LY], [f5(l, g, 'd_true_fict_hi') for l in LY], col, 0.15) + ax.line(LY, ys, col, 2.6, r=3.3)
        vals.append(f'true−fict {g}: ' + ', '.join(f'L{l} {v:+.3f}' for l, v in zip(LY, ys)))
    v40 = f5(40, 'target', 'd_true_fict')
    bo += f'<circle cx="{ax.X(40):.1f}" cy="{ax.Y(v40):.1f}" r="7" fill="none" stroke="{OR}" stroke-width="2.2"/>'
    bo += T(ax.X(40) + 4, ax.Y(v40) - 14, f'L40 {fmt(v40)}', 13, OR, 'middle', weight=700)
    bo += L.legend(130, 462, [('target (true − made-up)', BL, 'line'), ('control', CTRL, 'line'), ('target, true − false title', BL, 'dash')], fs=13, gap=12)
    tc40 = (f5(40, 'T-C within bin', 'd_true_fict'), f5(40, 'T-C within bin', 'd_true_fict_lo'), f5(40, 'T-C within bin', 'd_true_fict_hi'))
    bo += ntext(130, 480, f'band = 95% CI · target − control (within bins) L40 {fmt(tc40[0])} {cif(tc40[1], tc40[2])}; only L32 excludes 0')
    # right: high − low citation half, target − control
    fx0 = 640; bo += T(fx0, 208, 'Exposure: high − low citation half, target − control', 16, INK, weight=700)
    ax2 = Ax(fx0 + 250, 228, 290, 4 * 38, -0.09, 0.09, 0, 1)
    for v in (-0.08, -0.04, 0, 0.04, 0.08):
        X = ax2.X(v); bo += (f'<line x1="{X:.1f}" y1="228" x2="{X:.1f}" y2="{228 + 152}" stroke="{INK if v == 0 else "#E7DADA"}" stroke-width="{1.6 if v == 0 else 1}" stroke-dasharray="{"" if v == 0 else "3 4"}"/>'
                             + T(X, 396, f'{v:+.2f}'.replace('-', '−') if v else '0', 12, PEN, 'middle'))
    for i, (lab, key) in enumerate(SETS):
        y = 228 + 38 * (i + 0.5); e, lo, hi = c(key, 'high - low'), c(key, 'high - low', 'lo'), c(key, 'high - low', 'hi')
        col = BL
        bo += T(fx0 + 242, y + 1, lab, 13, INK, 'end')
        bo += f'<line x1="{ax2.X(max(lo, -0.09)):.1f}" y1="{y:.1f}" x2="{ax2.X(min(hi, 0.09)):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.4"/><circle cx="{ax2.X(e):.1f}" cy="{y:.1f}" r="4.5" fill="{col}"/>'
        bo += T(fx0 + 242, y + 15, f'{fmt(e)} {cif(lo, hi)}', 11, PEN, 'end', font=SANS)
        vals.append(f'{key} high−low {e:+.4f} [{lo:+.4f}, {hi:+.4f}]')
    bo += ntext(fx0, 420, 'each probe set split at its own median citation count; target − control within citation bins; team CI')
    bo += ntext(fx0, 436, 'thin high-citation control group (119 / 331 papers) → wide intervals')
    # bottom
    y = 512
    how = ('How computed: left = addendum 20 papers, title-position probe refitted on the 9,108 true runs (team folds), applied to the true, made-up and false_0 title states; '
           'right = stored per-paper probe outputs (title probe V0 reuse-free set and per-donor set; name-position probe of the locked H3 test), split by citations; '
           'team-cluster bootstrap, 2,000 draws · 391_groups/summary_a20/S5_E4b_probe.csv · 381_stage13/summary_explore_citesplit_probes_20261121/')
    t, h_ = para(70, y, how, 10.5, 760, '#4B5363', lh=13.4); bo += t; y += h_ + 6
    bold = (f'Exploratory: at the title the real-title extra is small (L40 target {fmt(v40)} {cif(f5(40, "target", "d_true_fict_lo"), f5(40, "target", "d_true_fict_hi"))}, '
            f'about a fifth of true − false {fmt(f5(40, "target", "d_true_f0"))}); it grows to {fmt(f5(52, "target", "d_true_fict"))}–{fmt(f5(56, "target", "d_true_fict"))} by L52–L56. '
            f'More-cited papers are not stronger at the title or name-position probes (all high − low CIs include 0): this points to the saying step for the exposure gap.')
    t, h_ = para(70, y, bold, 13, 760, INK, lh=16.6); bo += t.replace('<text ', '<text font-weight="700" ', 1); y += h_
    REC['a_bottom'] = y
    bo += ntext(70, 676, 'n = 1,127 papers left (566 target + 561 control) · right: 1,395 / 4,654 papers (split at medians 55 / 66)', 11.5)
    bo += L.footer('391_groups/summary_a20/S5_E4b_probe.csv · 381_stage13/summary_explore_citesplit_probes_20261121/report.md', y=694)
    sec = L.section('Exploratory: real-title extra and exposure gap at the probes', pid, bo)
    lead = '<div class="lead">← slide 80: the made-up title recovers three quarters. <b>Here:</b> is the real-title extra already at the title? → where it appears, slide 82</div>'
    note = keynote(fmt(v40), 'true − made-up at the title, L40 (target): small, CI touches 0')
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + note + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['values']['a'] = vals
    return sec

# ------------------------------------------------------------------ new slide B (new 86)
def slide_b():
    pid = 'xpb'; vals = []
    bo = L.frame(pid, 'Recognition moves many quiet directions, not the author or attribute axes',
                 'Name positions, surname first token · PCA of the per-paper target − control differences · overlap with probe directions', 'Names in the middle layers', title_fs=42)
    bd, bw = L.badge(70, 124, BADGE, col='#B54708', fs=16); bo += bd
    fm, fw = L.formula(1210 - 440, 118, 'Δ = mean_T d − mean_C d,  d = h_true − mean h_false', 'd per paper at the name position; PCs of the target rows d − mean_C d', fs=16, w=440); bo += fm
    # left: PC1-10 variance share, L40 vs L48
    ax = Ax(130, 222, 420, 190, 0.4, 10.6, 0, 0.075)
    bo += ax.frame(list(range(1, 11)), [0, 0.025, 0.05, 0.075], xlab=lambda v: f'{v}', ylab=lambda v: f'{v * 100:.1f}%' if v else '0',
                   title='Variance per principal component (share)')
    for j, (l, col) in enumerate((('40', LIGHT), ('48', BL))):
        ev = pc[l]['main_ev10']
        for k, v in enumerate(ev, 1):
            x = ax.X(k) - 9 + j * 10
            bo += f'<rect x="{x:.1f}" y="{ax.Y(v):.1f}" width="9" height="{ax.Y(0) - ax.Y(v):.1f}" fill="{col}" stroke="{INK}" stroke-width="0.6"/>'
        vals.append(f'L{l} PC1-10 ' + ', '.join(f'{v:.3f}' for v in ev) + f'; n50 {pc[l]["main_n50"]} n80 {pc[l]["main_n80"]}')
    bo += L.legend(130, 450, [('L40', LIGHT, 'box'), ('L48', BL, 'box')], fs=13, gap=14)
    bo += T(232, 450, f'PCs to 50% / 80%: L40 {pc["40"]["main_n50"]} / {pc["40"]["main_n80"]} · L48 {pc["48"]["main_n50"]} / {pc["48"]["main_n80"]}', 13.5, INK, font=SANS)
    # middle mini table: where Δ and the probe readout sit
    tx = 130; ty = 478
    rows = [('share of Δ on PC1', pc['40']['delta_share_mainPC']['1'], pc['48']['delta_share_mainPC']['1']),
            ('share of Δ in top 10 PCs', pc['40']['delta_share_mainPC']['10'], pc['48']['delta_share_mainPC']['10']),
            ('probe readout in top 10 PCs', pc['40']['probeQ_share_mainPC']['10'], pc['48']['probeQ_share_mainPC']['10'])]
    bo += T(tx + 300, ty, 'L40', 13, PEN, 'end', font=SANS) + T(tx + 380, ty, 'L48', 13, PEN, 'end', font=SANS)
    for i, (lab, a, b_) in enumerate(rows):
        yy = ty + 18 * (i + 1)
        bo += T(tx, yy, lab, 13.5, INK, font=SANS) + T(tx + 300, yy, f'{a * 100:.1f}%', 13.5, INK, 'end', font=SANS) + T(tx + 380, yy, f'{b_ * 100:.1f}%', 13.5, OR if i < 2 else INK, 'end', font=SANS, weight=700 if i < 2 else None)
        vals.append(f'{lab} L40 {a:.3f} L48 {b_:.3f}')
    # right: cosines
    fx0 = 650; bo += T(fx0, 208, 'Does Δ point along probe directions? cos(Δ, direction)', 16, INK, weight=700)
    dirs = [('author probe: true-author readout', 'author_gold (target papers)'), ('author probe: direction 1', 'author_svd 1'),
            ('author probe: direction 5', 'author_svd 5'), ('citations', 'attr log citations'), ('year', 'attr year')]
    fields = [r['direction'] for r in OV if r['direction'].startswith('attr field=') and r['layer'] == '48']
    ax3 = Ax(fx0 + 230, 228, 300, 6 * 30, -0.18, 0.18, 0, 1)
    rnd = 0.014
    bo += f'<rect x="{ax3.X(-rnd):.1f}" y="228" width="{ax3.X(rnd) - ax3.X(-rnd):.1f}" height="180" fill="{LIGHT}" fill-opacity="0.45"/>'
    for v in (-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15):
        X = ax3.X(v); bo += (f'<line x1="{X:.1f}" y1="228" x2="{X:.1f}" y2="408" stroke="{INK if v == 0 else "#E7DADA"}" stroke-width="{1.6 if v == 0 else 1}" stroke-dasharray="{"" if v == 0 else "3 4"}"/>'
                             + (T(X, 424, f'{v:+.2f}'.replace('-', '−') if v else '0', 12, PEN, 'middle') if abs(v) in (0, 0.1) or v == 0 else ''))
    allrows = dirs + [('field (largest |cos| of 8)', None)]
    for i, (lab, key) in enumerate(allrows):
        y = 228 + 30 * (i + 0.5)
        if key: a40, a48 = ov[(40, key)], ov[(48, key)]
        else:
            f40 = max((ov[(40, f)] for f in fields), key=abs); f48 = max((ov[(48, f)] for f in fields), key=abs); a40, a48 = f40, f48
        bo += T(fx0 + 222, y + 5, lab, 13, INK, 'end')
        bo += f'<circle cx="{ax3.X(a40):.1f}" cy="{y:.1f}" r="4.5" fill="{LIGHT}" stroke="{INK}" stroke-width="0.8"/><circle cx="{ax3.X(a48):.1f}" cy="{y:.1f}" r="5" fill="{BL}"/>'
        vals.append(f'cos {lab}: L40 {a40:+.3f} L48 {a48:+.3f}')
    bo += ntext(fx0, 446, f'grey band = random direction (±{rnd}, 1 sd) · light dot L40, blue dot L48')
    a40, a48 = OVJ['40']['Delta_share_all_dirs'], OVJ['48']['Delta_share_all_dirs']
    bo += T(fx0, 470, f'All 17 directions together hold {a40 * 100:.1f}% (L40) / {a48 * 100:.1f}% (L48) of Δ', 14, OR, font=SANS, weight=700)
    vals.append(f'all17 L40 {a40:.4f} L48 {a48:.4f}')
    # bottom
    y = 556
    how = ('How computed: stored name-position states (surname first token, usable false titles as in the locked H3 test); PCA of the target rows minus the control mean; '
           'attribute directions = ridge refits of year, log citations and field on the true name-position states (the published attribute probes read the title position); '
           'author directions = the published name-position probe map, refitted · 381_stage13/summary_explore_pca_np_20261120/ · summary_explore_dir_overlap_20261121/')
    t, h_ = para(70, y, how, 10.5, 760, '#4B5363', lh=13.4); bo += t; y += h_ + 6
    bold = ('Exploratory: per-paper differences are spread over many directions (no PC above 7%), but the average target − control shift gathers by L48 '
            f'(PC1 {pc["40"]["delta_share_mainPC"]["1"] * 100:.0f}% → {pc["48"]["delta_share_mainPC"]["1"] * 100:.0f}%). It barely follows the author or attribute directions, '
            'and the author probe reads from low-variance directions.')
    t, h_ = para(70, y, bold, 13, 760, INK, lh=16.6); bo += t.replace('<text ', '<text font-weight="700" ', 1); y += h_
    REC['b_bottom'] = y
    bo += ntext(70, 676, f'n = 4,654 papers ({pc["40"]["n_target"]:,} target + {pc["40"]["n_control"]:,} control) · surname first token · L40, L48', 11.5)
    bo += L.footer('381_stage13/summary_explore_pca_np_20261120/report.md · summary_explore_dir_overlap_20261121/report.md', y=694)
    sec = L.section('Exploratory: directions of the name-position difference', pid, bo)
    lead = '<div class="lead">← slide 85: probe beats lens. <b>Here:</b> along which directions do recognised papers differ? → slide 87</div>'
    note = keynote(f'{a48 * 100:.0f}–{a40 * 100:.0f}%', 'of the recognised-vs-not shift lies on the 17 author + attribute directions')
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + note + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['values']['b'] = vals
    return sec

# ------------------------------------------------------------------ slide 59 addition
def add59(sec):
    line = (f'Exploratory · group A, ≥ 1 full true author: F0 {b("A", "F0") * 100:.1f}% → F4 {b("A", "F4") * 100:.1f}%; '
            f'{(1 - b("A", "F4")) * 100:.0f}% still none (fixes ~{fixed * 100:.0f}%) · B {b("B", "F0") * 100:.1f}% → {b("B", "F4") * 100:.1f}%')
    t = f'<text x="70" y="672" font-size="11" fill="#B54708" font-family="{SANS}" font-weight="700">{esc(line)}</text>'
    REC['values']['s59'] = line
    i = sec.rindex('</svg>'); return sec[:i] + t + sec[i:]

A, B = slide_a(), slide_b()
SL2 = list(SL); SL2[58] = add59(SL[58])
order = SL2[:80] + [A] + SL2[80:84] + [B] + SL2[84:]
assert len(order) == 99
def newnum(n):  # old slide number -> new
    return n if n <= 80 else (n + 1 if n <= 84 else n + 2)
def remap(t):
    def r(m):
        a = int(m.group(2)); out = m.group(1) + str(newnum(a))
        if m.group(4): out += m.group(3) + str(newnum(int(m.group(4))))
        return out
    return re.sub(r'(\bslides? )(\d{1,3})(?:([–-])(\d{1,3}))?', r, t)
fixed_refs = []
for k, sec in enumerate(order):
    if sec in (A, B): continue
    new = remap(sec)
    if new != sec: fixed_refs.append(k + 1)
    order[k] = new
# lead of slide 80 points to the new 81; lead of old 81 (new 82) starts from the new 81
i80 = 79; assert '→ slide 82</div>' in order[i80]; order[i80] = order[i80].replace('→ slide 82</div>', '→ slide 81</div>')
assert order[81].count('← slide 80: the made-up title recovers three quarters.') == 1
order[81] = order[81].replace('← slide 80: the made-up title recovers three quarters.', '← slide 81: the extra is small at the title.')
REC['refs_remapped_on_slides'] = fixed_refs
# assemble
parts, last = [], 0
head, tail = s[:ms[0].start()], s[ms[-1].end():]
between = [s[ms[i].end():ms[i + 1].start()] for i in range(96)]
assert all(x in ('', '\n') for x in between), set(between)
o = head + '\n'.join(order) + tail
# contents menu
m = re.search(r'<nav class="toc-list" aria-label="All slides">(.*?)</nav></div>', o, re.S)
groups = re.findall(r'<section class="toc-g" aria-labelledby="toc-h(\w+)"><h3 class="toc-h" id="toc-h\w+">(.*?)<span class="toc-r">(.*?)</span></h3><ul>(.*?)</ul></section>', m.group(1), re.S)
titles, gstart = [], []
for gid, name, rng, ul in groups:
    its = re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', ul); gstart.append((gid, len(titles), name))
    for n_, t_ in its: assert int(n_) == len(titles) + 1; titles.append(t_)
assert len(titles) == 97
TA = esc('Not at the title: the real-title extra and the exposure gap both form later')
TB = esc('Recognition moves many quiet directions, not the author or attribute axes')
titles = titles[:80] + [TA] + titles[80:84] + [TB] + titles[84:]
# block starts: 'Meaning or this paper?' 77 stays; 'Names in the middle layers' old 82 -> 83 (new slide 81 inside Meaning); later blocks shift by 2
gs2 = []
for gid, a, name in gstart:
    n0 = a + 1
    gs2.append((gid, (n0 if n0 <= 81 else (n0 + 1 if n0 <= 84 else n0 + 2)) - 1, name))
gstart = gs2
grp = []
for j, (gid, a, name) in enumerate(gstart):
    b_ = gstart[j + 1][1] if j + 1 < len(gstart) else 99
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span><span class="toc-t">{titles[k]}</span></a></li>' for k in range(a, b_))
    rng = f'{a + 1}–{b_}' if b_ - a > 1 else f'{a + 1}'
    grp.append(f'<section class="toc-g" aria-labelledby="toc-h{gid}"><h3 class="toc-h" id="toc-h{gid}">{name}<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
o = o[:m.start(1)] + ''.join(grp) + o[m.end(1):]
assert o.count('<span class="toc-cnt">97 slides</span>') == 1
o = o.replace('<span class="toc-cnt">97 slides</span>', '<span class="toc-cnt">99 slides</span>')
for NEW in (A, B):
    vis = re.sub(r'<script.*?</script>|<style.*?</style>|data:[^"]+', '', NEW, flags=re.S)
    assert not CJK.search(re.sub(r'<[^>]+>', ' ', vis))
OUT.write_text(o, encoding='utf-8')
REC['toc'] = [{'id': g, 'start': a + 1, 'name': n} for g, a, n in gstart]; REC['new_slides'] = [81, 86]
(Path(__file__).parent / 'build_20261121b_deck.json').write_text(json.dumps(REC, indent=1, ensure_ascii=False))
print('ok', REC['a_bottom'], REC['b_bottom'], REC['toc'], 'remapped on', fixed_refs)
