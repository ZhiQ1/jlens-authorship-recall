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
