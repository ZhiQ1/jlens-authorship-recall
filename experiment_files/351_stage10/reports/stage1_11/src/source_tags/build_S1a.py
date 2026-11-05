# Builds S1a.json. Each entry: (old_with_markers, [tags], fix_old_new or None). '¤' marks where a tag goes.
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from segs import bounds
D = __file__.rsplit('/', 1)[0]
s = open(D + '/report_v26_readonly.html', encoding='utf-8').read()
a, b = bounds(s)['S1a']; t = s[a:b]
AR = 'jlens_archive_stage1_8/experiment_files/'
def T(x): return '<span class="src">（' + x + '）</span>'

E = []
def add(old, tags, fix=None):
    E.append((old, tags, fix))

# ---------------- header / overview ----------------
add('（小样本：20 → 50 → 200 篇¤）与 Stage 10–11 报告（全量 9,108 篇¤）',
    ['Stage 4 Benchmark20、Pilot50、Stage 8 新论文的篇数；' + AR + '351_all/351_stage4_readout.log、' + AR + '351_stage5_crossed_v2/cohort/pilot50_v1.csv、' + AR + '351_stage8/cohort/stage8_papers.csv',
     '标注包全部论文；' + AR + '351_all/351_audit.json "total"'])
add('Stage 1–9 在 20–200 篇论文上建立信号并逐一排除替代解释；Stage 10–11 在全部 9,108 篇论文上¤逐层定位',
    ['Stage 1–9 样本 20/50/200 篇见 ' + AR + '351_all/351_stage4_readout.log、351_stage5_crossed_v2/cohort/pilot50_v1.csv、351_stage8/cohort/stage8_papers.csv；全量 9,108 篇见 351_stage10/cohort/papers.parquet'])
add('L56 真标题比错误标题高 +9.3 pp（Pilot50）¤，200 篇新论文上 +5.2 pp¤。',
    ['Stage 7.3，J-Lens L56，真标题胜率 − 20 个错误标题平均；50 篇论文均值；' + AR + '351_stage7_3/summary/paper_null_distribution.csv（pool=combined，mode=jlens_L56）',
     'Stage 8D RQ1，J-Lens L56，真标题 − 20 个错误标题；200 篇；' + AR + '351_stage8/stage8D/summary/primary_questions.csv 行 RQ1_L56_replication'])
add('“标题特异信号”在 L62 约 0.44¤；名字先验只占目标−对照差的约 1/3¤，在姓的第一个 token 上约为 0¤。',
    ['Stage 10，真标题 − 5 个假标题平均，public J-lens L62，全部 9,108 篇均值 0.442（三种 Jacobian lens 0.436–0.444）；351_stage10/summary_extra/X3_means.csv',
     'Stage 12 CPU 名字先验拆解（报告 §6.12），最终输出 L63，全部名字 token，引用档内目标−对照：先验 +0.087 / 真标题差 +0.247；371_stage12/summary_cpu/A_prior_decomposition.csv',
     '同上，姓的第一个 token，先验目标−对照 +0.022 [−0.019, +0.063]；371_stage12/summary_cpu/A_prior_decomposition.csv'])
add('中间层约为 0，输出处 +0.21¤；两组都只用 R0 时 +0.20¤，结论不变',
    ['Stage 10，真标题 − 5 个假标题平均，引用档内目标−对照；最终输出 L63 +0.207 [0.196, 0.220]；目标 4,621 + 对照 2,220 篇；351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv',
     'Stage 10 R0 口径 A − B，最终输出 L63，引用档内，+0.199 [0.187, 0.212]；3,423 + 2,151 篇；351_stage10/reports/r0_r1_analysis.md §1'])
add('L48 已恢复 83%，L52 起 100%¤；从 L52 起阻断',
    ['Stage 11 E1 替换，真标题→false_0，标题后全部位置；最终输出名字 token 恢复比例，L48 0.825 [0.807, 0.842]，L52 0.996；593+593 篇；§6.11 恢复比例图；361_stage11/summary/E1_recovery.csv'])
add('对标题的注意力已没有影响¤。',
    ['Stage 11 E2 注意力阻断，标题后全部位置，从 L52 起；损失比例 0.007 [0.001, 0.013]；593+593 篇；361_stage11/summary/E2_knockout.csv'])
add('target = A + C（4,621），control = B + D（2,220）。A = 认得出·R0（4,110），B = 认不出·R0（2,186），C = 认得出·R1（511），D = 认不出·R1（34）¤。R0 = 开放回答一个真作者都没写对；R1 = 写对了一部分但 HR2 &gt; 0.5¤。',
    ['Stage 1 四组篇数；' + AR + '351_all/351_audit.json "group_counts"；target/control 篇数见 labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 第 7 行',
     'HR2 阈值 0.5 为标注规则；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/rules.yaml、label_README.md'])

# ---------------- Part 1 summary ----------------
add('Stage 8 在 200 篇全新论文上¤做冻结设计',
    ['Stage 8 新论文篇数；' + AR + '351_stage8/cohort/stage8_papers.csv'])
add('Pilot50 中 L56 真标题比 20 个错误标题平均高 +9.3 个百分点（35/50 篇为正）¤；在 200 篇新论文上为 +5.18 pp [+2.93, +7.48]¤。',
    ['Stage 7.3，J-Lens L56，真标题胜率 − 20 个错误标题平均；50 篇论文均值 +0.0934，35 篇为正；' + AR + '351_stage7_3/summary/paper_null_distribution.csv（pool=combined，mode=jlens_L56）',
     'Stage 8D RQ1，J-Lens L56，真标题 − 20 个错误标题；200 篇；论文 bootstrap 95% CI；' + AR + '351_stage8/stage8D/summary/primary_questions.csv 行 RQ1_L56_replication'])
add('Stage 8 为 +4.98 pp [+0.32, +9.91]¤，但去掉最大的 10 对后降为 −0.39 pp¤。',
    ['Stage 8D RQ2，J-Lens L56，匹配 A − B；100 对；配对 bootstrap 95% CI；' + AR + '351_stage8/stage8D/summary/primary_questions.csv 行 RQ2_matched_A_minus_B',
     '同上，按 A − B 降序去掉前 10 对后其余 90 对的均值（事后诊断）；' + AR + '351_stage8/stage8D/summary/matched_pair_differences.csv（mode=jlens_L56）重算'])
add('Stage 7.4 为 +0.002 [−0.008, +0.012]¤，Stage 8 为 −1.38 pp [−3.48, +0.68]¤。',
    ['Stage 7.4，J-Lens − Vanilla 标题优势，7 层积分；50 篇；论文 bootstrap 95% CI；' + AR + '351_stage7_4/summary/jlens_increment_bootstrap.csv 行 integrated',
     'Stage 8D，L56 J-Lens − Vanilla 标题优势；200 篇；论文 bootstrap 95% CI；' + AR + '351_stage8/stage8D/summary/jlens_minus_vanilla.csv'])
add('集中在名字的后续 token</b>（+0.021）¤，第一个 token 几乎为 0',
    ['Stage 7.1，J-Lens 后续 token JMRR，7 层积分，匹配 A − B +0.0206 [+0.0022, +0.0385]（第一个 token +0.0014 [−0.0114, +0.0149]）；20 对；' + AR + '351_stage7_1/summary/layer_and_integrated_effects.csv'])

# ---------------- Stage 1 ----------------
add('2026-10-15 标注包共 9,108 篇论文¤，每个',
    [AR + '351_all/351_audit.json "total"'])
add('分析队列为冻结的 6,841 篇（351_prepare_all.py 保留 group_tight = target/control 且 HR2 &gt; 0.5 的论文），其余 2,267 篇 guard/中间情况排除¤。',
    ['Stage 1 队列；' + AR + '351_all/351_audit.json "four_group_total"、"group_counts.excluded"；HR2 阈值见 00_cohort/351_prepare_all.py:17-19'])
add('多出来的 R1 论文几乎全在 target 一侧（C 511 篇，D 仅 34 篇）¤。',
    ['Stage 1 四组篇数；' + AR + '351_all/351_audit.json "group_counts"'])
add('输出处的目标−对照标题特异差为 +0.199 [0.187, 0.212]，合并口径为 +0.207¤，各层形状相同；C 比 A 强（+0.11）¤，但同样',
    ['Stage 10，真标题 − 5 个假标题平均，最终输出 L63，引用档内目标−对照；R0 口径 A − B 3,423 + 2,151 篇，合并口径 +0.207 [0.195, 0.220]；论文 bootstrap 95% CI；351_stage10/reports/r0_r1_analysis.md §1',
     'Stage 10，最终输出 L63，标题特异信号，引用档内 C − A +0.110 [0.086, 0.133]；485 + 3,204 篇；351_stage10/reports/r0_r1_analysis.md §2'])
add('识别通过 = 4 种选项顺序全对且真选项平均概率 ≥ 0.5；失败 = 0–1 次对¤。',
    ['标注规则 group_tight；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md、rules.yaml（tightened: min_orders 4, min_p_true 0.5）'])
add('（A8/B8/C3/D1；这 20 篇是 Stage 4 用种子 3514 在"组 × 引用档"内打乱后轮流抽取的），再新增 30 篇（A12/B12/C4/D2）¤。',
    ['Pilot50 构造；04_stage4/351_stage4_readout.py:14-40、05_stage5/351_stage5.py:52-63；' + AR + '351_stage5_crossed_v2/cohort/pilot50_v1.csv 列 stage4_existing'])
add('按 sha256("35150" + paper_id) 排序，按这个确定性的哈希顺序依次选取，并在同领域、同引用档内配对¤。',
    ['05_stage5/351_stage5.py:7, :34, :63'])
add('<li>20 对 A/B 在完全相同的领域和引用档内匹配，先最大化配对数，再最小化 |Δ年份| + 2×|Δ作者数|¤。',
    ['05_stage5/351_stage5.py:126-145；' + AR + '351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv（20 行）'])
add('平均年份差 1.65（最大 4），作者数差 1.15（最大 7）；年份 SMD +0.016，作者数 SMD +0.287¤。',
    ['Pilot50，20 对 A/B；' + AR + '351_stage5_crossed_v2/matching/pilot50_ab_pairs.csv 列 year_gap、author_count_gap；SMD 为方法手册重算'])
add('4097+ 档在全队列中没有 B、D 组论文¤。',
    [AR + '351_all/351_bin_counts.csv'])
add('0–2 引用档的识别通过率为 38.6%（普通）/ 25.5%（严格），高于预设的 ≤10% 下限¤，',
    ['标注包自检，0-2 档 796 篇；labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/label_README.md 第 8 行'])

# ---------------- Stage 2 ----------------
add('积分 JMRR = 7 个源层的平均，L63 作为参照不计入¤。',
    [AR + '351_stage6/config/protocol.json "paper_integrated"'])
add('J-Lens 与 Vanilla 的最终 logit 差超过 0.1 即拒绝¤。',
    ['05_stage5/351_stage5.py:205-206；04_stage4/351_stage4_readout.py:86-89'])

# ---------------- Stage 3 ----------------
add('Public-557（557 条 WikiText-103 提示词拟合，覆盖 L0–L62）和自己拟合的 Self-100（100 条提示词，6 个层）¤。',
    [AR + '351_provenance_audit/summary/audit_summary.json；351_provenance_audit/reports/audit_report.md（recorded n=557 / n=100）；qwen32b_jlens_prelim_100_config.json'])
add('形状 5,120×5,120（63/63、6/6 通过）¤。',
    ['Self-100 见 ' + AR + '351_self100_validation/numerical/matrices.csv 列 finite；Public 63 层见 351_stage8/recompute_2026-10-30/stage3_lens_frobenius_norms.csv 列 finite'])
add('系统性偏低约 0.25%，2026-10-30 重算）¤',
    ['Stage 3 Exp 1，L48 Frobenius 范数，float64 / float32；351_stage8/recompute_2026-10-30/stage3_lens_frobenius_norms.csv 行 layer=48 列 frobenius_fp64、frobenius_fp32（作业 11500587）'])
add('在 20 条通用提示和 20 条论文提示上¤比较',
    ['02_self_lens_validation/351_self_jlens_validation.py:13-50'])
add('Self-100 在 6/6 个通用层、5/6 个论文层 KL 更低¤，',
    ['Stage 3 Exp 2/4，Self − Public KL；各 20 条提示；' + AR + '351_self100_validation/summary/paired_bootstrap_ci.csv、summary/metrics.csv；图 3.1 与上表'])
add('两个 lens 互不占优；L48 都是 14/20 全名胜出¤。',
    ['Stage 3 Exp 3，全名胜率 0.70 × 20 篇；' + AR + '351_self100_gold_false/archive/summary/layer_summary.csv 列 full_win_rate'])
add('Self-100 用冻结的 1,000 条 WikiText 语料前 100 条；与 40 条评估提示 0 次完全匹配、0 次 8 词重叠¤。Public-557 只能确认处理过索引 0–556¤，',
    ['Stage 3 Exp 5；' + AR + '351_provenance_audit/reports/audit_report.md "Audit 3"',
     AR + '351_provenance_audit/summary/audit_summary.json → public_config（prompts_fitted 557）'])
add('两份 fitting.py 的 519 行 diff¤ 显示',
    ['~/jlens_work/03_provenance_audit/351_jlens_fitting_diff.txt（wc -l = 519）'])
add('最后相对变化 0.006215，未达 0.002 阈值）¤。',
    ['Stage 3 Exp 6，层数 63 vs 6、dim_batch 64 vs 8、557 条人工停止、final_mean_rel_change 0.006215、stop_at_delta 0.002；' + AR + '351_provenance_audit/summary/protocol_comparison.csv、summary/audit_summary.json → public_config'])
add('（A 用时 1,971 s，B 1,504 s）¤。',
    ['偶数 / 奇数索引各 50 条见 ' + AR + '351_self100_split_half/fits/config_A.json、config_B.json；用时见 fits/complete_A.json、complete_B.json "elapsed_seconds"（1,971.33 / 1,503.67 s）'])
add('矩阵余弦从 L24 的 0.678 升到 L62 的 0.9998，相对 Frobenius 差从 0.807 降到 0.018¤。论文 L48 上 A 的 KL 更好（8.38 vs 9.04）¤，',
    ['Stage 3 Exp 7，A 半 vs B 半各 50 条；图 3.2 左；' + AR + '351_self100_split_half/summary/matrix_stability.csv',
     '20 条论文提示；图 3.2 右；' + AR + '351_self100_split_half/readout_comparison/reports/readout_stability_report.md 行 paper 48'])
add('<figcaption>图 3.1 两个 lens 与 Vanilla 的 KL（越低越好），20 条通用提示（左）与 20 条论文提示（右）¤</figcaption>',
    [AR + '351_self100_validation/summary/metrics.csv；351_all/351_paper_fidelity.log'])

# ---------------- Stage 4 ----------------
add('<p>20 篇论文、93 位作者（A8 / B8 / C3 / D1），平均 90.68 秒/篇，GPU 峰值约 29.5 GiB（历史报告值）¤。',
    ['Stage 4 Benchmark20；' + AR + '351_all/351_stage4_readout.log "STAGE 4 BENCHMARK ===== 20 papers"、"Mean seconds per paper 90.68"、gpu=29.5GiB'])
add('恢复了全部 20 篇和 93 个作者实例¤。',
    [AR + '351_stage6/summary/summary.json "reused_stage4": 20；' + AR + '351_all/351_stage4_readout.log authors_scored 93'])
add('L56 第一作者 J-Lens 平均 RR = 0.00704，中位数仅 0.00092；一篇论文贡献了总和的 71.03%，去掉后平均降为 0.00215¤。',
    ['Stage 4，J-Lens L56，第一作者首 token 倒数名次；20 篇；' + AR + '351_all/351_stage4_artifacts/audit/audit_report.md 表 1 行 L56'])

# ---------------- Stage 5 ----------------
add('<p>50 篇冻结论文。',
    None, None)  # placeholder removed below
E.pop()
add('<p>50 篇冻结论文¤。每篇论文 P',
    [AR + '351_stage5_crossed_v2/cohort/pilot50_v1.csv'])
add('再用种子哈希（35150）。50 对中没有出现 G 与 F 首 token 相同的情况¤。',
    ['05_stage5/351_stage5.py:103-117；' + AR + '351_stage5_crossed_v2/reports/pilot50_audit_manifest.json "n_same_first_token": 0'])
add('积分终点为 7 个源层平均。bootstrap 2,000 次¤。',
    ['05_stage5/351_stage5.py:277-280, :319-324'])
add('<p>全部 50 篇：L56 +1.167 [+0.533, +1.838]，L62 +1.077 [+0.363, +1.816]¤。匹配 A−B 积分：+0.081 [−0.427, +0.648]¤。</p>',
    ['Stage 5，J-Lens，交叉对比 T（logit 差）；50 篇；论文 bootstrap 95% CI；图 5.1 左；' + AR + '351_stage5_crossed_v2/summary/layer_summary.csv 行 group=ALL',
     'Stage 5，J-Lens 7 层积分，匹配 A − B；20 对；配对 bootstrap 95% CI；图 5.1 右；' + AR + '351_stage5_crossed_v2/summary/matched_ab_summary.csv 行 layer=integrated'],
    ('+0.081 [−0.427, +0.648]', '+0.081 [−0.426, +0.648]'))
add('<figcaption>图 5.1 J-Lens 交叉对比：全部 50 篇（左）与 20 对 A−B（右）¤</figcaption>',
    [AR + '351_stage5_crossed_v2/summary/layer_summary.csv、matched_ab_summary.csv'])

add('所以有了 7.2（扩到 100 个错误作者）和 7.3（扩到 20 个错误标题）¤。',
    ['Stage 7.2/7.3 设计：每篇 50 个匹配 + 50 个随机错误作者，20 个错误标题；' + AR + '351_stage7_2/summary/quality.json、07_2_stage7_2/351_stage7_2.py:62-111、07_3_stage7_3/351_stage7_3.py:83-91'])

# ---------------- Stage 6 ----------------
add('<p>50 篇全部完成：复用 Stage 4 的 20 篇（核对 schema、提示词、作者和 token 名次后），新算 30 篇¤。',
    [AR + '351_stage6/summary/summary.json "completed" 50、"reused_stage4" 20、"measured_gpu" 30'])
add('上下文上限 512，名字上限 32 token（超长拒绝而非截断）¤。共 227 个作者实例、972 个 token 实例、14,580 行（15 种读出 × 层），最长名字 10 token¤。',
    ['06_stage6/351_stage6.py:173-181, :382',
     'Stage 6，Pilot50；' + AR + '351_stage6/raw/token_layer_scores.csv（方法手册统计）'])
add('<figcaption>图 6.1 条件全名 JMRR 逐层轨迹，按组平均（A=20, B=20, C=7, D=3）¤</figcaption>',
    [AR + '351_stage6/summary/summary.json "groups"；351_stage6/summary/paper_layer_trajectories.csv'])
add('<p>L62 A−B = +0.0966 [+0.0282, +0.1630]；Vanilla 也为正 +0.0907 [+0.0161, +0.1676]¤。',
    ['Stage 6，条件全名 JMRR，L62 匹配 A − B，J-Lens / Vanilla；20 对；配对 bootstrap 95% CI；' + AR + '351_stage6/summary/matched_ab_bootstrap.csv 行 layer=62'])

out = []
for old, tags, fix in E:
    parts = old.split('¤')
    assert len(parts) - 1 == len(tags), old
    o = ''.join(parts)
    n = parts[0]
    for tg, p in zip(tags, parts[1:]):
        n += T(tg) + p
    e = {'old': o, 'new': n}
    if fix:
        assert fix[0] in n
        e['new'] = n.replace(fix[0], fix[1]); e['fix'] = True
    out.append(e)
json.dump(out, open(D + '/S1a.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
