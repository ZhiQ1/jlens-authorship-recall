"""Sync 2026-11-08 c, part 4: notes 81 and 28 still overflow after part 3 (job 11740225: slide 81 1105 px, slide 28 935 px > 898). Shorter wording, same numbers."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'
d = json.loads(N.read_text(encoding='utf-8')); LOG = json.loads((R / 'sync_20261107/apply_log_20261108c.json').read_text(encoding='utf-8'))
def rep(k, old, new, why):
    assert d[k]['text'].count(old) == 1, (k, old[:60]); d[k]['text'] = d[k]['text'].replace(old, new); LOG.append((why, 'notes_zh.json #' + k, old[:150], new, 1))
t = d['81']['text']; i = t.index('P1 / P2 用 5 个假标题（批次 1 第 3 项，已完成）：'); j = t.index('批次 2（补充 11、12）', i)
rep('81', t[i:j], 'P1 / P2 用 5 个假标题（已完成）：5 个假标题平均为主结果，与 false_0 之差的区间都含 0，结论不变；p9 各假标题 694–711 篇，集合不同，未加权；“:” 分子 B/A 0.72–0.87（false_0 0.78–0.99）。'
    'C / D 组补全（已完成）：C 462 篇，同一引用档内与 A 时间点相同；D 33 篇只作描述〔b1_p12f_report.md；b2_cd_report.md〕。', 'notes 81 shortened again (overflow)')
rep('81', '，这一差别不再作为 H2 的证据（只看标题文字的 BERT 基线 +0.088 不弱于 Qwen L8 +0.018）', '，不再作为 H2 的证据', 'notes 81 X4 sentence shortened (overflow)')
t = d['28']['text']; i = t.index(' 2026-11-08 补（补充 11 B，C / D 组补全）：')
rep('28', t[i:], ' 2026-11-08 补（补充 11 B）：C 补全到 462 篇后，同一引用档内与 A 时间点相同（E1 L48 −0.037 [−0.080, +0.009]），真假标题差距更大（C − A +0.075 [+0.024, +0.130]）；D 33 篇只作描述〔391_groups/reports/b2_cd_report.md〕。', 'notes 28 shortened (overflow)')
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
(R / 'sync_20261107/apply_log_20261108c.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=1), encoding='utf-8'); print('ok', len(LOG))
