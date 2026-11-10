"""Round h, part 3: note 81 still 935 px (job 11763778). Shorter source tags in note 81 only; no wording change. Appends to the manifest."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'; d = json.loads(N.read_text(encoding='utf-8')); rows = []
for a, b in [('〔补充 10 第 1 项，硬检查 PASS；381_stage13/reports/b1_xall_report.md〕', '〔b1_xall_report.md〕'), ('〔381_stage13/reports/b1_e4b5_report.md〕', '〔b1_e4b5_report.md〕'),
             ('〔381_stage13/config/prereg_addendum12_deviations.json〕', '〔prereg_addendum12_deviations.json〕'), ('〔381_stage13/config/prereg_addendum14.json〕', '〔prereg_addendum14.json〕')]:
    if d['81']['text'].count(a) == 1: d['81']['text'] = d['81']['text'].replace(a, b); rows.append((a, b))
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(f'| h3-{i} | notes_zh.json #81 (overflow) | {a} | {b} | 1 |' for i, (a, b) in enumerate(rows, 1)) + '\n')
print('ok', len(rows))
