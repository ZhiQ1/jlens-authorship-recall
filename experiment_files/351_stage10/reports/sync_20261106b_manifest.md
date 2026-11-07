# Sync 2026-11-06 b — manifest (local only; nothing published, nothing pushed)

Content: user-confirmed batch-1 wording (PROGRESS 2026-11-06 ~13:30 a–e): X1–X4 all authors (b), E4b five false titles (d) + surname target − control (a), X7 (c, already in v29), C-1..C-5 (e, already in v29, verified by asserts); C-3b (sensitivity only); P1/P2 still running (116/194, no numbers); batch 2 code ready / auto start / D12-1..D12-3 / 2-7 source; batch 3 (addendum 14) code in progress, 3-4/3-5 not run.
Rules kept: every edit by a new script, backups `*.before_20261106b.*` (merge step: `*.before_merge_20261106b.*`), no existing number changed (superseded statements only flagged), no rm except own scratchpad temp, no scancel, STATUS/PROGRESS/HANDOFF untouched. Version names: report stays v29, deck v20, handbook 2026-11-06; new download files carry a `b` suffix so the earlier local v29/v20/20261106 files stay.
Before publishing: local sources of advisor, process report, scoring audit, downloads page were diffed against the live pages today (~21:00): identical except the artifact wrapper. Live copies saved under `pages_20261106b/live_*/`. Main session must still re-read live versions before publishing (rule).

## 1. Pages to publish (local HTML → artifact)

| # | Document | Local HTML to publish | Artifact | Edit script | Screenshots checked |
|---|---|---|---|---|---|
| 1 | Report v29 (b) | `351_stage10/reports/stage1_11/stage1_11_report.html` | https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe | `stage1_11/src/edit_v29b.py` (backup `stage1_11_report.before_20261106b.html`) | `stage1_11/chk_20261106b/*.png` (ov, pd_running, alltok_tc, alltok_boxes, alltok_c3b, x1x4_box, x3_ptr, x2_ptr) via `src/shot_v29b.py` |
| 2 | Deck v20 (b), 82 slides | `351_stage10/reports/merged_deck/stage1_11_deck.html` | https://claude.ai/artifact/XcgK4YF2dYQxudWfhk8MsD | `talk/src/export/deck_v20b_new.py` + `edit_deck_v20b.py` (backups `stage1_11_deck.before_20261106b.html`, `slides.before_20261106b.json`, `notes_zh.before_20261106b.json`); pptx `patch_editable_v20b.py` | `talk/src/export/shots/v20b/s72.png s75.png s81.png` (HTML), `pptx_s72.png pptx_s81.png` (pptx via LibreOffice), `notespdf_81.png` |
| 3 | Methods handbook 2026-11-06 b | `351_stage10/reports/methods/methods_handbook.html` | https://claude.ai/artifact/W7r7xVte3eaNcbo8D8cybo | `methods/edit_20261106b.py` then `build_methods.py` (part backups `parts/*.before_20261106b.html`) | `methods/shots_20261106b/*.png` (xall, alltok_tc, alltok_e4b5, k_running, k_e4b5, g_v61) |
| 4 | Advisor progress report (MERGED, current) | `351_stage10/reports/advisor/index.html` (+ `x5_layer_order.png`) | https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs | `pages_20261106b/edit_pages_20261106b.py`, then `pages_20261106b/merge_advisor_20261106b.py` | `pages_20261106b/chk_advisor_box.png, chk_advisor_flag.png, chk_merged_selfcheck.png, chk_merged_next.png` |
| 5 | Talk doc 给老师的进度汇报 (SUPERSEDED) | `talk_docs/progress_report_for_advisor_zh.html` | https://claude.ai/artifact/8XcY8CRpz3AAjfDE4n6V6e | `talk_docs/edit_talkdocs_20261106b.py` (status sentence) + red top line "本页已过时，最新内容见 https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs" by `merge_advisor_20261106b.py` | `talk_docs/chk_20261106b_progress_redo.png`, `pages_20261106b/chk_talkdoc_superseded.png` |
| 6 | Talk doc Stage 13 讲稿 | `talk_docs/stage13_script_zh_en.html` | https://claude.ai/artifact/KC2kW4NmjD41couEghy365 | `talk_docs/edit_talkdocs_20261106b.py` | `talk_docs/chk_20261106b_stage13_script_zh_en.png` |
| 7 | Other four talk docs | unchanged since 20261106 (they do not mention batch 1): walkthrough RBLSRBo4YcL1gAKi8gpp4m, walkthrough methods RX4KpcC5xGu7ynM6AzYSTz, keys & shelves UfKPpZNLicWhFDZbwTevAm, handbook guide WUk8MdPwVhfzJmyopp6JBs | publish the 20261106 versions | — | — |
| 8 | 实验全过程汇总 | `351_stage10/reports/process_report/index.html` (built from `draft_zh.md` by `build_process_report.py`, + `style.css`) | https://claude.ai/artifact/TmqEtZg3gHTz7p7vCkaiB4 | `edit_pages_20261106b.py` (new §0 + flags; backup `draft_zh.before_20261106b.md`) | `pages_20261106b/chk_process_box.png, chk_process_flag.png` |
| 9 | 打分单位审计 | `/scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html` | https://claude.ai/artifact/C6UVJDUtg4JJmkaKBrnwd7 | `edit_pages_20261106b.py` (backup `scoring_audit.before_20261106b.html`) | `pages_20261106b/chk_audit_box.png` |
| 10 | 方法补遗 (no local source before; live copy saved by Artifact read) | `351_stage10/reports/pages_20261106b/methods_addendum/index.html` | https://claude.ai/artifact/VkyyqsvE43k2BkU6VSZ2kg | `edit_pages_20261106b.py` (backup `index.before_20261106b.html` = live version 1793864088-9b4d) | `pages_20261106b/chk_addendum_box.png, chk_addendum_flag.png` |
| 11 | Downloads page | source `351_stage10/reports/downloads/index.html` (= live 1793918868-98f1, still lists v28/v19 as newest) | https://claude.ai/artifact/5Tdt1mQa8xnPiqQEKvjzta | NOT edited (rows below) | — |
| 12 | README draft | `351_stage10/reports/github/README_draft_20261106b.md` (input `README_draft_20261106.md` unchanged) | repo README (push by main session) | `github/make_readme_draft_20261106b.py` | text checked (status table one line per item) |
| 13 | Plan document | `351_stage10/reports/plan/plan_master_queue_20261106b.{md,html}` | repo docs / downloads | `plan/make_plan_20261106b.py` | `plan/chk_plan_20261106b.png` (+ `_mid.png`) |

Checks: report 0 duplicate ids / 0 broken internal links; handbook 0 / 0 (build_methods.py); secondary pages 0 / 0; `minyan` 0 everywhere. Deck HTML has 2 duplicate SVG ids (`mpatcg`, `mpatca3C78B4`) that were already in v20 before this edit (not introduced here).

## 2. Files produced in `351_stage10/reports/downloads/` (previous versions kept)

| File | Pages / size | Replaces on the downloads page |
|---|---|---|
| Stage1-13_report_v29b_A4.pdf | 115 p, 11.7 MB | Stage1-13_report_v28_A4.pdf (→ 上一版); local v29 PDF never published |
| Stage1-13_deck_v20b_slides.pdf | 82 p, 12.4 MB (JPEG q65 to stay < 15 MB; q80 gave 16.6 MB) | v19 slides |
| Stage1-13_deck_v20b_with_notes_zh.pdf | 82 p, 14.4 MB (notes page 1280×1620) | v19 with notes |
| Stage1-13_deck_v20b_editable.pptx (+ .b64.txt) | 82 slides, 4.8 MB (b64 6.4 MB) | v19 pptx |
| Stage1-13_methods_handbook_A4.v20261106b.pdf | 215 p, 10.3 MB | v20261105c |
| jlens_progress_report_2026-11-06b_A4.pdf (merged advisor page) | 9 p, 3.0 MB | jlens_progress_report_2026-11-04_A4.pdf |
| jlens_process_report_2026-11-06b_A4.pdf | 28 p, 2.8 MB | jlens_process_report_2026-11-04_A4.pdf |
| scoring_audit_2026-11-06b_A4.pdf | 33 p, 0.9 MB | (new row) |
| methods_addendum_2026-11-06b_A4.pdf | 20 p, 1.5 MB | methods_addendum_2026-11-05_A4.pdf (not on /scratch; only inline on the live page) |
| talkdoc_progress_report_for_advisor_zh_20261106b_A4.pdf | 7 p, 0.7 MB (with "已过时" line) | talkdoc_…_20261106 |
| talkdoc_stage13_script_zh_en_20261106b_A4.pdf | 6 p, 0.3 MB | talkdoc_…_20261106 |
| talkdoc_{experiment_walkthrough_zh, experiment_walkthrough_methods_zh, keys_and_shelves_script_zh_en, methods_handbook_guide_plain_zh}_20261106_A4.pdf | unchanged | — |
| plan_master_queue_20261106b_A4.pdf | 5 p, 0.1 MB | plan_master_queue_20261106_A4.pdf |
| keys_and_shelves_evidence_v20.pdf | 18 p (15 slides + 3 tables), 1280×720 landscape, 3.1 MB | (new row) |
| Stage13_hypotheses_table_v28_en_{tableonly,slide,wide}.png | 0.2–0.3 MB each | (new; English) |

### New rows needed on the downloads page (format of the existing `<li>`: name · meta · size · 保存 button with data-f / data-b64)
1. Stage1-13_report_v29b_A4.pdf — 新 · 实验报告第 29 版（Stage 1–13；补充 9–13 重做结果、批次 1 的 X1–X4 全部作者、E4b 5 个假标题、C-3b），115 页 · 11.7 MB. v28 → 上一版; v27 row removed (keep only newest + previous).
2. Stage1-13_deck_v20b_with_notes_zh.pdf — 新 · PPT v20 带中文讲稿，82 页 · 14.4 MB; 3. …_slides.pdf — 82 页 · 12.4 MB; 4. …_editable.pptx — 可编辑版，82 页 · 4.8 MB (data-b64 …pptx.b64.txt). v19 → 上一版, v18 rows removed.
5. Stage1-13_methods_handbook_A4.v20261106b.pdf — 新 · 方法手册（2026-11-06 b：重做计划、补充 9、X7 五个假标题、补充 13、批次 1），215 页 · 10.3 MB. 20261105c → 上一版, 20261105 removed.
6. jlens_progress_report_2026-11-06b_A4.pdf — 新 · 进度汇报（合并版：原进度汇报 + 讲稿版的自查表和下一步 + 2026-11-06 更新），9 页 · 3.0 MB; 11-04 → 上一版.
7. jlens_process_report_2026-11-06b_A4.pdf — 新 · 实验全过程汇总（加 §0 2026-11-06 更新），28 页 · 2.8 MB; 11-04 → 上一版.
8. methods_addendum_2026-11-06b_A4.pdf — 新 · 方法补遗（加 2026-11-06 更新框与已更新标注），20 页 · 1.5 MB; 11-05 → 上一版 (keep its inline data, `data-inline="pdf-addendum"`).
9. scoring_audit_2026-11-06b_A4.pdf — 新 · 打分单位审计（加 2026-11-06 更新框），33 页 · 0.9 MB.
10. keys_and_shelves_evidence_v20.pdf — 新 · Keys and shelves 证据页（讲演短版：v20 的 15 页 + 3 张英文假设表），18 页 · 3.1 MB.
11. Talk docs: talkdoc_progress_report_for_advisor_zh_20261106b_A4.pdf（已过时，指向合并版）, talkdoc_stage13_script_zh_en_20261106b_A4.pdf; the other four keep their 20261106 rows.
12. plan_master_queue_20261106b_A4.pdf — 实验安排表（2026-11-06 21:00 状态）, 5 页.
13. Stage13_hypotheses_table_v28_en_{tableonly,slide,wide}.png — 英文假设表（新，由中文 v28 表逐句翻译）.

## 3. What changed, per document
- **Report v29 b**: header line; overview ④ (X1–X4 + E4b done, P1/P2 running); #alltok-results: surname target − control sentence = wording a (replaces "L16–L52 约为 0"; note "下表为只用 false_0 的版本"), C-3 box "该版本已完成，见下框", new green box batch-1 item 4 (wording d + a) and grey box C-3b; Part 4: green box X1–X4 all authors (wording b + hard check) at the end of #m3x1x4-results, pointer notes in #x3-results and #x2-results; Part 5 #pd-running: done list, batch-1 heading, #pd-b1-xall (b), #pd-b1-p12f (running 116/194), #pd-b1-e4b5 (d + a + C-3b), batch 2 status + D12-1..3 + 2-7 source, new batch-3 line; two Fit B status sentences. Full source tags (file + section/table + n + CI method) on every new number.
- **Deck v20 b**: slide 72 (target − control bullet = wording a, note box "Five false titles (batch 1)" with file tags), slide 75 (divider line 3), slide 81 (title "addenda 10–14", six bullets: done / batch 1 done / batch 1 running / batch 2 / batch 3 / not done, file tags); notes 69, 70, 71 (+ all-author sentence), 72, 81 rewritten with 〔source〕 tags. pptx: only slides 72, 75, 81 text and notes 69–72, 81 differ from v20 (checked by text diff).
- **Handbook**: F s13-x1 new box #s13-xall (wording b, full provenance) + pointers in s13-x2/x3/x4; s13-alltok: wording a, five-title result (d), C-3b, limits, status; G: V58 done, new V61 (C-3b), V62 (D12 deviations, 2-7 source); C: Fit B status; B: two prereg-deviation rows; K rebuilt from report v29 b Part 5; header.
- **Advisor page (merged)**: update box (7 items, each with source file + table/section + method), orange "已更新" flags on 9 superseded statements, meta line "合并更新", self-check table and 待确认/下一步 from the talk doc (verbatim; X7 row and Fit B item flagged).
- **Talk docs**: progress report status sentence (batch 1) + E4b line + superseded banner; Stage 13 script: zh + en box (b, d, a).
- **Process report**: new §0 (same 7 items) + 4 inline flags. **Scoring audit**: update box + mapping of audit findings to redo items. **Methods addendum**: update box + 4 flags (L41–L47/L49, X7 control 0.051, Fit B, E4b first token).
- **README draft b**: redo-programme bullets (batch 1 results, short, file tags) and Status table = one line per item (what / conclusion / status / source).
- **Plan b**: batch 1 items 1, 2, 4 done, 3 running; C-3b done (sensitivity only); batch 2 "code ready, queued (auto)" (+ D12 / 2-7 notes); batch 3 rows 3-1..3-3 "code in progress", 3-4/3-5 not done.
- **Hypothesis-table images**: table content NOT changed by this sync, so the Chinese `Stage13_hypotheses_table_v28_tableonly.png` was not re-rendered. No English version existed: rendered English `…_v28_en_{tableonly,slide,wide}.png` by `stage1_11/src/hyp_table_png_v28_en.py` — my sentence-by-sentence translation of the v28 table cells (numbers unchanged; script asserts the Chinese source cells are unchanged). The user may want to check the wording.

## 4. Keys and shelves evidence page: v16 → v20 mapping (from `talk/v16_to_v20_page_map.csv`, direct counterparts; the "new in v17" method pages were not used)
48→59 Keys and shelves · 8→10 How we read the model · 4→4 Same papers, two ways of grouping · 7→9 How groups and contrasts are built · 9→11 Can we trust the numbers? · 16→22 Knowing the paper shows up only at the end · 30→39 Read early: a probe finds it at the title · 18→25 The probe signal is paper-specific · 37→48 Stage 11: intervene, do not just read · 38→49 The title is read in L24-L50, early · 35→44 Target pulls ahead only in the last layers · 36→45 It builds up over the last dozen layers · 27→36 Names become readable late · 28→37 Which lens reads best? · 29→38 Do lenses reveal hidden paper knowledge?. All 15 have a counterpart. Pages taken from `Stage1-13_deck_v20b_slides.pdf` (none of these slides changed in b). Script `talk/src/export/make_keys_shelves_evidence_v20.py`; screenshot grid `talk/src/export/shots/v20b/ks_grid.png` (pages 1, 7, 16, 18). File name has no `_A4` because pages are 1280×720 slides.

## 5. Conclusions flagged (no per-item data behind them, or inconsistent) — not deleted, for the user
1. Advisor page (merged) self-check table (from the talk doc): rows have no per-row result file; a note points to handbook G4 and the process report §6.
2. "可能的下一步" in the merged advisor page: suggestions, labelled "没有数据支撑，不是结论".
3. Inconsistency: advisor page says the Stage 8 primary endpoint was changed to L56 "在冻结前", the talk-doc table says "在冻结后". Not changed; user to decide.
4. Report #alltok-results: the confirmed sentence "这一差别主要来自首字母和名" now sits next to wording a (surname positive from L24 with five false titles). Both are user-confirmed; user may want to reconcile.
5. Deck v20 slide 64 (English deck) still embeds the Chinese hypothesis-table image; the English image now exists if the user wants it swapped.
6. A full sweep of every older conclusion in all documents for a missing source was NOT done in this pass (only the content touched here was given full provenance; superseded statements were flagged). Suggest the separate checker covers this.

## 6. Current vs superseded inventory
| Kind | Current (local, to publish) | Superseded (keep as 上一版 or archive) |
|---|---|---|
| Report | stage1_11_report.html = v29 b; PDF v29b | v28 (live), v29 local PDF (never published), v27 and older |
| Deck | stage1_11_deck.html = v20 b; v20b PDFs/pptx | v19 (live), v20 local exports, v18 and older |
| Handbook | methods_handbook.html 2026-11-06 b; PDF v20261106b | 20261105c (live), 20261106, older |
| Advisor report | advisor/index.html (merged) | talk doc 8XcY8CRpz3AAjfDE4n6V6e (now marked 已过时); PDF 2026-11-04 |
| Process report | process_report/index.html (§0 added) | 2026-11-04 PDF |
| Scoring audit | audit_20261105/scoring_audit.html (update box) | 2026-11-05 live version |
| Methods addendum | pages_20261106b/methods_addendum/index.html | live 1793864088-9b4d; PDF 2026-11-05 |
| Talk docs | 2 changed (20261106b), 4 unchanged (20261106) | before_20261106 versions |
| README | README_draft_20261106b.md | README_draft_20261106.md; repo README (2026-10-30) |
| Plan | plan_master_queue_20261106b.* | plan_master_queue_20261106.* |
| Hypothesis tables | v28 zh tableonly (unchanged) + v28 en ×3 (new) | v22 (slide/wide/tableonly), v23 (`Stage13_hypotheses_table_v23.png` is a wrong crop of the report TOC, not a table), v23_tableonly |
| Evidence page | keys_and_shelves_evidence_v20.pdf | — |

## 7. Not done / open
- Downloads page HTML not edited (rows listed above); nothing published; git not pushed (main session).
- P1/P2 five-false-title result: placeholder only (still running).
- talk_docs/README.md version table not updated (main session may add the 20261106b line).
