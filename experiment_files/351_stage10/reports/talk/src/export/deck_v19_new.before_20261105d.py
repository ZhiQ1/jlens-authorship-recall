"""2026-11-05 deck v19 (copy of deck_v18_new.py + X2 slide + group results / re-runs; user decisions ~17:20). Original docstring: deck v18: new slides (Stage 12/13 results in full; post-defence section) as one spec -> HTML section + native pptx shapes.
Segments of a bullet: ('t', text) plain, ('b', text) bold, ('s', text) grey source tag.  Notes (Chinese) carry full source tags in 〔…〕."""
import html as H

G = '/scratch/zhang.zhiqi2/jlens/391_groups/figures/'

def S(t): return ('s', t)
def T(t): return ('t', t)
def B(t): return ('b', t)

SLIDES = []

# ---------------------------------------------------------------- Stage 12 / 13 results (after the Stage 12-13 summary page)
SLIDES.append(dict(key='s12', where='after_summary', tag='Stage 12', title='Stage 12: where the paper information travels',
  sub='All 408 GPU units done · true title → false_0 · share of the true−false gap recovered at the output',
  left=[
   [B('P1 one position at a time: '), T('the colon carries at most 0.17 (L52)'), S('(Stage 12 P1, 1,186 papers, paper bootstrap; P1_patch_pos.csv)'),
    T('; all name positions together 0.85 at L52'), S('(same; CI [0.830, 0.864])'), T('; the whole prompt 1.00 (= Stage 11 E1)'), S('(same, 0.996)')],
   [B('P2 one component of one layer: '), T('attention at L48 +0.23 [0.22, 0.24]'), S('(Stage 12 P2, 1,186 papers; P2_patch_comp.csv)'),
    T(', MLP at L52–L56 +0.18 to +0.22'), S('(same)'), T(' → attention reads the title in, MLP processes it next')],
   [B('N1 name plausibility: '), T('without a title the true list looks "most real" in 0.255 of papers (chance 0.25)'),
    S('(Stage 12 N1, 8,894 R0/R1 papers; N1_prior_mc.csv)'), T('; with the true title 0.625'), S('(same, CI [0.615, 0.635])')],
   [B('N2 pure name prior (no paper): '), T('target − control +0.047 [0.031, 0.062] vs +0.247 with the true title'),
    S('(Stage 12 N2, final L63, 4,621 + 2,220, within bin; stage12_report.md)'), T(' → prior ≈ 19% of the gap')],
   [B('F2 lens fitted on author prompts: '), T('target − control ≤ 0 at L24–L56, +0.238 only at L62'),
    S('(Stage 12 F2, name positions, Stage 11 sample, true − 5 false; F2_author_lens.csv)')]],
  note=('No single "notebook" token', 'The paper leaves the title at L44–L48 and is spread over the name positions; a lens fitted on author prompts still reads nothing paper-specific in the middle layers.'),
  notes='Stage 12（408 个 GPU 单元全部完成）。P1 一次只替换一个位置：“:” 最多恢复 0.17〔Stage 12 P1，真标题→false_0，只替换 “:”，L52，最终输出恢复比例，Stage 11 样本 1,186 篇，论文 bootstrap 95% CI [0.156, 0.187]；报告第四部分 Stage 12 P1 表；371_stage12/summary/P1_patch_pos.csv〕，全部名字位置一起 0.85〔同上，全部名字位置，L52 0.847 [0.830, 0.864]〕，整个提示 1.00〔同上，= Stage 11 E1，L52 0.996〕。P2 只替换一层的一个组件：L48 注意力 +0.23〔Stage 12 P2，标题之后全部 token，1,186 篇，L48 注意力 0.231 [0.221, 0.244]；371_stage12/summary/P2_patch_comp.csv〕，L52–L56 的 MLP +0.18 到 +0.22〔同上，MLP L52 0.178 [0.168, 0.190]、L56 0.224 [0.208, 0.239]〕：先是注意力把标题读进来，然后 MLP 接着处理。N1：不给标题时，真作者列表在 4 个选项里“最像真的”的比例 0.255〔Stage 12 N1，删去标题，R0/R1 论文 8,894 篇，CI [0.246, 0.264]；371_stage12/summary/N1_prior_mc.csv〕，与随机的 0.25 一样；给真标题后 0.625〔同上，真标题，CI [0.615, 0.635]〕。N2：纯名字提示下 target − control 只有 +0.047〔Stage 12 N2，纯名字提示，最终输出 L63，目标 4,621 / 对照 2,220，引用档内差，论文 bootstrap 95% CI [0.031, 0.062]；371_stage12/reports/stage12_report.md〕，真标题下 +0.247〔同上，真标题，[0.229, 0.266]〕，先验约占 19%〔0.047 ÷ 0.247，由上两数算出〕。F2：用作者提示拟合的 lens 在名字位置 L24–L56 的 target − control 都 ≤ 0，只有 L62 为 +0.238〔Stage 12 F2，名字位置，真 − 5 个假标题平均，Stage 11 样本，[0.210, 0.267]；371_stage12/summary/F2_author_lens.csv〕。'))

SLIDES.append(dict(key='x6x7', where='after_summary', tag='Stage 13 · X6 X7', title='The Stage 11 timing holds for all 5 false titles',
  sub='X6: replacement with each of the 5 false titles · X7: knockout minus the same knockout on the false-title run (S = T − F)',
  left=[
   [B('X6 replacement: '), T('mean over 5 false titles 0.821 at L48 and 0.995 at L52'),
    S('(Stage 13 X6, 1,186 papers, team-cluster CI; x6_recovery.csv)'), T('; each false title within 0.02 of false_0'), S('(x6_report.md)'),
    T(' → "≈80% at L48, all from L52" is not specific to false_0')],
   [B('By name-token role: '), T('surname first token 0.734 at L48, surname continuation 0.893; all roles ≥ 0.96 at L52'),
    S('(X6 roles, all papers; x6x7_roles.md)')],
   [B('X7 knockout: '), T('blocking the title on the false-title run RAISES the true author score (F < 0), so the paper-specific loss S(L0) ≈ 1.00'),
    S('(Stage 13 X7, 1,186 papers, all: 1.004; x7_report.md)'), T('; S(L52) = 0.029 [0.021, 0.038]'), S('(same, all papers)')],
   [B('Pre-registered verdict: '), T('holds for target (S(L52) 0.018) and all papers; control just misses (0.051, threshold 0.05)'),
    S('(X7, target 593 / control 593; x7_report.md)'), T(' → control needs the title until L54–L56')]],
  note=('What changes', 'Nothing in the timing: the title is used up to about L52 (control L54–56) and the paper information sits in the post-title positions by then.'),
  notes='X6：把 Stage 11 的替换换成 5 个假标题各做一遍，平均恢复 L48 为 0.821、L52 为 0.995〔Stage 13 X6，真标题→5 个假标题平均，标题后全部位置，最终输出恢复比例（均值比），1,186 篇，团队聚类 95% CI L48 [0.806, 0.835]、L52 [0.990, 1.001]；报告第四部分 X6 表；381_stage13/summary_x6/x6_recovery.csv〕；每个假标题与 false_0 相差不超过 0.02〔381_stage13/reports/x6_report.md；对照组最大 0.019〕。按名字 token 角色：姓的第一个 token L48 为 0.734，姓的后续 token 0.893〔X6 角色拆分，全部论文，团队 CI [0.711, 0.757] / [0.880, 0.906]；381_stage13/reports/x6x7_roles.md〕，L52 各角色都 ≥ 0.96〔同上〕。X7：在假标题运行上做同样的阻断，真作者的分数反而上升（F 为负），所以论文特有的损失 S(L0) ≈ 1.00〔Stage 13 X7，S = T − F，1,186 篇，全部 1.004；381_stage13/reports/x7_report.md〕，S(L52) = 0.029〔同上，全部论文，团队 CI [0.021, 0.038]〕。预注册判定 S(L52) ≤ 0.05：target 成立（0.018〔X7，target 593 篇，[0.010, 0.027]〕），control 差一点不成立（0.051〔X7，control 593 篇，[0.033, 0.068]〕），control 要到 L54–L56 才完全不需要标题。'))

SLIDES.append(dict(key='m3x1', where='after_summary', tag='Stage 13 · M3 X1', title='Same title, different question',
  sub='M3: probes across three questions (authors / year / field) · X1: patch A’s title state from another question into B’s author prompt',
  left=[
   [B('M3 transfer at the title: '), T('T ≥ 0.92 at L16–L40, but never above the L4 text level'),
    S('(Stage 13 M3, 9,108 papers, team folds; m3_report.md)'), T(' (year T − T(L4) −0.03 to −0.06)'), S('(same, CIs exclude 0)'),
    T(' → M3 does not support H2')],
   [B('M3 at the colon: '), T('T < 0.5 → the state is already organised by the question (H1)'), S('(same; summary_m3/m3_transfer.csv)')],
   [B('X1 replacement: '), T('R ≈ 0.99 (L24), 0.92 (L40), 0.42 (L48) whichever question the state came from'),
    S('(Stage 13 X1, test 582 pairs, team CI; x1_report.md)'), T('; authors − year within ±0.02, except a small +0.019 at L48'),
    S('(same, [0.012, 0.026])')],
   [B('Retrieval (added 2026-11-05): '), T('no layer retrieves the paper across questions better than L4'),
    S('(X5 retrieval, 9,108 papers; x5_retrieval.md; post-defence)')]],
  note=('Reading', 'The title state hardly depends on the question, and the replacement effect is task-independent; but nothing goes beyond what the title text alone gives at L4.'),
  notes='M3：同一篇论文换三种问法，标题最后一个 token 上的迁移比 T 在 L16–L40 都 ≥ 0.92〔Stage 13 M3，9,108 篇，按作者团队分 5 折的 probe，迁移比 = 跨问法成绩 ÷ 同问法成绩；报告第四部分 M3 表；381_stage13/reports/m3_report.md〕，但按补充 2 只看相对 L4 的变化：年份 T − T(L4) 为 −0.03 到 −0.06〔同上，团队聚类 95% CI 都不含 0；summary_m3/m3_transfer.csv〕，不高于文字水平，所以 M3 不支持 H2。“:” 位置 T < 0.5〔同上〕，状态已按问题重新组织。X1：把 A 在别的问法下的标题状态替换进 B 的作者提示，恢复 R 在 L24 约 0.99、L40 0.92、L48 0.42〔Stage 13 X1，测试集 582 对，作者问法来源，团队聚类 95% CI；381_stage13/reports/x1_report.md〕，三种来源几乎相同；作者 − 年份在 ±0.02 以内，只有 L48 有 +0.019〔同上，[0.012, 0.026]〕。答辩后补算的跨任务检索（X5 预注册曲线）也没有一层高于 L4〔X5 检索，9,108 篇，top-1；381_stage13/reports/x5_retrieval.md；事后补算〕。'))

SLIDES.append(dict(key='x4x3', where='after_summary', tag='Stage 13 · X4 X3', title='Patchscope and paraphrases',
  sub='X4: decode year / first author / field from the paper’s own title state · X3: paraphrased title vs a word-matched other paper',
  left=[
   [B('X4 first author: '), T('decodable from L8, D = +0.046 [0.035, 0.059]'), S('(Stage 13 X4, test split, team CI; x4_report.md)'),
    T('; year only from L40, +0.013 [0.008, 0.018]'), S('(same)'), T('; field never → order opposite to the H2 prediction')],
   [B('But: '), T('the L8 signal sits on the surname (+0.066), where the text-baseline check failed'),
    S('(X4 role split, 1,178 papers; x4_rolesplit.csv)'), T(' → may be explained by the title text')],
   [B('X3 paraphrase: '), T('closer to the original than a word-matched paper beyond L4, peak L36 +0.16'),
    S('(Stage 13 X3, test 552 papers, G′ − G′(L4), team CI [0.146, 0.171]; x3_report.md)'),
    T('; behaviour keeps ≈ 90% of the first-author preference'), S('(same, 0.90 [0.87, 0.94])')],
   [B('Post-hoc checks: '), T('a sentence-embedding model without author knowledge shows a comparable advantage, and target = control'),
    S('(X3 text baselines and group split; x3_textbase_recovery.md, x3_groupsplit.md)'), T(' → meaning, not separable from paper identity')]],
  note=('H2 / H3 so far', 'H2 partly supported but not established (rests on M2 and X1); H3: insufficient evidence (text baseline not weaker than Qwen).'),
  notes='X4：把论文自己的标题状态注入“X 的第一作者 / 年份 / 领域是”提示。第一作者从 L8 起可解码，D = +0.046〔Stage 13 X4，测试集，团队聚类 95% CI [0.035, 0.059]；报告第四部分 X4 表；381_stage13/reports/x4_report.md〕；年份要到 L40，+0.013〔同上，[0.008, 0.018]〕；领域读不出——顺序与 H2 的预测相反。L8 的作者信号主要在姓的第一个 token 上（+0.066〔X4 按 token 角色，1,178 篇，[0.045, 0.088]；381_stage13/summary_x1x4/x4_rolesplit.csv〕），而姓氏上文本基线的阳性对照没有通过，所以可能来自标题文字。X3：改写标题在 L28–L40 比用词相近的近邻 D 更接近原标题，超出 L4 文字水平，最高 L36 +0.16〔Stage 13 X3，主分析测试集 552 篇，G′ − G′(L4)，团队 CI [0.146, 0.171]；381_stage13/reports/x3_report.md〕；行为上保留约 90% 的第一作者偏好〔同上，教师强制打分，0.90 [0.87, 0.94]〕。事后加的检验：不认识作者的句子向量模型在用词匹配子集上也有相当优势，target 与 control 没有差别〔381_stage13/reports/x3_textbase_recovery.md、x3_groupsplit.md〕，所以只能说中间层表示了标题的意思，不能与论文身份区分。'))

# ---------------------------------------------------------------- post-defence section (after the last slide)
SLIDES.append(dict(key='x2', where='after_summary', tag='Stage 13 · X2', title='X2: swap only a subspace',
  sub='Patch only the paper-attribute (S_id, 9-dim) or the author (S_auth, 10-dim) component of A’s title states into B · test 582 pairs · team-cluster 95% CI',
  left=[
   [B('Carry: '), T('S_id at L40 moves +0.005 of the gap (random +0.003, full replacement +0.920); S_auth at L48 moves +0.018 (random +0.003, full +0.428)'),
    S('(Stage 13 X2, test 582 pairs; x2_report.md Verdict)')],
   [B('Pre-registered verdict: '), T('H2 not supported (R_id 0.005 < 0.5 × R_full 0.460); H3 passes (R_auth − R_id +0.014 [+0.008, +0.020])'), S('(same, L40 / L48)')],
   [B('But: '), T('the author subspace hardly decodes authors (held-out R² ≤ 0.003; first-author token hit rate 0.078, below the constant baseline 0.080) and moves only about 4% of the full replacement'),
    S('(subspace fits on 5,041 training papers, 5 team folds; x2_report.md)')],
   [B('Remove arm: '), T('setting either component to the mean costs no more than a random subspace (+0.001)'), S('(test, L_S − L_rand; same)')]],
  note=('Reading', 'H3 passes by the pre-registered rule and H2 is not supported, but the author subspace cannot decode authors, so this is no strong evidence for H3. The information carried from the title to the names lies almost entirely outside both subspaces.'),
  notes='X2 只替换子空间（预注册补充 6，2026-11-05 完成）。在 B 的作者提示里只把标题位置状态在某个子空间上的分量换成 A 的：论文属性子空间 S_id（年份、引用数、领域，9 维）在 L40 只搬动 +0.005〔Stage 13 X2，测试集 582 对，R_S（均值比）；随机子空间 +0.003，完整替换 +0.920；381_stage13/reports/x2_report.md Verdict 表〕，作者子空间 S_auth 在 L48 搬动 +0.018〔同上，L48；随机 +0.003，完整替换 +0.428〕。按预注册判据，H3 通过、H2 不支持〔H2：R_id 0.005 &lt; 0.5 × R_full 0.460；H3：R_auth − R_id +0.014 [+0.008, +0.020]，团队聚类 95% CI；同上〕。但作者子空间本身几乎解码不出作者（留出 R² ≤ 0.003〔S_auth 作者映射，5,041 篇训练论文，5 折团队留出 R² 0.0009–0.0033；x2_report.md Subspace fits 表〕，第一作者名字 token 猜中率 0.078〔同表 author top-1〕，低于常数基线 0.080〔同表 majority〕），它搬动的量只有完整替换的约 4%〔0.018 ÷ 0.428〕，因此不能作为 H3 的有力证据。从标题传到作者名字的信息，几乎全部分散在这两个子空间之外。与预注册的出入：X2 的 H3 判定按规则通过，但因子空间本身无解码能力而降级，与 X3 的处理方式相同；S_id 只有 9 维。'.replace('&lt;', '<')))

SLIDES.append(dict(key='pd0', where='end', kind='divider', tag='Added after the defence', title='Added after the defence (2026-11-05)',
  sub='Group comparisons (plan fixed before the results: addenda 7, 8) · CPU leftovers (post-hoc) · experiments still running',
  left=[[T('1. Group comparisons A / B / C / D: three findings, intervention re-runs (numerator / denominator), recognition')],
        [T('2. CPU leftovers on existing data: X5 retrieval curve, M3 scores, N2 by layer, paper vs team intervals, M5')],
        [T('3. In progress (status only): all-token probe (addendum 9), P1 / P2 numerator / denominator by group')]],
  notes='这一部分是答辩（2026-11-02 定稿）之后新增的内容。分组对比是答辩后新增的分析，分析计划在看结果前写定（补充 7、8）；CPU 补充分析是事后分析，只作描述；正在进行的实验只说状态，没有结果。X2 的结果放在 Stage 13 部分。'))

SLIDES.append(dict(key='pd1', where='end', tag='Added after the defence · groups', title='Group comparisons: three findings',
  sub='Plan fixed before the results (addenda 7, 8) · unwritten authors only · output (L63) title-specific signal · within citation bin · team-bootstrap 95% CI · Holm over 4 tests',
  left=[
   [B('1 Recognition: '), T('with no author written (R0), recognised papers (A) beat unrecognised ones (B) by '), B('+0.200 [0.188, 0.213]'),
    S('(P1 A − B, 3,417 / 2,148 papers, Holm p ≤ 0.002; primary.csv)'), T('; with confounders +0.173 [0.161, 0.186]'),
    S('(paper level, 5,565)'), T(', author level + position +0.151 [0.139, 0.163]'), S('(19,893 authors)')],
   [B('2 Graded: '), T('each extra multiple-choice order right adds '), B('+0.059 [0.056, 0.063]'),
    S('(P3, 8,288 R0 papers, bin FE; Holm p ≤ 0.002)'), T(' (confounders +0.046 [0.042, 0.049]'), S('(author level)'),
    T('); ≈ 0.17 with none right, ≈ 0.46 with all four'), S('(R0, 927 / 4,105 papers; stage10_curves.csv)')],
   [B('3 Partial recall helps little (≈ ⅓ of recognition), output only: '), T('C − A co-authors '), B('+0.061 [0.034, 0.090]'),
    S('(P2-other, 390 / 2,826 papers, Holm p ≤ 0.002)'), T(', first author +0.031 [−0.007, 0.069], n.s.'), S('(P2-first, 292 / 3,199)'),
    T('; ≈ 0 at L48–L62 with the logit lens, −0.07 to −0.11 at L48–L59 with the public J-lens'), S('(stage10_contrasts.csv, unwritten_other)'),
    T('. The earlier ≈ +0.11 used all authors (circular)'), S('(r0_r1_analysis.md §2)')],
   [B('Reference only: '), T('R2 written authors +0.844'), S('(200 papers; summary_table.md)'), T('; only 28 R2 papers have unwritten authors'), S('(same)')]],
  img=G + 'fig3_primary_contrasts.png', img_w=400, cap='Primary contrasts (blue) and regression versions; team-bootstrap 95% CI (391_groups/figures/fig3)',
  notes='分组对比，答辩后新增的分析，分析计划在看结果前写定（补充 7、8）。只比较模型没写出的作者，指标是输出层（L63）的标题特异信号（真标题 − 5 个假标题平均）。发现 1，识别的效应：两组都一个作者没写对（R0）时，在模型没写出的作者上，认得出的论文（A）比认不出的论文（B）在输出层的标题特异信号高 +0.200 [0.188, 0.213]〔分组对比 P1 A − B，A 3,417 / B 2,148 篇、10 个引用档，引用档内差，团队聚类 95% CI；Holm 校正后 p ≤ 0.002，受 2,000 次重抽的分辨率限制；391_groups/primary.csv〕。控制领域、年份、作者人数和首字母开头名字的比例后：论文层面 +0.173 [0.161, 0.186]〔5,565 篇；primary.csv〕；作者层面再加作者排位 +0.151 [0.139, 0.163]〔19,893 位作者；primary.csv〕。发现 2，识别程度与信号成梯度关系：在 R0 论文里，多选题 4 种选项顺序中每多答对一次，输出层信号高 +0.059 [0.056, 0.063]〔P3，R0 论文 8,288 篇，引用档固定效应；primary.csv〕；控制混杂后 +0.046 [0.042, 0.049]〔作者层面，30,060 位作者〕。全错时约 0.17，全对时约 0.46〔0 种对 927 篇 0.170、4 种对 4,105 篇 0.463；391_groups/stage10_curves.csv〕；识别不确定的论文落在两组之间。发现 3，写对一部分作者，对没写出的作者的额外帮助较小（约为识别效应的三分之一），而且只出现在最终输出：合作者 +0.061 [0.034, 0.090]〔P2-other C − A，C 390 / A 2,826 篇，Holm p ≤ 0.002；primary.csv〕，第一作者 +0.031 [−0.007, 0.069]，不显著〔P2-first，C 292 / A 3,199 篇；primary.csv〕。logit lens 下 L48–L62 约为 0〔P2-other 按层，logit lens −0.019 到 +0.035，区间都含 0〕；公开 J-lens 下 L48–L59 为 −0.07 到 −0.11〔public J-lens，区间都在 0 以下；391_groups/stage10_contrasts.csv〕。以前用全部作者算出的约 +0.11〔351_stage10/reports/r0_r1_analysis.md §2〕，主要是因为模型已经写出的作者分数本来就高（循环论证）。参照：R2 写出的作者在输出层为 +0.844〔200 篇；391_groups/summary_table.md〕，只作上限参照；R2 里有未写出作者的论文只有 28 篇，不做对比。'))

SLIDES.append(dict(key='pd2', where='end', tag='Added after the defence · re-runs', title='Re-runs: numerator and denominator',
  sub='Addendum 8 · E1 recovery R = mean(patched − false) ÷ mean(true − false) · unwritten authors · team-cluster 95% CI',
  table=(('group (unwritten authors)', 'papers', 'denominator: true − false', 'E1 numerator L48', 'E1 R(L48)', 'E1 R(L52)'),
         [('A  R0 × recognised', '557', '+0.407 [0.386, 0.430]', '+0.330', '+0.811 [0.790, 0.832]', '+0.988 [0.980, 0.996]'),
          ('B  R0 × not recognised', '586', '+0.214 [0.196, 0.234]', '+0.186', '+0.869 [0.835, 0.906]', '+1.016 [1.002, 1.031]'),
          ('U0  R0 × uncertain', '599', '+0.293 [0.271, 0.316]', '+0.248', '+0.844 [0.814, 0.877]', '+1.000 [0.988, 1.012]'),
          ('C  R1 × recognised (descriptive)', '32', '+0.464 [0.388, 0.538]', '+0.335', '+0.721 [0.650, 0.806]', '+0.996 [0.968, 1.026]'),
          ('R2 written authors (reference)', '200', '+0.845 [0.798, 0.897]', '+0.566', '+0.670 [0.630, 0.707]', '+0.948 [0.927, 0.965]')]),
  bottom=[[B('B’s higher ratio is a small-denominator effect: '), T('numerator B − A −0.010, −0.040, −0.144, −0.184 at L24 / L40 / L48 / L52, all CIs below 0'),
           S('(e1_e2_num_den_B_minus_A.csv)'), T(' — B carries no more absolute paper-specific signal than A at any layer.')],
          [B('U0 timing as A and B (descriptive); R2 upper reference only; '), T('C 32 / D 5 / R2-unwritten 28 papers → descriptive'), S('(rerun_report.md Counts)')]],
  notes='补充 8 的干预重跑（R2 × strong 204 篇、R0 × uncertain 600 篇）与 Stage 11 原样本一起，只按模型没写出的作者汇总。E1 恢复比例 R = mean(替换 − 假标题) ÷ mean(真标题 − 假标题)。分母（真标题 − 假标题）：A 0.407、B 0.214、U0 0.293、C 0.464〔E1，未写出作者，最终输出；A 557、B 586、U0 599、C 32 篇；391_groups/reports/e1_num_den.md〕。分子 B − A 在 L24、L40、L48、L52 为 −0.010、−0.040、−0.144、−0.184，区间都在 0 以下〔配对团队 bootstrap；391_groups/summary_rerun/e1_e2_num_den_B_minus_A.csv〕：B 的恢复比例较高（L48 0.869 对 A 0.811〔e1_num_den.md〕）只是因为分母约为 A 的一半（B/A 0.53），B 在任何一层携带的论文特有绝对信号都不比 A 多。U0 的时间点与 A、B 相同（R(L48) 0.844、R(L52) 1.000〔U0 599 篇；rerun_report.md〕，描述）。R2 只作上限参照（写出的作者真假差距 0.845〔R2 写出的作者 200 篇〕）；C 32 篇、D 5 篇、R2 未写出作者 28 篇〔rerun_report.md Counts 表〕只作描述。'))

SLIDES.append(dict(key='pd3', where='end', tag='Added after the defence · groups', title='Recognition changes the size, not the timing',
  sub='Unwritten authors, output (L63) signal, plain means with team-bootstrap 95% CI; n < 30 descriptive',
  img=G + 'fig2_signal_vs_mc.png', img_w=1000, cap='Left: multiple-choice orders right (0–4); right: mean probability of the true option. Blue R0, green R1 (391_groups/figures/fig2)',
  bottom=[[B('Re-runs: '), T('over 0–4 orders right the denominator rises 0.185 → 0.407, while E1 R(L48) stays flat, 0.90 → 0.81'),
           S('(R0 papers A + U0 + B, 241 / 557 papers at 0 / 4; rerun_report.md “Continuous recognition”)')],
          [B('Still being computed: '), T('P1 / P2 numerator and denominator by group (placeholder)')]],
  notes='左图：R0 论文（蓝）未写出作者的输出层信号随多选题答对的选项顺序数从约 0.17 升到约 0.46〔R0 未写出作者，最终输出 L63，简单平均，团队聚类 95% CI；0 种对 927 篇 0.170，4 种对 4,105 篇 0.463；391_groups/stage10_curves.csv；报告图 P5.2〕。干预重跑：从 0 种到 4 种答对，真假标题差距（分母）从 0.185 升到 0.407〔R0 论文 A + U0 + B，E1 分母；0 种对 241 篇、4 种对 557 篇；391_groups/reports/rerun_report.md Continuous recognition 表〕，而 E1 R(L48) 基本持平，从 0.90 到 0.81〔同表 L48 列，0.904 [0.848, 0.965] → 0.811 [0.790, 0.832]〕：识别程度改变信号的大小，不改变时间。P1 / P2 按组的分子 / 分母拆分还在计算，结果出来后补入。'))

SLIDES.append(dict(key='pd4', where='end', tag='Added after the defence · CPU', title='CPU leftovers on existing data (post-hoc)',
  sub='No new GPU runs · descriptive only · not in the pre-registration except the X5 retrieval curve',
  left=[
   [B('X5 retrieval curve (pre-registered, computed now): '), T('top-1 retrieval of the same paper across questions is never above L4'),
    S('(M3 cache, 9,108 papers; x5_retrieval.md)'), T(' (title token 1.000 up to L44, 0.734 at the output)'), S('(same, team CI)')],
   [B('M3 behaviour scores: '), T('year target − control +0.007 [0.003, 0.012]; first-author first token +0.147 [0.096, 0.191]'),
    S('(output, 4,621 / 2,220, within bin, team CI; m3_scores.md)')],
   [B('N2 by layer: '), T('pure name prior target − control +0.047 at the output, +0.039 at logit L62; public J-lens L48 −0.133 (true title)'),
    S('(Stage 12 N2 rescored by layer; n2_layers.md)'), T(' → only L62 reproduces the output pattern')],
   [B('Paper vs team intervals: '), T('width ratio 0.97–1.00 (median); "excludes 0" changes in 2 of 1,155 rows'),
    S('(X1, X4, X6, X7, M3; v42_paper_vs_team.md)')],
   [B('M5 true vs false title at the name positions: '), T('output 0.919; logit L24 0.516 → L62 0.899'),
    S('(share of pairs, all papers × 5 false titles, team CI; m5_report.md)'), T('; probe at title / colon AUROC 0.50–0.52'), S('(same, Part B)')]],
  notes='答辩后补算的 CPU 分析，都用已有数据，属于事后分析，只作描述。X5 预注册的跨任务检索曲线：同一篇论文在三种问法下的标题状态能否在全部论文中检索回自己，没有一层高于 L4〔X5 检索，M3 残差缓存，9,108 篇，top-1，团队聚类 95% CI；381_stage13/reports/x5_retrieval.md〕；标题最后一个 token 上 L44 以前都是 1.000，最终输出 0.734〔同上，[0.725, 0.742]〕。M3 提示下的行为分数：年份 target − control +0.007〔M3 年份分数，最终输出，目标 4,621 / 对照 2,220，引用档内差，团队 CI [0.003, 0.012]；381_stage13/reports/m3_scores.md〕，第一作者首 token +0.147〔同上，[0.096, 0.191]〕，作者差与分组定义有关。N2 按层：纯名字提示 target − control 在最终输出 +0.047〔Stage 12 N2，团队 CI [0.031, 0.062]；371_stage12/reports/n2_layers.md〕，logit lens L62 +0.039〔同上〕；public J-lens L48 真标题下 −0.133〔同上，[−0.161, −0.107]〕，只有 L62 重现输出端的模式。论文与团队区间：宽度比中位数 0.97–1.00〔381_stage13/reports/v42_paper_vs_team.md 第 1 节〕，“区间是否含 0”只在 1,155 行中的 2 行改变〔同上第 2 节〕。M5：名字位置上真标题运行胜过假标题运行的比例，最终输出 0.919〔M5 Part A，全部论文 × 5 个假标题，团队 CI [0.915, 0.924]；381_stage13/reports/m5_report.md〕，logit lens L24 0.516、L62 0.899〔同上〕；标题和 “:” 位置用 probe 区分真/假标题运行，AUROC 0.50–0.52〔同上 Part B〕，基本分不开。'))

SLIDES.append(dict(key='pd5', where='end', tag='Added after the defence · running', title='Still running (status only, no results)',
  sub='Pre-registered before any data (addenda 8 and 9) · X2 is done: see the Stage 13 pages',
  left=[
   [B('All-token probe (addendum 9): '), T('the title-position probe (E4b) so far scores only the FIRST name token, mostly an initial; the new version scores every name token, split into initial / given name / surname')],
   [B('Group re-runs (addendum 8): '), T('E1 / E2 done (previous pages); P1 / P2 numerator / denominator by group being computed')]],
  notes='正在进行，只说状态。全部名字 token 的标题位置 probe（补充 9）：现在的 E4b 只给每位作者名字的第一个 token 打分，73% 的名字以首字母开头〔Stage 11 E4b 打分规则，stage11_analyze.py:163–171；方法手册 E4b 节〕，所以多数时候是首字母；新版本给每个名字 token 打分，按首字母 / 名 / 姓分开。分组重跑（补充 8）：E1、E2 已完成（见前两页）；P1 / P2 按组的分子 / 分母拆分正在计算。X2（补充 6）已完成，结果见 Stage 13 部分。'))


# ================================================================ HTML
def seg_html(segs):
    out = []
    for k, t in segs:
        e = H.escape(t)
        out.append(f'<b>{e}</b>' if k == 'b' else (f'<span class="src">{e}</span>' if k == 's' else e))
    return ''.join(out)


def html_section(sp, img_uri=None):
    if sp.get('kind') == 'divider':
        items = ''.join(f'<li>{seg_html(b)}</li>' for b in sp['left'])
        return (f'<section class="slide lt" aria-label="{H.escape(sp["title"])}"><span class="tag ov">{H.escape(sp["tag"])}</span>'
                f'<h2 style="margin-top:120px;font-size:72px">{H.escape(sp["title"])}</h2><p class="sub" style="font-size:23px">{H.escape(sp["sub"])}</p>'
                f'<ul class="t" style="font-size:24px;list-style:none;padding-left:0;margin-top:30px">{items}</ul><span class="pg"></span></section>\n')
    hd = (f'<section class="slide lt" aria-label="{H.escape(sp["title"])}"><span class="tag">{H.escape(sp["tag"])}</span>'
          f'<h2 style="font-size:52px">{H.escape(sp["title"])}</h2><p class="sub" style="font-size:19px;margin-bottom:12px">{H.escape(sp["sub"])}</p>')
    body = ''
    if sp.get('left'):
        ul = ''.join(f'<li>{seg_html(b)}</li>' for b in sp['left'])
        left = f'<div class="col"><ul class="t" style="font-size:21.5px;line-height:1.32">{ul}</ul></div>'
        right = ''
        if sp.get('img'):
            right = (f'<div style="width:{sp["img_w"]}px;flex:none"><figure class="card"><img alt="{H.escape(sp["cap"])}" src="{img_uri}">'
                     f'<figcaption>{H.escape(sp["cap"])}</figcaption></figure></div>')
        elif sp.get('note'):
            right = (f'<div style="width:300px;flex:none"><div class="note" style="font-size:18px;margin-top:20px"><span class="h">{H.escape(sp["note"][0])}</span>'
                     f'{H.escape(sp["note"][1])}</div></div>')
        body = f'<div class="row" style="gap:22px">{left}{right}</div>'
    elif sp.get('img'):
        body = (f'<div style="width:{sp["img_w"]}px;margin:0 auto"><figure class="card"><img alt="{H.escape(sp["cap"])}" src="{img_uri}">'
                f'<figcaption>{H.escape(sp["cap"])}</figcaption></figure></div>')
    elif sp.get('table'):
        hd_, rows = sp['table']
        th = ''.join(f'<th>{H.escape(c)}</th>' for c in hd_)
        tr = ''.join('<tr>' + ''.join(f'<td>{H.escape(c)}</td>' for c in r) + '</tr>' for r in rows)
        body = f'<table class="tb" style="font-size:17px;width:100%"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'
    if sp.get('bottom'):
        body += ''.join(f'<p style="font-size:18px;line-height:1.3;margin-top:12px">{seg_html(b)}</p>' for b in sp['bottom'])
    return hd + body + '<span class="pg"></span></section>\n'


def slide_text(sp):
    parts = [sp['tag'], sp['title'], sp['sub']]
    for b in sp.get('left', []) + sp.get('bottom', []):
        parts.append(''.join(t for k, t in b))
    if sp.get('table'):
        parts += [' | '.join(r) for r in [sp['table'][0]] + sp['table'][1]]
    return ' '.join(parts)
