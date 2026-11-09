"""Write 351_stage10/reports/sync_20261108a_manifest.md from apply_log_20261108a.json + the later scripts (h, i, j, k, l) + export list."""
import json, re, os, glob
import fitz
R = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
L = json.load(open(R + 'sync_20261107/apply_log_20261108a.json'))
out = ['# Sync 2026-11-08 a (round e) — change manifest (user approved 2026-11-08; local only, NOT published, NOT pushed)', '',
       'Sources:',
       '- `~/jlens_work/for_user_2026-11-07.md` §f (wording B version 3, verbatim); every number re-checked against `381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv` (V0 / Vpd / V5x0, tc / tc_lo / tc_hi) by assertion in the script;',
       '- `381_stage13/c13_C2_followup/c2_followup_proxy.csv` (aa_all int6 rq1_team_lo 0.108476).',
       'Scripts:',
       '- `sync_20261107/apply_20261108a.py`: reads the CURRENT files; fresh backups `*.before_20261108a.*` are made from them and never used as input; log in `sync_20261107/apply_log_20261108a.json`.',
       '- `methods/edit_20261107d.py`: handbook K regenerated + build. `process_report/build_process_report.py`.',
       '- pptx: patch_editable_v20b_20261107b.py → pptx_text_fix_20261107b.py → pptx_text_fix_20261107d.py → pptx_text_fix_20261108a.py.',
       '- Deck PDFs: `talk/src/export/export_v20g_full.sbatch` (job 11721868, COMPLETED). Other PDFs: `sync_20261107/export_pdfs_20261108a.py`.', '',
       '## Changes (rule · file · before → after · count)', '', '| # | rule | file / note | before | after | count |', '|---|---|---|---|---|---|']
for i, (why, f, a, b, c) in enumerate(L, 1):
    a = re.sub(r'\s+', ' ', str(a)); b = re.sub(r'\s+', ' ', str(b))
    a = (a[:160] + '…') if len(a) > 160 else a; b = (b[:220] + '…') if len(b) > 220 else b
    out.append(f'| {i} | {why} | {f} | {a.replace("|", "/")} | {b.replace("|", "/")} | {c} |')
out += ['', '## Notes',
        '- Wording B v3 is written in full (zh) in: report #alltok-results text, #alltok-results batch-1 box, #pd-b1-e4b5 (→ handbook K), handbook F #s13-alltok, deck note 72, advisor, scoring audit and methods addendum update boxes, process report §0, talk docs progress_report_for_advisor_zh and stage13_script_zh_en.',
        '- In English (full, faithful translation) in README b and the Stage 13 script.',
        '- Deck slide 72 carries a compact English version (layout); the full text is in note 72. The same compact text is in the pptx.',
        '- README b vs plan: README b now has v3 (en); `plan_master_queue_20261106b.md` / `20261107.md` contain only item titles and statuses, no wording-B sentence, so nothing needed reconciling.',
        '- Item titles: "减 5 个假标题(平均)" kept. The first occurrence per document got "（实际每篇可用假标题个数见正文）": report, advisor, process report, scoring audit, methods addendum, handbook (part B, the first part that contains it).',
        '- The deck, README and talk docs no longer contain the item title (the English note "actual usable false titles per paper: see text" was not needed).',
        '- Version labels (item 2): the addendum-9 numbers (+0.071 / +0.044 / +0.124 …) now say "预注册版 V0：只减 false_0，目标 + 对照 1,395 篇" in 6 talk docs, deck slide 24/72 caveat (en), README table and scoring audit.',
        '- Vpd numbers (+0.076, +0.033, +0.066) were already labelled "逐个假标题排除版（4,654 篇…）" in round d; C-3 / C-3b numbers are labelled C-3 / C-3b with 6,841 papers; V5x0 +0.072 / +0.024 appear only inside the v3 text (labelled ③). No wrong number found.',
        '- RQ1 lower bound 0.109 → 0.108 in report #p1-s8, deck slide 19 (HTML + pptx), note 19, handbook #s19-s8d.',
        '- Oral-correction item 8: for_user file only, nothing to do.', '',
        '## Strict check after the round',
        '- `CLAIMS_DEFS=claims_defs_v7`: 592 claims, 3,200 occurrences, all 一致.', '',
        '## Exports (downloads/, previous kept)', '| file | pages | MB |', '|---|---|---|']
D = R + 'downloads/'
fs = ['Stage1-13_report_v29g_A4.pdf', 'Stage1-13_methods_handbook_A4.v20261108a.pdf'] + sorted(os.path.basename(x) for x in glob.glob(D + 'Stage1-13_deck_v20g_*')) + \
     sorted(os.path.basename(x) for x in glob.glob(D + '*20261108a_A4.pdf') + glob.glob(D + '*2026-11-08a_A4.pdf'))
for f in fs:
    n = len(fitz.open(D + f)) if f.endswith('.pdf') else ''
    out.append(f'| {f} | {n} | {os.path.getsize(D + f) / 1e6:.1f} |')
out += ['', 'Screenshots checked:',
        '- `sync_20261107/shots_e/` (report #alltok-results v3 paragraph, #pd-b1-e4b5, Stage 8 C-2 box; handbook #s13-alltok; advisor box);',
        '- `talk/src/export/shots/v20g/` (deck slides 19, 24, 72).', '',
        'Local HTML files to publish: same paths and artifacts as in `sync_20261107_manifest.md`, FINAL section.']
open(R + 'sync_20261108a_manifest.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n'); print('rows', len(L))
