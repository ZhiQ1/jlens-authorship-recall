# Brief: source tags for every number in the deck v17 (slides + Chinese speaker notes)

Project jlens (Qwen3-32B: at which layer does the model "know" a paper's authors). NEU Explorer, 2-CPU node.
User complaint: "data points in the text cannot be found in the figures/tables next to them" → EVERY number on the slides and in the
Chinese speaker notes gets a short source tag right after it. Report v27 already does this; you do the deck.

DIR = /tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/deck
Read-only inputs in DIR: `deck_v17_readonly.html` (67 slides; 1280×720; `deck_tools.sections()` splits it), `notes_v17_readonly.json`
(Chinese notes, key = slide number "1".."67", value {"new":bool,"text":…}), `slides_v17_readonly.json` (kind: html / deck; `deck` = page
number of the talk deck built by `build_v17_readonly.py`, shown as a JPEG image), `build_v17_readonly.py` (python-pptx source of those
image pages; English text on the slides + English notes in new_slide()).
Sources of numbers: report v27 tags are the best index — `TAGDIR/S*.json` (each "new" has a `<span class="src">` with the source) in
/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/ ; the report itself
/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html (v27 after ~12:30; v26 copy in tags/report_v26_readonly.html);
methods handbook /scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods/methods_handbook.html; result files under /scratch/zhang.zhiqi2/jlens/
(351_* Stage 1–10, 361_stage11, 371_stage12, 381_stage13, 391_groups; Stage 1–8 archive /scratch/zhang.zhiqi2/jlens_archive_stage1_8/).

## Tag content
Slides: SHORT, e.g. `(Stage 10, final L63, 9,108 papers, Fig. 6.3)` — experiment/stage, readout+layer, sample n, and where (report section
"§6.11" or figure, or a short file name). Notes: FULL detail in Chinese: experiment/stage · condition (真标题 vs 5 个假标题平均 / true→false_0 /
delete) · readout and layer · group/sample and n · statistic (引用档内 目标−对照, 团队聚类 95% CI, 均值比, 恢复比例 …) · where (报告 §x.y 图/表,
or file path relative to /scratch/zhang.zhiqi2/jlens/).
Which numbers: every data value (estimates, CIs, ratios, %, p, AUROC, R², ranks, n of papers/authors/tokens/pairs). One tag per quantity
(estimate + CI = one); a run of values from the same source in one clause may share one tag. Not tagged: stage/section/exp numbers, layer
names used as places, dates, job ids, seeds, versions, citation-bin labels. Never guess a source; if none is found, still tag with what is
certain and end with "source file not found" / "出处文件未找到", and list it. If a number is clearly wrong and the source is unambiguous, fix it
and list it.
E4b / title-position probe numbers: the tag (slide) or text (notes) must say the probe scores ONLY THE FIRST NAME TOKEN (mostly an initial);
the all-token, by-role version (prereg addendum 9) is in progress, no result yet.

## Hard rules
Never rm/delete; never modify the read-only inputs or any project file — write ONLY your own output files in DIR (named in your task).
No jobs, no GPU, no model loading. Python `~/conda-envs/jlens/bin/python`; playwright needs
`PLAYWRIGHT_BROWSERS_PATH=/scratch/zhang.zhiqi2/pw PYTHONPATH=/scratch/zhang.zhiqi2/pylib2`. Never write the word "Minyan".
Finish with a short reply: counts, unsourced numbers, mismatches (fixed or not), files written.
