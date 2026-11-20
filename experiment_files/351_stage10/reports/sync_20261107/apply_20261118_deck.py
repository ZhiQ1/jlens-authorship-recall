"""2026-11-18: new chart slides for the merged main deck (stage1_11_deck.html), same conventions as round r
(apply_20261112r_lib.py). Builds 7 <section>s into r_frag_20261118/*.html from the source CSVs; inserted by
apply_20261118_insert.py.  Stage 13 block (after C24): addendum 18b items 1, 5, 6, 4 (layer order).
Groups appendix (after 'P1 / P2: the same small-denominator effect'): addendum 16 (B, D), C (fabricated names), addendum 19 (F).
Every plotted number is an SVG <text>; source under each chart; every chart has a formula box and 'n = ... papers'."""
import csv, math
from pathlib import Path
import numpy as np
import apply_20261112r_lib as L
from apply_20261112r_lib import T, para, Ax, f3, ci, rows, INK, PEN, OR, BL, GR, RD, PINK, LIGHT, SANS, HAND

OUT = Path(__file__).parent / 'r_frag_20261118'; OUT.mkdir(exist_ok=True)
R13, G = L.R13, L.G391
GREY = '#8a8f98'


def save(name, html_):
    (OUT / f'{name}.html').write_text(html_, encoding='utf-8')


def valpara(x, y, s, maxw=1140):
    return para(x, y, s, 9, maxw, '#7A808C', lh=11)


def how1(x, y, s, maxw=1140):
    return para(x, y, '怎么算：' + s, 10.5, maxw, '#4B5363', lh=13.2)


def nlab(x, y, s, anchor='start'):
    return T(x, y, s, 12, GREY, anchor, font=SANS)


def cn(x, y, s, bold=False, maxw=1140, fs=13.5):
    t, h = para(x, y, s, fs, maxw, INK, lh=17)
    if bold: t = t.replace('<text ', '<text font-weight="700" ', 1)
    return t, h


def fmt(v, sign=True, d=3):
    s = f'{v:+.{d}f}' if sign else f'{v:.{d}f}'
    return s.replace('-', '−')


def cif(lo, hi, sign=True, d=3):
    return f'[{fmt(lo, sign, d)}, {fmt(hi, sign, d)}]'


def bar(ax, x, v, w, col, op=0.85):
    y0, y1 = ax.Y(0), ax.Y(v)
    return f'<rect x="{ax.X(x) - w / 2:.1f}" y="{min(y0, y1):.1f}" width="{w:.1f}" height="{abs(y0 - y1):.1f}" fill="{col}" fill-opacity="{op}" stroke="{INK}" stroke-width="1"/>'


def fill_bottom(b, y, blocks):
    """blocks: list of (kind, text) rendered from y downward; returns svg"""
    for kind, s in blocks:
        if kind == 'how':
            t, h = how1(70, y, s)
        elif kind == 'val':
            t, h = valpara(70, y, s)
        elif kind == 'bold':
            t, h = cn(70, y, s, True)
        else:
            t, h = cn(70, y, s)
        b += t; y += h + (4 if kind == 'how' else 8 if kind == 'val' else 4)
    return b, y


# ================================================================ 18b item 1: readout map
def s_item1():
    pid = 'r18b1'
    M = rows(R13 / 'summary_a18b_item1/item1_map.csv'); C = rows(R13 / 'summary_a18b_item1/item1_criterion.csv')
    layers = [8, 16, 24, 32, 36] + list(range(40, 53)) + [56, 60]
    pos = [('title_all', 'title: all'), ('title_content', 'title: content'), ('title_first', 'title: first'), ('title_last', 'title: last'),
           ('quote', 'quote after title'), ('year', 'year digits'), ('close', '")?\\n"'), ('authors', '"Authors"'), ('colon', '":"')]
    ref = ('name_surname_first', 'name: surname 1st (ref.)')
    idx = {(m['readout'], m['kind'], m['position'], int(m['layer'])): m for m in M}
    met = {}
    for r in C:
        if r['layers_meeting_rule']:
            met[(r['readout'], r['kind'], r['position'])] = [int(x) for x in r['layers_meeting_rule'].split(';')]
    b = L.frame(pid, 'Readout map: where does the paper signal show first?',
                'Addendum 18b item 1 (locked 2026-11-17) · 3 readouts × 9 prompt positions × 20 layers · gold = surname first token · within-bin target − control of spec', 'Stage 13 · 18b item 1')
    bd, bw = L.badge(70, 124, '锁定规则：部分格子满足 · 效应小 · 未做多重比较校正'); b += bd
    fm, fw = L.formula(1210 - 560, 120, 'T−C(pos, l) = Σ_b w_b [ spec̄_T,b − spec̄_C,b ]', 'spec = nlr(true) − mean_k nlr(false_k),  nlr = log10(1/rank)', fs=16, w=560); b += fm
    cw, rh, x_lab, y0 = 17, 17, 70, 206
    panels = [('logit', 'logit lens'), ('jlens_public', 'public J-lens'), ('probe', 'name-token probe')]
    x0s = [70 + 112 + k * (20 * cw + 18) for k in range(3)]
    allrows = pos + [ref]
    for k, (ro, lab) in enumerate(panels):
        x0 = x0s[k]
        b += T(x0, y0 - 8, lab, 15, INK, weight=700)
        # rule limit at L48 (after column of L48)
        xl = x0 + (layers.index(48) + 1) * cw
        b += f'<line x1="{xl:.1f}" y1="{y0 - 3:.1f}" x2="{xl:.1f}" y2="{y0 + rh * len(allrows) + 3:.1f}" stroke="{RD}" stroke-width="1.4" stroke-dasharray="4 3"/>'
        for i, (p, plab) in enumerate(allrows):
            y = y0 + i * rh
            kind = 'next_token' if p == ref[0] else 'surname'
            if k == 0:
                b += T(x0 - 6, y + 12.5, plab, 11.5, INK if p != ref[0] else PEN, 'end')
            for j, Lr in enumerate(layers):
                m = idx.get((ro, kind, p, Lr)); x = x0 + j * cw
                v = float(m['tc']) if m and m['tc'] not in ('', 'nan') else float('nan')
                if math.isnan(v):
                    b += f'<rect x="{x + .5:.1f}" y="{y + .5:.1f}" width="{cw - 1}" height="{rh - 1}" fill="#EEEEEE" stroke="none"/>'
                    continue
                a = min(abs(v) / 0.05, 1.0) * 0.85
                col = OR if v > 0 else BL
                b += f'<rect x="{x + .5:.1f}" y="{y + .5:.1f}" width="{cw - 1}" height="{rh - 1}" fill="{col}" fill-opacity="{a:.2f}" stroke="#E7DADA" stroke-width="0.5"/>'
                if float(m['tc_lo']) > 0:
                    b += f'<circle cx="{x + cw / 2:.1f}" cy="{y + rh / 2:.1f}" r="2.3" fill="{INK}"/>'
                if Lr in met.get((ro, kind, p), []):
                    b += f'<rect x="{x + 1.2:.1f}" y="{y + 1.2:.1f}" width="{cw - 2.4}" height="{rh - 2.4}" fill="none" stroke="{RD}" stroke-width="2"/>'
        yb = y0 + rh * len(allrows)
        for j, Lr in enumerate(layers):
            if Lr in (8, 24, 40, 48, 56):
                b += T(x0 + j * cw + cw / 2, yb + 13, f'L{Lr}', 11, PEN, 'middle')
    yb = y0 + rh * len(allrows)
    b += nlab(x0s[0], yb + 28, 'n = 600 papers (300 target + 300 control; Stage 11 subsample, seed 1817) · grey = not estimable')
    # legend
    lx, ly = x0s[0], yb + 44
    b += f'<rect x="{lx}" y="{ly - 10}" width="14" height="12" fill="{OR}" fill-opacity="0.6"/>' + T(lx + 18, ly, 'T − C > 0', 12, INK)
    b += f'<rect x="{lx + 88}" y="{ly - 10}" width="14" height="12" fill="{BL}" fill-opacity="0.6"/>' + T(lx + 106, ly, '< 0 (shade to ±0.05)', 12, INK)
    b += f'<circle cx="{lx + 240}" cy="{ly - 4}" r="2.6" fill="{INK}"/>' + T(lx + 247, ly, 'CI > 0', 12, INK)
    b += f'<rect x="{lx + 300}" y="{ly - 11}" width="14" height="13" fill="none" stroke="{RD}" stroke-width="2"/>' + T(lx + 318, ly, 'meets the locked rule', 12, INK)
    b += f'<line x1="{lx + 450}" y1="{ly - 10}" x2="{lx + 450}" y2="{ly + 2}" stroke="{RD}" stroke-width="1.4" stroke-dasharray="4 3"/>' + T(lx + 456, ly, 'L48 limit', 12, INK)
    # counts
    grp = [r for r in C if r['kind'] != 'next_token']
    n_met = sum(1 for r in grp if r['layers_meeting_rule'])
    cells = [m for m in M if m['kind'] != 'next_token' and int(m['layer']) <= 48 and m['tc'] not in ('', 'nan') and not math.isnan(float(m['tc']))]
    n_pos = sum(1 for m in cells if float(m['tc_lo']) > 0)
    n_rule = sum(len(r['layers_meeting_rule'].split(';')) for r in grp if r['layers_meeting_rule'])
    effs = []
    for r in grp:
        for Lr in (r['layers_meeting_rule'].split(';') if r['layers_meeting_rule'] else []):
            effs.append(float(idx[(r['readout'], r['kind'], r['position'], int(Lr))]['tc']))
    assert len(cells) == 672 and n_pos == 60 and n_rule == 59 and n_met == 15, (len(cells), n_pos, n_rule, n_met)
    earliest = {}
    for r in grp:
        if r['layers_meeting_rule']:
            earliest.setdefault((r['readout'], r['kind']), []).append(f"{r['position']} L{r['layers_meeting_rule'].split(';')[0]}")
    def e(ro, k): return ', '.join(earliest.get((ro, k), [])) or '—'
    one = ('T−C = 引用分箱内 target − control 的 spec（spec = 真标题 − 5 个假标题平均，nlr = log10(1/rank)，只在 9,137 个名字 token id 内排名）；锁定规则：某位置组在 L ≤ 48 的某层 T−C CI > 0，'
           '而同层名字位置（姓首 token）CI 含 0 → "柜子先在该位置" · 600 篇（Stage 11 子样本）· 团队整群 2,000 次 · 381_stage13/summary_a18b_item1/item1_map.csv、item1_criterion.csv')
    vals = (f"Earliest layer meeting the rule — surname gold: logit {e('logit', 'surname')}; J-lens {e('jlens_public', 'surname')}; probe {e('probe', 'surname')} | "
            f"first-token gold: logit {e('logit', 'first')}; J-lens {e('jlens_public', 'first')}; probe {e('probe', 'first')} | "
            f"name position (ref.) first CI > 0: logit L52, J-lens L56, probe L48 | rule met in {n_met} of 48 position × gold × readout groups ('quote' not estimable), {n_rule} cells; "
            f"T − C in those cells {fmt(min(effs))} to {fmt(max(effs))}")
    b, y = fill_bottom(b, yb + 64, [
        ('how', one), ('val', vals),
        ('bold', f'按锁定规则：部分格子满足"柜子先在该位置"（logit lens 姓首 token：年份 L40 起、":" L45 起、"Authors" L36；J-lens 标题首 token L8；probe 标题全部 L32、年份 L32），'
                 f'但效应小（{fmt(min(effs))} 至 {fmt(max(effs))}）。'),
        ('bold', f'多重比较：L ≤ 48 共检验 672 格（3 种读出 × 2 种 gold × 8 个位置组 × 14 层），{n_pos} 格 CI > 0；若各格独立、无效应，按单侧 2.5% 约 17 格会偶然 CI > 0（相邻层高度相关，'
                 f'这个数只作量级参考）。未做校正，因此只作为位置线索，不据此下"柜子在年份 / 标题"的结论。'),
        ('plain', '前提：规则比较两个 CI（该位置 CI > 0、名字位置 CI 含 0），不是配对差检验；probe 只用这 600 篇训练，比补充 11 的 9,108 篇 probe 弱；"first" gold 的结果在上方数字行。'),
    ])
    b += L.footer('381_stage13/summary_a18b_item1/item1_report.md · item1_map.csv (tc, tc_lo, tc_hi per readout × kind × position × layer) · item1_criterion.csv (locked rule) · config/prereg_addendum18b.md (sha256 9104c351…)')
    save('a_item1', L.section('Addendum 18b item 1: readout map', pid, b))
    return y


# ================================================================ 18b item 5: title tokens
def s_item5():
    pid = 'r18b5'
    R = {(r['readout'], r['quantity']): r for r in rows(R13 / 'summary_a18b_item5/item5_table.csv')}
    g = lambda q, k='est': float(R[('final', q)][k])
    n = lambda q: int(R[('final', q)]['n_papers'])
    cls = [('content', 'content words'), ('rare', 'rare words'), ('function', 'function words'), ('firstlast', 'first / last token')]
    b = L.frame(pid, 'Which title words carry the paper signal?',
                'Addendum 18b item 5 (design locked 2026-11-17, no numeric rule → descriptive) · replace one word class by WordNet synonyms or random tokens · final output', 'Stage 13 · 18b item 5')
    bd, bw = L.badge(70, 124, '描述性（无锁定判据）'); b += bd
    fm, fw = L.formula(1210 - 520, 120, 'loss = S(true) − S(variant),  Δ = loss(syn) − loss(rand)', 'S = nlr(true) − mean_k nlr(false_k), paper mean; Δ < 0 → synonyms keep more', fs=16, w=520); b += fm
    ax = Ax(120, 215, 520, 190, 0, 4, 0, 0.42)
    b += ax.frame([], [0, 0.1, 0.2, 0.3, 0.4], ylab=lambda v: f'{v:.1f}', title='Loss of the paper signal when a word class is replaced', ytitle='loss (nlr)')
    S = g('spec_true')
    b += ax.hline(S, RD, '6 4', 1.6, f'all of the signal: S(true) = {f3(S)}', 'end', -5, 12)
    vals = [f"S(true) {f3(S)} {ci(g('spec_true', 'lo'), g('spec_true', 'hi'))} (n {n('spec_true')})"]
    for i, (c, lab) in enumerate(cls):
        xc = i + 0.5
        for dx, kind, col in ((-0.17, 'syn', GR), (0.17, 'rand', OR)):
            q = f'loss_{c}_{kind}'; v, lo, hi = g(q), g(q, 'lo'), g(q, 'hi')
            b += bar(ax, xc + dx, v, 30, col) + ax.whisk(xc + dx, lo, hi, INK, 1.4, 3)
            b += T(ax.X(xc + dx), ax.Y(hi) - 5, f3(v), 12, INK, 'middle', weight=700)
            vals.append(f'{lab} {kind} {f3(v)} {ci(lo, hi)} (n {n(q)})')
        b += T(ax.X(xc), ax.Y(0) + 17, lab, 13.5, INK, 'middle')
        b += nlab(ax.X(xc), ax.Y(0) + 31, f"n {n(f'loss_{c}_syn')} / {n(f'loss_{c}_rand')}", 'middle')
    b += L.legend(120, 460, [('WordNet synonym', GR, 'box'), ('random tokens', OR, 'box')], fs=13)
    b += nlab(120, 478, 'n = papers with ≥ 1 word of that class changed (of 600)')
    # right: forest of syn - rand
    fr = []
    for c, lab in cls:
        q = f'syn_minus_rand_loss_{c}'; v, lo, hi = g(q), g(q, 'lo'), g(q, 'hi')
        fr.append((lab, v, lo, hi, PINK, 1.0, f'{fmt(v)} {cif(lo, hi)}'))
        vals.append(f'{lab} syn − rand {fmt(v)} {cif(lo, hi)} (n {n(q)})')
    b += T(700, 199, 'Synonym − random (Δ), paired', 17, INK, weight=700)
    fo, fh = L.forest(700, 222, 530, fr, -0.32, 0.02, [-0.3, -0.2, -0.1, 0], rowh=34, labw=130, fs=14); b += fo
    b += nlab(700, 222 + fh + 18, 'n = 596 / 397 / 580 / 544 papers (both variants changed)')
    P = R13 / 'summary_a18b_item5/item5_table.csv'
    pr = {(r['readout'], r['quantity']): r for r in rows(P)}
    pl = [float(pr[(f'probe_L{l}_surname', 'syn_minus_rand_loss_content')]['est']) for l in (8, 12, 16, 20, 24)]
    b += T(700, 222 + fh + 44, f'Title-position probe (last title token, L8–L24, surname gold):', 13.5, INK)
    b += T(700, 222 + fh + 62, f'content Δ {fmt(max(pl))} to {fmt(min(pl))}, all CI < 0 — same direction, small', 13.5, INK)
    vals.append('probe L8–L24 surname gold, content syn − rand: ' + '; '.join(f'L{l} {fmt(v)}' for l, v in zip((8, 12, 16, 20, 24), pl)))
    one = ('loss = S(true) − S(替换后)，S = 论文平均 nlr(真标题) − 5 个假标题平均；Δ = loss(同义词) − loss(随机)，同一组 bootstrap 上配对；词类与替换表在任何 GPU 输出前固定（罕见 = 队列标题文档频率 ≤ 5；同义词 = WordNet 3.0；功能词 = 固定近义表）'
           ' · 600 篇（Stage 11 子样本），某变体没有可替换词的论文不计入 · 团队整群 2,000 次 · 381_stage13/summary_a18b_item5/item5_table.csv')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', f"描述性：内容词换成随机 token 损失 {fmt(g('loss_content_rand'))} {cif(g('loss_content_rand', 'lo'), g('loss_content_rand', 'hi'))}（信号全部消失，S 变成 {fmt(g('spec_content_rand'))}），"
                 f"换成同义词只损失 {fmt(g('loss_content_syn'))}；Δ {fmt(g('syn_minus_rand_loss_content'))} {cif(g('syn_minus_rand_loss_content', 'lo'), g('syn_minus_rand_loss_content', 'hi'))}。罕见词、功能词、首末 token 的损失都小得多。"),
        ('plain', '局限：WordNet 同义词很粗糙（不保证意思不变），这只是弱的"保留意思"检验；随机替换改动的 token 更多（内容词平均 12.8 vs 5.6 个 token），Δ 的一部分可能来自改动量；'
                  '有同义词的论文更少（罕见词 397 篇）；600 篇子样本，无锁定判据。'),
    ])
    b += L.footer('381_stage13/summary_a18b_item5/item5_report.md · item5_table.csv (readout final and probe_L8–L24; est, lo, hi, n_papers) · variant table a18b_config/item5_variants_v3.parquet · config/prereg_addendum18b.md')
    save('b_item5', L.section('Addendum 18b item 5: title-token importance', pid, b))
    return y


# ================================================================ 18b item 6: MLP lookup L52-56
def s_item6():
    pid = 'r18b6'
    P = {r['config']: r for r in rows(R13 / 'summary_a18b_item6/item6_patch_mean5.csv')}
    NE = rows(R13 / 'summary_a18b_item6/item6_neurons.csv') if (R13 / 'summary_a18b_item6/item6_neurons.csv').exists() else []
    Ls = [52, 53, 54, 55, 56]
    b = L.frame(pid, 'L52–L56: MLPs carry the paper signal, mostly not as author-name directions',
                'Addendum 18b item 6 (design locked 2026-11-17, no numeric rule → descriptive) · patch true → false, whole aligned tail · 5 false titles · 600 papers', 'Stage 13 · 18b item 6', title_fs=40)
    bd, bw = L.badge(70, 124, '描述性（无锁定判据）'); b += bd
    fm, fw = L.formula(1210 - 590, 120, 'R = mean_p[ nlr_patched − nlr_false ] / mean_p[ nlr_true − nlr_false ]', 'patched output = out_F + P (out_T − out_F);  P = full / author-aligned 512-d / orthogonal / random 512-d', fs=16, w=590); b += fm
    ax = Ax(120, 210, 500, 186, 52, 56, 0, 0.32)
    b += ax.frame(Ls, [0, 0.1, 0.2, 0.3], ylab=lambda v: f'{v:.1f}', title='Recovery R by layer and patched part', ytitle='R')
    series = [('mlp_full', 'MLP full', OR, None), ('mlp_orth', 'MLP orthogonal', OR, '6 4'), ('attn_full', 'attention full', BL, None),
              ('mlp_aligned', 'MLP author-aligned', RD, None), ('mlp_rand', 'MLP random 512-d', '#9AA3B2', None)]
    vals = []
    for key, lab, col, dash in series:
        m = [float(P[f'{key}@{l}']['recovery']) for l in Ls]; lo = [float(P[f'{key}@{l}']['lo']) for l in Ls]; hi = [float(P[f'{key}@{l}']['hi']) for l in Ls]
        b += ax.band(Ls, lo, hi, col, 0.15) + ax.line(Ls, m, col, w=2.6 if dash is None else 2, dash=dash, r=3)
        vals.append(f'{lab}: ' + '; '.join(f'L{l} {f3(a)} {ci(c, d)}' for l, a, c, d in zip(Ls, m, lo, hi)))
        k = 2 if key in ('mlp_full', 'mlp_orth') else 4
        b += T(ax.X(Ls[k]) + (6 if k == 4 else 0), ax.Y(m[k]) - 7 + (14 if key in ('mlp_orth', 'mlp_rand') else 0), f3(m[k]), 12, col, 'start' if k == 4 else 'middle', weight=700)
    b += L.legend(120, 440, [(lab, col, 'dash' if dash else 'line') for _, lab, col, dash in series[:3]], fs=12, gap=8)
    b += L.legend(120, 456, [(lab, col, 'dash' if dash else 'line') for _, lab, col, dash in series[3:]], fs=12, gap=8)
    b += nlab(120, 474, 'n = 600 papers (300 target + 300 control) · five-title mean · shaded = team 95% CI')
    # right: target - control of MLP full + contrasts
    fr = []
    for l in Ls:
        r = P[f'mlp_full@{l}']; v, lo, hi = float(r['tc_diff']), float(r['tc_lo']), float(r['tc_hi'])
        fr.append((f'L{l}', v, lo, hi, OR, 1.0, f'{fmt(v)} {cif(lo, hi)}'))
    vals.append('MLP full target − control: ' + '; '.join(f'{a} {t}' for a, _, _, _, _, _, t in fr))
    b += T(690, 199, 'MLP full: target − control of R', 17, INK, weight=700)
    fo, fh = L.forest(690, 222, 540, fr, -0.10, 0.06, [-0.08, -0.04, 0, 0.04], rowh=26, labw=60, fs=14); b += fo
    b += nlab(690, 222 + fh + 18, 'n = 300 target + 300 control papers')
    cyy = 222 + fh + 44
    CT = {(int(r['layer']), r['contrast']): r for r in rows(R13 / 'summary_a18b_item6/item6_contrasts.csv')}
    a_r = [float(CT[(l, 'mlp_aligned − mlp_rand')]['diff']) for l in Ls]
    b += T(690, cyy, f'aligned − random (paired): {fmt(min(a_r))} to {fmt(max(a_r))}, all CI > 0', 13.5, INK)
    b += T(690, cyy + 18, 'neurons (a): top-50 changed neurons overlap 0.27–0.30 within', 13.5, INK)
    b += T(690, cyy + 36, 'a paper vs 0.01–0.05 between papers (Jaccard)', 13.5, INK)
    vals.append('aligned − random: ' + '; '.join(f'L{l} {fmt(v)}' for l, v in zip(Ls, a_r)))
    mf = [float(P[f'mlp_full@{l}']['recovery']) for l in Ls]; at = [float(P[f'attn_full@{l}']['recovery']) for l in Ls]
    ma = [float(P[f'mlp_aligned@{l}']['recovery']) for l in Ls]; mr = [float(P[f'mlp_rand@{l}']['recovery']) for l in Ls]; mo = [float(P[f'mlp_orth@{l}']['recovery']) for l in Ls]
    one = ('R = mean_p[ nlr(替换后) − nlr(假标题) ] / mean_p[ nlr(真标题) − nlr(假标题) ]，5 个假标题平均；在整个对齐尾部（P2 位置）把第 l 层 MLP 或注意力输出换成 out_F + P(out_T − out_F)；'
           '作者子空间 = 9,137 个名字 token 的 lm_head 行 × final-norm 权重（中心化）的前 512 个右奇异向量（占方差 0.339），对照 = 随机 512 维 · 600 篇 · 团队整群 2,000 次（配对）· 381_stage13/summary_a18b_item6/item6_patch_mean5.csv、item6_contrasts.csv')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', f'描述性：替换整个 MLP 输出可恢复真 − 假差距的 {f3(min(mf))}–{f3(max(mf))}（L54 最高），注意力 {f3(min(at))}–{f3(max(at))}；与作者名字输出方向对齐的 512 维只恢复 {f3(min(ma))}–{f3(max(ma))}，'
                 f'略高于随机 512 维（{f3(min(mr))}–{f3(max(mr))}）；大部分在正交部分（{f3(min(mo))}–{f3(max(mo))}）→ 这些 MLP 携带论文信息，但不是现成的"作者名字方向"。'),
        ('plain', '前提：control 论文的恢复比例略高于 target（L52–L54 CI < 0，L55–L56 含 0）；作者子空间只占名字行方差的 0.339；自检 WARN：未替换的 false_0 名次与已存 Stage 11 行完全一致的比例 0.538（阈值 0.95，bf16 批形状差异），按规则继续算。'),
    ])
    b += L.footer('381_stage13/summary_a18b_item6/item6_report.md · item6_patch_mean5.csv (recovery, lo, hi, tc_diff) · item6_contrasts.csv · item6_neurons.csv · config/prereg_addendum18b.md · P2 reference: 391_groups/summary_b1_p12f/p12f_mean5.csv')
    save('c_item6', L.section('Addendum 18b item 6: MLP memory lookup', pid, b))
    return y


# ================================================================ 18b item 4: L57-61 ablation
def s_item4():
    pid = 'r18b4'
    TB = {r['quantity']: r for r in rows(R13 / 'summary_a18b_item4/item4_table.csv')}
    CR = {r['layer']: r for r in rows(R13 / 'summary_a18b_item4/item4_criterion.csv')}
    Ls = [57, 58, 59, 60, 61]
    b = L.frame(pid, 'L57–L61: the last layers are written by the MLPs',
                'Addendum 18b item 4 (locked 2026-11-17) · mean ablation of one component in one layer · prompt tail + all name inputs · 600 papers', 'Stage 13 · 18b item 4')
    allmet = all('MLP > attention' in CR[str(l)]['verdict'] for l in Ls)
    bd, bw = L.badge(70, 124, '锁定判据：达成（5 / 5 层）' if allmet else '锁定判据：未全部达成'); b += bd
    fm, fw = L.formula(1210 - 540, 120, 'loss(c, l) = S(none) − S(c ablated at l)', 'S = nlr(true) − mean_k nlr(false_k), final output;  criterion: loss(MLP) − loss(attn) > 0', fs=16, w=540); b += fm
    ax = Ax(120, 215, 500, 200, 56.4, 61.6, -0.004, 0.06)
    b += ax.frame(Ls, [0, 0.02, 0.04, 0.06], ylab=lambda v: f'{v:.2f}', title='Loss when one component is mean-ablated', ytitle='loss (nlr)')
    vals = [f"S(none) {f3(float(TB['S_none']['all']))} {ci(float(TB['S_none']['all_lo']), float(TB['S_none']['all_hi']))}"]
    for l in Ls:
        for dx, comp, col in ((-0.18, 'attn', BL), (0.18, 'mlp', OR)):
            r = TB[f'loss_{comp}{l}']; v, lo, hi = float(r['all']), float(r['all_lo']), float(r['all_hi'])
            b += bar(ax, l + dx, v, 30, col) + ax.whisk(l + dx, lo, hi, INK, 1.4, 3)
            if comp == 'mlp':
                b += T(ax.X(l + dx), ax.Y(hi) - 5, f3(v), 12, INK, 'middle', weight=700)
                b += T(ax.X(l + dx), ax.Y(hi) - 19, f"{float(r['share_of_S']) * 100:.0f}% of S", 11, PEN, 'middle')
            vals.append(f'{comp} L{l} {fmt(v)} {cif(lo, hi)}')
    b += T(ax.X(56.82), ax.Y(0.006), 'attn ≈ 0', 12, BL, 'middle', weight=700)
    b += L.legend(120, 462, [('attention ablated', BL, 'box'), ('MLP ablated', OR, 'box')], fs=13)
    b += nlab(120, 478, f"n = 600 papers (300 target + 300 control) · S(none) = {f3(float(TB['S_none']['all']))}")
    fr = []
    for l in Ls + ['mean']:
        r = CR[str(l)]; v, lo, hi = float(r['mlp_minus_attn_loss']), float(r['lo']), float(r['hi'])
        fr.append((f'L{l}' if l != 'mean' else 'mean L57–61', v, lo, hi, OR if l != 'mean' else INK, 1.0, f'{fmt(v)} {cif(lo, hi)}'))
        vals.append(f"MLP − attn {'L' + str(l) if l != 'mean' else 'mean'} {fmt(v)} {cif(lo, hi)}, T − C {fmt(float(r['tc']))} {cif(float(r['tc_lo']), float(r['tc_hi']))}")
    b += T(690, 199, 'Criterion: MLP loss − attention loss (paired)', 17, INK, weight=700)
    fo, fh = L.forest(690, 222, 540, fr, 0, 0.06, [0, 0.02, 0.04, 0.06], rowh=27, labw=110, fs=14); b += fo
    b += nlab(690, 222 + fh + 18, 'n = 600 papers · one shared bootstrap draw → paired')
    rm = CR['mean']
    b += T(690, 222 + fh + 44, f"target − control of the difference: {fmt(float(rm['tc']))} {cif(float(rm['tc_lo']), float(rm['tc_hi']))}", 13.5, INK)
    b += T(690, 222 + fh + 62, 'reference P2 (patching, ≤ L56): MLP 0.181 at L52, 0.226 at L56', 13.5, INK)
    mlp = [float(TB[f'loss_mlp{l}']['all']) for l in Ls]; sh = [float(TB[f'loss_mlp{l}']['share_of_S']) for l in Ls]
    att = [float(TB[f'loss_attn{l}']['all']) for l in Ls]
    one = ('loss = S(不消融) − S(消融)，S = 终输出 nlr(真标题) − 5 个假标题平均（论文平均）；消融 = 在标题后的尾部（p1..p9）和全部名字输入位置，把第 l 层的注意力或 MLP 输出换成参考均值（另外 586 篇、5 个假标题下同一位置的平均，事先固定）；'
           '判据 = loss(MLP) − loss(注意力) 配对 CI > 0 · 600 篇 · 团队整群 2,000 次（同一组抽样 → 配对）· 381_stage13/summary_a18b_item4/item4_table.csv、item4_criterion.csv')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', f"按锁定判据：L57–L61 每层 MLP 消融的损失都大于注意力消融（配对差 {fmt(min(float(CR[str(l)]['mlp_minus_attn_loss']) for l in Ls))} 至 {fmt(max(float(CR[str(l)]['mlp_minus_attn_loss']) for l in Ls))}，"
                 f"均值 {fmt(float(rm['mlp_minus_attn_loss']))} {cif(float(rm['lo']), float(rm['hi']))}，CI 都 > 0）→ \"后段由 MLP 写出\"。注意力消融损失 ≈ 0（≤ {max(att):.4f}）；每层 MLP 去掉 S 的 {min(sh) * 100:.0f}–{max(sh) * 100:.0f}%。"),
        ('plain', '前提：均值消融、每次只消一层一个成分，不检验层间冗余或合起来的效果；target 论文损失更大（差的 T − C > 0）；自检 WARN：未消融名次与已存 Stage 11 E1 行完全一致的比例 true 0.627 / false_0 0.527（阈值 0.95，bf16 批形状差异），按规则继续算。'),
    ])
    b += L.footer('381_stage13/summary_a18b_item4/item4_report.md · item4_table.csv (all / target / control / tc, share_of_S) · item4_criterion.csv (locked criterion) · config/prereg_addendum18b.md (sha256 9104c351…)')
    save('d_item4', L.section('Addendum 18b item 4: L57–L61 mean ablation', pid, b))
    return y


# ================================================================ addendum 16: B + D
def s_a16():
    pid = 'ra16'
    H = {(r['test'], r['quantity']): r for r in rows(G / 'summary_a16_20261115/holm.csv')}
    D = rows(G / 'summary_a16_20261115/d_contrasts.csv')
    dget = lambda grp, ver, con='G1': [r for r in D if r['group'] == grp and r['version'] == ver and r['contrast'] == con and r['score'] == 'all_tokens' and r['fa_type'] == 'all'][0]
    b = L.frame(pid, 'Output format (B) and name chain (D)',
                'Addendum 16 (pre-registered, Holm over 5 tests) · B: greedy generation, 600 A + 600 B papers · D: teacher forcing, 1,428 papers · team-cluster 95% CI', 'Added after the defence · groups')
    bd, bw = L.badge(70, 124, 'B：只通过 F4 支持 · D：效应存在，但不是论文特有'); b += bd
    fm, fw = L.formula(1210 - 560, 120, 'DiD(c) = Δ_A(c) − Δ_B(c),   G(1) = S(P_true(1)) − S(P_other(1))', 'Δ_g(c) = [rate_true − rate_chance]_g(c) − [same]_g(F0)', fs=16, w=560); b += fm
    fr = []; vals = []
    labs = {'B_F1': 'F1 surname first', 'B_F2': 'F2 surnames only', 'B_F3': 'F3 first author surname', 'B_F4': 'F4 first initial given'}
    for t in ('B_F1', 'B_F2', 'B_F3', 'B_F4'):
        r = H[(t, 'DiD_A-B')]; v, lo, hi = float(r['est']), float(r['holm_ci_lo']), float(r['holm_ci_hi'])
        ok = r['rejected_holm'] == 'True'
        fr.append((labs[t], v, lo, hi, OR if ok else '#9AA3B2', 1.0 if ok else 0.75, f"{fmt(v)} {cif(lo, hi)}  p_Holm {float(r['p_holm']):.4f}"))
        vals.append(f"{t} DiD A − B {fmt(v)} Holm CI {cif(lo, hi)} p_Holm {float(r['p_holm']):.4f}")
    r = H[('B_F4', 'Delta_A')]
    vals.append(f"B_F4 Δ_A {fmt(float(r['est']))} Holm CI {cif(float(r['holm_ci_lo']), float(r['holm_ci_hi']))}")
    b += T(70, 199, 'B: does a different answer format help A more than B?', 17, INK, weight=700)
    fo, fh = L.forest(70, 222, 560, fr, -0.04, 0.14, [0, 0.05, 0.10], rowh=30, labw=170, fs=14); b += fo
    b += nlab(70, 222 + fh + 18, 'n = 600 A + 600 B papers · DiD with Holm-adjusted 95% CI')
    b += T(70, 222 + fh + 40, f"F4 alone: Δ_A {fmt(float(r['est']))} [Holm {fmt(float(r['holm_ci_lo']))}, {fmt(float(r['holm_ci_hi']))}]", 13.5, INK)
    dr = [('G_A(1), true title', dget('A', 'true'), OR), ('title-specific (true − false)', dget('A', 'spec'), '#9AA3B2'), ('title deleted', dget('A', 'delete'), OR),
          ('A − B', dget('A-B', 'true'), '#9AA3B2'), ('group B, true title', dget('B', 'true'), OR), ('group C, true title', dget('C', 'true'), OR)]
    fd = []
    for lab, rr, col in dr:
        v, lo, hi = float(rr['est']), float(rr['lo']), float(rr['hi'])
        fd.append((lab, v, lo, hi, col, 1.0, f"{fmt(v)} {cif(lo, hi)} (n {int(rr['n'])})"))
        vals.append(f"D {lab} {fmt(v)} {cif(lo, hi)} n {int(rr['n'])}")
    b += T(660, 199, 'D: one true co-author given first (vs a wrong one)', 17, INK, weight=700)
    fo, fh2 = L.forest(660, 222, 570, fd, -0.06, 0.26, [0, 0.1, 0.2], rowh=27, labw=190, fs=13.5); b += fo
    b += nlab(660, 222 + fh2 + 18, 'n = 1,428 papers (A 600, B 600, C 227–228) · G_A(1): Holm CI [0.141, 0.189], p_Holm 0.0025')
    one = ('B：每个格式 c 下"真作者匹配率 − 机会匹配率"（机会 = 事先固定的同领域对照论文的作者，F4 用同首字母对照），Δ_A(c) = A 组在 c 下减去 F0 下的同一量，DiD = Δ_A − Δ_B；'
           'D：teacher forcing 下先给出 k = 1 个名字，只给其余作者打分，G(1) = S(给真合作者) − S(给同领域另一篇的作者)；title-specific = 真标题 − 5 个假标题平均 · '
           'B 600 + 600 篇、D 1,428 篇 · 团队整群 2,000 次，Holm 5 项 · 391_groups/summary_a16_20261115/holm.csv、d_contrasts.csv')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', 'B 支持，但只通过 F4（给出第一作者的首字母）：DiD A − B +0.085 [Holm 0.047, 0.124]，p_Holm 0.0025；F1–F3 的 DiD 都不显著。'
                 'D 效应存在（G_A(1) +0.167），但标题特有部分只有 +0.012 [−0.001, 0.025]，删掉标题反而更大（+0.223），A − B −0.019 [−0.045, 0.007] → 合作者网络的关联，不是这篇论文特有的记忆。'),
        ('plain', '前提：行为标签来自另一次生成（label package），F0 用作本提示的基线；B 的停止 / 截断规则在 shard 0 输出后改过（偏离 D16-4，已记录）；D 组 C 只有 227 篇，功效低；只用贪心解码。'),
    ])
    b += L.footer('391_groups/summary_a16_20261115/report.md · holm.csv (Holm-adjusted CIs) · b_main.csv · d_contrasts.csv (group, version, contrast G1, all_tokens) · config/prereg_addendum16.md, prereg_addendum16_deviations.md')
    save('e_a16', L.section('Addendum 16: output format (B) and name chain (D)', pid, b))
    return y


# ================================================================ C: fabricated names
def s_fab():
    pid = 'rfab'
    import re
    rep = (G / 'summary_fabricated_20261114/report.md').read_text()
    # main table values (from report.md main table; same numbers as class_shares_by_group.csv)
    main = {'coauthor': (4.0, 3.0, 5.2, 2.6, 5.3, 1.3), 'same_field': (20.2, 19.4, 21.0, 18.0, 22.2, 22.6),
            'other_cohort': (25.4, 24.8, 26.0, 25.8, 25.2, 25.7), 'not_in_data': (50.4, 49.0, 51.7, 53.7, 47.4, 50.5)}
    for k, (a, lo, hi, t, c, ch) in main.items():
        line = [l for l in rep.splitlines() if l.startswith(f'| {k} |')][0]
        assert f'{a:.1f}% [{lo:.1f}%, {hi:.1f}%]' in line and f'{t:.1f}%' in line and f'{c:.1f}%' in line and line.rstrip(' |').endswith(f'{ch:.1f}%'), (k, line)
    tcs = {}
    for l in rep.splitlines():
        m = re.match(r'\| (si|full|si_rare) \| (\w+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \|$', l)
        if m and m.group(1) + m.group(2) not in tcs:
            tcs[m.group(1) + m.group(2)] = tuple(float(m.group(i)) for i in (3, 4, 5))
    b = L.frame(pid, 'Fabricated names: mostly people not in the data',
                'Exploratory, post hoc (not pre-registered) · open-recall answers (greedy) · 40,219 fabricated names in 8,872 papers · team-cluster 95% CI', 'Added after the defence · groups')
    bd, bw = L.badge(70, 124, '邻居混淆（C）：不支持（探索性）'); b += bd
    fm, fw = L.formula(1210 - 520, 120, 'share(class) = #names in class / #classifiable names', 'classes: co-author of a true author → same field → other cohort author → not in data', fs=16, w=520); b += fm
    labs = [('coauthor', 'co-author'), ('same_field', 'same-field author'), ('other_cohort', 'other cohort author'), ('not_in_data', 'not in the data')]
    ax = Ax(250, 215, 320, 190, 0, 60, 0, 1)
    rh = 190 / 4
    b += T(70, 199, 'Where fabricated names come from (all papers)', 17, INK, weight=700)
    vals = []
    for v in (0, 20, 40, 60):
        X = ax.X(v); b += f'<line x1="{X:.1f}" y1="215" x2="{X:.1f}" y2="405" stroke="#E7DADA" stroke-dasharray="3 4"/>' + T(X, 421, f'{v}%', 13, PEN, 'middle')
    for i, (k, lab) in enumerate(labs):
        a, lo, hi, t, c, ch = main[k]; y = 215 + rh * (i + 0.5)
        b += T(242, y + 5, lab, 14, INK, 'end')
        b += f'<rect x="{ax.X(0):.1f}" y="{y - 11:.1f}" width="{ax.X(a) - ax.X(0):.1f}" height="22" fill="{OR}" fill-opacity="0.8" stroke="{INK}" stroke-width="1"/>'
        b += f'<line x1="{ax.X(lo):.1f}" y1="{y:.1f}" x2="{ax.X(hi):.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="1.6"/>'
        b += f'<path d="M{ax.X(ch):.1f} {y - 15:.1f} l6 -7 h-12 z" fill="{BL}"/><line x1="{ax.X(ch):.1f}" y1="{y - 14:.1f}" x2="{ax.X(ch):.1f}" y2="{y + 13:.1f}" stroke="{BL}" stroke-width="2"/>'
        b += T(ax.X(max(hi, ch)) + 10, y + 5, f'{a:.1f}%  (chance {ch:.1f}%)', 13, INK)
        vals.append(f'{lab} {a:.1f}% [{lo:.1f}, {hi:.1f}] (target {t:.1f}%, control {c:.1f}%; permuted same-field chance {ch:.1f}%)')
    b += L.legend(250, 448, [('share, all papers', OR, 'box')], fs=13)
    b += f'<line x1="400" y1="438" x2="400" y2="452" stroke="{BL}" stroke-width="2"/>' + T(408, 448, 'chance: permuted names, same field', 13, INK)
    b += nlab(70, 470, 'n = 8,872 papers, 40,219 classifiable names (target 4,578 / control 2,187 papers)')
    fr = []
    for key, lab in (('sicoauthor', 'co-author, surname + initial'), ('fullcoauthor', 'co-author, full name'), ('si_rarecoauthor', 'co-author, rare surname'), ('sinot_in_data', 'not in data, surname + initial')):
        v, lo, hi = tcs[key]
        fr.append((lab, v, lo, hi, PINK if 'coauthor' in key else '#9AA3B2', 1.0, f'{fmt(v)} {cif(lo, hi)}'))
        vals.append(f'T − C {lab} {fmt(v)} {cif(lo, hi)}')
    b += T(690, 199, 'Target − control of the share (pooled, paired)', 17, INK, weight=700)
    fo, fh = L.forest(690, 222, 540, fr, -0.05, 0.09, [-0.04, 0, 0.04, 0.08], rowh=30, labw=200, fs=13.5); b += fo
    b += nlab(690, 222 + fh + 18, 'n = 4,578 target / 2,187 control papers · shares as fractions')
    one = ('每个编造的名字（与真作者不匹配、按姓 + 名首字母）依次归类，先匹配先算：真作者的合作者 → 同领域的真实作者 → 队列中其他作者 → 不在数据中；占可分类名字的比例（合并比率）；'
           '机会基线 = 打乱编造名字后在同领域重算（20 次）；全名 / 罕见姓为敏感性 · 8,872 篇、40,219 个名字 · 团队整群 2,000 次 · 391_groups/summary_fabricated_20261114/report.md')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', '邻居混淆（C）不支持（探索性、事后）：编造的名字一半是数据里没有的人（50.4% [49.0, 51.7]），与同领域打乱基线 50.5% 相同；合作者占 4.0% [3.0, 5.2]，高于打乱基线 1.3%，'
                 '但用全名或罕见姓匹配时，合作者的 target − control ≈ 0。'),
        ('plain', '前提：只用原 label package 的开放回答（贪心）；"不在数据中"只指不在 9,108 篇队列的作者表里，不等于现实中不存在；未预注册，只作描述。'),
    ])
    b += L.footer('391_groups/summary_fabricated_20261114/report.md (main table, target − control) · class_shares_by_group.csv · chance_baselines.csv · target_minus_control.csv · script ~/jlens_work/14_groups/fabricated_names_20261114.py')
    save('f_fab', L.section('C: fabricated names (exploratory)', pid, b))
    return y


# ================================================================ addendum 19: exposure threshold
def s_exp():
    pid = 'rexp19'
    TH = {r['quantity']: r for r in rows(G / 'summary_exposure_prereg19/thresholds_ratio.csv')}
    TR = rows(G / 'summary_exposure_prereg19/trend_by_bin.csv')
    b = L.frame(pid, 'Exposure: writing needs far more citations than recognising',
                'Addendum 19 (locked 2026-11-17; confirmatory analysis of already-seen data, post hoc lock) · 9,108 papers, 7,247 teams, 2,000 team draws', 'Added after the defence · groups', title_fs=46)
    bd, bw = L.badge(70, 124, '确认（事后锁定）：ρ 的 CI 全部 > 1'); b += bd
    fm, fw = L.formula(1210 - 540, 120, 'ρ = c50(recall) / c50(recognition),  log10(1 + c50) = −β0 / β1', 'logistic  y ~ log10(1 + citations) + (year − mean year), at the mean year', fs=16, w=540); b += fm
    ax = Ax(120, 215, 500, 200, 0, 4.6, 0, 1)
    tick_c = [0, 9, 99, 999, 9999]
    b += f'<g data-name="axes">'
    for c in tick_c:
        X = ax.X(math.log10(1 + c)); b += f'<line x1="{X:.1f}" y1="415" x2="{X:.1f}" y2="420" stroke="{INK}" stroke-width="1.6"/>' + T(X, 434, {0: '0', 9: '10', 99: '100', 999: '1k', 9999: '10k'}[c], 13, PEN, 'middle')
    b += '</g>'
    b += ax.frame([], [0, 0.25, 0.5, 0.75, 1], ylab=lambda v: f'{v:g}', title='Fitted probability vs citations (log scale)', ytitle='P(pass)')
    b += T(ax.X(4.6), 448, 'citations (axis = log10(1 + c))', 12, PEN, 'end')
    b += ax.hline(0.5, '#9AA3B2', '4 4', 1.2)
    vals = []
    for q, lab, col in (('c50_recognition', 'recognition (MC, strong)', BL), ('c50_recall', 'recall (≥ 1 author written)', OR)):
        r = TH[q]; x50, s = float(r['log10_1p_est']), float(r['slope_log10cit'])
        xs = np.linspace(0, 4.6, 70); ys = 1 / (1 + np.exp(-s * (xs - x50)))
        b += ax.line(list(xs), list(ys), col, w=2.6, pts=False)
        lo, hi = float(r['log10_1p_lo']), float(r['log10_1p_hi'])
        b += f'<line x1="{ax.X(lo):.1f}" y1="{ax.Y(0.5):.1f}" x2="{ax.X(hi):.1f}" y2="{ax.Y(0.5):.1f}" stroke="{col}" stroke-width="5" stroke-opacity="0.5"/>'
        b += f'<circle cx="{ax.X(x50):.1f}" cy="{ax.Y(0.5):.1f}" r="5" fill="{col}" stroke="{INK}"/>'
        est = float(r['est']); clo, chi = float(r['lo']), float(r['hi'])
        txt = f'c50 = {est:,.0f} [{clo:,.0f}, {chi:,.0f}]'
        b += T(ax.X(x50) + (10 if q == 'c50_recognition' else -10), ax.Y(0.5) + (22 if q == 'c50_recognition' else 40), txt, 12.5, col, 'start' if q == 'c50_recognition' else 'end', font=SANS, weight=700)
        vals.append(f'{lab}: c50 {est:,.1f} [{clo:,.1f}, {chi:,.1f}], slope {s:.3f} per log10(1 + c)')
    rr = TH['rho_recall_over_recognition']; rs = TH['rho_recall_over_recognition_excl_uncertain']
    b += f'<line x1="{ax.X(float(TH["c50_recognition"]["log10_1p_est"])) + 8:.1f}" y1="{ax.Y(0.62):.1f}" x2="{ax.X(float(TH["c50_recall"]["log10_1p_est"])) - 10:.1f}" y2="{ax.Y(0.62):.1f}" stroke="{INK}" stroke-width="1.8" marker-end="url(#{pid}a)"/>'
    b += T((ax.X(float(TH["c50_recognition"]["log10_1p_est"])) + ax.X(float(TH["c50_recall"]["log10_1p_est"]))) / 2, ax.Y(0.62) - 8, f'ρ = {float(rr["est"]):.0f} [{float(rr["lo"]):.0f}, {float(rr["hi"]):.0f}]', 15, INK, 'middle', weight=700)
    vals.append(f'ρ {float(rr["est"]):.1f} [{float(rr["lo"]):.1f}, {float(rr["hi"]):.1f}], log10 ρ {float(rr["log10_1p_est"]):.3f} [{float(rr["log10_1p_lo"]):.3f}, {float(rr["log10_1p_hi"]):.3f}]; sensitivity (excl. uncertain) ρ {float(rs["est"]):,.0f} [{float(rs["lo"]):,.0f}, {float(rs["hi"]):,.0f}]')
    b += L.legend(120, 466, [('recognition', BL, 'line'), ('recall', OR, 'line')], fs=13)
    b += nlab(330, 466, 'n = 9,108 papers · bar on the 0.5 line = 95% CI of c50')
    # right: trend
    ax2 = Ax(730, 215, 490, 200, 0, 3.8, 0, 0.5)
    b += ax2.frame([], [0, 0.1, 0.2, 0.3, 0.4, 0.5], ylab=lambda v: f'{v:.1f}', title='Within-bin target − control by citation bin', ytitle='T − C (spec, L63)')
    for c in (0, 9, 99, 999):
        X = ax2.X(math.log10(1 + c)); b += f'<line x1="{X:.1f}" y1="415" x2="{X:.1f}" y2="420" stroke="{INK}" stroke-width="1.6"/>' + T(X, 434, {0: '0', 9: '10', 99: '100', 999: '1k', 9999: '10k'}[c], 13, PEN, 'middle')
    b += T(ax2.X(3.8), 448, 'median citations of the bin (log)', 12, PEN, 'end')
    xs, ys, ws = [], [], []
    for r in TR:
        if r['diff'] in ('', 'nan'): continue
        x, v, lo, hi = float(r['x']), float(r['diff']), float(r['lo']), float(r['hi']); used = r['used_in_slope'] == 'True'
        col = OR if used else '#9AA3B2'
        b += ax2.whisk(x, lo, hi, col, 1.5, 3) + f'<circle cx="{ax2.X(x):.1f}" cy="{ax2.Y(v):.1f}" r="4" fill="{col}" stroke="{INK}" stroke-width="0.8"/>'
        vals.append(f"{r['citation_bin']}: {fmt(v)} {cif(lo, hi)}{'' if used else ' (not in slope)'}")
        if used: xs.append(x); ys.append(v); ws.append(1 / float(r['var_boot']))
    X_, Y_, W_ = map(np.array, (xs, ys, ws))
    A = np.vstack([np.ones_like(X_), X_]).T; Wm = np.diag(W_)
    b0, b1 = np.linalg.solve(A.T @ Wm @ A, A.T @ Wm @ Y_)
    tr = rows(G / 'summary_exposure_prereg19/trend_by_bin.csv')
    import json
    J = json.load(open(G / 'summary_exposure_prereg19/prereg19_results.json'))['trend']
    assert abs(b1 - J['slope']) < 1e-9, (b1, J['slope'])
    b += f'<line x1="{ax2.X(0):.1f}" y1="{ax2.Y(b0):.1f}" x2="{ax2.X(max(xs)):.1f}" y2="{ax2.Y(b0 + b1 * max(xs)):.1f}" stroke="{RD}" stroke-width="2" stroke-dasharray="6 4"/>'
    b += T(ax2.X(0.1), ax2.Y(0.46), f"WLS slope {fmt(J['slope'])} [{fmt(J['lo'])}, {fmt(J['hi'])}] per 10× citations", 13.5, RD, weight=700)
    vals.append(f"WLS slope {fmt(J['slope'], d=4)} [{fmt(J['lo'], d=4)}, {fmt(J['hi'], d=4)}] over {J['n_bins']} bins")
    nused = sum(int(r['n_papers']) for r in TR if r['used_in_slope'] == 'True')
    b += nlab(730, 466, f'n = {nused:,} papers in the 10 bins used (orange) · grey = < 30 control, not in slope')
    one = ('认出 = 多选题团队结果 strong（uncertain 算未通过）；写出 = R1 或 R2（至少写对 1 个作者）；各自做 logistic y ~ log10(1 + 引用) + (年份 − 平均年份)，c50 = 平均年份下概率 0.5 的引用数；ρ = c50(写出) / c50(认出)，规则：CI 全部 > 1；'
           '次要：每个引用分箱内 target − control（spec，L63），对 log10(1 + 分箱中位引用) 做 WLS（权重 1/bootstrap 方差，只用每组 ≥ 30 篇的 10 个分箱），规则：斜率 CI > 0 · 9,108 篇、7,247 个团队 · 团队整群 2,000 次 · '
           '391_groups/summary_exposure_prereg19/thresholds_ratio.csv、trend_by_bin.csv')
    b, y = fill_bottom(b, 500, [
        ('how', one), ('val', 'Plotted — ' + ' | '.join(vals)),
        ('bold', f'按锁定规则确认（看过数据后的事后锁定）：ρ = 276 [203, 390]，CI 全部 > 1 → 写出需要的曝光远多于认出；分箱内 target − control 随曝光增大，WLS 斜率 +0.030 [+0.014, +0.044] / 10 倍引用（10 箱，每箱 +0.175 至 +0.298）。'),
        ('plain', '前提：单一模型；引用数只是训练曝光的代理；分箱是分层样本，不是总体比例；低箱的认出含约 25% 猜对底线；写出阈值接近观测范围顶部（只有 16 / 9,108 篇引用 > 11,038），易受外推影响；276 倍是估计值；敏感性（排除 uncertain）ρ 1,184 [851, 1,712]。'),
    ])
    b += L.footer('391_groups/summary_exposure_prereg19/report.md · thresholds_ratio.csv (c50, slope_log10cit, rho) · trend_by_bin.csv · prereg19_results.json · config/prereg_addendum19.md (sha256 f6b65072…) · job 11951874')
    save('g_exp19', L.section('Addendum 19: exposure threshold (F)', pid, b))
    return y


if __name__ == '__main__':
    for f in (s_item1, s_item5, s_item6, s_item4, s_a16, s_fab, s_exp):
        y = f(); print(f.__name__, 'bottom text ends at y =', round(y, 1))
