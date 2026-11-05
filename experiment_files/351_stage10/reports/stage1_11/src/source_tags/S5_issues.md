# S5 issues (cross-stage R0/R1, two-stage comparison, Stage 12 results, Stage 13 X6, X7)

## (a) Numbers I could not source
None. Every tagged number was traced to a result file or report. Two tags point to secondary sources and not to the raw file:
- "合并口径 3,734 / 2,182" (§1 note): r0_r1_analysis.md gives no n for the pooled view. The value comes from methods handbook part D (D_stage10_11.html line 74: "target 3,734 / control 2,182 篇"). I did not open tc_pooled.csv for its n columns.
- "约 46 个不同首 token": 45.76 is a handbook count from the Stage 7.2 candidates csv (C_stage1_9.html). quality.json gives only the 156/5,000 collisions.

## (b) Numbers that do not match their source exactly (none fixed)
1. §2 prose, "到 L52 两者都恢复 0.97 以上": the source value for C (n = 36) at L52 is 0.968 [0.937, 0.994] (361_stage11/summary_r0r1/stage11_curves_by_recall.csv, E1, C target R1). 0.968 rounds to 0.97 but is not above 0.97. A is 0.988. Not fixed. Suggested wording: "约 0.97 及以上".
2. X6 prose, "各假标题之间的差都不超过 0.02": this is true only when each false title is compared with false_0 (the pre-registered check). Then the maxima are target 0.015, control 0.019 and all 0.012. Between titles the control range at L48 is 0.864–0.885, which is 0.021. The tag says the comparison is with false_0. Not fixed.
3. X7 prose, "Stage 11 从 L0 阻断时的 83% 损失": 0.831 is the all-papers value. For target alone it is 0.839, and §2 of the R0/R1 section quotes 0.84. Both are consistent. The tag gives both.
4. X7 note, "最大差 1×10⁻¹⁶": the source is 9.9e-17 (x7_report.md). This is consistent after rounding. Not changed.

## (c) Tables/figures without a source line
- The "两阶段对照" tables ("设计上改了什么" / "结论上变了什么") have no source line or note. Some cell values (Pilot +9.3 pp, 200 篇 +5.2 pp, L62 ≈ 0.44, ρ = 0.45, 9,108 / 33,811 / 149,999) are in td cells, so they were left untagged under the rules. The "小样本阶段提醒" list items are now tagged.
- The Stage 12 tables P1 and P2 and the X6 / X7 tables rely on the section notes ("报告：…"). P1/P2 point to 371_stage12/reports/stage12_report.md. There is no explicit csv line (371_stage12/summary/P1_patch_pos.csv, P2_patch_comp.csv).
- The R0/R1 section has one consolidated "代码/结果" note at the end. It covers all five subsection tables.
