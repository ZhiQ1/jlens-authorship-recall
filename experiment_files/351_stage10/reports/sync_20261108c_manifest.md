# Sync 2026-11-08 c — change manifest (report v30, deck v21, handbook 2026-11-08 c; LOCAL only, NOT published, NOT pushed)

Source of truth: `~/jlens_work/conclusions_v30_draft.md` (C01–C23, L01–L14, §六) and `conclusions_v30_checks.md`. User-confirmed: D13-1 (for_user_2026-11-07.md §a), R1 = C04, R4 = C08 (review_queue.md "已确认", PROGRESS 2026-11-08). Other changes are downgrades / premises / limitations / status (HANDOFF autonomous sync mode).

Scripts: `sync_20261107/apply_20261108c.py` (main; asserts every number against 391_groups/summary_b1_p12f/*.csv and reports/b2_cd_report.md, b1_p12f_report.md), `sync_20261107/apply_20261108c_part2.py` (remaining status notes). Fresh backups `*.before_20261108c` (asserted not to exist before). Log: `sync_20261107/apply_log_20261108c.json`.
Rebuilt (not edited by hand): `methods/methods_handbook.html` = build_methods.py(parts) — part K regenerated from the report (edit_20261107d.py conversion, lead "第 30 版"); `process_report/index.html` = build_process_report.py(draft_zh.md); `talk/src/export/with_notes.html` is rewritten by the deck export from notes_zh.json (here only the D13-1 passage was re-inserted).
D13-1: all 16 held passages re-inserted verbatim (anchors from `*.before_20261108b`): report ×4, notes ×1, with_notes ×1, parts B/G/C ×3 directly; handbook entries 6–10 and K entries 12–13 via the rebuild (checked by assertion after the build).

## Changes per file (count)

| file | changes |
|---|---|
| /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 5 |
| advisor/index.html | 10 |
| github/README_draft_20261106b.md | 13 |
| merged_deck/stage1_11_deck.html | 17 |
| methods/build_methods.py | 1 |
| methods/parts/B_global2.html | 1 |
| methods/parts/C_stage1_9.html | 3 |
| methods/parts/E_stage12.html | 1 |
| methods/parts/F_stage13.html | 3 |
| methods/parts/G_appendix.html | 1 |
| methods/parts/K_post_defence.html | 1 |
| notes_zh.json | 19 |
| pages_20261106b/methods_addendum/index.html | 7 |
| process_report/draft_zh.md | 7 |
| stage1_11/stage1_11_report.html | 34 |
| talk/src/export/notes_zh.json | 1 |
| talk/src/export/with_notes.html | 1 |
| talk_docs/experiment_walkthrough_methods_zh.html | 3 |
| talk_docs/experiment_walkthrough_zh.html | 3 |
| talk_docs/keys_and_shelves_script_zh_en.html | 2 |
| talk_docs/methods_handbook_guide_plain_zh.html | 2 |
| talk_docs/progress_report_for_advisor_zh.html | 6 |
| talk_docs/stage13_script_zh_en.html | 4 |

## All changes (rule · file · before → after · count)

| # | rule | file | before | after | count |
|---|---|---|---|---|---|
| 1 | a D13-1 back (held json) | stage1_11/stage1_11_report.html | （用户 2026-11-06 决定） | （用户 2026-11-06 决定，偏离 D13-1，见下框） | 1 |
| 2 | a D13-1 back (held json) | stage1_11/stage1_11_report.html | (anchor: 有做（用户 2026-11-06 决定，偏离 D13-1，见下框）。</div>) |  ⏎ <div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>按补充 13 C-2 的判定规则（prereg_addendum13.json 第 18 行），全部作者 CPU 代理（public J-lens 名次、Stage 10 的 5 个假标题——… | 1 |
| 3 | a D13-1 back (held json) | stage1_11/stage1_11_report.html | <li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做；CPU 代理见 Stage 8 节）。</li> | <li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做，列为偏离 D13-1：规则是 RQ1 或 RQ2 任一改变即触发，本次只来自 L56（PROTOCOL.md 后改的终点，U28）的 RQ2；在锁定计划的 7 … | 1 |
| 4 | a D13-1 back (held json) | stage1_11/stage1_11_report.html | (anchor: 3_33_v2/v2_C1_summary.json）</span></li> ⏎ ) | <li><b>Stage 8 L56 的 RQ2 没有用原统计量复核。</b>CPU 代理只在后改的 L56 上区间含 0，按补充 13 触发了 W 的 GPU 重算；用户决定不做（偏离 D13-1，见 Stage 8 节）。</li> ⏎  | 1 |
| 5 | a D13-1 back (held json) | talk/src/export/notes_zh.json | (anchor: 81_stage13/b3_33_v2/v2_C1_summary.json〕）) | Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1〔381_stage13/reports/c13_C2.md；381_stage13/c13_C2_followup/c2_followup_proxy.csv〕）。 | 1 |
| 6 | a D13-1 back (held json) | talk/src/export/with_notes.html | (anchor: e13/b3_33_v2/v2_C1_summary.json）</span>）) | Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1<span class="src">（381_stage13/reports/c13_C2.md；381_stage13/c13_C2_followup/c2_followup_proxy.csv）</span>）。 | 1 |
| 7 | a D13-1 back (held json) | methods/parts/B_global2.html | (anchor: ports/b1_x7f_report.md</span></td></tr> ⏎ ) | <tr><td>D13-1（补充 13 C-2）</td><td>代理与已发表结论不一致时按原 W 在 GPU 上重算</td><td>只在后改的 L56 上 RQ2 区间含 0（+0.064 [−0.032, +0.163]）；用户决定不做；规则是 RQ1 或 RQ2 任一改变即触发，本次只来自 … | 1 |
| 8 | a D13-1 back (held json) | methods/parts/G_appendix.html | <tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）</td><td><span class="st st-plan">不做</span></td><td>用户 2026-11-06 决定不做；只报 CPU 代理（public J… | <tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）= 偏离 D13-1</td><td><span class="st st-plan">不做</span>（偏离 D13-1）</td><td>用户 2026-11-06 决定不… | 1 |
| 9 | a D13-1 back (held json) | methods/parts/C_stage1_9.html | （用户 2026-11-06 决定） | （用户 2026-11-06 决定，偏离 D13-1，见附录 V59） | 1 |
| 10 | version header v30 | stage1_11/stage1_11_report.html | 更新于 2026-11-06（第 29 版：Stage 1–13；答辩后新增见第五部分；补充 9–13 的重做结果已写入各节，批次 1 只剩 P1 / P2 五个假标题在运行；正文数字后的灰色小字是出处） | 更新于 2026-11-08（第 30 版：Stage 1–13；答辩后新增见第五部分；补充 9–13 的重做结果已写入各节；批次 1 全部完成，批次 2 的 C / D 组补全已完成、其余各项进行中，批次 3 等批次 2 结束后开始；本版放回偏离 D13-1，写明 Stage 8 结论的三个前提，… | 1 |
| 11 | b status (intro box) | stage1_11/stage1_11_report.html | X1–X4 改为全部作者、E4b 逐个假标题排除版（补充 10 第 4 项）也已完成，结论不变；P1 / P2 用 5 个假标题还在运行（第五部分）。 | X1–X4 改为全部作者、E4b 逐个假标题排除版（补充 10 第 4 项）、P1 / P2 用 5 个假标题（补充 10 第 3 项）也已完成，结论不变；批次 2 中 C / D 组补全已完成：C 的信号更大，但时间点与 A 相同（第五部分）。 | 1 |
| 12 | version label (hypotheses table) | stage1_11/stage1_11_report.html | 目前结果（第 29 版，2026-11-07） | 目前结果（第 30 版，2026-11-08） | 1 |
| 13 | d X4 not H2 evidence (table) | stage1_11/stage1_11_report.html | 另外，X4 最早可解码的顺序是第一作者（L8）早于年份（L40），与 H2 预测的方向相反。<b>X2 不支持。</b></td> | 另外，X4 最早可解码的顺序是第一作者（L8）早于年份（L40），与 H2 预测的方向相反；X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。<b>X2 不支持。</b></td… | 1 |
| 14 | d X4 not H2 evidence (overall judgement) | stage1_11/stage1_11_report.html | X4 的顺序与 H2 预测相反，X2 不支持（2026-11-05）。H3： | X4 的顺序与 H2 预测相反，X2 不支持（2026-11-05）。第 30 版补：X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。H3： | 1 |
| 15 | d X4 not H2 evidence (X4 section) | stage1_11/stage1_11_report.html | 但这些层是事后选的，只作探索。全部作者版本（+0.031 到 +0.052）没有做调参/测试拆分。年份没有这种差别。 | 但这些层是事后选的，只作探索。全部作者版本（+0.031 到 +0.052）没有做调参/测试拆分。年份没有这种差别。这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。 | 1 |
| 16 | e L01 qualifier (X4 year L40) | stage1_11/stage1_11_report.html | 年份要到 L40 才能读出，而且很弱。 | 年份要到 L40 才能读出（前一个测量层是 L32，真实起点在 L33–L40 之间；作者早于年份的顺序不受影响），而且很弱。 | 1 |
| 17 | e L01 qualifier (X4 peak L40) | stage1_11/stage1_11_report.html | +0.046 [0.035, 0.059]，L40 最高 +0.068</td> | +0.046 [0.035, 0.059]，L40 最高 +0.068（两侧测量层为 L32、L48，真实峰值可能在 L33–L47）</td> | 1 |
| 18 | e L01 qualifier (Jacobian vs logit from L40) | stage1_11/stage1_11_report.html | Jacobian lens 从 L40 起明显好于 logit lens（约 −3.0） | Jacobian lens 从 L40 起（前一个测量层是 L32，跳变在 L33–L40 的哪一层不知道）明显好于 logit lens（约 −3.0） | 1 |
| 19 | e L01 qualifier (en) | stage1_11/stage1_11_report.html | The Jacobian lenses beat the logit lens from L40 on (about −3.0) | The Jacobian lenses beat the logit lens from L40 on (the previous measured layer is L32, so the jump lies somewhere in L33–L40; about −3.0) | 1 |
| 20 | a/C07 Stage 8 box: int6 is not the frozen endpoint | stage1_11/stage1_11_report.html | 用 Stage 10 已有的原始分数，在 Stage 8 的 200 篇论文上重算冻结的多层终点：全部作者、全部名字 token 的版本中 RQ1 和 RQ2 都成立——public J-lens 6 层平均 RQ1 +0.130 [0.108, 0.153] | 用 Stage 10 已有的原始分数，在 Stage 8 的 200 篇论文上重算：全部作者、全部名字 token 的版本中，public J-lens 6 层平均（int6，L24–L62 每 8 层，少了 L16，与 10-18 14:29 锁定的 7 层积分终点不是同一终点）RQ1 和 RQ2… | 1 |
| 21 | a/C07 Stage 8: three premises | stage1_11/stage1_11_report.html | （用户 2026-11-06 决定，偏离 D13-1，见下框）。</div> | （用户 2026-11-06 决定，偏离 D13-1，见下框）。Stage 8 的结论（RQ1、RQ2）较稳，但有三个前提：① W 只给第一作者名字的第一个 token 打分，在 Stage 8 的 200 篇里有 129 篇（64.5%）这个 token 只是首字母<span class="src… | 1 |
| 22 | c C08 (Stage 10 R1 section) | stage1_11/stage1_11_report.html | C 只有 36 篇，这一点只作描述<span class="src">（Stage 11 样本 target R1；351_stage10/reports/r0_r1_analysis.md §5）</span>。</p> | 这 36 篇只作描述<span class="src">（Stage 11 样本 target R1；351_stage10/reports/r0_r1_analysis.md §5）</span>。<b>2026-11-08 补（补充 11 B，C / D 组补全）：</b>C 组未写出作者 46… | 1 |
| 23 | c C08 (three-scope table) | stage1_11/stage1_11_report.html | <td>同样 L52 完成，L40–48 略慢（n = 36）</td> | <td>同样 L52 完成；36 篇中 L40–48 略慢，补全到 462 篇后同一引用档内时间点与 A 相同（补充 11 B）</td> | 1 |
| 24 | c table P5.1 C row (R4) | stage1_11/stage1_11_report.html | <td>+0.721 [+0.650, +0.806]; n = 32 (166 authors)</td><td>+0.996 [+0.968, +1.026]; n = 32 (166 authors)</td><td>+0.016 [-0.023, +0.048]; n = 32 (166 a… | <td>+0.731 [+0.705, +0.757]; n = 462 (2103 authors)</td><td>+0.985 [+0.977, +0.994]; n = 462 (2103 authors)</td><td>+0.014 [+0.005, +0.023]; n = 462 (… | 1 |
| 25 | c table P5.1 D row (R4) | stage1_11/stage1_11_report.html | <td>+0.745; n = 5 (16 authors); n &lt; 30, descriptive</td><td>+0.979; n = 5 (16 authors); n &lt; 30, descriptive</td><td>+0.023; n = 5 (16 authors); … | <td>+0.786 [+0.674, +0.952]; n = 33 (141 authors); descriptive (addendum 11)</td><td>+0.968 [+0.917, +1.041]; n = 33 (141 authors); descriptive (adden… | 1 |
| 26 | c table P5.1 source note (R4) | stage1_11/stage1_11_report.html | U0 和 R2s 的 E1 / E2 格来自补充 8 的重跑（391_groups/summary_rerun/rerun_group_values.csv）；R2s 只作参照，不给区间。</p> | U0 和 R2s 的 E1 / E2 格来自补充 8 的重跑（391_groups/summary_rerun/rerun_group_values.csv）；R2s 只作参照，不给区间。C、D 的 E1 / E2 格来自补充 11 B 的补全（C 462 篇、D 33 篇有未写出作者；391_gr… | 1 |
| 27 | c C denominator 0.464 -> 0.559 | stage1_11/stage1_11_report.html | A 0.407、B 0.214、U0 0.293、C 0.464<span class="src">（补充 8 / Stage 11，E1，未写出作者，最终输出，mean(真 − false_0)；A 557、B 586、U0 599、C 32 篇；391_groups/reports/e1_num… | A 0.407、B 0.214、U0 0.293、C 0.559<span class="src">（补充 8 / Stage 11，E1，未写出作者，最终输出，mean(真 − false_0)；A 557、B 586、U0 599 篇；391_groups/reports/e1_num_den.… | 1 |
| 28 | c C/D completion (groups list) | stage1_11/stage1_11_report.html | C 只有 32 篇、D 5 篇、R2 中有未写出作者的论文 28 篇<span class="src">（rerun_report.md Counts 表，papers_unwritten 列）</span>，都只作描述，不下结论。</li> | C 组已按补充 11 B 补全到 462 篇（未写出作者），可以下结论，见下文 C / D 组补全；D 33 篇按补充 11 只作描述；R2 中有未写出作者的论文 28 篇<span class="src">（rerun_report.md Counts 表，papers_unwritten 列；3… | 1 |
| 29 | c table P5.2 C row | stage1_11/stage1_11_report.html | <tr><td>C（R1 × 认得出，描述）</td><td>32</td><td>+0.464 [0.388, 0.538]</td><td>+0.335</td><td>+0.721 [0.650, 0.806]</td><td>+0.462</td><td>+0.996 [0.968, 1.0… | <tr><td>C（R1 × 认得出；补充 11 B 补全）</td><td>462</td><td>+0.559 [0.529, 0.590]</td><td>+0.408</td><td>+0.731 [0.705, 0.757]</td><td>+0.551</td><td>+0.985 [0… | 1 |
| 30 | c table P5.2 note | stage1_11/stage1_11_report.html | ；D（5 篇）和 R2 中未写出的作者（28 篇）见原表，只作描述。</p> | ；C 行为补充 11 B 补全后的 462 篇（391_groups/reports/b2_cd_report.md；原 Stage 11 样本 32 篇时分母 0.464、R(L48) 0.721）；D（33 篇，补充 11 B）和 R2 中未写出的作者（28 篇）只作描述。</p> | 1 |
| 31 | b R1 colon B/A | stage1_11/stage1_11_report.html | ':' token 在 L44–L48 两组分子相近（B/A 0.78–0.99<span class="src">（P1 只替换 “:”，分子 B/A：L44 0.78、L48 0.99；同一文件 B_over_A_numerator 列）</span>） | ':' token 在 L44–L48 两组分子相近（B/A：5 个假标题版 0.72–0.87，false_0 版 0.78–0.99<span class="src">（P1 只替换 “:”，分子 B/A：5 个假标题版 L44 0.72、L48 0.87，391_groups/reports/… | 1 |
| 32 | b batch-1 status | stage1_11/stage1_11_report.html | <li><b>批次 1（补充 10）：</b>第 1、2、4 项已完成；第 3 项还在运行。 | <li><b>批次 1（补充 10）：</b>第 1–4 项都已完成。 | 1 |
| 33 | b R1 P1/P2 result (report) | stage1_11/stage1_11_report.html | <li id="pd-b1-p12f"><b>P1 / P2 用 5 个假标题（补充 10 第 3 项）：还在运行。</b>结果经用户确认后补入。</li> | <li id="pd-b1-p12f"><b>P1 / P2 用 5 个假标题（补充 10 第 3 项，已完成）：</b>按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L4… | 1 |
| 34 | b R1 note at Stage 12 P1 table | stage1_11/stage1_11_report.html | (regex) (<tr><td>标题的右引号（p9）</td>.*?</table></div>) | (computed) | 1 |
| 35 | f batch-2 status | stage1_11/stage1_11_report.html | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 36 | f batch-2 status | advisor/index.html | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 37 | f batch-2 status | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 38 | f batch-2 status | pages_20261106b/methods_addendum/index.html | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 39 | f batch-2 status | process_report/draft_zh.md | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 40 | f batch-2 status | notes_zh.json #81 | 代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成；2-11 模型自生成名字的首名复现率 0.880 < 0.90，按预注册停止，改为 2-11b（补充 15，已锁定），只跑第 0 个分片，排队中；名字位置 probe 等其余各项进行中，没有可报告的结果 | 1 |
| 41 | f batch-3 status | stage1_11/stage1_11_report.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始 | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 42 | f batch-3 status | advisor/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始 | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 43 | f batch-3 status | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始 | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 44 | f batch-3 status | pages_20261106b/methods_addendum/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始 | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 45 | f batch-3 status | process_report/draft_zh.md | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：代码已就绪，第二批之后开始 | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 46 | f batch-3 status (short form) | talk_docs/progress_report_for_advisor_zh.html | 3-1、3-2 代码已就绪，第二批之后开始 | 3-1、3-2 编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 47 | f batch-3 status (short form) | notes_zh.json #81 | 3-1、3-2 代码已就绪，第二批之后开始 | 3-1、3-2 编排作业已提交，第二批全部结束后自动开始（进行中） | 1 |
| 48 | e limitations L01-L05, L09 (report) | stage1_11/stage1_11_report.html | <li><b>高引用档缺对照。</b>4097+ 档没有 B / D 论文<span class="src">（Stage 10 队列 4097+ 档：目标 84 篇、对照 0 篇；381_stage13/reports/m3_scores.md 第 2 节）</span>，引用档内比较用不到这一档… | <li><b>高引用档缺对照。</b>4097+ 档没有 B / D 论文<span class="src">（Stage 10 队列 4097+ 档：目标 84 篇、对照 0 篇；381_stage13/reports/m3_scores.md 第 2 节）</span>，引用档内比较用不到这一档… | 1 |
| 49 | d X4 not H2 evidence (batch-1 sentence) | stage1_11/stage1_11_report.html | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 2 |
| 50 | d X4 not H2 evidence (batch-1 sentence) | advisor/index.html | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 51 | d X4 not H2 evidence (batch-1 sentence) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 52 | d X4 not H2 evidence (batch-1 sentence) | pages_20261106b/methods_addendum/index.html | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 53 | d X4 not H2 evidence (batch-1 sentence) | process_report/draft_zh.md | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 54 | d X4 not H2 evidence (batch-1 sentence) | talk_docs/stage13_script_zh_en.html | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 55 | d X4 not H2 evidence (batch-1 sentence) | notes_zh.json #70 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 56 | d X4 not H2 evidence (batch-1 sentence) | notes_zh.json #81 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释 | ；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 57 | f box title | advisor/index.html | <b>2026-11-06 更新：答辩后的重做计划（批次 1 结果，用户已确认措辞）</b> | <b>2026-11-06 / 11-08 更新：答辩后的重做计划（批次 1 全部结果、批次 2 的 C / D 组补全、报告第 30 版的前提和局限，用户已确认措辞）</b> | 1 |
| 58 | f box title | pages_20261106b/methods_addendum/index.html | <b>2026-11-06 更新：答辩后的重做计划（批次 1 结果，用户已确认措辞）</b> | <b>2026-11-06 / 11-08 更新：答辩后的重做计划（批次 1 全部结果、批次 2 的 C / D 组补全、报告第 30 版的前提和局限，用户已确认措辞）</b> | 1 |
| 59 | f box title (audit) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | <b>2026-11-06 更新：本审计指出的打分单位问题，答辩后已重做的部分</b> | <b>2026-11-06 / 11-08 更新：本审计指出的打分单位问题，答辩后已重做的部分（含报告第 30 版的前提和局限）</b> | 1 |
| 60 | b/c/a/e update box (advisor, audit, addendum) | advisor/index.html | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项）：还在运行</b>，结果经用户确认后补入。<span style="color:#8a8f98;font-size:.8em">（g391_b1p12f 作业链（14_groups/b1_p12f_gpu_v2.sbatch））<… | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集… | 1 |
| 61 | b/c/a/e update box (advisor, audit, addendum) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项）：还在运行</b>，结果经用户确认后补入。<span style="color:#8a8f98;font-size:.8em">（g391_b1p12f 作业链（14_groups/b1_p12f_gpu_v2.sbatch））<… | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集… | 1 |
| 62 | b/c/a/e update box (advisor, audit, addendum) | pages_20261106b/methods_addendum/index.html | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项）：还在运行</b>，结果经用户确认后补入。<span style="color:#8a8f98;font-size:.8em">（g391_b1p12f 作业链（14_groups/b1_p12f_gpu_v2.sbatch））<… | <li><b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集… | 1 |
| 63 | f process §0 title | process_report/draft_zh.md | ## 0. 2026-11-06 更新：答辩后的重做计划（批次 1 结果，用户已确认措辞） | ## 0. 2026-11-06 / 11-08 更新：答辩后的重做计划（批次 1 全部结果、批次 2 的 C / D 组补全、报告第 30 版的前提和局限，用户已确认措辞） | 1 |
| 64 | b/c/a/e process §0 | process_report/draft_zh.md | - **P1 / P2 用 5 个假标题（批次 1 第 3 项）：还在运行**，结果经用户确认后补入。【g391_b1p12f 作业链（14_groups/b1_p12f_gpu_v2.sbatch）】 | - **P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：**按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集到名字位置… | 1 |
| 65 | version label (advisor) | advisor/index.html | 〔2026-11-06 已更新：当前为第 29 版（本地已备，待发布）；见页首更新框〕 | 〔2026-11-08 已更新：当前为第 30 版；见页首更新框〕 | 1 |
| 66 | d X4 (advisor H2 row) | advisor/index.html | 不支持或分不开：M3 不高于 L4；X3 分不开语义与论文身份；X4 顺序与预测相反 | 不支持或分不开：M3 不高于 L4；X3 分不开语义与论文身份；X4 顺序与预测相反；X4 中认得出的论文更高这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | 1 |
| 67 | e limitations (advisor) | advisor/index.html | <li>Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1）。</li> | <li>Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1）。Stage 8 的结论有三个前提：W 只给第一作者的第一个 token 打分（64.5% 是首字母）；D13-1；U28（L56 是后改的终点，原因待查）。</li> ⏎ <li><b>层不完整（第 30 版补）。… | 1 |
| 68 | e limitations pointer (process) | process_report/draft_zh.md | - 已知局限（不再补做）：单模型；teacher forcing；Fit B 未完成，lens 稳定性只有 Fit A 一份证据；F1 未做对半拟合；X2 未做。〔2026-11-06 已更新：X2 已完成；Fit B、F1 对半列入批次 2；见第 0 节〕 | - 已知局限（不再补做）：单模型；teacher forcing；Fit B 未完成，lens 稳定性只有 Fit A 一份证据；F1 未做对半拟合；X2 未做。〔2026-11-06 已更新：X2 已完成；Fit B、F1 对半列入批次 2；见第 0 节〕〔2026-11-08 已更新：第 30 … | 1 |
| 69 | version label (walkthrough) | talk_docs/experiment_walkthrough_zh.html | 2026-11-06 起与报告 v29 一致，重做计划的新结果用绿色框标出。 | 2026-11-06 起与报告 v29 一致，2026-11-08 起与报告第 30 版一致，重做计划的新结果用绿色框标出。 | 1 |
| 70 | version label (walkthrough methods) | talk_docs/experiment_walkthrough_methods_zh.html | 配合 PPT v20 和报告 v29 使用（2026-11-06 更新：补充 9、X7 五个假标题等重做结果已加入）。 | 配合 PPT v21 和报告第 30 版使用（2026-11-08 更新：P1 / P2 五个假标题、C / D 组补全、Stage 8 的三个前提和新增局限已加入；2026-11-06 更新：补充 9、X7 五个假标题等重做结果已加入）。 | 1 |
| 71 | a/C07 premises (walkthrough) | talk_docs/experiment_walkthrough_zh.html | 改动人和理由待查（U28）；我们把原定主终点和 L56 都报告了。</p> | 改动人和理由待查（U28）；我们把原定主终点和 L56 都报告了。</p> ⏎ <p class="upd">2026-11-08（报告第 30 版）：Stage 8 的结论（真标题让模型更偏好真实第一作者 RQ1；A 组强于 B 组 RQ2）较稳，但有三个前提：① W 只给第一作者名字的第一个 tok… | 1 |
| 72 | a/C07 premises (walkthrough methods) | talk_docs/experiment_walkthrough_methods_zh.html | 改动人和理由待查（U28）；两种都报告。）</p> | 改动人和理由待查（U28）；两种都报告。）</p> ⏎ <p class="upd">2026-11-08（报告第 30 版）：Stage 8 的结论（真标题让模型更偏好真实第一作者 RQ1；A 组强于 B 组 RQ2）较稳，但有三个前提：① W 只给第一作者名字的第一个 token 打分，在 Stag… | 1 |
| 73 | b/c/d/e update (walkthrough end) | talk_docs/experiment_walkthrough_zh.html | <p><strong>局限</strong>：“只用了一个模型；测的是把正确名字放进去打分的偏好，不是真实生成；读出工具的稳定性只有一份拟合证据。”</p> | <p><strong>局限</strong>：“只用了一个模型；测的是把正确名字放进去打分的偏好，不是真实生成；读出工具的稳定性只有一份拟合证据。”</p> ⏎ <p class="upd">2026-11-08（报告第 30 版）：<b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，… | 1 |
| 74 | b/c/d/e update (walkthrough methods end) | talk_docs/experiment_walkthrough_methods_zh.html | <p><strong>局限</strong>：一个模型；teacher forcing 下的偏好不是生成；lens 拟合稳定性只有 Fit A；高引用档几乎没有 control。</p> | <p><strong>局限</strong>：一个模型；teacher forcing 下的偏好不是生成；lens 拟合稳定性只有 Fit A；高引用档几乎没有 control。</p> ⏎ <p class="upd">2026-11-08（报告第 30 版）：<b>P1 / P2 用 5 个假标题（… | 1 |
| 75 | b/c R1 + C/D (Stage 13 script zh) | talk_docs/stage13_script_zh_en.html | 381_stage13/reports/e4b_alltok.md；b1_e4b5_report.md）</span>。P1/P2 五个假标题还在运行。</p> | 381_stage13/reports/e4b_alltok.md；b1_e4b5_report.md）</span>。<b>P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：</b>按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。… | 1 |
| 76 | b/c R1 + C/D (Stage 13 script en) | talk_docs/stage13_script_zh_en.html | <span class="src">(b1_e4b5_report.md)</span>. P1 / P2 with five false titles still running.</p> | <span class="src">(b1_e4b5_report.md)</span>. P1 / P2 with five false titles, done: Addendum 10 line 27 makes the five-title mean primary; the publish… | 1 |
| 77 | d X4 (Stage 13 script) | talk_docs/stage13_script_zh_en.html | 另外 X4 最早解码出的是第一作者（L8），年份要到 L40，和 H2 预测的顺序相反。 | 另外 X4 最早解码出的是第一作者（L8），年份要到 L40，和 H2 预测的顺序相反；X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。 | 1 |
| 78 | d X4 (handbook guide) | talk_docs/methods_handbook_guide_plain_zh.html | 和 H2 预测的“先年份后作者”顺序相反</strong>。</p> | 和 H2 预测的“先年份后作者”顺序相反</strong>。X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。</p> | 1 |
| 79 | a/b/c/d/e update (handbook guide) | talk_docs/methods_handbook_guide_plain_zh.html | (regex) (<p>配合《Stage 1–13 方法手册》（259 页，2026-10-30 版）使用。.*?</p>) | (computed) | 1 |
| 80 | e L02 (keys and shelves zh) | talk_docs/keys_and_shelves_script_zh_en.html | 需要坦白的一点是：一致性容差是在看到差距之后才从 0.25 放宽到 0.5 的，这一点写在局限里。</p> | 需要坦白的一点是：一致性容差是在看到差距之后才从 0.25 放宽到 0.5 的，这一点写在局限里；而且这次放宽确实用到了：Stage 10 主轮 25 个（读出 × 层）组合的最大差 0.367，只有按 0.5 才通过。</p> | 1 |
| 81 | e L02 (keys and shelves en) | talk_docs/keys_and_shelves_script_zh_en.html | the parity tolerance was relaxed from 0.25 to 0.5 after we saw the gaps, and this is listed as a limitation.</p> | the parity tolerance was relaxed from 0.25 to 0.5 after we saw the gaps, and this is listed as a limitation; the relaxation was actually used: the Sta… | 1 |
| 82 | d X4 (talk-doc progress report) | talk_docs/progress_report_for_advisor_zh.html | X4 先解码出第一作者（L8）再解码年份（L40），和 H2 预测的顺序相反；X3 见下 | X4 先解码出第一作者（L8）再解码年份（L40），和 H2 预测的顺序相反；X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。X3 见下 | 1 |
| 83 | b/c/f status (talk-doc progress report) | talk_docs/progress_report_for_advisor_zh.html | ；P1/P2 五个假标题还在运行。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）代码和测试已完成，批次 1 结束后自动开始； | ；P1/P2 五个假标题也已完成（5 个假标题平均为主结果，与 false_0 版的差别区间都含 0，结论不变）<span class="src">（b1_p12f_report.md）</span>。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）已开始：C / D… | 1 |
| 84 | e/a limitations (talk-doc progress report) | talk_docs/progress_report_for_advisor_zh.html | <li>高引用档几乎没有 control 论文，结论主要来自中低引用论文。</li> | <li>高引用档几乎没有 control 论文，结论主要来自中低引用论文。</li> ⏎ <li><b>层不完整（第 30 版补）。</b>Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划（补充 14 只补 L41–L47、L49 和 L0–L… | 1 |
| 85 | version label (talk-doc progress report) | talk_docs/progress_report_for_advisor_zh.html | <td>实验报告（主报告；当前 v29，2026-11-06）</td> | <td>实验报告（主报告；当前第 30 版，2026-11-08）</td> | 1 |
| 86 | version label (talk-doc progress report) | talk_docs/progress_report_for_advisor_zh.html | <td>汇报 PPT（当前 v20，82 页）</td> | <td>汇报 PPT（当前 v21，82 页）</td> | 1 |
| 87 | a/C07 handbook s19-s8d | methods/parts/C_stage1_9.html | 用 Stage 10 的原始分数在 200 篇论文上重算冻结的多层终点：全部作者、全部 token 的版本中 RQ1 和 RQ2 都成立（public J-lens 6 层平均 RQ1 +0.130 [0.108, 0.153]，RQ2 +0.054 [0.008, 0.102]） | 用 Stage 10 的原始分数在 200 篇论文上重算：全部作者、全部 token 的版本中，public J-lens 6 层平均（int6，少了 L16，与锁定的 7 层积分终点不是同一终点）RQ1 和 RQ2 都为正（RQ1 +0.130 [0.108, 0.153]，RQ2 +0.054 … | 1 |
| 88 | a/C07 handbook s19-s8d premises | methods/parts/C_stage1_9.html | (regex) (<h3 id="s19-s8d">8D 冻结统计分析（RQ1–RQ3、J−V）</h3>\n<div class="fix">.*?)</div> | (computed) | 1 |
| 89 | b R1 handbook E (P1) | methods/parts/E_stage12.html | (regex) (<tr><td>p9 右引号</td>.*?</table>\n<p>p2、p3、p4、p6、p7、p8 在所有层都 ≤ 0.008。.*?</p>) | (computed) | 1 |
| 90 | d X4 handbook F | methods/parts/F_stage13.html | 只作探索（v42_paper_vs_team.md §3）；year 都含 0。 | 只作探索（v42_paper_vs_team.md §3）；这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）；year 都含 0。 | 1 |
| 91 | e L01 qualifier handbook F | methods/parts/F_stage13.html | patchscope 年份到 L40 才出现， | patchscope 年份到 L40 才出现（前一个测量层是 L32，真实起点在 L33–L40 之间）， | 1 |
| 92 | d X4 handbook F (batch-1 sentence) | methods/parts/F_stage13.html | (regex) (认得出的论文方向上更高，但按预注册在测试集上不显著<span class="src">第一作者，调参集选层 L8，测试集 target − control \+0\.023 \[−0\.001, \+0\.048\].*?</span>) | (computed) | 1 |
| 93 | a/C07 slide 19 title | merged_deck/stage1_11_deck.html | <section class="slide lt" aria-label="Stage 8 frozen endpoint, re-scored on CPU"><span class="tag">Stage 8 · CPU proxy</span><h2 style="font-size:52px… | <section class="slide lt" aria-label="Stage 8 re-scored on CPU: three premises"><span class="tag">Stage 8 · CPU proxy</span><h2 style="font-size:52px"… | 1 |
| 94 | a/C07 slide 19 | merged_deck/stage1_11_deck.html | <li><b>Multi-layer endpoint: </b>RQ1 +0.130 [0.108, 0.153], RQ2 +0.054 [0.008, 0.102] → both hold<span class="src">(public J-lens 6-layer mean; c13_C2… | <li><b>6-layer mean (int6, no L16): </b>RQ1 +0.130 [0.108, 0.153], RQ2 +0.054 [0.008, 0.102] → both positive, but not the locked 7-layer endpoint<span… | 1 |
| 95 | a/C07 slide 19 | merged_deck/stage1_11_deck.html | <li><b>L56 alone: </b>RQ2 +0.064 [−0.032, +0.163], not significant<span class="src">(same, L56)</span></li> | <li><b>L56 alone: </b>RQ2 +0.064 [−0.032, +0.163], CI includes 0 → addendum-13 rule triggered the W re-run; not done = deviation D13-1<span class="src… | 1 |
| 96 | a/C07 slide 19 | merged_deck/stage1_11_deck.html | <li><b>What it is not: </b>a CPU proxy with Stage 10’s 5 false titles and the rank metric; the GPU re-run of the original W was not done (user decisio… | <li><b>What it is not: </b>a CPU proxy with Stage 10’s 5 false titles and the rank metric, not W; locked 7-layer endpoint (approx., no L16): RQ2 +0.04… | 1 |
| 97 | a/C07 slide 19 note box | merged_deck/stage1_11_deck.html | <span class="h">Reading</span>The frozen multi-layer conclusion survives an all-author, all-token re-scoring; the single-layer L56 A − B gap does not. | <span class="h">Three premises</span>W scores only the first author’s first token (64.5% are initials); D13-1 (rule triggered at L56 only); U28 (L56 m… | 1 |
| 98 | version label slide 65 | merged_deck/stage1_11_deck.html | Hypotheses H1–H3 × readouts M1–M3 and current results (report v29, 2026-11-07) | Hypotheses H1–H3 × readouts M1–M3 and current results (report v30, 2026-11-08) | 1 |
| 99 | d X4 slide 70 | merged_deck/stage1_11_deck.html | H2 partly supported but not established (rests on M2 and X1); H3: insufficient evidence (text baseline not weaker than Qwen). | H2 partly supported but not established (rests on M2 and X1; X4 recognition gap no longer counted); H3: insufficient evidence (text baseline not weake… | 1 |
| 100 | c slide 77 C row | merged_deck/stage1_11_deck.html | <tr><td>C  R1 × recognised (descriptive)</td><td>32</td><td>+0.464 [0.388, 0.538]</td><td>+0.335</td><td>+0.721 [0.650, 0.806]</td><td>+0.996 [0.968, … | <tr><td>C  R1 × recognised (addendum 11 B)</td><td>462</td><td>+0.559 [0.529, 0.590]</td><td>+0.408</td><td>+0.731 [0.705, 0.757]</td><td>+0.985 [0.97… | 1 |
| 101 | c slide 77 footer | merged_deck/stage1_11_deck.html | <b>U0 timing as A and B (descriptive); R2 upper reference only; </b>C 32 / D 5 / R2-unwritten 28 papers → descriptive<span class="src">(rerun_report.m… | <b>U0 timing as A and B (descriptive); R2 upper reference only; </b>C completed to 462 papers: within bin same timing as A, larger gap (C − A +0.075 [… | 1 |
| 102 | b slide 79 colon B/A | merged_deck/stage1_11_deck.html | (B/A 0.78–0.99) | (B/A 0.72–0.87 with five false titles; false_0 0.78–0.99) | 1 |
| 103 | f slide 81 date | merged_deck/stage1_11_deck.html | status 2026-11-06 evening | status 2026-11-08 | 1 |
| 104 | b slide 81 P1/P2 | merged_deck/stage1_11_deck.html | <li><b>Batch 1, running: </b>P1 / P2 with five false titles — result after approval</li> | <li><b>Batch 1, done: </b>P1 / P2 with five false titles (five-title mean primary, false_0 beside): every mean5 − false_0 CI includes 0 → conclusions … | 1 |
| 105 | f slide 81 batch 2 | merged_deck/stage1_11_deck.html | <li><b>Batch 2 (addenda 11, 12): </b>code, tiny tests and hard-check unit tests done; starts automatically after batch 1; | <li><b>Batch 2 (addenda 11, 12): </b>running; C / D completion done (C 462 papers: same timing as A); 2-11 stopped by its hard check → 2-11b (addendum… | 1 |
| 106 | f slide 81 batch 3 | merged_deck/stage1_11_deck.html | 3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: code ready, after batch 2 | 3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: queued, start after batch 2 | 1 |
| 107 | e slide 82 subtitle | merged_deck/stage1_11_deck.html | <p class="sub" style="font-size:19px;margin-bottom:12px">Written 2026-11-06</p> | <p class="sub" style="font-size:19px;margin-bottom:12px">Written 2026-11-06; last two items added 2026-11-08 (v30)</p> | 1 |
| 108 | e slide 82 items | merged_deck/stage1_11_deck.html | <span class="src">(84 target, 0 control; m3_scores.md §2)</span>, so within-bin comparisons cannot use it</li></ul> | <span class="src">(84 target, 0 control; m3_scores.md §2)</span>, so within-bin comparisons cannot use it</li><li><b>Layers and samples: </b>Stage 10 … | 1 |
| 109 | a/C07 note 19 | notes_zh.json #19 | Stage 8 的 CPU 代理（补充 13 C-2，事后）：用 Stage 10 已有的原始分数，在 Stage 8 的 200 篇论文上重算冻结的多层终点。全部作者、全部名字 token 的版本中 RQ1 和 RQ2 都成立：public J-lens 6 层平均 RQ1 | Stage 8 的 CPU 代理（补充 13 C-2，事后）：用 Stage 10 已有的原始分数，在 Stage 8 的 200 篇论文上重算。全部作者、全部名字 token 的版本中，public J-lens 6 层平均（int6，少了 L16，与锁定的 7 层积分终点不是同一终点）RQ1 和… | 1 |
| 110 | a/C07 note 19 premises | notes_zh.json #19 | 按原 W 的 GPU 重算没有做（用户 2026-11-06 决定）。 | 按原 W 的 GPU 重算没有做（用户 2026-11-06 决定）。Stage 8 的结论（真标题让模型更偏好真实第一作者 RQ1；A 组强于 B 组 RQ2）较稳，但有三个前提：① W 只给第一作者名字的第一个 token 打分，在 Stage 8 的 200 篇里有 129 篇（64.5%）这… | 1 |
| 111 | d X4 note 65 | notes_zh.json #65 | 所以 H2 部分支持但未确立，H3 证据不足。 | 所以 H2 部分支持但未确立，H3 证据不足；X4 中认得出的论文第一作者 D 更高（测试集不显著）这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）。 | 1 |
| 112 | c note 77 denominator | notes_zh.json #77 | A 0.407、B 0.214、U0 0.293、C 0.464〔E1，未写出作者，最终输出；A 557、B 586、U0 599、C 32 篇；391_groups/reports/e1_num_den.md〕 | A 0.407、B 0.214、U0 0.293、C 0.559〔E1，未写出作者，最终输出；A 557、B 586、U0 599 篇；391_groups/reports/e1_num_den.md；C 为补充 11 B 补全后的 462 篇，[0.529, 0.590]，391_groups/r… | 1 |
| 113 | c note 77 C/D | notes_zh.json #77 | ；C 32 篇、D 5 篇、R2 未写出作者 28 篇〔rerun_report.md Counts 表〕只作描述。 | ；D 33 篇、R2 未写出作者 28 篇〔rerun_report.md Counts 表；b2_cd_report.md〕只作描述。C / D 组补全 E1 / E2（批次 2 第 2-6 项，补充 11 B，已完成）：C 组未写出作者 462 篇，同一引用档内与 A 相比（6 个引用档，C 2… | 1 |
| 114 | b note 79 colon B/A | notes_zh.json #79 | ':' token 在 L44–L48 两组分子相近（B/A 0.78–0.99〔只替换 “:”，分子 B/A：L44 0.78、L48 0.99；同一文件〕） | ':' token 在 L44–L48 两组分子相近（B/A：5 个假标题版 0.72–0.87，false_0 版 0.78–0.99〔只替换 “:”，分子 B/A：5 个假标题版 L44 0.72、L48 0.87，391_groups/reports/b1_p12f_report.md；fal… | 1 |
| 115 | b/c note 81 | notes_zh.json #81 | 批次 1 还在运行：P1/P2 用 5 个假标题，结果经用户确认后补入。 | P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集到名字位置，注意力在 … | 1 |
| 116 | e note 82 title | notes_zh.json #82 | 不能补做的局限（2026-11-06 写定）： | 不能补做的局限（2026-11-06 写定；2026-11-08 第 30 版补充后两项）： | 1 |
| 117 | e note 82 limitations | notes_zh.json #82 | (append) | 2026-11-08（报告第 30 版）补充的局限：… | 1 |
| 118 | c note C/D (R1 figure note) | notes_zh.json #28 | (append) | C / D 组补全… | 1 |
| 119 | README links v30 | github/README_draft_20261106b.md | (v29 prepared 2026-11-06, batch-1 results added) | (v30, 2026-11-08: batch 1 complete, groups C / D completed, Stage 8 premises and new limitations) | 1 |
| 120 | README links v21 | github/README_draft_20261106b.md | (v20 prepared 2026-11-06, 82 slides) | (v21, 2026-11-08, 82 slides) | 1 |
| 121 | README links handbook | github/README_draft_20261106b.md | [Stage 1–13 methods handbook](https://claude.ai/artifact/W7r7xVte3eaNcbo8D8cybo) (2026-11-06) | [Stage 1–13 methods handbook](https://claude.ai/artifact/W7r7xVte3eaNcbo8D8cybo) (2026-11-08 c) | 1 |
| 122 | README latest conclusions | github/README_draft_20261106b.md | see the plan document `docs/plan_master_queue_20261106.md` (to be copied in at the next sync). | see the plan document `docs/plan_master_queue_20261106.md` (to be copied in at the next sync). ⏎  ⏎ **Latest (2026-11-08, report v30).** P1 / P2 with five… | 1 |
| 123 | README C07 | github/README_draft_20261106b.md | Stage 8 CPU proxy: RQ1 +0.130, RQ2 +0.054 multi-layer, L56 RQ2 n.s. <sub>(c13_C2.md; not the W statistic)</sub> | Stage 8 CPU proxy: RQ1 +0.130, RQ2 +0.054 on the 6-layer mean (int6, not the locked 7-layer endpoint), L56 RQ2 n.s. → addendum-13 rule triggered, W re… | 1 |
| 124 | README redo list | github/README_draft_20261106b.md | - Batch 1, running: P1 / P2 with five false titles. | - Batch 1, done: P1 / P2 with five false titles — Addendum 10 line 27 makes the five-title mean primary; the published false_0 numbers stand beside it… | 1 |
| 125 | README batch 2 | github/README_draft_20261106b.md | - Batch 2 (addenda 11–12): code, tiny tests and hard-check unit tests done; starts automatically after batch 1; | - Batch 2 (addenda 11–12): running since batch 1 ended; C / D completion done; 2-11 stopped by its hard check (0.880 < 0.90) → 2-11b (addendum 15), sh… | 1 |
| 126 | README batch 3 | github/README_draft_20261106b.md | Stage 10 L41–L47, L49 and L0–L23 code ready, after batch 2; | Stage 10 L41–L47, L49 and L0–L23 queued, start after batch 2; | 1 |
| 127 | README limits | github/README_draft_20261106b.md | - Cannot be redone: one model; teacher forcing; label pipeline not on the cluster; the 4097+ citation bin has no B / D papers. | - Cannot be redone: one model; teacher forcing; label pipeline not on the cluster; the 4097+ citation bin has no B / D papers. Added 2026-11-08 (v30):… | 1 |
| 128 | README status C07 | github/README_draft_20261106b.md | ; Stage 8 CPU proxy RQ1 +0.130, RQ2 +0.054 \| done \| | ; Stage 8 CPU proxy RQ1 +0.130, RQ2 +0.054 (int6, not the locked endpoint; D13-1) \| done \| | 1 |
| 129 | README status rows | github/README_draft_20261106b.md | \| Batch 1 item 3 \| P1 / P2 with five false titles \| — \| running \| 391_groups/reports/b1_p12f_report.md (when done) \| | \| Batch 1 item 3 \| P1 / P2 with five false titles \| five-title mean primary; every mean5 − false_0 CI includes 0, conclusions unchanged \| done (hard c… | 1 |
| 130 | README status batch 2 | github/README_draft_20261106b.md | \| — \| code ready, queued (starts automatically after batch 1) \| | \| — \| running (C / D done; 2-11 stopped → 2-11b shard 0 queued; other items in progress) \| | 1 |
| 131 | README status batch 3 | github/README_draft_20261106b.md | \| 3-1, 3-2 code ready (after batch 2); | \| 3-1, 3-2 queued (after batch 2); | 1 |
| 132 | K regenerated from the report (v30) | methods/parts/K_post_defence.html | 与《Stage 1–13 实验报告》第 29 版第五部分内容相同（图号、表号沿用报告）。</p> | 第 30 版 … | 1 |
| 133 | handbook header 2026-11-08 c | methods/build_methods.py | 2026-11-03 定稿，2026-11-06 补充（第十一部分：答辩后新增与重做计划；X2、补充 9 全部名字 to… | … + 2026-11-08 c 版 | 1 |
| 134 | f slide 75 agenda status | merged_deck/stage1_11_deck.html | done, batch 1 (only P1 / P2 with five false titles still running), batches 2 and 3; limits that cannot be redone | done, batch 1 (complete), batches 2 and 3 (in progress); limits that cannot be redone | 1 |
| 135 | f Fit B status note | advisor/index.html | Fit B 与 holdout 列入批次 2，代码已就绪，自动开始； | Fit B 与 holdout 列入批次 2，代码已就绪，自动开始；2026-11-08：已在运行，尚无结果； | 1 |
| 136 | f Fit B status note | process_report/draft_zh.md | Fit B 与 holdout 列入批次 2，代码已就绪，自动开始； | Fit B 与 holdout 列入批次 2，代码已就绪，自动开始；2026-11-08：已在运行，尚无结果； | 1 |
| 137 | f Fit B status note (next steps) | advisor/index.html | Fit B 与 holdout 已列入批次 2（补充 12 第 2-1 项），代码已就绪，批次 1 结束后自动开始； | Fit B 与 holdout 已列入批次 2（补充 12 第 2-1 项），2026-11-08 已在运行，尚无结果； | 1 |
| 138 | f Fit B status note (addendum) | pages_20261106b/methods_addendum/index.html | Fit B 续跑与 holdout 列入批次 2（补充 12 第 2-1 项），代码已就绪； | Fit B 续跑与 holdout 列入批次 2（补充 12 第 2-1 项），2026-11-08 已在运行，尚无结果； | 1 |
| 139 | f batch-3 status note (addendum) | pages_20261106b/methods_addendum/index.html | 批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码已就绪，第二批之后开始； | 批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），编排作业已提交，第二批全部结束后自动开始； | 1 |
| 140 | notes 81 shortened (overflow) | notes_zh.json #81 | P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列。两版所有“5 个假标题平均 − false_0”的区间都含 0，已发表结论不变：论文信息在 L44–L52 汇集到名字位置，注意力在  | P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成）：5 个假标题平均为主结果，false_0 并列；两版之差的区间都含 0，结论不变（P1 全部位置 L48 +0.821，false_0 0.825；P2 注意力 L48 +0.237，MLP L56 +0.226）；p9 各假标题 6… | 1 |
| 141 | notes 82 shortened (overflow) | notes_zh.json #82 |  2026-11-08（报告第 30 版）补充的局限：层不完整：Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划（补充 14 只补 L41–L47、L49 和 L0–L23，都在排队）。主要结论的起始层都不在缺口里；落在缺口里的只有三条描述 |  2026-11-08（第 30 版）补充的局限：Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划；容差 0.25 → 0.5 已用于 Stage 10 主轮（最大差 0.367）；干预只用 1,186 / 9,108 篇；分母效应（C 0… | 1 |
| 142 | notes 81 shortened again (overflow) | notes_zh.json #81 | P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成）：5 个假标题平均为主结果，false_0 并列；两版之差的区间都含 0，结论不变（P1 全部位置 L48 +0.821，false_0 0.825；P2 注意力 L48 +0.237，MLP L56 +0.226）；p9 各假标题 6 | P1 / P2 用 5 个假标题（已完成）：5 个假标题平均为主结果，与 false_0 之差的区间都含 0，结论不变；p9 各假标题 694–711 篇，集合不同，未加权；“:” 分子 B/A 0.72–0.87（false_0 0.78–0.99）。C / D 组补全（已完成）：C 462 篇，… | 1 |
| 143 | notes 81 X4 sentence shortened (overflow) | notes_zh.json #81 | ，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018） | ，不再作为 H2 的证据 | 1 |
| 144 | notes 28 shortened (overflow) | notes_zh.json #28 |  2026-11-08 补（补充 11 B，C / D 组补全）：C 组未写出作者 462 篇，同一引用档内与 A 相比（6 个引用档，C 258 篇、A 323 篇）：E1 恢复比例 L48 −0.037 [−0.080, +0.009]，L52 +0.007 [−0.009, +0.024]；L |  2026-11-08 补（补充 11 B）：C 补全到 462 篇后，同一引用档内与 A 时间点相同（E1 L48 −0.037 [−0.080, +0.009]），真假标题差距更大（C − A +0.075 [+0.024, +0.130]）；D 33 篇只作描述〔391_groups/repo… | 1 |

## Exports (sbatch, short)
- 11740139 export_0108c (COMPLETED): hypotheses PNGs `downloads/Stage13_hypotheses_table_v30_tableonly.png`, `…_v30_en_{tableonly,slide,wide}.png` (generators `stage1_11/src/hyp_table_png_v30.py`, `hyp_table_png_v30_en.py`); deck slide-65 image (`sync_20261107/deck_slide65_img_20261108c.py`); `Stage1-13_report_v30_A4.pdf`; `Stage1-13_methods_handbook_A4.v20261108c.pdf`; `talkdoc_*_20261108c_A4.pdf` ×6; `jlens_progress_report_2026-11-08c_A4.pdf`, `jlens_process_report_2026-11-08c_A4.pdf`, `scoring_audit_2026-11-08c_A4.pdf`, `methods_addendum_2026-11-08c_A4.pdf`; screenshots `sync_20261107/shots_g/`.
- pptx v21: `talk/src/export/pptx_text_fix_20261108c.py` v20h → `downloads/Stage1-13_deck_v21_editable.pptx` (+ .b64.txt). 25/25 rules hit, 2 bullets added on slide 82, slide-65 table image replaced (first in-job run also replaced the shared background image → fixed: only the "chart image" picture; final file re-made by hand after the fix, verified only slide 65 picture differs from v20h), 8 notes replaced.
- Deck PDFs v21: `talk/src/export/export_v21_full.sbatch` jobs 11740140 → 11740225 → 11740255 (final; re-run after notes 81/82/28 were shortened by apply_20261108c_part3.py / _part4.py because the with-notes pages overflowed). Remaining overflow: slide 72 (1071 px, pre-existing) and slide 81 (1003 px; was 901 in v20h).

## round d (after checks)

Script `sync_20261107/apply_20261108d.py` (checker out_20261108_192440/wording_v30/; backups `*.before_20261108d`). Handbook and process page rebuilt; K regenerated from the report.

| # | rule | file | before | after | count |
|---|---|---|---|---|---|
| d1 | 1 L02 attribution | stage1_11/stage1_11_report.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d2 | 1 L02 attribution | advisor/index.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 2 |
| d3 | 1 L02 attribution | process_report/draft_zh.md | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d4 | 1 L02 attribution | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d5 | 1 L02 attribution | pages_20261106b/methods_addendum/index.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d6 | 1 L02 attribution | talk_docs/experiment_walkthrough_zh.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d7 | 1 L02 attribution | talk_docs/experiment_walkthrough_methods_zh.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d8 | 1 L02 attribution | talk_docs/methods_handbook_guide_plain_zh.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d9 | 1 L02 attribution | talk_docs/progress_report_for_advisor_zh.html | 最多变 0.070。保留在事后改动清单里 | 最多变 0.070。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendment… | 1 |
| d10 | 1 L02 attribution (keys zh) | talk_docs/keys_and_shelves_script_zh_en.html | 只有按 0.5 才通过。</p> | 只有按 0.5 才通过。原定 0.25 时，Stage 10 主轮一致性检查（12 个上下文、52 个 token 位置）的 25 个 lens × 层组合中有 10 个超出 0.25，最大差 0.367（351_stage10/reports/parity_before_tol05_amendme… | 1 |
| d11 | 1 L02 attribution (keys en) | talk_docs/keys_and_shelves_script_zh_en.html | passes only at 0.5.</p> | passes only at 0.5. With the original 0.25, 10 of the 25 lens × layer pairs of the Stage 10 main-round parity check (12 contexts, 52 token positions) … | 1 |
| d12 | 1 L02 attribution (README) | github/README_draft_20261106b.md | post-hoc change, kept listed); | post-hoc change, kept listed; With the original 0.25, 10 of the 25 lens × layer pairs of the Stage 10 main-round parity check (12 contexts, 52 token p… | 2 |
| d13 | 1 L02 attribution (slide 82) | merged_deck/stage1_11_deck.html | parity tolerance 0.25 → 0.5 was used (Stage 10 main round, max 0.367); | parity tolerance 0.25 → 0.5 was used, a post-hoc change (main round: 10 of 25 pairs above 0.25, max 0.367; size matches bf16 rounding, up to ~0.46); | 1 |
| d14 | 1 L02 attribution (note 82) | notes_zh.json #82 | 容差 0.25 → 0.5 已用于 Stage 10 主轮（最大差 0.367） | 容差 0.25 → 0.5 已用于 Stage 10 主轮（原定 0.25 时 25 个组合有 10 个超出，最大差 0.367；3-3 按 0.25 有 99.81% 在容差内；量级与 bf16 舍入随前向长度变化（最大约 0.46）一致，但放宽属事后修改） | 1 |
| d15 | 2 advisor deck label | advisor/index.html | 〔2026-11-06 已更新：当前为 v20（本地已备，待发布）；见页首更新框〕 | 〔2026-11-08 已更新：当前为 v21；见页首更新框〕 | 1 |
| d16 | 3 v30 numbers registered | stage1_11/stage1_11_report.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d17 | 3 v30 numbers registered | advisor/index.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 2 |
| d18 | 3 v30 numbers registered | process_report/draft_zh.md | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d19 | 3 v30 numbers registered | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d20 | 3 v30 numbers registered | pages_20261106b/methods_addendum/index.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d21 | 3 v30 numbers registered | talk_docs/experiment_walkthrough_zh.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d22 | 3 v30 numbers registered | talk_docs/experiment_walkthrough_methods_zh.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d23 | 3 v30 numbers registered | talk_docs/methods_handbook_guide_plain_zh.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d24 | 3 v30 numbers registered | talk_docs/progress_report_for_advisor_zh.html | ；另有约 1,024 个像结论的数字还没登记（2026-11-07 的计数）；第 30 版新放回或新增的数字（D13-1、P1 / P2 五个假标题、C / D 组补全）尚待登记 | ；第 30 版新放回或新增的数字已登记进严格核对（claims_defs_v9，结果见核对表）；另约 1,024 个结论性数字未登记（2026-11-07 计数） | 1 |
| d25 | 3 v30 numbers registered (note 82) | notes_zh.json #82 | 数字核对已登记 680 个、4,307 处全部一致，约 1,024 个未登记 | 第 30 版的数字已登记进严格核对（claims_defs_v9），另约 1,024 个结论性数字未登记 | 1 |
| d26 | 3 v30 numbers registered (README) | github/README_draft_20261106b.md | about 1,024 conclusion-like numbers not registered (count from 2026-11-07). | the v30 numbers are registered in the strict checker (claims_defs_v9); about 1,024 conclusion-like numbers are not registered (count from 2026-11-07). | 2 |
| d27 | 4 D13-1 version labels | stage1_11/stage1_11_report.html | 报告 v29 和 PPT v20 都以锁定计划的 | 报告 v30 和 PPT v21 都以锁定计划的 | 1 |
| d28 | 5 slide 77 258/462 | merged_deck/stage1_11_deck.html | within bin same timing as A, larger gap | within bin (258 of 462 C papers, 6 bins) same timing as A, larger gap | 1 |
| d29 | 5 slide 81 p9 | merged_deck/stage1_11_deck.html | colon numerator B/A 0.72–0.87<span class="src">(b1_p12f_report.md)</span> | colon numerator B/A 0.72–0.87; p9: 694–711 papers per false title, different sets, unweighted<span class="src">(b1_p12f_report.md)</span> | 1 |
| d30 | 5 slide 81 258/462 | merged_deck/stage1_11_deck.html | C / D completion done (C 462 papers: same timing as A) | C / D completion done (C 462 papers; within bin 258 of 462 vs A: same timing) | 1 |
| d31 | 5 slide 82 subtitle | merged_deck/stage1_11_deck.html | Written 2026-11-06; last two items added 2026-11-08 (v30) | Written 2026-11-06; last three items added 2026-11-08 (v30) | 1 |
| d32 | 5 slide 82 L01 consequences + 2-11 | merged_deck/stage1_11_deck.html | pipeline use false_0 only, no plan</li></ul> | pipeline use false_0 only, no plan</li><li><b>Layer gap, stopped item: </b>X4 year onset somewhere in L33–L40; Jacobian vs logit jump between L32 and … | 1 |
| d33 | 6 note 82 no plan + L33-L40 | notes_zh.json #82 | M5 B 部分和 E4b 的 X1 对照流程只用 false_0； | M5 B 部分和 E4b 的 X1 对照流程只用 false_0，没有补做计划；落在层缺口里的只有描述：X4 年份起点在 L33–L40 之间，Jacobian 对 logit 的跳变在 L32–L40 之间，X4 第一作者峰值可能在 L33–L47； | 1 |
| d34 | 6 note 81 shortened (overflow) | notes_zh.json #81 | （2-1、2-2 用较省但包含原始提示逐位复现重拟合的硬检查；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述） |  | 1 |
| d35 | 6 note 81 shortened (duplicate C/D clause) | notes_zh.json #81 | 批次 1 结束后已由编排作业开始运行：C / D 组补全 E1 / E2（2-6）已完成； | 批次 1 结束后已由编排作业开始运行； | 1 |
| d36 | 6 note 81 shortened (E4b detail, in note 72) | notes_zh.json #81 | ，逐个排除版（4,654 篇）第一个 token +0.066；原 E4b（1,395 篇）+0.061；置换对照首字母仍 +0.018，其余 ≈ 0 |  | 1 |
| d37 | 6 note 81 shortened (sources) | notes_zh.json #81 | 〔381_stage13/config/prereg_addendum14_deviations.json；381_stage13/summary_b3_71b/gate.json；381_stage13/b3_33_v2/v2_C1_summary.json〕；3-4 | 〔381_stage13/config/prereg_addendum14_deviations.json〕；3-4 | 1 |
| d38 | 6 note 72 shortened (probe definition is in report / handboo… | notes_zh.json #72 | probe 的定义：输入是第 l 层标题最后一个 token 的残差；目标是模型自己在 L63、在预测该角色名字 token 的位置上的状态，按论文平均；ridge，按作者团队分折；在 9,137 个名字 token 的词表里解码；标题特异 = 真标题 − false_0。 |  | 1 |
| d39 | 6 note 72 shortened (source) | notes_zh.json #72 | 〔381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv（version = V0 / Vpd / V5x0，列 tc / tc_lo / tc_hi；引用档内 target − control，团队整群 bootstrap 2,000 次 95%… | 〔381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv；b1_e4b5_report.md〕 | 1 |
| d40 | 6 note 72 shortened (source 2) | notes_zh.json #72 | 〔381_stage13/reports/b1_e4b5_report.md 第 2 节与 “Per-donor exclusion” 节，目标 + 对照，团队聚类 95% CI〕 | 〔381_stage13/reports/b1_e4b5_report.md〕 | 1 |
| d41 | 7 talk-doc progress report C04/C08/2-11 | talk_docs/progress_report_for_advisor_zh.html | ；P1/P2 五个假标题也已完成（5 个假标题平均为主结果，与 false_0 版的差别区间都含 0，结论不变）<span class="src">（b1_p12f_report.md）</span>。批次 2（补充 11、12，含 Stage 9 Fit B 与 holdout）已开始：C / D… | ；P1/P2 五个假标题也已完成：按补充 10 第 27 行，5 个假标题平均为主结果，原 false_0 版并列，两版之差的区间都含 0，结论不变；“:” 位置分子 B/A 5 个假标题版 0.72–0.87，false_0 版 0.78–0.99（B 的比例高只因分母约为 A 的一半）；p9 各… | 1 |
| d42 | 8 README X4 sentence | github/README_draft_20261106b.md | In X4, the X4 recognised − control difference is no longer counted as H2 evidence (text-only BERT baseline +0.088 not weaker than Qwen L8 +0.018). | In X4, the recognised − control difference (test set L8 +0.023 [−0.001, +0.048], not significant) is no longer counted as H2 evidence (text-only BERT … | 1 |
| d43 | 9 2,103 | stage1_11/stage1_11_report.html | n = 462 (2103 authors) | n = 462 (2,103 authors) | 5 |
| d44 | K regenerated from the report | methods/parts/K_post_defence.html | (part 5 of the report) | (regenerated) | 1 |
| d2-1 | d2 note 72 shortened (overflow) | notes_zh.json #72 | 原 E4b 只给每位作者的第一个 token 打分，而这个 token 多半是首字母，所以它低估了标题位置携带的名字信息。 | (deleted) | 1 |
| d2-2 | d2 note 72 shortened (overflow) | notes_zh.json #72 | （与补充 9 已发表值相同，e4b_alltok.md） | (deleted) | 1 |
| d2-3 | d2 note 72 shortened (overflow) | notes_zh.json #72 | 〔6,841 篇；381_stage13/reports/c13_C3b.md〕 | 〔6,841 篇；c13_C3b.md〕 | 1 |
| d2-4 | d2 note 81 shortened (overflow) | notes_zh.json #81 | 〔381_stage13/reports/b1_x7f_report.md、e4b_alltok.md、c13_C1.md–c13_C5.md〕 | 〔b1_x7f_report.md、e4b_alltok.md、c13_C1–C5.md〕 | 1 |
| d2-5 | d2 note 81 shortened (overflow) | notes_zh.json #81 | （偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071） | （偏离 D1，4,654 篇，每篇约 1.5 个可用假标题） | 1 |

Round d exports: 11740702 export_0108d (report v30 PDF, handbook 20261108c PDF, page / talk-doc PDFs 20261108c, overwritten; COMPLETED); pptx v21 by `talk/src/export/pptx_text_fix_20261108d.py` from `Stage1-13_deck_v21_editable.pptx.before_20261108d` (5/5 rules, 1 bullet added on slide 82, notes 72/81/82 replaced); deck v21 PDFs 11740706 → 11740745 (final, after `apply_20261108d_part2.py` shortened notes 72/81). Notes overflow after the fix: slides 30, 72, 81 at 901 px against 898 (3 px; slide 30 was already 901 in v20h); before the fix slide 72 was 1071 and slide 81 was 1003.

## round e

Script `sync_20261107/apply_20261108e.py` (backups `*.before_20261108e`). Leak share recomputed by `381_stage13/e4b_standardisation_check/v5x0_leak_share.py` (json/md beside it): surname 4,402 / 5,580 = 78.89% (target 78.35%, control 79.86%; matches stored dropped_k); given name 2,894 / 6,824 = 42.4%; initial 4,567 / 6,360 = 71.8%. "约 79%" kept and qualified as the surname set.

| # | file | before | after | count |
|---|---|---|---|---|
| e1 | stage1_11/stage1_11_report.html | 也就是说，R1 论文的标题信息被读取得略晚一点，但完成时间相同。 | 补全前（C 组 36 篇）曾观察到 C 略晚；补全到 462 篇后（档内可比 258 篇），C 与 A 的时间点相同、信号更大（分母 C − A +0.075 [+0.024, +0.130]），原观察未被重现<span class="src">（391_groups/reports/b2_cd_r… | 1 |
| e2 | stage1_11/stage1_11_report.html | “略晚”在补全后的同一引用档比较中没有得到确认（见第五部分 C / D 组补全）。 | (deleted) | 1 |
| e3 | stage1_11/stage1_11_report.html | <td>同样 L52 完成；36 篇中 L40–48 略慢，补全到 462 篇后同一引用档内时间点与 A 相同（补充 11 B）</td> | <td>同样 L52 完成；补全前（C 组 36 篇）曾观察到 C 略晚；补全到 462 篇后（档内可比 258 篇），C 与 A 的时间点相同、信号更大（分母 C − A +0.075 [+0.024, +0.130]），原观察未被重现<span class="src">（391_groups/r… | 1 |
| e4 | stage1_11/stage1_11_report.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 3 |
| e5 | advisor/index.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e6 | process_report/draft_zh.md | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e7 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e8 | pages_20261106b/methods_addendum/index.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e9 | talk_docs/stage13_script_zh_en.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e10 | talk_docs/progress_report_for_advisor_zh.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e11 | methods/parts/F_stage13.html | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e12 | notes_zh.json #72 | false_1..4 中约 79% 本应剔除 | false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | 1 |
| e13 | github/README_draft_20261106b.md | about 79% of false_1..4 should have been excluded | about 79% of false_1..4 should have been excluded (surname set, 1,395 papers: 4,402 / 5,580; given name 42%, initial 72%; v5x0_leak_share.json) | 1 |
| e14 | talk_docs/stage13_script_zh_en.html | about 79% of false_1..4 should have been excluded | about 79% of false_1..4 should have been excluded (surname set, 1,395 papers: 4,402 / 5,580; given name 42%, initial 72%; v5x0_leak_share.json) | 1 |
| e15 | methods/parts/K_post_defence.html | (part 5) | (regenerated from the report) | 1 |
| e2-1 | notes_zh.json #72 (overflow) | （姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json） | （姓 4,402 / 5,580；名 42%、首字母 72%；v5x0_leak_share.json） | 1 |
| e2-2 | notes_zh.json #72 (overflow) | 〔补充 9，标题最后一个 token，真标题 − false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md 第 5 节〕 | 〔1,395 篇，剔除标题复用；e4b_alltok.md 第 5 节〕 | 1 |
Round e exports: report/handbook/pages 11741368; deck v21 11741367 -> 11741399 (final).

## round f

Script `sync_20261107/apply_20261109f.py` (backups `*.before_20261109f`; numbers asserted against 381_stage13/summary_m2_f5/M2_f5_mean.csv and exclusion_audit.csv). H2 verdict and tiers unchanged; deck / notes / pptx contain no M2 false-title numbers or M2 in the false_0-only list → unchanged.

| # | file | before | after | count |
|---|---|---|---|---|
| f1 | stage1_11/stage1_11_report.html | 但仍然读得出，与真标题运行相当：表示仍然跟着提示里的标题走。</li> | 但仍然读得出，与真标题运行相当：表示仍然跟着提示里的标题走。<b>2026-11-09 补（M2 用 5 个假标题，团队分折）：</b>5 个假标题平均 L48 读借出论文的年份 R² 0.527（false_0 版 0.535），引用数 0.507（false_0 版 0.488），去掉年份后的引… | 1 |
| f2 | stage1_11/stage1_11_report.html | 假标题 false_0 的运行用标题所属论文的标签，检验 probe 读的是标题对应的论文。 | 假标题 false_0 的运行用标题所属论文的标签，检验 probe 读的是标题对应的论文（2026-11-09 补做 false_1..4，见第四部分切分审计）。 | 1 |
| f3 | stage1_11/stage1_11_report.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span class="src">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f4 | advisor/index.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span style="color:#8a8f98;font-size:.8em">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 2 |
| f5 | process_report/draft_zh.md | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定【conclusions_v30_checks.md A3】 | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f6 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span style="color:#8a8f98;font-size:.8em">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f7 | pages_20261106b/methods_addendum/index.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span style="color:#8a8f98;font-size:.8em">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f8 | talk_docs/experiment_walkthrough_zh.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span class="src">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f9 | talk_docs/experiment_walkthrough_methods_zh.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span class="src">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f10 | talk_docs/methods_handbook_guide_plain_zh.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span class="src">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f11 | talk_docs/progress_report_for_advisor_zh.html | M2 的假标题运行也只用 false_0，改用 5 个假标题只需 CPU（残差已在盘上，约 3 小时），是否做待定<span class="src">（conclusions_v30_checks.md A3）</span> | M2 已不在此列：M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示… | 1 |
| f12 | github/README_draft_20261106b.md | (M2 with five titles needs CPU only, decision pending) | (M2 has since been redone with five false titles: five-title mean primary, false_0 beside; the title-reuse / donor-in-training-fold exclusion is 0 row… | 2 |
| f13 | methods/parts/F_stage13.html | R13/reports/split_compare.md 第 119-152 行</span></p> | R13/reports/split_compare.md 第 119-152 行</span></p> <div class="fix"><b>2026-11-09 补：</b>5 个假标题（2026-11-09，团队分折）：5 个假标题平均 L48 读借出论文的年份 R² 0.527（false_… | 1 |
| f14 | methods/parts/B_global2.html | paper-split 的 false_0 数字被 addendum 1 判为无效。 | paper-split 的 false_0 数字被 addendum 1 判为无效。2026-11-09：5 个假标题平均 L48 year 0.527（false_0 版 0.535）、log citations 0.507（false_0 版 0.488）、citations\|year 0.49… | 1 |
| f15 | methods/parts/G_appendix.html | 区间平均宽 1.15 倍（true 1.02、false_0 1.32），0 个翻转。 | 区间平均宽 1.15 倍（true 1.02、false_0 1.32），0 个翻转。2026-11-09 补做 5 个假标题：5 个假标题平均 L48 donor 年份 R² 0.527（false_0 版 0.535）、log 引用 0.507（false_0 版 0.488）；false_1.… | 1 |
| f16 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md |   - false_0 运行读借出论文的年份：L48 R² 改为团队分折后从 0.623 降到 0.535，仍读得出。 |   - 假标题运行读借出论文的年份（团队分折）：5 个假标题平均 L48 R² 0.527（false_0 版 0.535；按论文分折的 0.623 作废），仍读得出；其余见 `R13/reports/m2_f5_report.md`（引用数 0.507（false_0 版 0.488），去掉年份后… | 1 |
| f17 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 只用 false_0（假标题运行；用 5 个假标题重做只需 CPU，约 3 小时，见 CHK A3） | M2 的假标题运行已补 5 个假标题；标题复用和供体在训练折的排除对每个假标题都为 0 行（exclusion_audit.csv）；另有约 7,240–7,370 行/假标题的供体论文以 target 行出现在训练折中（显示另一篇论文的标题和标签，只有年份在 ':' 之后进入提示），未作为泄漏处理… | 1 |
| f18 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md |   - M2 的假标题运行也只用 false_0。按 CHK A3，5 个假标题的残差已在 `R13/raw/b1_titlepos5/false_1..4`，只需 CPU（M2 约 3 小时 × 16 核，M5 B 部分 < 1 小时），但尚未排入计划。 |   - M2 已不在此列：2026-11-09 已补 5 个假标题（见 C13 前提）。M5 B 部分补做只需 CPU（< 1 小时，CHK A3），尚未排入计划。 | 1 |
| f19 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | M2 的 5 个假标题重做只需 CPU。 | M2 已补 5 个假标题（2026-11-09，5 个假标题平均为主值、false_0 并列；排除审计 0 行）。 | 1 |
| f20 | methods/parts/K_post_defence.html | (part 5) | (regenerated from the report) | 1 |
Round f export: 11747113 (report v30, handbook 20261108c, page / talk-doc PDFs; deck/pptx unchanged).
| g1 | H2 status (wording check) | talk_docs/stage13_script_zh_en.html | H2 部分支持： | H2 部分支持但未确立： | 1 |

## round g

Script `sync_20261107/apply_20261109g.py` (backups `*.before_20261109g`, stage13_script_zh_en `.before_20261109g2`; numbers asserted against 381_stage13/reports/b2_e1noise.md, b2_e1t5.md, b2_e1t5_numden.md, b2_x3role.md, b2_m3tok.md). No tier change; H2 status unchanged.

| # | file | before | after | count |
|---|---|---|---|---|
| g1 | stage1_11/stage1_11_report.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 2 |
| g2 | advisor/index.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g3 | process_report/draft_zh.md | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g4 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g5 | pages_20261106b/methods_addendum/index.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g6 | talk_docs/experiment_walkthrough_zh.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g7 | talk_docs/experiment_walkthrough_methods_zh.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g8 | talk_docs/stage13_script_zh_en.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g9 | talk_docs/methods_handbook_guide_plain_zh.html | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g10 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 2 |
| g11 | notes_zh.json #77 | 个别层差异极小，不作解释 | 个别层差异极小，不作解释（小于批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md… | 1 |
| g12 | stage1_11/stage1_11_report.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g13 | advisor/index.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g14 | process_report/draft_zh.md | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g15 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g16 | pages_20261106b/methods_addendum/index.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g17 | talk_docs/experiment_walkthrough_zh.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g18 | talk_docs/experiment_walkthrough_methods_zh.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g19 | talk_docs/stage13_script_zh_en.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g20 | talk_docs/methods_handbook_guide_plain_zh.html | 两版所有“5 个假标题平均 − false_0”的区间都含 0 | 两版所有“5 个假标题平均 − false_0”的区间都含 0（差 0.004–0.006，在批量舍入噪声的量级内：组级最大 0.0148） | 1 |
| g21 | stage1_11/stage1_11_report.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g22 | advisor/index.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 2 |
| g23 | process_report/draft_zh.md | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g24 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g25 | pages_20261106b/methods_addendum/index.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g26 | talk_docs/experiment_walkthrough_zh.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g27 | talk_docs/experiment_walkthrough_methods_zh.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g28 | talk_docs/keys_and_shelves_script_zh_en.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g29 | talk_docs/methods_handbook_guide_plain_zh.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g30 | talk_docs/progress_report_for_advisor_zh.html | 属于事后修改。 | 属于事后修改。批量大小本身造成的组级 E1 恢复比例差最大 0.0148（L40），单 token 的 log10(1/名次) 差 p99 最高 0.22（补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md）。 | 1 |
| g31 | stage1_11/stage1_11_report.html | 这一时间对 5 个假标题都成立<span class="src">（Stage 13 X6 | 这一时间对 5 个假标题都成立（5 个标题之间 L52 的差别在批量舍入噪声的量级内：组级最大 0.0148，补充 12 第 2-4 项）<span class="src">（Stage 13 X6 | 1 |
| g32 | stage1_11/stage1_11_report.html | ：标题最后一个 token 本身携带的信息很少。</p> | ：标题最后一个 token 本身携带的信息很少。E1t 用 5 个假标题（补充 12 第 2-8 项，已完成）：5 个假标题平均与 false_0 版一致——全部论文 L24 +0.136 [+0.125, +0.147]（false_0 版 +0.142）、L40 +0.134（+0.139）、L… | 1 |
| g33 | methods/parts/D_stage10_11.html | target 与 control 形状相同（control 略高，例如 L24 0.175 vs 0.125）。 | target 与 control 形状相同（control 略高，例如 L24 0.175 vs 0.125）。2026-11-09 补：E1t 用 5 个假标题（补充 12 第 2-8 项，已完成）：5 个假标题平均与 false_0 版一致——全部论文 L24 +0.136 [+0.125, +… | 1 |
| g34 | stage1_11/stage1_11_report.html | ② 补充 5 要求“按 token 角色”报告，但 para_run 只存了每个名字的平均分，无法按角色拆分。 | ② 补充 5 要求“按 token 角色”报告；原 para_run 只存了每个名字的平均分，已由补充 12 第 2-3 项用逐 token 打分补做：X3 行为按 token 角色拆开后（补充 12 第 2-3 项，全部作者，测试集），恢复比在 0.806–0.924 之间（首字母 0.851 [… | 1 |
| g35 | methods/parts/F_stage13.html | ① 补充 4/5 要求所有 X3 结果也按 token 角色报告，但 para_run 只存了每个名字的平均分，<b>做不到</b>； | ① 补充 4/5 要求所有 X3 结果也按 token 角色报告，但 para_run 只存了每个名字的平均分，<b>做不到</b>（2026-11-09：已由补充 12 第 2-3 项补做；X3 行为按 token 角色拆开后（补充 12 第 2-3 项，全部作者，测试集），恢复比在 0.806–… | 1 |
| g36 | methods/parts/B_global2.html | 偏离：按 token 角色报告做不到（para_run 只存每个名字的平均分）； | 偏离：按 token 角色报告做不到（para_run 只存每个名字的平均分；2026-11-09 已由补充 12 第 2-3 项补做，C14 不变）； | 1 |
| g37 | methods/parts/G_appendix.html | <td><span class="st st-plan">计划未做</span>（做不到）</td><td>para_run 只存了每个名字的平均分，没有逐 token 分数，无法按角色拆分；不补跑。 | <td><span class="st st-done">已完成（2026-11-09，补充 12 第 2-3 项）</span></td><td>原 para_run 只存了每个名字的平均分；已用批次 1 全部作者的逐 token 打分补做：X3 行为按 token 角色拆开后（补充 12 第 2… | 1 |
| g38 | process_report/draft_zh.md | 按 token 角色报告做不到（V51） | 按 token 角色报告做不到（V51；2026-11-09 已由补充 12 第 2-3 项补做，C14 不变） | 1 |
| g39 | process_report/draft_zh.md | V51 X3 按 token 角色； | V51 X3 按 token 角色（2026-11-09 已完成）； | 1 |
| g40 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | <b>X3 by token role</b> (V51) | <b>X3 by token role</b> (V51; 2026-11-09: done in addendum 12 item 2-3, all roles 0.806–0.924, target − control includes 0, C14 unchanged; b2_x3role.m… | 1 |
| g41 | stage1_11/stage1_11_report.html | 作者差与分组的定义（认得出作者名单）有关，只是描述。 | 作者差与分组的定义（认得出作者名单）有关，只是描述。2026-11-09 补（补充 12 第 2-10 项）：对全部作者的全部名字 token 打分，引用档内 target − control 为 +0.234 [+0.215, +0.252]（团队区间，10 档），姓的第一个 token +0.3… | 1 |
| g42 | stage1_11/stage1_11_report.html | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g43 | advisor/index.html | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g44 | process_report/draft_zh.md | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g45 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g46 | pages_20261106b/methods_addendum/index.html | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g47 | notes_zh.json #81 | 只跑第 0 个分片，排队中 | 第 0 片已完成，其余 47 片运行中 | 1 |
| g48 | stage1_11/stage1_11_report.html | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g49 | advisor/index.html | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g50 | process_report/draft_zh.md | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g51 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g52 | pages_20261106b/methods_addendum/index.html | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g53 | notes_zh.json #81 | 名字位置 probe 等其余各项进行中，没有可报告的结果 | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g54 | talk_docs/progress_report_for_advisor_zh.html | 改为 2-11b（补充 15），只跑第 0 个分片；其余各项进行中； | 改为 2-11b（补充 15），第 0 片已完成，其余 47 片运行中；2-3、2-4、2-8、2-10 已完成；Patchscope 和名字位置 probe 的最终分析进行中；2-1 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中； | 1 |
| g55 | merged_deck/stage1_11_deck.html | 2-11b (addendum 15), shard 0 only, queued; other items in progress; | 2-11b (addendum 15): shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis ru… | 1 |
| g56 | github/README_draft_20261106b.md | 2-11b (addendum 15), shard 0 only, queued; other items in progress; | 2-11b (addendum 15): shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis ru… | 1 |
| g57 | github/README_draft_20261106b.md | 2-11 stopped → 2-11b shard 0 queued; other items in progress | 2-11 stopped → 2-11b: 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope and name-position probe: final analysis running; 2-1 gate re-run | 1 |
| g58 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 全部 token 版 2-10 进行中〕 | 全部 token 版 2-10 已完成：+0.234 [+0.215, +0.252]，姓的第一个 token +0.362，首字母 +0.028（`R13/reports/b2_m3tok.md`），是输出层行为分数，不是分层表征指标，不作为 H2 证据，C06 不变〕 | 1 |
| g59 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md |   - M3 行为分数只有第一作者的第一个 token（2-10 进行中）。 |   - （M3 行为分数已由 2-10 补全部 token，不再属于此项；C06 的 T / I 指标不变。） | 1 |
| g60 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | - 第二批其余项（2-1、2-2、2-3、2-4、2-7、2-8、2-9、2-10）：运行中，没有可报告的结果。 | - 2-3、2-4、2-8、2-10：已完成（2026-11-09，结果写进 C02、C04、C08、C14、L02、U46，见 RQ "第二批结果"）。 - 2-7、2-9（Patchscope）和名字位置 probe：最终分析进行中。 - 2-1：门槛重跑中（集群作业结束脚本误杀，已加看护作业）… | 1 |
| g61 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | - **2-11b**（现场生成名字，补充 15 已锁定）：只跑第 0 个分片，GPU 作业 11736874 排队中；其余 47 片要另行决定（PG 2026-11-08 ~18:15 条）。 | - **2-11b**（现场生成名字，补充 15 已锁定）：第 0 片已完成，其余 47 片运行中。 | 1 |
| g62 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | - **名字位置 probe**（2-5，补充 11 A，主结果按 D11-1 第 2 版用逐个排除版）：GPU 单元还在跑。编排状态 np = rest（`R13/orch_b2/state.json`），2026-11-08 13:30 时为 240 / 432 个单元（RQ R3）。 | - **名字位置 probe**（2-5，补充 11 A，主结果按 D11-1 第 2 版用逐个排除版）：GPU 单元已齐，最终分析进行中。 | 1 |
| g63 | ~/jlens_work/conclusions_v30_draft.md | (C14) | X3 行为按 token 角色拆开后（补充 12 第 2-3 项，全部作者，测试集），恢复比在 0.806–0.924 之间（首字母 0.851 [0.723, 0.978]，姓的第一个 token 0.900 [0.863, 0.935]），各角色、各分层 target − control 的区间… | 1 |
| g64 | ~/jlens_work/conclusions_v30_draft.md | (C02) | 批量舍入噪声：同一输入按 batch 1 和 15 元素 batch 计算，组级 E1 恢复比例的差最大 0.0148（L40），L52 约 0.002，只给分布、没有 CI；补充 12 第 2-4 项，381_stage13/reports/b2_e1noise.md | 1 |
| g65 | methods/parts/K_post_defence.html | (part 5) | (regenerated from the report) | 1 |
| g2-1 | notes_zh.json #81 (overflow) | X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 2-3、2-4、2-8、2-10 已完成；Patchscope 和名字位置 probe 最终分析进行中；2-1 门槛重跑中（作业被误杀，已加看护） | 1 |
Round g exports: 11759923 (report v30, handbook 20261108c, page / talk-doc PDFs); deck v21 11759920 → 11760055 (final, after note 81 shortened; overflow slides 30/72/81 at 901 px vs 898). pptx: pptx_text_fix_20261109g.py (slide 81 status, notes 77/81).
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | advisor/index.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | methods/methods_handbook.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | methods/parts/K_post_defence.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | pages_20261106b/methods_addendum/index.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | process_report/draft_zh.md | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | process_report/index.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | stage1_11/stage1_11_report.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | talk_docs/experiment_walkthrough_methods_zh.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | talk_docs/experiment_walkthrough_zh.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | talk_docs/methods_handbook_guide_plain_zh.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | talk_docs/stage13_script_zh_en.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |
| h1 | P1/P2 mean5 − false_0 range (checker: p12f_mean5.csv |diff| 0.0005–0.0055) | ../../audit_20261105/scoring_audit.html | 差 0.004–0.006 | 差的绝对值 0.001–0.006 | 1 |

## round h

Script `sync_20261107/apply_20261109h.py` (backups `*.before_20261109h2`; numbers asserted against 381_stage13/reports/b2_np_report_v2.md lines 80, 91, 102, 113, 124, 373, 377, 443). H3 "证据不足" → "部分支持" (user decision 2026-11-09); X2- / X4-only statements keep their own verdict; historical records (11-03 wording log, V57) unchanged.

| # | file | before | after | count |
|---|---|---|---|---|
| h1 | stage1_11/stage1_11_report.html | <p><b>总体判断（2026-11-03）：H2 部分支持但未确立，H3 证据不足。</b> | <p><b>总体判断（2026-11-03；2026-11-09 更新 H3）：H2 部分支持但未确立，H3 部分支持。</b> | 1 |
| h2 | stage1_11/stage1_11_report.html | H3：X2 按规则通过，但作者子空间几乎解码不出作者，证据仍不足。</p> | H3：按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L48 +0.103 [0.097, 0.110]；target − control L40 +0.031 [0.… | 1 |
| h3 | stage1_11/stage1_11_report.html | <td><b>文本基线不弱于 Qwen，不能排除文字解释，证据不足</b>（X4： | <td><b>部分支持（2026-11-09，名字位置 probe，补充 11）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L48 +0.103 [0.0… | 1 |
| h4 | stage1_11/stage1_11_report.html | <b>X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足</b></td> | 单看 X2：<b>X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足</b></td> | 1 |
| h5 | advisor/index.html | 〔2026-11-06 已更新：X2 已于 2026-11-05 完成，H3 仍证据不足；见页首更新框〕 | 〔2026-11-06 已更新：X2 已于 2026-11-05 完成；2026-11-09 已更新：名字位置 probe 后 H3 改为部分支持；见页首更新框〕 | 1 |
| h6 | stage1_11/stage1_11_report.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 3 |
| h7 | advisor/index.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h8 | process_report/draft_zh.md | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h9 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h10 | pages_20261106b/methods_addendum/index.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h11 | talk_docs/stage13_script_zh_en.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h12 | methods/parts/F_stage13.html | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h13 | notes_zh.json #71 | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h14 | notes_zh.json #81 | H3 仍证据不足 | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h15 | stage1_11/stage1_11_report.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 3 |
| h16 | advisor/index.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 2 |
| h17 | process_report/draft_zh.md | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 2 |
| h18 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 2 |
| h19 | pages_20261106b/methods_addendum/index.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 2 |
| h20 | talk_docs/stage13_script_zh_en.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 1 |
| h21 | methods/parts/F_stage13.html | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 1 |
| h22 | notes_zh.json #65 | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 1 |
| h23 | notes_zh.json #71 | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 1 |
| h24 | notes_zh.json #81 | H3 证据仍不足 | 单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持） | 1 |
| h25 | notes_zh.json #65 | H2 部分支持但未确立，H3 证据不足 | H2 部分支持但未确立，H3 部分支持（名字位置 probe，补充 11） | 1 |
| h26 | notes_zh.json #74 | H2 部分支持但未确立，H3 证据不足 | H2 部分支持但未确立，H3 部分支持（名字位置 probe，补充 11） | 1 |
| h27 | talk_docs/experiment_walkthrough_zh.html | ；H3 证据不足。”</p> | ；H3 部分支持（名字位置 probe，补充 11）。”</p> | 1 |
| h28 | talk_docs/experiment_walkthrough_methods_zh.html | X4 顺序相反；H3 证据不足。</p> | X4 顺序相反；H3 部分支持（名字位置 probe，补充 11）。</p> | 1 |
| h29 | talk_docs/experiment_walkthrough_zh.html | 但不能排除来自标题文字，所以 H3 证据不足。 | 但不能排除来自标题文字，所以单看 X4，H3 证据不足（H3 总体判断见名字位置 probe：部分支持）。 | 1 |
| h30 | talk_docs/experiment_walkthrough_methods_zh.html | 但不能排除来自标题文字，H3 证据不足； | 但不能排除来自标题文字，单看 X4，H3 证据不足（H3 总体判断见名字位置 probe：部分支持）； | 1 |
| h31 | talk_docs/methods_handbook_guide_plain_zh.html | 所以 H3 证据不足，仍是开放问题。 | 所以单看 X4，H3 证据不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）。 | 1 |
| h32 | talk_docs/stage13_script_zh_en.html | H3 证据不足：连专门用作者提示拟合的读出工具也读不出名字； | H3 原为证据不足（2026-11-09 按名字位置 probe 改为部分支持，见下）：连专门用作者提示拟合的读出工具也读不出名字； | 1 |
| h33 | talk_docs/stage13_script_zh_en.html | H3 has insufficient evidence: | H3 had insufficient evidence before the name-position probe (now partly supported, see below): | 1 |
| h34 | talk_docs/keys_and_shelves_script_zh_en.html | H3 是作者已经在那里、只是不在词表方向上，证据不足： | H3 是作者已经在那里、只是不在词表方向上，原为证据不足（2026-11-09 按名字位置 probe 改为部分支持）： | 1 |
| h35 | talk_docs/keys_and_shelves_script_zh_en.html | off the vocabulary directions, has insufficient evidence: | off the vocabulary directions, had insufficient evidence (since 2026-11-09 partly supported by the name-position probe): | 1 |
| h36 | talk_docs/progress_report_for_advisor_zh.html | ；“作者已经在那里”证据不足。</p> | ；“作者已经在那里”部分支持（名字位置 probe，补充 11）。</p> | 1 |
| h37 | talk_docs/progress_report_for_advisor_zh.html | <td><strong>H3 作者已在、只是不在词表方向</strong></td> <td>证据不足</td> | <td><strong>H3 作者已在、只是不在词表方向</strong></td> <td>部分支持（2026-11-09，名字位置 probe）</td> | 1 |
| h38 | advisor/index.html | <span class="pill no">证据不足</span> | <span class="pill part">部分支持</span> | 1 |
| h39 | process_report/draft_zh.md | 假设：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 证据不足。 | 假设：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 证据不足（2026-11-09 按名字位置 probe 改为部分支持，见第 0 节）。 | 1 |
| h40 | methods/parts/F_stage13.html | <li><b>H3</b>：X4 文本基线不弱于 Qwen，不能排除文字解释，证据不足； | <li><b>H3</b>（2026-11-09 改为部分支持）：按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L48 +0.103 [0.097, 0.110]；t… | 1 |
| h41 | methods/parts/F_stage13.html | <p><b>总体判断（2026-11-03，与报告、PPT 统一）：H2 部分支持但未确立，H3 证据不足。</b></p> | <p><b>总体判断（2026-11-03，与报告、PPT 统一）：H2 部分支持但未确立，H3 证据不足；2026-11-09 按名字位置 probe 改为 H3 部分支持（见上）。</b></p> | 1 |
| h42 | stage1_11/stage1_11_report.html | <li id="pd-b2-cd"> | <li id="pd-b2-np"><b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.… | 1 |
| h43 | advisor/index.html | <li><b>2026-11-08（报告第 30 版）补充的局限：</b> | <li><b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L4… | 1 |
| h44 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | <li><b>2026-11-08（报告第 30 版）补充的局限：</b> | <li><b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L4… | 1 |
| h45 | pages_20261106b/methods_addendum/index.html | <li><b>2026-11-08（报告第 30 版）补充的局限：</b> | <li><b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L4… | 1 |
| h46 | process_report/draft_zh.md |  - **2026-11-08（报告第 30 版）补充的局限：** |  - **名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：**按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0.069 [0.064, 0.074]、L48 +0… | 1 |
| h47 | talk_docs/experiment_walkthrough_zh.html | <p class="upd">2026-11-08（报告第 30 版）： | <p class="upd">2026-11-09：<b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0… | 2 |
| h48 | talk_docs/experiment_walkthrough_methods_zh.html | <p class="upd">2026-11-08（报告第 30 版）： | <p class="upd">2026-11-09：<b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0… | 2 |
| h49 | talk_docs/methods_handbook_guide_plain_zh.html | <p class="upd">2026-11-08（报告第 30 版）： | <p class="upd">2026-11-09：<b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；probe L40 +0… | 1 |
| h50 | talk_docs/progress_report_for_advisor_zh.html | <li>高引用档几乎没有 control 论文，结论主要来自中低引用论文。</li> | <li>高引用档几乎没有 control 论文，结论主要来自中低引用论文。</li> <li><b>名字位置 probe（批次 2 第 2-5 项，补充 11 A，已完成；H3 改为部分支持）：</b>按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，… | 1 |
| h51 | talk_docs/stage13_script_zh_en.html | P1 / P2 with five false titles, done:  | Name-position probe (addendum 11 A), done: By the addendum-11 pre-registered criterion, the surname first token meets H3 at L40/L48 (name-position pro… | 1 |
| h52 | stage1_11/stage1_11_report.html | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h53 | advisor/index.html | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h54 | process_report/draft_zh.md | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h55 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h56 | pages_20261106b/methods_addendum/index.html | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h57 | talk_docs/progress_report_for_advisor_zh.html | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h58 | notes_zh.json #81 | 第 0 片已完成，其余 47 片运行中 | 第 0 片已完成，其余分片运行中 | 1 |
| h59 | stage1_11/stage1_11_report.html | Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中 | 1 |
| h60 | advisor/index.html | Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中 | 1 |
| h61 | process_report/draft_zh.md | Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中 | 1 |
| h62 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中 | 1 |
| h63 | pages_20261106b/methods_addendum/index.html | Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中 | 1 |
| h64 | talk_docs/progress_report_for_advisor_zh.html | Patchscope 和名字位置 probe 的最终分析进行中 | 名字位置 probe 已完成（H3 部分支持）；Patchscope 的最终分析进行中 | 1 |
| h65 | notes_zh.json #81 | Patchscope 和名字位置 probe 最终分析进行中 | 名字位置 probe 已完成（H3 部分支持）；Patchscope 最终分析进行中 | 1 |
| h66 | merged_deck/stage1_11_deck.html | shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis running; | shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis ru… | 1 |
| h67 | github/README_draft_20261106b.md | shard 0 done, other 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope (2-7, 2-9) and name-position probe: final analysis running; | shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis ru… | 1 |
| h68 | github/README_draft_20261106b.md | 2-11b: 47 shards running; 2-3, 2-4, 2-8, 2-10 done; Patchscope and name-position probe: final analysis running | 2-11b: other shards running; 2-3, 2-4, 2-5, 2-8, 2-10 done; Patchscope: final analysis running | 1 |
| h69 | merged_deck/stage1_11_deck.html | H3 (hidden author knowledge): insufficient evidence · X2 (2026-11-05): H2 not supported; H3 passes by rule but the author subspace can hardly decode a… | H3 (hidden author knowledge): partly supported (name-position probe, addendum 11: criterion met for the surname at L40/L48, but lens intervals also ex… | 1 |
| h70 | merged_deck/stage1_11_deck.html | H3: insufficient evidence (text baseline not weaker than Qwen). | H3: partly supported by the name-position probe (addendum 11); X4 alone cannot exclude the title text. | 1 |
| h71 | merged_deck/stage1_11_deck.html | subspace R² ≤ 0.009, H3 still insufficient) | subspace R² ≤ 0.009, X2 alone leaves H3 insufficient) | 1 |
| h72 | notes_zh.json #65 | 所以 H2 部分支持但未确立，H3 部分支持（名字位置 probe，补充 11）； | 所以 H2 部分支持但未确立，H3 部分支持（名字位置 probe，补充 11：姓首 token L40/L48 按判据满足，但 lens 区间也不含 0、尺度不同，降为部分支持）； | 1 |
| h73 | github/README_draft_20261106b.md | H3 (hidden author knowledge) insufficient evidence.** | H3 (hidden author knowledge) partly supported.** The name-position probe (addendum 11) meets the pre-registered criterion for the surname first token … | 1 |
| h74 | github/README_draft_20261106b.md | H2 partly supported, not established; H3 insufficient \| | H2 partly supported, not established; H3 partly supported (name-position probe, 2026-11-09) \| | 1 |
| h75 | github/README_draft_20261106b.md | H3 still insufficient) <sub> | X2 alone leaves H3 insufficient) <sub> | 1 |
| h76 | github/README_draft_20261106b.md | **Latest (2026-11-08, report v30).** | **Latest (2026-11-09).** Name-position probe (addendum 11 A): By the addendum-11 pre-registered criterion, the surname first token meets H3 at L40/L48… | 1 |
| h77 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | ### C22 作者子空间几乎解码不出作者，H3 的证据仍不足（X2，补充 10 全部作者） | ### C22 H3 部分支持：名字位置 probe 按补充 11 判据满足，但 lens 区间也不含 0（2-5）；X2 作者子空间几乎解码不出作者 | 1 |
| h78 | ~/jlens_work/conclusions_v30_draft.md | (C22 body) | 按补充 11 预注册判据，姓首 token 在 L40/L48 满足 H3（名字位置 probe，逐个假标题排除版；pr | 1 |
| h79 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 当前总体判断（REP 第 1101 行，v30 沿用）：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 证据不足。 | 当前总体判断（2026-11-09 更新 H3）：H1 在 ":" 和名字位置成立；H2 部分支持但未确立；H3 部分支持。 | 1 |
| h80 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | \| C22 \| 未定 \| H3 \| 证据不足 \| 按规则通过但解码量极小 \| | \| C22 \| 未定 \| H3 \| 部分支持 \| 名字位置 probe 按补充 11 判据满足（姓 L40/L48），lens 区间也不含 0、尺度不同；X2 解码量极小 \| | 1 |
| h81 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | - **名字位置 probe**（2-5，补充 11 A，主结果按 D11-1 第 2 版用逐个排除版）：GPU 单元已齐，最终分析进行中。 | - **名字位置 probe**（2-5，补充 11 A）：已完成，见 C22。 | 1 |
| h82 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | - 2-7、2-9（Patchscope）和名字位置 probe：最终分析进行中。 | - 2-7、2-9（Patchscope）：最终分析进行中。 | 1 |
| h83 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 第 0 片已完成，其余 47 片运行中。 | 第 0 片已完成，其余分片运行中。 | 1 |
| h84 | stage1_11/src/hyp_table_png_v30_en.py | 'X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足' | 'X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足', '部分支持（2026-11-09，名字位置 probe，补充 11）' | 1 |
| h85 | stage1_11/src/hyp_table_png_v30_en.py |   '<b>Text baseline not weaker than Qwen, a text explanation cannot be excluded: insufficient evidence</b> (X4: |   '<b>Partly supported (2026-11-09, name-position probe, addendum 11):</b> By the addendum-11 pre-registered criterion, the surname first token meets … | 1 |
| h86 | stage1_11/src/hyp_table_png_v30_en.py | <b>X2 passes by rule, but the author subspace | X2 alone: <b>X2 passes by rule, but the author subspace | 1 |
| h87 | stage1_11/src/hyp_table_png_v30_en.py | JUDGE = ('<b>Overall (2026-11-03): H2 partly supported but not established; H3 insufficient evidence.</b> | JUDGE = ('<b>Overall (2026-11-03; H3 updated 2026-11-09): H2 partly supported but not established; H3 partly supported.</b> | 1 |
| h88 | stage1_11/src/hyp_table_png_v30_en.py | H3: X2 passes by rule, but the author subspace hardly decodes authors, so the evidence is still insufficient.') | H3: the name-position probe meets the addendum-11 criterion for the surname at L40/L48, but the lens intervals also exclude 0 and the scales differ, s… | 1 |
| h89 | stage1_11/src/hyp_table_png_v30_en.py | assert '总体判断（2026-11-03）：H2 部分支持但未确立，H3 证据不足。' in s | assert '总体判断（2026-11-03；2026-11-09 更新 H3）：H2 部分支持但未确立，H3 部分支持。' in s | 1 |
| h90 | methods/parts/K_post_defence.html | (part 5) | (regenerated from the report) | 1 |
| h2-1 | stage1_11/stage1_11_report.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 3 |
| h2-2 | advisor/index.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-3 | process_report/draft_zh.md | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-4 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-5 | pages_20261106b/methods_addendum/index.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-6 | talk_docs/stage13_script_zh_en.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-7 | methods/parts/F_stage13.html | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-8 | notes_zh.json #71 | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持） | 1 |
| h2-9 | notes_zh.json #81 | 单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3… | 单看 X2，H3 证据仍不足 | 1 |
| h2-K | methods/parts/K_post_defence.html | (part 5) | regenerated | 1 |
Round h exports: 11763611 + deck 11763628 (superseded); final 11763773 (PNGs v30, slide-65 image, pptx v21, report / handbook / page PDFs) + deck v21 11763778.
| h3-1 | notes_zh.json #81 (overflow) | 〔补充 10 第 1 项，硬检查 PASS；381_stage13/reports/b1_xall_report.md〕 | 〔b1_xall_report.md〕 | 1 |
| h3-2 | notes_zh.json #81 (overflow) | 〔381_stage13/reports/b1_e4b5_report.md〕 | 〔b1_e4b5_report.md〕 | 1 |
| h3-3 | notes_zh.json #81 (overflow) | 〔381_stage13/config/prereg_addendum12_deviations.json〕 | 〔prereg_addendum12_deviations.json〕 | 1 |
| h3-4 | notes_zh.json #81 (overflow) | 〔381_stage13/config/prereg_addendum14.json〕 | 〔prereg_addendum14.json〕 | 1 |
Round h final deck v21: 11763989 (after note 81 source tags shortened).
| i1 | deck slide H3 cell (wording check) | merged_deck/stage1_11_deck.html | but lens intervals also exclude 0) | ... and the scales differ, so sizes cannot be compared) | 1 |

## round i

Script `sync_20261107/apply_20261112i.py` (backups `*.before_20261112i`; numbers asserted against 381_stage13/reports/b2_f1team_report.md and b3_3_1_report.md). Autonomous changes only; H1/H2/H3 unchanged; Patchscope and 2-11b numbers not written. The Stage 10 §6.1 sentence is about the true-title readout LEVEL (−3.0 vs −4.4), which 3-1 does not report; it is kept and the 3-1 title-specific-signal range (J-lens +0.007 to +0.014 at L41–L46, logit ≈ 0, nearly equal at L47) is added beside it.

| # | file | before | after | count |
|---|---|---|---|---|
| i1 | stage1_11/stage1_11_report.html | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i2 | advisor/index.html | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i3 | process_report/draft_zh.md | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i4 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i5 | pages_20261106b/methods_addendum/index.html | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i6 | talk_docs/progress_report_for_advisor_zh.html | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i7 | notes_zh.json #81 | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i8 | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 第 0 片已完成，其余分片运行中 | 已完成，结论待定 | 1 |
| i9 | advisor/index.html | 其余各项进行中（含 Stage 9 Fit B 与 holdout、F1 对半拆分、名字位置 probe 等） | 其余各项进行中 | 1 |
| i10 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 其余各项进行中（含 Stage 9 Fit B 与 holdout、F1 对半拆分、名字位置 probe 等） | 其余各项进行中 | 1 |
| i11 | pages_20261106b/methods_addendum/index.html | 其余各项进行中（含 Stage 9 Fit B 与 holdout、F1 对半拆分、名字位置 probe 等） | 其余各项进行中 | 1 |
| i12 | stage1_11/stage1_11_report.html | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定） | 1 |
| i13 | advisor/index.html | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定） | 1 |
| i14 | process_report/draft_zh.md | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定） | 1 |
| i15 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定） | 1 |
| i16 | pages_20261106b/methods_addendum/index.html | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）的最终分析进行中；2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中 | 名字位置 probe（2-5）已完成（H3 部分支持）；Patchscope（2-7、2-9）已完成，结果待写入（描述性），x4tok 已补全部层；F1 对半拆分（2-2）已完成，F2 的结论在两半都成立；2-1 停止（D12-1，待用户定） | 1 |
| i17 | talk_docs/progress_report_for_advisor_zh.html | 名字位置 probe 已完成（H3 部分支持）；Patchscope 的最终分析进行中；2-1 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中； | 名字位置 probe 已完成（H3 部分支持）；Patchscope 已完成，结果待写入（描述性）；2-2 已完成；2-1 停止（D12-1，待用户定）； | 1 |
| i18 | notes_zh.json #81 | 名字位置 probe 已完成（H3 部分支持）；Patchscope 最终分析进行中；2-1 门槛重跑中（作业被误杀，已加看护） | 名字位置 probe、2-2 已完成；Patchscope 已完成，结果待写入；2-1 停止（D12-1，待定） | 1 |
| i19 | stage1_11/stage1_11_report.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504） | 1 |
| i20 | advisor/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504） | 1 |
| i21 | process_report/draft_zh.md | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504） | 1 |
| i22 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504） | 1 |
| i23 | pages_20261106b/methods_addendum/index.html | 3-1 Stage 10 补 L41–L47、L49，3-2 补 L0–L23：编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 Stage 10 补 L41–L47、L49：已完成；3-2 补 L0–L23：运行中（194 / 504） | 1 |
| i24 | talk_docs/progress_report_for_advisor_zh.html | 3-1、3-2 编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 已完成，3-2 运行中（194 / 504） | 1 |
| i25 | notes_zh.json #81 | 3-1、3-2 编排作业已提交，第二批全部结束后自动开始（进行中） | 3-1 已完成，3-2 运行中（194 / 504） | 1 |
| i26 | merged_deck/stage1_11_deck.html | shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis ru… | done, conclusion pending; 2-2, 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9) done, results to be wri… | 1 |
| i27 | github/README_draft_20261106b.md | shard 0 done, other shards running; 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9): final analysis ru… | done, conclusion pending; 2-2, 2-3, 2-4, 2-5 (name-position probe: H3 partly supported), 2-8, 2-10 done; Patchscope (2-7, 2-9) done, results to be wri… | 1 |
| i28 | github/README_draft_20261106b.md | 2-11b: other shards running; 2-3, 2-4, 2-5, 2-8, 2-10 done; Patchscope: final analysis running; 2-1 gate re-run | 2-11b done, conclusion pending; 2-2, 2-3, 2-4, 2-5, 2-7/2-9, 2-8, 2-10 done; 2-1 stopped (D12-1) | 1 |
| i29 | merged_deck/stage1_11_deck.html | 3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23: queued, start after batch 2 | 3-1 Stage 10 L41–L47, L49: done · 3-2 L0–L23: running (194/504) | 1 |
| i30 | github/README_draft_20261106b.md | Stage 10 L41–L47, L49 and L0–L23 queued, start after batch 2; | Stage 10 L41–L47, L49 done (3-1); L0–L23 running (3-2, 194/504); | 1 |
| i31 | github/README_draft_20261106b.md | \| 3-1, 3-2 queued (after batch 2); | \| 3-1 done; 3-2 running (194/504); | 1 |
| i32 | stage1_11/stage1_11_report.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i33 | advisor/index.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 2 |
| i34 | process_report/draft_zh.md | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i35 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i36 | pages_20261106b/methods_addendum/index.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i37 | talk_docs/experiment_walkthrough_zh.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i38 | talk_docs/experiment_walkthrough_methods_zh.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i39 | talk_docs/methods_handbook_guide_plain_zh.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i40 | talk_docs/progress_report_for_advisor_zh.html | （补充 14 只补 L41–L47、L49 和 L0–L23，都在排队） | （补充 14 的 3-1 已补 L41–L47、L49，2026-11-12 完成；3-2 补 L0–L23，运行中，194 / 504） | 1 |
| i41 | stage1_11/stage1_11_report.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i42 | advisor/index.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 2 |
| i43 | process_report/draft_zh.md | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i44 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i45 | pages_20261106b/methods_addendum/index.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i46 | talk_docs/experiment_walkthrough_zh.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i47 | talk_docs/experiment_walkthrough_methods_zh.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i48 | talk_docs/methods_handbook_guide_plain_zh.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i49 | talk_docs/progress_report_for_advisor_zh.html | “L24–L48 约为 0”在缺口层没有测过 | “L24–L48 约为 0”在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L41–L… | 1 |
| i50 | stage1_11/stage1_11_report.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i51 | advisor/index.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 2 |
| i52 | process_report/draft_zh.md | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i53 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i54 | pages_20261106b/methods_addendum/index.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i55 | talk_docs/experiment_walkthrough_zh.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i56 | talk_docs/experiment_walkthrough_methods_zh.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i57 | talk_docs/methods_handbook_guide_plain_zh.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i58 | talk_docs/progress_report_for_advisor_zh.html | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道） | Stage 10 真标题下 Jacobian lens 从 L40 起明显好于 logit lens（跳变在 L33–L40 的哪一层不知道；3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-le… | 1 |
| i59 | stage1_11/stage1_11_report.html | 明显好于 logit lens（约 −3.0） | 明显好于 logit lens（约 −3.0；这是真标题下的读出水平。3-1 补测后，标题特异信号上 J-lens 在 L41–L46 为 +0.007 到 +0.014、logit 约为 0，到 L47 两者几乎相同（J-lens +0.001 [−0.005, +0.006]，logit −0.… | 1 |
| i60 | stage1_11/stage1_11_report.html | beat the logit lens from L40 on (the previous measured layer is L32, so the jump lies somewhere in L33–L40; about −3.0) | beat the logit lens from L40 on (the previous measured layer is L32, so the jump lies somewhere in L33–L40; about −3.0; this is the true-title readout… | 1 |
| i61 | notes_zh.json #82 | Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划； | Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划（L41–L47、L49 已由 3-1 补齐）； | 1 |
| i62 | merged_deck/stage1_11_deck.html | (no L25–L31, L33–L39; no plan to fill) | (no L25–L31, L33–L39; no plan to fill; L41–L47, L49 filled by 3-1) | 1 |
| i63 | github/README_draft_20261106b.md | (no L25–L31, L33–L39) with no plan to fill them | (no L25–L31, L33–L39) with no plan to fill them (L41–L47, L49 filled by 3-1 on 2026-11-12: logit target − control within ±0.005 there, J-lens negative… | 2 |
| i64 | stage1_11/stage1_11_report.html | <li id="pd-b2-np"> | <li id="pd-b2-f1"><b>F1 对半拆分（批次 2 第 2-2 项，已完成）：</b>F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033… | 1 |
| i65 | advisor/index.html | <li><b>名字位置 probe（批次 2 第 2-5 项 | <li><b>F1 对半拆分（批次 2 第 2-2 项，已完成）：</b>F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L6… | 1 |
| i66 | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | <li><b>名字位置 probe（批次 2 第 2-5 项 | <li><b>F1 对半拆分（批次 2 第 2-2 项，已完成）：</b>F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L6… | 1 |
| i67 | pages_20261106b/methods_addendum/index.html | <li><b>名字位置 probe（批次 2 第 2-5 项 | <li><b>F1 对半拆分（批次 2 第 2-2 项，已完成）：</b>F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L6… | 1 |
| i68 | process_report/draft_zh.md |  - **名字位置 probe（批次 2 第 2-5 项 |  - **F1 对半拆分（批次 2 第 2-2 项，已完成）：**F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L62：+0… | 1 |
| i69 | advisor/index.html | 作者提示 lens 没做对半拟合。<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：Fit B 与 F1 对半拆分都列入批次 2；见页首更新框〕</span> | 作者提示 lens 没做对半拟合。<span style="color:#A15C07;font-size:.85em">〔2026-11-06 已更新：Fit B 与 F1 对半拆分都列入批次 2；2026-11-12 已更新：F1 对半拆分已完成，F2 的结论在两半都成立，中间层 lens 矩阵… | 1 |
| i70 | ~/jlens_work/conclusions_v30_draft.md | 样本不完整（F1 只用 40 篇拟合；对半拆分 2-2 进行中） | 样本不完整（F1 只用 40 篇拟合；对半拆分 2-2 已完成：F2 的阴性结论在两半拟合中都成立——名字位置 target − control L48：A 半 −0.050 [−0.078, −0.022]、B 半 −0.063 [−0.094, −0.033]、全部 −0.058；L62：+0.… | 1 |
| i71 | ~/jlens_work/conclusions_v30_draft.md | 事后改判据（一致性容差 0.25 → 0.5，主轮数据靠 0.5 才通过，见 CHK A2）〕 | 事后改判据（一致性容差 0.25 → 0.5，主轮数据靠 0.5 才通过，见 CHK A2）；2026-11-12：3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 tar… | 1 |
| i72 | ~/jlens_work/conclusions_v30_draft.md | 也没有 L41–L47、L49、L0–L23） | 也没有 L0–L23（3-2 运行中）；L41–L47、L49 已由 3-1 补齐） | 1 |
| i73 | ~/jlens_work/conclusions_v30_draft.md | - **第三批**（3-1 补 L41–L47、L49；3-2 补 L0–L23）：编排作业 b3_orch 等第二批全部结束后自动开始。3-3 已停止（见 L07）。 | - **第三批**：3-1（补 L41–L47、L49）已完成；3-2（补 L0–L23）运行中（194 / 504）。3-3 已停止（见 L07）。 | 1 |
| i74 | ~/jlens_work/conclusions_v30_draft.md | - 2-7、2-9（Patchscope）：最终分析进行中。 | - 2-7、2-9（Patchscope）：已完成，结果待写入（描述性）；x4tok 已补全部层。 | 1 |
| i75 | ~/jlens_work/conclusions_v30_draft.md | - 2-1：门槛重跑中（集群作业结束脚本误杀，已加看护作业）。2-2：进行中。 | - 2-1：停止（D12-1，待用户定）。2-2：已完成（见 C16、L13）。 | 1 |
| i76 | ~/jlens_work/conclusions_v30_draft.md |   - L41–L47、L49 由 3-1 补，排队中。L0–L23 由 3-2 补，排队中，只补 logit 和 public，只补 target + control 6,841 篇。 |   - L41–L47、L49 已由 3-1 补齐（2026-11-12）。L0–L23 由 3-2 补，运行中（194 / 504），只补 logit 和 public，只补 target + control 6,841 篇。 | 1 |
| i77 | ~/jlens_work/conclusions_v30_draft.md |   - "L24–L48 约为 0"在缺口层没有测过。 |   - "L24–L48 约为 0"在 L25–L31、L33–L39 没有测过；3-1 补测的 L41–L49 上，logit 的 target − control 都在 ±0.005 以内、从 L50 起为正（起始层不变）；public J-lens 的 target − control 在 L… | 1 |
| i78 | ~/jlens_work/conclusions_v30_draft.md |   - F1 作者 lens 只用 40 篇拟合（2-2 进行中）； |   - F1 作者 lens 只用 40 篇拟合；2-2 对半拆分已完成，F2 结论在两半都成立，但中间层 lens 矩阵随拟合集变化大（A–B 余弦 L24 0.64、L40 0.85、L48 0.94；L24 top-10 重合 0.28）； | 1 |
| i79 | ~/jlens_work/conclusions_v30_draft.md |   - Stage 9 Fit B 停在 66 / 100（2-1 进行中）。 |   - Stage 9 Fit B 停在 66 / 100（2-1 停止，D12-1，待用户定）。 | 1 |
| i80 | methods/parts/K_post_defence.html | (part 5) | (regenerated from the report) | 1 |
Round i exports: 11831475 (report v30, handbook 20261108c, page / talk-doc PDFs) + deck v21 11831474; pptx via pptx_text_fix_20261112i.py (3/3 rules, notes 81/82).
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | stage1_11/stage1_11_report.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | github/README_draft_20261106b.md | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 0+2 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | methods/methods_handbook.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | methods/parts/K_post_defence.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | advisor/index.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 2+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | pages_20261106b/methods_addendum/index.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | process_report/index.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | process_report/draft_zh.md | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | talk_docs/experiment_walkthrough_methods_zh.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | talk_docs/experiment_walkthrough_zh.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | talk_docs/methods_handbook_guide_plain_zh.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | talk_docs/progress_report_for_advisor_zh.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | ../../audit_20261105/scoring_audit.html | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 1+0 |
| j1 | 3-1 J-lens T − C range (checker v15: L56 +0.007 [−0.014, +0.029]) | /home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md | 在 L41–L56 为负 / negative to L56 | 在 L41–L55 为负、L56 约为 0 / negative through L55, about 0 at L56 | 2+0 |
