"""Sync 2026-11-08 c, part 2 (after apply_20261108c.py; same backups *.before_20261108c, which hold the pre-c state): remaining stale status notes
(deck agenda slide 75; orange '2026-11-06 已更新' notes on Fit B / batch 3 in advisor, addendum, process report). Appends to apply_log_20261108c.json, rebuilds the process page."""
import json, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
F = {'DECK': R / 'merged_deck/stage1_11_deck.html', 'ADV': R / 'advisor/index.html', 'ADD': R / 'pages_20261106b/methods_addendum/index.html', 'PROCMD': R / 'process_report/draft_zh.md'}
for p in F.values(): assert Path(str(p) + '.before_20261108c').exists()
S = {k: p.read_text(encoding='utf-8') for k, p in F.items()}
LOG = json.loads((R / 'sync_20261107/apply_log_20261108c.json').read_text(encoding='utf-8'))
def R_(old, new, keys, n, why):
    tot = 0
    for k in keys:
        c = S[k].count(old)
        if c: S[k] = S[k].replace(old, new); tot += c; LOG.append((why, str(F[k]).replace(str(R) + '/', ''), old, new, c))
    assert tot == n, (why, tot, n)
R_('done, batch 1 (only P1 / P2 with five false titles still running), batches 2 and 3; limits that cannot be redone', 'done, batch 1 (complete), batches 2 and 3 (in progress); limits that cannot be redone', ['DECK'], 1, 'f slide 75 agenda status')
R_('Fit B 与 holdout 列入批次 2，代码已就绪，自动开始；', 'Fit B 与 holdout 列入批次 2，代码已就绪，自动开始；2026-11-08：已在运行，尚无结果；', ['ADV', 'PROCMD'], 2, 'f Fit B status note')
R_('Fit B 与 holdout 已列入批次 2（补充 12 第 2-1 项），代码已就绪，批次 1 结束后自动开始；', 'Fit B 与 holdout 已列入批次 2（补充 12 第 2-1 项），2026-11-08 已在运行，尚无结果；', ['ADV'], 1, 'f Fit B status note (next steps)')
R_('Fit B 续跑与 holdout 列入批次 2（补充 12 第 2-1 项），代码已就绪；', 'Fit B 续跑与 holdout 列入批次 2（补充 12 第 2-1 项），2026-11-08 已在运行，尚无结果；', ['ADD'], 1, 'f Fit B status note (addendum)')
R_('批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），代码已就绪，第二批之后开始；', '批次 3 第 3-1 项补算 L41–L47、L49（6,841 篇，logit 与 public），编排作业已提交，第二批全部结束后自动开始；', ['ADD'], 1, 'f batch-3 status note (addendum)')
for k, p in F.items():
    if S[k] != p.read_text(encoding='utf-8'): p.write_text(S[k], encoding='utf-8')
(R / 'sync_20261107/apply_log_20261108c.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=1), encoding='utf-8')
subprocess.run([sys.executable, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
print('part 2 ok;', len(LOG), 'log rows')
