"""v71 (user 2026-11-24, HANDOFF item 32): two explanation slides, built as fragments (deck not changed).
A: after v70 slide 73 — "How the 75% is computed"  (numbers: v70 slide 73 + backup B18 / slide 157)
B: after v70 slide 102 — "The locked rule of this slide" (numbers: v70 slide 102 + backup B16 / slide 155)
Helpers are taken verbatim from build_part56.py (everything above its data section)."""
import re, html as H
src = open('/home/zhang.zhiqi2/jlens_work/27_v67/build_part56.py').read()
exec(src[:src.index('# ================================================================ data')])
OUT = '/home/zhang.zhiqi2/jlens_work/27_v67/fragments/'


# ------------------------------------------------------------------ A: how the 75% is computed
def slide_a():
    slot = 'v71-explain-75'
    b = []
    # ① three scores
    b.append(qsvg(84, 136, 1)); b.append(t(100, 141, 'Score each paper three ways (final output, all authors, all name tokens)', 14, INK, weight=700))
    for k, (lab, sub, col) in enumerate([('true title', 'S_true', ORANGE), ('made-up title', 'S_fict', GREEN), ('5 false titles', 'F̄ = mean of false_0…false_4', GREY)]):
        x = 84 + k * 190
        b.append(box(x, 154, 176, 44, '#fff', col)); b.append(t(x + 10, 173, lab, 14, col, weight=700)); b.append(t(x + 10, 190, sub, 11.5, GREY, font=SANS))
    # ② number line with G, A, R
    b.append(qsvg(84, 236, 2)); b.append(t(100, 241, 'Put the three scores on one line (target papers, means)', 14, INK, weight=700))
    x0, x1, yl = 110, 600, 330
    def X(v): return x0 + v / 0.425 * (x1 - x0)
    b.append(f'<line x1="{x0 - 10}" y1="{yl}" x2="{x1 + 20}" y2="{yl}" stroke="{INK}" stroke-width="2"/>')
    for v, lab, col in [(0, 'F̄', GREY), (0.319, 'S_fict', GREEN), (0.425, 'S_true', ORANGE)]:
        b.append(f'<circle cx="{X(v):.1f}" cy="{yl}" r="7" fill="{col}"/>'); b.append(t(X(v), yl + 26, lab, 13, col, 'middle', weight=700))
    # segments
    b.append(f'<line x1="{X(0):.1f}" y1="{yl - 46}" x2="{X(0.425):.1f}" y2="{yl - 46}" stroke="{ORANGE}" stroke-width="3"/>')
    b.append(t((X(0) + X(0.425)) / 2, yl - 54, 'G = S_true − F̄ = 0.425  (true-title advantage)', 12.5, ORANGE, 'middle', weight=700))
    b.append(f'<line x1="{X(0):.1f}" y1="{yl - 20}" x2="{X(0.319):.1f}" y2="{yl - 20}" stroke="{GREEN}" stroke-width="3"/>')
    b.append(t((X(0) + X(0.319)) / 2, yl - 27, 'A = S_fict − F̄ = 0.319', 12.5, GREEN, 'middle', weight=700))
    b.append(f'<line x1="{X(0.319):.1f}" y1="{yl - 20}" x2="{X(0.425):.1f}" y2="{yl - 20}" stroke="{RED}" stroke-width="3"/>')
    b.append(t((X(0.319) + X(0.425)) / 2, yl - 27, 'R = S_true − S_fict = 0.106', 12, RED, 'middle', weight=700))
    # ③ phi
    b.append(qsvg(84, 368, 3)); b.append(t(100, 373, 'φ = A ÷ G: the share of the advantage the made-up title brings back', 14, INK, weight=700))
    b.append(t(110, 400, 'sum over the papers of a group first, then divide (ratio of sums)', 12, GREY, font=SANS))
    b.append(t(110, 426, 'target: 0.319 ÷ 0.425 → φ̂ = 0.751 [0.723, 0.778]', 15, INK, weight=700))
    # ④ band scale
    b.append(qsvg(84, 468, 4)); b.append(t(100, 473, 'Read φ̂ on the bands fixed before the run', 14, INK, weight=700))
    bx0, bx1, by = 110, 600, 500
    def B(v): return bx0 + v * (bx1 - bx0)
    for a_, c_, col in [(0, 0.3, '#F6E3E1'), (0.3, 0.5, '#FBEFD9'), (0.5, 1.0, '#E3F0E6')]:
        b.append(f'<rect x="{B(a_):.1f}" y="{by}" width="{B(c_) - B(a_):.1f}" height="22" fill="{col}" stroke="#C9CED6"/>')
    for v in (0, 0.3, 0.5, 1):
        b.append(t(B(v), by + 38, f'{v:g}', 12, GREY, 'middle'))
    b.append(f'<rect x="{B(0.723):.1f}" y="{by - 4}" width="{B(0.778) - B(0.723):.1f}" height="30" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    b.append(f'<circle cx="{B(0.751):.1f}" cy="{by + 11}" r="7" fill="{INK}"/>'); b.append(ring(B(0.751), by + 11, 12))
    b.append(t(B(0.751), by - 10, '0.751', 13, INK, 'middle', weight=700))
    ov = ask('how exactly is “about 75%” computed from the three scores, and how is it read?')
    ov += tagrow('<span class="tg lsup">locked</span> rule fixed before the run &nbsp;·&nbsp; explanation page for slide 73')
    ov += fxu(110, 556, 520, [r'$S=\overline{\log_{10}(1/\mathrm{rank})}_{\mathrm{name\ tokens}}$', r'$G=S_{\mathrm{true}}-\bar F,\ A=S_{\mathrm{fict}}-\bar F,\ R=S_{\mathrm{true}}-S_{\mathrm{fict}}$', r'$\varphi=\sum A/\sum G$'],
              'n = 566 target · 561 control papers', ['φ ≈ 1: meaning alone brings back the whole true-title advantage'])
    # right: band table
    tbl = ('<div style="position:absolute;z-index:4;left:668px;top:130px;width:560px;font-family:\'Noto Sans SC\',sans-serif;font-size:14px;color:#22304A">'
           '<div style="font-weight:700;margin-bottom:6px">Verdict bands (locked before the run)</div>'
           '<table style="border-collapse:collapse;width:100%">'
           '<tr style="border-bottom:2px solid #22304A"><th style="text-align:left;padding:5px">φ̂</th><th style="text-align:left;padding:5px">reading</th></tr>'
           '<tr style="background:#F6E3E1"><td style="padding:6px">&lt; 0.3</td><td style="padding:6px">strongly supported (paper identity)</td></tr>'
           '<tr style="background:#FBEFD9"><td style="padding:6px">0.3 – 0.5</td><td style="padding:6px">partly supported, limited weight</td></tr>'
           '<tr style="background:#E3F0E6;outline:3px solid #D9772B"><td style="padding:6px"><b>≥ 0.5</b></td><td style="padding:6px"><b>partly supported, meaning explains most</b> ← <b>0.751</b></td></tr>'
           '</table></div>')
    ov += tbl
    ov += cats(668, 318, 560, [
        ('Gate', 'φ̂ is read <b>only</b> if the 95% CI of R̄ lies entirely above 0 — here <b>+0.106 [+0.094, +0.118]</b>, so it is read.', [
            'R̄ CI includes 0 → not supported; R̄ CI below 0 → refuted.']),
        ('Borderline', 'if the φ CI crosses 0.3 or 0.5; here [0.723, 0.778] stays inside the top band.', []),
        ('Result', '<span class="mk">φ̂ = 0.751: the made-up title brings back about three quarters of the true-title advantage</span>.', []),
        ('Inputs', 'S_true and the false-title scores come from the stored full-cohort run; S_fict from this test’s run.', []),
        ('Caveat', '<span class="ul">this is the locked reading of this one test; the overall H2 verdict combines it with the later tests (slides 78–81)</span>.', []),
    ])
    ov += soln('“about 75%” = φ̂, the made-up title’s share of the true-title advantage (0.319 of 0.425); it falls in the top band, so meaning explains most of what the title gives.')
    return section(slot, 'How the 75% is computed', 'How the 75% is computed', 'Part 4 · H2', ''.join(b), ov, 30)


# ------------------------------------------------------------------ B: the locked rule of the readout map
def slide_b():
    slot = 'v71-locked-rule'
    b = []
    POS = ['title: all', 'title: content', 'title: first', 'title: last', 'quote', 'after title', 'year digits', '"Authors"', '":"']
    NL = 20
    gx, gy, cw, ch = 210, 150, 21, 25
    b.append(t(70, 132, 'Grid for one readout: 9 prompt positions × 20 layers; each cell = within-bin target − control of spec', 13.5, INK, weight=700))
    rows = POS + ['name (reference)']
    for i, p in enumerate(rows):
        col = BLUE if i == len(POS) else INK
        b.append(t(gx - 8, gy + i * ch + ch / 2 + 4, p, 12, col, 'end', weight=700 if i == len(POS) else None))
        for j in range(NL):
            fill = '#EEF1F5' if i < len(POS) else '#E8F0FA'
            b.append(f'<rect x="{gx + j * cw + 1}" y="{gy + i * ch + 1}" width="{cw - 2}" height="{ch - 2}" rx="2" fill="{fill}" stroke="#D5DAE2"/>')
    # L48 limit line after column index 13 (schematic)
    jl = 13
    xl = gx + (jl + 1) * cw
    b.append(f'<line x1="{xl}" y1="{gy - 8}" x2="{xl}" y2="{gy + len(rows) * ch + 4}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 3"/>')
    b.append(t(xl + 4, gy + len(rows) * ch + 18, 'L48 limit (rule applies at L ≤ 48)', 12, RED, weight=700))
    b.append(f'<rect x="{xl}" y="{gy}" width="{(NL - jl - 1) * cw}" height="{len(rows) * ch}" fill="url(#HATCH)" opacity="0.35"/>')
    # example cell ①
    ei, ej = 6, 9
    ex, ey = gx + ej * cw, gy + ei * ch
    b.append(f'<rect x="{ex + 1}" y="{ey + 1}" width="{cw - 2}" height="{ch - 2}" rx="2" fill="#FFD9B8" stroke="{ORANGE}" stroke-width="2.6"/>')
    b.append(qsvg(ex + cw / 2, ey - 10, 1))
    # same layer, name row ②
    ny = gy + len(POS) * ch
    b.append(f'<rect x="{ex + 1}" y="{ny + 1}" width="{cw - 2}" height="{ch - 2}" rx="2" fill="#fff" stroke="{BLUE}" stroke-width="2.6"/>')
    b.append(f'<line x1="{ex + cw / 2}" y1="{ey + ch}" x2="{ex + cw / 2}" y2="{ny}" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="3 3"/>')
    b.append(qsvg(ex + cw / 2 + 16, ny + ch + 14, 2, BLUE))
    b.append(t(gx, gy + len(rows) * ch + 40, 'layers →  (schematic: 20 tested layers)', 11.5, GREY, font=SANS))
    # condition boxes
    cy = 452
    b.append(box(70, cy, 270, 64, '#FFF4EC', ORANGE)); b.append(qsvg(86, cy + 18, 1))
    b.append(t(102, cy + 23, 'this position, this layer:', 13, INK, weight=700)); b.append(t(86, cy + 46, 'CI of T − C above 0, at a layer L ≤ 48', 12.5, INK, font=SANS))
    b.append(t(360, cy + 38, 'AND', 15, INK, 'middle', weight=700))
    b.append(box(384, cy, 270, 64, '#EEF4FB', BLUE)); b.append(qsvg(400, cy + 18, 2, BLUE))
    b.append(t(416, cy + 23, 'same layer, name position:', 13, INK, weight=700)); b.append(t(400, cy + 46, 'CI of T − C includes 0', 12.5, INK, font=SANS))
    b.append(t(70, cy + 92, 'Both conditions must hold for a cell to count as an “earlier shelf” (the author signal at a position before the names).', 12.5, INK))
    ov = ask('what exactly does the slide-102 rule require before a position counts as an earlier shelf?')
    ov += tagrow('<span class="tg expl">exploratory</span> rule fixed before the run, no multiplicity correction &nbsp;·&nbsp; explanation page for slide 102')
    ov += fxu(70, 576, 600, [r'$\Delta(p,l)=\overline{\mathrm{spec}}_{T}-\overline{\mathrm{spec}}_{C}\ \mathrm{(within\ bin)}$',
                             r'$\mathrm{shelf}(p,l):\ \mathrm{CI}_{p,l}>0\ \wedge\ 0\in\mathrm{CI}_{\mathrm{name},l},\ l\leq48$'],
              'n = 600 papers (300 target + 300 control) · team bootstrap ×2,000', ['shelf = true: the author signal shows at that position before the names do'])
    ov += cats(700, 128, 530, [
        ('Rule', 'a cell counts only if ' + q(1) + ' and ' + q(2) + ' both hold, at some layer up to L48.', []),
        ('Result', 'the rule is met in a few cells:', [
            'logit lens: year from L40, “:” L45, “Authors” L36;', 'J-lens: first title token L8;', 'probe: title L32;',
            'effects small: <b>+0.008 to +0.049</b>.']),
        ('Chance', '<span class="ul">672 cells tested, 60 with CI > 0, about 17 expected by chance, no correction</span> → position hints only.', []),
        ('Caveat', 'the rule compares two CIs, not a paired test; the probe is trained on 600 papers.', []),
        ('So', '<span class="mk">no clear earlier shelf</span>: only faint, scattered traces before L48.', []),
    ])
    ov += soln('a position counts as an earlier shelf only if its own CI is above 0 while the names’ CI at that layer still includes 0; a few cells meet this, but they are small and about what chance predicts — no clear earlier shelf.')
    return section(slot, 'The locked rule of this slide', 'The locked rule of the readout map (slide 102)', 'Part 5 · route + H3', ''.join(b), ov, 30)


open(OUT + 'v71_explain_75.html', 'w').write(slide_a())
open(OUT + 'v71_locked_rule.html', 'w').write(slide_b())
deck = open('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html').read()
i = deck.find('<section'); k = deck.find('id="count"'); j = deck.rfind('</section>', 0, k) + len('</section>')
body = open(OUT + 'v71_explain_75.html').read() + '\n' + open(OUT + 'v71_locked_rule.html').read()
open('/home/zhang.zhiqi2/jlens_work/27_v67/v71_render/test_v71.html', 'w').write(deck[:i] + body + deck[j:])
print('ok')
