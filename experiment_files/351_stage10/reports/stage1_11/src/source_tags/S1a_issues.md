# S1a issues (report start: overview, Stage 1–9 summary, Stage 1–6)

AR = /scratch/zhang.zhiqi2/jlens_archive_stage1_8/experiment_files/

## (a) Numbers I could not source
None. Every tagged number was found in a result file.
Left untagged on purpose:
- Overview item 3, "标题信息在 L24–50 被读取，到 L57–61 才在名字位置被 lens 读出": these are layer ranges (places), not values. They summarise Stage 11 E2 knockout and the Stage 10 layer profile.
- Repeated mentions in conclusion boxes and in the overview tables (`<td>`), which the brief excludes.

## (b) Numbers that do not match their source
1. **FIXED**: Stage 5 result paragraph, "匹配 A−B 积分：+0.081 [−0.427, +0.648]". The source is AR/351_stage5_crossed_v2/summary/matched_ab_summary.csv, row mode=jlens, layer=integrated, ci95_low = −0.42649972, which rounds to **−0.426**. The handbook (C_stage1_9.html §5.1) also gives −0.426. The text was changed to [−0.426, +0.648] (entry marked `"fix": true`).
2. Not fixed, and probably not an error: "+0.199 [0.187, 0.212]" (R0-only A − B, final L63), which appears in the Stage 1 R0/R1 box. It matches 351_stage10/reports/r0_r1_analysis.md §1 exactly. However, 351_stage10/reports/r0_sensitivity.md gives the same estimate as [+0.188, +0.212], which comes from a separate bootstrap run, and the BRIEF example quotes 0.188. The tag cites r0_r1_analysis.md. Pick one file and use it in every place the number appears.
3. Not fixed, wording only: overview item 2 and the overview table say the within-bin target − control title-specific signal is "中间层约为 0". In summary_title/B_spec_target_vs_control_within_bin.csv it is about 0 at L24–L40 and L56. At L48 all three Jacobian lenses give −0.037 to −0.054, with CIs below 0. "约为 0" is loose for L48.
4. Not a number, but a definition: in Stage 1 the text says "351_prepare_all.py 保留 group_tight = target/control 且 HR2 > 0.5 的论文". The handbook (§1.1 step 5) states that HR2 > 0.5 is an assert self-check, not an extra filter. Counts are unaffected.
5. The Stage 1 bx mentions "C 比 A 强（+0.11）". The source gives +0.110 [0.086, 0.133] (r0_r1_analysis.md §2), and r0_sensitivity.md gives [0.086, 0.135]. This is the same kind of duplicate-file difference as in item 2.

## (c) Tables and figures with no source line
Stage 1–6 sections of the report have no "结果 Results" path line at all. Suggested sources:
- Overview table "线 / 问题 / Stage 1–9 / Stage 10–11" (no numbers) and the "小样本与全量对照" table (+9.3 pp, +5.2 pp, 0.44, +0.21, +0.199 [0.187, 0.212], ρ = 0.45). Sources: Stage 7.3 paper_null_distribution.csv; Stage 8D primary_questions.csv; 351_stage10/summary_extra/X3_means.csv; summary_title/B_spec_target_vs_control_within_bin.csv; reports/r0_r1_analysis.md; summary_extra/X2_spearman.csv (final L63, all, spec, ρ = 0.451).
- Stage 1 group table (4,110 / 2,186 / 511 / 34 / 6,841; Pilot50 20/20/7/3) and the R0/R1 × target/control table. Sources: AR/351_all/351_audit.json; AR/351_stage5_crossed_v2/cohort/pilot50_v1.csv.
- Stage 1 "阶段 / Stage / 作用" table: no numbers.
- Stage 2 parameter table. Sources: AR/351_stage6/config/protocol.json; 05_stage5/351_stage5.py.
- Stage 3 Exp 2/4 table and Fig. 3.1 (caption tagged). Sources: AR/351_self100_validation/summary/paired_bootstrap_ci.csv, summary/metrics.csv; AR/351_all/351_paper_fidelity.log.
- Stage 3 Exp 3 table. Source: AR/351_self100_gold_false/archive/summary/layer_summary.csv.
- Fig. 3.2 (prose tagged). Sources: AR/351_self100_split_half/summary/matrix_stability.csv; readout_comparison/summary/paired_summary.csv.
- Stage 4 table and Fig. 4.1. Source: AR/351_all/351_stage4_readout.log "STAGE 4 BENCHMARK" block (20 papers).
- Fig. 5.1 (caption tagged). Sources: AR/351_stage5_crossed_v2/summary/layer_summary.csv, matched_ab_summary.csv.
- Stage 6 group table and Fig. 6.1 (caption tagged). Sources: AR/351_stage6/summary/integrated_group.csv; summary/paper_layer_trajectories.csv.

## Notes
- The overview number "名字先验只占约 1/3" is in report §6.12, which is labelled "Stage 11 · CPU". The files, however, are in 371_stage12/summary_cpu/A_prior_decomposition.csv (prior +0.087 / true-title gap +0.247 = 0.35). The tag calls it "Stage 12 CPU 名字先验拆解（报告 §6.12）".
- Stage 1–8 paths use the archive (jlens_archive_stage1_8/experiment_files/...). The 2026-10-30 recompute files (Frobenius norms) exist only under 351_stage8/recompute_2026-10-30/, so they are cited there.
