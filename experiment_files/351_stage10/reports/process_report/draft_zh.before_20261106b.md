# jlens 项目过程报告（素材稿，2026-11-04）

> 用途：中文过程报告的素材汇编。每条后面的【】是出处：`P` = `~/jlens_work/PROGRESS.md` 条目（日期/时间 + 标题关键词），`S§` = `/scratch/zhang.zhiqi2/jlens/STATUS.md` 节号，`H` = `~/jlens_work/HANDOFF.md`，`手册 X` = `351_stage10/reports/methods/parts/` 下的方法手册节（B_global2 / C_stage1_9 / G_appendix 的锚点），`V##`/`U##` = 手册附录 G4/G3 编号。数字均照抄来源，未重算。路径中 `351_*`、`361_*`、`371_*`、`381_*` 均在 `/scratch/zhang.zhiqi2/jlens/` 下。

---

## 1. 数据与论证链

### 1.1 研究问题与固定设置
- 模型 Qwen/Qwen3-32B，revision `9216db5781bf21249d130ec9da846c4624c16137`，bf16，只做前向（teacher forcing），不生成。【S§1；手册 s19-common】
- 问题：模型写不出作者、却能在多选题里认出真作者名单的论文，其作者信息在网络哪一层形成、经过哪些位置、能被哪种读出工具看到？【S§1；advisor 页 `351_stage10/reports/advisor/index.html`】

### 1.2 数据：从 9,108 篇到各阶段样本
| 层级 | 数量 | 说明 | 出处 |
|---|---|---|---|
| 数据来源 | OAG v2 随机 9,999,863 → 过滤 → 1,921,209 → 8 领域 × 13 引用档、每格 ≤ 100 篇 → 9,108 | Dreaming Up Authors 代码包；原始种子 None，选择不可复现 | P 2026-10-30 16:30（DUA package）；P 2026-10-27 ~18:55 |
| 全队列 | 9,108 篇 | 组长标注包 `zhiqi_qwen3-32b_labels_2026-10-15`，主表 sha256 b4ff5e1d… | 手册 s19-s1-cohort |
| group_tight | target 4,621 / control 2,220 / guard 214 / excluded 2,053 | target = R0/R1 且 4 种选项顺序全对、真选项平均概率 ≥ 0.5；control = R0/R1 且 ≤ 1 种顺序对 | S§2 |
| 冻结四组（Stage 4–8 用） | 6,841 篇：A 4,110 / B 2,186 / C 511 / D 34 | A = target·R0，B = control·R0，C = target·R1，D = control·R1；`351_all/351_four_groups.csv` | 手册 s19-s1-cohort |
| Benchmark20（Stage 4） | 20 篇（A8/B8/C3/D1），93 位作者 | seed 3514 | 手册 s19-s4-readout |
| Pilot50（Stage 5–7.4） | 50 篇（A20/B20/C7/D3），20 对 A/B | 哈希排序（不是随机抽样），配对用最大权匹配 | 手册 s19-s1-pilot50 |
| Stage 8 | 200 篇 / 100 对（与 Pilot50 不重叠，只用 A、B） | SEED 3518001，确定性哈希排序 + 贪心 | 手册 s19-s8a |
| Stage 10 | 9,108 篇，33,811 个作者上下文，149,999 个名字 token，72 shard × 128 篇 | target − control 档内比较只用两组都 ≥ 30 篇的 10 个引用档（n_a 3,734、n_b 2,182） | S§3；手册 h-stats-bins |
| Stage 11 样本 | 1,186 篇（593 target + 593 control，10 档内平衡，seed 11，24 shard） | E3、E4 用全部 9,108 篇 | S§3 Stage 11 |
| Stage 12 F1 拟合集 | 40 篇（Stage 11 样本外，seed 12） | 3 篇评估论文与拟合集同名，F2 评估时剔除 | P 2026-10-28 12:00 |
| Stage 13 X1/X3/X4 配对 | 1,178 对（`381_stage13/config/pairs.parquet`） | 按作者团队切 tune/test | P 2026-10-28 ~08:00、11:45 |

- 标签规则：开放回答贪心解码、thinking 关、max_new_tokens 96；姓名匹配得 m/h/u，HR2 = (h+u)/(m+h+u)；HR2 > 0.5 且 m = 0 → R0，HR2 > 0.5 且 m > 0 → R1，HR2 ≤ 0.5 → R2。多选题 3 个干扰项是其他论文的真实作者团队（同领域、相近规模/引用档/年份），4 种顺序 ABDC/BCAD/CDBA/DACB。【手册 s19-s1-cohort；P 2026-10-30 16:30】
- 标签由组长的 `elm` 流程生成，elm 源码与 run.json 不在集群上；DUA 包 NameMatcher L4 复算 (m,h,u) 与标注包 9,095/9,108 一致。【P 2026-10-30 16:30；U01、U05】
- 标注包自检：0-2 档 tight 通过率 25.5%（≈ 固定偏好某选项的 25%），team_b 重抽一致率 83.6%（kappa 0.63）。【手册 s19-s1-cohort】

### 1.3 提示、打分与对照
- 读出提示（无 chat template）：`Who are the authors of the paper titled "{title}" ({year})?\nAuthors:`，其后接一个作者名，逐 token teacher forcing。Stage 11 E3 改为 "Authors: A1, A2, …" 链式。【S§2】
- Stage 1–9 指标：名次 r = 1 + logit 严格大于目标的 token 数，RR = 1/r，JMRR；Stage 10 起改为 log10(1/rank)（rank 1 → 0，最小约 −5.18），原主指标"每篇 Σ1/rank"被取代（V13）。【手册 s19-s2-protocol；S§2；V13】
- 标题条件（Stage 10）：true、5 个元数据匹配的假标题 false_0..4（代价 |Δyear|/5 + |Δn_authors| + |Δtitle tokens| + 1.5·|Δcitation bin|，分级 strict 35,898 / medium 1,638 / loose 2,565 / nearest 5,439）、delete。标题特异信号 = true − 5 个假标题均值；total = true − delete；topic = 假标题均值 − delete。【S§2】
- 读出：logit lens、public（Neuronpedia，557 条 WikiText-103）、self100（L24/32/40/48/56/62）、fitA（Stage 9，L16–62）、final L63。三把 Jacobian lens 都拟合在通用文本上。【S§2】
- 统计：档内加权 w ∝ n_t·n_c/(n_t+n_c)，论文 bootstrap B = 2,000；Stage 13 起（补充 2）作者团队整群 bootstrap 为主；Stage 10–13 没有多重比较校正，规则是"所有层都报告"。【手册 h-stats-strat、h-stats-boot、h-stats-mult】

### 1.4 四条论证线及每阶段要排除什么
| 论证线 | 问题 | 小样本 Stage | 全量 Stage |
|---|---|---|---|
| A 这篇论文？ | 信号针对这篇论文，还是名字本身好猜 | 5、7.2、7.3、8 | 10 标题特异信号；11/12 名字先验、probe 对照；13 X3 |
| B 读出工具 | 不同工具各能看到什么 | 3、7.4、8、9 | 10 三把 Jacobian lens + logit；11 probe；12 作者提示 lens；13 M2、X4 |
| C 哪一层 | 何时出现、何时被使用 | 4、7.2、7.3、8 | 10 细层；11 替换/阻断；12 P1/P2；13 X5–X7 |
| D 哪个 token | 名字和提示哪一部分带信号 | 6、7.1 | 10 名字格式与角色；11 标题之后的 token |
【advisor 页"怎么系统地做"；P 2026-10-27 ~19:30 STAGES.md】

### 1.5 结论如何被修订（主线）
1. Stage 4：均值被单篇驱动（L56 最大单篇占 71.03%）→ Stage 5 起加对照设计。【手册 s19-s4-readout】
2. Stage 5–8：真标题优于错误标题（Pilot50 L56 +9.34 pp；Stage 8 L56 +5.18 pp），A − B 在 Stage 8 RQ2 为 +4.98 pp 但对少数大对敏感（去 10 对变号）；冻结主终点（7 层积分）+2.33 / +2.41 pp；Holm 后逐层只有 L62 通过。【手册 s19-s73、s19-s8d】
3. Stage 10（全量）：中间层 L24–L48 标题特异信号 ≈ 0，从 L50 起爬升，target − control 输出 +0.207；"认得出的论文中间层先知道"不成立。【S§3 Stage 10】
4. Stage 11：因果干预显示论文信息在 L24–L50 已离开标题、进入标题之后的位置，早于名字位置可读（L56–62）→ 结论改为"读得早，说得晚"。【P 2026-10-27 08:17】
5. 复核（10-28）：E4b probe"用假标题训练更强"是泄漏，撤回；"搬到标题之后的 token"经 P1 + X6 改写为"从 L24 起在标题位置逐渐形成，在 L44–L52 汇集到名字位置"（再于 11-03 定为"信息在 L44–52 进入名字位置，部分经由标题之后的 token"）。【P 2026-10-28 13:30；P 2026-10-30（report v19）；P 2026-11-03 08:20】
6. Stage 13：中间层"表示什么"——M3 按补充 2 重判不支持 H2；X3 不能把语义与论文身份分开；X4 顺序与 H2 相反、可能是文本可解释 → H2"部分支持但未确立"，H3"证据不足"（11-03 统一措辞）。【S§0；P 2026-11-03】

---

## 2. 实验过程（按阶段）

### Stage 1 · 队列与标签（继承）
- 日期：标注包 2026-10-15；`00_cohort/351_prepare_all.py`（CPU）2026-10-17 运行。输出 `351_four_groups.csv`（6,841 行）。Git e2c7156。【手册 s19-s1-cohort】
- 之后：10-27 发现 target 含 11% R1（control 1.5%），措辞由"写不出"改为"写不全（R0/R1）"，并做 R0-only 敏感性。【S§2 后 10-27 evening；P 2026-10-27 ~19:30】

### Stage 2 · 模型、提示、打分协议
- 无独立目录和脚本，协议散在 Stage 4/5/6 的 config；Stage 5 helper sha256 4fd4c9fb…c339 在 7.1B、8C 中复核一致。【手册 s19-s2-protocol】
- 问法选择过程未记录、未系统比较（U11，用户决定写法）。

### Stage 3 · J-Lens 搭建与验证（Exp 1–7）
- Self-100：WikiText-103 前 100 条，6 层，dim_batch 8，max_seq_len 128，H200 拟合（10-17/18，约 5.7 h 墙钟，4 次续跑；最后一段在 H200 d4054 作业 11180979）。【手册 s19-s3-exp0、h-compute-hw】
- 公共 lens 任务验证：`351_validate_public_lens.py` 40GB 卡 OOM、`…_offload.py` meta tensor 报错，`…_offload_fixed.py`（29 层上 GPU）跑通（V01）。
- 结果：Exp 2/4 Self-100 在 6/6 通用层、5/6 论文层 KL 更低；Exp 3 两 lens 互不占优；Exp 5 Self-100 与评估提示 0 重叠，Public 无法核对；Exp 7 split-half 余弦 L24 0.678 → L62 0.99985。【手册 s19-s3-exp24 至 exp7】
- 10-30 重算范数（作业 11500587）：已发布的"L48 105.8"是 Public lens float32 值（float64 106.07）。【手册 s19-s3-exp1；V02】

### Stage 4 · Benchmark20 读出
- 2026-10-15（报告生成 10-18），20 篇 93 作者，平均 90.68 s/篇，GPU 峰值 29.5 GiB。L56 J-Lens 第一作者 RR 均值 0.00704、中位数 0.00092，最大一篇占 71.03%。【手册 s19-s4-readout】

### Stage 5 · 交叉标题 × 作者（Pilot50）
- 2026-10-15，50 篇，约 11.5 s/篇。全部 50 篇 J-Lens L56 +1.167 [+0.533, +1.838] logit；匹配 A − B 7 层积分 +0.081 [−0.426, +0.648]。【手册 s19-s5-crossed】

### Stage 6 · 全作者全 token 条件 JMRR
- 2026-10-15，227 作者、972 token、14,580 行；复用 Stage 4 20/20。7 层积分 A 0.0849 / B 0.0683；匹配 A − B 只有 L62 区间不含 0（J-Lens +0.0966 [+0.0282, +0.1630]）。【手册 s19-s6-jmrr】

### Stage 7 · 排除替代解释
- 7.1（CPU）：差异在后续 token（7 层积分 A − B +0.0206 [+0.0022, +0.0385]），首 token ≈ 0。
- 7.1B：只完成 1,166 / 15,519 上下文，最后作业 11296093@d1029 于 10-22 08:31 被用户账号结束（距时限约 23 min），未分析（V04，U23 待确认）。
- 7.2：每篇 1 金标准 + 100 错误作者（5,050 候选、75,000 行）；J-Lens 合并池 A − B L48 +0.193 [+0.071, +0.318]；7 层积分区间原无出处，10-30 重算 +0.105 [−0.012, +0.229]。
- 7.3：每篇 20 个错误标题（1,000 上下文），7.3A 冻结 10-18 11:49；L56 标题优势 +9.34 pp，重算区间 [+4.77, +14.00]。
- 7.4（10-18）：J-Lens − Vanilla 积分标题优势 +0.00221 [−0.00753, +0.01241]，J-Lens 没有多读出标题信息。【手册 s19-s71 至 s19-s74】

### Stage 8 · 200 篇独立验证
- 8A 冻结 10-18 14:29（analysis_plan.json：主终点 = 7 层积分）；PROTOCOL.md 10-18 21:14 改 L56 为主；8B 冻结 21:25；8C 打分 21:47 起，4,200/4,200 上下文，约 6.1 s/条，最后写入 10-20 09:05；8D 10-20；supplement 10-21（分支 3a4f605，10-30 合入 main a4c1f0a）。【手册 s19-s8-protocol 至 s19-s8dsupp】
- 结果：RQ1 L56 +5.18 pp [+2.93, +7.48]；RQ2 +4.98 pp [+0.32, +9.91]（去 10 对 −0.39）；RQ3 +2.45 [−3.69, +8.60]；J − V −1.38 pp。冻结主终点 RQ1 积分 +2.33 [+1.50, +3.19]、RQ2 积分 +2.41 [+0.91, +4.00]。
- 10-30 事后补算（作业 11500770，CPU）：Holm（B = 100,000）计划族 7 个逐层 A − B 只有 L62 通过（p_Holm 0.029）；LOPO 积分 A − B 100/100 区间不含 0，L56 A − B 14/100 跨 0；8E 从 8C 原始 logits 重算，点估计与报告相同。【P 2026-10-30 13:00；手册 s19-s8d、s19-s8e】

### Stage 9 · FullFit 拟合可靠性
- 9A.1（10-18）：WikiText-103 train → fit_A/fit_B/holdout 各 100，random.Random(3519001)。
- Fit A：7 层，dim_batch 1，约 325 s/prompt，单条峰值内存约 62 GiB；第一段 A100-40GB（d1026，11191976），其余 A100-80GB；索引 66 的提示只有 14 token 被跳过，修复协议 A_APPEND_ONE_V1 追加 1 条替补，最终 VERIFIED_100_VALID_OF_101，lens sha 4881b830…，完成于 10-22 05:33，即 Stage 10 的 fitA。
- Fit B：停在 66/100（作业 11289356 到 2 h 时限，10-21 19:12 最后写检查点，可续跑），用户 10-30 决定答辩前不补（V10，U33）。9B、9C 未实现（V11、V12）。【手册 s19-s9-*、h-compute-table】

### Stage 10 · 全量逐层读出（10-23 冻结 → 10-26 完成）
- 设计：9,108 篇 × 7 条件；logit + public 于 L24/32/40/48/56/62 及扩展 L50–55、57–61；self100、fitA 于 6 层；final L63。主轮 504 个单元，扩展 11,088 个文件。【P 2026-10-23；P 2026-10-23 night】
- 代码：`10_stage10/351_stage10.py`（冻结，sha256 校验）；GPU 经 `351_stage10_fix1.py`；池化 `stage10_pool.py`、`stage10_steal.py`、`stage10_guard.py`；预检 `stage10_preflight.py`。【S§3】
- 作业：parity 11334054（崩溃）、11338000（ext PASS）、11347585（main FAIL @0.25）、11350174（重复，逐位相同）；决策门 s10_decision 11363838；调度器 s10_pool 11363842 → 11374266；guard 11371880；主/扩展 GPU 作业 11363844–11363863；分析 11373362（main）、11375853（title）、11378377（ext）。全部 1×A100-80GB（`--constraint=a100@80g`）。【P 2026-10-24 ~13:30 至 2026-10-26 08:21】
- 时长（shard 秒数合计，不含加载）：主轮 6.31 h（~45 s/shard），扩展 5.87 h。【手册 h-compute-table】
- 进度：10-25 22:32 首次拿到 4 张卡；main true 约 20 min 完成；main 7/7 于 10-26 ~03:00；扩展 11,088/11,088 于 10-26 06:22；ext 分析 16 min。【P 2026-10-25 22:52；2026-10-26 03:20、08:21】
- 结果（S§3 Stage 10）：L24–L48 ≤ 0.05；logit target − control L50 +0.007 [0.001, 0.014]、L56 +0.065、L60 +0.178、L62 +0.229；public L48–54 为负，L57 起为正；输出处标题特异 target − control +0.207 [0.196, 0.220]（只看真标题 +0.247）；L62 target +0.56、control +0.24；标点负对照 ≤ 0.014；Spearman ρ（引用档）0.45；与 Stage 6 交叉核对 972 token、id 完全一致。
- 额外 CPU 分析：X1–X3（作业 11376473）、名字格式（11376890：73% 首字母开头，首字母 target − control +0.048，后续 +0.253）、R0-only（会话内运行，在交互作业 11371284 中）、R0/R1（11429580：R0 视角 +0.199 [0.187, 0.212]，C − A +0.110 始于 L56）。结论不变。【P 2026-10-26 ~05:00、~05:20；P 2026-10-28 ~00:00；U35】
- 之后：10-26 13:10 更正——self100/fitA 只有 6–7 层，细层需重新拟合；提出 patching / chain / knockout 三个方向 → Stage 11。【P 2026-10-26 ~13:10】

### Stage 11 · 替换、阻断、作者链（10-26 13:40 → 10-27 07:40）
- 设计：E1 尾部 patching（false_0 运行里逐层替换为 true 运行的残差，L24–L63）、E2 注意力阻断（l 起后续位置不看标题，l = 64 为基线）、E3 作者链；补充 1（10-27）加 E1t（只换最后一个标题 token）、E2n（只阻断 ":" 与名字位置）、E4 标题位置 lens、E4b ridge probe。共 1,033 个单元。【P 2026-10-26 ~13:40；P 2026-10-27 补充 1】
- 预检：CPU preflight 8/8，tiny 模型干跑 10/10 → 20/20，作业内 smoke gate，真实权重 CPU 检查 11396804（120G/16 CPU，REALCHECK PASS 13/13，26 min）。【P 2026-10-26 ~15:10、~21:30；P 2026-10-27 06:17】
- 作业：6 个 s11w（11385963/71/75/78/79/80），14 个 Stage 10 剩余池作业交接（`logs/accept_stage10_jobs`），keeper 11401810，分析门 11385983，guard 11371880 + 11385981（GUARD_PREFIX=s11）。实际计算由 11363847–11363851（d1029，交接）完成，shard 合计 4.66 h。【S§3；手册 h-compute-table】
- 结果：E1 恢复 L24 0.08 → L40 0.29 → L48 0.83 → L52 起 1.00；E2 损失 L0 0.83 → L40 0.14 → L48 0.06 → L52 起 ≈ 0；E2n ≤ 0.15；E1t ≈ 0.12（L8–40）→ 0（L56）；E4 lens ≈ 0.01–0.03；E4b +0.04 至 +0.08；E3 后续作者原始增益 +0.17 至 +0.23，标题特异 −0.05 至 −0.16。target 与 control 时间相同，target 信号约 2 倍（0.42 vs 0.21）。【P 2026-10-27 08:17；S§3】
- 之后：报告 §6.11、talk、GitHub 746214c；10-28 复核 E4b 泄漏 → Stage 13 重算。【P 2026-10-27 ~15:00】

### Stage 12 · 位置/组件 patching、名字先验、作者提示 lens（10-27 15:10 → 10-28 ~20:00）
- 单元 408：P1 patch_pos 24、P2 patch_comp 24、N1 prior_mc 144、N2 prior_pure 72、F1 拟合 40 prompt（L24–62）→ F2 alens_read 144；CPU `stage12_cpu.py`（作业 11413574）。【P 2026-10-27 ~15:10】
- 队列：keeper s12_keeper 11413494，guard 11413501，分析门 s12_analyze 11413617；首批 s12fit 11413569、11413557，s12w 11413572/84/86/91；12 个 Stage 10/11 剩余作业交接（`371_stage12/logs/accept_handover`）。【同上】
- GPU 时长：单元 4.42 h；F1 拟合 ~269 s/prompt × 40 ≈ 3.0 h（10-27 15:28 → 10-28 17:12）。【手册 h-compute-table】
- 结果（S§3 Stage 12）：P1 ":" 到 L52 +0.172，全部名字位置 L52 +0.85；P2 注意力 L48 +0.231，MLP L52 +0.178、L56 +0.224；N1 无标题时真名单"最像"0.255（机会 0.25）；N2 名字先验约占真标题差距 19%；F2 名字位置 L24–L56 target − control ≤ 0，只有 L62 +0.238。
- 之后：U40 P2 hook 显式检查（10-30/31，见第 4 节）通过；F1 对半拟合不做（V50）。

### Stage 13 · 中间层若不是名字，那是什么（10-28 07:15 → 11-02）
- 假设：H1 任务/格式，H2 论文身份，H3 不在词表方向的作者信息。【P 2026-10-28 ~07:15】
- 预注册：prereg.json（sha256 18409398…）+ 补充 1–5；实际写入时间 10-28 10:39 / 10:50 / 11:05 / 11:41 / 11:55 EDT 与 10-30 22:42（补充 5，sha256 181c72f7…b113ab）；文件内 written 字段是手填错误（U18）。【手册 h-prereg-files】
- CPU 部分：M1/M2（11438885）、M2 加年份控制（11439283）、M2b（11441993）、M2c BERT（11443232）、团队切重跑（11443403）、团队 CI（11443686/11443696）、E4b 复核（11443587）、M3 分析（11472899）、X1/X4 分析（11472859）、X6 分析（11461197）、X7 分析（11470524）、X3 分析（11521572）、X5（11-02，CPU，无作业）。
- GPU 部分（经 Stage 12 → 13 交接）：X6 xf_patch、M3 task、X1 xpatch、X4 pscope、X3 para_gen、X7 ko_false，合计 4.41 h（10-28 19:46 → 10-29）；X3 para_run + U40 0.23 h（10-31 07:05 → 09:59，作业 11513313、11385978）；follow-up x4tok/judge（11485349、11500083、11500437、11501072）。共 289 个 GPU 单元。【手册 h-compute-table；P 2026-10-31 10:15】
- 主要结果：
  - M1：中间层 Jacobian lens top-1 全是标点/格式 token，logit lens 是垃圾吸引子；名字状 token 从 L51–52 起。【P 2026-10-28 08:30】
  - M2：标题最后 token 年份 R² 0.39（L16）→ 0.56，log 引用 0.28 → 0.53，认得出 AUROC 0.62 → 0.67，领域准确率 0.69–0.72。【P 2026-10-28 09:35】
  - M2c：BERT 认得出 AUROC 0.63 ≥ Qwen − 0.05 → 认得出与否大部分可由标题本身预测。【P 2026-10-28 13:30】
  - M3（10-31 按补充 2 重判）：标题位置 T − T(L4) < 0，I − I(L4) 处处 < 0 → 不支持 H2；":" 位置任务特定。【P 2026-10-31 01:00】
  - X1：L24–L48 任务无关；相对随机 C 重算判定不变，L48 a − year +0.019 [+0.012, +0.026]。【P 2026-10-31 00:00】
  - X3：G′ − G′(L4) 在 L28–L40 +0.06 至 +0.16（峰值 L36 +0.159 [0.146, 0.171]）；起始层 L8（主）/ L24（敏感性）→ 不稳健；行为 para − D +0.239；预注册判"存在身份信号"，事后文本基线（mpnet 在匹配 D 子集 ≈ Qwen）与 target/control 无差别 → 降为"语义表示，不能与论文身份区分"。【P 2026-10-31 10:15、11:22；P 2026-11-02】
  - X4：第一作者 L8 起可解码（+0.046，主要在姓上 +0.066），年份 L40，领域读不出；名首 token 上 BERT 基线 +0.088 ≥ Qwen +0.018 → 不能排除文本解释。【P 2026-10-29 09:30；P 2026-10-30 15:00】
  - X6：5 个假标题 R(L48) 0.821、R(L52) 0.995（全部），各标题与 false_0 差 ≤ 0.02 → Stage 11 时间结论成立。【P 2026-10-29 00:55】
  - X7：S(L52) target 0.018、all 0.029 成立；control 0.051 [0.033, 0.068] 差 0.001 未过 0.05。【P 2026-10-29 07:40】
  - X5：层序——标题属性与第一作者 token ≤ L8–L16；尾部 patching R ≥ 0.5 于 L48、≥ 0.95 于 L52；阻断从 L52 起无代价；lens 读出名字 L53–L62；预注册 top-1 检索曲线未算（V56）。【P 2026-11-02 10:27】
- 状态：M4 = Stage 12 F1/F2；M5 并入 X4/放弃；X2 用户暂停。【S§0】

---

## 3. HPC 实操（Northeastern Explorer）

### 3.1 节点、分区与 QOS
- 登录节点会杀掉 torch 重进程或长进程，计算一律 sbatch / srun 到 `short`（`--account=cs7980.202710`）。【CLAUDE.md；H】
- 分区（sinfo）：courses 1 d、gpu 8 h、sharing 1 h（A100-40GB）、short 2 d；没有 long 分区。【P 2026-10-27 02:40】
- 提交上限：gpu 8 提交 / 4 运行、gpu-short 8 / 2（2 h 时限）、gpu-interactive 4 提交 / 2 运行（2 h）；每作业 GPU 数 gpu-short 2、gpu/gpu-interactive 1。【P 2026-10-23 ~21:00；P 2026-10-28 04:30；S§4】
- 硬件：A100-80GB 只在 d1028/d1029（共 8 张）；d1026 为 3×A100-40GB；Qwen3-32B bf16 权重 65.5 GB，单张 80GB 可放；2×V100-32GB 放不下。Stage 10–13 GPU 日志全部为 A100-SXM4-80GB（37 次单卡、2 次双卡）。【S§4；手册 h-compute-hw；P 2026-10-28 ~08:00】
- 总用量（sacct，10-15 起）：申请到 GPU 的作业 135 个，约 124.3 GPU-h；交互式 bash 69 个 89.4 GPU-h（Stage 3–9），s10p_* 43 个 21.1，s12w 12 个 9.2 等；CPU 作业 97 个。【手册 h-compute-hw】

### 3.2 Claude 自身的运行方式（srun → relay）
- tmux 会话 `cc` 在登录节点 explorer-01；Claude 跑在 `srun -p short --account=cs7980.202710 -c 2 --mem=8G -t 2-00:00:00 --pty bash` 里，再 `cd ~/jlens_work && claude --continue`。【CLAUDE.md Session】
- `~/jlens_work/claude_relay.sh`（10-27 02:40）：循环 srun，作业在 09:00 结束（1–2 天后，分钟数上限 2875），结束后 60 s 重启，并用提示让 Claude 重读 STATUS.md / PROGRESS.md、重建每小时检查。自动启动 tmux 窗口的尝试被权限分类器拒绝，由用户手动启动。【P 2026-10-27 02:40；脚本本身】
- Claude 自己的作业在 CPU 分区，不占 GPU 提交名额。会话内 cron 检查随会话消失，新会话需重建。【P 2026-10-27 03:10；S§6 第 7 条】
- 手机/笔记本通过 ssh 后输入 `cc`（`ssh -t explorer-01 tmux attach -t cc`）接入；`jstat` 显示队列与进度。【CLAUDE.md】

### 3.3 sbatch 模板与常用参数
- GPU 工作者（例 `11_stage11/stage11_work.sbatch`、`10_stage10/stage10_pool_job.sbatch`）：`--gres=gpu:a100:1 --constraint=a100@80g --nodes=1 --cpus-per-task=8 --mem=96G`，`--mail-user=zhang.zhiqi2@northeastern.edu`；导出 `HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1`；先 `nvidia-smi` 记录 GPU 型号。（注：这两个工作者文件写的是 `--mail-type=FAIL`，CLAUDE.md 规则写 END,FAIL。）
- 提交方式：`sbatch --partition=<gpu|gpu-short|gpu-interactive> --time=<min> --export=ALL,BUDGET=<min-15> stage11_work.sbatch`。【H Stage 11】
- CPU keeper / gate（例 `12_stage12/stage12_keeper.sbatch`）：`--partition=short --account=cs7980.202710 --time=1-23:50:00 --signal=B:USR1@600`，bash trap 收到 USR1 后杀掉 python、sbatch 下一轮（ROUND < 6，约 12 天）。测试：12 分钟作业收到 USR1 后 23 s 起下一轮（11402179 → 11402218）；第一次测试失败只因脚本在节点本地 /tmp。【脚本；P 2026-10-27 03:10】
- `--export` 按逗号切分：列表改用 ":"，脚本里 `${SHARDS//:/,}` 还原。【S§4；stage10_pool_job.sbatch】

### 3.4 作业链与门控
- Stage 10 初版链：parity → 工作者 w0/w1（`--dependency=afterok`），工作者 440 min 停下自我重提交，最后一个提交 analyze（MODE=main 再 MODE=title）；parity FAIL 时工作者停在 DependencyNeverSatisfied。gpu-interactive 主块用 `--dependency=afterok:11347585?afterok:11350174`（任一 parity PASS 即放行）。【H "How the pipeline runs"；P 2026-10-24 ~15:40】
- 扩展自动化：gate `s10x_wait`（11337857）等主轮分析完成，再提交 ext parity 与 ext 工作者，最后 ext analyze 先快照到 `snapshot_main_round/`。【P 2026-10-23 night】
- 决策门 `s10_decision` 11363838：parity.json 总状态 PASS 才结束 OK，所有 GPU 块 afterok 依赖它；Slurm 只在作业 eligible 后才累积 age 优先级（无 ACCRUE_ALWAYS；age 权重 5000/7 天 ≈ 30/h）。【P 2026-10-25 ~11:00】
- 分析门：s11_analyze 11385983（remaining = 0 时运行）、s12_analyze 11413617。

### 3.5 池化、认领与交接
- `stage10_pool.py`（s10_pool）：保持 gpu + gpu-short（后加 gpu-interactive）提交位填满，每个作业拥有不相交的 chunk；单实例锁，通过 `--comment=track|cond|shards` 收养孤儿作业；FAILED 且 ExitCode 0:9 记为 killed，到 12 次才停；PAUSED 存在时不提交。状态 `351_stage10/logs/pool/state.json`。【P 2026-10-23 ~21:00、2026-10-26 00:15】
- 工作窃取 `stage10_steal.py`（`logs/pool/steal_mode`）：作业忽略自己的 chunk，加载模型一次后按 main true → false_0..4 → delete → ext 取下一个单元；认领 = 原子 `mkdir logs/pool/claims/<unit>`，owner 不在 RUNNING 即视为过期接管。3 个假作业测试 41/41 无重复。【P 2026-10-25 ~22:10】
- 交接链：Stage 10 池作业找不到工作 → Stage 11（`361_stage11/logs/accept_stage10_jobs`）→ Stage 12（`371_stage12/logs/accept_handover`）→ Stage 13（`381_stage13/logs/accept_handover`）。新规则：下一阶段必须在当前阶段用完之前接进交接链。【P 2026-10-27 ~18:25；P 2026-10-28 ~07:15】
- Stage 11 认领加固：输出写临时文件再 `os.replace`；owner 原子写入，空 owner 10 min 后才算过期；3 轮 × 6 并发 × 300 单元 300/300 唯一。【P 2026-10-27 03:10】
- Keeper：s11_keeper 11401810 每 10 min 用 90 min 的 s11w 填满 gpu 8 / gpu-short 8 / gpu-interactive 4；s12_keeper 11413494 先填最空的分区，并保持一个 s12fit 排队。【P 2026-10-27 02:50；P 2026-10-27 ~15:10】
- Stage 12 `work()`：`try_fit()` 让任何作业在拟合空闲时接手作者 lens 拟合（需 ≥ 20 min 预算，有 fit_error 则跳过），CPU mock 测试 9/9；10-28 起只有单卡 ≥ 70 GB 才接拟合，2×40GB 只做前向单元，非 A100 只做 prior 单元并先跑 parity（WARN）。单元崩溃写 `logs/broken_<type>.json`、释放认领、只禁用该类型。【P 2026-10-27 ~18:45；P 2026-10-28 04:30；P 2026-10-27 ~15:40】
- 预算控制：`work()` 把预算封顶为已用时间 + `squeue %L` − 8 min（`slurm_minutes_left()`），作业在时限前干净退出。【P 2026-10-27 02:30】

### 3.6 Guard：PAUSED + scontrol hold
- `stage10_guard.py`（11371880，后加 11385981 前缀 s11、11413501 前缀 s12）：每 60 s 查 sacct，GPU 作业 120 s 内结束（日志写 "nothing left to claim" 的除外）→ 写 `logs/pool/PAUSED`、在 PROGRESS.md 顶部写 ALARM、发 S10_ALARM_PAUSED 邮件、`scontrol hold` 所有待运行 s10p_*/s11w 作业（不取消）。恢复：`mv logs/pool/PAUSED logs/pool/PAUSED_resolved_<date>`，再 `scontrol release`。回放 sacct 历史可抓到全部 19 次快速退出。【P 2026-10-25 ~22:15；guard 源码】
- Stage 11 smoke gate 失败时 `stop_queue()` 同样写 PAUSED 并 hold；10-27 起 PASS/WARN 都继续，只有 ERROR（代码崩溃）才停。【P 2026-10-26 ~21:30；P 2026-10-27 03:10】

### 3.7 自检体系
1. CPU preflight：Stage 10 30/30（作业 11371865，提示编码与冻结 id 一致、lens sha、17 个权重文件、真实作业命令跑到"no GPU visible"）；Stage 11 8/8。【P 2026-10-25 ~22:15】
2. tiny 模型干跑：64 层随机小 Qwen3 + 真 tokenizer。Stage 11 10/10 → 20/20；Stage 12 14/14；Stage 13 14/14 → 26/26 → 27/27 → 31/31；Stage 13 全流程测试 48/48（claim → 计算 → 保存 → 日志 → 读回）。【P 各阶段条目；P 2026-10-28 23:30】
3. 作业内 smoke gate / 复现核对：Stage 11 smoke.json；X6 false_0 shard 0 与 Stage 11 逐值相同（516 × 15）；X7、U40 hook 检查等。
4. 真实权重 CPU 检查：11396804 REALCHECK PASS 13/13。
5. 规则（10-28 固定）：先 tiny 全流程；新脚本先 1 个真实 shard；日志/进度出错只记 WARNING；结果列名集中在一个模块；sbatch 报错后先查 squeue/sacct；改完 PPT/报告重新渲染截图；工作副本放 /scratch。【H "Fixed rules"】
6. 容差原则：parity/一致性未达标记 WARN 继续算（10-27 起长期规则），容差至少留几个 bf16 单位（|logit| 32–64 时间隔 0.25）；唯一例外是 x4tok 自检被用户定为致命的正确性检查。【CLAUDE.md；手册 h-compute-tol】

### 3.8 权重加载与断点续跑
- from_pretrained 经 mmap 读 /scratch 约 35 MB/s（加载 25–30 min）；顺序读 617 MB/s → `fix1.load_model` 先用 4 线程顺序读 17 个分片（65.5 GB），之后 from_pretrained 44 s；作业约 3–5 min 进入第一个 shard。【P 2026-10-25 ~22:10、22:52】
- 输出 `raw/<readout>/L<layer>/shard_k.npz`，已存在即跳过，重提交总是安全；Stage 9 拟合每条 prompt 存检查点。【H；手册 s19-s9-fitA】

### 3.9 Fairshare、backfill 与时限调整
- 优先级以 fairshare 为主：Stage 10 约 20 GPU-h 后 fairshare 约 1,776（他人 > 10,000）；10-28 fairshare 0.090，优先级约 4,900（age 580 + fairshare 1,801 + jobsize 2,500）；10-31 优先级 4516 = age 70 + fairshare 1886 + job size 2500。【S§4；P 2026-10-28 11:05；P 2026-10-31 02:10】
- 时限调整（均为 `scontrol update TimeLimit`，不取消）：10-27 20 个待运行作业改 90 min；10-28 改 60 min；10-31 s11w 1:00 → 0:45；11511973 1:00 → 0:30，11511965 1:45 → 0:40；另提交合并作业 11513313（gpu-interactive 0:50，两步各自非致命、各自跳过已完成）。【P 2026-10-27 02:30；P 2026-10-28 11:05；P 2026-10-31 02:10、08:20】
- 10-28 无 A100-80GB 4.5 h：用户批准后把 11414108、11428778 改为 `gres/gpu:a100:2` 并去掉 80g 约束。【P 2026-10-28 04:30】

### 3.10 Git 同步
- 仓库 https://github.com/ZhiQ1/jlens-authorship-recall，本地克隆 `/scratch/zhang.zhiqi2/jlens-authorship-recall_update`（SSH deploy key）。`python ~/jlens_work/sync_to_git.py` 显示差异，`--push -m "msg"` 提交推送；代码进 `code/scratch_scripts/`，结果进 `experiment_files/`，跳过 raw/ 与 > 50 MB parquet，刷新 SHA256 清单，`git add -f` 冻结 parquet。【P 2026-10-27 sync_to_git；README.md】
- 作者规则：只署 `Zhiqi_ <zhang.zhiqi2@northeastern.edu>`，无 Claude 署名；10-27 经用户批准重写 6 个提交并 `--force-with-lease`（新 head 5a14006，本地 tag backup-before-rewrite）。【P 2026-10-27 history rewritten】
- 标签：stage10-done → c739b95，stage11-done → 746214c，defense-2026-11（11-02，11-03/11-04 移动）。【P 2026-10-27 ~19:30；P 2026-11-03、11-04】

### 3.11 文档流水线
- 两份"活文档"（10-28 起只更新这两份）：合并报告 QB335qoaBWvSdFyfvc2bSe（最终 v26）与合并 PPT XcgK4YF2dYQxudWfhk8MsD（最终 v16）；另有方法手册 W7r7xVte3eaNcbo8D8cybo 与下载页 5Tdt1mQa8xnPiqQEKvjzta。【S§0、10-28 note】
- 报告：`stage1_11/src/build_report.py` 合并、`edit_vNN.py` 逐版修改，备份 `*.before_*`/`.vNN.html`；PDF 用 headless Chromium（playwright，浏览器在 `/scratch/zhang.zhiqi2/pw`），`reports/tools/export_pdf_a4.py`；最终 report v26 82 页 8.5 MB。【P 2026-10-28 19:00；P 2026-11-03】
- 讲稿：`talk/src/charts.py` + `build.py` → LibreOffice（soffice）PDF → pymupdf 1920×1080 JPEG 嵌入合并 PPT；`export_deck.py` 出 slides/notes PDF；可编辑 pptx 原由 `build_editable.py`（DOM 抽取），集群上缺输入，v14 起改用 `patch_editable_v14/15/16.py` 修补 v11 pptx。v16：54 页，slides 11.8 MB、notes 12.9 MB、editable 4.0 MB。【P 2026-10-28 19:10；P 2026-11-02 10:45；P 2026-11-04】
- 方法手册：`methods/build_methods.py` 合并 parts A–J，检查重复 id、断链、自检；最终 PDF 290 页 9.5 MB。【P 2026-10-30 18:10；P 2026-11-03】
- 每次修改后重新渲染截图核对（固定规则 6）。

---

## 4. 遇到的问题与调整

格式：日期｜问题｜原因｜处理｜对结果的影响

### 4.1 工程问题
1. 10-22｜7.1B 停在 1,166/15,519｜作业 11296093 被用户账号在时限前约 23 min 结束｜未续跑，由 Stage 10 覆盖｜计划未做（V04）【手册 s19-s71b】
2. 10-21｜Stage 9 Fit B 停在 66/100｜作业 11289356 到 2 h 时限（加载 18 min 且部分 offload）｜不补做｜计划未做（V10）【手册 s19-s9-fitB】
3. 10-23｜3 个调度器重复提交（11338002/033/068）及重复 gate 11337853/57｜调度器无单实例锁｜加锁 + `--comment` 收养；`.pool_active` 让重复 gate 无害；不 scancel｜无（重复 chunk 跑到时直接 NOTHING TO DO）【P 2026-10-23 ~23:40、~21:00】
4. 10-24｜parity 11334054 崩溃 `AttributeError: … 'hf_device_map'`｜transformers 5.19 单卡模型不设该属性｜`351_stage10_fix1.py` 包装 + `jlens/_stage10_compat.py` 兜底，冻结脚本不动｜无输出，重提 11347585【P 2026-10-24 ~13:30；V15】
5. 10-25｜main parity 在 0.25 下 FAIL（10/25 对，max 0.367 在 final@L63）｜一次前向 vs 逐前缀前向的 bf16 累加顺序，约 1–1.5 ulp；两次运行逐位相同｜用户批准放宽到 0.5，只在 CPU 上重判，parity.json 加 `tolerance_amendment`；之后 parity 必须 `--tol 0.5`｜无重跑；事后定容差，作为偏离公开说明（V14）【P 2026-10-25 ~01:20、~22:00；手册 h-compute-tol】
6. 10-25 00:22–00:31、~07:10｜19 个池作业拿到 A100 后数秒退出｜池只按 ext parity 放行，`run()` 检查总状态 FAIL（设计错误）｜决策门 11363838；guard 11371880｜无数据，损失排队位置【P 2026-10-25 ~15:00、~21:40】
7. 10-25｜加载 25–30 min｜mmap 读 /scratch 约 35 MB/s｜顺序预读 617 MB/s，加载降到约 1 min｜仅速度【P 2026-10-25 ~22:10】
8. 10-26 00:04:37｜同节点 3 个作业被 SIGKILL（11363844/54/60，ExitCode 0:9）｜推测是节点作业结束清理（未证实）｜调度器把 0:9 记为 killed，12 次才停；认领过期接管｜每作业丢一个进行中的 shard，自动重做【P 2026-10-26 00:15】
9. 10-26｜d1028 被 squeue 看不到的分配占用（cpu=2, mem=48G, gres/gpu=4）｜推测为隐藏/管理分配｜等待｜延迟【P 2026-10-26 00:55】
10. 10-26｜s10x_wait 11369477/78 FAILED｜提交 ext parity 时遇 `QOSMaxSubmitJobPerUserLimit`｜无需处理（ext parity 已 PASS）｜无【P 2026-10-26 04:41】
11. 10-26｜Stage 11 干跑发现 `_smoke` 假定完整 `C.papers`｜测试路径 bug｜修复；改 smoke 判据（跨 kernel 比较用 rank 一致 ≥ 0.75、|Δlog10 rank| ≤ 0.05）｜GPU 前修复【P 2026-10-26 ~15:10】
12. 10-27｜认领竞争：4 作业测试 200 单元出 202 个认领｜读者看到写到一半的空 owner 当作过期｜owner 原子写，空 owner 10 min 才过期｜GPU 前修复【P 2026-10-27 03:10】
13. 10-27 05:20｜Stage 11 smoke WARN：ko 基线 0.70、patch_title L63 = false 0.70｜批 12 与批 1 的 GEMM 舍入不同；CPU 上精确｜E1t 改用同批 L63 元素作基线（原值存 `false_batch1`）；E1 批噪声约 0.01 写入报告｜无（V16、V47）【P 2026-10-27 05:20】
14. 10-27 07:32–07:35｜5 个作业 9–76 s 退出｜Stage 11 已完、Stage 12 代码未写，无下一阶段｜规则：下一阶段先接入交接链｜无【P 2026-10-27 ~18:25】
15. 10-27 ~15:40｜Stage 12 P1 首个单元崩溃（作业 11371622）｜8/9 token 尾部 `np.concatenate` 项数不同；干跑两篇尾长相同未覆盖｜固定项集 + `valid` 掩码，干跑加 8/9 token 论文 14/14；单元崩溃改为只禁用该类型；PAUSED 改名、release 11 个作业｜修复后重算（V19）【P 2026-10-27 ~15:40】
16. 10-27 18:45｜拟合只能由 s12fit 作业做，其他卡会空闲｜设计缺口｜`try_fit()` 任意作业接手｜无【P 2026-10-27 ~18:45】
17. 10-28｜无 A100-80GB 4.5 h｜集群繁忙；V100 2×32GB 放不下 65.5 GB｜scontrol 改两作业为 2×A100；非 80GB 作业只做部分单元并先跑 parity（WARN）；`stage12_v100.py` 写好未用｜无（V20）【P 2026-10-28 04:30】
18. 10-28 20:20｜Stage 13 交接作业在日志行崩溃 `KeyError: 'paper_id'`（11385971、11405680；也有 11414120）｜xf_patch 输出用 `row_id`｜只改日志行（备份 `381_stage13.py.before_logfix_20261028`），计算不变；guard ALARM 当时漏看，10-29 03:30 才按步骤恢复（release 8 个作业）｜无（崩溃在 save 之后，false_1 shard 1–4 已保存）【P 2026-10-28 20:35；P 2026-10-29 03:30】
19. 10-28｜Stage 13 `dry()` 从未跑过 work/save/log/读回｜测试覆盖不足｜新全流程测试：11459551 发现 2 个测试工具 bug，修后 11459594 PIPELINE PASS 48/48｜无【P 2026-10-28 23:30】
20. 10-29 11:05、10-31 09:59:58｜guard 误报（11385963 40 s、11385979 11 s）｜作业无事可做而退出，guard 找不到 s11w 日志（log None）未识别豁免｜PAUSED 故意保留（没有剩余单元），s11w 被 hold；guard 是冻结脚本不改｜无【P 2026-10-29 13:45；P 2026-10-31 10:15】
21. 10-29｜会话 scratchpad 丢失（报告/讲稿工作副本、extract.js、pylib）｜relay 换节点后 /tmp 为空｜重做，固定规则 8：工作副本放 /scratch｜无（已发布版本与 git 安全）【P 2026-10-29 10:10】
22. 10-29｜`/scratch/zhang.zhiqi2/pylib` 部分安装拉入 numpy 2.4｜依赖冲突｜`--no-deps` 重装到 pylib2；旧 pylib 经用户批准删除｜无【P 2026-10-29 10:40、12:40】
23. 10-29｜X7 分析 11470471 崩溃｜自检里 `D.T` 是 pandas 转置｜改 `D['T']`，自检只 WARN，重跑 11470524｜无（V44）【P 2026-10-29 07:40】
24. 10-29｜X4 报告出现 "Lnan"｜格式化 bug｜修复后重跑 11472901｜无【P 2026-10-29 09:30】
25. 10-29｜sbatch 超时（exit 124）｜控制器忙｜sacct 显示已排队，不重提（11475014）｜无【P 2026-10-29 12:10】
26. 10-29｜follow-up tiny 测试 11485182 失败｜`apply_chat_template(…, return_tensors='pt')` 返回 BatchEncoding｜修复，11485266 PASS｜无【P 2026-10-29 20:40】
27. 10-30｜x4tok 自检 FAIL（11485349，max |diff| 0.068 > 0.05）｜原 X4 一次注入 7 层（batch 7），x4tok 用 batch 2 → bf16 舍入｜同时算 b7 与 b2；用户定为致命检查；11500083 b7 逐值相同，全量 11500437 4,712 个值相同，L8 平均 D 差 0.0006｜无（V40）【P 2026-10-30 03:30、11:50、15:00】
28. 10-30 11:20｜"Unexpected message received" 后三次提交都生效（11500083/101/099）｜squeue 滞后数分钟｜两个 hold；后按用户明确指示 scancel 11500099、11500101｜无【P 2026-10-30 11:20、11:50】
29. 10-30｜group_folds 分折随 CPU 不同｜pandas value_counts（numpy 1.26.4 不稳定快排）在 AVX-512 节点（d0026/d0027）给出不同分折（6,713/9,108 篇）｜审计作业 11511921–11511930、11512064；所有原始运行都在非 AVX-512 节点且与存档一致；group_folds 改为读存档 npz｜无重跑；只有已标 BAD 的小测试 11501115 不一致（V48）【P 2026-10-30 17:30、23:00】
30. 10-30｜辅助代理违反 rm 规则（删 tiny 输出 `shard_000.csv`、一个 .pyc）｜未先询问｜向用户报告；之后坏输出一律改名保留｜无【P 2026-10-30 11:20、17:30】
31. 10-30｜3 个辅助代理撞到 5 小时 API 用量上限｜外部限额｜重置后用 SendMessage 继续｜延迟【P 2026-10-30 15:00】
32. 10-31｜单独排队的 para shard 与 U40 作业长时间不启动｜fairshare 低｜缩短时限 + 合并作业 11513313；按用户指示 scancel 11511973、11511965｜无【P 2026-10-31 02:10、全条】
33. 10-31｜U40 hook 检查唯一 WARN：full_false 相对批量 none −0.0118（界 0.01）｜批量与单条差 0.64 logit，bf16 批大小舍入｜记 WARN，U40 判通过｜无【P 2026-10-31 07:15】
34. 10-29｜X7 不屏蔽元素只有 60% 行与 Stage 11 false run 相同｜批量舍入（平均 |Δlog10 rank| 0.0105，无偏）｜WARN｜无【P 2026-10-29 07:40】
35. 10-28｜build.py 引号截断字符串、重复 sbatch、漏 pptx 项｜粗心｜形成 HANDOFF 固定规则 1–7｜无【H Fixed rules】
36. 11-02｜`build_editable.py` 在集群上缺输入；集群没有中文字体｜环境｜`patch_editable_v14.py` 修补；X5 图用英文标签｜无【P 2026-11-02 10:45、10:27】
37. 10-27｜relay 自动启动被权限分类器拒绝｜被视为未授权持久化｜用户手动启动｜无【P 2026-10-27 02:40】
38. 收尾｜s11w 11405916、11385980（11-02）与 s10_guard 11548189/11570133/11577283（11-04）｜无剩余工作｜均按用户明确指示 scancel｜无【P 2026-11-02；P 2026-11-04】

### 4.2 方法问题
1. 10-23｜原主指标 Σ1/rank 只看前几名｜指标设计｜分析层改为 log10(1/rank)，raw 存名次｜重新分析（V13）【V13】
2. 10-18（10-30 追查）｜Stage 8 主终点从 7 层积分（14:29 冻结）改为 L56（21:14 PROTOCOL.md），无书面决定｜改动在打分前、但在 pilot 看过 L56 之后｜补算冻结主终点（supplement +2.33/+2.41），10-30 补 Holm/LOPO；决定者与依据仍待确认｜报告两套终点（V06、U28）【手册 s19-s8-protocol】
3. 10-30｜7.2、7.3、8D、8E 的若干区间在原输出中找不到｜原脚本/输出缺失｜作业 11500770 等从原始数据重算，点估计相同，原区间落在 Monte-Carlo 范围内｜改用重算值（V05、V09）【P 2026-10-30 13:00】
4. 10-30｜Pilot50/8A/8B 写成"随机抽样"｜实为 sha256 哈希排序｜措辞改为"哈希排序"｜措辞【P 2026-10-30 13:00】
5. 10-30｜Stage 3"105.8"被误读为 split-half A 半｜手册旧稿错误｜作业 11500587 重算：Public L48 float32 值｜措辞（V02）
6. 10-26｜§6.7"信号多不在首 token"｜来自首字母开头的名字（Simpson 效应）｜按名字格式拆分（11376890）｜结论修订【P 2026-10-26 ~05:20】
7. 10-27｜target 含 11% R1｜分组合并 R0/R1｜R0-only 与 R0/R1 分层（输出 +0.199）｜结论不变；措辞改"写不全（R0/R1）"【P 2026-10-27 ~19:30；P 2026-10-28 ~00:00】
8. 10-28 11:45｜probe 切分泄漏：M2 false_0 有 2,004 个 donor 标题跨折；2,319 对论文共享全名跨折｜按论文随机分折｜union-find 团队分折（group_folds），重跑 11443403；补充 1 判 paper-split 的 false_0 数字无效；团队整群 CI（380 行中 4 行翻转，均在 0 附近）｜false_0 数字作废（V23）；主结果不变【P 2026-10-28 11:45、14:30；手册 h-leak】
9. 10-28｜":" 位置年份 probe R² 0.98｜提示里已有年份｜只作阳性对照；citations/recognition 加 year-only 基线；新实验用无年份等长模板｜降级（V24）【P 2026-10-28 ~08:00、09:35】
10. 10-28｜E4b 标题复用（title reuse）：probe 训练见过测试论文 prompt 中的标题｜分折设计｜确认版 = 团队折 + 剔除复用，保留 1,863 篇（896/499）；"用假标题训练更强"（+0.068/+0.081/+0.094）撤回，修后 +0.050/+0.057/+0.074｜一项结论作废（V18），target − control 保留【P 2026-10-28 13:30；P 2026-10-28 17:55】
11. 10-30｜E4b 标准化用了全部论文（含测试折）｜`stage10_extra_r0r1.py:244`、`stage11_analyze.py:176`｜训练折标准化重算 11500917，最大差 0.0075，无翻转（L44 下界 +0.000 边界）｜复核通过（V49）【P 2026-10-30 15:40】
12. 10-28｜F1 拟合集与 F2 评估集有 3 篇同名作者｜按论文而非团队隔离｜评估时剔除（`alens_eval_exclude.json`），不重拟合（省约 4 GPU-h）｜无修前数字（V22）【P 2026-10-28 12:00】
13. 10-28｜6.11"搬到标题之后的 token"/"notebook"措辞｜P1 显示信息主要在名字位置、":" 至多约 17%｜标 待复核，P1 + X6 后改写（report v19，11-03 再定稿）｜措辞【P 2026-10-28 13:05、14:05；P 2026-10-30】
14. 10-28 14:45｜补充 4：所有结果限定为 teacher forcing 下的偏好，不是生成；单模型｜审读｜写入局限｜措辞【P 2026-10-28 14:45】
15. 10-29｜X3 词 Jaccard 只保留 > 3 字母、无词形还原（symmetric ≠ symmetrical，#3 得 0.00）｜分词函数｜jaccard2（停用词表、任意长度、轻度词干），写入补充 5，D 预先计算｜para_run 前修复（V35）【P 2026-10-29 12:40】
16. 10-29｜X3 改写：27 条与原标题相同；44 条拒绝中 37 条是姓氏子串误拒（"li" in "application"）｜自动检查｜27 条排除，37 条维持拒绝（保守）｜写入补充 5（V36）【P 2026-10-29 04:40】
17. 10-29/30｜意义检查：NLI 漏掉 #3/#15/#4、误拒 4 条；Qwen 判断器 v1 一致率 0.37；v2 在 B 组 0.55 < 0.80｜阈值/顺序不对称；自评偏差｜判断器不用，走备用方案（40 条人工标注：改意思 6/40 = 0.15 [0.071, 0.291]），NLI 只定敏感性集合｜V37、V46【P 2026-10-29 13:45；P 2026-10-30 03:30、15:00】
18. 10-29｜X4 kNN 文本基线阳性对照失败（TF-IDF −0.025、BERT −0.159）｜多数第一作者在队列中只出现一次，精确姓匹配太稀｜改用监督式 textbase2（11475517）｜kNN 结论不成立（V38）【P 2026-10-29 13:10】
19. 10-30 11:40｜textbase2 bug：821 篇无 given_first 的论文经 OOV 分支计入 D_text（BERT 平均 +0.027）；给用户的消息还混用了 2,442 与 357 两个计数｜代码 + 转述错误｜CPU 按实际角色重算（BERT +0.048、given_first +0.088），更正后告知用户｜结论不变（V39）【P 2026-10-30 11:40】
20. 10-30｜X4 L8 作者信号主要在姓上，名首 token 上 BERT 基线 ≥ Qwen｜文本可解释性｜结论写为"不能排除文本解释"（用户批准）｜措辞【P 2026-10-30 15:00、23:00】
21. 10-31｜M3 自动判定按绝对阈值判 H2，未纳入 T − T(L4)｜实现与补充 2 不符｜`stage13_m3_verdict2.py` 重判 → 不支持 H2；旧段标 SUPERSEDED｜结论翻转（V28）【P 2026-10-31 01:00】
22. 10-31｜X1 random C 只打 NULL FLAG；给辅助代理的说明误写 ±0.02（补充 2 为 ±0.1）｜实现不全 + 转述错误｜相对 C 重算（11512702），C 完全抵消，按 ±0.1 判定不变；±0.02 下 L48"未定"｜无翻转（V31）【P 2026-10-31 00:00、01:00】
23. 10-31｜X3 预注册判"存在身份信号"，但事后文本基线与 target/control 无差别｜补充 4 判据不含文本基线｜两者都报告，列为偏离（V54）；起始层不稳健（V55）；按 token 角色报告做不到（V51）｜降级解读【P 2026-11-02】
24. 10-30｜prereg 文件内 written 字段比真实写入晚 20 min – 2 h 45 min｜会话手填错误｜以 mtime/git 为准，答辩引用 git 时间｜无（U18）【P 2026-10-30 12:30】
25. 10-30｜报告写"去掉作者 ≥ 20 位"｜代码是保留 1–20、只去 > 20（MAX_AUTHORS = 20）｜报告 v21 更正｜措辞【P 2026-10-30 16:30、23:00】
26. 10-28 17:55｜probe 样本数"~1,800"与"1,395"并存｜同一数据两种计数｜统一写"1,863（896 target、499 control）"｜措辞【P 2026-10-28 17:55】
27. 10-30/11-01｜转录错误被手册核对发现：姓首 token CI 下界 0.046 → 0.045；report v23 matched-D 恢复 0.73 [0.57, 0.89] → test 0.75 [0.56, 0.97]，敏感性行若干数｜手抄错误｜改正并重新发布（report 版本 25）｜改正数字【P 2026-10-30 23:00；P 2026-11-01】
28. 10-26 13:10｜self100/fitA 没有细层｜只拟合 6–7 层｜写入局限，next step 改为阻断实验｜措辞【P 2026-10-26 ~13:10】
29. 11-02｜X5 预注册 top-1 检索曲线未算｜以 M3 I − I(L4) 代替｜列为偏离｜V56【P 2026-11-02 10:27】
30. 11-03｜H2/H3 措辞在报告、手册、PPT 间不一｜多轮修改｜统一为"H2 部分支持但未确立，H3 证据不足"｜措辞【P 2026-11-03】

---

## 5. 主要发现汇总（STATUS §0 / report v26 / advisor 页）
1. 真标题有帮助且针对这篇论文：Pilot50 L56 +9.3 pp；Stage 8 L56 +5.18 pp [+2.93, +7.48]；冻结主终点 +2.33 / +2.41 pp，Holm 后逐层只有 L62。全量标题特异信号 L62 约 0.44；名字先验约占 target − control 差距的 1/3（N2 按无标题提示 35%，纯先验 19%），姓第一个 token 上约为 0。【advisor 页；S§3】
2. "认得出"的优势真实但只在最后几层：档内 target − control 中间层 ≈ 0，输出 +0.207（R0-only +0.199）；从 L50 爬升，L57–L61 最陡；随引用数单调上升（ρ = 0.45）。【S§3】
3. 论文信息从 L24 起在标题位置逐渐形成，L44–L52 进入名字位置（部分经由标题之后的 token）：E1/X6 L48 恢复 0.82、L52 0.995；阻断从 L52 起论文特有损失 0.029（control 0.051）；名字位置单独 L52 0.85，":" 至多 0.17；注意力 L48、MLP L52–56。【advisor 页；S§3 Stage 11/12；P 2026-10-29】
4. 读出工具在中间层读不到"这篇论文的作者"：lens L24–L48 ≈ 0；F2 作者提示 lens 到 L62 才区分；标题位置 probe 少量信号（L24 +0.050、L40 +0.061、L56 +0.075），只打首 token。【advisor 页】
5. 标题位置表示论文属性（年份 R² 到 0.56、引用到 0.53、领域约 0.70），":" 位置表示任务；M3 不高于 L4，不能说明超出文字。【advisor 页；P 2026-10-31 01:00】
6. X3：中间层表示改写后的意思（L36 +0.16），但分不出是否"认出论文"。【P 2026-10-31】
7. X4：第一作者 L8 起可解码，可能来自标题文字；年份 L40，领域读不出，顺序与 H2 相反。【P 2026-10-30】
8. 名字内部：73% 作者首字母开头，信号在姓上（+0.253 vs 首字母 +0.048）。【S§3】
- 假设：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 证据不足。全部结论是相关性/teacher forcing 下的偏好，单模型。【S§0；advisor 页"局限"】

---

## 6. 未做 / 作废 / 偏离（附录 G4 V01–V56 摘要）
- 计划未做：V04 7.1B；V10 Fit B；V11 9B；V12 9C；V20 V100 路径；V21 N2 层剖面；V29 M5；V32 X2（暂停）；V47 E1 同批无替换基线；V50 F1 对半拟合；V51 X3 按 token 角色；V56 X5 top-1 检索。
- 作废/失败运行：V01 Stage 3 两次验证；V15 parity 11334054 与 19 个池作业；V18 "假标题训练更强"；V19 P1 首次运行；V23 M2 paper-split false_0；V37/V46 判断器 v1/v2；V38 X4 kNN 基线；V44 X7 分析 11470471。
- 被取代/修订：V03 split-half → Stage 9（未完成）；V06 Stage 8 主终点；V13 Σ1/rank；V14 容差 0.25；V16 E1t 基线；V17 E4b 原措辞；V22 F1 改为评估时剔除；V24 ":" 年份降为阳性对照；V26 M2c 单向；V27 M3 原规则；V30 X1 选层；V35 X3 Jaccard/G；V39 textbase2 D_text；V40 x4tok b2。
- 事后补算/复核通过：V02、V05、V07、V08、V09、V25、V28、V31、V33、V34、V36、V41、V43（有偏离）、V48、V49。
- 仍待复核：V42（X4 recognition 用 min_n = 10、无 tune/test；X1/X4/X6/X7/M3 只给团队版区间）。
- 其他偏离：V45 文档与代码不符（STATUS 代价公式省分母、"≥ 20 位"、para_gen chat 模板说法、7.3 日期）；V52 X3 n 少于补充 5（1,110/1,012）；V53 ":" 位置 L4–L8 不解读；V54 X3 事后分析；V55 起始层不稳健。
【手册 G_appendix ap-void】

---

## 7. 尚待确认的问题（STATUS §0；附录 G3）
- 向组长：U01 run.json / elm 版本 / open_results_noise；U03 多选题 thinking 与答案位置（开放题已确认 thinking 关）；U04 panel.py 名字切分；U06 干扰团队抽取（容差、种子、共同作者排除）；U07 "et al." 截断；U10 Stage 1 标注运行配置（加载、batch、GPU、时长）。
- 向用户：U21 Exp 1–7 编号来源 docx（在笔记本上）；U23 7.1B 是否有意放弃；U28 Stage 8 主终点 7 层积分 → L56 的决定者与依据（影响唯一的确认性检验）；U14 public lens 模型/语料 revision（需问 Neuronpedia）；U34 Stage 10 冻结 sha 847e7dde 与运行版 9107c80b 之间的改动。
- 部分解决：U14、U23（如上）、U03。
- 已知局限（不再补做）：单模型；teacher forcing；Fit B 未完成，lens 稳定性只有 Fit A 一份证据；F1 未做对半拟合；X2 未做。

---

### 附：本稿未能找到出处或刻意未写的内容
- Stage 4/5/6/7.1 的"2026-10-15"是用户给定日期，HPC 文件 mtime 为 10-18（P 2026-10-27 Stage 4–8 dates）；7.3 打分 STAGES.md 写 10-21，与 mtime（10-18 13:56）不符。
- Stage 1–9 的交互作业号大多无法逐一对应实验（约 15 个作业无法追溯，U20）。
