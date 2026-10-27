# Stages 1–12：研究问题、状态、结论、路径

模型始终是 Qwen/Qwen3-32B（bf16，revision `9216db57`）。每个 Stage 的输入都是组长的标注包 `labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/`（9,108 篇论文；`00_cohort/`）。

**路径约定。**
- 代码：`~/jlens_work/<目录>/`，每个目录有 `README.md`，写明脚本、运行顺序和输出。
- 结果：`/scratch/zhang.zhiqi2/jlens/<结果目录>/`。
- GitHub：`ZhiQ1/jlens-authorship-recall`，`main` 分支。仓库里脚本平放在 `code/scratch_scripts/`，各 Stage 的 README 在 `code/stage_readmes/<目录>/README.md`，Stage 10–12 的结果在 `experiment_files/<结果目录>/`。
- 已完成的 Stage 打了 tag：`stage10-done`、`stage11-done`。

**怎么划分 Stage。**
- **Stage** 按研究问题划分。
- **Substage**（7.1、8A 这种编号）是同一个问题下的不同实验任务。
- prepare、audit、checkpoint、resume、repair 这类工程步骤不单独算 Stage，只写在所属 Substage 的说明里。
- 编号越大不代表实验越高级。实际上三种工作交织在一起：
  - **Stage 1–4**：建立测量对象（论文、标签、读出指标），先确认能不能看到内部作者信号。
  - **Stage 5–8**：排除替代解释（名字先验、tokenization、错误标题、样本选择），并用独立样本验证。
  - **Stage 9 及以后**：检验测量工具（lens 的拟合可靠性）和机制（信号在哪一层形成、经过哪些位置、能否被干预改变）。
- 最关键的衔接：Stage 4 看到作者信号，不代表信号来自正确标题；Stage 5–7 排除这类混淆；Stage 8 检查结果能否独立复现；Stage 9 反过来检查测量工具本身是否可靠；Stage 10 把 4–8 的问题放大到全部 9,108 篇论文并逐层定位；Stage 11–12 用干预确定时间和路径。

**四条论证线**（汇报按线组织；每条线都在缩小答案的范围）：

| 线 | 问题 | 依次用到的 Stage | 目前收窄到 |
|---|---|---|---|
| A 标题特异性 | 是不是"这篇论文"的知识？ | 5 → 7.3 → 8 RQ1 → 10（真 / 5 个假 / 删标题，标点阴性对照）→ 12 CPU（名字先验拆分）→ 12 N1/N2 | 不是名字好猜，也不是主题相关，是对这篇论文的知识 |
| B 读出工具 | 用什么读？ | 3 → 7.4 → 8（J−V）→ 9（换拟合数据）→ 10（三种 J-Lens）→ 11 E4（标题位置的 lens 和 probe）→ 12 CPU（probe 对照）→ 12 F1/F2 | 信息在中间层就有，但现有 lens 读不出那种形式 |
| C 在哪一层 | 何时形成？ | 4 → 10（6 层 + 细层 L50–61）→ 11 E1/E2（替换、阻断）→ 12 P2 | 读得早（L24–50），说得晚（L57–61） |
| D 在哪个位置 | 经过哪条路径？ | 6 → 7.1 → 10（token 角色、名字格式）→ 11 E1t/E2n/E3 → 12 P1 | 标题 → 标题之后的几个 token → 名字；具体是哪个 token 待 P1 |

每条线里都可以比较：目标组 vs 对照组、引用数高低、多选题答对次数。

---

## Stage 1 — Labels & Cohort

- **问题。**我们究竟研究哪些论文？怎样定义模型"记得"或"不记得"？
- **状态。**完成。标注包日期 2026-10-15，由组长的标注流程生成。
- **内容。**
  - 9,108 篇论文来自 *Dreaming Up Authors* 的评测集：OAG v2 加 Semantic Scholar，8 个领域 × 13 个引用档，每格最多 100 篇。
  - 开放回答：贪心解码；模糊姓名匹配得到 HR2，据此分 R0、R1、R2。
  - 4 选 1 多选题，按 4 种顺序各问一次，得到 `mc_team_a`。
  - Stage 4–8 用 A/B/C/D 分组（4,110 / 2,186 / 511 / 34）；Stage 10 起改用 `group_tight`（target 4,621、control 2,220、guard 214、excluded 2,053）。
- **代码。**`00_cohort/351_prepare_all.py`，以及标注包 zip。
- **结果。**`351_all/`、`labels_20261015/`。
- **Git。**`e2c7156`。
- **未解决。**开放回答的生成长度上限和 thinking 模式设置记录在标注运行的 `run.json` 里，标注包没有附带，需要向组长要。

## Stage 2 — Model & Prompt Validation

- **问题。**后续实验是不是在同一个可复现的模型和输入条件下进行？
- **状态。**完成，但没有独立的目录。
- **内容。**
  - 模型 revision 固定为 `9216db57`。
  - 提示词、tokenization 和层的设置，写在 Stage 4 的 `config/run_config.json` 和 Stage 10 的 `config/` 里。
  - Stage 10 的 parity 检查和 Stage 6 交叉核对，又把这些设置复核了一次。
- **代码 / 结果。**见 Stage 3、Stage 4 和 Stage 10 的 config。
- **Git。**`e2c7156`。

## Stage 3 — J-Lens Setup

- **问题。**能不能用中间层的隐藏状态估计最终的 token 分布？
- **状态。**完成。
- **内容。**
  - 获取、加载并验证 Neuronpedia 公开 lens：smoke、fidelity、带 offload 的验证、作者特异性。
  - 拟合自己的 self100 lens：WikiText-103 的 100 条，L24/32/40/48/56/62，dim_batch 8。
  - 早期的 split-half 检验（3.5.1）：self100 拆成 50 + 50 两半，留出集是 20 条通用文本加 20 条论文提示词。
  - 来源审计：对比公开 lens 与本地拟合的设置差异。
- **代码。**`01_public_lens_validation/`、`02_self_lens_validation/`、`03_provenance_audit/`。
- **结果。**
  - `351_all/351_public_fidelity.jsonl` 等；
  - `351_self100_validation/`、`351_self100_split_half/`、`351_self100_gold_false/`；
  - `351_provenance_audit/`；
  - 公开 lens 文件在 `public_neuronpedia/`。
- **Git。**`e2c7156`。

## Stage 4 — Author Readout

- **问题。**正确作者在模型内部有没有可读出的信号？
- **状态。**完成，2026-10-15。
- **数据和方法。**
  - Benchmark20：20 篇论文（A8 / B8 / C3 / D1），93 位作者。
  - 公开 J-Lens 和 Vanilla，L16–62，逐层计算真实作者 token 的 rank 和 score。
  - 主指标：在 ":" 处第一作者第一个 token 的 RR。
- **主要结论。**L56 的 RR 均值 .0070，中位数只有 .0009，一篇论文贡献了均值的 71%。所以只看均值，看不出信号是普遍可读的。
- **代码。**`04_stage4/`。
- **结果。**`351_all/351_stage4_artifacts/`。
- **Git。**`e2c7156`。

## Stage 5 — Crossed Title–Author Control

- **问题。**作者得高分，是因为标题对了，还是名字本身好预测？
- **状态。**完成，2026-10-15。
- **数据和方法。**Pilot50（A20 / B20 / C7 / D3），20 对 A/B。2 个标题 × 2 位作者交叉组合，在同一组 logits 上比较正确首 token 和错误首 token。
- **主要结论。**存在标题敏感性（L56 合并后的 logit 对比 +1.17），但 A−B 的置信区间跨过 0。
- **代码。**`05_stage5/`。
- **结果。**`351_stage5_crossed_v2/`。
- **Git。**`e2c7156`。

## Stage 6 — Full-author JMRR

- **问题。**从第一个 token 扩展到完整姓名后，结论还成立吗？
- **状态。**完成，2026-10-15。
- **数据和方法。**Pilot50 的 227 个"论文 × 作者"实例。用教师强制给每个名字 token 打分，计算 JMRR；读出方式为公开 J-Lens、Vanilla 和 Final，L16–62。
- **主要结论。**得到了按论文、层、引用档分开的完整姓名读出轨迹，作为 7.1 的输入。
- **代码。**`06_stage6/`。
- **结果。**`351_stage6/`。
- **Git。**`e2c7156`。

## Stage 7 — Confounder & Null Controls

- **问题。**原先的优势，能不能用 token 位置、作者先验或替换标题来解释？Stage 7 不是重复同一个实验，而是逐个排除 Stage 4–6 可能的替代解释。
- **状态。**完成，2026-10-15；7.3 的打分在 2026-10-21 完成。
- **Git。**`e2c7156`（7.1B 另行归档，不在 git 里）。

| Substage | 做了什么 | 关键结果 | 代码 | 结果 |
|---|---|---|---|---|
| 7.1 First vs Continuation | 把作者首 token 和姓名后续 token 分开分析（含 7.1B terminal） | 后续 token 的 A−B 约 +0.02064，首 token 为 +0.00137（CI 跨 0） | `07_1_stage7_1/` | `351_stage7_1/`、`351_stage7_1B_terminal/` |
| 7.2 Matched False Authors | 每篇论文 100 个真实的错误作者（50 个匹配 + 50 个随机）作为竞争候选 | 5,050 个候选，75,000 条成对评分；A−B 的 CI 跨 0；100 个名字平均只有 45.8 种不同的首 token | `07_2_stage7_2/` | `351_stage7_2/` |
| 7.3 Shuffled-title Null | 把真实标题换成 20 个按元数据匹配的错误标题 | 1,000 个错误标题上下文；L56 Title Advantage +0.0934；A−B 的 CI 跨 0 | `07_3_stage7_3/` | `351_stage7_3/` |
| 7.4 Cross-stage Audit | 对照此前各阶段的评分、样本和结论，并比较同一篇论文上 J-Lens 和 Vanilla 的差 | 测量一致性中等（L56 Pearson .45）；J−V +.002，CI 跨 0 | `07_4_stage7_4/` | `351_stage7_4/` |

## Stage 8 — Independent Validation

- **问题。**前面的探索性发现，能不能在独立的 200 篇论文上复现？
- **状态。**8A 完成于 2026-10-15，8B–8D 完成于 2026-10-20；**8E 是方案，没有执行**。
- **主要结论。**
  - 新论文上标题效应仍然存在（RQ1）。
  - A−B 差异勉强显著，而且依赖少数几对差异很大的论文（RQ2）。
  - 高低引用之间没有清楚差异（RQ3）。
  - J-Lens 没有比 Vanilla 更好。
- **代码。**`08_stage8/`。
- **结果。**`351_stage8/`（8D 在 `stage8D/`）。
- **Git。**`e2c7156`。

| Substage | 内容 | 状态 |
|---|---|---|
| 8A | 冻结此前探索阶段之外的 200 篇论文，组成 100 对匹配样本（Low/Middle/High = 25/50/25 对） | 完成 |
| 8B | 为每篇论文冻结 100 个错误作者候选和 20 个匹配的错误标题 | 完成 |
| 8C | 对真实标题和错误标题做 GPU 读出：4,200 个上下文，15 种打分模式（J-Lens / Vanilla 等） | 完成 |
| 8D | 统计和稳健性检验：True−Wrong Title、A−B、Low−High、J-Lens−Vanilla，均给出置信区间 | 完成 |
| 8E | 后续提出的审计方案（例如 token 去重） | **方案，未执行**；旧草稿里的数字不算已核实的证据 |

8D 的结果（L56 是预先指定的主层，均为 95% bootstrap CI）：

| 检验 | 效应 | 95% CI | N |
|---|---|---|---|
| RQ1 True − Wrong Title | +5.18 pp | [+2.93, +7.48] | 200 |
| RQ2 A − B | +4.98 pp | [+0.32, +9.91] | 100 对 |
| RQ3 Low − High | +2.45 pp | [−3.69, +8.60] | 50 |
| J-Lens − Vanilla | −1.38 pp | [−3.48, +0.68] | 200 |

## Stage 9 — FullFit Reliability

- **问题。**J-Lens 的结果依不依赖特定的拟合样本？换一批数据拟合，结论还稳定吗？
- **和早期 3.5.1 split-half 的区别：**

| 项目 | 早期 3.5.1 split-half（Stage 3） | Stage 9 FullFit |
|---|---|---|
| 训练集 | 原 self100 拆成 50 + 50 | 两套互不重叠的 100 + 100（WikiText-103，规范化后 sha256 去重） |
| 留出集 | 20 条通用文本 + 20 条论文提示词 | 独立的 100 条 WikiText 留出集 |
| 源层 | 6 层 | 7 层，增加 L16 |
| 目的 | 检查现有 self lens 的重复性 | 拟合数据和测试数据都独立时，检验拟合的稳定性和泛化 |
| 状态 | A/B 拟合和读出比较都已完成 | 见下表（2026-10-27 已核实） |

- **状态（2026-10-27 核实）。**只完成了 9A 的一半：Fit A。Fit B、9B、9C 都没做完。所以 Stage 9 的问题"换一批数据拟合，结论还稳不稳"**还没有回答**。

| Substage | 内容 | 状态（核实依据） |
|---|---|---|
| 9A Split-half Fitting | 分别独立拟合 Fit A 和 Fit B：L16/24/32/40/48/56/62 → L63，max_seq_len 128，skip_first 16，dim_batch 1 | **Fit A 完成**：`runner_runs/full_A_repair_101_100valid/final_status.json` 状态为 `VERIFIED_100_VALID_OF_101_CANDIDATES`（原运行里 jlens.fit 跳过 1 条，补 1 条经核验的 128 token 替补，得到 100 条有效；估计方法没有改动）。**Fit B 没做完**：检查点 `full_B_100_7layers/checkpoint.pt` 为 n_done = 66，最后写入是 2026-10-21 19:12，之后没有续跑 |
| 9B 在共同留出集上比较两套 lens | 用 `prompts/holdout.jsonl`（100 条，已冻结）比较 Fit A 和 Fit B 的读出 | **未执行**：没有任何留出集比较的结果。`reports/` 里只有 `stage9_resume_comparison.json`，是检验续跑方法的工程对比 |
| 9C 影响因素 | 提示词格式、token 类型、Final-logit anchor 等 | **未执行** |

- **Stage 10 用的 fitA 就是 Stage 9 的最终 Fit A。**Stage 10 的 `config/lenses.json` 登记的 fitA 路径是 `351_stage9/runner_runs/full_A_repair_101_100valid/lens.pt`，sha256 `4881b830…`，和 `final_status.json` 里的 `lens_sha256` 完全一致。
- **代码。**`09_stage9/`（备份）。可运行的原件在 `/scratch/zhang.zhiqi2/jlens/`，几个脚本按绝对路径互相加载。
- **结果。**`351_stage9/`。
- **Git。**不在 git 里（另行归档）。

## Stage 10 — Full-cohort Layer Readout

- **问题。**规模放大后，论文特有的作者信息在哪一层出现？目标组什么时候领先？
- **状态。**完成。2026-10-23 冻结，GPU 运行 10-24 → 10-26；细层扩展和补充分析 2026-10-26 完成。
- **数据和方法。**
  - 9,108 篇论文，33,811 个作者上下文，149,999 个名字 token。每位作者单独接在 "Authors:" 后面，用教师强制打分。
  - 7 种标题条件：真标题、5 个匹配的假标题、删掉标题。
  - 5 种读出方式：logit lens（Vanilla）、公开 lens、self100、fitA，加上 Final。层为 L24/32/40/48/56/62，另外 public 和 Vanilla 加算细层 L50–55、L57–61。
  - 指标 log10(1/rank)；标题特异信号 = 真标题 − 5 个假标题的平均；目标组 − 对照组只在引用档内比较。
- **主要结论。**
  - 论文特有的作者信息很晚才能用 lens 读出：从 L50 前后开始，L57–61 上升最快。
  - 输出处目标 − 对照为 +0.21（只用 R0 论文为 +0.20）。在名字位置，中间层没有领先。
  - 标点阴性对照约为 0。
  - J-Lens 在中间层比 Vanilla 多读出 +0.007 到 +0.030 的标题特异信号，但这部分不偏向目标组。
- **代码。**`10_stage10/`：`351_stage10.py` 已冻结，经 `351_stage10_fix1.py` 运行；补充分析在 `stage10_extra*.py`。
- **结果。**
  - `351_stage10/`：`reports/stage10_report.md`、`stage10_title_summary.md`、双语报告、`talk/`；
  - R0 敏感性：`summary_r0/`、`reports/r0_sensitivity.md`。
- **Git。**`b4b76ed` … `c739b95`，tag **`stage10-done`**。

| Substage | 内容 |
|---|---|
| 10A 主轮 | 7 个条件 × 72 个 shard × 25 组"读出 × 层" |
| 10B 细层扩展 | public 和 Vanilla 的 L50–55、L57–61 |
| 10C 补充分析 | 第一个 token 与后续 token、名字格式、引用数、lens 比较、R0 敏感性（CPU） |

## Stage 11 — Causal Interventions

- **问题。**标题信息在什么时候被读取？经过哪些位置传到名字？
- **状态。**完成，2026-10-27。
- **数据。**
  - E1/E1t/E2/E2n：593 篇目标组 + 593 篇对照组论文。只用两组都至少 30 篇的引用档，每档每组随机抽 min(60, n_t, n_c) 篇，种子 11。
  - E3/E4：全部 9,108 篇。
- **主要结论（读得早，说得晚）。**
  - 标题在 L24–50 被读进标题之后的几个 token：替换在 L48 恢复 0.83，从 L52 起恢复 1.00；从 L52 起阻断不再有影响。
  - 标题最后一个 token 本身带的信息很少（E1t 约 0.12）。
  - 在标题位置，lens 几乎读不出来（0.01–0.03），线性 probe 能读出 +0.04 到 +0.08，目标组高 +0.02 到 +0.04。
  - 作者连写时，后面的作者更好猜（+0.17 到 +0.23），合作者部分替代了标题的作用。
- **代码。**`11_stage11/`：`361_stage11.py`、`stage11_analyze.py`。
- **结果。**`361_stage11/`：`reports/stage11_report.md`、`summary/E*.csv`、`summary_r0/`。
- **Git。**`c86112f` … `746214c`，tag **`stage11-done`**。

| Substage | 内容 |
|---|---|
| E1 patch | 在假标题（false_0）运行里，把标题之后各位置的残差换成真标题运行的，一次只换一层（L24–L63） |
| E1t patch_title | 只替换标题最后一个 token（L8–L63） |
| E2 knockout | 从第 l 层到最后一层，标题之后的每个位置都不能注意标题 token，掩码对所有注意力头生效 |
| E2n knockout_name | 只挡 ":" 和名字位置 |
| E3 chain | "Authors: A1, A2, …" 连写，覆盖 7 个条件 |
| E4 titlepos | 在标题最后一个 token 上用 lens 读，并训练 ridge probe |

## Stage 12 — Localization（进行中）

- **问题。**具体是哪个 token、是注意力还是 MLP 在传递信息？专门拟合的 lens 能不能读出更多？名字先验到底有多大？
- **状态。**进行中，2026-10-27 开始。CPU 部分已完成；GPU 部分截至 2026-10-27 晚的进度见下表。原"实验五"（换一个模型）已取消，因为分组来自组长对 Qwen3-32B 的标注。
- **代码。**`12_stage12/`：`371_stage12.py`、`stage12_analyze.py`、`stage12_cpu.py`、`stage12_keeper.py`。
- **结果。**`371_stage12/`：`reports/stage12_cpu_report.md`、`summary_cpu/`；GPU 部分的报告完成后在 `reports/stage12_report.md`。
- **Git。**`13ae7ec`、`95dd94d`、`37b8b7b`、`d076bbe`，以及之后的 `main`。

| Substage | 内容 | 状态（2026-10-27 晚） |
|---|---|---|
| CPU：名字先验 A/B/C | 拆分目标 − 对照差（不给标题时就有的部分 +0.087 / 主题 −0.047 / 论文特有 +0.207）；先验与多选题的相关；名字常见程度 | 完成 |
| CPU：probe 对照 X1 | 评分时换成另一篇论文或同领域论文的作者；只用假标题训练 | 完成：probe 信号是这篇论文特有的 |
| P1 patch_pos | 逐个替换标题之后的单个位置（p9…p1、names、all），层 L32–56 | 24/24 |
| P2 patch_comp | 只替换注意力输出或只替换 MLP 输出，层 L8–56 | 15/24 |
| N1 prior_mc | 4 个多选选项在不给标题和给真标题两种提示下的打分 | 0/144 |
| N2 prior_pure | 完全不提论文的提示词（"The following is the name of a researcher."） | 0/72 |
| F1 alens_fit | 用 40 条作者提示词拟合 lens（L24–62 → L63） | 10/40 |
| F2 alens_read | 用 F1 的 lens 在名字位置和标题位置读 | 等 F1 完成 |
