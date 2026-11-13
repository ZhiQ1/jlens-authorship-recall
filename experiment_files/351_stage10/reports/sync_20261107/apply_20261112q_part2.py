"""Round q, part 2: note 81 overflowed (935 px, job 11838414). Shorter deviations clause in note 81 only (same facts). Appends to the manifest."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'; d = json.loads(N.read_text(encoding='utf-8'))
a = '；与预注册的出入记在补充 12 出入记录 D12-1 到 D12-3〔prereg_addendum12_deviations.json〕，2-7 的来源改用不含年份的 X4 提示。'
b = '；出入记录见补充 12（D12-1 到 D12-5；2-7 的来源改用不含年份的 X4 提示）。'
assert d['81']['text'].count(a) == 1; d['81']['text'] = d['81']['text'].replace(a, b)
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write(f'| q2-1 | notes_zh.json #81 (overflow) | {a} | {b} | 1 |\n')
print('ok')
