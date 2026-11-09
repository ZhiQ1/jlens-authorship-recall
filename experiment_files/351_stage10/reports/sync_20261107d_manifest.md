# Sync 2026-11-07 d — change manifest (round approved ~21:00; local only, NOT published, NOT pushed)

Sources: `~/jlens_work/for_user_2026-11-07.md` §a (D13-1, revised ~22:00), §b (X4, E4b scheme 2), §c, §e; `numcheck/claims/out_20261107_183155/` (v6_all_non_ok.csv, v5_definition_issues.csv).
Scripts in `351_stage10/reports/sync_20261107/`:
- `apply_20261107g.py`: main round. Backups `*.before_20261107d.*`; full log in `apply_log_20261107g.json`.
- `apply_20261107h.py`: two prose leftovers.
- `apply_20261107i.py`: D13-1 rewording (user change ~22:00). Backups `*.before_20261107i.*`.
- `apply_20261107j.py`: double full stop after the X4 sentence.
- `apply_20261107k.py`: REPAIR, see below.
- `apply_20261107l.py`: handbook D correction note.
- `export_pdfs_20261107d.py`, `export_pdfs_20261107d2.py`: PDFs.
Other scripts:
- `methods/edit_20261107d.py`: handbook part K regenerated + build.
- `talk/src/export/pptx_text_fix_20261107d.py`: pptx text fixes.
- `talk/src/export/export_v20f_full.sbatch`: deck PDFs, job 11716762, COMPLETED.

**Repair note:** `apply_20261107g.py` took the report from `stage1_11_report.before_20261107d.html`, a backup name already used at ~02:50, so its input was a pre-03:00 state. The report therefore lost the 03:00 edits: the U0 tag 2,001, the H1 cell and the X1 late-layer qualifier. `apply_20261107k.py` re-applied exactly those edits on the current report, and the handbook was rebuilt. The strict check below runs on the repaired files.

## Changes (rule · file · before → after · count)

| # | rule (why) | file / note | before | after | count |
|---|---|---|---|---|---|
| 1 | 8 P1/P2 | stage1_11/stage1_11_report.html | 194 个计算单元已完成 116 个，其余 78 个分三条并行的作业链计算；结果经用户确认后补入 | 194 个计算单元已完成 187 个，结果尚未出来；结果经用户确认后补入 | 1 |
| 2 | 8 P1/P2 | advisor/index.html | 194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算 | 194 个计算单元已完成 187 个，结果尚未出来 | 1 |
| 3 | 8 P1/P2 | process_report/draft_zh.md | 194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算 | 194 个计算单元已完成 187 个，结果尚未出来 | 1 |
| 4 | 8 P1/P2 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算 | 194 个计算单元已完成 187 个，结果尚未出来 | 1 |
| 5 | 8 P1/P2 | pages_20261106b/methods_addendum/index.html | 194 个计算单元已完成 116 个，其余 78 个分三条并行作业链计算 | 194 个计算单元已完成 187 个，结果尚未出来 | 1 |
| 6 | 8 P1/P2 | notes_zh.json #81 | 194 个单元已完成 116 个，其余 78 个分三条并行作业链计算 | 194 个单元已完成 187 个，结果尚未出来 | 1 |
| 7 | 8 P1/P2 | talk_docs/progress_report_for_advisor_zh.html | （194 个单元已完成 116 个） | （194 个单元已完成 187 个，结果尚未出来） | 1 |
| 8 | 8 P1/P2 | merged_deck/stage1_11_deck.html | 116 / 194 units done, 78 left in three parallel chains | 187 / 194 units done, result pending | 1 |
| 9 | 8 P1/P2 | github/README_draft_20261106b.md | (116 / 194 units done) | (187 / 194 units done, result pending) | 1 |
| 10 | 8 P1/P2 | github/README_draft_20261106b.md | running (116 / 194 units) | running (187 / 194 units, result pending) | 1 |
| 11 | 1 3-3 stopped | stage1_11/stage1_11_report.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写； | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [… | 1 |
| 12 | 1 3-3 stopped | advisor/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写； | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [… | 1 |
| 13 | 1 3-3 stopped | process_report/draft_zh.md | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写； | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [… | 1 |
| 14 | 1 3-3 stopped | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写； | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [… | 1 |
| 15 | 1 3-3 stopped | pages_20261106b/methods_addendum/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23，3-3 Stage 7.1B 快路径：代码在写； | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始；3-3 Stage 7.1B 快路径：已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [… | 1 |
| 16 | 1 3-3 stopped (notes 81) | notes_zh.json #81 | 批次 3（补充 14）：3-1、3-2、3-3 代码在写； | 批次 3（补充 14）：3-1、3-2 代码已就绪，第二批之后开始；3-3（7.1B 快路径补完）已停止（偏离 D14-1）：3-3 停止：只有 7 篇论文同时有旧逐前缀结果和快路径结果，不足以确认两者在 ±0.02 内等效（输出层 target−control 差值之差 +0.0059，按论文 Welch 95% CI [−0.0207, +0.0324]；论文级 bootstrap [−0.0005, +0.0181]，因每组仅 3… | 1 |
| 17 | 1 3-3 stopped | talk_docs/progress_report_for_advisor_zh.html | 批次 3（补充 14）代码在写。 | 批次 3（补充 14）：3-1、3-2 代码已就绪，第二批之后开始；3-3（7.1B 快路径补完）已停止（偏离 D14-1）：无法确认与旧逐前缀结果等效（论文级 Welch 95% CI [−0.0207, +0.0324] 超出 ±0.02）。 | 1 |
| 18 | 1 batch 3 status | pages_20261106b/methods_addendum/index.html | 批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码在写 | 批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码已就绪，第二批之后开始 | 1 |
| 19 | 1 3-3 stopped (deck slide 81) | merged_deck/stage1_11_deck.html | 3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23 · 3-3 Stage 7.1B fast path: code in progress | 3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: code ready, after batch 2 · 3-3 Stage 7.1B fast path: stopped (deviation D14-1; equivalence with the old per-prefix results not confirmed) | 1 |
| 20 | 1 3-3 stopped (README) | github/README_draft_20261106b.md | Batch 3 (addendum 14: Stage 10 L41–L47, L49; L0–L23; Stage 7.1B fast path): code in progress. | Batch 3 (addendum 14): Stage 10 L41–L47, L49 and L0–L23 code ready, after batch 2; Stage 7.1B fast path stopped (deviation D14-1: equivalence with the old per-prefix results could not be confirmed, paper-level Welch 95% … | 1 |
| 21 | 1 3-3 stopped (README table) | github/README_draft_20261106b.md | / Batch 3 (addendum 14) / 3-1 Stage 10 L41–L47, L49; 3-2 L0–L23; 3-3 Stage 7.1B fast path / — / code in progress / | / Batch 3 (addendum 14) / 3-1 Stage 10 L41–L47, L49; 3-2 L0–L23; 3-3 Stage 7.1B fast path / 3-3: equivalence with the old per-prefix results not confirmed / 3-1, 3-2 code ready (after batch 2); 3-3 stopped (deviation D14… | 1 |
| 22 | 1+2 limitations (report #pd-limits) | stage1_11/stage1_11_report.html | <li><b>标注流程。</b>标注包作者的 elm 代码 | <li><b>Stage 7.1B 未完成。</b>Stage 7.1B 的终端读出只完成 1,166 / 15,519 个上下文（7.5%）；用 Stage 10 快路径补完的尝试（补充 14 第 3-3 项）因无法确认与旧逐前缀结果等效而停止，7.1B 的估计量不报告。<span class="src">（补充 14 出入记录 D14-1；381_stage13/b3_33_v2/prereg_addendum14_deviatio… | 1 |
| 23 | 1+2 limitations (advisor) | advisor/index.html | <li>只用了一个模型（Qwen3-32B，bf16）。</li> | <li>只用了一个模型（Qwen3-32B，bf16）。</li> <li>Stage 7.1B 的终端读出只完成 1,166 / 15,519 个上下文（7.5%）；用 Stage 10 快路径补完的尝试（补充 14 第 3-3 项）因无法确认与旧逐前缀结果等效而停止，7.1B 的估计量不报告。（偏离 D14-1）</li> <li>Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1）。</li> | 1 |
| 24 | 1+2 limitations (deck note 82) | notes_zh.json #82 | (append) | Stage 7.1B 的终端读出只完成 1,166 / 15,519 个上下文（7.5%）；用 Stage 10 快路径 | 1 |
| 25 | 2 D13-1 box (report Stage 8) | stage1_11/stage1_11_report.html | GPU 上按原 W 重算没有做（用户 2026-11-06 决定）。</div>  | GPU 上按原 W 重算没有做（用户 2026-11-06 决定，偏离 D13-1，见下框）。</div> <div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>按补充 13 C-2 的判定规则（prereg_addendum13.json 第 18 行），全部作者 CPU 代理（public J-lens 名次、Stage 10 的 5 个假标题，不是原 W）只在 L56 的 RQ2… | 1 |
| 26 | 2 D13-1 (report Part 5) | stage1_11/stage1_11_report.html | <li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做；CPU 代理见 Stage 8 节）。</li> | <li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做，列为偏离 D13-1：CPU 代理只在后改的 L56 上 RQ2 区间含 0，在原定的 7 层积分终点上同向且区间不含 0，RQ2 +0.046 [+0.007, +0.088]；见 Stage 8 节）。</li> | 1 |
| 27 | 2 D13-1 (handbook V59) | methods/parts/G_appendix.html | <tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）</td><td><span class="st st-plan">不做</span></td><td>用户 2026-11-06 决定不做； | <tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）= 偏离 D13-1</td><td><span class="st st-plan">不做</span>（偏离 D13-1）</td><td>用户 2026-11-06 决定不做。D13-1：CPU 代理只在 L56 的 RQ2 上与已发表结论不一致（+0.064 [−0.032, +0.163]，区间含 0）；在… | 1 |
| 28 | 1+2 handbook deviation list (B) | methods/parts/B_global2.html | <tr><td>X1–X4 全部作者（补充 10 第 1 项）</td> | <tr><td>D13-1（补充 13 C-2）</td><td>代理与已发表结论不一致时按原 W 在 GPU 上重算</td><td>只在后改的 L56 上 RQ2 区间含 0（+0.064 [−0.032, +0.163]）；用户决定不做；锁定的 7 层积分终点上同向、区间不含 0</td><td><span class="st st-review">偏离</span></td><td><span class="src">381_s… | 1 |
| 29 | 2 D13-1 pointer (handbook C) | methods/parts/C_stage1_9.html | 按原 W 的 GPU 重算没有做（用户 2026-11-06 决定）。 | 按原 W 的 GPU 重算没有做（用户 2026-11-06 决定，偏离 D13-1，见附录 V59）。 | 1 |
| 30 | 3 X4 (report #m3x1x4-results) | stage1_11/stage1_11_report.html | (regex) 在同一引用档内，认得出的论文（target）比 control 更容易读出作者：标题位置 L8–L40 高 \+0\.04 到 \+0\.06，区间都不含 0<span class="src">（[^<]*）</span> | (fn) | 1 |
| 31 | 3 X4 (report m3x1x4 box + #pd-b1-xall) | stage1_11/stage1_11_report.html | ，认得出的论文在 L8–L40 更高<span class="src">（同节 Recognition 表，引用档内 target − control，全部作者 L8 +0.031 到 L40 +0.052，团队 CI 不含 0）</span> | ，认得出的论文方向上更高，但按预注册在测试集上不显著<span class="src">（第一作者，调参集选层 L8，测试集 target − control +0.023 [−0.001, +0.048]，582 篇，团队整群 95% CI；v42_paper_vs_team.md §3。全部作者 L8 +0.031 到 L40 +0.052 是全部 1,178 对合并，没有做调参/测试拆分；b1_xall_report.md Rec… | 2 |
| 32 | 3 X4 (handbook #s13-xall) | methods/parts/F_stage13.html | ，认得出的论文在 L8–L40 更高<span class="src">同节 Recognition 表：引用档内 target − control，全部作者 L8 +0.031 [0.017, 0.045] 到 L40 +0.052 [0.038, 0.067]</span> | ，认得出的论文方向上更高，但按预注册在测试集上不显著<span class="src">第一作者，调参集选层 L8，测试集 target − control +0.023 [−0.001, +0.048]（582 篇，团队整群 95% CI；v42_paper_vs_team.md §3）；同节 Recognition 表的全部作者 L8 +0.031 [0.017, 0.045] 到 L40 +0.052 [0.038, 0.067]… | 1 |
| 33 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | talk_docs/stage13_script_zh_en.html | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 34 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | advisor/index.html | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 35 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | process_report/draft_zh.md | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 36 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 37 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | pages_20261106b/methods_addendum/index.html | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 38 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | notes_zh.json #70 | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 39 | 3 X4 (notes 70/81, advisor, process, audit, addendum, Stage 13 script) | notes_zh.json #81 | 认得出的论文在 L8–L40 更高； | 认得出的论文方向上更高，但按预注册在测试集上不显著（L8 +0.023 [−0.001, +0.048]，v42_paper_vs_team.md §3）； | 1 |
| 40 | 3 X4 (handbook #s13-x4) | methods/parts/F_stage13.html | 认得出：author/title 的 target − control 在 L8–L40 为 +0.040 到 +0.060（区间不含 0），year 都含 0。 | 认得出：author/title 的 target − control 在全部 1,178 篇合并时 L8–L40 为 +0.040 到 +0.060（区间不含 0），但按预注册（调参集选层 L8、测试集确认）测试集为 +0.023 [−0.001, +0.048]，未确认；测试集 L16–L48 也为正（+0.025 到 +0.060）但为事后选层，只作探索（v42_paper_vs_team.md §3）；year 都含 0。 | 1 |
| 41 | 4 E4b §1 zh | stage1_11/stage1_11_report.html | 全部论文标题特异信号 L24 0.050、L40 0.061、L56 0.075，标准化只在训练折内拟合（作业 11500917） | E4b，target + control 1,395 篇的标题特异信号 L24 0.050、L40 0.061、L56 0.075，训练折标准化（作业 11500917） | 1 |
| 42 | 4 E4b §1 en | stage1_11/stage1_11_report.html | all papers L24 0.050, L40 0.061, L56 0.075, standardisation fitted on training folds only (job 11500917) | E4b, target + control (1,395 papers) L24 0.050, L40 0.061, L56 0.075, train-fold standardisation (job 11500917) | 1 |
| 43 | 4 E4b §6.11 zh | stage1_11/stage1_11_report.html | 真标题 − false_0；全部 1,863 篇；论文 bootstrap | 真标题 − false_0；target + control 1,395 篇（剔除标题复用后全部论文 1,863 篇，E4b 只用其中 1,395 篇）；论文 bootstrap | 1 |
| 44 | 4 E4b §6.11 en | stage1_11/stage1_11_report.html | true − false_0; all 1,863 papers; paper bootstrap | true − false_0; target + control, 1,395 papers (1,863 after the title-reuse exclusion; E4b uses 1,395 of them); paper bootstrap | 1 |
| 45 | 4 E4b §7 zh | stage1_11/stage1_11_report.html | 真标题 − false_0，全部 1,863 篇，L24–L60 | 真标题 − false_0，target + control 1,395 篇，L24–L60 | 1 |
| 46 | 4 E4b §7 en | stage1_11/stage1_11_report.html | true − false_0, all 1,863 papers, L24–L60 | true − false_0, target + control, 1,395 papers, L24–L60 | 1 |
| 47 | 4 standardisation §6.11 zh | stage1_11/stage1_11_report.html | 改后最大变化 0.0075，正则化强度不变 | 两种标准化差别最大 0.0007（L24/L40/L56 ≤ 0.0004；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py），正则化强度不变 | 1 |
| 48 | 4 standardisation §6.11 en | stage1_11/stage1_11_report.html | Largest change 0.0075, in the confirmatory configuration | The two standardisations differ by at most 0.0007 (≤ 0.0004 at L24/L40/L56; 381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py); in the confirmatory configuration | 1 |
| 49 | 4 standardisation tag zh | stage1_11/stage1_11_report.html | 381_stage13/reports/e4b_trainstd_compare.md "Max /new - orig/" 行与 All 4 configurations 表 | 381_stage13/reports/e4b_trainstd_compare.md All 4 configurations 表 | 1 |
| 50 | 4 standardisation tag en | stage1_11/stage1_11_report.html | 381_stage13/reports/e4b_trainstd_compare.md "Max /new - orig/" line and All 4 configurations table | 381_stage13/reports/e4b_trainstd_compare.md, All 4 configurations table | 1 |
| 51 | 4 E4b p4-plan narrative | stage1_11/stage1_11_report.html | 上面的数字用全部论文（含测试折）算均值和标准差。改为只用训练折后（作业 11500917），全部论文平均 L24 +0.050、L40 +0.061、L56 +0.075 | 上面“全部论文平均 +0.050 / +0.066 / +0.080”是 X1 对照流程（全部论文 1,863 篇）的数字。E4b（target + control 1,395 篇，训练折标准化，作业 11500917）为 L24 +0.050、L40 +0.061、L56 +0.075 | 1 |
| 52 | 4 standardisation p4-plan | stage1_11/stage1_11_report.html | 。最大变化 0.0075<span class="src">（381_stage13/reports/e4b_trainstd_compare.md “Max /new − orig/” 行）</span>，正则化强度不变，没有结论翻转。 | 。两种标准化差别最大 0.0007<span class="src">（L24/L40/L56 ≤ 0.0004；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py）</span>，正则化强度不变，没有结论翻转；0.066 / 0.080 与 0.061 / 0.075 的差别来自论文集合不同（1,863 篇 vs 1,395 篇），不是标准化。 | 1 |
| 53 | 4 X1-pipeline label (p4-plan) | stage1_11/stage1_11_report.html | 全部论文平均：L24 为 +0.050（原来 +0.045），L40 为 +0.066（原来 +0.062），L56 为 +0.080（原来 +0.081） | X1 对照流程，全部论文 1,863 篇平均：L24 为 +0.050（原来 +0.045），L40 为 +0.066（原来 +0.062），L56 为 +0.080（原来 +0.081） | 1 |
| 54 | 5 report §4 range | stage1_11/stage1_11_report.html | 全部论文标题特异信号 L16–L60 +0.042 到 +0.080，按团队分折并剔除标题复用（1,863 篇） | L16–L60 +0.041 到 +0.075（E4b，target + control 1,395 篇，训练折标准化），按团队分折并剔除标题复用 | 1 |
| 55 | 4 E4b notes 24 | notes_zh.json #24 | 训练折内标准化，全部 1,863 篇，L40 +0.061 | 训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇），L40 +0.061 | 1 |
| 56 | 4 E4b notes 39/40/73 | notes_zh.json #39 | 训练折内标准化，全部 1,863 篇：L24 +0.050 | 训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇）：L24 +0.050 | 1 |
| 57 | 4 E4b notes 39/40/73 | notes_zh.json #40 | 训练折内标准化，全部 1,863 篇：L24 +0.050 | 训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇）：L24 +0.050 | 1 |
| 58 | 4 E4b notes 39/40/73 | notes_zh.json #73 | 训练折内标准化，全部 1,863 篇：L24 +0.050 | 训练折内标准化，target + control 1,395 篇（剔除后全部论文 1,863 篇，E4b 只用其中 1,395 篇）：L24 +0.050 | 1 |
| 59 | 4 E4b deck method-page footnote | merged_deck/stage1_11_deck.html | all papers (1,863), team folds | target + control (1,395), team folds | 1 |
| 60 | 4 standardisation (advisor) | advisor/index.html | 标准化改为只在训练折内拟合，最大变化 0.0075，无结论翻转。 | 标准化改为只在训练折内拟合；两种标准化差别最大 0.0007，无结论翻转（381_stage13/e4b_standardisation_check/）。 | 1 |
| 61 | 4 standardisation (process) | process_report/draft_zh.md | 训练折标准化重算 11500917，最大差 0.0075，无翻转 | 训练折标准化重算 11500917，两种标准化差别最大 0.0007，无翻转 | 1 |
| 62 | 4 standardisation (handbook D) | methods/parts/D_stage10_11.html | 全部论文的标题特异信号最大差 0.0075； | 全部论文的标题特异信号最大差 0.0007（更正：原写 0.0075 来自 e4b_trainstd_compare.md 在 L24/L40/L56 混入 X1 行的标注错误；381_stage13/e4b_standardisation_check/trainstd_orig_corrected_fix.py）； | 1 |
| 63 | 4 E4b (handbook D) | methods/parts/D_stage10_11.html | 全部论文信号 L40 +0.066 → +0.061、L56 +0.080 → +0.075，区间都 &gt; 0； | E4b（target + control 1,395 篇）L40 +0.061、L56 +0.075，区间都 &gt; 0（+0.066 / +0.080 是 X1 对照流程全部 1,863 篇的数字，差别来自论文集合，不是标准化）； | 1 |
| 64 | 4 standardisation (handbook G) | methods/parts/G_appendix.html | ：最大差 0.0075，α 不变 | ：两种标准化差别最大 0.0007，α 不变 | 2 |
| 65 | 4 E4b (walkthrough methods) | talk_docs/experiment_walkthrough_methods_zh.html | L24 +0.050，L40 +0.066，L56 +0.080； | L24 +0.050，L40 +0.061，L56 +0.075（E4b，target + control 1,395 篇；X1 对照流程全部 1,863 篇为 +0.050 / +0.066 / +0.080）； | 1 |
| 66 | 4 standardisation (walkthrough methods) | talk_docs/experiment_walkthrough_methods_zh.html | 只在训练折内标准化的重算最大差 0.0075。 | 两种标准化差别最大 0.0007（L24/L40/L56 ≤ 0.0004）。 | 1 |
| 67 | 4 E4b narrative (walkthrough methods, addendum) | talk_docs/experiment_walkthrough_methods_zh.html | 全部论文信号 L40 0.066 → 0.061、L56 0.080 → 0.075 | E4b（target + control 1,395 篇）为 L40 0.061、L56 0.075；两种标准化差别最大 0.0007，0.066 / 0.080 是 X1 对照流程全部 1,863 篇的数字，差别来自论文集合，不是标准化 | 1 |
| 68 | 4 E4b narrative (walkthrough methods, addendum) | pages_20261106b/methods_addendum/index.html | 全部论文信号 L40 0.066 → 0.061、L56 0.080 → 0.075 | E4b（target + control 1,395 篇）为 L40 0.061、L56 0.075；两种标准化差别最大 0.0007，0.066 / 0.080 是 X1 对照流程全部 1,863 篇的数字，差别来自论文集合，不是标准化 | 1 |
| 69 | 4 E4b 1,395 note | talk_docs/experiment_walkthrough_methods_zh.html | 剩 1,863 篇（target 896、control 499）。</li> | 剩 1,863 篇（target 896、control 499）；E4b 信号只用其中 target + control 的 1,395 篇。</li> | 1 |
| 70 | 4 E4b (guide) | talk_docs/methods_handbook_guide_plain_zh.html | 剔除一题两用的论文（剩 1,863 篇）、只在训练折内标准化（最大差 0.0075，结论不变） | 剔除一题两用的论文（剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇）、只在训练折内标准化（两种标准化差别最大 0.0007，结论不变） | 1 |
| 71 | 4 E4b (walkthrough) | talk_docs/experiment_walkthrough_zh.html | 剩 1,863 篇。原版标准化用了全部论文（含测试折），复核时改为只在训练折内标准化重算，L40 从 0.066 变为 0.061、L56 从 0.080 变为 0.075，结论不变。 | 剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075。原版标准化用了全部论文（含测试折），复核时改为只在训练折内标准化；两种标准化差别最大 0.0007，结论不变。 | 1 |
| 72 | 4 E4b (keys & shelves zh) | talk_docs/keys_and_shelves_script_zh_en.html | 最后剩 1,863 篇。结果从 L24 起 | 最后剩 1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇。结果从 L24 起 | 1 |
| 73 | 4 standardisation (keys & shelves zh) | talk_docs/keys_and_shelves_script_zh_en.html | 原版标准化用了全部论文（含测试折），改成只在训练折内标准化重算后，L40 为 +0.061、L56 为 +0.075，结论不变。 | 原版标准化用了全部论文（含测试折），改成只在训练折内标准化；两种标准化差别最大 0.0007，L40 为 +0.061、L56 为 +0.075，结论不变。 | 1 |
| 74 | 4 E4b (keys & shelves en) | talk_docs/keys_and_shelves_script_zh_en.html | That leaves 1,863 papers. | That leaves 1,863 papers, of which the E4b signal uses the 1,395 target and control papers. | 1 |
| 75 | 4 standardisation (keys & shelves en) | talk_docs/keys_and_shelves_script_zh_en.html | refitting the standardisation on training folds only gives +0.061 at L40 and +0.075 at L56. | refitting the standardisation on training folds only changes the values by at most 0.0007 (+0.061 at L40, +0.075 at L56). | 1 |
| 76 | 4 E4b (progress talk doc) | talk_docs/progress_report_for_advisor_zh.html | 在按作者团队分折、剔除标题复用后（1,863 篇） | 在按作者团队分折、剔除标题复用后（1,863 篇，E4b 信号只用其中 target + control 的 1,395 篇） | 1 |
| 77 | 4 standardisation (progress talk doc) | talk_docs/progress_report_for_advisor_zh.html | 原版标准化用了全部论文，改为只在训练折内标准化重算后，L40 为 0.061、L56 为 0.075，结论不变。 | 原版标准化用了全部论文，改为只在训练折内标准化；两种标准化差别最大 0.0007，L40 为 0.061、L56 为 0.075，结论不变。 | 1 |
| 78 | 4 E4b (addendum) | pages_20261106b/methods_addendum/index.html | “全部论文”信号用 1,863 篇，组间比较用 1,395 篇。 | E4b 的信号和组间比较都用 target + control 的 1,395 篇；1,863 篇是剔除标题复用后的全部论文（X1 对照流程用）。 | 1 |
| 79 | 4 E4b label (advisor) | advisor/index.html | 换成随机论文的作者后约为 0） | 换成随机论文的作者后约为 0；E4b，target + control 1,395 篇，训练折标准化） | 1 |
| 80 | 4 E4b label (process) | process_report/draft_zh.md | 标题位置 probe 少量信号（L24 +0.050、L40 +0.061、L56 +0.075） | 标题位置 probe 少量信号（E4b，target + control 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075） | 1 |
| 81 | 4 原 E4b +0.066 (report) | stage1_11/stage1_11_report.html | 原 E4b 第一个 token +0.066<span class="src">（同节 Vpd 表 e4b_parity 行，L40 [0.059, 0.073]）</span> | 逐个排除版（4,654 篇）第一个 token +0.066<span class="src">（同节 Vpd 表 e4b_parity 行，L40 [0.059, 0.073]）</span>；原 E4b（1,395 篇）+0.061<span class="src">（同一报告第 2 节 V0 e4b_parity L40）</span> | 2 |
| 82 | 4 原 E4b +0.066 (others) | methods/parts/F_stage13.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 83 | 4 原 E4b +0.066 (others) | talk_docs/progress_report_for_advisor_zh.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 84 | 4 原 E4b +0.066 (others) | talk_docs/stage13_script_zh_en.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 85 | 4 原 E4b +0.066 (others) | advisor/index.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 86 | 4 原 E4b +0.066 (others) | process_report/draft_zh.md | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 87 | 4 原 E4b +0.066 (others) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 88 | 4 原 E4b +0.066 (others) | pages_20261106b/methods_addendum/index.html | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 89 | 4 原 E4b +0.066 (others) | notes_zh.json #72 | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 90 | 4 原 E4b +0.066 (others) | notes_zh.json #81 | 原 E4b 第一个 token +0.066 | 逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061 | 1 |
| 91 | 4 Vpd wording (d) | stage1_11/stage1_11_report.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 2 |
| 92 | 4 Vpd wording (d) | methods/parts/F_stage13.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 93 | 4 Vpd wording (d) | talk_docs/progress_report_for_advisor_zh.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 94 | 4 Vpd wording (d) | talk_docs/stage13_script_zh_en.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 95 | 4 Vpd wording (d) | advisor/index.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 96 | 4 Vpd wording (d) | process_report/draft_zh.md | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 97 | 4 Vpd wording (d) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 98 | 4 Vpd wording (d) | pages_20261106b/methods_addendum/index.html | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 99 | 4 Vpd wording (d) | notes_zh.json #72 | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 100 | 4 Vpd wording (d) | notes_zh.json #81 | E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题 | E4b 逐个假标题排除版（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071 | 1 |
| 101 | 4 Vpd wording (progress talk doc) | talk_docs/progress_report_for_advisor_zh.html | E4b 减 5 个假标题（L40 姓首 token +0.076 [0.068, 0.083]，4,654 篇） | E4b 逐个假标题排除版（L40 姓首 token +0.076 [0.068, 0.083]，4,654 篇，每篇平均约 1.5 个可用假标题；预注册版 1,395 篇为 +0.071） | 1 |
| 102 | 4 Vpd wording (advisor flag) | advisor/index.html | 减 5 个假标题平均 +0.076 | 逐个假标题排除版（4,654 篇，每篇约 1.5 个可用假标题）+0.076 | 1 |
| 103 | 4 Vpd wording (deck 81) | merged_deck/stage1_11_deck.html | E4b minus five false titles: surname L40 +0.076 | E4b, per-donor exclusion (4,654 papers, ~1.5 false titles each): surname L40 +0.076 | 1 |
| 104 | 4 Vpd wording (README, Stage 13 script en) | github/README_draft_20261106b.md | E4b minus five false titles (per-donor exclusion, 4,654 papers) | E4b with per-donor exclusion (4,654 papers, ~1.5 usable false titles per paper, 0–4; pre-registered false_0 version: +0.071 on 1,395 papers) | 1 |
| 105 | 4 Vpd wording (README, Stage 13 script en) | talk_docs/stage13_script_zh_en.html | E4b minus five false titles (per-donor exclusion, 4,654 papers) | E4b with per-donor exclusion (4,654 papers, ~1.5 usable false titles per paper, 0–4; pre-registered false_0 version: +0.071 on 1,395 papers) | 1 |
| 106 | 4 Vpd wording (README table) | github/README_draft_20261106b.md | / E4b minus five false titles (per-donor exclusion) / | / E4b with per-donor exclusion (~1.5 usable false titles per paper) / | 1 |
| 107 | 4 Vpd wording (deck 72 note title) | merged_deck/stage1_11_deck.html | <span class="h">Five false titles (batch 1)</span> | <span class="h">Per-donor exclusion (batch 1)</span> | 1 |
| 108 | 6 Pilot50 CI (notes 14) | notes_zh.json #14 | [4.7, 13.9] | [4.8, 14.0] | 1 |
| 109 | 6 Pilot50 CI (notes 14/30/61) | notes_zh.json #14 | [0.047, 0.139] | [0.048, 0.140] | 1 |
| 110 | 6 Pilot50 CI (notes 14/30/61) | notes_zh.json #30 | [0.047, 0.139] | [0.048, 0.140] | 1 |
| 111 | 6 Pilot50 CI (notes 14/30/61) | notes_zh.json #61 | [0.047, 0.139] | [0.048, 0.140] | 1 |
| 112 | 6 X3 lower bound 0.8647 -> 0.86 | stage1_11/stage1_11_report.html | 0.90 [0.87, 0.94] | 0.90 [0.86, 0.94] | 2 |
| 113 | 6 X3 lower bound 0.8647 -> 0.86 | merged_deck/stage1_11_deck.html | 0.90 [0.87, 0.94] | 0.90 [0.86, 0.94] | 1 |
| 114 | 6 X3 lower bound 0.8647 -> 0.86 | methods/parts/F_stage13.html | 0.90 [0.87, 0.94] | 0.90 [0.86, 0.94] | 1 |
| 115 | 6 X3 lower bound 0.8647 -> 0.86 | methods/parts/G_appendix.html | 0.90 [0.87, 0.94] | 0.90 [0.86, 0.94] | 1 |
| 116 | 6 X3 lower bound 0.8647 -> 0.86 | notes_zh.json #70 | 0.90 [0.87, 0.94] | 0.90 [0.86, 0.94] | 1 |
| 117 | 6 deck slide 17 | merged_deck/stage1_11_deck.html | low +6.8 [2.6, 11.6] | low +6.8 [2.5, 11.6] | 1 |
| 118 | 6 notes 30 | notes_zh.json #30 | +0.207 [0.20, 0.22] | +0.207 [0.195, 0.220] | 1 |
| 119 | 6 M2 year R² L16 (写法不统一) | stage1_11/stage1_11_report.html | 年份 R² 从 0.39（L16） | 年份 R² 从 0.38（L16） | 1 |
| 120 | 7 约 1/3 -> 0.35 | stage1_11/stage1_11_report.html | 名字先验只占目标−对照差的约 1/3 | 名字先验只占目标−对照差的约 0.35（约三分之一） | 1 |
| 121 | 7 约 1/3 -> 0.35 | advisor/index.html | 名字先验只占目标−对照差的约 1/3 | 名字先验只占目标−对照差的约 0.35（约三分之一） | 1 |
| 122 | 7 ~1/3 -> 0.35 (deck 30) | merged_deck/stage1_11_deck.html | Name prior is only ~1/3 of the gap | Name prior (delete-title condition) is only ~0.35 of the gap | 1 |
| 123 | 7 N2 19% definition (deck 67) | merged_deck/stage1_11_deck.html | → prior ≈ 19% of the gap | → pure name prior ≈ 19% of the gap (delete-title prior of §6.12: 0.35) | 1 |
| 124 | 7 N2 19% definition (notes 67) | notes_zh.json #67 | 先验约占 19%〔0.047 ÷ 0.247，由上两数算出〕 | 纯名字先验约占 19%〔0.047 ÷ 0.247，由上两数算出；与 §6.12 删标题条件下的先验 0.35 定义不同〕 | 1 |
| 125 | 7 约 0.70 -> 0.70–0.72 (advisor) | advisor/index.html | 领域准确率约 0.70， | 领域准确率约 0.70–0.72， | 1 |
| 126 | 7 约 0.70 -> 0.70–0.72 (process) | process_report/draft_zh.md | 领域约 0.70） | 领域约 0.70–0.72） | 1 |

Later edits (not in the log above):
- `apply_20261107h.py`: report #ov "…E4b 减 5 个假标题平均也已完成" → "…E4b 逐个假标题排除版（补充 10 第 4 项）也已完成"; progress talk doc "减 5 个假标题平均的版本（2026-11-06 完成）" → "逐个假标题排除的版本（补充 10 第 4 项，2026-11-06 完成）".
- `apply_20261107i.py`, D13-1 in its final wording (for_user §a lines 9–12):
  - Report Stage 8 box rebuilt. "因此，不一致只出现在后改的 L56 上；在原定的主终点上，代理结果不要求重算。" is deleted.
  - Added: the rule triggers when RQ1 or RQ2 changes, and this trigger came only from L56; report v29 / PPT v20 treat the 7-layer integral as the frozen primary endpoint (#p1-s8, PPT slide 17); L56 was an exploratory secondary that the 21:14 PROTOCOL.md promoted (U28); the 7-layer proxy is an approximation (Stage 10 has no L16); Stage 10 has exactly 5 false titles per paper (351_stage10.py lines 302, 863).
  - Report Part 5 "不做" line, handbook V59 and the B deviation-list row aligned to the same wording.
  - Numbers come from c2_followup_proxy.csv (aa_all). The 7-layer L16 = L24 RQ2 lower bound is 0.0055 in the CSV, so the documents write +0.005; the for_user text says +0.006.
- `apply_20261107j.py`: "拆分。。" → "拆分。" (report X4 sentence).
- `apply_20261107k.py`: re-applied U0 "n = 2,001" (tag and table), the H1 hypothesis-table cell and the X1 late-layer qualifier in the report.
- `apply_20261107l.py`: handbook D correction note no longer quotes the superseded 0.0075.
- pptx `Stage1-13_deck_v20f_editable.pptx`: slides 17, 24, 30, 67, 70, 72, 81 fixed at run level (all rules hit).

## 等用户定措辞 (held, unchanged)
Wording B, "按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 +0.030 [0.013, 0.048]）…", and its English and deck forms. The new audit gives the true 5-title average (V5x0, 1,395 papers) surname L40 = +0.024 [−0.006, +0.052], not significant. Locations:
- report: #alltok-results text, the batch-1 item-4 box in #alltok-results, #pd-b1-e4b5 (→ handbook K #k-b1-e4b5);
- handbook F #s13-alltok;
- deck note 72; deck slide 72 bullet "Target − control (five false titles, per-donor exclusion)" (HTML + pptx);
- advisor update box; methods addendum update box; scoring audit update box; process report §0;
- talk docs: progress_report_for_advisor_zh, stage13_script_zh_en (zh + en);
- README draft b (en).

## Not applied / for the user
- Item names that quote the pre-registered item title "E4b 与全部 token probe 减 5 个假标题平均" are left as item names: report Part 5 heading, box titles, handbook V58/B rows, and the plan 20261107 row "4 E4b and all-token probe minus five false titles".
- `plan_master_queue_20261107.md` already had 187/194 and 3-3 stopped. None of the round-d rules matched it, so it is unchanged.
- Deck slide 81 "Not done" line does not name D13-1. It was left unchanged for layout; deck note 82 carries the D13-1 limitation.
- Hypothesis-table images: no number changed, so they were not touched.
- Evidence PDF: none of its slides changed this round, so it was not re-exported.

## Strict check after the round
- `CLAIMS_DEFS=claims_defs_v6` (out_20261107_184952): 516 claims, 2,910 occurrences, all 一致.
- `claims_v5_post.py`: v6_all_non_ok = 0.
- v5_definition_issues still lists 34 rows. That list is static per claim (issue texts in the defs); each place now carries the fix in its text (1,395 / X1-pipeline labels, X4 test value, N2 definition note). The defs owner should mark them resolved.

## Exports (downloads/, previous kept)
| file | pages | MB |
|---|---|---|
| Stage1-13_report_v29f_A4.pdf | 116 | 11.8 |
| Stage1-13_methods_handbook_A4.v20261107d.pdf | 218 | 10.4 |
| Stage1-13_deck_v20f_editable.pptx |  | 4.8 |
| Stage1-13_deck_v20f_editable.pptx.b64.txt |  | 6.4 |
| Stage1-13_deck_v20f_slides_part1of3_p1-27.pdf | 27 | 9.1 |
| Stage1-13_deck_v20f_slides_part2of3_p28-55.pdf | 28 | 11.8 |
| Stage1-13_deck_v20f_slides_part3of3_p56-82.pdf | 27 | 7.7 |
| Stage1-13_deck_v20f_with_notes_zh_part1of3_p1-27.pdf | 27 | 10.4 |
| Stage1-13_deck_v20f_with_notes_zh_part2of3_p28-55.pdf | 28 | 13.1 |
| Stage1-13_deck_v20f_with_notes_zh_part3of3_p56-82.pdf | 27 | 9.2 |
| jlens_process_report_2026-11-07d_A4.pdf | 28 | 2.9 |
| jlens_progress_report_2026-11-07d_A4.pdf | 10 | 3.0 |
| methods_addendum_2026-11-07d_A4.pdf | 21 | 3.3 |
| scoring_audit_2026-11-07d_A4.pdf | 33 | 1.5 |
| talkdoc_experiment_walkthrough_methods_zh_20261107d_A4.pdf | 10 | 0.8 |
| talkdoc_experiment_walkthrough_zh_20261107d_A4.pdf | 5 | 0.4 |
| talkdoc_keys_and_shelves_script_zh_en_20261107d_A4.pdf | 6 | 0.4 |
| talkdoc_methods_handbook_guide_plain_zh_20261107d_A4.pdf | 12 | 0.8 |
| talkdoc_progress_report_for_advisor_zh_20261107d_A4.pdf | 7 | 0.7 |
| talkdoc_stage13_script_zh_en_20261107d_A4.pdf | 6 | 0.3 |

Screenshots checked:
- `sync_20261107/shots_d/` (report D13-1 box, #pd-running, #pd-limits, X4 sentence, §6.11; handbook V59; advisor limitations);
- `talk/src/export/shots/v20f/` (deck slides 17, 24, 30, 67, 70, 72, 81).

Local HTML files to publish: same paths and artifacts as in `sync_20261107_manifest.md`, FINAL section.
