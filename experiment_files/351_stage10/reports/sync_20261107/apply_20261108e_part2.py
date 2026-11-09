"""Round e, part 2: note 72 overflowed again (969 px, job 11741367) after the 79% qualifier. Shorter source tag and qualifier; numbers unchanged. Appends to the manifest."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'; d = json.loads(N.read_text(encoding='utf-8')); rows = []
def rep(a, b):
    assert d['72']['text'].count(a) == 1, a[:50]; d['72']['text'] = d['72']['text'].replace(a, b); rows.append((a, b))
rep('（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json）', '（姓 4,402 / 5,580；名 42%、首字母 72%；v5x0_leak_share.json）')
rep('〔补充 9，标题最后一个 token，真标题 − false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md 第 5 节〕', '〔1,395 篇，剔除标题复用；e4b_alltok.md 第 5 节〕')
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh:
    fh.write('\n'.join(f'| e2-{i} | notes_zh.json #72 (overflow) | {a} | {b} | 1 |' for i, (a, b) in enumerate(rows, 1)) + '\n')
print('ok')
