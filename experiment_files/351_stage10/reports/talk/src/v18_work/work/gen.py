import json, sys
D = '/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/deck/'
E = []
def S(t): return '<span class="src">\u200b(' + t + ')</span>'
def add(slide, old, tag, after=None):
    """insert tag after substring `after` (default: end of old)"""
    if after is None: new = old + S(tag)
    else:
        i = old.index(after) + len(after); new = old[:i] + S(tag) + old[i:]
    E.append({'slide': slide, 'old': old, 'new': new})
def foot(slide, lines, y0=None, x=70):
    n = len(lines); y0 = y0 or (712 - 14 * (n - 1))
    t = ''.join(f'<text x="{x}" y="{y0 + 14*i}" class="src" font-size="12.5" fill="#8a8f98" text-anchor="start">{l}</text>' for i, l in enumerate(lines))
    E.append({'slide': slide, 'old': '</svg>', 'new': t + '</svg>'})

# 1
add(1, '20 → 50 → 200 papers</p>', 'Stage 4, Pilot50, Stage 8 cohorts', after='papers')
add(1, '9,108 papers · 149,999 name tokens</p>', 'Stage 10 cohort: papers.parquet, name_tokens.parquet', after='tokens')
# 3
add(3, '<li>Pilot50 / Stage 8: 50 and 200 papers</li>', 'pilot50_v1.csv, stage8_papers.csv', after='papers')
add(3, '<li>All 9,108 papers, every author, every token</li>', 'papers.parquet', after='9,108 papers')
add(3, 'the output gap is +0.199 vs +0.207', 'Stage 10, final L63, R0 3,423 vs 2,151; §6.13')
# 4
add(4, 'Counts from the 6,841-paper cohort.', 'Stage 1, 351_audit.json group_counts')
add(4, 'adds 511 partial-recall papers', '351_audit.json', after='511')
add(4, 'the output gap is +0.199, versus +0.207 for target vs control', 'Stage 10, final L63, within-bin; §6.13')
# 6 (SVG)
foot(6, ['Counts: 351_stage10/cohort/papers.parquet (recall_level × MC outcome); 593 + 593: 361_stage11 sample (1,186 papers); 1,178 pairs: Stage 13 X1/X3 pair table'])
# 7
add(7, 'From the 15 Oct label package (9,108 papers) to a frozen 6,841-paper analysis cohort', '351_audit.json total, four_group_total')
add(7, '<th>Full</th>', '351_audit.json', after='Full')
add(7, '<th>Pilot50</th>', 'pilot50_v1.csv', after='Pilot50')
add(7, 'the strict pass rate is <b>25.5%</b>', '796 papers; label_README.md l.8')
# 13
add(13, 'L62 +1.08 [0.36, 1.82]', 'Stage 5, J-Lens, 50 papers, layer_summary.csv')
add(13, '+0.08 [−0.43, +0.65]', '20 pairs, matched_ab_summary.csv')
# 14
add(14, '35/50 papers positive', 'J-Lens L56, 50 papers; paper_null_distribution.csv; CI recomputed 10-30')
add(14, 'Leave-one-out: +8.6 to +10.0 pp', 'stage7_l56_loo.csv')
add(14, 'final output +7.2 pp', 'paper_null_distribution.csv')
add(14, '+0.018 [−0.021, +0.063]', '20 pairs, integrated_ab_bootstrap.csv')
# 15
add(15, 'Excluding them: +0.026 → +0.028.', 'quality.json; paper_null_distribution.csv')
add(15, 'pooled +0.026 to +0.032; all six A−B CIs include 0.', 'stage7_weighting_title_advantage.csv')
add(15, '0/6 beyond its own 20-title tail (≤ 0.05).', 'floor_L56_low_six.csv')
add(15, '(CI below 0).', '20 pairs, matched_ab_bootstrap.csv')
# 16 (SVG)
foot(16, ['+5.18 pp: Stage 8D RQ1, J-Lens L56, 200 papers, stage8D/summary/primary_questions.csv · +2.33 pp: J-Lens 7-layer, 200 papers, recompute_2026-10-30/s8_endpoints.csv'])
# 17
add(17, '<tr><th></th><th>Estimate</th>', 'Stage 8D, J-Lens L56; primary_questions.csv', after='<th>')
add(17, '<td class="a">RQ1 title</td>', '200 papers', after='RQ1 title')
add(17, '<td class="a">RQ2 A−B</td>', '100 pairs', after='RQ2 A−B')
add(17, '<td class="a">RQ3 low−high</td>', '25 + 25 pairs', after='RQ3 low−high')
add(17, '<td class="b">J-Lens−Vanilla</td>', 'jlens_minus_vanilla.csv', after='J-Lens−Vanilla')
add(17, 'high +4.4 [−1.1, 10.0]', '50/100/50 papers; layer_and_band_summary.csv')
# 18
add(18, 'median +4.4 pp</li>', 'J-Lens L56; matched_pair_differences.csv', after='+4.4 pp')
add(18, 'top 10 → <span class="r">−0.4 pp</span>', 'recomputed from same file')
add(18, 'RQ1 +4.6, RQ2 +5.4 pp', 's8_8E_weighting_by_paper.csv')
add(18, '+0.12 pp per token', '200 papers; s8_unsourced_intervals.csv')
# 19 (SVG)
foot(19, ['Ranks: 351_stage10/raw/[cond_*/]final/L63/shard_011.npz rows 25025–40 (author 1 shown) · nlr, spec, total, topic: summary_title/paper_title_contrasts.parquet (final, L63)'])
# 20 (SVG)
foot(20, ['7,247 teams among 9,108 papers: 381_stage13/reports/cluster_ci.md'])
# 23 (SVG)
foot(23, ['+0.061: Stage 13 E4b re-check, probe scores ONLY THE FIRST NAME TOKEN, all papers (1,863), team folds, title reuse dropped; e4b_trainstd_compare.md',
          'year R² 0.38 → 0.56: Stage 13 M2, 9,108 papers, team CI; summary_cpu_teamci/M2_teamci.csv'])
# 26 (SVG)
# 29
add(29, 'pilot L56 +9.3 pp', '7.3, 50 papers')
add(29, '<span class="a">+5.2 pp</span>', '8D RQ1, 200 papers')
add(29, '+5.0 pp on 200 papers but gone after dropping 10 pairs', '8D RQ2, 100 pairs')
add(29, '≈0.44 at L62', 'L62, §6.9')
add(29, '[0.20, 0.22] at the output', 'L63, §6.4')
add(29, 'Name prior is only ~1/3 of the gap; ~0 on surnames', '§6.12')
add(29, '(ρ = 0.45)', '§6.8')
add(29, '<span class="b">+0.20</span> [0.19, 0.21]', 'R0, §6.13')
add(29, '(+0.11 over A)', '§6.13')
# 31
add(31, '(63/63 and 6/6 finite)', 'matrices.csv; frobenius_norms.csv')
add(31, '(paper L32: 11.1 → 7.2)', '20 + 20 prompts; metrics.csv')
add(31, 'Top-10 overlap is worse (0.36 vs 0.72)', 'metrics.csv')
add(31, 'both lenses 14/20 full-name wins at L48', '20 papers, layer_summary.csv')
# 32
add(32, 'r = 0.45, ρ = 0.47; signs agree 32/50', '50 papers, cross_stage_correlations.csv')
add(32, '24/50 positive', 'jlens_increment_bootstrap.csv')
add(32, '<td>−0.014 [−0.033, +0.004]</td>', '20 pairs', after='+0.004]')
# 33
add(33, '~324 s Jacobian time per prompt, ~62 GiB CPU RAM', 'full_A.log; benchmark log')
add(33, '<figcaption>Archived progress: Fit A 4/100, Fit B 0/100 at the time of writing', '351_stage9 checkpoints')
# 34 (SVG)
foot(34, ['Ranks of “Co” (author 1, token 5), true title: 351_stage10/raw/logit/L{24…62}/shard_011.npz row 25029; out = raw/final/L63'])
# 39
add(39, '(7.4: +0.002; Stage 8: −1.4 pp)', '50 / 200 papers')
add(39, 'top-10 rate 15–18% at L48 vs 1% for logit lens', '9,108 papers; X3_means.csv')
add(39, 'Extra title-specific signal only +0.01–0.03', 'L24–L48; X3_means.csv')
add(39, '+0.05 → +0.08 (re-checked)', 'E4b, scores only the first name token; e4b_trainstd_compare.md')
# 41
add(41, '~91 s per paper, ~29.5 GiB GPU', '351_stage4_readout.log')
add(41, 'L56 first-author mean RR 0.0070, median only 0.0009', '20 papers; audit_report.md table 1')
add(41, 'Dropping it: 0.0070 → 0.0021.', 'same file')
# 42
add(42, '75,000 scored pairs', 'candidate_pairwise_scores.csv')
add(42, 'L62 +0.04 (spans 0)', '20 pairs, matched_ab_bootstrap.csv')
E.append({'slide': 42, 'old': '7-layer integrated: +0.105 [−0.012, +0.228]', 'new': '7-layer integrated: +0.105 [−0.012, +0.229]' + S('20 pairs; recomputed 10-30')})
add(42, '156/5,000 false names share the gold first token (ties)', 'quality.json')
add(42, 'only ~46 distinct first tokens', 'mean of 50 papers; candidates csv')
# 45, 46, 61, 62, 63 (SVG)
foot(45, ['R(l): Stage 13 X6, mean of 5 false titles, all 1,186 papers; 381_stage13/summary_x6/x6_recovery.csv'])
foot(46, ['S(l): Stage 13 X7, 1,186 papers (593 target + 593 control); 381_stage13/reports/x7_report.md'], x=390)
foot(61, ['R: Stage 13 X1, test set 582 papers; 381_stage13/reports/x1_report.md'])
foot(62, ['Word overlap 0.22 / 0.14: config/x3_lexical_neighbour_j2.csv (this paper) · medians: x3_report.md (primary set, 1,110) · G′: x3_textbase_recovery.md (test)',
          '+0.239: Stage 13 X3 behaviour, test, 552 papers; x3_textbase_recovery.md'])
foot(63, ['D: Stage 13 X4, test set, team CI; first author L8 +0.046 [0.035, 0.059], year L40 +0.013 [0.008, 0.018]; 381_stage13/reports/x4_report.md'])
# 49
add(49, 'driven by one paper (71%)', 'audit_report.md')
add(49, 'recovers 80–87% at L48, 100% from L52', 'Stage 11 E1, 593 + 593; x6_report.md')
# 51
add(51, '50 papers, 227 authors, 972 name tokens', 'token_layer_scores.csv')
add(51, '<th>Integrated JMRR</th>', 'integrated_group.csv', after='Integrated JMRR')
add(51, 'Vanilla also +0.091', '20 pairs, matched_ab_bootstrap.csv')
# 52
add(52, '<th>A−B (7 layers)</th>', '20 pairs; layer_and_integrated_effects.csv', after='A−B (7 layers)')
add(52, 'continuation +0.121 (15/20)', 'layer_position_effects.csv')
# 57
add(57, 'not the first token (+0.001)', '7.1, 20 pairs')
add(57, '73% of names start with an initial', '24,739 / 33,780; §6.7')
add(57, 'help predict them (+0.22)', 'final L63; §6.7')
add(57, 'the colon alone little (+0.17)', 'P1, 1,186 papers; P1_patch_pos.csv')
# 58
add(58, 'True title beats false titles (≈0.44 at L62)', '§6.9', after='≈0.44 at L62')
add(58, 'name positions alone 0.61 → 0.85; ‘:’ alone ≤ 0.17', 'E1, P1; 1,186 papers')
add(58, '(+0.21 at output)', '§6.4', after='+0.21 at output')
add(58, 'MLP takes over at L52–56 (0.18, 0.22)', 'P2, 1,186 papers')
# 59
add(59, 'one paper = 71% of the Stage 4 L56 mean', '20 papers')
add(59, 'removing 10 of 100 pairs', '8D, matched_pair_differences.csv')
add(59, '3% tie with gold', '7.2 quality.json: 156/5,000')
add(59, 'strict “pass” 25.5% in the 0–2 citation bin', 'label_README.md')
# 60
add(60, '+9.3 pp pilot, +5.2 pp new 200', '7.3; 8D RQ1')
add(60, '≈0.44 title-specific at L62', 'X3_means.csv')
add(60, '<td>+0.21 at output, ≈0 middle</td>', '§6.4', after='+0.21 at output')
add(60, '+0.20 at output, ≈0 middle; R1 adds strength', '§6.13', after='+0.20 at output')
add(60, 'monotonic, ρ = 0.45', 'X2_spearman.csv')

json.dump(E, open(D + 'html_tags.json', 'w'), ensure_ascii=False, indent=1)
print(len(E), sorted({e['slide'] for e in E}))
