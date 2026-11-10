"""Round h, part 2: (a) fix a chained replacement in apply_20261109h.py: the X2 clause became
'单看 X2，单看 X2，H3 证据仍不足（…）（…）' where the original said 'H3 仍证据不足' -> collapse to one clause; (b) note 81 overflowed (969 px, job 11763628): short X2 clause there.
Same backups as round h (*.before_20261109h2 = pre-round-h state). K regenerated, handbook + process rebuilt. Appends to the manifest."""
import json, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable
FILES = [R / 'stage1_11/stage1_11_report.html', R / 'advisor/index.html', R / 'process_report/draft_zh.md', J / 'audit_20261105/scoring_audit.html', R / 'pages_20261106b/methods_addendum/index.html',
         *[R / f'talk_docs/{k}.html' for k in ['experiment_walkthrough_zh', 'experiment_walkthrough_methods_zh', 'stage13_script_zh_en', 'keys_and_shelves_script_zh_en', 'methods_handbook_guide_plain_zh', 'progress_report_for_advisor_zh']],
         R / 'methods/parts/F_stage13.html', R / 'methods/parts/G_appendix.html']
BAD = '单看 X2，单看 X2，H3 证据仍不足（2026-11-09 名字位置 probe 后 H3 总体改为部分支持）（H3 总体判断已按名字位置 probe 改为部分支持）'
GOOD = '单看 X2，H3 证据仍不足（H3 总体判断已按名字位置 probe 改为部分支持）'
rows = []
for p in FILES:
    s = p.read_text(encoding='utf-8'); c = s.count(BAD)
    if c: p.write_text(s.replace(BAD, GOOD), encoding='utf-8'); rows.append((str(p).replace(str(R) + '/', ''), BAD, GOOD, c))
N = R / 'talk/src/export/notes_zh.json'; d = json.loads(N.read_text(encoding='utf-8'))
for k, v in d.items():
    c = v['text'].count(BAD)
    if c: v['text'] = v['text'].replace(BAD, '单看 X2，H3 证据仍不足' if k == '81' else GOOD); rows.append(('notes_zh.json #' + k, BAD, '单看 X2，H3 证据仍不足' if k == '81' else GOOD, c))
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
for p in FILES + [N]: assert '单看 X2，单看 X2' not in p.read_text(encoding='utf-8'), p
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); import re; exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
K = R / 'methods/parts/K_post_defence.html'; ks = K.read_text(encoding='utf-8'); lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
K.write_text(ks[:ks.index(lead) + len(lead)] + makeK(FILES[0].read_text(encoding='utf-8')).replace('id="pd-b2-np"', 'id="k-b2-np"') + '\n</section>', encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
assert '单看 X2，单看 X2' not in (R / 'methods/methods_handbook.html').read_text(encoding='utf-8')
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh:
    fh.write('\n'.join(f'| h2-{i} | {f} | {o[:60]}… | {n} | {c} |' for i, (f, o, n, c) in enumerate(rows, 1)) + '\n| h2-K | methods/parts/K_post_defence.html | (part 5) | regenerated | 1 |\n')
print('fixed', sum(r[3] for r in rows), 'in', len(rows), 'files/notes')
