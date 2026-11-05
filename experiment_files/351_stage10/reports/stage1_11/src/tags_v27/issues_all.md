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
# S2 issues (Stage 10–11 part, §1–§5)

## (a) Numbers I could not source to a project file

1. §3.1, paragraph 2 (zh and en): "随机抽 100,000 篇 … 合计约占整理后数据的 76.95%" / "random sample of 100,000 papers … about 76.95% of the curated data".
   Not in the Dreaming Up Authors code package (`~/archives/dreaming-up-authors-code-v0.zip`: README.md, PAPER_EXPERIMENTS.md, config/config.yaml, PKG-INFO), not in the label package, STATUS.md, PROGRESS.md or the handbook parts (J_dua_package, B_global2, D_stage10_11).
   The only copy I found is a user-pasted LaTeX text "Dataset Provenance, Behavioral Labels, and Jacobian Lens Fitting" (Claude paste cache, lines 71 and 74), which states both numbers. The tag cites that text and ends with "出处文件未找到 / source file not found". Someone should point the tag at the Dreaming Up Authors paper or a project copy of that text.

## (b) Numbers that do not match their source

1. **FIXED**: §3.2 ③ (zh and en): "4 个字母概率之和平均为 1.00，没有一次低于 0.5" / "never below 0.5".
   Source: `labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/mc_results.jsonl` (kind=team, 36,432 orders). The mean mass is 0.998, so "1.00" is right. But 3 orders have mass below 0.5 (minimum 0.142), all for one paper (`mc_n_low_mass` = 3 in paper_labels_with_papers.csv). label_README.md rounds this to "0.0%".
   Changed to "36,432 次中只有 3 次低于 0.5" / "fall below 0.5 in only 3 of 36,432 orders".
2. **FIXED**: R0/R1 paragraph after §3.2 (zh and en): "+0.199 [0.187, 0.212]".
   Source: `351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv`, where the lower bound is 0.187664. `reports/r0_sensitivity.md` prints it as 0.188.
   Changed to [0.188, 0.212]. Other segments (Part III, §6) may print 0.187 too. Check them for consistency.
3. **NOT FIXED**: §4.4 (zh and en): "0-2 档目标组占 25%，4097+ 档占 99%" / "target share 25% in bin 0-2, 99% in 4097+".
   The text comes from the caveat in `351_stage10/reports/stage10_report.md`. Recomputed from paper_labels_with_papers.csv:
   - Share of papers recognised 4/4 (mc_team_outcome strong): 25.5% in bin 0-2 and 99.2% in 4097+. This matches 25% / 99%.
   - Share of the `group_tight` target group, which is what the sentence claims: 25.1% and 68.9% of all papers in the bin (84 of 122 in 4097+; the other 37 are guard). As a share of target + control it is 36.2% and 100%.

   So "目标组 … 99%" is accurate only if "target" means "recognised", which includes guard. I left the text unchanged because the intended wording is a judgement call. The tag gives both readings. Suggested wording: "0-2 档认出（4/4）的论文占 25%，4097+ 档占 99%".
4. **NOT FIXED**, rounding only: §1 (zh and en): "L48 已恢复 83%" / "recovers 83% at L48".
   Source: `361_stage11/summary/E1_recovery.csv`, group=all, L48 = 0.824853 (stage11_report.md prints +0.825). That is 82% after one rounding; 83% comes from rounding twice. By group: target 0.803, control 0.866. Not changed, because the same 83% appears in other segments (§7 and the unknown-research section).
5. **Note**, not a mismatch: §5 "主轮实际约 7 GPU 小时". The only measured basis is PROGRESS.md 2026-10-25 22:52: about 46 s per main shard. 504 shards × 46 s ≈ 6.4 GPU-h, so "约 7" is a rough upper rounding.
   The tag sits after "每个 shard 约 46 秒", which ends the same sentence, and covers the GPU-h figure. No separate job-accounting (sacct) total was found.

All other values checked against their source within rounding:
- 9,108 papers; field counts; years 1817–2020 (median 2006); citations 0–63,901 (median 50.5); mean 3.71 authors (1–20).
- group_tight counts 4,621 / 2,220 / 214 / 2,053; A/B/C/D 4,110 / 2,186 / 511 / 34.
- 98.1%; 83.6% (296 + 122 of 500); kappa 0.63.
- 33,811 contexts and 149,999 tokens, all 7 role counts.
- Tiers 35,898 / 1,638 / 2,565 / 5,439; 557 prompts; Fit A 100 of 101; Fit B 66/100.
- Parity: 12 contexts, 52 positions, max 0.156–0.367, ranks < 42 equal, tolerance 0.25 → 0.5.
- Stage 6 crosscheck: 972 tokens, 100%, median diff 3e-6 to 6.6e-5, rank_exact 76.5–95.5%.
- Title-specific: +0.207 to +0.231; X1 +0.253 / +0.048 / +0.174 / +0.202; X2 ρ 0.451; X3 +0.007 to +0.030.
- E1 L52 0.996; E2 L52 0.007; P1 names L52 0.847 and ":" 0.172; X7 control S at L52 / L54 / L56 = 0.051 / 0.018 / 0.000; X6 L52+ 0.98–1.02.
- E4b group / title-reuse dropped: all papers 0.050–0.080; target − control 0.036–0.078.
- R0: +0.199, pooled +0.207; C − A +0.110; R1 written − missed +0.199.

## (c) Tables or figures without a source line

1. §3.2 group table (target 4,621 / control 2,220 / guard 214 / excluded 2,053): no source line under the table. I did not edit it, per the rule on td cells.
   Source: `labels_20261015/zhiqi_qwen3-32b_labels_2026-10-15/paper_labels_with_papers.csv`, column `group_tight`. The counts match.
2. §1–§5 have no "结果 Results" path line at the end of any section, so every tag had to be traced individually.

## Side note
I wrote helper files in the scratchpad that are not the two outputs: `scratchpad/s2work/build.py`, `scratchpad/tags/S2_text.html`, `scratchpad/tags/_*.html.txt`, and an extracted copy of the DUA package config and markdown in `scratchpad/dua_unz/`. They are scratch only and can be ignored or removed.
# S3 issues (§6.1–§6.10, Stage 10 results)

All numbers were checked against the CSVs under `/scratch/zhang.zhiqi2/jlens/351_stage10/` (summary/, summary_title/, summary_extra/, config/manifest.json).

## (a) Numbers I could not source
None. Two values come from logs or notes, not from a CSV:
- §6.7 "姓的第一个 token 出现在第 1 个位置的比例为 0%" / "0% of first-surname tokens are at position 1". Source: the share at token_index 0 printed by `stage10_extra_format.py:62–65`, cited in handbook part D line 304 and in PROGRESS.md (2026-10-26 05:20). No CSV holds this number.
- §6.7 "平均 4.4 个" / "4.4 on average". Source: `351_stage10/config/manifest.json` (n_tokens 149,999 / n_contexts 33,811 = 4.44), as in handbook part D.

## (b) Numbers that do not match their source
1. **FIXED** §6.7, "知道第一个 token 之后" paragraph (zh and en). Text: "L62 的 logit lens 和 Jacobian lens 也只差 +0.05 到 +0.07" / "differ by only +0.05 to +0.07".
   Source `summary_extra/X1_cond.csv` (unit=token, group=all, L62, later_level_diff): logit +0.072, public +0.051, self100 +0.053, **fitA +0.036**. Changed to "+0.04 到 +0.07" / "+0.04 to +0.07".
2. **FIXED** §6.7, same paragraph. Text: "L56 只有 0.2%–1.2%" / "0.2%–1.2% at L56".
   Source `X1_cond.csv` share_first_top10 at L56: logit 0.22%, public 1.25%, self100 1.26%, **fitA 1.31%**. Changed to "0.2%–1.3%".
3. **Not fixed (small)**, §6.9 table caption: "均值的置信区间宽度均小于 ±0.01" / "narrower than ±0.01". In `X3_means.csv` the largest half-width is about 0.011 (level at L56, e.g. public −3.189 to −3.166). This rounds to ±0.01. I gave the tag the real maximum.
4. **Not fixed (small)**, §6.2: final-output CI is printed as [0.230, 0.265]. The CSV has hi 0.2655, which displays as 0.266. This is a rounding difference.
5. Values that are fine but easy to misread (no change):
   - §6.3 "目标组 +0.48 到 +0.58": +0.48 is the final output L63 (0.481), and +0.58 is logit L62 (0.583). The tag says so.
   - §6.9 "15%–18%": self100 is 14.7%. This rounds to 15%.
   - §6.6 ρ = 0.27: the CSV value is 0.268.

## (c) Tables, figures or source lines with problems
- **§6.6, wrong file in the Results line.** It cites `summary_title/C_graded_mc_team_a.csv`. The numbers in the text (−0.137, −0.122, −0.047, −0.018, +0.076; ρ 0.27) are true-title *level* values (metric=mean_nlr) from `summary/C_graded_mc_team_a.csv`. The title-specific file gives −0.131 … +0.068, ρ 0.329. My tags cite the correct file. The Results line itself is in a `files` div and the `mono` path, so I did not touch it. Suggestion: add `summary/C_graded_mc_team_a.csv` to it.
- **§6.6 and §6.5 have no table or figure.** The numbers appear only in the prose.
- All other tables and figures in §6.1–§6.10 have a Results line pointing to the correct CSVs.
# S4 issues (§6.11 Stage 11, §6.12 name prior / E4b controls, §6.13 R0-only, §7, §8)

S4.json: 124 entries, 125 tags (zh and en both tagged). Validator: `S4: 124 entries, 125 tags, 0 problems`.

## (a) Numbers I could not source

None are fully unsourced. One value is derived, not read from a file:
- §6.11 小结 / Summary: "早了约 5–10 层" / "about five to ten layers". This is the gap between the Stage 11 layers (L44–L52) and the Stage 10 lens-readable layers (L56–62). The tag says it is derived and cites `351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv`.

## (b) Numbers that do not match their source

1. **FIXED. §7 finding 3, zh "目标组比对照组高（+0.04 到 +0.08…）" and en "(target − control +0.04 to +0.08…)".**
   - Source: `381_stage13/reports/e4b_trainstd_compare.md`, Confirmatory second table (team folds + title-reuse exclusion, training-fold standardisation).
   - L24–L60 values: +0.052, +0.070, +0.064, **+0.0345 (L44)**, +0.078, +0.064, +0.077, +0.078. The range is +0.03 to +0.08, which is what §6.11 already says.
   - Changed to "+0.03 到 +0.08" / "+0.03 to +0.08".
2. **FIXED. §6.12 en "training the probe only on false-title pairs makes it stronger".**
   - This is the superseded result, where the same borrowed title appeared in both training and test.
   - The zh paragraph was already updated: comparable or slightly lower, +0.050 / +0.057 / +0.074 vs +0.050 / +0.066 / +0.080 (`e4b_trainstd_compare.md` Controls (X1) table; `summary_cpu_trainstd/X1controls_4configs.csv`).
   - Rewrote the en clause to match the zh and added tags. The entry has `"fix": true`.
3. **Not fixed. §6.11 "没有任何区间从“不含 0”变成“含 0”" / en "no CI changes whether it contains 0".**
   - This holds only for the confirmatory configuration.
   - `e4b_trainstd_compare.md` says "E4b tc_pooled 1/36" changed: team folds, no exclusion, L16 went from [+0.000, +0.028] to [−0.000, +0.028].
   - The tag states the qualification. The wording could say "确认版配置中".
4. **Not fixed. §6.12 "真标题让平均名次再好约 2.4 倍" / "improves the average rank by about 2.4×".**
   - 2.4× is true vs false title: +0.378 → 10^0.378.
   - The sentence follows the no-title prior, so it reads as true vs no title. That comparison is +0.278 → 1.9× (`371_stage12/summary_cpu/A_prior_decomposition.csv` all_tokens/all).
   - The tag gives both. Suggest rewording to "比假标题好约 2.4 倍（比不给标题好约 1.9 倍）".
5. **Not fixed, minor. §6.11 E1t "恢复比例只有约 0.12（L8–L40）" / "about 0.12".**
   - The values are 0.12–0.145 for all papers, 0.11–0.13 for target and 0.14–0.175 for control (`361_stage11/summary/E1t_recovery.csv`). "about 0.12–0.15" would be more accurate.
   - The tag gives the range.
6. **Not fixed, wording. §7 finding 3 "优势只出现在最后两层" / "appears only in the last two layers".**
   - This is true for the three J-lenses on the main-round layers: about 0 at L56, about +0.23 at L62.
   - The logit lens already gives +0.065 [0.050, 0.080] at L56 (`r0_sensitivity.md` / `summary_title/B_spec_target_vs_control_within_bin.csv`).
   - Finding 1 itself says the difference rises over L57–L61.
   - The tag gives the values.

Values I checked against the sources and found matching (rounding aside):
- E1, E2, E2n and E3 values; denominators 0.418 / 0.214.
- E4 lens 0.01–0.03; E4b original and re-checked values; 1,863 = 896 + 499 + 433 + 35.
- 73% initials (24,739 / 33,780 contexts).
- Stage 12 A/B/C values (rank 12, 146 → 24, +0.087 / −0.047 / +0.207 / +0.247, +0.022 / +0.42, ρ +0.085 / +0.329 / −0.215).
- R0-only values (511 / 34, 4,110 / 2,186, 3,423 / 2,151, +0.199 [0.188, 0.212], +0.22 at L62, +0.204, +0.247 → +0.239, +0.110, 41 = 36 + 5, 0.28 / 0.34, 0.81 / 0.87, 0.84 / 0.81).
- §7 values (+0.35 → +0.64, +0.04, +0.22, X6/X7 control L54–56).
- §8 values (0.25 → 0.5, 4097+ = 0, 83.6% / kappa 0.63, 6–7 fitted layers, 6 main layers).

## (c) Tables and figures without a full source line

- §6.12, prose vs the adjacent table: the re-checked false-trained probe values (+0.050 / +0.057 / +0.074, and +0.050 / +0.066 / +0.080 for the ordinary probe) are **not in the table next to them**. The table still shows the superseded rows, marked in red. The "结果 Results" line under §6.12 lists only `371_stage12` files, not `381_stage13/reports/e4b_trainstd_compare.md` or `summary_cpu_trainstd/X1controls_4configs.csv`. This is the kind of gap the user complained about. Suggest adding the re-checked rows, or the 381_stage13 paths, to the files line.
- §6.11: the "结果 Results" line lists only `361_stage11` files. The re-checked E4b numbers in the prose come from `381_stage13/reports/e4b_trainstd_compare.md`, which the prose names, but the files line does not. The title-position table shows only the original (paper-fold) probe values, not the re-checked ones.
- §6.11 summary paragraph: the claim "注意力在 L48 读入，MLP 在 L52–56 接手" comes from Stage 12 P2 (`371_stage12/summary/P2_patch_comp.csv`), which no table or files line in the section shows. It is now tagged.
- §7 finding 2 (X6/X7) and findings 6–7 (§6.7 / Stage 10) have no figure or table in this segment. The tags point to `381_stage13/reports/x6_report.md`, `x7_report.md` and `351_stage10/summary_extra/`, `summary_title/`.
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
