# Sync 2026-11-07 — manifest (user decisions ~01:30; local only, nothing published, nothing pushed)

Scripts: `351_stage10/reports/sync_20261107/apply_20261107.py` (+ `apply_20261107b.py`, `verify_no_data_20261107.py`, `export_pdfs_20261107.py`), `methods/edit_20261107.py` (part K regenerated + build), `talk/src/export/patch_editable_v20b_20261107.py` + `pptx_text_fix_20261107.py` (pptx), `talk/src/export/export_v20c_full.sbatch` (deck PDFs, job 11696647 COMPLETED 1:23). Backups `*.before_20261107.*` (report also `.before_20261107b.html`). Publish targets are the same local HTML files as in `sync_20261106b_manifest.md` §1.

## Done
1. Five mismatches: Stage 10 L63 now "+0.207 [0.195, 0.220]" everywhere (13 places, incl. notes, README b, process report); #ov n → 3,734 / 2,182 (separator "+" kept, as in 9 other places); E4b trainstd range max → +0.075 (report #p4-plan, notes 39/40/73); R0 lower bound → 0.188 (advisor, process report) and report "+0.20" → "+0.199"; report §1 old E4b values → L40 0.061, L56 0.075 with the trainstd source (zh + en).
2. All 108 写法不统一 → canonical: 124 replacements in total (incl. item 1). Summary: `numcheck/claims/unify_summary_20261107.md`.
3. Report conclusions without data: 12 sentences verified by code; 10 got provenance, 2 weakened ("几乎全部是标题特异的" → "主要是" (84% of +0.247); "没有哪种 lens…" → "都很小或为负…logit lens L24–L32 有很小的正值"). Details: `numcheck/claims/no_data_fixes_20261107.md`.
A. Stage 8 endpoint sentence unified (report 8A box, advisor ×2, talk docs: progress report, two walkthroughs, handbook guide; deck slide 60 + note, English translated). Handbook C/G and process report already said the same thing; left as is.
C. Deck: the hypothesis table is on v20 slide **65** (= v17/v19 slide 64). Its image is now `Stage13_hypotheses_table_v28_en_tableonly.png` (HTML, pptx, PDFs). PNG for the user: `talk/src/export/shots/v20b/s64_en_table.png` (= v20 slide 65).

## NOT done
B. Not written: initial-token target − control at L40 is +0.014 [−0.002, +0.030] (CI includes 0), so "首字母…从约 L24 起为正" is not supported. Old sentence unchanged. Given-name first token is positive from L16; given_cont is not significant at L44/L48; surname first token is positive from L24, L40 +0.030 [0.013, 0.048]. Source: `381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv`, version Vpd, column tc.

## Exports (downloads/; previous files kept)
Report `Stage1-13_report_v29c_A4.pdf` (115 p). Deck v20c, lossless PNG, two parts each:
- `Stage1-13_deck_v20c_slides_part1_p1-41.pdf` 15.0 MB, `…part2_p42-82.pdf` 13.5 MB
- `…_with_notes_zh_part1_p1-41.pdf` 16.6 MB, `…part2_p42-82.pdf` 15.0 MB

Three of these are ≥ 15 MB; the artifact limit for one binary file is 15 MB, so use three parts if they go on the downloads page. Editable pptx: `Stage1-13_deck_v20c_editable.pptx` (+ b64). The v20b pptx was restored unchanged.

Handbook `…A4.v20261107.pdf` (215 p). Talk docs `talkdoc_{experiment_walkthrough_methods_zh, experiment_walkthrough_zh, methods_handbook_guide_plain_zh, progress_report_for_advisor_zh}_20261107_A4.pdf`. Advisor page `jlens_progress_report_2026-11-07_A4.pdf`, process report `jlens_process_report_2026-11-07_A4.pdf`.

Unchanged today: scoring audit, methods addendum, plan b, keys-and-shelves evidence PDF (none of its slides changed), Stage 13 script, keys & shelves script.

## Screenshots checked
- `sync_20261107/shots/` (report #ov, 8A box, §7 F14, §1; advisor; handbook guide)
- `talk/src/export/shots/v20b_0107/` (s30, s60, s65 HTML; pptx_s60/s65; pdf_s65)

## Strict check after the edits (latest out_*)
- 1,235 一致, 2 不一致, 0 写法不统一.
- The 2 不一致 are E4b-all-L40 in report §1 (zh + en). The checker still selects the superseded full-sample-standardisation file (+0.066); the user's decision 1 is the trainstd value 0.061, so the checker's selector needs updating.
- Occurrences dropped from 1,267 to 1,237: some claim patterns only match the old short forms (see the unify summary notes).
- Conclusions without data: 7 left, all heading sentences or non-conclusions.

---------------------------------------------------------------------------------------------------------
# 2026-11-07 ~02:20 decisions D, B, E, F (local only)
Scripts: `sync_20261107/apply_20261107c.py` (D, B, F2–F4; backups `*.before_20261107b.*`, report `*.before_20261107c.html`), `apply_20261107d.py` (F16 tag 2,001), `deck_slide65_img_20261107b.py`,
`methods/edit_20261107b.py` (K + build), `stage1_11/src/hyp_table_png_v29.py` / `hyp_table_png_v29_en.py`, `talk/src/export/deck_v20b_new_20261107.py`, `patch_editable_v20b_20261107b.py`, `pptx_text_fix_20261107b.py`,
`export_deck_v20d_split3.py` + `export_v20d_full.sbatch` (job 11696989 COMPLETED), `sync_20261107/export_pdfs_20261107b.py`. B wording and its numbers: `sync_20261107/B_text_20261107.json` (recomputed from perdonor_by_run_layer.csv, Vpd).
- D: report §1 en and deck slide 50 "99.6% from L52"; keys & shelves zh/en L48 0.82 (user decision; the check lists 0.82 vs canonical 0.825 as 写法不统一).
- B: written (report #alltok-results text + box + #pd-b1-e4b5, handbook F + K, deck slide 72 + note, advisor, process report, scoring audit, methods addendum, talk docs progress report + Stage 13 script zh/en, README b en). Old "这一差别主要来自首字母和名" deleted (report, handbook F, note 72).
- E: deck v20d lossless, three parts each, all ≤ 15 MB: slides part1of3_p1-27 9.1 MB, part2of3_p28-55 11.8 MB, part3of3_p56-82 7.7 MB; with_notes_zh 10.4 / 13.1 / 9.1 MB. Editable pptx `Stage1-13_deck_v20d_editable.pptx` (+ b64).
- F1 NOT written: the ':' "question share" (question-change ÷ paper-change relative distance, 381_stage13/reports/x1_similarity.md colon table, 9,108 papers, mean over 3 question pairs) is 4.7 (L4), 4.9 (L8), 4.1 (L16), 3.8 (L24), 3.8 (L28), 3.7 (L32), 3.3 (L36), 3.0 (L40), 2.9 (L44), 2.2 (L48), 1.8 (L52), 1.3–1.5 (L56–L63): "3–5×" holds only at L4–L40.
- F2–F4 done: report table H3 cell + header "目前结果（第 29 版，2026-11-07）", handbook F H3 summary, deck slide 65 subtitle/caption/image. New images `downloads/Stage13_hypotheses_table_v29_tableonly.png` (zh), `…_v29_en_{tableonly,slide,wide}.png`; slide PNG `talk/src/export/shots/v20b/s65_en_table_v2.png`. X2 all-author numbers verified: R_auth 0.0323, old 0.0157, R_full 0.4566, share 7.1% (summary_b1_xall/x2_verdict_new__all.csv), R² max 0.0092 (fit_authall_sanity.csv).
- Exports (previous kept): report `Stage1-13_report_v29d_A4.pdf`; handbook `…A4.v20261107b.pdf`; talk docs keys & shelves, Stage 13 script, progress report `_20261107b_A4.pdf`; advisor `jlens_progress_report_2026-11-07b_A4.pdf`; process report `…2026-11-07b_A4.pdf`; scoring audit `scoring_audit_2026-11-07b_A4.pdf`; methods addendum `methods_addendum_2026-11-07b_A4.pdf`.
- Screenshots: `sync_20261107/shots_b/` (report alltok t−c, report hypothesis table, handbook alltok, keys & shelves 0.82), `talk/src/export/shots/v20d/` (s50, s65, s72).
- Strict check: v2 1,383 一致 / 3 写法不统一; v3 (`numcheck/claims/claims_defs_v3.py`, + B, F3, F2, D claims; all of them 一致) 1,514 一致 / 3 写法不统一. Remaining: E1-L48 keys & shelves 0.82 (user decision D); F16-U0-n "n = 2001" in the summary-table cell of report #pd-groups and handbook #k-groups (table mirrors 391_groups/summary_table.md, no thousands separator in any row; left unchanged, user to decide).

---------------------------------------------------------------------------------------------------------
# FINAL (2026-11-07 ~03:15, after the user's approval ~03:00) — local only, nothing published, nothing pushed

Last edits:
- `sync_20261107/apply_20261107e.py`: H1 result cell in the report table. Backups `*.before_20261107c.*`, report `.before_20261107e.html`.
- The colon-ratio numbers were recomputed from `381_stage13/summary_m3/x1_similarity.csv` (= x1_similarity.md colon table): L4–L40 3.0–4.9, L48 2.2, L56–L63 1.3–1.5. Saved in `sync_20261107/H1_numbers_20261107.json`.
- U0 "n = 2,001" in the report; handbook K regenerated by `methods/edit_20261107c.py`.
- Images: `hyp_table_png_v29.py` (zh, source tags hidden in the image) and `hyp_table_png_v29_en.py`; deck slide 65 re-embedded.
- pptx v20e built by `patch_editable_v20b_20261107b.py` + `pptx_text_fix_20261107b.py`. Deck PDFs by `export_v20e_full.sbatch` (job 11697187, COMPLETED). Evidence PDF by `make_keys_shelves_evidence_v20e.py`. Other PDFs by `sync_20261107/export_pdfs_20261107c.py`.
- Slide PNG: `talk/src/export/shots/v20b/s65_en_table_v3.png`. Other screenshots in `sync_20261107/shots_c/`.

Every unqualified colon "3–5×" now has the layer range: talk docs experiment_walkthrough_methods_zh, experiment_walkthrough_zh, keys_and_shelves zh + en, progress_report_for_advisor, stage13_script zh + en; report X1 sentence (L56–L63 part added) and report table H1 cell. None found in: deck HTML, notes, pptx text, handbook, advisor, process report, audit, addendum, README b, plan. The evidence PDF's slide pages carry no such text; its tables are v29.

Strict check:
- v4 (`numcheck/claims/claims_defs_v4.py`: + H1 claims; keys & shelves 0.82 as its own claim "用户决定 D（源 0.825 两位小数为 0.82）"): 1,566 occurrences, all 一致.
- The checker has no custom-status mechanism, so the D label appears in the statement column with status 一致.
- v3 for comparison: 1,517 一致 / 1 写法不统一 (the 0.82).

## Local HTML files to publish (path → artifact)
| Document | Local file | Artifact |
|---|---|---|
| Report v29 | 351_stage10/reports/stage1_11/stage1_11_report.html | https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe |
| Deck v20 (82 slides) | 351_stage10/reports/merged_deck/stage1_11_deck.html | https://claude.ai/artifact/XcgK4YF2dYQxudWfhk8MsD |
| Methods handbook | 351_stage10/reports/methods/methods_handbook.html | https://claude.ai/artifact/W7r7xVte3eaNcbo8D8cybo |
| Advisor progress report (merged, current) | 351_stage10/reports/advisor/index.html (+ x5_layer_order.png) | https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs |
| Process report | 351_stage10/reports/process_report/index.html (+ style.css) | https://claude.ai/artifact/TmqEtZg3gHTz7p7vCkaiB4 |
| Scoring audit | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | https://claude.ai/artifact/C6UVJDUtg4JJmkaKBrnwd7 |
| Methods addendum | 351_stage10/reports/pages_20261106b/methods_addendum/index.html | https://claude.ai/artifact/VkyyqsvE43k2BkU6VSZ2kg |
| Talk doc: experiment walkthrough | 351_stage10/reports/talk_docs/experiment_walkthrough_zh.html | https://claude.ai/artifact/RBLSRBo4YcL1gAKi8gpp4m |
| Talk doc: walkthrough (methods) | …/talk_docs/experiment_walkthrough_methods_zh.html | https://claude.ai/artifact/RX4KpcC5xGu7ynM6AzYSTz |
| Talk doc: keys and shelves | …/talk_docs/keys_and_shelves_script_zh_en.html | https://claude.ai/artifact/UfKPpZNLicWhFDZbwTevAm |
| Talk doc: Stage 13 script | …/talk_docs/stage13_script_zh_en.html | https://claude.ai/artifact/KC2kW4NmjD41couEghy365 |
| Talk doc: handbook guide | …/talk_docs/methods_handbook_guide_plain_zh.html | https://claude.ai/artifact/WUk8MdPwVhfzJmyopp6JBs |
| Talk doc: progress report (SUPERSEDED) | …/talk_docs/progress_report_for_advisor_zh.html | https://claude.ai/artifact/8XcY8CRpz3AAjfDE4n6V6e |
| Downloads page | 351_stage10/reports/downloads/index.html (NOT edited; = live 1793918868-98f1; rows below) | https://claude.ai/artifact/5Tdt1mQa8xnPiqQEKvjzta |

Not pages: README `github/README_draft_20261106b.md` (repo, push by main session); plan `plan/plan_master_queue_20261106b.{md,html}`.

Superseded page banner (top of 8XcY8CRpz3AAjfDE4n6V6e, red box): "本页已过时，最新内容见 https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs". No other page is superseded.

## New download files for the downloads page (final versions; earlier local intermediates of today — v29c/v29d, v20c/v20d, 20261107/20261107b talk docs — are not for the page)
| File | Pages | MB |
|---|---|---|
| Stage1-13_report_v29e_A4.pdf | 115 | 11.8 |
| Stage1-13_deck_v20e_slides_part1of3_p1-27.pdf | 27 | 9.1 |
| Stage1-13_deck_v20e_slides_part2of3_p28-55.pdf | 28 | 11.8 |
| Stage1-13_deck_v20e_slides_part3of3_p56-82.pdf | 27 | 7.7 |
| Stage1-13_deck_v20e_with_notes_zh_part1of3_p1-27.pdf | 27 | 10.4 |
| Stage1-13_deck_v20e_with_notes_zh_part2of3_p28-55.pdf | 28 | 13.1 |
| Stage1-13_deck_v20e_with_notes_zh_part3of3_p56-82.pdf | 27 | 9.1 |
| Stage1-13_deck_v20e_editable.pptx (+ .b64.txt 6.4 MB) | 82 slides | 4.8 |
| Stage1-13_methods_handbook_A4.v20261107c.pdf | 215 | 10.3 |
| keys_and_shelves_evidence_v20e.pdf (15 slides + 3 English tables, landscape) | 18 | 11.3 |
| jlens_progress_report_2026-11-07b_A4.pdf (merged advisor page) | 10 | 3.0 |
| jlens_process_report_2026-11-07b_A4.pdf | 28 | 2.8 |
| scoring_audit_2026-11-07b_A4.pdf | 33 | 1.5 |
| methods_addendum_2026-11-07b_A4.pdf | 20 | 3.2 |
| talkdoc_experiment_walkthrough_zh_20261107c_A4.pdf | 5 | 0.4 |
| talkdoc_experiment_walkthrough_methods_zh_20261107c_A4.pdf | 10 | 0.8 |
| talkdoc_keys_and_shelves_script_zh_en_20261107c_A4.pdf | 6 | 0.4 |
| talkdoc_stage13_script_zh_en_20261107c_A4.pdf | 6 | 0.3 |
| talkdoc_progress_report_for_advisor_zh_20261107c_A4.pdf (superseded, with banner) | 7 | 0.7 |
| talkdoc_methods_handbook_guide_plain_zh_20261107_A4.pdf (unchanged since the first 11-07 round) | 12 | 0.8 |
| plan_master_queue_20261106b_A4.pdf | 5 | 0.1 |
| Stage13_hypotheses_table_v29_tableonly.png (zh) | — | 0.3 |
| Stage13_hypotheses_table_v29_en_{tableonly,slide,wide}.png | — | 0.3–0.4 |

Every file is ≤ 15 MB. Keep the previous version of each category as 上一版 (report v28 / deck v19 / handbook 20261105c on the live page).
