# S6 issues (Stage 13 M3/X1/X4, X3, X5, Stage 13 plan section)

138 entries / 138 tags. Validator: `S6: 138 entries, 138 tags, 0 problems`.

## (a) Numbers that could not be sourced

None of the numbers is left without a source. Two notes:
- 第二个 warn box 第 5 条 "（例如 L52 有 13 篇超出 ±5）": no report or PROGRESS entry has this number. I recomputed it from `361_stage11/raw/patch/shard_*.npz` + `351_stage10/cohort/name_tokens.parquet` with the stage11_analyze estimator (paper means). Result: 13 papers with |per-paper ratio| > 5 at L52. The same run reproduces 0.996 (ratio of means), median 0.988, mean 1.31, |gap| < 0.05 share 0.102 and negative-gap share 0.101. The tag says "本次由 raw/patch 复算".
- 标记状态 box "共 1,395 篇" is derived (896 + 499), and the tag says so.

## (b) Numbers that do not match their source

1. **FIXED**: X3 "文本模型基线" paragraph. Old text: "但在用词匹配的 66 篇子集上，mpnet（1.40）与 Qwen（1.90）之差的区间含 0". In `381_stage13/reports/x3_textbase_recovery.md` (Scale-free comparison table), 1.40 and 1.90 are the rows for **primary/d_matched/test, 37 papers** (Qwen − mpnet +0.50 [−0.50, +4.02]). For all 66 matched papers the values are mpnet 1.52 and Qwen 1.65 (Qwen − mpnet +0.14 [−0.53, +1.42]); that interval also includes 0, so the conclusion does not change. New text: "用词匹配子集的测试集（37 篇）上". The numbers stay as they were.
2. Not fixed (rounding): M3 "怎么读" paragraph, "标题位置 −0.003 到 −0.016". The source `summary_m3/m3_verdict_addendum2.csv` gives min −0.01663 at L28, which rounds to −0.017.
3. Not fixed (rounding): M3 "引用数为 −0.02 到 −0.05". The source range is −0.0157 to −0.0548, which rounds to −0.02 to −0.05. OK, listed only for completeness.
4. Not fixed (wording): first warn box ("第 5 版审读后的处理"), item 2: "随机分折时，约 80% 的测试论文会被去掉，剩 1,863 篇（目标 896、对照 499）". The 1,863 count is for the **author-team folds** (e4b_split_compare / B_global2: "按团队分折"). The E4b box below also says "按团队分折". With per-paper (random) folds, about 1,850 papers are kept (`summary_cpu_group/perpaper_probe_spec.parquet`, split=paper, excl=title-reuse, random-gold control rows). Suggest "按团队分折时" instead of "随机分折时".
5. Not fixed (scope): X1 paragraph, "对照：在 “:” 位置，换问法的移动距离是换论文的 3–5 倍". In `x1_similarity.md` (colon), this holds for L4–L40 (3.0–4.9). The ratio is 2.86 at L44, 2.19 at L48 and 1.3–1.8 at L52–L63. The tag states the L4–L40 range.
6. Not fixed (minor wording): X3 "同领域里与原标题词重合超过 0.3 的论文只占 2.4%". The source (`x3_groupsplit.md`, "share of D with jaccard2 > 0.3: 0.024") is the share of the chosen lexical neighbours D, that is, the most-overlapping same-field paper per title. So it is the share of titles whose best same-field neighbour exceeds 0.3, not the share of all same-field papers.
7. Not independently verified: 标记状态 box and E4b box, "只用假标题训练 … 剩 1,568 篇（目标 810、对照 399）". 1,568 matches `perpaper_probe_spec.parquet` (group split, title-reuse dropped). My own join to `cohort/papers.parquet` `group` gave target 985 / control 399. The handbook (B_global2 泄漏表 (c)) states 810/399, probably on a different group column (e.g. group_tight). I tagged it with the handbook; worth a check.

## (c) Tables / figures without a source line (not tagged: cells are off-limits)

- M3 table: the source is only in the section note (m3_report.md) and in "完整数字见 summary_m3/". There is no line directly under the table.
- X1 table: no source line under the table. `x1_report.md` is named only in the section note, and `x1_vsC.md` appears mid-paragraph.
- X4 decodability table ("答案 / 最早可读出层"): no source line under it. The section note names x4_report.md.
- Stage 13 plan section: the tables "开跑前的数据来源审计", "三种假设及其预测", "实验" and "预注册判定规则" have no source lines. Their cells hold untagged numbers:
  - 审计表: "17.5% 相同（平均差 2.2 年）".
  - 假设表 H3 row: "BERT +0.088 ≥ Qwen L8 +0.018".
  - 实验表 X3 row: 1,186 条, 1,115, 1,015, "一致率 0.55 < 0.80", "40 条人工标注中改意思 6 条 0.15 [0.07, 0.29]，边界 7 条 0.175 [0.09, 0.32]".
  - 实验表 X1 row: "1,178 篇有合格的 B".
  - 实验表 X7 row: "L0 的 83%".
  - 实验表 M3 row: "27,324 次前向", "8 GB", "14/14".
  - 实验表 M4 row: "35/40".
  These should get a source line under each table, e.g. `381_stage13/config/prereg*.json`, `x3_report.md`, PROGRESS 2026-10-28/10-30 entries.
- X5 figure (图 X5) and the X5 table: the section note has the sources (x5_report.md, summary_x5/x5_layer_order.csv). There is no line directly under the table.
