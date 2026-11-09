# Sync 2026-11-08 a (round e) — change manifest (user approved 2026-11-08; local only, NOT published, NOT pushed)

Sources:
- `~/jlens_work/for_user_2026-11-07.md` §f (wording B version 3, verbatim); every number re-checked against `381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv` (V0 / Vpd / V5x0, tc / tc_lo / tc_hi) by assertion in the script;
- `381_stage13/c13_C2_followup/c2_followup_proxy.csv` (aa_all int6 rq1_team_lo 0.108476).
Scripts:
- `sync_20261107/apply_20261108a.py`: reads the CURRENT files; fresh backups `*.before_20261108a.*` are made from them and never used as input; log in `sync_20261107/apply_log_20261108a.json`.
- `methods/edit_20261107d.py`: handbook K regenerated + build. `process_report/build_process_report.py`.
- pptx: patch_editable_v20b_20261107b.py → pptx_text_fix_20261107b.py → pptx_text_fix_20261107d.py → pptx_text_fix_20261108a.py.
- Deck PDFs: `talk/src/export/export_v20g_full.sbatch` (job 11721868, COMPLETED). Other PDFs: `sync_20261107/export_pdfs_20261108a.py`.

## Changes (rule · file · before → after · count)

| # | rule | file / note | before | after | count |
|---|---|---|---|---|---|
| 1 | 1 wording B v3 (report ×3) | stage1_11/stage1_11_report.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 3 |
| 2 | 1 wording B v3 (talk docs) | talk_docs/progress_report_for_advisor_zh.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 3 | 1 wording B v3 (talk docs) | talk_docs/stage13_script_zh_en.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 4 | 1 wording B v3 (handbook F) | methods/parts/F_stage13.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 5 | 1 wording B v3 (update boxes) | advisor/index.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 6 | 1 wording B v3 (update boxes) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 7 | 1 wording B v3 (update boxes) | pages_20261106b/methods_addendum/index.html | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 8 | 1 wording B v3 (process report) | process_report/draft_zh.md | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 9 | 1 wording B v3 (deck note 72) | notes_zh.json #72 | (regex) (?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.0… | (computed) | 1 |
| 10 | 1 wording B v3 (en: README b, Stage 13 script) | github/README_draft_20261106b.md | target − control positive from L16 for the given-name first token and from L24 for the surname (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 … | Title-position probe target − control (within citation bin) has three versions: ① pre-registered (false_0 only; false_0 is the only false title checked for title reuse, a clean single control; given name 1,706, surname 1… | 1 |
| 11 | 1 wording B v3 (en: README b, Stage 13 script) | talk_docs/stage13_script_zh_en.html | target − control positive from L16 for the given-name first token and from L24 for the surname (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 … | Title-position probe target − control (within citation bin) has three versions: ① pre-registered (false_0 only; false_0 is the only false title checked for title reuse, a clean single control; given name 1,706, surname 1… | 1 |
| 12 | 1 wording B v3 (deck slide 72, compact en; full text in note 72) | merged_deck/stage1_11_deck.html | <li><b>Target − control (five false titles, per-donor exclusion): </b>given-name first token positive from L16, surname from L24 (L40 +0.030 [0.013, 0.048]); in… | <li><b>Target − control, three versions: </b>pre-registered (false_0; 1,706 / 1,395 papers): given name + at L24–L48, surname n.s. (L40 +0.012 [−0.026, +0.048]); per-donor (post hoc, D1; 4,654 papers): surname + from L24… | 1 |
| 13 | 1 item-title note (first occurrence) | stage1_11/stage1_11_report.html | 减 5 个假标题平均 | 减 5 个假标题平均（实际每篇可用假标题个数见正文） | 1 |
| 14 | 1 item-title note (first occurrence) | advisor/index.html | 减 5 个假标题 | 减 5 个假标题（实际每篇可用假标题个数见正文） | 1 |
| 15 | 1 item-title note (first occurrence) | process_report/draft_zh.md | 减 5 个假标题 | 减 5 个假标题（实际每篇可用假标题个数见正文） | 1 |
| 16 | 1 item-title note (first occurrence) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | 减 5 个假标题 | 减 5 个假标题（实际每篇可用假标题个数见正文） | 1 |
| 17 | 1 item-title note (first occurrence) | pages_20261106b/methods_addendum/index.html | 减 5 个假标题 | 减 5 个假标题（实际每篇可用假标题个数见正文） | 1 |
| 18 | 1 item-title note (first occurrence) | methods/parts/B_global2.html | 减 5 个假标题 | 减 5 个假标题（实际每篇可用假标题个数见正文） | 1 |
| 19 | 2 V0 label (addendum-9 sentence) | talk_docs/experiment_walkthrough_methods_zh.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 20 | 2 V0 label (addendum-9 sentence) | talk_docs/experiment_walkthrough_zh.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 21 | 2 V0 label (addendum-9 sentence) | talk_docs/keys_and_shelves_script_zh_en.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 22 | 2 V0 label (addendum-9 sentence) | talk_docs/methods_handbook_guide_plain_zh.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 23 | 2 V0 label (addendum-9 sentence) | talk_docs/progress_report_for_advisor_zh.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 24 | 2 V0 label (addendum-9 sentence) | talk_docs/stage13_script_zh_en.html | （目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | （预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md） | 1 |
| 25 | 2 V0 label (en) | merged_deck/stage1_11_deck.html | (1,395 papers; e4b_alltok.md) | (pre-registered V0: false_0 only, 1,395 papers; e4b_alltok.md) | 1 |
| 26 | 2 V0 label (en) | talk_docs/stage13_script_zh_en.html | (1,395 papers; e4b_alltok.md) | (pre-registered V0: false_0 only, 1,395 papers; e4b_alltok.md) | 1 |
| 27 | 2 V0 label (README table) | github/README_draft_20261106b.md | surname first token L40 +0.071 [0.058, 0.085] / | surname first token L40 +0.071 [0.058, 0.085] (pre-registered V0, false_0 only, 1,395 papers) / | 1 |
| 28 | 2 V0 label (audit) | /scratch/zhang.zhiqi2/jlens/audit_20261105/scoring_audit.html | Addendum 9 shows surname_first L40 +0.071 and given_first +0.124 | Addendum 9 (pre-registered version V0, false_0 only; 1,395 / 1,706 papers) shows surname_first L40 +0.071 and given_first +0.124 | 1 |
| 29 | 3 RQ1 lower bound (report #p1-s8, deck slide 19 + note, handbook #s19-s8d) | stage1_11/stage1_11_report.html | +0.130 [0.109, 0.153] | +0.130 [0.108, 0.153] | 1 |
| 30 | 3 RQ1 lower bound (report #p1-s8, deck slide 19 + note, handbook #s19-s8d) | merged_deck/stage1_11_deck.html | +0.130 [0.109, 0.153] | +0.130 [0.108, 0.153] | 1 |
| 31 | 3 RQ1 lower bound (report #p1-s8, deck slide 19 + note, handbook #s19-s8d) | methods/parts/C_stage1_9.html | +0.130 [0.109, 0.153] | +0.130 [0.108, 0.153] | 1 |
| 32 | 3 RQ1 lower bound (report #p1-s8, deck slide 19 + note, handbook #s19-s8d) | notes_zh.json #19 | +0.130 [0.109, 0.153] | +0.130 [0.108, 0.153] | 1 |

## Notes
- Wording B v3 is written in full (zh) in: report #alltok-results text, #alltok-results batch-1 box, #pd-b1-e4b5 (→ handbook K), handbook F #s13-alltok, deck note 72, advisor, scoring audit and methods addendum update boxes, process report §0, talk docs progress_report_for_advisor_zh and stage13_script_zh_en.
- In English (full, faithful translation) in README b and the Stage 13 script.
- Deck slide 72 carries a compact English version (layout); the full text is in note 72. The same compact text is in the pptx.
- README b vs plan: README b now has v3 (en); `plan_master_queue_20261106b.md` / `20261107.md` contain only item titles and statuses, no wording-B sentence, so nothing needed reconciling.
- Item titles: "减 5 个假标题(平均)" kept. The first occurrence per document got "（实际每篇可用假标题个数见正文）": report, advisor, process report, scoring audit, methods addendum, handbook (part B, the first part that contains it).
- The deck, README and talk docs no longer contain the item title (the English note "actual usable false titles per paper: see text" was not needed).
- Version labels (item 2): the addendum-9 numbers (+0.071 / +0.044 / +0.124 …) now say "预注册版 V0：只减 false_0，目标 + 对照 1,395 篇" in 6 talk docs, deck slide 24/72 caveat (en), README table and scoring audit.
- Vpd numbers (+0.076, +0.033, +0.066) were already labelled "逐个假标题排除版（4,654 篇…）" in round d; C-3 / C-3b numbers are labelled C-3 / C-3b with 6,841 papers; V5x0 +0.072 / +0.024 appear only inside the v3 text (labelled ③). No wrong number found.
- RQ1 lower bound 0.109 → 0.108 in report #p1-s8, deck slide 19 (HTML + pptx), note 19, handbook #s19-s8d.
- Oral-correction item 8: for_user file only, nothing to do.

## Strict check after the round
- `CLAIMS_DEFS=claims_defs_v7`: 592 claims, 3,200 occurrences, all 一致.

## Exports (downloads/, previous kept)
| file | pages | MB |
|---|---|---|
| Stage1-13_report_v29g_A4.pdf | 116 | 11.8 |
| Stage1-13_methods_handbook_A4.v20261108a.pdf | 219 | 10.4 |
| Stage1-13_deck_v20g_editable.pptx |  | 4.8 |
| Stage1-13_deck_v20g_editable.pptx.b64.txt |  | 6.4 |
| Stage1-13_deck_v20g_slides_part1of3_p1-27.pdf | 27 | 9.1 |
| Stage1-13_deck_v20g_slides_part2of3_p28-55.pdf | 28 | 11.8 |
| Stage1-13_deck_v20g_slides_part3of3_p56-82.pdf | 27 | 7.7 |
| Stage1-13_deck_v20g_with_notes_zh_part1of3_p1-27.pdf | 27 | 10.4 |
| Stage1-13_deck_v20g_with_notes_zh_part2of3_p28-55.pdf | 28 | 13.1 |
| Stage1-13_deck_v20g_with_notes_zh_part3of3_p56-82.pdf | 27 | 9.2 |
| jlens_process_report_2026-11-08a_A4.pdf | 28 | 2.9 |
| jlens_progress_report_2026-11-08a_A4.pdf | 11 | 3.0 |
| methods_addendum_2026-11-08a_A4.pdf | 21 | 3.3 |
| scoring_audit_2026-11-08a_A4.pdf | 34 | 1.5 |
| talkdoc_experiment_walkthrough_methods_zh_20261108a_A4.pdf | 10 | 0.8 |
| talkdoc_experiment_walkthrough_zh_20261108a_A4.pdf | 5 | 0.4 |
| talkdoc_keys_and_shelves_script_zh_en_20261108a_A4.pdf | 6 | 0.4 |
| talkdoc_methods_handbook_guide_plain_zh_20261108a_A4.pdf | 12 | 0.8 |
| talkdoc_progress_report_for_advisor_zh_20261108a_A4.pdf | 7 | 0.8 |
| talkdoc_stage13_script_zh_en_20261108a_A4.pdf | 7 | 0.3 |

Screenshots checked:
- `sync_20261107/shots_e/` (report #alltok-results v3 paragraph, #pd-b1-e4b5, Stage 8 C-2 box; handbook #s13-alltok; advisor box);
- `talk/src/export/shots/v20g/` (deck slides 19, 24, 72).

Local HTML files to publish: same paths and artifacts as in `sync_20261107_manifest.md`, FINAL section.
