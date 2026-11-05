# Brief: grey source tags for every number in report v26 (one segment per helper)

Project jlens (Qwen3-32B: in which layer does the model "know" a paper's authors). Cluster: NEU Explorer, you are on a 2-CPU compute node.
User complaint: "data points in the text cannot be found in the figures/tables next to them". Fix: EVERY number in the
report prose gets a small grey parenthetical source tag right after it.

## Files
- Report (READ-ONLY copy, v26): `/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/report_v26_readonly.html` (2.2 MB; base64 images inside, so grep/python on it, do not cat whole).
  Your segment = `segs.bounds(s)[SEG]` (character range), see `/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/segs.py`.
- Methods handbook (best index of sources; its `<span class="src">` spans give script/result-file provenance for most numbers):
  `/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/methods_handbook.html` and its parts `.../methods/parts/*.html`.
- Result files: `/scratch/zhang.zhiqi2/jlens/351_*` (Stage 1–10; Stage 1–8 archive also `/scratch/zhang.zhiqi2/jlens_archive_stage1_8/`),
  `361_stage11/`, `371_stage12/`, `381_stage13/` (summary_*/ csv, reports/*.md), `351_stage10/reports/*.md`,
  `351_stage10/summary_title/`. The report itself often has a "结果 Results" line with paths at the end of each section — use it.
- State/history: `/scratch/zhang.zhiqi2/jlens/STATUS.md`, `~/jlens_work/PROGRESS.md` (long; grep).

## Output (the ONLY files you write)
1. `/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/SEG.json`: JSON list of `{"old": "...", "new": "..."}`.
   - `old` = exact substring of the report, occurring EXACTLY ONCE inside your segment; entries must not overlap.
     Keep it short but unique (the number plus a little following context).
   - `new` = `old` with one or more `<span class="src">…</span>` inserted (nothing else changed).
   - If a number is clearly WRONG and the source is unambiguous: correct it in `new`, add `"fix": true` and log it (issues file).
2. `/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/SEG_issues.md`: (a) numbers you could not source (quote, location, what you tried); (b) numbers that do not match their
   source (text value, source value, file/row; fixed or not); (c) tables/figures that have no source line.
3. Run `~/conda-envs/jlens/bin/python /tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/validate.py SEG /tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/SEG.json` until it prints `0 problems`.

## Tag format
- Chinese text (zh paragraphs, the Stage 1–9 part): `<span class="src">（…）</span>`; English text (`p.en`, `span.en`, `li` in English):
  `<span class="src">(…)</span>` with the same content in English (may be a bit shorter).
- Content, in this order, leaving out what does not apply, separated by "，" (zh) / ", " (en):
  experiment/stage (e.g. Stage 10, Stage 11 E1 替换, Stage 13 X1) · condition (真标题 vs 5 个假标题平均 / true vs false_0 / delete …) ·
  readout and layer (最终输出 L63, logit lens L56, public J-lens L48, probe at the last title token L40 …) ·
  group / sample and n (目标 4,621 + 对照 2,220 篇; Stage 11 样本 593+593; 测试集 582 对 …) ·
  statistic (引用档内 目标−对照; 团队聚类 95% CI; 论文 bootstrap 95% CI; 均值比; 恢复比例; AUROC …) ·
  where it appears (图 8.2 / §6.11 恢复比例图 / §6.4 表) and/or the source file (path relative to `/scratch/zhang.zhiqi2/jlens/`, e.g.
  `361_stage11/summary/xxx.csv`; for Stage 1–8 the archive path).
  Example zh: `L52 起达到 1.00<span class="src">（Stage 11 E1 替换，真标题→false_0，标题后全部位置，各层；最终输出名字 token 恢复比例；593+593 篇；§6.11 恢复比例图；361_stage11/summary/E1_*.csv）</span>`
  Example en: `+0.199 [0.188, 0.212]<span class="src">(Stage 10 R0-only, true − mean of 5 false titles, final L63, within-bin target − control, paper bootstrap 95% CI; 351_stage10/reports/r0_sensitivity.md)</span>`
- Figures in the Stage 10–11 part are not numbered: refer to them by section + content ("§6.11 恢复比例图", "§6.4 表"). Stage 1–9 part has numbered figures (图 7.2).

## Which numbers
- Tag every data value: estimates, CIs, ratios, shares, percentages, p values, AUROC, R², ranks, counts of papers/authors/tokens/pairs (n),
  times/costs that are results. One tag per quantity: an estimate and its CI are one quantity (tag after the CI). A run of values of the
  same statistic from the same source in one clause (e.g. "L24 0.07–0.09，L40 0.27–0.34，L48 0.80–0.87") may share one tag at its end.
- Design constants in a definition sentence (seeds, number of bootstrap draws, layer lists, shard sizes, "5 false titles", thresholds):
  one tag per sentence citing the script/config (or handbook section) is enough.
- Not numbers to tag: Stage / section / Exp / addendum numbers, layer names used as places (L52), dates, times of day, job ids, sha256,
  version numbers, file names, citation-bin labels (0-2, 513-1024).
- Do NOT touch: headings (h1–h4), anything inside `<svg>`, table cells (`<td>`, `<th>`), `<span class="mono">` paths, `<pre>`, the
  `<head>`/CSS, existing `<span class="st">` / `class="ln"` labels. Tag only prose: `<p>`, `<li>`, `<figcaption>`, note/callout/finding
  divs, `<span class="en">` inside prose.
- Check every value against its source (rounding differences are fine). Never guess a source. If no source is found, still add a tag with
  what is certain from the context and end it with "出处文件未找到" / "source file not found", and list it in the issues file.

## Hard rules
- Read-only everywhere except your two output files. Never rm/delete anything, never scancel, never submit jobs, no GPU, no model loading.
- Python: `~/conda-envs/jlens/bin/python` (pandas/pyarrow available). Keep memory low (8 GB node).
- Never write the word "Minyan" (any case) anywhere.
- Finish with a short reply: number of entries/tags, number of unsourced numbers, number of mismatches (and which you fixed), and the
  validator output line.
