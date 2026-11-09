"""Write 351_stage10/reports/sync_20261107d_manifest.md from apply_log_20261107g.json + the later scripts (h, i, j, k, l) + export list."""
import json, re, os, glob
import fitz
R = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
L = json.load(open(R + 'sync_20261107/apply_log_20261107g.json'))
out = ['# Sync 2026-11-07 d — change manifest (round approved ~21:00; local only, NOT published, NOT pushed)', '',
       'Sources: `~/jlens_work/for_user_2026-11-07.md` §a (D13-1, revised ~22:00), §b (X4, E4b scheme 2), §c, §e; `numcheck/claims/out_20261107_183155/` (v6_all_non_ok.csv, v5_definition_issues.csv).',
       'Scripts in `351_stage10/reports/sync_20261107/`:',
       '- `apply_20261107g.py`: main round. Backups `*.before_20261107d.*`; full log in `apply_log_20261107g.json`.',
       '- `apply_20261107h.py`: two prose leftovers.',
       '- `apply_20261107i.py`: D13-1 rewording (user change ~22:00). Backups `*.before_20261107i.*`.',
       '- `apply_20261107j.py`: double full stop after the X4 sentence.',
       '- `apply_20261107k.py`: REPAIR, see below.',
       '- `apply_20261107l.py`: handbook D correction note.',
       '- `export_pdfs_20261107d.py`, `export_pdfs_20261107d2.py`: PDFs.',
       'Other scripts:',
       '- `methods/edit_20261107d.py`: handbook part K regenerated + build.',
       '- `talk/src/export/pptx_text_fix_20261107d.py`: pptx text fixes.',
       '- `talk/src/export/export_v20f_full.sbatch`: deck PDFs, job 11716762, COMPLETED.', '',
       '**Repair note:** `apply_20261107g.py` took the report from `stage1_11_report.before_20261107d.html`, a backup name already used at ~02:50, so its input was a pre-03:00 state. The report therefore lost the 03:00 edits: the U0 tag 2,001, the H1 cell and the X1 late-layer qualifier. `apply_20261107k.py` re-applied exactly those edits on the current report, and the handbook was rebuilt. The strict check below runs on the repaired files.', '',
       '## Changes (rule · file · before → after · count)', '', '| # | rule (why) | file / note | before | after | count |', '|---|---|---|---|---|---|']
for i, (why, f, a, b, c) in enumerate(L, 1):
    a = re.sub(r'\s+', ' ', str(a)); b = re.sub(r'\s+', ' ', str(b))
    a = (a[:160] + '…') if len(a) > 160 else a; b = (b[:220] + '…') if len(b) > 220 else b
    out.append(f'| {i} | {why} | {f} | {a.replace("|", "/")} | {b.replace("|", "/")} | {c} |')
out += ['', 'Later edits (not in the log above):',
        '- `apply_20261107h.py`: report #ov "…E4b 减 5 个假标题平均也已完成" → "…E4b 逐个假标题排除版（补充 10 第 4 项）也已完成"; progress talk doc "减 5 个假标题平均的版本（2026-11-06 完成）" → "逐个假标题排除的版本（补充 10 第 4 项，2026-11-06 完成）".',
        '- `apply_20261107i.py`, D13-1 in its final wording (for_user §a lines 9–12):',
        '  - Report Stage 8 box rebuilt. "因此，不一致只出现在后改的 L56 上；在原定的主终点上，代理结果不要求重算。" is deleted.',
        '  - Added: the rule triggers when RQ1 or RQ2 changes, and this trigger came only from L56; report v29 / PPT v20 treat the 7-layer integral as the frozen primary endpoint (#p1-s8, PPT slide 17); L56 was an exploratory secondary that the 21:14 PROTOCOL.md promoted (U28); the 7-layer proxy is an approximation (Stage 10 has no L16); Stage 10 has exactly 5 false titles per paper (351_stage10.py lines 302, 863).',
        '  - Report Part 5 "不做" line, handbook V59 and the B deviation-list row aligned to the same wording.',
        '  - Numbers come from c2_followup_proxy.csv (aa_all). The 7-layer L16 = L24 RQ2 lower bound is 0.0055 in the CSV, so the documents write +0.005; the for_user text says +0.006.',
        '- `apply_20261107j.py`: "拆分。。" → "拆分。" (report X4 sentence).',
        '- `apply_20261107k.py`: re-applied U0 "n = 2,001" (tag and table), the H1 hypothesis-table cell and the X1 late-layer qualifier in the report.',
        '- `apply_20261107l.py`: handbook D correction note no longer quotes the superseded 0.0075.',
        '- pptx `Stage1-13_deck_v20f_editable.pptx`: slides 17, 24, 30, 67, 70, 72, 81 fixed at run level (all rules hit).', '',
        '## 等用户定措辞 (held, unchanged)',
        'Wording B, "按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 +0.030 [0.013, 0.048]）…", and its English and deck forms. The new audit gives the true 5-title average (V5x0, 1,395 papers) surname L40 = +0.024 [−0.006, +0.052], not significant. Locations:',
        '- report: #alltok-results text, the batch-1 item-4 box in #alltok-results, #pd-b1-e4b5 (→ handbook K #k-b1-e4b5);',
        '- handbook F #s13-alltok;',
        '- deck note 72; deck slide 72 bullet "Target − control (five false titles, per-donor exclusion)" (HTML + pptx);',
        '- advisor update box; methods addendum update box; scoring audit update box; process report §0;',
        '- talk docs: progress_report_for_advisor_zh, stage13_script_zh_en (zh + en);',
        '- README draft b (en).', '',
        '## Not applied / for the user',
        '- Item names that quote the pre-registered item title "E4b 与全部 token probe 减 5 个假标题平均" are left as item names: report Part 5 heading, box titles, handbook V58/B rows, and the plan 20261107 row "4 E4b and all-token probe minus five false titles".',
        '- `plan_master_queue_20261107.md` already had 187/194 and 3-3 stopped. None of the round-d rules matched it, so it is unchanged.',
        '- Deck slide 81 "Not done" line does not name D13-1. It was left unchanged for layout; deck note 82 carries the D13-1 limitation.',
        '- Hypothesis-table images: no number changed, so they were not touched.',
        '- Evidence PDF: none of its slides changed this round, so it was not re-exported.', '',
        '## Strict check after the round',
        '- `CLAIMS_DEFS=claims_defs_v6` (out_20261107_184952): 516 claims, 2,910 occurrences, all 一致.',
        '- `claims_v5_post.py`: v6_all_non_ok = 0.',
        '- v5_definition_issues still lists 34 rows. That list is static per claim (issue texts in the defs); each place now carries the fix in its text (1,395 / X1-pipeline labels, X4 test value, N2 definition note). The defs owner should mark them resolved.', '',
        '## Exports (downloads/, previous kept)', '| file | pages | MB |', '|---|---|---|']
D = R + 'downloads/'
fs = ['Stage1-13_report_v29f_A4.pdf', 'Stage1-13_methods_handbook_A4.v20261107d.pdf'] + sorted(os.path.basename(x) for x in glob.glob(D + 'Stage1-13_deck_v20f_*')) + \
     sorted(os.path.basename(x) for x in glob.glob(D + '*20261107d_A4.pdf') + glob.glob(D + '*2026-11-07d_A4.pdf'))
for f in fs:
    n = len(fitz.open(D + f)) if f.endswith('.pdf') else ''
    out.append(f'| {f} | {n} | {os.path.getsize(D + f) / 1e6:.1f} |')
out += ['', 'Screenshots checked:',
        '- `sync_20261107/shots_d/` (report D13-1 box, #pd-running, #pd-limits, X4 sentence, §6.11; handbook V59; advisor limitations);',
        '- `talk/src/export/shots/v20f/` (deck slides 17, 24, 30, 67, 70, 72, 81).', '',
        'Local HTML files to publish: same paths and artifacts as in `sync_20261107_manifest.md`, FINAL section.']
open(R + 'sync_20261107d_manifest.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n'); print('rows', len(L))
