import json,sys
sys.path.insert(0,'/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags')
from segs import bounds
D='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/'
s=open(D+'report_v26_readonly.html',encoding='utf-8').read()
a,b=bounds(s)['S1b']; t=s[a:b]
def T(x): return '<span class="src">（'+x+'）</span>'
# (old, insert_after_substring or None=end, tag)
E=[
("（种子 35171）。", "（种子 35171）", "Stage 7.1 设计，作者等权、按配对重抽；~/jlens_work/07_1_stage7_1/351_stage7.py:14,86-87,181"),
("（最大差 1.1×10⁻¹⁶）", None, "Stage 7.1 与 Stage 6 历史聚合值逐行核对，750 行；351_stage7_1/reports/experiment_report.md"),
("L62 r=0.77，", "L62 r=0.77", "Stage 7.1 补充，J-Lens，Pilot50 50 篇，论文级 Pearson r；方法手册 C 部分从 351_stage6/raw/token_layer_scores.csv 重算一致；报告原出处文件未找到"),
("（来自 6,841 篇，种子 35172）。", "（来自 6,841 篇，种子 35172）", "Stage 7.2 设计，Pilot50 每篇 1 金标准 + 50 匹配 + 50 随机，共 5,050 条候选；~/jlens_work/07_2_stage7_2/351_stage7_2.py:62-111；351_stage7_2/summary/quality.json"),
("实际匹配数 2,159 / 182 / 135 / 24。", "2,159 / 182 / 135 / 24", "Stage 7.2，tier 0/1/2/3 匹配错误作者数，50 篇 × 50；351_stage7_2/summary/quality.json \"matching_tiers\""),
("（50 × 100 × 15）。", "（50 × 100 × 15）", "Stage 7.2，50 篇 × 100 个错误作者 × 15 种读出；351_stage7_2/summary/candidate_pairwise_scores.csv"),
("配对 bootstrap 10,000 次</figcaption>", "配对 bootstrap 10,000 次", "Stage 7.2，真标题，J-Lens 各层，合并池，Pilot50 20 对；351_stage7_2/summary/matched_ab_bootstrap.csv"),
("L62 +0.038（跨 0）。", "L62 +0.038（跨 0）", "Stage 7.2，真标题，首 token 金标准胜率，J-Lens 各层，合并池，Pilot50 20 对 A−B，配对 bootstrap 95% CI；图 7.2；351_stage7_2/summary/matched_ab_bootstrap.csv"),
("2026-10-30 按逐对数据重算）", None, "Stage 7.2，真标题，首 token 金标准胜率 7 层积分，合并池，20 对 A−B，配对 bootstrap 95% CI；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 \"7.2 integrated7 A-B jlens/vanilla pool=combined\""),
("156 个与金标准首 token 相同，记为平局", None, "Stage 7.2，50 篇 × 100 个错误作者，A 79、B 62、C 9、D 6；351_stage7_2/summary/quality.json \"first_token_collision_count_by_group\""),
("45.76 个不同的首 token。", "45.76 个不同的首 token", "Stage 7.2，50 篇平均；方法手册 C 部分从 351_stage7_2/candidates/pilot50_author_candidates.csv 统计"),
("全部出现在同一篇 A 论文中", None, "Stage 7.2，配对 P004；方法手册 C 部分从 351_stage7_2/candidates/pilot50_author_candidates.csv 统计"),
("种子 20261037；2026-10-30 重算）", None, "Stage 7.3，J-Lens，匹配池，去掉 P004 后 19 对，7 层积分标题优势 A−B，配对 bootstrap 95% CI；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 \"7.3 integrated7 A-B drop P004 jlens pool=matched\""),
("共 1,000 个上下文。", "共 1,000 个上下文", "Stage 7.3 设计，50 篇 × 20 个替代标题；~/jlens_work/07_3_stage7_3/351_stage7_3.py:83-91；351_stage7_3/reports/freeze_audit.md"),
("放宽引用档（179）。", "放宽引用档（179）", "Stage 7.3，1,000 个替代标题按 tier 0/1/2 计数；351_stage7_3/summary/quality.json"),
("同档 82.1%。", "同档 82.1%", "Stage 7.3，1,000 个替代标题与目标论文的差异均值和比例；351_stage7_3/summary/quality.json"),
("20 个替代标题的平均 W。", "20 个替代标题的平均 W", "Stage 7.3 定义；~/jlens_work/07_3_stage7_3/351_stage7_3_score.py:156-158"),
("论文内标题优势（右）</figcaption>", "论文内标题优势（右）", "Stage 7.3，J-Lens 各层，合并池，Pilot50 50 篇；351_stage7_3/summary/paper_null_distribution.csv"),
("种子 20261046；原区间无出处文件，2026-10-30 重算）", None, "Stage 7.3，J-Lens L56，真标题 − 20 个替代标题平均，合并池，50 篇，论文 bootstrap 95% CI；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 \"7.3 L56 J-Lens title advantage pool=combined (B=20,000)\""),
("+8.64 到 +9.99。", "+8.64 到 +9.99", "Stage 7.3，J-Lens L56 标题优势，50 篇逐一留出一篇的均值范围；351_stage7_3/recompute_2026-10-30/stage7_l56_loo.csv"),
("最终输出 +7.2 pp：", "最终输出 +7.2 pp", "Stage 7.3，Vanilla L56 / 最终输出 L63，真标题 − 20 个替代标题平均，合并池，50 篇；351_stage7_3/summary/paper_null_distribution.csv"),
("Vanilla +0.0315 [−0.0090, +0.0757]，均跨 0。", "均跨 0", "Stage 7.3，7 层积分标题优势的匹配 A−B，合并池，20 对，配对 bootstrap 95% CI；351_stage7_3/summary/integrated_ab_bootstrap.csv 行 pool=combined"),
("L32 −0.032 [−0.058, −0.006]。", "L32 −0.032 [−0.058, −0.006]", "Stage 7.3，J-Lens 单层标题优势的匹配 A−B，合并池，20 对，配对 bootstrap 95% CI；351_stage7_3/summary/matched_ab_bootstrap.csv 行 jlens_L56 / jlens_L32 combined"),
("扣除 20 标题参照后的 A−B 胜率对比</figcaption>", "扣除 20 标题参照后的 A−B 胜率对比", "Stage 7.3，Pilot50 20 对，J-Lens 与 Vanilla；351_stage7_3/summary/matched_ab_bootstrap.csv"),
("199/1,000 个替代标题的来源论文作者在错误作者池中。", "199/1,000 个替代标题的来源论文作者在错误作者池中", "Stage 7.3；351_stage7_3/summary/quality.json"),
("+0.0262 变为 +0.0283。", "+0.0262 变为 +0.0283", "Stage 7.3，J-Lens 7 层积分标题优势，合并池，50 篇均值；351_stage7_3/summary/paper_null_distribution.csv 列 title_advantage / advantage_no_source_false_overlap，方法手册重算"),
("（分别为 +0.026 / +0.032 / +0.027）", None, "Stage 7.3，J-Lens 7 层积分标题优势，作者加权 / 唯一 token / 去平局，50 篇；351_stage7_3/recompute_2026-10-30/stage7_weighting_title_advantage.csv"),
("全部跨 0（2026-10-30 重算，见 351_stage7_3/recompute_2026-10-30/）", None, "Stage 7.3，3 种加权 × J-Lens/Vanilla 的 7 层积分 A−B，20 对，配对 bootstrap 95% CI；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv 行 16–27"),
("1/21 ≈ 0.048）。", "1/21 ≈ 0.048）", "Stage 7.4 低引用分析，J-Lens L56 标题优势，0–2 档 6 篇；351_stage7_4/summary/floor_L56_low_six.csv、overview.json \"floor_low_six_L56\""),
("bootstrap 20,000 次（种子 741）。", "bootstrap 20,000 次（种子 741）", "Stage 7.4 设计；~/jlens_work/07_4_stage7_4/351_stage7_4.py:10-13"),
("−0.000046 到 +0.003494：", "−0.000046 到 +0.003494", "Stage 7.4，J-Lens − Vanilla 7 层积分标题优势，50 篇留一法；351_stage7_4/summary/overview.json \"integrated_jlens_minus_vanilla\""),
("合并标题优势 +9.34 pp，", "合并标题优势 +9.34 pp", "Stage 7.3，J-Lens L56，真标题 − 20 个替代标题平均，50 篇；351_stage7_3/recompute_2026-10-30/stage7_interval_recompute.csv"),
("3|Δ作者数|）。", "3|Δ作者数|）", "Stage 8A 设计；~/jlens_work/08_stage8/351_stage8.py:26-55"),
("种子 3518001 只用于哈希）。", "种子 3518001 只用于哈希）", "Stage 8A 设计；~/jlens_work/08_stage8/351_stage8.py:8,30,56-61"),
("高（129+）25 对。", "高（129+）25 对", "Stage 8A，可用候选对 low 194、mid 1,154、high 314；351_stage8/summary/matching_audit.json \"actual\""),
("7 个单层比较做 Holm 校正", None, "Stage 8 冻结计划；351_stage8/config/analysis_plan.json \"multiplicity\""),
("20 个匹配错误标题。", "20 个匹配错误标题", "Stage 8B 设计，种子 3518201；~/jlens_work/08_stage8/351_stage8B.py；351_stage8/config/stage8B_manifest.json"),
("共 20,200 条候选记录、4,000 条错误标题记录。", "4,000 条错误标题记录", "Stage 8B，200 金标准 + 10,000 匹配 + 10,000 随机；200 篇 × 20 个错误标题；351_stage8/config/stage8B_manifest.json"),
("不打后续 token。", "不打后续 token", "Stage 8C 设计；~/jlens_work/08_stage8/351_stage8C.py:126,360-400"),
("63,000 个上下文-模式组合全部完成。", "63,000 个上下文-模式组合全部完成", "Stage 8C，200 篇 × 21 个上下文 × 15 种模式；351_stage8C_full.log 末行 \"4200/4200\"；351_stage8/raw/stage8C_context_scores.jsonl"),
("（上下文不等于独立论文）</figcaption>", "（上下文不等于独立论文）", "Stage 8C，200 篇 × 21 个上下文；351_stage8/raw/stage8C_context_scores.jsonl"),
("种子 3518401；单位为百分点。", "种子 3518401", "Stage 8D 设计，RQ1/RQ2/RQ3 分别 +1/+2/+3；~/jlens_work/08_stage8/351_stage8D.py:9,34-49"),
("最有影响的一对 S8P094 约 +84.4 pp。", "约 +84.4 pp", "Stage 8D RQ2，J-Lens L56 匹配 A−B，100 对；351_stage8/stage8D/summary/matched_pair_differences.csv mode=jlens_L56"),
("100 对的 L56 A−B 差</figcaption>", "100 对的 L56 A−B 差", "Stage 8D RQ2，J-Lens L56；351_stage8/stage8D/summary/matched_pair_differences.csv mode=jlens_L56"),
("短标题 +4.82 pp。", "短标题 +4.82 pp", "Stage 8D，J-Lens L56 标题优势，200 篇（短标题 199 篇）；351_stage8/stage8D/summary/sensitivity.csv"),
("+4.79 [−0.24, +9.83]（99 对）。", "+4.79 [−0.24, +9.83]（99 对）", "Stage 8D，J-Lens L56 匹配 A−B，100 对（标题差 ≤10 为 99 对），配对 bootstrap 95% CI；351_stage8/recompute_2026-10-30/s8_unsourced_intervals.csv 行 \"8D paired sensitivity L56 A-B\""),
("种子 20261132，2026-10-30 重算）", None, "Stage 8E，J-Lens L56，4,000 个错误标题上下文，200 篇，论文固定效应 OLS 斜率，论文聚类 bootstrap 95% CI；351_stage8/recompute_2026-10-30/s8_unsourced_intervals.csv 行 \"8E title-token-gap slope\""),
("+2.33 pp [+1.50, +3.19]，", "+2.33 pp [+1.50, +3.19]", "Stage 8 冻结计划主终点，J-Lens 7 层积分，真标题 − 20 个错误标题平均，200 篇，论文 bootstrap 95% CI；351_stage8/recompute_2026-10-30/s8_endpoints.csv"),
("（bootstrap 双侧 p = 0.002）", None, "Stage 8 主组检验，J-Lens 7 层积分匹配 A−B，100 对，配对 bootstrap 95% CI；351_stage8/recompute_2026-10-30/s8_endpoints.csv；p = 0.0019 见 s8_holm.csv F0"),
("+2.14 到 +2.61 之间，区间全部不含 0", None, "Stage 8 逐对剔除 100 次，J-Lens 7 层积分 A−B，每次 99 对；351_stage8/recompute_2026-10-30/s8_lopo_summary.csv 行 jlens_int7 RQ2"),
("14 / 100 次的区间跨 0", None, "Stage 8 逐对剔除，J-Lens L56 匹配 A−B，n_ci_excluding_0 = 86；351_stage8/recompute_2026-10-30/s8_lopo_summary.csv 行 jlens_56 RQ2"),
("（0.17、0.19）", None, "Stage 8 F1 族，J-Lens 7 个单层匹配 A−B，100 对，bootstrap 双侧 p，B = 100,000，Holm；351_stage8/recompute_2026-10-30/s8_holm.csv"),
("在 200 篇新论文上复现", None, "Stage 8D RQ1，J-Lens L56，200 篇；351_stage8/stage8D/summary/primary_questions.csv"),
("Holdout100。", "Holdout100", "Stage 9A.1 设计，三份各 100 条；351_stage9.py:50-62；351_stage9/config/plan.json、manifest.json \"counts\""),
("CPU 内存峰值约 62.06 GiB。", "CPU 内存峰值约 62.06 GiB", "Stage 9 单条提示 7 层基准；351_stage9_benchmark_A1_7layers.log"),
("（下降但不能说明收敛）。", "（下降但不能说明收敛）", "Stage 9 正式 Fit A 第 1–4 条，每条 325/323/325/322 s；351_stage9_full_A.log"),
("约 8.6 计算小时，不含排队。", "约 8.6 计算小时", "Stage 9，按 96 × 323.75 s 线性外推；351_stage9_full_A.log"),
("20–200 篇论文。", "20–200 篇论文", "Stage 5–7 Pilot50 50 篇 / 20 对，Stage 8 200 篇；351_stage7_4/summary/overview.json、351_stage8/summary/matching_audit.json"),
("2.5% / 97.5% 百分位。", "2.5% / 97.5% 百分位", "附录 A 表所列各 Stage 脚本的 bootstrap 实现；方法手册 parts/C_stage1_9.html 各 Stage 第 4 步"),
]
out=[]
for old,at,tag in E:
    c=t.count(old)
    if c!=1: print('COUNT',c,old); continue
    if at is None: new=old+T(tag)
    else:
        assert old.count(at)==1,(old,at); i=old.index(at)+len(at); new=old[:i]+T(tag)+old[i:]
    out.append({'old':old,'new':new})
json.dump(out,open(D+'S1b.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(out))
