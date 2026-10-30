import os
os.chdir('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11')
p='stage1_11_report.html'; s=open(p).read()
SRC8='（重算脚本与结果：~/jlens_work/08_stage8/recompute_2026-10-30/、351_stage8/recompute_2026-10-30/，2026-10-30）'
R=[
# Stage 3 norm
('Frobenius 范数相近（如 L48 105.8 vs 104.9），',
 'Frobenius 范数相近（如 L48：Public 106.07 vs Self-100 105.16，float64 精确值；原记录的 105.8 / 104.9 用 float32 求和，系统性偏低约 0.25%，2026-10-30 重算），'),
# Pilot50 sampling
('种子 35150，保留 Stage 4 的 20 篇，新增 30 篇。',
 '强制纳入 Stage 4 的 20 篇（A8/B8/C3/D1；这 20 篇是 Stage 4 用种子 3514 在"组 × 引用档"内打乱后轮流抽取的），再新增 30 篇（A12/B12/C4/D2）。新增的 30 篇<b>不是随机抽样</b>：每组其余论文按 sha256("35150" + paper_id) 排序，按这个确定性的哈希顺序依次选取，并在同领域、同引用档内配对。'),
# 7.2 integrated
('7 层积分：J-Lens +0.105 [−0.012, +0.228]，Vanilla +0.106 [−0.005, +0.217]（20,000 次 bootstrap）。',
 '7 层积分（合并池，20 对）：J-Lens +0.105 [−0.012, +0.229]，Vanilla +0.106 [−0.006, +0.216]（配对 bootstrap 20,000 次，种子 20261031 / 20261032；原区间无出处文件，2026-10-30 按逐对数据重算）。'),
# P004
('去掉这一对后 7.3 匹配池 A−B 为 +0.023 [−0.018, +0.069]。',
 '去掉这一对后，7.3 匹配池 7 层积分 A−B 为 +0.023 [−0.017, +0.068]（19 对，配对 bootstrap 10,000 次，种子 20261037；2026-10-30 重算）。'),
# 7.3 L56
('L56 标题优势 +9.34 pp，新审计区间 [+4.75, +13.95]，留一法均值 +8.6 到 +10.0。',
 'L56 标题优势 +9.34 pp [+4.77, +14.00]（论文 bootstrap 20,000 次，种子 20261046；原区间无出处文件，2026-10-30 重算），留一篇论文后均值 +8.64 到 +9.99。'),
# 7.3 weighting source
('<b>候选加权</b>：作者加权、唯一 token、去平局三种方式下，合并标题优势为 +0.026 到 +0.032；6 个 A−B 区间全部跨 0。',
 '<b>候选加权</b>：作者加权、唯一 token、去平局三种方式下，合并标题优势为 +0.026 到 +0.032（分别为 +0.026 / +0.032 / +0.027）；J-Lens 与 Vanilla 各 3 个 A−B 区间，共 6 个，全部跨 0（2026-10-30 重算，见 351_stage7_3/recompute_2026-10-30/）。'),
# 8D pair sensitivity
('配对重算：去平局 +5.03 [+0.15, +9.87]，去来源重叠 +4.53 [−0.34, +9.41]，标题差 ≤10 +4.79 [−0.39, +9.80]。',
 '配对重算（配对 bootstrap 10,000 次；原区间无出处文件，2026-10-30 重算）：去平局 +5.03 [+0.23, +9.95]，去来源重叠 +4.53 [−0.15, +9.53]，标题差 ≤10 +4.79 [−0.24, +9.83]（99 对）。'),
# 8E header + note
('8E 外部事后审计（非正式完成实验）</h3>\n<p>数值来自外部报告的审计，原始 8E 脚本与中间输出尚未在 Explorer 上找到或重跑。</p>',
 '8E 事后审计（2026-10-30 已在 Explorer 上从原始 logits 重算）</h3>\n<p>原 8E 脚本没有找到。下表是从原始 logits 和冻结的候选首 token 完整重算的值：点估计与原表逐位一致，区间差异在 bootstrap 抽样误差之内。'+SRC8+'</p>'),
# 8E table
('<td>冻结的作者加权</td><td>+5.18 [2.90, 7.51]</td><td>+4.98 [0.28, 9.77]</td></tr><tr><td>唯一 token</td><td>+4.58 [2.53, 6.67]</td><td>+5.40 [1.10, 9.73]</td></tr><tr><td>去金标准平局</td><td>+5.32 [2.98, 7.70]</td><td>+5.03 [0.22, 9.92]</td></tr><tr><td>唯一 token + 去平局</td><td>+4.64 [2.56, 6.77]</td><td>+5.46 [1.10, 9.88]</td>',
 '<td>冻结的作者加权</td><td>+5.18 [2.91, 7.44]</td><td>+4.98 [0.34, 9.81]</td></tr><tr><td>唯一 token</td><td>+4.58 [2.52, 6.68]</td><td>+5.40 [1.19, 9.70]</td></tr><tr><td>去金标准平局</td><td>+5.32 [3.07, 7.72]</td><td>+5.03 [0.27, 9.98]</td></tr><tr><td>唯一 token + 去平局</td><td>+4.64 [2.53, 6.73]</td><td>+5.46 [1.19, 9.84]</td>'),
('论文固定效应斜率 +0.12 pp/token [+0.015, +0.236]',
 '论文固定效应斜率 +0.12 pp/token [+0.015, +0.240]（论文聚类 bootstrap 10,000 次，种子 20261132，2026-10-30 重算）'),
# 8A sampling
('从 6,841 篇中排除 Pilot50，在完全相同的领域和引用档内匹配 A/B，用年份和作者数排序。',
 '从 6,841 篇中排除 Pilot50，在完全相同的领域和引用档内匹配 A/B（配对代价 10|Δ年份| + 3|Δ作者数|）。选取<b>不是随机抽样</b>：所有候选对按（代价，sha256 哈希）排序，在低 / 中 / 高三段内按配额依次选取（贪心，确定性顺序，种子 3518001 只用于哈希）。'),
# 8B random pool
('每篇：第一作者金标准 + 50 个匹配错误作者 + 50 个随机错误作者 + 20 个匹配错误标题。',
 '每篇：第一作者金标准 + 50 个匹配错误作者 + 50 个"随机池"错误作者 + 20 个匹配错误标题。"随机池"并不是随机抽样，而是把非匹配的候选按 sha256 哈希排序后取前 50 个（确定性顺序）。'),
# protocol change box
('<b>协议变更</b>早期 README 把 7 层积分 A−B 定为主终点、L56 为次终点；后来的执行记录把 L56 定为主终点。需要用带日期的文件核对这次变更，而不是事后改写。',
 '<b>协议变更（待确认）</b>哈希锁定的分析计划（analysis_plan.json，2026-10-18 14:29）规定：主终点是 7 层积分的论文级标题优势和积分 A−B，L56 是"探索性的次终点"，7 个单层比较做 Holm 校正，逐对剔除列为敏感性分析。当天 21:14 的 PROTOCOL.md 改成以 L56 为主终点；这份文件是从聊天窗口粘贴生成的，改动由谁、依据什么做出，尚待确认。两种终点的结果都在下方并列报告。'),
# conclusion: add paragraph
('Stage 8 结论</b>RQ1：正确标题提升金标准作者首 token 判别，在 200 篇新论文上复现，换加权方式仍为正。',
 'Stage 8 结论</b>按哈希锁定的冻结计划：主终点 7 层积分标题优势 +2.33 pp [+1.50, +3.19]，主组检验积分 A−B +2.41 pp [+0.91, +4.00]（bootstrap 双侧 p = 0.002）。逐对剔除 100 次后，积分 A−B 在 +2.14 到 +2.61 之间，区间全部不含 0；L56 A−B 在 +4.18 到 +5.50 之间、不变号，但 14 / 100 次的区间跨 0。计划规定的 7 个单层 A−B 经 Holm 校正后只有 L62 显著（p_Holm = 0.029），L48、L56 不再显著（0.17、0.19）。p 值公式和检验族的划分计划没有写明，按 bootstrap 双侧 p 计算，详见方法手册。'+SRC8+'<br>RQ1：正确标题提升金标准作者首 token 判别，在 200 篇新论文上复现，换加权方式仍为正。'),
# E4b notes (6.11 zh)
('换成线性 probe（5 折 ridge 回归，把标题位置的表示映射到模型在 ":" 处 L63 的表示）能读出一些。',
 '换成线性 probe（5 折 ridge 回归，把标题位置的表示映射到模型在 ":" 处 L63 的表示）能读出一些。<b>说明：</b>probe 只给每位作者名字的<b>第一个 token</b> 打分，73% 的作者名以首字母开头，所以多数时候打分的是首字母；标题特异信号只减 <b>false_0</b> 这一个假标题，不是 5 个假标题的平均。'),
# 6.11 en (stale numbers + notes)
("A linear probe (5-fold ridge from the title-position state to the model's own L63 \":\" state) reads a little more: about +0.04 at L16 and +0.08 at L52–56, with target above control by +0.02 to +0.04 (CIs above zero).",
 "A linear probe (5-fold ridge from the title-position state to the model's own L63 \":\" state) reads a little more: re-checked with team folds and title reuse removed, about +0.05 at L24, +0.07 at L40 and +0.08 at L56, with target above control by +0.04 to +0.08 (CIs above zero). Note: the probe scores only the <b>first token</b> of each author's name (73% of names start with an initial, so usually the initial), and the title-specific signal subtracts only <b>false_0</b>, not the mean of 5 false titles."),
]
for a,b in R:
    n=s.count(a); assert n==1,(n,a[:60]); s=s.replace(a,b)
open(p,'w').write(s); print('applied', len(R))
