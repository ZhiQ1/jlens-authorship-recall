"""Sync 2026-11-08 c, part 3: speaker notes 81 and 82 overflowed the notes page in the v21 with-notes PDF (job 11740140: 1548 / 1139 px > 898).
Replace the long batch-1/CD text (note 81) and the appended limitations (note 82) by short versions with the same numbers. Appends to apply_log_20261108c.json."""
import json, re
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'
d = json.loads(N.read_text(encoding='utf-8')); LOG = json.loads((R / 'sync_20261107/apply_log_20261108c.json').read_text(encoding='utf-8'))
t = d['81']['text']; i = t.index('P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成，硬检查 PASS）：'); j = t.index('批次 2（补充 11、12）', i)
new81 = ('P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成）：5 个假标题平均为主结果，false_0 并列；两版之差的区间都含 0，结论不变（P1 全部位置 L48 +0.821，false_0 0.825；'
         'P2 注意力 L48 +0.237，MLP L56 +0.226）；p9 各假标题 694–711 篇，集合不同，未加权；“:” 分子 B/A 0.72–0.87（false_0 0.78–0.99）〔391_groups/reports/b1_p12f_report.md〕。'
         'C / D 组补全（2-6，已完成）：C 462 篇，同一引用档内与 A 时间点相同，真假标题差距更大（C − A +0.075 [+0.024, +0.130]）；D 33 篇只作描述〔391_groups/reports/b2_cd_report.md〕。')
LOG.append(('notes 81 shortened (overflow)', 'notes_zh.json #81', t[i:j][:150], new81, 1)); d['81']['text'] = t[:i] + new81 + t[j:]
t = d['82']['text']; i = t.index(' 2026-11-08（报告第 30 版）补充的局限：')
new82 = (' 2026-11-08（第 30 版）补充的局限：Stage 10 在 L24–L40 每 8 层取一层（没有 L25–L31、L33–L39），没有补层计划；容差 0.25 → 0.5 已用于 Stage 10 主轮（最大差 0.367）；'
         '干预只用 1,186 / 9,108 篇；分母效应（C 0.559 对 A 0.407）；M5 B 部分和 E4b 的 X1 对照流程只用 false_0；数字核对已登记 680 个、4,307 处全部一致，约 1,024 个未登记'
         '〔conclusions_v30_checks.md A1–A3〕。Stage 8 的三个前提：首 token 64.5% 是首字母；偏离 D13-1；U28。')
LOG.append(('notes 82 shortened (overflow)', 'notes_zh.json #82', t[i:][:150], new82, 1)); d['82']['text'] = t[:i] + new82
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
(R / 'sync_20261107/apply_log_20261108c.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=1), encoding='utf-8'); print('ok', len(LOG))
