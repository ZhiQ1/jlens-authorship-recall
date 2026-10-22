# READ ME FIRST — 标题如何支持作者预测？

## 一页摘要

**问题：论文标题能否提高正确作者的读出分数？**

- 模型：Qwen3-32B。比较J-Lens、Vanilla和Final-model输出。
- 读出：先看Gold Token排名，再区分姓名首Token与正确前缀后的补全。
- 对照：固定作者候选，比较真实标题和匹配的错误标题；最后在新论文上验证。

**最强结果：Stage8的200篇新论文在L56的平均Title Advantage为+5.18个百分点；A−B平均差为+4.98个百分点，但对少数强正向配对敏感。**

不能据此声称完整作者身份恢复、因果Recall或J-Lens优于Vanilla。完整性与排除范围见 [ARCHIVE_NOTES.md](ARCHIVE_NOTES.md)。本文件引用 `docs/assets/` 中的图片，二者须一起放在归档根目录。

## 先读这里

| 你的任务 | 阅读路径 |
|---|---|
| 理解研究 | 摘要 → 概念 → 研究主干 → Stage8结果 |
| 检查证据 | Stage卡片 → 对应Report/CSV → Config/Raw |
| 接手运行 | 文件地图 → CPU练习 → ARCHIVE_NOTES与实际CLI |

## 概念速查

- **J-Lens（Jacobian Lens）**：本项目用generic文本估计的Jacobian映射，把某source layer的内部表示读向target layer表示空间，再经输出读出得到词表分数。输入是模型的中间表示；输出是Token分数/排名，不是“知识是否存在”的标签。精确归一化和映射操作以本包所用实现与配置为准。
- **Vanilla**：不使用Jacobian映射，直接按基线读出路径把中间表示转成Token分数。
- **Layers**：L16/24/32/40/48/56/62为source layers；L63是Final层，单列为Reference，七层Integrated不含它。
- **Gold / False**：真实作者候选 / 错误作者候选。后期主要比较第一位作者的首Token。
- **Wrong-title / Shuffled**：预先选定的metadata-matched替换标题（报告里的Shuffled即此类对照）【“不是字词打乱”待核对】，不是天然可交换的随机化样本。
- **Recognition**：从选项中认出作者团队的行为结果。**R0**是m=0，无匹配作者；**R1**是m>0的部分匹配。

| 行为组 | Recognition | Recall | 当前cohort N |
|---|---|---|---:|
| A | Pass | R0 | 4110 |
| B | Fail | R0 | 2186 |
| C | Pass | R1 | 511 |
| D | Fail | R1 | 34 |

**共同设置：** Qwen3-32B BF16；model revision `9216db5781bf21249d130ec9da846c4624c16137`；source layers L16/24/32/40/48/56/62。具体参数以各Stage冻结config为准。

**样本：** 共6841篇，源标签覆盖9108篇。Pilot50=A20/B20/C7/D3（20对A/B）；Stage8=200篇新论文（排除Pilot50）、100对A/B，Low/Middle/High为25/50/25对。HR2沿用标签包定义，不能自行解释为作者Recall Accuracy。当前工作没有新建Build/Tune/Test；早期matched split属于历史方案。

**三套A/B不要混用：行为A/B是Recognition分组；历史Lens A/B是50/50拟合文本；Stage9 Fit A/B是新100/100拟合文本。**

| 指标 | 怎么算/测什么 |
|---|---|
| RR | 1 / Gold Token全词表排名 |
| Full-name JMRR | 作者内Token平均，再论文内作者平均；后续Token给正确前缀 |
| Gold Win Rate | Gold首Token胜过False记录记1，平分记.5，失败记0，再平均 |
| Title Advantage | True-title Win Rate − 20个Wrong-title Win Rate均值 |
| A−B | 匹配论文对的效应差 |
| J−V | 同论文、同条件下J-Lens效应减Vanilla效应 |

## 研究逻辑主干

**分数来自哪里？** Stage4 → Stage6 → Stage7.1。  
**是否依赖正确标题？** Stage5 → Stage7.2 → Stage7.3。  
**是否一致、能否推广？** Stage7.4 → Stage8。  
Fidelity、来源审计和历史Split-half贯穿这三条线。

### Stage4 · 均值是否被少数论文拉高？
- 做法：Benchmark20，检查论文分布和单篇贡献。
- 关键数字：L56 first-listed first-token RR mean .007040（median .000920）；单篇贡献71.03%。
- 判断：均值不足以说明广泛可及，转向作者覆盖与姓名位置。

### Stage5 · 分数是否依赖标题作者对应？
- 做法：两标题×两作者交叉；Q作者与Q标题必须同源。
- 关键数字：L56 pooled logit contrast +1.16679；Integrated A−B区间跨零。
- 判断：有标题敏感性，单个False/Title参考仍过窄。

### Stage6 → 7.1 · 优势是在开始姓名前，还是已有前缀后？
- 做法：50篇、227个paper-author实例；复用逐Token评分拆分First/Continuation。
- 关键数字：A−B：First +.00137（CI跨零）；Continuation +.02064（名义CI为正）。【归档报告原文未标明层/汇总方式，待核对是否为Integrated】
- 判断：差异集中在条件补全；没有因果隔离前缀作用。

### Stage7.2 → 7.3 · Gold优势扣掉错误标题背景后还在吗？
- 做法：100 False/篇；固定候选，增加20 Wrong titles/篇。
- 关键数字：100名字平均45.76种首Token；Pilot50 L56 Title Advantage +.093435。
- 判断：总体标题效应保留，Integrated A−B仍不确定；候选首Token不是完整身份。

### Stage7.4 · 方法是否一致，J-Lens是否多提供信息？
- 做法：同50篇跨阶段相关与同论文J−V比较。
- 关键数字：L56 Pearson .445；Integrated J−V +.00221，CI跨零。
- 判断：中等测量一致性，未证明独立复制或J-Lens增量。

### Stage8 · 新论文能否保留信号？
- 做法：排除Pilot50，冻结200篇/100对、候选与标题；L56为预设主层。
- 关键数字：RQ1 +5.18 pp；RQ2 +4.98 pp。
- 判断：新目标保留平均标题效应；组差要结合影响分析读。

## 目录地图：去哪里找证据

![目录地图](docs/assets/directory_map.png)

完整性与排除范围见 [ARCHIVE_NOTES.md](ARCHIVE_NOTES.md)。下表所有输出均从 `experiment_files/` 算起，源码从 `code/scratch_scripts/` 算起。

| 内容 | 源码 | 输出入口 |
|---|---|---|
| Cohort | 351_prepare_all.py | 351_all/；labels_20261015/ |
| Stage4 | 351_stage4_readout.py；351_stage4_audit.py | 351_all/351_stage4_artifacts/ |
| Stage5 | 351_stage5.py | 351_stage5_crossed_v2/ |
| Stage6 | 351_stage6.py | 351_stage6/ |
| Stage7.1 | 351_stage7.py | 351_stage7_1/ |
| Stage7.2/7.3 | 351_stage7_2.py/351_stage7_3.py及各_score.py | 351_stage7_2/；351_stage7_3/ |
| Stage7.4 | 351_stage7_4.py | 351_stage7_4/ |
| Stage8A–D | 351_stage8.py、351_stage8B/C/D.py | 351_stage8/；8D在其stage8D/下 |

每个实验按 **config → cohort/matching/controls → raw → summary → figures/reports** 读；不同阶段不一定包含全部子目录。

## 7. 状态表

| 状态 | 内容 |
|---|---|
| 已执行且有产物、已归档 | Stage4–8D；cohort、历史拟合/validation及Split-half材料 |
| 执行身份需按run逐项核验 | 当前收集源码是否逐字对应历史执行版本；部分历史环境/参数 |
| 未执行 | Stage8E；草稿数字不作为已验证证据 |
| 本包排除、另行归档 | Stage7.1B、Stage9（归档时运行中） |

