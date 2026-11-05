# S1b issues (Stage 7, 8, 9, synthesis, open items, appendix)

Paths in tags are relative to /scratch/zhang.zhiqi2/jlens/ (identical copies of the Stage 7–8 dirs exist in
/scratch/zhang.zhiqi2/jlens_archive_stage1_8/experiment_files/; the 2026-10-30 recompute dirs exist only under jlens/).
Script paths are written as ~/jlens_work/<NN_stage>/...

## (a) Numbers without a primary result file
1. §7.1 补充 "L40 r=0.69、L56 r=0.72、L62 r=0.77": no output file of the original computation. The methods handbook
   (parts/C_stage1_9.html, 7.1 step 7) recomputed it from 351_stage6/raw/token_layer_scores.csv (0.691/0.723/0.771) and
   says "报告原始出处文件未找到". Tag cites the handbook recomputation and says the original file was not found.
2. §7.2 "45.76 个不同的首 token" and "24 个 tier-3 ... 同一篇 A 论文": counted by the handbook from
   351_stage7_2/candidates/pilot50_author_candidates.csv; no summary file holds them. Tag cites the csv + handbook.
3. §7.3 "+0.0262 变为 +0.0283": no summary file; recomputed here as 50-paper mean of the jlens_* rows (pool=combined) of
   351_stage7_3/summary/paper_null_distribution.csv (0.026244 / 0.028323). Matches.
4. §9 "约 8.6 计算小时": derived (96 × 323.75 s = 8.63 h) from 351_stage9_full_A.log; no file states it.
5. 附录 "2.5% / 97.5% 百分位": design statement, tagged to the appendix-A scripts / handbook; not checked per script.

## (b) Mismatches
None found that need a fix. Minor notes (not changed):
- §8 结论 "bootstrap 双侧 p = 0.002": s8_holm.csv F0 gives 0.00194 (rounds to 0.002). OK.
- §7.2 drop-P004 "+0.023 [−0.017, +0.068]" is the pool=matched row (seed 20261037); the handbook text also quotes the
  pool=combined value +0.022 [−0.018, +0.068]. Report value matches its stated seed.
- §8 结论 L56 LOPO "14 / 100 次的区间跨 0" = 100 − n_ci_excluding_0 (86). OK.
- §8B prose "20 个匹配错误标题" vs table "错误标题同领域同档 4,000/4,000": consistent.

## (c) Tables / figures without a source line in the report
Tables (cells not touched; source found and listed here for a possible caption/source line):
- §7.1 table (first/continuation/all token A−B): 351_stage7_1/summary/layer_and_integrated_effects.csv, reports/experiment_report.md
- §7.3 per-layer table (真标题胜率/参照均值/正向篇数): 351_stage7_3/summary/paper_null_distribution.csv (pool=combined, mean over papers)
- §7.4 diagnostics table: 351_stage7_4/summary/overview.json, cross_stage_correlations.csv (jlens,56), jlens_increment_bootstrap.csv
- §8 RQ design table: ~/jlens_work/08_stage8/351_stage8_PROTOCOL.md
- §8B pre-scoring checks table: 351_stage8/config/stage8B_manifest.json, controls/stage8_control_quality.csv, controls/stage8_shuffled_titles.csv
- §8D main results table: 351_stage8/stage8D/summary/primary_questions.csv, jlens_minus_vanilla.csv
- §8D citation-band table: 351_stage8/stage8D/summary/layer_and_band_summary.csv (row jlens_L56)
- §8D "去掉最大正向对数" table: recomputed by the handbook from stage8D/summary/matched_pair_differences.csv (mode=jlens_L56); post-hoc, no output file
- §8E table has a source line (recompute_2026-10-30) — OK.
- §9 comparison table, fit config table, synthesis table, appendix A/B/C tables: no source line (config tables: 351_stage9/runner_runs/full_A_repair_101_100valid/repair_manifest.json, 09_stage9/351_stage9_README.md; Fit A/B status: final_status.json, full_B checkpoint).
  Note: §9 comparison-table cell "Fit A 4/100，Fit B 0/100" is the archive-time status; the same cell already adds the later status. Handbook says Fit B actually stopped at 66/100 (checkpoint n_done 66), so "Fit B 与 holdout 未做" is fine but "Fit B 0/100" is archive-time only (not edited; inside a td).
Figures with no source line: 图 7.1, 7.3, 7.6, 8.2, 8.4, 8.5, 9.1 (no data numbers in their captions, so no tag added).
Probable sources: 7.1 → 351_stage7_1/summary/layer_and_integrated_effects.csv; 7.3 → 351_stage7_3/recompute_2026-10-30/stage7_weighting_title_advantage.csv (not certain);
7.6 → 351_stage7_4/summary/jlens_increment_bootstrap.csv; 8.2 → 351_stage8/stage8D/summary/primary_questions.csv;
8.4 → stage8D/summary/matched_pair_differences.csv; 8.5 → 351_stage8/recompute_2026-10-30/s8_unsourced_intervals.csv; 9.1 → 351_stage9_full_A.log.
