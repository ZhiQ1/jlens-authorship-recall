"""2026-11-20b: addendum 20 (H2 fictitious titles, LOCKED confirmatory) woven into the merged HTML deck.
Source = merged_deck/stage1_11_deck.html.before_20261120b (= published v43) -> merged_deck/stage1_11_deck.html.
  * two new data slides after slide 79 (18b item 5, title words) = new 80 (decomposition G = A + R, phi with decision bands,
    sensitivities) and 81 (layer profile of R-bar, E1 patching with the fictitious donor); old 80..94 -> 82..96.
  * H2 status text updated on slides 2, 68, 78, 87 (old numbering); slide 79 lead pointer; slide-number references >= 80 remapped.
  * contents menu rebuilt from its own markup (two items inserted, numbers / ranges / '96 slides' updated).
All numbers read from 391_groups/summary_a20/*.csv at build time. Idempotent (always rebuilds from the backup).
Writes build_20261120b_deck.json."""
import re, json, html, csv
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, INK, PEN, OR, BL, GR, RD, PINK, LIGHT, SANS, HAND, TITLE

D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
A20 = Path('/scratch/zhang.zhiqi2/jlens/391_groups/summary_a20')
SRC = D / 'stage1_11_deck.html.before_20261120b'
OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S))
assert len(ms) == 94, len(ms)
SL = {k + 1: m.group(0) for k, m in enumerate(ms)}
GREY = '#8a8f98'
SERIF = "'STIX Two Math','Cambria Math','DejaVu Serif','Times New Roman',serif"
CJK = re.compile('[　-〿一-鿿＀-￯]')
CHANGED = {}


def rep(k, a, b, msg, count=1):
    assert SL[k].count(a) == count, (k, SL[k].count(a), a[:90])
    SL[k] = SL[k].replace(a, b); CHANGED.setdefault(k, []).append(msg)


def rows(p): return list(csv.DictReader(open(p, encoding='utf-8')))
def fmt(v, d=3, sign=True): return (f'{v:+.{d}f}' if sign else f'{v:.{d}f}').replace('-', '−')
def cif(lo, hi, d=3, sign=True): return f'[{fmt(lo, d, sign)}, {fmt(hi, d, sign)}]'
def esc(x): return html.escape(str(x), quote=False)


def ftext(x, y, s_, fs=12.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{INK}" font-style="italic" text-anchor="{anchor}" font-family="{SERIF}">{esc(s_)}</text>'


def ntext(x, y, s_, fs=11.5, anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{fs}" fill="{GREY}" text-anchor="{anchor}" font-family="{SANS}">{esc(s_)}</text>'


# ---------------------------------------------------------------- data
P = {r['label']: r for r in rows(A20 / 'primary_secondary_sensitivity.csv')}
g = lambda lab, k: float(P[lab][k])
PT, PC = 'PRIMARY target final L63', 'S1 control final L63'
assert P[PT]['row'] == 'Rbar_T CI > 0 and phi_T >= 0.5' and P[PT]['borderline'] == 'False' and int(P[PT]['n']) == 566 and int(P[PC]['n']) == 561
VERDICT = 'H2 partly supported — a real-paper component exists, but meaning similarity explains most of the signal'
assert P[PT]['verdict'] == VERDICT.replace(' — ', ': ')
RES = json.load(open(A20 / 'a20_results.json'))
tcR, tcphi, dose = RES['tc_R'], RES['tc_phi'], RES['dose_trend']
S3 = {(r['readout'], int(r['layer']), r['group']): r for r in rows(A20 / 'S3_layer_profile.csv')}
S4 = {(r['group'], int(r['layer'])): r for r in rows(A20 / 'S4_E1_fict_donor.csv')}
S5 = rows(A20 / 'S5_E4b_probe.csv')
PL = {r['group']: r for r in rows(A20 / 'Sf_title_logprob.csv')}
NT, NC = 566, 561
NLINE = f'n = {NT + NC:,} papers ({NT} target, {NC} control; 59 excluded by the generation rule) · team-cluster bootstrap, 2,000 draws'
REC = {'verdict': VERDICT}


# ======================================================================= slide A: decomposition
def slide_a():
    pid = 'a20a'
    b = L.frame(pid, 'A made-up title with the same meaning: how far does it get?',
                'Addendum 20 (locked before the run) · every paper also gets a fictitious title with the same meaning that matches no real paper (Crossref check) · final output L63',
                'Stage 13 · H2 fictitious titles', title_fs=46)
    bd, bw = L.badge(70, 124, 'Locked confirmatory: H2 partly supported — meaning explains most', col='#2E7D46', fs=16); b += bd
    fm, fw = L.formula(1210 - 470, 118, 'φ = ΣA / ΣG,   R = S_true − S_fict',
                       'F = mean of 5 false titles;  G = S_true − F = A + R,  A = S_fict − F', fs=19, w=470); b += fm
    # left: stacked bars G = A + R
    x0, wpx, gmax = 200, 400, 0.45
    sc = lambda v: v / gmax * wpx
    b += T(70, 202, 'True − false gap, split into two parts', 17, INK, weight=700)
    for v in (0, 0.1, 0.2, 0.3, 0.4):
        X = x0 + sc(v)
        b += f'<line x1="{X:.1f}" y1="214" x2="{X:.1f}" y2="372" stroke="#E7DADA" stroke-width="1" stroke-dasharray="3 4"/>' + T(X, 390, f'{v:.1f}', 13, PEN, 'middle')
    b += T(x0 + wpx / 2, 408, 'mean log10(1/rank) per name token (paper mean)', 13, PEN, 'middle')
    vals = []
    for i, (lab, key, nn) in enumerate((('target', PT, NT), ('control', PC, NC))):
        y = 226 + i * 76
        A_, R_, G_ = g(key, 'Abar'), g(key, 'Rbar'), g(key, 'Gbar')
        b += T(x0 - 12, y + 24, lab, 18, INK, 'end', weight=700) + T(x0 - 12, y + 42, f'n = {nn}', 12.5, GREY, 'end', font=SANS)
        b += f'<rect x="{x0}" y="{y}" width="{sc(A_):.1f}" height="36" fill="{BL}" fill-opacity="0.85" stroke="{INK}" stroke-width="1"/>'
        b += f'<rect x="{x0 + sc(A_) + 2:.1f}" y="{y}" width="{max(sc(R_) - 2, 1):.1f}" height="36" fill="{OR}" fill-opacity="0.9" stroke="{INK}" stroke-width="1"/>'
        b += T(x0 + sc(A_) / 2, y + 24, f'A {fmt(A_, 3, False)}', 15, '#FFFFFF', 'middle', weight=700)
        b += T(x0 + sc(G_) + 8, y + 16, f'R {fmt(R_)} {cif(g(key, "R_lo"), g(key, "R_hi"))}', 13.5, '#B54708', weight=700)
        b += T(x0 + sc(G_) + 8, y + 34, f'G {fmt(G_, 3, False)}', 13.5, INK)
        b += T(x0, y + 56, f'φ = {fmt(g(key, "phi"), 3, False)} {cif(g(key, "phi_lo"), g(key, "phi_hi"), 3, False)}', 14.5, INK, weight=700)
        vals.append(f'{lab}: G {G_:.3f} [{g(key, "G_lo"):.3f}, {g(key, "G_hi"):.3f}], A {A_:.3f} [{g(key, "A_lo"):.3f}, {g(key, "A_hi"):.3f}], '
                    f'R {R_:.3f} [{g(key, "R_lo"):.3f}, {g(key, "R_hi"):.3f}], phi {g(key, "phi"):.3f} [{g(key, "phi_lo"):.3f}, {g(key, "phi_hi"):.3f}] (n {nn})')
    b += L.legend(200, 432, [('A: recovered by the made-up title (meaning)', BL, 'box'), ('R: only the real title gives it', OR, 'box')], fs=13.5, gap=14)
    b += T(70, 458, f'within-bin target − control: R {fmt(tcR[0])} {cif(tcR[1], tcR[2])} (the direction H2 predicts); φ {fmt(tcphi[0])} {cif(tcphi[1], tcphi[2])}', 13, INK, font=SANS)
    vals.append(f'T−C R {tcR[0]:.3f} [{tcR[1]:.3f}, {tcR[2]:.3f}]; T−C phi {tcphi[0]:.3f} [{tcphi[1]:.3f}, {tcphi[2]:.3f}]')
    # right: phi forest with decision bands
    fx0, fy0, fw_ = 700, 222, 530
    labw = 196
    ax = Ax(fx0 + labw, fy0, fw_ - labw - 120, 0, 0, 1, 0, 1)
    SEN = [('target (primary)', PT, INK), ('control', PC, BL),
           ('(a) false_0 only', '(a) false_0 instead of the 5-title mean', PEN), ('(b) Crossref j2 ≥ 0.4 out', '(b) without fict titles with Crossref jaccard2 >= 0.4', PEN),
           ('(c) titles ≥ 6 words', '(c) true titles >= 6 words', PEN), ('(d) first author only', '(d1) first author only', PEN),
           ('(d) surname 1st token', '(d2) surname first token only', PEN), ('(e) R0 papers only', '(e) R0 papers only', PEN),
           ('(f) title log-prob, tertile 1', '(f) title log-prob true - fict, target tertile 1', PINK), ('(f) tertile 2', '(f) title log-prob true - fict, target tertile 2', PINK),
           ('(f) tertile 3', '(f) title log-prob true - fict, target tertile 3', PINK)]
    rowh = 21; hgt = rowh * len(SEN)
    b += T(fx0, 199, 'φ by the locked rule, and every sensitivity analysis', 17, INK, weight=700)
    for lo, hi, col, lab in ((0, 0.3, '#E3F1E6', 'strong'), (0.3, 0.5, '#FFF1D6', 'limited weight'), (0.5, 1.0, '#F3E4EA', 'meaning explains most')):
        b += f'<rect x="{ax.X(lo):.1f}" y="{fy0}" width="{ax.X(hi) - ax.X(lo):.1f}" height="{hgt}" fill="{col}" stroke="none"/>'
    for v in (0, 0.3, 0.5, 1.0):
        b += f'<line x1="{ax.X(v):.1f}" y1="{fy0}" x2="{ax.X(v):.1f}" y2="{fy0 + hgt}" stroke="{RD if v in (0.3, 0.5) else "#C9B9B9"}" stroke-width="{1.4 if v in (0.3, 0.5) else 1}" stroke-dasharray="5 4"/>'
        b += T(ax.X(v), fy0 + hgt + 15, f'{v:g}', 12.5, PEN, 'middle')
    sens_phi = []
    for i, (lab, key, col) in enumerate(SEN):
        y = fy0 + rowh * (i + 0.5); est, lo, hi = g(key, 'phi'), g(key, 'phi_lo'), g(key, 'phi_hi')
        b += T(fx0 + labw - 8, y + 4.5, lab, 13, INK if i < 2 else PEN, 'end')
        b += f'<line x1="{ax.X(lo):.1f}" y1="{y:.1f}" x2="{ax.X(hi):.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>'
        b += f'<circle cx="{ax.X(est):.1f}" cy="{y:.1f}" r="{5 if i < 2 else 4}" fill="{col}"/>'
        b += T(fx0 + fw_ - 112, y + 4.5, f'{est:.3f} ({int(P[key]["n"])})', 12.5, INK, font=SANS)
        vals.append(f'{lab} phi {est:.3f} [{lo:.3f}, {hi:.3f}] R {g(key, "Rbar"):.3f} n {P[key]["n"]}')
        if i >= 2: sens_phi.append(est)
    lx = fx0
    for col, lab in (('#E3F1E6', 'φ < 0.3 strongly supported'), ('#FFF1D6', '0.3–0.5 limited weight'), ('#F3E4EA', '≥ 0.5 meaning explains most')):
        b += f'<rect x="{lx:.1f}" y="{fy0 + hgt + 20:.1f}" width="12" height="10" fill="{col}" stroke="{PEN}" stroke-width="0.8"/>' + ntext(lx + 16, fy0 + hgt + 29, lab, 11)
        lx += 16 + L.width(lab, 11) * 0.95 + 12
    b += ntext(fx0, fy0 + hgt + 43, 'value (n papers) · bands fixed before the run; φ is read only when the CI of R̄ lies above 0', 11)
    REC['sens_phi_range'] = [min(sens_phi), max(sens_phi)]
    assert abs(min(sens_phi) - 0.708) < 0.0006 and abs(max(sens_phi) - 0.778) < 0.0006, sens_phi
    # bottom text
    y = 512
    how = ('How computed: per paper, S = mean over name tokens of log10(1/rank) at the final output (all authors, all tokens); S_true, S_fict, F̄ = mean of the 5 false titles; '
           'G = S_true − F̄, A = S_fict − F̄, R = S_true − S_fict; φ = ΣA / ΣG over the group (ratio of sums); verdict by the point estimate φ̂_T, read only when the 95% CI of R̄_T lies entirely above 0 '
           '(φ̂ < 0.3 strongly supported; 0.3–0.5 partly, limited weight; ≥ 0.5 partly, meaning explains most; R̄ CI ∋ 0 not supported; R̄ CI < 0 refuted); borderline if the φ CI crosses 0.3 or 0.5 · '
           'S_true, S_false from the stored Stage 10 run, S_fict from this run · 391_groups/summary_a20/primary_secondary_sensitivity.csv')
    t, h = para(70, y, how, 10.5, 1140, '#4B5363', lh=13.4); b += t; y += h + 6
    bold = (f'Locked verdict: R̄_T {fmt(g(PT, "Rbar"))} {cif(g(PT, "R_lo"), g(PT, "R_hi"))} > 0 and φ̂_T = {g(PT, "phi"):.3f} {cif(g(PT, "phi_lo"), g(PT, "phi_hi"), 3, False)} ≥ 0.5 → '
            f'{VERDICT}. Not borderline; unchanged in every sensitivity analysis (φ_T {min(sens_phi):.3f}–{max(sens_phi):.3f}).')
    t, h = para(70, y, bold, 13, 1140, INK, lh=16.6); b += t.replace('<text ', '<text font-weight="700" ', 1); y += h + 4
    cav = (f'Caveats: one model; the made-up titles are more likely under the model than the real ones (title log-prob true − fict {fmt(float(PL["target"]["true_minus_fict"]))} target, {fmt(float(PL["control"]["true_minus_fict"]))} control); '
           'φ rises with meaning closeness (cos tertiles), so the real-title extra may partly be closeness that the made-up title missed; parity WARN (exact-rank share 0.55–0.66 < 0.75; mean |Δlog10 rank| ≤ 0.014), numbers kept.')
    t, h = para(70, y, cav, 12, 1140, PEN, lh=15.2); b += t; y += h
    b += ntext(70, 700, NLINE, 11.5)
    b += L.footer('391_groups/summary_a20/a20_report.md · primary_secondary_sensitivity.csv · a20_results.json (tc_R, tc_phi) · config/prereg_addendum20.md (sha256 fee691de…)', y=714)
    sec = L.section('Fictitious titles (addendum 20): meaning vs this paper', pid, b)
    lead = ('<div class="lead">← slide 79: content words carry it. <b>Here:</b> does a made-up title with the same meaning do as well? → slide 81</div>')
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['slide_a_values'] = vals
    return sec, y


# ======================================================================= slide B: layers and patching
def slide_b():
    pid = 'a20b'
    b = L.frame(pid, 'Where the real-title extra appears',
                'Addendum 20, secondary comparisons (descriptive) · same 1,127 papers · lens readouts at the name positions; patching of the post-title tail (E1 design)',
                'Stage 13 · H2 fictitious titles', title_fs=46)
    bd, bw = L.badge(70, 124, 'Secondary · descriptive', col='#6A7385', fs=16); b += bd
    fm, fw = L.formula(1210 - 500, 118, 'rec(l) = mean(patched_l − false_0) / mean(true − false_0)',
                       'donor = true title (stored Stage 11 E1) or the made-up title (this run)', fs=17, w=500); b += fm
    vals = []
    # left: R-bar by layer
    ax = Ax(130, 220, 440, 210, 20, 66, -0.06, 0.14)
    b += ax.frame([24, 32, 40, 48, 56, 63], [-0.04, 0, 0.04, 0.08, 0.12], xlab=lambda v: f'L{v}', ylab=lambda v: f'{v:+.2f}'.replace('-', '−') if v else '0',
                  title='mean R = S_true − S_fict by layer (name positions)', ytitle='R (nlr)')
    b += ax.hline(0, PEN, '3 4', 1.2)
    LY = [24, 32, 40, 48, 56, 62]
    for ro, dash, labr in (('jlens_public', None, 'J-lens'), ('logit', '6 4', 'logit lens')):
        for grp, col in (('target', OR), ('control', BL)):
            ys = [float(S3[(ro, l, grp)]['Rbar']) for l in LY]
            if dash is None: b += ax.band(LY, [float(S3[(ro, l, grp)]['R_lo']) for l in LY], [float(S3[(ro, l, grp)]['R_hi']) for l in LY], col, 0.14)
            b += ax.line(LY, ys, col, 2.6 if dash is None else 1.8, dash, r=3.5 if dash is None else 2.5)
            vals.append(f'{labr} {grp} R: ' + ', '.join(f'L{l} {v:+.3f}' for l, v in zip(LY, ys)))
    for grp, col in (('target', OR), ('control', BL)):
        r = S3[('final', 63, grp)]; v = float(r['Rbar'])
        b += f'<rect x="{ax.X(63) - 5:.1f}" y="{ax.Y(v) - 5:.1f}" width="10" height="10" fill="{col}" stroke="{INK}" stroke-width="1"/>' + ax.whisk(63, float(r['R_lo']), float(r['R_hi']), INK, 1.2, 3)
        b += T(ax.X(63) + 9, ax.Y(v) + 5, f'{v:+.3f}', 12.5, INK)
    jt = float(S3[('jlens_public', 62, 'target')]['Rbar'])
    b += T(ax.X(62) - 9, ax.Y(jt) + 2, f'J-lens L62 {jt:+.3f}', 12.5, '#B54708', 'end', weight=700)
    b += L.legend(130, 470, [('target', OR, 'line'), ('control', BL, 'line'), ('logit lens', PEN, 'dash'), ('final L63 (squares)', INK, 'box')], fs=13, gap=12)
    b += ntext(130, 488, 'band = 95% CI (J-lens); R̄ ≈ 0 up to L48; J-lens L32 and L48 (target) dip below 0')
    # right: E1 recovery
    ax2 = Ax(720, 220, 440, 210, 20, 66, 0, 1.08)
    b += ax2.frame([24, 32, 40, 48, 56, 63], [0, 0.25, 0.5, 0.75, 1.0], ylab=lambda v: f'{v:g}', title='Patching the tail at layer l: share of the gap recovered', ytitle='rec(l)')
    LE = [24, 32, 40, 48, 50, 52, 54, 56, 58, 60, 62, 63]
    for grp, w_, op in (('target', 2.8, 1.0), ('control', 1.6, 0.55)):
        rt = [float(S4[(grp, l)]['rec_true']) for l in LE]; rf = [float(S4[(grp, l)]['rec_fict']) for l in LE]
        b += ax2.line(LE, rt, INK, w_, None if grp == 'target' else '5 4', r=3 if grp == 'target' else 0, op=op)
        b += ax2.line(LE, rf, PINK, w_, None if grp == 'target' else '5 4', r=3 if grp == 'target' else 0, op=op)
        vals.append(f'E1 {grp} rec_true: ' + ', '.join(f'L{l} {v:.3f}' for l, v in zip(LE, rt)) + ' | rec_fict: ' + ', '.join(f'L{l} {v:.3f}' for l, v in zip(LE, rf)))
    d54 = S4[('target', 54)]
    b += f'<line x1="{ax2.X(60):.1f}" y1="{ax2.Y(float(S4[("target", 60)]["rec_true"])) + 4:.1f}" x2="{ax2.X(60):.1f}" y2="{ax2.Y(float(S4[("target", 60)]["rec_fict"])) - 4:.1f}" stroke="#B54708" stroke-width="1.6"/>'
    b += T(ax2.X(63), ax2.Y(0.62), f'gap {fmt(float(d54["diff"]))}', 13, '#B54708', 'end', weight=700)
    b += T(ax2.X(63), ax2.Y(0.62) + 15, f'{cif(float(d54["diff_lo"]), float(d54["diff_hi"]))} (L54)', 12, '#B54708', 'end')
    b += L.legend(720, 470, [('true-title donor', INK, 'line'), ('made-up-title donor', PINK, 'line'), ('control (dashed)', PEN, 'dash')], fs=13, gap=12)
    b += ntext(720, 488, f'made-up donor plateaus at ≈ {float(S4[("target", 63)]["rec_fict"]):.3f} from L52 (true donor 1.00)')
    # bottom
    p5 = {(r['group'], int(r['layer'])): r for r in S5}
    tf = [float(p5[('target', l)]['d_true_fict']) for l in (16, 24, 32, 40, 44, 48, 52, 56, 60)]
    tf0 = [float(p5[('target', l)]['d_true_f0']) for l in (16, 24, 32, 40, 44, 48, 52, 56, 60)]
    assert 0.015 <= min(tf) and max(tf) <= 0.042 and 0.057 <= min(tf0) and max(tf0) <= 0.102, (tf, tf0)
    REC['probe_true_minus_fict_target'] = tf; REC['probe_true_minus_f0_target'] = tf0
    y = 512
    how = ('How computed: R̄ = mean over papers of S_true − S_fict at each readout (logit lens, public J-lens) and layer, name positions, within each group; rec(l): the post-title tail of the false_0 run is replaced at layer l '
           'by the donor run’s states, rec = mean(patched − false_0) / mean(true − false_0) (denominator and true-donor curve from the stored Stage 11 E1 run; L63 identity checked: 0.7453 = 0.7453) · '
           'team-cluster bootstrap, 2,000 draws · 391_groups/summary_a20/S3_layer_profile.csv, S4_E1_fict_donor.csv, S5_E4b_probe.csv, a20_results.json (dose_trend)')
    t, h = para(70, y, how, 10.5, 1140, '#4B5363', lh=13.4); b += t; y += h + 6
    bold = ('Descriptive: the part only the real title gives shows up late — R̄ is clearly above 0 only from L56 (J-lens L62 '
            f'{jt:+.3f}, final {g(PT, "Rbar"):+.3f}); patching with the made-up title recovers ≈ three quarters of the gap from L52 on, the real title all of it.')
    t, h = para(70, y, bold, 13, 1140, INK, lh=16.6); b += t.replace('<text ', '<text font-weight="700" ', 1); y += h + 4
    dz = f'{fmt(dose[0])} {cif(dose[1], dose[2])}'
    side = (f'Also: at the title position the probe separates true from made-up titles by only +0.02 to +0.04 (target; true vs a false title +0.06 to +0.10); '
            f'φ rises with meaning closeness, 0.722 / 0.740 / 0.794 over cosine tertiles (tertile 3 − 1 {dz}), the direction a title-text explanation predicts.')
    t, h = para(70, y, side, 12, 1140, PEN, lh=15.2); b += t; y += h
    b += ntext(70, 700, NLINE, 11.5)
    b += L.footer('391_groups/summary_a20/a20_report.md (§2 S3, S4, S5, S7) · config/prereg_addendum20.md', y=714)
    sec = L.section('Fictitious titles (addendum 20): layers and patching', pid, b)
    lead = '<div class="lead">← slide 80: the made-up title recovers three quarters. <b>Here:</b> where the real-title extra appears → subspace swap, slide 82</div>'
    sec = sec.replace('<span class="pg"></span></section>', '<span class="pg"></span>' + lead + f'<!-- plotted numbers: {esc(" | ".join(vals))} --></section>')
    REC['slide_b_values'] = vals
    return sec, y


NA, ya = slide_a()
NB_, yb = slide_b()
REC['text_bottom'] = [ya, yb]

# remap slide-number references >= 80 (old numbering) by +2
REMAP = []
def remap_refs(k):
    def f(m):
        nums = m.group(0)
        out = re.sub(r'\d+', lambda x: str(int(x.group(0)) + 2) if int(x.group(0)) >= 80 else x.group(0), nums)
        if out != nums: REMAP.append((k, nums, out))
        return out
    SL[k] = re.sub(r'[Ss]lides? \d+(?:(?:[,–-]| and | to |, )\s*\d+)*', f, SL[k])
for k in SL:
    head_ = re.sub(r'data:[^"]+', '', SL[k])
    remap_refs(k)
REC['remapped_refs'] = REMAP
assert sorted({k for k, _, _ in REMAP}) == [79, 84, 86], REMAP

# ======================================================================= status text on existing slides
ST = 'partly supported, meaning explains most (addendum 20, locked)'
rep(2, '12–13 route, title words, made-up names', '12–13 route, title words, fictitious titles, made-up names', 'roadmap pill: fictitious titles')
rep(68, 'H2 (paper identity) partly supported but not established;', f'H2 (paper identity) {ST};', 'H2 status')
rep(68, 'title meaning matters more than wording (item 5) <span class="st c4">descriptive</span> → slide 79; still not separable from paper identity.',
    'title meaning matters more than wording (item 5) <span class="st c4">descriptive</span> → slide 79; made-up title recovers 0.75, real title +0.11 (add. 20) <span class="st c1">locked</span> → slide 80.',
    'H2 latest result')
rep(78, 'H2 partly supported but not established (rests on M2 and X1; X4 recognition gap no longer counted);',
    'H2 partly supported: a real-paper component exists, but meaning explains most (addendum 20, slide 80; before: M2 and X1);', 'H2 status')
rep(79, '→ subspace swap, slide 82</div>', '→ made-up titles, slide 80</div>', 'lead pointer (after remap)')
rep(87, '– H2 (paper identity) partly supported but not established<br>', '– H2 (paper identity): partly supported, meaning similarity explains most (addendum 20); the real-title extra is +0.11<br>', 'H2 status (limits)')
for k, t in SL.items(): assert 'partly supported but not established' not in t, k

# ======================================================================= reassemble
order = list(range(1, 80)) + ['A', 'B'] + list(range(80, 95))
NEW = {'A': NA, 'B': NB_}
body = [SL[o] if isinstance(o, int) else NEW[o] for o in order]
parts, last = [], 0
for i, m in enumerate(ms):
    parts.append(s[last:m.start()])
    if i == 79 - 1:
        parts.append(SL[79] + '\n' + NA + '\n' + NB_)
    else:
        parts.append(SL[i + 1])
    last = m.end()
o = ''.join(parts) + s[last:]
newsecs = [m.group(0) for m in re.finditer(r'<section class="slide.*?</section>', o, re.S)]
assert len(newsecs) == 96 and newsecs == body

# ======================================================================= contents menu
m = re.search(r'<nav class="toc-list" aria-label="All slides">(.*?)</nav></div>', o, re.S)
groups = re.findall(r'<section class="toc-g" aria-labelledby="toc-h(\d+)"><h3 class="toc-h" id="toc-h\d+">(.*?)<span class="toc-r">.*?</span></h3><ul>(.*?)</ul></section>', m.group(1), re.S)
assert len(groups) == 9
titles, gstart = [], []
for j, name, ul in groups:
    its = re.findall(r'<span class="toc-n">(\d+)</span><span class="toc-t">(.*?)</span>', ul)
    gstart.append((len(titles), name))
    for n_, t_ in its:
        assert int(n_) == len(titles) + 1; titles.append(t_)
assert len(titles) == 94
ta = esc('A made-up title with the same meaning: how far does it get?'); tb = esc('Where the real-title extra appears')
titles = titles[:79] + [ta, tb] + titles[79:]
gstart = [(a if a < 79 else a + 2, n) for a, n in gstart]
assert len(set(titles)) == 96
grp_html = []
for j, (a, name) in enumerate(gstart):
    b_ = gstart[j + 1][0] if j + 1 < len(gstart) else 96
    items = ''.join(f'<li><a class="toc-i" href="#s{k + 1}" data-i="{k}"><span class="toc-n">{k + 1}</span><span class="toc-t">{titles[k]}</span></a></li>' for k in range(a, b_))
    rng = f'{a + 1}–{b_}' if b_ - a > 1 else f'{a + 1}'
    grp_html.append(f'<section class="toc-g" aria-labelledby="toc-h{j}"><h3 class="toc-h" id="toc-h{j}">{name}<span class="toc-r">{rng}</span></h3><ul>{items}</ul></section>')
o = o[:m.start(1)] + ''.join(grp_html) + o[m.end(1):]
assert o.count('<span class="toc-cnt">94 slides</span>') == 1
o = o.replace('<span class="toc-cnt">94 slides</span>', '<span class="toc-cnt">96 slides</span>')
REC['toc_groups'] = [{'start': a + 1, 'name': n} for a, n in gstart]
vis = re.sub(r'<script.*?</script>|<style.*?</style>|data:[^"]+', '', NA + NB_, flags=re.S)
assert not CJK.search(re.sub(r'<[^>]+>', ' ', vis)), CJK.findall(vis)[:5]
OUT.write_text(o, encoding='utf-8')
REC.update({'source': str(SRC), 'out': str(OUT), 'changed': CHANGED, 'new_slides': {80: 'decomposition', 81: 'layers and patching'},
            'bytes_in': len(s.encode()), 'bytes_out': len(o.encode())})
(Path(__file__).parent / 'build_20261120b_deck.json').write_text(json.dumps(REC, indent=1, ensure_ascii=False))
print('ok', len(s), '->', len(o), 'bottom y', ya, yb); print(json.dumps(CHANGED, ensure_ascii=False)); print(REMAP)
