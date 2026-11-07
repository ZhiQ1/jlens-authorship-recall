"""2026-11-06 b: deck v20 (82 slides, unpublished) with the user-confirmed batch-1 results. Works on the v20 outputs of edit_deck_v20.py
(merged_deck/stage1_11_deck.html, slides.json, notes_zh.json), backed up first as *.before_20261106b.* and always used as input (idempotent).
- slides 72 (alltok), 75 (pd0 divider), 81 (pd5 redo programme): sections re-rendered from deck_v20b_new (each old section must equal the
  deck_v20_new rendering, so nothing else on them is lost); slides.json text and notes updated
- notes 69 (M3/X1), 70 (X4/X3), 71 (X2): one sentence each on the all-author version (wording b)
Then: patch_editable_v20b.py (pptx), export_deck_v18.py (PDFs)."""
import json, re, shutil, sys
from pathlib import Path
HERE = Path(__file__).parent; sys.path.insert(0, str(HERE))
import importlib
N0 = importlib.import_module('deck_v20_new')
SPEC0 = {k: dict(v) for k, v in ((s['key'], s) for s in N0.SLIDES)}          # copies before deck_v20b_new mutates them
SEC0 = {k: N0.html_section(N0.SLIDES[[s['key'] for s in N0.SLIDES].index(k)]) for k in ('alltok', 'pd0', 'pd5')}
TXT0 = {k: N0.slide_text(N0.SLIDES[[s['key'] for s in N0.SLIDES].index(k)]) for k in ('alltok', 'pd0', 'pd5')}
import deck_v20b_new as N

DECK = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck/stage1_11_deck.html')
FILES = [DECK, HERE / 'slides.json', HERE / 'notes_zh.json']
for f in FILES:
    b = f.with_name(f.stem + '.before_20261106b' + f.suffix)
    if not b.exists(): shutil.copy2(f, b)
bk = lambda f: f.with_name(f.stem + '.before_20261106b' + f.suffix)
h = bk(DECK).read_text(encoding='utf-8'); meta = json.loads(bk(HERE / 'slides.json').read_text()); notes = json.loads(bk(HERE / 'notes_zh.json').read_text())
order = [tuple(x) for x in json.loads((HERE / 'v20_order.json').read_text())]
assert len(order) == len(meta) == len(notes) == 82
pos = {v: k for k, (kind, v) in enumerate(order, 1) if kind == 'new'}
assert (pos['alltok'], pos['pd0'], pos['pd5']) == (72, 75, 81), pos

head, rest = h.split('<section class="slide', 1); rest = '<section class="slide' + rest
body, tail = rest.split('\n</div>\n<nav', 1); tail = '\n</div>\n<nav' + tail
secs = [x for x in re.split(r'(?=<section class="slide)', body) if x]; assert len(secs) == 82
BY = {s['key']: s for s in N.SLIDES}
for key in ('alltok', 'pd0', 'pd5'):
    k = pos[key]
    assert secs[k - 1] == SEC0[key], ('slide changed after the v20 build', k)
    secs[k - 1] = N.html_section(BY[key])
    assert meta[k - 1]['text'] == TXT0[key]; meta[k - 1]['text'] = N.slide_text(BY[key]); meta[k - 1]['updated'] = '2026-11-06b'
    notes[str(k)] = {'new': True, 'text': BY[key]['notes']}

ADD = {69: ' 2026-11-06（批次 1 第 1 项）：X1–X4 改为给全部作者打分（全部名字 token）并按作者排位分层，结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]〔补充 10 第 1 项，测试集，团队聚类 95% CI；381_stage13/reports/b1_xall_report.md〕）。',
       70: ' 2026-11-06（批次 1 第 1 项，全部作者）：X3 改写标题保留约 90% 的作者偏好，target 与 control 一样；X4 从 L8 起可解码出作者，各作者排位相同，认得出的论文在 L8–L40 更高；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释〔381_stage13/reports/b1_xall_report.md〕。',
       71: ' 2026-11-06（批次 1 第 1 项）：用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009），H3 仍证据不足〔381_stage13/reports/b1_xall_report.md “X2: verdict” 与 “New S_auth” 节〕。'}
for k, t in ADD.items():
    assert '2026-11-06（批次 1' not in notes[str(k)]['text']; notes[str(k)]['text'] += t

out = head + ''.join(secs) + tail
assert not re.search('minyan', out + json.dumps(notes, ensure_ascii=False), re.I)
DECK.write_text(out, encoding='utf-8')
(HERE / 'slides.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1))
(HERE / 'notes_zh.json').write_text(json.dumps(notes, ensure_ascii=False, indent=1))
print('deck v20b written', len(secs), 'slides; changed 72, 75, 81; notes 69-72, 75, 81')
