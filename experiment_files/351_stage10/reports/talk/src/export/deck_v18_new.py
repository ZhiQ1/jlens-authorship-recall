"""2026-11-05 deck v18: new slides (Stage 12/13 results in full; post-defence section) as one spec -> HTML section + native pptx shapes.
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
SLIDES.append(dict(key='pd0', where='end', kind='divider', tag='Added after the defence', title='Added after the defence (2026-11-05)',
  sub='Group comparisons (plan fixed before the results: addenda 7, 8) · CPU leftovers (post-hoc) · experiments still running',
  left=[[T('1. Group comparisons A / B / C / D: plan and status (results after the re-runs are approved)')],
        [T('2. CPU leftovers on existing data: X5 retrieval curve, M3 scores, N2 by layer, paper vs team intervals, M5')],
        [T('3. In progress (status only): X2 subspace patching, all-token probe, group re-runs')]],
  notes='这一部分是答辩（2026-11-02 定稿）之后新增的内容。分组对比的分析计划在看结果前写定（补充 7、8）；CPU 补充分析是事后分析，只作描述；正在进行的实验只说状态，没有结果。'))

SLIDES.append(dict(key='pd1', where='end', tag='Added after the defence · groups', title='Group comparisons: plan and status',
  sub='Plan fixed before any result (addenda 7, 8) · results go to the user and advisor first; not shown until approved',
  left=[
   [B('Groups: '), T('open answer R0 / R1 / R2 × multiple-choice recognition strong / uncertain / fail; A = R0 × strong 4,110, B = R0 × fail 2,186, C = R1 × strong 511, D = R1 × fail 34'),
    S('(cohort papers.parquet; addendum 7)')],
   [B('No circularity: '), T('every comparison uses only the authors the model did NOT write; written authors are a reference column')],
   [B('Primary tests: '), T('P1 recognition A − B; P2 partial recall C − A (first author / co-authors); P3 slope on orders right (0–4) in R0; within citation bin, team bootstrap, Holm over 4; confounder regressions beside each')],
   [B('Status: '), T('CPU part computed and sent for review. Still running: intervention re-runs for R2 × strong (204 papers) and R0 × uncertain (600), and the E1 numerator / denominator by group'),
    S('(addendum 8; rerun_R2.parquet, rerun_U0_600.parquet)')]],
  note=('Why no numbers here', 'User decision 2026-11-05: group results appear in the deck and report only after the re-runs and the E1 numerator / denominator are in and approved.'),
  notes='分组对比（答辩后新增）：分析计划在看结果前写定（补充 7、8）。分组按开放回答（R0 / R1 / R2）× 多选识别（strong / uncertain / fail）交叉：A = R0 × strong 4,110 篇，B = R0 × fail 2,186，C = R1 × strong 511，D = R1 × fail 34〔351_stage10/cohort/papers.parquet，recall_level × mc_team_outcome_tight；补充 7 “groups”〕。为避免循环论证，所有比较只用模型没写出的作者。三个主要检验：P1 识别的效应 A − B，P2 写对一部分作者的额外帮助 C − A（第一作者 / 合作者分开），P3 R0 论文的信号对多选题答对顺序数的斜率；引用档内比较、按作者团队重抽、Holm 校正 4 个检验，并各做控制混杂的回归。状态：CPU 部分已算完，结果先交用户和导师审阅；R2 × strong（204 篇）和 R0 × uncertain（600 篇）的干预重跑以及 E1 分子/分母按组拆开还在进行。按用户 2026-11-05 的决定，确认之前不在讲稿和报告里给结果数字。'))

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
  sub='All pre-registered before any data: addenda 6, 8 and 9 (sha256 in the report)',
  left=[
   [B('X2 subspace patching (addendum 6): '), T('subspaces fitted; GPU shard 0 of 24 done and checked; the rest is queued behind the group re-runs')],
   [B('All-token probe (addendum 9): '), T('the title-position probe (E4b) so far scores only the FIRST name token, mostly an initial; the new version scores every name token, split into initial / given name / surname. GPU data step (~1 A100-hour) queued after the re-runs and X2')],
   [B('Group re-runs (addendum 8): '), T('E1 / E2 (and P1 / P2 for R2) for R2 × strong and R0 × uncertain; E1 numerator / denominator by group')]],
  notes='正在进行，只说状态。X2 子空间替换（补充 6）：子空间已拟合，24 个 GPU 分片中第 0 个已完成并通过检查，其余排在分组重跑之后。全部名字 token 的标题位置 probe（补充 9）：现在的 E4b 只给每位作者名字的第一个 token 打分，73% 的名字以首字母开头〔Stage 11 E4b 打分规则，stage11_analyze.py:163–171；方法手册 E4b 节〕，所以多数时候是首字母；新版本给每个名字 token 打分，按首字母 / 名 / 姓分开，主要问题是姓的第一个 token 在 L40 是否有标题特异信号；需要约 1 个 A100 小时的 GPU 数据步骤，排在分组重跑和 X2 之后。分组重跑（补充 8）：R2 × strong 和 R0 × uncertain 的 E1、E2（R2 另加 P1/P2），以及 E1 分子/分母按组拆开。'))


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
