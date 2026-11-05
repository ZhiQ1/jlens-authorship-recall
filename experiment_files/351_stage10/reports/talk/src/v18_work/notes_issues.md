# Notes v18: source tags for the Chinese speaker notes

Output: `notes_v18_tagged.json` (67 notes; same keys; `new` flags unchanged; only `text` changed).
Build files: `notes_spec.py` (fixes, anchors and tags), `build_notes.py`, `check_notes.py`.
Paths in the tags are relative to `/scratch/zhang.zhiqi2/jlens/`. The Stage 1–8 directories cited there, such as `351_all` and `351_stage7_3`, also exist in `jlens_archive_stage1_8/experiment_files/`. Script paths start with `~/jlens_work/`.

## Counts
- There are 222 tags in 57 notes.
- 10 notes have no number to tag: 2, 5, 12, 24, 30, 40, 50, 53 and 64 contain only layer names or no numbers. Note 26 was left out on purpose (see below).
- E4b caveat sentence: added at the end of 8 notes (23, 24, 27, 30, 38, 39, 58, 66).
- "Stage 1–11" renamed to "Stage 1–13": 0. No note uses "Stage 1–11" for the documents. "Stage 1–9" and "Stage 10–11" are stage ranges, so they were left as they are.
- Validation (`check_notes.py`): I removed every 〔…〕 and compared the result with the original text plus the 3 fixes and the caveats. Result: 67 notes, 222 tags, **0 mismatches**. Keys, `new` flags and bracket balance all match. Every result path cited in the tags exists on disk; the only miss is the glob `raw/logit/L*`.

## Slide 26 (method page "Group comparisons"): not tagged
- New user rule, passed on by the coordinating agent: post-defence group-comparison numbers from 391_groups (P1, P2, dose) may not appear yet.
- Note 26 is unchanged and untagged; another helper will rewrite it as a schematic.
- Note 26 still contains these numbers: P1 +0.200 [0.188, 0.213]; P2 co-authors +0.061 [0.034, 0.090]; first author +0.031 [−0.006, 0.069]; dose 0.17 → 0.46.
  - Their sources are `391_groups/primary.csv` and `391_groups/stage10_curves.csv`.
- No other note cites 391_groups numbers.
  - The +0.199 / +0.20 values in notes 4, 27, 29, 43 and 60 are the Stage 10 R0-only result (`351_stage10/reports/r0_sensitivity.md`), not 391_groups P1.
  - The two numbers are almost the same: 0.1996 vs 0.199.

## Fixes (number changed in the text)
1. **Note 38**, "目标组比对照组高 0.04 到 0.08" was changed to **0.03 到 0.08**.
   - Source: `381_stage13/reports/e4b_trainstd_compare.md`, Confirmatory table 2 (team folds, title reuse dropped, training-fold standardisation).
   - L24–L60 runs from +0.035 (L44) to +0.078.
   - Report v27 made the same fix (S4 issue b1). The method slide 23 (+0.061) already uses this version.
2. **Note 66**, "目标组高 +0.04 到 +0.08" was changed to **+0.03 到 +0.08**, for the same reason.
3. **Note 56**, "标题特异信号从 0.45 降到 0.26" was changed to **0.42 → 0.26**.
   - Source: `361_stage11/summary/E3_chain.csv`, final output, target.
   - 0.45 is the isolated score at author position 2 (0.454). 0.26 is the chained score at position 4+. The two numbers come from different positions.
   - At position 4+ the change is 0.421 → 0.260. Report §6.11 says the same.
   - The English note in `build_v17_readonly.py` and the deck page still say 0.45.

## Mismatches and imprecise values (not changed)
- **Notes 48 and 58: "L48 恢复 83%" / "0.83".**
  - E1 all = 0.8249 (`361_stage11/summary/E1_recovery.csv`), which is 82% after one rounding.
  - Same issue as report S2 b4. The tags give 0.825.
- **Note 62: "jaccard2 中位数 改写 0.61".**
  - The primary set gives 0.611 (n = 1,110, `x3_report.md`). The method-slide SOURCES cite 0.615 (n = 1,115), which is the sensitivity-set value.
  - The tag gives both. Only the slide source line needs a decision.
- **Note 7: "高于原计划的 10% 上限".** The report wording is "预设的 ≤10% 下限". The wording differs but the number is the same.
- **Note 27: "R0 口径为 +0.02 到 +0.04".** This is correctly labelled as the pre-recheck (paper-fold) value. The tag says so.
- **Note 39: "+0.04 升到 +0.08".** These are pre-recheck values for the target group (`361_stage11/summary/E4_probe.csv` spec_target: L16 +0.043 → L56 +0.082). The note says so itself.
- **Note 49: "80–87%".** These are the target / control values at L48 (0.803 / 0.866). The value for all papers is 0.825. The tag gives all three.
- **Note 14:** the CI [4.7, 13.9] for the L56 +9.3 pp effect comes from the 2026-10-30 recompute file. The original analysis wrote no interval to a file.

## Numbers left untagged on purpose
- Note 10, "排第 1 为 0，排第 10 为 −1": definitional examples of log10(1/rank), not data.
- Note 26: see above.
- Layer names (L16, L24–L50, L57–61 and so on), stage, experiment and addendum numbers, dates and times (note 16), citation-bin labels (0–2, 4097+), and the dose x-axis "0 到 4": all excluded under the brief.
- Chinese-numeral design words such as "三种 Jacobian lens", "两个 lens" and "四条论证线": not tagged. Arabic design counts, such as 5 false titles, 20 wrong titles and 100 names, are tagged.

## Unsourced numbers
- None of the tagged numbers is unsourced.
- Some tags point to secondary sources, not a primary result file:
  - Note 18: "+1.9 after dropping 5 pairs". I recomputed it here from `matched_pair_differences.csv` and got 0.0190. No summary file holds it.
  - Notes 42 and 59: "约 46 个不同首 token". This is the handbook count (45.76), taken from the candidates CSV.
  - Note 31: the Public-557 KL value at L32 (11.135) is only in `351_all/351_paper_fidelity.log`.

## Other notes for the deck owner
- Note 47 describes the probe method but reports no result, so it did not get the caveat. The same goes for notes 64 and 67, whose probe mentions are the M2 attribute probes, not E4b.
- Note 58 says the title probe reads authors "从 L24 起". Slide 58 says "from L16". The re-checked E4b is significant at L16 as well (L16–L60 +0.042 to +0.080 in report S6#49), so the slide and note differ only in which layer they start from. Not changed.
