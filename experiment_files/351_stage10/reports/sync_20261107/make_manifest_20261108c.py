"""Write sync_20261108c_manifest.md from sync_20261107/apply_log_20261108c.json (apply_20261108c.py + _part2.py)."""
import json, collections
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports')
L = json.loads((R / 'sync_20261107/apply_log_20261108c.json').read_text(encoding='utf-8'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ⏎ ')
per = collections.Counter()
for w, f, o, n, c in L: per[f.split(' #')[0]] += c
out = ['# Sync 2026-11-08 c — change manifest (report v30, deck v21, handbook 2026-11-08 c; LOCAL only, NOT published, NOT pushed)', '',
       'Source of truth: `~/jlens_work/conclusions_v30_draft.md` (C01–C23, L01–L14, §六) and `conclusions_v30_checks.md`. User-confirmed: D13-1 (for_user_2026-11-07.md §a), R1 = C04, R4 = C08 (review_queue.md "已确认", PROGRESS 2026-11-08). Other changes are downgrades / premises / limitations / status (HANDOFF autonomous sync mode).', '',
       'Scripts: `sync_20261107/apply_20261108c.py` (main; asserts every number against 391_groups/summary_b1_p12f/*.csv and reports/b2_cd_report.md, b1_p12f_report.md), `sync_20261107/apply_20261108c_part2.py` (remaining status notes). Fresh backups `*.before_20261108c` (asserted not to exist before). Log: `sync_20261107/apply_log_20261108c.json`.',
       'Rebuilt (not edited by hand): `methods/methods_handbook.html` = build_methods.py(parts) — part K regenerated from the report (edit_20261107d.py conversion, lead "第 30 版"); `process_report/index.html` = build_process_report.py(draft_zh.md); `talk/src/export/with_notes.html` is rewritten by the deck export from notes_zh.json (here only the D13-1 passage was re-inserted).',
       'D13-1: all 16 held passages re-inserted verbatim (anchors from `*.before_20261108b`): report ×4, notes ×1, with_notes ×1, parts B/G/C ×3 directly; handbook entries 6–10 and K entries 12–13 via the rebuild (checked by assertion after the build).', '',
       '## Changes per file (count)', '', '| file | changes |', '|---|---|']
out += [f'| {f} | {c} |' for f, c in sorted(per.items())]
out += ['', '## All changes (rule · file · before → after · count)', '', '| # | rule | file | before | after | count |', '|---|---|---|---|---|---|']
out += [f'| {i} | {cut(w, 60)} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {c} |' for i, (w, f, o, n, c) in enumerate(L, 1)]
(R / 'sync_20261108c_manifest.md').write_text('\n'.join(out) + '\n', encoding='utf-8'); print('manifest rows', len(L))
