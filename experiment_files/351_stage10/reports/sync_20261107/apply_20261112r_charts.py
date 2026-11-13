"""Round r (priority, 2026-11-12 evening): chart slides built from source CSVs -> r_frag/*.html (full <section>s).
67 P1/P2 (five-title mean, false_0 thin), 68 X6/X7, 72 all-token probe, NEW np (name-position probe), NEW c24 (2-11b),
and the chart SVG for slide 82 (E1 denominators by group). Every plotted number is an SVG <text>; source under each chart."""
import json
from pathlib import Path
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, f3, ci, rows, INK, PEN, OR, BL, GR, RD, PINK, LIGHT, SANS, HAND
OUT = Path(__file__).parent / 'r_frag'; OUT.mkdir(exist_ok=True)
L.check_verbatim()
R13, G = L.R13, L.G391
ONE = {}  # slide -> one-line 怎么算 (also used for notes)
FIVE = {}

def save(name, html_):
    (OUT / f'{name}.html').write_text(html_, encoding='utf-8')

def valpara(x, y, s, maxw):
    t, h = para(x, y, s, 9, maxw, '#7A808C', lh=11); return t, h

def how1(x, y, s, maxw=1140):
    t, h = para(x, y, '怎么算：' + s, 10.5, maxw, '#4B5363', lh=13.2); return t, h

# ================================================================ 67 P1 / P2
def s67():
    pid = 'r67'; M = rows(G / 'summary_b1_p12f/p12f_mean5.csv')
    def get(exp, item, grp='all'):
        r = [x for x in M if x['experiment'] == exp and x['item'] == item and x['group'] == grp and x['who'] == 'all_authors']
        r.sort(key=lambda x: int(x['layer'])); return r
    b = L.frame(pid, 'Stage 12: where the paper information travels', 'P1 / P2 with five false titles (addendum 10, item 3) · share of the true − false gap recovered at the output · 1,186 papers', 'Stage 12')
    # P1
    ax = Ax(120, 160, 470, 210, 32, 56, 0, 1.0)
    b += ax.frame([32, 40, 44, 48, 52, 56], [0, 0.25, 0.5, 0.75, 1.0], title='P1 · patch a set of positions at layer l', ytitle='recovery')
    vals = []
    for item, col, lab in [('all', INK, 'all positions after the title'), ('names', BL, 'name positions only'), ('p1', OR, "':' only")]:
        r = get('P1', item); xs = [int(x['layer']) for x in r]
        m = [float(x['ratio']) for x in r]; lo = [float(x['ratio_lo']) for x in r]; hi = [float(x['ratio_hi']) for x in r]; f0 = [float(x['ratio_false0']) for x in r]
        b += ax.band(xs, lo, hi, col) + ax.line(xs, f0, col, w=1.2, dash='4 3', pts=False) + ax.line(xs, m, col, r=3.5)
        k = xs.index(52); b += T(ax.X(52) + 6, ax.Y(m[k]) - 6 if item != 'p1' else ax.Y(m[k]) - 8, f'{f3(m[k])}', 13, col, weight=700)
        if item != 'p1': k48 = xs.index(48); b += T(ax.X(48) - 10, ax.Y(m[k48]) - 7, f3(m[k48]), 13, col, 'end', weight=700)
        vals.append(f"{lab}: " + '; '.join(f"L{x} {f3(a)} {ci(c, d)} (false_0 {f3(e)})" for x, a, c, d, e in zip(xs, m, lo, hi, f0)))
    b += L.legend(120, 410, [('all positions', INK, 'line'), ('names', BL, 'line'), ("':'", OR, 'line'), ('false_0 only', PEN, 'dash')], fs=13, gap=12)
    # P2
    ax2 = Ax(720, 160, 500, 210, 8, 56, 0, 0.3)
    b += ax2.frame([8, 16, 24, 32, 40, 48, 56], [0, 0.1, 0.2, 0.3], title='P2 · patch one component of one layer', ytitle='recovery')
    for item, col, lab in [('attn', BL, 'attention'), ('mlp', OR, 'MLP')]:
        r = get('P2', item); xs = [int(x['layer']) for x in r]
        m = [float(x['ratio']) for x in r]; lo = [float(x['ratio_lo']) for x in r]; hi = [float(x['ratio_hi']) for x in r]; f0 = [float(x['ratio_false0']) for x in r]
        b += ax2.band(xs, lo, hi, col) + ax2.line(xs, f0, col, w=1.2, dash='4 3', pts=False) + ax2.line(xs, m, col, r=3.5)
        for Lh in ([48] if item == 'attn' else [52, 56]):
            k = xs.index(Lh); dx, dy, an = {48: (-9, 2, 'end'), 52: (9, 16, 'start'), 56: (-6, 22, 'end')}[Lh]
            b += T(ax2.X(Lh) + dx, ax2.Y(m[k]) + dy, f'{f3(m[k])} ({f3(f0[k])})', 13, col, an, weight=700)
        vals.append(f"{lab}: " + '; '.join(f"L{x} {f3(a)} {ci(c, d)} (false_0 {f3(e)})" for x, a, c, d, e in zip(xs, m, lo, hi, f0)))
    b += L.legend(720, 410, [('attention', BL, 'line'), ('MLP', OR, 'line'), ('false_0 only', PEN, 'dash')], fs=13)
    one = f"{L.F['rec']}（P1 位置子集 / P2 单层单组件；5 个假标题平均，细虚线 = 只用 false_0）· Stage 11 样本 1,186 篇 · 团队整群 95% CI · 391_groups/summary_b1_p12f/p12f_mean5.csv（b1_p12f_report.md）"
    t, h = how1(70, 432, one); b += t; y = 432 + h + 2
    t, h = valpara(70, y, 'Plotted (mean of 5 false titles [team 95% CI] (false_0)) — ' + ' | '.join(vals), 1140); b += t; y += h + 6
    # kept text (N1, N2, F2)
    txt = [('N1 name plausibility: ', 'without a title the true list looks "most real" in 0.255 of papers (chance 0.25); with the true title 0.625 [0.615, 0.635]', '(Stage 12 N1, 8,894 R0/R1 papers, paper bootstrap; N1_prior_mc.csv)'),
           ('N2 pure name prior: ', 'target − control +0.047 [0.031, 0.062] vs +0.247 with the true title → ≈ 19% of the gap (delete-title prior of §6.12: 0.35)', '(Stage 12 N2, final L63, 4,621 + 2,220, within bin, paper bootstrap; stage12_report.md)'),
           ('F2 lens fitted on author prompts: ', 'target − control ≤ 0 at L24–L56, +0.238 only at L62', '(Stage 12 F2, name positions, Stage 11 sample, true − 5 false; F2_author_lens.csv)')]
    g_, _ = L.bullets(70, max(y + 16, 590), txt, fs=16); b += g_
    b += L.footer('P1 / P2: 391_groups/summary_b1_p12f/p12f_mean5.csv (columns ratio, ratio_lo, ratio_hi, ratio_false0; who = all_authors, group = all); 391_groups/reports/b1_p12f_report.md')
    save('slide67', L.section('Stage 12: where the paper information travels', pid, b))
    ONE[67] = one
    FIVE[67] = L.how(L.F['rec'] + '（P1、P2 同一估计量：分子换成"替换后 − 未替换"，分母"真 − 未替换"，见方法手册 D-P1 / D-P2）', 'Stage 11 样本 1,186 篇（target 593 + control 593），全部作者全部名字 token，最终输出 L63；P1 层 L32–L56，P2 层 L8–L56',
                     '5 个假标题 false_0..false_4 各做一次替换，取平均（主线）；细虚线 = 只用 false_0（原 Stage 12 发表版）', L.CI['team'], '391_groups/summary_b1_p12f/p12f_mean5.csv；391_groups/reports/b1_p12f_report.md')

# ================================================================ 68 X6 / X7
def s68():
    pid = 'r68'; X6 = [r for r in rows(R13 / 'summary_x6/x6_recovery.csv') if r['group'] == 'all']
    b = L.frame(pid, 'The Stage 11 timing holds for all 5 false titles', 'X6: replacement with each of the 5 false titles · X7: knockout minus the same knockout on the false-title run (S = T − F)', 'Stage 13 · X6 X7')
    ax = Ax(120, 160, 470, 210, 24, 63, 0, 1.05)
    b += ax.frame([24, 32, 40, 48, 52, 56, 63], [0, 0.25, 0.5, 0.75, 1.0], xlab=lambda v: 'out' if v == 63 else f'L{v}', title='X6 · recovery R(l), all 1,186 papers', ytitle='R(l)')
    tcols = ['#9AA3B2', '#C9A27A', '#8FB3D6', '#A8C99A', '#D4A5B5']; vals = []
    for k in range(5):
        r = sorted([x for x in X6 if x['false_title'] == f'false_{k}'], key=lambda x: int(x['layer']))
        xs = [int(x['layer']) for x in r]; ys = [float(x['R']) for x in r]
        b += ax.line(xs, ys, tcols[k], w=1.4, pts=False)
        vals.append(f'false_{k}: ' + ' '.join(f'L{x} {f3(y)}' for x, y in zip(xs, ys)))
    r = sorted([x for x in X6 if x['false_title'] == 'average'], key=lambda x: int(x['layer']))
    xs = [int(x['layer']) for x in r]; m = [float(x['R']) for x in r]; lo = [float(x['lo']) for x in r]; hi = [float(x['hi']) for x in r]
    b += ax.band(xs, lo, hi, INK, 0.15) + ax.line(xs, m, INK, r=3.2)
    for Lh, dx, anc in [(48, 8, 'start'), (52, 8, 'start'), (40, 8, 'start')]:
        k = xs.index(Lh); b += T(ax.X(Lh) + dx, ax.Y(m[k]) + (14 if Lh == 52 else 4), f'{f3(m[k])} {ci(lo[k], hi[k])}' if Lh != 40 else f3(m[k]), 12.5, INK, anc, weight=700)
    vals.insert(0, 'mean of 5: ' + '; '.join(f'L{x} {f3(a)} {ci(c, d)}' for x, a, c, d in zip(xs, m, lo, hi)))
    b += L.legend(120, 410, [('mean of 5 (team CI)', INK, 'line')] + [(f'false_{k}', tcols[k], 'thin') for k in range(5)], fs=12.5, gap=8)
    # X7
    X7 = rows(R13 / 'summary_b1_x7f/x7f_knockout.csv')
    ax2 = Ax(720, 160, 500, 210, 0, 62, -0.05, 1.05)
    b += ax2.frame([0, 24, 32, 40, 48, 52, 56, 62], [0, 0.25, 0.5, 0.75, 1.0], title='X7 · paper-specific loss S(l), mean of 5 false titles', ytitle='S(l)')
    b += ax2.hline(0.05, RD, '6 4', 1.6, 'decision line S = 0.05', 'start', -5, 12.5)
    for grp, col in [('target', OR), ('control', BL), ('all', INK)]:
        r = sorted([x for x in X7 if x['group'] == grp and x['title'] == 'mean5'], key=lambda x: int(x['start_layer']))
        xs = [int(x['start_layer']) for x in r]; m = [float(x['S']) for x in r]; lo = [float(x['S_lo']) for x in r]; hi = [float(x['S_hi']) for x in r]
        b += ax2.band(xs, lo, hi, col, 0.14) + ax2.line(xs, m, col, w=2.4, r=3)
        vals.append(f'S {grp}: ' + '; '.join(f'L{x} {f3(a, True)} {ci(c, d, True)}' for x, a, c, d in zip(xs, m, lo, hi)))
        k = xs.index(52); yo = {'all': 0, 'target': 1, 'control': 2}[grp]
        if yo == 0: b += T(ax2.X(40), ax2.Y(0.93), 'S(L52), mean of 5 false titles:', 13, INK, weight=700)
        b += T(ax2.X(40) + 10, ax2.Y(0.93) + 18 * (yo + 1), f'{grp} {f3(m[k], True)} {ci(lo[k], hi[k], True)}' + ('  ≤ 0.05' if hi[k] <= 0.05 or m[k] <= 0.05 else ''), 13, col, weight=700)
    b += L.legend(720, 410, [('target 593', OR, 'line'), ('control 593', BL, 'line'), ('all 1,186', INK, 'line')], fs=13)
    one = f"X6：{L.F['x6']} · X7：{L.F['S']} · 1,186 篇（593 + 593），标题后全部位置，最终输出 · 团队整群 95% CI · summary_x6/x6_recovery.csv；summary_b1_x7f/x7f_knockout.csv"
    t, h = how1(70, 432, one); b += t; y = 432 + h + 2
    t, h = valpara(70, y, 'Plotted — ' + ' | '.join(vals), 1140); b += t; y += h + 8
    g_, _ = L.bullets(70, max(y + 16, 612), [('By name-token role: ', 'surname first token 0.734 at L48, surname continuation 0.893; all roles ≥ 0.96 at L52', '(X6 roles, all papers; x6x7_roles.md)'),
                                     ('Pre-registered verdict (false_0 only): ', 'target S(L52) 0.018 holds, control 0.051 just misses 0.05; 5-title mean: all groups pass', '(X7 x7_report.md; addendum 10 item 2, b1_x7f_report.md)')], fs=16); b += g_
    b += L.footer('X6: 381_stage13/summary_x6/x6_recovery.csv (group = all; false_0..4, average) · X7: 381_stage13/summary_b1_x7f/x7f_knockout.csv (title = mean5; S, S_lo, S_hi); x6_report.md, b1_x7f_report.md')
    save('slide68', L.section('The Stage 11 timing holds for all 5 false titles', pid, b))
    ONE[68] = one
    FIVE[68] = L.how(f"X6：{L.F['x6']}；X7：{L.F['S']}", 'Stage 11 样本 1,186 篇（target 593 + control 593），标题后全部位置，全部作者全部名字 token，最终输出；X6 层 L24–L63，X7 起始层 L0–L62',
                     'X6：5 个假标题各替换一次（细线），粗线为平均；X7：同样的阻断在假标题运行上做一遍（F），S = T − F；判据 S(L52) ≤ 0.05（红虚线）', L.CI['team'], '381_stage13/summary_x6/x6_recovery.csv；381_stage13/summary_b1_x7f/x7f_knockout.csv；x6_report.md；b1_x7f_report.md')

# ================================================================ 72 all-token probe
def s72():
    pid = 'r72'; C = rows(R13 / 'summary_alltok/alltok_controls.csv'); P = rows(R13 / 'summary_b1_e4b5/perdonor_by_run_layer.csv')
    prim = {r['quantity']: r for r in rows(R13 / 'summary_alltok/primary_L40.csv')}
    b = L.frame(pid, 'The probe on every name token', 'Title-position probe, all authors, all name tokens, split by role · L40 · team-cluster 95% CI', 'Stage 13 · addendum 9')
    roles = [('given_first', 'given name, first token'), ('surname_first', 'surname, first token'), ('initial', 'initial')]
    ctl = [('probe (real gold)', INK, 'probe (true − false_0)'), ('gold = random other paper', '#9AA3B2', 'gold = random other paper'), ('gold = random paper of the same field', '#C9B48A', 'gold = same-field paper')]
    ax = Ax(120, 160, 470, 210, 0, 3, -0.02, 0.17)
    b += ax.frame([], [0, 0.05, 0.10, 0.15], ylab=lambda v: f'{v:.2f}', title='Signal by role at L40, with permutation controls', ytitle='spec (nlr)')
    b += f'<line x1="{ax.x0}" y1="{ax.Y(0):.1f}" x2="{ax.x0 + ax.w}" y2="{ax.Y(0):.1f}" stroke="{INK}" stroke-width="1.4"/>'
    vals = []
    for i, (run, lab) in enumerate(roles):
        b += T(ax.X(i + 0.5), ax.y0 + ax.h + 19, lab, 13.5, INK, 'middle')
        for j, (cn, col, cl) in enumerate(ctl):
            r = [x for x in C if x['run'] == run and x['layer'] == '40' and x['control'] == cn][0]
            e, lo, hi, n = float(r['est']), float(r['lo']), float(r['hi']), int(float(r['n']))
            xc = i + 0.22 + j * 0.28; bw = 0.24 * ax.w / 3
            y0, y1 = ax.Y(max(e, 0)), ax.Y(min(e, 0))
            b += f'<rect x="{ax.X(xc) - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 0.8):.1f}" rx="2" fill="{col}" stroke="{INK}" stroke-width="1.2"/>' + ax.whisk(xc, lo, hi, INK, 1.4, 3)
            b += T(ax.X(xc), ax.Y(max(hi, 0)) - 5, f3(e, True), 11.5, INK if j == 0 else PEN, 'middle', weight=700 if j == 0 else None)
            vals.append(f'{lab} · {cl}: {f3(e, True)} {ci(lo, hi, True)} (n {n:,})')
    b += L.legend(120, 410, [(cl, col, 'box') for _, col, cl in ctl], fs=12.5, gap=10)
    # forest
    vers = [('V0', 'pre-registered (false_0)', INK, 1.0), ('Vpd', 'per-donor (post hoc, D1)', BL, 1.0), ('V5x0', '5-title mean 含泄漏，仅敏感性', '#9AA3B2', 0.55)]
    fr = []
    for run, lab in roles:
        for v, vl, col, op in vers:
            r = [x for x in P if x['run'] == run and x['layer'] == '40' and x['version'] == v][0]
            e, lo, hi, n = float(r['tc']), float(r['tc_lo']), float(r['tc_hi']), int(float(r['n']))
            fr.append((f'{lab.split(",")[0]} · {v}', e, lo, hi, col, op, f'{f3(e, True)} {ci(lo, hi, True)}'))
            vals.append(f'T − C {lab} {v}: {f3(e, True)} {ci(lo, hi, True)} (n {n:,})')
    b += T(680, 146, 'Target − control at L40 (within citation bin), three versions', 17, INK, weight=700)
    g, h = L.forest(680, 160, 560, fr, -0.04, 0.10, [-0.04, 0, 0.04, 0.08], rowh=22.5, labw=150, fs=13)
    b += g
    b += L.legend(700, 410, [('V0 pre-registered', INK, 'box'), ('Vpd per-donor', BL, 'box'), ('V5x0 含泄漏，仅敏感性', '#C3C9D2', 'box')], fs=12.5, gap=8)
    one = f"spec(p) = score(p, X_true) − score(p, X_false_0)，每个名字 token 按角色取名次 → nlr；T − C：{L.F['tc']} · L40，名 1,706 / 姓 1,395 / 首字母 1,590 篇（V0）；Vpd 3,046 / 4,654 / 4,812 篇 · 团队整群 95% CI · alltok_controls.csv；perdonor_by_run_layer.csv"
    t, hh = how1(70, 432, one); b += t; y = 432 + hh + 2
    t, hh = valpara(70, y, 'Plotted — ' + ' | '.join(vals), 1140); b += t; y += hh + 8
    sm = prim['surname_minus_initial']
    lines = [('Surname first token above the initial: ', f"{f3(float(prim['surname_first']['est']), True)} vs {f3(float(prim['initial']['est']), True)}, difference {f3(float(sm['est']), True)} {ci(float(sm['lo']), float(sm['hi']), True)} → both pre-registered checks pass; E4b (first token only, mostly initials) underestimated it", '(e4b_alltok.md §5)'),
             ('Permutation controls: ', '≈ 0 on surname and given-name tokens; ≈ +0.02 on initials → about half of the initial’s signal is not paper-specific', '(e4b_alltok.md §7)'),
             ('Target − control: ', 'given name positive in all three versions; surname not significant pre-registered, positive only post hoc (per-donor) → surname evidence weak', '(b1_e4b5_report.md)')]
    g_, _ = L.bullets(70, max(y + 16, 590), lines, fs=16); b += g_
    b += L.footer('Bars: 381_stage13/summary_alltok/alltok_controls.csv (layer 40) · forest: 381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv (tc, tc_lo, tc_hi; V0 / Vpd / V5x0) · e4b_alltok.md, b1_e4b5_report.md')
    save('slide72', L.section('The probe on every name token', pid, b))
    ONE[72] = one
    FIVE[72] = L.how('score(p, x) = mean_{a ∈ authors(p)} −log10( 1 + #{v ∈ V: ℓ_v(x) > ℓ_{g_a}(x)} )，ℓ(x) = RMSNorm(probe(x)) · W_Vᵀ；spec(p) = score(p, X_true) − score(p, X_false_0)（推广到全部作者全部名字 token，按角色取 gold）；target − control：' + L.F['tc'],
                     '标题最后一个 token 的残差，L40；target + control 论文，剔除标题复用后：名 1,706、姓 1,395、首字母 1,590 篇（V0）；逐个排除版 Vpd 名 3,046、姓 4,654、首字母 4,812 篇',
                     '置换对照：gold 换成随机另一篇 / 同领域另一篇论文的作者；三个版本 V0（预注册，只减 false_0）/ Vpd（事后偏离 D1）/ V5x0（5 个假标题平均，含泄漏，仅敏感性）', L.CI['team'],
                     '381_stage13/summary_alltok/alltok_controls.csv；381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv；e4b_alltok.md；b1_e4b5_report.md')

# ================================================================ NEW name-position probe
def snp():
    pid = 'rnp'; LC = rows(R13 / 'summary_b2_np/np_lens_compare_v2.csv'); RL = rows(R13 / 'summary_b2_np/np_role_layer_v2.csv')
    b = L.frame(pid, 'Name-position probe: H3 partly supported', 'Addendum 11 A · per-donor version Vpd (D11-1) · surname first token · all papers 4,654 · team-cluster 95% CI', 'Stage 13 · addendum 11 A')
    g, xe = L.flow(pid, 70, 128, ['title in prompt', 'residual at name-predicting position, layer l', 'ridge probe', "→ model's own L63 state", 'decode among 9,137 names → nlr'], gap=18, fs=14.5)
    b += g
    fm, fw = L.formula(70, 174, 'spec = probe(true) − probe(false)', 'false = mean of the usable false titles (Vpd)', fs=18)
    b += fm
    t, _ = para(90 + fw, 196, '按补充 11 预注册判据通过（姓首 token L40/L48）；事后检验：lens 区间同样不含 0、尺度不同无法比较大小，因此降为部分支持', 14, 1190 - 90 - fw, INK, lh=18); b += t
    ax = Ax(120, 262, 470, 170, 32, 56, -0.0, 0.3)
    b += ax.frame([32, 40, 48, 52, 56], [0, 0.1, 0.2, 0.3], ylab=lambda v: f'{v:.1f}', title='spec by layer: probe vs lenses', ytitle='spec (nlr)')
    vals = []
    sel = lambda rd: sorted([r for r in LC if r['version'] == 'Vpd' and r['run'] == 'surname_first' and r['readout'] == rd], key=lambda r: int(r['layer']))
    pr = sel('logit'); xs = [int(r['layer']) for r in pr]
    series = [('probe (9,137 name tokens)', OR, [float(r['probe_spec']) for r in pr], [float(r['probe_lo']) for r in pr], [float(r['probe_hi']) for r in pr])]
    for rd, lab, col in [('jlens_public', 'public J-lens', BL), ('logit', 'logit lens', PEN)]:
        q = sel(rd); series.append((lab + ' (full vocabulary)', col, [float(r['lens_spec']) for r in q], [float(r['lens_lo']) for r in q], [float(r['lens_hi']) for r in q]))
    for lab, col, m, lo, hi in series:
        b += ax.band(xs, lo, hi, col, 0.16) + ax.line(xs, m, col, w=2.6, r=3.2)
        for Lh in (40, 48):
            k = xs.index(Lh); dx, dy, an = {OR: (0, -9, 'middle'), BL: (-8, -3, 'end'), PEN: (8, -5, 'start')}[col]
            b += T(ax.X(Lh) + dx, ax.Y(m[k]) + dy, f3(m[k], True), 12, col, an, weight=700)
        vals.append(f'{lab}: ' + '; '.join(f'L{x} {f3(a, True)} {ci(c, d, True)}' for x, a, c, d in zip(xs, m, lo, hi)))
    b += L.legend(120, 470, [('probe', OR, 'line'), ('public J-lens', BL, 'line'), ('logit lens', PEN, 'line')], fs=13)
    b += T(120, 488, 'different rank scales (9,137 names vs full vocabulary): compare sign and CI, not size', 12, PEN)
    fr = []
    for r in sorted([r for r in RL if r['version'] == 'Vpd' and r['run'] == 'surname_first'], key=lambda r: int(r['layer'])):
        e, lo, hi = float(r['tc_diff']), float(r['tc_lo']), float(r['tc_hi'])
        fr.append((f"L{r['layer']}", e, lo, hi, OR, 1.0, f'{f3(e, True)} {ci(lo, hi, True)}')); vals.append(f"probe T − C L{r['layer']}: {f3(e, True)} {ci(lo, hi, True)}")
    b += T(680, 250, 'Probe target − control by layer (within citation bin)', 17, INK, weight=700)
    g, h = L.forest(680, 262, 560, fr, -0.02, 0.16, [0, 0.05, 0.10, 0.15], rowh=30, labw=70, fs=14); b += g
    ini = [r for r in RL if r['version'] == 'Vpd' and r['run'] == 'initial' and r['layer'] == '40'][0]
    ini_t = f"Initials (L40): permutation-control row {f3(float(ini['any_est']), True)} {ci(float(ini['any_lo']), float(ini['any_hi']), True)} ≈ half of the signal {f3(float(ini['spec']), True)} {ci(float(ini['lo']), float(ini['hi']), True)}"
    b += T(680, 470, ini_t, 13, INK); vals.append(ini_t)
    b += T(680, 488, '首字母的对照行约为信号的一半：约一半信号不是论文特有的', 12.5, PEN, font=SANS)
    one = f"{L.NOTE['np']} · T − C：档内合并差 · Vpd 4,654 篇（姓首 token），层 L32–L56 · 团队整群 95% CI · summary_b2_np/np_lens_compare_v2.csv；np_role_layer_v2.csv"
    t, hh = how1(70, 512, one); b += t; y = 512 + hh + 2
    t, hh = valpara(70, y, 'Plotted — ' + ' | '.join(vals), 1140); b += t; y += hh + 6
    b += L.footer('381_stage13/summary_b2_np/np_lens_compare_v2.csv (Vpd, surname_first; probe_spec, lens_spec) · np_role_layer_v2.csv (tc_diff; initial any_est) · 381_stage13/reports/b2_np_report_v2.md')
    save('slide_np', L.section('Name-position probe: H3 partly supported', pid, b))
    ONE['np'] = one
    FIVE['np'] = L.how(L.NOTE['np'] + '；target − control：' + L.F['tc'], 'target + control 6,841 篇中逐个假标题排除后保留 4,654 篇（姓首 token；每篇平均约 1.5 个可用假标题），名字位置（预测每个名字 token 的位置），L32、L40、L48、L52、L56；teacher forcing',
                       '主版本 Vpd（D11-1）；V0（只减 false_0）与 V5x0（含泄漏，仅敏感性）见报告；lens 对照：logit lens、public J-lens 在同一组论文、token、假标题上读；置换对照：gold 换成随机另一篇论文的作者', L.CI['team'], '381_stage13/summary_b2_np/np_lens_compare_v2.csv；np_role_layer_v2.csv；381_stage13/reports/b2_np_report_v2.md（第 5 节判据表）')

# ================================================================ NEW C24 (2-11b)
def sc24():
    pid = 'rc24'; PW = rows(R13 / 'b2_gennames_b/summary/probe_within.csv'); RB = rows(R13 / 'b2_gennames_b/summary/robust_posthoc.csv')
    b = L.frame(pid, 'Names the model writes itself: true vs fabricated', 'C24 · addendum 15, item 2-11b · 518 target papers, 671 true names (M) vs fabricated (H) · team-cluster 95% CI', 'Stage 13 · C24 (2-11b)')
    bd, bw = L.badge(800, 92, '初步：输出置信度基线进行中'); b += bd
    g, xe = L.flow(pid, 70, 128, ['model writes the author list itself', 'residuals saved during generation', 'label each written name true / fabricated', 'within-paper AUROC'], gap=20, fs=15)
    b += g
    nm = sorted([r for r in PW if r['position'] == 'name_mean'], key=lambda r: int(r['layer'])); pf = sorted([r for r in PW if r['position'] == 'pred_first'], key=lambda r: int(r['layer']))
    xs = [int(r['layer']) for r in nm]
    rb = sorted(RB, key=lambda r: int(r['layer']))
    vals = []
    ax = Ax(120, 210, 470, 210, 16, 56, 0.4, 0.85)
    b += ax.frame([16, 24, 32, 40, 48, 52, 56], [0.4, 0.5, 0.6, 0.7, 0.8], ylab=lambda v: f'{v:.1f}', title='(ii) on the name tokens: probe vs baselines', ytitle='AUROC')
    base = [('position', '#9AA3B2', float(nm[0]['position_baseline']), float(nm[0]['pos_lo']), float(nm[0]['pos_hi'])),
            ('name / string features', '#C9B48A', float(nm[0]['string_baseline']), float(nm[0]['str_lo']), float(nm[0]['str_hi'])),
            ('fame (post hoc)', '#D4A5B5', float(rb[0]['fame']), float(rb[0]['fame_lo']), float(rb[0]['fame_hi'])),
            ('combined (post hoc)', GR, float(rb[0]['combined']), float(rb[0]['comb_lo']), float(rb[0]['comb_hi']))]
    for lab, col, v, lo, hi in base:
        b += f'<rect x="{ax.x0:.1f}" y="{ax.Y(hi):.1f}" width="{ax.w:.1f}" height="{ax.Y(lo) - ax.Y(hi):.1f}" fill="{col}" fill-opacity="0.13"/>' + ax.hline(v, col, '7 4', 2)
        b += T(ax.x0 + ax.w + 4, ax.Y(v) + 4 + (8 if lab.startswith('fame') else (-6 if lab.startswith('name') else 0)), f'{f3(v)}', 12, col, weight=700)
        vals.append(f'{lab}: {f3(v)} {ci(lo, hi)}')
    sh = [float(r['shuffled']) for r in rb]
    b += ax.hline(0.5, RD, '3 3', 1.4) + ax.line(xs, sh, RD, w=1.4, r=2.5)
    b += T(ax.X(20), ax.Y(0.425), 'shuffled labels (≈ 0.5)', 12, RD)
    vals.append('shuffled: ' + '; '.join(f"L{r['layer']} {f3(float(r['shuffled']))} {ci(float(r['sh_lo']), float(r['sh_hi']))}" for r in rb))
    m = [float(r['auroc_within']) for r in nm]; lo = [float(r['lo']) for r in nm]; hi = [float(r['hi']) for r in nm]
    b += ax.band(xs, lo, hi, OR, 0.2) + ax.line(xs, m, OR, r=3.5)
    for Lh in (16, 48, 56):
        k = xs.index(Lh); b += T(ax.X(Lh) + (8 if Lh == 16 else 0), ax.Y(hi[k]) - 6, f3(m[k]), 12.5, OR, 'start' if Lh == 16 else 'middle', weight=700)
    vals.append('probe (ii) name tokens: ' + '; '.join(f'L{x} {f3(a)} {ci(c, d)}' for x, a, c, d in zip(xs, m, lo, hi)))
    b += L.legend(120, 462, [('probe (ii)', OR, 'line'), ('position', '#9AA3B2', 'dash'), ('string', '#C9B48A', 'dash'), ('fame', '#D4A5B5', 'dash'), ('combined', GR, 'dash'), ('shuffled', RD, 'thin')], fs=12, gap=7)
    # panel 2: (i) vs (ii)
    ax2 = Ax(720, 210, 500, 210, 16, 56, 0.4, 0.85)
    b += ax2.frame([16, 24, 32, 40, 48, 52, 56], [0.4, 0.5, 0.6, 0.7, 0.8], ylab=lambda v: f'{v:.1f}', title='Before the name (i) vs on the name (ii)', ytitle='AUROC')
    pv = float(nm[0]['position_baseline'])
    b += ax2.hline(pv, '#9AA3B2', '7 4', 2, f'position baseline {f3(pv)}', 'end', -5, 12) + ax2.hline(0.5, RD, '3 3', 1.4)
    m2 = [float(r['auroc_within']) for r in pf]; lo2 = [float(r['lo']) for r in pf]; hi2 = [float(r['hi']) for r in pf]
    b += ax2.band(xs, lo, hi, OR, 0.18) + ax2.line(xs, m, OR, r=3.2) + ax2.band(xs, lo2, hi2, BL, 0.18) + ax2.line(xs, m2, BL, r=3.2)
    for Lh in (24, 48):
        k = xs.index(Lh); b += T(ax2.X(Lh), ax2.Y(lo2[k]) + 16, f3(m2[k]), 12.5, BL, 'middle', weight=700)
    vals.append('probe (i) pre-name position: ' + '; '.join(f'L{x} {f3(a)} {ci(c, d)}' for x, a, c, d in zip(xs, m2, lo2, hi2)))
    b += L.legend(720, 462, [('(ii) name tokens (primary)', OR, 'line'), ('(i) position before the name (secondary)', BL, 'line')], fs=12.5)
    one = f"{L.NOTE['auroc']} · 518 篇 target 论文、3,388 个 M–H 对，L16–L56 · 团队整群 95% CI · b2_gennames_b/summary/probe_within.csv；robust_posthoc.csv"
    t, hh = how1(70, 486, one); b += t; y = 486 + hh + 2
    t, hh = valpara(70, y, 'Plotted — ' + ' | '.join(vals), 1140); b += t; y += hh + 8
    yy = max(y + 16, 612)
    for k, s in enumerate(['补充 15 预注册判据：(ii) 在 L16–L56 七层都同时高于排位基线和名字特征基线（例如 L48 0.782 [0.754, 0.812]）；(i) 名字写出之前读不出（不高于排位基线）。',
                           '前提：chat 模板下现场生成（不是 teacher forcing）；标签来自规则匹配；control 只作描述；与 H3 的关系未预注册；输出置信度基线（生成时 log-prob / 熵）进行中。']):
        t, _ = para(70, yy + k * 22, s, 13.5, 1140, INK, lh=17); b += t
    b += L.footer('381_stage13/b2_gennames_b/summary/probe_within.csv (auroc_within, lo, hi; position / string baselines) · robust_posthoc.csv (fame, combined, shuffled CI) · b2_gennames_b_report.md, b2_gennames_b_robust_posthoc.md')
    save('slide_c24', L.section('Names the model writes itself: true vs fabricated (C24)', pid, b))
    ONE['c24'] = one
    FIVE['c24'] = L.how(L.NOTE['auroc'] + '；判据：CI(probe − 排位) > 0 且 CI(probe − 名字特征) > 0', 'target 论文中至少有 1 个真作者和 1 个编造名字的 518 篇，671 个真名，3,388 个论文内名字对；L16–L56 七层；(ii) 名字 token 平均（主）、(i) 写名字之前的位置（次）；chat 模板下现场生成',
                        '基线：名字在列表中的位置；名字长度与队列内频率；名气（事后）；三者合并（事后）；打乱标签（训练折内置换）≈ 0.5', L.CI['team'], '381_stage13/b2_gennames_b/summary/probe_within.csv；robust_posthoc.csv；381_stage13/reports/b2_gennames_b_report.md；b2_gennames_b_robust_posthoc.md')

# ================================================================ 82 chart (E1 denominators)
def s82_svg():
    V = [r for r in rows(G / 'b2_cd/summary/cd_group_values.csv') if r['experiment'] == 'E1' and r['who'] == 'unwritten' and r['layer'] == '48' and r['item'] == 'recovery']
    ax = Ax(70 + 60, 12, 420, 120, 0, 4, 0, 0.7)
    o = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 190" width="1140" height="190" role="img" aria-label="E1 denominators by group">'
    o += ax.frame([], [0, 0.2, 0.4, 0.6], ylab=lambda v: f'{v:.1f}', ytitle='')
    o += T(560, 22, 'Denominator effect (L03): E1 true − false gap by group, unwritten authors', 15, INK, weight=700)
    vals = []
    for i, gname in enumerate(['A', 'B', 'C', 'D']):
        r = [x for x in V if x['group'] == gname and x['source'] != 'stage11'] or [x for x in V if x['group'] == gname]
        r = r[0]; d, lo, hi, n = float(r['denominator']), float(r['den_lo']), float(r['den_hi']), int(float(r['n_papers']))
        col = {'A': OR, 'B': BL, 'C': '#E9B27A', 'D': '#9DBCE0'}[gname]; xc = i + 0.5; bw = 60
        o += f'<rect x="{ax.X(xc) - bw / 2:.1f}" y="{ax.Y(d):.1f}" width="{bw}" height="{ax.Y(0) - ax.Y(d):.1f}" rx="3" fill="{col}" stroke="{INK}" stroke-width="1.2"/>' + ax.whisk(xc, lo, hi, INK, 1.4, 4)
        o += T(ax.X(xc), ax.Y(hi) - 5, f3(d), 13, INK, 'middle', weight=700) + T(ax.X(xc), ax.Y(0) + 17, f'{gname} ({n:,})' + (' descr.' if gname == 'D' else ''), 13, INK, 'middle')
        vals.append(f'{gname}: {f3(d)} {ci(lo, hi)} (n {n:,})')
    t, _ = para(600, 48, '怎么算：分母 = mean_p[ T̄_p − F̄_p ]（' + L.F['rec'] + ' 的分母，false_0）· 未写出的作者，Stage 11 样本 + 补充 11 B 补全（C 462、D 33 篇只作描述）· 团队整群 95% CI · 出处：391_groups/b2_cd/summary/cd_group_values.csv（b2_cd_report.md）', 10.5, 530, '#4B5363', lh=13.5); o += t
    t, _ = para(600, 118, 'Plotted — ' + ' | '.join(vals), 9.5, 530, '#7A808C', lh=11.6); o += t
    o += '</svg>'
    ONE[82] = '分母 = mean_p[ T̄_p − F̄_p ] · 未写出作者，A 557 / B 586 / C 462 / D 33 篇 · 团队整群 · cd_group_values.csv'
    FIVE[82] = L.how('分母 = mean_p[ T̄_p − F̄_p ]，即 ' + L.F['rec'] + ' 的分母；parity：max |Δlogit|（容差 0.25 → 0.5）；首名复现率 = 复现出的第一作者名字比例', 'E1 未写出作者：A 557、B 586、C 462、D 33 篇（D 只作描述）；parity 12 个上下文、25 对；2-11 首名复现率 0.880',
                     '分母只用 false_0；C 与 A 比较在同一引用档内（258 篇可比）', L.CI['team'] + '（分母柱）；parity 与复现率无区间', '391_groups/b2_cd/summary/cd_group_values.csv；351_stage10/reports/parity.json；381_stage13/orch_b2/state.json；m3_scores.md §2')
    return o

if __name__ == '__main__':
    s67(); s68(); s72(); snp(); sc24(); svg82 = s82_svg(); (OUT / 'slide82_chart.svg').write_text(svg82, encoding='utf-8')
    json.dump({'one': {str(k): v for k, v in ONE.items()}, 'five': {str(k): v for k, v in FIVE.items()}}, open(OUT / 'charts_how.json', 'w'), ensure_ascii=False, indent=1)
    print('ok', sorted(map(str, ONE)))
