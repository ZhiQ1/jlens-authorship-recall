"""Round r (2026-11-12, LOCAL only), report / handbook part (items E, F of the coordinator's round-r message; the deck is done by apply_20261112r*.py of the deck helper).
E) numcheck/claims/image_slides_numbers_20261112.csv: numbers on the OK whole-image deck slides, transcribed from ~/jlens_work/deck_image_audit_20261112.md (parts 1-2), for checker registration.
F1) Report §1 (text line ~729/730): "目标组更高（+0.04 到 +0.08 …）" -> wording B v3 (same text as round o, W3 / W3E), old first-token version in "（旧版只打首 token：…）"; English the same.
F2) Handbook: two definitions after G5.5 in parts/A_global1.html (survive rebuilds): g-def-auroc-2-11b, g-def-np-spec. Handbook + process report rebuilt; K part regenerated from the report as in round q.
Backups *.before_20261112r. Manifest "round r (report/handbook)"."""
import csv, json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; R13 = J / '381_stage13'; PY = sys.executable
REP = R / 'stage1_11/stage1_11_report.html'; PA = R / 'methods/parts/A_global1.html'; K = R / 'methods/parts/K_post_defence.html'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'; CSV = R / 'numcheck/claims/image_slides_numbers_20261112.csv'
SUF = '.before_20261112r'; EDIT = [REP, PA, K]
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + SUF).exists(), p
assert not CSV.exists()
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; LOG = []

# ---------------- E. image-slide numbers (v21 numbering before the two inserted slides; slide_after_r = +2 from 73 on)
SC = '351_stage10/summary_title/'; SX = '351_stage10/summary_extra/'
ROWS = [
 (9, 'HR2 = (H+U)/(M+H+U); R2: HR2 ≤ 0.5; R0: M = 0; R1: M > 0', 'stage1_11_report.html', 'REP text line 748', 'label rule (group lead package), fixed rule'),
 (9, '4/4, mean p(true) ≥ 0.5 (target); ≤ 1/4 (control)', 'rules.yaml (label package)', 'REP text line 744', 'multiple choice over 4 option orders'),
 (9, '79% strict (35,898 / 45,540)', '351_stage10/config/conditions_manifest.json', 'tier_summary (REP 797)', 'false-title donors in the strict tier / all donors'),
 (9, 'Jaccard ≤ 0.6', '351_stage10/config/conditions_manifest.json', 'hard_exclusions', 'title-word Jaccard > 0.6 excluded'),
 (9, '|dyear|/5 + |dauthors| + |dtitle tokens| + 1.5|dcitation bin|', '351_stage10.py', 'line 281; conditions_manifest.json "cost"', 'min-cost matching (figure shorthand; full: |dn_authors|/max(1, .25n) + |dtitle_tokens|/max(1, .2len))'),
 (9, '10 bins, ≥ 30 per group, w = n_t·n_c/(n_t+n_c), 2,000 paper bootstrap', '351_stage10/config/analysis_plan.json', 'B_primary_contrast (REP 802)', 'within-bin target − control'),
 (9, 'drop bins 0–4 (sensitivity)', '351_stage10/summary/B_sens_drop_low_bins.csv', 'analysis_plan.json "drop bins 0-2 and 3-4"', 'sensitivity analysis'),
 (10, 'layers 24, 32, 40, 48, 56, 62', '351_stage10/config/protocol.json', 'main-round layers', 'main round only (L50–L55, L57–L61, 3-1 L41–L47, L49 added later)'),
 (10, 'log10(1/rank): 0 = rank 1, −1 = rank 10', 'stage1_11_report.html', 'REP text line 780', 'nlr'),
 (10, '7 title conditions', 'stage1_11_report.html', 'REP text line 797', 'true, 5 false, no title'),
 (10, 'public 557 / self100 100 / fitA 100 prompts', '351_stage10/config/lenses.json', 'n_prompts', 'lens fit prompts'),
 (11, 'max diff 0.37 logit', '351_stage10/reports/parity.json', 'runs, max_abs_logit_diff (0.367)', 'fast vs slow path, bf16'),
 (11, 'ranks 1–41 identical; 12 contexts', '351_stage10/reports/parity.json', 'REP 807', 'parity check'),
 (11, '972 tokens; log-prob diff median ~1e-5 (3e-6 to 6.6e-5)', '351_stage10/reports/crosscheck_stage6.csv', 'REP 809', 'Stage 6 cross-check'),
 (11, 'punctuation spec max 0.014', SC + 'negative_control_by_role.csv', 'spec_mean_nlr_punct_mean (REP 971)', 'negative control, 9,108 papers'),
 (11, 'tolerance 0.25 → 0.5', 'conclusions_v30_draft.md', 'CV 325–335', 'post-hoc parity tolerance'),
 (13, 'L56 1.17 [0.53, 1.84]; L62 1.08 [0.36, 1.82]; L40 +0.18', 'jlens_archive_stage1_8/experiment_files/351_stage5_crossed_v2/summary/layer_summary.csv', 'group=ALL', 'Stage 5 title-specific logit advantage, 50 papers'),
 (13, '20 A/B pairs, all CIs include 0', 'jlens_archive_stage1_8/experiment_files/351_stage5_crossed_v2/summary/matched_ab_summary.csv', 'REP 334', 'A − B'),
 (14, 'L56 0.616 vs 0.523 (+0.093); L62 0.622 vs 0.555 (+0.066)', '351_stage7_3/summary/paper_null_distribution.csv', 'pool=combined, mode=jlens_L56 (REP 41)', 'gold win rate, true vs mean of 20 substitute titles'),
 (15, 'J-Lens L56 +0.11 (CI spans 0); L32 −0.03; L62 +0.03', '351_stage7_3/summary/matched_ab_bootstrap.csv', '20 pairs', 'A − B win rate by layer'),
 (18, '4.98, 4.18, 3.52, 2.93, 1.9, −0.39 pp (drop 0, 1, 2, 3, 5, 10 largest pairs)', '351_stage8/stage8D/summary/matched_pair_differences.csv', 'mode=jlens_L56 (REP 92)', 'remaining A − B mean, diagnostic only'),
 (22, 'L24–L48 max 0.04 (0.039)', SC + '../summary/A_group_layer.csv', 'REP 905', 'title-specific signal by group, all readouts'),
 (22, 'L62 target +0.56, control +0.24 (+0.560 / +0.235)', '381_stage13/reports/b3_3_1_report.md', '§3 jlens_public table, L62 row', 'public J-lens spec, 4,621 + 2,220 papers'),
 (22, 'L56 rise +0.10 to +0.18', 'stage1_11_report.html', 'REP 905', 'public J-lens spec'),
 (26, '+0.35 → +0.64 (+0.347 [0.317, 0.377] → +0.644 [0.591, 0.701]); 200 / 84 papers', SX + 'X2_by_bin.csv', 'REP 1148', 'target spec at final output, lowest vs highest citation bin'),
 (26, 'Spearman 0.45 / 0.33 / 0.19 (0.451 / 0.328 / 0.187)', SX + 'X2_spearman.csv', 'REP 1255', 'Spearman(spec, citations): all / target / control, 9,108 papers'),
 (29, '495 R1 papers; written − missed +0.20 (+0.199 [0.168, 0.232])', '351_stage10/summary_r0r1/R1_author_written_minus_missed.csv', 'row 2 (CV 220; REP 2339)', 'within-paper pairs, final L63'),
 (29, '≈ 0 before L52, grows from L54', '351_stage10/summary_r0r1/R1_author_written_minus_missed.csv', 'REP 2339, 2371', 'by layer'),
 (29, 'no title (prior) +0.10 (+0.097 [0.060, 0.134])', '351_stage10/summary_r0r1/R1_author_written_minus_missed.csv', 'REP 2339', 'delete-title condition'),
 (32, 'paper prompts L32: Public 11.1, Self 7.2; L62 0.6–1.5', 'Stage 3 Exp 1–4 metrics.csv', 'HB 2089', 'mean KL, 20 generic + 20 paper prompts'),
 (33, 'J-Lens − Vanilla +0.002 [−0.008, +0.012]', '351_stage7_4/summary/jlens_increment_bootstrap.csv', 'REP 93', 'lens increment, all CIs include 0'),
 (37, 'L48 top-10 hit 15–18% (fitA best), logit 1% (1.1%)', SX + 'X3_means.csv', 'REP 1300', 'share of gold tokens in top 10, 9,108 papers'),
 (37, 'L62 logit 59% (59.3%; Jacobian lenses 53.6–54.6%)', SX + 'X3_means.csv', 'REP 1300', 'share of gold tokens in top 10'),
 (38, 'extra signal +0.01 to +0.03 (+0.007 to +0.030), L24–L48', SX + 'X3_pairwise.csv', 'REP 1513', 'lens − logit spec, 9,108 papers'),
 (38, 'L62 ≈ 0.44 (0.436–0.463)', SX + 'X3_means.csv', 'REP 1513', 'spec, four readouts'),
 (38, 'L48–L56 negative (−0.04 to −0.06)', SX + 'X3_tc_spec_vs_logit.csv', 'REP 1513', 'target − control of the extra signal'),
 (42, 'J-Lens first-author first-token RR L56 ≈ 7×10⁻³ (0.0070), L62 ≈ 5.5×10⁻²; Vanilla L62 ≈ 0.2', '351_all/351_stage4_readout.log', 'audit_report.md table 1 (REP 283)', 'RR = 1/rank'),
 (43, 'J-Lens L40 +0.15, L48 +0.19, L56 +0.19, L62 +0.04; Vanilla L32 +0.20', '351_stage7_2/summary/matched_ab_bootstrap.csv', '20 pairs', 'paired A − B win rate'),
 (48, '593 + 593 = 1,186 papers; min(60, n_t, n_c) per bin, seed 11', '361_stage11/summary/E1_recovery.csv', 'row 35 n_papers (CV 339)', 'Stage 11 sample'),
 (48, 'recovery = (intervention − false) / (true − false); false_0', 'stage1_11_report.html', 'REP 1715', 'E1 recovery'),
 (49, 'E1 L48 0.825, L52 0.996', '361_stage11/summary/E1_recovery.csv', 'rows 35, 37 (CV 48)', 'recovery(l), all 1,186 papers, false_0'),
 (49, 'E1 L24 0.07–0.09, L40 0.27–0.34, L48 0.80–0.87', '361_stage11/summary/E1_recovery.csv', 'REP 1715', 'recovery(l), target / control'),
 (49, 'E1t 0.12–0.15', '361_stage11/summary/E1t_recovery.csv', 'REP 1715', 'only the last title token patched'),
 (49, 'E2 from L0 0.83 (0.831), from L52 ≈ 0 (0.007)', '361_stage11/summary/E2_knockout.csv', 'rows 26, 32 (CV 58)', 'loss(l)'),
 (49, 'CI ≈ ±0.02', '361_stage11/summary/E1_recovery.csv', 'lo / hi columns', 'paper bootstrap'),
 (49, 'L44–L52 into the name positions', '371_stage12/summary/P1_patch_pos.csv', 'CV 64', 'P1 names item'),
 (52, 'A 20 / B 20 / C 7 / D 3; L62 C 0.59, A 0.43, B 0.34, D 0.24; L48 0.06–0.09', '351_stage6/summary/integrated_group.csv', 'raw/token_layer_scores.csv (REP 337)', 'conditional JMRR by group'),
 (53, 'first token +0.001 [−0.011, +0.015] (+0.0014); later +0.021 [+0.002, +0.039] (+0.0206 [+0.0022, +0.0385]); all +0.017 [+0.003, +0.030]; Vanilla ≈ +0.015 / +0.017 / +0.017', '351_stage7_1/summary/layer_and_integrated_effects.csv', 'REP 94', 'integrated A − B by token position'),
 (54, 'initial-first: first token 0.112 / later 0.447 (spec); 0.048 / 0.253 (target − control)', SX + 'X1_by_format.csv', 'readout=final, columns spec / spec_tc', 'by name format'),
 (54, 'given-first: first token 0.358 / later 0.396 (spec); 0.174 / 0.202 (target − control)', SX + 'X1_by_format.csv', 'readout=final, columns spec / spec_tc', 'by name format'),
 (55, 'surname +0.22 (+0.222 [0.165, 0.275]) at output, logit L62 +0.32 (+0.322 [0.253, 0.388]); 8,876 authors (678 with given name in top 10)', SX + 'X1_cond_by_first_role.csv', 'REP 1100', 'conditional surname score, given name in top 10 vs not'),
 (55, 'initial in top 10: −0.01, −0.03, +0.03', SX + 'X1_cond_by_first_role.csv', 'REP 1100', 'conditional surname score, initial-first'),
 (56, 'surname first +0.68 (0.685), surname rest +0.58 (0.580), given first +0.36 (0.364), initial +0.13 (0.129), punct +0.00 (0.005)', SC + 'negative_control_by_role.csv', 'all, final, 63; spec_mean_nlr_{role}_mean', 'title-specific signal by token role'),
 (56, '−0.137 → +0.076 (−0.137 / −0.122 / −0.047 / −0.018 / +0.076); ρ = 0.27 (0.268), p < 0.001; 8,894 papers', '351_stage10/summary/C_graded_mc_team_a.csv', 'REP 976', 'spec centred within bin by MC correct count 0–4'),
 (57, 'later authors +0.17 to +0.23 (gain_true 0.173 / 0.229 / 0.234)', '361_stage11/summary/E3_chain.csv', 'final, 63; target', 'chain − isolated scoring by author position, 4,621 target'),
 (57, 'target − control chain_spec 0.151 / 0.124 / 0.114; target chain_spec 0.531 → 0.260', '361_stage11/summary/E3_chain.csv', 'final, 63', 'E3 chain'),
 (76, 'P1 A − B 0.200 [0.188, 0.213]; bin only 0.200; + confounders 0.173; author level + first/other 0.151; + numeric position 0.150', '391_groups/primary.csv', 'P1 row 2 (CV 81)', 'within-bin A − B, team bootstrap'),
 (76, 'P2-first C − A 0.031 (spans 0); regression 0.031–0.034', '391_groups/primary.csv', 'HB 8732–8740', 'C − A, first author'),
 (76, 'P2-other C − A 0.061; regression 0.061, 0.070, 0.056, 0.056', '391_groups/primary.csv', 'HB 8732–8740', 'C − A, other authors'),
 (76, 'P2-pooled C − A 0.037–0.053 (reference only)', '391_groups/primary.csv', 'HB 8732–8740', 'pooled'),
 (76, 'P3 slope 0.059, 0.052, 0.046, 0.045', '391_groups/primary.csv', 'HB 8732–8740', 'recognition slope'),
 (78, 'R0 by MC correct 0–4: 0.17 (n 927), 0.22 (1,256), 0.256 (972), 0.317 (1,028), 0.463 (4,105)', '391_groups/stage10_curves.csv', 'figures/fig2', 'plain means of unwritten-author spec, team bootstrap'),
 (78, 'R1 by MC correct 0–4: 0.27 (15), 0.225 (18), 0.385 (22), 0.37 (26), 0.55 (462)', '391_groups/stage10_curves.csv', 'figures/fig2', 'plain means; n < 30 descriptive'),
 (78, 'R0 by p(true) bin: 0.147 (497), 0.19 (827), 0.237 (1,465), 0.294 (1,207), 0.362 (799), 0.482 (3,493)', '391_groups/stage10_curves.csv', 'figures/fig2', 'plain means by mean p(true) bin'),
 (78, 'R1 by p(true) bin: 0.20 (8), 0.27 (10), 0.295 (24), 0.388 (30), 0.32 (18), 0.556 (453)', '391_groups/stage10_curves.csv', 'figures/fig2', 'plain means; n < 30 descriptive'),
]
OK = {9, 10, 11, 13, 14, 15, 18, 22, 26, 29, 32, 33, 37, 38, 42, 43, 48, 49, 52, 53, 54, 55, 56, 57, 76, 78}
assert {r[0] for r in ROWS} == OK, OK - {r[0] for r in ROWS}

# ---------------- F1. report §1 sentence
W3 = ('预注册版中名的第一个 token 在 L24–L48 为正，姓在 L24–L48 不显著（L40 +0.012 [−0.026, +0.048]）；事后的逐个排除版中姓从 L24 起为正（L40 +0.030 [0.013, 0.048]）。名的信号在三版中一致；姓的证据弱，只来自事后版本。'
      '首字母在个别层为正、模式不一致（未做多层校正），不作结论')
W3E = ('in the pre-registered version the given-name first token is positive at L24–L48 and the surname is not significant at L24–L48 (L40 +0.012 [−0.026, +0.048]); in the post-hoc per-donor version '
       'the surname is positive from L24 (L40 +0.030 [0.013, 0.048]). The given-name signal is consistent across the three versions; the surname evidence is weak and comes only from the post-hoc version. '
       'The initial is positive at some layers with an inconsistent pattern (no multi-layer correction); no conclusion is drawn')
assert S[REP].count(W3) >= 1
LEAD = 'target − control（同一引用档内，全部作者全部名字 token 按角色，措辞 B 第 3 版）：'; assert S[REP].count(LEAD) >= 1
SRCZ = '<span class="src">（同上，引用档内目标−对照合并，L24–L60 为 0.036–0.078，95% CI 均在 0 以上；381_stage13/reports/e4b_split_compare.md）</span>'
BADGE = '<span style="display:inline-block;font-size:12px;font-weight:700;padding:0 6px;margin:0 4px;border-radius:4px;background:#2F7D3B;color:#fff">已复核</span>（已按作者团队分折、并剔除 probe 训练时见过同一标题的论文后复核，见第四部分）'
oz = '），目标组更高（+0.04 到 +0.08' + SRCZ + '）' + BADGE + '。一句话概括：'
nz = '）' + BADGE + '；' + LEAD + W3 + '（旧版只打首 token：目标组更高 +0.04 到 +0.08' + SRCZ + '）。一句话概括：'
assert S[REP].count(oz) == 1; S[REP] = S[REP].replace(oz, nz); LOG.append(('stage1_11/stage1_11_report.html', oz, nz, 1))
SRCE = '<span class="src">(same, within-bin target − control pooled, L24–L60 0.036–0.078, 95% CIs above 0; 381_stage13/reports/e4b_split_compare.md)</span>'
oe = '), more for target papers (target − control +0.04 to +0.08' + SRCE + '; re-checked with team folds and title reuse removed). In one line:'
ne = '; re-checked with team folds and title reuse removed); target − control (within citation bin, all name tokens of all authors by role, wording B v3): ' + W3E + ' (old first-token-only version: target − control +0.04 to +0.08' + SRCE + '). In one line:'
assert S[REP].count(oe) == 1; S[REP] = S[REP].replace(oe, ne); LOG.append(('stage1_11/stage1_11_report.html', oe, ne, 1))

# ---------------- F2. handbook definitions (part A, after G5.5, before the end of section g-scoring)
gn = (R13 / 'reports/b2_gennames_b_report.md').read_text(encoding='utf-8').splitlines()
assert gn[23].startswith('## Within-paper AUROC on target papers (team-cluster 95% CI, 2,000 draws); signal = CI(probe - position) > 0 and CI(probe - string) > 0')
an = (Path.home() / 'jlens_work/13_stage13/stage13_b2_gennames_b_analyze.py').read_text(encoding='utf-8')
assert '(pairs within paper, ties 0.5), 95% CI by author-team cluster bootstrap (2,000 draws, shared by all scores -> paired diffs).' in an
npr = (R13 / 'reports/b2_np_report_v2.md').read_text(encoding='utf-8')
assert "Ridge from the layer-l residual at each name-token-predicting position to the model's own L63 state at the same position, trained on true-title rows" in npr and 'decoded within the 9,137 name token ids' in npr
DEFS = '''
<h3 id="g-def-auroc-2-11b">定义：2-11b 论文内 AUROC</h3>
<pre class="code">对象：补充 15（2-11b）中模型自己写出的作者名单；每个写出的名字标为 M（真作者）或 H（编造），P、U 不参与。
只用 target 论文中至少有 1 个 M 且至少有 1 个 H 的论文（518 篇，3,388 对）。
对每篇这样的论文 p：取 p 内全部 (M 名字, H 名字) 配对，probe 分数 M &gt; H 记 1，相等记 0.5，否则记 0；
AUROC_p = 这些配对得分的平均；论文内 AUROC = 跨论文汇总全部配对的平均（配对只在同一篇论文内组成）。
probe = L2 logistic（第 l 层残差 → M / H），C 在第 0 折上选，按存档的作者团队 5 折做折外预测，训练折标准化。
基线（同一套拟合）：排位基线（名字在列表中的序号、相对序号）、名字特征基线（字符长度、log(1 + 全名在队列中的出现次数)）。
信号 = CI(probe − 排位) &gt; 0 且 CI(probe − 名字特征) &gt; 0；95% CI：按作者团队整群 bootstrap 2,000 次（所有分数共用同一组抽样，差值为配对差）。
打乱标签对照：在训练折内打乱标签（rng 1212）后重算。</pre>
<p>位置：(ii) name_mean（名字 token 平均，主分析）、(i) pred_first（写出名字之前、预测第一个名字 token 的位置，次分析）、last（描述）。control 论文只给点估计。<span class="src">381_stage13/reports/b2_gennames_b_report.md 第 24 行（"Within-paper AUROC on target papers (team-cluster 95% CI, 2,000 draws); signal = CI(probe - position) &gt; 0 and CI(probe - string) &gt; 0"）· 13_stage13/stage13_b2_gennames_b_analyze.py 文件说明第 4–10 行 · config/prereg_addendum15.json</span></p>

<h3 id="g-def-np-spec">定义：名字位置 probe spec</h3>
<pre class="code">对象：补充 11 A（2-5）名字位置 probe，teacher forcing 下的偏好，不是生成。
输入 x = 第 l 层、每个"预测名字 token 的位置"上的残差（标题为 true / false_k 的运行各一份）；
probe = ridge 回归，目标是同一位置模型自己的 L63 状态；只用真标题行训练，按存档的作者团队分折，训练折标准化，α 在第 0 折上选；
预测出的 L63 状态 → final norm → 9,137 个名字 token id 的 lm_head 行 → gold token 的名次 rank → nlr = log10(1/rank)，论文内按 token 平均。
spec = probe(true) − probe(false)      （false = 可用假标题的平均，见下方三个版本）
  Vpd（主分析，偏离 D11-1）：每篇只平均供体不是本运行其他训练折论文的假标题（逐个假标题排除）；没有可用假标题的论文不计。
  V0：probe(true) − probe(false_0)，只用 false_0 可用的论文（干净的单一对照）。
  V5x0：5 个假标题平均，只按 false_0 剔除论文——含泄漏，仅敏感性。
target − control：同一引用档内合并差（同 G5.4）；95% CI：作者团队整群 bootstrap 2,000 次。
置换对照：gold 换成随机另一篇 / 同领域另一篇论文作者的 token，与主结果用同一组假标题（D11-1 第 2 版）。</pre>
<p>lens 比较：logit lens 与 public J-lens 在同一批论文、token、层与假标题上的 spec；lens 在全词表上排名，probe 在 9,137 个名字 token 内排名，两者尺度不同，只比较符号与区间，不比较大小。<span class="src">381_stage13/reports/b2_np_report_v2.md 开头说明与第 4 节 · config/prereg_addendum11.json · config/prereg_addendum11_deviations.json（D11-1）· _v2.json（D11-1 第 2 版）</span></p>
'''
i = S[PA].index('<h3 id="g-scoring-worked">'); j = S[PA].index('</section>', i)
assert 'g-def-auroc-2-11b' not in S[PA]
S[PA] = S[PA][:j] + DEFS.lstrip('\n') + S[PA][j:]
LOG.append(('methods/parts/A_global1.html', '(after G5.5, end of section g-scoring)', '+ 定义：2-11b 论文内 AUROC (#g-def-auroc-2-11b); 定义：名字位置 probe spec (#g-def-np-spec)', 2))

# ---------------- K part regenerated from the report (as round q)
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
kk = makeK(S[REP])
for z in ['np', 'f1', 'gn', 'ps']: kk = kk.replace(f'id="pd-b2-{z}"', f'id="k-b2-{z}"')
newK = S[K][:S[K].index(lead) + len(lead)] + kk + '\n</section>'
if newK != S[K]: S[K] = newK; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))

# ---------------- write
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + SUF))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
with open(CSV, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh); w.writerow(['slide', 'slide_after_r', 'number_as_written', 'source_file', 'column/row', 'how_computed'])
    for s, num, f, cr, how in ROWS: w.writerow([s, s + 2 if s >= 73 else s, num, f, cr, how])
LOG.append(('numcheck/claims/image_slides_numbers_20261112.csv', '(new)', f'{len(ROWS)} rows, {len(OK)} OK image slides (from deck_image_audit_20261112.md)', len(ROWS)))
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
h = HB.read_text(encoding='utf-8'); assert 'id="g-def-auroc-2-11b"' in h and 'id="g-def-np-spec"' in h
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round r (report/handbook)', '', 'Script `sync_20261107/apply_20261112r_docs.py` (backups `*.before_20261112r`). Items E, F of the round-r message: image-slide numbers CSV; report §1 wording B v3; two handbook definitions. Handbook + process report rebuilt.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| rd{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round r docs:', len(LOG), 'log rows;', len(ROWS), 'csv rows')
