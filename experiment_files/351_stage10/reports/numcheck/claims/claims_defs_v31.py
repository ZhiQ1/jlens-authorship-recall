"""claims_defs v31 (2026-11-21): v30 + addendum 21 (injection / sufficiency test, locked confirmatory, 391_groups/summary_a21/).
New ids 'A31-'.  Run with:  CLAIMS_DEFS=claims_defs_v31 bash claims_run.sh"""
from claims_defs_v30 import *          # noqa: F401,F403
from claims_defs_v30 import C, csv, MANUAL
from claims_defs_v5 import A as _A5


def A(cid, *a, **k):
    _A5('\x00' + cid, *a, **k)
    c = C[-1]; c['id'] = 'A31-' + cid; MANUAL[-1] = c['id']


SN = r'[+−\-]?[\d.,]+'
P = '391_groups/summary_a21/primary.csv'
T = '391_groups/summary_a21/tf.csv'
CF = '补充 21 注入检验（锁定），1,200 篇（A 600、B 600），团队整群 bootstrap 2,000 次；'
w = dict(grp='A', outcome='any_full', layer=52, beta=2, contrast='own - mis')
A('S52b2', '补充 21：S = 自己 − 另一篇，L52 β2', csv(P, 'est', **w), CF, '600 篇 A', 3, [r'(?:最大 |largest )L52 β2 #(?= \[)'])
A('S52b2-lo', '同上（下限）', csv(P, 'lo', **w), CF, '600 篇 A', 3, [r'(?:最大 |largest )L52 β2 \+0\.020 \[#(?=, )'], sign=False)
A('S52b2-hi', '同上（上限）', csv(P, 'hi', **w), CF, '600 篇 A', 3, [r'(?:最大 |largest )L52 β2 \+0\.020 \[' + SN + r', #\]'], sign=False)
A('S52b2-pholm', '同上（Holm p）', csv(P, 'p_holm', **w), CF, '600 篇 A', 2, [r'Holm p #(?=[）)])'], sign=False)
for lay, b, est in [(48, 4, r'−0\.054'), (52, 4, r'−0\.102')]:
    ww = dict(grp='A', layer=lay, beta=b, contrast='own - base')
    A(f'TF{lay}b{b}', f'补充 21：teacher-forcing 输出名次 自己 − 基线，L{lay} β{b}', csv(T, 'est', **ww), CF, '600 篇 A', 3, [rf'L{lay} β{b} #(?= \[−0\.(?:06|11))'])
    A(f'TF{lay}b{b}-lo', '同上（下限）', csv(T, 'lo', **ww), CF, '600 篇 A', 3, [rf'L{lay} β{b} {est} \[#(?=, )'])
    A(f'TF{lay}b{b}-hi', '同上（上限）', csv(T, 'hi', **ww), CF, '600 篇 A', 3, [rf'L{lay} β{b} {est} \[' + SN + r', #\]'])
