# -*- coding: utf-8 -*-
"""Spec for tagging the Chinese speaker notes (deck v17 -> v18).
FIXES: key -> list of (old, new) applied to the original text first (listed in notes_issues.md).
TAGS:  key -> list of (anchor, tag). Anchors are searched in order from a moving cursor; the tag
       〔tag〕 is inserted right after the anchor. Paths are relative to /scratch/zhang.zhiqi2/jlens/."""

CAVEAT = ('注意：这个 probe 只给每位作者名字的第一个 token 打分（73% 的名字以首字母开头，多数时候是首字母）；'
          '给全部名字 token 打分、按首字母/名/姓分开的版本按补充 9 进行中，尚无结果。')
CAVEAT_NOTES = ['23', '24', '27', '30', '38', '39', '58', '66']

# ---------------------------------------------------------------- common source strings
SPEC = '真标题 − 5 个假标题平均'
TC = '引用档内 目标−对照（共有引用档 目标 3,734 + 对照 2,182 篇）'
BOOT = '论文 bootstrap 95% CI'
F_B_SPEC = '351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'
F_A_SPEC = '351_stage10/summary_title/A_group_layer.csv'
F_CELLS = '351_stage10/cohort/papers.parquet recall_level × mc_team_outcome_tight（method_figs/cohort_cells.csv）'
T_CELLS = f'标注包分组，9,108 篇按开放回答 recall_level × 多选 mc_team_outcome_tight 计数；{F_CELLS}；报告 Stage 1 分组表'
T_N9108 = '标注包全部论文 = Stage 10 全量队列；351_stage10/cohort/papers.parquet；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/paper_labels_with_papers.csv'
T_N149999 = 'Stage 10 冻结队列，33,811 个作者上下文的名字 token 总数；351_stage10/cohort/name_tokens.parquet；351_stage10/config/manifest.json'
T_SMALLN = ('Stage 4 Benchmark20 20 篇、Pilot50 50 篇（Stage 5–7）、Stage 8 新论文 200 篇；351_all/351_stage4_readout.log、'
            '351_stage5_crossed_v2/cohort/pilot50_v1.csv、351_stage8/cohort/stage8_papers.csv')
T_R0 = ('Stage 10 只用 R0（A 对 B），' + SPEC + '，最终输出 L63，引用档内 目标−对照，A 3,423 + B 2,151 篇，'
        '+0.199 [0.188, 0.212]，' + BOOT + '；报告 §6.13 表；351_stage10/reports/r0_sensitivity.md；351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv')
T_POOL = ('Stage 10 合并口径（target = A + C 对 control = B + D），' + SPEC + '，最终输出 L63，' + TC +
          '，+0.207 [0.196, 0.220]，' + BOOT + '；报告 §6.4 表；' + F_B_SPEC)
T_R1SHARE = '目标组 R1 511 / 4,621 篇 = 11%，对照组 R1 34 / 2,220 篇 = 1.5%；351_stage10/reports/r0_sensitivity.md 第一张表；351_stage10/reports/r0_r1_analysis.md §0'
T_N593 = 'Stage 11 抽样，10 个可比引用档内配平，目标 593 + 对照 593 = 1,186 篇；361_stage11/config/sample.parquet；361_stage11/config/protocol.json'
T_K5 = 'Stage 10 标题条件设计：每篇 5 个匹配假标题（false_0–false_4）加删去标题；351_stage10/config/conditions_manifest.json'
T_E1 = lambda v: ('Stage 11 E1 替换，真标题→false_0，标题之后全部位置，最终输出名字 token 恢复比例（均值比），目标 593 + 对照 593 篇，'
                  + v + '；报告 §6.11 恢复比例图；361_stage11/summary/E1_recovery.csv（group=all）')
T_E2 = lambda v: ('Stage 11 E2 阻断，标题之后全部位置从第 l 层起不能注意标题，最终输出损失比例（÷ 真标题 − false_0 差距），1,186 篇，'
                  + v + '；报告 §6.11 阻断图；361_stage11/summary/E2_knockout.csv（group=all）')
T_P1 = ('Stage 12 P1 逐位置替换，真标题→false_0，最终输出名字 token 恢复比例，Stage 11 样本 1,186 篇：只换名字位置 L48 0.61、L52 0.847，'
        '单个位置最大为 “:” L52 0.172 [0.156, 0.187]；报告 Stage 12 节 P1 表；371_stage12/summary/P1_patch_pos.csv')
T_X6 = ('Stage 13 X6，用 5 个假标题分别做 Stage 11 E1 替换，全部 1,186 篇，5 个假标题平均 R：L24 0.080、L40 0.302、L48 0.821、L52 0.995，'
        '团队聚类 95% CI；报告 Stage 13 X6 节；381_stage13/reports/x6_report.md（all 表 average 列）')
T_E4B_RECHECK_ALL = ('Stage 13 E4b 复核，标题最后一个 token 上的线性 probe，probe 只打分每位作者名字的第一个 token，真标题 − false_0，'
                     '按作者团队分折 + 剔除标题复用 + 训练折内标准化，全部 1,863 篇：L24 +0.050、L40 +0.061、L56 +0.075（L24–L60 为 +0.047 到 +0.080），'
                     + BOOT + '；报告 §6.11；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第一张表')
T_E4B_RECHECK_TC = ('同上 E4b 复核，probe 只打分第一个名字 token，引用档内 目标−对照，目标 896、对照 499 篇，L24–L60 为 +0.035（L44）到 +0.078，'
                    + BOOT + '；报告 §6.11；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第二张表')
T_E4B_N = ('Stage 13 E4b 复核样本，按作者团队分折并剔除 probe 训练时见过同一标题的论文后剩 1,863 篇（目标 896、对照 499、excluded 433、guard 35）；'
           '381_stage13/reports/e4b_split_compare.md；381_stage13/summary_cpu_trainstd/E4b_4configs.csv')
T_E4_LENS = ('Stage 11 E4，标题最后一个 token，logit lens 与 public J-lens 读第一个名字 token，' + SPEC +
             '，全部 9,108 篇，约 0.01–0.03；报告 §6.11 标题位置表；361_stage11/summary/E4_titlepos_lens.csv')
T_X3_EXTRA = ('Stage 10 补充 X3，三种 Jacobian lens 减 logit lens 的标题特异信号（' + SPEC + '），L24–L48，全部 9,108 篇，'
              '+0.007 到 +0.030，' + BOOT + ' 均在 0 以上；报告 §6.9 表；351_stage10/summary_extra/X3_pairwise.csv')
T_044 = ('Stage 10，' + SPEC + '，L62，全部 9,108 篇均值，三种 Jacobian lens 0.436–0.444（public 0.442）；报告 §6.9 表；351_stage10/summary_extra/X3_means.csv')
T_X2 = ('Stage 10 补充 X2，标题特异信号（' + SPEC + '，最终输出 L63）对 log10(引用数+1) 的 Spearman ρ，全部 9,108 篇 0.451 [0.433, 0.467]，'
        'bootstrap 95% CI；报告 §6.8 表；351_stage10/summary_extra/X2_spearman.csv')
T_PRIOR3 = ('Stage 12 名字先验拆解（CPU），最终输出 L63，全部名字 token，引用档内 目标−对照（目标 4,621、对照 2,220 篇）：先验 +0.087 [0.070, 0.103] ÷ 真标题差 +0.247 = 0.35；'
            '报告 §6.12 第二张表；371_stage12/summary_cpu/A_prior_decomposition.csv')
T_PRIORSUR = ('同上，姓的第一个 token，先验 目标−对照 +0.022 [−0.019, +0.063]，论文特有 +0.423 [0.393, 0.454]；报告 §6.12 第二张表；371_stage12/summary_cpu/A_prior_decomposition.csv')
T_FINE = ('Stage 10 主轮 + 细层扩展，' + SPEC + '，logit lens，' + TC + '：L50 +0.007 [0.001, 0.014]、L52 +0.018、L54 +0.030、L56 +0.065、'
          'L58 +0.114、L60 +0.178、L62 +0.229，' + BOOT + '；报告 §6.10 图与表；' + F_B_SPEC)
T_PUB57 = ('同上，public J-lens：L48–L54 为 −0.02 到 −0.05，L57 起转正 +0.029 [0.009, 0.048]，L61 +0.207；报告 §6.10 图与表；' + F_B_SPEC)
T_SPEC_TC_LATE = ('Stage 10，' + SPEC + '，' + TC + '，L62 四种读出 +0.228 到 +0.231，最终输出 L63 +0.207 [0.196, 0.220]，' + BOOT +
                  '；报告 §6.4 表；' + F_B_SPEC)
T_E2N = ('Stage 11 E2n，只阻断 “:” 和名字位置对标题的注意力，从 L0 起，最终输出损失比例，1,186 篇，0.153 [0.136, 0.172]；报告 §6.11 阻断图虚线；361_stage11/summary/E2n_knockout.csv')
T_P2 = ('Stage 12 P2，标题之后全部位置只替换单层 attention 或 MLP 输出，最终输出恢复比例，1,186 篇：attention L48 0.231（MLP 0.07），MLP L52 0.178、L56 0.224；'
        '报告 Stage 12 节 P2 表；371_stage12/summary/P2_patch_comp.csv')
T_71 = ('Stage 4，J-Lens L56，第一作者首 token 倒数名次，20 篇，最大单篇占总和 71.03%；351_all/351_stage4_artifacts/audit/audit_report.md 表 1 行 L56；报告 Stage 4 节')
T_8D_TAIL = ('Stage 8D RQ2，J-Lens L56 金标准胜率匹配 A−B，100 对，均值 +4.98 pp，按 A−B 降序去掉前 10 对后其余 90 对均值 −0.39 pp（事后诊断）；'
             '351_stage8/stage8D/summary/matched_pair_differences.csv（mode=jlens_L56）重算；报告 Stage 8D 节')
T_46 = ('Stage 7.2，Pilot50 每篇 100 个错误名字（50 匹配 + 50 随机），共 5,000 个；每篇平均 45.76 个不同首 token（方法手册 C 部分由 351_stage7_2/candidates/pilot50_author_candidates.csv 统计）；'
        '156 / 5,000 = 3.1% 与金标准首 token 相同记为平局（351_stage7_2/summary/quality.json）')
T_255 = ('标注包自检，0-2 引用档 796 篇，收紧规则（4/4 且真选项平均概率 ≥ 0.5）多选通过率 25.5%（普通规则 38.6%）；'
         'labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 第 8 行')
T_93 = ('Stage 7.3，J-Lens L56，真标题胜率 − 20 个错误标题平均胜率，合并池，Pilot50 50 篇均值 +0.0934 [0.047, 0.139]（2026-10-30 重算区间，B = 20,000），35/50 篇为正；'
        '351_stage7_3/summary/paper_null_distribution.csv（pool=combined, mode=jlens_L56）；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv；报告 Stage 7.3 节')
T_52 = ('Stage 8D RQ1，J-Lens L56，真标题 − 20 个匹配错误标题，200 篇新论文，+5.18 pp [2.93, 7.48]，' + BOOT +
        '；351_stage8/stage8D/summary/primary_questions.csv 行 RQ1_L56_replication；报告 Stage 8D 节')
T_50AB = ('Stage 8D RQ2，J-Lens L56 匹配 A − B，100 对，+4.98 pp [0.32, 9.91]，配对 bootstrap 95% CI；351_stage8/stage8D/summary/primary_questions.csv 行 RQ2_matched_A_minus_B')
T_E4B_ORIG_TGT = ('Stage 11 E4b 原始版（论文分折、未剔除标题复用），标题最后一个 token 上的 probe，probe 只打分第一个名字 token，真标题 − false_0，'
                  '目标组 L16 +0.043 到 L52–L56 +0.080/+0.082；' + BOOT + '；报告 §6.11 标题位置表 probe 行；361_stage11/summary/E4_probe.csv 列 spec_target')
T_X7 = ('Stage 13 X7，S = T − F（真标题运行的阻断损失减去 false_0 运行的同样阻断），÷ 真 − 假差距，全部 1,186 篇：L0 1.004、L24 0.873、L40 0.293、L48 0.143、'
        'L52 0.029（target 0.018、control 0.051），团队聚类 95% CI；报告 Stage 13 X7 表；381_stage13/reports/x7_report.md；381_stage13/summary_x7/x7_knockout.csv')

FIXES = {
    '38': [('目标组比对照组高 0.04 到 0.08', '目标组比对照组高 0.03 到 0.08')],
    '56': [('从 0.45 降到 0.26', '从 0.42 降到 0.26')],
    '66': [('目标组高 +0.04 到 +0.08', '目标组高 +0.03 到 +0.08')],
}

TAGS = {
'1': [
    ('20、50、200 篇小样本', T_SMALLN),
    ('全部 9,108 篇论文', T_N9108),
    ('149,999 个名字 token', T_N149999),
],
'3': [
    ('小样本阶段用 50 和 200 篇论文', 'Pilot50 50 篇（351_stage5_crossed_v2/cohort/pilot50_v1.csv）、Stage 8 新论文 200 篇（351_stage8/cohort/stage8_papers.csv）'),
    ('1 个或 100 个错误名字', 'Stage 5 交叉对照每篇 1 个来源论文作者；Stage 7.2 每篇 50 个匹配 + 50 个随机错误作者；351_stage7_2/summary/quality.json；~/jlens_work/07_2_stage7_2/351_stage7_2.py:62-111'),
    ('1 个交叉标题或 20 个打乱标题', 'Stage 5 每篇 1 个交叉标题；Stage 7.3 / Stage 8 每篇 20 个元数据匹配的错误标题；~/jlens_work/07_3_stage7_3/351_stage7_3.py:83-91；351_stage8/config/stage8B_manifest.json'),
    ('全部 9,108 篇', T_N9108),
    ('5 个匹配假标题', T_K5),
],
'4': [
    ('A = 4,110、B = 2,186、C = 511、D = 34', T_CELLS),
    ('511 篇 R1', T_CELLS),
    ('输出处的差是 +0.199', T_R0),
    ('合并口径是 +0.207', T_POOL),
],
'6': [
    ('9,108 篇论文', T_N9108),
    ('R0（一个真作者都没写对）8,298 篇、R1 596 篇、R2（基本写出了作者）214 篇', T_CELLS + '；R0/R1/R2 = 8,298 / 596 / 214'),
    ('R2 为 204、9、1', T_CELLS + '；R0 4,110/2,002/2,186，R1 511/51/34，R2 204/9/1（strong/uncertain/fail）'),
    ('target = A + C = 4,621，control = B + D = 2,220', '351_stage10/cohort/papers.parquet 列 group_tight；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 第 7 行'),
    ('全部 9,108 篇', T_N9108),
    ('593 + 593 = 1,186 篇', T_N593 + '（361_stage11.py:56, 109–115）'),
    ('1,178 对', 'Stage 13 X 系列配对，1,186 篇中有合格配对论文的 1,178 篇；381_stage13/config/pairs.parquet'),
],
'7': [
    ('9,108 篇论文', T_N9108 + '；351_all/351_audit.json "total"'),
    ('冻结了 6,841 篇', 'Stage 1 分析队列 = A + B + C + D 四组；351_all/351_audit.json "four_group_total"；00_cohort/351_prepare_all.py'),
    ('4 种选项顺序全对，并且真选项的平均概率至少 0.5', '标注规则 group_tight（tightened: min_orders 4, min_p_true 0.5）；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/rules.yaml、label_README.md'),
    ('4 次里最多对 1 次', '同上 rules.yaml，control = 4 种顺序中至多 1 次答对'),
    ('严格通过率有 25.5%', T_255),
    ('原计划的 10% 上限', 'Stage 1 预设的标签质量门槛（0-2 档通过率 ≤ 10%）；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 第 8 行；报告 Stage 1 节'),
],
'8': [
    ('revision 9216db57，64 层，隐藏维度 5,120', 'Qwen3-32B 配置；351_stage6/config/protocol.json、351_stage6/config/runtime.json；hidden_size 5120 见 HF config.json'),
    ('L16 到 L62 共 7 层', 'Stage 2 读出层 L16、24、32、40、48、56、62；351_stage6/config/protocol.json；~/jlens_work/05_stage5/351_stage5.py'),
    ('超过 0.1', '守卫阈值；~/jlens_work/05_stage5/351_stage5.py:205-206；~/jlens_work/04_stage4/351_stage4_readout.py:86-89'),
],
'9': [
    ('HR2 不超过 0.5', '标注规则 recall_failure_threshold 0.5；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/rules.yaml、step1_README.md'),
    ('另外 3 篇论文', '多选题 4 个选项 = 真团队 + 3 个干扰团队；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/step1_README.md；mc_team.jsonl'),
    ('问 4 种顺序', '顺序 ABDC、BCAD、CDBA、DACB；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/step1_README.md'),
    ('平均总和 1.00', '标注包 mc_results.jsonl，kind=team，36,432 次：字母概率和均值 0.998，最小 0.142，低于 0.5 的只有 3 次（同一篇论文）；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 检查行'),
    ('4 次全对且真字母平均概率至少 0.5', '标注规则 group_tight（min_orders 4, min_p_true 0.5）；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/rules.yaml'),
    ('最多对 1 次', '同上 rules.yaml，control = 至多 1/4'),
],
'10': [
    ('5 个匹配的假标题', T_K5),
],
'11': [
    ('972 个重叠 token', 'Stage 10 与 Stage 6 交叉核对，13 组读出×层各 972 个 token，名次完全相同比例 76.5–95.5%；351_stage10/reports/crosscheck_stage6.csv'),
    ('从 0.25 放宽到 0.5', 'Stage 10 parity，12 个上下文、52 个位置，最大 |logit 差| 0.156–0.367（final@L63 0.367）；351_stage10/reports/parity.json tolerance_amendment；351_stage10/config/analysis_plan.json amendments'),
],
'13': [
    ('全部 50 篇论文上', 'Pilot50；351_stage5_crossed_v2/cohort/pilot50_v1.csv'),
    ('L56 为 +1.17 [0.53, 1.84]，L62 为 +1.08 [0.36, 1.82]', 'Stage 5，J-Lens，交叉对比（G 对 F 的 logit 差在两种标题下的变化），50 篇，论文 bootstrap 95% CI：L56 +1.167 [0.533, 1.838]、L62 +1.077 [0.363, 1.816]；报告 Stage 5 节图 5.1 左；351_stage5_crossed_v2/summary/layer_summary.csv 行 group=ALL'),
    ('20 对 A/B 匹配的 7 层积分只有 +0.08 [−0.43, +0.65]', 'Stage 5，J-Lens 7 层积分，匹配 A − B，20 对，+0.081 [−0.426, +0.648]，配对 bootstrap 95% CI；报告 Stage 5 节图 5.1 右；351_stage5_crossed_v2/summary/matched_ab_summary.csv 行 layer=integrated'),
],
'14': [
    ('20 个元数据匹配的错误标题，共 1,000 个上下文', 'Stage 7.3 设计，50 篇 × 20 个替代标题；~/jlens_work/07_3_stage7_3/351_stage7_3.py:83-91；351_stage7_3/reports/freeze_audit.md'),
    ('全部 50 篇合并', 'Pilot50 50 篇；351_stage7_3/summary/paper_null_distribution.csv'),
    ('真标题 0.616 对错误标题平均 0.523', 'Stage 7.3，J-Lens L56，金标准首 token 胜率，合并池，50 篇均值：真标题 0.6160、20 个错误标题平均 0.5226；351_stage7_3/summary/paper_null_distribution.csv（pool=combined, mode=jlens_L56）列 true_win、null_mean'),
    ('高 +9.3 个百分点 [4.7, 13.9]，50 篇里 35 篇为正', T_93),
    ('在 +8.6 到 +10.0 之间', 'Stage 7.3，J-Lens L56 标题优势，50 篇逐一留出一篇后的均值范围 +8.64 到 +9.99 pp；351_stage7_3/recompute_2026-10-30/stage7_l56_loo.csv'),
    ('Vanilla 在 L56 为 +10.6，最终输出 +7.2', 'Stage 7.3，Vanilla L56 / 最终输出 L63，真标题胜率 − 20 个错误标题平均，合并池，50 篇均值 +0.1063 / +0.0716；351_stage7_3/summary/paper_null_distribution.csv（mode=vanilla_L56、final_L63）'),
    ('+0.018 [−0.021, +0.063]', 'Stage 7.3，J-Lens 7 层积分标题优势的匹配 A − B，合并池，20 对，+0.0177 [−0.0211, +0.0626]，配对 bootstrap 95% CI；351_stage7_3/summary/integrated_ab_bootstrap.csv 行 jlens/combined'),
],
'15': [
    ('1,000 个错误标题里有 199 个', 'Stage 7.3，199/1,000 个替代标题的来源论文作者在错误作者池中；351_stage7_3/summary/quality.json'),
    ('从 +0.026 变为 +0.028', 'Stage 7.3，J-Lens 7 层积分标题优势，合并池，50 篇均值 +0.0262 → 剔除重叠后 +0.0283；351_stage7_3/summary/paper_null_distribution.csv 列 title_advantage / advantage_no_source_false_overlap（方法手册重算）'),
    ('合并效应在 +0.026 到 +0.032 之间', 'Stage 7.3，J-Lens 7 层积分标题优势，作者加权 / 唯一 token / 去平局 +0.026 / +0.032 / +0.027，50 篇；351_stage7_3/recompute_2026-10-30/stage7_weighting_title_advantage.csv'),
    ('六个 A−B 区间都含 0', 'Stage 7.3，3 种加权 × J-Lens/Vanilla 的 7 层积分匹配 A − B，20 对，配对 bootstrap 95% CI；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 16–27'),
    ('6 篇论文 L56 为 +0.22，6 篇里 5 篇为正', 'Stage 7.4 低引用分析，J-Lens L56 标题优势，0-2 档 6 篇，均值 +0.224，5/6 为正，0 篇超出自身 20 个错误标题的 5% 尾部；351_stage7_4/summary/floor_L56_low_six.csv；351_stage7_4/summary/overview.json "floor_low_six_L56"'),
    ('20 个错误标题的尾部', 'Stage 7.3 每篇 20 个替代标题；~/jlens_work/07_3_stage7_3/351_stage7_3.py:83-91'),
    ('L56 为 +0.11，L32 却为 −0.03（区间在 0 以下）', 'Stage 7.3，J-Lens 单层标题优势的匹配 A − B，合并池，20 对，配对 bootstrap 95% CI：L56 +0.113 [−0.005, +0.225]，L32 −0.032 [−0.058, −0.006]；351_stage7_3/summary/matched_ab_bootstrap.csv 行 jlens_L56 / jlens_L32 combined'),
],
'16': [
    ('200 篇新论文（100 对 A/B）', 'Stage 8A 抽样，100 对匹配 A/B；351_stage8/cohort/stage8_papers.csv；351_stage8/summary/matching_audit.json'),
    ('真标题相对 20 个假标题的胜率高 +5.18 个百分点 [2.93, 7.48]', T_52),
    ('+2.33 [1.50, 3.19]', 'Stage 8 冻结计划主终点，J-Lens 7 层积分，真标题 − 20 个错误标题平均，200 篇，+2.33 pp [1.50, 3.19]，' + BOOT + '；351_stage8/recompute_2026-10-30/s8_endpoints.csv'),
],
'17': [
    ('在 200 篇全新论文上', 'Stage 8 新论文；351_stage8/cohort/stage8_papers.csv'),
    ('RQ1 标题效应 +5.18 个百分点 [+2.93, +7.48]', T_52),
    ('RQ2 的 A−B 为 +4.98 [+0.32, +9.91]', T_50AB),
    ('RQ3 低引用减高引用为 +2.45，区间含 0', 'Stage 8D RQ3，J-Lens L56，配对平衡的低引用 − 高引用，50 对，+2.45 pp [−3.69, +8.60]；351_stage8/stage8D/summary/primary_questions.csv 行 RQ3_low_minus_high'),
    ('J-Lens 减 Vanilla 为 −1.38，区间含 0', 'Stage 8D，L56 J-Lens − Vanilla 标题优势，200 篇，−1.38 pp [−3.48, +0.68]，' + BOOT + '；351_stage8/stage8D/summary/jlens_minus_vanilla.csv'),
    ('低档 +6.8，中档 +4.8，高档 +4.4', 'Stage 8D，J-Lens L56 标题优势按引用带，低 50 / 中 100 / 高 50 篇：+6.83 / +4.75 / +4.38 pp；351_stage8/stage8D/summary/layer_and_band_summary.csv（mode=jlens_L56, scope=citation_band）'),
],
'18': [
    ('100 对里 55 对为正、45 对为负，中位数 +4.4 个百分点', 'Stage 8D RQ2，J-Lens L56 匹配 A − B，100 对：55 正 / 45 负，中位数 +4.41 pp；351_stage8/stage8D/summary/primary_questions.csv 行 RQ2_matched_A_minus_B；matched_pair_differences.csv（mode=jlens_L56）'),
    ('大约 +84', 'Stage 8D RQ2，最大一对 S8P094 A − B = +84.4 pp；351_stage8/stage8D/summary/matched_pair_differences.csv（mode=jlens_L56）'),
    ('去掉最大的 5 对后降到 +1.9', 'Stage 8D RQ2，按 A − B 降序去掉前 5 对后其余 95 对均值 +1.90 pp（事后诊断，方法手册 C 部分重算）；351_stage8/stage8D/summary/matched_pair_differences.csv（mode=jlens_L56）'),
    ('去掉 10 对后变成 −0.4', T_8D_TAIL),
],
'19': [
    ('7 个提示后面', 'Stage 10 标题条件：真标题、5 个匹配假标题（false_0–false_4）、删去标题；351_stage10/config/conditions_manifest.json'),
    ('83、2、25、1、61、1、1', 'Stage 10，示例论文 Coifman 等（2007），第一作者 7 个 token，真标题，最终输出 L63 全词表名次；351_stage10/raw/final/L63/shard_011.npz 行 25025–25031；351_stage10/reports/method_figs/coifman_layer_ranks.csv（condition=true, readout=final）'),
    ('对 16 个 token 求平均', '示例论文 3 位作者共 16 个名字 token；351_stage10/raw/final/L63/shard_011.npz 行 25025–25040'),
    ('真标题 −0.7190，5 个假标题平均 −1.1126，删去标题 −0.8808', 'Stage 10，示例论文，最终输出 L63，16 个名字 token 的平均 log10(1/名次)；方法手册 A_global1 G5.5（351_stage10/reports/methods/parts/A_global1.html）；351_stage10/summary_title/paper_title_contrasts.parquet（readout=final, layer=63）'),
    ('total = 真 − 删 = +0.1618，topic = 假 − 删 = −0.2318', '同上，示例论文 spec +0.3935、total +0.1618、topic −0.2318；方法手册 A_global1 G5.5；351_stage10/summary_title/paper_title_contrasts.parquet（readout=final, layer=63）'),
],
'20': [
    ('13 个引用档', 'Stage 10 引用档 0-2 … 4097+ 共 13 档；~/jlens_work/10_stage10/351_stage10.py；351_stage10/summary_extra/X2_by_bin.csv'),
    ('各至少 30 篇的档', '设计常数 MIN_STRATUM = 30；~/jlens_work/10_stage10/351_stage10.py:642；351_stage10/config/analysis_plan.json'),
    ('主分析 10 档', '满足每组 ≥ 30 篇的 10 个引用档，共有引用档 目标 3,734 + 对照 2,182 篇；' + F_B_SPEC),
    ('该档 target 441 篇、control 165 篇', 'Stage 10 队列 group_tight × citation_bin，65-128 档；351_stage10/cohort/papers.parquet'),
    ('9,108 篇共 7,247 个团队', 'Stage 13 团队划分（共享任一作者全名的论文并成一组），9,108 篇 7,247 组；381_stage13/reports/cluster_ci.md 第 3 行；~/jlens_work/13_stage13/stage13_cpu.py group_folds'),
],
'21': [
    ('大约是对照组的两倍', 'Stage 10，' + SPEC + '，最终输出 L63 各组均值：目标 4,621 篇 0.481，对照 2,220 篇 0.200（比值约 2.4）；报告 §6.3 图；' + F_A_SPEC),
],
'22': [
    ('排在第 12 名左右', 'Stage 12 名字先验（CPU），不给标题，最终输出 L63，全部 9,108 篇、全部名字 token，平均 log10(1/名次) −1.089 ≈ 第 12.3 名；报告 §6.12；371_stage12/summary_cpu/A_prior_decomposition.csv（all_tokens/all）'),
    ('从大约第 146 名提到第 24 名', 'Stage 12 A，姓的第一个 token，目标 4,621 篇，平均 log10(1/名次) 不给标题 −2.164（≈ 第 146 名）→ 真标题 −1.380（≈ 第 24 名）；报告 §6.12 第一张表；371_stage12/summary_cpu/A_prior_decomposition.csv'),
    ('约 0.09 在不给标题时就已存在', 'Stage 12 A，全部名字 token，最终输出 L63，引用档内 目标−对照（目标 4,621、对照 2,220 篇）：先验 +0.087 [0.070, 0.103]；报告 §6.12 第二张表；371_stage12/summary_cpu/A_prior_decomposition.csv'),
    ('假标题再抵消 0.05，剩下 0.21 是这篇论文特有的', '同上：主题（假标题 − 不给标题）−0.047 [−0.055, −0.038]，论文特有（真 − 假）+0.207 [0.195, 0.220]，' + BOOT + '；报告 §6.12 第二张表；371_stage12/summary_cpu/A_prior_decomposition.csv'),
    ('先验部分约为 0，论文特有部分为 0.42', T_PRIORSUR),
    ('Spearman 0.09，论文特有部分为 0.33', 'Stage 12 B，R0/R1 论文 8,894 篇，引用档内中心化后与多选题答对顺序数（0–4）的 Spearman：先验 +0.085 [0.063, 0.106]，论文特有 +0.329 [0.312, 0.346]；371_stage12/reports/stage12_cpu_report.md B；371_stage12/summary_cpu/B_prior_vs_recognition.csv'),
],
'23': [
    ('5 折岭回归', 'Stage 11 E4b / Stage 13 复核设计：5 折、按作者团队分折，α ∈ {0.1, 1, 10}；~/jlens_work/10_stage10/stage10_extra_r0r1.py probe()；381_stage13/reports/e4b_trainstd_compare.md'),
    ('L40 为 +0.061 [0.047, 0.076]', 'Stage 13 E4b 复核，标题最后一个 token 上的 probe，probe 只打分第一作者名字的第一个 token，真标题 − false_0，按作者团队分折 + 剔除标题复用 + 训练折内标准化，全部 1,863 篇，L40 +0.061 [0.047, 0.076]，' + BOOT + '；报告 §6.11；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 表 L40 行 new 列'),
    ('从 L16 的 0.38 升到 L52 的 0.56', 'Stage 13 M2，真标题，标题最后一个 token，年份岭回归 R²，9,108 篇：L16 0.383 → L52 0.561，团队整群 95% CI；报告 Stage 13 M2 节；381_stage13/reports/m2_teamci.md 第 46、86 行'),
],
'25': [
    ('从 0–2 档的 +0.35 升到 4097+ 档的 +0.64', 'Stage 10，' + SPEC + '，最终输出 L63，目标组各引用档均值：0-2 档 +0.347（200 篇）→ 4097+ 档 +0.644 [0.591, 0.701]（84 篇），' + BOOT + '；报告 §6.8 图与表；351_stage10/summary_title/A_group_bin_layer.csv（readout=final）；351_stage10/summary_extra/X2_by_bin.csv'),
    ('全部 0.45', T_X2),
    ('目标组内 0.33，对照组内 0.19', '同上 X2，组内 Spearman ρ：目标 4,621 篇 0.328，对照 2,220 篇 0.187；读出水平只有 0.181 / 0.084；报告 §6.8 表；351_stage10/summary_extra/X2_spearman.csv'),
],
# '26' intentionally untagged: post-defence group-comparison numbers (391_groups) must not appear yet; note kept unchanged.
'27': [
    ('目标组里 11% 是 R1，对照组里只有 1.5%', T_R1SHARE),
    ('输出处为 +0.199', T_R0),
    ('合并口径为 +0.207', T_POOL),
    ('R1 目标论文对 R0 对照为 +0.37', 'Stage 10，R1 目标（C）对 R0 对照（B），' + SPEC + '，最终输出 L63，引用档内，391 + 885 篇，+0.372 [0.342, 0.405]，' + BOOT + '；351_stage10/reports/r0_r1_analysis.md §1；351_stage10/summary_r0r1/tc_R1target_vs_R0control.csv'),
    ('对照组 R1 只有 34 篇', T_CELLS + '；D = 34'),
    ('R1 目标论文（36 篇）', 'Stage 11 样本中的 R1 目标论文 36 篇（对照 R1 5 篇）；351_stage10/reports/r0_r1_analysis.md §5；361_stage11/summary_r0r1/stage11_curves_by_recall.csv'),
    ('R0 口径为 +0.02 到 +0.04', 'Stage 11 E4b 原始版（论文分折、未剔除标题复用），标题最后一个 token 上的 probe，probe 只打分第一个名字 token，probe(真标题) − probe(false_0)，A − B 引用档内，A 4,110 / B 2,186 篇：L16 +0.018、L32 +0.034、L56 +0.038，bootstrap 95% CI 均在 0 以上；361_stage11/summary_r0r1/E4b_probe_by_recall.csv'),
],
'28': [
    ('在 99.3% 的 R1 论文里', '重建匹配人数 = 标注包 m 的比例：R0 99.9%、R1 99.3%（596 篇）、R2 98.1%；351_stage10/reports/r0_r1_analysis.md §4；~/jlens_work/10_stage10/stage10_extra_r0r1.py'),
    ('在 495 篇同时有写对和漏掉作者的论文里', '351_stage10/reports/r0_r1_analysis.md §4；351_stage10/summary_r0r1/R1_author_hits.csv'),
    ('高 +0.20', 'Stage 10，R1 论文内 写对 − 没写对的作者（论文内配对），' + SPEC + '，最终输出 L63，495 篇，+0.199 [0.168, 0.232]，' + BOOT + '；报告 R0/R1 节 §4 表；351_stage10/summary_r0r1/R1_author_written_minus_missed.csv'),
    ('在 L52 之前约为 0', '同上，logit lens L48 −0.007、L52 +0.019、L54 +0.046、L57–L61 +0.173 到 +0.349；351_stage10/summary_r0r1/R1_author_written_minus_missed.csv'),
    ('高 +0.10', '同上，不给标题（名字先验），最终输出 L63，写对 − 没写对 +0.097 [0.060, 0.134]，495 篇；351_stage10/summary_r0r1/R1_author_written_minus_missed.csv'),
],
'29': [
    ('Pilot 在 L56 高 +9.3 个百分点', T_93),
    ('200 篇新论文上 +5.2', T_52),
    ('在 200 篇上是 +5.0', T_50AB),
    ('去掉 10 对就消失', T_8D_TAIL),
    ('L62 约 0.44', T_044),
    ('输出处 +0.21 [0.20, 0.22]', T_POOL),
    ('约三分之一', T_PRIOR3),
    ('在姓上约为 0', T_PRIORSUR),
    ('（ρ = 0.45）', T_X2),
    ('为 +0.20 [0.19, 0.21]', T_R0),
    ('比 A 多 +0.11', 'Stage 10，目标组内 R1 − R0（C − A），' + SPEC + '，最终输出 L63，引用档内（每格 ≥ 10 篇），C 485 + A 3,204 篇，+0.110 [0.086, 0.135]，' + BOOT + '；351_stage10/summary_r0/target_R1_minus_R0_within_bin.csv；351_stage10/reports/r0_sensitivity.md'),
    ('7 层平均', 'Stage 5–8 的积分终点 = 7 个源层平均（L63 不计入）；351_stage6/config/protocol.json "paper_integrated"；351_stage8/config/analysis_plan.json'),
],
'31': [
    ('20 条通用提示和 20 条论文提示', 'Stage 3 Exp 2/4 提示集；~/jlens_work/02_self_lens_validation/351_self_jlens_validation.py:13-50'),
    ('6 个通用层中的 6 层、6 个论文层中的 5 层', 'Stage 3 Exp 2/4，Self-100 − Public KL，各 20 条提示；351_self100_validation/summary/paired_bootstrap_ci.csv、summary/metrics.csv；报告 Stage 3 节图 3.1'),
    ('从 11.1 降到 7.2', 'Stage 3，论文提示 20 条，L32 KL(final ‖ lens)：Public-557 11.135（351_all/351_paper_fidelity.log L32 jlens 行）→ Self-100 7.180（351_self100_validation/summary/metrics.csv paper/self100/32）'),
    ('（0.58 对 0.81）', 'Stage 3，论文提示 20 条，L62 KL：Self-100 0.578、Vanilla 0.808；351_self100_validation/summary/metrics.csv（task=paper, layer=62, kl_final_to_lens_nats）'),
    ('（0.36 对 0.72）', '同上，L62 前 10 名重合度：Self-100 0.355、Vanilla 0.720；351_self100_validation/summary/metrics.csv（top10_overlap）'),
    ('20 次里 14 次全名胜出', 'Stage 3 Exp 3，L48 全名胜率 0.70 × 20 篇，两个 lens 相同；351_self100_gold_false/archive/summary/layer_summary.csv 列 full_win_rate'),
],
'32': [
    ('20,000 次 bootstrap', 'Stage 7.4 设计，种子 741；~/jlens_work/07_4_stage7_4/351_stage7_4.py:10-13'),
    ('r = 0.45，50 篇里 32 篇方向一致', 'Stage 7.4，J-Lens L56，Stage 5 与 Stage 7.3 的论文级相关，50 篇，Pearson 0.445，同号比例 0.64 = 32/50；351_stage7_4/summary/overview.json "L56_jlens_stage5_stage73"；351_stage7_4/summary/cross_stage_correlations.csv'),
    ('+0.002 [−0.008, +0.012]，中位数 −0.002，50 篇里 24 篇为正', 'Stage 7.4，J-Lens − Vanilla 标题优势，7 层积分，50 篇，均值 +0.0022 [−0.0075, +0.0124]，中位数 −0.0019，24 篇为正，论文 bootstrap 95% CI；351_stage7_4/summary/jlens_increment_bootstrap.csv 行 integrated；overview.json'),
    ('A−B 为 −0.014', 'Stage 7.4，J-Lens 增量的匹配 A − B，20 对，−0.0139 [−0.0332, +0.0036]；351_stage7_4/summary/overview.json "matched_ab_difference_of_lens_increment"'),
    ('去掉一篇论文就可能让 J-Lens 增量变号', 'Stage 7.4，逐一留出一篇后 7 层积分增量范围 −0.000046 到 +0.003494；351_stage7_4/summary/overview.json "integrated_jlens_minus_vanilla"'),
],
'33': [
    ('50 + 50 拆分', 'Stage 3 Exp 7 历史拆分，偶数 / 奇数索引各 50 条；351_self100_split_half/fits/config_A.json、config_B.json'),
    ('两套互不重叠的 100 条提示，外加独立的 100 条 WikiText 留出集', 'Stage 9A.1 设计，FitA100 / FitB100 / Holdout100 各 100 条；351_stage9/config/plan.json、manifest.json "counts"；~/jlens_work/09_stage9/351_stage9.py:50-62'),
    ('层数增加到 7 层', 'Stage 9 拟合层 L16–L62 共 7 层；351_stage9/runner_runs/full_A_100_7layers/fitting_config.json；351_stage10/config/lenses.json fitA'),
    ('约需 324 秒、约 62 GiB CPU 内存', 'Stage 9 正式 Fit A 第 1–4 条每条 325/323/325/322 s（均值 323.75 s，351_stage9_full_A.log）；单条提示 7 层基准 CPU 内存峰值约 62.06 GiB（351_stage9_benchmark_A1_7layers.log）'),
],
'34': [
    ('L24 名次 37,675，L56 120,750，L61 9,811，L62 120，输出层 61', 'Stage 10，示例论文 Coifman 等（2007），真标题，第一作者姓的首个 token “Co”（行 25029），logit lens L24–L62 与最终输出 L63 全词表名次；351_stage10/raw/logit/L*/shard_011.npz、raw/final/L63/shard_011.npz；351_stage10/reports/method_figs/coifman_layer_ranks.csv（列 r5_Co）'),
    ('第一作者 7 个 token 的平均 nlr 到 L58 都在 −4 左右，L62 升到 −1.11、输出层 −0.77', '同上，第一作者 7 个 token（行 25025–25031）的平均 log10(1/名次)，logit lens：L24–L58 为 −4.47 到 −3.92，L62 −1.111，最终输出 −0.772；351_stage10/reports/method_figs/coifman_layer_ranks.csv 列 mean_log10_inv_rank'),
    ('在输出层是 −1.19', '同上，false_0 条件，最终输出 L63，−1.194；351_stage10/raw/cond_false_0/final/L63/shard_011.npz；351_stage10/reports/method_figs/coifman_layer_ranks.csv（condition=false_0, readout=final）'),
],
'35': [
    ('名次在几万名', 'Stage 10，真标题，logit lens L24–L48，目标 4,621 + 对照 2,220 篇，平均 log10(1/名次) 约 −4.4 到 −4.6；报告 §6.1 表；351_stage10/summary/A_group_layer.csv'),
],
'36': [
    ('比例是 15–18%，logit lens 只有 1%', 'Stage 10 X3，真标题，全部 9,108 篇，同一批 token 配对，L48 前 10 命中率（token 比例）：三种 Jacobian lens 14.7%–18%，logit lens 1.1%；报告 §6.9 表；351_stage10/summary_extra/X3_means.csv'),
],
'37': [
    ('多出 +0.01 到 +0.03 的标题特异信号', T_X3_EXTRA),
    ('和 L62 的 0.44 相比', T_044),
    ('多出部分的目标−对照约为 0，在 L48 和 L56 甚至为负', 'Stage 10 X3，(lens − logit) 标题特异信号的引用档内 目标−对照，三种 Jacobian lens：L24–L40 约 0，L48 与 L56 为 −0.04 到 −0.06，' + BOOT + '；报告 §6.9 最后一表；351_stage10/summary_extra/X3_tc_spec_vs_logit.csv'),
],
'38': [
    ('只有约 0.01 到 0.03', T_E4_LENS),
    ('剩 1,863 篇，其中目标 896、对照 499', T_E4B_N),
    ('L24 约 0.05，到 L56 升到约 0.08', T_E4B_RECHECK_ALL),
    ('目标组比对照组高 0.03 到 0.08', T_E4B_RECHECK_TC),
],
'39': [
    ('7.4 为 +0.002', 'Stage 7.4，J-Lens − Vanilla 标题优势，7 层积分，50 篇，+0.002 [−0.008, +0.012]；351_stage7_4/summary/jlens_increment_bootstrap.csv 行 integrated'),
    ('Stage 8 为 −1.4 个百分点', 'Stage 8D，L56 J-Lens − Vanilla 标题优势，200 篇，−1.38 pp [−3.48, +0.68]；351_stage8/stage8D/summary/jlens_minus_vanilla.csv'),
    ('比例为 15–18%，logit lens 为 1%', 'Stage 10 X3，真标题，全部 9,108 篇，L48 前 10 命中率：三种 Jacobian lens 14.7%–18%，logit lens 1.1%；报告 §6.9 表；351_stage10/summary_extra/X3_means.csv'),
    ('只有 +0.01 到 0.03', T_X3_EXTRA),
    ('从 +0.04 升到 +0.08', T_E4B_ORIG_TGT),
    ('页面上 +0.04 到 +0.08 是复核前的数字', T_E4B_ORIG_TGT),
    ('复核后为 +0.05 到 +0.08', T_E4B_RECHECK_ALL),
],
'41': [
    ('20 篇论文、93 位作者，A 8 篇、B 8 篇、C 3 篇、D 1 篇，每篇约 91 秒、约 29.5 GiB 显存', 'Stage 4 Benchmark20；351_all/351_stage4_readout.log "STAGE 4 BENCHMARK ===== 20 papers"、authors_scored 93、"Mean seconds per paper 90.68"、gpu=29.5GiB；报告 Stage 4 节表'),
    ('平均倒数名次是 0.0070，中位数只有 0.0009；一篇论文就占了 L56 均值的 71%，去掉它均值降到 0.0021', 'Stage 4，J-Lens L56，第一作者首 token 倒数名次，20 篇：均值 0.00704，中位数 0.00092，最大单篇占总和 71.03%，去掉后均值 0.00215；351_all/351_stage4_artifacts/audit/audit_report.md 表 1 行 L56'),
],
'42': [
    ('每篇论文 50 个匹配名字（同领域、同 token 数、同年份）加 50 个随机名字，共 75,000 对', 'Stage 7.2 设计，Pilot50 50 篇 × 100 个错误作者 × 15 种读出 = 75,000；~/jlens_work/07_2_stage7_2/351_stage7_2.py:62-111；351_stage7_2/summary/quality.json；351_stage7_2/summary/candidate_pairwise_scores.csv'),
    ('L40 +0.15，L48 +0.19，L56 +0.19，区间都在 0 以上；L62 为 +0.04，区间含 0', 'Stage 7.2，真标题，首 token 金标准胜率，J-Lens，合并池，Pilot50 20 对 A − B，配对 bootstrap 95% CI：L40 +0.150 [0.013, 0.289]、L48 +0.193 [0.071, 0.318]、L56 +0.187 [0.015, 0.345]、L62 +0.038 [−0.144, +0.215]；报告 Stage 7.2 节图 7.2；351_stage7_2/summary/matched_ab_bootstrap.csv'),
    ('7 层积分 +0.105 [−0.012, +0.228]', 'Stage 7.2，7 层积分，J-Lens，合并池，20 对 A − B，配对 bootstrap 95% CI（2026-10-30 按逐对数据重算）；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 "7.2 integrated7 A-B jlens pool=combined"'),
    ('5,000 个错误名字里有 156 个与正确名字共享第一个 token，100 个名字只有约 46 个不同的第一个 token', T_46),
],
'43': [
    ('为 +0.21 到 +0.23', T_SPEC_TC_LATE),
    ('目标组 11% 是 R1（写对少数作者），对照组只有 1.5%', T_R1SHARE),
    ('输出处的差是 +0.199', T_R0),
    ('而不是 +0.207', T_POOL),
],
'44': [
    ('L62 为 +0.23', T_FINE),
    ('L57 转正', T_PUB57),
    ('两组都在 L61 达到最高', 'Stage 10，' + SPEC + '，logit lens 各组均值：目标 L50 +0.022 → L61 +0.596，对照 +0.020 → +0.282（L62 为 +0.583 / +0.252）；报告 §6.10；' + F_A_SPEC),
],
'45': [
    ('1,186 篇、5 个假标题平均：L24 0.080、L40 0.302、L48 0.821、L52 0.995', T_X6),
],
'46': [
    ('X7（1,186 篇）：从 L0 阻断 S = 1.00，L24 0.87，L40 0.29，L48 0.14，L52 0.029（target 0.018，control 0.051）', T_X7),
],
'47': [
    ('用了 593 篇目标论文和 593 篇对照论文', T_N593),
],
'48': [
    ('L40 恢复 29%，L48 恢复 83%', T_E1('L40 0.291 [0.274, 0.308]，L48 0.825 [0.807, 0.842]（四舍五入为 82%–83%）')),
    ('L52 起全部恢复', T_E1('L52 0.996 [0.989, 1.003]')),
    ('只复制标题最后一个 token 只恢复约 12%', 'Stage 11 E1t，只替换标题最后一个 token，真标题→false_0，最终输出恢复比例，全部 1,186 篇 L8–L40 为 0.12–0.15，L56 0.004；报告 §6.11 恢复比例图虚线；361_stage11/summary/E1t_recovery.csv'),
    ('去掉 83% 的效应；从 L32 起 37%，从 L48 起 6%，从 L52 起为 0', T_E2('L0 0.831 [0.801, 0.862]、L32 0.372、L48 0.064、L52 0.007 [0.001, 0.013]')),
    ('最多去掉 15%', T_E2N),
    ('在 L52 恢复 0.85，只换冒号最多 0.17', T_P1),
    ('L48 恢复约 0.82，L52 起约 1.0', T_X6),
],
'49': [
    ('由一篇论文撑起（71%）', T_71),
    ('在 L48 恢复 80–87%', 'Stage 11 E1 替换，真标题→false_0，标题之后全部位置，最终输出名字 token 恢复比例，L48 目标 593 篇 0.803、对照 593 篇 0.866（全部 0.825）；报告 §6.11 恢复比例图；361_stage11/summary/E1_recovery.csv'),
    ('L52 起恢复 100%', T_E1('L52 0.996 [0.989, 1.003]（目标 0.986、对照 1.016）')),
],
'51': [
    ('50 篇论文、227 位作者、972 个名字 token', 'Stage 6，Pilot50；351_stage6/raw/token_layer_scores.csv（方法手册统计）；351_stage6/summary/summary.json'),
    ('A 组 0.085 [0.075, 0.096]，B 组 0.068 [0.057, 0.080]，C 组 0.106，D 组 0.050', 'Stage 6，J-Lens 条件完整作者 JMRR，7 层积分，各组论文均值（A 20、B 20、C 7、D 3 篇），论文 bootstrap 95% CI；报告 Stage 6 节图 6.1；351_stage6/summary/integrated_group.csv'),
    ('L62 上 A−B 为 +0.097 [0.028, 0.163]，Vanilla 也是 +0.091', 'Stage 6，条件全名 JMRR，L62 匹配 A − B，20 对：J-Lens +0.0966 [0.0282, 0.1630]，Vanilla +0.0907 [0.0161, 0.1676]，配对 bootstrap 95% CI；351_stage6/summary/matched_ab_bootstrap.csv 行 layer=62'),
],
'52': [
    ('做了 10,000 次配对 bootstrap', 'Stage 7.1 设计，种子 35171；~/jlens_work/07_1_stage7_1/351_stage7.py:14,86-87,181'),
    ('第一个 token +0.001 [−0.011, +0.015]，后续 token +0.021 [+0.002, +0.039]，全部 token +0.017 [+0.003, +0.030]', 'Stage 7.1，J-Lens JMRR 7 层积分，匹配 A − B，20 对，配对 bootstrap 95% CI：第一个 token +0.0014 [−0.0114, +0.0149]，后续 token +0.0206 [+0.0022, +0.0385]，全部 token +0.0166 [+0.0026, +0.0299]；报告 Stage 7.1 节表；351_stage7_1/summary/layer_and_integrated_effects.csv'),
    ('第一个 token +0.014（20 对里 12 对为正），后续 token +0.121（20 对里 15 对为正）', '同上，L62：第一个 token +0.0141（12/20 为正），后续 token +0.1215（15/20 为正）；351_stage7_1/summary/layer_and_integrated_effects.csv（layer=62）'),
],
'54': [
    ('姓在输出处高 +0.22，logit lens 在 L62 高 +0.32', 'Stage 10 §6.7，真标题，完整名开头的 8,876 位作者（名进前 10：678 位），姓（后续 token）平均 log10(1/名次)，进前 10 − 未进，论文聚类 bootstrap 95% CI：最终输出 L63 +0.222 [0.165, 0.275]，logit lens L62 +0.322 [0.253, 0.388]；351_stage10/summary_extra/X1_cond_by_first_role.csv'),
],
'55': [
    ('（Spearman 0.27）', 'Stage 10，真标题，最终输出 L63，引用档内中心化的平均 log10(1/名次) 与多选题答对顺序数 0–4，R0/R1 论文 8,894 篇，引用档内 Spearman ρ = 0.268（p < 0.001）；报告 §6.6；351_stage10/summary/C_graded_mc_team_a.csv（metric=mean_nlr）'),
],
'56': [
    ('目标组高 +0.17 到 +0.23，对照组高 +0.12 到 +0.18', 'Stage 11 E3 连写 − 单独打分，真标题，最终输出 L63，作者位置 2 到 4+：目标 +0.173 / +0.229 / +0.234（4,073 / 2,978 / 2,030 篇），对照 +0.118 / +0.164 / +0.183，' + BOOT + '；报告 §6.11 连写表 gain 列；361_stage11/summary/E3_chain.csv'),
    ('从 0.42 降到 0.26', 'Stage 11 E3，目标组第 4 位起作者，标题特异信号（' + SPEC + '，最终输出）单独打分 +0.421 → 连写 +0.260，2,030 篇（第 2 位为 +0.454 → +0.405）；报告 §6.11 连写表 4+ · target 行；361_stage11/summary/E3_chain.csv'),
    ('目标组仍然高于对照组 +0.11 到 +0.15', 'Stage 11 E3 连写，标题特异，引用档内 目标−对照，作者位置 2 / 3 / 4+：+0.151 / +0.124 / +0.114；报告 §6.11 连写表；361_stage11/summary/E3_chain.csv'),
],
'57': [
    ('在后续 token 上（+0.021），不在第一个 token 上（+0.001）', 'Stage 7.1，J-Lens JMRR 7 层积分，匹配 A − B，20 对：后续 token +0.0206 [+0.0022, +0.0385]，第一个 token +0.0014 [−0.0114, +0.0149]；351_stage7_1/summary/layer_and_integrated_effects.csv'),
    ('73% 的名字以首字母开头', 'Stage 10 名字格式，24,739 / 33,780 个作者上下文以首字母开头；报告 §6.7；351_stage10/summary_extra/X1_cond_by_first_role.csv 列 n_contexts（readout=final）'),
    ('还能帮助预测姓（+0.22）', 'Stage 10 §6.7，完整名开头 8,876 位作者，名进前 10 − 未进，最终输出 L63 姓 +0.222 [0.165, 0.275]，论文聚类 bootstrap 95% CI；351_stage10/summary_extra/X1_cond_by_first_role.csv'),
    ('只换名字位置在 L52 恢复 0.85，只换冒号最多 0.17', T_P1),
    ('X6 用 5 个假标题', T_X6),
],
'58': [
    ('L62 约 0.44', T_044),
    ('整段提示替换在 L48 恢复 0.83', T_E1('L48 0.825 [0.807, 0.842]')),
    ('L52 起约 1.0', T_E1('L52 0.996 [0.989, 1.003]')),
    ('只换名字位置从 0.61 升到 0.85，只换“:”最多 0.17', T_P1),
    ('L52 之后阻断几乎没有损失', T_E2('L52 0.007 [0.001, 0.013]')),
    ('（输出处 +0.21）', T_POOL),
    ('（恢复 0.23）', T_P2),
    ('（0.18、0.22）', T_P2),
],
'59': [
    ('一篇论文占 Stage 4 L56 均值的 71%', T_71),
    ('去掉 100 对中的 10 对就消失', T_8D_TAIL),
    ('100 个错误名字只有约 46 个不同的第一个 token，3% 与正确名字打平', T_46),
    ('严格通过率为 25.5%', T_255),
],
'60': [
    ('Pilot +9.3', T_93),
    ('新 200 篇 +5.2 个百分点', T_52),
    ('全量 L62 标题特异约 0.44', T_044),
    ('全量输出处 +0.21', T_POOL),
    ('输出 +0.20', T_R0),
    ('全量单调上升 ρ = 0.45', T_X2),
    ('三把用不同文本拟合的 Jacobian lens', 'Stage 10 三种 Jacobian lens：public（557 条 WikiText-103）、self100（100 条）、fitA（Stage 9 Fit A 100 条）；351_stage10/config/lenses.json；报告 §6.9'),
],
'61': [
    ('L24 约 0.99，L40 约 0.92，L48 约 0.42', 'Stage 13 X1，测试集 582 篇，R = (patched − other) ÷ (own − other)，来源问题 作者/年份/领域：L24 0.991/0.985/0.992，L40 0.921/0.917/0.915，L48 0.424/0.405/0.417，团队聚类 95% CI；报告 Stage 13 X1 表；381_stage13/reports/x1_report.md test 表'),
    ('（测试集 582 篇）', 'Stage 13 X1 调参集/测试集按作者团队各半：测试 582、调参 596 篇；381_stage13/reports/x1_report.md 第 3 行；381_stage13/config/pairs.parquet'),
],
'62': [
    ('L8 为 +0.32，L36 峰值 +0.46', 'Stage 13 X3，主分析测试集，标题最后一个 token，G′ = cos(原, 改写) − cos(原, D)：L8 +0.316 [0.293, 0.338]，峰值 L36 +0.463；报告 Stage 13 X3 节；381_stage13/reports/x3_report.md Verdict 节与 G′ 表'),
    ('中位数是改写 0.61、D 0.15', 'Stage 13 X3 主分析 1,110 篇，修正版 Jaccard（jaccard2）中位数：改写 0.611，近邻 D 0.154（敏感性集 1,012 篇为 0.615 / 0.150）；381_stage13/reports/x3_report.md Word overlap 表'),
    ('（本例 0.22 和 0.14）', '示例论文 Coifman 等（2007）：改写 jaccard2 0.222，近邻 D 0.143；381_stage13/config/x3_lexical_neighbour_j2.csv；381_stage13/summary_x3/para_nli.csv'),
    ('改写 − D 为 +0.239', 'Stage 13 X3 行为，第一作者教师强制打分 log10(1/名次)，改写标题 − 近邻 D 标题，主分析测试集 552 篇，+0.239 [0.212, 0.266]，团队聚类 95% CI；381_stage13/reports/x3_report.md Behaviour 表'),
],
'63': [
    ('第一作者从 L8 起可以解码（+0.046）', 'Stage 13 X4，标题位置，D = 本篇状态 − 配对论文状态的答案分数（log10(1/名次)），最早层在调参集选出、测试集 582 篇确认：第一作者 L8 +0.046 [0.035, 0.059]，团队聚类 95% CI；报告 Stage 13 X4 表；381_stage13/reports/x4_report.md 第 9–11 行'),
    ('年份从 L40 起（+0.013）', '同上，年份 L40 +0.013 [0.008, 0.018]；381_stage13/reports/x4_report.md'),
],
'65': [
    ('替换在 L48 恢复 R ≥ 0.5，L52 起 ≥ 0.95', 'Stage 13 X5 汇总，取 X6 5 个假标题平均恢复比例 L48 0.821、L52 0.995（团队聚类），X5 规则 R ≥ 0.5 / ≥ 0.95；381_stage13/summary_x5/x5_layer_order.csv X6 行；381_stage13/summary_x6/x6_recovery.csv；381_stage13/reports/x5_report_v2.md'),
    ('从 L52 起阻断标题不再有损失', 'Stage 13 X7，论文特有阻断损失 S(L52)：全部 0.029、target 0.018、control 0.051（control L54 0.018、L56 0.000）；381_stage13/reports/x7_report.md'),
],
'66': [
    ('+0.05 到 +0.08', T_E4B_RECHECK_ALL),
    ('目标组高 +0.03 到 +0.08', T_E4B_RECHECK_TC),
],
'67': [
    ('X6/X7 用 5 个假标题', 'Stage 13 X6 用 false_0–false_4 五个假标题重做 Stage 11 替换（L48 平均 0.821、L52 0.995），X7 在 false_0 运行上重做阻断；381_stage13/reports/x6_report.md、x7_report.md'),
],
}
