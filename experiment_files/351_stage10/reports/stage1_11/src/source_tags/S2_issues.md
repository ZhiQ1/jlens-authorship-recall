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
