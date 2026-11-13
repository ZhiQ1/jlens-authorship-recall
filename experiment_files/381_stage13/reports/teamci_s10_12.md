# Team-cluster CIs for the Stage 10-12 CIs in core conclusions C01-C24

Generated Thu Nov 12 19:22:17 2026 by `~/jlens_work/13_stage13/stage13_teamci_s10_12.py` (+ `_report.py`). CPU only, read-only on frozen outputs.

**Method.** (1) The published paper-level bootstrap CI is first reproduced by re-running the frozen estimator functions with their original seed and call order (Stage 10 rng 3511 / 3512 / 3513, Stage 11 rng 3611, Stage 12 rng 3713; outputs redirected to `summary_teamci_s10_12/replay/`). Check: reproduced lo / hi equal the published values at 3 decimals; otherwise no team CI is given for that quantity. (2) Team-cluster bootstrap: archived Stage 13 author-team ids (`stage13_cpu.group_folds`, via `stage13_c13_s10lib.team_ids`; 7,247 teams over 9,108 papers), 2,000 multinomial team draws, seed 1414, one draw per paper population; same point estimate, same citation-bin strata and within-bin weights (bins with >= 30 papers per group), same ratio-of-means for E1 / E2. For Stage 10 target + control the draw is identical to batch 3 item 3-1 (`reports/b3_3_1_report.md`), so the stored-layer values there are the same numbers.

## 1. Inventory: Stage 10-12 CIs that enter C01-C24

Already team-cluster in their sources (not recomputed): C04 P1 / P2 five-false-title mean (`R391/reports/b1_p12f_report.md`, team seed 391); C05 A - B (`R391/primary.csv`, groups_core team draw); C08 C / D (`R391/reports/b2_cd_report.md`, team seed 391); C01 3-1 layers L41-L49 (`b3_3_1_report.md`, team seed 1414). C07 (Stage 8) and all Stage 13 items (C06, C09-C15, C18-C24) are outside Stage 10-12. X6 / X7 numbers in C02 / C03 are Stage 13. Everything below was paper-level bootstrap.

## 2. Paper vs team CI side by side

| concl. | stage | quantity | n | estimate | paper CI (published) | team CI | width team/paper | replay check | decision line used | under team CI |
|---|---|---|---|---|---|---|---|---|---|---|
| C01 | Stage 10 | title-specific target - control within bin, output (final L63) | 3734 / 2182 (10 bins) | +0.207 | [+0.195, +0.220] | [+0.196, +0.220] | 0.98 | match | C01: output > 0 | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, logit L24 | 3734 / 2182 (10 bins) | +0.007 | [+0.003, +0.010] | [+0.003, +0.011] | 1.05 | match | C01: "about 0" = |est| <= 0.05; CI not used by the wording | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, logit L32 | 3734 / 2182 (10 bins) | +0.005 | [+0.000, +0.011] | [-0.000, +0.011] | 1.01 | match | C01: "about 0" = |est| <= 0.05; CI not used by the wording | unchanged (excludes-0 flips: paper pos, team zero; wording unaffected) |
| C01 | Stage 10 | title-specific target - control within bin, logit L50 | 3734 / 2182 (10 bins) | +0.007 | [+0.001, +0.014] | [+0.001, +0.014] | 1.03 | match | C01: onset "from about L50" (lo > 0) | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, logit L56 | 3734 / 2182 (10 bins) | +0.065 | [+0.050, +0.080] | [+0.049, +0.082] | 1.09 | match | C01: > 0 | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, logit L62 | 3734 / 2182 (10 bins) | +0.229 | [+0.213, +0.244] | [+0.214, +0.245] | 0.98 | match | C01: > 0 | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, public J-lens L48 | 3734 / 2182 (10 bins) | -0.044 | [-0.058, -0.030] | [-0.059, -0.029] | 1.04 | match | C01: < 0 (no mid-layer lead) | unchanged |
| C01 | Stage 10 | title-specific target - control within bin, public J-lens L57 | 3734 / 2182 (10 bins) | +0.029 | [+0.009, +0.048] | [+0.008, +0.052] | 1.11 | match | C01: J-lens positive from L57 | unchanged |
| C01 | Stage 10 | R0 papers only, title-specific target - control within bin, output | 3423 / 2151 (10 bins) | +0.199 | [+0.188, +0.212] | [+0.188, +0.212] | 0.98 | match | C01: R0-only output > 0 | unchanged |
| C02 | Stage 11 | E1 recovery (false_0, all papers), L48 | 1186 papers | +0.825 | [+0.807, +0.842] | [+0.808, +0.843] | 1.03 | match | C02: "most recovered" at L48 (lo > 0.5) | unchanged |
| C02 | Stage 11 | E1 recovery (false_0, all papers), L52 | 1186 papers | +0.996 | [+0.989, +1.003] | [+0.989, +1.003] | 0.97 | match | C02: "almost fully" from L52 (CI covers ~1 / lo >= 0.95) | unchanged |
| C03 | Stage 11 | E2 knockout loss (all papers), from L0 | 1186 papers | +0.831 | [+0.801, +0.862] | [+0.800, +0.861] | 1.01 | match | C03: large loss from L0 (lo > 0.5) | unchanged |
| C03 | Stage 11 | E2 knockout loss (all papers), from L52 | 1186 papers | +0.007 | [+0.001, +0.013] | [+0.001, +0.013] | 1.05 | match | C03: no effect from L52 (hi < 0.05) | unchanged |
| C16 | Stage 12 | F2 author-prompt lens, name position, target - control within bin, L62 | 590 / 593 (10 bins) | +0.238 | [+0.210, +0.267] | [+0.209, +0.268] | 1.04 | match | C16: only L62 positive | unchanged |
| C17 | Stage 10 | R1 papers: written - missed author, title-specific, output (paired within paper) | 495 papers | +0.199 | [+0.168, +0.232] | [+0.168, +0.232] | 1.00 | match | C17: written > missed at output | unchanged |

## 3. Replay check (paper bootstrap reproduced with the frozen code)

| concl. | quantity | published lo / hi | replayed lo / hi | max abs diff | match at 3 dp |
|---|---|---|---|---|---|
| C01 | title-specific target - control within bin, output (final L63) | +0.19535 / +0.21976 | +0.19535 / +0.21976 | 8.33e-17 | True |
| C01 | title-specific target - control within bin, logit L24 | +0.00298 / +0.01044 | +0.00298 / +0.01044 | 7.63e-17 | True |
| C01 | title-specific target - control within bin, logit L32 | +0.00007 / +0.01056 | +0.00007 / +0.01056 | 5.90e-17 | True |
| C01 | title-specific target - control within bin, logit L50 | +0.00144 / +0.01365 | +0.00144 / +0.01365 | 6.77e-17 | True |
| C01 | title-specific target - control within bin, logit L56 | +0.04956 / +0.07976 | +0.04956 / +0.07976 | 6.94e-17 | True |
| C01 | title-specific target - control within bin, logit L62 | +0.21283 / +0.24446 | +0.21283 / +0.24446 | 5.55e-17 | True |
| C01 | title-specific target - control within bin, public J-lens L48 | -0.05840 / -0.02959 | -0.05840 / -0.02959 | 9.02e-17 | True |
| C01 | title-specific target - control within bin, public J-lens L57 | +0.00905 / +0.04838 | +0.00905 / +0.04838 | 4.86e-17 | True |
| C01 | R0 papers only, title-specific target - control within bin, output | +0.18766 / +0.21228 | +0.18766 / +0.21228 | 8.33e-17 | True |
| C02 | E1 recovery (false_0, all papers), L48 | +0.80731 / +0.84219 | +0.80731 / +0.84219 | 0.00e+00 | True |
| C02 | E1 recovery (false_0, all papers), L52 | +0.98926 / +1.00342 | +0.98926 / +1.00342 | 0.00e+00 | True |
| C03 | E2 knockout loss (all papers), from L0 | +0.80056 / +0.86204 | +0.80056 / +0.86204 | 0.00e+00 | True |
| C03 | E2 knockout loss (all papers), from L52 | +0.00127 / +0.01313 | +0.00127 / +0.01313 | 0.00e+00 | True |
| C16 | F2 author-prompt lens, name position, target - control within bin, L62 | +0.20985 / +0.26728 | +0.20985 / +0.26728 | 0.00e+00 | True |
| C17 | R1 papers: written - missed author, title-specific, output (paired within paper) | +0.16842 / +0.23229 | +0.16842 / +0.23229 | 5.55e-17 | True |

## 4. Does any conclusion change under the team CI?

15 quantities; all 15 paper CIs reproduced exactly with the frozen code (max |diff| 9.0e-17). Changed: 0. Team / paper width ratio 0.97-1.11.

- C01: unchanged. Output, L50 onset, L56, L62 stay > 0; public J-lens L48 stays < 0 and L57 stays > 0; R0-only stays > 0. logit L32 (+0.005) now includes 0 under the team CI ([-0.000, +0.011]); the conclusion already calls L24-L48 "about 0" (|est| <= 0.05), so the wording is, if anything, better supported. Logit L24 (+0.007) still excludes 0 under both CIs, also covered by "about 0".
- C02: unchanged (E1 L48 0.825 still well below 1 and well above 0.5; L52 CI still covers 1).
- C03: unchanged (E2 from L52 0.007, team CI [+0.001, +0.013] still tiny and > 0; from L0 0.831).
- C16: unchanged (F2 L62 > 0).
- C17: unchanged (written - missed > 0 at output).


## 5. 方法手册段落草稿（未应用，供审阅）

**两种重抽方式：论文 bootstrap 与团队整群 bootstrap**

本项目的 95% 区间都是百分位 bootstrap（2,000 次重抽），点估计都不随重抽方式改变；两种方式只差在"重抽的单位"。

- **论文 bootstrap（Stage 10–12 已发表的区间）**：把每篇论文当作独立单位，有放回地重抽论文。分档比较（同一引用档内 target − control）时，在每个"引用档 × 组"格子内各自重抽论文，再按格子权重 n_a·n_b /(n_a + n_b) 合并；比例类指标（E1 恢复比例、E2 损失比例）按论文成对重抽分子和分母后取均值之比。各脚本用固定种子（Stage 10：3510–3513；Stage 11：3611；Stage 12：3713），可以逐位复现。
- **团队整群 bootstrap（Stage 13 起的主区间）**：同一作者团队的论文并不独立（作者重叠的论文在名字 token 上的得分相关）。团队的定义与 Stage 13 probe 分折相同：任意一位作者全名（规范化后）相同的论文并为一组，取并查集的连通块（`stage13_cpu.group_folds`，使用 2026-10-30 存档的团队编号，9,108 篇论文共 7,247 个团队；同名不同人也并在一起，偏保守）。每次重抽按多项分布有放回地抽团队，每篇论文的权重等于它所在团队被抽中的次数；同一批抽样在所有层、所有格子、所有组之间共用（因此差值和层间比较是配对的）。分档比较时，档的取舍（每组 ≥ 30 篇）和档权重与原估计完全相同，只是每个档内的均值改为按团队权重加权。
- **差别**：团队整群区间考虑了同一团队论文之间的相关，一般略宽或持平；Stage 10–12 的已发表区间宽度比（团队 / 论文）在 0.92–1.21 之间（`381_stage13/reports/cluster_ci.md`，本报告第 2 节），点估计不变。只有恰好贴近 0 的区间可能翻转"是否含 0"，例如 Stage 10 logit L32 的 target − control +0.005：论文区间 [0.0001, 0.011]，团队区间 [−0.000, +0.011]（本报告；2026-10-28 的 cluster_ci 用另一种子为 [−0.000, 0.010]）；这一层在结论中本来就按"约为 0"处理。
- **哪个 Stage 用哪种**：Stage 10、11、12 原始报告中的区间是论文 bootstrap；Stage 13 起（含补充 7–15、391_groups 的分组比较、批次 1–3，例如 3-1 补测 Stage 10 层、P1 / P2 五个假标题版、C / D 组补全）的主区间是团队整群 bootstrap。Stage 10–12 中进入核心结论的区间已在 `381_stage13/reports/teamci_s10_12.md` 用团队整群方式重算并与原区间并列；重算前先用原代码和原种子复现了已发表的论文区间（到发表的舍入位一致）。Stage 4–8（含 Stage 8 RQ1 / RQ2）仍是各自原来的论文 / 配对 bootstrap，不在本次重算之内。
