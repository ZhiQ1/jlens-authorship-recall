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
