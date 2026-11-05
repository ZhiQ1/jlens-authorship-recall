"""Apply v18 source-tag edits to build_v18.py (each old string must occur exactly once)."""
import sys
from pathlib import Path
P = Path(sys.argv[1]); src = P.read_text()
E = []
def e(old, new): E.append((old, new))

# deck 4 (build 3b): rules cards
e("'no shared surname, Jaccard <= 0.6', '79% strict tier']",
  "'no shared surname, Jaccard <= 0.6', [T('79% strict tier'), S('Stage 10, 35,898 of 45,540 pairs, conditions_manifest.json')]]")
e("'10 bins with >= 30 per group', 'weight",
  "[T('10 bins with >= 30 per group'), S('Stage 10, §6.2')], 'weight")
e("box(s, 0.75 + (i % 2) * 6.15, 1.65 + (i // 2) * 2.7, 5.85, 2.5, [[B(h, col)]] + [[T(l)] for l in lines]",
  "box(s, 0.75 + (i % 2) * 6.15, 1.65 + (i // 2) * 2.7, 5.85, 2.5, [[B(h, col)]] + [[T(l)] if isinstance(l, str) else l for l in lines]")

# deck 5 (build 4): method caption
e("cap(s, 'Lenses (model weights never change; Jacobians to L63 averaged over prompts): public = 557 WikiText-103 prompts (Neuronpedia) · self100 = 100 frozen WikiText-103 prompts · fitA = 100 other WikiText-103 prompts (Stage 9: one skipped prompt replaced -> 100 valid)', y=6.7)",
  "cap(s, [[T('Lenses (model weights never change; Jacobians to L63 averaged over prompts): public = 557 WikiText-103 prompts (Neuronpedia) · self100 = 100 frozen WikiText-103 prompts · fitA = 100 other WikiText-103 prompts (Stage 9: one skipped prompt replaced -> 100 valid)'), S('n_prompts: 351_stage10/config/lenses.json; Stage 9 final_status.json', 10)]], y=6.7)")

# deck 6 (build 7): spec by layer
e("note(s, 9.0, 1.9, 3.7, 3.4, [[B('L24-L48: ~0'), T(' for both groups')], [T('rises at '), B('L56')], [T('L62: '), B('target +0.56', TGT), T(' vs '), B('control +0.24', CTL)]], rot=-1.5)",
  "note(s, 9.0, 1.9, 3.7, 3.4, [[B('L24-L48: ~0'), T(' for both groups'), S('Stage 10, all readouts max 0.04, §6.3')], [T('rises at '), B('L56')], [T('L62: '), B('target +0.56', TGT), T(' vs '), B('control +0.24', CTL), S('Stage 10, public lens L62, 4,621 + 2,220 papers, §6.3 fig.')]], rot=-1.5)")

# deck 7 (build 8): target - control
e("[B('+0.21 to +0.23', TGT)], [T('almost all title-specific')], [B('R0 only'), T(' (no author written): output +0.199 vs +0.207')]], rot=1.5, size=18)",
  "[B('+0.21 to +0.23', TGT), S('Stage 10, L62 + final L63, 3,734 + 2,182 papers, §6.4')], [T('almost all title-specific')], [B('R0 only'), T(' (no author written): output +0.199 vs +0.207'), S('Stage 10, 3,423 + 2,151 R0 papers, §6.13')]], rot=1.5, size=18)")

# deck 8 (build 8b): fine layers
e("[B('+0.007 at L50', CTL)], [B('+0.23 at L62', TGT)], [T('steepest rise '), B('L57-L61')]], rot=-1.5, size=19)",
  "[B('+0.007 at L50', CTL)], [B('+0.23 at L62', TGT), S('Stage 10 logit lens, 3,734 + 2,182 papers, §6.10')], [T('steepest rise '), B('L57-L61')]], rot=-1.5, size=19)")

# deck 9 (build S11a)
e("title(s, 'Stage 11: intervene, do not just read', '593 + 593 papers: min(60, n_t, n_c) per citation bin, seed 11 · patch uses false_0 · knockout masks all heads · all 9,108 for probe and chain')",
  "title(s, 'Stage 11: intervene, do not just read', [[T('593 + 593 papers: min(60, n_t, n_c) per citation bin, seed 11'), S('Stage 11 sample.parquet, §6.11')], [T('patch uses false_0 · knockout masks all heads · all 9,108 for probe and chain'), S('Stage 10 manifest.json')]])")

# deck 10 (build S11b)
e("title(s, 'The title is read in L24-L50, early', 'model output · share of the true-false gap · CIs about +/-0.02')",
  "title(s, 'The title is read in L24-L50, early', [[T('model output · share of the true-false gap · CIs about +/-0.02'), S('Stage 11 E1/E2, 593 + 593 papers, §6.11')]])")

# deck 11 (build S11c) title position: tags, caveat, notes caveat
e("Read early, spoken late.')\ntitle(s, 'Read early: a probe finds it at the title'",
  "Read early, spoken late. ' + PROBE_CAVEAT)\ntitle(s, 'Read early: a probe finds it at the title'")
e("'title-specific signal at the last title token · lenses: all 9,108 papers · probe: re-checked, title reuse removed: 1,863 papers (896 target, 499 control)')",
  "[[T('title-specific signal at the last title token · lenses: all 9,108 papers · probe: re-checked, title reuse removed: 1,863 papers (896 target, 499 control)'), S('Stage 11 E4; Stage 13 E4b', 10)]])")
e("note(s, 9.95, 1.9, 2.9, 5.0, [[T('lenses: '), B('~0.01-0.03')], [T('probe: '), B('0.05 -> 0.08', GRN)], [T('target > control by '), B('+0.04-0.08', TGT)],",
  "note(s, 9.95, 1.9, 2.9, 5.0, [[T('lenses: '), B('~0.01-0.03'), S('Stage 11 E4, 4,621 + 2,220, §6.11')], [T('probe: '), B('0.05 -> 0.08', GRN), S('Stage 13 E4b, 1,863 papers, first name token only')], [T('target > control by '), B('+0.04-0.08', TGT), S('E4b, 896 vs 499, within bin')],")
e("chart(s, 'c13_title_position', 0.5, 1.6, 9.2)\n",
  "chart(s, 'c13_title_position', 0.5, 1.6, 9.2)\ncaveat(s, y=6.1, w=9.2)\n")

# deck 12 (build S12a) name prior
e("note(s, 9.95, 1.9, 2.9, 3.9, [[T('no title: rank '), B('~12')], [T('target - control: '), B('+0.09', MUTE), T(' prior, '), B('+0.21', TGT), T(' paper')], [T('surname 1st: prior ~0, paper '), B('+0.42', TGT)], [T('prior vs recognition rho '), B('0.09')]], rot=1.5, size=17)",
  "note(s, 9.95, 1.9, 2.9, 3.9, [[T('no title: rank '), B('~12'), S('Stage 12 A, 9,108 papers, §6.12')], [T('target - control: '), B('+0.09', MUTE), T(' prior, '), B('+0.21', TGT), T(' paper'), S('Stage 12 A, 4,621 + 2,220, within bin, §6.12')], [T('surname 1st: prior ~0, paper '), B('+0.42', TGT), S('same, 1st surname token')], [T('prior vs recognition rho '), B('0.09'), S('Stage 12 B, 8,894 R0/R1 papers')]], rot=1.5, size=17)")

# deck 13 (build R0/R1 a)
e("note(s, 9.95, 1.9, 2.9, 4.4, [[B('R0 only (A - B):', TGT)], [T('output +0.199 vs +0.207, same shape')], [B('R1 (C - B):', PUR), T(' +0.37, also late')], [T('C - A within target: +0.11, from L56')], [B('patching:'), T(' R1 a bit later, done by L52')]], rot=1.5, size=17)",
  "note(s, 9.95, 1.9, 2.9, 4.4, [[B('R0 only (A - B):', TGT)], [T('output +0.199 vs +0.207, same shape'), S('Stage 10, A 3,423 / B 2,151, §6.13')], [B('R1 (C - B):', PUR), T(' +0.37, also late'), S('C 391 / B 885')], [T('C - A within target: +0.11, from L56'), S('C 485 / A 3,204')], [B('patching:'), T(' R1 a bit later, done by L52'), S('Stage 11 E1, 36 R1 targets')]], rot=1.5, size=17)")

# deck 14 (build 15) conclusions
e("('No lens lead', 'Read with a lens at the names, target is not ahead of control in middle layers; the +0.21 gap is at the end (probe at the title: target − control +0.04–0.08, re-checked).'),",
  "('No lens lead', [[T('Read with a lens at the names, target is not ahead of control in middle layers; the +0.21 gap is at the end'), S('Stage 10, final L63, §6.4'), T(' (probe at the title: target − control +0.04–0.08, re-checked'), S('Stage 13 E4b, first name token only'), T(').')]]),")
e("('Real knowledge', 'Name prior is ~1/3 of the gap overall but ~0 on surnames; the rest is paper-specific and grows with citations.'),",
  "('Real knowledge', [[T('Name prior is ~1/3 of the gap overall but ~0 on surnames'), S('Stage 12 A, 0.087 / 0.247, §6.12'), T('; the rest is paper-specific and grows with citations.')]]),")

# deck 17 (build 5) checks
e("for i, (h, b, col) in enumerate([('fast = slow', 'One forward pass vs one per prefix: max gap 0.37 logit (bf16 rounding); ranks 1-41 identical', CTL),\n                                 ('matches Stage 6', '972 tokens: same token ids, median log-prob gap ~1e-5', GRN),\n                                 ('negative control', 'Punctuation tokens show ~0 title-specific signal at every layer', TGT)]):\n    box(s, 0.9 + i * 4.1, 2.0, 3.7, 2.6, [[B(h, col)], [T(b)]], color=col, size=19, rot=[-1, 1, -0.5][i])",
  "for i, (h, b, col) in enumerate([('fast = slow', [T('One forward pass vs one per prefix: max gap 0.37 logit (bf16 rounding); ranks 1-41 identical'), S('Stage 10, 12 contexts, parity.json')], CTL),\n                                 ('matches Stage 6', [T('972 tokens: same token ids, median log-prob gap ~1e-5'), S('Stage 10, crosscheck_stage6.csv')], GRN),\n                                 ('negative control', [T('Punctuation tokens show ~0 title-specific signal at every layer'), S('Stage 10, max 0.014, 9,108 papers, §6.5')], TGT)]):\n    box(s, 0.9 + i * 4.1, 2.0, 3.7, 2.6, [[B(h, col)], b], color=col, size=19, rot=[-1, 1, -0.5][i])")
e("[[B('Caveat: '), T('the parity tolerance was raised 0.25 -> 0.5 after seeing these bf16 gaps.')]]",
  "[[B('Caveat: '), T('the parity tolerance was raised 0.25 -> 0.5 after seeing these bf16 gaps.'), S('parity.json tolerance_amendment')]]")

# deck 18 (build 6) level by layer
e("title(s, 'Names become readable late', 'all 9,108 papers · true title')",
  "title(s, 'Names become readable late', [[T('all 9,108 papers · true title'), S('Stage 10 cohort, §6.1')]])")
e("[T('Everything jumps at '), B('L62', TGT), T(' (rank ~10)')]], rot=1.5)",
  "[T('Everything jumps at '), B('L62', TGT), T(' (rank ~10)'), S('Stage 10, logit L62 -0.93, §6.1')]], rot=1.5)")

# deck 19 (build S11d) chain
e("title(s, 'Co-authors help, and partly replace the title', 'model output · all 9,108 papers · 95% CI')",
  "title(s, 'Co-authors help, and partly replace the title', [[T('model output · all 9,108 papers · 95% CI'), S('Stage 11 E3, §6.11')]])")
e("[[T('later authors '), B('+0.17 to +0.23', TGT)], [T('title-specific part '), B('shrinks')]",
  "[[T('later authors '), B('+0.17 to +0.23', TGT), S('Stage 11 E3, 4,621 target, §6.11')], [T('title-specific part '), B('shrinks')]")

# deck 20 (build R0/R1 b)
e("title(s, 'Authors it wrote vs authors it missed', 'inside 495 R1 papers · paired within paper · 95% CI')",
  "title(s, 'Authors it wrote vs authors it missed', [[T('inside 495 R1 papers · paired within paper · 95% CI'), S('Stage 10, r0_r1_analysis.md §4')]])")
e("[[T('written - missed, output: '), B('+0.20', TGT)], [T('~0 up to L52, grows from '), B('L54')], [T('no title (prior): +0.10')]",
  "[[T('written - missed, output: '), B('+0.20', TGT), S('Stage 10, final L63, 495 papers')], [T('~0 up to L52, grows from '), B('L54')], [T('no title (prior): +0.10'), S('same, no title')]")

# deck 21 (build S12b) probe controls: tags, caveat, notes caveat
e("even though the lenses cannot read it.')",
  "even though the lenses cannot read it. ' + PROBE_CAVEAT)")
e("[[T('another paper\\'s authors: '), B('0')], [T('same-field paper: '), B('0')],",
  "[[T('another paper\\'s authors: '), B('0')], [T('same-field paper: '), B('0'), S('Stage 12 X1 + Stage 13 re-check, §6.12')],")
e("chart(s, 'c16_probe_controls', 0.6, 1.6, 8.0)\n",
  "chart(s, 'c16_probe_controls', 0.6, 1.6, 8.0)\ncaveat(s, y=6.3, w=8.3)\n")

# deck 22 (build 9) lens quality
e("[T('fitA best; at L48 15-18% top-10 vs 1% for logit')], [B('L62:', CTL), T(' logit lens best (59%)')]]",
  "[T('fitA best; at L48 15-18% top-10 vs 1% for logit'), S('Stage 10 X3, 9,108 papers, §6.9')], [B('L62:', CTL), T(' logit lens best (59%)'), S('same, L62')]]")

# deck 23 (build 10) lens extra
e("[[T('Extra signal: '), B('+0.01 to +0.03')], [T('vs ~0.44 at L62')],",
  "[[T('Extra signal: '), B('+0.01 to +0.03'), S('Stage 10 X3, L24-L48, 9,108 papers, §6.9')], [T('vs ~0.44 at L62'), S('same, L62')],")

# deck 24 (build 11) citations
e("[[T('Target: '), B('+0.35 -> +0.64', TGT)], [T('Spearman (title-specific)')], [B('0.45'), T(' all · 0.33 target · 0.19 control')],",
  "[[T('Target: '), B('+0.35 -> +0.64', TGT), S('Stage 10, final, 200 / 84 papers, §6.8')], [T('Spearman (title-specific)')], [B('0.45'), T(' all · 0.33 target · 0.19 control'), S('Stage 10 X2, 9,108 papers, §6.8')],")

# deck 26 (build 13) given name helps
e("[T('surname +0.22 (output)')], [T('+0.32 (logit L62)')]",
  "[T('surname +0.22 (output)'), S('Stage 10, 8,876 authors, §6.7')], [T('+0.32 (logit L62)'), S('same')]")

# deck 27 (build 14) roles
e("cap(s, 'Right: R0/R1 papers, centred within citation bin; Spearman rho = 0.27, p < 0.001.')",
  "cap(s, [[T('Right: R0/R1 papers, centred within citation bin; Spearman rho = 0.27, p < 0.001.'), S('Stage 10, 8,894 papers, §6.6')]])")

for old, new in E:
    n = src.count(old)
    assert n == 1, (n, old[:90])
    src = src.replace(old, new)
P.write_text(src); print('applied', len(E), 'edits')
