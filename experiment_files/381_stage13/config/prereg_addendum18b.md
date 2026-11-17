# Addendum 18b — LOCKED 2026-11-17: shelf map, all remaining items of prereg18_draft.md

Status: locked by the user on 2026-11-17 ("补充 18 柜子地图：锁定草稿 prereg18_draft.md，记 sha256 … 按成本顺序排队其余 GPU 项目，每项不超过 5 GPU 小时，超过的先用 300–600 篇子样本"). sha256 in prereg_addendum18b.md.sha256. The text below the line is ~/jlens_work/prereg18_draft.md verbatim (draft of 2026-11-14, sha256 of the draft file recorded in addendum18b_lock.json); every criterion marked "判据草案" / "待定" there is fixed as written by this lock.
Lock-time amendments (only these):
1. Item 3 part 5(b) (E1 + X6 at L41–47, L49, L51) was already locked as addendum 18 item 3 on 2026-11-14 and has been run (381_stage13/summary_e1x6_extra_20261114/); it is not rerun.
2. Per-item cap 5 GPU-hours: item 3 (per-cell patching) uses a 600-paper subsample of the Stage 11 sample (1,186 papers), target/control balanced within bins, fixed seed (est. 3.1 GPU-h); item 1 uses 600 papers; item 2 uses the 6 non-overlapping windows on 600 papers (step-2 sensitivity only if the first run measures under budget); items 4–6 as costed in the draft.
3. Queue order by estimated cost: item 4 → item 1 → item 6 → item 5 → item 2 → item 3. Each item: CPU precheck → tiny-model full-pipeline test → 1 shard to measure cost → rest. If a 1-shard measurement projects an item above 5 GPU-h, the subsample is reduced (not below 300 papers) and the change is logged before the remaining shards run.
4. Known before locking (stated honestly): the CPU feasibility results in 381_stage13/summary_prereg18_feasibility_20261114/ (item 1 at stored positions/layers) and all published Stage 11–13 results; no GPU output of items 1, 2, 3 (except 5(b)), 4, 5, 6 exists at lock time.

---

# 补充 18 草案："柜子地图"（shelf map）：预注册前的可行性检查

**状态：草案，未锁定（NOT LOCKED）。** 本文件不是预注册。文中引用的可行性结果都标为"预注册前的可行性检查、未预注册、探索性"。锁定前要做三件事：用户确认设计和判据，写成 `381_stage13/config/prereg_addendum18.md`，并算出 sha256。
起草日期：2026-11-14。可行性输出：`/scratch/zhang.zhiqi2/jlens/381_stage13/summary_prereg18_feasibility_20261114/`（report.md）。
存储清单见同目录 `report.md` 第 A 节；层 / 位置覆盖见 `~/jlens_work/coverage_matrix.md` 2026-11-14 补节。

## 0. 共同设计（六项通用）
- 模型、提示、打分与 Stage 10 相同：log10(1/rank)，teacher forcing，每篇论文先对全部作者、全部名字 token 取平均；另报第一作者的首 token。
- 标题条件：真标题，加 5 个元数据匹配的假标题（false_0..4）。spec = 真 − 5 个假标题的平均。干预类实验用 S = T − F，F 取 5 个假标题的平均，同时报每个假标题的最小值 / 最大值。
- 组：target / control（`group_tight`）。target − control 只在引用分箱内比较（每格每组 ≥ 30 篇，权重 n_t·n_c/(n_t+n_c)），与 Stage 10 定义相同。
- 区间：按存档的作者团队做整群 bootstrap，2,000 次；组间、条件间的差在同一组抽样上配对计算。
- 样本：可以抽 300–600 篇的子样本，在 10 个分箱内 target / control 平衡，种子固定。优先用 Stage 11 样本（1,186 篇）的子集，以便直接对照已存的 E1 / E2 / P1 / P2 / X6 / X7。
- GPU 流程：CPU 预检 → 小模型全流程试跑 → 1 个分片测实际成本 → 跑其余分片。实测预计超过 5 GPU 小时的先问用户。自检只记 WARN（数值和阈值都保留），不因容差停止；只有代码崩溃才停队列。容差至少留 4 个 bf16 单位。

## 1. 读出地图（位置组 × 层）
- **位置组**：标题 token（全部 / 内容词 / 首 / 末）、标题后的引号、年份数字、")?\n"、"Authors"、":"、名字位置（姓首 token、全部名字 token）。
- **层**：L8、16、24、32、36，L40–L52 每层，L56、L60。
- **读出**：logit lens 和 public J-lens 都只在同一套 9,137 个名字 token id 内排名（与 H3 同尺度那项的做法相同），和 probe 在同一尺度上比较（名字 token 的 ridge probe；属性 probe：年份 / 引用 / 领域）。
- **统计量**：每格的 spec（5 个假标题）和分箱内的 target − control，都用团队 CI。
- **主比较（待定）**：在不同位置组之间，比较 target − control 最早出现 CI 不含 0 的层。判据草案：某位置组在 L≤48 有 target − control CI > 0，而名字位置同层的 CI 含 0，记为"柜子先在该位置"；否则记为"没有更早的位置"。
- **可行性（已做，CPU，未预注册）**：已存状态只覆盖三处：最后一个标题 token（L16–L60，9 层）、":"（同 9 层加 L63）、名字位置（L32–L56，5 层）。结果在 `report_item1.md` 和 `item1_map.csv`。其余位置组，以及 L8、L36、L41–43、45–47、49–51，都没有存状态，需要 GPU。
- **GPU 需求**：一次前向，在 GPU 上直接算受限名次（不存残差）；或者对子样本存残差。600 篇 × 6 个条件约 0.4–0.6 GPU 小时，全体 9,108 篇约 5 GPU 小时。

## 2. 分窗口的注意力屏蔽
- 窗口：L40–L63 每 4 层一个，共 6 个不重叠窗口；敏感性分析用步长 2（11 个窗口）。
- 只断开一条边（所有头）：名字←标题、名字←尾部、尾部←标题、":"←标题、名字←":"。
- 读出 S = T − F（终输出的名字 token 损失，F = 5 个假标题的平均），target / control 分开报。已存的 E2、E2n、X7 作为"从第 l 层起全部屏蔽"的参照。
- 判据草案：某条边在某个窗口的 S 损失 CI > 0，且大于同窗口其他边的损失 → 该窗口内的信息走这条边。
- 可行性：没有存注意力权重，也没有窗口屏蔽的结果，只能用 GPU。
- 成本：每篇每个配置约 0.04 s（X7 实测每片 28 s / 13 个配置）。600 篇 × 6 个条件 × 30 个配置 ≈ 1.2 GPU 小时；1,186 篇约 2.4 小时；步长 2 的 11 个窗口、600 篇约 2.3 小时。

## 3. 逐格替换（合并补充 17 第 5(b) 项）
- 位置组（":"、名字、p5 年份十位、p9 引号、其余尾部、整个尾部）× 层（L40–L52 每层、L56、L60）。true → false_k，5 个假标题都做。
- 第 5(b) 项并入这里：E1 "整个尾部"在 L41–47、49、51 按组（A、B、U0、C）分别报。
- **硬检查（必须过才算新代码有效；没过记 WARN，继续算）**：
  - (a) 新驱动在已有的格子（"整个尾部" L48 / L52，5 个假标题）上逐行名次与已存的 `371_stage12/raw/patch_pos`、`391_groups/raw/b1_p12f/patch_pos` 完全一致；
  - (b) 在原 1,186 篇上，五标题平均恢复比例复现 0.821（L48）和 0.995（L52）（`391_groups/summary_b1_p12f/p12f_mean5.csv`），|差| ≤ 1e-6。若用子样本，(b) 由已存的逐行数据加新数据拼起来复算。
- 可行性：只有已有的格子可以在 CPU 上复算（P1 p1–p9 / names / all × L32、40、44、48、50、52、56；E1 的 15 层）；新的格子需要 GPU。
- 成本：每篇每配置 0.035–0.041 s（P1 实测每片 143 s / 84 个配置）。90 格 × 5 个假标题 = 450 个配置：300 篇约 1.5 小时，600 篇约 3.1 小时，1,186 篇约 6.1 小时（超过 5 小时，要先问）。只做 5(b)（E1 / X6 加 9 层）约 1.5 小时（见 coverage_matrix 补节）。

## 4. L57–L61 注意力 / MLP 均值消融
- 在名字位置和尾部，把 L57–L61 每层的注意力输出或 MLP 输出换成参考均值。参考均值来自独立的一半论文、5 个假标题条件下同一位置的输出，事先固定。
- 读出：终输出的 spec 损失和 target − control。P2（到 L56 为止）作为参照。
- 判据草案：MLP 消融的损失 > 注意力消融（配对 CI 不含 0）→ "后段由 MLP 写出"。
- 可行性：没有存 L57 以上的成分输出，只能用 GPU。
- 成本：10 个配置 × 6 个条件，加基线：600 篇约 0.45 GPU 小时，1,186 篇约 0.9 小时；另加一次算均值的前向，约 0.1 小时。

## 5. 标题 token 的重要性（L8–L24）
- 把标题 token 分成内容词 / 罕见词（按语料频率）/ 功能词 / 首末 token 四类。替换方式有两种：同义词替换（WordNet，或者 Qwen 生成后人工抽查）和同长度的随机 token 替换。
- 读出：L8–L24 的标题位置 probe，以及终输出的 spec 变化。用"同义词替换损失 − 随机替换损失"区分"靠意思"还是"靠字面"。
- 可行性：只存了最后一个标题 token 的状态，只能用 GPU。CPU 能做的准备只有分类 token 和构造替换表。
- 成本：每篇每个提示变体约 0.3–0.4 s（3-1 / 3-2 实测每片 128 篇 35–52 s）。8 个变体 × 600 篇 ≈ 0.55 小时；若用 Qwen 生成同义词另加约 0.3 小时；合计约 0.8–1.2 GPU 小时。

## 6. MLP 查记忆（补充 17 第 6 项 / plan_batch_20261114b 第 6 项）
- (a) L52–L56 MLP 神经元激活在真 / 假标题下的差，是否论文特有（同一神经元，团队 CI）。
- (b) 替换 MLP 输出时，只换与作者 token 嵌入（lm_head 行）对齐的子空间，与只换正交子空间对比。
- (c) 与注意力输出的分工。
- 可行性：MLP 激活没有存，(a)(b) 都要 GPU。CPU 只能先做两件事：用 `summary_alltok/vocab_rows.npz` 构造作者嵌入子空间；把已存的 L52 / L56 名字位置残差（`raw/b2_npprobe`）投影到这个子空间，看真 / 假标题的差（只是残差，不是 MLP 输出）。
- 成本：(a) 存激活约 0.4 小时，(b) 50 个配置约 0.35 小时，合计约 1 GPU 小时。仍然只写设计，不排期。

## GPU 小时估算汇总（未含排队；每个作业另加 2–5 分钟加载；以 1 片实测为准）
| 项 | 300–600 篇 | 全样本 |
|---|---|---|
| 1 读出地图（缺的层 / 位置） | 0.4–0.6 | ≈ 5（9,108 篇） |
| 2 分窗口屏蔽 | 1.2（6 窗）/ 2.3（11 窗） | 2.4 / 4.6（1,186 篇） |
| 3 逐格替换 | 1.5（300 篇）/ 3.1（600 篇） | 6.1（1,186 篇；要先问） |
| 3 只做 5(b) | — | ≈ 1.5 |
| 4 L57–61 消融 | 0.55 | 1.0 |
| 5 标题 token 重要性 | 0.8–1.2 | — |
| 6 MLP 查记忆 | ≈ 1 | — |
