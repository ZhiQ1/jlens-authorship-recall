"""Round d, part 2: notes 72 / 81 still overflow after job 11740706 (969 / 935 px > 898). Shorter source tags and one explanatory sentence; numbers unchanged. Appends to the manifest (round d)."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'
d = json.loads(N.read_text(encoding='utf-8')); rows = []
def rep(k, a, b, why):
    assert d[k]['text'].count(a) == 1, (k, a[:50]); d[k]['text'] = d[k]['text'].replace(a, b); rows.append((why, 'notes_zh.json #' + k, a, b, 1))
rep('72', '原 E4b 只给每位作者的第一个 token 打分，而这个 token 多半是首字母，所以它低估了标题位置携带的名字信息。', '', 'd2 note 72 shortened (overflow)')
rep('72', '（与补充 9 已发表值相同，e4b_alltok.md）', '', 'd2 note 72 shortened (overflow)')
rep('72', '〔6,841 篇；381_stage13/reports/c13_C3b.md〕', '〔6,841 篇；c13_C3b.md〕', 'd2 note 72 shortened (overflow)')
rep('81', '〔381_stage13/reports/b1_x7f_report.md、e4b_alltok.md、c13_C1.md–c13_C5.md〕', '〔b1_x7f_report.md、e4b_alltok.md、c13_C1–C5.md〕', 'd2 note 81 shortened (overflow)')
rep('81', '（偏离 D1，保留 4,654 篇，每篇平均约 1.5 个可用假标题，0–4 个；预注册版只减 false_0、1,395 篇时 L40 姓首 token 为 +0.071）', '（偏离 D1，4,654 篇，每篇约 1.5 个可用假标题）', 'd2 note 81 shortened (overflow)')
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|')
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh:
    fh.write('\n'.join(f'| d2-{i} | {w} | {f} | {cut(a)} | {cut(b) or "(deleted)"} | {c} |' for i, (w, f, a, b, c) in enumerate(rows, 1)) + '\n')
print('ok', len(rows))
